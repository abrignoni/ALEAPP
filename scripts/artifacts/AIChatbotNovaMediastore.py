__artifacts_v2__ = {
    "nova_user_submissions": {
        "name": "User Media Submissions",
        "description": "Extracts Nova AI media. Identifies files via database indexing (MediaStore) and performs a filesystem sweep for orphaned camera captures.",
        "author": "Guilherme Guilherme",
        "version": "3.6",
        "date": "2026-05-30",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": "Integrates chat-ai.db history with physical filesystem discovery. Note: chat-ai.db contains text data only, not media files.",
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

import os
from types import SimpleNamespace
from scripts.ilapfuncs import (
    artifact_processor,
    logfunc,
    open_sqlite_db_readonly,
    check_in_media,
    get_file_path,
)


@artifact_processor
def get_nova_user_submissions(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing Nova User Media (Logic + Physical Sweep)")

    # Use the artifact_info injected by the framework (cleaner than inspect.stack)
    artifact_info = SimpleNamespace(**get_nova_user_submissions.artifact_info)
    artifact_info.filename = __file__

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
        with open_sqlite_db_readonly(media_db) as db:
            cur = db.cursor()
            cur.execute("SELECT _display_name, _data FROM files WHERE _data IS NOT NULL")
            for name, path in cur.fetchall():
                key = (name or os.path.basename(str(path))).lower()
                media_lookup[key] = path

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
                    media_ref = check_in_media(
                        artifact_info, report_folder, seeker, files_found, ext_path, name
                    )
                    processed_paths.add(ext_path)

                all_items.append(
                    (
                        name,
                        "Document",
                        msg,
                        "",
                        "",
                        float(ts) / 1000 if ts else None,
                        "",
                        mime,
                        media_ref,
                        dev_path or "Cloud-only",
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
                    media_ref = check_in_media(
                        artifact_info,
                        report_folder,
                        seeker,
                        files_found,
                        ext_path,
                        fname,
                    )
                    processed_paths.add(ext_path)

                all_items.append(
                    (
                        fname,
                        "Image",
                        f"Msg: {msg} | Prompt: {prompt}",
                        "",
                        "",
                        float(ts) / 1000 if ts else None,
                        "",
                        "image/jpeg",
                        media_ref,
                        dev_path or "Cloud-only",
                    )
                )

    # 3. Physical Sweep (Orphaned Files in /Nova)
    for file_path in files_found:
        if nova_path_part in str(file_path) and str(file_path) not in processed_paths:
            fname = os.path.basename(file_path)
            media_ref = check_in_media(
                artifact_info, report_folder, seeker, files_found, str(file_path), fname
            )
            all_items.append(
                (
                    fname,
                    "Orphaned Media",
                    "Found in /Nova folder (No DB link)",
                    "",
                    "",
                    None,
                    "",
                    "image/jpeg",
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
