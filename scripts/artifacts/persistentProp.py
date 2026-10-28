__artifacts_v2__ = {
    "get_persistentProp": {
        "name": "Persistent Properties - Matched Text Observations",
        "description": "Reports the boot reason entries of persistent_properties (persist.sys.boot.reason.history and persist.sys.boot.reason): "
                       "read from the protobuf store when the file is one, otherwise text lines selected by the existing reboot-like "
                       "prefix rules. The last comma field is converted using the Unix-seconds rule when representable; raw text and "
                       "conversion status are retained.",
        "author": "@abrignoni, @AlexisBrignoni, Codex, @danjethh, Claude",
        "creation_date": "2021-08-18",
        "last_update_date": "2026-10-27",
        "requirements": "none",
        "category": "Wipe & Setup",
        "notes": "These are the platform's kept boot reason texts, not proof of a reboot, "
                 "wipe, event completion or ownership: an entry says that the platform kept that text at a start, not why the start "
                 "happened. Two readings share the columns. (1) When the file is a persistent property store (a protobuf file written by "
                 "init: a repeated record with the property name as field 1 and the value as field 2), it is decoded directly. One row "
                 "is written for each line of persist.sys.boot.reason.history and one for a non-empty persist.sys.boot.reason. Event is the "
                 "entry without its epoch, Raw Timestamp Text is the last number of a history entry, Timestamp is that number read as "
                 "seconds since the Unix epoch when it falls between 2009 and 2100 (this tool's reading) and blank otherwise, and Input Line "
                 "Ordinal is blank. Property, Reason (the text before the first comma), Subreason (the text between the first comma and "
                 "the epoch), Position (0 for the first entry stored; the newest first in the tested files) and factory_reset Reason "
                 "Present ('yes' when the text factory_reset appears anywhere in the entry, ignoring case, 'no' otherwise) are filled for "
                 "these rows only. 'no' says only that the stored entries do not contain the word: the history holds a few entries (2 to 3 "
                 "in the files tested), so an older reset is not expected in it. A file cut inside a record gives the records before "
                 "the cut and a log line. (2) A file that does not start with such a record, or a store with no boot reason entry, is read as text with the earlier rules: the "
                 "three independent selectors and the Unix-seconds assumption are retained, matched text is stripped UTF-8 "
                 "replacement-decoded text (not reversible original bytes), Input Line Ordinal follows text-loader iteration, not "
                 "chronology, and the columns added for the store reading are blank. The earlier reading used only (2) on every file and "
                 "gave no row on the two Android 16 files tested, where reading (1) gives 2 and 3. Invalid or unrepresentable timestamps retain a blank date and "
                 "their raw text. Source paths include actual contributors only; Source File is "
                 "added only when rows combine distinct evidence-relative origins.\n"
                 "Evidence tiers. Data-proven on two Samsung full file system extractions (Android 16): the history property held 2 and 3 "
                 "entries, each dated within 2 days before the date of the extraction, with the reasons 'reboot', 'reboot,userrequested' and "
                 "'reboot,device_locked_3days'; persist.sys.boot.reason was empty on both; no entry contains factory_reset. The counts "
                 "equal a count of the history lines read by a separate protobuf walk. Constructed only: a factory_reset entry, entries "
                 "without an epoch, text and out-of-range epochs, a cut file and a file that is not a store. The sample_data counts below "
                 "were taken with the text reading only and were not measured again. Not examined: Android before 16 with the store "
                 "reading, other vendors, and a store with another record layout.",
        "paths": ('*/property/persistent_properties',),
        "output_types": "standard",
        "artifact_icon": "info-circle",
        "sample_data": {
            "anne_a15": "Android 15 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 2 rows",
            "sharon_a14": "Android 14 | 1 row",
            "russell_pixel6a_a13": "Android 13 | 1 row",
            "userb2_a13": "Android 13 | 0 rows",
        },
    }
}

import datetime
import json

from scripts import android_boot_reason as boot
from scripts.ilapfuncs import artifact_processor, logfunc

