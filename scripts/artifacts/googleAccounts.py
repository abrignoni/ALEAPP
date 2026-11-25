import datetime
import hashlib
import sqlite3
from pathlib import Path

from scripts.ilapfuncs import artifact_processor, get_file_path_list_checking_uid, logfunc, \
    open_sqlite_db_readonly

__artifacts_v2__ = {
    "googleAccounts": {
        "name": "Google Accounts",
        "description": "Google accounts (type com.google) in each Android user's accounts_ce.db, with the "
                       "GoogleUserId, firstName and lastName values stored for the account in its extras "
                       "table, and GoogleUserIdRefreshTime shown as a UTC time.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-15",
        "last_update_date": "2026-11-15",
        "requirements": "none",
        "category": "Accounts & Credentials",
        "notes": "One row per accounts row of type com.google in each accounts_ce.db under system_ce/<user>; Android User is that folder name. accounts_ce.db is the Android account service's CE database (https://github.com/aosp-mirror/platform_frameworks_base/blob/299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368/services/core/java/com/android/server/accounts/AccountsDb.java#L135), and its extras table holds key and value text per account (https://github.com/aosp-mirror/platform_frameworks_base/blob/299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368/services/core/java/com/android/server/accounts/AccountsDb.java#L224-L229, tag android-14.0.0_r1). In AOSP at that tag, the platform writes extras from the bundle given when an account is added (https://github.com/aosp-mirror/platform_frameworks_base/blob/299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368/services/core/java/com/android/server/accounts/AccountManagerService.java#L1889-L1892) and through setUserData, which accepts only a caller that manages the account type (AccountManagerService.java#L2797-L2821), and it deletes an account's extras with the account (AccountsDb.java#L234-L242), so by the source a removed account leaves no row; no tested image has a known removed account. The key names GoogleUserId, firstName, lastName and GoogleUserIdRefreshTime do not appear in AccountsDb.java or AccountManagerService.java at that commit; the columns carry those names. firstName, lastName and GoogleUserId are shown as stored, and a missing key shows as blank. GoogleUserId: on the 18 tested images that hold Google Play services' files/authaccount/shared/GaiaIdAccountInfoStore.pb, the value on each of the 22 rows (16 distinct values) is also in that file on the same image, a file whose name calls it a GAIA ID; galaxys10_a10, pixel3_a11 and emu_a15_oss_v17 hold no such file. GoogleUserIdRefreshTime (UTC) reads the stored value as milliseconds since 1970. The unit is not documented; all 23 stored values are 13-digit numbers that read as dates from 2021 to 2026. What event sets it is not established. On a lab emulator signed in to a Google account (not in the corpus) it fell inside the minutes the account was being added, and firstName, lastName and GoogleUserId matched the values in Google Play services' profile_info.pb and GaiaIdAccountInfoStore.pb on that device. GoogleUserIdRefreshTime had no value on pixel3_a11 (Android 11), the only tested image without the key. firstName and lastName held an empty string on 5 of the 24 rows (anne_a15, s20fe_a13, samsunga53_a14 twice, samsungs20_a13). Not reported: the profile image URL, which on the lab emulator was found only in profile_info.pb, a protobuf for which no published schema was found; the other extras keys, among them the capabilities keys, services, keys prefixed EXP:, SCOPES: and perm., oauthAccessToken, lastDroidguardPeriodicRun and capability_sync_time; and the authtokens table, which accounts_ce_authtokens reports. Byte-identical copies of one user's accounts_ce.db are read once. Paths containing 'mirror' are skipped, as in accounts_ce; no tested image had such a path.",
        "paths": ('*/system_ce/*/accounts_ce.db*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 1 row",
            "anne_a15": "Android 15 | 1 row",
            "cookbook_a11": "Android 11 | 1 row",
            "falken_a326u_a13": "Android 13 | 1 row",
            "galaxys10_a10": "Android 10 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | 1 row",
            "hc_pixel8pro_a17": "Android 17 | 1 row",
            "hickman_a13": "Android 13 | 1 row",
            "kevin_pocox7_a15": "Android 15 | 1 row",
            "pixel3_a11": "Android 11 | 1 row",
            "pixel3_a12": "Android 12 | 1 row",
            "pixel7a_a14": "Android 14 | 1 row",
            "russell_a14": "Android 14 | 2 rows (users 0 and 10)",
            "russell_pixel6a_a13": "Android 13 | 2 rows (users 0 and 10)",
            "s20fe_a13": "Android 13 | 1 row",
            "samsunga53_a14": "Android 14 | 2 rows",
            "samsungs20_a13": "Android 13 | 2 rows (users 0 and 150)",
            "sharon_a13": "Android 13 | 1 row",
            "sharon_a14": "Android 14 | 1 row",
            "userb2_a13": "Android 13 | 1 row",
            "emu_a15_oss_v17": "Android 15 | 0 rows (accounts table empty for users 0 and 10)",
        },
    }
}

_KEYS = ('GoogleUserId', 'firstName', 'lastName', 'GoogleUserIdRefreshTime')


def _ms_to_utc(value):
    try:
        ms = int(value)
    except (TypeError, ValueError):
        return None
    if ms <= 0:
        return None
    try:
        return datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(milliseconds=ms)
    except OverflowError:
        return None


def _dedupe_identical(paths):
    by_hash = {}
    for path in sorted(paths):
        try:
            with open(path, 'rb') as handle:
                digest = hashlib.sha1(handle.read()).hexdigest()
        except OSError as ex:
            logfunc(f'Google Accounts: could not hash {path}: {ex}')
            by_hash[path] = path
            continue
        # only copies of the same user's file collapse; another user's identical file is kept
        by_hash.setdefault((Path(path).parts[-2], digest), path)
    return list(by_hash.values())


@artifact_processor
def googleAccounts(context):
    files_found = context.get_files_found()
    databases = _dedupe_identical(get_file_path_list_checking_uid(files_found, 'accounts_ce.db', -2, 'mirror'))
    data_list = []
    sources = []
    for db_path in databases:
        user = Path(db_path).parts[-2]
        db = open_sqlite_db_readonly(db_path)
        if db is None:
            logfunc(f'Google Accounts: could not open {db_path}')
            continue
        try:
            tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if 'accounts' not in tables:
                logfunc(f'Google Accounts: no accounts table in {db_path}')
                sources.append(db_path)
                continue
            extras = {}
            if 'extras' in tables:
                for account_id, key, value in db.execute(
                        'SELECT accounts_id, key, value FROM extras WHERE key IN (?, ?, ?, ?)', _KEYS):
                    extras.setdefault(account_id, {})[key] = value
            else:
                logfunc(f'Google Accounts: no extras table in {db_path}')
            for account_id, name in db.execute(
                    "SELECT _id, name FROM accounts WHERE type = 'com.google' ORDER BY _id"):
                values = extras.get(account_id, {})
                data_list.append((
                    _ms_to_utc(values.get('GoogleUserIdRefreshTime')),
                    user,
                    name,
                    values.get('firstName', ''),
                    values.get('lastName', ''),
                    values.get('GoogleUserId', ''),
                ))
            sources.append(db_path)
        except sqlite3.Error as ex:
            logfunc(f'Google Accounts: could not read {db_path}: {ex}')
        finally:
            db.close()

    data_headers = (('GoogleUserIdRefreshTime (UTC)', 'datetime'), 'Android User', 'Account Name', 'firstName',
                    'lastName', 'GoogleUserId')
    return data_headers, data_list, '\n'.join(sources)
