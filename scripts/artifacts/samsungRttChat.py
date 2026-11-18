"""Samsung Phone real-time text (RTT) call transcripts.

Samsung's in-call UI (com.samsung.android.incallui) keeps the text typed during an RTT call
in rtt_chat_history_db.db under the package's device-encrypted storage (user_de).
"""

__artifacts_v2__ = {
    "get_samsung_rtt_chat": {
        "name": "Samsung Phone - RTT Call Text",
        "description": (
            "Parses the text lines exchanged during real-time text (RTT) calls from the Samsung "
            "in-call UI database rtt_chat_history_db.db, one row per stored line, with the time "
            "of the line, whether it was typed on this device, the call it belongs to and, where "
            "the Samsung call log of the same Android user holds exactly one call with the same "
            "start time, that call's number, name, type and duration."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Call Logs",
        "notes": (
            "Read from com.samsung.android.incallui/databases/rtt_chat_history_db.db. The "
            "table history holds one row per line (history_id, history_is_me, history_msg, "
            "history_time, log_history_time). The table logs (log_id, log_time) held one "
            "row for the one RTT call in the known data. "
            "The tables were only readable with the -wal beside the database on "
            "samsung_a166u_a16_known_20261117 (without it the file held no history or logs "
            "table), so the paths take the sidecars. "
            "Meanings observed on known data (samsung_a166u_a16_known_20261117: one "
            "outgoing call to a second test phone, RTT turned on by the other phone during "
            "the call, two lines typed on each side, typing times logged on the phone that "
            "typed them): history_time is the line's time in milliseconds since the Unix "
            "epoch, stored as text, and matched the logged typing times to within one "
            "second on all four lines (whether it marks the first character or the end of "
            "the line is not established); history_is_me was 1 on the two lines typed on "
            "this phone and 0 on the two typed on the other phone, shown as Typed On This "
            "Device Yes or No, and any other stored value is shown as stored; "
            "log_history_time and log_time both equalled the call's start time in the call "
            "log to the millisecond (the dial time, not the moment RTT was turned on). "
            "Line Time is history_time and Call Start is log_history_time, both converted "
            "to UTC and cut to the whole second. "
            "Message is history_msg with trailing carriage returns and line feeds removed: "
            "on the known data the lines typed on this phone ended in CR LF and the "
            "received lines did not. The module changes nothing else in the text. "
            "Number, Name, Call Type and Call Duration (sec) come from the Samsung contacts "
            "provider's calllog.db: a call log row is used only when its date equals the "
            "RTT row's log_history_time exactly, its calllog.db sits in the same Android "
            "user's storage, and it is the only such row; when two or more different rows "
            "share that time the columns are left blank. The Android user comes from the "
            "path (user_de/N, user/N and data_mirror/data_de or data_ce/<volume>/N give "
            "user N, data/data gives user 0). Copies of one storage area read under more "
            "than one of these spellings are reported once. "
            "When Number, Name, Call Type and Call Duration (sec) are all blank, no single "
            "call log row with that start time was found for that user in the calllog.db "
            "files read; it does not show that the call had no number. When Call Type is "
            "filled and Number is blank, the call log row itself held no number. "
            "Call Type uses the AOSP CallLog.Calls codes 1 Incoming, 2 Outgoing, 3 Missed, "
            "4 Voicemail, 5 Rejected, 6 Blocked and 7 Answered Externally; any other value "
            "is shown as Unknown (N). Whether Samsung writes other values here is not "
            "established. "
            "Only the outgoing direction was exercised: an incoming RTT call, a call with "
            "RTT turned on by this phone, and a call whose call log row was deleted are not "
            "in the known data. Whether the app removes these rows when the call log entry "
            "is deleted is not established. The cross-user non-match, the several-rows "
            "blank and the Unknown (N) label are code paths no run exercised. "
            "The logs table is not reported on its own: on the known data its one row holds "
            "a row id and log_time, and log_time repeats the Call Start shown on every "
            "line. An RTT call with a logs row and no history rows would not appear in this "
            "report. "
            "On samsung_a166u_a16_known_20261117 the four lines belong to one call, so Call "
            "Start, Number, Name, Call Type, Call Duration (sec) and Android User held one "
            "value on all four rows. On the five other images run that hold "
            "rtt_chat_history_db.db (samsung_a166u_a16_known_20261116, anne_a15, "
            "cookbook_a11, falken_a326u_a13, samsunga53_a14) the history and logs tables "
            "are empty."
        ),
        "paths": (
            "*/com.samsung.android.incallui/databases/rtt_chat_history_db.db*",
            "*/com.samsung.android.providers.contacts/databases/calllog.db*",
        ),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.samsung.android.incallui | 4 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.incallui | empty history table | 0 rows",
            "anne_a15": "Android 15 | com.samsung.android.incallui | empty history table | 0 rows",
            "cookbook_a11": "Android 11 | com.samsung.android.incallui | empty history table | 0 rows",
            "falken_a326u_a13": "Android 13 | com.samsung.android.incallui | empty history table | 0 rows",
            "samsunga53_a14": "Android 14 | com.samsung.android.incallui | empty history table | 0 rows",
            "adams_ss135dl_a13": "Android 13 | no rtt_chat_history_db.db | 0 rows",
            "galaxys10_a10": "Android 10 | no rtt_chat_history_db.db | 0 rows",
            "s20fe_a13": "Android 13 | no rtt_chat_history_db.db | 0 rows",
            "samsungs20_a13": "Android 13 | no rtt_chat_history_db.db | 0 rows",
            "sharon_a13": "Android 13 | no rtt_chat_history_db.db | 0 rows",
            "sharon_a14": "Android 14 | no rtt_chat_history_db.db | 0 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Call Start",
                "textColumn": "Message",
                "directionColumn": "Typed On This Device",
                "directionSentValue": "Yes",
                "timeColumn": "Line Time",
                "senderColumn": "Number",
                "sentMessageStaticLabel": "Local User",
            }
        },
    }
}

