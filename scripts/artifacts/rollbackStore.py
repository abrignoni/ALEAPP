__artifacts_v2__ = {
    "rollbackStore": {
        "name": "Package Rollbacks",
        "description": "Rollback records kept by Android's RollbackManager in data/rollback and "
                       "data/rollback-history: one row per package of each record, with the record's "
                       "time, state and state description, and the package's two version codes.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-27",
        "last_update_date": "2026-10-27",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "Reads the rollback.json in each folder of data/rollback (records the system still "
                 "held) and data/rollback-history (records it had deleted). One row per package listed "
                 "in a record, with the record's own fields repeated, so rows that share a Rollback ID "
                 "and Folder are one record. The format and the meanings below come from AOSP "
                 "frameworks/base at tag android-14.0.0_r1 (commit "
                 "299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368), "
                 "services/core/java/com/android/server/rollback; line numbers are in that commit. "
                 "RollbackStore.java#313 writes the file; when a record is deleted it is saved again "
                 "under data/rollback-history in a folder named for the rollback ID and its time in "
                 "seconds as hex (RollbackStore.java#348). A record does not mean a package was rolled "
                 "back. The system makes one when an install asks for rollback to be enabled, and the "
                 "version columns carry the AOSP field names: versionRolledBackFrom is the version being "
                 "installed and versionRolledBackTo the version installed before it "
                 "(Rollback.java#389-390). For a package inside an APEX (Is APK in APEX true) the code "
                 "writes 0 as the version being installed (Rollback.java#413), and all 1,466 such rows "
                 "on the tested images held 0. A committed record, which is an actual rollback, has "
                 "state committed, a Committed Session ID other than -1 (Rollback.java#657) and Cause "
                 "Packages; none of the 319 records on the tested images was committed: Committed Session "
                 "ID held -1 on every row and Cause Packages was empty on every row, so that path was "
                 "not exercised. "
                 "Timestamp is the record's time as stored, in UTC. It is set when the record is made "
                 "(Rollback.java#219) and again when the rollback becomes available (Rollback.java#477), "
                 "and while the system holds the record it is moved by the size of any clock change "
                 "(RollbackManagerServiceImpl.java#425). Deleting a record does not change it, so on a "
                 "rollback-history row it is not the time of deletion, and the file stores no deletion "
                 "time. On all 291 history folders on the tested images the hex part of the folder name "
                 "equalled the Timestamp in seconds. 25 records on hc_pixel8pro_a16, hc_pixel8pro_a17, "
                 "russell_a14 and sharon_a14 carried times after 2026-10-27, up to 2035; their cause was "
                 "not established. State is as stored: enabling, available, committed or deleted "
                 "(Rollback.java#847-850). Every history record held deleted, and the 28 records in "
                 "data/rollback held available (23) or enabling (5). Folder and State held one value on every row of "
                 "adams_ss135dl_a13 and sharon_a14 (rollback-history, deleted) and of falken_a326u_a13 "
                 "and s20fe_a13 (rollback, available), which held files in only one of the two folders. State Description holds, on a "
                 "deleted record, the reason passed when it was deleted (Rollback.java#731), as stored. RollbackManagerServiceImpl.java passes 'Fingerprint "
                 "changed' when, on loading the records, the package manager reported the device upgrading "
                 "(#206), which its documentation describes as 'such as first boot "
                 "after OTA' (core/java/android/content/pm/PackageManager.java#9728); 'Package <name> "
                 "replaced' when a package of an available record is found at another version (#665); "
                 "'Expired by timeout' once the record's lifetime, 14 days by default, has passed (#719, "
                 "#133); 'Session <n> failed' (#1114); 'Failed to enable rollback for all packages in "
                 "session' (#1140); and 'Rollback canceled' (#271). On the tested images these occurred "
                 "93, 92, 56, 47, 2 and 1 times; the source's other reasons ('Package <name> removed', "
                 "'Expired by API', 'Session <n> not existed or failed') did not occur. Is Staged is "
                 "isStaged, documented as the rollback needing a reboot to take effect once committed "
                 "(core/java/android/content/rollback/RollbackInfo.java#82); it was true on 292 records "
                 "and false on 27, and on russell_a14 Is Staged held true on every row. Rollback Lifetime ms is "
                 "rollbackLifetimeMillis as stored, a field the writer adds at tag android-15.0.0_r1 "
                 "(commit 4e43ad12e1b211f15152e9c5b16b0fe88e6b93f3, RollbackStore.java#328); it held 0 "
                 "on 90 records and 86400000 on 4, and was absent on 225, so Rollback Lifetime ms is "
                 "blank on every row of the Android 14 and earlier images. 13 records on galaxys10_a10, "
                 "pixel3_a11, pixel3_a12, sharon_a13 and sharon_a14 use an older layout with "
                 "stagedSessionId instead of originalSessionId; Original Session ID falls back to it as "
                 "the AOSP reader does (RollbackStore.java#384). The one record on galaxys10_a10 has no "
                 "userId, stateDescription, installerPackageName or isApkInApex, so User ID, State "
                 "Description, Installer Package Name and Is APK in APEX are blank on its row. 2 "
                 "records on kevin_pocox7_a15, both deleted with 'Failed to enable rollback for all "
                 "packages in session', listed no packages; each gives one row with the package cells "
                 "blank. On the "
                 "tested images Installer Package Name held com.android.vending on every row that "
                 "stored one, User ID held 0 on every row that stored one, and every package was named com.google.* (3,715 rows) or "
                 "com.android.* (58). Not reported: the copies of the earlier package versions kept in "
                 "data/rollback/<id>/<package>/, and the app data snapshots under "
                 "data/misc_ce/<user>/rollback and data/misc_de/<user>/rollback, which this artifact "
                 "does not read. A rollback.json inside an app's own data folder is not read. The files "
                 "on the Samsung images adams_ss135dl_a13, falken_a326u_a13, galaxys10_a10 and s20fe_a13 "
                 "carried the keys the AOSP writer writes (galaxys10_a10 those of android-10.0.0_r1, the "
                 "other three those of android-14.0.0_r1). "
                 "cookbook_a11, samsunga53_a14, samsungs20_a13 and the two emulator images held no "
                 "rollback.json.",
        "paths": ('*/data/rollback/*/rollback.json', '*/data/rollback-history/*/rollback.json'),
        "output_types": "standard",
        "artifact_icon": "rotate-ccw",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 117 rows",
            "anne_a15": "Android 15 | 261 rows",
            "cookbook_a11": "Android 11 | 0 rows",
            "emu_a15_oss2_v3": "Android 15 | 0 rows",
            "emu_a15_oss_v17": "Android 15 | 0 rows",
            "falken_a326u_a13": "Android 13 | 38 rows",
            "galaxys10_a10": "Android 10 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | 358 rows",
            "hc_pixel8pro_a17": "Android 17 | 409 rows",
            "hickman_a13": "Android 13 | 188 rows",
            "kevin_pocox7_a15": "Android 15 | 279 rows",
            "pixel3_a11": "Android 11 | 1 row",
            "pixel3_a12": "Android 12 | 40 rows",
            "pixel7a_a14": "Android 14 | 329 rows",
            "russell_a14": "Android 14 | 794 rows",
            "russell_pixel6a_a13": "Android 13 | 115 rows",
            "s20fe_a13": "Android 13 | 38 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 153 rows",
            "sharon_a14": "Android 14 | 609 rows",
            "userb2_a13": "Android 13 | 45 rows",
        },
    }
}

