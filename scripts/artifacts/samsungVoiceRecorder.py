"""Samsung Voice Recorder (com.sec.android.app.voicenote): recordings, categories, searches.

The app keeps its own index of recordings in databases/label.db (recording_items), its
categories in labels and its saved searches in recent_search. The audio files themselves sit
in shared storage, by default Recordings/Voice Recorder/.
"""

__artifacts_v2__ = {
    "get_samsung_voice_recorder_recordings": {
        "name": "Samsung Voice Recorder - Recordings",
        "description": (
            "Parses the recordings listed by Samsung Voice Recorder in label.db, one row per "
            "recording with a stored path, with the time stored for it, the file and its "
            "audio, the category and the stored favourite and bookmark flags."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Samsung Voice Recorder",
        "notes": (
            "Read from the recording_items table of "
            "com.sec.android.app.voicenote/databases/label.db with its -wal. Rows without a "
            "stored PATH are left out: label.db held one on "
            "samsung_a166u_a16_known_20261116 and on samsung_a166u_a16_known_20261117 "
            "(MEDIA_ID 17, every other column empty), and what it is is not established. "
            "Observed on known data (samsung_a166u_a16_known_20261116 and "
            "samsung_a166u_a16_known_20261117, Voice Recorder actions logged with times "
            "during the sessions): Saved is the timestamp column, milliseconds since the "
            "Unix epoch converted to UTC and cut to the whole second; on both recordings it "
            "fell within one second of the logged save, not at the start of recording (the "
            "file name the app gives a new recording carries the local start time). "
            "Audio is the file at the stored PATH, found in the extraction by its full path "
            "under that Android user's shared storage (data/media/<user>/ or "
            "storage/emulated/<user>/); File In Extraction says whether it was found. "
            "Category is CATEGORY_NAME as stored; the default category is stored as the "
            "text None. "
            "Favorite (as stored), Has Bookmark (as stored), Recording Type (as stored), "
            "Recording Mode (as stored) and Is Trash (as stored) are not decoded. On the "
            "2026-11-17 recording, which had one bookmark added while recording, "
            "HAS_BOOKMARK held 0, so the column does not show bookmarks on the known data. "
            "IS_FAVORITE held 1 on that recording although the session log records no "
            "favourite being set; what sets it is not established. "
            "Recordings moved to the app's trash are not here: on "
            "samsung_a166u_a16_known_20261117 the trashed recording's row was removed from "
            "recording_items and label.db's own trash table stayed empty, while the Samsung "
            "trash provider recorded the deletion and the file under "
            "Android/.Trash/com.sec.android.app.voicenote/. That record is reported by the "
            "Samsung Trash artifact. "
            "Left out: labels (category names, with the default None; a category added on "
            "the known data remains after its only recording was trashed) and the ai_* "
            "tables (transcripts, summaries, keywords and speakers), which were empty on "
            "every registered image that holds label.db (sharon_a14's label.db has no ai_* "
            "tables). A recording with an AI transcript is not in the known data. "
            "anne_a15 and sharon_a14 hold label.db with no recording that has a stored "
            "path."
        ),
        "paths": (
            "*/com.sec.android.app.voicenote/databases/label.db*",
            "*/media/*/Recordings/*",
            "*/storage/emulated/*/Recordings/*",
        ),
        "output_types": "standard",
        "artifact_icon": "mic",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.sec.android.app.voicenote | 1 row",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.sec.android.app.voicenote 21.5.81.38 | 1 row",
            "anne_a15": "Android 15 | no recording with a stored path | 0 rows",
            "sharon_a14": "Android 14 | no recording with a stored path | 0 rows",
        },
    },
    "get_samsung_voice_recorder_searches": {
        "name": "Samsung Voice Recorder - Search History",
        "description": (
            "Parses the search terms Samsung Voice Recorder keeps in the recent_search table of "
            "label.db, with the time stored for each."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Samsung Voice Recorder",
        "notes": (
            "Read from the recent_search table (LABEL, TIME) of "
            "com.sec.android.app.voicenote/databases/label.db. On "
            "samsung_a166u_a16_known_20261117 the one row matches the search for 'KD' "
            "logged at the same second; Saved is TIME, milliseconds since the Unix epoch "
            "converted to UTC. LABEL is the table's primary key, so a term searched again "
            "keeps one row; whether TIME then moves to the later search is not established. "
            "No other registered image holds a row."
        ),
        "paths": ("*/com.sec.android.app.voicenote/databases/label.db*",),
        "output_types": "standard",
        "artifact_icon": "search",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.sec.android.app.voicenote | 1 row",
            "samsung_a166u_a16_known_20261116": "Android 16 | recent_search empty | 0 rows",
            "anne_a15": "Android 15 | recent_search empty | 0 rows",
            "sharon_a14": "Android 14 | recent_search empty | 0 rows",
        },
    },
}

