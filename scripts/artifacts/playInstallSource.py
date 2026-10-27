__artifacts_v2__ = {
    "playInstallSource": {
        "name": "Google Play Store - Install Source",
        "description": "Rows of the install_source table of the Google Play Store's install_source.db: "
                       "per package, the install reason the Play Store stored for it, with the name "
                       "that reason has in the Play Store's own enum.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "Reads the install_source table of each install_source.db in the Play Store's databases "
                 "folder; one row per table row. The meanings below come from the Play Store build "
                 "installed on pixel7a_a14 (base.apk, SHA-256 "
                 "4b600ace4af875f579a607d79ae2bcf63fb033032d2a37ae8aa89d752f5ad98d), decompiled with jadx "
                 "1.5.6; its class names are obfuscated and can differ between builds, and other builds "
                 "were not decompiled. In that build each row's data blob is an InstallSourceInfo record "
                 "(the name its parse error message uses) with two fields: field 1 the package name and "
                 "field 2 the install reason, an enum of 83 values; Install Reason is that value as "
                 "stored with the name it has in the build's enum class. The blob is decoded with those "
                 "two field types; field 1 equalled the row's pk on all 2,231 rows of the tested "
                 "databases, duplicate storage copies included. The record is written by a listener that "
                 "logs itself as InstallSourceListener: when an install reaches one state (6) it writes "
                 "or replaces the package's record with that install's reason, and at another (8) it "
                 "removes the record. The names of those two states were not resolved in the decompiled "
                 "build. The stored reason is therefore the one from the package's most recent such "
                 "event, so a package installed by hand and later updated through the Play Store is "
                 "expected to show the update's reason (inferred from the code, not tested with known "
                 "data). On pixel7a_a14, sharon_a14 and russell_a14, 1, 16 and 6 rows named a package "
                 "not listed in data/system/packages.list, so a row is not evidence that the package is "
                 "still installed. Across the 1,620 rows reported on the tested images the reasons were "
                 "AUTO_UPDATE (923), BULK_UPDATE (285), SINGLE_INSTALL (175), BULK_INSTALL (102), "
                 "RESTORE_VPA (75), NDE_APP_REINSTALL (17, all on samsungs20_a13), "
                 "SELF_UPDATE_VIA_AUTO_UPDATE (13) and seven others with 8 rows or fewer. The "
                 "install_source table carries no time. The database also has an install_source_audit "
                 "table with a timestamp column; it was empty in every copy on the tested images and is "
                 "not reported. Android User is the user whose app data folder holds the database; "
                 "the same database under data/data, data/user/0 and data_mirror is read once, and the "
                 "second users on cookbook_a11 and samsungs20_a13 (150) and russell_a14 and "
                 "russell_pixel6a_a13 (10) were reported separately.",
        "paths": ('*/com.android.vending/databases/install_source.db*',),
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 60 rows",
            "anne_a15": "Android 15 | 63 rows",
            "cookbook_a11": "Android 11 | 44 rows",
            "falken_a326u_a13": "Android 13 | 33 rows",
            "galaxys10_a10": "Android 10 | 26 rows",
            "hc_pixel8pro_a16": "Android 16 | 110 rows",
            "hc_pixel8pro_a17": "Android 17 | 115 rows",
            "hickman_a13": "Android 13 | 129 rows",
            "kevin_pocox7_a15": "Android 15 | 68 rows",
            "pixel3_a11": "Android 11 | 80 rows",
            "pixel3_a12": "Android 12 | 103 rows",
            "pixel7a_a14": "Android 14 | 119 rows",
            "russell_a14": "Android 14 | 154 rows",
            "russell_pixel6a_a13": "Android 13 | 71 rows",
            "s20fe_a13": "Android 13 | 31 rows",
            "samsunga53_a14": "Android 14 | 61 rows",
            "samsungs20_a13": "Android 13 | 105 rows",
            "sharon_a13": "Android 13 | 72 rows",
            "sharon_a14": "Android 14 | 102 rows",
            "userb2_a13": "Android 13 | 74 rows",
        },
    }
}

import sqlite3

from scripts.ilapfuncs import artifact_processor, decode_protobuf, logfunc, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import user_files

