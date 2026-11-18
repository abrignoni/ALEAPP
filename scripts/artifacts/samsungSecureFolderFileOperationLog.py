"""Samsung Secure Folder (com.samsung.knox.securefolder): file operations in the SecureFolderDumpLog text files."""

__artifacts_v2__ = {
    "samsungSecureFolderFileOperationLog": {
        "name": "Samsung Secure Folder - File Operation Log",
        "description": (
            "File operation lines from the Secure Folder's SecureFolderDumpLog text files: the provider call, "
            "the paths named, the result message and the launch application, one row per logged line."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Knox Secure Folder",
        "notes": (
            "Read from the SecureFolderDumpLog_<kind><yyyymmddHHMMSS>.xml files in "
            "com.samsung.knox.securefolder/cache/dump/ of each Android user that has them. Despite "
            "the .xml name each file is plain text, one log line per line: month-day and time, three "
            "numbers, a level letter, the logging Android user in brackets, a tag and a message. Only "
            "lines tagged RemoteContentHistoryImpl are read, and of those only the lines whose "
            "message names a path (filePath, scannedPath or directoryPath), a provider call method "
            "other than dumpStart, a result message, a destination container, the launch application "
            "or a file operation result. Other tags in these files (application, provisioning, "
            "launcher, shortcut, backup and managed configuration history) are not reported. The same "
            "line is often written to more than one dump file; it is shown once, keyed on its time, "
            "the two process numbers, the logging user and the message. Log Time is the line's "
            "month-day and time as logged, with the year taken from the dump file's name, plus one "
            "when the line's month is earlier than the month in the name. No zone is recorded. "
            "Component and Function are the bracketed class name and the function name that start the "
            "message. Path is the text inside filePath[...], scannedPath[...] or directoryPath[...]. "
            "Detail is the text inside method[...], resultMessage[...], destContainerId[...], "
            "launchApplication[...] or fileOperationResult[...]. Message is the whole message as "
            "logged. Logging User is the number in brackets on the line. The app's code was not read "
            "(no Secure Folder APK is in the tested extraction), so what each function does is not "
            "established beyond its name and the known data below. Known data "
            "(samsung_a166u_a16_known_20261117, phone zone UTC-5 on that date): one file was moved "
            "from Android user 0's Download folder into the Secure Folder with My Files between "
            "14:59:49 and 15:00:46 UTC, per the session record. The logs held 12 such lines from "
            "10:00:32.767 to 10:00:36.545, which agrees with phone local time: a MoveToSecureFolder "
            "call logged by user 150, three calls logged by user 0, a getLastModified line naming the "
            "file in the user 0 Download folder, an updateLastModified line and a scan line naming it "
            "in the user 150 Download folder, the result message 1 item moved., destination container "
            "150, the user 150 Download folder, launch application MyFiles and result SUCCESS. This "
            "is the only record found that names the file moved: the Secure Folder History Log "
            "artifact gives the folders and the count. A move out of the Secure Folder, a failed move "
            "and more than one file are not exercised. On the other tested images that hold dump "
            "files (anne_a15, falken_a326u_a13, s20fe_a13, samsung_a166u_a16_known_20261116, "
            "samsunga53_a14, samsungs20_a13, sharon_a13, sharon_a14) no line matched."
        ),
        "paths": ("*/com.samsung.knox.securefolder/cache/dump/SecureFolderDumpLog_*",),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "lock",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.samsung.knox.securefolder | 12 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.knox.securefolder | no file operation line | 0 rows",
            "anne_a15": "Android 15 | com.samsung.knox.securefolder | no file operation line | 0 rows",
            "sharon_a14": "Android 14 | com.samsung.knox.securefolder | no file operation line | 0 rows",
            "samsungs20_a13": "Android 13 | com.samsung.knox.securefolder | no file operation line | 0 rows",
            "samsunga53_a14": "Android 14 | com.samsung.knox.securefolder | no file operation line | 0 rows",
        },
    },
}

import os
import re

from scripts.ilapfuncs import artifact_processor, logfunc

_FILE_NAME = re.compile(r"SecureFolderDumpLog_[A-Za-z]+(\d{4})(\d{2})\d{8}\.xml$")
_LINE = re.compile(
    r"^(\d{2})-(\d{2}) (\d{2}:\d{2}:\d{2}\.\d{3}) (\d+) (\d+) (\d+) [VDIWEF] \[(\d+)\](\w+?): ?(.*)$")
_TAG = "RemoteContentHistoryImpl"
_HEAD = re.compile(r"^\[(\w+)\] ([\w:]+)")
_PATH = re.compile(r"\b(?:filePath|scannedPath|directoryPath)\[([^\]]*)\]")
_DETAIL = re.compile(
    r"\b(?:method|resultMessage|destContainerId|launchApplication|fileOperationResult)\[([^\]]*)\]")


def _year(line_month, file_year, file_month):
    return file_year + 1 if line_month < file_month else file_year


@artifact_processor
def samsungSecureFolderFileOperationLog(context):
    data_list = []
    source_paths = []
    seen = set()
    for file_found in sorted(str(f) for f in context.get_files_found()):
        name = file_found.replace("\\", "/").rsplit("/", 1)[-1]
        match = _FILE_NAME.search(name)
        if not match or not os.path.isfile(file_found):
            continue
        file_year, file_month = int(match.group(1)), int(match.group(2))
        try:
            with open(file_found, "r", encoding="utf-8", errors="replace") as handle:
                lines = handle.read().split("\n")
        except OSError as error:
            logfunc(f"Secure Folder dump log not read: {file_found}: {error}")
            continue
        found_here = False
        for line in lines:
            parsed = _LINE.match(line.rstrip("\r"))
            if not parsed or parsed.group(8) != _TAG:
                continue
            message = parsed.group(9)
            paths = _PATH.findall(message)
            details = _DETAIL.findall(message)
            if not paths and not details:
                continue
            if "method[dumpStart]" in message:
                continue
            key = (parsed.group(1), parsed.group(2), parsed.group(3), parsed.group(5), parsed.group(6),
                   parsed.group(7), message)
            if key in seen:
                found_here = True
                continue
            seen.add(key)
            found_here = True
            month = int(parsed.group(1))
            year = _year(month, file_year, file_month)
            head = _HEAD.match(message)
            data_list.append((
                f"{year}-{parsed.group(1)}-{parsed.group(2)} {parsed.group(3)}",
                parsed.group(7),
                head.group(1) if head else "",
                head.group(2).split("::")[0] if head else "",
                "; ".join(paths),
                "; ".join(details),
                message,
            ))
        if found_here:
            source_paths.append(file_found)
    data_list.sort(key=lambda row: row[0])
    data_headers = (
        "Log Time (as logged, year from file name)",
        "Logging User",
        "Component",
        "Function",
        "Path",
        "Detail",
        "Message",
    )
    return data_headers, data_list, "\n".join(source_paths)
