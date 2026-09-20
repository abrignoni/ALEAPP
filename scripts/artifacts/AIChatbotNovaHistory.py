__artifacts_v2__ = {
    "nova_chatbot_history": {
        "name": "History",
        "description": "Extracts conversation index from Nova AI Chatbot",
        "author": "Guilherme Guilherme",
        "creation_date": "2026-05-29",
        "last_update_date": "2026-09-19",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": (
            "The AI Model and Assistant Persona names are mapped from the numeric codes as observed in the app by the author; the mapping is not vendor-documented, so the stored code is shown beside every name and an unmapped code is reported as stored. Role reads type 0 as USER and 1 as ASSISTANT on the same basis. Stored epochs are read as milliseconds above 1e11 and as seconds below it, and reported in UTC; every timestamp in the tested extraction was a 13-digit millisecond value. An extraction can carry one chat-ai.db per Android user and every copy is read, so the located at line lists each database and the row identifiers are per database. Developed against the author's own installation; no registered corpus image carries this app. The committed test case is the author's own extraction of the app's private data directory. The store's MyBot table holds two integer columns and no text, and its Assistant table held no rows in the tested extraction, so neither is reported. Created At and Updated At are separate stored columns and hold the same value on every row of the committed test case, where no conversation had been updated after it was created."
        ),
        "paths": ("*/com.scaleup.chatai/databases/chat-ai.db",),
        "output_types": "all",
        "artifact_icon": "message-square",
    },
    "nova_chatbot_history_detail": {
        "name": "HistoryDetail",
        "description": "Extracts individual messages from Nova AI Chatbot",
        "author": "Guilherme Guilherme",
        "creation_date": "2026-05-29",
        "last_update_date": "2026-09-19",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": (
            "The AI Model and Assistant Persona names are mapped from the numeric codes as observed in the app by the author; the mapping is not vendor-documented, so the stored code is shown beside every name and an unmapped code is reported as stored. Role reads type 0 as USER and 1 as ASSISTANT on the same basis. Stored epochs are read as milliseconds above 1e11 and as seconds below it, and reported in UTC; every timestamp in the tested extraction was a 13-digit millisecond value. An extraction can carry one chat-ai.db per Android user and every copy is read, so the located at line lists each database and the row identifiers are per database. Developed against the author's own installation; no registered corpus image carries this app. The committed test case is the author's own extraction of the app's private data directory. Has Link reads No on every row of the committed test case because that store's HistoryDetailLink table holds no rows."
        ),
        "paths": ("*/com.scaleup.chatai/databases/chat-ai.db",),
        "output_types": "all",
        "artifact_icon": "message-circle",
    },
    "nova_chatbot_documents": {
        "name": "HistoryDetailDocuments",
        "description": "Extracts document records from Nova AI Chatbot (Firebase URLs)",
        "author": "Guilherme Guilherme",
        "creation_date": "2026-05-29",
        "last_update_date": "2026-09-19",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": (
            "The AI Model and Assistant Persona names are mapped from the numeric codes as observed in the app by the author; the mapping is not vendor-documented, so the stored code is shown beside every name and an unmapped code is reported as stored. Role reads type 0 as USER and 1 as ASSISTANT on the same basis. Stored epochs are read as milliseconds above 1e11 and as seconds below it, and reported in UTC; every timestamp in the tested extraction was a 13-digit millisecond value. An extraction can carry one chat-ai.db per Android user and every copy is read, so the located at line lists each database and the row identifiers are per database. Developed against the author's own installation; no registered corpus image carries this app. The committed test case is the author's own extraction of the app's private data directory. The Size (as stored) column is the integer the store keeps under that name, reported without a unit: its unit is not established, and all three records in the tested extraction hold 3, one of them a video."
        ),
        "paths": ("*/com.scaleup.chatai/databases/chat-ai.db",),
        "output_types": "all",
        "artifact_icon": "file-text",
    },
    "nova_chatbot_images": {
        "name": "HistoryDetailImages",
        "description": "Extracts image records from Nova AI Chatbot (Firebase URLs)",
        "author": "Guilherme Guilherme",
        "creation_date": "2026-05-29",
        "last_update_date": "2026-09-19",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": (
            "The AI Model and Assistant Persona names are mapped from the numeric codes as observed in the app by the author; the mapping is not vendor-documented, so the stored code is shown beside every name and an unmapped code is reported as stored. Role reads type 0 as USER and 1 as ASSISTANT on the same basis. Stored epochs are read as milliseconds above 1e11 and as seconds below it, and reported in UTC; every timestamp in the tested extraction was a 13-digit millisecond value. An extraction can carry one chat-ai.db per Android user and every copy is read, so the located at line lists each database and the row identifiers are per database. Developed against the author's own installation; no registered corpus image carries this app. The committed test case is the author's own extraction of the app's private data directory."
        ),
        "paths": ("*/com.scaleup.chatai/databases/chat-ai.db",),
        "output_types": "all",
        "artifact_icon": "image",
    },
    "nova_chatbot_links": {
        "name": "HistoryDetailLinks",
        "description": "Extracts link records from Nova AI Chatbot",
        "author": "Guilherme Guilherme",
        "creation_date": "2026-05-29",
        "last_update_date": "2026-09-19",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": (
            "The AI Model and Assistant Persona names are mapped from the numeric codes as observed in the app by the author; the mapping is not vendor-documented, so the stored code is shown beside every name and an unmapped code is reported as stored. Role reads type 0 as USER and 1 as ASSISTANT on the same basis. Stored epochs are read as milliseconds above 1e11 and as seconds below it, and reported in UTC; every timestamp in the tested extraction was a 13-digit millisecond value. An extraction can carry one chat-ai.db per Android user and every copy is read, so the located at line lists each database and the row identifiers are per database. Developed against the author's own installation; no registered corpus image carries this app. The committed test case is the author's own extraction of the app's private data directory. The HistoryDetailLink table held no rows in the committed test case, so this artifact is code present and unexercised by it."
        ),
        "paths": ("*/com.scaleup.chatai/databases/chat-ai.db",),
        "output_types": "all",
        "artifact_icon": "link",
    },
}

