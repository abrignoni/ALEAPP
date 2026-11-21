"""Resolve Chromium download MediaStore URIs and attach files at their recorded paths."""

__artifacts_v2__ = {
    "get_chromeDownloadMediaStore": {
        "name": "Chromium Downloads - MediaStore Correlation",
        "description": "Links Chromium download records to MediaStore metadata by content URI and row ID, with the acquired file where its recorded shared-storage path resolves uniquely.",
        "author": "@ForensikITGmbH, @AlexisBrignoni, Codex",
        "creation_date": "2026-10-12",
        "last_update_date": "2026-11-19",
        "requirements": "none",
        "category": "Chromium",
        "notes": (
            "Correlates content://media/<volume>/downloads/<id> with the MediaStore files table. "
            "Extraction root and Android user are kept separate. An explicit user-qualified URI "
            "takes precedence over the browser's user. Duplicate Android storage views are collapsed; "
            "rollback snapshots and Magisk mirrors are excluded. Different provider databases are "
            "retained as separate candidates. Ambiguous IDs are not resolved arbitrarily. "
            "File metadata is the MediaStore record at acquisition, not proof of file existence or "
            "unchanged content at download time. Size comparison is not a hash comparison. State "
            "retains the stored Chromium value. Start/End Time are Chromium microseconds since "
            "1601-01-01 UTC; MediaStore dates are Unix seconds. Only downloads whose target or "
            "current path is a content://media/<volume>/downloads/<id> URI are reported. A URI "
            "naming the internal volume is not reported, because the external database cannot "
            "resolve it. The Downloads artifact reports every row of the downloads table in those "
            "History files without this filter. A URI with no "
            "matching MediaStore row is retained with its Correlation Status. "
            "Media attaches the file currently acquired at that MediaStore row's full _data path, "
            "using ALEAPP's seeker and check_in_media. Media Source Path names its evidence path. "
            "Shared-storage views under data/media, userdata/media and storage/emulated are supported; "
            "user-0 aliases sdcard, mnt/sdcard and storage/self/primary and removable storage under "
            "storage/<volume> or mnt/media_rw/<volume> are also searched. Extraction root and user "
            "must match. No filename-only lookup is used. Byte-identical storage views are attached "
            "once; differing copies are ambiguous and are not attached. Missing files, unsupported "
            "paths and unresolved or ambiguous MediaStore rows retain their metadata with a Media "
            "Status and an empty Media cell. The attached file is the content at acquisition, not "
            "proof that its bytes are unchanged since download. "
            "A focused run on sharon_a14 attached all 105 files to their rows (images, PDFs and "
            "Office documents); each exported file matched the acquired bytes. The additional "
            "storage layouts, literal glob characters, missing files and ambiguous storage views "
            "were exercised with synthetic files. "
            "On the sample_data images 110 rows were reported. All 110 had one MediaStore row, with "
            "File Size equal to Received Bytes and Owner Package equal to Browser Package. Current "
            "Path, Target Path and MediaStore URI were identical on all 110 rows and every URI "
            "named the external volume with no user qualifier. samsungs20_a13 stores app data "
            "under userdata/data/<package> and userdata/user/<user>/<package>; its 2 rows, one "
            "under Android user 0 and one under user 150, each had one row in the external.db "
            "of the same user. No sample_data image produced a Correlation Status other than "
            "'MediaStore row found'. User-qualified URIs and multiple candidates were exercised with synthetic "
            "databases only, as was a named volume, and only where it does not match. The "
            "external-<volume>.db file name is handled by code that no test or image has exercised. "
            "References: "
            "https://developer.android.com/reference/android/provider/MediaStore.Downloads; "
            "https://developer.android.com/reference/android/provider/MediaStore.MediaColumns; "
            "AOSP MediaProvider at tag android-14.0.0_r1, "
            "apex/framework/java/android/provider/MediaStore.java (DATE_ADDED and DATE_MODIFIED "
            "are annotated as seconds) and src/com/android/providers/media/DatabaseHelper.java "
            "(the downloads view selects from files where is_download=1)"
        ),
        "paths": (
            "*/app_chrome/Default/History*",
            "*/app_sbrowser/Default/History*",
            "*/app_opera/History*",
            "*/app_webview/Default/History*",
            "*/com.google.android.providers.media.module/databases/external*.db*",
            "*/com.android.providers.media.module/databases/external*.db*",
            "*/com.android.providers.media/databases/external*.db*",
        ),
        "output_types": "standard",
        "artifact_icon": "download",
        "sample_data": {
            "sharon_a14": "Android 14 | com.sec.android.app.sbrowser, com.android.chrome | 105 rows",
            "pixel7a_a14": "Android 14 | com.microsoft.emmx downloads hold empty paths | 0 rows",
            "samsungs20_a13": "Android 13 | com.microsoft.emmx (Android user 0), com.brave.browser (Android user 150) | 2 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.chrome | 1 row",
            "russell_pixel6a_a13": "Android 13 | com.brave.browser, Android user 10 | 1 row",
            "userb2_a13": "Android 13 | com.android.chrome | 1 row",
        },
    }
}

