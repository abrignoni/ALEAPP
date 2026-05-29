__artifacts_v2__ = {
    "nova_chatbot_history": {
        "name": "History",
        "description": "Extracts conversation index from Nova AI Chatbot",
        "author": "Guilherme Guilherme",
        "version": "6.1",
        "date": "2026-05-29",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "paths": ("*/com.scaleup.chatai/databases/chat-ai.db",),
        "function": "get_nova_chatbot_history",
        "output_types": "all",
        "artifact_icon": "message-square",
    },
    "nova_chatbot_history_detail": {
        "name": "History Detail",
        "description": "Extracts individual messages from Nova AI Chatbot",
        "author": "Guilherme Guilherme",
        "version": "6.1",
        "date": "2026-05-29",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "paths": ("*/com.scaleup.chatai/databases/chat-ai.db",),
        "function": "get_nova_chatbot_history_detail",
        "output_types": "all",
        "artifact_icon": "message-circle",
    },
    "nova_chatbot_documents": {
        "name": "History Detail Documents",
        "description": "Extracts document records from Nova AI Chatbot (Firebase URLs)",
        "author": "Guilherme Guilherme",
        "version": "6.1",
        "date": "2026-05-29",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "paths": ("*/com.scaleup.chatai/databases/chat-ai.db",),
        "function": "get_nova_chatbot_documents",
        "output_types": "all",
        "artifact_icon": "file-text",
    },
    "nova_chatbot_images": {
        "name": "History Detail Images",
        "description": "Extracts image records from Nova AI Chatbot (Firebase URLs)",
        "author": "Guilherme Guilherme",
        "version": "6.1",
        "date": "2026-05-29",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "paths": ("*/com.scaleup.chatai/databases/chat-ai.db",),
        "function": "get_nova_chatbot_images",
        "output_types": "all",
        "artifact_icon": "image",
    },
    "nova_chatbot_links": {
        "name": "History Detail Links",
        "description": "Extracts link records from Nova AI Chatbot",
        "author": "Guilherme Guilherme",
        "version": "6.1",
        "date": "2026-05-29",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "paths": ("*/com.scaleup.chatai/databases/chat-ai.db",),
        "function": "get_nova_chatbot_links",
        "output_types": "all",
        "artifact_icon": "link",
    },
}

from scripts.ilapfuncs import (
    artifact_processor,
    get_file_path,
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


def format_size(bytes_val):
    if not bytes_val:
        return ""
    try:
        b = int(bytes_val)
        if b < 1024:
            return f"{b} B"
        if b < 1048576:
            return f"{b / 1024:.1f} KB"
        return f"{b / 1048576:.1f} MB"
    except (ValueError, TypeError):
        return str(bytes_val)


def get_role(role_int):
    if role_int == 0:
        return "USER"
    if role_int == 1:
        return "ASSISTANT"
    return f"UNKNOWN ({role_int})"


@artifact_processor
def get_nova_chatbot_history(files_found, report_folder, seeker, wrap_text):
    db_path = get_file_path(files_found, "chat-ai.db")
    if not db_path:
        return (), [], ""

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
                row[8] or "",  # syncState
                row[9] or 0,  # syncRetryCount
                row[10],  # createdAt (Raw Epoch)
                row[11],  # updatedAt (Raw Epoch)
                row[12],  # lastModifiedAt (Raw Epoch)
                row[13] or 0,  # message count
                row[14],  # last message at (Raw Epoch)
                row[15] or "",  # first user message
            )
        )

    headers = (
        ("Conv ID", "text"),
        ("UUID", "text"),
        ("Title", "text"),
        ("AI Model", "text"),
        ("Assistant", "text"),
        ("Caption History ID", "text"),
        ("Starred", "text"),
        ("Soft Deleted", "text"),
        ("Sync State", "text"),
        ("Sync Retry Count", "text"),
        ("Created At", "date time"),
        ("Updated At", "date time"),
        ("Last Modified At", "date time"),
        ("Message Count", "text"),
        ("Last Message At", "date time"),
        ("First User Message", "text"),
    )

    return headers, data_list, db_path


