__artifacts_v2__ = {
    "nova_cache_images": {
        "name": "Nova AI Chatbot - Cached Images (Glide Disk Cache)",
        "description": (
            "Extracts all cached image files from the Nova AI Chatbot app's Glide disk cache "
            "(cache/image_manager_disk_cache/*.0). These .0 files are raw JPEG images that were "
            "downloaded from Firebase Storage and cached locally. The module embeds the original "
            "cache file paths as file:// URLs in the HTML report, allowing direct preview from "
            "the extracted data folder. No copying is performed, preserving forensic integrity. "
            "Each image is displayed as a clickable thumbnail with file metadata."
        ),
        "author": "Guilherme Guilherme",
        "version": "1.3",
        "date": "2026-05-03",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": (
            "The Glide disk cache location: cache/image_manager_disk_cache/*.0. "
            "Each .0 file is a raw JPEG. The filename is a SHA-256 hash of the signed Firebase URL. "
            "The module directly links to the original file using absolute paths. "
            "For the preview to work, the report must be opened on the same computer that extracted "
            "the data, and the browser must allow file:// links (most do when the report is also "
            "opened from a file:// location)."
        ),
        "paths": ("*/com.scaleup.chatai/cache/image_manager_disk_cache",),
        "function": "get_nova_cache_images",
    }
}

import os
import csv
import datetime
import html as html_module
from scripts.artifact_report import ArtifactHtmlReport
import scripts.ilapfuncs


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
        elif size_bytes < 1024**3:
            return f"{size_bytes / (1024**2):.1f} MB"
        else:
            return f"{size_bytes / (1024**3):.2f} GB"
    except (ValueError, TypeError):
        return str(size_bytes)


def get_nova_cache_images(files_found, report_folder, seeker, wrap_text):
    """
    Entry point for the nova_cache_images artifact.
    Scans for *.0 files, and generates an HTML gallery with direct file:// links
    to the original cache files. No copying is performed.
    """
    # Collect all unique cache directories from the glob matches
    cache_dirs = set()
    for path in files_found:
        path = str(path)
        if os.path.isdir(path):
            cache_dirs.add(path)
        else:
            parent = os.path.dirname(path)
            cache_dirs.add(parent)

    if not cache_dirs:
        scripts.ilapfuncs.logfunc("[nova_cache_images] No cache directory found.")
        return

    all_images = []  # list of dict with metadata and absolute path

    for cache_dir in cache_dirs:
        if not os.path.isdir(cache_dir):
            continue
        for fname in os.listdir(cache_dir):
            if not fname.endswith(".0"):
                continue
            src_path = os.path.join(cache_dir, fname)
            try:
                stat = os.stat(src_path)
                all_images.append(
                    {
                        "original_name": fname,
                        "abs_path": src_path,
                        "size": stat.st_size,
                        "mtime": stat.st_mtime,
                    }
                )
            except Exception as e:
                scripts.ilapfuncs.logfunc(
                    f"[nova_cache_images] Error reading {src_path}: {e}"
                )

    if not all_images:
        scripts.ilapfuncs.logfunc("[nova_cache_images] No .0 cache files found.")
        return

    all_images.sort(key=lambda x: x["mtime"], reverse=True)

    # Prepare HTML rows
    headers = [
        "Thumbnail & Filename",
        "File Size",
        "Last Modified (UTC)",
        "Original Cache Filename",
    ]
    html_rows = []
    tsv_rows = []

    for img in all_images:
        # Convert absolute path to file:// URL
        abs_url = "file://" + os.path.abspath(img["abs_path"])
        # For display, use the basename as label
        display_name = f"{img['original_name']}"
        thumbnail_html = (
            f'<div style="text-align:center;">'
            f'  <a href="{abs_url}" target="_blank" title="Open original .0 file">'
            f'    <img src="{abs_url}" style="max-width:300px; max-height:200px; '
            f"         border:1px solid #bdc3c7; border-radius:6px; margin:6px; "
            f'         box-shadow:2px 2px 6px rgba(0,0,0,0.1);" '
            f'         alt="{_e(display_name)}" />'
            f"  </a><br>"
            f"  <strong>{_e(display_name)}</strong>"
            f"</div>"
        )
        size_str = _format_file_size(img["size"])
        mtime_str = _convert_timestamp(img["mtime"])
        html_rows.append((thumbnail_html, size_str, mtime_str, img["original_name"]))
        tsv_rows.append((display_name, size_str, mtime_str, img["original_name"]))

    # Generate HTML report directly inside report_folder (top-level _HTML)
    report_name = "Nova AI Chatbot - Cached Images"
    report = ArtifactHtmlReport(report_name)
    report.start_artifact_report(report_folder, report_name)
    report.add_script()
    report.write_artifact_data_table(
        headers, html_rows, "cache/image_manager_disk_cache", html_escape=False
    )
    report.end_artifact_report()

    # TSV export
    tsv_path = os.path.join(report_folder, f"{report_name}.tsv")
    with open(tsv_path, "w", newline="", encoding="utf-8") as tsvfile:
        writer = csv.writer(tsvfile, delimiter="\t")
        writer.writerow(
            ["Filename", "File Size", "Last Modified (UTC)", "Original Cache Filename"]
        )
        writer.writerows(tsv_rows)

    scripts.ilapfuncs.logfunc(
        f"[nova_cache_images] Displayed {len(all_images)} cached images using file:// links."
    )
