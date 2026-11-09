__artifacts_v2__ = {
    "kdl_known_data": {
        "name": "KDL Known Data",
        "description": "Actions, marks, system rows and exports logged by KDL (Known-data logger), "
                       "a test-phone app that records what a tester did and when",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-09",
        "last_update_date": "2026-11-09",
        "requirements": "none",
        "category": "KDL (Known-data logger)",
        "sample_data": {
            "emu_a15_kdl_v1": "KDL 0.3.0 | 15 rows",
        },
        "notes": ("KDL (Known-data logger, com.abrignoni.knowndatalogger, "
                  "github.com/abrignoni/known-data-logger) is an app for test phones that logs what a tester "
                  "did and when. One row per log entry in its current version, read from databases/kl.db. When "
                  "an Android user has no kl.db in the extraction, the rows come from that user's "
                  "Android/data/com.abrignoni.knowndatalogger/files/actions-live.jsonl, and when that is "
                  "missing too, from the union of that user's export folders; KDL Setup says which store was "
                  "read. The current version follows the app's own rule (Timeline.current in Model.kt, "
                  "known-data-logger v0.3.0): the highest revision_n of each entry_id, and an entry whose "
                  "latest version is a tombstone was removed in the app and is listed only in KDL Edit History. "
                  "Raw events from the capture service (kind auto_event) are in KDL Captured Events. Source and "
                  "Kind are as stored. Reviewed is No only for an action a rule inferred that nobody accepted "
                  "in the app (docs/DATABASE.md, known-data-logger v0.3.0); the rule is named in Detail. Time "
                  "is the device clock at the action as stored in Unix milliseconds. A tester can change the "
                  "clock as a test step, so the app orders entries by Boot Count, then Time Since Boot (ms). "
                  "LAVA keeps whole seconds; the HTML and TSV keep the milliseconds. Edited is filled only for "
                  "an entry with more than one version. Screenshot is the PNG the app took for the entry, or "
                  "for the mark it refers to, linked by the app's screenshots table or an export's manifest and "
                  "checked against the SHA-256 the app stored at capture. Screenshot Check reports a match, a "
                  "mismatch, a missing file, or a file linked only by its name when no record survives (the app "
                  "names each file after its entry id, CaptureService.kt). Tested on emu_a15_kdl_v1 (KDL 0.3.0, "
                  "schema 3): 15 rows, 6 with a screenshot, all 6 matching their stored hash. In that sample "
                  "Conversation ID, Expected Artifacts and Window (s) had no value on any row, and Reviewed "
                  "held Yes, Time Quality held exact, Time Zone held America/New_York, Boot Count held 1, "
                  "Scenario held clock_locate_01, Device Label held phoneA and Android User held 0 on all 15 "
                  "rows. They are kept because they change between tests, sessions and users. Reading from the "
                  "live copy or the exports, a removed entry, a second Android user, a screenshot whose bytes "
                  "differ from the stored hash and a screenshot with no record were each run on test trees "
                  "built from that image, not on another device. Only KDL 0.3.0 has been tested."),
        "paths": (
            '*/com.abrignoni.knowndatalogger/databases/kl.db*',
            '*/com.abrignoni.knowndatalogger/files/screens/*',
            '*/Android/data/com.abrignoni.knowndatalogger/files/actions-live.jsonl',
            '*/kdl_*/manifest.json',
            '*/kdl_*/actions.jsonl',
            '*/kdl_*/screens/*',
        ),
        "output_types": "standard",
        "artifact_icon": "clipboard",
    },
    "kdl_captured_events": {
        "name": "KDL Captured Events",
        "description": "Screens, taps, typed text, notifications and marks the KDL capture service "
                       "recorded in the apps it was set to watch",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-09",
        "last_update_date": "2026-11-09",
        "requirements": "none",
        "category": "KDL (Known-data logger)",
        "sample_data": {
            "emu_a15_kdl_v1": "KDL 0.3.0 | 51 rows",
        },
        "notes": ("Log entries of kind auto_event: the raw events KDL's accessibility service recorded in the "
                  "apps it was set to capture (KDL Setup lists them), read from the same store as KDL Known "
                  "Data, with the same rule for the current version. Event is the stored action, for example "
                  "screen, tap, typed_text, notification, field_cleared or mark. Text is the stored content: a "
                  "screen title, a tap label, a notification's text, or a field's typed value, which the app "
                  "records as the field's final value stamped at the last keystroke (README, known-data-logger "
                  "v0.3.0). On a phone where KDL ran, this table can hold what was typed and shown in the "
                  "captured apps. Detail is as stored, for example the view id or class the service reported. A "
                  "MARK row carries the screenshot taken when it was pressed, checked against the SHA-256 the "
                  "app stored at capture. Tested on emu_a15_kdl_v1 (KDL 0.3.0): 51 rows, 5 of them marks with a "
                  "screenshot matching its stored hash. In that sample Time Zone held America/New_York, Boot "
                  "Count held 1, Scenario held clock_locate_01, Device Label held phoneA and Android User held "
                  "0 on all 51 rows."),
        "paths": (
            '*/com.abrignoni.knowndatalogger/databases/kl.db*',
            '*/com.abrignoni.knowndatalogger/files/screens/*',
            '*/Android/data/com.abrignoni.knowndatalogger/files/actions-live.jsonl',
            '*/kdl_*/manifest.json',
            '*/kdl_*/actions.jsonl',
            '*/kdl_*/screens/*',
        ),
        "output_types": "standard",
        "artifact_icon": "eye",
    },
    "kdl_edit_history": {
        "name": "KDL Edit History",
        "description": "Stored versions of KDL log entries that were edited, accepted or removed",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-09",
        "last_update_date": "2026-11-09",
        "requirements": "none",
        "category": "KDL (Known-data logger)",
        "sample_data": {
            "emu_a15_kdl_v1": "KDL 0.3.0 | 4 rows",
        },
        "notes": ("Every stored version of each KDL log entry that has more than one version or was removed, in "
                  "the order the entries were first written. An edit in the app writes a new row with a higher "
                  "revision_n, and removing an entry writes a tombstone row, reported here as Change removed "
                  "(docs/DATABASE.md, known-data-logger v0.3.0). Accepting an inferred action is an edit: on "
                  "emu_a15_kdl_v1 both edited entries were messages inferred by a rule, Reviewed went from No "
                  "to Yes, and Action Time stayed the same in both versions. Tested on emu_a15_kdl_v1 (KDL "
                  "0.3.0): 4 rows, 2 entries with an original and an edited version. In that sample App held "
                  "com.google.android.apps.messaging, Source held auto_rule, Kind held action and Android User "
                  "held 0 on all 4 rows. A removed entry was run only on a test tree built from that image with "
                  "a tombstone row added by hand, not on a real removal."),
        "paths": (
            '*/com.abrignoni.knowndatalogger/databases/kl.db*',
            '*/Android/data/com.abrignoni.knowndatalogger/files/actions-live.jsonl',
            '*/kdl_*/manifest.json',
            '*/kdl_*/actions.jsonl',
        ),
        "output_types": "standard",
        "artifact_icon": "edit",
    },
    "kdl_setup": {
        "name": "KDL Setup",
        "description": "KDL settings, the apps it was set to capture, its device snapshots and the "
                       "result of checking the hash chain of each log it kept",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-09",
        "last_update_date": "2026-11-09",
        "requirements": "none",
        "category": "KDL (Known-data logger)",
        "sample_data": {
            "emu_a15_kdl_v1": "KDL 0.3.0 | 13 rows",
        },
        "notes": ("Per Android user: the hash chain check of each KDL log in the extraction, which store the "
                  "log tables were read from, and, from kl.db, the settings rows, the apps KDL was set to "
                  "capture and its device snapshots. The chain is checked with the app's own rule "
                  "(chain_canonical in tools/make_documentation.py, known-data-logger v0.3.0): a SHA-256 over "
                  "each row's fields and the previous row's hash, in seq order. BROKEN names the first row that "
                  "does not match, which follows a row being changed, removed or inserted after it was written. "
                  "On emu_a15_kdl_v1 the chains of kl.db and actions-live.jsonl were intact over 68 rows, and a "
                  "test tree with one row added by hand reported BROKEN at that row. Settings are listed as "
                  "stored; capture_session_active 1 means a capture session was started and not stopped "
                  "(Repo.kt, known-data-logger v0.3.0). App to capture rows give the version the app read when "
                  "the app was added. Profile notes and carrier are typed by the tester. Time is filled only on "
                  "rows that carry a time (session_start, apps, device snapshots): 4 of 13 rows on "
                  "emu_a15_kdl_v1, where Android User held 0 on all 13 rows."),
        "paths": (
            '*/com.abrignoni.knowndatalogger/databases/kl.db*',
            '*/Android/data/com.abrignoni.knowndatalogger/files/actions-live.jsonl',
            '*/kdl_*/manifest.json',
            '*/kdl_*/actions.jsonl',
        ),
        "output_types": "standard",
        "artifact_icon": "settings",
    },
    "kdl_exports": {
        "name": "KDL Exports",
        "description": "KDL export folders found in the extraction, with their own integrity checks",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-09",
        "last_update_date": "2026-11-09",
        "requirements": "none",
        "category": "KDL (Known-data logger)",
        "sample_data": {
            "emu_a15_kdl_v1": "KDL 0.3.0 | 2 rows",
        },
        "notes": ("One row per KDL export folder in the extraction: a folder whose name starts with kdl_ and "
                  "holds a manifest.json whose format is known-data-logger. A folder renamed to anything else "
                  "is not found, and a kdl_ folder with another format was ignored on a test tree. "
                  "actions.jsonl Check compares the file's SHA-256 with the one the manifest recorded. Hash "
                  "Chain checks the rows with the app's rule and against the row count and last hash the "
                  "manifest recorded. Screenshots counts the PNGs the manifest lists that are present in the "
                  "folder's screens/. The tester picks where an export goes, so an export saved off the phone "
                  "is not in the extraction. Tested on emu_a15_kdl_v1 (KDL 0.3.0): 2 rows, both matching their "
                  "manifest with intact chains, in shared storage under Documents/. Android User held 0 on both "
                  "rows."),
        "paths": (
            '*/kdl_*/manifest.json',
            '*/kdl_*/actions.jsonl',
            '*/kdl_*/screens/*',
        ),
        "output_types": "standard",
        "artifact_icon": "upload",
    },
}