import re

from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc,
    does_table_exist_in_db,
    get_sqlite_db_records,
    is_sqlite_sidecar,
    logfunc,
)

RTT_PACKAGE = "com.samsung.android.incallui"
CALLLOG_PACKAGE = "com.samsung.android.providers.contacts"

CALL_TYPES = {
    1: "Incoming",
    2: "Outgoing",
    3: "Missed",
    4: "Voicemail",
    5: "Rejected",
    6: "Blocked",
    7: "Answered Externally",
}

_USER_RE = re.compile(r"/(?:user|user_de|data_mirror/data_(?:ce|de)/[^/]+)/(\d+)/")


def _android_user(path, package):
    """Android user id of the package container a path sits in, or None."""
    norm = str(path).replace("\\", "/")
    marker = f"/{package}/"
    idx = norm.find(marker)
    if idx < 0:
        return None
    head = norm[:idx + 1]
    match = None
    for match in _USER_RE.finditer(head):
        pass
    if match and head.endswith(f"/{match.group(1)}/"):
        return int(match.group(1))
    if head.endswith("/data/data/"):
        return 0
    return None


def _storage_area(path):
    """'de' for device-encrypted storage (user_de), 'ce' for /data/data and /data/user."""
    norm = str(path).replace("\\", "/")
    return "de" if ("/user_de/" in norm or "/data_mirror/data_de/" in norm) else "ce"


def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _calllog_index(files_found):
    """Map (android user, call start in ms) to the call log row(s) with that start time.

    Each entry carries the calllog.db path it came from, so the report names it as a source.
    """
    index = {}
    for path in files_found:
        path = str(path)
        if is_sqlite_sidecar(path) or not path.endswith("calllog.db"):
            continue
        if f"/{CALLLOG_PACKAGE}/" not in path.replace("\\", "/"):
            continue
        user = _android_user(path, CALLLOG_PACKAGE)
        if user is None or not does_table_exist_in_db(path, "calls"):
            continue
        rows = get_sqlite_db_records(path, "SELECT date, number, name, type, duration FROM calls")
        for date, number, name, call_type, duration in rows:
            key = (user, _to_int(date))
            entry = (number or "", name or "", call_type, duration, path)
            index.setdefault(key, [])
            if entry[:4] not in [e[:4] for e in index[key]]:
                index[key].append(entry)
    return index


@artifact_processor
def get_samsung_rtt_chat(context):
    files_found = context.get_files_found()
    calllog = _calllog_index(files_found)
    data_list = []
    source_paths = []
    seen = set()
    for path in files_found:
        path = str(path)
        if is_sqlite_sidecar(path) or not path.endswith("rtt_chat_history_db.db"):
            continue
        if f"/{RTT_PACKAGE}/" not in path.replace("\\", "/"):
            continue
        if not does_table_exist_in_db(path, "history"):
            logfunc(f"Samsung RTT: no history table in {path}")
            source_paths.append(path)
            continue
        user = _android_user(path, RTT_PACKAGE)
        source_paths.append(path)
        rows = get_sqlite_db_records(
            path,
            "SELECT history_id, history_is_me, history_msg, history_time, log_history_time "
            "FROM history ORDER BY log_history_time, CAST(history_time AS INTEGER), history_id",
        )
        area = _storage_area(path)
        for history_id, is_me, message, line_ms, call_ms in rows:
            row_key = (user, area, history_id, line_ms, call_ms, is_me, message)
            if row_key in seen:
                continue
            seen.add(row_key)
            line_ms_int = _to_int(line_ms)
            call_ms_int = _to_int(call_ms)
            line_time = convert_unix_ts_to_utc(line_ms_int) if line_ms_int else ""
            call_start = convert_unix_ts_to_utc(call_ms_int) if call_ms_int else ""
            if is_me == 1:
                typed_here = "Yes"
            elif is_me == 0:
                typed_here = "No"
            else:
                typed_here = "" if is_me is None else str(is_me)
            text = message.rstrip("\r\n") if isinstance(message, str) else message
            matches = calllog.get((user, call_ms_int), []) if user is not None else []
            if len(matches) == 1:
                number, name, call_type, duration, calllog_path = matches[0]
                source_paths.append(calllog_path)
                call_type_label = CALL_TYPES.get(call_type, f"Unknown ({call_type})") \
                    if call_type is not None else ""
            else:
                if len(matches) > 1:
                    logfunc(f"Samsung RTT: {len(matches)} call log rows share start time "
                            f"{call_ms_int}; number left blank")
                number = name = call_type_label = ""
                duration = ""
            data_list.append((
                line_time, call_start, typed_here, number, text, name, call_type_label,
                duration, history_id, "" if user is None else user,
            ))

    data_headers = (
        ("Line Time", "datetime"),
        ("Call Start", "datetime"),
        "Typed On This Device",
        ("Number", "phonenumber"),
        "Message",
        "Name",
        "Call Type",
        "Call Duration (sec)",
        "History ID",
        "Android User",
    )
    return data_headers, data_list, "\n".join(sorted(set(source_paths)))
