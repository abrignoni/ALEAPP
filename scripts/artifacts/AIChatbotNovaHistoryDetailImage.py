__artifacts_v2__ = {
    "nova_chatbot_images": {
        "name": "HistoryDetailImages",
        "description": (
            "Extracts user-submitted image links and AI-generated image records from the "
            "HistoryDetailImage table, enriched with parent message and conversation context."
        ),
        "author": "Guilherme Guilherme",
        "version": "1.0",
        "date": "2026-05-21",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": "Database: com.scaleup.chatai/databases/chat-ai.db",
        "paths": ("*/com.scaleup.chatai/databases/chat-ai.db",),
        "function": "get_nova_chatbot_images",
        "output_types": "standard",
        "artifact_icon": "image",
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

IMAGE_STATE_MAP = {
    0: "Pending",
    1: "Success",
    2: "Failed",
}

QUERY = """
SELECT
    i.id,
    i.historyDetailID,
    i.url,
    i.prompt,
    i.state,
    i.mimeType,
    i.styleId,
    i.pipeline,
    hd.historyID,
    hd.type,
    hd.text,
    hd.createdAt,
    h.UUID,
    h.title,
    h.chatBotModel,
    h.softDeleted
FROM HistoryDetailImage i
INNER JOIN HistoryDetail hd ON hd.id = i.historyDetailID
INNER JOIN History h        ON h.id = hd.historyID
ORDER BY i.id ASC
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


def get_nova_chatbot_images(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for HistoryDetail Images")

    # Filter out secondary transactional database engines
    files_found = [
        x for x in files_found if not x.endswith(("-journal", "-wal", "-shm"))
    ]
    file_found = next((str(x) for x in files_found if "chat-ai.db" in str(x)), None)

    if not file_found:
        logfunc("[nova_chatbot_images] Nova database file not found.")
        return

    try:
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute(QUERY)
        rows_raw = cursor.fetchall()
        db.close()
    except Exception as e:
        logfunc(f"[nova_chatbot_images] Error reading {file_found}: {e}")
        return

    if not rows_raw:
        logfunc(f"[nova_chatbot_images] No image records found in {file_found}.")
        return

    headers = (
        "Image ID",
        "Msg. ID",
        "Conv. ID",
        "Conv. UUID",
        "Conv. Title",
        "AI Model",
        "Conv. Deleted",
        "Media Submitted By",
        "Msg. Text",
        "Msg. Timestamp (UTC)",
        "Prompt",
        "State",
        "Pipeline",
        "Style ID",
        "MIME Type",
        "Firebase Storage Path",
        "Forensic Notes",
    )

    rows = []
    for row in rows_raw:
        model_int = row[14]
        model_name = "Unknown"
        if model_int is not None:
            name_lookup = CHAT_BOT_MODEL_MAP.get(model_int)
            model_name = (
                f"{name_lookup} ({model_int})"
                if name_lookup
                else f"Unknown Model ({model_int})"
            )

        state_int = row[4]
        state_label = ""
        if state_int is not None:
            name_state = IMAGE_STATE_MAP.get(state_int)
            state_label = f"{name_state} ({state_int})" if name_state else f"Unknown ({state_int})"

        raw_role = row[9]
        if raw_role == 0:
            submitted_by = "USER"
            forensic_note = (
                "Media element actively selected and submitted by the user to the chatbot interface. "
                "The file content resides remotely on Firebase Storage and is not locally cached."
            )
        elif raw_role == 1:
            submitted_by = "AI ASSISTANT"
            forensic_note = (
                "Media element generated or provided back by the AI response. "
                "Stored on Firebase Storage; temporary local copies might be found in cache/image_manager_disk_cache/."
            )
        else:
            submitted_by = f"UNKNOWN ({raw_role})"
            forensic_note = "Unknown structural context for media origin."

        rows.append(
            (
                row[0],
                row[1],
                row[8],
                row[12] or "",
                row[13] or "",
                model_name,
                "DELETED" if row[15] == 1 else "No",
                submitted_by,
                row[10] or "",
                _convert_ms_timestamp(row[11]),
                row[3] or "",
                state_label,
                row[7] or "",
                row[6] if row[6] is not None else "",
                row[5] or "",
                row[2] or "",
                forensic_note,
            )
        )

    report_name = "HistoryDetailImages"
    report = ArtifactHtmlReport(report_name)
    report.start_artifact_report(report_folder, report_name)
    report.add_script()

    # Enforce safe framework-side text escaping to block script injection vectors entirely
    report.write_artifact_data_table(headers, rows, file_found, html_escape=True)
    report.end_artifact_report()

    tsv(report_folder, headers, rows, report_name, file_found)
    timeline(report_folder, report_name, rows, headers)
    logfunc(
        f"[nova_chatbot_images] Processed {len(rows)} submitted image records."
    )
