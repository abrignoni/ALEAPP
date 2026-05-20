__artifacts_v2__ = {
    "nova_user_submissions": {
        "name": "Nova AI Chatbot - User Media Submissions",
        "description": (
            "Identifies ALL media files submitted by the user to Nova AI Chatbot. "
            "This includes uploaded documents and photos captured using the in-app camera. "
            "The artifact lists recovered filenames, user context, timestamps, MIME types, "
            "and resolved physical paths from the extracted filesystem."
        ),
        "author": "Guilherme Guilherme",
        "version": "2.7",
        "date": "2026-05-20",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": (
            "Sources: chat-ai.db and Android MediaStore databases. "
            "Resolves extracted filesystem paths and falls back to filename search when needed. "
            "This module does not embed previews; it focuses on metadata and physical path reporting."
        ),
        "paths": (
            "*/com.scaleup.chatai/databases/chat-ai.db",
            "*/com.android.providers.media/databases/external*.db",
            "*/com.google.android.providers.media.module/databases/external*.db",
        ),
        "function": "get_nova_user_submissions",
    }
}

import os
import csv
import sqlite3
import datetime
import html as html_module
from scripts.artifact_report import ArtifactHtmlReport
import scripts.ilapfuncs


def _e(text):
    return html_module.escape(str(text)) if text else ""


def _convert_ms_timestamp(ms):
    if ms is None:
        return ""
    try:
        return datetime.datetime.utcfromtimestamp(ms / 1000).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )
    except Exception:
        return str(ms)


def _convert_sec_timestamp(ts):
    if ts is None:
        return ""
    try:
        return datetime.datetime.utcfromtimestamp(int(ts)).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )
    except Exception:
        return str(ts)


def _format_file_size(size_bytes):
    if size_bytes is None:
        return ""
    try:
        size_bytes = int(size_bytes)
        if size_bytes < 1024:
            return f"{size_bytes} B"
        if size_bytes < 1024**2:
            return f"{size_bytes / 1024:.1f} KB"
        if size_bytes < 1024**3:
            return f"{size_bytes / (1024**2):.1f} MB"
        return f"{size_bytes / (1024**3):.2f} GB"
    except Exception:
        return str(size_bytes)


def _normalize_media_path(media_path):
    if not media_path:
        return None
    p = media_path.replace("\\", "/")
    if p.startswith("/storage/emulated/0/"):
        p = p.replace("/storage/emulated/0/", "/data/media/0/", 1)
    return p


def _resolve_extraction_path(extraction_root, media_path):
    if not extraction_root or not media_path:
        return None

    normalized = _normalize_media_path(media_path)
    candidate = os.path.normpath(os.path.join(extraction_root, normalized.lstrip("/")))
    if os.path.exists(candidate):
        return candidate

    fname = os.path.basename(normalized)
    filename_candidate = os.path.normpath(os.path.join(extraction_root, fname))
    if os.path.exists(filename_candidate):
        return filename_candidate

    data_media_candidate = os.path.normpath(
        os.path.join(extraction_root, "data/media/0", fname)
    )
    if os.path.exists(data_media_candidate):
        return data_media_candidate

    for root, dirs, files in os.walk(extraction_root):
        if fname in files:
            return os.path.join(root, fname)

    return None