import datetime
import hashlib
import json
import math
import os
import re

from scripts.ilapfuncs import artifact_processor, check_in_media, get_sqlite_db_records, logfunc
from scripts.artifacts.storagePathViews import unique_files

PACKAGE = 'com.abrignoni.knowndatalogger'
EXPORT_FORMAT = 'known-data-logger'

# The fields the app hashes for each row, in the order of tools/make_documentation.py in the
# known-data-logger repository (Chain in Model.kt computes the same text).
CHAIN_FIELDS = (
    'account', 'action', 'app_package', 'app_version', 'boot_count', 'content', 'conversation_id',
    'counterpart', 'detail', 'device_label', 'direction', 'edited_utc_ms', 'elapsed_ms', 'entry_id',
    'expected_artifacts', 'gnss_time_ms', 'kind', 'network_time_ms', 'prev_hash', 'profile_id',
    'refers_to', 'revision_n', 'reviewed', 'scenario_id', 'seq', 'source', 'time_quality', 'tz_id',
    'tz_offset_min', 'utc_ms',
)

_PNG = b'\x89PNG\r\n\x1a\n'

# Android user of a path, from the storage layout it sits in. Credential and device encrypted
# app storage, the Android 11+ mirrors, and the emulated shared storage roots.
_USER_PATTERNS = (
    re.compile(r'(?:^|/)(?:user)?data/data/'),
    re.compile(r'(?:^|/)(?:user)?data/user(?:_de)?/(\d+)/'),
    re.compile(r'(?:^|/)data_mirror/data_(?:ce|de)/[^/]+/(\d+)/'),
    re.compile(r'(?:^|/)data/media/(\d+)/'),
    re.compile(r'(?:^|/)storage/emulated/(\d+)/'),
)


