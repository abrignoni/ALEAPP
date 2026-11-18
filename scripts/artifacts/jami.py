__artifacts_v2__ = {
    "jami_messages": {
        "name": "Jami - Messages",
        "description": 'Messages, file transfers and membership changes in Jami '
                       'conversations, read from the git repository the Jami daemon '
                       'keeps for each conversation, with each transferred file shown'
                       ' on its message row when a file on the device has the size '
                       'and SHA3-512 the message recorded.',
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "dulwich",
        "category": "Jami",
        "notes": 'Jami (cx.ring) keeps one git repository per conversation under '
                 'files/<account>/conversations/<conversation id>; every message is a'
                 ' commit whose message is a JSON object, except merge commits '
                 '(commit_message.h L94-L100). The repositories are read with '
                 'dulwich, loose and packed objects alike, walking every branch and '
                 'remote-tracking branch, so a commit fetched from a peer but not '
                 "merged would be reported with 'On Main Branch' No; that case does "
                 "not occur on the test image. 'Timestamp' is the commit time, which "
                 'the daemon reports as the message time (conversationrepository.cpp '
                 "parseCommit). 'Type' is the stored type; a commit with more than "
                 "one parent is labelled merge. 'Name in Commit' is the commit's "
                 "author name as stored: the daemon writes the sender's display name "
                 'with < and > removed, or the device id when no display name is set '
                 "or git rejects the name (L835-L848). 'Sender Device ID' is the "
                 "author email, which is the sending device's id (L847). 'Sender' is "
                 "the issuer UID of the device certificate stored in the commit's "
                 "tree (devices/<device id>.crt), the file the daemon's "
                 "uriFromDeviceAtCommit reads, or in its parent's tree when the "
                 "commit's own tree does not hold it (a member leaving removes its "
                 'certificate; not exercised on the test image). The daemon also '
                 'consults its certificate store and verifies the binding; this '
                 'artifact does neither, and does not verify commit signatures. '
                 "'Sender' is shown as the profile vCard name followed by the URI in "
                 'parentheses when a vCard with a name is on the device, and as the '
                 "URI alone otherwise. 'Direction' is Sent when that account is the "
                 'local account (config.yml username), on any of its devices, '
                 'Received when it is another account, and Unknown when no device '
                 'certificate names one; Unknown does not occur on the test image. '
                 "'Member Action' and 'Member URI' are the action and uri of a member"
                 ' commit (add, join, remove, ban, unban; commit_message.h L76-L82); '
                 'for an initial commit they show the word invited and the stored '
                 "invited id. 'Reply To', 'Reaction To' and 'Edit Of' hold the id of "
                 'the commit the message answers, reacts to or replaces; an edit with'
                 ' an empty body deletes a message or removes a reaction '
                 '(commit_message.h L129-L159), and the original stays on its own row'
                 ' (not exercised on the test image). For a file transfer, the file '
                 'is looked for under the name the daemon gives it, <commit '
                 'id>_<tid>.<extension> in '
                 'files/<account>/conversation_data/<conversation id> '
                 '(data_transfer.cpp getFileId), then under the display name in '
                 'files/conversation_data/<account>/<conversation id>. A file is '
                 'shown only when the commit records both a size and a SHA3-512 and '
                 "the file has both (the daemon's own check, data_transfer.cpp "
                 "isExpectedFile, fileutils.cpp sha3File); 'File on Device' says "
                 'which file matched, that none did, or that the commit records no '
                 'size or hash to compare. On dragna_pixel9a_a16 all 13 transfers '
                 'matched: the display-name folder held all 13 files, 12 were shown '
                 "from there and 1 from the daemon's folder, which held the same "
                 "file. 'On Main Branch' held Yes on every row, 'Account' (the "
                 'registered name, else the account URI, else the folder name) held '
                 "one value on every row (the image has one account), 'Reply To' held"
                 ' no value on any row (one reaction and one edit occur), the commit '
                 'and author times were equal on all 44 commits, and neither '
                 'repository held a commit object that no branch reaches. Any other '
                 'type (calls, profile updates, votes, collaborative documents, '
                 'merges) is reported with its type and no decoding; none occur on '
                 'the test image. Not reported: cache/<account>/messages, '
                 'conversation_data/<conversation id>/status, convRequests, '
                 'incomingTrustRequests and syncingMetadatas (empty maps or delivery '
                 'state on the test image), and archive.gz (the account archive, not '
                 'opened). Source references are to jami-daemon at commit 25fadf1 (gi'
                 'thub.com/savoirfairelinux/jami-daemon/tree/25fadf1a1245259c6e7f33e6'
                 '9c0a917f81d6201f), dated after the last commit on the test image, '
                 'whose stores show an older writer (legacy knownDevices layout, no '
                 'millisecond contact keys). Needs the dulwich package; without it '
                 'the artifact logs that and returns no rows.',
        "paths": (
            '*/cx.ring/files/*/conversations/*/.git/*',
            '*/cx.ring/files/*/config.yml',
            '*/cx.ring/files/*/profiles/*.vcf',
            '*/cx.ring/files/*/profile.vcf',
            '*/cx.ring/files/*/conversation_data/*',
            '*/cx.ring/files/conversation_data/*',
        ),
        "output_types": ["standard", "timeline"],
        "artifact_icon": "message-circle",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | Jami versionCode 505 | 44 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Sent",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender",
                "mediaColumn": "Media",
            }
        },
    },
    "jami_conversations": {
        "name": "Jami - Conversations",
        "description": 'Jami conversations recorded for the local account, with the '
                       'created, removed and erased times the daemon stored, the mode'
                       ' and the members.',
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "dulwich",
        "category": "Jami",
        "notes": 'Read from the msgpack file files/<account>/convInfo (ConvInfo, '
                 'conversation.h). The daemon writes each time twice, in seconds and '
                 "in milliseconds ('createdMs'); the milliseconds are used when "
                 "present. 'Created', 'Removed' and 'Erased' are the times the daemon"
                 ' stored; it sets them from more than one path, including sync from '
                 "another device, so 'Created' is not necessarily when the "
                 "conversation began. A conversation is removed when 'Removed' is at "
                 "or after 'Created' (ConvInfo::isRemoved); 'Removed' and 'Erased' "
                 "are blank when the stored value is 0. 'Mode' maps the stored number"
                 ' with ConversationMode (commit_message.h): 0 One to one, 1 Admin '
                 'invites only, 2 Invites only, 3 Public, 4 Document, 5 Feed. '
                 "'Members' comes from "
                 'files/<account>/conversation_data/<conversation id>/members, a '
                 'msgpack list of URI and role (ConversationMember, MemberRole in '
                 'conversationrepository.h: admin, member, invited, banned, left), '
                 'and from the convInfo member list when that file is missing. '
                 "'Commits' counts the commits in the conversation's repository, "
                 "which Jami - Messages lists, and is blank without dulwich. 'Last "
                 "Displayed' is the stored lastDisplayed value, which the daemon "
                 'documents as an id (conversation.h). On dragna_pixel9a_a16 '
                 "'Removed', 'Erased', 'Parent' and 'Last Displayed' held no value on"
                 " any row, and 'Mode' was One to one on both rows. Source references"
                 ' are to jami-daemon at commit 25fadf1.',
        "paths": (
            '*/cx.ring/files/*/convInfo',
            '*/cx.ring/files/*/config.yml',
            '*/cx.ring/files/*/profiles/*.vcf',
            '*/cx.ring/files/*/conversation_data/*/members',
            '*/cx.ring/files/*/conversations/*/.git/*',
        ),
        "output_types": ["standard"],
        "artifact_icon": "message-square",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | Jami versionCode 505 | 2 rows",
        },
    },
    "jami_contacts": {
        "name": "Jami - Contacts",
        "description": 'Jami contacts of the local account, with the added and '
                       'removed times and the stored confirmed and banned flags.',
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Jami",
        "notes": 'Read from the msgpack file files/<account>/contacts (Contact, '
                 "jami_contact.h), a map from the contact's 20-byte account id, shown"
                 " as hex ('Contact URI'), to its record. Times are seconds, or "
                 "'addedMs' and 'removedMs' in milliseconds where the daemon wrote "
                 'them; a stored 0 is blank; the test image holds seconds only. '
                 "'Status' follows the daemon's own rule: Active when 'Added' is "
                 "after 'Removed', Banned when not active and banned, otherwise "
                 "Removed (Contact::isActive, isBanned). 'Banned' is the stored flag."
                 " 'Confirmed' is the stored flag, which the daemon sets when it got "
                 'confirmation that the contact also added the local account '
                 "(jami_contact.h). 'Name' is the FN of the profile vCard "
                 'files/<account>/profiles/<base64 of the URI>.vcf (naming observed '
                 'on the test image) when one is on the device and not empty. On '
                 "dragna_pixel9a_a16 'Removed' held no value on any row, 'Name' was "
                 'blank on both rows (one profile file is empty, the other contact '
                 'has none), and every contact was Active and confirmed. Source '
                 'references are to jami-daemon at commit 25fadf1.',
        "paths": (
            '*/cx.ring/files/*/contacts',
            '*/cx.ring/files/*/config.yml',
            '*/cx.ring/files/*/profiles/*.vcf',
        ),
        "output_types": ["standard"],
        "artifact_icon": "users",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | Jami versionCode 505 | 2 rows",
        },
    },
    "jami_accounts": {
        "name": "Jami - Accounts",
        "description": "The Jami accounts set up on the device: account URI, registered name, "
                       "display name, device name and profile photo.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Jami",
        "notes": 'One row per account folder under files/, read from its config.yml. '
                 'Only the five keys reported are read, and only as single-line '
                 'values; a key written in any other YAML form is left blank, and '
                 "surrounding quotes are removed. 'Account URI' is the username key; "
                 "on the test image it equals the issuer UID of the account's device "
                 "certificate. 'Registered Name', 'Alias', 'Display Name' and 'Device"
                 " Name' are the Account.registeredName, alias, displayName and "
                 "Account.deviceName keys as stored, blank when absent. 'Account ID' "
                 "is the folder name, the daemon's local id for the account. 'Profile"
                 " Name' and 'Profile Photo' come from profile.vcf in the account "
                 'folder when present, else profiles/<base64 of the URI>.vcf; the '
                 'test image has only the second. The photo is the base64 PHOTO '
                 'property, decoded and shown without further checks. config.yml also'
                 ' carries the push token, the account receipt and its signature, and'
                 ' the names of the certificate and key files; none are reported.',
        "paths": (
            '*/cx.ring/files/*/config.yml',
            '*/cx.ring/files/*/profiles/*.vcf',
            '*/cx.ring/files/*/profile.vcf',
        ),
        "output_types": ["standard"],
        "artifact_icon": "user",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | Jami versionCode 505 | 1 row",
        },
    },
    "jami_known_devices": {
        "name": "Jami - Known Devices",
        "description": "Devices known to belong to the local Jami account, with each one's name "
                       "and last synchronisation time.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Jami",
        "notes": 'Read from the msgpack file files/<account>/knownDevices, a map from'
                 " the 32-byte device id, shown as hex, to the device's record. Older"
                 ' daemons store the record as [name, last sync in seconds] and newer'
                 ' ones as a map with name and syncMs in milliseconds; both are read '
                 '(KnownDeviceData, jami_contact.h, and '
                 "ContactList::loadKnownDevices). 'Last Sync' is the time of the last"
                 ' received device sync, blank for a value out of range. The device '
                 "id is the one Jami - Messages shows as 'Sender Device ID'. "
                 'dragna_pixel9a_a16 has the older layout and one device. Source '
                 'references are to jami-daemon at commit 25fadf1.',
        "paths": (
            '*/cx.ring/files/*/knownDevices',
            '*/cx.ring/files/*/config.yml',
        ),
        "output_types": ["standard"],
        "artifact_icon": "smartphone",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | Jami versionCode 505 | 1 row",
        },
    },
}

