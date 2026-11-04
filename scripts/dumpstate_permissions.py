"""Readers for the permission parts of an Android bug report text (the dumpstate file).

These readers plug into the single pass of ``scripts/dumpstate_reader.py``: each one is
handed the lines of one dumpsys service section while that section is read, keeps bounded
rows on the report object and never touches the file itself. Nothing is decoded or judged:
modes, states, flags and times are kept as the dump printed them.

Sections and the parts of them that are read:

* ``package``: the permission lines of each package, hidden system package and shared user
  (``install permissions:`` and, per user, ``runtime permissions:``), and the ``Permissions:``
  table of permission definitions. The rest of the package dump belongs to other readers.
* ``appops``: per uid the uid-level modes (``OP: mode=X``), and per package each op line
  (``OP (mode):``) with the Access and Reject lines printed under it. The watcher lists, the
  restrictions and the uid state event log are not read.
* ``role``: the roles of each user and their holders.
* ``permissionmgr``: the ``App ID`` / ``User`` / ``Permissions:`` grant lines. The permission,
  group and tree lists that the same dump starts with are not read.

This module does not import ``dumpstate_reader`` (that module imports this one to register the
readers), so the few helpers it needs are written out here.
"""
import collections
import re

# Characters that cannot be shown in a report: NUL and other control characters become a space.
_CONTROL = re.compile('[\x00-\x08\x0b-\x1f\x7f]')

# Longest text kept for a name or a free text value.
NAME_CHARS = 300
FLAGS_CHARS = 1000
OPS_CHARS = 8000
# Uid-level mode lines kept for one uid (a real uid has about 40); the rest are counted as unread.
MAX_UID_MODES = 5000

PackagePermission = collections.namedtuple(
    'PackagePermission', 'holder_type holder app_id kind user permission granted flags line')
PermissionDefinition = collections.namedtuple(
    'PermissionDefinition', 'permission source_package uid gids perm_type protection flags line')
AppOpMode = collections.namedtuple(
    'AppOpMode', 'scope uid package mode op_count ops switch uid_state capability line')
AppOpAccess = collections.namedtuple(
    'AppOpAccess', 'kind uid package op op_mode tag uid_state op_flags time_text offset duration_text duration_ms '
                   'proxy_uid proxy_package proxy_tag running_start start_nesting line')
RoleHolder = collections.namedtuple('RoleHolder', 'user role holders fallback line')
PermissionGrant = collections.namedtuple('PermissionGrant', 'app_id user permission granted flags line')

# The names of the tables on the report object (set on first use, the shared Report class does not know them).
TABLES = ('package_permissions', 'permission_definitions', 'appop_modes', 'appop_accesses', 'role_holders',
          'permission_grants')


def tidy(value):
    """A text value with control characters shown as a space."""
    if value is None:
        return ''
    return _CONTROL.sub(' ', str(value))


def cut(value, limit=NAME_CHARS):
    """A tidy text cut to ``limit`` characters."""
    return tidy(value)[:limit]


def to_int(text):
    """Integer value of a printed decimal number, or None."""
    value = str(text).strip().rstrip(',')
    if value.isascii() and value.lstrip('-').isdigit():
        return int(value)
    return None


def table(report, name):
    """The list that holds the rows of ``name`` on the report (created on first use)."""
    if not hasattr(report, name):
        setattr(report, name, [])
    return getattr(report, name)


def rows_of(report, name):
    """The rows of ``name`` a report holds (none when no reader of this module ran on it)."""
    return getattr(report, name, [])


class PermissionReader:
    """Same contract as the readers of ``dumpstate_reader.SectionReader``: ``kind``, ``name``, ``feed``, ``finish``."""
    kind = 'service'
    name = ''
    tables = ()

    def __init__(self, report, section):
        self.report = report
        self.section = section
        for name in self.tables:
            table(report, name)

    def feed(self, line_no, text):
        """One line of the section body (the header line is not included)."""

    def finish(self):
        """The section ended."""


def indent_of(text):
    return len(text) - len(text.lstrip(' '))


