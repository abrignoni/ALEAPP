__artifacts_v2__ = {
    "threema_account": {
        "name": "Threema - Account",
        "description": "The signed-in Threema account's own Threema ID, display "
                       "nickname, and any mobile number linked to it, read from the "
                       "app's main preferences file.",
        "author": "@Gear-I & Claude",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-08-17",
        "requirements": "none",
        "category": "Threema",
        "notes": "Threema does not use email/password sign-in; the account is the Threema ID itself (an "
                 "8-character code generated on first launch). 'Linked Mobile Number' is only present when a "
                 "phone number has been linked to the ID for discoverability; it is not required to use the "
                 "account and is absent if never set.",
        "paths": ('*/ch.threema.app/shared_prefs/ch.threema.app_preferences.xml',),
        "output_types": ["standard"],
        "artifact_icon": "user",
        "sample_data": {
            "pixel7a_a14": "Android 14 | ch.threema.app | 1 row",
        },
    },
    "threema_contacts": {
        "name": "Threema - Contacts",
        "description": "Contacts recorded in Threema's local, SQLCipher-encrypted "
                       "database, with each one's verification level as Threema's own "
                       "client displays it and when the contact was first added.",
        "author": "@Gear-I & Claude",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-08-17",
        "requirements": "sqlcipher3", 
        "category": "Threema",
        "notes": "Threema encrypts its main database (threema4.db) at rest with "
                 "SQLCipher; this module decrypts it in memory before reading it, "
                 "using the same key.dat unwrapping algorithm documented publicly at "
                 "github.com/wilzbach/threema-decrypt (a fixed 32-byte XOR mask "
                 "followed by a SHA-1 checksum verification), reverse engineered and "
                 "verified against this device's real key.dat and threema4.db - the "
                 "checksum embedded in key.dat matched the derived key exactly, and "
                 "the resulting decryption produced real, readable contact and "
                 "message content that matches this device's documented action "
                 "sheet. This only covers the common case where no local app "
                 "passphrase/PIN was set to further protect key.dat (key.dat's own "
                 "first byte, read directly rather than assumed, records this; on a "
                 "device where it indicates passphrase protection this module leaves "
                 "the database undecrypted rather than guess at a passphrase-derived "
                 "key). The database is opened strictly read-only, and its "
                 "write-ahead log (threema4.db-wal) is opened alongside it so that "
                 "any transaction committed to the log but not yet checkpointed into "
                 "the main file is still included - on the device this was validated "
                 "against, the main file alone was several weeks stale and missing "
                 "real, later content that only existed in the log. 'Verification "
                 "Level' is Threema's own contact-verification indicator "
                 "(0=Unverified, 1=Server-verified, 2=Fully verified, e.g. via QR "
                 "code or NFC scan); on the device this was validated against, the "
                 "one contact recorded at level 2 corresponds exactly to a 'via QR "
                 "scan' verification event documented for that same contact. "
                 "'Group-Only / Removed' reflects Threema's own AcquaintanceLevel "
                 "field on the contact record; Threema's own Android source "
                 "documents this as a combined state meaning either that the "
                 "contact is only known through a shared group and was never "
                 "directly added, or that the user directly removed a formerly "
                 "direct contact - the two cases cannot be told apart from this "
                 "field alone, so both are reported together rather than guessing "
                 "which applies.",
        "paths": (
            '*/ch.threema.app/files/key.dat',
            '*/ch.threema.app/databases/threema4.db*',
        ),
        "output_types": ["standard"],
        "artifact_icon": "address-book",
        "sample_data": {
            "pixel7a_a14": "Android 14 | ch.threema.app | 3 rows",
        },
    },
    "threema_messages": {
        "name": "Threema - Messages",
        "description": "One-to-one messages recorded in Threema's local, "
                       "SQLCipher-encrypted database: text, image, static location, "
                       "and voice/video call events, with direction, delivery/read "
                       "status, and any quote-reply relationship between messages.",
        "author": "@Gear-I & Claude",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-08-17",
        "requirements": "sqlcipher3",
        "category": "Threema",
        "notes": "Decrypted the same way as Threema - Contacts, including reading "
                 "the database's write-ahead log alongside the main file; see that "
                 "artifact's notes for the key.dat/SQLCipher method and its "
                 "passphrase-protected limitation. On the device this was validated "
                 "against, a pair of static-location messages exchanged in one "
                 "conversation existed only in the write-ahead log and would have "
                 "been missed entirely by reading the main database file alone. "
                 "Only the four message-type combinations confirmed on this device "
                 "are decoded: plain text; an image (filename, MIME type and file "
                 "size are read from the message's own structured content, matched "
                 "by value rather than by trusting a fixed field position, since "
                 "that content is a positional JSON array with no field names of "
                 "its own); a static location (latitude, longitude, accuracy in "
                 "metres and a resolved address, read by fixed field position, "
                 "since this content's structure - unlike the image case - showed "
                 "the same fixed [latitude, longitude, accuracy, address] shape on "
                 "every location message observed); and a call event (status/call "
                 "ID/duration are read by name, since that part of the structure is "
                 "a JSON object). Every call on this device carried the same "
                 "numeric call-type marker regardless of whether it was really an "
                 "audio or a video call, so this module does not report an "
                 "audio/video distinction rather than guess at one; duration and "
                 "direction are still reported and, on this device, matched a "
                 "documented audio and video call exactly by duration. 'Quoted "
                 "Message' is resolved via the replying message's own "
                 "quotedMessageId against the original message's apiMessageId (a "
                 "server-assigned protocol ID distinct from the database's own row "
                 "id), not by row order. Group messages, distribution lists and "
                 "polls are out of scope for this release: every corresponding "
                 "table was empty on the device this was validated against, so "
                 "their column mapping could not be confirmed against real "
                 "content. A message can be missing from this table with a gap in "
                 "the numbering between its neighbours; on the device this was "
                 "validated against, exactly one such gap exists at the point in "
                 "the conversation where the action sheet documents a message "
                 "being deleted, but this module does not assert deletion from the "
                 "gap alone since a gap has other possible causes (e.g. a message "
                 "never finishing sync before extraction), and the database's own "
                 "deletedAtUtc/editedAtUtc columns, which would confirm a deletion "
                 "or edit directly, were unset on every row on this device.",
        "paths": (
            '*/ch.threema.app/files/key.dat',
            '*/ch.threema.app/databases/threema4.db*',
        ),
        "output_types": ["standard", "timeline"],
        "artifact_icon": "message-circle",
        "sample_data": {
            "pixel7a_a14": "Android 14 | ch.threema.app | 33 rows",
        },
    },
}

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_path, logfunc
from scripts.artifacts.storagePathViews import unique_files

