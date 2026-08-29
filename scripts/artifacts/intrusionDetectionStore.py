"""Google Play services intrusion detection on-device event store.

com.google.android.gms/databases/intrusion_detection_event_database is the local queue kept
by the GMS intrusiondetection module, the on-device side of Android Advanced Protection's
intrusion logging (see the securitylab.amnesty.org reference in intrusion_logging.py, which
parses the decrypted exports of the same events). Each row's blob is an Android
Parcel-serialized event:

    int32 kind    1 = DnsEvent, 2 = ConnectEvent, 0 = SecurityEvent
    kind 1/2: the matching android.app.admin.NetworkEvent subclass parcel
              (parcel token, then the fields in writeToParcel order)
    kind 0:   int64 event id, then a byte array holding a logd logger_entry
              (uint16 len, uint16 hdr_size, int32 pid, int32 tid, uint32 sec, uint32 nsec,
              uint32 log id, uint32 uid) whose payload is a binary event log record:
              uint32 tag, then typed values (0 int32, 1 int64, 2 string, 3 list, 4 float)

Field order and meaning are pinned to AOSP at commit 664d64ffec5f6d657da71ca8e980a26a47be84eb
(github.com/aosp-mirror/platform_frameworks_base, core/java/android/app/admin/):
DnsEvent.java and ConnectEvent.java writeToParcel, NetworkEvent.java (timestamps are
milliseconds since epoch; the event id resets on reboot and when network logging is enabled),
and SecurityLogTags.logtags for the security tag numbers and their field names. The layout was
additionally cross-validated against a decrypted Intrusion Logging export from the same test
device: all 3,919 stored events on one image matched an export event line one-to-one on event
id and timestamp, with field values agreeing. The differences were rendering only: the export
prefixes addresses with a slash, shows the store's ::ffff: IPv4-mapped addresses as bare IPv4
and shows success integers as booleans.
"""

import os
import sqlite3
import struct
from datetime import datetime, timedelta, timezone

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_path, logfunc, \
    open_sqlite_db_readonly