import datetime
import filecmp
import os
import re
import sqlite3
from collections import defaultdict
from urllib.parse import urlsplit

from scripts.ilapfuncs import artifact_processor, check_in_media, logfunc, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import canonical_path, unique_files


_PROVIDERS = {
    "com.google.android.providers.media.module",
    "com.android.providers.media.module",
    "com.android.providers.media",
}
_DOWNLOAD_COLUMNS = (
    "id", "guid", "start_time", "end_time", "tab_url", "referrer", "current_path",
    "target_path", "state", "received_bytes", "total_bytes", "mime_type",
)
_MEDIA_COLUMNS = (
    "_id", "_data", "_display_name", "_size", "owner_package_name", "mime_type",
    "date_added", "date_modified", "volume_name", "is_download", "is_pending", "is_trashed",
)
_HEADERS = (
    ("Start Time", "datetime"), ("End Time", "datetime"),
    ("MediaStore Date Added", "datetime"), ("MediaStore Date Modified", "datetime"),
    "Browser Package", ("Media", "media"), "Android User ID", "Download ID", "Download GUID", "Tab URL",
    "Referrer", "Download URL Chain", "Current Path", "Target Path", "URI Field",
    "MediaStore URI", "MediaStore Volume", "MediaStore ID", "MediaStore User ID",
    "Correlation Status", "Candidate Count", "File Name", "File Path",
    "Media Status", "Media Source Path", "File Size",
    "Size Comparison", "Owner Package", "MediaStore MIME Type",
    "State (as stored)", "Received Bytes", "Total Bytes", "Download MIME Type",
    "History DB Path", "MediaStore DB Path", "Notes",
)


def _scope(relative_path):
    """Evidence root, Android user and package, without guessing a missing user."""
    key, _ = canonical_path(relative_path)
    match = re.search(r"\x00(?:ce|de):(\d+)\x00/([^/]+)/", key)
    if match is None:
        return None
    return key[:match.start()].rstrip("/"), int(match.group(1)), match.group(2)


def _media_uri(value):
    if not isinstance(value, str):
        return None
    try:
        uri = urlsplit(value)
    except ValueError:
        return None
    authority = re.fullmatch(r"(?:(\d+)@)?media", uri.netloc)
    path = re.fullmatch(r"/([^/]+)/downloads/(\d+)", uri.path)
    if uri.scheme != "content" or authority is None or path is None or uri.query or uri.fragment:
        return None
    # An external.db cannot resolve internal-volume URIs.
    if path.group(1) == "internal":
        return None
    try:
        record_id = int(path.group(2))
        explicit_user = int(authority.group(1)) if authority.group(1) is not None else None
    except ValueError:
        return None
    if record_id > 9223372036854775807 or (explicit_user is not None and explicit_user > 2147483647):
        return None
    return path.group(1), record_id, explicit_user


def _references(download):
    refs = {}
    for field in ("target_path", "current_path"):
        value = download[field]
        parsed = _media_uri(value)
        if parsed is not None:
            if parsed not in refs:
                refs[parsed] = [value, []]
            refs[parsed][1].append(field)
    return [(parsed, value, ", ".join(fields)) for parsed, (value, fields) in refs.items()]


def _columns(db, table):
    return {row[1] for row in db.execute(f'PRAGMA table_info("{table}")')}


def _projection(names, available):
    # All identifiers come from the fixed column lists above, not database values.
    return ", ".join(f'"{name}"' if name in available else f'NULL AS "{name}"' for name in names)


def _time(value, chromium=False):
    if value in (None, "", 0):
        return ""
    try:
        if chromium:
            return datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(
                microseconds=int(value)
            )
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    except (ValueError, TypeError, OverflowError, OSError):
        return ""


def _read_history(path, source):
    db = open_sqlite_db_readonly(path)
    if db is None:
        return []
    try:
        db.row_factory = sqlite3.Row
        columns = _columns(db, "downloads")
        if "id" not in columns:
            return []
        chains = defaultdict(list)
        if {"id", "chain_index", "url"} <= _columns(db, "downloads_url_chains"):
            for row in db.execute("SELECT id, chain_index, url FROM downloads_url_chains ORDER BY id, chain_index"):
                chains[row["id"]].append(str(row["url"] or ""))
        rows = db.execute(f'SELECT {_projection(_DOWNLOAD_COLUMNS, columns)} FROM downloads ORDER BY id')
        return [(dict(row), "\n".join(chains[row["id"]])) for row in rows]
    except sqlite3.Error as error:
        logfunc(f"Unable to read Chromium downloads in {source}: {error}")
        return []
    finally:
        db.close()