@artifact_processor
def get_nova_chatbot_history_detail(files_found, report_folder, seeker, wrap_text):
    db_path = get_file_path(files_found, "chat-ai.db")
    if not db_path:
        return (), [], ""

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
                row[10] or "",  # token
                row[11] or "",  # reasoningContent
                row[12],  # createdAt (Raw Epoch)
                row[13],  # lastModifiedAt (Raw Epoch)
                row[14] or "",  # syncState
                row[15] or 0,  # syncRetryCount
                "Yes" if row[16] else "No",  # has image
                "Yes" if row[17] else "No",  # has document
                "Yes" if row[18] else "No",  # has link
            )
        )

    headers = (
        ("Msg ID", "text"),
        ("Msg UUID", "text"),
        ("Conv ID", "text"),
        ("Conv UUID", "text"),
        ("Conv Title", "text"),
        ("AI Model", "text"),
        ("Assistant Persona", "text"),
        ("Conv Deleted", "text"),
        ("Role", "text"),
        ("Message Text", "text"),
        ("Token Count", "text"),
        ("Reasoning Content", "text"),
        ("Message Timestamp", "date time"),
        ("Last Modified At", "date time"),
        ("Sync State", "text"),
        ("Sync Retry Count", "text"),
        ("Has Image", "text"),
        ("Has Document", "text"),
        ("Has Link", "text"),
    )

    return headers, data_list, db_path


@artifact_processor
def get_nova_chatbot_documents(files_found, report_folder, seeker, wrap_text):
    db_path = get_file_path(files_found, "chat-ai.db")
    if not db_path:
        return (), [], ""

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
                row[10],  # createdAt (Raw Epoch)
                row[3] or "Unknown",  # file name
                row[6] or "",  # mimeType
                format_size(row[5]),  # size
                doc_type,  # source type
                row[2] or "",  # Firebase URL string output safely as text
            )
        )

    headers = (
        ("Doc ID", "text"),
        ("Msg ID", "text"),
        ("Conv ID", "text"),
        ("Conv UUID", "text"),
        ("Conv Title", "text"),
        ("AI Model", "text"),
        ("Assistant Persona", "text"),
        ("Conv Deleted", "text"),
        ("Submitted By", "text"),
        ("Msg Text", "text"),
        ("Msg Timestamp", "date time"),
        ("File Name", "text"),
        ("MIME Type", "text"),
        ("Size", "text"),
        ("Source Type", "text"),
        (
            "Cloud Storage URL",
            "text",
        ),  # Kept as text to natively display remote paths safely
    )

    return headers, data_list, db_path


@artifact_processor
def get_nova_chatbot_images(files_found, report_folder, seeker, wrap_text):
    db_path = get_file_path(files_found, "chat-ai.db")
    if not db_path:
        return (), [], ""

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
                row[11],  # createdAt (Raw Epoch)
                row[3] or "",  # prompt
                state,  # state
                row[7] or "",  # pipeline
                row[6] or "",  # styleId
                row[5] or "",  # mimeType
                row[2] or "",  # Firebase URL string output safely as text
            )
        )

    headers = (
        ("Image ID", "text"),
        ("Msg ID", "text"),
        ("Conv ID", "text"),
        ("Conv UUID", "text"),
        ("Conv Title", "text"),
        ("AI Model", "text"),
        ("Assistant Persona", "text"),
        ("Conv Deleted", "text"),
        ("Submitted By", "text"),
        ("Msg Text", "text"),
        ("Msg Timestamp", "date time"),
        ("Prompt", "text"),
        ("State", "text"),
        ("Pipeline", "text"),
        ("Style ID", "text"),
        ("MIME Type", "text"),
        (
            "Cloud Storage URL",
            "text",
        ),  # Kept as text to natively display remote paths safely
    )

    return headers, data_list, db_path


@artifact_processor
def get_nova_chatbot_links(files_found, report_folder, seeker, wrap_text):
    db_path = get_file_path(files_found, "chat-ai.db")
    if not db_path:
        return (), [], ""

    with open_sqlite_db_readonly(db_path) as db:
        cursor = db.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='HistoryDetailLink'"
        )
        if not cursor.fetchone():
            logfunc("HistoryDetailLink table not found in Nova database")
            return (), [], ""

    query = """
        SELECT l.id, l.historyDetailID, l.url, hd.historyID, hd.type, hd.text,
               hd.createdAt, h.UUID, h.title, h.chatBotModel, h.assistantId, h.softDeleted
        FROM HistoryDetailLink l
        INNER JOIN HistoryDetail hd ON hd.id = l.historyDetailID
        INNER JOIN History h ON h.id = hd.historyID
        ORDER BY l.id ASC
    """

    data_list = []
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
                row[6],  # createdAt (Raw Epoch)
                row[2] or "",  # URL string output safely as text
            )
        )

    headers = (
        ("Link ID", "text"),
        ("Msg ID", "text"),
        ("Conv ID", "text"),
        ("Conv UUID", "text"),
        ("Conv Title", "text"),
        ("AI Model", "text"),
        ("Assistant Persona", "text"),
        ("Conv Deleted", "text"),
        ("Msg Role", "text"),
        ("Msg Text", "text"),
        ("Msg Timestamp", "date time"),
        ("URL", "text"),  # Kept as text to natively display remote paths safely
    )

    return headers, data_list, db_path
