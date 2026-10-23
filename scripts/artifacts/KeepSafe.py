__artifacts_v2__ = {
    "keepsafe_media": {
        "name": "KeepSafe - Media Files",
        "description": (
            "Files held in the KeepSafe vault, decoded from the 'file' documents of the "
            "Couchbase Lite database files/media_meta_db/mediaDb.cblite2, each linked to its "
            "on-disk copy under files/media/XX/ID/TYPE (XX the first two characters of the ID, "
            "TYPE e.g. PHOTO, VIDEO, THUMBNAIL)."
        ),
        "author": "@charpy4n6, Claude, @AlexisBrignoni",
        "creation_date": "2026-10-22",
        "last_update_date": "2026-10-23",
        "requirements": "none",
        "category": "KeepSafe",
        "notes": (
            "Document bodies are Fleece-encoded and are decoded with the database's own "
            "SharedKeys entry in kv_info; a store in the LiteCore 2.x layout, whose body column "
            "holds a revision tree, is read from its current revision, a path not exercised on "
            "an Android image. db.sqlite3 is opened read-only with its -wal, where "
            "most documents lived on the validation image. Each store is paired only with the "
            "media files of the same Android user (data/user/<n>, with data/data as user 0), and "
            "Android User names it; the same store seen under data/data and data/user/0 is read "
            "once. Column names from the database are "
            "its own field names written as words (isInTrash is Is In Trash, albumId is Album "
            "ID); values are as stored, booleans shown as Yes/No and epoch seconds or "
            "milliseconds converted to UTC. Album Name is the name field of the album document "
            "whose id equals albumId. Type, MIME Type, Width, Height, Data Size, Duration, Local "
            "Hash and ETag come from the entry of the document's media list whose type equals "
            "the document's type; no unit is stored for Duration. On the validation image Local "
            "Hash matched the SHA-1 of the on-disk PHOTO/VIDEO file and Data Size its byte "
            "count, those files being stored unencrypted. What each Vault Type value means is "
            "not established. Documents in kv_del_default have no body and are reported with "
            "only their ID and In kv_del_default set to Yes. Created At and Imported At "
            "(createdAt, importedAt) are not established to mean any particular event; they are "
            "not the time in the file: on the validation image they were identical on every "
            "file and did not match the photos' EXIF dates. "
            "Date/Time In File, Make, Model, Software and "
            "location are read from the file itself: for images from EXIF (DateTimeOriginal "
            "with OffsetTimeOriginal, falling back to DateTimeDigitized and DateTime), converted "
            "to UTC only when an offset tag is present; for MP4 from mvhd creation_time "
            "(seconds since 1904, UTC), the com.android.* keys of the QuickTime meta box and "
            "the ISO 6709 udta/©xyz location. On the validation image the camera photos kept "
            "their GPS tags but every value was zero or NaN, and the videos' udta held a "
            "zero-filled box in place of ©xyz; both are reported as empty with a note, never "
            "as 0,0. On the validation image the PNG screenshots carried EXIF DateTimeOriginal "
            "and Software but no Make or Model."
        ),
        "paths": (
            "*/com.kii.safe/files/media_meta_db/mediaDb.cblite2/db.sqlite3*",
            "*/com.kii.safe/files/media/*/*/*",
        ),
        "output_types": "standard",
        "artifact_icon": "image",
    },
    "keepsafe_albums": {
        "name": "KeepSafe - Albums",
        "description": (
            "The 'album' documents of mediaDb.cblite2, with the number of 'file' documents "
            "whose albumId equals each album's id."
        ),
        "author": "@charpy4n6, Claude, @AlexisBrignoni",
        "creation_date": "2026-10-22",
        "last_update_date": "2026-10-23",
        "requirements": "none",
        "category": "KeepSafe",
        "notes": (
            "Column names are the document's field names written as words. File Count is "
            "computed by this module. On the validation image there were two albums with "
            "specialType '.main_folder', one of type 'private' and one of type 'decoy'; what "
            "each type means is not established. Both had createdAt 0, which is left blank."
        ),
        "paths": ("*/com.kii.safe/files/media_meta_db/mediaDb.cblite2/db.sqlite3*",),
        "output_types": "standard",
        "artifact_icon": "folder",
    },
    "keepsafe_breakins": {
        "name": "KeepSafe - Break-in Records",
        "description": (
            "The 'breakIn' documents of files/breakin_db/breakinDb.cblite2, with the photo "
            "file each one's photoFileUri names."
        ),
        "author": "@charpy4n6, Claude, @AlexisBrignoni",
        "creation_date": "2026-10-22",
        "last_update_date": "2026-10-23",
        "requirements": "none",
        "category": "KeepSafe",
        "notes": (
            "Column names are the document's field names written as words; values are as "
            "stored, booleans shown as Yes/No and timeCaptured (epoch milliseconds) converted to "
            "UTC. The photo is read from files/breakin/NAME.ksd of the same Android user, the name "
            "taken from photoFileUri. Its first bytes are read: a JPEG, PNG or WebP file is shown, "
            "and anything else is named in Photo Format (sniffed) and not shown. On the "
            "validation image the .ksd file was a plain JPEG."
        ),
        "paths": (
            "*/com.kii.safe/files/breakin_db/breakinDb.cblite2/db.sqlite3*",
            "*/com.kii.safe/files/breakin/*",
        ),
        "output_types": "all",
        "artifact_icon": "alert-triangle",
    },
    "keepsafe_browser": {
        "name": "KeepSafe - Browser Tabs",
        "description": "The 'browserTab' documents of files/browser_db/browserDb.cblite2.",
        "author": "@charpy4n6, Claude, @AlexisBrignoni",
        "creation_date": "2026-10-22",
        "last_update_date": "2026-10-23",
        "requirements": "none",
        "category": "KeepSafe",
        "notes": (
            "Column names are the document's field names written as words; createdAt and "
            "lastAccessTime (epoch milliseconds) are converted to UTC. Matches Session "
            "currentTabId and Session Search Engine come from the 'browserSession' document's "
            "currentTabId and searchEngine fields. The webViewState value is not decoded."
        ),
        "paths": ("*/com.kii.safe/files/browser_db/browserDb.cblite2/db.sqlite3*",),
        "output_types": "all",
        "artifact_icon": "globe",
    },
    "keepsafe_account": {
        "name": "KeepSafe - Account & Preferences",
        "description": (
            "Selected values from the MessagePack record list in files/accountsv2.mpack (group "
            "Account), followed by KeepSafe preference and related values."
        ),
        "author": "@charpy4n6, Claude, @AlexisBrignoni",
        "creation_date": "2026-10-22",
        "last_update_date": "2026-10-23",
        "requirements": "none",
        "category": "KeepSafe",
        "notes": (
            "The file is a MessagePack array of records whose keys are small integers; it "
            "stores no field names. In Stored Key, the record type is the value of key 4 and "
            "the key is the one each value was read from. The Account Field labels are this module's, inferred from the "
            "values on the validation image: Package was com.kii.safe; App Version Code equalled "
            "initial-install-version in com.kii.keepsafe.preferences.xml; Email values had the "
            "form of an email address; Owner ID equalled couchbase_owner_id; Device Name held "
            "the device's model name; Device ID equalled device_id in device_id.xml.xml; Device "
            "UUID was a UUID in the same record as Device ID; Country held a two-letter country "
            "code; Language held a two-letter language code; and "
            "Firebase Push Token equalled the Fid in files/PersistedInstallation*.json followed "
            "by a token. Only these keys are reported. Record type 98 holds local key material, "
            "including an RSA private key, and is not reported."
            " Preference rows that held the same value as an Account row (couchbase_owner_id "
            "and device_id.xml.xml device_id) are not repeated. Stored Key gives the record ID, "
            "record type and key for Account rows and the preference key for the others."
            "Values are reported as stored. key-last-saved-pin-hash held a bcrypt hash "
            "($2b$04$) on the validation image. 'Secret Door (selected)' is the secret_door value "
            "as stored, which names a disguise (e.g. CALCULATOR). It does not show the disguise "
            "is active: on the validation image it named a disguise while the app's launcher "
            "icon was not disguised. This module does not read the launcher state. Three launch "
            "counters are kept (app-launches-count, app-lifetime-open-count and "
            "Usage-Metrics.xml LAUNCH_COUNT) and held three different values on the validation "
            "image; what each one counts is not established, so each is reported under its own "
            "key. App Theme Color and Dark Mode are "
            "theme_preferences.xml appTheme/darkMode as stored (SYSTEM follows the device "
            "setting); prev_pref_pin_theme is a numeric code whose mapping is not established. "
            "The Account Device ID is 16 hex characters, the format of Android's "
            "Settings.Secure.ANDROID_ID; that it equals the device's ANDROID_ID is not "
            "established here and can be checked against settings_ssaid.xml. files/device-id "
            "and files/internal-device-id are JSON holding app-generated UUIDs. The Amplitude "
            "device_id and AppsFlyer AF_INSTALLATION are the bundled SDKs' own identifiers. "
            "signup-date is stored as YYYYMMDD "
            "text with no time or zone, so it is not converted. install-timestamp is epoch "
            "seconds, first_open_time and the trash/session values epoch milliseconds, and "
            "appsFlyerFirstInstall local time with its UTC offset; these are converted to UTC. "
            "First Install and First Open come from the AppsFlyer and Google Analytics SDKs "
            "bundled in the app, not from KeepSafe's own preferences. Rows are grouped by Android "
            "user (data/user/<n>, with data/data as user 0); a file whose path names no user is "
            "logged and not reported. Last Analytics Event and "
            "Last Session Start are last_event_time and previous_session_id (epoch "
            "milliseconds) from the bundled Amplitude SDK's database. Blocklist values are the "
            "private browser's tracker blocklist download, from browser_privacy.xml. Help "
            "Center Visit is a WebView Local Storage key of a getkeepsafe.com origin whose name "
            "is a date string, reported with the offset it carries. The LevelDB is read with "
            "ccl_leveldb; for each key only the record with the highest sequence number counts, "
            "and a key whose latest record is a deletion is not reported."
        ),
        "paths": (
            "*/com.kii.safe/files/accountsv2.mpack",
            "*/com.kii.safe/shared_prefs/*.xml",
            "*/com.kii.safe/files/device-id",
            "*/com.kii.safe/files/internal-device-id",
            "*/com.kii.safe/databases/com.amplitude.api*",
            "*/com.kii.safe/app_webview/Default/Local Storage/leveldb/*",
        ),
        "output_types": "standard",
        "artifact_icon": "user",
    },
}