def get_nova_user_submissions(files_found, report_folder, seeker, wrap_text):
    nova_db = None
    media_db = None

    for file_found in files_found:
        file_found = str(file_found)
        if "chat-ai.db" in file_found:
            nova_db = file_found
        elif "external" in file_found and file_found.endswith(".db"):
            media_db = file_found

    if not nova_db:
        scripts.ilapfuncs.logfunc("[nova_user_submissions] Nova database not found.")
        return

    extraction_root = getattr(seeker, "search_dir", "")
    scripts.ilapfuncs.logfunc(
        f"[nova_user_submissions] Extraction root: {extraction_root}"
    )

    media_lookup = {}

    if media_db and os.path.exists(media_db):
        try:
            db = sqlite3.connect(media_db)
            cursor = db.cursor()
            cursor.execute("""
                SELECT _display_name, _data, _size, date_added, mime_type
                FROM files
                WHERE _data IS NOT NULL
            """)
            for (
                display_name,
                data_path,
                size,
                date_added,
                mime_type,
            ) in cursor.fetchall():
                normalized_path = _normalize_media_path(data_path or "")
                if not normalized_path:
                    continue

                if not any(
                    x in normalized_path.lower()
                    for x in ["/download/", "/nova/", "/com.scaleup.chatai/"]
                ):
                    continue

                key = (display_name or os.path.basename(normalized_path)).lower()
                media_lookup[key] = {
                    "media_path": normalized_path,
                    "extraction_path": _resolve_extraction_path(
                        extraction_root, normalized_path
                    ),
                    "size": size,
                    "timestamp": date_added,
                    "mime": mime_type or "",
                }

            db.close()
        except Exception as e:
            scripts.ilapfuncs.logfunc(
                f"[nova_user_submissions] Error reading MediaStore: {e}"
            )

    all_items = []

    query_docs = """
        SELECT
            hdd.name,
            hdd.url,
            hdd.mimeType,
            hdd.size,
            hd.text,
            hd.createdAt,
            h.title
        FROM HistoryDetailDocument hdd
        INNER JOIN HistoryDetail hd ON hd.id = hdd.historyDetailID
        INNER JOIN History h ON h.id = hd.historyID
        WHERE hd.type = 0
        ORDER BY hd.createdAt DESC
    """

    try:
        db = sqlite3.connect(nova_db)
        cursor = db.cursor()
        cursor.execute(query_docs)
        for (
            file_name,
            firebase_url,
            mime_type,
            size_db,
            message,
            created_at,
            conversation,
        ) in cursor.fetchall():
            media_match = media_lookup.get((file_name or "").lower())
            all_items.append(
                {
                    "type": "submitted_document",
                    "name": file_name or "Unknown",
                    "firebase_url": firebase_url or "",
                    "mime": mime_type or "",
                    "size_db": size_db,
                    "message": message or "",
                    "timestamp": created_at,
                    "conversation": conversation or "Untitled",
                    "media_path": media_match["media_path"] if media_match else None,
                    "extraction_path": media_match["extraction_path"]
                    if media_match
                    else None,
                }
            )
        db.close()
    except Exception as e:
        scripts.ilapfuncs.logfunc(
            f"[nova_user_submissions] Error querying documents: {e}"
        )

    if media_db and os.path.exists(media_db):
        try:
            db = sqlite3.connect(media_db)
            cursor = db.cursor()
            cursor.execute("""
                SELECT _display_name, _data, _size, date_added, mime_type
                FROM files
                WHERE bucket_display_name = 'Nova' OR _data LIKE '%/Nova/%'
                ORDER BY date_added DESC
            """)
            for (
                display_name,
                data_path,
                size,
                date_added,
                mime_type,
            ) in cursor.fetchall():
                normalized_path = _normalize_media_path(data_path or "")
                extraction_path = _resolve_extraction_path(
                    extraction_root, normalized_path
                )
                all_items.append(
                    {
                        "type": "camera_photo",
                        "name": display_name
                        or os.path.basename(normalized_path or "")
                        or "Unknown",
                        "mime": mime_type or "image/jpeg",
                        "size_db": size,
                        "message": "",
                        "timestamp": date_added,
                        "conversation": "Camera photo (not associated with a message)",
                        "media_path": normalized_path,
                        "extraction_path": extraction_path,
                    }
                )
            db.close()
        except Exception as e:
            scripts.ilapfuncs.logfunc(
                f"[nova_user_submissions] Error querying camera photos: {e}"
            )

    deduped = []
    seen = set()
    for item in all_items:
        key = (item["name"].lower(), item.get("media_path") or "")
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    deduped.sort(key=lambda x: x.get("timestamp", 0) or 0, reverse=True)

    if not deduped:
        scripts.ilapfuncs.logfunc("[nova_user_submissions] No media found.")
        return

    headers = (
        "File Name",
        "Type",
        "User Message / Context",
        "Conversation",
        "Date (UTC)",
        "Size",
        "MIME Type",
        "Physical Path",
    )

    rows = []
    tsv_rows = []

    for item in deduped:
        type_label = (
            "📤 Submitted to AI"
            if item["type"] == "submitted_document"
            else "📷 Camera Photo"
        )
        context = item.get("message") or "<em>No message recorded</em>"
        if isinstance(context, str) and len(context) > 150:
            context = _e(context[:150] + "...")
        date_str = (
            _convert_ms_timestamp(item["timestamp"])
            if item["type"] == "submitted_document"
            else _convert_sec_timestamp(item["timestamp"])
        )
        size_str = _format_file_size(item.get("size_db"))

        if item.get("extraction_path") and os.path.exists(item["extraction_path"]):
            physical_path = item["extraction_path"]
        elif item.get("media_path"):
            physical_path = item["media_path"]
        else:
            physical_path = "Cloud-only (Firebase Storage)"

        rows.append(
            (
                _e(item["name"]),
                type_label,
                context,
                _e(item["conversation"]),
                date_str,
                size_str,
                _e(item.get("mime") or ""),
                _e(physical_path),
            )
        )

        tsv_rows.append(
            (
                item["name"],
                type_label,
                context,
                item["conversation"],
                date_str,
                size_str,
                item.get("mime") or "",
                physical_path,
            )
        )

    report_name = "Nova AI Chatbot - User Media Submissions"
    report = ArtifactHtmlReport(report_name)
    report.start_artifact_report(report_folder, report_name)
    report.add_script()
    report.write_artifact_data_table(headers, rows, nova_db, html_escape=False)
    report.end_artifact_report()

    tsv_path = os.path.join(report_folder, f"{report_name}.tsv")
    with open(tsv_path, "w", newline="", encoding="utf-8") as tsvfile:
        writer = csv.writer(tsvfile, delimiter="\t")
        writer.writerow(
            [
                "File Name",
                "Type",
                "User Message",
                "Conversation",
                "Date (UTC)",
                "Size",
                "MIME Type",
                "Physical Path",
            ]
        )
        writer.writerows(tsv_rows)

    scripts.ilapfuncs.logfunc(
        f"[nova_user_submissions] Found {len(deduped)} total items."
    )