__artifacts_v2__ = {
    "intrusion_store_dns_events": {
        "name": "Intrusion Detection Store - DNS Events",
        "description": "DNS lookup events from the on-device event store kept by the Google "
                       "Play services intrusion detection module (Android Advanced Protection "
                       "intrusion logging): requested hostname, resolved IP addresses and the "
                       "requesting package. The store holds a recent window of events, not a "
                       "full history. Rows readable only before the write-ahead log is applied "
                       "are reported with Record Origin = Recovered.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-29",
        "last_update_date": "2026-08-29",
        "requirements": "none",
        "category": "Android Intrusion Logging",
        "notes": "Same events, same identifiers and same field values as the dns_event lines "
                 "in a decrypted Intrusion Logging export (the intrusion_logging.py "
                 "artifacts): on the tested Android 16 image every stored event, 3,919 of "
                 "3,919 across the three event kinds, matched an export line one-to-one on "
                 "event id and timestamp with field values agreeing. Event Time is stored as "
                 "milliseconds since epoch and Event ID resets on reboot and when network "
                 "logging is enabled, per the AOSP NetworkEvent source pinned in the module "
                 "docstring, so Event ID is not unique across a store. IP Count is stored "
                 "separately from the address list and can exceed it when there were too many "
                 "addresses to log, per the AOSP DnsEvent source. Most tested events carried "
                 "no addresses at all: Resolved IPs was empty and IP Count 0 on 2,229 of "
                 "2,270 events on the Android 16 store and on all 674 on the Android 17 "
                 "store. Addresses are reported as stored, which keeps the "
                 "::ffff: IPv4-mapped form the export renders as bare IPv4. The store is a "
                 "queue that is emptied during normal operation: on the tested images the "
                 "events table AUTOINCREMENT counter far exceeded the rows present (17,782 "
                 "vs 3,919 and 110,935 vs 982), so absence of an event from this store is not "
                 "evidence it did not happen. Record Origin: Live rows come back from a "
                 "normal read of the database; Recovered rows are present only before the "
                 "write-ahead log is applied (on one tested image the log carried the "
                 "deletion of every stored row, so the whole table is Recovered). Record "
                 "Origin is populated on every row and is uniform on a store that yields "
                 "rows through only one reading; Recovery Method and Recovery Location are "
                 "filled only on Recovered rows and empty otherwise. Sibling "
                 "files in the same GMS container checked and not parsed: "
                 "files/intrusiondetection/shared/intrusion_detection_state.pb repeats the "
                 "selected account name next to one undocumented integer, "
                 "intrusiondetection_sampling.pb holds undocumented counters, and the "
                 "files/phenotype/shared intrusiondetection registration carries module flag "
                 "state, not events. The database's room_master_table and android_metadata "
                 "are Room/SQLite bookkeeping.",
        "paths": ('*/com.google.android.gms/databases/intrusion_detection_event_database*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 262031035 | 2270 rows (all Live)",
            "hc_pixel8pro_a17": "Android 17 | com.google.android.gms vc 262634035 | 674 rows (all Recovered)",
        },
    },
    "intrusion_store_connect_events": {
        "name": "Intrusion Detection Store - Connection Events",
        "description": "TCP connect events from the on-device event store kept by the Google "
                       "Play services intrusion detection module (Android Advanced Protection "
                       "intrusion logging): destination IP address, port and the connecting "
                       "package. The store holds a recent window of events, not a full "
                       "history. Rows readable only before the write-ahead log is applied are "
                       "reported with Record Origin = Recovered.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-29",
        "last_update_date": "2026-08-29",
        "requirements": "none",
        "category": "Android Intrusion Logging",
        "notes": "Same events, same identifiers and same field values as the connect_event "
                 "lines in a decrypted Intrusion Logging export (the intrusion_logging.py "
                 "artifacts); the one-to-one cross-validation, the millisecond timestamps, "
                 "the Event ID reset behaviour, the as-stored ::ffff: address form, the "
                 "queue emptying observed on the tested images and the Record Origin "
                 "vocabulary are described in the Intrusion Detection Store - DNS Events "
                 "notes and apply unchanged here: Record Origin is populated on every row, "
                 "and Recovery Method and Recovery Location are filled only on Recovered "
                 "rows and empty otherwise. TCP is the connection type the AOSP "
                 "ConnectEvent class documents; the row itself stores only address, port and "
                 "package.",
        "paths": ('*/com.google.android.gms/databases/intrusion_detection_event_database*',),
        "output_types": "standard",
        "artifact_icon": "wifi",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 262031035 | 875 rows (all Live)",
            "hc_pixel8pro_a17": "Android 17 | com.google.android.gms vc 262634035 | 308 rows (all Recovered)",
        },
    },
    "intrusion_store_security_events": {
        "name": "Intrusion Detection Store - Security Events",
        "description": "Android security log events from the on-device event store kept by "
                       "the Google Play services intrusion detection module (Android Advanced "
                       "Protection intrusion logging): ADB shell commands and file transfers, "
                       "app process starts, keyguard lock and unlock actions, OS startup, "
                       "keystore key events and more. The store holds a recent window of "
                       "events, not a full history. Rows readable only before the write-ahead "
                       "log is applied are reported with Record Origin = Recovered.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-29",
        "last_update_date": "2026-08-29",
        "requirements": "none",
        "category": "Android Intrusion Logging",
        "notes": "Each blob wraps a binary Android security log record; timestamps carry "
                 "nanosecond precision in the store and are reported to the microsecond. "
                 "Action Type and the field names in Details come from AOSP "
                 "SecurityLogTags.logtags, pinned in the module docstring, with the "
                 "security_ prefix dropped; the decrypted export renders some of the same "
                 "actions under slightly different names (adb_shell_cmd for "
                 "adb_shell_command, adb_sync_send_file for adb_sync_send, key_destruction "
                 "for key_destroyed). An unrecognized tag is reported as the number as "
                 "stored, with its values unnamed. Success fields are reported as stored, 1 "
                 "for the value the export renders as True. On the tested Android 16 image "
                 "all 774 stored security events matched export security_event lines "
                 "one-to-one on nanosecond timestamp, covering 16 of the 46 tags AOSP "
                 "defines; the other 30 decode by the same sourced table but are unexercised "
                 "here. Event ID is as stored and was 0 on most tested rows, matching the "
                 "export's event_id for every matched event. The tested Android 17 store "
                 "held no security events in either database reading while holding hundreds "
                 "of network events; the queue emptying described in the DNS Events notes "
                 "applies, so that absence is not evidence no security events occurred. "
                 "Record Origin is populated on every row and is uniform on a store that "
                 "yields rows through only one reading; Recovery Method and Recovery "
                 "Location are filled only on Recovered rows and empty otherwise. The "
                 "logd header's pid, tid and uid are not reported: they belong to the "
                 "process that wrote the log entry, and on every tested row that uid "
                 "followed the action family (the shell uid on the adb events, the "
                 "keystore uid on the key events, the system uid on the rest), so it "
                 "repeats what Action Type already says. Where an event records an acting "
                 "app's uid, that uid is a named field in Details.",
        "paths": ('*/com.google.android.gms/databases/intrusion_detection_event_database*',),
        "output_types": "standard",
        "artifact_icon": "shield",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 262031035 | 774 rows (all Live)",
            "hc_pixel8pro_a17": "Android 17 | com.google.android.gms vc 262634035 | 0 rows (no security events in either "
                                "database reading, confirmed by a direct decode of all 982 "
                                "stored blobs)",
        },
    },
    "intrusion_store_selected_account": {
        "name": "Intrusion Detection Store - Selected Account",
        "description": "Account name in the selected_accounts table of the on-device event "
                       "store kept by the Google Play services intrusion detection module.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-29",
        "last_update_date": "2026-08-29",
        "requirements": "none",
        "category": "Android Intrusion Logging",
        "notes": "The table stores the account name alone, no timestamps. On both tested "
                 "images it held one row whose Row ID and AUTOINCREMENT counter were both 2, "
                 "so a row with id 1 existed at some point and is no longer present; nothing "
                 "in the store says what it held. The same account string also sits in "
                 "files/intrusiondetection/shared/intrusion_detection_state.pb in the same "
                 "container (checked on both tested images, not parsed separately). Record "
                 "Origin works as in the event artifacts and is populated on every row: a "
                 "row readable only before the write-ahead log is applied is reported as "
                 "Recovered, and Recovery Method and Recovery Location are filled only on "
                 "such rows and empty otherwise. Account Name held one value across the "
                 "tested images' single rows.",
        "paths": ('*/com.google.android.gms/databases/intrusion_detection_event_database*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 262031035 | 1 row (Live)",
            "hc_pixel8pro_a17": "Android 17 | com.google.android.gms vc 262634035 | 1 row (Live)",
        },
    },
}