import hashlib
import json
import math
import os
import re
import sqlite3
import struct
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from PIL import ExifTags, Image, UnidentifiedImageError

from scripts.ccl import ccl_leveldb
from scripts.ilapfuncs import artifact_processor, check_in_media, logfunc, open_sqlite_db_readonly

# ---------------------------------------------------------------------------
# Couchbase Lite (LiteCore) store reader.
#
# Document bodies are Fleece. The decoder follows couchbase/fleece at commit
# 8ce5f690480b77c0f93d03f456a29828b5a55d66: Fleece.md, Fleece/Core/Value.cc,
# Fleece/Core/Array.cc and Fleece/Core/Pointer.hh. Dict keys that are integers index
# the store's SharedKeys array, kept in kv_info under the key 'SharedKeys'.
# A kv_default table without an 'extra' column is the LiteCore 2.x layout, where 'body'
# is a revision tree holding the Fleece body of each revision
# (couchbase-lite-core LiteCore/RevTrees/RawRevTree.hh at 3f90f2e97b9a07ca84af6ea56a8b1b0d25860e1f);
# the current revision is first. Same decoder as iLEAPP's KeepSafe module.
# ---------------------------------------------------------------------------

class _FleeceError(ValueError):
    pass


_FLEECE_UNDEFINED = object()


def _fleece_uvarint(buf, pos):
    result = shift = 0
    for i in range(10):
        if pos + i >= len(buf):
            raise _FleeceError("varint runs past the end of the data")
        byte = buf[pos + i]
        result |= (byte & 0x7F) << shift
        if byte < 0x80:
            return result, i + 1
        shift += 7
    raise _FleeceError("varint is too long")


def _fleece_deref(buf, pos, wide):
    if wide:
        if pos + 4 > len(buf):
            raise _FleeceError("wide pointer runs past the end of the data")
        raw = struct.unpack_from(">I", buf, pos)[0]
        external, offset = raw & 0x40000000, (raw & 0x3FFFFFFF) << 1
    else:
        raw = struct.unpack_from(">H", buf, pos)[0]
        external, offset = raw & 0x4000, (raw & 0x3FFF) << 1
    if external:
        # Pointer.cc derefExtern / carefulDeref (couchbase/fleece 8ce5f690): with no base
        # document to resolve against, a narrow pointer is read as a legacy pointer from before
        # the extern flag existed, whose offset is fifteen bits, and kept only if it lands
        # inside the data. A wide one is refused.
        legacy = (raw & 0x7FFF) << 1
        if wide or legacy == 0 or legacy > pos:
            raise _FleeceError("external pointer")
        return pos - legacy
    if offset == 0 or offset > pos:
        raise _FleeceError(f"pointer at {pos} has an invalid offset {offset}")
    return pos - offset


