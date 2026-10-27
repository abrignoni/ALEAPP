__artifacts_v2__ = {
    "gmsScreenlockStateHistory": {
        "name": "Google Play Services - Screen Lock State History",
        "description": "Entries of the screen lock state history that Google Play Services keeps in its "
                       "DeviceStateSyncManager preferences: the time of the last check in each run of "
                       "one state, whether the device was secure at that check, and how many checks "
                       "the run had.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-27",
        "last_update_date": "2026-10-27",
        "requirements": "none",
        "category": "Device Settings",
        "notes": "Reads screenlock_state_history and acknowledged_secure_lock_state from Google Play Services' "
                 "com.google.android.gms.auth.authzen.cryptauth.DeviceStateSyncManager preferences (plain or "
                 "ABX XML); one row per history entry, in stored order, Entry 1 being the oldest kept. The "
                 "meanings below come from the Play Services build installed on pixel7a_a14 (24.26.32, "
                 "base.apk SHA-256 06c467b1bc80356cf530c5775d7ce76a757d5e58765c813c3098f75eb766005e), whose "
                 "classes2.dex was decompiled with jadx 1.5.6; other builds were not decompiled. The two keys "
                 "are also present in the 21.09.15 build on galaxys10_a10 and the 26.26.34 build on "
                 "hc_pixel8pro_a17, which shows the keys exist there, not that the logic is the same. In that "
                 "build DeviceStateSyncManager$CheckStateEventIntentOperation is registered, in the APK's "
                 "ChimeraManifest.pb (decoded without a schema), for android.intent.action.USER_PRESENT, which "
                 "Android sends when the user is present after the device wakes up, for example when the "
                 "keyguard is gone (frameworks/base tag android-14.0.0_r1, commit "
                 "299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368, "
                 "https://android.googlesource.com/platform/frameworks/base/+/299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368/core/java/android/content/Intent.java#2539). "
                 "On that broadcast it sets an inexact alarm of type 3, ELAPSED_REALTIME, which is not "
                 "delivered while the device sleeps "
                 "(https://android.googlesource.com/platform/frameworks/base/+/299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368/apex/jobscheduler/framework/java/android/app/AlarmManager.java#139), "
                 "for 15 seconds later, so a check runs at least 15 seconds after the broadcast and possibly "
                 "much later. A check is skipped when the newest entry is less than 30 seconds old. Otherwise "
                 "it reads KeyguardManager.isDeviceSecure(), true if a PIN, pattern or password was set, a "
                 "locked SIM not counting "
                 "(https://android.googlesource.com/platform/frameworks/base/+/299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368/core/java/android/app/KeyguardManager.java#697). "
                 "If the result equals the newest entry's, that entry is replaced with the current time and "
                 "its count plus one; otherwise a new entry with count 1 is added; only the newest 5 are kept. "
                 "Last Check in Run (timestamp_millis, read as Unix milliseconds) is therefore the time of the "
                 "last check in a run of one state, not when the state began, and a change between consecutive "
                 "entries happened after the earlier entry's time and no later than the later entry's time. "
                 "Checks in Run is the number of checks in that run, not a count of unlocks: skipped checks, "
                 "and broadcasts whose alarm never fired, are not counted. The history is reset to empty when "
                 "the newest entry is later than the current clock or the stored text does not parse, so a "
                 "short history is not evidence of a short period. Device Secure (as checked) and Checks in "
                 "Run are is_secure and count as stored. Acknowledged Secure Lock State (as stored) is "
                 "acknowledged_secure_lock_state, one value per preferences file repeated on each of its rows: "
                 "the build writes it after a successful sync of the state to Google's server and removes it "
                 "when the state changed during that sync. It was present in every tested file and held true "
                 "on 28 and false on 7 of the 35 rows. On sharon_a14 and hc_pixel8pro_a17 the last check of a "
                 "not-secure run came 78 and 51 seconds before the time the Lock Settings artifact reports as "
                 "LSKF Last Changed for user 0, and the next entry was secure. Across the 35 rows of the "
                 "tested images Device Secure (as checked) held true on 24 and false on 11, Checks in Run "
                 "ranged from 1 to 3,017, and no user held more than 4 entries. Android User is the user whose "
                 "app data folder holds the file; the same file under data/data and data/user/0 is read once, "
                 "and the second users on cookbook_a11 and samsungs20_a13 (150) and russell_a14 and "
                 "russell_pixel6a_a13 (10) were reported separately, so Android User held 0 on every row of "
                 "the other images. An entry that is not a JSON object is reported as a row with blank values "
                 "and logged.",
        "paths": ('*/com.google.android.gms/shared_prefs/'
                  'com.google.android.gms.auth.authzen.cryptauth.DeviceStateSyncManager.xml',),
        "output_types": "standard",
        "artifact_icon": "lock",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 1 row",
            "anne_a15": "Android 15 | 1 row",
            "cookbook_a11": "Android 11 | 2 rows",
            "emu_a15_oss2_v3": "Android 15 | 1 row",
            "emu_a15_oss_v17": "Android 15 | 1 row",
            "falken_a326u_a13": "Android 13 | 2 rows",
            "galaxys10_a10": "Android 10 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | 3 rows",
            "hc_pixel8pro_a17": "Android 17 | 4 rows",
            "hickman_a13": "Android 13 | 1 row",
            "kevin_pocox7_a15": "Android 15 | 2 rows",
            "pixel3_a11": "Android 11 | 1 row",
            "pixel3_a12": "Android 12 | 1 row",
            "pixel7a_a14": "Android 14 | 1 row",
            "russell_a14": "Android 14 | 2 rows",
            "russell_pixel6a_a13": "Android 13 | 2 rows",
            "s20fe_a13": "Android 13 | 1 row",
            "samsunga53_a14": "Android 14 | 1 row",
            "samsungs20_a13": "Android 13 | 2 rows",
            "sharon_a13": "Android 13 | 2 rows",
            "sharon_a14": "Android 14 | 2 rows",
            "userb2_a13": "Android 13 | 1 row",
        },
    }
}

