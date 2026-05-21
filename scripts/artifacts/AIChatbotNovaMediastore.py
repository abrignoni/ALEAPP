__artifacts_v2__ = {
    "nova_user_submissions": {
        "name": "User Media Submissions",
        "description": (
            "Identifies media files submitted by the user to Nova AI Chatbot, including "
            "uploaded documents and photos captured using the in-app camera. The artifact "
            "lists recovered filenames, conversation context, timestamps, MIME types, and resolved "
            "physical paths from the extracted filesystem."
        ),
        "author": "Guilherme Guilherme",
        "version": "3.3",
        "date": "2026-05-21",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": "Sources: chat-ai.db and Android MediaStore databases.",
        "paths": (
            "*/com.scaleup.chatai/databases/chat-ai.db",
            "*/com.android.providers.media/databases/external*.db",
            "*/com.google.android.providers.media.module/databases/external*.db",
        ),
        "function": "get_nova_user_submissions",
        "output_types": "standard",
        "artifact_icon": "folder",
    }
}

import os
import datetime
from datetime import timezone
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, open_sqlite_db_readonly, media_to_html


def _parse_path(raw_path):
    """Normalizes paths and slices them to always start at /data."""
    if not raw_path:
        return ""
    normalized = str(raw_path).replace("\\", "/")
    if "/data/" in normalized:
        return "/data/" + normalized.split("/data/", 1)[1]
    elif "data/data/" in normalized:
        return "/data/data/" + normalized.split("data/data/", 1)[1]
    return normalized


