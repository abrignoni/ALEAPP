"""Builds a synthetic com.sec.android.easyMover tree (Samsung Smart Switch) for tests.

Nothing here comes from a real device. The file names and field names are the ones the
Smart Switch app writes on an Android 16 (One UI 8) image; every value below is made up.
"""
import json
import pathlib
import sqlite3

APP = 'data/data/com.sec.android.easyMover/files'
T0 = 1767225600000  # 2026-01-01 00:00:00 UTC in milliseconds

MAIN_MODEL = {
    'ServiceType': 'AccessoryD2d', 'SenderType': 'Receiver', 'RestoreType': 'NORMAL',
    'SsmState': 'Complete', 'ConnectType': 'UNKNOWN', 'SecOtgType': 'Unknown',
    'CompletedServiceFlag': 1025,
}


def peer(uuid='00000000-1111-2222-3333-444444444444'):
    return {
        'Dummy': 'x', 'UUID': uuid, 'IMEI': '000000000000000',
        'AccountInfos': {'Accounts': [{'Type': 'com.example.chat', 'Name': 'user-a'},
                                      {'Type': 'com.google', 'Name': ''}]},
        'AllContactAccounts': [{'Account': 'acct-a', 'Type': 'com.google', 'Selected': True,
                                'Syncable': True, 'isESIM': False, 'BinCount': 0, 'BinSize': 0,
                                'PhotoCount': 2, 'Count': 10, 'Size': 2048, 'IconPath': '/x',
                                'ContactIds': '1,2'}],
        'ContactAccounts': [{'Account': 'acct-a', 'Type': 'com.google', 'Selected': False,
                             'Syncable': True, 'isESIM': False, 'BinCount': 1, 'BinSize': 5,
                             'PhotoCount': 2, 'Count': 10, 'Size': 2048, 'IconPath': '/x',
                             'ContactIds': '1,2'}],
        'ModelName': 'SM-TEST1', 'OsType': 'Android', 'OsVer': '36', 'OneUiVer': 80000,
        'GoogleAccount': 'someone@example.invalid', 'Vendor': 'samsung', 'ProductType': 'S1',
        'ProductCode': 'SM-TEST1ZZZ', 'DisplayName': 'Test phone', 'AppVer': '1.2.3',
        'SalesCode': 'XXX', 'AvailInMemSize': 123456789, 'DeviceStorageSize': 256,
        'CountryCode': 'us', 'BrandName': 'Galaxy Test', 'AccessoryRole': 'Sender',
        'CategoryInfoExtra': [
            {'Type': 'CONTACT', 'PackageName': 'com.example.contacts', 'VersionName': '1.0',
             'AppName': 'Contacts', 'VersionCode': 100, 'StubVersionCode': 0,
             'StubContentSize': 0, 'SupportStubInstall': True, 'LastTimeUsed': T0 - 5000,
             'RuntimePermissions': [{'name': 'a'}, {'name': 'b'}]},
            {'Type': 'MESSAGE', 'PackageName': 'com.example.messages', 'VersionName': '2.0',
             'AppName': 'Messages', 'VersionCode': 200, 'StubVersionCode': 7,
             'StubContentSize': 99, 'SupportStubInstall': False, 'LastTimeUsed': 0},
        ],
        'MessagePeriods': [
            {'Period': 'ALL_DATA', 'Count': 30, 'CountSms': 20, 'CountMms': 8, 'CountRcs': 2,
             'CountRcsFt': 1, 'CountRcsIm': 1, 'Size': 1000, 'SizeMms': 800, 'SizeRcsFt': 100},
            {'Period': 'LAST_YEAR', 'Count': 3, 'CountSms': 3, 'CountMms': 0, 'CountRcs': 0,
             'CountRcsFt': 0, 'CountRcsIm': 0, 'Size': 10, 'SizeMms': 0, 'SizeRcsFt': 0},
        ],
    }


def items():
    return {'ItemList': [
        {'Status': 'COMPLETED', 'Type': 'CONTACT', 'ViewCount': 5, 'ContentCount': 5,
         'Size': 1000, 'DataSize': 900, 'BackupTime': 12, 'CrmPredictBackupTime': 1400,
         'FileListCount': 1, 'FileListSize': 3, 'ListInfoFilePath': '/x',
         'ContentBnrResult': {'Result': True, 'Step': 'Restore', 'Request': 'Name[CONTACT]',
                              'Response': {'Result': 0, 'Err_Code': 0, 'Extra': ''},
                              'Error': ''},
         'CrmBackupBnrResult': {'Result': True, 'Step': 'Backup', 'Error': ''}},
        {'Status': 'NODATA', 'Type': 'MEDIASEARCH', 'ViewCount': 1, 'ContentCount': 1,
         'Size': 10, 'DataSize': 10, 'BackupTime': -1, 'CrmPredictBackupTime': -1,
         'ContentBnrResult': {'Result': False, 'Step': 'Restore', 'Error': 'failed'}},
        'not an object',
    ]}


def write_json(path, content):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content), encoding='utf-8')
    return path


def make_backup_media(path):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute('CREATE TABLE bkmedia (_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, '
                'file_path TEXT, backup_file_path TEXT, size INTEGER, uniqueid LONG, count INTEGER)')
    con.executemany('INSERT INTO bkmedia (name, file_path, backup_file_path, size, uniqueid, count) '
                    'VALUES (?, ?, ?, ?, ?, ?)',
                    [('a.jpg', '/sdcard/a.jpg', '/bk/a', 10, 1001, 1),
                     ('b.mp4', '/sdcard/b.mp4', '/bk/b', 20, 1002, 2)])
    con.commit()
    con.close()
    return path


def make_tree(root):
    """Two history folders in user 0 (one also under data/user/0), one in user 10."""
    root = pathlib.Path(root)
    paths = []
    first, second = str(T0), str(T0 + 3600000)
    for base in (APP, 'data/user/0/com.sec.android.easyMover/files'):
        for name, content in (('mainDataModel.json', MAIN_MODEL), ('peerDeviceInfo.json', peer()),
                              ('objItems.json', items())):
            paths.append(write_json(root / base / 'History' / first / name, content))
    # Only a peerDeviceInfo.json in the second folder: the other two files are missing.
    paths.append(write_json(root / APP / 'History' / second / 'peerDeviceInfo.json', peer()))
    paths.append(write_json(root / 'data/user/10/com.sec.android.easyMover/files/History' / first
                            / 'mainDataModel.json', dict(MAIN_MODEL, SenderType='Sender')))
    paths.append(write_json(root / APP / 'TransferredHistory/List.json', {
        'TransferredHistoryList': [{'UUID': '00000000-1111-2222-3333-444444444444',
                                    'DisplayName': 'Test phone', 'Time': T0 + 3600052}]}))
    paths.append(make_backup_media(root / APP / 'SmartSwitch/SmartSwitchBackup/backup_media.db'))
    return paths
