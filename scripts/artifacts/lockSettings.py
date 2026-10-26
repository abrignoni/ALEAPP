__artifacts_v2__ = {
    "lockSettings": {
        "name": "Lock Settings",
        "description": "Rows of the locksettings table of Android's system locksettings.db, with the "
                       "LSKF last changed time converted and, for keys "
                       "named in AOSP source, the constant that names them.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Device Settings",
        "notes": "Reads the locksettings table (name, user, value) of each system locksettings.db; one "
                 "row per table row, except internal migration and version markers (names starting "
                 "with migrated or enable-sp-for-, or ending in .ver), which are not reported. Value "
                 "(as stored) and User are the value and user columns as stored; a NULL value is shown "
                 "as an empty cell. AOSP Constant names the frameworks/base constant for keys found at "
                 "tag android-14.0.0_r1 (commit 299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368) in "
                 "core/java/com/android/internal/widget/LockPatternUtils.java and "
                 "services/core/java/com/android/server/locksettings/LockSettingsService.java "
                 "(https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-14.0.0_r1/core/java/com/android/internal/widget/LockPatternUtils.java#174), "
                 "including lock_screen_owner_info and lock_screen_owner_info_enabled, which "
                 "LockPatternUtils writes here from setOwnerInfo (lines 187 and 796). Keys not in this "
                 "mapping were not found in those sources, their meaning is not established, and AOSP "
                 "Constant is blank. Other Android versions were not sourced. LSKF Last Changed is the value of sp-handle-ts read as Unix milliseconds: "
                 "Android 14 writes System.currentTimeMillis() under LSKF_LAST_CHANGED_TIME_KEY each "
                 "time it records the current LSKF based protector "
                 "(https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-14.0.0_r1/services/core/java/com/android/server/locksettings/LockSettingsService.java#2777), "
                 "both when the synthetic password is first initialised, possibly with no credential "
                 "set, and when the credential is changed (callers at lines 2759 and 2892), and its own "
                 "dumpsys labels the value LSKF last changed (line 3215). LSKF is the user's Lock Screen "
                 "Knowledge Factor, which may be empty "
                 "(https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-14.0.0_r1/services/core/java/com/android/server/locksettings/SyntheticPasswordManager.java#82). "
                 "The time therefore marks the last of those two events, not which one. It was present "
                 "on 35 of the 412 rows of the tested images and absent on galaxys10_a10 (Android 10). "
                 "On the tested images the password hint held no value (NULL) wherever the key was "
                 "present, the owner info held no value (NULL or empty), and the lockout deadline "
                 "values were 0. User held 0, 10, 150, 1000, "
                 "1001 and -2 on the tested images; what each non-zero value denotes is not "
                 "established here.",
        "paths": ('*/system/locksettings.db*',),
        "output_types": "standard",
        "artifact_icon": "lock",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 19 rows",
            "anne_a15": "Android 15 | 23 rows",
            "cookbook_a11": "Android 11 | 36 rows",
            "emu_a15_oss2_v3": "Android 15 | 12 rows",
            "emu_a15_oss_v17": "Android 15 | 12 rows",
            "falken_a326u_a13": "Android 13 | 25 rows",
            "galaxys10_a10": "Android 10 | 15 rows (no sp-handle-ts)",
            "hc_pixel8pro_a16": "Android 16 | 11 rows",
            "hc_pixel8pro_a17": "Android 17 | 11 rows",
            "hickman_a13": "Android 13 | 9 rows",
            "kevin_pocox7_a15": "Android 15 | 9 rows",
            "pixel3_a11": "Android 11 | 16 rows",
            "pixel3_a12": "Android 12 | 9 rows",
            "pixel7a_a14": "Android 14 | 10 rows",
            "russell_a14": "Android 14 | 21 rows",
            "russell_pixel6a_a13": "Android 13 | 19 rows",
            "s20fe_a13": "Android 13 | 26 rows",
            "samsunga53_a14": "Android 14 | 19 rows",
            "samsungs20_a13": "Android 13 | 32 rows",
            "sharon_a13": "Android 13 | 32 rows",
            "sharon_a14": "Android 14 | 35 rows",
            "userb2_a13": "Android 13 | 11 rows",
        },
    }
}

