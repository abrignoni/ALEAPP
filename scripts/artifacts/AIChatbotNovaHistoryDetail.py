__artifacts_v2__ = {
    "nova_chatbot_history_detail": {
        "name": "HistoryDetail",
        "description": (
            "Extracts every individual message from the AI Chatbot - Nova app "
            "(com.scaleup.chatai) from the HistoryDetail table, enriched with parent "
            "conversation context and attachment existence flags."
        ),
        "author": "Guilherme Guilherme",
        "version": "1.0",
        "date": "2026-05-21",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": "Database: com.scaleup.chatai/databases/chat-ai.db",
        "paths": ("*/com.scaleup.chatai/databases/chat-ai.db",),
        "function": "get_nova_chatbot_history_detail",
        "output_types": "standard",
        "artifact_icon": "message-circle",
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
    hd.id,
    hd.UUID,
    hd.historyID,
    h.UUID,
    h.title,
    h.chatBotModel,
    h.softDeleted,
    hd.type,
    hd.text,
    hd.token,
    hd.reasoningContent,
    hd.createdAt,
    hd.lastModifiedAt,
    hd.syncState,
    hd.syncRetryCount,
    EXISTS(SELECT 1 FROM HistoryDetailImage i WHERE i.historyDetailID = hd.id),
    EXISTS(SELECT 1 FROM HistoryDetailDocument d WHERE d.historyDetailID = hd.id),
    EXISTS(SELECT 1 FROM HistoryDetailLink l WHERE l.historyDetailID = hd.id)
FROM HistoryDetail hd
INNER JOIN History h ON h.id = hd.historyID
ORDER BY hd.historyID ASC, hd.createdAt ASC
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


def get_nova_chatbot_history_detail(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for HistoryDetail")

    # Filter out secondary transactional database engines
    files_found = [
        x for x in files_found if not x.endswith(("-journal", "-wal", "-shm"))
    ]
    file_found = next((str(x) for x in files_found if "chat-ai.db" in str(x)), None)

    if not file_found:
        logfunc("[nova_chatbot_history_detail] Nova database file not found.")
        return

    try:
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute(QUERY)
        rows_raw = cursor.fetchall()
        db.close()
    except Exception as e:
        logfunc(f"[nova_chatbot_history_detail] Error reading {file_found}: {e}")
        return

    if not rows_raw:
        logfunc(f"[nova_chatbot_history_detail] No records found in {file_found}.")
        return

    headers = (
        "Msg. ID",
        "Msg. UUID",
        "Conv. ID",
        "Conv. UUID",
        "Conv. Title",
        "AI Model",
        "Conv. Deleted",
        "Role",
        "Message Text",
        "Token Count",
        "Reasoning Content",
        "Message Timestamp (UTC)",
        "Last Modified At (UTC)",
        "Sync State",
        "Sync Retry Count",
        "Has Image",
        "Has Document",
        "Has Link",
    )

    rows = []
    for row in rows_raw:
        model_int = row[5]
        model_name = "Unknown"
        if model_int is not None:
            name_lookup = CHAT_BOT_MODEL_MAP.get(model_int)
            model_name = (
                f"{name_lookup} ({model_int})"
                if name_lookup
                else f"Unknown Model ({model_int})"
            )

        role_int = row[7]
        role_label = (
            "USER"
            if role_int == 0
            else "ASSISTANT"
            if role_int == 1
            else f"UNKNOWN ({role_int})"
        )

        rows.append(
            (
                row[0],
                row[1] or "",
                row[2],
                row[3] or "",
                row[4] or "",
                model_name,
                "DELETED" if row[6] == 1 else "No",
                role_label,
                row[8] or "",
                row[9] if row[9] is not None else "",
                row[10] or "",
                _convert_ms_timestamp(row[11]),
                _convert_ms_timestamp(row[12]),
                row[13] if row[13] is not None else "",
                row[14] if row[14] is not None else "",
                "Yes" if row[15] else "No",
                "Yes" if row[16] else "No",
                "Yes" if row[17] else "No",
            )
        )

    report_name = "HistoryDetail"
    report = ArtifactHtmlReport(report_name)
    report.start_artifact_report(report_folder, report_name)
    report.add_script()

    # Delegates script-side sanitization directly to framework tables safely
    report.write_artifact_data_table(headers, rows, file_found, html_escape=True)
    report.end_artifact_report()

    tsv(report_folder, headers, rows, report_name, file_found)
    timeline(report_folder, report_name, rows, headers)
    logfunc(
        f"[nova_chatbot_history_detail] Processed {len(rows)} message detail records."
    )
