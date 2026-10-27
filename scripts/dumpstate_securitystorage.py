"""Section readers for the security, storage and configuration parts of an Android bug report.

These readers run inside the single pass of ``dumpstate_reader`` (they are registered in its READERS
list) and keep bounded rows on the report object: device policy, lock settings, biometrics, trust,
the ADB manager, two vendor security services, storage (df, mount, vold, storaged, diskstats), the
SQLite connection pools (dbinfo), the device config flags, the platform compat change list, the
build-time release flags and the SDK extension versions.

Every reader prints what the text prints and does not judge it. A row keeps the number of the line
it came from. Lines the reader does not understand are skipped, and a few counts are warned about
so that a section that was read only in part does not look complete.

Import ``scripts.dumpstate_reader`` before this module: the reader module registers these readers
from the end of its own text, so importing this one first would find the reader module half built.
"""
import collections
import json
import re
from datetime import timezone

from scripts import dumpstate_reader as base
from scripts.dumpstate_reader import SectionReader, tidy, to_int, key_values, parse_wall_time

TEXT_CAP = 2000
SQL_CAP = 2000
MAX_JSON_LINES = 100000
BIGGEST_INT = (1 << 63) - 1

# The tables these readers fill on the report object (created on first use, the shared Report class is not edited).
TABLES = ('ss_dp_admins', 'ss_dp_state', 'ss_dp_policies', 'ss_lock_users', 'ss_lock_files', 'ss_lock_state', 'ss_lock_log',
          'ss_bio_stats', 'ss_bio_sensors', 'ss_bio_events', 'ss_trust_agents', 'ss_trust_events', 'ss_adb',
          'ss_knox_log', 'ss_knox_custom', 'ss_df', 'ss_df_inodes', 'ss_mounts', 'ss_volumes', 'ss_vold',
          'ss_storage_io', 'ss_disk_items', 'ss_package_sizes', 'ss_db_pools', 'ss_db_files', 'ss_db_ops',
          'ss_device_config', 'ss_compat', 'ss_release_flags', 'ss_sdk')

DpAdmin = collections.namedtuple(
    'DpAdmin', 'user provisioning component package uid test_only policies source_dir password_quality min_length '
               'wipe_after encryption_requested keyguard_disabled network_logging vpn_package vpn_lockdown is_parent '
               'common_criteria line')
DpState = collections.namedtuple('DpState', 'group user name value line')
DpPolicy = collections.namedtuple('DpPolicy', 'scope user key package authorities admin_value mechanism resolved_value line')
LockUser = collections.namedtuple(
    'LockUser', 'user protector_id changed_text previous_protector backup_protector si_checker secure_mode sid quality '
                'credential_type separate_challenge metrics failed_attempts sp_handle other line')
LockFile = collections.namedtuple('LockFile', 'location directory size mtime_text name line')
LockState = collections.namedtuple('LockState', 'group user name value line')
LockLog = collections.namedtuple('LockLog', 'state time_text message detail frames line')
BioStat = collections.namedtuple('BioStat', 'service sensor_id provider provider_service print_id counters hal_deaths line')
BioSensor = collections.namedtuple('BioSensor', 'sensor_id oem_strength updated_strength modality state cookie line')
BioEvent = collections.namedtuple('BioEvent', 'service sequence event user sensor_id request_id strength successful text line')
TrustAgent = collections.namedtuple(
    'TrustAgent', 'user_id user_name flags qualifiers trust_state trusted trust_managed device_locked active_unlock '
                  'strong_auth note agent bound connected managing agent_trusted line')
TrustEvent = collections.namedtuple('TrustEvent', 'user_id user_name sequence time_text event detail line')
AdbRow = collections.namedtuple('AdbRow', 'path value line')
KnoxLog = collections.namedtuple('KnoxLog', 'kind time_text tag message line')
KnoxCustom = collections.namedtuple('KnoxCustom', 'manager name value text line')
DfRow = collections.namedtuple('DfRow', 'filesystem blocks used available use_percent mount line')
InodeRow = collections.namedtuple('InodeRow', 'filesystem inodes used free use_percent mount line')
MountRow = collections.namedtuple('MountRow', 'device mount_point fs_type options line')
Volume = collections.namedtuple(
    'Volume', 'kind volume_id state path internal_path description primary removable emulated mount_flags mount_user '
              'disk_id fs_type fs_uuid fs_label volume_type other line')
VoldLog = collections.namedtuple('VoldLog', 'time_text pid tid component message buffer line')
StorageIo = collections.namedtuple('StorageIo', 'name values line')
DiskItem = collections.namedtuple('DiskItem', 'section item value line')
PackageSize = collections.namedtuple('PackageSize', 'index package app_size data_size cache_size line')
DbPool = collections.namedtuple(
    'DbPool', 'pid process path open max_connections total_time total_statements average_time configuration read_only '
              'secure wal connections operations other line')
DbFile = collections.namedtuple('DbFile', 'pid process directory name size ctime mtime atime line')
DbOp = collections.namedtuple(
    'DbOp', 'pid process path connection listing index time_text operation took_ms status sql sql_length details line')
ConfigFlag = collections.namedtuple('ConfigFlag', 'namespace flag value line')
CompatChange = collections.namedtuple('CompatChange', 'change_id name since_sdk after_sdk disabled logging_only overridable other line')
ReleaseFlag = collections.namedtuple(
    'ReleaseFlag', 'partition name namespace description declared_type declared_value value_type value workflow containers')
SdkRow = collections.namedtuple('SdkRow', 'group name value line')


# ---------------------------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------------------------
def add(report, table, row):
    """Append to one of the tables above, creating it on the report object on first use."""
    if not hasattr(report, table):
        setattr(report, table, [])
    report.add(table, row)


def cap(text, size=TEXT_CAP):
    return tidy(text)[:size]


def number(text):
    """An int for a printed integer that SQLite can hold, the printed text for any other value, '' for nothing."""
    value = str(text).strip()
    if not value:
        return ''
    digits = value.lstrip('-')
    if digits.isascii() and digits.isdigit():
        as_int = int(value)
        return as_int if abs(as_int) <= BIGGEST_INT else value
    return tidy(value)


def split_pair(body):
    """``(name, value)`` for ``name=value`` or ``name: value``, whichever delimiter comes first."""
    equals = body.find('=')
    colon = body.find(':')
    if equals >= 0 and (colon < 0 or equals < colon):
        return body[:equals].strip(), body[equals + 1:].strip()
    if colon >= 0:
        return body[:colon].strip(), body[colon + 1:].strip()
    return body.strip(), ''


def indent_of(text):
    return len(text) - len(text.lstrip(' '))


def keyed_split(text, key_pattern):
    """Split ``mA=1 two words mB=x`` into a dict where keys are the words that match ``key_pattern`` followed by ``=``."""
    found = collections.OrderedDict()
    marks = [(match.start(1), match.end(), match.group(1))
             for match in re.finditer(r'(?:(?<=\s)|^)(' + key_pattern + r')=', text)]
    for position, (_start, end, key) in enumerate(marks):
        stop = marks[position + 1][0] if position + 1 < len(marks) else len(text)
        if key not in found:
            found[key] = text[end:stop].strip()
    return found


def utc_from_iso(text):
    """Timezone-aware UTC datetime from ``2026-04-27T15:30:05.259227Z`` or None."""
    moment = parse_wall_time(text)
    return moment.replace(tzinfo=timezone.utc) if moment is not None else None


