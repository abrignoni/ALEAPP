__artifacts_v2__ = {
    "nova_chatbot_links": {
        "name": "Nova AI Chatbot - Shared Links",
        "description": (
            "Extracts all link records from the AI Chatbot - Nova app "
            "(HistoryDetailLink table). Each row represents one URL shared within "
            "a conversation and is enriched with parent message context from "
            "HistoryDetail and parent conversation context from History, including "
            "the message text that accompanied the link, the role of the sender "
            "(USER or ASSISTANT), the AI model used in the conversation, and the "
            "soft-deleted status of the parent conversation. "
            "Links are rendered as clickable anchors in the HTML report. "
            "The table is currently empty in observed samples but the module is "
            "future-proof and will extract records if the table is populated in "
            "other device images or application versions."
        ),
        "author": "Guilherme Guilherme",
        "version": "0.2",
        "date": "2025-04-27",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": (
            "Database: com.scaleup.chatai/databases/chat-ai.db. "
            "HistoryDetailLink.url stores the full URL shared in the message. "
            "Links may be shared by the USER (e.g. a webpage submitted for AI "
            "analysis) or by the ASSISTANT (e.g. a reference link in a response). "
            "The role of the message is determined by HistoryDetail.type: "
            "0 = USER, 1 = ASSISTANT. "
            "softDeleted is inherited from the parent History record; DELETED means "
            "the conversation was removed by the user but the link record remains "
            "physically in the database and is forensically recoverable. "
            "If this report contains no rows the HistoryDetailLink table was empty "
            "in the examined database — this is normal for the current app version."
        ),
        "paths": ("*/com.scaleup.chatai/databases/chat-ai.db",),
        "function": "get_nova_chatbot_links",
    }
}

import sqlite3
import datetime
import html as html_module
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
# One row per HistoryDetailLink, enriched with parent message and
# conversation context.
# ---------------------------------------------------------------------------
QUERY = """
SELECT
    -- Link record
    l.id                    AS link_id,
    l.historyDetailID       AS msg_id,
    l.url                   AS link_url,

    -- Parent message context (HistoryDetail)
    hd.historyID            AS conv_id,
    hd.type                 AS msg_type,
    hd.text                 AS msg_text,
    hd.createdAt            AS msg_created_at,

    -- Parent conversation context (History)
    h.UUID                  AS conv_uuid,
    h.title                 AS conv_title,
    h.chatBotModel          AS chat_bot_model,
    h.softDeleted           AS soft_deleted

FROM HistoryDetailLink l
INNER JOIN HistoryDetail hd ON hd.id = l.historyDetailID
INNER JOIN History h        ON h.id  = hd.historyID
ORDER BY l.id ASC
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _e(text):
    return html_module.escape(str(text)) if text else ""


def _convert_ms_timestamp(ms):
    if ms is None:
        return ""
    try:
        return datetime.datetime.utcfromtimestamp(ms / 1000).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )
    except (OSError, OverflowError, ValueError):
        return str(ms)


def _resolve_model(model_int):
    if model_int is None:
        return "Unknown"
    name = CHAT_BOT_MODEL_MAP.get(model_int)
    return f"{name} ({model_int})" if name else f"Unknown Model ({model_int})"


def _format_soft_deleted(value):
    return "DELETED" if value == 1 else "No"


def _format_role(type_int):
    return {0: "USER", 1: "ASSISTANT"}.get(type_int, f"UNKNOWN ({type_int})")


def _build_link_cell(url):
    """Render a URL as a clearly labelled clickable anchor."""
    if not url:
        return ""
    return (
        f'<div style="font-size:12px; line-height:1.8;">'
        f'  <span style="font-size:18px;">🔗</span><br>'
        f'  <a href="{_e(url)}" target="_blank"'
        f'     style="word-break:break-all;">{_e(url)}</a>'
        f"</div>"
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def get_nova_chatbot_links(files_found, report_folder, seeker, wrap_text):
    """
    Entry point for the nova_chatbot_links artifact.

    Extracts every HistoryDetailLink record enriched with parent message and
    conversation context. Outputs HTML report, TSV, and timeline.
    Handles an empty HistoryDetailLink table gracefully.
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
                f"[nova_chatbot_links] Error reading {file_found}: {e}"
            )
            continue

        # Gracefully handle an empty table — log and produce an empty report
        # so the examiner knows the module ran and the table had no records.
        if not rows_raw:
            scripts.ilapfuncs.logfunc(
                f"[nova_chatbot_links] HistoryDetailLink table is empty in {file_found}."
            )
            report_name = "Nova AI Chatbot - HistoryDetailLinks"
            report = ArtifactHtmlReport(report_name)
            report.start_artifact_report(report_folder, report_name)
            report.add_script()
            report.write_artifact_data_table(
                [
                    "Link ID",
                    "Msg. ID",
                    "Conv. ID",
                    "Conv. UUID",
                    "Conv. Title",
                    "AI Model",
                    "Conv. Deleted",
                    "Msg. Role",
                    "Msg. Text",
                    "Msg. Timestamp (UTC)",
                    "Link URL",
                ],
                [],
                file_found,
                html_escape=False,
            )
            report.end_artifact_report()
            continue

        headers = [
            # Link identity
            "Link ID",
            "Msg. ID",
            "Conv. ID",
            # Conversation context
            "Conv. UUID",
            "Conv. Title",
            "AI Model",
            "Conv. Deleted",
            # Message context
            "Msg. Role",
            "Msg. Text",
            "Msg. Timestamp (UTC)",
            # Link (HTML rendered)
            "Link URL",
        ]

        html_rows = []
        tsv_rows = []

        for row in rows_raw:
            (
                link_id,
                msg_id,
                link_url,
                conv_id,
                msg_type,
                msg_text,
                msg_created_at,
                conv_uuid,
                conv_title,
                chat_bot_model,
                soft_deleted,
            ) = row

            common = (
                link_id,
                msg_id,
                conv_id,
                conv_uuid or "",
                conv_title or "",
                _resolve_model(chat_bot_model),
                _format_soft_deleted(soft_deleted),
                _format_role(msg_type),
                msg_text or "",
                _convert_ms_timestamp(msg_created_at),
            )

            html_rows.append(common + (_build_link_cell(link_url),))
            tsv_rows.append(common + (link_url or "",))

        # HTML report
        report_name = "Nova AI Chatbot - HistoryDetailLinks"
        report = ArtifactHtmlReport(report_name)
        report.start_artifact_report(report_folder, report_name)
        report.add_script()
        report.write_artifact_data_table(
            headers, html_rows, file_found, html_escape=False
        )
        report.end_artifact_report()

        # TSV
        scripts.ilapfuncs.tsv(report_folder, headers, tsv_rows, report_name, file_found)

        # Timeline (Msg. Timestamp, index 9)
        scripts.ilapfuncs.timeline(report_folder, report_name, tsv_rows, headers)