import base64
import binascii
import hashlib
import importlib.util
import json
import os
import re
from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import canonical_path, unique_files
from scripts.ilapfuncs import (artifact_processor, check_in_embedded_media,
                               check_in_media, logfunc)

# files/<account>/<rest>: the daemon's per-account folder. The client's own copy of
# transferred files sits in files/conversation_data/<account>/<conversation>/ instead.
_ACCOUNT_FILE = re.compile(r'^(?P<pre>.*/cx\.ring)/files/(?P<acc>[^/]+)/(?P<rest>.+)$')
_CLIENT_FILE = re.compile(
    r'^(?P<pre>.*/cx\.ring)/files/conversation_data/(?P<acc>[^/]+)/(?P<conv>[^/]+)/(?P<name>[^/]+)$')
_GIT_DIR = re.compile(r'^conversations/(?P<conv>[^/]+)/\.git/')
_UID_OID = '0.9.2342.19200300.100.1.1'

_MODES = {0: 'One to one', 1: 'Admin invites only', 2: 'Invites only', 3: 'Public',
          4: 'Document', 5: 'Feed'}
_CONFIG_KEYS = ('username', 'alias', 'displayName', 'Account.registeredName',
                'Account.deviceName')
_ROLES = {0: 'admin', 1: 'member', 2: 'invited', 3: 'banned', 4: 'left'}