def _norm(path):
    return str(path).replace('\\', '/')


def _user(relative):
    """The Android user a path belongs to, or '' when its layout does not say."""
    path = _norm(relative)
    for pattern in _USER_PATTERNS:
        match = pattern.search(path)
        if match:
            return match.group(1) if pattern.groups else '0'
    return ''


def _ms_to_utc(value):
    """A Unix millisecond value as a UTC datetime, keeping the milliseconds."""
    if value in (None, ''):
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _ms_text(value):
    """A Unix millisecond value written out for a text column."""
    when = _ms_to_utc(value)
    return when.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + ' UTC' if when else 'not stored'


def _text(value):
    if value is None:
        return ''
    if isinstance(value, bool):
        return 'Yes' if value else 'No'
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _chain_canonical(row):
    """The exact text the app hashes for a row."""
    data = {key: row.get(key) for key in CHAIN_FIELDS}
    window = row.get('window_s')
    # Java Math.round, as the app stores window_ms
    data['window_ms'] = None if window is None else int(math.floor(window * 1000 + 0.5))
    return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def _verify_chain(rows):
    """Check the hash chain the app writes over its rows, in seq order."""
    ordered = sorted(rows, key=lambda r: r.get('seq') or 0)
    if not ordered or all(r.get('row_hash') is None for r in ordered):
        return 'not present (written before KDL 0.3)'
    previous = ''
    for row in ordered:
        if row.get('prev_hash') != previous:
            return f"BROKEN at seq {row.get('seq')}: link to the previous row does not match"
        digest = hashlib.sha256(_chain_canonical(row).encode('ascii')).hexdigest()
        if digest != row.get('row_hash'):
            return f"BROKEN at seq {row.get('seq')}: row content does not match its hash"
        previous = row['row_hash']
    return f'intact, {len(ordered)} rows, last hash {previous}'