try:
    from sqlcipher3 import dbapi2 as sqlcipher
    _SQLCIPHER_AVAILABLE = True
except ImportError as _sqlcipher_import_error:
    # Without this guard a missing sqlcipher3 install would raise at
    # module-import time and abort loading of ALL ALEAPP artifacts, not just
    # these two - see browserArtifactsViaMisterSkinnylegs.py for the same
    # pattern already established in this project.
    _SQLCIPHER_AVAILABLE = False
    logfunc(f"Threema: sqlcipher3 not available, encrypted-database "
            f"artifacts disabled: {_sqlcipher_import_error}")

_INVALID_XML_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
# Some binary values (e.g. a Threema Safe backup hash) get written out as
# per-byte numeric character references, including control-code bytes that
# are syntactically well-formed XML entities but not valid XML characters
# (only tab/LF/CR are valid below 0x20) - ElementTree rejects the whole file
# for these the same as it would a raw control byte, so they need the same
# stripping, just matched in their &#N; / &#xN; encoded form instead.
_INVALID_XML_NUMERIC_REF = re.compile(r'&#x?[0-9a-fA-F]+;')


def _strip_invalid_numeric_refs(text):
    def _replace(match):
        ref = match.group(0)
        try:
            if ref[2:3] in ('x', 'X'):
                code_point = int(ref[3:-1], 16)
            else:
                code_point = int(ref[2:-1])
        except ValueError:
            return ref
        is_valid = (code_point in (0x09, 0x0A, 0x0D)
                    or 0x20 <= code_point <= 0xD7FF
                    or 0xE000 <= code_point <= 0xFFFD
                    or 0x10000 <= code_point <= 0x10FFFF)
        return ref if is_valid else ''
    return _INVALID_XML_NUMERIC_REF.sub(_replace, text)

