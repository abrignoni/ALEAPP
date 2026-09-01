__artifacts_v2__ = {
    "aurora_store_accounts": {
        "name": "Aurora Store - Accounts",
        "description": "Parses the signed-in account from the Aurora Store Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "Aurora Store",
        "sample_data": {
            "emu_a15_oss_v6": "Aurora Store 4.8.4 | 1 rows",
        },
        "notes": "One row per entry in the account table of databases/aurora_database. Aurora "
                 "Store is an open source client for Google Play. Each row is a session the app "
                 "holds, with the Email and Display Name it carries, the Account Type, and Added "
                 "which is Unix milliseconds reported as UTC. Account Type is the app's own value "
                 "and is reported as stored; on the tested device it read ANONYMOUS, which is the "
                 "app's shared-account mode, so the email shown belongs to an account the project "
                 "operates rather than to the person using the device. A GOOGLE value in that "
                 "column is the other case the app offers and would carry the signed-in person's "
                 "own address, so the Account Type is what decides whether the Email identifies "
                 "anyone. The stored auth and AAS tokens are credentials and are deliberately not "
                 "reported. The row records that Aurora Store was set up on this device and when, "
                 "which is what bounds the periods the other Aurora artifacts can cover.",
        "paths": ('*/com.aurora.store/databases/aurora_database*',),
        "output_types": "standard",
        "artifact_icon": "user",
    },
    "aurora_store_downloads": {
        "name": "Aurora Store - Downloads",
        "description": "Parses the app download history from the Aurora Store Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "Aurora Store",
        "sample_data": {
            "emu_a15_oss_v6": "Aurora Store 4.8.4 | 0 rows, checked: the download table is present and empty",
        },
        "notes": "One row per entry in the download table of databases/aurora_database. Each row "
                 "is an app Aurora Store was asked to download, with its Package, Display Name, "
                 "Version Code, Size in bytes, the Download Status as the app records it, how "
                 "many of the expected files arrived, the Target SDK, whether the app Requires "
                 "GMS, and Downloaded At as Unix milliseconds reported as UTC. Installed is the "
                 "app's flag for a download it went on to install. The download table was present "
                 "and empty on the tested device because no app was downloaded through Aurora "
                 "Store there, so the columns are described from the schema and the app's own "
                 "source rather than from decoded rows; a sample carrying a completed download "
                 "would close that gap. The related update and ignored_update tables, which hold "
                 "the updates Aurora offered and the ones a person chose to ignore, were likewise "
                 "present and empty and are reported by the Updates artifact.",
        "paths": ('*/com.aurora.store/databases/aurora_database*',),
        "output_types": "standard",
        "artifact_icon": "download",
    },
    "aurora_store_favourites": {
        "name": "Aurora Store - Favourites",
        "description": "Parses favourited apps from the Aurora Store Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "Aurora Store",
        "sample_data": {
            "emu_a15_oss_v6": "Aurora Store 4.8.4 | 1 rows",
        },
        "notes": "One row per entry in the favourite table of databases/aurora_database. A "
                 "favourite is an app marked in Aurora Store's own list, which is a deliberate "
                 "action rather than something the app records on its own, so a row shows an app "
                 "someone singled out without necessarily installing it. Each row carries the "
                 "Package, the Display Name, Added as Unix milliseconds reported as UTC, and Mode "
                 "which is the app's own value for how the entry was created and is reported as "
                 "stored; the tested device recorded MANUAL for an entry added from an app's page. "
                 "On the tested device one app was favourited and never downloaded, which is the "
                 "distinction this artifact exists to show against the Downloads artifact.",
        "paths": ('*/com.aurora.store/databases/aurora_database*',),
        "output_types": "standard",
        "artifact_icon": "star",
    },
    "aurora_store_updates": {
        "name": "Aurora Store - Updates and Reviews",
        "description": "Parses pending updates and written reviews from the Aurora Store Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "Aurora Store",
        "sample_data": {
            "emu_a15_oss_v6": "Aurora Store 4.8.4 | 0 rows, checked: the update and review tables are present and empty",
        },
        "notes": "Rows from the update and review tables of databases/aurora_database, combined "
                 "because both key on a package and both were empty on the tested device. An "
                 "update row is an update Aurora found for an installed app, with its Package, "
                 "Version Name and Code, Developer, Size and the Updated On date, and it records "
                 "what the app offered rather than anything a person did. A review row is the "
                 "opposite: it is text someone wrote, with the Title, Comment, Rating and the "
                 "account Email it was posted under, so it is user-authored content tied to an "
                 "identity. Kind names which table a row came from. Both tables were present and "
                 "empty on the tested device, where no app was installed through Aurora Store and "
                 "no review was written, so this artifact is a checked absence there; the columns "
                 "come from the schema. The ignored_update table holds only a package and a "
                 "version code for updates a person dismissed and is named here rather than given "
                 "its own artifact. The exodus_tracker table held 432 rows on the tested device "
                 "and is the Exodus Privacy tracker catalogue the app downloads for its privacy "
                 "reports, so it is reference data rather than device activity and is not parsed.",
        "paths": ('*/com.aurora.store/databases/aurora_database*',),
        "output_types": "standard",
        "artifact_icon": "refresh-cw",
    },
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/aurora_database'


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


def _yesno(value):
    if value in (1, '1'):
        return 'Yes'
    if value in (0, '0'):
        return 'No'
    return ''


@artifact_processor
def aurora_store_accounts(context):
    query = '''SELECT addedAt, email, displayName, type, isDefault, authViaMicroG, id
               FROM account ORDER BY addedAt DESC'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((_ms(r[0]), r[1] or '', r[2] or '', r[3] or '',
                              _yesno(r[4]), _yesno(r[5]), r[6] or '',
                              context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (('Added', 'datetime'), 'Email', 'Display Name',
                    'Account Type (as stored)', 'Default', 'Via microG', 'Account ID',
                    'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def aurora_store_downloads(context):
    query = '''SELECT downloadedAt, displayName, packageName, versionCode, size,
                      downloadStatus, isInstalled, totalFiles, downloadedFiles,
                      targetSdk, requiresGMS, id
               FROM download ORDER BY downloadedAt DESC'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((_ms(r[0]), r[1] or '', r[2] or '', r[3], r[4],
                              r[5] or '', _yesno(r[6]), r[7], r[8], r[9],
                              _yesno(r[10]), r[11],
                              context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (('Downloaded At', 'datetime'), 'Display Name', 'Package',
                    'Version Code', 'Size (bytes)', 'Download Status (as stored)',
                    'Installed', 'Total Files', 'Downloaded Files', 'Target SDK',
                    'Requires GMS', 'Download ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def aurora_store_favourites(context):
    query = '''SELECT added, displayName, packageName, mode
               FROM favourite ORDER BY added DESC'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((_ms(r[0]), r[1] or '', r[2] or '', r[3] or '',
                              context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (('Added', 'datetime'), 'Display Name', 'Package',
                    'Mode (as stored)', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def aurora_store_updates(context):
    update_query = '''SELECT updatedOn, displayName, packageName, versionName, versionCode,
                             developerName, size, changelog
                      FROM "update"'''
    review_query = '''SELECT timeStamp, packageName, title, comment, rating, accountEmail,
                             userName, appVersion
                      FROM review'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        seen = False
        for r in get_sqlite_db_records(db_path, update_query):
            seen = True
            data_list.append(('Update', _ms(r[0]), r[1] or '', r[2] or '', r[3] or '',
                              r[4], r[5] or '', r[6], '', '', r[7] or '',
                              context.get_relative_path(db_path)))
        for r in get_sqlite_db_records(db_path, review_query):
            seen = True
            data_list.append(('Review', _ms(r[0]), r[6] or '', r[1] or '', r[7] or '',
                              '', '', '', r[4], r[5] or '', f'{r[2] or ""} {r[3] or ""}'.strip(),
                              context.get_relative_path(db_path)))
        if seen and db_path not in sources:
            sources.append(db_path)

    data_headers = ('Kind', ('Timestamp', 'datetime'), 'Display Name', 'Package',
                    'Version', 'Version Code', 'Developer', 'Size (bytes)', 'Rating',
                    'Account Email', 'Text', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
