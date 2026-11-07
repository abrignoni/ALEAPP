__artifacts_v2__ = {
    "get_telephony_trafficstats": {
        "name": "Telephony Network Lookups (trafficstats)",
        "description": "Rows of the trafficstats table in the phone app's echolocate_system_network_db: a timestamp (13-digit millisecond values on the tested devices), a cell id, signal reading, technology and band, and for "
                       "each row a DNS lookup type, the address items text (32 hexadecimal digits per item on the tested devices, not IP addresses), response time and response code",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Network Usage",
        "notes": "One row per row of the trafficstats table of each echolocate_system_network_db found (on the tested devices the database sat in the phone app's device encrypted storage; one copy per Android user, the "
                 "duplicate storage views of one file collapsed). Columns are read by name because the "
                 "networkDetail column is the fifth column in one tested build and the last in another. Rows "
                 "are listed in _id order.\n"
                 "Timestamp is the timeStamp text read as a Unix timestamp whose unit is taken from its magnitude (13 digits, read as milliseconds, on every row of the two tested devices) and shown in UTC. A value that is not a positive whole number is left blank and logged; Cell ID, RSRP, Technology, Network Detail, Band, Transaction ID, DNS Type, Response "
                 "Time, Response Code and Consumed are reported as stored and are not translated. Cell ID is "
                 "the cellId integer as stored; no location is derived from it. Address Items lists the "
                 "items of the stored IPAddress text, which on the tested devices has the form '[ip : a, ip : b]', without the "
                 "brackets and 'ip :' labels; text that does not match that form is shown unchanged. Despite the "
                 "column name, every item on every row of both tested devices is 32 hexadecimal digits, for A, "
                 "AAAA and failed (-1) lookups alike (70,878 and 49,676 items), never a dotted or colon "
                 "separated address, so the items are not readable as IP addresses; whether they are digests "
                 "of an address or of a name, and of what, is not known, and they are reported as stored. In both tested schemas the table holds no host name, no byte count and no SIM or "
                 "subscription column: Consumed was the text 0 on every row of both tested devices, so this "
                 "artifact does not show data volume per network or SIM, and nothing in the table ties a row to a particular SIM.\n"
                 "What the file is: the component that writes it is not documented in any source found. The file "
                 "was present on the two tested devices that had a T-Mobile 'echolocate' application installed "
                 "and absent from the five that did not (one of them lists permissions for that application "
                 "but holds no such database), so it may be specific to builds carrying that application; "
                 "whether other carriers' builds or other vendors write it was not tested.\n"
                 "Observations on the two tested devices, not general rules: DNS Type was A or AAAA on every row "
                 "with Response Code 0 and -1 on every row with another code, so the type appears to be "
                 "unrecorded for failed lookups; the response codes seen were 0, 2, 4, 7, 11 and 255 and the "
                 "transaction ids 0, 52 and values from 100 to 116, none of which is documented here. Technology -1 with a "
                 "colon-separated six byte hexadecimal value in Network Detail occurred on 495 rows of one "
                 "device and has the shape of a MAC address; what it identifies was not verified. "
                 "Technology -2 with Network Detail -2 and band -1 occurred on 2,277 and 1,787 rows (cell id "
                 "-2 on 2,283 and 1,787 rows), with RSRP between -999 and -80 on them; -999 was stored on "
                 "2,056 and 1,437 rows, 2 of which on the first device were NR rows. Technology and Network "
                 "Detail pairs seen were NR with SA, LTE with LTE or NSA, -2 with -2, and -1 with the colon-separated value above. The table appears to be a rolling window: row ids start at 1 "
                 "on one device (14,442 rows spanning 79 days, on 26 distinct days) and at 2,208,874 on the other, whose sqlite_sequence "
                 "is 2,220,249 (11,376 rows spanning 56 days, on 27 distinct days), so older rows were removed on that one; absence of "
                 "a day or a cell is not evidence the device was elsewhere or idle. One row on that device is "
                 "out of timestamp order against its _id.\n"
                 "Timeline output is deliberately off: the table produced hundreds of timestamped rows per active day on the tested devices. Validation boundary: two Samsung devices (Android 16, One UI 8.5, SIMs of T-Mobile brands), "
                 "14,442 and 11,376 rows; no Pixel or other vendor build holding the file and no Android version other than 16 was available (the corpus Pixel and emulator images do not hold it), so the schema is verified for two variants only (with "
                 "networkDetail fifth and NOT NULL, and with networkDetail last and nullable, both "
                 "user_version 2). A file that is not SQLite or cannot be opened is logged and skipped; a truncated database yields the rows readable before the damage. Android User held one value (0) on every row of both tested devices and stays because an image can carry another Android user's copy. No Android corpus image holds echolocate_system_network_db; on samsunga53_a14, sharon_a14, anne_a15 and hc_pixel8pro_a16 the artifact ran without error and reports no rows, so the rows described here come only from the contributor's Samsung Android 16 extractions.",
        "paths": ('*/com.android.phone/databases/echolocate_system_network_db*',),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "radio",
        "sample_data": {
            "samsunga53_a14": "Android 14 | com.android.phone | 0 rows",
            "sharon_a14": "Android 14 | com.android.phone | 0 rows",
            "anne_a15": "Android 15 | com.android.phone | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.phone | 0 rows",
        },
    },
    "get_telephony_cell_summary": {
        "name": "Telephony Network Lookups, Cells Seen",
        "description": "One row per cell id, technology, network detail and band in the trafficstats table of "
                       "echolocate_system_network_db, with the first and last timestamp, the row count and the lowest and highest signal reading other than -999",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Network Usage",
        "notes": "A grouping of the rows reported by Telephony Network Lookups (trafficstats), per Android user, "
                 "by the stored cellId, techType, networkDetail and bandNumber. First Seen and Last Seen are "
                 "the earliest and latest stored timestamp in UTC; Rows is the number of table rows (read here as one logged lookup each), not a count of connections or of data. RSRP Min and RSRP Max are "
                 "the lowest and highest stored value among the rows of the group other than -999 (a value "
                 "that stands apart from the dBm-like readings in the tested data; the meaning of -999 is not "
                 "documented) and are blank when every row is -999. All values are as stored; no location, "
                 "operator or sector is derived from a cell id, and a cell id on its own does not say where the "
                 "device was. Rows with a timestamp that is not a positive whole number count toward Rows and not toward the dates. See "
                 "Telephony Network Lookups (trafficstats) for the file, the retention window and the "
                 "validation boundary (two Samsung devices, 75 and 25 distinct cell ids). Android User held one value (0) on every row of both tested devices and stays because an image can carry another Android user's copy. No Android corpus image holds echolocate_system_network_db; on samsunga53_a14, sharon_a14, anne_a15 and hc_pixel8pro_a16 the artifact ran without error and reports no rows, so the rows described here come only from the contributor's Samsung Android 16 extractions.",
        "paths": ('*/com.android.phone/databases/echolocate_system_network_db*',),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "radio",
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
from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records, logfunc, \
    null_absent_columns

TRAFFIC_QUERY = '''
SELECT _id, cellId, rsrp, techType, networkDetail, bandNumber, timeStamp, transactionID, DNSType,
IPAddress, responseTime, responseCode, consumed
FROM trafficstats
ORDER BY _id
'''

ITEM = re.compile(r'ip\s*:\s*([^,\]\s]+)')


def _stamp(value):
    """The timeStamp text as a UTC datetime, or None when it is not a whole number."""
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        return None
    if number <= 0:
        return None
    try:
        return convert_unix_ts_to_utc(number)
    except (ValueError, OverflowError, OSError):
        return None


def parse_address_items(text):
    """The items of a stored '[ip : a, ip : b]' text joined by ', '; other text unchanged."""
    if text is None:
        return ''
    text = str(text)
    found = ITEM.findall(text)
    return ', '.join(found) if found else text


def _traffic_files(context):
    found = []
    for path in unique_files(context):
        if os.path.basename(str(path).replace('\\', '/')) == 'echolocate_system_network_db':
            found.append((str(path), android_user(context.get_relative_path(path))))
    return found


def _traffic_rows(path):
    try:
        return list(get_sqlite_db_records(path, null_absent_columns(path, TRAFFIC_QUERY)))
    except sqlite3.DatabaseError as ex:
        logfunc(f'Could not read {os.path.basename(str(path))}: {ex}')
        return []


@artifact_processor
def get_telephony_trafficstats(context):
    data_headers = (('Timestamp', 'datetime'), 'ID', 'Cell ID (as stored)', 'RSRP (as stored)',
                    'Technology (as stored)', 'Network Detail (as stored)', 'Band (as stored)',
                    'Transaction ID (as stored)', 'DNS Type (as stored)', 'Address Items',
                    'Response Time (as stored)', 'Response Code (as stored)', 'Consumed (as stored)',
                    'Android User')
    data_list = []
    sources = []
    for path, user in _traffic_files(context):
        sources.append(path)
        for row in _traffic_rows(path):
            stamp = _stamp(row[6])
            if stamp is None:
                logfunc(f'trafficstats row {row[0]} in {os.path.basename(path)} has a timeStamp that is not a positive whole number')
            data_list.append((stamp, row[0], row[1], row[2], row[3], row[4], row[5], row[7], row[8],
                              parse_address_items(row[9]), row[10], row[11], row[12], user))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def get_telephony_cell_summary(context):
    data_headers = (('First Seen', 'datetime'), ('Last Seen', 'datetime'), 'Cell ID (as stored)',
                    'Technology (as stored)', 'Network Detail (as stored)', 'Band (as stored)', 'Rows',
                    'RSRP Min (excluding -999)', 'RSRP Max (excluding -999)', 'Android User')
    groups = {}
    sources = []
    for path, user in _traffic_files(context):
        sources.append(path)
        for row in _traffic_rows(path):
            key = (user, row[1], row[3], row[4], row[5])
            group = groups.setdefault(key, {'first': None, 'last': None, 'rows': 0, 'min': None, 'max': None})
            group['rows'] += 1
            stamp = _stamp(row[6])
            if stamp is not None:
                group['first'] = stamp if group['first'] is None else min(group['first'], stamp)
                group['last'] = stamp if group['last'] is None else max(group['last'], stamp)
            try:
                rsrp = float(row[2])
            except (TypeError, ValueError):
                continue
            if rsrp != -999:
                group['min'] = rsrp if group['min'] is None else min(group['min'], rsrp)
                group['max'] = rsrp if group['max'] is None else max(group['max'], rsrp)
    data_list = []
    for key, group in sorted(groups.items(), key=lambda item: (item[1]['first'] is None, item[1]['first'], str(item[0]))):
        user, cell, tech, detail, band = key
        data_list.append((group['first'], group['last'], cell, tech, detail, band, group['rows'],
                          group['min'], group['max'], user))
    return data_headers, data_list, '\n'.join(sources)
