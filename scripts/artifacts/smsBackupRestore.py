__artifacts_v2__ = {
    "smsbackuprestore_backup_sets": {
        "name": "SMS Backup and Restore Backup Sets",
        "description": "Backup files SMS Backup and Restore wrote, with the time of each and the number of items it recorded",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "SMS Backup and Restore",
        "sample_data": {
            "emu_a15_oss_v16": "SMS Backup & Restore 10.26.010 | 1 row",
        },
        "notes": "One row per backup file the app wrote, read from the file's own <smses> or "
                 "<calls> element. Backup Time is that element's backup_date attribute, Unix "
                 "milliseconds, reported as UTC; on the tested image it matched the run to the "
                 "second. Item Count is the count attribute the app wrote, and Items Parsed is "
                 "how many child elements this module actually read, so a disagreement between "
                 "the two is visible rather than hidden. Backup Set is the backup_set attribute "
                 "as stored. Backup Type is the type attribute, 'full' on the tested image. On "
                 "the tested device the backup location was the app's own files directory, which "
                 "is why the path is inside the app container, and that is the only location "
                 "exercised here. A backup written to another folder, or held only by a cloud "
                 "service, would sit outside this glob and go unreported. A backup file records "
                 "the messages as they stood when it was written, so it can hold messages that "
                 "are no longer in the live message store.",
        "paths": ('*/com.riteshsahu.SMSBackupRestore/files/sms-*.xml',
                  '*/com.riteshsahu.SMSBackupRestore/files/calls-*.xml'),
        "output_types": "standard",
        "artifact_icon": "archive",
    },
    "smsbackuprestore_messages": {
        "name": "SMS Backup and Restore Messages",
        "description": "Text messages recorded inside the backup files SMS Backup and Restore wrote",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "SMS Backup and Restore",
        "sample_data": {
            "emu_a15_oss_v16": "SMS Backup & Restore 10.26.010 | 3 rows",
        },
        "notes": "One row per <sms> element inside a backup file the app wrote. These are "
                 "messages as they stood when the backup ran, so a row can describe a message "
                 "that is no longer on the device. "
                 "Timestamp is the element's date attribute, Unix milliseconds, reported as UTC. "
                 "The file also carries the app's own readable_date, which is a local time string "
                 "with no zone, and it is reported as stored beside the converted value so the "
                 "two can be compared; on the tested image 1788675512995 and 'Sep 6, 2026 2:18:32 "
                 "AM' are the same moment in the device's America/New_York zone. "
                 "Direction is decoded from the type attribute, where 1 is a received message and "
                 "2 is a sent one, taken from the values present rather than from any published "
                 "source, so anything else is reported as stored. Read is the app's read flag as "
                 "stored. Contact Name is the contact_name attribute as stored; it read "
                 "'(Unknown)' on all three rows of the tested image, where no contacts were "
                 "saved. Whether it holds a name when the number is in contacts was not "
                 "exercised. Only <sms> elements are read here. <mms> elements and calls-*.xml "
                 "files are not parsed; neither was present on the tested image, and both are "
                 "named here so the gap is visible rather than silent.",
        "paths": ('*/com.riteshsahu.SMSBackupRestore/files/sms-*.xml',),
        "output_types": "standard",
        "artifact_icon": "message-square",
    },
}

import os
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, logfunc
from scripts.artifacts.storagePathViews import unique_files

BACKUP_DIR = 'com.riteshsahu.SMSBackupRestore/files/'
# Observed on the tested image; anything else is reported as stored.
DIRECTIONS = {'1': 'Received', '2': 'Sent'}


def _backup_files(context, prefix):
    out = []
    for found in unique_files(context):
        path = str(found).replace('\\', '/')
        if BACKUP_DIR in path and os.path.basename(path).startswith(prefix) and path.endswith('.xml'):
            out.append(path)
    return out


def _root(path):
    """The parsed root element, or None when the file will not parse."""
    try:
        return ET.parse(path).getroot()
    except (OSError, ET.ParseError) as error:
        logfunc(f'SMS Backup and Restore: could not read {os.path.basename(path)}: {error}')
        return None


def _ms(value):
    if not value:
        return ''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    try:
        return convert_unix_ts_to_utc(value // 1000)
    except (OverflowError, OSError, ValueError):
        return ''


@artifact_processor
def smsbackuprestore_backup_sets(context):
    data_list = []
    sources = []
    for path in _backup_files(context, 'sms-') + _backup_files(context, 'calls-'):
        root = _root(path)
        if root is None:
            continue
        parsed = len(list(root))
        data_list.append((
            _ms(root.get('backup_date')),
            os.path.basename(path),
            root.get('count') or '',
            parsed,
            root.get('type') or '',
            root.get('backup_set') or '',
            context.get_relative_path(path)))
        if path not in sources:
            sources.append(path)

    data_list.sort(key=lambda row: row[0], reverse=True)
    data_headers = (
        ('Backup Time', 'datetime'), 'Backup File', 'Item Count (as stored)',
        'Items Parsed', 'Backup Type', 'Backup Set', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def smsbackuprestore_messages(context):
    data_list = []
    sources = []
    for path in _backup_files(context, 'sms-'):
        root = _root(path)
        if root is None:
            continue
        seen = False
        for sms in root.findall('sms'):
            seen = True
            kind = sms.get('type') or ''
            data_list.append((
                _ms(sms.get('date')),
                DIRECTIONS.get(kind, f'{kind} (as stored)' if kind else ''),
                sms.get('address') or '',
                sms.get('body') or '',
                sms.get('contact_name') or '',
                sms.get('readable_date') or '',
                sms.get('read') or '',
                _ms(sms.get('date_sent')),
                os.path.basename(path),
                context.get_relative_path(path)))
        if seen and path not in sources:
            sources.append(path)

    data_list.sort(key=lambda row: row[0], reverse=True)
    data_headers = (
        ('Timestamp', 'datetime'), 'Direction', 'Number', 'Message',
        'Contact Name (as stored)', 'Readable Date (as stored)', 'Read (as stored)',
        ('Date Sent', 'datetime'), 'Backup File', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
