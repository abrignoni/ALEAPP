__artifacts_v2__ = {
    "nova_chatbot_conversations": {
        "name": "Conversations (Full Detail)",
        "description": (
            "Reconstructs full conversations from the AI Chatbot - Nova app by joining "
            "History, HistoryDetail, HistoryDetailImage, HistoryDetailDocument, and "
            "HistoryDetailLink tables. Produces one row per message with all attachment "
            "metadata surfaced inline. Image origin (user‑submitted vs AI‑generated) is "
            "determined by the parent message role. Generated images are not resolvable "
            "locally due to Firebase signed URL tokens; the report shows the Firebase path "
            "and a forensic note. Documents are displayed with full metadata and a note "
            "confirming they were submitted by the user. Soft‑deleted conversations are "
            "flagged on every associated message row."
        ),
        "author": "Guilherme Guilherme",
        "version": "0.5",
        "date": "2026-05-03",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": (
            "Message timestamps are stored as Unix milliseconds (INTEGER) and are "
            "converted to UTC for display and timeline submission. "
            "HistoryDetail.type: 0 = USER, 1 = ASSISTANT. "
            "Attachment columns are empty when no attachment is linked to a message. "
            "A conversation flagged as DELETED means History.softDeleted = 1; the record "
            "remains in the database after user deletion and is forensically recoverable. "
            "chatBotModel is an integer mapped to known AI model names where possible. "
            "Image origin is correctly identified by the parent message role: "
            "USER messages contain user‑submitted images (e.g., vision queries); "
            "ASSISTANT messages contain AI‑generated images. "
            "All images are stored on Firebase Storage; local cache filenames are hashes "
            "of signed URLs (tokens not on device), so automatic matching is impossible. "
            "Documents are also stored on Firebase; no local copy is kept. "
            "TSV export contains plain‑text equivalents for all attachment fields."
        ),
        "paths": ("*/com.scaleup.chatai/databases/chat-ai.db",),
        "function": "get_nova_chatbot_conversations",
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
# ---------------------------------------------------------------------------
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
# Scalar helpers
# ---------------------------------------------------------------------------


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


def _resolve_image_state(state_int):
    if state_int is None:
        return ""
    label = IMAGE_STATE_MAP.get(state_int)
    return f"{label} ({state_int})" if label else f"Unknown State ({state_int})"


def _resolve_document_type(type_int):
    if type_int is None:
        return ""
    label = DOCUMENT_TYPE_MAP.get(type_int)
    return f"{label} ({type_int})" if label else f"Unknown Type ({type_int})"


def _format_role(type_int):
    return {0: "USER", 1: "ASSISTANT"}.get(type_int, f"UNKNOWN ({type_int})")


def _format_soft_deleted(value):
    return "DELETED" if value == 1 else "No"


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


def _e(text):
    return html_module.escape(str(text)) if text else ""


# ---------------------------------------------------------------------------
# Image resolution – always None (no local preview)
# ---------------------------------------------------------------------------
def _resolve_image_file(db_url, seeker, images_dir):
    return None


# ---------------------------------------------------------------------------
# Rich HTML cell builders
# ---------------------------------------------------------------------------


def _build_image_html(msg_type, img_urls, img_prompts, img_states, resolved_filenames):
    """
    Build HTML cell for images. Uses msg_type to determine origin.
    """
    if not img_urls:
        return ""

    urls = [u.strip() for u in img_urls.split(",") if u.strip()]
    prompts = (
        [p.strip() for p in img_prompts.split(",") if p.strip()] if img_prompts else []
    )

    parts = []
    for i, url in enumerate(urls):
        prompt = prompts[i] if i < len(prompts) else ""
        filename = resolved_filenames[i] if i < len(resolved_filenames) else None

        cell = '<div style="font-size:12px; line-height:1.8; text-align:center;">'

        # Prompt
        if prompt:
            cell += f'<div style="text-align:left; margin-bottom:6px;"><strong>Prompt:</strong> {_e(prompt)}</div>'

        # Forensic note based on msg_type
        if msg_type == 0:  # USER → user‑submitted (vision query)
            cell += (
                f'<div style="padding:8px; background:#fef9e7; border-left:3px solid #f39c12; '
                f'font-size:11px; margin-bottom:6px; text-align:left;">'
                f"  📤 <strong>User‑submitted image</strong><br>"
                f"  This image was uploaded by the device user (e.g., as part of a vision query). "
                f"  The file content is stored on Firebase Storage and is not cached locally."
                f"</div>"
            )
        else:  # ASSISTANT or unknown → AI‑generated
            cell += (
                f'<div style="padding:8px; background:#eaf4fb; border:1px solid #aed6f1; border-radius:4px; '
                f'font-size:11px; margin-bottom:6px; text-align:left;">'
                f"  🤖 <strong>AI‑generated image</strong><br>"
                f"  This image was created by the AI based on the user prompt. "
                f"  It is stored on Firebase Storage; a temporary local copy may exist "
                f"  in <code>cache/image_manager_disk_cache/*.0</code> but the filename "
                f"  is a hash of a signed URL that includes a token not stored on the device. "
                f"  Manual inspection of <code>.0</code> files is recommended.<br>"
                f"  <strong>Forensic action:</strong> Examine <code>.0</code> files directly as JPEG."
                f"</div>"
            )

        # Firebase path (was "Internal path")
        cell += (
            f'<div style="text-align:left; margin-top:6px; font-size:10px; color:#7f8c8d;">'
            f"  <strong>Firebase path:</strong><br>"
            f'  <code style="word-break:break-all;">{_e(url)}</code>'
            f"</div>"
        )
        cell += "</div>"

        if i < len(urls) - 1:
            cell += (
                '<hr style="border:none; border-top:1px solid #ecf0f1; margin:6px 0;">'
            )
        parts.append(cell)

    return "".join(parts)


def _build_document_html(doc_names, doc_mime_types, doc_sizes, doc_urls, doc_types):
    """
    Build HTML cell for documents – no local preview, shows Firebase path and forensic note.
    """
    if not doc_names:
        return ""

    names = [n.strip() for n in doc_names.split(",") if n.strip()]
    mimes = (
        [m.strip() for m in doc_mime_types.split(",") if m.strip()]
        if doc_mime_types
        else []
    )
    sizes = [s.strip() for s in doc_sizes.split(",") if s.strip()] if doc_sizes else []
    urls = [u.strip() for u in doc_urls.split(",") if u.strip()] if doc_urls else []
    types = [t.strip() for t in doc_types.split(",") if t.strip()] if doc_types else []

    parts = []
    for i, name in enumerate(names):
        mime = mimes[i] if i < len(mimes) else ""
        size_raw = sizes[i] if i < len(sizes) else None
        url = urls[i] if i < len(urls) else ""
        dtype_raw = types[i] if i < len(types) else None

        icon = MIME_ICON_MAP.get(mime, "📎")
        size_label = (
            _format_file_size(int(size_raw))
            if size_raw and size_raw.lstrip("-").isdigit()
            else ""
        )
        dtype_label = (
            _resolve_document_type(int(dtype_raw))
            if dtype_raw and dtype_raw.lstrip("-").isdigit()
            else ""
        )

        cell = (
            f'<div style="font-size:12px; line-height:1.7;">'
            f'  <div style="font-size:22px; margin-bottom:2px;">{icon}</div>'
            f'  <div><strong style="font-size:13px;">{_e(name)}</strong></div>'
        )
        if mime:
            cell += f"  <div><strong>MIME Type:</strong> {_e(mime)}</div>"
        if size_label:
            cell += f"  <div><strong>Size:</strong> {_e(size_label)}</div>"
        if url:
            cell += (
                f"  <div><strong>Firebase path:</strong><br>"
                f'  <code style="font-size:10px; word-break:break-all;">{_e(url)}</code></div>'
            )
        if dtype_label:
            cell += f"  <div><strong>Source Type:</strong> {_e(dtype_label)}</div>"

        # Forensic note – same as standalone document module
        cell += (
            f'  <div style="margin-top:5px; padding:4px 6px;'
            f"              background:#fef9e7; border-left:3px solid #f39c12;"
            f'              font-size:11px; color:#7d6608;">'
            f"    ⚠️ <strong>Forensic note:</strong> This file was submitted by the"
            f"    user to the AI assistant as part of this conversation."
            f"  </div>"
            f"</div>"
        )

        if i < len(names) - 1:
            cell += (
                '<hr style="border:none; border-top:1px solid #ecf0f1; margin:6px 0;">'
            )
        parts.append(cell)

    return "".join(parts)


# ---------------------------------------------------------------------------
# Plain-text builders for TSV / timeline
# ---------------------------------------------------------------------------


def _build_image_tsv(
    msg_type, img_urls, img_prompts, img_states, img_mime_types, img_pipelines
):
    """Flat plain‑text representation for TSV."""
    if not img_urls:
        return ""
    origin = "user-submitted" if msg_type == 0 else "ai-generated"
    parts = [f"Origin: {origin}", f"URL: {img_urls}"]
    if img_prompts:
        parts.append(f"Prompt: {img_prompts}")
    if img_states:
        states = ", ".join(
            _resolve_image_state(int(s.strip()))
            for s in img_states.split(",")
            if s.strip().lstrip("-").isdigit()
        )
        if states:
            parts.append(f"State: {states}")
    if img_mime_types:
        parts.append(f"MIME: {img_mime_types}")
    if img_pipelines:
        parts.append(f"Pipeline: {img_pipelines}")
    return " | ".join(parts)


def _build_document_tsv(doc_names, doc_mime_types, doc_sizes, doc_urls, doc_types):
    """Flat plain‑text representation for TSV."""
    if not doc_names:
        return ""
    size_label = (
        _format_file_size(doc_sizes)
        if doc_sizes and doc_sizes.lstrip("-").isdigit()
        else ""
    )
    dtype_label = ""
    if doc_types:
        first_type = doc_types.split(",")[0].strip()
        if first_type.lstrip("-").isdigit():
            dtype_label = _resolve_document_type(int(first_type))
        else:
            dtype_label = first_type
    parts = [f"Name: {doc_names}"]
    if doc_mime_types:
        parts.append(f"MIME: {doc_mime_types}")
    if size_label:
        parts.append(f"Size: {size_label}")
    if doc_urls:
        parts.append(f"Path: {doc_urls}")
    if dtype_label:
        parts.append(f"Type: {dtype_label}")
    parts.append("Note: File submitted by user to AI assistant")
    return " | ".join(parts)


# ---------------------------------------------------------------------------
# SQL (unchanged)
# ---------------------------------------------------------------------------
QUERY = """
SELECT
    h.id                        AS conv_id,
    h.UUID                      AS conv_uuid,
    h.title                     AS conv_title,
    h.chatBotModel              AS chat_bot_model,
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
    GROUP_CONCAT(DISTINCT hdi.state)        AS img_states,
    GROUP_CONCAT(DISTINCT hdi.mimeType)     AS img_mime_types,
    GROUP_CONCAT(DISTINCT hdi.pipeline)     AS img_pipelines,

    GROUP_CONCAT(DISTINCT hdd.name)         AS doc_names,
    GROUP_CONCAT(DISTINCT hdd.mimeType)     AS doc_mime_types,
    GROUP_CONCAT(DISTINCT hdd.size)         AS doc_sizes,
    GROUP_CONCAT(DISTINCT hdd.url)          AS doc_urls,
    GROUP_CONCAT(DISTINCT hdd.type)         AS doc_types,

    GROUP_CONCAT(DISTINCT hdl.url)          AS link_urls

FROM History h
INNER JOIN HistoryDetail hd
    ON hd.historyID = h.id
LEFT JOIN HistoryDetailImage hdi
    ON hdi.historyDetailID = hd.id
LEFT JOIN HistoryDetailDocument hdd
    ON hdd.historyDetailID = hd.id
LEFT JOIN HistoryDetailLink hdl
    ON hdl.historyDetailID = hd.id
GROUP BY hd.id
ORDER BY h.id ASC, hd.createdAt ASC
"""

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def get_nova_chatbot_conversations(files_found, report_folder, seeker, wrap_text):
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
                f"[nova_chatbot_conversations] Error reading {file_found}: {e}"
            )
            continue

        if not rows_raw:
            scripts.ilapfuncs.logfunc(
                f"[nova_chatbot_conversations] No records found in {file_found}."
            )
            continue

        images_dir = os.path.join(report_folder, "nova_images")
        os.makedirs(images_dir, exist_ok=True)

        headers = [
            "Conv. ID",
            "Conv. UUID",
            "Conv. Title",
            "AI Model",
            "Conv. Deleted",
            "Conv. Sync State",
            "Msg. ID",
            "Msg. UUID",
            "Role",
            "Message Text",
            "Token Count",
            "Reasoning Content",
            "Message Timestamp (UTC)",
            "Msg. Sync State",
            "Image Attachment",
            "Document Attachment",
            "Link URL(s)",
        ]

        html_rows = []
        tsv_rows = []

        for row in rows_raw:
            (
                conv_id,
                conv_uuid,
                conv_title,
                chat_bot_model,
                soft_deleted,
                conv_sync_state,
                msg_id,
                msg_uuid,
                msg_type,
                msg_text,
                msg_token,
                msg_reasoning,
                msg_created_at,
                msg_sync_state,
                img_urls,
                img_prompts,
                img_states,
                img_mime_types,
                img_pipelines,
                doc_names,
                doc_mime_types,
                doc_sizes,
                doc_urls,
                doc_types,
                link_urls,
            ) = row

            # Resolve images (always None, but we need a list parallel to URLs)
            resolved_filenames = []
            if img_urls:
                for raw_url in img_urls.split(","):
                    raw_url = raw_url.strip()
                    resolved_filenames.append(
                        _resolve_image_file(raw_url, seeker, images_dir)
                    )

            # Common scalar columns
            common = (
                conv_id,
                conv_uuid or "",
                conv_title or "",
                _resolve_model(chat_bot_model),
                _format_soft_deleted(soft_deleted),
                conv_sync_state if conv_sync_state is not None else "",
                msg_id,
                msg_uuid or "",
                _format_role(msg_type),
                msg_text or "",
                msg_token if msg_token is not None else "",
                msg_reasoning or "",
                _convert_ms_timestamp(msg_created_at),
                msg_sync_state if msg_sync_state is not None else "",
            )

            # HTML cells
            img_html = _build_image_html(
                msg_type, img_urls, img_prompts, img_states, resolved_filenames
            )
            doc_html = _build_document_html(
                doc_names, doc_mime_types, doc_sizes, doc_urls, doc_types
            )
            html_rows.append(common + (img_html, doc_html, link_urls or ""))

            # TSV cells
            img_tsv = _build_image_tsv(
                msg_type,
                img_urls,
                img_prompts,
                img_states,
                img_mime_types,
                img_pipelines,
            )
            doc_tsv = _build_document_tsv(
                doc_names, doc_mime_types, doc_sizes, doc_urls, doc_types
            )
            tsv_rows.append(common + (img_tsv, doc_tsv, link_urls or ""))

        # HTML report
        report_name = "Conversations (Full Detail)"
        report = ArtifactHtmlReport(report_name)
        report.start_artifact_report(report_folder, report_name)
        report.add_script()
        report.write_artifact_data_table(
            headers, html_rows, file_found, html_escape=False
        )
        report.end_artifact_report()

        # TSV and timeline
        scripts.ilapfuncs.tsv(report_folder, headers, tsv_rows, report_name, file_found)
        scripts.ilapfuncs.timeline(report_folder, report_name, tsv_rows, headers)