def _sha256_file(path):
    digest = hashlib.sha256()
    try:
        with open(path, 'rb') as handle:
            for block in iter(lambda: handle.read(1 << 20), b''):
                digest.update(block)
    except OSError:
        return None
    return digest.hexdigest()


def _is_png(path):
    try:
        with open(path, 'rb') as handle:
            return handle.read(8) == _PNG
    except OSError:
        return False


def _db_rows(db_path, query):
    records = get_sqlite_db_records(db_path, query)
    if not records:
        return []
    names = [d[0] for d in records.description]
    return [dict(zip(names, record)) for record in records]


def _entry_from_db(row):
    """A kl.db entries row in the shape the app writes to actions.jsonl."""
    row = dict(row)
    row['reviewed'] = bool(row.get('reviewed'))
    raw = row.get('expected_artifacts')
    try:
        row['expected_artifacts'] = json.loads(raw) if raw else []
    except (TypeError, ValueError):
        row['expected_artifacts'] = raw
    return row


def _read_jsonl(path):
    rows, bad = [], 0
    try:
        with open(path, 'rb') as handle:
            raw = handle.read()
    except OSError as error:
        logfunc(f'KDL: could not read {path}: {error.strerror}')
        return None, None, 0
    for line in raw.decode('utf-8', errors='replace').splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except ValueError:
            bad += 1
    return rows, raw, bad


class _User:
    def __init__(self, user):
        self.user = user
        self.db = None
        self.live = None
        self.private_screens = {}
        self.exports = []
        self.rows = []
        self.shots = {}
        self.read_from = ''
        self.read_path = None
        self.settings = []
        self.apps = []
        self.profiles = []
        self.chain = []


