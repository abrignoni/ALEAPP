__artifacts_v2__ = {
    "nova_chatbot_conversations": {
        "name": "Conversations (Full Detail)",
        "description": (
            "Reconstructs full conversations from the AI Chatbot - Nova app by joining "
            "History, HistoryDetail, HistoryDetailImage, HistoryDetailDocument, and "
            "HistoryDetailLink tables. Cross-references local file attachments with the "
            "Android MediaStore database to map real physical file storage paths for both "
            "documents and user-submitted images."
        ),
        "author": "Guilherme Guilherme",
        "version": "1.1",
        "date": "2026-05-21",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": "Sources: chat-ai.db and Android MediaStore databases.",
        "paths": (
            "*/com.scaleup.chatai/databases/chat-ai.db",
            "*/com.android.providers.media/databases/external*.db",
            "*/com.google.android.providers.media.module/databases/external*.db",
        ),
        "function": "get_nova_chatbot_conversations",
        "output_types": "standard",
        "artifact_icon": "message-square",
    }
}

import os
import datetime
from datetime import timezone
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import (
    logfunc,
    tsv,
    timeline,
    open_sqlite_db_readonly,
    media_to_html,
)

CHAT_BOT_MODEL_MAP = {
    0: "ChatGPT 3.5",
    1: "GPT-5",
    2: "GPT-4o",
    3: "Bard / Image Gen.",
    4: "Image Generator",
    5: "Vision",
    6: "Google Vision",
    7: "Document",
    8: "LLaMA 2",
    9: "Nova",
    10: "Gemini",
    11: "Superbot",
    12: "Logo Generator",
    13: "Tattoo Generator",
    14: "Web Search",
    15: "Claude",
    16: "DeepSeek",
    17: "Signature Generator",
    18: "Mistral",
    19: "Grok",
    20: "DeepSeek R1",
    21: "AI Filter",
    22: "Voice Chat",
    23: "Snap & Solve",
    24: "Study Planner",
    25: "Quiz Maker",
    26: "Essay Helper",
    27: "Gemini 3 Pro",
    28: "GPT-5.1",
    29: "GPT-4o Mini",
}

QUERY = """
SELECT
    h.id                        AS conv_id,
    h.UUID                      AS conv_uuid,
    h.title                     AS conv_title,
    h.chatBotModel              AS chat_bot_model,
    h.softDeleted               AS soft_deleted,
    h.syncState                 AS conv_sync_state,

    hd.id                       AS msg_id,
    hd.UUID                     AS msg_uuid,
    hd.type                     AS msg_type,
    hd.text                     AS msg_text,
    hd.token                    AS msg_token,
    hd.reasoningContent         AS msg_reasoning,
    hd.createdAt                AS msg_created_at,
    hd.syncState                AS msg_sync_state,

    GROUP_CONCAT(DISTINCT hdi.url)          AS img_urls,
    GROUP_CONCAT(DISTINCT hdi.prompt)       AS img_prompts,

    GROUP_CONCAT(DISTINCT hdd.name)         AS doc_names,
    GROUP_CONCAT(DISTINCT hdd.mimeType)     AS doc_mimes,
    GROUP_CONCAT(DISTINCT hdd.url)          AS doc_urls,

    GROUP_CONCAT(DISTINCT hdl.url)          AS link_urls

FROM History h
INNER JOIN HistoryDetail hd ON hd.historyID = h.id
LEFT JOIN HistoryDetailImage hdi ON hdi.historyDetailID = hd.id
LEFT JOIN HistoryDetailDocument hdd ON hdd.historyDetailID = hd.id
LEFT JOIN HistoryDetailLink hdl ON hdl.historyDetailID = hd.id
GROUP BY hd.id
ORDER BY h.id ASC, hd.createdAt ASC
"""


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


def _convert_ms_timestamp(ms):
    """Safely converts Unix millisecond timestamp using modern timezone.utc."""
    if ms is None:
        return ""
    try:
        return datetime.datetime.fromtimestamp(float(ms) / 1000, timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )
    except (OSError, OverflowError, ValueError):
        return str(ms)


