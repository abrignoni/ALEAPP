__artifacts_v2__ = {
    "get_whatsapp_google_drive_backup": {
        "name": "WhatsApp - Google Drive Backup",
        "description": "Values WhatsApp's shared preferences hold under its gdrive_last_successful_backup "
                       "keys: the account named in the key, the stored backup time and sizes, the encrypted "
                       "flag as stored, and the backup frequency setting.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-20",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "One row per account named in a gdrive_last_successful_backup_timestamp key, per preferences file, WhatsApp data folder and Android user; no corpus folder held these keys in both files. A folder that holds a backup frequency and no such key gets one row with only the frequency. The keys were in com.whatsapp_preferences_light.xml on the 4 images running WhatsApp 2.23.12.78 or 2.24.16.76, and in backup_prefs.xml on the 3 running 2.25.25.73, 2.25.26.74 or 2.26.39.79 (anne_a15, kevin_pocox7_a15, dragna_pixel9a_a16); the version where this changed is not established. Both files are read. The account, time, encrypted and size values of a row come from one file; Backup Frequency comes from the first of the two files that holds it. The data/data, data/user/0 and data_mirror copies of one folder are read once. What writes the keys was read in WhatsApp 2.26.39.79 decompiled with jadx (from dragna_pixel9a_a16). The setters (X.HRE) name each key gdrive_last_successful_backup_<field>:<account name>; the callers pass gdrive_account_name, or the text gms-account or vault-account for other backup providers (X.HRE.A05); neither text was seen on the corpus. Last Successful Backup (UTC) is the timestamp key read as milliseconds since 1970 UTC. In 2.26.39.79 the key is written with the phone's clock when a backup finishes, and also at the start of a backup run with the update time of the backup found on the server. On the 3 images whose WhatsApp app log (files/Logs) still covers that day (sharon_a13, kevin_pocox7_a15, dragna_pixel9a_a16), it was within 1 second after the last gdrive/backup/upload/success line of that run, once the log's local time was converted with the time zone offset its header records; these checks cover the first case only. On the other 4 images with a row the stored time was older than the log. Account (as stored) is the text after the colon in the key names; it had the form of an email address on all 7 account rows. Encrypted (as stored) is the encrypted key; it held false on all 7 account rows, so a true value was not exercised, and on the 5 images whose backup_prefs.xml holds backup_encryption_method (2 of them with an account row) it held unencrypted. Total Size, Media Size and Video Size are the total_size, media_size and video_size keys as stored; their unit is not established; Video Size (as stored) held 0 on all 7 account rows. Backup Frequency is interface_gdrive_backup_frequency with the name WhatsApp's own log uses for it (the same mapping in 2.26.39.79, X.C13W.A04, and in 2.23.12.78 from sharon_a13, X.C60682sp: 0 off, 1 daily, 2 weekly, 3 monthly, 4 manual); the mapping was read in those two versions and is applied to the others. 1 and 3 were seen on account rows, and 0 on hickman_a13, pixel3_a11 and pixel3_a12, which hold no gdrive_last_successful_backup_timestamp key. A missing frequency is left blank. User held 0 on all rows. A row records what the phone stored; it does not show that a backup still exists on Google Drive. Not reported: gdrive_state and gdrive_error_code (meaning not established), the backup network and include-videos settings, the <name>_backup_size and <name>_backup_status keys, the backup token timestamps, msg_backup_timestamp (local backup files are in WhatsApp - Local Backups), and other gdrive_ and backup_ keys. WhatsApp Business (com.whatsapp.w4b) is not read; no com.whatsapp.w4b copy of these two files was found on the registered Android images searched.",
        "sample_data": {
            "anne_a15": "Android 15 | 1 row",
            "dragna_pixel9a_a16": "Android 16 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "hickman_a13": "Android 13 | 1 row",
            "kevin_pocox7_a15": "Android 15 | 1 row",
            "pixel3_a11": "Android 11 | 1 row",
            "pixel3_a12": "Android 12 | 1 row",
            "pixel7a_a14": "Android 14 | 0 rows",
            "russell_a14": "Android 14 | 1 row",
            "russell_pixel6a_a13": "Android 13 | 1 row",
            "samsung_a166u_a16_known_20261116": "Android 16 | 0 rows",
            "samsung_a166u_a16_known_20261117": "Android 16 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 1 row",
            "sharon_a14": "Android 14 | 1 row",
        },
        "paths": ('*/com.whatsapp/shared_prefs/com.whatsapp_preferences_light.xml',
                  '*/com.whatsapp/shared_prefs/backup_prefs.xml'),
        "output_types": "standard",
        "artifact_icon": "upload-cloud",
    }
}