def _load(context):
    """Find KDL's stores in the extraction and read them, grouped by Android user."""
    users = {}
    export_dirs = {}

    def user_of(path):
        key = _user(context.get_relative_path(path))
        if key not in users:
            users[key] = _User(key)
        return users[key]

    for found in unique_files(context):
        path = _norm(found)
        if os.path.isdir(found):
            continue
        name = os.path.basename(path)
        parent = os.path.dirname(path)
        if path.endswith(f'/{PACKAGE}/databases/kl.db'):
            user_of(found).db = found
        elif f'/{PACKAGE}/files/screens/' in path and f'/Android/data/{PACKAGE}/' not in path:
            user_of(found).private_screens[name] = found
        elif path.endswith(f'/Android/data/{PACKAGE}/files/actions-live.jsonl'):
            user_of(found).live = found
        elif os.path.basename(parent).startswith('kdl_') and name in ('manifest.json', 'actions.jsonl'):
            export_dirs.setdefault(parent, {})[name] = found
        elif os.path.basename(parent) == 'screens' and \
                os.path.basename(os.path.dirname(parent)).startswith('kdl_'):
            export_dirs.setdefault(os.path.dirname(parent), {}).setdefault('screens', {})[name] = found

    for folder in sorted(export_dirs):
        files = export_dirs[folder]
        manifest_path = files.get('manifest.json')
        if not manifest_path:
            continue
        try:
            with open(manifest_path, encoding='utf-8') as handle:
                manifest = json.load(handle)
        except (OSError, ValueError):
            continue
        if not isinstance(manifest, dict) or manifest.get('format') != EXPORT_FORMAT:
            continue
        export = {'folder': folder, 'manifest': manifest, 'manifest_path': manifest_path,
                  'actions_path': files.get('actions.jsonl'), 'screens': files.get('screens', {}),
                  'rows': None, 'raw': None, 'bad_lines': 0}
        if export['actions_path']:
            export['rows'], export['raw'], export['bad_lines'] = _read_jsonl(export['actions_path'])
        user_of(manifest_path).exports.append(export)

    for state in users.values():
        if state.db:
            _read_db(state)
        if state.live:
            rows, _, bad = _read_jsonl(state.live)
            if rows is not None:
                state.chain.append(('actions-live.jsonl', state.live, _verify_chain(rows), bad))
                if not state.read_from:
                    state.rows = rows
                    state.read_from = 'actions-live.jsonl'
                    state.read_path = state.live
                    state.shots = {r['entry_id']: r['screenshot'] for r in rows
                                   if isinstance(r.get('screenshot'), dict) and r.get('entry_id')}
        if not state.read_from:
            # Neither the database nor the live copy: the union of the exports, newest first.
            merged = {}
            newest = sorted(state.exports, key=lambda e: _export_time_ms(e) or 0, reverse=True)
            for export in newest:
                for row in export['rows'] or []:
                    merged.setdefault((row.get('entry_id'), row.get('revision_n')), row)
                    if isinstance(row.get('screenshot'), dict) and row.get('entry_id'):
                        state.shots.setdefault(row['entry_id'], row['screenshot'])
            if merged:
                state.rows = list(merged.values())
                state.read_from = 'exports'
                state.read_path = '\n'.join(e['actions_path'] for e in newest if e['actions_path'])
        # The live copy is written before a screenshot exists, so its rows carry none. The
        # screenshot records an export kept fill in what the log itself did not record.
        for export in sorted(state.exports, key=lambda e: _export_time_ms(e) or 0, reverse=True):
            for shot in export['manifest'].get('screenshots') or []:
                if isinstance(shot, dict) and shot.get('entry_id'):
                    state.shots.setdefault(shot['entry_id'], shot)
    return [users[key] for key in sorted(users)]


def _read_db(state):
    entries = _db_rows(state.db, 'SELECT * FROM entries ORDER BY seq')
    rows = [_entry_from_db(r) for r in entries]
    state.chain.append(('kl.db', state.db, _verify_chain(rows), 0))
    state.rows = rows
    state.read_from = 'kl.db'
    state.read_path = state.db
    for shot in _db_rows(state.db, 'SELECT entry_id, file, sha256, status, utc_ms FROM screenshots'):
        state.shots[shot['entry_id']] = shot
    state.settings = _db_rows(state.db, 'SELECT key, value FROM settings ORDER BY key')
    state.apps = _db_rows(state.db, 'SELECT * FROM apps ORDER BY added_utc_ms, package')
    state.profiles = _db_rows(state.db, 'SELECT * FROM profiles ORDER BY id')


