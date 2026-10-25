__artifacts_v2__ = {
    "smartswitch_sessions": {
        "name": "Samsung Smart Switch - Transfer Sessions",
        "description": (
            "One row per folder under files/History of com.sec.android.easyMover, with the "
            "session state and the device description Smart Switch stored for the other "
            "device of the session."
        ),
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Samsung Smart Switch",
        "notes": (
            "Each folder under files/History is named with a number that reads as epoch "
            "milliseconds; History Folder Time is that number shown as UTC. What event the "
            "folder name marks is not established here; on the tested image the later of "
            "two folder names fell within one second of the Time of the TransferredHistory "
            "entry. Service Type, Sender Type, Restore Type, State, Connect Type, Sec OTG "
            "Type and Completed Service Flag are the values of mainDataModel.json as stored; "
            "their meaning is not decoded. Every other column is a field of peerDeviceInfo.json "
            "in the same folder, a file the app itself names for the peer device, and is the "
            "device description as that file stored it, not a value this module checked "
            "against the other device. Display Name, Google Account, UUID and IMEI are "
            "free text or identifiers the file holds and can be empty. OS Version is reported as stored (36 on the tested image, which "
            "is an Android API level, not a release name). One UI Version is the integer "
            "stored (80000 on the tested image). Available Memory is a byte count, Device "
            "Storage Size is the number stored with no unit named in the file. Account Count "
            "is the number of entries in AccountInfos. Item Count is the number of entries "
            "objItems.json holds for the same folder. Tested on an Android 16 (One UI 8) "
            "full file system extraction, where two sessions were present, both with a Smart "
            "Switch role stored as Receiver; two further Android 16 (One UI 8) extractions held one session each, so the count varies with the device; versions before One UI 7 are not verified. A "
            "folder missing one of the three files is still reported, with the columns of the "
            "missing file empty. The absence of a folder is not evidence that no transfer "
            "took place."
            " On the two further Android 16 images Connect Type and Product Code were empty, because mainDataModel.json and peerDeviceInfo.json there hold no ConnectType or ProductCode key."
        ),
        "paths": (
            '*/com.sec.android.easyMover/files/History/*/mainDataModel.json',
            '*/com.sec.android.easyMover/files/History/*/peerDeviceInfo.json',
            '*/com.sec.android.easyMover/files/History/*/objItems.json',
        ),
        "output_types": "standard",
        "artifact_icon": "smartphone",
        "sample_data": {
            "samsung_ffs_a16_set1": "Android 16 | com.sec.android.easyMover | 2 rows",
            "samsung_ffs_a16_set2": "Android 16 | com.sec.android.easyMover | 0 rows",
            "samsung_ffs_a16_set3": "Android 16 | com.sec.android.easyMover | 1 row",
            "samsung_ffs_a16_set4": "Android 16 | com.sec.android.easyMover | 1 row",
        },
    },
    "smartswitch_items": {
        "name": "Samsung Smart Switch - Transferred Data Categories",
        "description": (
            "The ItemList of objItems.json in each Smart Switch history folder: one row per "
            "data category with its status, counts, sizes and the result of the restore and "
            "backup steps."
        ),
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Samsung Smart Switch",
        "notes": (
            "Type, Status, View Count, Content Count, Size, Data Size, Backup Time, Predicted "
            "Backup Time, File List Count and File List Size are the values of each ItemList "
            "entry as stored. Size and Data Size are reported as stored (bytes is assumed by "
            "the field names only); Backup Time and Predicted Backup Time carry no unit in the "
            "file, and -1 is shown as stored. Restore Result, Restore Step, Restore Error, "
            "Restore Request, Restore Response Result and Restore Error Code come from the "
            "ContentBnrResult object and Backup Result, Backup Step and Backup Error from the "
            "CrmBackupBnrResult object. The Request text is the app's own log string and "
            "names package and folder paths on the device. Content Count counts what Smart "
            "Switch listed for the category; it is not a count of items found on the other "
            "device by this module. Tested on an Android 16 (One UI 8) full file system "
            "extraction, where one session listed 32 categories (29 with a status of COMPLETED "
            "and 3 with NODATA), among them contacts, call logs, messages, calendar, notes, "
            "photos and videos, and a second session listed 11; on two further Android 16 images one session each listed 92 and 65. A category missing from the list is not evidence that its "
            "data was not on the other device."
            " Android User, History ID and History Folder Time held one value on every row of an image with one user and one session. On the first tested image Restore Step and Backup Step held one value each (Restore and Backup) on all 43 rows, and Restore Error and Backup Error were identical on all 43 rows because the file stores the same text in ContentBnrResult and CrmBackupBnrResult (empty on 41 rows, the same app message on 2), while Restore Result and Backup Result differed. On the two further images Predicted Backup Time, Restore Step, Backup Result, Backup Step and Backup Error were empty on every row, because those entries hold no CrmPredictBackupTime or CrmBackupBnrResult and their ContentBnrResult holds no Step; it holds CategoryType, FailCount, FailSize, ChildInfo and Extra fields that this artifact does not report."
        ),
        "paths": ('*/com.sec.android.easyMover/files/History/*/objItems.json',),
        "output_types": "standard",
        "artifact_icon": "list",
        "sample_data": {
            "samsung_ffs_a16_set1": "Android 16 | com.sec.android.easyMover | 43 rows",
            "samsung_ffs_a16_set2": "Android 16 | com.sec.android.easyMover | 0 rows",
            "samsung_ffs_a16_set3": "Android 16 | com.sec.android.easyMover | 92 rows",
            "samsung_ffs_a16_set4": "Android 16 | com.sec.android.easyMover | 65 rows",
        },
    },
    "smartswitch_peer_apps": {
        "name": "Samsung Smart Switch - Peer App Categories",
        "description": (
            "The CategoryInfoExtra list of peerDeviceInfo.json in each Smart Switch history "
            "folder: the apps and components the transfer listed, with the version and last "
            "used time stored for each."
        ),
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Samsung Smart Switch",
        "notes": (
            "One row per CategoryInfoExtra entry. Category is the entry's Type, Package, App "
            "Name, Version Name, Version Code, Stub Version Code, Stub Content Size and Support "
            "Stub Install are as stored, and Last Time Used is LastTimeUsed (epoch milliseconds) "
            "shown as UTC, blank when absent or zero. Runtime Permissions is the number of "
            "RuntimePermissions entries listed. The list covers the categories Smart Switch "
            "offers (including system components), not every app on the other device, and a "
            "package missing from the list is not evidence that it was not installed there. "
            "Last Time Used is the value in the file; where the file's writer took it from is "
            "not established here. Tested on an Android 16 (One UI 8) full file system "
            "extraction, where each of two sessions listed 118 entries, and the one session on each of two further images listed 97 and 66."
            " Android User held one value (0) on every row of each tested image, and History ID and History Folder Time held one value on every row of an image with one session."
        ),
        "paths": ('*/com.sec.android.easyMover/files/History/*/peerDeviceInfo.json',),
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "samsung_ffs_a16_set1": "Android 16 | com.sec.android.easyMover | 236 rows",
            "samsung_ffs_a16_set2": "Android 16 | com.sec.android.easyMover | 0 rows",
            "samsung_ffs_a16_set3": "Android 16 | com.sec.android.easyMover | 97 rows",
            "samsung_ffs_a16_set4": "Android 16 | com.sec.android.easyMover | 66 rows",
        },
    },
    "smartswitch_peer_accounts": {
        "name": "Samsung Smart Switch - Peer Accounts",
        "description": (
            "AccountInfos of peerDeviceInfo.json in each Smart Switch history folder: the "
            "account types and names stored for the other device."
        ),
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Samsung Smart Switch",
        "notes": (
            "One row per entry of AccountInfos.Accounts, with Type and Name as stored. An "
            "account type is the Android account type string. The Name can be empty or "
            "masked by the other device before it is written. The list shows accounts "
            "the file recorded; it does not show that an app was in use. Tested on an "
            "Android 16 (One UI 8) full file system extraction, where each of two sessions "
            "listed 8 accounts, and the one session on each of two further images listed 7 and 10."
            " Android User held one value (0) on every row of each tested image, and History ID and History Folder Time held one value on every row of an image with one session."
        ),
        "paths": ('*/com.sec.android.easyMover/files/History/*/peerDeviceInfo.json',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "samsung_ffs_a16_set1": "Android 16 | com.sec.android.easyMover | 16 rows",
            "samsung_ffs_a16_set2": "Android 16 | com.sec.android.easyMover | 0 rows",
            "samsung_ffs_a16_set3": "Android 16 | com.sec.android.easyMover | 7 rows",
            "samsung_ffs_a16_set4": "Android 16 | com.sec.android.easyMover | 10 rows",
        },
    },
    "smartswitch_peer_messages": {
        "name": "Samsung Smart Switch - Peer Message Counts",
        "description": (
            "MessagePeriods of peerDeviceInfo.json in each Smart Switch history folder: "
            "message counts and sizes stored for the other device."
        ),
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Samsung Smart Switch",
        "notes": (
            "One row per MessagePeriods entry: Period, Count, SMS, MMS, RCS, RCS file transfer "
            "and RCS instant message counts, and Size, MMS Size and RCS File Transfer Size, as "
            "stored; no unit is named for the sizes. The values are counts the file holds, not "
            "messages found by this module, and the messages themselves are not in this file. "
            "Tested on an Android 16 (One UI 8) full file system extraction, where each of two "
            "sessions held six entries (periods such as ALL_DATA and LAST_2YEARS)."
            " Android User held one value (0) on every row of each tested image, and History ID and History Folder Time held one value on every row of an image with one session. On one further image Count, SMS Count, MMS Count, RCS Count, RCS File Transfer Count, RCS Instant Message Count, Size, MMS Size and RCS File Transfer Size were empty on all six rows, because its MessagePeriods entries hold only a Period and a CalcTime; on another RCS File Transfer Size held one value on all six rows."
        ),
        "paths": ('*/com.sec.android.easyMover/files/History/*/peerDeviceInfo.json',),
        "output_types": "standard",
        "artifact_icon": "message-square",
        "sample_data": {
            "samsung_ffs_a16_set1": "Android 16 | com.sec.android.easyMover | 12 rows",
            "samsung_ffs_a16_set2": "Android 16 | com.sec.android.easyMover | 0 rows",
            "samsung_ffs_a16_set3": "Android 16 | com.sec.android.easyMover | 6 rows",
            "samsung_ffs_a16_set4": "Android 16 | com.sec.android.easyMover | 6 rows",
        },
    },
    "smartswitch_peer_contacts": {
        "name": "Samsung Smart Switch - Peer Contact Accounts",
        "description": (
            "AllContactAccounts and ContactAccounts of peerDeviceInfo.json in each Smart "
            "Switch history folder: per contact account counts and sizes."
        ),
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Samsung Smart Switch",
        "notes": (
            "One row per entry of each of the two lists; List names which one. Account and "
            "Type are the contact account's name and type as stored, and Selected, Syncable, "
            "eSIM, Count, Size, Binary Count, Binary Size and Photo Count are the other fields "
            "of the entry as stored. Contact IDs, when the file holds them, are not reported. "
            "The counts are those the file holds, not contacts found by this module. Tested on "
            "an Android 16 (One UI 8) full file system extraction. On two further Android 16 images "
            "one session listed no contact accounts and the other listed six entries across the two lists."
            " Android User held one value (0) on every row of each tested image, and History ID and History Folder Time held one value on every row of an image with one session. Selected, eSIM, Binary Count and Binary Size held one value on every row (Yes, No, 0 and 0)."
        ),
        "paths": ('*/com.sec.android.easyMover/files/History/*/peerDeviceInfo.json',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "samsung_ffs_a16_set1": "Android 16 | com.sec.android.easyMover | 12 rows",
            "samsung_ffs_a16_set2": "Android 16 | com.sec.android.easyMover | 0 rows",
            "samsung_ffs_a16_set3": "Android 16 | com.sec.android.easyMover | 0 rows",
            "samsung_ffs_a16_set4": "Android 16 | com.sec.android.easyMover | 6 rows",
        },
    },
    "smartswitch_transferred_history": {
        "name": "Samsung Smart Switch - Transferred History",
        "description": "Entries of TransferredHistory/List.json in com.sec.android.easyMover.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Samsung Smart Switch",
        "notes": (
            "One row per entry of TransferredHistoryList: UUID and Display Name as stored, and "
            "Time (epoch milliseconds) shown as UTC. The UUID is the identifier Smart Switch "
            "stored for the other device; the Display Name is free text. On the tested "
            "Android 16 (One UI 8) image the list held one entry, its UUID equalled the UUID in "
            "the peerDeviceInfo.json of both History folders, and its Time was within one second "
            "of the later folder's name; the match is not made by this module."
        ),
        "paths": ('*/com.sec.android.easyMover/files/TransferredHistory/List.json',),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "samsung_ffs_a16_set1": "Android 16 | com.sec.android.easyMover | 1 row",
            "samsung_ffs_a16_set2": "Android 16 | com.sec.android.easyMover | 0 rows",
            "samsung_ffs_a16_set3": "Android 16 | com.sec.android.easyMover | 1 row",
            "samsung_ffs_a16_set4": "Android 16 | com.sec.android.easyMover | 1 row",
        },
    },
    "smartswitch_backup_media": {
        "name": "Samsung Smart Switch - Backup Media Index",
        "description": (
            "The bkmedia table of files/SmartSwitch/SmartSwitchBackup/backup_media.db in "
            "com.sec.android.easyMover."
        ),
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "Samsung Smart Switch",
        "notes": (
            "One row per bkmedia row: name, file path, backup file path, size, unique id and "
            "count as stored. The table lists media files Smart Switch recorded for backup; "
            "that a listed file exists at the path or in the backup is not checked here, and "
            "what the unique id and count denote is not established. Tested on an Android 16 "
            "(One UI 8) full file system extraction, where the table held 5,169 rows. The "
            "database is read with its -wal file. It was absent from the two further Android 16 images "
            "checked, so those report no rows."
            " Android User, Unique ID and Count each held one value on all 5,169 rows of the tested image (0, one number, and 1)."
        ),
        "paths": ('*/com.sec.android.easyMover/files/SmartSwitch/SmartSwitchBackup/backup_media.db*',),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
            "samsung_ffs_a16_set1": "Android 16 | com.sec.android.easyMover | 5169 rows",
            "samsung_ffs_a16_set2": "Android 16 | com.sec.android.easyMover | 0 rows",
            "samsung_ffs_a16_set3": "Android 16 | com.sec.android.easyMover | 0 rows",
            "samsung_ffs_a16_set4": "Android 16 | com.sec.android.easyMover | 0 rows",
        },
    },
}

