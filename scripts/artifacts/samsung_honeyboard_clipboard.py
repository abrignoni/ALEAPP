"""
Samsung Honeyboard — Clipboard History & Image Clips
ALEAPP module

Parses:
  1. ClipItem.db      — clipboard text history (live entries)
  2. ClipItem.db-wal  — clip_table rows from earlier committed states in the WAL
  3. clip files       — clipboard image clips (JPEG), with the package named in
                        the Samsung trailer's Captured_App_Info field

Supersedes the original SamsungHoneyboard.py (@segumarc), adding WAL
recovery (now through scripts/sqlite_wal.py), Samsung SEFT source-app decoding,
dual-schema support, and packages.xml UID resolution.

Authors: @segumarc (original Honeyboard artifacts); Al3x101 (MSAB) — rewrite
"""

__artifacts_v2__ = {
    "get_honeyboard_clipboard_live": {
        "name": "Samsung Honeyboard - Clipboard (Live entries)",
        "description": (
            "Parses ClipItem.db clipboard text entries. Supports both the old "
            "schema (caller_app_uid) and new schema (caller_package_name); "
            "old-schema numeric UIDs are resolved via packages.xml when present. "
            "The type integer is shown with a label (1 Text, 2 Intent, 3 URI, "
            "4 HTML/Rich Text; the source for these labels is not recorded) and "
            "the html and uri columns are reported where the table has them."
        ),
        "author": "@segumarc, Al3x101, @AlexisBrignoni, Codex",
        "creation_date": "2024-05-30",
        "last_update_date": "2026-07-13",
        "requirements": "",
        "category": "Clipboard",
        "notes": (
            "Schema detected automatically. user_id is reported as stored; what "
            "each value stands for is not sourced here. Old-schema UIDs are "
            "resolved from the first packages.xml found in the extraction, read as "
            "text XML or binary ABX. A UID with no match is shown as UID:n and a "
            "stored 0 or empty UID as Unknown."
        ),
        # Match ClipItem.db*, not just ClipItem.db, so the -wal/-shm are
        # co-extracted — the live schema/rows can reside entirely in an
        # un-checkpointed WAL (a 4 KB main db is common).
        "paths": ('*/com.samsung.android.honeyboard/databases/ClipItem.db*',),
        "output_types": "standard",
        "artifact_icon": "clipboard",
        "sample_data": {
            "samsungs20_a13": "Android 13 | com.samsung.android.honeyboard | 11 rows",
            "samsunga53_a14": "Android 14 | com.samsung.android.honeyboard | 1 row",
            "sharon_a14": "Android 14 | com.samsung.android.honeyboard vc 560051300 | 19 rows",
            "anne_a15": "Android 15 | com.samsung.android.honeyboard vc 590202300 | 8 rows",
        },
    },
    "get_honeyboard_clipboard_deleted": {
        "name": "Samsung Honeyboard - Clipboard (Earlier WAL States)",
        "description": (
            "Reports clip_table rows held by an earlier committed state of ClipItem.db that is "
            "still in ClipItem.db-wal, when the current state does not hold a row with the same "
            "values in the reported columns. Each state is read by SQLite from a copy of the "
            "database whose log copy is cut at the end of a committed transaction."
        ),
        "author": "@AlexisBrignoni, Codex, Claude",
        "creation_date": "2026-07-13",
        "last_update_date": "2026-10-26",
        "requirements": "",
        "category": "Clipboard",
        "notes": (
            "State n is the database after the first n committed transactions in the log; state 0 "
            "is the database file without its log. First State and Last State are the oldest and "
            "newest states the row was read in. WAL State Status is 'Earlier version of a current "
            "row' when the current state holds the same id with different values, otherwise 'Not "
            "in current state', which does not establish who or what removed the row. Timestamp "
            "(UTC) is the earlier state's time_stamp read as Unix milliseconds; Current Row "
            "Timestamp (UTC) is the current state's time_stamp for that id, read the same way, and "
            "is empty for a row not in the current state. Type uses the live artifact's labels, "
            "whose source is not recorded. Only the log's current generation is read, up to its "
            "last checksum-valid commit; frames after it, frames left by an earlier generation, "
            "freelist pages and free space in the database file are not read, and the run log "
            "names how many frames were skipped when any were. Measured on samsungs20_a13, "
            "sharon_a14 and anne_a15 (2, 5 and 1 rows; 17, 27 and 12 committed transactions): "
            "every row's WAL State Status was 'Earlier version of a current row', and comparing "
            "all clip_table columns, time_stamp was the only one that differed, earlier than the "
            "current value on all 8, by between 27 ms and about 35 days; on one sharon_a14 row "
            "the two fall in the same second and the report shows them as equal. "
            "samsunga53_a14 (4 committed transactions) had none. User ID held 0 on all 8 rows; "
            "URI held the text null on all 8 rows, as stored; Type held Text on all 5 rows from "
            "sharon_a14 and on 7 of the 8; HTML Content was empty on 7; and First State equalled "
            "Last State on 7. The same rows came back from an independent rebuild that writes the "
            "log's page images onto a copy of the database. Why the app rewrites time_stamp is not "
            "sourced. Original Honeyboard work: @segumarc; earlier WAL parser: Al3x101 (MSAB)."
        ),
        # Match ClipItem.db* so the -wal is staged beside the database it belongs to.
        "paths": ('*/com.samsung.android.honeyboard/databases/ClipItem.db*',),
        "output_types": "standard",
        "artifact_icon": "clipboard",
        "sample_data": {
            "samsungs20_a13": "Android 13 | com.samsung.android.honeyboard | 2 rows",
            "samsunga53_a14": "Android 14 | com.samsung.android.honeyboard | 0 rows",
            "sharon_a14": "Android 14 | com.samsung.android.honeyboard | 5 rows",
            "anne_a15": "Android 15 | com.samsung.android.honeyboard | 1 row",
        },
    },
    "get_honeyboard_screenshot": {
        "name": "Samsung Honeyboard - Clipboard Image Clips",
        "description": (
            "Parses the image clips in the Honeyboard clipboard folder "
            "(extensionless JPEG 'clip' files). Reports the parent directory name as "
            "a time, EXIF DateTimeOriginal, the package named in the Samsung SEFT "
            "trailer, the image dimensions and the image itself. Files that are not "
            "JPEG and files under remote_send are skipped."
        ),
        "author": "@segumarc, Al3x101, @AlexisBrignoni, Codex",
        "creation_date": "2024-05-30",
        "last_update_date": "2026-10-04",
        "requirements": "Pillow (PIL) for EXIF and the image; SEFT decoding is pure Python.",
        "category": "Clipboard",
        "notes": (
            "Captured App Info Package is the package part of the comp value in the "
            "Captured_App_Info field of the trailer Samsung appends after the JPEG "
            "end marker (FF D9), as stored; what Samsung records in that field was "
            "not sourced. A file with no such field is shown as Unknown: 18 of the "
            "22 clips on samsungs20_a13, samsunga53_a14, sharon_a14 and anne_a15. "
            "Clip Folder Name Time is the parent directory name read as Unix "
            "milliseconds; what moment the app names the directory for was not "
            "sourced. On those 22 clips every directory name was 13 digits, and the "
            "clip file's modification time recorded in the archive was within one "
            "second before it. EXIF DateTimeOriginal is the stored text with the "
            "EXIF sub-second and offset values appended where present, and no time "
            "zone is applied. Image is the whole picture re-saved as PNG, not a "
            "reduced copy, and is blank when Pillow is not installed. Any JPEG clip "
            "is reported: the trailer named a screenshot (Samsung_Capture_Info) on 7 "
            "of the 22 clips, and the other 15 carried no trailer."
        ),
        "paths": ('*/com.samsung.android.honeyboard/clipboard/*/clip',),
        "output_types": "standard",
        "artifact_icon": "clipboard",
        "sample_data": {
            "samsungs20_a13": "Android 13 | com.samsung.android.honeyboard | 1 row",
            "samsunga53_a14": "Android 14 | com.samsung.android.honeyboard | 1 row",
            "sharon_a14": "Android 14 | com.samsung.android.honeyboard vc 560051300 | 17 rows",
            "anne_a15": "Android 15 | com.samsung.android.honeyboard vc 590202300 | 3 rows",
        },
    },
}