def _export_time_ms(export):
    value = (export['manifest'].get('export') or {}).get('utc_ms')
    return value if isinstance(value, int) else None


def _order(row):
    return (row.get('boot_count') or 0, row.get('elapsed_ms') or 0, row.get('seq') or 0)


def _current(rows):
    """The app's rule: an entry's current version is its highest revision; a tombstone removes it."""
    by_entry = {}
    for row in rows:
        by_entry.setdefault(row.get('entry_id'), []).append(row)
    current = []
    for revisions in by_entry.values():
        latest = max(revisions, key=lambda r: (r.get('revision_n') or 0, r.get('seq') or 0))
        if latest.get('kind') != 'tombstone':
            current.append((latest, len(revisions)))
    return sorted(current, key=lambda item: _order(item[0]))


def _screenshot(state, row):
    """(media reference, check text) for the screenshot that belongs to a row."""
    shot = state.shots.get(row.get('entry_id')) or state.shots.get(row.get('refers_to'))
    if not shot:
        # No screenshot record. The app names each file after its entry (CaptureService.kt).
        for entry_id in (row.get('entry_id'), row.get('refers_to')):
            found = entry_id and _find_screen(state, f'{entry_id}.png')
            if found:
                return _show(found, f'{entry_id}.png'), 'no screenshot record; linked by file name, no stored hash'
        return '', ''
    status = shot.get('status') or ''
    name = shot.get('file')
    if not name:
        return '', f'no file ({status})' if status else 'no file'
    found = _find_screen(state, name)
    if not found:
        return '', f'{name} not in the extraction ({status})'
    stored = shot.get('sha256') or shot.get('sha256_at_capture')
    actual = _sha256_file(found)
    if not stored:
        check = 'no stored hash'
    elif actual == stored:
        check = 'matches the hash stored at capture'
    else:
        check = 'DIFFERS from the hash stored at capture'
    if status and status != 'ok':
        check = f'{status}; {check}'
    media = _show(found, name)
    if not media:
        check = f'{check}; not a PNG, not shown'
    return media, check


def _find_screen(state, name):
    """A screenshot file of this user: the app's own folder first, then the newest export."""
    found = state.private_screens.get(name)
    if found:
        return found
    for export in sorted(state.exports, key=lambda e: _export_time_ms(e) or 0, reverse=True):
        if name in export['screens']:
            return export['screens'][name]
    return None


def _show(found, name):
    if not _is_png(found):
        return ''
    return check_in_media(found, name, force_type='image/png', force_extension='png') or ''


def _sources(users):
    paths = []
    for state in users:
        for path in (state.read_path or '').split('\n'):
            if path and path not in paths:
                paths.append(path)
    return '\n'.join(paths)


@artifact_processor
def kdl_known_data(context):
    users = _load(context)
    data_list = []
    for state in users:
        for row, revisions in _current(state.rows):
            if row.get('kind') == 'auto_event':
                continue
            media, check = _screenshot(state, row)
            edited = _ms_to_utc(row.get('edited_utc_ms')) if (row.get('revision_n') or 0) > 0 else ''
            window = row.get('window_s')
            data_list.append((
                _ms_to_utc(row.get('utc_ms')), edited, _text(row.get('action')),
                _text(row.get('app_package')), _text(row.get('app_version')), _text(row.get('content')),
                _text(row.get('counterpart')), _text(row.get('direction')), _text(row.get('conversation_id')),
                _text(row.get('source')), _text(row.get('reviewed')), media, check,
                ', '.join(row.get('expected_artifacts') or []) if isinstance(row.get('expected_artifacts'), list)
                else _text(row.get('expected_artifacts')),
                _text(row.get('detail')), _text(row.get('time_quality')), '' if window is None else window,
                _text(row.get('tz_id')), row.get('boot_count'), row.get('elapsed_ms'), _text(row.get('kind')),
                revisions, _text(row.get('scenario_id')), _text(row.get('device_label')),
                _text(row.get('entry_id')), _text(row.get('refers_to')), state.user,
            ))
    data_headers = (
        ('Time', 'datetime'), ('Edited', 'datetime'), 'Action', 'App', 'App Version', 'Content',
        'Counterpart', 'Direction', 'Conversation ID', 'Source', 'Reviewed', ('Screenshot', 'media'),
        'Screenshot Check', 'Expected Artifacts', 'Detail', 'Time Quality', 'Window (s)', 'Time Zone',
        'Boot Count', 'Time Since Boot (ms)', 'Kind', 'Revisions', 'Scenario', 'Device Label',
        'Entry ID', 'Refers To', 'Android User')
    return data_headers, data_list, _sources(users)