# ---------------------------------------------------------------------------------------------
# device policy
# ---------------------------------------------------------------------------------------------
ADMIN_FIELDS = {
    'uid': 'uid', 'testOnlyAdmin': 'test_only', 'passwordQuality': 'password_quality',
    'minimumPasswordLength': 'min_length', 'maximumFailedPasswordsForWipe': 'wipe_after',
    'encryptionRequested': 'encryption_requested', 'disabledKeyguardFeatures': 'keyguard_disabled',
    'isNetworkLoggingEnabled': 'network_logging', 'mAlwaysOnVpnPackage': 'vpn_package',
    'mAlwaysOnVpnLockdown': 'vpn_lockdown', 'isParent': 'is_parent', 'mCommonCriteriaMode': 'common_criteria'}
_ENFORCING_PACKAGE = re.compile(r'mPackageName=\s*([^,}]*)')
_ENFORCING_AUTHORITIES = re.compile(r'mAuthorities=\s*\[([^\]]*)\]')
_ADMIN_USER_HEADER = re.compile(r'^Enabled Device Admins \(User (-?\d+), provisioningState: (-?\d+)\):?$')


def enforcing_admin(text):
    """``(package, authorities)`` of an ``EnforcingAdmin { mPackageName= ..., mAuthorities= [...] ...}`` text."""
    package = _ENFORCING_PACKAGE.search(text)
    authorities = _ENFORCING_AUTHORITIES.search(text)
    return (tidy(package.group(1).strip()) if package else '', tidy(authorities.group(1).strip()) if authorities else '')


class DevicePolicyReader(SectionReader):
    """``dumpsys device_policy``: device admins, owners, policy state and the policy engine's local and global policies."""
    kind = 'service'
    name = 'device_policy'

    def __init__(self, report, section):
        SectionReader.__init__(self, report, section)
        self.mode = ''            # top level block: main, cache, devstate, personal
        self.sub = ''             # block of the main state
        self.user = None
        self.provisioning = ''
        self.admin = None
        self.policies_listed = False
        self.owner = ''
        self.policy_user = None
        self.policy = None
        self.policy_mode = ''
        self.last_name = ''

    # -- rows
    def _state(self, group, user, name, value, line_no):
        add(self.report, 'ss_dp_state', DpState(group, user, cap(name, 300), cap(value), line_no))

    def _close_admin(self):
        admin = self.admin
        self.admin = None
        self.policies_listed = False
        if admin is None:
            return
        add(self.report, 'ss_dp_admins', DpAdmin(
            admin['user'], admin['provisioning'], admin['component'], admin['component'].partition('/')[0], to_int(admin.get('uid')),
            admin.get('test_only', ''), ', '.join(admin['policies']), admin.get('source_dir', ''),
            admin.get('password_quality', ''), to_int(admin.get('min_length')), to_int(admin.get('wipe_after')),
            admin.get('encryption_requested', ''), admin.get('keyguard_disabled', ''), admin.get('network_logging', ''),
            admin.get('vpn_package', ''), admin.get('vpn_lockdown', ''), admin.get('is_parent', ''),
            admin.get('common_criteria', ''), admin['line']))

    def _close_policy(self):
        policy = self.policy
        self.policy = None
        self.policy_mode = ''
        if policy is None:
            return
        scope, user = policy['scope'], policy['user']
        if not policy['admins']:
            add(self.report, 'ss_dp_policies', DpPolicy(scope, user, cap(policy['key'], 300), '', '', '', policy['mechanism'],
                                                        cap(policy['resolved']), policy['line']))
        for item in policy['admins']:
            package, authorities = enforcing_admin(item['admin'])
            add(self.report, 'ss_dp_policies', DpPolicy(scope, user, cap(policy['key'], 300), package, authorities,
                                                        cap(item['value']), policy['mechanism'], cap(policy['resolved']),
                                                        policy['line']))

    # -- the lines
    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            return
        indent = indent_of(text)
        if indent == 0:
            self._top(line_no, body)
            return
        if self.mode == 'main':
            self._main(line_no, indent, body)
        elif self.mode in ('cache', 'devstate'):
            self._cache(line_no, indent, body)
        elif self.mode == 'personal' and indent == 2:
            name, value = split_pair(body)
            self._state('Personal apps suspension helper', None, name, value, line_no)

    def _top(self, line_no, body):
        self._leave_main()
        if body.startswith(('Service host process PID', 'Threads in use', 'Client PIDs')):
            return
        if body.startswith('Current Device Policy Manager state'):
            self.mode = 'main'
        elif body.startswith('Device policy cache'):
            self.mode, self.last_name = 'cache', ''
        elif body.startswith('Device state cache'):
            self.mode, self.last_name = 'devstate', ''
        elif body.startswith('PersonalAppsSuspensionHelper'):
            self.mode = 'personal'
        else:
            self.mode = ''
            name, value = split_pair(body)
            self._state('Device policy manager', None, name, value, line_no)

    def _leave_main(self):
        self._close_admin()
        self._close_policy()
        self.sub = ''

    def _main(self, line_no, indent, body):
        if indent == 2:
            self._leave_main()
            header = _ADMIN_USER_HEADER.match(body)
            if header:
                self.sub = 'admins'
                self.user, self.provisioning = int(header.group(1)), header.group(2)
            elif body in ('Immutable state:', 'Constants:', 'Stats:'):
                self.sub = 'immutable' if body.startswith('Immutable') else 'skip'
            elif re.match(r'^(Profile|Device) [Oo]wner', body) and body.endswith(':'):
                self.sub = 'owner'
                self.owner = body[:-1].strip()
                match = re.search(r'\(User (-?\d+)\)', body)
                self.user = int(match.group(1)) if match else None
            elif body.startswith('Local Policies'):
                self.sub, self.policy_user = 'local', None
            elif body.startswith('Global Policies'):
                self.sub, self.policy_user = 'global', None
            elif body.startswith('Admin Policies size'):
                self.sub, self.policy_user = 'adminsize', None
            elif re.match(r'^User (-?\d+):$', body):
                self.sub, self.policy_user = 'adminsize', int(body[5:-1])
            else:
                name, value = split_pair(body)
                self._state('Device policy manager state', None, name, value, line_no)
            return
        if self.sub == 'immutable' and indent == 4:
            name, value = split_pair(body)
            self._state('Immutable state', None, name, value, line_no)
        elif self.sub == 'owner' and indent == 4:
            name, value = split_pair(body)
            self._state(self.owner, self.user, name, value, line_no)
        elif self.sub == 'admins':
            self._admins(line_no, indent, body)
        elif self.sub in ('local', 'global'):
            self._policies(indent, body, line_no)
        elif self.sub == 'adminsize':
            user = re.match(r'^User (-?\d+):$', body)
            if user:
                self.policy_user = int(user.group(1))
            elif body.startswith('Admin :'):
                text = body[len('Admin :'):]
                package, _authorities = enforcing_admin(text)
                value = text.rpartition('} :')[2].strip() if '} :' in text else ''
                self._state('Admin policies size', self.policy_user, package or cap(text, 200), value, line_no)

    def _admins(self, line_no, indent, body):
        if indent == 4:
            self._close_admin()
            if body.endswith(':') and '/' in body and '=' not in body:
                self.admin = {'user': self.user, 'provisioning': to_int(self.provisioning), 'component': cap(body[:-1], 300),
                              'policies': [], 'line': line_no}
            elif '=' in body or ':' in body:
                name, value = split_pair(body)
                self._state('Device admins state', self.user, name, value, line_no)
            return
        admin = self.admin
        if admin is None:
            return
        if indent == 6:
            self.policies_listed = body == 'policies:'
            if body.endswith(':') or '=' not in body:
                return
            name, value = body.split('=', 1)
            if name in ADMIN_FIELDS and ADMIN_FIELDS[name] not in admin:
                admin[ADMIN_FIELDS[name]] = cap(value, 300)
        elif indent == 8 and self.policies_listed:
            admin['policies'].append(cap(body, 100))
        elif indent > 8:
            if body.startswith('sourceDir=') and 'source_dir' not in admin:
                admin['source_dir'] = cap(body.split('=', 1)[1], 300)

    def _policies(self, indent, body, line_no):
        key_indent = 6 if self.sub == 'local' else 4
        scope = 'Local' if self.sub == 'local' else 'Global'
        if self.sub == 'local' and indent == 4:
            self._close_policy()
            user = re.match(r'^User (-?\d+):$', body)
            self.policy_user = int(user.group(1)) if user else None
            return
        if indent == key_indent:
            self._close_policy()
            self.policy = {'scope': scope, 'user': self.policy_user, 'key': body, 'admins': [], 'mechanism': '',
                           'resolved': '', 'line': line_no}
            return
        policy = self.policy
        if policy is None:
            return
        if body.startswith('Per-admin Policy'):
            self.policy_mode = 'per'
        elif body.startswith('Resolved Policy'):
            self.policy_mode = 'res'
            open_at, close_at = body.find('('), body.rfind(')')
            policy['mechanism'] = cap(body[open_at + 1:close_at], 100) if 0 <= open_at < close_at else ''
        elif self.policy_mode == 'per':
            if body.startswith('EnforcingAdmin'):
                policy['admins'].append({'admin': body, 'value': ''})
            elif policy['admins'] and body != 'null':
                item = policy['admins'][-1]
                item['value'] = (item['value'] + ' ' + body).strip()
        elif self.policy_mode == 'res' and body != 'null':
            policy['resolved'] = (policy['resolved'] + ' ' + body).strip()

    def _cache(self, line_no, indent, body):
        group = 'Device policy cache' if self.mode == 'cache' else 'Device state cache'
        name, value = split_pair(body)
        if indent == 2:
            self.last_name = name
            self._state(group, None, name, value, line_no)
        elif indent >= 4:
            self._state(group, None, self.last_name + ' / ' + name if self.last_name else name, value, line_no)

    def finish(self):
        self._leave_main()