def _norm(path):
    return str(path).replace('\\', '/')


def _container_key(relative_prefix):
    """One key for every storage spelling of the same app folder (see storagePathViews)."""
    key, _rank = canonical_path(relative_prefix + '/')
    return key


class _Account:
    def __init__(self, acc_id):
        self.acc_id = acc_id
        self.files = {}         # path relative to files/<account>/ -> file on disk
        self.git_dirs = {}      # conversation id -> .git folder on disk
        self.client_files = {}  # (conversation id, display name) -> file on disk
        self.uri = ''
        self.config = None


def _accounts(context):
    """Account folders keyed by (container, account id), duplicates of a container merged."""
    accounts = {}
    for file_found in unique_files(context):
        file_found = str(file_found)
        relative = _norm(context.get_relative_path(file_found))
        on_disk = _norm(file_found)
        client = _CLIENT_FILE.match(relative)
        if client:
            key = (_container_key(client.group('pre')), client.group('acc'))
            acc = accounts.setdefault(key, _Account(client.group('acc')))
            acc.client_files[(client.group('conv'), client.group('name'))] = file_found
            continue
        match = _ACCOUNT_FILE.match(relative)
        if not match or match.group('acc') == 'conversation_data':
            continue
        key = (_container_key(match.group('pre')), match.group('acc'))
        acc = accounts.setdefault(key, _Account(match.group('acc')))
        rest = match.group('rest')
        acc.files[rest] = file_found
        git = _GIT_DIR.match(rest)
        if git and rest.endswith('/.git/HEAD'):
            acc.git_dirs[git.group('conv')] = on_disk[:-len('/HEAD')]
    return accounts