import base64
import datetime
import io
import json
import os
import sqlite3
import struct
import xml.etree.ElementTree as ET

try:
    from PIL import Image as _PIL_Image
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False

from scripts.ilapfuncs import (artifact_processor, logfunc, open_sqlite_db_readonly,
                               check_in_embedded_media, checkabx, abxread)
from scripts.sqlite_wal import EARLIER_VERSION, rows_not_in_current

# ClipData type codes
_TYPE_CODES = {1: "Text", 2: "Intent", 3: "URI", 4: "HTML/Rich Text"}

# Timezone-aware minimum used as a sort fallback for rows lacking a timestamp;
# mixing a naive datetime.min with tz-aware values raises TypeError.
_AWARE_MIN = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)

# EXIF SubIFD (capture-time tags live here, not in IFD0)
_EXIF_IFD = 0x8769
_TAG_DATETIME_ORIGINAL = 36867
_TAG_SUBSEC_ORIGINAL = 37521
_TAG_OFFSET_ORIGINAL = 36881


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ms_to_utc(value):
    """Convert a millisecond Unix timestamp to a UTC datetime."""
    if not value:
        return ""
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ""


def _decode_type(type_code):
    """Map a ClipData integer type code to a human-readable label."""
    try:
        return _TYPE_CODES.get(int(type_code), f"Type({type_code})")
    except (TypeError, ValueError):
        return str(type_code)