def _fleece_slot(buf, pos, wide, shared_keys, depth):
    if pos + 2 > len(buf):
        raise _FleeceError("collection slot runs past the end of the data")
    if buf[pos] & 0x80:
        pos = _fleece_deref(buf, pos, wide)
    return _fleece_value(buf, pos, shared_keys, depth + 1)


def _fleece_value(buf, pos, shared_keys, depth):
    if depth > 200:
        raise _FleeceError("values are nested too deeply")
    if pos + 2 > len(buf):
        raise _FleeceError("value runs past the end of the data")
    b0, b1 = buf[pos], buf[pos + 1]
    tag = b0 >> 4
    if tag == 0:
        small = ((b0 & 0x0F) << 8) | b1
        return small - 0x1000 if small & 0x800 else small
    if tag == 1:
        size = (b0 & 0x07) + 1
        data = buf[pos + 1:pos + 1 + size]
        if len(data) != size:
            raise _FleeceError("integer runs past the end of the data")
        return int.from_bytes(data, "little", signed=not b0 & 0x08)
    if tag == 2:
        fmt, size = ("<d", 8) if b0 & 0x08 else ("<f", 4)
        if pos + 2 + size > len(buf):
            raise _FleeceError("float runs past the end of the data")
        return struct.unpack_from(fmt, buf, pos + 2)[0]
    if tag == 3:
        return {0x00: None, 0x04: False, 0x08: True, 0x0C: _FLEECE_UNDEFINED}[b0 & 0x0C]
    if tag in (4, 5):
        size, start = b0 & 0x0F, pos + 1
        if size == 0x0F:
            size, used = _fleece_uvarint(buf, start)
            start += used
        data = buf[start:start + size]
        if len(data) != size:
            raise _FleeceError("string runs past the end of the data")
        return data.decode("utf-8", "replace") if tag == 4 else bytes(data)
    if tag in (6, 7):
        wide = bool(b0 & 0x08)
        width = 4 if wide else 2
        count = ((b0 & 0x07) << 8) | b1
        first = pos + 2
        if count == 0x7FF:
            # the long count is 2047 plus a varint, padded to an even length (Array.cc)
            extra, used = _fleece_uvarint(buf, first)
            count += extra
            first += used + (used & 1)
        if tag == 6:
            return [_fleece_slot(buf, first + i * width, wide, shared_keys, depth) for i in range(count)]
        result = {}
        for i in range(count):
            key_pos = first + 2 * i * width
            key = _fleece_slot(buf, key_pos, wide, None, depth)
            value = _fleece_slot(buf, key_pos + width, wide, shared_keys, depth)
            if key == -2048:
                # dict inheritance: the value is the parent dict, overridden by the keys after it
                if isinstance(value, dict):
                    result.update(value)
                continue
            if isinstance(key, int) and shared_keys and 0 <= key < len(shared_keys):
                key = shared_keys[key]
            if value is _FLEECE_UNDEFINED:
                result.pop(key, None)
            else:
                result[key] = value
        return result
    raise _FleeceError(f"unexpected pointer at {pos}")


def _fleece_decode(data, shared_keys=None):
    """Return the root value of a Fleece document. Raises _FleeceError on data it cannot read."""
    buf = bytes(data)
    if len(buf) < 2 or len(buf) % 2:
        raise _FleeceError(f"length {len(buf)} is not a positive even number")
    pos = len(buf) - 2
    if buf[pos] & 0x80:
        pos = _fleece_deref(buf, pos, False)
        if buf[pos] & 0x80:
            pos = _fleece_deref(buf, pos, True)
    return _fleece_value(buf, pos, shared_keys, 0)


def _revtree_current_body(data):
    """Body of the first (current) revision in a LiteCore 2.x RawRevTree, or None when that
    revision carries no body."""
    buf = bytes(data)
    if len(buf) < 12:
        raise _FleeceError("revision tree is too short")
    size = struct.unpack_from(">I", buf, 0)[0]
    _parent, flags, rev_id_len = struct.unpack_from(">HBB", buf, 4)
    if size < 8 + rev_id_len or size > len(buf):
        raise _FleeceError(f"revision size {size} does not fit the data")
    if not flags & 0x80:  # RawRevision::kHasData
        return None
    _sequence, used = _fleece_uvarint(buf, 8 + rev_id_len)
    return buf[8 + rev_id_len + used:size]


# ---------------------------------------------------------------------------
# Android user scoping. A file is paired only with files of the same Android user, so a
# second user's copy of the app cannot supply a picture or a value for this one's rows.
# data/data is user 0's credential-encrypted storage, the same storage as data/user/0.
# ---------------------------------------------------------------------------

_USER_VIEWS = (
    re.compile(r"(?:^|/)data/user/(\d+)/com\.kii\.safe/"),
    re.compile(r"(?:^|/)data_mirror/data_ce/[^/]+/(\d+)/com\.kii\.safe/"),
)
_USER_ZERO = re.compile(r"(?:^|/)data/data/com\.kii\.safe/")


def _android_user(path):
    """The Android user a KeepSafe file belongs to, or '' when its path does not name one."""
    path = str(path).replace("\\", "/")
    for pattern in _USER_VIEWS:
        match = pattern.search(path)
        if match:
            return match.group(1)
    return "0" if _USER_ZERO.search(path) else ""


def _file_digest(path):
    digest = hashlib.sha256()
    try:
        with open(path, "rb") as file_obj:
            for chunk in iter(lambda: file_obj.read(1 << 20), b""):
                digest.update(chunk)
    except OSError:
        return None
    return digest.hexdigest()


def _db_paths(files_found, db_name):
    """(Android user, path) for each <db_name>.cblite2/db.sqlite3, one per user and content:
    the same store seen under data/data and data/user/0 is read once."""
    suffix = f"{db_name}.cblite2/db.sqlite3"
    chosen, seen = [], set()
    for path in sorted(f for f in files_found if f.replace("\\", "/").endswith(suffix)):
        if os.path.isdir(path):
            continue
        user = _android_user(path)
        if not user:
            logfunc(f"KeepSafe: no Android user in the path of {path}; its files are not paired with it")
        wal = _file_digest(path + "-wal") if os.path.exists(path + "-wal") else ""
        key = (user, _file_digest(path), wal)
        if key in seen:
            continue
        seen.add(key)
        chosen.append((user, path))
    return chosen