import datetime
import os
import sqlite3

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly

# Keys and the AOSP constant that names them (frameworks/base, see the notes for the tag).
_AOSP_14 = {
    'lockscreen.password_type': 'LockPatternUtils.PASSWORD_TYPE_KEY',
    'lockscreen.password_type_alternate': 'LockPatternUtils.PASSWORD_TYPE_ALTERNATE_KEY',
    'lockscreen.disabled': 'LockPatternUtils.DISABLE_LOCKSCREEN_KEY',
    'lockscreen.passwordhistory': 'LockPatternUtils.PASSWORD_HISTORY_KEY',
    'lockscreen.patterneverchosen': 'LockPatternUtils.PATTERN_EVER_CHOSEN_KEY',
    'lockscreen.enabledtrustagents': 'LockPatternUtils.ENABLED_TRUST_AGENTS',
    'lockscreen.knowntrustagents': 'LockPatternUtils.KNOWN_TRUST_AGENTS',
    'lockscreen.auto_pin_confirm': 'LockPatternUtils.AUTO_PIN_CONFIRM',
    'lockscreen.profilechallenge': 'LockSettingsService.SEPARATE_PROFILE_CHALLENGE_KEY',
    'sp-handle': 'LockPatternUtils.CURRENT_LSKF_BASED_PROTECTOR_ID_KEY',
    'prev-sp-handle': 'LockSettingsService.PREV_LSKF_BASED_PROTECTOR_ID_KEY',
    'sp-handle-ts': 'LockSettingsService.LSKF_LAST_CHANGED_TIME_KEY',
    'serial-number': 'LockSettingsService.USER_SERIAL_NUMBER_KEY',
    'lockscreen.istrustusuallymanaged': 'LockPatternUtils.IS_TRUST_USUALLY_MANAGED',
    'lock_screen_owner_info': 'LockPatternUtils.LOCK_SCREEN_OWNER_INFO',
    'lock_screen_owner_info_enabled': 'LockPatternUtils.LOCK_SCREEN_OWNER_INFO_ENABLED',
}
_LAST_CHANGED_KEY = 'sp-handle-ts'
# Internal migration and version markers, not reported (see the notes).
_INTERNAL_PREFIXES = ('migrated', 'enable-sp-for-')
_INTERNAL_SUFFIXES = ('.ver',)


def _internal(name):
    return name.startswith(_INTERNAL_PREFIXES) or name.endswith(_INTERNAL_SUFFIXES)


def _unix_millis(value):
    try:
        millis = int(value)
    except (TypeError, ValueError):
        return ''
    if millis <= 0:
        return ''
    return datetime.datetime.fromtimestamp(millis / 1000, datetime.timezone.utc)


@artifact_processor
def lockSettings(context):
    data_list = []
    sources = []
    for path in context.get_files_found():
        path = str(path)
        if os.path.basename(path) != 'locksettings.db':
            continue
        db = open_sqlite_db_readonly(path)
        if db is None:
            continue
        try:
            rows = db.execute('SELECT name, user, value FROM locksettings ORDER BY user, name').fetchall()
        except sqlite3.Error as ex:
            logfunc(f'Lock Settings: could not read {context.get_relative_path(path)}: {ex}')
            continue
        finally:
            db.close()
        sources.append(path)
        for name, user, value in rows:
            if name is None or _internal(name):
                continue
            changed = _unix_millis(value) if name == _LAST_CHANGED_KEY else ''
            constant = _AOSP_14.get(name, '')
            data_list.append((changed, name, value if value is not None else '', user, constant))

    data_headers = (('LSKF Last Changed', 'datetime'), 'Name', 'Value (as stored)',
                    'User', 'AOSP Constant')
    return data_headers, data_list, '\n'.join(sources)