def _resolve_uid(uid, uid_map):
    """Resolve an old-schema numeric UID to a package name via the packages.xml map.

    Returns the package name if found, otherwise 'UID:<n>' (or 'Unknown').
    """
    if uid is None or uid == 0:
        return "Unknown"
    try:
        n = int(uid)
    except (TypeError, ValueError):
        return str(uid)
    return uid_map.get(n, f"UID:{n}")


def _build_uid_map(seeker):
    """Build a {uid: package_name} map from packages.xml in the extraction.

    packages.xml (/data/system/packages.xml) is present in full FFS extractions.
    On Android 12+ it is stored as binary ABX rather than text XML, so it is
    decoded with ALEAPP's checkabx/abxread helpers when needed. The seeker
    searches the whole extraction, not just the Honeyboard directory. Returns an
    empty dict when packages.xml is absent or cannot be parsed.
    """
    uid_map = {}
    if seeker is None:
        return uid_map
    try:
        pkg_files = seeker.search('*/packages.xml')
    except (AttributeError, OSError):
        return uid_map

    for f in pkg_files:
        f = str(f)
        try:
            tree = abxread(f, False) if checkabx(f) else ET.parse(f)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            # packages.xml is a best-effort secondary lookup; a malformed file
            # (partial/encrypted extraction, or an ABX the vendored decoder
            # rejects) must not abort clipboard parsing.
            logfunc(f"honeyboard_clipboard: could not parse {f}: {exc}")
            continue
        for pkg in tree.getroot().iter("package"):
            name = pkg.get("name", "")
            user_id = pkg.get("userId", "")
            if name and user_id:
                try:
                    uid_map[int(user_id)] = name
                except ValueError:
                    pass
        if uid_map:
            logfunc(f"honeyboard_clipboard: resolved {len(uid_map)} UIDs from {f}")
            break

    return uid_map


def _dedup_rows(rows, key):
    """Collapse rows that are identical apart from their bind-mount source path.

    Android exposes an app's data under several mirror paths (data/data,
    data/user/0, data_mirror/data_ce/...), so the same ClipItem.db — and hence
    the same clip — is parsed once per mirror. Rows with the same content
    signature are the same clip; keep the first occurrence and drop the rest.
    """
    seen = set()
    out = []
    for row in rows:
        sig = key(row)
        if sig not in seen:
            seen.add(sig)
            out.append(row)
    return out