_UNIX_EPOCH_UTC = datetime(1970, 1, 1, tzinfo=timezone.utc)
_EVENTS_SQL = 'SELECT id, intrusion_detection_event FROM intrusion_detection_events'
_ACCOUNTS_SQL = 'SELECT id, account_name FROM selected_accounts'
_DB_BASENAME = 'intrusion_detection_event_database'

# Provenance vocabulary, shared with snapchat.py (ALEAPP PR #1053). Record Origin is a closed
# two-value set so a viewer can branch on it; Recovery Method names the technique and is empty
# on Live rows; Recovery Location says where in the evidence the row came from.
_ORIGIN_LIVE = 'Live'
_ORIGIN_RECOVERED = 'Recovered'
_METHOD_WAL_DIFF = 'WAL diff'

# android.app.admin.NetworkEvent parcel tokens.
_TOKEN_DNS = 1
_TOKEN_CONNECT = 2

# Everything the strict blob decoder can raise on drifted or truncated input.
_DECODE_ERRORS = (ValueError, struct.error, IndexError, UnicodeDecodeError)

# Security log tag numbers -> (event name, field name per value position), from AOSP
# core/java/android/app/admin/SecurityLogTags.logtags at the commit pinned in the module
# docstring, with the security_ prefix dropped from the names.
_SECURITY_TAGS = {
    210001: ('adb_shell_interactive', ()),
    210002: ('adb_shell_command', ('command',)),
    210003: ('adb_sync_recv', ('path',)),
    210004: ('adb_sync_send', ('path',)),
    210005: ('app_process_start', ('process', 'start_time', 'uid', 'pid', 'seinfo', 'sha256')),
    210006: ('keyguard_dismissed', ()),
    210007: ('keyguard_dismiss_auth_attempt', ('success', 'method_strength')),
    210008: ('keyguard_secured', ()),
    210009: ('os_startup', ('boot_state', 'verity_mode')),
    210010: ('os_shutdown', ()),
    210011: ('logging_started', ()),
    210012: ('logging_stopped', ()),
    210013: ('media_mounted', ('path', 'label')),
    210014: ('media_unmounted', ('path', 'label')),
    210015: ('log_buffer_size_critical', ()),
    210016: ('password_expiration_set', ('package', 'admin_user', 'target_user', 'timeout')),
    210017: ('password_complexity_set', ('package', 'admin_user', 'target_user', 'length',
                                         'quality', 'num_letters', 'num_non_letters',
                                         'num_numeric', 'num_uppercase', 'num_lowercase',
                                         'num_symbols')),
    210018: ('password_history_length_set', ('package', 'admin_user', 'target_user', 'length')),
    210019: ('max_screen_lock_timeout_set', ('package', 'admin_user', 'target_user', 'timeout')),
    210020: ('max_password_attempts_set', ('package', 'admin_user', 'target_user',
                                           'num_failures')),
    210021: ('keyguard_disabled_features_set', ('package', 'admin_user', 'target_user',
                                                'features')),
    210022: ('remote_lock', ('package', 'admin_user', 'target_user')),
    210023: ('wipe_failed', ('package', 'admin_user')),
    210024: ('key_generated', ('success', 'key_id', 'uid')),
    210025: ('key_imported', ('success', 'key_id', 'uid')),
    210026: ('key_destroyed', ('success', 'key_id', 'uid')),
    210027: ('user_restriction_added', ('package', 'admin_user', 'restriction')),
    210028: ('user_restriction_removed', ('package', 'admin_user', 'restriction')),
    210029: ('cert_authority_installed', ('success', 'subject', 'target_user')),
    210030: ('cert_authority_removed', ('success', 'subject', 'target_user')),
    210031: ('crypto_self_test_completed', ('success',)),
    210032: ('key_integrity_violation', ('key_id', 'uid')),
    210033: ('cert_validation_failure', ('reason',)),
    210034: ('camera_policy_set', ('package', 'admin_user', 'target_user', 'disabled')),
    210035: ('password_complexity_required', ('package', 'admin_user', 'target_user',
                                              'complexity')),
    210036: ('password_changed', ('password_complexity', 'target_user')),
    210037: ('wifi_connection', ('bssid', 'event_type', 'reason')),
    210038: ('wifi_disconnection', ('bssid', 'reason')),
    210039: ('bluetooth_connection', ('addr', 'success', 'reason')),
    210040: ('bluetooth_disconnection', ('addr', 'reason')),
    210041: ('package_installed', ('package_name', 'version_code', 'user_id')),
    210042: ('package_updated', ('package_name', 'version_code', 'user_id')),
    210043: ('package_uninstalled', ('package_name', 'version_code', 'user_id')),
    210044: ('backup_service_toggled', ('package', 'admin_user', 'enabled')),
    210045: ('nfc_enabled', ()),
    210046: ('nfc_disabled', ()),
}