import datetime

import os

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    get_sqlite_db_records,
    logfunc,
    open_sqlite_db_readonly,
)

# Model mappings
MODEL_MAP = {
    0: "ChatGPT 3.5",
    1: "GPT-5",
    2: "GPT-4o",
    3: "Bard/Image Gen",
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

IMAGE_STATE_MAP = {0: "Pending", 1: "Success", 2: "Failed"}


def _nova_databases(context):
    """Every chat-ai.db the extraction carries, duplicate storage views removed.

    An Android extraction repeats an app's private directory under data/data,
    data/user/0 and data_mirror, and can carry a second Android user's own copy
    under data/user/<n>. unique_files collapses the first kind and keeps the
    second, so a second user's chats are read rather than skipped. Matching the
    basename exactly also keeps a -wal, -shm or -journal sidecar out of the list.
    """
    return sorted(
        str(f) for f in unique_files(context)
        if os.path.basename(str(f)) == "chat-ai.db"
    )


def _epoch_to_utc(value):
    """Convert a stored epoch to an aware UTC datetime.

    chat-ai.db stores epochs in milliseconds; the two magnitudes do not
    overlap for any plausible date (milliseconds are ~1e12, seconds ~1e9),
    so a value below 1e11 is read as seconds. Returns '' for empty or
    unparseable values.
    """
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



def get_model(model_id):
    if model_id is None:
        return "Unknown"
    name = MODEL_MAP.get(model_id)
    return f"{name} ({model_id})" if name else f"Unknown Model ({model_id})"


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


def _as_stored(value):
    """Nothing recorded reads as blank; a recorded 0 is a value and must not.

    syncState, syncRetryCount, token and styleId are integers the store writes as
    0, so `value or ""` would render a real 0 as an empty cell, which an examiner
    reads as "not recorded".
    """
    return "" if value is None else value


def get_role(role_int):
    if role_int == 0:
        return "USER"
    if role_int == 1:
        return "ASSISTANT"
    return f"UNKNOWN ({role_int})"


@artifact_processor
def nova_chatbot_history(context):
    headers = (
        "Conv ID",
        "UUID",
        "Title",
        "AI Model",
        "Assistant",
        "Caption History ID",
        "Starred",
        "Soft Deleted",
        "Sync State",
        "Sync Retry Count",
        ("Created At", "datetime"),
        ("Updated At", "datetime"),
        ("Last Modified At", "datetime"),
        "Message Count",
        ("Last Message At", "datetime"),
        "First User Message",
    )

    db_paths = _nova_databases(context)
    if not db_paths:
        return headers, [], ""

    query = """
        SELECT h.id, h.UUID, h.title, h.chatBotModel, h.assistantId,
               h.captionHistoryId, h.starred, h.softDeleted, h.syncState,
               h.syncRetryCount, h.createdAt, h.updatedAt, h.lastModifiedAt,
               COUNT(hd.id), MAX(hd.createdAt),
               MIN(CASE WHEN hd.type = 0 THEN hd.text END)
        FROM History h
        LEFT JOIN HistoryDetail hd ON hd.historyID = h.id
        GROUP BY h.id
        ORDER BY h.createdAt ASC
    """

    data_list = []
    sources = []
    for db_path in db_paths:
        for row in get_sqlite_db_records(db_path, query):
            data_list.append(
                (
                    row[0],  # id
                    row[1] or "",  # UUID
                    row[2] or "",  # title
                    get_model(row[3]),  # chatBotModel
                    get_assistant(row[4]),  # assistantId
                    row[5] or "",  # captionHistoryId
                    "Yes" if row[6] else "No",  # starred
                    "Yes" if row[7] else "No",  # softDeleted
                    _as_stored(row[8]),  # syncState
                    _as_stored(row[9]),  # syncRetryCount
                    _epoch_to_utc(row[10]),  # createdAt
                    _epoch_to_utc(row[11]),  # updatedAt
                    _epoch_to_utc(row[12]),  # lastModifiedAt
                    row[13] or 0,  # message count
                    _epoch_to_utc(row[14]),  # last message at
                    row[15] or "",  # first user message
                )
            )

        sources.append(db_path)

    return headers, data_list, "\n".join(sources)


@artifact_processor
def nova_chatbot_history_detail(context):
    headers = (
        "Msg ID",
        "Msg UUID",
        "Conv ID",
        "Conv UUID",
        "Conv Title",
        "AI Model",
        "Assistant Persona",
        "Conv Deleted",
        "Role",
        "Message Text",
        "Token Count",
        "Reasoning Content",
        ("Message Timestamp", "datetime"),
        ("Last Modified At", "datetime"),
        "Sync State",
        "Sync Retry Count",
        "Has Image",
        "Has Document",
        "Has Link",
    )

    db_paths = _nova_databases(context)
    if not db_paths:
        return headers, [], ""

    query = """
        SELECT hd.id, hd.UUID, hd.historyID, h.UUID, h.title, h.chatBotModel,
               h.assistantId, h.softDeleted, hd.type, hd.text, hd.token,
               hd.reasoningContent, hd.createdAt, hd.lastModifiedAt,
               hd.syncState, hd.syncRetryCount,
               EXISTS(SELECT 1 FROM HistoryDetailImage WHERE historyDetailID = hd.id),
               EXISTS(SELECT 1 FROM HistoryDetailDocument WHERE historyDetailID = hd.id),
               EXISTS(SELECT 1 FROM HistoryDetailLink WHERE historyDetailID = hd.id)
        FROM HistoryDetail hd
        INNER JOIN History h ON h.id = hd.historyID
        ORDER BY hd.historyID ASC, hd.createdAt ASC
    """

    data_list = []
    sources = []
    for db_path in db_paths:
        for row in get_sqlite_db_records(db_path, query):
            data_list.append(
                (
                    row[0],  # id
                    row[1] or "",  # UUID
                    row[2],  # historyID
                    row[3] or "",  # conversation UUID
                    row[4] or "",  # conversation title
                    get_model(row[5]),  # chatBotModel
                    get_assistant(row[6]),  # assistantId
                    "Yes" if row[7] else "No",  # softDeleted
                    get_role(row[8]),  # type
                    row[9] or "",  # text
                    _as_stored(row[10]),  # token
                    row[11] or "",  # reasoningContent
                    _epoch_to_utc(row[12]),  # createdAt
                    _epoch_to_utc(row[13]),  # lastModifiedAt
                    _as_stored(row[14]),  # syncState
                    _as_stored(row[15]),  # syncRetryCount
                    "Yes" if row[16] else "No",  # has image
                    "Yes" if row[17] else "No",  # has document
                    "Yes" if row[18] else "No",  # has link
                )
            )

        sources.append(db_path)

    return headers, data_list, "\n".join(sources)


@artifact_processor
def nova_chatbot_documents(context):
    headers = (
        "Doc ID",
        "Msg ID",
        "Conv ID",
        "Conv UUID",
        "Conv Title",
        "AI Model",
        "Assistant Persona",
        "Conv Deleted",
        "Submitted By",
        "Msg Text",
        ("Msg Timestamp", "datetime"),
        "File Name",
        "MIME Type",
        "Size (as stored)",
        "Source Type",
        "Cloud Storage URL",  # plain text; a URL column must never render as a live link
    )

    db_paths = _nova_databases(context)
    if not db_paths:
        return headers, [], ""

    query = """
        SELECT d.id, d.historyDetailID, d.url, d.name, d.type, d.size, d.mimeType,
               hd.historyID, hd.type, hd.text, hd.createdAt, h.UUID, h.title,
               h.chatBotModel, h.assistantId, h.softDeleted
        FROM HistoryDetailDocument d
        INNER JOIN HistoryDetail hd ON hd.id = d.historyDetailID
        INNER JOIN History h ON h.id = hd.historyID
        ORDER BY d.id ASC
    """

    data_list = []
    sources = []
    for db_path in db_paths:
        for row in get_sqlite_db_records(db_path, query):
            doc_type = (
                "Local File"
                if row[4] == 0
                else "Remote File"
                if row[4] == 1
                else f"Unknown ({row[4]})"
            )

            data_list.append(
                (
                    row[0],  # id
                    row[1],  # historyDetailID
                    row[7],  # historyID
                    row[11] or "",  # conversation UUID
                    row[12] or "",  # conversation title
                    get_model(row[13]),  # chatBotModel
                    get_assistant(row[14]),  # assistantId
                    "Yes" if row[15] else "No",  # softDeleted
                    get_role(row[8]),  # submitted by
                    row[9] or "",  # message text
                    _epoch_to_utc(row[10]),  # createdAt
                    row[3] or "Unknown",  # file name
                    row[6] or "",  # mimeType
                    _as_stored(row[5]),  # size, as stored
                    doc_type,  # source type
                    row[2] or "",  # Firebase URL string output safely as text
                )
            )

        sources.append(db_path)

    return headers, data_list, "\n".join(sources)


@artifact_processor
def nova_chatbot_images(context):
    headers = (
        "Image ID",
        "Msg ID",
        "Conv ID",
        "Conv UUID",
        "Conv Title",
        "AI Model",
        "Assistant Persona",
        "Conv Deleted",
        "Submitted By",
        "Msg Text",
        ("Msg Timestamp", "datetime"),
        "Prompt",
        "State",
        "Pipeline",
        "Style ID",
        "MIME Type",
        "Cloud Storage URL",  # plain text; a URL column must never render as a live link
    )

    db_paths = _nova_databases(context)
    if not db_paths:
        return headers, [], ""

    query = """
        SELECT i.id, i.historyDetailID, i.url, i.prompt, i.state, i.mimeType,
               i.styleId, i.pipeline, hd.historyID, hd.type, hd.text,
               hd.createdAt, h.UUID, h.title, h.chatBotModel,
               h.assistantId, h.softDeleted
        FROM HistoryDetailImage i
        INNER JOIN HistoryDetail hd ON hd.id = i.historyDetailID
        INNER JOIN History h ON h.id = hd.historyID
        ORDER BY i.id ASC
    """

    data_list = []
    sources = []
    for db_path in db_paths:
        for row in get_sqlite_db_records(db_path, query):
            state = (
                IMAGE_STATE_MAP.get(row[4], f"Unknown ({row[4]})")
                if row[4] is not None
                else ""
            )

            data_list.append(
                (
                    row[0],  # id
                    row[1],  # historyDetailID
                    row[8],  # historyID
                    row[12] or "",  # conversation UUID
                    row[13] or "",  # conversation title
                    get_model(row[14]),  # chatBotModel
                    get_assistant(row[15]),  # assistantId
                    "Yes" if row[16] else "No",  # softDeleted
                    get_role(row[9]),  # submitted by
                    row[10] or "",  # message text
                    _epoch_to_utc(row[11]),  # createdAt
                    row[3] or "",  # prompt
                    state,  # state
                    row[7] or "",  # pipeline
                    _as_stored(row[6]),  # styleId
                    row[5] or "",  # mimeType
                    row[2] or "",  # Firebase URL string output safely as text
                )
            )

        sources.append(db_path)

    return headers, data_list, "\n".join(sources)


@artifact_processor
def nova_chatbot_links(context):
    headers = (
        "Link ID",
        "Msg ID",
        "Conv ID",
        "Conv UUID",
        "Conv Title",
        "AI Model",
        "Assistant Persona",
        "Conv Deleted",
        "Msg Role",
        "Msg Text",
        ("Msg Timestamp", "datetime"),
        "URL",  # Kept as text to natively display remote paths safely
    )

    db_paths = _nova_databases(context)
    if not db_paths:
        return headers, [], ""

    query = """
        SELECT l.id, l.historyDetailID, l.url, hd.historyID, hd.type, hd.text,
               hd.createdAt, h.UUID, h.title, h.chatBotModel, h.assistantId, h.softDeleted
        FROM HistoryDetailLink l
        INNER JOIN HistoryDetail hd ON hd.id = l.historyDetailID
        INNER JOIN History h ON h.id = hd.historyID
        ORDER BY l.id ASC
    """

    data_list = []
    sources = []
    for db_path in db_paths:
        with open_sqlite_db_readonly(db_path) as db:
            cursor = db.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
                " AND name='HistoryDetailLink'"
            )
            if not cursor.fetchone():
                logfunc(f"Nova links - no HistoryDetailLink table in {db_path}")
                continue

        for row in get_sqlite_db_records(db_path, query):
            data_list.append(
                (
                    row[0],  # id
                    row[1],  # historyDetailID
                    row[3],  # historyID
                    row[7] or "",  # conversation UUID
                    row[8] or "",  # conversation title
                    get_model(row[9]),  # chatBotModel
                    get_assistant(row[10]),  # assistantId
                    "Yes" if row[11] else "No",  # softDeleted
                    get_role(row[4]),  # msg role
                    row[5] or "",  # message text
                    _epoch_to_utc(row[6]),  # createdAt
                    row[2] or "",  # URL string output safely as text
                )
            )

        sources.append(db_path)

    return headers, data_list, "\n".join(sources)