def _clip_select(cols):
    """The clip_table query for the columns this ClipItem.db has.

    Returns (query, new_schema, has_html, has_uri).
    """
    new_schema = "caller_package_name" in cols
    has_html = "html" in cols
    has_uri = "uri" in cols
    app_col = "caller_package_name" if new_schema else "caller_app_uid"
    select_cols = ["id", "time_stamp", "type", "text", app_col]
    select_cols.append("user_id" if "user_id" in cols else "0 AS user_id")
    if has_html:
        select_cols.append("html")
    if has_uri:
        select_cols.append("uri")
    query = f"SELECT {', '.join(select_cols)} FROM clip_table ORDER BY time_stamp ASC"
    return query, new_schema, has_html, has_uri


def _clip_fields(row, new_schema, has_html, has_uri, uid_map):
    """(id, time_stamp, type, text, source app, user_id, html, uri) from a _clip_select row."""
    app_id = row[4]
    user_id = row[5] if row[5] is not None else 0
    html_val = row[6] if has_html and len(row) > 6 else ""
    uri_idx = 7 if has_html else 6
    uri_val = row[uri_idx] if has_uri and len(row) > uri_idx else ""
    source_app = app_id if (new_schema and app_id) else _resolve_uid(app_id, uid_map)
    return row[0], row[1], row[2], row[3], source_app, user_id, html_val, uri_val


# ---------------------------------------------------------------------------
# Samsung SEFT trailer parser
# ---------------------------------------------------------------------------

def _parse_seft_trailer(jpeg_data):
    """Decode the Samsung SEFT trailer from a clipboard image clip (JPEG).

    Samsung appends a proprietary trailer after the JPEG EOI marker (FF D9).
    The 'Captured_App_Info' field contains a Base64-encoded JSON object with a
    'comp' key in component form (package/class); what Samsung records there
    is not sourced.

    Returns a dict with keys: source_app_package, trailer_present, decode_error.
    """
    result = {"source_app_package": None, "trailer_present": False, "decode_error": None}

    eoi = jpeg_data.rfind(b"\xff\xd9")
    if eoi < 0 or len(jpeg_data) <= eoi + 2:
        return result

    trailer = jpeg_data[eoi + 2:]
    result["trailer_present"] = trailer.endswith(b"SEFT")

    ai_pos = trailer.find(b"Captured_App_Info")
    if ai_pos < 0:
        return result

    after = ai_pos + len(b"Captured_App_Info")
    b64_buf = bytearray()
    for byte in trailer[after: after + 1024]:
        if (48 <= byte <= 57 or 65 <= byte <= 90 or
                97 <= byte <= 122 or byte in (43, 47, 61)):
            b64_buf.append(byte)
        else:
            break

    if not b64_buf:
        result["decode_error"] = "No Base64 data after Captured_App_Info"
        return result

    for try_len in range(len(b64_buf) - (len(b64_buf) % 4), 3, -4):
        try:
            decoded = base64.b64decode(bytes(b64_buf[:try_len]), validate=True)
        except ValueError:
            continue
        if not decoded.rstrip().endswith(b"}"):
            continue
        try:
            comp = json.loads(decoded).get("comp", "")
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        if "/" in comp:
            result["source_app_package"] = comp.split("/", 1)[0]
        return result

    result["decode_error"] = "Could not find valid JSON in Captured_App_Info Base64 data"
    return result


# ---------------------------------------------------------------------------
# Artifact 1: Live clipboard entries from ClipItem.db
# ---------------------------------------------------------------------------