# ---------------------------------------------------------------------------------------------
# lock settings
# ---------------------------------------------------------------------------------------------
LOCK_USER_KEYS = {
    'LSKF-based SP protector ID': 'protector_id', 'LSKF last changed': 'changed', 'Last changed': 'changed',
    'Backup protector': 'backup_protector',
    'SI Checker': 'si_checker', 'Secure Mode': 'secure_mode', 'SID': 'sid', 'Quality': 'quality',
    'CredentialType': 'credential_type', 'SeparateChallenge': 'separate_challenge', 'Metrics': 'metrics',
    'failed attempt': 'failed_attempts', 'SP Handle': 'sp_handle'}
_LOCK_USER = re.compile(r'^User (-?\d+)$')
_LOCK_FILE = re.compile(r'^(\d+) (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) (.+)$')
_LOCK_DIR = re.compile(r'^(User -?\d+|Backup) \[(.*)\]:$')
_PREVIOUS = re.compile(r'^(.*?) \(previous protector: ([^)]*)\)$')
_LOG_BOUNDARY = re.compile(r'^-+ (Start|End) (.*?) state -+$')
# an entry time with a year (Android 14 and later) or without one (the Android 13 Samsung layout, indented by two spaces)
_LOG_TIME = re.compile(r'^((?:\d{4}-)?\d\d-\d\d \d\d:\d\d:\d\d(?:\.\d+)?) ?(.*)$')
_LOG_ENTRY_INDENT = 2
_LOG_FRAME = re.compile(r'^\s+[A-Za-z_$][\w$.]*\.[\w$<>]+:\d+$')


class LockSettingsReader(SectionReader):
    """``dumpsys lock_settings``: the credential protector state of each user, the protector files and the strong auth state."""
    kind = 'service'
    name = 'lock_settings'

    def __init__(self, report, section):
        SectionReader.__init__(self, report, section)
        self.part = ''
        self.fields = None
        self.location = ''
        self.directory = ''
        self.group = ''
        self.log_state = ''
        self.entry = None

    def _flush_entry(self):
        entry, self.entry = self.entry, None
        if entry is not None:
            add(self.report, 'ss_lock_log', LockLog(entry['state'], entry['time'], cap(entry['message'], 600),
                                                    cap(' | '.join(entry['detail']), 1000), entry['frames'], entry['line']))

    def _log(self, line_no, text):
        body = text.rstrip()
        stripped = body.strip()
        if not stripped:
            return
        boundary = _LOG_BOUNDARY.match(stripped)
        if boundary:
            self._flush_entry()
            self.log_state = boundary.group(2) if boundary.group(1) == 'Start' else ''
            return
        # an entry starts at the left or two spaces in; a deeper line that starts with a time is detail of the entry above
        match = _LOG_TIME.match(stripped) if stripped[0].isdigit() and indent_of(body) <= _LOG_ENTRY_INDENT else None
        if match:
            self._flush_entry()
            self.entry = {'state': cap(self.log_state, 60), 'time': match.group(1), 'message': match.group(2).strip(), 'detail': [],
                          'frames': 0, 'line': line_no}
        elif self.entry is not None:
            if _LOG_FRAME.match(body) or stripped == '<bottom of call stack>':
                self.entry['frames'] += 1
            elif len(self.entry['detail']) < 50:
                self.entry['detail'].append(stripped)

    def _flush_user(self):
        fields = self.fields
        self.fields = None
        if fields is None:
            return
        changed = fields.pop('changed', '')
        previous = ''
        match = _PREVIOUS.match(changed)
        if match:
            changed, previous = match.group(1), match.group(2)
        user, line_no = fields.pop('user'), fields.pop('line')
        add(self.report, 'ss_lock_users', LockUser(
            user, fields.pop('protector_id', ''), cap(changed, 100), cap(previous, 100),
            cap(fields.pop('backup_protector', ''), 200), cap(fields.pop('si_checker', ''), 200),
            fields.pop('secure_mode', ''), fields.pop('sid', ''), fields.pop('quality', ''),
            fields.pop('credential_type', ''), fields.pop('separate_challenge', ''), fields.pop('metrics', ''),
            fields.pop('failed_attempts', ''), fields.pop('sp_handle', ''),
            cap('; '.join('%s: %s' % (key, value) for key, value in fields.items()), 400), line_no))

    def _state(self, group, user, name, value, line_no):
        add(self.report, 'ss_lock_state', LockState(group, user, cap(name, 300), cap(value), line_no))

    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            return
        if self.part == 'log':
            self._log(line_no, text)
            return
        if body.startswith(('Service host process PID', 'Threads in use', 'Client PIDs', 'Current lock settings service state')):
            return
        indent = indent_of(text)
        if indent == 0:
            self._heading(line_no, body)
            return
        match = _LOCK_USER.match(body)
        if match and self.part in ('users', 'oldusers'):
            self._flush_user()
            self.fields = {'user': int(match.group(1)), 'line': line_no}
            return
        if self.part in ('users', 'oldusers'):
            if self.fields is not None:
                key, separator, value = body.partition(': ') if ': ' in body else body.partition(' = ')
                if separator:
                    key = key.strip()
                    target = LOCK_USER_KEYS.get(key, key)
                    self.fields[target if target not in self.fields else key] = value.strip()
        elif self.part == 'keys':
            self._state('Keys in namespace', None, '', body, line_no)
        elif self.part == 'storage':
            self._storage(line_no, body)
        elif self.part in ('strong', 'escrow'):
            self._strong(line_no, indent, body)

    def _heading(self, line_no, body):
        self._flush_user()
        self.group = body.rstrip(':')
        headings = {'User State:': 'users', 'Keys in namespace:': 'keys', 'Storage:': 'storage', 'StrongAuth:': 'strong',
                    'RebootEscrow:': 'escrow', 'LSSLog:': 'log'}
        if body in headings:
            self.part = headings[body]
        elif body.endswith(':'):
            self.part = ''
        else:
            self.part = 'oldusers' if body.startswith('SP Enabled') else 'top'
            name, value = body.split(' = ', 1) if ' = ' in body else split_pair(body)
            self._state('Service', None, name.strip(), value.strip(), line_no)

    def _storage(self, line_no, body):
        directory = _LOCK_DIR.match(body)
        if directory:
            self.location, self.directory = directory.group(1), directory.group(2)
            return
        match = _LOCK_FILE.match(body)
        if match and self.location:
            add(self.report, 'ss_lock_files', LockFile(self.location, cap(self.directory, 300), int(match.group(1)),
                                                     match.group(2), cap(match.group(3), 300), line_no))

    def _strong(self, line_no, indent, body):
        prefix = 'StrongAuth' if self.part == 'strong' else 'RebootEscrow'
        if indent == 2 and body.endswith(':'):
            self.group = prefix + ': ' + body[:-1]
            return
        group = self.group if self.group.startswith(prefix) else prefix
        user_match = re.match(r'^userId=(-?\d+),\s*(.*)$', body)
        if user_match:
            user = int(user_match.group(1))
            for key, value in key_values(user_match.group(2).replace(', ', ' ').replace(',', ' ')).items():
                self._state(group, user, key, value, line_no)
        else:
            name, value = split_pair(body)
            self._state(group, None, name, value, line_no)

    def finish(self):
        self._flush_user()
        self._flush_entry()


