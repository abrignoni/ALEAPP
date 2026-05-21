__artifacts_v2__ = {
    "nova_chatbot_history": {
        "name": "Conversation History",
        "description": (
            "Extracts the conversation index from the AI Chatbot - Nova app "
            "(com.scaleup.chatai) from the History table."
        ),
        "author": "Guilherme Guilherme",
        "version": "1.0",
        "date": "2026-05-21",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": "Database: com.scaleup.chatai/databases/chat-ai.db",
        "paths": ("*/com.scaleup.chatai/databases/chat-ai.db",),
        "function": "get_nova_chatbot_history",
        "output_types": "standard",
        "artifact_icon": "message-square",
    }
}

import datetime
from datetime import timezone
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly

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
    h.id,
    h.UUID,
    h.title,
    h.chatBotModel,
    h.assistantId,
    h.captionHistoryId,
    h.starred,
    h.softDeleted,
    h.syncState,
    h.syncRetryCount,
    h.createdAt,
    h.updatedAt,
    h.lastModifiedAt,
    COUNT(hd.id),
    MAX(hd.createdAt),
    MIN(CASE WHEN hd.type = 0 THEN hd.text END)
FROM History h
LEFT JOIN HistoryDetail hd ON hd.historyID = h.id
GROUP BY h.id
ORDER BY h.createdAt ASC
"""


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


def get_nova_chatbot_history(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Conversation History")

    # Clean the file list of any SQLite journal artifacts
    files_found = [
        x for x in files_found if not x.endswith(("-journal", "-wal", "-shm"))
    ]
    file_found = next((str(x) for x in files_found if "chat-ai.db" in str(x)), None)

    if not file_found:
        logfunc("[nova_chatbot_history] Nova database file not found.")
        return

    try:
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute(QUERY)
        rows_raw = cursor.fetchall()
        db.close()
    except Exception as e:
        logfunc(f"[nova_chatbot_history] Error reading {file_found}: {e}")
        return

    if not rows_raw:
        logfunc(f"[nova_chatbot_history] No records found in {file_found}.")
        return

    headers = (
        "Conv. ID",
        "Conv. UUID",
        "Title",
        "AI Model",
        "Assistant ID",
        "Caption History ID",
        "Starred",
        "Soft Deleted",
        "Sync State",
        "Sync Retry Count",
        "Created At (UTC)",
        "Updated At (UTC)",
        "Last Modified At (UTC)",
        "Message Count",
        "Last Message At (UTC)",
        "First User Message",
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

        rows.append(
            (
                row[0],
                row[1] or "",
                row[2] or "",
                model_name,
                row[4] if row[4] is not None else "",
                row[5] or "",
                "Yes" if row[6] else "No",
                "DELETED" if row[7] == 1 else "No",
                row[8] if row[8] is not None else "",
                row[9] if row[9] is not None else "",
                _convert_ms_timestamp(row[10]),
                _convert_ms_timestamp(row[11]),
                _convert_ms_timestamp(row[12]),
                row[13] if row[13] is not None else 0,
                _convert_ms_timestamp(row[14]),
                row[15] or "",
            )
        )

    report_name = "History"
    report = ArtifactHtmlReport(report_name)
    report.start_artifact_report(report_folder, report_name)
    report.add_script()

    # html_escape=True hands escaping entirely to the framework backend safely
    report.write_artifact_data_table(headers, rows, file_found, html_escape=True)
    report.end_artifact_report()

    tsv(report_folder, headers, rows, report_name, file_found)
    timeline(report_folder, report_name, rows, headers)
    logfunc(
        f"[nova_chatbot_history] Processed {len(rows)} conversation history records."
    )