@artifact_processor
def get_honeyboard_clipboard_live(context):
    """Parse ClipItem.db for live (non-deleted) clipboard text entries.

    Schema detection:
      NEW — has column caller_package_name (package name string)
      OLD — has column caller_app_uid     (numeric UID, resolved via packages.xml)
    """
    files_found = context.get_files_found()
    seeker = context.get_seeker()
    data_list = []
    source_path = ""

    uid_map = _build_uid_map(seeker)

    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith("-wal") or file_found.endswith("-shm"):
            continue

        source_path = file_found
        try:
            db = open_sqlite_db_readonly(file_found)
            cur = db.cursor()

            cols = [row[1] for row in cur.execute("PRAGMA table_info(clip_table)")]
            if not cols:
                logfunc(f"honeyboard_clipboard: clip_table not found in {file_found}")
                db.close()
                continue

            query, new_schema, has_html, has_uri = _clip_select(cols)

            for row in cur.execute(query):
                clip_id, ts_ms, ctype, text, source_app, user_id, html_val, uri_val = _clip_fields(
                    row, new_schema, has_html, has_uri, uid_map)

                data_list.append((
                    _ms_to_utc(ts_ms),
                    clip_id,
                    _decode_type(ctype),
                    text or "",
                    source_app or "Unknown",
                    user_id,
                    "New (package name)" if new_schema else "Old (UID)",
                    html_val or "",
                    uri_val or "",
                ))
            db.close()

        except sqlite3.Error as exc:
            logfunc(f"honeyboard_clipboard: error reading {file_found}: {exc}")

    # Collapse identical rows produced by ClipItem.db bind-mount mirrors
    data_list = _dedup_rows(data_list, key=lambda r: r)

    data_headers = (
        ("Timestamp (UTC)", "datetime"),
        "ID",
        "Type",
        "Clipboard Content",
        "Source App",
        "User ID",
        "DB Schema",
        "HTML Content",
        "URI",
    )
    return data_headers, data_list, source_path


# ---------------------------------------------------------------------------
# Artifact 2: Clipboard rows from earlier committed states in ClipItem.db-wal
# ---------------------------------------------------------------------------

@artifact_processor
def get_honeyboard_clipboard_deleted(context):
    """Report clip_table rows held by an earlier committed state of ClipItem.db.

    Each committed state the -wal still holds is read by SQLite through
    scripts/sqlite_wal.py, with the same query as the live artifact. A row is
    reported when the current state does not hold it with the same values.
    """
    files_found = context.get_files_found()
    uid_map = _build_uid_map(context.get_seeker())
    data_list = []
    source_paths = set()

    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith(("-wal", "-shm", "-journal")):
            continue
        if not os.path.exists(file_found + "-wal"):
            logfunc(f"honeyboard_clipboard WAL states: no -wal beside {file_found}")
            continue

        db = open_sqlite_db_readonly(file_found)
        if db is None:
            continue
        current_times = {}
        try:
            cols = [row[1] for row in db.execute("PRAGMA table_info(clip_table)")]
            if cols:
                current_times = dict(db.execute("SELECT id, time_stamp FROM clip_table"))
        except sqlite3.Error as exc:
            logfunc(f"honeyboard_clipboard WAL states: error reading {file_found}: {exc}")
            cols = []
        finally:
            db.close()
        if not cols:
            logfunc(f"honeyboard_clipboard WAL states: clip_table not found in {file_found}")
            continue

        query, new_schema, has_html, has_uri = _clip_select(cols)
        try:
            _columns, earlier, wal = rows_not_in_current(file_found, query, key_columns=[0])
        except (OSError, sqlite3.Error) as exc:
            logfunc(f"honeyboard_clipboard WAL states: could not read the states of "
                    f"{file_found}: {exc}")
            continue
        logfunc(f"honeyboard_clipboard WAL states: {wal.summary()}")
        source_paths.add(file_found + "-wal")

        for item in earlier:
            clip_id, ts_ms, ctype, text, source_app, user_id, html_val, uri_val = _clip_fields(
                item.values, new_schema, has_html, has_uri, uid_map)
            current_ts = ""
            if item.status == EARLIER_VERSION:
                current_ts = _ms_to_utc(current_times.get(clip_id))
            data_list.append((
                _ms_to_utc(ts_ms),
                current_ts,
                clip_id,
                _decode_type(ctype),
                text or "",
                source_app or "Unknown",
                user_id,
                html_val or "",
                uri_val or "",
                item.status,
                item.first_state,
                item.last_state,
            ))

    # Collapse identical rows produced by ClipItem.db bind-mount mirrors
    data_list = _dedup_rows(data_list, key=lambda r: r)
    data_list.sort(key=lambda r: r[0] if isinstance(r[0], datetime.datetime) else _AWARE_MIN)

    data_headers = (
        ("Timestamp (UTC)", "datetime"),
        ("Current Row Timestamp (UTC)", "datetime"),
        "ID",
        "Type",
        "Clipboard Content",
        "Source App",
        "User ID",
        "HTML Content",
        "URI",
        "WAL State Status",
        "First State",
        "Last State",
    )
    return data_headers, data_list, "\n".join(sorted(source_paths))