# ---------------------------------------------------------------------------------------------
# biometrics and trust
# ---------------------------------------------------------------------------------------------
BIO_COUNTERS = ('count', 'accept', 'reject', 'quality', 'acquire', 'lockout', 'permanentLockout', 'acceptCrypto',
                'rejectCrypto', 'qualityCrypto', 'acquireCrypto', 'lockoutCrypto', 'permanentLockoutCrypto')
_BIO_SENSOR = re.compile(r'^Dumping for sensorId: (-?\d+), provider: (.*)$')
_BIO_EVENT = re.compile(r'^#(\d+)\s+(.*)$')
_BIO_SENSOR_LINE = re.compile(
    r'^ID\((-?\d+)\), oemStrength: (-?\d+), updatedStrength: (-?\d+), modality (-?\d+), state: (-?\d+), cookie: (-?\d+)$')


class BiometricReader(SectionReader):
    """The ``fingerprint`` and ``face`` service dumps: the statistics JSON and the authentication session coordinator log."""
    kind = 'service'

    def __init__(self, report, section):
        SectionReader.__init__(self, report, section)
        self.sensor_id = None
        self.provider = ''
        self.stats = []
        self.hal_deaths = ''
        self.in_log = False

    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            return
        match = _BIO_SENSOR.match(body)
        if match:
            self.sensor_id, self.provider = int(match.group(1)), cap(match.group(2), 100)
        elif body.startswith('{"service":'):
            self._json(line_no, body)
        elif body.startswith(('HAL deaths since last reboot:', 'HAL Deaths:')):
            self.hal_deaths = body.split(':', 1)[1].strip()
        elif body.startswith('---AuthSessionCoordinator logs begin'):
            self.in_log = True
        elif self.in_log and body.startswith('---'):
            self.in_log = False
        elif self.in_log:
            event = _BIO_EVENT.match(body)
            if event:
                self._event(line_no, int(event.group(1)), event.group(2))

    def _json(self, line_no, body):
        try:
            data = json.loads(body)
            prints = data.get('prints', [])
            service = data.get('service', '')
        except (ValueError, AttributeError):
            self.report.warn('%s: a statistics line at line %d could not be read' % (self.name, line_no))
            return
        for item in prints if isinstance(prints, list) else []:
            if isinstance(item, dict):
                self.stats.append((cap(service, 100), item, line_no))

    def _event(self, line_no, sequence, rest):
        rest = rest.strip()
        internal = rest.startswith('internal :')
        clean = rest[len('internal :'):].strip() if internal else rest
        name, _, args = clean.partition('(')
        args = args.rsplit(')', 1)[0]
        fields = dict(re.findall(r'(\w+)=([^,\s)]+)', args))
        user = to_int(fields.get('userId'))
        if user is None and not fields and base.is_digits(args.strip()):
            user = int(args.strip())
        add(self.report, 'ss_bio_events', BioEvent(
            self.name, sequence, ('internal: ' if internal else '') + cap(name.strip(), 100), user, to_int(fields.get('sensorId')),
            to_int(fields.get('requestId')), to_int(fields.get('biometricStrength')),
            cap(fields.get('wasSuccessful', ''), 20), cap(rest, 300), line_no))

    def finish(self):
        for service, item, line_no in self.stats:
            counters = collections.OrderedDict((key, item[key]) for key in BIO_COUNTERS if key in item)
            extra = ['%s=%s' % (key, item[key]) for key in item if key != 'id' and key not in BIO_COUNTERS]
            if extra:
                counters['other'] = cap('; '.join(extra), 300)
            add(self.report, 'ss_bio_stats', BioStat(self.name, self.sensor_id, self.provider, service, to_int(item.get('id')),
                                                     counters, to_int(self.hal_deaths), line_no))


class FingerprintReader(BiometricReader):
    name = 'fingerprint'


class FaceReader(BiometricReader):
    name = 'face'


class BiometricSensorReader(SectionReader):
    """The ``Sensors:`` list of the biometric service dump."""
    kind = 'service'
    name = 'biometric'

    def feed(self, line_no, text):
        match = _BIO_SENSOR_LINE.match(text.strip())
        if match:
            add(self.report, 'ss_bio_sensors', BioSensor(*[int(value) for value in match.groups()], line_no))


_TRUST_USER = re.compile(r'^ *User "(.*)" \(id=(-?\d+), flags=(0x[0-9a-fA-F]+)\)(.*)$')
_TRUST_EVENT = re.compile(r'^\s*#(\d+)\s+(\d\d-\d\d \d\d:\d\d:\d\d(?:\.\d+)?)\s+([^:]+):\s*(.*)$')