# Which named field, in precedence order, fills the Process/Package/UID column, mirroring the
# extraction the decrypted-export artifacts make from the same events.
_SUBJECT_FIELDS = ('process', 'package_name', 'package', 'uid')


class _Parcel:
    """Sequential reader over one Parcel-serialized blob (little-endian)."""

    def __init__(self, buf):
        self.buf = buf
        self.offset = 0

    def read_int32(self):
        value = struct.unpack_from('<i', self.buf, self.offset)[0]
        self.offset += 4
        return value

    def read_int64(self):
        value = struct.unpack_from('<q', self.buf, self.offset)[0]
        self.offset += 8
        return value

    def read_string16(self):
        '''Parcel writeString: int32 char count (-1 for null), UTF-16LE chars, a NUL
        terminator, padded to a 4-byte boundary.'''
        length = self.read_int32()
        if length == -1:
            return None
        end = self.offset + length * 2
        if end > len(self.buf):
            raise ValueError('string past end of blob')
        value = self.buf[self.offset:end].decode('utf-16-le')
        self.offset += ((length + 1) * 2 + 3) & ~3
        return value

    def read_byte_array(self):
        '''Parcel writeByteArray: int32 length, the bytes, padded to a 4-byte boundary.'''
        length = self.read_int32()
        end = self.offset + length
        if length < 0 or end > len(self.buf):
            raise ValueError('byte array past end of blob')
        value = self.buf[self.offset:end]
        self.offset += (length + 3) & ~3
        return value

    def expect_done(self):
        if self.offset < len(self.buf):
            raise ValueError(f'{len(self.buf) - self.offset} undecoded bytes at end of blob')


