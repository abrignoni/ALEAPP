__artifacts_v2__ = {
    "samsungSecureFolderHistoryLog": {
        "name": "Samsung Secure Folder - History Log",
        "description": (
            "Parses the Samsung Secure Folder HistoryLog database "
            "(com.samsung.knox.securefolder, Android user 150) and reconstructs "
            "folder move-in/move-out activity between the personal profile "
            "(user 0) and the Secure Folder. Request/result records are paired "
            "into events that show direction, source app, requested vs. moved "
            "file counts, and the source/destination folder paths."
        ),
        "author": "4n6Wizard",
        "creation_date": "2026-06-30",
        "last_update_date": "2026-06-30",
        "requirements": "none",
        "category": "Knox Secure Folder",
        "notes": (
            "Ported from the Samsung Secure Folder History Log Parser by 4n6Wizard: "
            "https://github.com/4n6Wizard/Samsung-HistoryLog-Parser . "
            "Triage tool: it reports live HistoryLog records only and performs no "
            "carving or deleted-record recovery. The HistoryLog stores the folders "
            "and the number of files moved, NOT the individual file names. "
            "Timestamps are stored in the device's LOCAL time zone and are "
            "reported as recorded (no UTC conversion is applied)."
        ),
        "paths": (
            "*/com.samsung.knox.securefolder/databases/*",
        ),
        "output_types": "standard",
        "artifact_icon": "lock",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.knox.securefolder vc 192100000 | 0 rows",
            "galaxys10_a10": "Android 10 | com.samsung.knox.securefolder | 0 rows",
            "samsunga53_a14": "Android 14 | com.samsung.knox.securefolder | 0 rows",
            "samsungs20_a13": "Android 13 | com.samsung.knox.securefolder | 0 rows",
            "sharon_a14": "Android 14 | com.samsung.knox.securefolder vc 191200000 | 0 rows",
        },
    }
}

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from scripts.ilapfuncs import (
    artifact_processor,
    does_table_exist_in_db,
    get_sqlite_db_records,
    logfunc,
)

HISTORY_TABLE = "HistoryLog"
PATH_FIELD_NA = "N/A"
SOURCE_PATH_EXTRACTED_NOTE = "Source Path extracted from request message."
SOURCE_PATH_DERIVED_NOTE = (
    "Source Path derived from transferred path using source/destination profile IDs."
)
SOURCE_PATH_UNAVAILABLE_NOTE = "Source Path not available in HistoryLog data."
MAX_PAIR_SECONDS = 30 * 60

DIRECTION_RE = re.compile(r"\[(?P<src>\d+)\s*->\s*(?P<dst>\d+)\]")
REQUEST_RE = re.compile(
    r"\[\s*(?P<src>\d+)\s*->\s*(?P<dst>\d+)\s*\]\s*"
    r"\[(?P<app>[^\]\r\n]+)\]\s*"
    r"Count\s*:\s*(?P<count>\d+)\b",
    re.IGNORECASE,
)
COUNT_RE = re.compile(r"\bCount\s*:\s*(?P<count>\d+)\b", re.IGNORECASE)
TOTAL_RE = re.compile(r"\[\s*Total\s*:\s*(?P<total>\d+)\s*\]", re.IGNORECASE)
PATH_RE = re.compile(r"(?m)(/(?:storage/emulated|data|mnt)/[^\]\[\r\n\t\x00\"']*)")
LEADING_RESULT_COUNT_RE = re.compile(
    r"\]\s*\[\s*(?P<count>\d+)\b.*?\[\s*Total\s*:",
    re.IGNORECASE | re.DOTALL,
)
LEADING_BRACKET_COUNT_RE = re.compile(r"\]\s*\[\s*(?P<count>\d+)\b", re.DOTALL)