class TrustReader(SectionReader):
    """The trust manager dump: each user's trust state, the trust agents and the event list."""
    kind = 'service'
    name = 'trust'

    def __init__(self, report, section):
        SectionReader.__init__(self, report, section)
        self.user = None
        self.agent = None
        self.part = ''

    def _flush(self):
        user, self.user = self.user, None
        self.agent = None
        if user is None:
            return
        values = user['values']
        head = (user['id'], user['name'], user['flags'], user['qualifiers'], cap(values.get('trustState', ''), 40),
                cap(values.get('trusted', ''), 40), cap(values.get('trustManaged', ''), 40), cap(values.get('deviceLocked', ''), 40),
                cap(values.get('isActiveUnlockRunning', ''), 40), cap(values.get('strongAuthRequired', ''), 40),
                user['note'])
        for agent in user['agents'] or [None]:
            if agent is None:
                add(self.report, 'ss_trust_agents', TrustAgent(*head, '', '', '', '', '', user['line']))
            else:
                add(self.report, 'ss_trust_agents', TrustAgent(
                    *head, agent['name'], agent.get('bound', ''), agent.get('connected', ''), agent.get('managingTrust', ''),
                    agent.get('trusted', ''), agent['line']))

    def feed(self, line_no, text):
        if not text.strip():
            return
        match = _TRUST_USER.match(text)
        if match:
            self._flush()
            head, _, tail = match.group(4).partition(':')
            values = {}
            for piece in tail.split(','):
                key, separator, value = piece.partition('=')
                if separator:
                    values[key.strip()] = value.strip()
            self.user = {'id': int(match.group(2)), 'name': cap(match.group(1), 200), 'flags': match.group(3),
                         'qualifiers': cap(', '.join(re.findall(r'\(([^)]*)\)', head)), 100), 'values': values,
                         'agents': [], 'note': '', 'line': line_no}
            self.part = ''
            return
        if self.user is None:
            return
        body = text.strip()
        if body == 'Enabled agents:':
            self.part = 'agents'
        elif body == 'Events:':
            self.part = 'events'
        elif self.part == 'events':
            event = _TRUST_EVENT.match(text)
            if event:
                add(self.report, 'ss_trust_events', TrustEvent(self.user['id'], self.user['name'], int(event.group(1)), event.group(2),
                                                              cap(event.group(3).strip(), 100), cap(event.group(4), 300), line_no))
        elif self.part == 'agents':
            if '=' not in body and '/' in body:
                self.agent = {'name': cap(body, 300), 'line': line_no}
                self.user['agents'].append(self.agent)
            elif self.agent is not None and '=' in body:
                for piece in body.split(','):
                    key, _, value = piece.partition('=')
                    self.agent[key.strip()] = value.strip()
        elif not self.user['note']:
            self.user['note'] = cap(body, 300)

    def finish(self):
        self._flush()


class AdbManagerReader(SectionReader):
    """The ADB manager state: nested ``name={`` blocks with ``key=value`` leaves, shown as ``path`` and ``value``."""
    kind = 'service'
    name = 'adb'

    def __init__(self, report, section):
        SectionReader.__init__(self, report, section)
        self.path = []

    def feed(self, line_no, text):
        body = text.strip().rstrip(',')
        if not body or body.startswith(('ADB MANAGER STATE', 'Service host process PID', 'Threads in use', 'Client PIDs')):
            return
        if body in ('{', '[', '{}', '[]'):
            return
        if body.startswith(('}', ']')):
            if self.path:
                self.path.pop()
            return
        if body.endswith(('={', '=[')):
            self.path.append(cap(body[:-2], 200))
            return
        name, separator, value = body.partition('=')
        if separator:
            add(self.report, 'ss_adb', AdbRow(cap('.'.join(self.path + [name.strip()]), 400), cap(value.strip()), line_no))


# ---------------------------------------------------------------------------------------------
# vendor security services
# ---------------------------------------------------------------------------------------------
_KNOX_EVENT = re.compile(r'^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) : \[([^\]]*)\] ?(.*)$')
# time : pid|tid : message, the message sometimes led by a [tag]; the message keeps the ids
_KNOX_THREAD_EVENT = re.compile(r'^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) : (\d+\|\d+ : (?:\[([^\]]*)\])?.*)$')


class KnoxGuardReader(SectionReader):
    """The ``knoxguard_service`` dump: a few state lines and the timestamped event lines."""
    kind = 'service'
    name = 'knoxguard_service'

    def feed(self, line_no, text):
        body = text.strip()
        if not body or body.startswith(('Service host process PID', 'Threads in use', 'Client PIDs', '*** SERVICE')):
            return
        event = _KNOX_EVENT.match(body)
        if event:
            add(self.report, 'ss_knox_log', KnoxLog('Log', event.group(1), cap(event.group(2), 200),
                                                   cap(event.group(3), 600), line_no))
            return
        event = _KNOX_THREAD_EVENT.match(body)
        if event:
            add(self.report, 'ss_knox_log', KnoxLog('Log', event.group(1), cap(event.group(3) or '', 200),
                                                   cap(event.group(2), 600), line_no))
        elif not body.endswith('state:'):
            add(self.report, 'ss_knox_log', KnoxLog('State', '', '', cap(body, 600), line_no))


class KnoxCustomReader(SectionReader):
    """The ``knoxcustom`` dump: ``Manager:Name: value`` lines."""
    kind = 'service'
    name = 'knoxcustom'

    def feed(self, line_no, text):
        body = text.strip()
        if not body or body.startswith(('Service host process PID', 'Threads in use', 'Client PIDs',
                                        'KnoxCustomManagerService state')):
            return
        manager, separator, rest = body.partition(':')
        if not separator:
            return
        rest = rest.strip()
        if ': ' in rest:
            name, value = rest.split(': ', 1)
        elif ' is ' in rest:
            name, value = rest.split(' is ', 1)
        elif ':' in rest:
            name, value = rest.split(':', 1)
        else:
            name, value = '', rest
        add(self.report, 'ss_knox_custom', KnoxCustom(cap(manager, 100), cap(name, 200), cap(value), cap(body, 600), line_no))


# ---------------------------------------------------------------------------------------------
# storage
# ---------------------------------------------------------------------------------------------
class DfReader(SectionReader):
    """``df`` (the free space of each file system)."""
    kind = 'command'
    name = 'FILESYSTEMS & FREE SPACE'
    table = 'ss_df'
    header = 'Filesystem'

    def __init__(self, report, section):
        SectionReader.__init__(self, report, section)
        self.unreadable = 0

    def feed(self, line_no, text):
        body = text.strip()
        if not body or body.startswith(self.header):
            return
        parts = body.split(None, 5)
        if len(parts) < 6:
            self.unreadable += 1
            return
        add(self.report, self.table, self.make(parts, line_no))

    @staticmethod
    def make(parts, line_no):
        return DfRow(cap(parts[0], 300), number(parts[1]), number(parts[2]), number(parts[3]), cap(parts[4], 20),
                     cap(parts[5], 400), line_no)

    def finish(self):
        if self.unreadable:
            self.report.warn('%s: %d lines did not have the six columns and were not read' % (self.name, self.unreadable))


class DfInodesReader(DfReader):
    """``df -i`` (the inode counts of each file system), kept as printed because a count can be larger than 2^63."""
    name = 'FILESYSTEMS & FREE INODE'
    table = 'ss_df_inodes'

    @staticmethod
    def make(parts, line_no):
        return InodeRow(cap(parts[0], 300), cap(parts[1], 40), cap(parts[2], 40), cap(parts[3], 40), cap(parts[4], 20),
                        cap(parts[5], 400), line_no)


_MOUNT_LINE = re.compile(r'^(.*?) on (.*) type (\S+) \((.*)\)$')