# ---------------------------------------------------------------------------------------------
# package: permission lines of packages and shared users, and the permission definitions
# ---------------------------------------------------------------------------------------------
_GRANTED = re.compile(r'granted=([^,\s]*)')
_FLAGS = re.compile(r'flags=\[(.*?)\]')
_USER_ID = re.compile(r'userId=(-?\d+)')
_DEFINITION = re.compile(r'uid=(\S+)\s+gids=(\[.*?\]|\S+)\s+type=(\S+)\s+prot=(.*)$')

BLOCK_HOLDERS = {'Packages': 'Package', 'Hidden system packages': 'Hidden system package', 'Shared users': 'Shared user'}


def parse_permission_line(body):
    """``(permission, granted, flags, user id)`` of ``name: granted=true, flags=[ A|B], userId=11``, or None."""
    name, separator, rest = body.partition(': granted=')
    if not separator or not name or ' ' in name:
        return None
    granted = _GRANTED.match('granted=' + rest)
    flags = _FLAGS.search(rest)
    user_id = _USER_ID.search(rest)
    return (name, granted.group(1) if granted else '', flags.group(1).strip() if flags else '',
            int(user_id.group(1)) if user_id else None)


class PackagePermissionsReader(PermissionReader):
    """``dumpsys package``: install and runtime permission lines of each holder, and the Permissions table."""
    name = 'package'
    tables = ('package_permissions', 'permission_definitions')

    def __init__(self, report, section):
        PermissionReader.__init__(self, report, section)
        self.block = ''
        self.holder = ''
        self.holder_type = ''
        self.app_id = None
        self.mode = ''            # install, runtime or ''
        self.user = None
        self.definition = None

    def _close_definition(self):
        item = self.definition
        self.definition = None
        if item is not None:
            self.report.add('permission_definitions', PermissionDefinition(
                item['permission'], item['source'], item['uid'], item['gids'], item['type'], item['prot'],
                item['flags'], item['line']))

    def feed(self, line_no, text):
        if not text.strip():
            return
        indent = indent_of(text)
        body = text.strip()
        if indent == 0:
            self._close_definition()
            self.mode = ''
            if text.startswith('***') or not text.rstrip().endswith(':'):
                return          # a heading ends with a colon; another line at column 0 is not one
            self.block = text.rstrip().rstrip(':')
            self.holder = ''
            self.user = None
            return
        if self.block == 'Permissions':
            self._definition_line(indent, body, line_no)
            return
        if self.block not in BLOCK_HOLDERS:
            return
        if indent == 2:
            self.mode = ''
            self.user = None
            if body.startswith(('Package [', 'SharedUser [')) and ']' in body:
                self.holder = cut(body[body.find('[') + 1:body.find(']')])
                self.holder_type = BLOCK_HOLDERS[self.block]
                self.app_id = None
            else:
                self.holder = ''
            return
        if not self.holder:
            return
        if indent == 4:
            self.mode = ''
            if body == 'install permissions:':
                self.mode = 'install'
                self.user = None
            elif body.startswith('User ') and ':' in body:
                self.user = to_int(body[5:body.find(':')])
            elif body.startswith(('appId=', 'userId=')) and self.app_id is None:
                self.app_id = to_int(body.split('=', 1)[1])
            return
        if indent == 6:
            if self.mode == 'install':
                self._permission(body, line_no, 'install')
            elif body == 'runtime permissions:' and self.user is not None:
                self.mode = 'runtime'
            elif self.mode == 'runtime':
                self.mode = ''
            return
        if indent == 8 and self.mode == 'runtime':
            self._permission(body, line_no, 'runtime')

    def _permission(self, body, line_no, kind):
        found = parse_permission_line(body)
        if found is None:
            return
        permission, granted, flags, user_id = found
        user = self.user if kind == 'runtime' else user_id
        self.report.add('package_permissions', PackagePermission(
            self.holder_type, self.holder, self.app_id, kind, user, cut(permission), cut(granted, 40),
            cut(flags, FLAGS_CHARS), line_no))

    def _definition_line(self, indent, body, line_no):
        if indent == 2:
            self._close_definition()
            if body.startswith('Permission [') and ']' in body:
                self.definition = {'permission': cut(body[len('Permission ['):body.find(']')]), 'source': '', 'uid': '',
                                   'gids': '', 'type': '', 'prot': '', 'flags': '', 'line': line_no}
            return
        item = self.definition
        if item is None or indent != 4:
            return
        if body.startswith('sourcePackage='):
            item['source'] = cut(body.split('=', 1)[1])
        elif body.startswith('uid='):
            found = _DEFINITION.match(body)
            if found:
                item['uid'], item['gids'], item['type'], item['prot'] = (
                    cut(found.group(1), 40), cut(found.group(2), 200), cut(found.group(3), 40), cut(found.group(4), 400))
        elif body.startswith('flags='):
            item['flags'] = cut(body.split('=', 1)[1], 100)

    def finish(self):
        self._close_definition()