def _read_cblite(db_path):
    """Yields (doc_id, decoded_body_or_None, purged) for kv_default and kv_del_default."""
    db = open_sqlite_db_readonly(db_path)
    if db is None:
        return
    try:
        tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        shared_keys = None
        if "kv_info" in tables:
            row = db.execute("SELECT body FROM kv_info WHERE key = 'SharedKeys'").fetchone()
            if row and row[0]:
                try:
                    shared_keys = _fleece_decode(row[0])
                except _FleeceError as ex:
                    logfunc(f"KeepSafe: SharedKeys in {db_path} could not be decoded ({ex}); "
                            "document keys are reported as integers")
        if not isinstance(shared_keys, list):
            shared_keys = None
        for table, purged in (("kv_default", False), ("kv_del_default", True)):
            if table not in tables:
                continue
            columns = {row[1] for row in db.execute(f'PRAGMA table_info("{table}")')}
            rev_tree_layout = "extra" not in columns
            for doc_id, body in db.execute(f'SELECT key, body FROM "{table}" ORDER BY sequence'):
                value = None
                if body:
                    try:
                        fleece = _revtree_current_body(body) if rev_tree_layout else body
                        value = _fleece_decode(fleece, shared_keys) if fleece else None
                    except (_FleeceError, KeyError, struct.error) as ex:
                        logfunc(f"KeepSafe: undecoded document {doc_id!r} in {db_path}: {ex}")
                yield doc_id, value if isinstance(value, dict) else None, purged
    except sqlite3.Error as ex:
        logfunc(f"KeepSafe: error reading {db_path}: {ex}")
    finally:
        db.close()


def _utc(value, millis=False):
    """UTC datetime for a Unix epoch value. KeepSafe mixes units within one document
    (createdAt in seconds, movedToTrashAt in milliseconds), so a value too large to be
    seconds is read as milliseconds whatever the caller expected."""
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
        return ""
    if millis or value > 1e11:
        value /= 1000
    return datetime.fromtimestamp(value, timezone.utc)


def _yes_no(value):
    if value is None:
        return ""
    return "Yes" if value else "No"


# ---------------------------------------------------------------------------
# Embedded metadata of the vault file itself (EXIF for images, MP4 atoms for video).
# ---------------------------------------------------------------------------

_EMPTY_META = {"source": "", "capture_utc": "", "capture_raw": "", "make": "", "model": "", "software": "",
               "lat": "", "lon": "", "alt": "", "note": ""}


def _finite(value):
    try:
        value = float(value)
    except (TypeError, ValueError, ZeroDivisionError):
        return None
    return value if math.isfinite(value) else None


def _exif_coordinate(dms, ref):
    parts = [_finite(v) for v in dms] if isinstance(dms, (tuple, list)) and len(dms) == 3 else []
    if not parts or None in parts or not isinstance(ref, str) or ref.strip("\x00") == "":
        return None
    value = parts[0] + parts[1] / 60 + parts[2] / 3600
    return -value if ref.strip().upper() in ("S", "W") else value


def _exif_datetime(text, offset):
    """(UTC datetime or "", text as stored). Without an offset tag the stored time has no
    zone, so it is not converted."""
    text = str(text).strip("\x00 ") if text else ""
    offset = str(offset).strip("\x00 ") if offset else ""
    raw = f"{text} {offset}".strip()
    if not text:
        return "", ""
    match = re.fullmatch(r"([+-])(\d{2}):(\d{2})", offset)
    try:
        local = datetime.strptime(text, "%Y:%m:%d %H:%M:%S")
    except ValueError:
        return "", raw
    if not match:
        return "", raw
    sign = -1 if match.group(1) == "-" else 1
    tz = timezone(sign * timedelta(hours=int(match.group(2)), minutes=int(match.group(3))))
    return local.replace(tzinfo=tz).astimezone(timezone.utc), raw


def _image_metadata(path):
    meta = dict(_EMPTY_META)
    try:
        with Image.open(path) as img:
            exif = img.getexif()
    except (OSError, UnidentifiedImageError, ValueError) as ex:
        meta["note"] = f"Unreadable image: {ex}"
        return meta
    if not exif:
        meta["note"] = "No EXIF"
        return meta
    meta["source"] = "EXIF"
    sub = exif.get_ifd(ExifTags.IFD.Exif)
    meta["make"] = str(exif.get(271, "")).strip("\x00 ")
    meta["model"] = str(exif.get(272, "")).strip("\x00 ")
    meta["software"] = str(exif.get(305, "")).strip("\x00 ")
    for date_tag, offset_tag, tag_name in ((36867, 36881, "DateTimeOriginal"),
                                           (36868, 36882, "DateTimeDigitized"),
                                           (306, 36880, "DateTime")):
        stored = sub.get(date_tag) if date_tag != 306 else exif.get(306)
        if stored:
            meta["capture_utc"], raw = _exif_datetime(stored, sub.get(offset_tag))
            meta["capture_raw"] = f"EXIF {tag_name}: {raw}"
            break

    gps = exif.get_ifd(ExifTags.IFD.GPSInfo)
    if gps:
        lat = _exif_coordinate(gps.get(2), gps.get(1))
        lon = _exif_coordinate(gps.get(4), gps.get(3))
        if lat is None or lon is None or (lat == 0 and lon == 0):
            meta["note"] = "EXIF GPS tags present but empty"
        else:
            meta["lat"], meta["lon"] = round(lat, 6), round(lon, 6)
            alt = _finite(gps.get(6))
            if alt is not None:
                meta["alt"] = round(-alt if gps.get(5) in (1, b"\x01") else alt, 1)
    if not meta["note"] and not any(meta[k] for k in ("capture_raw", "make", "model", "software")):
        meta["note"] = "EXIF present without date, device or GPS tags"
    return meta


def _mp4_boxes(fh, start, end):
    pos = start
    while pos + 8 <= end:
        fh.seek(pos)
        size, box_type = struct.unpack(">I4s", fh.read(8))
        header = 8
        if size == 1:
            size = struct.unpack(">Q", fh.read(8))[0]
            header = 16
        elif size == 0:
            size = end - pos
        if size < header:
            return
        yield box_type, pos + header, min(pos + size, end)
        pos += size


_ISO6709_RE = re.compile(r"([+-]\d+(?:\.\d+)?)([+-]\d+(?:\.\d+)?)([+-]\d+(?:\.\d+)?)?")


