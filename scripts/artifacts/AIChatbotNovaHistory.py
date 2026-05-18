__artifacts_v2__ = {
    "nova_chatbot_history": {
        "name": "Nova AI Chatbot - Conversation History",
        "description": (
            "Extracts the conversation index from the AI Chatbot - Nova app "
            "(com.scaleup.chatai) from the History table. "
            "Each row represents one conversation and includes the conversation title, "
            "AI model used, starred and soft-deleted status, all relevant timestamps, "
            "and sync metadata. Each row is further enriched with three summary columns "
            "derived from HistoryDetail: total message count, timestamp of the last "
            "message, and the text of the first user message — providing immediate "
            "investigative context without requiring the full message detail report. "
            "Soft-deleted conversations are flagged on every row."
        ),
        "author": "Guilherme Guilherme",
        "version": "0.2",
        "date": "2025-04-27",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": (
            "Database: com.scaleup.chatai/databases/chat-ai.db. "
            "All timestamps (createdAt, updatedAt, lastModifiedAt) are stored as Unix "
            "milliseconds (INTEGER) and converted to UTC strings for display. "
            "chatBotModel is an integer mapped to known AI model names where possible; "
            "unknown values are shown as 'Unknown Model (N)'. "
            "softDeleted = 1 indicates the conversation was deleted by the user but "
            "remains physically present in the database and is forensically recoverable. "
            "starred = 1 indicates the user bookmarked the conversation. "
            "assistantId identifies a custom AI assistant persona assigned to the "
            "conversation when not NULL. "
            "captionHistoryId links to an associated caption or summary history entry "
            "when present. "
            "message_count, last_message_at, and first_user_message are aggregated "
            "from HistoryDetail via LEFT JOIN so conversations with zero messages are "
            "still returned. first_user_message reflects the earliest USER-role message "
            "text (HistoryDetail.type = 0)."
        ),
        "paths": ("*/com.scaleup.chatai/databases/chat-ai.db",),
        "function": "get_nova_chatbot_history",
    }
}

import sqlite3
import datetime
from scripts.artifact_report import ArtifactHtmlReport
import scripts.ilapfuncs

# ---------------------------------------------------------------------------
# Known mappings for the chatBotModel integer field.
# Source: FirestoreHistory.EngineTypes enum ordinals from decompiled APK source
# (com.scaleup.chatai.ui.conversation.FirestoreHistory).
# The integer stored in the database is the ENUM ORDINAL (0-based position),
# NOT the botId from chatbotAgentMap. These are two independent systems.
# Image-generating engines: 3 (legacy Bard ordinal reused), 4, 12, 13, 17.
# NOTE: ordinal 3 ('bard') was reused for image generation in newer app versions;
# presence of HistoryDetailImage records confirms image generation regardless of label.
# NOTE: ordinal 20 ('deepSeekR1') — if reasoningContent is NULL the actual API
# call may have used DeepSeek V3; the field reflects the UI selector, not the API.
# ---------------------------------------------------------------------------
CHAT_BOT_MODEL_MAP = {
    0: "ChatGPT 3.5",  # gpt-3.5
    1: "GPT-5",  # gpt-5
    2: "GPT-4o",  # gpt-4o
    3: "Bard / Image Gen.",  # bard (legacy; reused for image generation)
    4: "Image Generator",  # image-generator
    5: "Vision",  # vision
    6: "Google Vision",  # googleVision
    7: "Document",  # document
    8: "LLaMA 2",  # llama2
    9: "Nova",  # nova
    10: "Gemini",  # gemini
    11: "Superbot",  # superbot
    12: "Logo Generator",  # logo-generator
    13: "Tattoo Generator",  # tattoo-generator
    14: "Web Search",  # webSearch
    15: "Claude",  # claude
    16: "DeepSeek",  # deepSeek
    17: "Signature Generator",  # signature-generator
    18: "Mistral",  # mistral
    19: "Grok",  # grok
    20: "DeepSeek R1",  # deepSeekR1
    21: "AI Filter",  # aiFilter
    22: "Voice Chat",  # voiceChat
    23: "Snap & Solve",  # snapAndSolve
    24: "Study Planner",  # studyPlanner
    25: "Quiz Maker",  # quizMaker
    26: "Essay Helper",  # essayHelper
    27: "Gemini 3 Pro",  # gemini-3-pro
    28: "GPT-5.1",  # gpt-5.1
    29: "GPT-4o Mini",  # 4o-mini
}