# ---------------------------------------------------------------------------------------------
# appops: uid modes, package op modes and the access lines under them
# ---------------------------------------------------------------------------------------------
_UID_HEADING = re.compile(r'^Uid (\S+):$')
_UID_APP = re.compile(r'^u(\d+)a(\d+)$')
_UID_SYSTEM = re.compile(r'^u(\d+)s(\d+)$')
_UID_MODE = re.compile(r'^([A-Za-z0-9_]+): mode=(\S+)$')
_PACKAGE_OP = re.compile(r'^([A-Za-z0-9_]+) \(([^)]*)\):\s*$')
_ACCESS = re.compile(r'^(Access|Reject): \[([^\]]*)\]\s*(\d{4}-\d\d-\d\d[ T]\d\d:\d\d:\d\d(?:\.\d+)?)?\s*(?:\(([^)]*)\))?(.*)$')
_DURATION = re.compile(r'duration=(\S+)')
_PROXY = re.compile(r'proxy\[uid=(\S*?), pkg=(.*?), attributionTag=(.*?)\]')
_DURATION_PART = re.compile(r'(\d+)(ms|d|h|m|s)')
_DURATION_UNITS_MS = {'d': 86400000, 'h': 3600000, 'm': 60000, 's': 1000, 'ms': 1}


def uid_number(text):
    """The numeric uid for a printed ``Uid`` heading, or None.

    A number is kept. ``u<user>a<n>`` is user * 100000 + 10000 + n and ``u<user>s<n>`` is user * 100000 + n (the two
    shapes the dump prints for application and system uids of any user). The isolated shapes (``u0i1``,
    ``u0ai9000``) and anything else give None.
    """
    value = str(text).strip()
    if value.isascii() and value.isdigit():
        return int(value)
    found = _UID_APP.match(value)
    if found:
        return int(found.group(1)) * 100000 + 10000 + int(found.group(2))
    found = _UID_SYSTEM.match(value)
    if found:
        return int(found.group(1)) * 100000 + int(found.group(2))
    return None


def duration_ms(text):
    """Milliseconds of a printed duration such as ``+1h51m17s15ms`` (a sign is accepted), or None when it is another shape."""
    value = str(text).strip()
    sign = 1
    if value[:1] in '+-' and value:
        sign = -1 if value[0] == '-' else 1
        value = value[1:]
    parts = _DURATION_PART.findall(value)
    if not parts or ''.join(number + unit for number, unit in parts) != value:
        return None
    return sign * sum(int(number) * _DURATION_UNITS_MS[unit] for number, unit in parts)