# Fixed 32-byte XOR mask applied to a version-1 key.dat's stored key bytes,
# reverse engineered from github.com/wilzbach/threema-decrypt's cmg_clean.java
# and verified against this device's real key.dat (the file's own trailing
# SHA-1 checksum matched the derived key exactly).
_KEY_DAT_XOR_MASK = bytes([
    149, 13, 38, 122, 136, 234, 119, 16, 156, 80, 231, 63, 71, 224, 105, 114,
    218, 196, 57, 124, 153, 234, 126, 103, 175, 253, 221, 50, 218, 53, 247, 12,
])


def _parse_xml(file_found):
    try:
        return ET.parse(file_found).getroot()
    except ET.ParseError:
        try:
            with open(file_found, encoding='utf-8', errors='replace') as f:
                cleaned = _strip_invalid_numeric_refs(
                    _INVALID_XML_CHARS.sub('', f.read()))
            return ET.fromstring(cleaned)
        except ET.ParseError as ex:
            logfunc(f'Threema: could not parse {file_found}: {ex}')
            return ET.Element('empty')


def _xml_value(root, name):
    node = root.find(f".//*[@name='{name}']")
    if node is None:
        return None
    return node.get('value', node.text)


def _find_all(files_found, suffix):
    """Every file ending in suffix, sorted: an extraction can carry a container
    per Android user, and each user's Threema data is separate evidence. The
    exact-suffix test never matches a -wal/-shm/-journal sidecar."""
    return sorted(str(f) for f in files_found if str(f).endswith(suffix))


def _epoch_ms_to_utc(value):
    try:
        return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def _derive_sqlcipher_key(key_dat_path):
    """Unwrap a version-1 Threema key.dat into the raw 32-byte SQLCipher key.

    Format (all fixed-size, 45 bytes total): 1-byte protection flag, 32-byte
    XOR-masked key, 8 reserved bytes, 4-byte SHA-1(key)[:4] checksum. Returns
    None (logging why) if the file is passphrase-protected, the wrong size,
    or its own checksum does not verify - never a guessed/partial key.
    """
    with open(key_dat_path, 'rb') as f:
        raw = f.read()

    if len(raw) != 45:
        logfunc(f"Threema: key.dat is {len(raw)} bytes, expected 45 for the "
                f"version-1 format; skipping.")
        return None

    protected = raw[0] != 0
    if protected:
        logfunc("Threema: key.dat is passphrase-protected; this module only "
                "supports the unprotected case, skipping.")
        return None

    masked_key = raw[1:33]
    checksum = raw[41:45]
    key = bytes(k ^ m for k, m in zip(masked_key, _KEY_DAT_XOR_MASK))

    if hashlib.sha1(key).digest()[:4] != checksum:
        logfunc("Threema: key.dat checksum did not verify; derived key "
                "rejected rather than used unverified.")
        return None

    return key


def _open_decrypted_db(db_path, key):
    """Open threema4.db read-only through the derived key. Returns a live
    connection on success, or None (logging why) on failure - an unverified
    or wrong key fails here with a clear SQLCipher error rather than silently
    returning garbage, since SQLCipher HMAC-checks every page it decrypts.

    Opened via a read-only file: URI (the same helper and URI form used
    project-wide by scripts.ilapfuncs.open_sqlite_db_readonly) rather than a
    plain path, so evidence is never at risk of being modified, while still
    letting SQLite fold in any not-yet-checkpointed write-ahead log content
    sitting alongside the file - which on the device this was validated
    against held real content the main file alone did not.
    """
    try:
        uri = f"file:{get_sqlite_db_path(db_path)}?mode=ro"
        con = sqlcipher.connect(uri, uri=True)  # pylint: disable=no-member
        cur = con.cursor()
        cur.execute(f"PRAGMA key = 'x\"{key.hex()}\"';")
        # Threema's own DatabaseService overrides SQLCipher's default HMAC-key
        # KDF iteration count to 1; verified empirically against this
        # device's real database, since a wrong iteration count fails every
        # page's HMAC check rather than silently misreading.
        cur.execute("PRAGMA kdf_iter = 1;")
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1;")
        cur.fetchall()
        return con
    except Exception as ex:  # pylint: disable=broad-exception-caught
        logfunc(f"Threema: could not open threema4.db with the derived key: {ex}")
        return None