def _video_metadata(path):
    """Creation time from mvhd, the Android camera's com.android.* keys, and the
    ISO 6709 location in udta/©xyz."""
    meta = dict(_EMPTY_META)
    try:
        with open(path, "rb") as fh:
            fh.seek(0, os.SEEK_END)
            moov = next(((s, e) for t, s, e in _mp4_boxes(fh, 0, fh.tell()) if t == b"moov"), None)
            if not moov:
                meta["note"] = "No moov box"
                return meta
            keys, values, location = [], {}, None
            for box_type, start, end in _mp4_boxes(fh, *moov):
                fh.seek(start)
                if box_type == b"mvhd":
                    version = fh.read(4)[0]
                    raw = fh.read(8 if version == 1 else 4)
                    seconds = int.from_bytes(raw, "big")
                    if seconds:
                        created = datetime(1904, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds)
                        meta["capture_utc"] = created
                        meta["capture_raw"] = f"MP4 mvhd creation_time: {seconds} (seconds since 1904-01-01 UTC)"
                elif box_type == b"udta":
                    for sub_type, sub_start, sub_end in _mp4_boxes(fh, start, end):
                        if sub_type == b"\x00\x00\x00\x00":
                            location = location or ""    # a zero-filled child where ©xyz would sit
                        if sub_type == b"\xa9xyz":
                            fh.seek(sub_start + 4)
                            location = fh.read(sub_end - sub_start - 4).decode("utf-8", "replace")
                elif box_type == b"meta":
                    for sub_type, sub_start, sub_end in _mp4_boxes(fh, start, end):
                        fh.seek(sub_start)
                        if sub_type == b"keys":
                            count = struct.unpack(">I", fh.read(8)[4:])[0]
                            for _ in range(count):
                                size = struct.unpack(">I", fh.read(4))[0]
                                keys.append(fh.read(size - 4)[4:].decode("utf-8", "replace"))
                        elif sub_type == b"ilst":
                            for item_type, item_start, item_end in _mp4_boxes(fh, sub_start, sub_end):
                                index = int.from_bytes(item_type, "big")
                                for data_type, data_start, data_end in _mp4_boxes(fh, item_start, item_end):
                                    if data_type != b"data":
                                        continue
                                    fh.seek(data_start)
                                    well_known = struct.unpack(">I", fh.read(8)[:4])[0] & 0xFFFFFF
                                    payload = fh.read(data_end - data_start - 8)
                                    if well_known == 1:
                                        values[index] = payload.decode("utf-8", "replace")
                                    elif well_known == 23 and len(payload) == 4:
                                        values[index] = round(struct.unpack(">f", payload)[0], 3)
    except (OSError, struct.error, ValueError) as ex:
        meta["note"] = f"Unreadable video: {ex}"
        return meta

    meta["source"] = "MP4"
    named = {keys[i - 1]: v for i, v in values.items() if 0 < i <= len(keys)}
    meta["make"] = named.get("com.android.manufacturer", "")
    meta["model"] = named.get("com.android.model", "")
    meta["software"] = "; ".join(f"{key} {named[key]}" for key in ("com.android.version", "com.android.capture.fps")
                                 if key in named)
    match = _ISO6709_RE.match(location.strip()) if location else None
    if match and not (float(match.group(1)) == 0 and float(match.group(2)) == 0):
        meta["lat"], meta["lon"] = float(match.group(1)), float(match.group(2))
        meta["alt"] = float(match.group(3)) if match.group(3) else ""
    elif location is not None:
        meta["note"] = "MP4 udta location box present but empty"
    return meta


def _file_metadata(path, mime_type):
    if not path:
        return dict(_EMPTY_META)
    if str(mime_type).startswith("video/"):
        return _video_metadata(path)
    return _image_metadata(path)


def _media_file_index(files_found):
    """(Android user, id hex without dashes, TYPE) -> path, for files/media/<xx>/<id>/<TYPE>.
    Files whose path names no Android user are left out, so they are never paired."""
    index = {}
    for path in files_found:
        norm = path.replace("\\", "/")
        if "/com.kii.safe/files/media/" not in norm or os.path.isdir(path):
            continue
        user = _android_user(norm)
        if not user:
            continue
        parts = norm.split("/")
        index.setdefault((user, parts[-2].lower(), parts[-1].upper()), path)
    return index


def _sniff_image(path):
    """(MIME type, extension) for the image formats a report can show, or ("", "")."""
    try:
        with open(path, "rb") as file_obj:
            head = file_obj.read(16)
    except OSError:
        return "", ""
    if head.startswith(b"\xff\xd8\xff"):
        return "image/jpeg", "jpg"
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png", "png"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "image/webp", "webp"
    return "", ""


# ---------------------------------------------------------------------------
# Artifacts.
# ---------------------------------------------------------------------------

@artifact_processor
def keepsafe_media(context):
    files_found = [str(f) for f in context.get_files_found()]
    media_index = _media_file_index(files_found)
    data_list = []
    source_files = set()

    for user, db_path in _db_paths(files_found, "mediaDb"):
        docs = list(_read_cblite(db_path))
        albums = {doc_id: doc.get("name", "") for doc_id, doc, _ in docs
                  if doc and doc.get("modelType") == "album"}
        source_files.add(db_path)

        for doc_id, doc, purged in docs:
            if purged:
                data_list.append(("", "", "", "", "", "", "", "", "", "", "", "", None, None, user, doc_id,
                                  "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
                                  "", "", "", "Yes"))
                continue
            if not doc or doc.get("modelType") != "file":
                continue
            file_type = doc.get("type", "")
            media = [m for m in doc.get("media") or [] if isinstance(m, dict)]
            original = next((m for m in media if m.get("type") == file_type), media[0] if media else {})

            folder = doc_id.replace("-", "").lower()
            original_path = media_index.get((user, folder, str(original.get("type", "")).upper())) if user else None
            thumb_path = (media_index.get((user, folder, "THUMBNAIL")) or media_index.get((user, folder, "PREVIEW"))
                          if user else None)
            original_ref = check_in_media(original_path, doc_id) if original_path else None
            thumb_ref = check_in_media(thumb_path, f"{doc_id} thumbnail") if thumb_path else None
            for path in (original_path, thumb_path):
                if path:
                    source_files.add(path)

            album_id = doc.get("albumId", "")
            file_meta = _file_metadata(original_path, original.get("mimeType", ""))
            data_list.append((
                file_meta["capture_utc"],
                _utc(doc.get("createdAt")),
                _utc(doc.get("importedAt")),
                file_meta["capture_raw"],
                file_meta["source"],
                file_meta["make"],
                file_meta["model"],
                file_meta["software"],
                file_meta["lat"],
                file_meta["lon"],
                file_meta["alt"],
                file_meta["note"],
                thumb_ref,
                original_ref,
                user,
                doc_id,
                file_type,
                original.get("mimeType", ""),
                album_id,
                albums.get(album_id, ""),
                doc.get("vaultType", ""),
                _yes_no(doc.get("isInTrash")),
                _utc(doc.get("movedToTrashAt")),
                _yes_no(doc.get("isDeleted")),
                original.get("width", ""),
                original.get("height", ""),
                original.get("dataSize", ""),
                original.get("duration", ""),
                original.get("localHash", ""),
                original.get("etag", ""),
                doc.get("originalFilename", ""),
                doc.get("backupState", ""),
                _yes_no(doc.get("isShared")),
                doc.get("ownerId", ""),
                "No",
            ))

    data_headers = (
        ("Date/Time In File (UTC)", "datetime"),
        ("Created At", "datetime"),
        ("Imported At", "datetime"),
        "Date/Time In File (as stored)",
        "Metadata Source",
        "Make",
        "Model",
        "Software",
        "Latitude",
        "Longitude",
        "Altitude",
        "File Metadata Note",
        ("Thumbnail", "media"),
        ("Media", "media"),
        "Android User",
        "ID",
        "Type",
        "MIME Type",
        "Album ID",
        "Album Name",
        "Vault Type",
        "Is In Trash",
        ("Moved To Trash At", "datetime"),
        "Is Deleted",
        "Width",
        "Height",
        "Data Size",
        "Duration",
        "Local Hash",
        "ETag",
        "Original Filename",
        "Backup State",
        "Is Shared",
        "Owner ID",
        "In kv_del_default",
    )
    return data_headers, data_list, "\n".join(sorted(source_files))


