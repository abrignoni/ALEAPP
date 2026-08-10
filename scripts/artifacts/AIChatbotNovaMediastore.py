__artifacts_v2__ = {
    "nova_user_submissions": {
        "name": "User Media Submissions",
        "description": "Extracts Nova AI media. Identifies files via database indexing (MediaStore) and performs a filesystem sweep for orphaned camera captures.",
        "author": "Guilherme Guilherme",
        "creation_date": "2026-05-30",
        "last_update_date": "2026-08-10",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": ("Integrates chat-ai.db history with filesystem discovery; chat-ai.db holds text records only, not the media bytes. A path shown as Not in MediaStore means no MediaStore row matched the file name. The MIME column is the value the database records where present and blank otherwise; the file bytes are not sniffed. Developed against the author's own installation; no registered corpus image carries this app."),
        "paths": (
            "**/com.scaleup.chatai/databases/chat-ai.db",
            "**/com.android.providers.media/databases/external*.db",
            "**/com.google.android.providers.media.module/databases/external*.db",
            "**/data/media/0/Android/media/com.scaleup.chatai/Nova/*",
        ),
        "function": "get_nova_user_submissions",
        "output_types": ["standard", "lava"],
        "artifact_icon": "folder",
    }
}

import datetime
import os
import sqlite3
from scripts.ilapfuncs import (
    artifact_processor,
    logfunc,
    open_sqlite_db_readonly,
    check_in_media,
    get_file_path,
)


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


@artifact_processor
def get_nova_user_submissions(files_found, _report_folder, _seeker, _wrap_text):
    # Find databases
    nova_db = get_file_path(files_found, "chat-ai.db")
    media_db = next(
        (
            str(x)
            for x in files_found
            if "external" in str(x) and str(x).endswith(".db")
        ),
        None,
    )

    all_items = []
    processed_paths = set()

    # Pre-build lookup for files in the extraction to quickly find them by name
    # Focus on the Nova folder to avoid collisions
    nova_files_lookup = {}
    nova_path_part = "Android/media/com.scaleup.chatai/Nova"
    for f in files_found:
        if nova_path_part in str(f):
            nova_files_lookup[os.path.basename(f).lower()] = str(f)

    # 1. Database Indexed Lookup (MediaStore)
    media_lookup = {}
    if media_db:
        # A MediaStore database matches on every image whether or not Nova is
        # installed, and some builds carry no files table; a failed lookup
        # build must not kill the artifact.
        try:
            with open_sqlite_db_readonly(media_db) as db:
                cur = db.cursor()
                cur.execute("SELECT _display_name, _data FROM files WHERE _data IS NOT NULL")
                for name, path in cur.fetchall():
                    key = (name or os.path.basename(str(path))).lower()
                    media_lookup[key] = path
        except sqlite3.Error as exc:
            logfunc(f"Nova user submissions - MediaStore lookup unavailable ({exc})")

    # 2. Extract from Nova Chat DB
    if nova_db:
        with open_sqlite_db_readonly(nova_db) as db:
            cur = db.cursor()

            # Documents
            cur.execute(
                "SELECT hdd.name, hdd.mimeType, hd.text, hd.createdAt FROM HistoryDetailDocument hdd INNER JOIN HistoryDetail hd ON hd.id = hdd.historyDetailID"
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
                        "",
                        "",
                        _epoch_to_utc(ts),
                        "",
                        mime or "",
                        media_ref,
                        dev_path or "Not in MediaStore",
                    )
                )

            # Images
            cur.execute(
                "SELECT hdi.url, hdi.prompt, hd.text, hd.createdAt FROM HistoryDetailImage hdi INNER JOIN HistoryDetail hd ON hd.id = hdi.historyDetailID"
            )
            for url, prompt, msg, ts in cur.fetchall():
                fname = os.path.basename(url.split("?")[0])
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
                        "",
                        "",
                        _epoch_to_utc(ts),
                        "",
                        "",
                        media_ref,
                        dev_path or "Not in MediaStore",
                    )
                )

    # 3. Physical Sweep (Orphaned Files in /Nova)
    for file_path in files_found:
        if nova_path_part in str(file_path) and str(file_path) not in processed_paths:
            fname = os.path.basename(file_path)
            media_ref = check_in_media(str(file_path), name=fname) or '' 
            all_items.append(
                (
                    fname,
                    "Orphaned Media",
                    "Found in /Nova folder (No DB link)",
                    "",
                    "",
                    None,
                    "",
                    "",
                    media_ref,
                    str(file_path),
                )
            )

    headers = (
        "File Name",
        "Type",
        "Context",
        "Conv. Title",
        "UUID",
        ("Date (UTC)", "datetime"),
        "Size",
        "MIME",
        ("Media", "media"),
        "Path",
    )

    return headers, all_items, nova_db or "Filesystem"
