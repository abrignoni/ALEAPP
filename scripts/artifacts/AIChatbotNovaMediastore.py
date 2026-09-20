__artifacts_v2__ = {
    "nova_user_submissions": {
        "name": "User Media Submissions",
        "description": "Media the Nova app recorded, matched to the path the Android MediaStore index holds for each file, with the app's shared media folder swept for files no record names.",
        "author": "Guilherme Guilherme",
        "creation_date": "2026-05-30",
        "last_update_date": "2026-09-19",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": (
            "Integrates chat-ai.db history with filesystem discovery; chat-ai.db holds "
            "text records only, not the media bytes. A path shown as Not in MediaStore "
            "means no MediaStore row matched the file name. The MIME column is the value "
            "the database records where present and blank otherwise; the file bytes are "
            "not sniffed. An extraction can carry one copy of each database per Android "
            "user and every copy is read. The committed test case carries no file under "
            "the app's shared media folder, so the filesystem sweep and the media column "
            "are code present and unexercised by it. Developed against the author's own "
            "installation; no registered corpus image carries this app."
        ),
        "paths": (
            "**/com.scaleup.chatai/databases/chat-ai.db",
            "**/com.android.providers.media/databases/external*.db",
            "**/com.google.android.providers.media.module/databases/external*.db",
            "**/data/media/0/Android/media/com.scaleup.chatai/Nova/*",
        ),
        "output_types": ["standard", "lava"],
        "artifact_icon": "folder",
    }
}

import datetime
import os
import sqlite3

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    logfunc,
    open_sqlite_db_readonly,
)

NOVA_MEDIA_DIR = "Android/media/com.scaleup.chatai/Nova"


def _epoch_to_utc(value):
    """chat-ai.db epochs are milliseconds; values below 1e11 are read as
    seconds (the magnitudes cannot overlap for plausible dates)."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    if value > 1e11:
        value /= 1000
    try:
        return datetime.datetime.fromtimestamp(value, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError):
        return ''


def _media_lookup(media_dbs):
    """File name to recorded device path, from every MediaStore database read.

    A MediaStore database is present whether or not Nova is installed, and some
    builds carry no files table, so a failed lookup must not end the artifact.
    """
    lookup = {}
    for media_db in media_dbs:
        try:
            with open_sqlite_db_readonly(media_db) as db:
                cur = db.cursor()
                cur.execute("SELECT _display_name, _data FROM files WHERE _data IS NOT NULL")
                for name, path in cur.fetchall():
                    key = (name or os.path.basename(str(path))).lower()
                    lookup[key] = path
        except sqlite3.Error as exc:
            logfunc(f"Nova user submissions - MediaStore lookup unavailable ({exc})")
    return lookup


@artifact_processor
def nova_user_submissions(context):
    headers = (
        "File Name",
        "Type",
        "Context",
        ("Date", "datetime"),
        "MIME",
        ("Media", "media"),
        "Path",
    )

    # unique_files collapses the data/data, data/user/0 and data_mirror views of one
    # file and keeps a second Android user's own copy, so both users are reported.
    files_found = [str(f) for f in unique_files(context)]
    nova_dbs = sorted(f for f in files_found if os.path.basename(f) == "chat-ai.db")
    media_dbs = sorted(
        f for f in files_found
        if os.path.basename(f).startswith("external") and f.endswith(".db")
    )

    all_items = []
    sources = []
    processed_paths = set()

    # Files the extraction carries under the app's shared media folder, by name
    nova_files_lookup = {
        os.path.basename(f).lower(): f for f in files_found if NOVA_MEDIA_DIR in f
    }

    media_lookup = _media_lookup(media_dbs)
    sources.extend(media_dbs)

    for nova_db in nova_dbs:
        with open_sqlite_db_readonly(nova_db) as db:
            cur = db.cursor()

            cur.execute(
                "SELECT hdd.name, hdd.mimeType, hd.text, hd.createdAt "
                "FROM HistoryDetailDocument hdd "
                "INNER JOIN HistoryDetail hd ON hd.id = hdd.historyDetailID"
            )
            for name, mime, msg, ts in cur.fetchall():
                key = (name or "").lower()
                dev_path = media_lookup.get(key)
                media_ref = ""
                ext_path = nova_files_lookup.get(key)
                if ext_path:
                    media_ref = check_in_media(ext_path, name=name) or ''
                    processed_paths.add(ext_path)

                all_items.append(
                    (
                        name,
                        "Document",
                        msg,
                        _epoch_to_utc(ts),
                        mime or "",
                        media_ref,
                        dev_path or "Not in MediaStore",
                    )
                )

            cur.execute(
                "SELECT hdi.url, hdi.prompt, hd.text, hd.createdAt "
                "FROM HistoryDetailImage hdi "
                "INNER JOIN HistoryDetail hd ON hd.id = hdi.historyDetailID"
            )
            for url, prompt, msg, ts in cur.fetchall():
                fname = os.path.basename(str(url).split("?")[0])
                key = fname.lower()
                dev_path = media_lookup.get(key)
                media_ref = ""
                ext_path = nova_files_lookup.get(key)
                if ext_path:
                    media_ref = check_in_media(ext_path, name=fname) or ''
                    processed_paths.add(ext_path)

                all_items.append(
                    (
                        fname,
                        "Image",
                        f"Msg: {msg} | Prompt: {prompt}",
                        _epoch_to_utc(ts),
                        "",
                        media_ref,
                        dev_path or "Not in MediaStore",
                    )
                )

        sources.append(nova_db)

    # Files in the app's shared media folder that no database record named
    for file_path in sorted(nova_files_lookup.values()):
        if file_path in processed_paths:
            continue
        fname = os.path.basename(file_path)
        media_ref = check_in_media(file_path, name=fname) or ''
        all_items.append(
            (
                fname,
                "Orphaned Media",
                "Found in the app's shared media folder with no database record",
                None,
                "",
                media_ref,
                context.get_relative_path(file_path),
            )
        )
        sources.append(file_path)

    return headers, all_items, "\n".join(sources)