import datetime
import json
import os
import re

from scripts.ilapfuncs import artifact_processor, logfunc

# Instant.toString(): 2024-03-13T12:34:56Z with 0, 3, 6 or 9 fraction digits.
_INSTANT = re.compile(r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,9}))?Z$')


def _instant(value):
    match = _INSTANT.match(value or '')
    if not match:
        return ''
    stamp = datetime.datetime.strptime(match.group(1), '%Y-%m-%dT%H:%M:%S')
    micros = int((match.group(2) or '0').ljust(9, '0')[:6])
    return stamp.replace(microsecond=micros, tzinfo=datetime.timezone.utc)


# RollbackStore folder names: data/rollback/<rollbackId>, data/rollback-history/<rollbackId>-<hex>.
_FOLDER = {'rollback': re.compile(r'^\d+$'), 'rollback-history': re.compile(r'^\d+-[0-9a-f]+$')}


_PACKAGE = re.compile(r'^[A-Za-z]\w*(\.[A-Za-z_]\w*)+$')


def _in_app_folder(parts):
    """True when the path runs through an app's data folder: data/<package>/ or
    user[_de]/<n>/<package>/."""
    for i, part in enumerate(parts):
        if not _PACKAGE.match(part):
            continue
        if i >= 1 and parts[i - 1] == 'data':
            return True
        if i >= 2 and parts[i - 1].isdigit() and parts[i - 2] in ('user', 'user_de'):
            return True
    return False


