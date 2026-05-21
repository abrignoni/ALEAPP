__artifacts_v2__ = {
    "nova_chatbot_documents": {
        "name": "HistoryDetailDocuments",
        "description": (
            "Extracts document records submitted by the user to the AI from the "
            "HistoryDetailDocument table, enriched with parent message and conversation context."
        ),
        "author": "Guilherme Guilherme",
        "version": "1.0",
        "date": "2026-05-21",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": "Database: com.scaleup.chatai/databases/chat-ai.db",
        "paths": ("*/com.scaleup.chatai/databases/chat-ai.db",),
        "function": "get_nova_chatbot_documents",
        "output_types": "standard",
        "artifact_icon": "file-text",
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
    d.id,
    d.historyDetailID,
    d.url,
    d.name,
    d.type,
    d.size,
    d.mimeType,
    hd.historyID,
    hd.type,
    hd.text,
    hd.createdAt,
    h.UUID,
    h.title,
    h.chatBotModel,
    h.softDeleted
FROM HistoryDetailDocument d
INNER JOIN HistoryDetail hd ON hd.id = d.historyDetailID
INNER JOIN History h ON h.id = hd.historyID
ORDER BY d.id ASC
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


def _format_file_size(size_bytes):
    if size_bytes is None:
        return ""
    try:
        size_bytes = int(size_bytes)
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024**2):.1f} MB"
    except (ValueError, TypeError):
        return str(size_bytes)


def get_nova_chatbot_documents(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for HistoryDetail Submitted Documents")

    # Filter out secondary transactional database engines
    files_found = [
        x for x in files_found if not x.endswith(("-journal", "-wal", "-shm"))
    ]
    file_found = next((str(x) for x in files_found if "chat-ai.db" in str(x)), None)

    if not file_found:
        logfunc("[nova_chatbot_documents] Nova database file not found.")
        return

    try:
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute(QUERY)
        rows_raw = cursor.fetchall()
        db.close()
    except Exception as e:
        logfunc(f"[nova_chatbot_documents] Error reading {file_found}: {e}")
        return

    if not rows_raw:
        logfunc(f"[nova_chatbot_documents] No document records found in {file_found}.")
        return

    headers = (
        "Doc. ID",
        "Msg. ID",
        "Conv. ID",
        "Conv. UUID",
        "Conv. Title",
        "AI Model",
        "Conv. Deleted",
        "Media Submitted By",
        "Msg. Text",
        "Msg. Timestamp (UTC)",
        "File Name",
        "MIME Type",
        "Size",
        "Source Type",
        "Firebase Storage Path",
        "Forensic Notes",
    )

    rows = []
    for row in rows_raw:
        model_int = row[13]
        model_name = "Unknown"
        if model_int is not None:
            name_lookup = CHAT_BOT_MODEL_MAP.get(model_int)
            model_name = (
                f"{name_lookup} ({model_int})"
                if name_lookup
                else f"Unknown Model ({model_int})"
            )

        doc_type_int = row[4]
        doc_type_label = (
            "Local File"
            if doc_type_int == 0
            else "Remote File"
            if doc_type_int == 1
            else f"Unknown ({doc_type_int})"
        )
        
        raw_role = row[8]
        if raw_role == 0:
            submitted_by = "USER"
            forensic_note = "Media element actively selected and submitted by the user to the chatbot interface."
        elif raw_role == 1:
            submitted_by = "AI ASSISTANT"
            forensic_note = "Media element generated or provided back by the AI response."
        else:
            submitted_by = f"UNKNOWN ({raw_role})"
            forensic_note = "Unknown structural context for media origin."

        rows.append(
            (
                row[0],
                row[1],
                row[7],
                row[11] or "",
                row[12] or "",
                model_name,
                "DELETED" if row[14] == 1 else "No",
                submitted_by,
                row[9] or "",
                _convert_ms_timestamp(row[10]),
                row[3] or "Unknown",
                row[6] or "",
                _format_file_size(row[5]),
                doc_type_label,
                row[2] or "",
                forensic_note,
            )
        )

    report_name = "HistoryDetailDocuments"
    report = ArtifactHtmlReport(report_name)
    report.start_artifact_report(report_folder, report_name)
    report.add_script()

    # Enforce safe framework-side text escaping to block script injection vectors entirely
    report.write_artifact_data_table(headers, rows, file_found, html_escape=True)
    report.end_artifact_report()

    tsv(report_folder, headers, rows, report_name, file_found)
    timeline(report_folder, report_name, rows, headers)
    logfunc(
        f"[nova_chatbot_documents] Processed {len(rows)} submitted document records."
    )