import datetime
import json
import os
import re

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, logfunc

_VIEW = re.compile(
    r'(?:^|/)(?:(?:user)?data/(?:data|user(?:_de)?/(\d+))|data_mirror/data_[a-z]+/[^/]+/(\d+))/')


def _android_user(relative_path):
    """The Android user whose app folder holds the file; data/data is user 0."""
    match = _VIEW.search(str(relative_path).replace('\\', '/'))
    if not match:
        return ''
    return match.group(1) or match.group(2) or '0'


def _ms(value):
    """Epoch milliseconds as an aware UTC datetime; blank for empty, zero or invalid values."""
    if value is None or value == '' or isinstance(value, bool):
        return ''
    try:
        number = int(value)
    except (TypeError, ValueError):
        return ''
    if number <= 0:
        return ''
    try:
        return datetime.datetime.fromtimestamp(number / 1000, tz=datetime.timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _text(value):
    if value is None:
        return ''
    if isinstance(value, bool):
        return 'Yes' if value else 'No'
    return value


def _dict(value):
    return value if isinstance(value, dict) else {}


def _list(value):
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _load(context, path):
    """A JSON file's content, or None (logged) when it cannot be read."""
    try:
        with open(path, 'r', encoding='utf-8') as handle:
            return json.load(handle)
    except (OSError, ValueError) as error:
        logfunc(f'Smart Switch: could not read {context.get_relative_path(path)}: {error}')
        return None


def _history_files(context, name):
    """[(path, android user, history id)] for the history files called name."""
    found = []
    for path in unique_files(context):
        path = str(path)
        if os.path.basename(path) != name:
            continue
        relative = str(context.get_relative_path(path)).replace('\\', '/')
        match = re.search(r'/History/([^/]+)/', relative)
        if match:
            found.append((path, _android_user(relative), match.group(1)))
    return found


def _history_ms(history_id):
    return _ms(history_id) if re.fullmatch(r'\d+', history_id) else ''


def _source(paths):
    return '\n'.join(paths)


@artifact_processor
def smartswitch_sessions(context):
    sessions = {}
    sources = []
    for name in ('mainDataModel.json', 'peerDeviceInfo.json', 'objItems.json'):
        for path, user, history_id in _history_files(context, name):
            content = _load(context, path)
            sources.append(path)
            session = sessions.setdefault((user, history_id), {})
            session[name] = content if isinstance(content, (dict, list)) else None
    data_list = []
    for (user, history_id), session in sorted(sessions.items(), key=lambda item: (
            item[0][0], int(item[0][1]) if item[0][1].isdigit() else 0, item[0][1])):
        model = _dict(session.get('mainDataModel.json'))
        peer = _dict(session.get('peerDeviceInfo.json'))
        items = _dict(session.get('objItems.json'))
        accounts = _list(_dict(peer.get('AccountInfos')).get('Accounts'))
        data_list.append((
            user, history_id, _history_ms(history_id),
            _text(model.get('ServiceType')), _text(model.get('SenderType')),
            _text(model.get('RestoreType')), _text(model.get('SsmState')),
            _text(model.get('ConnectType')), _text(model.get('SecOtgType')),
            _text(model.get('CompletedServiceFlag')),
            _text(peer.get('ModelName')), _text(peer.get('BrandName')),
            _text(peer.get('DisplayName')), _text(peer.get('ProductCode')),
            _text(peer.get('SalesCode')), _text(peer.get('CountryCode')),
            _text(peer.get('OsType')), _text(peer.get('OsVer')), _text(peer.get('OneUiVer')),
            _text(peer.get('AppVer')), _text(peer.get('AccessoryRole')),
            _text(peer.get('UUID')), _text(peer.get('IMEI')), _text(peer.get('GoogleAccount')),
            _text(peer.get('DeviceStorageSize')), _text(peer.get('AvailInMemSize')),
            len(accounts) if peer else '', len(_list(items.get('ItemList'))) if items else '',
        ))
    headers = ('Android User', 'History ID', ('History Folder Time', 'datetime'),
               'Service Type', 'Sender Type', 'Restore Type', 'State', 'Connect Type',
               'Sec OTG Type', 'Completed Service Flag', 'Model Name', 'Brand Name',
               'Display Name', 'Product Code', 'Sales Code', 'Country Code', 'OS Type',
               'OS Version', 'One UI Version', 'Smart Switch App Version', 'Accessory Role',
               'UUID', 'IMEI', 'Google Account', 'Device Storage Size', 'Available Memory',
               'Account Count', 'Item Count')
    return headers, data_list, _source(sources)


@artifact_processor
def smartswitch_items(context):
    data_list = []
    sources = []
    for path, user, history_id in _history_files(context, 'objItems.json'):
        content = _load(context, path)
        sources.append(path)
        for item in _list(_dict(content).get('ItemList')):
            restore = _dict(item.get('ContentBnrResult'))
            backup = _dict(item.get('CrmBackupBnrResult'))
            response = _dict(restore.get('Response'))
            data_list.append((
                user, history_id, _history_ms(history_id), _text(item.get('Type')),
                _text(item.get('Status')), _text(item.get('ViewCount')),
                _text(item.get('ContentCount')), _text(item.get('Size')),
                _text(item.get('DataSize')), _text(item.get('BackupTime')),
                _text(item.get('CrmPredictBackupTime')), _text(item.get('FileListCount')),
                _text(item.get('FileListSize')),
                _text(restore.get('Result')), _text(restore.get('Step')),
                _text(restore.get('Error')), _text(restore.get('Request')),
                _text(response.get('Result')), _text(response.get('Err_Code')),
                _text(backup.get('Result')), _text(backup.get('Step')),
                _text(backup.get('Error')),
            ))
    headers = ('Android User', 'History ID', ('History Folder Time', 'datetime'), 'Type',
               'Status', 'View Count', 'Content Count', 'Size', 'Data Size', 'Backup Time',
               'Predicted Backup Time', 'File List Count', 'File List Size', 'Restore Result',
               'Restore Step', 'Restore Error', 'Restore Request', 'Restore Response Result',
               'Restore Error Code', 'Backup Result', 'Backup Step', 'Backup Error')
    return headers, data_list, _source(sources)


def _peer_files(context):
    """[(path, user, history id, parsed peerDeviceInfo.json)] for readable files."""
    peers = []
    for path, user, history_id in _history_files(context, 'peerDeviceInfo.json'):
        content = _load(context, path)
        peers.append((path, user, history_id, _dict(content)))
    return peers


@artifact_processor
def smartswitch_peer_apps(context):
    data_list = []
    peers = _peer_files(context)
    for _, user, history_id, peer in peers:
        for entry in _list(peer.get('CategoryInfoExtra')):
            permissions = entry.get('RuntimePermissions')
            data_list.append((
                user, history_id, _history_ms(history_id), _text(entry.get('Type')),
                _text(entry.get('PackageName')), _text(entry.get('AppName')),
                _text(entry.get('VersionName')), _text(entry.get('VersionCode')),
                _text(entry.get('StubVersionCode')), _text(entry.get('StubContentSize')),
                _text(entry.get('SupportStubInstall')), _ms(entry.get('LastTimeUsed')),
                len(permissions) if isinstance(permissions, list) else '',
            ))
    headers = ('Android User', 'History ID', ('History Folder Time', 'datetime'), 'Category',
               'Package', 'App Name', 'Version Name', 'Version Code', 'Stub Version Code',
               'Stub Content Size', 'Support Stub Install', ('Last Time Used', 'datetime'),
               'Runtime Permissions')
    return headers, data_list, _source(path for path, _, _, _ in peers)


@artifact_processor
def smartswitch_peer_accounts(context):
    data_list = []
    peers = _peer_files(context)
    for _, user, history_id, peer in peers:
        for entry in _list(_dict(peer.get('AccountInfos')).get('Accounts')):
            data_list.append((user, history_id, _history_ms(history_id),
                              _text(entry.get('Type')), _text(entry.get('Name'))))
    headers = ('Android User', 'History ID', ('History Folder Time', 'datetime'), 'Type', 'Name')
    return headers, data_list, _source(path for path, _, _, _ in peers)


@artifact_processor
def smartswitch_peer_messages(context):
    data_list = []
    peers = _peer_files(context)
    for _, user, history_id, peer in peers:
        for entry in _list(peer.get('MessagePeriods')):
            data_list.append((
                user, history_id, _history_ms(history_id), _text(entry.get('Period')),
                _text(entry.get('Count')), _text(entry.get('CountSms')),
                _text(entry.get('CountMms')), _text(entry.get('CountRcs')),
                _text(entry.get('CountRcsFt')), _text(entry.get('CountRcsIm')),
                _text(entry.get('Size')), _text(entry.get('SizeMms')),
                _text(entry.get('SizeRcsFt')),
            ))
    headers = ('Android User', 'History ID', ('History Folder Time', 'datetime'), 'Period',
               'Count', 'SMS Count', 'MMS Count', 'RCS Count', 'RCS File Transfer Count',
               'RCS Instant Message Count', 'Size', 'MMS Size', 'RCS File Transfer Size')
    return headers, data_list, _source(path for path, _, _, _ in peers)


@artifact_processor
def smartswitch_peer_contacts(context):
    data_list = []
    peers = _peer_files(context)
    for _, user, history_id, peer in peers:
        for list_name in ('AllContactAccounts', 'ContactAccounts'):
            for entry in _list(peer.get(list_name)):
                data_list.append((
                    user, history_id, _history_ms(history_id), list_name,
                    _text(entry.get('Account')), _text(entry.get('Type')),
                    _text(entry.get('Selected')), _text(entry.get('Syncable')),
                    _text(entry.get('isESIM')), _text(entry.get('Count')),
                    _text(entry.get('Size')), _text(entry.get('BinCount')),
                    _text(entry.get('BinSize')), _text(entry.get('PhotoCount')),
                ))
    headers = ('Android User', 'History ID', ('History Folder Time', 'datetime'), 'List',
               'Account', 'Type', 'Selected', 'Syncable', 'eSIM', 'Count', 'Size',
               'Binary Count', 'Binary Size', 'Photo Count')
    return headers, data_list, _source(path for path, _, _, _ in peers)


@artifact_processor
def smartswitch_transferred_history(context):
    data_list = []
    sources = []
    for path in unique_files(context):
        path = str(path)
        if os.path.basename(path) != 'List.json':
            continue
        relative = str(context.get_relative_path(path)).replace('\\', '/')
        user = _android_user(relative)
        content = _load(context, path)
        sources.append(path)
        for entry in _list(_dict(content).get('TransferredHistoryList')):
            data_list.append((user, _text(entry.get('UUID')), _text(entry.get('DisplayName')),
                              _ms(entry.get('Time'))))
    headers = ('Android User', 'UUID', 'Display Name', ('Time', 'datetime'))
    return headers, data_list, _source(sources)


@artifact_processor
def smartswitch_backup_media(context):
    data_list = []
    sources = []
    for path in unique_files(context):
        path = str(path)
        if os.path.basename(path) != 'backup_media.db':
            continue
        user = _android_user(str(context.get_relative_path(path)))
        sources.append(path)
        query = ('SELECT _id, name, file_path, backup_file_path, size, uniqueid, count '
                 'FROM bkmedia ORDER BY _id')
        for row in get_sqlite_db_records(path, query):
            data_list.append((user,) + tuple(row))
    headers = ('Android User', 'ID', 'Name', 'File Path', 'Backup File Path', 'Size',
               'Unique ID', 'Count')
    return headers, data_list, _source(sources)
