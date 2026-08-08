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

ASSISTANT_MAP = {
    1: "Margot Robbie",
    2: "Elon Musk",
    3: "Snoop Dogg",
    4: "Steve Jobs",
    5: "LeBron James",
    6: "Zendaya",
    7: "Steve Harvey",
    8: "Botanist",
    9: "Veterinarian",
    10: "Dietitian",
    11: "Accountant",
    12: "Architect",
    13: "Artist",
    14: "Chef",
    15: "Designer",
    16: "Software Developer",
    17: "Doctor",
    18: "Influencer",
    19: "Journalist",
    20: "Lawyer",
    21: "Math Teacher",
    22: "Personal Trainer",
    23: "Pilot",
    24: "Scientist",
    25: "Writer Assistant",
    26: "Taylor Swift",
    27: "Dermatologist",
    28: "Astrologer",
    29: "Fashion Designer",
    30: "Phoebe Buffay",
    31: "Thomas Shelby",
    32: "Barney Stinson",
    33: "Dwight Schrute",
    34: "Sub-Zero",
    35: "Pikachu",
    36: "Super Mario",
    37: "Hello Kitty",
    38: "Doctor Who",
    39: "Chandler Bing",
    40: "Michael Scott",
    41: "Walter White",
    42: "The Grinch",
    43: "Santa Claus",
    44: "Loki",
    45: "Dr. House",
    46: "Relationship Doctor",
    47: "Kylie Jenner",
    58: "Prophecy",
}


def get_assistant(assistant_id):
    if not assistant_id:
        return ""
    try:
        name = ASSISTANT_MAP.get(int(assistant_id))
        return (
            f"{name} ({assistant_id})" if name else f"Unknown Persona ({assistant_id})"
        )
    except (TypeError, ValueError):
        return str(assistant_id)


QUERY = """
SELECT
    h.id                        AS conv_id,
    h.UUID                      AS conv_uuid,
    h.title                     AS conv_title,
    h.chatBotModel              AS chat_bot_model,
    h.assistantId               AS assistant_id,
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
def get_nova_chatbot_conversations(files_found, report_folder, seeker, _wrap_text):
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
        except Exception as e:  # pylint: disable=broad-exception-caught
            logfunc(
                f"[nova_chatbot_conversations] Error building MediaStore lookup: {e}"
            )

    rows_raw = []
    try:
        with open_sqlite_db_readonly(nova_db) as db:
            cursor = db.cursor()
            cursor.execute(QUERY)
            rows_raw = cursor.fetchall()
    except Exception as e:  # pylint: disable=broad-exception-caught
        logfunc(f"[nova_chatbot_conversations] Error reading {nova_db}: {e}")
        return (), [], ""

    headers = (
        "Conv. ID",
        "Conv. UUID",
        "Conv. Title",
        "AI Model",
        "Assistant Persona",
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

        assistant_persona = get_assistant(row[4])

        raw_role = row[9]
        role_str = (
            "USER"
            if raw_role == 0
            else "AI ASSISTANT"
            if raw_role == 1
            else f"UNKNOWN ({raw_role})"
        )

        # A. Documents
        doc_names_raw = row[17]
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
        img_urls_raw = row[15]
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
                assistant_persona,
                "DELETED" if row[5] == 1 else "No",
                row[7],
                row[8] or "",
                role_str,
                row[10] or "",
                row[11] if row[11] is not None else "",
                row[12] or "",
                float(row[13]) / 1000 if row[13] else None,
                row[16] or "",
                img_media_refs[0] if img_media_refs else "",
                img_dev_path,
                row[15] or "",
                row[17] or "",
                doc_media_ref,
                doc_dev_path,
                row[19] or "",
                row[20] or "",
            )
        )

    return headers, rows, nova_db
