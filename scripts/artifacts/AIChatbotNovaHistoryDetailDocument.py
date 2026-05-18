__artifacts_v2__ = {
    "nova_chatbot_documents": {
        "name": "Nova AI Chatbot - Submitted Documents",
        "description": (
            "Extracts all document records submitted by the user to the AI from the "
            "AI Chatbot - Nova app (HistoryDetailDocument table). Each row represents "
            "one document and is enriched with parent message context from HistoryDetail "
            "and parent conversation context from History. "
            "Documents are stored on Firebase Storage; the database stores only the "
            "Firebase object path. No local cache of user‑submitted documents is kept "
            "on the device. The metadata and a forensic note are displayed in the HTML "
            "report. The full file content is not available for preview. "
            "A forensic note is shown on every row confirming the file was actively "
            "submitted by the device user to the AI assistant."
        ),
        "author": "Guilherme Guilherme",
        "version": "0.2",
        "date": "2025-04-27",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": (
            "Database: com.scaleup.chatai/databases/chat-ai.db. "
            "HistoryDetailDocument.url stores a Firebase path such as "
            "'/document/<user_id>/<timestamp>/document-input-<uuid>'. "
            "The file content is not stored locally on the device; it lives in "
            "Firebase Storage. The metadata record is still valuable for forensic "
            "timeline and user activity. "
            "type: 0 = Local File (uploaded from the device), 1 = Remote File. "
            "size is stored in bytes and converted to a human-readable string. "
            "mimeType identifies the document format (e.g. application/pdf). "
            "softDeleted is inherited from the parent History record; DELETED means "
            "the conversation was removed by the user but the document record remains "
            "physically in the database and is forensically recoverable. "
            "The user message text associated with the document reveals the query the "
            "user submitted alongside the file to the AI."
        ),
        "paths": ("*/com.scaleup.chatai/databases/chat-ai.db",),
        "function": "get_nova_chatbot_documents",
    }
}

import os
import shutil
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

DOCUMENT_TYPE_MAP = {
    0: "Local File",
    1: "Remote File",
}

MIME_ICON_MAP = {
    "application/pdf": "📄",
    "application/msword": "📝",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "📝",
    "application/vnd.ms-excel": "📊",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "📊",
    "text/plain": "📃",
    "text/csv": "📊",
    "image/jpeg": "🖼️",
    "image/png": "🖼️",
    "image/gif": "🖼️",
    "image/webp": "🖼️",
}

