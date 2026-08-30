__artifacts_v2__ = {
    "keepassdx_database_history": {
        "name": "KeePassDX - Database History",
        "description": "Parses the opened-database history recorded by the KeePassDX Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "KeePassDX",
        "notes": "One row per entry in the file_database_history table of the app's own Room store "
                 "databases/com.kunzisoft.keepass.database. KeePassDX is a password manager; the vault "
                 "itself (a .kdbx file) is encrypted and its contents are not recovered here. What this "
                 "table records is which KeePass databases the app has opened and where they are stored. "
                 "Each row carries the Database URI as stored (a content:// storage-provider URI or a "
                 "file:// path, depending on where the vault was opened from), the user-set Database "
                 "Alias, the Keyfile URI if the vault uses a key file, the Hardware Key type as stored "
                 "if a hardware key is used, the Read Only and User Verification flags as stored, and "
                 "Updated, which the app sets to System.currentTimeMillis() when the entry is added or "
                 "updated (fields per FileDatabaseHistoryEntity.kt at Kunzisoft/KeePassDX "
                 "4054d7d844f8386cfca479b1c979b37ca1a9a129). Updated is Unix milliseconds and was UTC on "
                 "the tested device (16:59 UTC matched the device's 12:59 local clock), so it is reported "
                 "as UTC. User Verification is the app's advanced-unlock flag for the database (device "
                 "credential or biometric); a set flag records that advanced unlock is configured, not "
                 "that a credential was stored. Quick Unlock Credential Stored is derived from the "
                 "cipher_database table: it is Yes when that table holds a row for the same Database URI. "
                 "cipher_database stores the master credential wrapped by an Android Keystore key for "
                 "biometric or device-credential quick unlock; the wrapped value and its cipher "
                 "parameters are never read or reported here, only whether a row is present. Two other "
                 "tables in the store are not evidential: room_master_table is Room schema bookkeeping "
                 "and android_metadata holds the locale. The app's shared_prefs "
                 "(com.kunzisoft.keepass.libre_preferences.xml) held only an app-lock timeout backup on "
                 "the tested device and is not parsed. The Room store runs in WAL mode and held its rows "
                 "in the -wal sidecar on the tested device, so the sidecar is in the paths and is "
                 "required. The package is com.kunzisoft.keepass with a store-specific suffix "
                 "(.libre on F-Droid, .free on Google Play), so the paths accept any suffix.",
        "paths": ('*/com.kunzisoft.keepass*/databases/com.kunzisoft.keepass.database*',),
        "output_types": "standard",
        "artifact_icon": "key",
        "sample_data": {
            "emu_a15_oss_v2": "Android 15 | com.kunzisoft.keepass.libre vc 45100 | 1 rows",
        },
    }
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/com.kunzisoft.keepass.database'


def _db_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(DB_SUFFIX)]


def _ms(value):
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value) // 1000)
    except (TypeError, ValueError):
        return ''


def _bool(value):
    if value in (1, '1'):
        return 'Yes'
    if value in (0, '0'):
        return 'No'
    return ''


@artifact_processor
def keepassdx_database_history(context):
    query = '''SELECT h.updated, h.database_uri, h.database_alias, h.keyfile_uri,
                      h.hardware_key, h.read_only, h.user_verification,
                      CASE WHEN c.database_uri IS NOT NULL THEN 1 ELSE 0 END AS quick_unlock
               FROM file_database_history h
               LEFT JOIN cipher_database c ON c.database_uri = h.database_uri
               ORDER BY h.updated DESC'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        if not records:
            continue
        for r in records:
            data_list.append((
                _ms(r[0]), r[1] or '', r[2] or '', r[3] or '', r[4] or '',
                _bool(r[5]), _bool(r[6]), _bool(r[7]),
                context.get_relative_path(db_path),
            ))
        if db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Updated', 'datetime'), 'Database URI', 'Database Alias', 'Keyfile URI',
        'Hardware Key', 'Read Only', 'User Verification', 'Quick Unlock Credential Stored',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)
