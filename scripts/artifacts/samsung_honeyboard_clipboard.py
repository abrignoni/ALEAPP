"""
Samsung Honeyboard — Clipboard History & Screenshot Clips
ALEAPP module

Parses:
  1. ClipItem.db      — clipboard text history (live entries)
  2. ClipItem.db-wal  — deleted entries recovered from the SQLite WAL
  3. clip files       — clipboard screenshot images with Samsung SEFT trailer
                        source-app extraction

Supersedes the original SamsungHoneyboard.py (@segumarc), adding WAL deleted-entry
recovery, Samsung SEFT source-app decoding, dual-schema support, and packages.xml
UID resolution.

Authors: @segumarc (original Honeyboard artifacts); Al3x101 (MSAB) — rewrite
"""

__artifacts_v2__ = {
    "get_honeyboard_clipboard_live": {
        "name": "Samsung Honeyboard - Clipboard (Live entries)",
        "description": (
            "Parses ClipItem.db clipboard text entries. Supports both the old "
            "schema (caller_app_uid) and new schema (caller_package_name); "
            "old-schema numeric UIDs are resolved via packages.xml when present. "
            "Decodes ClipData type codes and surfaces html/uri columns."
        ),
        "author": "@segumarc, Al3x101",
        "creation_date": "2024-05-30",
        "last_update_date": "2026-07-13",
        "requirements": "",
        "category": "Clipboard",
        "notes": (
            "Schema detected automatically. user_id 0 = primary user; "
            "150 = Samsung Secure Folder. Old-schema UIDs are resolved from "
            "packages.xml (text XML or, on Android 12+, binary ABX)."
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
        "name": "Samsung Honeyboard - Clipboard (WAL-recovered deleted entries)",
        "description": (
            "Recovers deleted clipboard entries from ClipItem.db-wal via direct "
            "SQLite WAL frame B-tree parsing with last-frame-wins deduplication. "
            "No external tools required. Entries appear only if the device was "
            "extracted before the WAL was checkpointed."
        ),
        "author": "Al3x101",
        "creation_date": "2026-07-13",
        "last_update_date": "2026-07-13",
        "requirements": "",
        "category": "Clipboard",
        "notes": (
            "WAL Frame and WAL Page columns identify the exact location of each "
            "recovered record for verification. A blank result means either no WAL "
            "was present or it had already been checkpointed before extraction. "
            "Records whose payload spills onto SQLite overflow pages are not "
            "reassembled, so very long clips may be truncated."
        ),
        # Match ClipItem.db* so the main .db is co-extracted alongside the -wal;
        # the main db supplies live row IDs used to exclude non-deleted rows.
        "paths": ('*/com.samsung.android.honeyboard/databases/ClipItem.db*',),
        "output_types": "standard",
        "artifact_icon": "clipboard",
        "sample_data": {
            "samsungs20_a13": "Android 13 | com.samsung.android.honeyboard | 0 rows",
            "samsunga53_a14": "Android 14 | com.samsung.android.honeyboard | 0 rows",
            "sharon_a14": "Android 14 | com.samsung.android.honeyboard | 0 rows",
            "anne_a15": "Android 15 | com.samsung.android.honeyboard | 0 rows",
        },
    },
    "get_honeyboard_screenshot": {
        "name": "Samsung Honeyboard - Clipboard Screenshot Clips",
        "description": (
            "Parses clipboard screenshot images (extensionless JPEG 'clip' files). "
            "Extracts copy timestamp (parent directory name), EXIF capture time, "
            "source app from the Samsung SEFT trailer, image dimensions, and a "
            "thumbnail."
        ),
        "author": "@segumarc, Al3x101",
        "creation_date": "2024-05-30",
        "last_update_date": "2026-07-13",
        "requirements": "Pillow (PIL) for EXIF and thumbnail; SEFT decoding is pure Python.",
        "category": "Clipboard",
        "notes": (
            "Source app decoded from Samsung's proprietary SEFT trailer appended "
            "after the JPEG EOI marker (FF D9) — invisible to standard viewers and "
            "absent from EXIF. Copy time from the parent directory name "
            "(millisecond Unix epoch); capture time from EXIF DateTimeOriginal."
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


# ---------------------------------------------------------------------------
# WAL frame-by-frame B-tree parser
# ---------------------------------------------------------------------------

class _WalRecovery:
    """Parse a SQLite WAL file and extract B-tree leaf cell payloads.

    Implements last-frame-wins deduplication: when the same database page
    appears in multiple frames, only the last frame is parsed. Earlier frames
    for the same page are superseded intermediate states and are skipped.

    Payloads that spill onto SQLite overflow pages are not reassembled, so a
    very long clipboard entry may be truncated to its in-cell portion.
    """

    WAL_MAGIC_LE = 0x377F0682
    WAL_MAGIC_BE = 0x377F0683
    FRAME_HDR = 24
    FILE_HDR = 32

    def __init__(self, wal_path):
        self.wal_path = wal_path
        self.page_size = 4096
        self.records = []
        self.error = None

    def parse(self):
        try:
            with open(self.wal_path, "rb") as fh:
                data = fh.read()
        except OSError as exc:
            self.error = str(exc)
            return False

        if len(data) < self.FILE_HDR:
            self.error = "WAL too small"
            return False

        magic = struct.unpack(">I", data[0:4])[0]
        if magic not in (self.WAL_MAGIC_LE, self.WAL_MAGIC_BE):
            self.error = f"Bad WAL magic 0x{magic:08x}"
            return False

        ps_raw = struct.unpack(">I", data[8:12])[0]
        self.page_size = 65536 if ps_raw in (0, 1) else ps_raw

        # Collect all frames — later frames overwrite earlier ones for the same
        # page_num (last-frame-wins, per SQLite WAL read semantics).
        page_to_frame = {}
        off = self.FILE_HDR
        fn = 0
        while off + self.FRAME_HDR + self.page_size <= len(data):
            fh_bytes = data[off: off + self.FRAME_HDR]
            page = data[off + self.FRAME_HDR: off + self.FRAME_HDR + self.page_size]
            page_num = struct.unpack(">I", fh_bytes[0:4])[0]
            page_to_frame[page_num] = {"frame": fn, "page_num": page_num, "data": page}
            off += self.FRAME_HDR + self.page_size
            fn += 1

        # Parse only the winning (most recent) frame for each page
        for fr in page_to_frame.values():
            try:
                for rec in self._parse_leaf_page(fr["data"]):
                    rec["frame"] = fr["frame"]
                    rec["page_num"] = fr["page_num"]
                    self.records.append(rec)
            except (struct.error, IndexError, ValueError):
                continue
        return True

    @staticmethod
    def _read_varint(data, off):
        result = 0
        for i in range(9):
            if off + i >= len(data):
                return result, i
            b = data[off + i]
            if i == 8:
                result = (result << 8) | b
                return result, 9
            result = (result << 7) | (b & 0x7F)
            if not (b & 0x80):
                return result, i + 1
        return result, 9

    def _parse_leaf_page(self, page):
        if len(page) < 8 or page[0] != 0x0D:
            return []
        num_cells = struct.unpack(">H", page[3:5])[0]
        ptrs = []
        for i in range(num_cells):
            o = 8 + i * 2
            if o + 2 > len(page):
                break
            ptrs.append(struct.unpack(">H", page[o: o + 2])[0])
        out = []
        for cp in ptrs:
            try:
                rec = self._parse_cell(page, cp)
                if rec:
                    out.append(rec)
            except (struct.error, IndexError, ValueError):
                continue
        return out

    def _parse_cell(self, page, off):
        if off >= len(page):
            return None
        payload_size, n = self._read_varint(page, off)
        off += n
        row_id, n = self._read_varint(page, off)
        off += n
        payload = page[off: off + payload_size]
        return {"row_id": row_id, "payload": payload}

    def decoded_records(self):
        out = []
        for rec in self.records:
            try:
                cols = self._decode_payload(rec["payload"])
            except (struct.error, IndexError, ValueError):
                continue
            if cols is not None:
                out.append({
                    "row_id": rec["row_id"],
                    "columns": cols,
                    "frame": rec["frame"],
                    "page_num": rec["page_num"],
                })
        return out

    def _decode_payload(self, payload):
        if not payload:
            return None
        hdr_size, n = self._read_varint(payload, 0)
        if hdr_size < 1 or hdr_size > len(payload):
            return None
        serial_types = []
        p = n
        while p < hdr_size:
            t, m = self._read_varint(payload, p)
            serial_types.append(t)
            p += m
        values = []
        body = hdr_size
        for t in serial_types:
            v, used = self._read_value(payload, body, t)
            values.append(v)
            body += used
        return values

    def _read_value(self, data, off, serial):
        if serial == 0:
            return (None, 0)
        if serial == 1:
            return (int.from_bytes(data[off:off + 1], "big", signed=True), 1)
        if serial == 2:
            return (int.from_bytes(data[off:off + 2], "big", signed=True), 2)
        if serial == 3:
            return (int.from_bytes(data[off:off + 3], "big", signed=True), 3)
        if serial == 4:
            return (int.from_bytes(data[off:off + 4], "big", signed=True), 4)
        if serial == 5:
            return (int.from_bytes(data[off:off + 6], "big", signed=True), 6)
        if serial == 6:
            return (int.from_bytes(data[off:off + 8], "big", signed=True), 8)
        if serial == 7:
            return (struct.unpack(">d", data[off:off + 8])[0], 8)
        if serial in (8, 9):
            return (serial - 8, 0)
        if serial >= 12 and serial % 2 == 0:
            n = (serial - 12) // 2
            return (data[off:off + n], n)
        if serial >= 13 and serial % 2 == 1:
            n = (serial - 13) // 2
            return (data[off:off + n].decode("utf-8", errors="replace"), n)
        return (None, 0)


# ---------------------------------------------------------------------------
# Samsung SEFT trailer parser
# ---------------------------------------------------------------------------

def _parse_seft_trailer(jpeg_data):
    """Decode the Samsung SEFT trailer from a clipboard screenshot JPEG.

    Samsung appends a proprietary trailer after the JPEG EOI marker (FF D9).
    The 'Captured_App_Info' field contains a Base64-encoded JSON object whose
    'comp' key identifies the Android component on screen at capture time.

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

            new_schema = "caller_package_name" in cols
            has_html = "html" in cols
            has_uri = "uri" in cols
            has_uid = "user_id" in cols

            app_col = "caller_package_name" if new_schema else "caller_app_uid"
            select_cols = ["id", "time_stamp", "type", "text", app_col]
            select_cols.append("user_id" if has_uid else "0 AS user_id")
            if has_html:
                select_cols.append("html")
            if has_uri:
                select_cols.append("uri")

            query = f"SELECT {', '.join(select_cols)} FROM clip_table ORDER BY time_stamp ASC"

            for row in cur.execute(query):
                clip_id = row[0]
                ts_ms = row[1]
                ctype = row[2]
                text = row[3]
                app_id = row[4]
                user_id = row[5] if row[5] is not None else 0
                html_val = row[6] if has_html and len(row) > 6 else ""
                uri_idx = 7 if has_html else 6
                uri_val = row[uri_idx] if has_uri and len(row) > uri_idx else ""

                source_app = app_id if (new_schema and app_id) else _resolve_uid(app_id, uid_map)

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
# Artifact 2: Deleted entries recovered from ClipItem.db-wal
# ---------------------------------------------------------------------------

@artifact_processor
def get_honeyboard_clipboard_deleted(context):
    """Recover deleted clipboard entries from ClipItem.db-wal.

    Uses direct SQLite WAL frame B-tree parsing with last-frame-wins
    deduplication — no external tools, no modification of original files.

    Column order in WAL rows (from PRAGMA table_info on observed devices):
      0:id  1:time_stamp  2:type  3:text  4:html  5:uri  6:uri_list
      7:mime_type  8:caller_app_uid  9:caller_package_name  10:origin  11:user_id
    """
    files_found = context.get_files_found()
    seeker = context.get_seeker()
    data_list = []
    source_path = ""

    uid_map = _build_uid_map(seeker)

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith("-wal"):
            continue

        source_path = file_found
        main_db_path = file_found[:-4]

        # Determine schema and collect live row IDs from the main DB
        new_schema = False
        live_ids = set()
        if os.path.exists(main_db_path):
            try:
                db = open_sqlite_db_readonly(main_db_path)
                cur = db.cursor()
                pragma_cols = [r[1] for r in cur.execute("PRAGMA table_info(clip_table)")]
                new_schema = "caller_package_name" in pragma_cols
                for (rid,) in cur.execute("SELECT id FROM clip_table"):
                    live_ids.add(rid)
                db.close()
            except sqlite3.Error:
                pass

        recov = _WalRecovery(file_found)
        if not recov.parse():
            logfunc(f"honeyboard_clipboard WAL: could not parse {file_found}: {recov.error}")
            continue

        seen_row_ids = set()
        for rec in recov.decoded_records():
            cols_vals = rec["columns"]
            if len(cols_vals) < 4:
                continue

            try:
                ts = int(cols_vals[1]) if isinstance(cols_vals[1], (int, float)) else None
                ctype = int(cols_vals[2]) if isinstance(cols_vals[2], (int, float)) else None
            except (ValueError, OverflowError):
                continue

            if ts is None or ctype not in _TYPE_CODES:
                continue

            text = cols_vals[3] if len(cols_vals) > 3 else None
            if not isinstance(text, str) or not text.strip():
                continue

            row_id = rec["row_id"]
            if row_id in live_ids or row_id in seen_row_ids:
                continue
            seen_row_ids.add(row_id)

            # Source app: prefer package name (col 9), fall back to UID (col 8)
            app_id = None
            if (new_schema and len(cols_vals) > 9
                    and isinstance(cols_vals[9], str) and "." in cols_vals[9]):
                app_id = cols_vals[9]
            elif (len(cols_vals) > 8
                  and isinstance(cols_vals[8], (int, float)) and cols_vals[8]):
                app_id = int(cols_vals[8])

            source_app = app_id if (new_schema and app_id) else _resolve_uid(app_id, uid_map)

            user_id = 0
            if len(cols_vals) > 11 and isinstance(cols_vals[11], (int, float)):
                user_id = int(cols_vals[11])

            data_list.append((
                _ms_to_utc(ts),
                row_id,
                _decode_type(ctype),
                text,
                source_app or "Unknown",
                user_id,
                rec["frame"],
                rec["page_num"],
            ))

    # Frame/page differ across mirror WALs, so exclude them from the signature
    data_list = _dedup_rows(data_list, key=lambda r: r[:6])
    data_list.sort(key=lambda r: r[0] if isinstance(r[0], datetime.datetime) else _AWARE_MIN)

    data_headers = (
        ("Timestamp (UTC)", "datetime"),
        "ID",
        "Type",
        "Clipboard Content",
        "Source App",
        "User ID",
        "WAL Frame",
        "WAL Page",
    )
    return data_headers, data_list, source_path


# ---------------------------------------------------------------------------
# Artifact 3: Clipboard screenshot clips
# ---------------------------------------------------------------------------

@artifact_processor
def get_honeyboard_screenshot(context):
    """Parse clipboard screenshot image clips.

    Each 'clip' file is an extensionless JPEG in a sub-directory whose name is a
    millisecond Unix epoch timestamp — the moment the image was copied to the
    clipboard. Three data sources are combined per image:
      1. Parent directory name  -> clipboard copy timestamp (UTC)
      2. EXIF DateTimeOriginal  -> capture timestamp (device local)
      3. Samsung SEFT trailer   -> source app package name

    Pillow is used for EXIF and the thumbnail; SEFT decoding is always available.
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

        # Copy timestamp from parent directory name (ms epoch)
        copy_ts = ""
        if parent_dir.isdigit():
            try:
                copy_ts = datetime.datetime.fromtimestamp(
                    int(parent_dir) / 1000, datetime.timezone.utc)
            except (ValueError, OverflowError, OSError):
                copy_ts = ""

        exif_capture_ts = ""
        width = height = None
        thumbnail = ""  # empty (not None) is the safe "no media" value for the media column

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
            logfunc("honeyboard_screenshot: Pillow not available — EXIF and thumbnails skipped.")

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
        ("Clipboard Copy Time (UTC)", "datetime"),
        "Capture Time (EXIF / device local)",
        "Source App (from SEFT trailer)",
        "Dimensions",
        ("Thumbnail", "media"),
        "Source Path",
    )
    return data_headers, data_list, source_path