class MountPointReader(SectionReader):
    """``mount`` (one line per mount: device, mount point, file system type and options)."""
    kind = 'command'
    name = 'MOUNT POINT DUMP'

    def feed(self, line_no, text):
        match = _MOUNT_LINE.match(text.strip())
        if match:
            add(self.report, 'ss_mounts', MountRow(cap(match.group(1), 300), cap(match.group(2), 400), cap(match.group(3), 50),
                                                  cap(match.group(4), 1000), line_no))


STORAGE_VOLUME_KEYS = r'm[A-Z][A-Za-z]*'
_VOLD_LINE = re.compile(r'^(\d{4}/\d\d/\d\d-\d\d:\d\d:\d\d\((?:GMT|UTC)\))\s+(\d+):(\d+)\s+(\S+)\s?(.*)$')
_VOLUME_INFO = re.compile(r'^VolumeInfo\{(.*)\}:?$')
_DISK_INFO = re.compile(r'^DiskInfo\{(.*)\}:?$')
VOLUME_SCALARS = ('Primary storage UUID', 'Internal storage', 'CE unlocked users', 'System unlocked users',
                  'Sharing media with parent', 'User pairs for sharing media')


class MountServiceReader(SectionReader):
    """The ``mount`` service dump: storage volumes, volumes, disks, the scalar lines and the vold log."""
    kind = 'service'
    name = 'mount'
    PARTS = {'StorageVolumes:': 'storage', 'Volumes:': 'volumes', 'Disks:': 'disks', 'Records:': 'records'}

    def __init__(self, report, section):
        SectionReader.__init__(self, report, section)
        self.part = ''
        self.current = None
        self.buffer = ''

    def _flush(self):
        item, self.current = self.current, None
        if item is None:
            return
        values = item['values']
        used = set()

        def pick(*keys):
            for key in keys:
                if key in values:
                    used.add(key)
                    return cap(values[key], 400)
            return ''
        row = Volume(item['kind'], cap(item['id'] or pick('mId'), 200), pick('mState', 'state'), pick('mPath', 'path'),
                     pick('mInternalPath', 'internalPath'), pick('mDescription'), pick('mPrimary'), pick('mRemovable'),
                     pick('mEmulated'), pick('mountFlags'), pick('mountUserId'), pick('diskId'), pick('fsType'),
                     pick('mFsUuid', 'fsUuid'), pick('fsLabel'), pick('type'), '', item['line'])
        other = '; '.join('%s=%s' % (key, value) for key, value in values.items() if key not in used)
        add(self.report, 'ss_volumes', row._replace(other=cap(other, 600)))

    def feed(self, line_no, text):
        body = text.strip()
        if not body or body.startswith(('Service host process PID', 'Threads in use', 'Client PIDs')):
            return
        if self.part == 'vold':
            match = _VOLD_LINE.match(body)
            if match:
                add(self.report, 'ss_vold', VoldLog(match.group(1), int(match.group(2)), int(match.group(3)), cap(match.group(4), 100),
                                                    cap(match.group(5), 600), self.buffer, line_no))
            else:
                add(self.report, 'ss_vold', VoldLog('', None, None, '', cap(body, 600), self.buffer, line_no))
            return
        if indent_of(text) == 0:
            self._flush()
            if body in self.PARTS:
                self.part = self.PARTS[body]
            elif body.startswith('VOLD LAST LOG BUF'):
                self.part = 'vold'
                self.buffer = cap(body[len('VOLD LAST LOG '):], 40)
            else:
                self._scalar(line_no, body)
            return
        self._volume_line(line_no, body)

    def _scalar(self, line_no, body):
        if body.startswith(VOLUME_SCALARS):
            name, value = split_pair(body.replace(' :', ':', 1))
            add(self.report, 'ss_disk_items', DiskItem('mount', cap(name, 200), cap(value), line_no))

    def _volume_line(self, line_no, body):
        if self.part == 'storage':
            if body == 'StorageVolume:':
                self._flush()
                self.current = {'kind': 'Storage volume', 'id': '', 'values': collections.OrderedDict(), 'line': line_no}
            elif self.current is not None and '=' in body:
                for key, value in keyed_split(body, STORAGE_VOLUME_KEYS).items():
                    self.current['values'].setdefault(key, value)
        elif self.part in ('volumes', 'disks'):
            kind, pattern = ('Volume', _VOLUME_INFO) if self.part == 'volumes' else ('Disk', _DISK_INFO)
            match = pattern.match(body)
            if match:
                self._flush()
                self.current = {'kind': kind, 'id': match.group(1), 'values': collections.OrderedDict(), 'line': line_no}
            elif self.current is not None and '=' in body:
                for key, value in key_values(body).items():
                    self.current['values'].setdefault(key, value)

    def finish(self):
        self._flush()


_IO_HISTORY = re.compile(r'^(last [^:]*?)\s*:\s*(\d[\d ]*)$')


class StoragedIoReader(SectionReader):
    """``storaged -u -p`` (the counters of each uid, with the column names the section prints)."""
    kind = 'command'
    name = 'STORAGED IO INFO'
    columns = 10

    def feed(self, line_no, text):
        body = text.strip()
        if not body or body.startswith('name/uid'):
            return
        history = _IO_HISTORY.match(body)
        if history:
            add(self.report, 'ss_disk_items', DiskItem('storaged -u -p', 'I/O perf history (KB/s, most recent first): ' + history.group(1).strip(),
                                                       cap(history.group(2).strip()), line_no))
            return
        parts = body.rsplit(None, self.columns)
        if len(parts) != self.columns + 1 or not all(base.is_digits(value) for value in parts[1:]):
            return
        add(self.report, 'ss_storage_io', StorageIo(cap(parts[0], 300), tuple(number(value) for value in parts[1:]), line_no))


def parse_array(text):
    """The items of a printed list such as ``["a","b"]`` or ``[1,2,3]``; a list that is cut gives its complete items.

    Returns ``(items, complete)``.
    """
    body = text.strip()
    try:
        data = json.loads(body)
        if isinstance(data, list):
            return data, True
    except ValueError:
        pass
    inner = body[1:] if body.startswith('[') else body
    if inner.startswith('"'):
        return [match.group(1) for match in re.finditer(r'"((?:[^"\\]|\\.)*)"', inner)], False
    pieces = inner.rstrip(']').split(',')[:-1]
    return [to_int(piece) for piece in pieces if piece.strip()], False


class DiskStatsReader(SectionReader):
    """The ``diskstats`` dump: free space lines, size totals, and the per-package size lists."""
    kind = 'service'
    name = 'diskstats'
    ARRAYS = ('Package Names', 'App Sizes', 'App Data Sizes', 'Cache Sizes')

    def __init__(self, report, section):
        SectionReader.__init__(self, report, section)
        self.arrays = {}
        self.array_lines = {}
        self.cut = []

    def feed(self, line_no, text):
        body = text.strip()
        if not body or body.startswith(('Service host process PID', 'Threads in use', 'Client PIDs')):
            return
        name, value = split_pair(body)
        if name in self.ARRAYS and value.strip().startswith('['):
            items, complete = parse_array(value)
            self.arrays[name] = items
            self.array_lines[name] = line_no
            if not complete:
                self.cut.append(name)
            return
        add(self.report, 'ss_disk_items', DiskItem('diskstats', cap(name, 200), cap(value), line_no))

    def finish(self):
        names = self.arrays.get('Package Names')
        if names is None:
            return
        if self.cut:
            self.report.warn('diskstats: the list(s) %s could not be read in full, only the complete items were kept'
                             % ', '.join(self.cut))
        sizes = [self.arrays.get(key) for key in ('App Sizes', 'App Data Sizes', 'Cache Sizes')]
        lengths = {len(names)} | {len(item) for item in sizes if item is not None}
        if len(lengths) > 1:
            self.report.warn('diskstats: the package and size lists have different lengths (%s), the shortest was used'
                             % ', '.join(str(size) for size in sorted(lengths)))
        for index in range(min(lengths)):
            add(self.report, 'ss_package_sizes', PackageSize(
                index, cap(names[index], 300), *[number(item[index]) if item is not None else '' for item in sizes],
                self.array_lines['Package Names']))