class AppOpsReader(PermissionReader):
    """``dumpsys appops``: ``Uid N:`` blocks with their uid modes, packages, ops and Access / Reject lines."""
    name = 'appops'
    tables = ('appop_modes', 'appop_accesses')

    def __init__(self, report, section):
        PermissionReader.__init__(self, report, section)
        self.uid = None
        self.uid_line = 0
        self.uid_state = ''
        self.capability = ''
        self.uid_modes = []       # (op, mode) in the order printed
        self.package = ''
        self.op = ''
        self.op_mode = ''
        self.tag = ''
        self.last_running = None
        self.unread = 0

    def _flush_uid(self):
        """One row for each mode value of the uid-level modes, with the ops in the order printed."""
        if self.uid is None or not self.uid_modes:
            self.uid_modes = []
            return
        groups = collections.OrderedDict()
        for op, mode in self.uid_modes:
            groups.setdefault(mode, []).append(op)
        for mode, ops in groups.items():
            self.report.add('appop_modes', AppOpMode(
                'Uid', self.uid, '', cut(mode, 60), len(ops), cut(', '.join(ops), OPS_CHARS), '', self.uid_state,
                self.capability, self.uid_line))
        self.uid_modes = []

    def _reset_package(self):
        self.package = ''
        self.op = ''
        self.op_mode = ''
        self.tag = ''
        self.last_running = None

    def feed(self, line_no, text):
        if not text.strip():
            return
        indent = indent_of(text)
        body = text.strip()
        if indent <= 2:
            self._reset_package()
            found = _UID_HEADING.match(body) if indent == 2 else None
            self._flush_uid()
            if found:
                self.uid = cut(found.group(1), 60)
                self.uid_line = line_no
                self.uid_state = ''
                self.capability = ''
            else:
                self.uid = None     # another heading: the watcher lists, the restrictions, the event log
            return
        if self.uid is None:
            return
        if indent == 4:
            self._reset_package()
            if body.startswith('Package ') and body.endswith(':'):
                self._flush_uid()       # the uid-level modes are printed before the packages of the uid
                self.package = cut(body[len('Package '):-1])
            elif body.startswith('state='):
                self.uid_state = cut(body[len('state='):], 60)
            elif body.startswith('capability='):
                self.capability = cut(body[len('capability='):], 60)
            return
        if indent == 6:
            self._op_line(body, line_no)
            return
        if not self.package:
            return
        if body.endswith('=[') and indent == 8:
            self.tag = cut(body[:-2], 200)
        elif body == ']' and indent == 8:
            self.tag = ''
        elif body.startswith(('Access:', 'Reject:')):
            self._access_line(body, line_no)
        elif body.startswith('Running start at: '):
            self._running_line(body, line_no)
        elif body.startswith('startNesting=') and self.last_running is not None:
            self._nesting(body)

    def _op_line(self, body, line_no):
        found = _UID_MODE.match(body)
        if found:
            if self.package:
                self.unread += 1        # a uid-level mode line printed after a package heading of the uid
            elif len(self.uid_modes) < MAX_UID_MODES:
                self.uid_modes.append((found.group(1), found.group(2)))
            else:
                self.unread += 1
            return
        found = _PACKAGE_OP.match(body)
        if not found or not self.package:
            return
        self.op = found.group(1)
        self.tag = ''
        self.last_running = None
        mode, _separator, switch = found.group(2).partition(' / switch ')
        self.op_mode = cut(mode, 60)
        self.report.add('appop_modes', AppOpMode(
            'Package', self.uid, self.package, self.op_mode, 1, self.op, cut(switch, 120), self.uid_state,
            self.capability, line_no))

    def _access_line(self, body, line_no):
        if not self.op:
            self.unread += 1
            return
        found = _ACCESS.match(body)
        if not found:
            self.unread += 1
            return
        kind, token, time_text, offset, rest = found.groups()
        state, _separator, flags = token.partition('-')
        duration = _DURATION.search(rest)
        proxy = _PROXY.search(rest)
        self.last_running = None
        self.report.add('appop_accesses', AppOpAccess(
            kind, self.uid, self.package, self.op, self.op_mode, self.tag, cut(state, 40), cut(flags, 40),
            time_text or '', cut(offset, 80), cut(duration.group(1), 80) if duration else '',
            duration_ms(duration.group(1)) if duration else None,
            cut(proxy.group(1), 40) if proxy else '', cut(proxy.group(2), 200) if proxy else '',
            cut(proxy.group(3), 200) if proxy else '', '', '', line_no))

    def _running_line(self, body, line_no):
        if not self.op:
            self.unread += 1
            return
        row = AppOpAccess('Running', self.uid, self.package, self.op, self.op_mode, self.tag, '', '', '', '', '', None,
                          '', '', '', cut(body[len('Running start at: '):], 80), '', line_no)
        self.report.add('appop_accesses', row)
        rows = table(self.report, 'appop_accesses')
        self.last_running = row if rows and rows[-1] is row else None

    def _nesting(self, body):
        rows = table(self.report, 'appop_accesses')
        if rows and rows[-1] is self.last_running:
            rows[-1] = self.last_running._replace(start_nesting=cut(body[len('startNesting='):], 40))
            self.last_running = rows[-1]

    def finish(self):
        self._flush_uid()
        if self.unread:
            self.report.warn('appops: %d lines could not be read (an access or running line outside an op, or a uid mode after a package)' % self.unread)