@dataclass
class Record:
    sequence: int
    raw_timestamp: str
    timestamp_sort: Optional[datetime]
    tag: str
    classification: str
    raw_direction: str = ""
    source_profile_id: Optional[int] = None
    destination_profile_id: Optional[int] = None
    source_app: str = ""
    requested_count: Optional[int] = None
    result_total_count: Optional[int] = None
    result_moved_count: Optional[int] = None
    paths: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class Event:
    event_id: int
    status: str
    request: Optional[Record] = None
    result: Optional[Record] = None
    unknown: Optional[Record] = None
    warnings: List[str] = field(default_factory=list)
    source_path: str = PATH_FIELD_NA
    transferred_path: str = PATH_FIELD_NA
    source_path_note: str = SOURCE_PATH_UNAVAILABLE_NOTE

    def primary_record(self):
        return self.request or self.result or self.unknown


def _int_or_none(value):
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _stringify(value):
    if value is None:
        return ""
    if isinstance(value, bytes):
        return "0x" + value.hex()
    return str(value)


def _parse_timestamp_for_sort(value):
    raw = _stringify(value).strip()
    if not raw:
        return None

    numeric_value = None
    if isinstance(value, (int, float)):
        numeric_value = float(value)
    elif re.fullmatch(r"\d{10}(\.\d+)?|\d{13}", raw):
        numeric_value = float(raw)

    if numeric_value is not None:
        seconds = numeric_value / 1000 if numeric_value > 10_000_000_000 else numeric_value
        try:
            dt = datetime(1970, 1, 1) + timedelta(seconds=seconds)
        except (OverflowError, OSError, ValueError):
            dt = None
        if dt and 2000 <= dt.year <= 2100:
            return dt

    try:
        dt = datetime.fromisoformat(raw)
        return dt if dt.tzinfo is None else None
    except ValueError:
        pass

    for fmt in (
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%m/%d/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
    ):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def _parse_record(sequence, raw_timestamp_value, tag_value, message_value):
    raw_timestamp = _stringify(raw_timestamp_value)
    tag = _stringify(tag_value)
    message = _stringify(message_value)

    warnings = []
    direction_match = DIRECTION_RE.search(message)
    raw_direction = ""
    source_profile_id = None
    destination_profile_id = None
    if direction_match:
        raw_direction = direction_match.group(0)
        source_profile_id = _int_or_none(direction_match.group("src"))
        destination_profile_id = _int_or_none(direction_match.group("dst"))

    # Request rows expose the requested item count via the structural
    # "Count : n" token after the direction/app brackets. Do not infer a
    # request count from arbitrary numbers; without a language-independent
    # fallback that would risk inventing evidence.
    request_match = REQUEST_RE.search(message)
    source_app = ""
    requested_count = None
    if request_match:
        source_app = request_match.group("app").strip()
        requested_count = _int_or_none(request_match.group("count"))
    else:
        count_match = COUNT_RE.search(message)
        if count_match:
            requested_count = _int_or_none(count_match.group("count"))

    total_match = TOTAL_RE.search(message)
    result_total_count = _int_or_none(total_match.group("total")) if total_match else None
    paths = [path.strip() for path in PATH_RE.findall(message) if path.strip()]

    result_moved_count = None
    moved_match = LEADING_RESULT_COUNT_RE.search(message)
    if moved_match:
        result_moved_count = _int_or_none(moved_match.group("count"))
    elif paths:
        moved_match = LEADING_BRACKET_COUNT_RE.search(message)
        if moved_match:
            result_moved_count = _int_or_none(moved_match.group("count"))

    classification = "unknown"
    if direction_match and request_match and requested_count is not None:
        classification = "request"
    elif direction_match and (result_total_count is not None or paths):
        classification = "result"
    else:
        if not direction_match:
            warnings.append("no direction pattern found")
        if direction_match and requested_count is None and result_total_count is None and not paths:
            warnings.append("direction found but no request/result structural pattern")
        if direction_match and requested_count is not None and not source_app:
            warnings.append("count found without source app bracket")

    if classification == "result" and result_moved_count is None and result_total_count is not None:
        result_moved_count = result_total_count

    return Record(
        sequence=sequence,
        raw_timestamp=raw_timestamp,
        timestamp_sort=_parse_timestamp_for_sort(raw_timestamp_value),
        tag=tag,
        classification=classification,
        raw_direction=raw_direction,
        source_profile_id=source_profile_id,
        destination_profile_id=destination_profile_id,
        source_app=source_app,
        requested_count=requested_count,
        result_total_count=result_total_count,
        result_moved_count=result_moved_count,
        paths=paths,
        warnings=warnings,
    )