def get_nova_user_submissions(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Nova User Media Submissions")

    files_found = [
        x for x in files_found if not x.endswith(("-journal", "-wal", "-shm"))
    ]
    nova_db = next((str(x) for x in files_found if "chat-ai.db" in str(x)), None)
    media_db = next(
        (
            str(x)
            for x in files_found
            if "external" in str(x) and str(x).endswith(".db")
        ),
        None,
    )

    if not nova_db:
        logfunc("[nova_user_submissions] Nova database not found.")
        return

    extraction_root = getattr(seeker, "search_dir", "") or ""
    media_lookup = {}

    # 1. Map the MediaStore database records to see what is on local storage
    if media_db:
        try:
            db = open_sqlite_db_readonly(media_db)
            cur = db.cursor()
            cur.execute("""
                SELECT _display_name, _data, _size, date_added, mime_type
                FROM files
                WHERE _data IS NOT NULL
            """)
            for display_name, data_path, size, date_added, mime_type in cur.fetchall():
                local_path = ""
                if data_path:
                    clean_rel = str(data_path).replace("\\", "/").lstrip("/")
                    if clean_rel.startswith("storage/emulated/0/"):
                        clean_rel = clean_rel.replace(
                            "storage/emulated/0/", "data/media/0/", 1
                        )

                    candidate_path = os.path.join(extraction_root, clean_rel)
                    if os.path.exists(candidate_path):
                        local_path = candidate_path

                key = (display_name or os.path.basename(str(data_path))).lower()
                media_lookup[key] = {"data_path": data_path, "local_path": local_path}
            db.close()
        except Exception as e:
            logfunc(f"[nova_user_submissions] Error building MediaStore lookup: {e}")

    all_items = []

    # 2. Process chat database attachments and cross-reference with MediaStore
    try:
        db = open_sqlite_db_readonly(nova_db)
        cur = db.cursor()
        cur.execute("""
            SELECT
                hdd.name,
                hdd.mimeType,
                hdd.size,
                hd.text,
                hd.createdAt,
                h.title,
                h.UUID
            FROM HistoryDetailDocument hdd
            INNER JOIN HistoryDetail hd ON hd.id = hdd.historyDetailID
            INNER JOIN History h ON h.id = hd.historyID
            WHERE hd.type = 0
            ORDER BY hd.createdAt DESC
        """)
        for (
            file_name,
            mime_type,
            size_db,
            message,
            created_at,
            conversation,
            conv_uuid,
        ) in cur.fetchall():
            mtime_str = ""
            if created_at:
                try:
                    mtime_str = datetime.datetime.fromtimestamp(
                        float(created_at) / 1000, timezone.utc
                    ).strftime("%Y-%m-%d %H:%M:%S UTC")
                except Exception:
                    mtime_str = str(created_at)

            match_key = (file_name or "").lower()
            if match_key in media_lookup:
                match = media_lookup[match_key]
                if match["local_path"]:
                    # Correctly links local images into ALEAPP's standard thumb pipeline
                    media_to_html(file_name, match["local_path"], report_folder)
                display_path = _parse_path(match["data_path"])
            else:
                display_path = "Cloud-only (Firebase Storage)"

            all_items.append(
                (
                    file_name or "Unknown",
                    "Submitted to AI",
                    message or "",
                    conversation or "Untitled",
                    conv_uuid or "",
                    mtime_str,
                    size_db if size_db is not None else "",
                    mime_type or "",
                    display_path,
                )
            )
        db.close()
    except Exception as e:
        logfunc(f"[nova_user_submissions] Error querying documents: {e}")

    # 3. Process standalone camera storage entries matching the application context
    if media_db:
        try:
            db = open_sqlite_db_readonly(media_db)
            cur = db.cursor()
            cur.execute("""
                SELECT _display_name, _data, _size, date_added, mime_type
                FROM files
                WHERE bucket_display_name = 'Nova' OR _data LIKE '%/Nova/%'
                ORDER BY date_added DESC
            """)
            for display_name, data_path, size, date_added, mime_type in cur.fetchall():
                mtime_str = ""
                if date_added:
                    try:
                        mtime_str = datetime.datetime.fromtimestamp(
                            int(date_added), timezone.utc
                        ).strftime("%Y-%m-%d %H:%M:%S UTC")
                    except Exception:
                        mtime_str = str(date_added)

                fname = display_name or (
                    os.path.basename(str(data_path)) if data_path else "Unknown"
                )

                clean_rel = str(data_path).replace("\\", "/").lstrip("/")
                if clean_rel.startswith("storage/emulated/0/"):
                    clean_rel = clean_rel.replace(
                        "storage/emulated/0/", "data/media/0/", 1
                    )

                local_path = os.path.join(extraction_root, clean_rel)
                if os.path.exists(local_path):
                    media_to_html(fname, local_path, report_folder)

                all_items.append(
                    (
                        fname,
                        "Camera Photo",
                        "",
                        "Camera photo (not associated with a message)",
                        "",  # Camera pictures do not have an associated conversation UUID
                        mtime_str,
                        size if size is not None else "",
                        mime_type or "image/jpeg",
                        _parse_path(data_path),
                    )
                )
            db.close()
        except Exception as e:
            logfunc(f"[nova_user_submissions] Error querying camera photos: {e}")

    if not all_items:
        logfunc("[nova_user_submissions] No media found.")
        return

    # Deduplicate entries safely using filename and localized storage path attributes
    deduped = []
    seen = set()
    for row in all_items:
        # Deduplicate using filename (index 0) and physical path data (index 8)
        key = (row[0].lower(), row[8])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)

    report_name = "User Media Submissions"
    report = ArtifactHtmlReport(report_name)
    report.start_artifact_report(report_folder, report_name)
    report.add_script()

    headers = (
        "File Name",
        "Type",
        "User Message / Context",
        "Conversation Title",
        "Conv. UUID",
        "Date (UTC)",
        "Size (Bytes)",
        "MIME Type",
        "Path",
    )

    # Compliant HTML injection vulnerability protection handled securely by the framework via DataTables
    report.write_artifact_data_table(
        headers,
        deduped,
        nova_db,
        table_id="NovaUserSubmissions",
        html_escape=True,
    )
    report.end_artifact_report()

    tsv(report_folder, headers, deduped, report_name, nova_db)
    logfunc(f"[nova_user_submissions] Found {len(deduped)} total items.")
