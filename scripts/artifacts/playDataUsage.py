__artifacts_v2__ = {
    "playDataUsage": {
        "name": "Google Play Store - App Data Usage",
        "description": "Rows of the app_data_usage table of the Google Play Store's data_usage.db: per "
                       "app and date, the bytes recorded with the connection type, foreground state, "
                       "metered state, roaming state and data usage type stored beside them.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "Reads the app_data_usage table of each data_usage.db in the Play Store's databases "
                 "folder; one row per table row. The meanings below come from the Play Store build "
                 "installed on pixel7a_a14 (base.apk, SHA-256 "
                 "4b600ace4af875f579a607d79ae2bcf63fb033032d2a37ae8aa89d752f5ad98d), decompiled with jadx "
                 "1.5.6; its class names are obfuscated and differ between builds, and other builds were "
                 "not decompiled. In that build the code that fills the table reads Android's "
                 "NetworkStats for each app: Package is the package name for the bucket's uid, Date is "
                 "the bucket's start time converted to a date in the device's time zone, and Bytes is "
                 "the bucket's received bytes plus transmitted bytes, summed with any existing record of "
                 "the same package, date and states. Bytes is field 8 of the row's data blob, decoded "
                 "without a schema; the blob's fields 1 to 7 equalled the package_name, date, "
                 "connection_type, foreground_state, metered_state, roaming_state and data_usage_type "
                 "columns on all 94,948 rows of the tested databases, duplicate storage copies "
                 "included, so field 8 is the one value the columns do not "
                 "hold, and it was present on every row. Date is reported as stored: the column is "
                 "declared INTEGER but held text in YYYY-MM-DD form on every tested row, a local "
                 "calendar date rather than a moment in time. Connection Type, Foreground State, "
                 "Metered State, Roaming State and Data Usage Type are the stored integers with the "
                 "name each value has in that build's enum classes. Data Usage Type was 1 (IN_APP) on "
                 "76,556 of the 78,474 rows reported on the tested images, the rest being install and "
                 "update types; Roaming State held one value, 2 (NOT_ROAMING), on every row of "
                 "pixel7a_a14. Android User is the user whose app data folder holds the database; the "
                 "same database under data/data, data/user/0 and data_mirror is read once, and the "
                 "second users on cookbook_a11 and samsungs20_a13 (150) and russell_a14 and "
                 "russell_pixel6a_a13 (10) were reported separately; Android User held one value on "
                 "every row of the single-user images. Not reported: the app_data_usage_audit table, which "
                 "held no rows on any tested image.",
        "paths": ('*/com.android.vending/databases/data_usage.db*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 1,600 rows",
            "anne_a15": "Android 15 | 5,985 rows",
            "cookbook_a11": "Android 11 | 4,088 rows (user 0 1,717, user 150 2,371)",
            "falken_a326u_a13": "Android 13 | 3,865 rows",
            "galaxys10_a10": "Android 10 | 2,485 rows",
            "hc_pixel8pro_a16": "Android 16 | 992 rows",
            "hc_pixel8pro_a17": "Android 17 | 3,814 rows",
            "hickman_a13": "Android 13 | 1,770 rows",
            "kevin_pocox7_a15": "Android 15 | 23,805 rows",
            "pixel3_a11": "Android 11 | 2,632 rows",
            "pixel3_a12": "Android 12 | 1,293 rows",
            "pixel7a_a14": "Android 14 | 2,926 rows",
            "russell_a14": "Android 14 | 3,957 rows (user 0 2,689, user 10 1,268)",
            "russell_pixel6a_a13": "Android 13 | 2,225 rows (user 0 1,409, user 10 816)",
            "s20fe_a13": "Android 13 | 596 rows",
            "samsunga53_a14": "Android 14 | 4,167 rows",
            "samsungs20_a13": "Android 13 | 3,926 rows (user 0 3,416, user 150 510)",
            "sharon_a13": "Android 13 | 2,585 rows",
            "sharon_a14": "Android 14 | 4,611 rows",
            "userb2_a13": "Android 13 | 1,152 rows",
        },
    }
}

import sqlite3

from scripts.ilapfuncs import artifact_processor, decode_protobuf, logfunc, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import user_files

# Enum constants as named in the Play Store's own classes (see notes for the build read).
_CONNECTION = {0: 'UNKNOWN', 1: 'NONE', 2: 'WIRED', 3: 'WIFI', 4: 'TWO_G', 5: 'THREE_G',
               6: 'FOUR_G', 7: 'CELLULAR_UNKNOWN', 8: 'BLUETOOTH', 9: 'FIVE_G'}
_FOREGROUND = {0: 'FOREGROUND_STATE_UNKNOWN', 1: 'FOREGROUND', 2: 'BACKGROUND'}
_METERED = {0: 'NETWORK_UNKNOWN', 1: 'METERED', 2: 'UNMETERED'}
_ROAMING = {0: 'ROAMING_STATE_UNKNOWN', 1: 'ROAMING', 2: 'NOT_ROAMING'}
_USAGE_TYPE = {0: 'UNKNOWN', 1: 'IN_APP', 2: 'INSTALL', 3: 'AUTO_UPDATE', 4: 'MANUAL_UPDATE',
               5: 'UPDATE_UNKNOWN', 6: 'SPLIT_UPDATE', 7: 'USER_LANGUAGE_CHANGE_UPDATE'}


def _named(value, names):
    if not isinstance(value, int):
        return value if value is not None else ''
    name = names.get(value)
    return f'{value} ({name})' if name else str(value)


def _bytes(blob):
    """Field 8 of the row's data blob, the byte count the Play Store stores with the row."""
    if not blob:
        return ''
    try:
        message, _ = decode_protobuf(blob)
    except Exception:  # pylint: disable=broad-exception-caught
        # blackboxprotobuf raises several unrelated types on a malformed blob.
        return ''
    value = message.get('8')
    return value if isinstance(value, int) else ''


@artifact_processor
def playDataUsage(context):
    data_list = []
    sources = []
    for path, user in user_files(context, 'data_usage.db'):
        if '/com.android.vending/' not in str(context.get_relative_path(path)).replace('\\', '/'):
            continue
        db = open_sqlite_db_readonly(path)
        if db is None:
            continue
        try:
            rows = db.execute('''
                SELECT date, package_name, data, data_usage_type, connection_type,
                       foreground_state, metered_state, roaming_state
                FROM app_data_usage ORDER BY date, package_name, pk''').fetchall()
        except sqlite3.Error as ex:
            logfunc(f'Play App Data Usage: could not read {context.get_relative_path(path)}: {ex}')
            continue
        finally:
            db.close()
        sources.append(path)
        for date, package, blob, usage_type, connection, foreground, metered, roaming in rows:
            data_list.append((date if date is not None else '', package, _bytes(blob),
                              _named(usage_type, _USAGE_TYPE), _named(connection, _CONNECTION),
                              _named(foreground, _FOREGROUND), _named(metered, _METERED),
                              _named(roaming, _ROAMING), user))

    data_headers = ('Date', 'Package', 'Bytes', 'Data Usage Type', 'Connection Type',
                    'Foreground State', 'Metered State', 'Roaming State', 'Android User')
    return data_headers, data_list, '\n'.join(sources)