@artifact_processor
def keepsafe_albums(context):
    files_found = [str(f) for f in context.get_files_found()]
    data_list = []
    source_files = set()

    for user, db_path in _db_paths(files_found, "mediaDb"):
        docs = [(doc_id, doc) for doc_id, doc, _ in _read_cblite(db_path) if doc]
        counts = {}
        for _doc_id, doc in docs:
            if doc.get("modelType") == "file":
                counts[doc.get("albumId")] = counts.get(doc.get("albumId"), 0) + 1
        source_files.add(db_path)
        for doc_id, doc in docs:
            if doc.get("modelType") != "album":
                continue
            data_list.append((
                _utc(doc.get("createdAt")),
                doc.get("name", ""),
                user,
                doc_id,
                doc.get("type", ""),
                doc.get("specialType", ""),
                counts.get(doc_id, 0),
                _yes_no(doc.get("isDeleted")),
                _yes_no(doc.get("isShared")),
                ", ".join(str(s) for s in doc.get("sharedWith") or []),
                doc.get("ownerId", ""),
            ))

    data_headers = (
        ("Created At", "datetime"),
        "Name",
        "Android User",
        "ID",
        "Type",
        "Special Type",
        "File Count",
        "Is Deleted",
        "Is Shared",
        "Shared With",
        "Owner ID",
    )
    return data_headers, data_list, "\n".join(sorted(source_files))


@artifact_processor
def keepsafe_breakins(context):
    files_found = [str(f) for f in context.get_files_found()]
    photos = {}
    for f in files_found:
        if "/com.kii.safe/files/breakin/" in f.replace("\\", "/") and not os.path.isdir(f) and _android_user(f):
            photos.setdefault((_android_user(f), os.path.basename(f)), f)
    data_list = []
    source_files = set()

    for user, db_path in _db_paths(files_found, "breakinDb"):
        source_files.add(db_path)
        for doc_id, doc, _purged in _read_cblite(db_path):
            if not doc or doc.get("modelType") != "breakIn":
                continue
            name = os.path.basename(str(doc.get("photoFileUri", "")).replace("\\", "/"))
            photo_path = photos.get((user, name)) if user else None
            photo_ref, photo_format = None, ""
            if photo_path:
                source_files.add(photo_path)
                mime_type, extension = _sniff_image(photo_path)
                if mime_type:
                    photo_format = mime_type
                    photo_ref = check_in_media(photo_path, doc_id, force_type=mime_type, force_extension=extension)
                else:
                    photo_format = "not a JPEG, PNG or WebP image"
            data_list.append((
                _utc(doc.get("timeCaptured"), millis=True),
                photo_ref,
                photo_format,
                user,
                doc.get("attemptedPin", ""),
                _yes_no(doc.get("isPinLockType")),
                _yes_no(doc.get("isRead")),
                doc.get("photoFileUri", ""),
                doc_id,
            ))

    data_headers = (
        ("Time Captured", "datetime"),
        ("Photo", "media"),
        "Photo Format (sniffed)",
        "Android User",
        "Attempted PIN",
        "Is PIN Lock Type",
        "Is Read",
        "Photo File URI",
        "ID",
    )
    return data_headers, data_list, "\n".join(sorted(source_files))


@artifact_processor
def keepsafe_browser(context):
    files_found = [str(f) for f in context.get_files_found()]
    data_list = []
    source_files = set()

    for user, db_path in _db_paths(files_found, "browserDb"):
        source_files.add(db_path)
        docs = [doc for _id, doc, _ in _read_cblite(db_path) if doc]
        current = {d.get("currentTabId") for d in docs if d.get("modelType") == "browserSession"}
        engine = next((d.get("searchEngine", "") for d in docs if d.get("modelType") == "browserSession"), "")
        for doc in docs:
            if doc.get("modelType") != "browserTab":
                continue
            data_list.append((
                _utc(doc.get("createdAt"), millis=True),
                _utc(doc.get("lastAccessTime"), millis=True),
                doc.get("title", ""),
                doc.get("url", ""),
                "Yes" if doc.get("id") in current else "No",
                engine,
                user,
                doc.get("id", ""),
                doc.get("ownerId", ""),
            ))

    data_headers = (
        ("Created At", "datetime"),
        ("Last Access Time", "datetime"),
        "Title",
        "URL",
        "Matches Session currentTabId",
        "Session Search Engine",
        "Android User",
        "ID",
        "Owner ID",
    )
    return data_headers, data_list, "\n".join(sorted(source_files))


# ---------------------------------------------------------------------------
# Minimal MessagePack decoder for files/accountsv2.mpack.
# ---------------------------------------------------------------------------

class _MsgpackError(ValueError):
    pass


