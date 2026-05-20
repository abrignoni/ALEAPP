__artifacts_v2__ = {
    "nova_mediastore": {
        "name": "Nova AI Chatbot - MediaStore Aggregation",
        "description": (
            "Extracts and correlates metadata for files created, downloaded, or shared "
            "by the Nova AI Chatbot app that are cataloged inside Android's MediaStore database. "
            "By querying the central system media provider index, this module resolves virtualized "
            "Scoped Storage paths and identifies artifacts physically saved across shared system "
            "folders (such as /sdcard/Movies/ or /sdcard/Download/) where owner_package_name matches "
            "the Nova AI identifier. Images and videos are displayed as clickable thumbnails with metadata."
        ),
        "author": "Guilherme Guilherme",
        "version": "1.0",
        "date": "2026-05-20",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": (
            "Target database: com.android.providers.media/databases/external.db. "
            "The module parses the 'files' table, pulling records explicitly linked to "
            "'com.scaleup.chatai' via the owner_package_name attribute. "
            "It establishes clickable previews for media rows directly to the file's raw path."
        ),
        "paths": ("*/com.android.providers.media/databases/external.db*",),
        "function": "get_nova_mediastore",
    }
}

import os
import csv
import datetime
import html as html_module
from scripts.artifact_report import ArtifactHtmlReport
import scripts.ilapfuncs
from scripts.ilapfuncs import open_sqlite_db_readonly


def _e(text):
    return html_module.escape(str(text)) if text else ""


def _convert_timestamp(ts_sec):
    if ts_sec is None:
        return ""
    try:
        return datetime.datetime.utcfromtimestamp(ts_sec).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )
    except (OSError, OverflowError, ValueError):
        return str(ts_sec)


def _format_file_size(size_bytes):
    if size_bytes is None:
        return ""
    try:
        size_bytes = int(size_bytes)
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024**2:
            return f"{size_bytes / (1024**2):.1f} MB"
        else:
            return f"{size_bytes / (1024**3):.2f} GB"
    except (ValueError, TypeError):
        return str(size_bytes)


def get_nova_mediastore(files_found, report_folder, seeker, wrap_text):
    """
    Entry point for the nova_mediastore artifact.
    Queries the Android MediaProvider system database to locate all indexed entries
    belonging to Nova AI, tracking down actual storage paths of media items.
    """
    db_file = None
    for file_found in files_found:
        if file_found.endswith("external.db"):
            db_file = file_found
            break

    if not db_file:
        scripts.ilapfuncs.logfunc(
            "[nova_mediastore] MediaStore 'external.db' database not found in extraction."
        )
        return

    try:
        db = open_sqlite_db_readonly(db_file)
        cursor = db.cursor()
        # Querying MediaStore files schema filtering specifically by Nova package name
        cursor.execute(
            """
            SELECT 
                _id,
                _data,
                _size,
                date_added,
                date_modified,
                mime_type,
                title
            FROM files 
            WHERE owner_package_name = 'com.scaleup.chatai'
            ORDER BY date_added DESC
        """
        )
        all_rows = cursor.fetchall()
    except Exception as e:
        scripts.ilapfuncs.logfunc(
            f"[nova_mediastore] Failed to query external.db: {e}"
        )
        return

    if not all_rows:
        scripts.ilapfuncs.logfunc(
            "[nova_mediastore] No entries found for package 'com.scaleup.chatai' inside MediaStore."
        )
        db.close()
        return

    headers = [
        "Media & Preview",
        "Physical Storage Path",
        "File Size",
        "Date Added (UTC)",
        "Date Modified (UTC)",
        "MIME Type",
    ]
    html_rows = []
    tsv_rows = []

    for row in all_rows:
        media_id = row[0]
        raw_path = str(row[1]) if row[1] else ""
        size_bytes = row[2]
        added_ts = row[3]
        modified_ts = row[4]
        mime_type = str(row[5]) if row[5] else ""
        title = str(row[6]) if row[6] else "Unknown"

        size_str = _format_file_size(size_bytes)
        added_str = _convert_timestamp(added_ts)
        modified_str = _convert_timestamp(modified_ts)

        # Build absolute URL link to the mapped data file location 
        abs_url = "file://" + os.path.abspath(raw_path)
        base_name = os.path.basename(raw_path) if raw_path else title

        # Create a preview column based on file MIME type categorization
        if mime_type.startswith("image/"):
            preview_html = (
                f'<div style="text-align:center;">'
                f'  <a href="{abs_url}" target="_blank" title="View Full Image">'
                f'    <img src="{abs_url}" style="max-width:250px; max-height:180px; '
                f"         border:1px solid #bdc3c7; border-radius:6px; margin:4px; "
                f'         box-shadow:2px 2px 5px rgba(0,0,0,0.1);" alt="{_e(base_name)}" />'
                f"  </a><br>"
                f"  <strong>{_e(base_name)}</strong>"
                f"</div>"
            )
        elif mime_type.startswith("video/"):
            preview_html = (
                f'<div style="text-align:center;">'
                f'  <video width="250" height="180" controls style="border:1px solid #bdc3c7; border-radius:6px;">'
                f'    <source src="{abs_url}" type="{_e(mime_type)}">'
                f"    Your browser does not support HTML video preview."
                f"  </video><br>"
                f'  <a href="{abs_url}" target="_blank"><strong>{_e(base_name)} (🎬 Video)</strong></a>'
                f"</div>"
            )
        else:
            # For documents or audio recordings, output a non-media generic folder block representation
            preview_html = (
                f'<div style="text-align:center; padding:10px;">'
                f'  <span style="font-size: 24px;">📄</span><br>'
                f'  <a href="{abs_url}" target="_blank"><strong>{_e(base_name)}</strong></a>'
                f"</div>"
            )

        html_rows.append(
            (preview_html, raw_path, size_str, added_str, modified_str, mime_type)
        )
        tsv_rows.append(
            (base_name, raw_path, size_str, added_str, modified_str, mime_type)
        )

    db.close()

    # Generate HTML report
    report_name = "Nova AI Chatbot - MediaStore Aggregation"
    report = ArtifactHtmlReport(report_name)
    report.start_artifact_report(report_folder, report_name)
    report.add_script()
    report.write_artifact_data_table(
        headers, html_rows, db_file, html_escape=False
    )
    report.end_artifact_report()

    # Generate TSV Export
    tsv_path = os.path.join(report_folder, f"{report_name}.tsv")
    with open(tsv_path, "w", newline="", encoding="utf-8") as tsvfile:
        writer = csv.writer(tsvfile, delimiter="\t")
        writer.writerow(
            [
                "Filename",
                "Physical Storage Path",
                "File Size",
                "Date Added (UTC)",
                "Date Modified (UTC)",
                "MIME Type",
            ]
        )
        writer.writerows(tsv_rows)

    scripts.ilapfuncs.logfunc(
        f"[nova_mediastore] Successfully mapped {len(all_rows)} files via MediaStore indexing using file:// URLs."
    )