def get_nova_chatbot_conversations(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Nova Full Conversations")

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
        logfunc("[nova_chatbot_conversations] Nova database file not found.")
        return

    extraction_root = getattr(seeker, "search_dir", "") or ""
    media_lookup = {}

    # 1. Map the MediaStore database entries to verify files present on local storage
    if media_db:
        try:
            db = open_sqlite_db_readonly(media_db)
            cur = db.cursor()
            cur.execute("""
                SELECT _display_name, _data 
                FROM files 
                WHERE _data IS NOT NULL
            """)
            for display_name, data_path in cur.fetchall():
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
            logfunc(
                f"[nova_chatbot_conversations] Error building MediaStore lookup: {e}"
            )

    # 2. Query chat timeline logs
    try:
        db = open_sqlite_db_readonly(nova_db)
        cursor = db.cursor()
        cursor.execute(QUERY)
        rows_raw = cursor.fetchall()
        db.close()
    except Exception as e:
        logfunc(f"[nova_chatbot_conversations] Error reading {nova_db}: {e}")
        return

    if not rows_raw:
        logfunc(f"[nova_chatbot_conversations] No records found in {nova_db}.")
        return

    headers = (
        "Conv. ID",
        "Conv. UUID",
        "Conv. Title",
        "AI Model",
        "Conv. Deleted",
        "Msg. ID",
        "Msg. UUID",
        "Role",
        "Message Text",
        "Token Count",
        "Reasoning Content",
        "Message Timestamp (UTC)",
        "Image Attachment Prompts",
        "Image Physical Path",
        "Image Firebase Path",
        "Document Attachment Name",
        "Document Physical Path",
        "Document Firebase Path",
        "Link URL(s)",
    )

    rows = []
    for row in rows_raw:
        model_int = row[3]
        model_name = "Unknown"
        if model_int is not None:
            name_lookup = CHAT_BOT_MODEL_MAP.get(model_int)
            model_name = (
                f"{name_lookup} ({model_int})"
                if name_lookup
                else f"Unknown Model ({model_int})"
            )

        raw_role = row[8]
        role_str = (
            "USER"
            if raw_role == 0
            else "AI ASSISTANT"
            if raw_role == 1
            else f"UNKNOWN ({raw_role})"
        )

        # A. Cross-reference documents using mapped MediaStore indices
        doc_names_raw = row[16]
        doc_phys_path_resolved = "Cloud-only (Firebase Storage)"

        if doc_names_raw:
            primary_doc = doc_names_raw.split(",")[0].strip()
            match_key = primary_doc.lower()
            if match_key in media_lookup:
                match = media_lookup[match_key]
                if match["local_path"]:
                    media_to_html(primary_doc, match["local_path"], report_folder)
                doc_phys_path_resolved = _parse_path(match["data_path"])

        # B. Cross-reference images inside conversation rows for local paths if available
        img_urls_raw = row[14]
        img_phys_path_resolved = "Cloud-only (Firebase Storage)"

        if img_urls_raw:
            # We evaluate the first image in the group for table display mapping
            primary_img_url = img_urls_raw.split(",")[0].strip()
            # Clean remote arguments out if present inside URL structures
            img_name = os.path.basename(primary_img_url.split("?")[0])
            img_key = img_name.lower()

            if img_key in media_lookup:
                match = media_lookup[img_key]
                if match["local_path"]:
                    media_to_html(img_name, match["local_path"], report_folder)
                img_phys_path_resolved = _parse_path(match["data_path"])

            # Also ensure any secondary images in a comma-separated list pass safely into the gallery pipelines
            if "," in img_urls_raw:
                for url_part in img_urls_raw.split(",")[1:]:
                    sec_name = os.path.basename(url_part.strip().split("?")[0])
                    sec_key = sec_name.lower()
                    if sec_key in media_lookup and media_lookup[sec_key]["local_path"]:
                        media_to_html(
                            sec_name, media_lookup[sec_key]["local_path"], report_folder
                        )

        rows.append(
            (
                row[0],
                row[1] or "",
                row[2] or "",
                model_name,
                "DELETED" if row[4] == 1 else "No",
                row[6],
                row[7] or "",
                role_str,
                row[9] or "",
                row[10] if row[10] is not None else "",
                row[11] or "",
                _convert_ms_timestamp(row[12]),
                row[15] or "",
                img_phys_path_resolved,
                row[14] or "",
                row[16] or "",
                doc_phys_path_resolved,
                row[18] or "",
                row[19] or "",
            )
        )

    report_name = "Conversations (Full Detail)"
    report = ArtifactHtmlReport(report_name)
    report.start_artifact_report(report_folder, report_name)
    report.add_script()

    # Enforce strict framework-side HTML cell escaping to protect against code injection
    report.write_artifact_data_table(headers, rows, nova_db, html_escape=True)
    report.end_artifact_report()

    tsv(report_folder, headers, rows, report_name, nova_db)
    timeline(report_folder, report_name, rows, headers)
    logfunc(
        f"[nova_chatbot_conversations] Processed {len(rows)} timeline message items."
    )