# ---------------------------------------------------------------------------
# SQL
# One row per HistoryDetailDocument, enriched with parent message and
# conversation context.
# ---------------------------------------------------------------------------
QUERY = """
SELECT
    -- Document record
    d.id AS doc_id,
    d.historyDetailID AS msg_id,
    d.url AS doc_url,
    d.name AS doc_name,
    d.type AS doc_type,
    d.size AS doc_size,
    d.mimeType AS mime_type,

    -- Parent message context (HistoryDetail)
    hd.historyID AS conv_id,
    hd.type AS msg_type,
    hd.text AS msg_text,
    hd.createdAt AS msg_created_at,

    -- Parent conversation context (History)
    h.UUID AS conv_uuid,
    h.title AS conv_title,
    h.chatBotModel AS chat_bot_model,
    h.softDeleted AS soft_deleted

FROM HistoryDetailDocument d
INNER JOIN HistoryDetail hd ON hd.id = d.historyDetailID
INNER JOIN History h ON h.id = hd.historyID
ORDER BY d.id ASC
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

def _resolve_doc_type(type_int):
    if type_int is None:
        return ""
    label = DOCUMENT_TYPE_MAP.get(type_int)
    return f"{label} ({type_int})" if label else f"Unknown ({type_int})"

def _format_file_size(size_bytes):
    if size_bytes is None:
        return ""
    try:
        size_bytes = int(size_bytes)
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes / (1024**2):.1f} MB"
        else:
            return f"{size_bytes / (1024**3):.2f} GB"
    except (ValueError, TypeError):
        return str(size_bytes)

def _format_soft_deleted(value):
    return "DELETED" if value == 1 else "No"

def _format_role(type_int):
    return {0: "USER", 1: "ASSISTANT"}.get(type_int, f"UNKNOWN ({type_int})")

# ---------------------------------------------------------------------------
# Document file resolution (always returns None – no local copy)
# ---------------------------------------------------------------------------
def _resolve_document_file(doc_url, doc_name, seeker, docs_dir):
    """
    Documents are stored on Firebase Storage. The database stores only the
    Firebase object path. No local cache of user‑submitted documents is
    kept on the device. Therefore this function always returns None.
    The HTML cell will show a notice explaining the file is not available
    locally.
    """
    return None

# ---------------------------------------------------------------------------
# HTML cell builder
# ---------------------------------------------------------------------------

def _build_document_cell(doc_name, mime_type, doc_size, doc_url, doc_type, filename):
    """
    Build a self-contained HTML cell for one document record showing:
      - File icon + name (plain text, no link)
      - MIME type, size, source type, and Firebase path
      - Forensic note confirming the user submitted this file to the AI
      - Notice that the file content is stored on Firebase and not available
    """
    icon = MIME_ICON_MAP.get(mime_type, "📎")
    size_label = _format_file_size(doc_size)
    type_label = _resolve_doc_type(doc_type)

    cell = f'<div style="font-size:12px; line-height:1.8;">'
    cell += f'<div style="margin-bottom:4px;">{icon} <strong>{_e(doc_name)}</strong></div>'

    if mime_type:
        cell += f"<div><strong>MIME Type:</strong> {_e(mime_type)}</div>"
    if size_label:
        cell += f"<div><strong>Size:</strong> {_e(size_label)}</div>"
    if type_label:
        cell += f"<div><strong>Source Type:</strong> {_e(type_label)}</div>"
    if doc_url:
        cell += (
            f'<div style="margin-top:4px; font-size:10px; color:#7f8c8d;">'
            f"  <strong>Firebase Path:</strong><br>"
            f'  <code style="word-break:break-all;">{_e(doc_url)}</code>'
            f"</div>"
        )

    # Notice that the file is not stored locally
    cell += (
        f'<div style="margin-top:6px; padding:4px 6px;'
        f" background:#eaf4fb; border:1px solid #aed6f1; border-radius:4px;"
        f' font-size:11px; margin-bottom:6px;">'
        f"  ☁️ <strong>File stored on Firebase Storage</strong><br>"
        f"  The document content is not available on the device. "
        f"  The database record confirms the user submitted this file to the AI; "
        f"  the file itself resides in Firebase Storage and is not cached locally."
        f"</div>"
    )

    # Forensic note (original)
    cell += (
        f'<div style="margin-top:4px; padding:4px 6px;'
        f" background:#fef9e7; border-left:3px solid #f39c12;"
        f' font-size:11px; color:#7d6608;">'
        f"  ⚠️ <strong>Forensic note:</strong> This file was actively submitted "
        f" by the device user to the AI assistant as part of this conversation."
        f"</div>"
    )
    cell += "</div>"
    return cell

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def get_nova_chatbot_documents(files_found, report_folder, seeker, wrap_text):
    """
    Entry point for the nova_chatbot_documents artifact.

    Extracts every HistoryDetailDocument record, resolves the document file from
    the device extraction, and produces an HTML report with document metadata
    cards and download links, TSV export, and timeline output.
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
                f"[nova_chatbot_documents] Error reading {file_found}: {e}"
            )
            continue

        if not rows_raw:
            scripts.ilapfuncs.logfunc(
                f"[nova_chatbot_documents] No document records found in {file_found}."
            )
            continue

        docs_dir = os.path.join(report_folder, "nova_documents")
        os.makedirs(docs_dir, exist_ok=True)

        headers = [
            # Document identity
            "Doc. ID",
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
            # Document card (HTML)
            "Document & Metadata",
            # Plain fields for TSV
            "File Name",
            "MIME Type",
            "Size",
            "Source Type",
            "Firebase Path",        # changed from "Internal Path"
        ]

        html_rows = []
        tsv_rows = []

        for row in rows_raw:
            (
                doc_id,
                msg_id,
                doc_url,
                doc_name,
                doc_type,
                doc_size,
                mime_type,
                conv_id,
                msg_type,
                msg_text,
                msg_created_at,
                conv_uuid,
                conv_title,
                chat_bot_model,
                soft_deleted,
            ) = row

            # Resolve document from extraction (always returns None)
            filename = _resolve_document_file(doc_url, doc_name, seeker, docs_dir)

            common = (
                doc_id,
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

            doc_cell = _build_document_cell(
                doc_name, mime_type, doc_size, doc_url, doc_type, filename
            )

            html_rows.append(
                common
                + (
                    doc_cell,
                    doc_name or "",
                    mime_type or "",
                    _format_file_size(doc_size),
                    _resolve_doc_type(doc_type),
                    doc_url or "",
                )
            )

            tsv_rows.append(
                common
                + (
                    "",  # no HTML in TSV
                    doc_name or "",
                    mime_type or "",
                    _format_file_size(doc_size),
                    _resolve_doc_type(doc_type),
                    doc_url or "",
                )
            )

        # HTML report
        report_name = "Nova AI Chatbot - HistoryDetailDocuments"
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