def _msgpack_unpack(data):
    pos = 0

    def read(n):
        nonlocal pos
        if pos + n > len(data):
            raise _MsgpackError(f"truncated at offset {pos}")
        chunk = data[pos:pos + n]
        pos += n
        return chunk

    def size(n_bytes):
        return int.from_bytes(read(n_bytes), "big")

    def value():
        tag = read(1)[0]
        if tag <= 0x7F:
            return tag
        if tag >= 0xE0:
            return tag - 0x100
        if 0x80 <= tag <= 0x8F:
            return {value(): value() for _ in range(tag & 0x0F)}
        if 0x90 <= tag <= 0x9F:
            return [value() for _ in range(tag & 0x0F)]
        if 0xA0 <= tag <= 0xBF:
            return read(tag & 0x1F).decode("utf-8", "replace")
        if tag in (0xC0, 0xC2, 0xC3):
            return {0xC0: None, 0xC2: False, 0xC3: True}[tag]
        if tag in (0xC4, 0xC5, 0xC6):
            return bytes(read(size(1 << (tag - 0xC4))))
        if tag in (0xC7, 0xC8, 0xC9):
            length = size(1 << (tag - 0xC7))
            read(1)
            return bytes(read(length))
        if tag == 0xCA:
            return struct.unpack(">f", read(4))[0]
        if tag == 0xCB:
            return struct.unpack(">d", read(8))[0]
        if 0xCC <= tag <= 0xCF:
            return size(1 << (tag - 0xCC))
        if 0xD0 <= tag <= 0xD3:
            return int.from_bytes(read(1 << (tag - 0xD0)), "big", signed=True)
        if 0xD4 <= tag <= 0xD8:
            read(1)
            return bytes(read(1 << (tag - 0xD4)))
        if tag in (0xD9, 0xDA, 0xDB):
            return read(size(1 << (tag - 0xD9))).decode("utf-8", "replace")
        if tag in (0xDC, 0xDD):
            return [value() for _ in range(size(2 if tag == 0xDC else 4))]
        if tag in (0xDE, 0xDF):
            return {value(): value() for _ in range(size(2 if tag == 0xDE else 4))}
        raise _MsgpackError(f"unsupported tag 0x{tag:02x} at offset {pos - 1}")

    return value()


# (record type in key 4, field key, label)
_ACCOUNT_FIELDS = (
    (6, 22, "Package"),
    (6, 16, "App Version Code"),
    (5, 10, "Email"),
    (20, 12, "Email"),
    (1, 9, "Owner ID"),
    (6, 15, "Device Name"),
    (6, 13, "Device ID"),
    (6, 10, "Device UUID"),
    (6, 17, "Country"),
    (20, 14, "Language"),
    (6, 25, "Firebase Push Token"),
)


def _account_rows(files_found, source_files, user):
    """(group, field, value, utc, stored key) rows from files/accountsv2.mpack."""
    data_list = []
    for path in sorted(f for f in files_found if f.replace("\\", "/").endswith("/files/accountsv2.mpack")
                       and _android_user(f) == user):
        try:
            with open(path, "rb") as file_obj:
                records = _msgpack_unpack(file_obj.read())
        except (OSError, _MsgpackError) as ex:
            logfunc(f"KeepSafe: error reading {path}: {ex}")
            continue
        if not isinstance(records, list):
            continue
        source_files.add(path)
        records = [r for r in records if isinstance(r, dict)]
        for record_type, key, label in _ACCOUNT_FIELDS:
            for record in records:
                if record.get(4) != record_type or record.get(key) in (None, ""):
                    continue
                data_list.append((
                    "Account",
                    label,
                    record[key],
                    "",
                    f"record {record.get(1, '')} (type {record_type}), key {key}",
                ))
    return data_list


# Groups in report order.
_GROUPS = (
    "Account",
    "Account & Login",
    "Install & Usage",
    "Device Identifiers",
    "Lock & Security",
    "Appearance",
    "Trash",
    "Private Browser & Web",
)

# (group, file, preference name, label, unit for _pref_time or None)
_SETTINGS = (
    ("Account & Login", "com.kii.keepsafe.preferences.xml", "signup-date", "Sign-up Date (YYYYMMDD, no time or zone)", None),
    ("Account & Login", "com.kii.safe_preferences.xml", "login_time", "Login Time", "ms"),
    ("Account & Login", "com.kii.safe_preferences.xml", "session-last-activity-time", "Session Last Activity", "ms"),
    ("Account & Login", "device_location.xml", "billing_country", "Billing Country", None),
    ("Install & Usage", "com.kii.keepsafe.preferences.xml", "install-timestamp", "Install Time", "s"),
    ("Install & Usage", "appsflyer-data.xml", "appsFlyerFirstInstall", "First Install (AppsFlyer)", "af"),
    ("Install & Usage", "com.google.android.gms.measurement.prefs.xml", "first_open_time", "First Open (Google Analytics)", "ms"),
    ("Install & Usage", "com.kii.keepsafe.preferences.xml", "initial-install-version-name", "Initial Install Version", None),
    ("Install & Usage", "com.kii.safe_preferences.xml", "last_update_time", "Last Update Time", "ms"),
    ("Install & Usage", "com.kii.keepsafe.preferences.xml", "app-launches-count", "app-launches-count (as stored)", None),
    ("Install & Usage", "com.kii.keepsafe.preferences.xml", "app-lifetime-open-count", "app-lifetime-open-count (as stored)", None),
    ("Install & Usage", "Usage-Metrics.xml", "LAUNCH_COUNT", "LAUNCH_COUNT (as stored)", None),
    ("Device Identifiers", "device-id", "id", "KeepSafe Device ID", None),
    ("Device Identifiers", "internal-device-id", "id", "KeepSafe Internal Device ID", None),
    ("Device Identifiers", "com.amplitude.api.$default_instance.com.kii.safe.xml", "device_id", "Device ID (Amplitude)", None),
    ("Device Identifiers", "appsflyer-data.xml", "AF_INSTALLATION", "Install ID (AppsFlyer)", None),
    ("Lock & Security", "com.kii.safe_preferences.xml", "key-last-saved-pin-hash", "PIN Hash (as stored)", None),
    ("Lock & Security", "com.kii.safe_preferences.xml", "key-new-real-password", "key-new-real-password (as stored)", None),
    ("Lock & Security", "com.kii.safe_preferences.xml", "pref_lock_type", "Lock Type (as stored)", None),
    ("Lock & Security", "com.kii.safe_preferences.xml", "pin-entry-number-of-tries", "PIN Entry Tries", None),
    ("Lock & Security", "secret_door_preferences.xml", "secret_door", "Secret Door (selected, not proof it is active)", None),
    ("Appearance", "com.kii.safe_preferences.xml", "pref_lock_style", "Lock Style", None),
    ("Appearance", "com.kii.safe_preferences.xml", "prev_pref_pin_theme", "Previous PIN Theme (as stored)", None),
    ("Appearance", "theme_preferences.xml", "appTheme", "App Theme Color", None),
    ("Appearance", "theme_preferences.xml", "darkMode", "Dark Mode", None),
    ("Trash", "trash-preferences.xml", "first-move-to-trash", "First Move To Trash", "ms"),
    ("Trash", "trash-preferences.xml", "last-item-added-time-in-millis", "Last Item Added To Trash", "ms"),
    ("Trash", "trash-preferences.xml", "last-trash-view-time-in-millis", "Last Trash View", "ms"),
    ("Private Browser & Web", "browser_privacy.xml", "last_successful_update_at", "Browser Blocklist Last Updated", "ms"),
    ("Private Browser & Web", "browser_privacy.xml", "active_blocklist_version", "Browser Blocklist Version", None),
)