def _read_eventlog_value(buf, offset):
    """One typed value from a binary event log payload, as (value, next offset)."""
    value_type = buf[offset]
    offset += 1
    if value_type == 0:                                        # int32
        return struct.unpack_from('<i', buf, offset)[0], offset + 4
    if value_type == 1:                                        # int64
        return struct.unpack_from('<q', buf, offset)[0], offset + 8
    if value_type == 2:                                        # string
        length = struct.unpack_from('<i', buf, offset)[0]
        if length < 0 or offset + 4 + length > len(buf):
            raise ValueError('event log string past end of payload')
        value = buf[offset + 4:offset + 4 + length].decode('utf-8', errors='replace')
        return value, offset + 4 + length
    if value_type == 3:                                        # list
        count = buf[offset]
        offset += 1
        items = []
        for _ in range(count):
            item, offset = _read_eventlog_value(buf, offset)
            items.append(item)
        return items, offset
    if value_type == 4:                                        # float
        return struct.unpack_from('<f', buf, offset)[0], offset + 4
    raise ValueError(f'unknown event log value type {value_type}')


def _parse_event(blob):
    """One decoded event dict from a stored blob, keyed by kind: dns, connect or security."""
    parcel = _Parcel(blob)
    kind = parcel.read_int32()
    if kind in (_TOKEN_DNS, _TOKEN_CONNECT):
        token = parcel.read_int32()
        if token != kind:
            raise ValueError(f'network event kind {kind} carries parcel token {token}')
        if kind == _TOKEN_DNS:
            hostname = parcel.read_string16()
            ip_addresses = [parcel.read_string16() for _ in range(parcel.read_int32())]
            ip_count = parcel.read_int32()
            package = parcel.read_string16()
            timestamp_ms = parcel.read_int64()
            event_id = parcel.read_int64()
            parcel.expect_done()
            return {'kind': 'dns', 'hostname': hostname, 'ip_addresses': ip_addresses,
                    'ip_count': ip_count, 'package': package, 'timestamp_ms': timestamp_ms,
                    'event_id': event_id}
        ip_address = parcel.read_string16()
        port = parcel.read_int32()
        package = parcel.read_string16()
        timestamp_ms = parcel.read_int64()
        event_id = parcel.read_int64()
        parcel.expect_done()
        return {'kind': 'connect', 'ip_address': ip_address, 'port': port, 'package': package,
                'timestamp_ms': timestamp_ms, 'event_id': event_id}
    if kind == 0:
        event_id = parcel.read_int64()
        raw = parcel.read_byte_array()
        parcel.expect_done()
        payload_len, header_size = struct.unpack_from('<HH', raw, 0)
        sec, nsec = struct.unpack_from('<II', raw, 12)
        payload = raw[header_size:header_size + payload_len]
        if len(payload) != payload_len:
            raise ValueError('security payload shorter than its declared length')
        tag = struct.unpack_from('<I', payload, 0)[0]
        values = []
        offset = 4
        while offset < len(payload):
            value, offset = _read_eventlog_value(payload, offset)
            values.append(value)
        return {'kind': 'security', 'event_id': event_id, 'sec': sec, 'nsec': nsec,
                'tag': tag, 'values': values}
    raise ValueError(f'unknown event kind {kind}')


