"""Samsung Secure Folder (com.samsung.knox.securefolder): file operations in the SecureFolderDumpLog text files."""

__artifacts_v2__ = {
    "samsungSecureFolderFileOperationLog": {
        "name": "Samsung Secure Folder - File Operation Log",
        "description": (
            "Selected lines from the Secure Folder's SecureFolderDumpLog text files: the "
            "provider call, the paths named, the result message, the destination container, the launch "
            "application and the operation result, one row per distinct logged line."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Cloud & Files",
        "notes": (
            "Read from the SecureFolderDumpLog_<kind><yyyymmddHHMMSS>.xml files in "
            "com.samsung.knox.securefolder/cache/dump/ of each Android user that has them. On the "
            "tested images each file is plain text despite the .xml name. Each entry starts on its "
            "own line with month-day and time, three numbers, a level letter, a number in brackets, a "
            "tag and a message; some messages continue on the following lines, and those continuation "
            "lines are not read. On every parsed line of the tested images the bracketed number "
            "equals the Android user whose folder holds the file. Only entries tagged "
            "RemoteContentHistoryImpl are read, and of those only the ones whose message names a path "
            "(filePath, scannedPath or directoryPath), a provider call method, a result message, a "
            "destination container, the launch application or a file operation result. Other tags "
            "seen in these files (ApplicationHistoryImpl, ProvisioningHistoryImpl, "
            "LauncherHistoryImpl, ShortcutHistoryImpl, BackupRestoreHistoryImpl) are not reported. On "
            "the known data every reported line was in two dump files of the same user, the "
            "RemoteContent file and an Application file. A line is shown once, keyed on its "
            "month-day, time, the second and third numbers, the bracketed number and the message. Log "
            "Time is the month-day and time as logged. The lines carry no year and no zone. Dump File "
            "Started is the date and time in the name of the dump file the row was read from. When a "
            "line is in two files, it is the file whose path sorts first (on the known data, the "
            "Application file). On every tested file the name equals the month-day and second of the "
            "file's first line. The name carries no zone. A dump file keeps being appended after it "
            "is named; on tested images the month of the lines goes backward inside a file (13 files "
            "on 5 images), as it does when a file spans a year change, so the name does not give the "
            "year of a line. Rows are ordered by Log Time, which can put lines from different years "
            "together. Component is the bracketed name that starts the message. Function is the text "
            "after it, up to the first opening parenthesis or space. Component and Function are blank "
            "when the message does not start with a bracketed name. Path is the text inside "
            "filePath[...], scannedPath[...] or directoryPath[...], up to the first closing bracket. "
            "Detail is the text inside method[...], resultMessage[...], destContainerId[...], "
            "launchApplication[...] or fileOperationResult[...]. Several values in one line are "
            "joined with a semicolon. Message is the first line of the message as logged. Logging "
            "User is the bracketed number. The column name comes from the match above, not from the "
            "app's code. The app's code was not read (no Secure Folder APK is in "
            "samsung_a166u_a16_known_20261117), so what each function does is not established beyond "
            "its name and the known data below. Known data (samsung_a166u_a16_known_20261117, phone "
            "zone UTC-5 on that date): one file was moved from Android user 0's Download folder into "
            "the Secure Folder with My Files between 14:59:49 and 15:00:46 UTC, per the session "
            "record. The logs held 12 such lines from 10:00:32.767 to 10:00:36.545, which agrees with "
            "phone local time: a MoveToSecureFolder call logged by user 150, three calls logged by "
            "user 0, a getLastModified line naming the file in the user 0 Download folder, an "
            "updateLastModified line and a scan line naming it in the user 150 Download folder, the "
            "result message 1 item moved., destination container 150, the user 150 Download folder, "
            "launch application MyFiles and result SUCCESS. On the known data this log named the file "
            "moved and the folder it came from. The user 150 MediaStore also holds a row for the file "
            "at its destination path (Emulated Storage Metadata artifacts), and the Samsung Secure "
            "Folder - History Log artifact gives the destination folder, a source folder it derives, "
            "and the count. A move out of the Secure Folder, a failed move, more than one file, a "
            "copy and a message that continues on a second line are not exercised. On the other "
            "tested images that hold dump files (anne_a15, falken_a326u_a13, s20fe_a13, "
            "samsung_a166u_a16_known_20261116, samsunga53_a14, samsungs20_a13, sharon_a13, "
            "sharon_a14) no line matched: seven hold no line with this tag, and samsungs20_a13 holds "
            "8 (4 distinct), none with a field this artifact reads."
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

_FILE_NAME = re.compile(r"SecureFolderDumpLog_[A-Za-z]+(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})\.xml$")
_LINE = re.compile(
    r"^(\d{2})-(\d{2}) (\d{2}:\d{2}:\d{2}\.\d{3}) (\d+) (\d+) (\d+) [VDIWEF] \[(\d+)\](\w+?): ?(.*)$")
_TAG = "RemoteContentHistoryImpl"
_HEAD = re.compile(r"^\[(\w+)\] ([^(\s]+)")
_PATH = re.compile(r"\b(?:filePath|scannedPath|directoryPath)\[([^\]]*)\]")
_DETAIL = re.compile(
    r"\b(?:method|resultMessage|destContainerId|launchApplication|fileOperationResult)\[([^\]]*)\]")


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
        started = "{}-{}-{} {}:{}:{}".format(*match.groups())
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
            key = (parsed.group(1), parsed.group(2), parsed.group(3), parsed.group(5), parsed.group(6),
                   parsed.group(7), message)
            if key in seen:
                found_here = True
                continue
            seen.add(key)
            found_here = True
            head = _HEAD.match(message)
            data_list.append((
                f"{parsed.group(1)}-{parsed.group(2)} {parsed.group(3)}",
                started,
                parsed.group(7),
                head.group(1) if head else "",
                head.group(2) if head else "",
                "; ".join(paths),
                "; ".join(details),
                message,
            ))
        if found_here:
            source_paths.append(file_found)
    data_list.sort(key=lambda row: (row[0], row[1]))
    data_headers = (
        "Log Time (month-day, as logged)",
        "Dump File Started",
        "Logging User",
        "Component",
        "Function",
        "Path",
        "Detail",
        "Message",
    )
    return data_headers, data_list, "\n".join(source_paths)