def _source_paths(paths):
    return '\n'.join(sorted(set(paths)))


def _utc_seconds(value):
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        return ''
    try:
        return datetime.fromtimestamp(value, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _utc_ms(value):
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        return ''
    try:
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _time(record, key):
    """The daemon writes '<key>Ms' in milliseconds beside '<key>' in seconds; prefer the first."""
    if isinstance(record.get(key + 'Ms'), int) and record.get(key + 'Ms'):
        return _utc_ms(record[key + 'Ms'])
    return _utc_seconds(record.get(key))


def _msgpack(path):
    import msgpack
    try:
        with open(path, 'rb') as handle:
            return msgpack.unpackb(handle.read(), raw=False, strict_map_key=False)
    except (OSError, ValueError, msgpack.ExtraData, msgpack.FormatError,
            msgpack.StackError) as error:
        logfunc(f'Jami: could not read {os.path.basename(path)}: {type(error).__name__}')
        return None


def _hex(value):
    if isinstance(value, (bytes, bytearray)):
        return value.hex()
    return str(value)


def _config(acc):
    if acc.config is not None:
        return acc.config
    acc.config = {}
    path = acc.files.get('config.yml')
    if not path:
        return acc.config
    try:
        with open(path, 'rb') as handle:
            lines = handle.read().decode('utf-8', 'replace').splitlines()
    except OSError as error:
        logfunc(f'Jami: could not read config.yml: {type(error).__name__}')
        return acc.config
    # Only the few top-level keys the artifacts report are read, and only when the value
    # is a single-line scalar; any other YAML form leaves the key unread (blank).
    for line in lines:
        key, sep, value = line.partition(': ')
        if not sep or key not in _CONFIG_KEYS:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] == '"' and '\\' not in value:
            value = value[1:-1]
        elif len(value) >= 2 and value[0] == value[-1] == "'":
            value = value[1:-1].replace("''", "'")
        elif value[:1] in ('"', "'", '|', '>', '&', '*', '!', '[', '{') or ' #' in value:
            continue
        acc.config[key] = value
    acc.uri = acc.config.get('username', '')
    return acc.config