def _pref_time(value, unit):
    """UTC datetime for a preference value: 's'/'ms' epoch, or 'af' for AppsFlyer's
    'YYYY-MM-DD_HHMMSS+hhmm' local time with offset."""
    try:
        if unit == "af":
            return datetime.strptime(str(value), "%Y-%m-%d_%H%M%S%z").astimezone(timezone.utc)
        return _utc(int(value), millis=unit == "ms")
    except (TypeError, ValueError, OverflowError, OSError):
        return ""


def _read_prefs(path):
    """name -> value for a shared_prefs XML file, or the top-level keys of a JSON file
    (files/device-id and files/internal-device-id)."""
    try:
        if not path.lower().endswith(".xml"):
            with open(path, encoding="utf-8") as file_obj:
                data = json.load(file_obj)
            return {str(k): v for k, v in data.items()} if isinstance(data, dict) else {}
        root = ET.parse(path).getroot()
    except (OSError, ValueError, ET.ParseError) as ex:
        logfunc(f"KeepSafe: error reading {path}: {ex}")
        return {}
    return {node.get("name"): node.get("value", node.text) for node in root}


@artifact_processor
def keepsafe_account(context):
    files_found = [str(f) for f in context.get_files_found()]
    users = sorted({_android_user(f) for f in files_found} - {""}, key=int)
    unscoped = [f for f in files_found if not _android_user(f) and not os.path.isdir(f)]
    if unscoped:
        logfunc(f"KeepSafe: {len(unscoped)} file(s) name no Android user in their path and are not reported")

    source_files = set()
    data_list = []
    for user in users:
        user_files = [f for f in files_found if _android_user(f) == user and not os.path.isdir(f)]
        user_rows = _account_rows(user_files, source_files, user)
        _preference_rows(user_files, source_files, user_rows)
        user_rows.sort(key=lambda row: _GROUPS.index(row[0]))
        data_list.extend((user,) + row for row in user_rows)

    # The HTML report sorts on the first column, so a row number keeps the user and group order.
    data_list = [(index,) + row for index, row in enumerate(data_list, 1)]
    data_headers = ("#", "Android User", "Group", "Field", "Value", ("Value as UTC", "datetime"), "Stored Key")
    return data_headers, data_list, "\n".join(sorted(source_files))


def _preference_rows(files_found, source_files, data_list):
    """Preference, Amplitude and WebView Local Storage rows for one Android user's files."""
    by_name = {}
    for path in files_found:
        by_name.setdefault(os.path.basename(path), []).append(path)
    cache = {}
    for group, file_name, key, label, unit in _SETTINGS:
        for path in sorted(by_name.get(file_name, [])):
            prefs = cache.setdefault(path, _read_prefs(path))
            if key not in prefs:
                continue
            value = prefs[key]
            converted = _pref_time(value, unit) if unit else ""
            source_files.add(path)
            data_list.append((group, label, value, converted, key))

    for path in sorted(f for f in files_found if f.replace("\\", "/").endswith("/databases/com.amplitude.api")):
        db = open_sqlite_db_readonly(path)
        if db is None:
            continue
        try:
            stored = dict(db.execute("SELECT key, value FROM long_store").fetchall())
        except sqlite3.Error as ex:
            logfunc(f"KeepSafe: error reading {path}: {ex}")
            stored = {}
        finally:
            db.close()
        for key, label in (("last_event_time", "Last Analytics Event (Amplitude)"),
                           ("previous_session_id", "Last Session Start (Amplitude)")):
            if key in stored:
                source_files.add(path)
                data_list.append(("Account & Login", label, stored[key], _pref_time(stored[key], "ms"), key))

    leveldb_dirs = sorted({os.path.dirname(f) for f in files_found
                           if "/app_webview/Default/Local Storage/leveldb/" in f.replace("\\", "/")})
    for leveldb_dir in leveldb_dirs:
        for origin, text, record_file in _help_center_visits(leveldb_dir):
            try:
                when = datetime.strptime(text.split(" (")[0], "%a %b %d %Y %H:%M:%S GMT%z")
            except ValueError:
                when = ""
            source_files.add(record_file)
            data_list.append(("Private Browser & Web", "Help Center Visit (WebView Local Storage)", f"{text} [{origin}]",
                              when.astimezone(timezone.utc) if when else "", "Local Storage"))


def _help_center_visits(leveldb_dir):
    """(origin, date text, file) for each live Local Storage key of a getkeepsafe.com origin
    whose name is a JavaScript Date string. Read with ccl_leveldb; for each key only the
    record with the highest sequence number counts, and a key whose latest record is a
    deletion is not reported."""
    try:
        records = list(ccl_leveldb.RawLevelDb(leveldb_dir).iterate_records_raw())
    except (OSError, ValueError, KeyError, IndexError, struct.error) as ex:
        logfunc(f"KeepSafe: error reading the LevelDB in {leveldb_dir}: {ex}")
        return []
    latest = {}
    for record in records:
        current = latest.get(record.user_key)
        if current is None or record.seq > current.seq:
            latest[record.user_key] = record
    visits = []
    for key, record in sorted(latest.items(), key=lambda item: item[1].seq):
        match = _HELP_VISIT_KEY_RE.fullmatch(key)
        if not match or record.state != ccl_leveldb.KeyState.Live:
            continue
        visits.append((match.group(1).decode("utf-8", "replace"), match.group(2).decode("latin-1"),
                       str(record.origin_file)))
    return visits


# A Local Storage key of a getkeepsafe.com origin whose name is a JavaScript Date string:
# "_" + origin + "\x00", then 0x01 and the key name in Latin-1.
_HELP_VISIT_KEY_RE = re.compile(
    rb"_(https://[a-z0-9.-]*getkeepsafe\.com)\x00\x01"
    rb"([A-Z][a-z]{2} [A-Z][a-z]{2} \d{2} \d{4} \d{2}:\d{2}:\d{2} GMT[+-]\d{4}(?: \([^)\x00]{1,60}\))?)"
)
