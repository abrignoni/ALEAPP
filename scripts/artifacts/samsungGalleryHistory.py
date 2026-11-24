"""Samsung Gallery (com.sec.android.gallery3d): search history and operation history.

Samsung Gallery keeps, in databases/local.db, the searches it remembers (search_history)
and a short history of operations on media items (operation_history), whose media_id
values on P, E and S rows are MediaStore ids on the tested images. The ids are resolved to file names
through the media provider's external.db where that database is in the extraction.
"""

__artifacts_v2__ = {
    "get_samsung_gallery_search_history": {
        "name": "Samsung Gallery - Search History",
        "description": (
            "Parses the search_history table of Samsung Gallery's local.db: each stored search with its date_added time, the stored title, the search kind and term split from the title where it holds a slash, and the stored search target."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Photos & Media",
        "notes": (
            "Read from the search_history table (title, date_added, search_target) of "
            "com.sec.android.gallery3d/databases/local.db with its -wal. Date Added is "
            "date_added, milliseconds since the Unix epoch converted to UTC and cut to the "
            "whole second. Search Kind and Search Term are the stored title split at its first slash. Two rows were seen: on samsung_a166u_a16_known_20261117 the title is key_word, a slash and the logged search term; on sharon_a14 the title holds no slash, so Search Kind is blank and Search Term is the whole title. Title (as stored) keeps the whole value, and Search Target is the stored search URI. "
            "On samsung_a166u_a16_known_20261117 the one row matches the one logged Gallery search; the stored time is within two seconds of the logged time. sharon_a14 holds one row. On the other ten images run the table is empty. Whether the "
            "app keeps every search or only recent ones is not established. "
            "Left out from local.db: the log table (its cells that hold encoded strings are reported by the Samsung Gallery Log Encoded Strings artifact), mxalbum (album and folder records: paths, names and counts, with no action column), cache (key and data columns, meaning not established) and the operation_history table, reported by Samsung Gallery - Operation History. The other tables in local.db are not reported; count_history holds rows on seven of the images run and its meaning is not established."
        ),
        "paths": ("*/com.sec.android.gallery3d/databases/local.db*",),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.sec.android.gallery3d | 1 row",
            "sharon_a14": "Android 14 | com.sec.android.gallery3d | 1 row",
            "samsung_a166u_a16_known_20261116": "Android 16 | search_history empty | 0 rows",
            "adams_ss135dl_a13": "Android 13 | search_history empty | 0 rows",
            "anne_a15": "Android 15 | search_history empty | 0 rows",
            "cookbook_a11": "Android 11 | search_history empty | 0 rows",
            "falken_a326u_a13": "Android 13 | search_history empty | 0 rows",
            "galaxys10_a10": "Android 10 | search_history empty | 0 rows",
            "s20fe_a13": "Android 13 | search_history empty | 0 rows",
            "samsunga53_a14": "Android 14 | search_history empty | 0 rows",
            "samsungs20_a13": "Android 13 | search_history empty | 0 rows",
            "sharon_a13": "Android 13 | search_history empty | 0 rows",
        },
    },
    "get_samsung_gallery_operation_history": {
        "name": "Samsung Gallery - Operation History",
        "description": (
            "Parses the operation_history table of Samsung Gallery's local.db: one row per "
            "stored operation with its time, the action code as stored, the media ids it "
            "names and, where the media provider's external.db for the same Android user is "
            "in the extraction, the file name and folder each id has there."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Photos & Media",
        "notes": (
            "Read from the operation_history table (timestamp, action, media_id) of "
            "com.sec.android.gallery3d/databases/local.db with its -wal. Timestamp is "
            "milliseconds since the Unix epoch converted to UTC and cut to the whole "
            "second. Media IDs (as stored) is the comma-separated media_id value. "
            "Each id is looked up as _id in the files table of the media provider's "
            "external.db (com.google.android.providers.media.module or "
            "com.android.providers.media) for the same Android user, and File Names and "
            "Folders give its _display_name and relative_path there, one per line in the stored order; when _display_name is empty the name is taken from the end of _data (no row on the images run needed that). Every lookup on the images run went through com.google.android.providers.media.module; the com.android.providers.media path was not exercised. Media Resolved counts the ids found. The lookup is against the media provider as extracted: a file renamed or moved since the operation would show the name and folder it has at extraction, and a deleted one would show nothing. This was not tested. "
            "Action (as stored) is not decoded. On samsung_a166u_a16_known_20261117 "
            "(Gallery actions logged during the session): P named the three screenshots "
            "that were then copied into a new album, E named the album copy that was "
            "cropped, and S named the file that was then shared with Quick Share; each "
            "stored time came before the logged action, by about 10 to about 80 seconds. On the eight images run that hold P, E or S rows, every id on those rows (19 ids on 17 rows) resolved through external.db; only on samsung_a166u_a16_known_20261117 was the resolved file checked against a logged action. V rows held ids of 2147483649 and above, none of which is an _id in external.db, so their files are not resolved and what V records is not "
            "established. "
            "Rows with no resolved id leave File Names and Folders blank. A media provider database for another Android user is read for that user's rows (cookbook_a11 has one E row under user 150, resolved)."
        ),
        "paths": (
            "*/com.sec.android.gallery3d/databases/local.db*",
            "*/com.google.android.providers.media.module/databases/external.db*",
            "*/com.android.providers.media/databases/external.db*",
        ),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.sec.android.gallery3d | 4 rows",
            "sharon_a14": "Android 14 | com.sec.android.gallery3d | 14 rows",
            "anne_a15": "Android 15 | com.sec.android.gallery3d | 7 rows",
            "samsungs20_a13": "Android 13 | com.sec.android.gallery3d | 4 rows",
            "falken_a326u_a13": "Android 13 | com.sec.android.gallery3d | 3 rows",
            "s20fe_a13": "Android 13 | com.sec.android.gallery3d | 3 rows",
            "adams_ss135dl_a13": "Android 13 | com.sec.android.gallery3d | 2 rows",
            "cookbook_a11": "Android 11 | com.sec.android.gallery3d, users 0 and 150 | 2 rows",
            "sharon_a13": "Android 13 | com.sec.android.gallery3d | 2 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.gallery3d | 1 row",
            "samsung_a166u_a16_known_20261116": "Android 16 | operation_history empty | 0 rows",
            "galaxys10_a10": "Android 10 | operation_history empty | 0 rows",
        },
    },
}