def _record_sort_key(record):
    if record.timestamp_sort is None:
        return (1, "", record.sequence)
    return (0, record.timestamp_sort.isoformat(), record.sequence)


def _event_sort_key(event):
    record = event.primary_record()
    if record is None or record.timestamp_sort is None:
        return (1, "", record.sequence if record else 0)
    return (0, record.timestamp_sort.isoformat(), record.sequence)


def _seconds_between(left, right):
    if left.timestamp_sort is None or right.timestamp_sort is None:
        return None
    return (right.timestamp_sort - left.timestamp_sort).total_seconds()


def _pairing_score(request, result):
    if request.raw_direction != result.raw_direction:
        return None
    delta = _seconds_between(request, result)
    if delta is not None:
        if delta < 0 or delta > MAX_PAIR_SECONDS:
            return None
        score = max(0.0, MAX_PAIR_SECONDS - delta)
    else:
        if result.sequence < request.sequence:
            return None
        score = 1.0

    if request.requested_count is not None and result.result_total_count is not None:
        if request.requested_count == result.result_total_count:
            score += 500
        else:
            score -= min(200, abs(request.requested_count - result.result_total_count) * 5)
    if request.requested_count is not None and result.result_moved_count is not None:
        if request.requested_count == result.result_moved_count:
            score += 200
    score -= max(0, result.sequence - request.sequence) * 0.01
    return score


def _pair_records(records):
    sorted_records = sorted(records, key=_record_sort_key)
    events = []
    pending_requests = []
    event_id = 1

    for record in sorted_records:
        if record.classification == "request":
            pending_requests.append(record)
            continue

        if record.classification == "result":
            best_index = None
            best_score = None
            for index, request in enumerate(pending_requests):
                score = _pairing_score(request, record)
                if score is None:
                    continue
                if best_score is None or score > best_score:
                    best_index = index
                    best_score = score
            if best_index is not None:
                request = pending_requests.pop(best_index)
                events.append(Event(event_id=event_id, status="paired", request=request, result=record))
            else:
                events.append(Event(
                    event_id=event_id,
                    status="unpaired_result",
                    result=record,
                    warnings=["no prior matching request record found"],
                ))
            event_id += 1
            continue

        events.append(Event(
            event_id=event_id,
            status="unknown",
            unknown=record,
            warnings=record.warnings or ["record did not match request/result patterns"],
        ))
        event_id += 1

    for request in pending_requests:
        events.append(Event(
            event_id=event_id,
            status="unpaired_request",
            request=request,
            warnings=["no later matching result record found"],
        ))
        event_id += 1

    events.sort(key=_event_sort_key)
    for index, event in enumerate(events, start=1):
        event.event_id = index
    return events


def _event_result_paths(event):
    return list(event.result.paths) if event.result else []


def _derive_source_paths_from_transferred_path(event):
    record = event.primary_record()
    if record is None or record.source_profile_id is None or record.destination_profile_id is None:
        return []
    destination_prefix = f"/storage/emulated/{record.destination_profile_id}/"
    source_prefix = f"/storage/emulated/{record.source_profile_id}/"
    derived_paths = []
    for transferred_path in _event_result_paths(event):
        if transferred_path.startswith(destination_prefix):
            derived_paths.append(source_prefix + transferred_path[len(destination_prefix):])
    return derived_paths


def _path_field_value(paths):
    return "\n".join(paths) if paths else PATH_FIELD_NA