# ---------------------------------------------------------------------------------------------
# the database connection pools (dbinfo)
# ---------------------------------------------------------------------------------------------
_DB_PROCESS = re.compile(r'^\*\* Database info for pid (\d+) \[(.*)\] \*\*$')
_DB_POOL = re.compile(r'^Connection pool for (.*):$')
_DB_FILES = re.compile(r'^Database files in (.*):$')
_DB_FILE = re.compile(r'^(.+?)\s+(\d+)b ctime=(\S+) mtime=(\S+) atime=(\S+)$')
_DB_OP = re.compile(r'^(\d+): \[([^\]]+)\] (?:\[Pid:\((\d+)\)\])?(.*)$')
_DB_BODY = re.compile(r'^(\S+) took (-?\d+)ms - (\w+)(.*)$')
_DB_CONNECTION = re.compile(r'^Connection #(\d+):$')


class DbInfoReader(SectionReader):
    """The ``dbinfo`` dump: connection pools, the database file listings and the recently executed operations."""
    kind = 'service'
    name = 'dbinfo'

    def __init__(self, report, section):
        SectionReader.__init__(self, report, section)
        self.pid = None
        self.process = ''
        self.pool = None
        self.directory = None
        self.connection = None
        self.listing = ''

    def _flush_pool(self):
        pool, self.pool = self.pool, None
        self.listing = ''
        if pool is None:
            return
        values = pool['values']
        spent = values.pop('Total execution time (ms)', None)
        spent = values.pop('Total execution time', '') if spent is None else spent
        add(self.report, 'ss_db_pools', DbPool(
            pool['pid'], pool['process'], pool['path'], values.pop('Open', ''), to_int(values.pop('Max connections', None)),
            number(spent), number(values.pop('Total statements executed', '')),
            number(values.pop('Average time per statement (ms)', '')), cap(values.pop('Configuration', ''), 400),
            values.pop('IsReadOnlyDatabase', ''), values.pop('Secure db', ''), 'yes' if pool['wal'] else '',
            pool['connections'], pool['operations'],
            cap('; '.join('%s: %s' % (key, value) for key, value in values.items()), 500), pool['line']))

    def feed(self, line_no, text):
        body = text.strip()
        if not body:
            return
        indent = indent_of(text)
        if indent == 0:
            self._heading(line_no, body)
            return
        if self.directory is not None:
            match = _DB_FILE.match(body)
            if match:
                add(self.report, 'ss_db_files', DbFile(self.pid, self.process, self.directory, cap(match.group(1), 300),
                                                     int(match.group(2)), match.group(3), match.group(4), match.group(5), line_no))
            return
        if self.pool is None:
            return
        if indent == 2:
            self.listing = ''
            if body == 'Use WAL mode.':
                self.pool['wal'] = True
            elif not body.startswith(('Available', 'Acquired', 'Connection waiters', '/')):
                name, value = split_pair(body)
                self.pool['values'].setdefault(name, value)
            return
        connection = _DB_CONNECTION.match(body)
        if connection:
            self.connection = int(connection.group(1))
            self.pool['connections'] += 1
            self.listing = ''
        elif body.startswith(('Most recently executed operations', 'Operations exceeding')):
            self.listing = cap(body.rstrip(':'), 100)
        elif self.listing:
            self._operation(line_no, body)

    def _heading(self, line_no, body):
        self._flush_pool()
        self.directory = None
        match = _DB_PROCESS.match(body)
        if match:
            self.pid, self.process = int(match.group(1)), cap(match.group(2), 300)
            return
        match = _DB_POOL.match(body)
        if match:
            self.pool = {'pid': self.pid, 'process': self.process, 'path': cap(match.group(1), 500),
                         'values': collections.OrderedDict(), 'connections': 0, 'operations': 0, 'wal': False, 'line': line_no}
            return
        match = _DB_FILES.match(body)
        if match:
            self.directory = cap(match.group(1), 500)

    def _operation(self, line_no, body):
        match = _DB_OP.match(body)
        if not match:
            return
        self.pool['operations'] += 1
        pid = to_int(match.group(3)) if match.group(3) else self.pid
        parsed = _DB_BODY.match(match.group(4))
        if parsed is None:
            add(self.report, 'ss_db_ops', DbOp(pid, self.process, self.pool['path'], self.connection, self.listing,
                                               int(match.group(1)), match.group(2), '', None, '', '', 0,
                                               cap(match.group(4), 500), line_no))
            return
        tail = parsed.group(4)
        sql, details = '', tail
        at = tail.find(', sql="')
        if at >= 0:
            start = at + len(', sql="')
            end = tail.rfind('", path=')
            if end < start:
                end = tail.rfind('"')
            if end < start:
                end = len(tail)
            sql = tail[start:end]
            details = tail[end + 1:] if end < len(tail) else ''
        add(self.report, 'ss_db_ops', DbOp(pid, self.process, self.pool['path'], self.connection, self.listing,
                                           int(match.group(1)), match.group(2), cap(parsed.group(1), 100), int(parsed.group(2)),
                                           cap(parsed.group(3), 40), cap(sql, SQL_CAP), len(sql), cap(details.strip(' ,'), 500), line_no))

    def finish(self):
        self._flush_pool()


# ---------------------------------------------------------------------------------------------
# configuration and build flags
# ---------------------------------------------------------------------------------------------
_CONFIG_LINE = re.compile(r'^([A-Za-z0-9_\-]+)/([^=\s]+)=(.*)$')


class DeviceConfigReader(SectionReader):
    """The ``device_config`` dump: one ``namespace/flag=value`` line for each flag (a value can continue on the next lines)."""
    kind = 'service'
    name = 'device_config'

    def __init__(self, report, section):
        SectionReader.__init__(self, report, section)
        self.current = None

    def _flush(self):
        item, self.current = self.current, None
        if item is not None:
            add(self.report, 'ss_device_config', ConfigFlag(cap(item[0], 200), cap(item[1], 300), cap(' '.join(item[2]), 1000), item[3]))

    def feed(self, line_no, text):
        body = text.strip()
        if not body or body.startswith(('Service host process PID', 'Threads in use', 'Client PIDs', 'DeviceConfig flags')):
            return
        match = _CONFIG_LINE.match(body)
        if match:
            self._flush()
            self.current = (match.group(1), match.group(2), [match.group(3)], line_no)
        elif self.current is not None and len(self.current[2]) < 2000:
            self.current[2].append(body)

    def finish(self):
        self._flush()


_COMPAT = re.compile(r'^ChangeId\((-?\d+)(.*)\)$')