def _vcard(acc, uri, own=False):
    """(FN, photo bytes, vCard path) from the profile vCard for uri, as far as it holds them."""
    candidates = []
    if own:
        candidates.append('profile.vcf')
    if uri:
        candidates.append('profiles/' + base64.b64encode(uri.encode()).decode() + '.vcf')
    for name in candidates:
        path = acc.files.get(name)
        if not path:
            continue
        try:
            with open(path, 'rb') as handle:
                text = handle.read().decode('utf-8', 'replace')
        except OSError:
            continue
        # vCard folds a long line by starting the next one with a space or a tab.
        text = re.sub(r'\r?\n[ \t]', '', text)
        fn, photo = '', None
        for line in text.splitlines():
            head, sep, value = line.partition(':')
            if not sep:
                continue
            prop = head.split(';')[0].upper()
            if prop == 'FN':
                fn = value.strip()
            elif prop == 'PHOTO' and ('BASE64' in head.upper() or 'ENCODING=B' in head.upper()):
                try:
                    photo = base64.b64decode(value.strip(), validate=False)
                except (binascii.Error, ValueError):
                    photo = None
        if fn or photo:
            return fn, photo, path
    return '', None, ''


def _issuer_uid(pem):
    """The UID in the issuer name of the first certificate in pem, else ''."""
    from Crypto.Util.asn1 import DerObject, DerObjectId, DerSequence, DerSetOf
    match = re.search(rb'-----BEGIN CERTIFICATE-----(.+?)-----END CERTIFICATE-----', pem, re.S)
    if not match:
        return ''
    try:
        der = base64.b64decode(b''.join(match.group(1).split()))
        cert = DerSequence().decode(der)
        tbs = DerSequence().decode(cert[0])
        # version is an explicit [0] tag when present, then serial, signature, issuer.
        start = 1 if isinstance(tbs[0], bytes) and tbs[0][:1] == b'\xa0' else 0
        for rdn in DerSequence().decode(tbs[start + 2]):
            for atv in DerSetOf().decode(rdn):
                pair = DerSequence().decode(atv)
                if DerObjectId().decode(pair[0]).value == _UID_OID:
                    value = DerObject()
                    value.decode(pair[1])
                    return value.payload.decode('utf-8', 'replace')
    except (ValueError, IndexError, TypeError):
        return ''
    return ''


def _tree_blob(repo, tree_id, parts):
    from dulwich.objects import Tree
    try:
        obj = repo[tree_id]
        for part in parts:
            if not isinstance(obj, Tree):
                return None
            _mode, sha = obj[part]
            obj = repo[sha]
        return obj.data
    except KeyError:
        return None