import re

from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc,
    does_table_exist_in_db,
    get_sqlite_db_records,
    is_sqlite_sidecar,
)

GALLERY = "com.sec.android.gallery3d"
MEDIA_PACKAGES = ("com.google.android.providers.media.module", "com.android.providers.media")
_USER_RE = re.compile(r"/(?:user|user_de|data_mirror/data_(?:ce|de)/[^/]+)/(\d+)/")


def _container(path, package):
    """(android user, storage area) of the package container a path sits in, or None."""
    norm = str(path).replace("\\", "/")
    idx = norm.find(f"/{package}/databases/")
    if idx < 0:
        return None
    head = norm[:idx + 1]
    area = "de" if ("/user_de/" in head or "/data_mirror/data_de/" in head) else "ce"
    match = None
    for match in _USER_RE.finditer(head):
        pass
    if match and head.endswith(f"/{match.group(1)}/"):
        return int(match.group(1)), area
    if head.rstrip("/").rsplit("/", 1)[-1] == "data":
        # /data/data/<pkg>, and layouts such as userdata/data/<pkg> that keep user 0 there
        return 0, area
    return None


def _gallery_databases(files_found):
    for path in files_found:
        path = str(path)
        if is_sqlite_sidecar(path) or not path.endswith("local.db"):
            continue
        container = _container(path, GALLERY)
        if container is not None:
            yield path, container