import datetime
import json
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import abxread, artifact_processor, checkabx, logfunc
from scripts.artifacts.storagePathViews import user_files

_PREFS = 'com.google.android.gms.auth.authzen.cryptauth.DeviceStateSyncManager.xml'


def _root(path):
    """The XML root, reading ABX binary XML or plain XML."""
    if checkabx(path):
        try:
            return abxread(path, False).getroot()
        except Exception:  # pylint: disable=broad-except
            return abxread(path, True).getroot()
    return ET.parse(path).getroot()


def _unix_millis(value):
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        return ''
    return datetime.datetime.fromtimestamp(value / 1000, datetime.timezone.utc)


def _as_stored(value):
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return '' if value is None else str(value)


@artifact_processor
def gmsScreenlockStateHistory(context):
    data_list = []
    sources = []
    for path, user in user_files(context, _PREFS):
        relative = context.get_relative_path(path)
        try:
            root = _root(path)
        except (ET.ParseError, OSError, ValueError) as ex:
            logfunc(f'Screen Lock State History: could not read {relative}: {ex}')
            continue
        sources.append(path)
        history, acknowledged = None, ''
        for element in root:
            name = element.get('name')
            if name == 'screenlock_state_history':
                history = element.text or ''
            elif name == 'acknowledged_secure_lock_state':
                acknowledged = element.get('value', '')
        if history is None:
            logfunc(f'Screen Lock State History: no screenlock_state_history in {relative}')
            continue
        try:
            entries = json.loads(history)
        except ValueError:
            logfunc(f'Screen Lock State History: history in {relative} is not JSON')
            continue
        if not isinstance(entries, list):
            logfunc(f'Screen Lock State History: history in {relative} is not a list')
            continue
        for number, entry in enumerate(entries, 1):
            if not isinstance(entry, dict):
                # The writer puts a null in the array when it cannot build an entry.
                logfunc(f'Screen Lock State History: entry {number} in {relative} is {entry!r}')
                entry = {}
            data_list.append((_unix_millis(entry.get('timestamp_millis')),
                              _as_stored(entry.get('is_secure')),
                              _as_stored(entry.get('count')),
                              number, acknowledged, user))

    data_headers = (('Last Check in Run', 'datetime'), 'Device Secure (as checked)', 'Checks in Run',
                    'Entry', 'Acknowledged Secure Lock State (as stored)', 'Android User')
    return data_headers, data_list, '\n'.join(sources)
