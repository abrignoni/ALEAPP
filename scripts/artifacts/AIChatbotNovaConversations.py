__artifacts_v2__ = {
    "nova_chatbot_conversations": {
        "name": "Conversations (Full Detail)",
        "description": (
            "Conversations from the AI Chatbot - Nova app, one row per message, joining "
            "History, HistoryDetail, HistoryDetailImage, HistoryDetailDocument and "
            "HistoryDetailLink, with the path the Android MediaStore index holds for each "
            "attached document and image."
        ),
        "author": "Guilherme Guilherme",
        "creation_date": "2026-05-30",
        "last_update_date": "2026-09-19",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": (
            "Sources: chat-ai.db and the Android MediaStore databases. The AI Model and Assistant Persona names are mapped from the numeric codes as observed in the app by the author; the mapping is not vendor-documented, so the stored code is shown beside every name and an unmapped code is reported as stored. A path shown as Not in MediaStore means no MediaStore row matched the file name, not that the file never existed locally. Attachment URLs are concatenated by SQLite and split on commas, so a URL containing a comma would split wrong; only the first image attachment is rendered as media. An extraction can carry one copy of each database per Android user and every copy is read, so the located at line lists each database and the row identifiers are per database. The committed test case carries no file under the app's shared media folder and no link record, so Image Media, Document Media and Link URL(s) have no value on any of its rows and Image Path reads Not in MediaStore throughout. Developed against the author's own installation; no registered corpus image carries this app."
        ),
        "paths": (
            "**/com.scaleup.chatai/databases/chat-ai.db",
            "**/com.android.providers.media/databases/external*.db",
            "**/com.google.android.providers.media.module/databases/external*.db",
        ),
        "output_types": ["standard", "lava"],
        "artifact_icon": "message-square",
    }
}

import datetime
import os
from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    logfunc,
    open_sqlite_db_readonly,
    check_in_media,
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
def nova_chatbot_conversations(context):
    # unique_files collapses the data/data, data/user/0 and data_mirror views of one
    # file and keeps a second Android user's own copy, so both users are reported.
    files_found = [str(f) for f in unique_files(context)]
    nova_dbs = sorted(f for f in files_found if os.path.basename(f) == "chat-ai.db")
    media_dbs = sorted(
        f for f in files_found
        if os.path.basename(f).startswith("external") and f.endswith(".db")
    )

    if not nova_dbs:
        logfunc("Nova conversations - chat-ai.db not found")
        return (), [], ""

    # Pre-build lookup for local files in the extraction
    nova_files_lookup = {}
    nova_path_part = "Android/media/com.scaleup.chatai/Nova"
    for f in files_found:
        if nova_path_part in f:
            nova_files_lookup[os.path.basename(f).lower()] = f

    media_lookup = {}
    sources = []
    for media_db in media_dbs:
        try:
            with open_sqlite_db_readonly(media_db) as db:
                cur = db.cursor()
                cur.execute(
                    "SELECT _display_name, _data FROM files WHERE _data IS NOT NULL"
                )
                for display_name, data_path in cur.fetchall():
                    key = (display_name or os.path.basename(str(data_path))).lower()
                    media_lookup[key] = data_path
            sources.append(media_db)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logfunc(f"Nova conversations - MediaStore lookup unavailable ({e})")

    rows_raw = []
    for nova_db in nova_dbs:
        try:
            with open_sqlite_db_readonly(nova_db) as db:
                cursor = db.cursor()
                cursor.execute(QUERY)
                rows_raw.extend(cursor.fetchall())
            sources.append(nova_db)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logfunc(f"Nova conversations - could not read the database ({e})")

    if not rows_raw:
        return (), [], "\n".join(sources)

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
        doc_dev_path = "Not in MediaStore"

        if doc_names_raw:
            primary_doc = doc_names_raw.split(",")[0].strip()
            key = primary_doc.lower()
            doc_dev_path = media_lookup.get(key, "Not in MediaStore")
            ext_path = nova_files_lookup.get(key)
            if ext_path:
                doc_media_ref = check_in_media(ext_path, name=primary_doc) or ''

        # B. Images
        img_urls_raw = row[15]
        img_media_refs = []
        img_dev_path = "Not in MediaStore"

        if img_urls_raw:
            # Handle comma separated images
            url_parts = img_urls_raw.split(",")
            for i, url_part in enumerate(url_parts):
                img_name = os.path.basename(url_part.strip().split("?")[0])
                key = img_name.lower()

                # We map dev path for the first one for the column
                if i == 0:
                    img_dev_path = media_lookup.get(key, "Not in MediaStore")

                ext_path = nova_files_lookup.get(key)
                if ext_path:
                    ref = check_in_media(ext_path, name=img_name)
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
                _epoch_to_utc(row[13]),
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

    return headers, rows, "\n".join(sources)