# ---------------------------------------------------------------------------
# Artifact 3: Clipboard screenshot clips
# ---------------------------------------------------------------------------

@artifact_processor
def get_honeyboard_screenshot(context):
    """Parse clipboard image clips.

    Each 'clip' file is an extensionless JPEG in a sub-directory whose name is
    read as a millisecond Unix epoch value; what moment the app names the
    directory for is not sourced. Three data sources are combined per image:
      1. Parent directory name  -> read as Unix milliseconds
      2. EXIF DateTimeOriginal  -> stored text, sub-second and offset appended
      3. Samsung SEFT trailer   -> package part of Captured_App_Info comp

    Pillow is used for EXIF and the image; SEFT decoding is always available.
    """
    files_found = context.get_files_found()
    data_list = []
    source_path = ""

    for file_found in files_found:
        file_found = str(file_found)

        parent_dir = os.path.basename(os.path.dirname(file_found))
        if parent_dir == "remote_send":
            continue

        try:
            with open(file_found, "rb") as fh:
                jpeg_data = fh.read()
        except OSError as exc:
            logfunc(f"honeyboard_screenshot: cannot read {file_found}: {exc}")
            continue

        if jpeg_data[:2] != b"\xff\xd8":
            continue

        # Parent directory name read as a ms epoch value
        copy_ts = ""
        if parent_dir.isdigit():
            try:
                copy_ts = datetime.datetime.fromtimestamp(
                    int(parent_dir) / 1000, datetime.timezone.utc)
            except (ValueError, OverflowError, OSError):
                copy_ts = ""

        exif_capture_ts = ""
        width = height = None
        thumbnail = ""  # whole image as PNG; empty (not None) is the safe "no media" value

        if _PIL_AVAILABLE:
            try:
                img = _PIL_Image.open(file_found)
                width, height = img.size

                buf = io.BytesIO()
                img.save(buf, format="PNG")
                name = f"{parent_dir}_{os.path.basename(file_found)}.png"
                media_ref = check_in_embedded_media(file_found, buf.getvalue(), name)
                thumbnail = media_ref if media_ref else ""

                # Capture-time tags live in the EXIF SubIFD (0x8769)
                exif_ifd = img.getexif().get_ifd(_EXIF_IFD)
                dto = exif_ifd.get(_TAG_DATETIME_ORIGINAL, "")
                subsec = exif_ifd.get(_TAG_SUBSEC_ORIGINAL, "")
                offset = exif_ifd.get(_TAG_OFFSET_ORIGINAL, "")
                if dto:
                    exif_capture_ts = f"{dto}.{subsec}{offset}".strip(".")
            except (OSError, ValueError, struct.error) as exc:
                logfunc(f"honeyboard_screenshot: image/EXIF error on {file_found}: {exc}")
        else:
            logfunc("honeyboard_screenshot: Pillow not available — EXIF and images skipped.")

        seft = _parse_seft_trailer(jpeg_data)
        source_app = seft["source_app_package"] or "Unknown"
        if seft["decode_error"]:
            logfunc(f"honeyboard_screenshot: SEFT issue for {file_found}: {seft['decode_error']}")

        dimensions = f"{width} x {height} px" if width and height else ""

        data_list.append((
            copy_ts,
            exif_capture_ts or "",
            source_app,
            dimensions,
            thumbnail,
            context.get_relative_path(file_found),
        ))
        source_path = os.path.dirname(os.path.dirname(file_found))

    # Source path differs across mirrors; dedup on the remaining columns
    data_list = _dedup_rows(data_list, key=lambda r: r[:5])
    data_list.sort(key=lambda r: r[0] if isinstance(r[0], datetime.datetime) else _AWARE_MIN)

    data_headers = (
        ("Clip Folder Name Time", "datetime"),
        "EXIF DateTimeOriginal",
        "Captured App Info Package",
        "Dimensions",
        ("Image", "media"),
        "Source Path",
    )
    return data_headers, data_list, source_path
