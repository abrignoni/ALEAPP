__artifacts_v2__ = {
    "nova_cache_images": {
        "name": "Cached Images (Glide Disk Cache)",
        "description": (
            "Extracts cached image files from the Nova AI Chatbot Glide disk cache "
            "(cache/image_manager_disk_cache/*.0). These files are raw JPEG images "
            "downloaded from Firebase Storage and cached locally."
        ),
        "author": "Guilherme Guilherme",
        "version": "2.0",
        "date": "2026-05-21",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": "Glide disk cache location: cache/image_manager_disk_cache/*.0.",
        "paths": (
            "*/com.scaleup.chatai/cache/image_manager_disk_cache/*",
            "*/data/data/com.scaleup.chatai/cache/image_manager_disk_cache/*",
        ),
        "function": "get_nova_cache_images",
        "output_types": "standard",
        "artifact_icon": "image",
    }
}

import os
import datetime
from datetime import timezone
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, media_to_html


def get_nova_cache_images(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Nova Cached Images")

    data_list = []

    for file_found in files_found:
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue

        fname = os.path.basename(file_found)
        if not fname.endswith(".0"):
            continue

        try:
            stat = os.stat(file_found)
            size_bytes = stat.st_size

            # Modern, non-deprecated timezone conversion
            mtime = datetime.datetime.fromtimestamp(stat.st_mtime, timezone.utc)
            mtime_str = mtime.strftime("%Y-%m-%d %H:%M:%S UTC")

            # Mandatory framework call: copies images to output structure and populates LAVA tracking manifests
            media_to_html(fname, file_found, report_folder)

            # Parse path so it consistently normalizes from the extraction /data node onward
            normalized_path = file_found.replace("\\", "/")
            if "/data/" in normalized_path:
                display_path = "/data/" + normalized_path.split("/data/", 1)[1]
            elif "data/data/" in normalized_path:
                display_path = "/data/data/" + normalized_path.split("data/data/", 1)[1]
            else:
                display_path = normalized_path

            data_list.append((fname, size_bytes, mtime_str, display_path))

        except Exception as e:
            logfunc(f"[nova_cache_images] Error reading {file_found}: {e}")

    if not data_list:
        logfunc("No Nova Cached Images data found.")
        return

    report_name = "Cached Images"
    report = ArtifactHtmlReport(report_name)
    report.start_artifact_report(report_folder, report_name)
    report.add_script()

    headers = (
        "Original Cache Filename",
        "File Size (Bytes)",
        "Last Modified (UTC)",
        "Path",
    )

    # HTML injection vulnerabilities are entirely eliminated by delegating escaping to the framework
    report.write_artifact_data_table(
        headers, data_list, report_folder, table_id="NovaCacheImages", html_escape=True
    )
    report.end_artifact_report()

    tsv(report_folder, headers, data_list, report_name)
    logfunc(f"[nova_cache_images] Displayed {len(data_list)} cached image entries.")