import datetime
import os
import xml.etree.ElementTree as ET

from scripts.artifacts.storagePathViews import canonical_path, unique_files
from scripts.ilapfuncs import artifact_processor, logfunc

_FILES = ('com.whatsapp_preferences_light.xml', 'backup_prefs.xml')
_PREFIX = 'gdrive_last_successful_backup_'
# WhatsApp 2.26.39.79 (X.C13W.A04) and 2.23.12.78 (X.C60682sp), decompiled from corpus images: the names its own log uses.
_FREQUENCY = {'0': 'off', '1': 'daily', '2': 'weekly', '3': 'monthly', '4': 'manual'}


def _ms_to_utc(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return ''
    if number <= 0:
        return ''
    try:
        return datetime.datetime.fromtimestamp(number / 1000, datetime.timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _number(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return value if value is not None else ''


def _user_of(key):
    """The Android user number canonical_path put in its key, else ''."""
    parts = key.split('\x00')
    if len(parts) >= 2 and ':' in parts[1]:
        return parts[1].split(':', 1)[1]
    return ''


def _read(file_found, label):
    try:
        root = ET.parse(file_found).getroot()
    except (ET.ParseError, OSError) as ex:
        logfunc(f'WhatsApp - Google Drive Backup: {label} could not be read as XML: {ex}')
        return None
    values = {}
    for element in root:
        name = element.get('name')
        if not name:
            continue
        value = element.get('value')
        if value is None:
            value = element.text or ''
        values[name] = value
    return values


@artifact_processor
def get_whatsapp_google_drive_backup(context):
    data_headers = (('Last Successful Backup (UTC)', 'datetime'), 'Account (as stored)', 'Encrypted (as stored)',
                    ('Total Size (as stored)', 'number'), ('Media Size (as stored)', 'number'),
                    ('Video Size (as stored)', 'number'), 'Backup Frequency', 'User')
    folders = {}
    for file_found in unique_files(context):
        file_found = str(file_found)
        name = os.path.basename(file_found)
        if name not in _FILES:
            continue
        relative = context.get_relative_path(file_found)
        key = canonical_path(relative)[0].rsplit('/', 1)[0]
        folders.setdefault(key, []).append((name, file_found, relative))

    data_list, sources = [], []
    for key in sorted(folders):
        frequency, read, rows = '', [], []
        for name, file_found, relative in sorted(folders[key]):
            values = _read(file_found, relative)
            if values is None:
                continue
            read.append(file_found)
            if values.get('interface_gdrive_backup_frequency', '') != '' and not frequency:
                frequency = values['interface_gdrive_backup_frequency']
            accounts = {}
            for item, value in values.items():
                if item.startswith(_PREFIX) and ':' in item:
                    field, account = item[len(_PREFIX):].split(':', 1)
                    accounts.setdefault(account, {})[field] = value
            # Each row takes its values from one file, so the two files are never mixed.
            for account in sorted(accounts):
                if 'timestamp' in accounts[account]:
                    rows.append((account, accounts[account]))
        if not read:
            continue
        frequency_text = f'{frequency} ({_FREQUENCY[frequency]})' if frequency in _FREQUENCY else frequency
        user = _user_of(key)
        for account, fields in rows:
            data_list.append((
                _ms_to_utc(fields.get('timestamp')), account, fields.get('encrypted', ''),
                _number(fields.get('total_size')), _number(fields.get('media_size')),
                _number(fields.get('video_size')), frequency_text, user))
        if not rows:
            if not frequency_text:
                continue
            data_list.append(('', '', '', '', '', '', frequency_text, user))
        sources.extend(read)
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))