def _read_media(path, source, record_ids):
    """Read only requested IDs, including any applicable WAL via ALEAPP's reader."""
    db = open_sqlite_db_readonly(path)
    if db is None:
        return None
    try:
        db.row_factory = sqlite3.Row
        table = "files"
        columns = _columns(db, table)
        if not columns:
            table = "downloads"
            columns = _columns(db, table)
        if "_id" not in columns:
            logfunc(f"MediaStore row ID column unavailable in {source}")
            return None
        records = []
        ordered_ids = sorted(record_ids)
        for offset in range(0, len(ordered_ids), 500):
            batch = ordered_ids[offset:offset + 500]
            marks = ",".join("?" for _ in batch)
            sql = f'SELECT {_projection(_MEDIA_COLUMNS, columns)} FROM "{table}" WHERE _id IN ({marks}) ORDER BY _id'
            for row in db.execute(sql, batch):
                record = dict(row)
                record["source"] = source
                basename = os.path.basename(path)
                record["legacy_volume"] = basename[len("external-"):-len(".db")] if basename.startswith("external-") else ""
                records.append(record)
        return records
    except sqlite3.Error as error:
        logfunc(f"Unable to read MediaStore metadata in {source}: {error}")
        return None
    finally:
        db.close()


def _volume_matches(volume, record):
    stored = record["volume_name"] or record["legacy_volume"]
    if volume == "external":
        return stored != "internal"
    if stored:
        return volume == stored
    # A named volume cannot be established from a database lacking volume metadata.
    return False


def _size_comparison(download, record):
    if record is None:
        return ""
    size, received = record["_size"], download["received_bytes"]
    try:
        size, received = int(size), int(received)
    except (ValueError, TypeError, OverflowError):
        return "Unavailable"
    if size < 0 or received < 0:
        return "Unavailable"
    return "Matches received bytes" if size == received else "Differs from received bytes"


def _acquisition_paths(recorded, root, user):
    """Exact evidence-relative spellings of a recorded shared-storage file path."""
    if not isinstance(recorded, str) or not recorded.startswith('/') or '\\' in recorded:
        return (), "Unsupported recorded file path"
    if any(part in ('', '.', '..') for part in recorded[1:].split('/')) or '\x00' in recorded:
        return (), "Unsupported recorded file path"
    shared = re.fullmatch(r'/(?:storage/emulated|data/media)/(\d+)/(.+)', recorded)
    alias = re.fullmatch(r'/(?:sdcard|mnt/sdcard|storage/self/primary)/(.+)', recorded)
    removable = re.fullmatch(r'/(?:storage|mnt/media_rw)/([0-9a-fA-F-]+)/(.+)', recorded)
    if shared or alias:
        if shared and int(shared[1]) != user:
            return (), "Recorded file path belongs to another Android user"
        tail = shared[2] if shared else alias[1]
        paths = [f'{layout}/{user}/{tail}' for layout in
                 ('data/media', 'userdata/media', 'storage/emulated')]
        if user == 0:
            paths.extend(f'{layout}/{tail}' for layout in
                         ('sdcard', 'mnt/sdcard', 'storage/self/primary'))
    elif removable:
        volume, tail = removable.groups()
        paths = [f'{layout}/{volume}/{tail}' for layout in ('storage', 'mnt/media_rw')]
    else:
        return (), "Unsupported recorded file path"
    return tuple(f'{root}/{path}' if root else path for path in paths), ''


def _acquired_media(context, record, root, user):
    """Attach a uniquely identified acquired file; never fall back to its basename."""
    paths, status = _acquisition_paths(record['_data'], root, user)
    if not paths:
        return '', status, ''
    seeker = context.get_seeker()
    # Another artifact (or the case harness) may already have staged the file.
    found = {info.source_path.lstrip('/'): str(staged)
             for staged, info in seeker.file_infos.items()
             if info.source_path.lstrip('/') in paths and os.path.isfile(staged)}
    for source in paths:
        if source in found:
            continue
        # Search patterns are globs, while evidence names (including [, * and ?) are literal.
        escaped = ''.join(f'[{char}]' if char in '[*?' else char for char in source)
        for staged in seeker.search('*/' + escaped):
            staged = str(staged)
            info = seeker.file_infos.get(staged)
            # The seeker also matches nested suffixes. Require the complete evidence path,
            # including the extraction root, before handing a staged file to check_in_media.
            if info and info.source_path.lstrip('/') == source and os.path.isfile(staged):
                found[source] = staged
    if not found:
        return '', 'File not found in acquisition', ''
    copies = sorted(found.items())
    source, staged = copies[0]
    try:
        if any(not filecmp.cmp(staged, other, shallow=False) for _, other in copies[1:]):
            return '', 'Ambiguous acquired files at storage views', ''
        reference = check_in_media(staged, os.path.basename(record['_data']))
    except OSError as error:
        logfunc(f'Unable to attach Chromium download at {source}: {error}')
        return '', 'Acquired file could not be attached', source
    if not reference:
        return '', 'Acquired file could not be attached', source
    return reference, 'Acquired file attached', source