# ---------------------------------------------------------------------------
# SQL
# One row per History entry, enriched with three summary columns from
# HistoryDetail via a LEFT JOIN + GROUP BY so conversations with zero
# messages are still returned.
# ---------------------------------------------------------------------------
QUERY = """
SELECT
    h.id                                                AS conv_id,
    h.UUID                                              AS conv_uuid,
    h.title                                             AS title,
    h.chatBotModel                                      AS chat_bot_model,
    h.assistantId                                       AS assistant_id,
    h.captionHistoryId                                  AS caption_history_id,
    h.starred                                           AS starred,
    h.softDeleted                                       AS soft_deleted,
    h.syncState                                         AS sync_state,
    h.syncRetryCount                                    AS sync_retry_count,
    h.createdAt                                         AS created_at,
    h.updatedAt                                         AS updated_at,
    h.lastModifiedAt                                    AS last_modified_at,
    COUNT(hd.id)                                        AS message_count,
    MAX(hd.createdAt)                                   AS last_msg_ts,
    MIN(CASE WHEN hd.type = 0 THEN hd.text END)         AS first_user_msg
FROM History h
LEFT JOIN HistoryDetail hd
    ON hd.historyID = h.id
GROUP BY h.id
ORDER BY h.createdAt ASC
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _convert_ms_timestamp(ms):
    """Convert a Unix millisecond timestamp to a human-readable UTC string."""
    if ms is None:
        return ""
    try:
        return datetime.datetime.utcfromtimestamp(ms / 1000).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )
    except (OSError, OverflowError, ValueError):
        return str(ms)


def _resolve_model(model_int):
    """Return a labelled model name, falling back to the raw integer for unknowns."""
    if model_int is None:
        return "Unknown"
    name = CHAT_BOT_MODEL_MAP.get(model_int)
    return f"{name} ({model_int})" if name else f"Unknown Model ({model_int})"


def _format_soft_deleted(value):
    """Return a clearly labelled string for the softDeleted field."""
    return "DELETED" if value == 1 else "No"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def get_nova_chatbot_history(files_found, report_folder, seeker, wrap_text):
    """
    Entry point for the nova_chatbot_history artifact.

    Queries the History table enriched with per-conversation summary data
    from HistoryDetail. Outputs HTML report, TSV, and timeline.
    """

    for file_found in files_found:
        file_found = str(file_found)

        if not file_found.endswith("chat-ai.db"):
            continue

        try:
            db = sqlite3.connect(file_found)
            cursor = db.cursor()
            cursor.execute(QUERY)
            rows_raw = cursor.fetchall()
            db.close()

        except Exception as e:
            scripts.ilapfuncs.logfunc(
                f"[nova_chatbot_history] Error reading {file_found}: {e}"
            )
            continue

        if not rows_raw:
            scripts.ilapfuncs.logfunc(
                f"[nova_chatbot_history] No records found in {file_found}."
            )
            continue

        headers = [
            # --- Identity ---
            "Conv. ID",
            "Conv. UUID",
            "Title",
            # --- Model ---
            "AI Model",
            "Assistant ID",
            "Caption History ID",
            # --- Flags ---
            "Starred",
            "Soft Deleted",
            "Sync State",
            "Sync Retry Count",
            # --- Timestamps ---
            "Created At (UTC)",
            "Updated At (UTC)",
            "Last Modified At (UTC)",
            # --- Summary from HistoryDetail ---
            "Message Count",
            "Last Message At (UTC)",
            "First User Message",
        ]

        rows = []
        for row in rows_raw:
            (
                conv_id,
                conv_uuid,
                title,
                chat_bot_model,
                assistant_id,
                caption_history_id,
                starred,
                soft_deleted,
                sync_state,
                sync_retry_count,
                created_at,
                updated_at,
                last_modified_at,
                message_count,
                last_msg_ts,
                first_user_msg,
            ) = row

            rows.append(
                (
                    conv_id,
                    conv_uuid or "",
                    title or "",
                    _resolve_model(chat_bot_model),
                    assistant_id if assistant_id is not None else "",
                    caption_history_id or "",
                    "Yes" if starred else "No",
                    _format_soft_deleted(soft_deleted),
                    sync_state if sync_state is not None else "",
                    sync_retry_count if sync_retry_count is not None else "",
                    _convert_ms_timestamp(created_at),
                    _convert_ms_timestamp(updated_at),
                    _convert_ms_timestamp(last_modified_at),
                    message_count if message_count is not None else 0,
                    _convert_ms_timestamp(last_msg_ts),
                    first_user_msg or "",
                )
            )

        # --- HTML report ---
        report_name = "Nova AI Chatbot - History"
        report = ArtifactHtmlReport(report_name)
        report.start_artifact_report(report_folder, report_name)
        report.add_script()
        report.write_artifact_data_table(
            headers,
            rows,
            file_found,
            html_escape=True,
        )
        report.end_artifact_report()

        # --- TSV output ---
        scripts.ilapfuncs.tsv(report_folder, headers, rows, report_name, file_found)

        # --- Timeline (uses Created At, index 10) ---
        scripts.ilapfuncs.timeline(report_folder, report_name, rows, headers)