@artifact_processor
def kdl_captured_events(context):
    users = _load(context)
    data_list = []
    for state in users:
        for row, _ in _current(state.rows):
            if row.get('kind') != 'auto_event':
                continue
            media, check = _screenshot(state, row)
            data_list.append((
                _ms_to_utc(row.get('utc_ms')), _text(row.get('action')), _text(row.get('app_package')),
                _text(row.get('content')), _text(row.get('counterpart')), _text(row.get('detail')),
                media, check, _text(row.get('tz_id')), row.get('boot_count'), row.get('elapsed_ms'),
                _text(row.get('scenario_id')), _text(row.get('device_label')), _text(row.get('entry_id')),
                state.user,
            ))
    data_headers = (
        ('Time', 'datetime'), 'Event', 'App', 'Text', 'Counterpart', 'Detail', ('Screenshot', 'media'),
        'Screenshot Check', 'Time Zone', 'Boot Count', 'Time Since Boot (ms)', 'Scenario',
        'Device Label', 'Entry ID', 'Android User')
    return data_headers, data_list, _sources(users)


@artifact_processor
def kdl_edit_history(context):
    users = _load(context)
    data_list = []
    for state in users:
        by_entry = {}
        for row in state.rows:
            by_entry.setdefault(row.get('entry_id'), []).append(row)
        # Entries in the order their first version was written.
        for revisions in sorted(by_entry.values(), key=lambda revs: min(r.get('seq') or 0 for r in revs)):
            if len(revisions) < 2 and revisions[0].get('kind') != 'tombstone':
                continue
            for row in sorted(revisions, key=lambda r: (r.get('revision_n') or 0, r.get('seq') or 0)):
                if row.get('kind') == 'tombstone':
                    change = 'removed'
                elif (row.get('revision_n') or 0) == 0:
                    change = 'original'
                else:
                    change = 'edited'
                data_list.append((
                    _ms_to_utc(row.get('edited_utc_ms')), _ms_to_utc(row.get('utc_ms')), change,
                    row.get('revision_n'), _text(row.get('action')), _text(row.get('app_package')),
                    _text(row.get('content')), _text(row.get('counterpart')), _text(row.get('direction')),
                    _text(row.get('source')), _text(row.get('reviewed')), _text(row.get('detail')),
                    _text(row.get('kind')), _text(row.get('entry_id')), row.get('seq'), state.user,
                ))
    data_headers = (
        ('Edited', 'datetime'), ('Action Time', 'datetime'), 'Change', 'Revision', 'Action', 'App',
        'Content', 'Counterpart', 'Direction', 'Source', 'Reviewed', 'Detail', 'Kind', 'Entry ID', 'Seq', 'Android User')
    return data_headers, data_list, _sources(users)


def _stamp_ms(value):
    try:
        stamp = json.loads(value)
    except (TypeError, ValueError):
        return None
    return stamp.get('utc_ms') if isinstance(stamp, dict) else None