def _ms_to_utc(timestamp_ms):
    return _UNIX_EPOCH_UTC + timedelta(milliseconds=timestamp_ms)


def _sec_nsec_to_utc(sec, nsec):
    return _UNIX_EPOCH_UTC + timedelta(seconds=sec, microseconds=nsec // 1000)


def _rows(source_path, sql):
    """Rows through a normal read-only open, write-ahead log applied. [] on any failure."""
    db = open_sqlite_db_readonly(source_path)
    if db is None:
        return []
    try:
        return db.cursor().execute(sql).fetchall()
    except sqlite3.Error as err:
        logfunc(f'Error reading {source_path}:')
        logfunc(f' - {err}')
        return []
    finally:
        db.close()


def _rows_pre_wal(source_path, sql):
    """Rows from the database file as of its last checkpoint, ignoring the write-ahead log.

    immutable=1 is strictly read-only; unlike mode=ro it does not even create a -shm
    sidecar. Path handling goes through the same get_sqlite_db_path() the normal open uses.
    """
    try:
        db = sqlite3.connect(f'file:{get_sqlite_db_path(source_path)}?immutable=1', uri=True)
    except sqlite3.Error:
        return []
    try:
        return db.cursor().execute(sql).fetchall()
    except sqlite3.Error:
        return []
    finally:
        db.close()


def _tables_with_provenance(context, sql):
    """Per store: (db path, [(rowid, payload, origin), ...]) in rowid order.

    Live rows are what a normal read returns with the write-ahead log applied. Recovered
    rows exist only in the pre-log reading: the log carries their deletion, so they are
    part of the file but absent from the store's current state.
    """
    out = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        if os.path.basename(file_found) != _DB_BASENAME:
            continue
        live = _rows(file_found, sql)
        live_ids = {row[0] for row in live}
        recovered = [row for row in _rows_pre_wal(file_found, sql)
                     if row[0] not in live_ids]
        rows = [(row[0], row[1], _ORIGIN_LIVE) for row in live]
        rows += [(row[0], row[1], _ORIGIN_RECOVERED) for row in recovered]
        rows.sort(key=lambda row: row[0])
        out.append((file_found, rows))
    return out


def _provenance(source_path, origin):
    if origin == _ORIGIN_LIVE:
        return (_ORIGIN_LIVE, '', '')
    return (_ORIGIN_RECOVERED, _METHOD_WAL_DIFF,
            f'{os.path.basename(source_path)} (pre-checkpoint)')


def _event_rows(context, artifact_name, wanted_kind):
    """Decoded events of one kind across every store, with per-row provenance columns."""
    out = []
    sources = set()
    for db_path, rows in _tables_with_provenance(context, _EVENTS_SQL):
        sources.add(db_path)
        failed = 0
        for rowid, blob, origin in rows:
            try:
                event = _parse_event(blob)
            except _DECODE_ERRORS as err:
                failed += 1
                if failed == 1:
                    logfunc(f'{artifact_name}: event blob id {rowid} in {db_path} '
                            f'did not decode: {err}')
                continue
            if event['kind'] == wanted_kind:
                out.append((db_path, rowid, origin, event))
        if failed:
            logfunc(f'{artifact_name}: {failed} of {len(rows)} event blobs in {db_path} '
                    'did not decode and are not reported')
    return out, sources


@artifact_processor
def intrusion_store_dns_events(context):
    data_list = []
    events, sources = _event_rows(context, 'Intrusion Detection Store - DNS Events', 'dns')
    for db_path, rowid, origin, event in events:
        origin_value, method, location = _provenance(db_path, origin)
        data_list.append((
            _ms_to_utc(event['timestamp_ms']),
            event['event_id'],
            event['package'],
            event['hostname'],
            ', '.join(ip for ip in event['ip_addresses'] if ip is not None),
            event['ip_count'],
            rowid,
            origin_value,
            method,
            location,
            context.get_relative_path(db_path),
        ))
    data_headers = (('Timestamp', 'datetime'), 'Event ID', 'Package Name', 'Hostname',
                    'Resolved IPs', 'IP Count', 'Row ID', 'Record Origin', 'Recovery Method',
                    'Recovery Location', 'Source File')
    return data_headers, data_list, '\n'.join(sorted(sources))


@artifact_processor
def intrusion_store_connect_events(context):
    data_list = []
    events, sources = _event_rows(
        context, 'Intrusion Detection Store - Connection Events', 'connect')
    for db_path, rowid, origin, event in events:
        origin_value, method, location = _provenance(db_path, origin)
        data_list.append((
            _ms_to_utc(event['timestamp_ms']),
            event['event_id'],
            event['package'],
            event['ip_address'],
            event['port'],
            rowid,
            origin_value,
            method,
            location,
            context.get_relative_path(db_path),
        ))
    data_headers = (('Timestamp', 'datetime'), 'Event ID', 'Package Name', 'Destination IP',
                    'Port', 'Row ID', 'Record Origin', 'Recovery Method', 'Recovery Location',
                    'Source File')
    return data_headers, data_list, '\n'.join(sorted(sources))


def _security_columns(event):
    """(action, subject, details) for one decoded security event.

    Field names come from the AOSP SecurityLogTags table. A tag outside it, or a payload
    whose value count does not match the table, degrades to as-stored values rather than
    guessed names.
    """
    values = event['values']
    if len(values) == 1 and isinstance(values[0], list):
        values = values[0]
    name, fields = _SECURITY_TAGS.get(event['tag'], (None, None))
    action = name if name else f'tag {event["tag"]} (as stored)'
    if fields is None or len(fields) != len(values):
        if name and values:
            logfunc('Intrusion Detection Store - Security Events: '
                    f'{name} carried {len(values)} values where AOSP names {len(fields)}; '
                    'reporting them unnamed')
        pairs = [(f'value{index}', value) for index, value in enumerate(values)]
    else:
        pairs = list(zip(fields, values))
    subject = ''
    for wanted in _SUBJECT_FIELDS:
        for field, value in pairs:
            if field == wanted:
                subject = value
                break
        if subject != '':
            pairs = [(field, value) for field, value in pairs if field != wanted]
            break
    details = ', '.join(f'{field}={value}' for field, value in pairs)
    return action, subject, details


@artifact_processor
def intrusion_store_security_events(context):
    data_list = []
    events, sources = _event_rows(
        context, 'Intrusion Detection Store - Security Events', 'security')
    for db_path, rowid, origin, event in events:
        origin_value, method, location = _provenance(db_path, origin)
        action, subject, details = _security_columns(event)
        data_list.append((
            _sec_nsec_to_utc(event['sec'], event['nsec']),
            event['event_id'],
            action,
            subject,
            details,
            rowid,
            origin_value,
            method,
            location,
            context.get_relative_path(db_path),
        ))
    data_headers = (('Timestamp', 'datetime'), 'Event ID', 'Action Type',
                    'Process/Package/UID', 'Details', 'Row ID', 'Record Origin',
                    'Recovery Method', 'Recovery Location', 'Source File')
    return data_headers, data_list, '\n'.join(sorted(sources))


@artifact_processor
def intrusion_store_selected_account(context):
    data_list = []
    sources = set()
    for db_path, rows in _tables_with_provenance(context, _ACCOUNTS_SQL):
        sources.add(db_path)
        for rowid, account_name, origin in rows:
            origin_value, method, location = _provenance(db_path, origin)
            data_list.append((
                account_name,
                rowid,
                origin_value,
                method,
                location,
                context.get_relative_path(db_path),
            ))
    data_headers = ('Account Name', 'Row ID', 'Record Origin', 'Recovery Method',
                    'Recovery Location', 'Source File')
    return data_headers, data_list, '\n'.join(sorted(sources))