def _device_uri(repo, commit, device, cache):
    """The account owning device, from devices/<device>.crt in the commit's tree (or its
    parent's, for a device that left in this commit), as uriFromDeviceAtCommit reads it."""
    if device in cache:
        return cache[device]
    uri = ''
    trees = [commit.tree]
    if len(commit.parents) == 1:
        try:
            trees.append(repo[commit.parents[0]].tree)
        except KeyError:
            pass
    for tree in trees:
        blob = _tree_blob(repo, tree, [b'devices', device.encode() + b'.crt'])
        if blob:
            uri = _issuer_uid(blob)
            if uri:
                break
    if uri:
        cache[device] = uri
    return uri


def _open_repo(git_dir):
    from dulwich.errors import NotGitRepository
    from dulwich.repo import Repo
    try:
        return Repo(git_dir, bare=True)
    except (NotGitRepository, OSError, KeyError, ValueError) as error:
        logfunc(f'Jami: could not open the repository of conversation '
                f'{os.path.basename(os.path.dirname(git_dir))}: {type(error).__name__}')
        return None


def _commits(repo):
    """(commit, on main) for every commit any branch reaches, newest first per walk."""
    refs = repo.get_refs()
    heads = [sha for name, sha in refs.items() if name != b'HEAD']
    main = refs.get(b'refs/heads/main') or refs.get(b'HEAD')
    on_main = set()
    if main:
        on_main = {entry.commit.id for entry in repo.get_walker(include=[main])}
    seen = set()
    for entry in repo.get_walker(include=heads):
        commit = entry.commit
        if commit.id in seen:
            continue
        seen.add(commit.id)
        yield commit, commit.id in on_main


def _sha3_512(path):
    digest = hashlib.sha3_512()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def _transfer_file(acc, conv, commit_id, body, context):
    """(media ref, status) for a transfer commit: the first candidate whose size and
    SHA3-512 equal what the commit recorded."""
    name = str(body.get('displayName') or '')
    tid = str(body.get('tid') or '')
    sha3 = str(body.get('sha3sum') or '').lower()
    try:
        size = int(body.get('totalSize'))
    except (TypeError, ValueError):
        size = None
    candidates = []
    if re.fullmatch(r'[0-9a-f]{40}', commit_id) and tid.isdigit():
        ext = name.rsplit('.', 1)[1] if '.' in name else ''
        daemon_name = f'{commit_id}_{tid}.{ext}' if ext and len(ext) <= 64 and not re.search(
            r'[\x00-\x1f\x7f/\\:*?"<>|.]', ext) else f'{commit_id}_{tid}'
        path = acc.files.get(f'conversation_data/{conv}/{daemon_name}')
        if path:
            candidates.append(path)
    path = acc.client_files.get((conv, name))
    if path:
        candidates.append(path)
    if not candidates:
        return '', 'not found'
    if size is None or not re.fullmatch(r'[0-9a-f]{128}', sha3):
        return '', 'found, but the commit records no size or SHA3-512 to compare'
    for path in candidates:
        try:
            if os.path.getsize(path) != size or _sha3_512(path) != sha3:
                continue
        except OSError:
            continue
        ref = check_in_media(path, name) or ''
        return ref, 'size and SHA3-512 match: ' + _norm(context.get_relative_path(path))
    return '', 'found, size or SHA3-512 does not match'


def _sender_label(acc, uri, names):
    if not uri:
        return ''
    if uri not in names:
        names[uri] = _vcard(acc, uri, own=(uri == acc.uri))[0]
    return f'{names[uri]} ({uri})' if names[uri] else uri


def _account_label(acc):
    config = _config(acc)
    return str(config.get('Account.registeredName') or acc.uri or acc.acc_id)


