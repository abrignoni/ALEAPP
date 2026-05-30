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
        "version": "1.2",
        "date": "2026-05-30",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": "Sources: chat-ai.db and Android MediaStore databases.",
        "paths": (
            "**/com.scaleup.chatai/databases/chat-ai.db",
            "**/com.android.providers.media/databases/external*.db",
            "**/com.google.android.providers.media.module/databases/external*.db",
        ),
        "function": "get_nova_chatbot_conversations",
        "output_types": ["standard", "lava"],
        "artifact_icon": "message-square",
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


@artifact_processor
def get_nova_chatbot_conversations(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Nova Full Conversations")

    # Use framework-injected artifact_info
    artifact_info = SimpleNamespace(**get_nova_chatbot_conversations.artifact_info)
    artifact_info.filename = __file__

    nova_db = get_file_path(files_found, "chat-ai.db")
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
        return (), [], ""

    # Pre-build lookup for local files in the extraction
    nova_files_lookup = {}
    nova_path_part = "Android/media/com.scaleup.chatai/Nova"
    for f in files_found:
        if nova_path_part in str(f):
            nova_files_lookup[os.path.basename(f).lower()] = str(f)

    media_lookup = {}
    if media_db:
        try:
            with open_sqlite_db_readonly(media_db) as db:
                cur = db.cursor()
                cur.execute(
                    "SELECT _display_name, _data FROM files WHERE _data IS NOT NULL"
                )
                for display_name, data_path in cur.fetchall():
                    key = (display_name or os.path.basename(str(data_path))).lower()
                    media_lookup[key] = data_path
        except Exception as e:
            logfunc(
                f"[nova_chatbot_conversations] Error building MediaStore lookup: {e}"
            )

    rows_raw = []
    try:
        with open_sqlite_db_readonly(nova_db) as db:
            cursor = db.cursor()
            cursor.execute(QUERY)
            rows_raw = cursor.fetchall()
    except Exception as e:
        logfunc(f"[nova_chatbot_conversations] Error reading {nova_db}: {e}")
        return (), [], ""

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
        ("Message Timestamp (UTC)", "datetime"),
        "Image Attachment Prompts",
        ("Image Media", "media"),
        "Image Path",
        "Image Cloud URL",
        "Document Name",
        ("Document Media", "media"),
        "Document Path",
        "Document Cloud URL",
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

        # A. Documents
        doc_names_raw = row[16]
        doc_media_ref = ""
        doc_dev_path = "Cloud-only"

        if doc_names_raw:
            primary_doc = doc_names_raw.split(",")[0].strip()
            key = primary_doc.lower()
            doc_dev_path = media_lookup.get(key, "Cloud-only")
            ext_path = nova_files_lookup.get(key)
            if ext_path:
                doc_media_ref = check_in_media(
                    artifact_info,
                    report_folder,
                    seeker,
                    files_found,
                    ext_path,
                    primary_doc,
                )

        # B. Images
        img_urls_raw = row[14]
        img_media_refs = []
        img_dev_path = "Cloud-only"

        if img_urls_raw:
            # Handle comma separated images
            url_parts = img_urls_raw.split(",")
            for i, url_part in enumerate(url_parts):
                img_name = os.path.basename(url_part.strip().split("?")[0])
                key = img_name.lower()

                # We map dev path for the first one for the column
                if i == 0:
                    img_dev_path = media_lookup.get(key, "Cloud-only")

                ext_path = nova_files_lookup.get(key)
                if ext_path:
                    ref = check_in_media(
                        artifact_info,
                        report_folder,
                        seeker,
                        files_found,
                        ext_path,
                        img_name,
                    )
                    if ref:
                        img_media_refs.append(ref)

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
                float(row[12]) / 1000 if row[12] else None,
                row[15] or "",
                img_media_refs[0] if img_media_refs else "",
                img_dev_path,
                row[14] or "",
                row[16] or "",
                doc_media_ref,
                doc_dev_path,
                row[18] or "",
                row[19] or "",
            )
        )

    return headers, rows, nova_db