class PlatformCompatReader(SectionReader):
    """The ``platform_compat`` dump: one ``ChangeId(id; name=...; flags)`` line for each compatibility change."""
    kind = 'service'
    name = 'platform_compat'

    def feed(self, line_no, text):
        match = _COMPAT.match(text.strip())
        if not match:
            return
        name, since, after, other = '', '', '', []
        flags = {'disabled': '', 'loggingOnly': '', 'overridable': ''}
        for piece in match.group(2).split(';'):
            piece = piece.strip()
            if not piece:
                continue
            if piece.startswith('name='):
                name = piece[5:]
            elif piece.startswith('enableSinceTargetSdk='):
                since = piece.split('=', 1)[1]
            elif piece.startswith('enableAfterTargetSdk='):
                after = piece.split('=', 1)[1]
            elif piece in flags:
                flags[piece] = 'yes'
            else:
                other.append(piece)
        add(self.report, 'ss_compat', CompatChange(int(match.group(1)), cap(name, 200), number(since), number(after),
                                                  flags['disabled'], flags['loggingOnly'], flags['overridable'],
                                                  cap('; '.join(other), 300), line_no))


def value_pair(value):
    """``(type, value)`` of an aconfig ``{"Val": {"BoolValue": true}}`` value."""
    if isinstance(value, dict):
        inner = value.get('Val', value)
        if isinstance(inner, dict) and inner:
            kind, item = next(iter(inner.items()))
            return cap(kind, 40), cap(item if isinstance(item, str) else json.dumps(item), 500)
    return '', ''


class ReleaseFlagsReader(SectionReader):
    """A ``BUILD-TIME RELEASE FLAGS`` section (the ``build_flags.json`` text of one partition)."""
    kind = 'command'
    name = 'SYSTEM BUILD-TIME RELEASE FLAGS'
    partition = 'system'

    def __init__(self, report, section):
        SectionReader.__init__(self, report, section)
        self.lines = []
        self.dropped = False

    def feed(self, line_no, text):
        if len(self.lines) >= MAX_JSON_LINES:
            self.dropped = True
            return
        self.lines.append(text)

    def finish(self):
        text = '\n'.join(self.lines).strip()
        self.lines = []
        if not text:
            return
        if self.dropped:
            self.report.warn('%s: more than %d lines, the text was not read' % (self.name, MAX_JSON_LINES))
            return
        try:
            data = json.loads(text)
        except ValueError:
            self.report.warn('%s: the text is not complete JSON and was not read' % self.name)
            return
        items = data.get('flags', data.get('flag_artifacts', [])) if isinstance(data, dict) else []
        for item in items if isinstance(items, list) else []:
            if not isinstance(item, dict) or not isinstance(item.get('flag_declaration'), dict):
                continue
            declaration = item['flag_declaration']
            declared_type, declared_value = value_pair(declaration.get('value'))
            value_type, value = value_pair(item.get('value'))
            containers = declaration.get('containers')
            workflow = declaration.get('workflow')
            add(self.report, 'ss_release_flags', ReleaseFlag(
                self.partition, cap(declaration.get('name', ''), 200), cap(declaration.get('namespace', ''), 200),
                cap(declaration.get('description', ''), 500), declared_type, declared_value, value_type, value,
                workflow if isinstance(workflow, int) else '',
                cap(', '.join(str(entry) for entry in containers) if isinstance(containers, list) else '', 200)))


class SystemReleaseFlagsReader(ReleaseFlagsReader):
    name = 'SYSTEM BUILD-TIME RELEASE FLAGS'
    partition = 'system'


class SystemExtReleaseFlagsReader(ReleaseFlagsReader):
    name = 'SYSTEM_EXT BUILD-TIME RELEASE FLAGS'
    partition = 'system_ext'


class ProductReleaseFlagsReader(ReleaseFlagsReader):
    name = 'PRODUCT BUILD-TIME RELEASE FLAGS'
    partition = 'product'


class VendorReleaseFlagsReader(ReleaseFlagsReader):
    name = 'VENDOR BUILD-TIME RELEASE FLAGS'
    partition = 'vendor'


class SdkExtensionsReader(SectionReader):
    """``derive_sdk --dump``: the extension version properties, the module versions and the version requirements."""
    kind = 'command'
    name = 'SDK EXTENSIONS'

    def __init__(self, report, section):
        SectionReader.__init__(self, report, section)
        self.group = ''

    def feed(self, line_no, text):
        body = text.strip()
        if not body or body.startswith('***'):
            return
        if indent_of(text) == 0:
            self.group = body.rstrip(':')
            return
        name, separator, value = body.partition(':')
        if separator and self.group:
            add(self.report, 'ss_sdk', SdkRow(cap(self.group, 100), cap(name, 200), cap(value.strip(), 500), line_no))


# Registered by dumpstate_reader.py in READERS.
SECURITY_STORAGE_READERS = [
    DevicePolicyReader, LockSettingsReader, FingerprintReader, FaceReader, BiometricSensorReader, TrustReader,
    AdbManagerReader, KnoxGuardReader, KnoxCustomReader, DfReader, DfInodesReader, MountPointReader, MountServiceReader,
    StoragedIoReader, DiskStatsReader, DbInfoReader, DeviceConfigReader, PlatformCompatReader,
    SystemReleaseFlagsReader, SystemExtReleaseFlagsReader, ProductReleaseFlagsReader, VendorReleaseFlagsReader,
    SdkExtensionsReader]

# Which artifacts present each section, for the section index.
SECURITY_STORAGE_READ_BY = {
    ('service', 'device_policy'): 'Device Policy Admins; Device Policy State; Device Policies',
    ('service', 'lock_settings'): 'Lock Settings Users; Lock Settings Files; Lock Settings State; Lock Settings Log',
    ('service', 'fingerprint'): 'Biometric Statistics; Biometric Authentication Events',
    ('service', 'face'): 'Biometric Statistics; Biometric Authentication Events',
    ('service', 'biometric'): 'Biometric Sensors',
    ('service', 'trust'): 'Trust Agents; Trust Events',
    ('service', 'adb'): 'ADB Manager State',
    ('service', 'knoxguard_service'): 'knoxguard_service Log',
    ('service', 'knoxcustom'): 'knoxcustom State',
    ('command', 'FILESYSTEMS & FREE SPACE'): 'File Systems',
    ('command', 'FILESYSTEMS & FREE INODE'): 'File System Inodes',
    ('command', 'MOUNT POINT DUMP'): 'Mount Points',
    ('service', 'mount'): 'Storage Volumes; Vold Log; Disk Statistics',
    ('command', 'STORAGED IO INFO'): 'Storage IO Counters; Disk Statistics',
    ('service', 'diskstats'): 'Disk Statistics; Package Sizes',
    ('service', 'dbinfo'): 'Open Databases; Database Files; Database Operations',
    ('service', 'device_config'): 'Device Config Flags',
    ('service', 'platform_compat'): 'Platform Compat Changes',
    ('command', 'SYSTEM BUILD-TIME RELEASE FLAGS'): 'Build Release Flags',
    ('command', 'SYSTEM_EXT BUILD-TIME RELEASE FLAGS'): 'Build Release Flags',
    ('command', 'PRODUCT BUILD-TIME RELEASE FLAGS'): 'Build Release Flags',
    ('command', 'VENDOR BUILD-TIME RELEASE FLAGS'): 'Build Release Flags',
    ('command', 'SDK EXTENSIONS'): 'SDK Extensions',
}


def register():
    """Add the readers and the section index entries to the pass of ``dumpstate_reader`` (once, in any import order)."""
    for reader_class in SECURITY_STORAGE_READERS:
        if reader_class not in base.READERS:
            base.READERS.append(reader_class)
    for key, value in SECURITY_STORAGE_READ_BY.items():
        base.READ_BY.setdefault(key, value)


register()
