__artifacts_v2__ = {
    "smartselect": {
        "name": "Android System Intelligence - Smart Select Fragments",
        "description": "Parses LinkFragmentEntity table containing smart text selection entities (OTP codes, phone numbers, email addresses and others) with surrounding context. Also lists rows that earlier committed states of the database hold (the database file read without its write-ahead log, and each commit in the log) and the current table does not.",
        "author": "@stark4n6, @AlexisBrignoni, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-11-11",
        "requirements": "none",
        "category": "Android System Intelligence",
        "notes": "Decodes serializedFragment protobuf blobs from LinkFragmentEntity. Field labels come from the shape of observed data, not from source. Record Origin: Live rows come from a normal read of the table. A Recovered row is an id that another state in smartselect_db-wal holds and the current LinkFragmentEntity table does not. An Earlier version row is an id the current table still holds whose serializedFragment or timestampMs differed in another state, one row per distinct version. Recovery Method and Recovery Location are filled in only on those rows. Why a row is absent from the current table is not established here. States are read by scripts/sqlite_wal.py: each readable committed state of the log's current generation (state n is the database after the first n committed transactions, state 0 the database file without its log; states the reader cannot rebuild exactly are skipped and counted in the run log), the previous generation's left-over frames where its checks pass, and frames after the last commit where SQLite's quick_check passes. Each row is reported as the newest state holding it stored it. Recovery Location names the committed states the row was read in, with their first and last numbers. Tested on six images: 77 Recovered rows on hc_pixel8pro_a16, hc_pixel8pro_a17, russell_pixel6a_a13 and russell_a14, all from committed states of the current generation (on russell_pixel6a_a13, 9 of them were first read in state 0, the database file without its log); pixel3_a12 and pixel7a_a14 gave no Recovered rows. No row on the six images was an Earlier version or came from the previous generation or from frames after the last commit, so those paths are present in the code and not exercised by corpus data.",
        "paths": (
            "*/com.google.android.as/databases/smartselect_db*",
        ),
        "output_types": "standard",
        "artifact_icon": "link",
    }
}

import json
import os
import sqlite3

from scripts.artifacts.storagePathViews import android_user, unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    decode_protobuf,
    get_sqlite_db_records,
    convert_ts_int_to_utc,
    logfunc,
)
from scripts.sqlite_wal import (
    KIND_COMMITTED,
    KIND_EARLIER,
    KIND_UNCOMMITTED,
    rows_not_in_current,
)

# Fixed typedef so field 5's fragments always decode as bytes. Without it the
# schema-less guesser reads an empty or digits-only fragment as a nested
# message and splits the rest into a "5-1" key, which shifts the positions.
FRAGMENT_TYPEDEF = {
    "4": {"type": "bytes"},
    "5": {
        "type": "message",
        "message_typedef": {"1": {"type": "bytes"}, "8": {"type": "int"}},
    },
    "6": {"type": "int"},
    "7": {"type": "int"},
    "12": {"type": "bytes"},
    "14": {"type": "int"},
    "15": {"type": "bytes"},
}

QUERY = """
    SELECT
        id,
        timestampMs,
        serializedFragment
    FROM LinkFragmentEntity
    ORDER BY timestampMs ASC;
"""

# id is LinkFragmentEntity's INTEGER PRIMARY KEY, so it is the key compared across states.
_KEY_INDEX = 0
_WAL_KINDS = (KIND_COMMITTED, KIND_EARLIER, KIND_UNCOMMITTED)
_ORIGIN_LIVE = "Live"
_ORIGIN_RECOVERED = "Recovered"
_ORIGIN_EARLIER = "Earlier version"
_METHOD_WAL_STATES = "WAL committed states"
_METHOD_WAL_UNCOMMITTED = "WAL uncommitted frames"


def _decode_bytes(val):
    if isinstance(val, bytes):
        return val.decode("utf-8", errors="replace")
    return str(val) if val is not None else ""


def parse_serialized_fragment(blob):
    """Decodes the serializedFragment protobuf BLOB using ilapfuncs.decode_protobuf."""
    if not blob:
        return "", "", "", "", "", "", "", ""

    try:
        msg, _ = decode_protobuf(blob, FRAGMENT_TYPEDEF)
    except Exception as e:
        return "", "", "", "", "", "", "", f"Error decoding protobuf: {e}"

    # Field 4: Entity Type (e.g., otp_code, phone, email, other)
    entity_type = _decode_bytes(msg.get("4", ""))

    # Field 5: Repeated sub-message containing text fragments (Field 1 inside Field 5)
    field_5 = msg.get("5", [])
    if isinstance(field_5, dict):
        field_5 = [field_5]

    fragments = [_decode_bytes(item.get("1", b"")) for item in field_5]

    pre_context = fragments[0] if len(fragments) > 0 else ""
    selected_text = (
        fragments[1]
        if len(fragments) > 1
        else (fragments[0] if len(fragments) == 1 else "")
    )
    post_context = fragments[2] if len(fragments) > 2 else ""
    full_text = "".join(fragments)

    # Field 12: Source Package (can hold package_not_in_allowlist instead of a name)
    source_pkg = _decode_bytes(msg.get("12", ""))

    # Field 15: Widget Type (e.g., notification, textview, edittext)
    widget_type = _decode_bytes(msg.get("15", ""))

    # Full JSON representation of the protobuf
    raw_json = json.dumps(msg, default=_decode_bytes, ensure_ascii=False)

    return (
        entity_type,
        selected_text,
        full_text,
        pre_context,
        post_context,
        source_pkg,
        widget_type,
        raw_json,
    )