def _assign_event_path_fields(events):
    for event in events:
        request_paths = list(event.request.paths) if event.request else []
        event.transferred_path = _path_field_value(_event_result_paths(event))

        if request_paths:
            event.source_path = _path_field_value(request_paths)
            event.source_path_note = SOURCE_PATH_EXTRACTED_NOTE
            continue

        derived_paths = _derive_source_paths_from_transferred_path(event)
        if derived_paths:
            event.source_path = _path_field_value(derived_paths)
            event.source_path_note = SOURCE_PATH_DERIVED_NOTE
            continue

        event.source_path = PATH_FIELD_NA
        event.source_path_note = SOURCE_PATH_UNAVAILABLE_NOTE


def _event_duration(event):
    if not event.request or not event.result:
        return PATH_FIELD_NA
    delta = _seconds_between(event.request, event.result)
    if delta is None or delta < 0:
        return PATH_FIELD_NA
    if delta < 1:
        return "<1 sec"
    rounded = int(round(delta))
    if rounded < 60:
        return f"{rounded} sec"
    minutes, remaining_seconds = divmod(rounded, 60)
    return f"{minutes} min {remaining_seconds} sec"


def _event_warnings(event):
    warnings = list(event.warnings)
    for record in (event.request, event.result, event.unknown):
        if record:
            warnings.extend(record.warnings)
    return list(dict.fromkeys(warnings))


def _direction_summary(record):
    if record.source_profile_id is not None and record.destination_profile_id is not None:
        return f"{record.source_profile_id} → {record.destination_profile_id}"
    return record.raw_direction or PATH_FIELD_NA


def _count_value(value):
    return str(value) if value is not None else PATH_FIELD_NA


def _event_to_row(event, source_db):
    request = event.request
    result = event.result
    primary = event.primary_record()

    status_text = "Paired Event"
    status_note = PATH_FIELD_NA
    if event.status == "unpaired_request":
        status_text = "Unpaired Request"
        status_note = "A request record was found, but no matching result record was identified."
    elif event.status == "unpaired_result":
        status_text = "Unpaired Result"
        status_note = "A result record was found, but no matching request record was identified."
    elif event.status == "unknown":
        status_text = "Unknown Event"
        status_note = "This record did not match the expected request/result structure."

    return (
        event.event_id,
        status_text,
        status_note,
        request.raw_timestamp if request else "",
        result.raw_timestamp if result else "",
        _event_duration(event),
        request.source_app if request and request.source_app else PATH_FIELD_NA,
        primary.raw_direction or _direction_summary(primary),
        _count_value(request.requested_count if request else None),
        _count_value(result.result_moved_count if result else None),
        event.source_path or PATH_FIELD_NA,
        event.transferred_path or PATH_FIELD_NA,
        event.source_path_note,
        "; ".join(_event_warnings(event)) or PATH_FIELD_NA,
        source_db,
    )


@artifact_processor
def samsungSecureFolderHistoryLog(context):
    data_headers = (
        "Event",
        "Status",
        "Status Note",
        # Local device time, reported verbatim. Plain text (not 'datetime') so
        # LAVA stores it as-is and does not offer a time-zone offset that would
        # wrongly shift these local timestamps.
        "Request Time",
        "Result Time",
        "Duration",
        "Source App",
        "Direction",
        "Requested Count",
        "Moved Count",
        "Source Path",
        "Transferred Path",
        "Source Path Note",
        "Warnings",
        "Source DB",
    )

    query = f"SELECT timestamp, tag, message FROM {HISTORY_TABLE} ORDER BY id"
    data_list = []
    source_path = ""

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not does_table_exist_in_db(file_found, HISTORY_TABLE):
            continue

        db_records = get_sqlite_db_records(file_found, query)
        if not db_records:
            continue

        source_path = context.get_relative_path(file_found)
        records = [
            _parse_record(sequence, row[0], row[1], row[2])
            for sequence, row in enumerate(db_records, start=1)
        ]
        events = _pair_records(records)
        _assign_event_path_fields(events)
        for event in events:
            data_list.append(_event_to_row(event, source_path))

        logfunc(
            f"Samsung Secure Folder HistoryLog: {len(events)} event(s) "
            f"from {len(records)} record(s) in {source_path}"
        )

    return data_headers, data_list, source_path