def _store(path):
    """'rollback' or 'rollback-history' when path ends data/<store>/<folder>/rollback.json
    with RollbackStore's folder naming, outside any app's data folder."""
    parts = path.replace('\\', '/').split('/')
    if len(parts) < 4 or parts[-1] != 'rollback.json' or parts[-4] != 'data':
        return None
    store, folder = parts[-3], parts[-2]
    if store not in _FOLDER or not _FOLDER[store].match(folder) or _in_app_folder(parts[:-4]):
        return None
    return store


def _as_stored(value):
    if value is None:
        return ''
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return value


def _version(package, key):
    versioned = package.get(key) or {}
    return versioned.get('packageName', ''), _as_stored(versioned.get('longVersionCode'))


def _cause_packages(info):
    return '\n'.join(f"{p.get('packageName', '')} {p.get('longVersionCode', '')}".strip()
                     for p in info.get('causePackages') or [] if isinstance(p, dict))


@artifact_processor
def rollbackStore(context):
    data_list = []
    sources = []
    seen = set()
    for path in context.get_files_found():
        path = str(path)
        store = _store(path)
        if store is None:
            continue
        key = (store, os.path.basename(os.path.dirname(path)))
        if key in seen:
            continue
        seen.add(key)
        try:
            with open(path, 'rb') as fh:
                record = json.loads(fh.read().decode('utf-8'))
            info = record['info']
        except (OSError, UnicodeDecodeError, ValueError, KeyError, TypeError) as ex:
            logfunc(f'Package Rollbacks: could not read {context.get_relative_path(path)}: {ex}')
            continue
        sources.append(path)
        packages = [p for p in info.get('packages') or [] if isinstance(p, dict)]
        session = record.get('originalSessionId', record.get('stagedSessionId', ''))
        shared = (_instant(record.get('timestamp')),
                  record.get('state', ''),
                  record.get('stateDescription', ''))
        tail = (_as_stored(info.get('rollbackId')),
                store,
                _as_stored(info.get('isStaged')),
                _as_stored(session),
                _as_stored(info.get('committedSessionId')),
                _cause_packages(info),
                record.get('installerPackageName', ''),
                _as_stored(record.get('userId')),
                _as_stored(record.get('rollbackLifetimeMillis')))
        if not packages:
            logfunc(f'Package Rollbacks: no packages in {context.get_relative_path(path)}')
            data_list.append(shared + ('', '', '', '', '') + tail)
            continue
        for package in packages:
            name, installing = _version(package, 'versionRolledBackFrom')
            to_name, before = _version(package, 'versionRolledBackTo')
            data_list.append(shared + (name or to_name, before, installing,
                                       _as_stored(package.get('isApex')),
                                       _as_stored(package.get('isApkInApex'))) + tail)

    data_headers = (('Timestamp', 'datetime'), 'State (as stored)', 'State Description (as stored)',
                    'Package Name', 'Version Before Install (versionRolledBackTo)',
                    'Version Being Installed (versionRolledBackFrom)', 'Is APEX', 'Is APK in APEX',
                    'Rollback ID', 'Folder', 'Is Staged', 'Original Session ID',
                    'Committed Session ID', 'Cause Packages', 'Installer Package Name', 'User ID',
                    'Rollback Lifetime ms (as stored)')
    return data_headers, data_list, '\n'.join(sources)