def _recovery_location(name, spans):
    """(method, location) for a row read in the states spans names."""
    parts = []
    committed, earlier = spans["committed"], spans["earlier"]
    if committed:
        first, last = committed
        if last == 0:
            parts.append(f"{name} without its log, state 0")
        elif first == 0:
            parts.append(f"{name} and {name}-wal, committed states 0 to {last}")
        else:
            states = f"state {first}" if first == last else f"states {first} to {last}"
            parts.append(f"{name}-wal, committed {states}")
    if earlier:
        first, last = earlier
        commits = f"commit {first}" if first == last else f"commits {first} to {last}"
        parts.append(f"{name}-wal, previous log generation, left-over {commits}")
    if not parts:
        return _METHOD_WAL_UNCOMMITTED, f"{name}-wal, frames after the last commit"
    return _METHOD_WAL_STATES, "; ".join(parts)


def _rows_in_log(db_file, live_rows):
    """Rows of QUERY that another state in the write-ahead log holds and the current one
    does not, read through scripts/sqlite_wal.py.

    An id the current table does not hold is Recovered, one row per id as the newest state
    holding it stored it. An id the current table still holds, with a different
    timestampMs or serializedFragment, is an Earlier version, one row per distinct version.
    Returns [(row, origin, method, location)].
    """
    try:
        _columns, found, wal = rows_not_in_current(str(db_file), QUERY, include=_WAL_KINDS)
    except (sqlite3.Error, OSError) as ex:
        logfunc(f"Smart Select: write-ahead log not read for {db_file}: {ex}")
        return []
    if wal.log:
        logfunc(f"Smart Select: {wal.summary()}")
    live_ids = {row[_KEY_INDEX] for row in live_rows}
    entries = {}
    for item in found:
        rec_id = item.values[_KEY_INDEX]
        if rec_id in live_ids:
            slot, origin = (rec_id, item.values), _ORIGIN_EARLIER
        else:
            slot, origin = (rec_id,), _ORIGIN_RECOVERED
        rank = ((2, item.last_state) if item.first_state is not None else
                (1, item.earlier_generation[1]) if item.earlier_generation else (0, 0))
        entry = entries.setdefault(slot, {"row": item.values, "origin": origin, "rank": rank,
                                          "committed": None, "earlier": None})
        if rank > entry["rank"]:
            entry["row"], entry["rank"] = item.values, rank
        for part, span in (("committed", (item.first_state, item.last_state)
                            if item.first_state is not None else None),
                           ("earlier", item.earlier_generation)):
            if span:
                old = entry[part]
                entry[part] = span if old is None else (min(old[0], span[0]), max(old[1], span[1]))
    name = os.path.basename(str(db_file))
    return [(entry["row"], entry["origin"], *_recovery_location(name, entry))
            for entry in entries.values()]


@artifact_processor
def smartselect(context):
    data_list = []
    source_files = []

    # unique_files drops the data/data, data/user/0 and data_mirror views of one
    # file and keeps a second Android user's own copy.
    for file_found in unique_files(context):
        file_found = str(file_found)
        if file_found.endswith(("-wal", "-shm", "-journal")):
            continue

        user = android_user(context.get_relative_path(file_found))
        try:
            live_rows = list(get_sqlite_db_records(file_found, QUERY))
        except Exception as e:
            logfunc(f"Error reading LinkFragmentEntity from {file_found}: {e}")
            live_rows = []

        rows = [(row, _ORIGIN_LIVE, "", "") for row in live_rows]
        rows.extend(_rows_in_log(file_found, live_rows))

        for row, origin, method, location in rows:
            rec_id, ts_ms, blob = row[0], row[1], row[2]

            # Convert Epoch Milliseconds to UTC datetime
            timestamp = convert_ts_int_to_utc(ts_ms / 1000.0) if ts_ms else ""

            (
                entity_type,
                selected_text,
                full_text,
                pre_context,
                post_context,
                source_pkg,
                widget_type,
                raw_json,
            ) = parse_serialized_fragment(blob)

            data_list.append(
                (
                    timestamp,
                    user,
                    rec_id,
                    entity_type,
                    selected_text,
                    full_text,
                    pre_context,
                    post_context,
                    source_pkg,
                    widget_type,
                    origin,
                    method,
                    location,
                    raw_json,
                )
            )

        if rows:
            source_files.append(file_found)

    data_list.sort(key=lambda r: (str(r[0]), r[2]))
    source_path = "\n".join(source_files)

    data_headers = (
        ("Timestamp", "datetime"),
        "Android User",
        "ID",
        "Entity Type",
        "Target / Selected Text",
        "Reconstructed Full Text",
        "Pre-Context Fragment",
        "Post-Context Fragment",
        "Source Package",
        "Widget Type",
        "Record Origin",
        "Recovery Method",
        "Recovery Location",
        "Decoded Protobuf (JSON)",
    )

    return data_headers, data_list, source_path