@artifact_processor
def jami_messages(context):
    data_headers = (
        ('Timestamp', 'datetime'), 'Direction', 'Sender', 'Message', ('Media', 'media'),
        'Conversation', 'Type', 'Member Action', 'Member URI', 'Reply To',
        'Reaction To', 'Edit Of', 'File Name', 'File Size (bytes)', 'File on Device',
        'On Main Branch', 'Commit ID', 'Sender Device ID', 'Name in Commit', 'Account',
    )
    if importlib.util.find_spec('dulwich') is None:
        logfunc('Jami: the dulwich package is not installed, so conversations are not read')
        return data_headers, [], ''
    data_list = []
    sources = []
    for acc in _accounts(context).values():
        _config(acc)
        account = _account_label(acc)
        names = {}
        for conv, git_dir in sorted(acc.git_dirs.items()):
            repo = _open_repo(git_dir)
            if repo is None:
                continue
            sources.append(acc.files[f'conversations/{conv}/.git/HEAD'])
            cache = {}
            try:
                for commit, on_main in _commits(repo):
                    commit_id = commit.id.decode()
                    try:
                        body = json.loads(commit.message.decode('utf-8'))
                    except (UnicodeDecodeError, ValueError):
                        body = {}
                    if not isinstance(body, dict):
                        body = {}
                    kind = 'merge' if len(commit.parents) > 1 else str(body.get('type', ''))
                    device = commit.author.decode('utf-8', 'replace')
                    name_in_commit = device.rsplit(' <', 1)[0]
                    device = device.rsplit('<', 1)[-1].rstrip('>') if '<' in device else ''
                    uri = _device_uri(repo, commit, device, cache) if device else ''
                    if not uri:
                        direction = 'Unknown'
                    elif acc.uri and uri == acc.uri:
                        direction = 'Sent'
                    else:
                        direction = 'Received'
                    member_action = member_uri = ''
                    if kind == 'member':
                        member_action = str(body.get('action', ''))
                        member_uri = str(body.get('uri', ''))
                    elif kind == 'initial':
                        member_action = 'invited'
                        member_uri = str(body.get('invited', ''))
                    media, file_status, file_name, file_size = '', '', '', ''
                    if kind == 'application/data-transfer+json':
                        file_name = str(body.get('displayName', ''))
                        file_size = body.get('totalSize', '')
                        media, file_status = _transfer_file(acc, conv, commit_id, body, context)
                    data_list.append((
                        _utc_seconds(commit.commit_time), direction,
                        _sender_label(acc, uri, names),
                        str(body.get('body', '')) if 'body' in body else '', media, conv, kind,
                        member_action, member_uri, str(body.get('reply-to', '')),
                        str(body.get('react-to', '')), str(body.get('edit', '')), file_name,
                        file_size, file_status, 'Yes' if on_main else 'No', commit_id,
                        device, name_in_commit, account,
                    ))
            finally:
                repo.close()
    data_list.sort(key=lambda row: (row[0] or datetime.min.replace(tzinfo=timezone.utc), row[5]))
    return data_headers, data_list, _source_paths(context.get_relative_path(p) for p in sources)


@artifact_processor
def jami_conversations(context):
    data_headers = (
        ('Created', 'datetime'), ('Removed', 'datetime'), ('Erased', 'datetime'),
        'Conversation ID', 'Mode', 'Members', 'Commits', 'Last Displayed', 'Parent', 'Account',
    )
    data_list = []
    sources = []
    for acc in _accounts(context).values():
        path = acc.files.get('convInfo')
        if not path:
            continue
        info = _msgpack(path)
        if not isinstance(info, dict):
            continue
        sources.append(path)
        account = _account_label(acc)
        for conv_id, record in info.items():
            if not isinstance(record, dict):
                continue
            conv_id = str(record.get('id') or conv_id)
            members = ''
            member_file = acc.files.get(f'conversation_data/{conv_id}/members')
            listed = _msgpack(member_file) if member_file else None
            if isinstance(listed, list):
                members = ', '.join(
                    f'{entry[0]} ({_ROLES.get(entry[1], entry[1])})'
                    for entry in listed if isinstance(entry, (list, tuple)) and len(entry) == 2)
            elif isinstance(record.get('members'), (list, tuple)):
                members = ', '.join(str(member) for member in record['members'])
            commits = ''
            git_dir = acc.git_dirs.get(conv_id)
            if git_dir:
                repo = _open_repo(git_dir) if importlib.util.find_spec('dulwich') else None
                if repo is not None:
                    try:
                        commits = sum(1 for _ in _commits(repo))
                    finally:
                        repo.close()
            mode = record.get('mode')
            data_list.append((
                _time(record, 'created'), _time(record, 'removed'), _time(record, 'erased'),
                conv_id, _MODES.get(mode, mode if mode is not None else ''), members, commits,
                str(record.get('lastDisplayed') or ''), str(record.get('parent') or ''), account,
            ))
    return data_headers, data_list, _source_paths(context.get_relative_path(p) for p in sources)