MAX_FILE_BYTES = 16 * 1024 * 1024
STORE_COLUMNS = 5     # Property, Reason, Subreason, Position, factory_reset Reason Present


def _matched_observation(raw, description, clean, ordinal, relative, branch):
    try:
        timestamp = datetime.datetime.fromtimestamp(int(raw), datetime.timezone.utc)
        status = 'Converted by existing Unix-seconds rule'
    except (ValueError, OverflowError, OSError) as error:
        timestamp = ''
        status = f'Not converted ({type(error).__name__})'
        source = json.dumps(relative[:240], ensure_ascii=True)
        if len(relative) > 240:
            source += ' [truncated]'
        logfunc(f'Persistent properties: timestamp not converted at {source}; input line ordinal {ordinal}; branch {branch} ({type(error).__name__})')
    return timestamp, raw, description, status, ordinal, clean


def _read_store(file_found, relative):
    """The boot reason rows of a file that is a persistent property store, or None when it is not one."""
    try:
        with open(file_found, 'rb') as handle:
            data = handle.read(MAX_FILE_BYTES)
    except OSError as error:
        logfunc(f'Persistent properties: {relative} could not be read: {error}')
        return None
    if not data:
        return None
    try:
        records, warning = boot.read_persistent_properties(data)
    except boot.StoreError:
        return None
    if warning:
        logfunc(f'Persistent properties: {relative}: {warning}')
    rows = []
    for item in boot.rows_from_records(records):
        status = ('Converted by Unix-seconds rule (2009 to 2100)' if item.moment else
                  'Not converted (no epoch, or outside 2009 to 2100)' if item.epoch_text else 'No epoch in the entry')
        event = item.entry[:-len(item.epoch_text)].rstrip(', ') if item.epoch_text and item.entry.endswith(item.epoch_text) else item.entry
        rows.append((item.moment if item.moment else '', item.epoch_text, event, status, '', item.entry,
                     item.property, item.reason, item.subreason, item.position, 'yes' if item.factory_reset else 'no'))
    return rows


@artifact_processor
def get_persistentProp(context):
    files_found = context.get_files_found()

    data_list = []
    contributors = []
    origins = []
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('persistent_properties'):
            continue  # Skip all other files

        relative = context.get_relative_path(file_found)
        first_row = len(data_list)
        store_rows = _read_store(file_found, relative)
        if store_rows:
            data_list.extend(store_rows)
        else:
            with open(file_found, 'r', encoding='utf-8', errors='replace') as f:
                for ordinal, line in enumerate(f, 1):
                    clean = line.strip()
                    if clean.startswith('persist.sys.boot.reason.historyDreboot'):
                        parts = clean.split(',')
                        description = parts[0]
                        data_list.append(_matched_observation(parts[-1], description, clean, ordinal, relative, 'history') + ('',) * STORE_COLUMNS)

                    if clean.startswith('reboot,factory_reset,'):
                        parts = clean.split(',')
                        description = parts[0] + ' ' + parts[1]
                        data_list.append(_matched_observation(parts[-1], description, clean, ordinal, relative, 'factory-reset') + ('',) * STORE_COLUMNS)

                    if clean.startswith('reboot'):
                        parts = clean.split(',')
                        if len(parts) == 2:
                            description = parts[0]
                            data_list.append(_matched_observation(parts[-1], description, clean, ordinal, relative, 'reboot') + ('',) * STORE_COLUMNS)

        count = len(data_list) - first_row
        origins.extend([relative] * count)
        if count and relative not in contributors:
            contributors.append(relative)

    data_headers = (('Timestamp', 'datetime'), 'Raw Timestamp Text', 'Event',
                    'Timestamp Conversion Status', 'Input Line Ordinal',
                    'Matched Text (replacement decoded)', 'Property', 'Reason', 'Subreason', 'Position',
                    'factory_reset Reason Present')
    if len(contributors) > 1:
        data_headers += ('Source File',)
        data_list = [row + (origin,) for row, origin in zip(data_list, origins)]
    return data_headers, data_list, '\n'.join(contributors)