@artifact_processor
def kdl_setup(context):
    users = _load(context)
    data_list = []
    paths = []
    for state in users:
        for name, path, status, bad in state.chain:
            detail = f'{bad} line(s) not valid JSON' if bad else ''
            data_list.append(('', 'Hash chain', name, status, detail, state.user))
            if path not in paths:
                paths.append(path)
        if state.read_from:
            data_list.append(('', 'Log read from', state.read_from,
                              f"{len(state.rows)} rows", '', state.user))
        for setting in state.settings:
            key, value = setting.get('key'), setting.get('value')
            time = _ms_to_utc(_stamp_ms(value)) if key == 'session_start' else ''
            data_list.append((time, 'Setting', _text(key), _text(value), '', state.user))
        for app in state.apps:
            detail = (f"version code {_text(app.get('version_code'))}; first install "
                      f"{_ms_text(app.get('first_install_ms'))}; last update "
                      f"{_ms_text(app.get('last_update_ms'))}")
            if app.get('account'):
                detail += f"; account {app.get('account')}"
            data_list.append((_ms_to_utc(app.get('added_utc_ms')), 'App to capture', _text(app.get('package')),
                              f"{_text(app.get('label'))} {_text(app.get('version_name'))}".strip(), detail,
                              state.user))
        for profile in state.profiles:
            value = ' '.join(v for v in (_text(profile.get('manufacturer')), _text(profile.get('model'))) if v)
            detail = '; '.join(f'{label} {_text(profile.get(key))}' for label, key in (
                ('Android', 'release'), ('SDK', 'sdk_int'), ('build', 'incremental'),
                ('security patch', 'security_patch'), ('fingerprint', 'fingerprint'),
                ('kernel', 'kernel'), ('baseband', 'baseband'), ('carrier', 'carrier'),
                ('notes', 'notes'), ('boot count', 'boot_count')) if profile.get(key) not in (None, ''))
            data_list.append((_ms_to_utc(profile.get('utc_ms')), 'Device snapshot',
                              f"profile {profile.get('id')}", value, detail, state.user))
        if state.db and state.db not in paths:
            paths.append(state.db)
    data_headers = (('Time', 'datetime'), 'Item', 'Name', 'Value', 'Detail', 'Android User')
    return data_headers, data_list, '\n'.join(paths)


@artifact_processor
def kdl_exports(context):
    users = _load(context)
    data_list = []
    paths = []
    for state in users:
        for export in sorted(state.exports, key=lambda e: _export_time_ms(e) or 0):
            manifest = export['manifest']
            listed = (manifest.get('files') or {}).get('actions.jsonl') or {}
            if export['raw'] is None:
                file_check = 'actions.jsonl not in the extraction'
                chain = ''
                rows = ''
            else:
                actual = hashlib.sha256(export['raw']).hexdigest()
                want = listed.get('sha256')
                file_check = 'matches the manifest' if actual == want else \
                    f'DIFFERS from the manifest (manifest {want}, file {actual})'
                rows = len(export['rows'])
                chain = _verify_chain(export['rows'])
                kept = manifest.get('hash_chain') or {}
                if chain.startswith('intact') and kept and (
                        kept.get('last_row_hash') != max(export['rows'], key=lambda r: r.get('seq') or 0)
                        .get('row_hash') or kept.get('rows') != rows):
                    chain = 'intact, but rows differ from the count or last hash in the manifest'
            listed_shots = manifest.get('screenshots') or []
            files = [s.get('file') for s in listed_shots if s.get('file')]
            present = sum(1 for name in files if name in export['screens'])
            shots = f'{present} of {len(files)} listed present'
            logger = manifest.get('logger') or {}
            data_list.append((
                _ms_to_utc(_export_time_ms(export)), context.get_relative_path(export['folder']),
                _text(manifest.get('scenario_id')), _text(manifest.get('device_label')), rows,
                file_check, chain, shots, _text(logger.get('version_name')), state.user,
            ))
            for path in (export['manifest_path'], export['actions_path']):
                if path and path not in paths:
                    paths.append(path)
    data_headers = (
        ('Export Time', 'datetime'), 'Folder', 'Scenario', 'Device Label', 'Rows', 'actions.jsonl Check',
        'Hash Chain', 'Screenshots', 'KDL Version', 'Android User')
    return data_headers, data_list, '\n'.join(paths)