# The install reason enum of the Play Store build named in the notes, values 0 to 82 in order.
_REASONS = (
    'UNKNOWN', 'SINGLE_INSTALL', 'BULK_INSTALL', 'DEPENDENCY', 'BULK_UPDATE', 'AUTO_UPDATE',
    'RAPID_AUTO_UPDATE', 'EARLY_UPDATE', 'TICKLE', 'SUICIDAL_TABSKY', 'RESTORE', 'RESTORE_VPA',
    'AUTO_UPDATE_DAILY_HYGIENE', 'AUTO_UPDATE_WIFI_CHECKER', 'SELF_UPDATE_LEGACY',
    'SELF_UPDATE_V2', 'WEAR_AUTO_UPDATE', 'WEAR_AUTO_INSTALL', 'CONTENT_DEPENDENCY',
    'SELF_UPDATE_VIA_DAILY_HYGIENE', 'SELF_UPDATE_NOTIFICATION', 'SELF_UPDATE_NOTIFICATION_RETRY',
    'PACKAGE_UPDATE_SERVICE', 'GMS_CORE_UPDATE_SERVICE', 'ISOTOPE_INSTALL', 'ARC_INSTALL',
    'WEBAPK_INSTALL', 'DEVICE_OWNER_INSTALL', 'MAINTENANCE_WINDOW', 'SPLIT_INSTALL_SERVICE',
    'DEVELOPER_TRIGGERED_UPDATE', 'RECOMMENDED', 'P2P_INSTALL', 'P2P_UPDATE', 'EC_CHOICE_INSTALL',
    'SPLIT_DEFERRED_INSTALL', 'RESTORE_RRO_VPA', 'ARC_DIRECT_PUSH_INSTALL',
    'ENTERPRISE_AUTO_INSTALL', 'PLAY_PROTECT_LINK', 'RECOVERY_EVENTS',
    'RESUME_OFFLINE_ACQUISITION', 'SYNCHRONIZED_GMS_UPDATE', 'USER_LANGUAGE_CHANGE', 'DSE_INSTALL',
    'PREREG_AUTO_INSTALL', 'INTERNAL_SHARING_LINK', 'HISTORICAL_VERSION_LINK', 'ASSET_MODULE',
    'BATTLESTAR_INSTALL', 'APP_PACK_INSTALL', 'SELF_UPDATE_VIA_LOCALE_CHANGE',
    'DEVICE_LOCK_CONTROLLER_INSTALL', 'ENX_HEADLESS_INSTALL', 'SELF_UPDATE_VIA_SETTINGS',
    'SELF_UPDATE_VIA_DEBUG', 'SELF_UPDATE_VIA_TOC', 'USER_LANGUAGE_CHANGE_RETRY',
    'USER_LANGUAGE_CHANGE_DEFERRED', 'APP_LANGUAGE_CHANGE', 'SELF_UPDATE_ENTERPRISE_SETUP_POLICY',
    'MANUAL_HIBERNATION', 'PAI_HIBERNATION', 'UNHIBERNATION', 'SUGGESTED_UPDATE', 'KEY_RESCUE',
    'AUTO_HIBERNATION', 'TIMESLICED_SSU', 'REMOTE_INSTALL', 'REMOTE_IN_APP_UPDATE',
    'DETAILS_PAGE_UNHIBERNATION', 'KIDS_SPACE_INSTALL', 'UNARCHIVE_FROM_STORE',
    'SELF_UPDATE_VIA_AUTO_UPDATE', 'APP_SYNC_REMOTE_INSTALL', 'APP_RECOVERY_SPLIT_INSTALL',
    'REMOTE_UPDATE_PROMPT', 'AUTOMATIC_SSU', 'UNARCHIVE_BROADCAST', 'MAINLINE_MANUAL_UPDATE',
    'MAINLINE_AUTO_UPDATE', 'RESTORE_PRE_ARCHIVE', 'NDE_APP_REINSTALL',
)
# InstallSourceInfo: field 1 the package name, field 2 the reason.
_TYPEDEF = {'1': {'type': 'bytes', 'name': ''}, '2': {'type': 'int', 'name': ''}}


def _reason(value):
    if not isinstance(value, int):
        return ''
    if 0 <= value < len(_REASONS):
        return f'{value} ({_REASONS[value]})'
    return str(value)


@artifact_processor
def playInstallSource(context):
    data_list = []
    sources = []
    for path, user in user_files(context, 'install_source.db'):
        if '/com.android.vending/' not in str(context.get_relative_path(path)).replace('\\', '/'):
            continue
        db = open_sqlite_db_readonly(path)
        if db is None:
            continue
        try:
            rows = db.execute('SELECT pk, data FROM install_source ORDER BY pk').fetchall()
        except sqlite3.Error as ex:
            logfunc(f'Play Install Source: could not read {context.get_relative_path(path)}: {ex}')
            continue
        finally:
            db.close()
        sources.append(path)
        for package, blob in rows:
            reason = ''
            if blob:
                try:
                    message, _ = decode_protobuf(blob, _TYPEDEF)
                    reason = _reason(message.get('2'))
                except Exception:  # pylint: disable=broad-exception-caught
                    # blackboxprotobuf raises several unrelated types on a malformed blob.
                    logfunc(f'Play Install Source: record for {package} not decoded')
            data_list.append((package, reason, user))

    data_headers = ('Package', 'Install Reason', 'Android User')
    return data_headers, data_list, '\n'.join(sources)