def _decrypted_connections(files_found):
    """[(connection or None, db path)] per app container, sorted by db path.

    An extraction can carry a container per Android user, each with its own
    key.dat and threema4.db. The pairing stays inside one container: a
    database only opens with the key file next to it, never another user's.
    A container whose key does not derive still reports its db path, so the
    report cites the store that could not be opened.
    """
    if not _SQLCIPHER_AVAILABLE:
        return []
    normalized = [str(f).replace('\\', '/') for f in files_found]
    keys_by_root = {f[:-len('files/key.dat')]: f for f in normalized
                    if f.endswith('files/key.dat')}
    pairs = []
    for db_path in sorted(f for f in normalized
                          if f.endswith('databases/threema4.db')):
        key_dat_path = keys_by_root.get(db_path[:-len('databases/threema4.db')])
        if not key_dat_path:
            continue
        key = _derive_sqlcipher_key(key_dat_path)
        con = _open_decrypted_db(db_path, key) if key is not None else None
        pairs.append((con, db_path))
    return pairs


_VERIFICATION_LEVELS = {
    0: "Unverified",
    1: "Server-verified",
    2: "Fully verified (e.g. QR/NFC scan)",
}


@artifact_processor
def threema_account(context):
    data_headers = ("Threema ID", "Nickname", "Linked Mobile Number")

    files_found = unique_files(context)
    prefs_paths = _find_all(files_found, 'ch.threema.app_preferences.xml')
    if not prefs_paths:
        return data_headers, [], ""

    data_list = []
    for prefs_path in prefs_paths:
        root = _parse_xml(prefs_path)
        identity = _xml_value(root, 'identity') or ''
        nickname = _xml_value(root, 'nickname') or ''
        linked_mobile = _xml_value(root, 'linked_mobile') or ''

        if not identity:
            continue

        logfunc(f"Threema Account: ID {identity} recovered.")
        data_list.append((identity, nickname, linked_mobile))

    return data_headers, data_list, '\n'.join(prefs_paths)


@artifact_processor
def threema_contacts(context):
    data_headers = (
        "Threema ID", "Display Name", "Verification Level",
        ("Date Added", "datetime"), "Group-Only / Removed", "Archived",
    )

    files_found = unique_files(context)
    pairs = _decrypted_connections(files_found)
    if not pairs:
        return data_headers, [], ""

    data_list = []
    for con, _db_path in pairs:
        if con is None:
            continue
        try:
            cur = con.cursor()
            cur.execute(
                "SELECT identity, firstName, lastName, publicNickName, "
                "verificationLevel, dateCreated, acquaintanceLevel, isArchived "
                "FROM contacts;")
            for (identity, first, last, nick, level, created,
                 acquaintance_level, archived) in cur.fetchall():
                display_name = " ".join(p for p in (first, last) if p) or nick or ''
                data_list.append((
                    identity,
                    display_name,
                    _VERIFICATION_LEVELS.get(level, str(level)),
                    _epoch_ms_to_utc(created),
                    "Yes" if acquaintance_level else "",
                    "Yes" if archived else "",
                ))
        finally:
            con.close()

    data_list.sort(key=lambda row: (row[3] is None, row[3]))
    logfunc(f"Threema Contacts: {len(data_list)} contact(s) recovered from "
            f"the decrypted database.")
    return data_headers, data_list, '\n'.join(db for _, db in pairs)


def _extract_media_info(body_json):
    """Pull filename/mime-type/size out of an image message's structured
    content by matching value shape, not a fixed array position - Threema's
    media message body is a positional JSON array with no field names of its
    own, and this project does not trust an undocumented position blindly.
    """
    filename = mime_type = ''
    size = None
    try:
        parts = json.loads(body_json)
    except (ValueError, TypeError):
        return filename, mime_type, size
    if not isinstance(parts, list):
        return filename, mime_type, size
    for part in parts:
        if isinstance(part, str) and '/' in part and not mime_type:
            mime_type = part
        elif isinstance(part, str) and '.' in part and not filename:
            filename = part
        elif isinstance(part, int) and size is None:
            size = part
    return filename, mime_type, size