def _ms(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ""
    return convert_unix_ts_to_utc(value) if value > 0 else ""


def _columns(path, table):
    return {row[1] for row in get_sqlite_db_records(path, f"PRAGMA table_info({table})")}


@artifact_processor
def get_samsung_gallery_search_history(context):
    data_list = []
    source_paths = []
    seen = set()
    for path, container in _gallery_databases(context.get_files_found()):
        source_paths.append(path)
        if not does_table_exist_in_db(path, "search_history"):
            continue
        cols = _columns(path, "search_history")
        if "title" not in cols:
            continue
        select = ", ".join(c if c in cols else f"NULL AS {c}"
                           for c in ("date_added", "title", "search_target")) + ", rowid"
        for added, title, target, row_id in get_sqlite_db_records(
                path, f"SELECT {select} FROM search_history ORDER BY date_added"):
            key = (container[0], row_id, title, added)
            if key in seen:
                continue
            seen.add(key)
            kind, _, term = (title or "").partition("/")
            if not term:
                kind, term = "", title or ""
            data_list.append((_ms(added), term, kind, title or "", target or "", container[0]))

    data_headers = (
        ("Date Added", "datetime"),
        "Search Term",
        "Search Kind",
        "Title (as stored)",
        "Search Target (as stored)",
        "Android User",
    )
    return data_headers, data_list, "\n".join(sorted(set(source_paths)))


def _media_index(files_found, wanted):
    """{(android user, MediaStore _id): (display name, relative path, path of external.db)}."""
    index = {}
    if not wanted:
        return index
    for path in files_found:
        path = str(path)
        if is_sqlite_sidecar(path) or not path.endswith("external.db"):
            continue
        container = None
        for package in MEDIA_PACKAGES:
            container = _container(path, package)
            if container is not None:
                break
        if container is None or not does_table_exist_in_db(path, "files"):
            continue
        ids = sorted(i for user, i in wanted if user == container[0])
        if not ids:
            continue
        cols = _columns(path, "files")
        name_col = "_display_name" if "_display_name" in cols else "NULL"
        folder_col = "relative_path" if "relative_path" in cols else "NULL"
        data_col = "_data" if "_data" in cols else "NULL"
        for start in range(0, len(ids), 500):
            chunk = ids[start:start + 500]
            query = (f"SELECT _id, {name_col}, {folder_col}, {data_col} FROM files "
                     f"WHERE _id IN ({', '.join(str(i) for i in chunk)})")
            for media_id, name, folder, data in get_sqlite_db_records(path, query):
                if not name and data:
                    name = str(data).rsplit("/", 1)[-1]
                index.setdefault((container[0], media_id), (name or "", folder or "", path))
    return index


@artifact_processor
def get_samsung_gallery_operation_history(context):
    files_found = context.get_files_found()
    rows = []
    source_paths = []
    seen = set()
    for path, container in _gallery_databases(files_found):
        source_paths.append(path)
        if not does_table_exist_in_db(path, "operation_history"):
            continue
        if not {"timestamp", "action", "media_id"} <= _columns(path, "operation_history"):
            continue
        for stamp, action, media_ids, row_id in get_sqlite_db_records(
                path, "SELECT timestamp, action, media_id, _id FROM operation_history "
                      "ORDER BY timestamp, _id"):
            key = (container[0], row_id, stamp, action, media_ids)
            if key in seen:
                continue
            seen.add(key)
            ids = [part.strip() for part in str(media_ids or "").split(",") if part.strip()]
            rows.append((stamp, action, media_ids, ids, row_id, container[0]))

    wanted = {(user, int(i)) for _s, _a, _m, ids, _r, user in rows for i in ids if i.isdigit()}
    media = _media_index(files_found, wanted)
    data_list = []
    for stamp, action, media_ids, ids, row_id, user in rows:
        names, folders = [], []
        resolved = 0
        for i in ids:
            hit = media.get((user, int(i))) if i.isdigit() else None
            if hit:
                resolved += 1
                names.append(hit[0])
                folders.append(hit[1])
                source_paths.append(hit[2])
            else:
                names.append("")
                folders.append("")
        if not resolved:
            names, folders = [], []
        data_list.append((
            _ms(stamp), action or "", len(ids), resolved, "\n".join(names),
            "\n".join(folders), media_ids or "", row_id, user,
        ))

    data_headers = (
        ("Timestamp", "datetime"),
        "Action (as stored)",
        ("Media Count", "number"),
        ("Media Resolved", "number"),
        "File Names (MediaStore)",
        "Folders (MediaStore)",
        "Media IDs (as stored)",
        "Operation ID",
        "Android User",
    )
    return data_headers, data_list, "\n".join(sorted(set(source_paths)))
