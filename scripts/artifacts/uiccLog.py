__artifacts_v2__ = {
    "get_uicc_log": {
        "name": "UICC Log (SIM Slot Events)",
        "description": "Rows of the uicclog table in the phone app's uicc_log.db: SIM state changes and card slot "
                       "status lines, with the slot, state, subscription id and card fields read out of the log "
                       "text. The text is also reported as stored.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Device Information",
        "notes": "One row per row of the uicclog table (_id, time, log) of each uicc_log.db found, read once per "
                 "Android user with the duplicate storage views of one file collapsed. Rows are listed in _id order; the stored times are not always in that order "
                 "(see below). On the tested devices, all Samsung, the file sat under com.android.phone; which component writes it was not established; no AOSP source for a file of this name was found, no documentation of it was found, and the line formats below are read from the "
                 "data, not from a source.\n"
                 "Log Time is the time column as stored. On the tested devices the column is declared as DEFAULT (datetime('now','localtime')), so a row written through that default holds the device local wall clock at write time, with no zone recorded in the file; the value is NOT converted to UTC here. On the two tested devices that also hold the "
                 "telephony traffic statistics database, the last log row falls 2 and 10 minutes before the "
                 "last traffic row if Log Time is read as UTC-4, and about 4 hours before it if read as UTC; "
                 "that is consistent with a local time but does not prove the zone, which can also have "
                 "changed over the months covered. Within bursts of rows written in the same second or the "
                 "same minute the stored times can run backwards (0 to 8 such steps per device, up to 72 "
                 "seconds); _id order is kept and the time is not corrected.\n"
                 "Line formats seen: 'SIM_STATE_CHANGED[n] STATE,null(s)', 'CardState[n]: CARDSTATE_x,"
                 "num_apps=a,SupportedMepMode=m,SlotPortMapping={physicalSlotIndex=p, portIndex=q}', "
                 "'SlotStatus: count=n{...}{...}' and 'switchSlots: [UiccSlotMapping (...), ...]'. Index is "
                 "the number in brackets. Subscription ID is the number in parentheses of a SIM_STATE_CHANGED "
                 "line, on the tested devices it was -1 on most ABSENT, NOT_READY and UNKNOWN lines and 0 or more on most READY and LOADED lines (a few "
                 "NOT_READY and UNKNOWN lines carry a non-negative id and one READY line carries -1); on all five tested "
                 "devices every non-negative value equals an _id of the siminfo table of the telephony "
                 "provider database (telephony.db) on the same device (see SIM Subscriptions Seen in UICC Log). "
                 "The SIM states seen on the tested devices (READY, LOADED, ABSENT, NOT_READY, UNKNOWN), and any other state token, card states, num_apps and MEP mode values are reported as stored and are not translated; what the null token before "
                 "the subscription id stands for is not known. Slot Layout shows the text after the 'SlotStatus:' or 'switchSlots:' label, outer whitespace trimmed; Raw Log holds the full line. Lines that match none of the formats are kept with Event set to Other and only Raw Log otherwise filled.\n"
                 "On the five tested devices the log carried no ICCID, IMSI or phone number: none of the 1,584 rows contains a run of seven or more digits. Which SIM a subscription id refers to "
                 "comes from telephony.db, see the second artifact. Row ids run from 1 on four devices and from 2001 on one, which is consistent with older rows having been removed there; treat the table as a log that can be trimmed; absence of "
                 "an event is not evidence it did not happen. A row records that the logging component wrote a "
                 "line; a SIM state is not by itself proof of who inserted or used a SIM.\n"
                 "Validation boundary: five Samsung devices (Android 16, One UI 8.5; S- and A-series "
                 "models) held uicc_log.db with 123, 223, 387, 423 and 428 rows; the file "
                 "was not present on the two older tested Samsung devices (Android 10 and Android 14), and no non-Samsung device holding the file was available (the corpus Pixel and emulator images, see below, do not hold it). Android users other than 0 were exercised only on a "
                 "constructed database. A file that is not SQLite or cannot be opened is logged and skipped; a truncated database yields the rows readable before the damage. Android User held one value (0) on every row of every tested device; it stays because an image can carry another Android user's copy of the file. No Android corpus image holds uicc_log.db (telephony.db is present on most); on samsunga53_a14, sharon_a14, anne_a15 and hc_pixel8pro_a16 the artifact ran without error and reports no rows, so the rows described here come only from the contributor's five Samsung Android 16 extractions.",
        "paths": ('*/com.android.phone/databases/uicc_log.db*',),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "smartphone",
        "sample_data": {
            "samsunga53_a14": "Android 14 | com.android.phone | 0 rows",
            "sharon_a14": "Android 14 | com.android.phone | 0 rows",
            "anne_a15": "Android 15 | com.android.phone | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.phone | 0 rows",
        },
    },
    "get_uicc_sim_history": {
        "name": "SIM Subscriptions Seen in UICC Log",
        "description": "One row per phone index and subscription id that appears in a SIM_STATE_CHANGED line of "
                       "uicc_log.db, with the first and last log time, the READY and LOADED line counts and the "
                       "matching siminfo row of telephony.db (display name, carrier name and id, ICCID, IMSI, number, embedded flag, slot index)",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Device Information",
        "notes": "Built from the SIM_STATE_CHANGED lines of uicc_log.db with a subscription id of 0 or more "
                 "(lines with -1 name no subscription and are left out; see UICC Log (SIM Slot Events) for every "
                 "line). First Seen and Last Seen are the smallest and largest stored Log Time among those lines "
                 "for the phone index and subscription id; the stored time is a device local time with no zone "
                 "(see the first artifact) and is not converted. READY Lines and LOADED Lines count the lines "
                 "with that state. They count log lines, not times a SIM was inserted.\n"
                 "The SIM details are the siminfo row whose _id equals the subscription id, read from the "
                 "telephony.db of the same Android user. ICC ID, IMSI and Phone Number are reported as stored; a NULL or empty value is shown blank. The join is by value: on all five tested devices every "
                 "non-negative subscription id in the log matched a siminfo _id (0 unmatched), and for the SIM "
                 "that was current at extraction the siminfo sim_id equalled the log's index, but the meaning of "
                 "the number in the log line is not documented anywhere that was found, so treat the join as an "
                 "observed match. a siminfo row may outlive the SIM it describes, and its display name and "
                 "carrier can have been edited after the log line was written, so the details describe the "
                 "database at extraction and not necessarily the SIM at First Seen. Where telephony.db is "
                 "missing or has no matching row the details are blank. Embedded (as stored) is siminfo's "
                 "is_embedded; this artifact does not say what that means for a given SIM.\n"
                 "A subscription seen only on LOADED/READY lines has a time span in the log, not proof of "
                 "continuous presence between First Seen and Last Seen, and nothing before the oldest retained "
                 "row. Validation boundary: five Samsung devices (Android 16, One UI 8.5), 1, 1, 1, 2 and 3 "
                 "subscriptions on the five devices; the same boundary as the first artifact applies. Android User held one value (0) on every row of every tested device and stays to attribute rows when an image carries a second user's copy. Carrier Name (as stored) had no value on the single row of three tested devices; on other rows it held the text No service or (Searching), so it appears to be a status text and is reported as stored. On one device Index and Embedded (as stored) were the same value on both rows; that is a coincidence of which SIM sat in which index there, not a derivation. No Android corpus image holds uicc_log.db (telephony.db is present on most); on samsunga53_a14, sharon_a14, anne_a15 and hc_pixel8pro_a16 the artifact ran without error and reports no rows, so the rows described here come only from the contributor's five Samsung Android 16 extractions.",
        "paths": ('*/com.android.phone/databases/uicc_log.db*',
                  '*/com.android.providers.telephony/databases/telephony.db*'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "smartphone",
        "sample_data": {
            "samsunga53_a14": "Android 14 | com.android.phone | 0 rows",
            "sharon_a14": "Android 14 | com.android.phone | 0 rows",
            "anne_a15": "Android 15 | com.android.phone | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.phone | 0 rows",
        },
    },
}

import os
import re
import sqlite3

from scripts.artifacts.storagePathViews import android_user, unique_files
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, logfunc, null_absent_columns

SIM_STATE = re.compile(r'SIM_STATE_CHANGED\[(-?\d+)\] (\S+?),(\S*?)\((-?\d+)\)\s*$')
CARD_STATE = re.compile(r'CardState\[(-?\d+)\]: (\S+?),num_apps=(-?\d+),SupportedMepMode=(\S+?),'
                        r'SlotPortMapping=\{physicalSlotIndex=(-?\d+), portIndex=(-?\d+)\}\s*$')

UICC_QUERY = 'SELECT _id, time, log FROM uicclog ORDER BY _id'

SIMINFO_QUERY = '''
SELECT _id, display_name, carrier_name, carrier_id, icc_id, imsi, number, is_embedded, sim_id
FROM siminfo
'''


def _is_sidecar(path):
    return str(path).endswith(('-wal', '-shm', '-journal'))


def _base(path):
    return os.path.basename(str(path).replace('\\', '/'))


def _uicc_files(context):
    """[(path, Android user)] of the uicc_log.db files, one per user and storage class."""
    found = []
    for path in unique_files(context):
        if _base(path) == 'uicc_log.db':
            found.append((str(path), android_user(context.get_relative_path(path))))
    return found


def parse_uicc_line(text):
    """(event, index, state, sub id, apps, mep mode, physical slot, port, layout) for a log line.

    Fields a line does not carry are ''. A line matching no known format returns the event
    'Other' and nothing else, so the caller keeps it through its raw text.
    """
    text = '' if text is None else str(text)
    match = SIM_STATE.match(text)
    if match:
        return ('SIM_STATE_CHANGED', int(match.group(1)), match.group(2), int(match.group(4)),
                '', '', '', '', '')
    match = CARD_STATE.match(text)
    if match:
        return ('CardState', int(match.group(1)), match.group(2), '', int(match.group(3)), match.group(4),
                int(match.group(5)), int(match.group(6)), '')
    if text.startswith('SlotStatus:'):
        return ('SlotStatus', '', '', '', '', '', '', '', text[len('SlotStatus:'):].strip())
    if text.startswith('switchSlots:'):
        return ('switchSlots', '', '', '', '', '', '', '', text[len('switchSlots:'):].strip())
    return ('Other', '', '', '', '', '', '', '', '')


def _read_uicc_rows(path):
    """All (_id, time, log) rows of a uicc_log.db, or [] when it cannot be read."""
    try:
        return list(get_sqlite_db_records(path, UICC_QUERY))
    except sqlite3.DatabaseError as ex:
        logfunc(f'Could not read {os.path.basename(str(path))}: {ex}')
        return []


@artifact_processor
def get_uicc_log(context):
    data_headers = ('Log Time (device local time, as stored)', 'Log ID', 'Event', 'Index', 'State',
                    'Subscription ID', 'num_apps (as stored)', 'Supported MEP Mode (as stored)',
                    'Physical Slot Index', 'Port Index', 'Slot Layout', 'Raw Log', 'Android User')
    data_list = []
    sources = []
    for path, user in _uicc_files(context):
        sources.append(path)
        for row in _read_uicc_rows(path):
            event, index, state, sub_id, apps, mep, physical, port, layout = parse_uicc_line(row[2])
            data_list.append((row[1], row[0], event, index, state, sub_id, apps, mep, physical, port,
                              layout, row[2], user))
    return data_headers, data_list, '\n'.join(sources)


def _siminfo_for(context):
    """({Android user: {siminfo _id: row}}, [telephony.db paths read]) from every telephony.db found."""
    result = {}
    paths = []
    for path in unique_files(context):
        if _base(path) != 'telephony.db':
            continue
        user = android_user(context.get_relative_path(path))
        paths.append(str(path))
        rows = {}
        try:
            for row in get_sqlite_db_records(path, null_absent_columns(path, SIMINFO_QUERY)):
                rows[row[0]] = row
        except sqlite3.DatabaseError as ex:
            logfunc(f'Could not read {os.path.basename(str(path))}: {ex}')
        result[user] = rows
    return result, paths


@artifact_processor
def get_uicc_sim_history(context):
    data_headers = ('First Seen (device local time, as stored)', 'Last Seen (device local time, as stored)',
                    'Index', 'Subscription ID', 'READY Lines', 'LOADED Lines', 'Display Name',
                    'Carrier Name (as stored)', 'Carrier ID', 'ICC ID', 'IMSI', 'Phone Number (as stored)',
                    'Embedded (as stored)', 'Slot Index in siminfo (as stored)', 'Android User')
    siminfo, sim_sources = _siminfo_for(context)
    groups = {}
    sources = []
    for path, user in _uicc_files(context):
        sources.append(path)
        for row in _read_uicc_rows(path):
            event, index, state, sub_id = parse_uicc_line(row[2])[:4]
            if event != 'SIM_STATE_CHANGED' or sub_id < 0:
                continue
            group = groups.setdefault((user, index, sub_id), {'first': None, 'last': None, 'READY': 0, 'LOADED': 0})
            stamp = '' if row[1] is None else str(row[1])
            if stamp:
                group['first'] = stamp if group['first'] is None else min(group['first'], stamp)
                group['last'] = stamp if group['last'] is None else max(group['last'], stamp)
            if state in ('READY', 'LOADED'):
                group[state] += 1
    data_list = []
    for (user, index, sub_id), group in sorted(groups.items(), key=lambda item: (item[1]['first'] or '', item[0])):
        sim = siminfo.get(user, {}).get(sub_id)
        details = tuple('' if value is None else value for value in sim[1:]) if sim else ('',) * 8
        data_list.append((group['first'], group['last'], index, sub_id, group['READY'], group['LOADED'])
                         + details + (user,))
    return data_headers, data_list, '\n'.join(sources + sim_sources)