import re

from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    convert_unix_ts_to_utc,
    does_table_exist_in_db,
    get_sqlite_db_records,
    is_sqlite_sidecar,
)

PACKAGE = "com.sec.android.app.voicenote"
_USER_RE = re.compile(r"/(?:user|user_de|data_mirror/data_(?:ce|de)/[^/]+)/(\d+)/")
_STORAGE_RE = re.compile(r"^/(?:storage/emulated|sdcard)(?:/(\d+))?/(.+)$")


def _container(path):
    """(android user, storage area) of the voicenote container a path sits in, or None."""
    norm = str(path).replace("\\", "/")
    idx = norm.find(f"/{PACKAGE}/databases/")
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


def _databases(files_found):
    for path in files_found:
        path = str(path)
        if is_sqlite_sidecar(path) or not path.endswith("label.db"):
            continue
        container = _container(path)
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


def _find_audio(files_found, stored_path, user):
    """The staged file for a stored /storage/emulated/<user>/... path, matched on the full
    relative path under that user's shared storage (media/<user>/ or emulated/<user>/)."""
    match = _STORAGE_RE.match(stored_path or "")
    if not match:
        return None
    path_user = int(match.group(1)) if match.group(1) is not None else user
    relative = match.group(2)
    suffixes = (f"/media/{path_user}/{relative}", f"/emulated/{path_user}/{relative}")
    for candidate in files_found:
        norm = str(candidate).replace("\\", "/")
        if norm.endswith(suffixes):
            return str(candidate)
    return None


@artifact_processor
def get_samsung_voice_recorder_recordings(context):
    files_found = context.get_files_found()
    data_list = []
    source_paths = []
    seen = set()
    for path, container in _databases(files_found):
        source_paths.append(path)
        if not does_table_exist_in_db(path, "recording_items"):
            continue
        cols = _columns(path, "recording_items")
        wanted = ("timestamp", "PATH", "CATEGORY_NAME", "IS_FAVORITE", "HAS_BOOKMARK",
                  "recordingtype", "recording_mode", "is_trash", "MEDIA_ID")
        select = ", ".join(c if c in cols else f"NULL AS {c}" for c in wanted)
        query = f"SELECT {select} FROM recording_items WHERE PATH IS NOT NULL AND PATH != ''"
        for row in get_sqlite_db_records(path, query):
            (saved, stored_path, category, favorite, bookmark, rec_type, rec_mode, is_trash,
             media_id) = row
            key = (container[0], media_id, stored_path, saved)
            if key in seen:
                continue
            seen.add(key)
            audio = _find_audio(files_found, stored_path, container[0])
            media_ref = check_in_media(audio, stored_path.rsplit("/", 1)[-1]) if audio else ""
            data_list.append((
                _ms(saved), stored_path.rsplit("/", 1)[-1], media_ref or "",
                "Yes" if audio else "No", category or "", favorite, bookmark, rec_type,
                rec_mode, is_trash, stored_path, media_id, container[0],
            ))

    data_headers = (
        ("Saved", "datetime"),
        "File Name",
        ("Audio", "media"),
        "File In Extraction",
        "Category",
        "Favorite (as stored)",
        "Has Bookmark (as stored)",
        "Recording Type (as stored)",
        "Recording Mode (as stored)",
        "Is Trash (as stored)",
        "Stored Path",
        "Media ID",
        "Android User",
    )
    return data_headers, data_list, "\n".join(sorted(set(source_paths)))


@artifact_processor
def get_samsung_voice_recorder_searches(context):
    data_list = []
    source_paths = []
    seen = set()
    for path, container in _databases(context.get_files_found()):
        source_paths.append(path)
        if not does_table_exist_in_db(path, "recent_search"):
            continue
        if not {"LABEL", "TIME"} <= _columns(path, "recent_search"):
            continue
        for label, saved in get_sqlite_db_records(
                path, "SELECT LABEL, TIME FROM recent_search ORDER BY TIME"):
            key = (container[0], label, saved)
            if key in seen:
                continue
            seen.add(key)
            data_list.append((_ms(saved), label or "", container[0]))

    data_headers = (("Saved", "datetime"), "Search Term", "Android User")
    return data_headers, data_list, "\n".join(sorted(set(source_paths)))