# ---------------------------------------------------------------------------------------------
# role: the roles of each user and their holders
# ---------------------------------------------------------------------------------------------
class RoleReader(PermissionReader):
    """``dumpsys role``: ``user_id=`` then, for each role, ``name=``, ``fallback_enabled=`` and ``holders=``."""
    name = 'role'
    tables = ('role_holders',)

    def __init__(self, report, section):
        PermissionReader.__init__(self, report, section)
        self.user = None
        self.role = None

    def _flush(self):
        role = self.role
        self.role = None
        if role is not None:
            self.report.add('role_holders', RoleHolder(self.user, role['name'], cut(role['holders'], 1000), role['fallback'],
                                                       role['line']))

    def feed(self, line_no, text):
        body = text.strip()
        if body.startswith('user_id='):
            self._flush()
            self.user = to_int(body[len('user_id='):])
        elif body.startswith('name='):
            self._flush()
            self.role = {'name': cut(body[len('name='):]), 'holders': '', 'fallback': '', 'line': line_no}
        elif self.role is not None and body.startswith('holders='):
            self.role['holders'] = body[len('holders='):]
        elif self.role is not None and body.startswith('fallback_enabled='):
            self.role['fallback'] = cut(body[len('fallback_enabled='):], 40)

    def finish(self):
        self._flush()


# ---------------------------------------------------------------------------------------------
# permissionmgr: permission grant lines per app id and user
# ---------------------------------------------------------------------------------------------
class PermissionManagerReader(PermissionReader):
    """``dumpsys permissionmgr``: ``App ID: N`` / ``User: U`` / ``Permissions:`` with ``name: granted=..., flags=[...]``."""
    name = 'permissionmgr'
    tables = ('permission_grants',)

    def __init__(self, report, section):
        PermissionReader.__init__(self, report, section)
        self.app_id = None
        self.user = None
        self.in_permissions = False

    def feed(self, line_no, text):
        if not text.strip():
            return
        indent = indent_of(text)
        body = text.strip()
        if indent == 0:
            self.in_permissions = False
            self.user = None
            self.app_id = to_int(body[len('App ID:'):]) if body.startswith('App ID:') else None
            return
        if self.app_id is None:
            return
        if indent == 2:
            self.in_permissions = False
            self.user = to_int(body[len('User:'):]) if body.startswith('User:') else None
            return
        if self.user is None:
            return
        if indent == 4:
            self.in_permissions = body == 'Permissions:'
            return
        if indent == 6 and self.in_permissions:
            found = parse_permission_line(body)
            if found is not None:
                permission, granted, flags, _user_id = found
                self.report.add('permission_grants', PermissionGrant(
                    self.app_id, self.user, cut(permission), cut(granted, 40), cut(flags, FLAGS_CHARS), line_no))


PERMISSION_READERS = [PackagePermissionsReader, AppOpsReader, RoleReader, PermissionManagerReader]
# Which artifacts present each section, for the section index. The package entry of the shared table is not changed here
# (it would also name Package Permissions and Permission Definitions); see the report of this branch.
PERMISSION_READ_BY = {
    ('service', 'appops'): 'App Ops Modes; App Ops Accesses',
    ('service', 'role'): 'Role Holders',
    ('service', 'permissionmgr'): 'Permission Manager Grants',
}