@artifact_processor
def jami_contacts(context):
    data_headers = (
        ('Added', 'datetime'), ('Removed', 'datetime'), 'Contact URI', 'Name', 'Status',
        'Confirmed', 'Banned', 'Conversation ID', 'Account',
    )
    data_list = []
    sources = []
    for acc in _accounts(context).values():
        path = acc.files.get('contacts')
        if not path:
            continue
        contacts = _msgpack(path)
        if not isinstance(contacts, dict):
            continue
        sources.append(path)
        _config(acc)
        account = _account_label(acc)
        for key, record in contacts.items():
            if not isinstance(record, dict):
                continue
            uri = _hex(key)
            added = record.get('addedMs') if record.get('addedMs') else (record.get('added') or 0) * 1000
            removed = record.get('removedMs') if record.get('removedMs') else (record.get('removed') or 0) * 1000
            banned = bool(record.get('banned'))
            if added > removed:
                status = 'Active'
            elif banned:
                status = 'Banned'
            else:
                status = 'Removed'
            data_list.append((
                _time(record, 'added'), _time(record, 'removed'), uri,
                _vcard(acc, uri)[0], status, str(bool(record.get('confirmed'))).lower(),
                str(banned).lower(), str(record.get('conversationId') or ''), account,
            ))
    return data_headers, data_list, _source_paths(context.get_relative_path(p) for p in sources)


@artifact_processor
def jami_accounts(context):
    data_headers = (
        'Account URI', 'Registered Name', 'Display Name', 'Alias', 'Device Name',
        'Profile Name', ('Profile Photo', 'media'), 'Account ID',
    )
    data_list = []
    sources = []
    for acc in _accounts(context).values():
        path = acc.files.get('config.yml')
        if not path:
            continue
        config = _config(acc)
        if not config:
            continue
        sources.append(path)
        fn, photo, vcard_path = _vcard(acc, acc.uri, own=True)
        media = ''
        if photo:
            sources.append(vcard_path)
            media = check_in_embedded_media(vcard_path, photo, f'{acc.acc_id}_profile_photo') or ''
        data_list.append((
            acc.uri, str(config.get('Account.registeredName') or ''),
            str(config.get('displayName') or ''), str(config.get('alias') or ''),
            str(config.get('Account.deviceName') or ''), fn, media, acc.acc_id,
        ))
    return data_headers, data_list, _source_paths(context.get_relative_path(p) for p in sources)


@artifact_processor
def jami_known_devices(context):
    data_headers = (('Last Sync', 'datetime'), 'Device ID', 'Device Name', 'Account')
    data_list = []
    sources = []
    for acc in _accounts(context).values():
        path = acc.files.get('knownDevices')
        if not path:
            continue
        devices = _msgpack(path)
        if not isinstance(devices, dict):
            continue
        sources.append(path)
        _config(acc)
        account = _account_label(acc)
        for key, record in devices.items():
            if isinstance(record, dict):
                name, last_sync = record.get('name', ''), _utc_ms(record.get('syncMs'))
            elif isinstance(record, (list, tuple)) and len(record) == 2:
                name, last_sync = record[0], _utc_seconds(record[1])
            else:
                logfunc('Jami: a knownDevices record has an unknown layout and is not read')
                continue
            data_list.append((last_sync, _hex(key), str(name or ''), account))
    return data_headers, data_list, _source_paths(context.get_relative_path(p) for p in sources)