def _extract_location_info(body_json):
    """Pull latitude/longitude/accuracy/address out of a static location
    message's structured content. Unlike the image case above, every
    location message observed on the validated device showed the same
    fixed [latitude, longitude, accuracy, address, poi-or-null] shape, so
    this reads by position - but still type-checks each field rather than
    trusting the position blindly.
    """
    try:
        parts = json.loads(body_json)
    except (ValueError, TypeError):
        return None, None, None, ''
    if not isinstance(parts, list) or len(parts) < 4:
        return None, None, None, ''
    lat, lon, accuracy, address = parts[0], parts[1], parts[2], parts[3]
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        return None, None, None, ''
    accuracy = accuracy if isinstance(accuracy, (int, float)) else None
    address = address if isinstance(address, str) else ''
    return lat, lon, accuracy, address


def _extract_call_info(body_json):
    """Pull status/callId/duration out of a call event's structured content
    by dictionary key - this part of the structure is a real JSON object
    with named fields, unlike the media message array above.
    """
    try:
        parts = json.loads(body_json)
    except (ValueError, TypeError):
        return None, None, None
    if not isinstance(parts, list):
        return None, None, None
    for part in parts:
        if isinstance(part, dict) and 'callId' in part:
            return part.get('status'), part.get('callId'), part.get('duration')
    return None, None, None


@artifact_processor
def threema_messages(context):
    data_headers = (
        ("Created", "datetime"), "Contact", "Direction", "Content Type",
        "Text / Filename / Address", "MIME Type", "Size (bytes)",
        "Latitude", "Longitude", "Location Accuracy (m)",
        "Call Status", "Call ID", "Call Duration (s)", "State", "Read",
        "Quoted Message", ("Delivered", "datetime"), ("Read At", "datetime"),
    )

    files_found = unique_files(context)
    pairs = _decrypted_connections(files_found)
    if not pairs:
        return data_headers, [], ""

    data_list = []
    for con, _db_path in pairs:
        if con is None:
            continue
        try:
            cur = con.cursor()
            contacts = {}
            for identity, first, last, nick in cur.execute(
                    "SELECT identity, firstName, lastName, publicNickName FROM contacts;"):
                contacts[identity] = " ".join(p for p in (first, last) if p) or nick or identity

            cur.execute(
                "SELECT identity, outbox, type, body, apiMessageId, quotedMessageId, "
                "state, isRead, createdAtUtc, deliveredAtUtc, readAtUtc "
                "FROM message ORDER BY createdAtUtc;")
            rows = cur.fetchall()

            api_id_to_text = {}
            for (identity, outbox, mtype, body, api_id, quoted_id, state,
                 is_read, created, delivered, read_at) in rows:
                if api_id and mtype == 0 and body:
                    api_id_to_text[api_id] = body

            for (identity, outbox, mtype, body, api_id, quoted_id, state,
                 is_read, created, delivered, read_at) in rows:
                contact_name = contacts.get(identity, identity)
                direction = "Sent" if outbox else "Received"
                text = filename = mime_type = ''
                size = call_status = call_id = duration = None
                lat = lon = accuracy = None
                content_type = "Text"

                if mtype == 0:
                    content_type = "Text"
                    text = body or ''
                elif mtype == 8:
                    content_type = "Image"
                    filename, mime_type, size = _extract_media_info(body)
                elif mtype == 4:
                    content_type = "Location"
                    lat, lon, accuracy, text = _extract_location_info(body)
                elif mtype == 9:
                    content_type = "Call"
                    call_status, call_id, duration = _extract_call_info(body)
                else:
                    content_type = f"Unrecognized (type={mtype})"
                    text = body or ''

                quoted_text = api_id_to_text.get(quoted_id, '') if quoted_id else ''

                data_list.append((
                    _epoch_ms_to_utc(created),
                    contact_name,
                    direction,
                    content_type,
                    text or filename,
                    mime_type,
                    size,
                    lat,
                    lon,
                    accuracy,
                    call_status,
                    call_id,
                    duration,
                    state or '',
                    "Yes" if is_read else "",
                    quoted_text,
                    _epoch_ms_to_utc(delivered),
                    _epoch_ms_to_utc(read_at),
                ))
        finally:
            con.close()

    logfunc(f"Threema Messages: {len(data_list)} message(s) recovered from "
            f"the decrypted database.")
    return data_headers, data_list, '\n'.join(db for _, db in pairs)