def _output(download, chain, source, scope, ref, candidates, status, attachment):
    parsed, uri, field = ref
    volume, record_id, explicit_user = parsed
    user = scope[1] if scope else ""
    media_user = explicit_user if explicit_user is not None else user
    record = candidates[0] if len(candidates) == 1 else None
    media = record or {}
    notes = []
    if explicit_user is not None and explicit_user != user:
        notes.append("MediaStore user is explicitly qualified in the URI")
    if len(candidates) > 1:
        notes.append("Multiple source databases contain this ID; file metadata is not selected")
    if record is not None:
        if record["owner_package_name"] and scope and record["owner_package_name"] != scope[2]:
            notes.append("MediaStore owner package differs from the browser package")
        if record["is_download"] == 0:
            notes.append("MediaStore row is not currently marked as a download")
        for column, label in (("is_pending", "Pending"), ("is_trashed", "Trashed")):
            if record[column] == 1:
                notes.append(f"MediaStore flag: {label}")
    return (
        _time(download["start_time"], True), _time(download["end_time"], True),
        _time(media.get("date_added")), _time(media.get("date_modified")),
        scope[2] if scope else "", attachment[0], user, download["id"], download["guid"], download["tab_url"],
        download["referrer"], chain, download["current_path"], download["target_path"], field,
        uri, volume, record_id, media_user, status, len(candidates),
        media.get("_display_name", ""), media.get("_data", ""), *attachment[1:], media.get("_size", ""),
        _size_comparison(download, record), media.get("owner_package_name", ""), media.get("mime_type", ""),
        download["state"],
        download["received_bytes"], download["total_bytes"], download["mime_type"], source,
        "\n".join(sorted({candidate["source"] for candidate in candidates})), "; ".join(notes),
    )


@artifact_processor
def get_chromeDownloadMediaStore(context):
    entries = []
    sources = []
    requested = defaultdict(set)
    media_files = []
    for path in unique_files(context):
        source = str(context.get_relative_path(path)).replace("\\", "/")
        if "/rollback/" in "/" + source or (".magisk" in source and "/mirror/" in source):
            continue
        scope = _scope(source)
        basename = os.path.basename(str(path))
        if basename == "History":
            sources.append(str(path))
            for download, chain in _read_history(path, source):
                refs = _references(download)
                if not refs:
                    # No MediaStore URI to resolve; the Downloads artifact reports the row.
                    continue
                entries.append((download, chain, source, scope, refs))
                if scope:
                    for parsed, _, _ in refs:
                        _, record_id, explicit_user = parsed
                        user = scope[1] if explicit_user is None else explicit_user
                        requested[(scope[0], user)].add(record_id)
        elif scope and scope[2] in _PROVIDERS and re.fullmatch(r"external(?:-[0-9a-fA-F-]+)?\.db", basename):
            media_files.append((str(path), source, scope))

    index = defaultdict(list)
    available = set()
    for path, source, scope in media_files:
        key = scope[:2]
        if key not in requested:
            continue
        sources.append(path)
        records = _read_media(path, source, requested[key])
        if records is None:
            continue
        available.add(key)
        for record in records:
            index[key + (record["_id"],)].append(record)

    data = []
    attachments = {}
    for download, chain, source, scope, refs in entries:
        for ref in refs:
            (volume, record_id, explicit_user), _, _ = ref
            candidates = []
            if scope is None:
                status = "Android user not determined from the History path"
            else:
                user = scope[1] if explicit_user is None else explicit_user
                key = (scope[0], user)
                candidates = [record for record in index[key + (record_id,)] if _volume_matches(volume, record)]
                if key not in available:
                    status = "MediaStore database unavailable for this user"
                elif not candidates:
                    status = "MediaStore row not found for this volume"
                elif len(candidates) > 1:
                    status = "Ambiguous MediaStore rows"
                else:
                    status = "MediaStore row found"
            attachment = ('', 'MediaStore row not uniquely resolved', '')
            if len(candidates) == 1:
                cache_key = (scope[0], user, candidates[0]['_data'])
                if cache_key not in attachments:
                    attachments[cache_key] = _acquired_media(context, candidates[0], scope[0], user)
                attachment = attachments[cache_key]
            data.append(_output(download, chain, source, scope, ref, candidates, status, attachment))
    return _HEADERS, data, "\n".join(dict.fromkeys(sources))
