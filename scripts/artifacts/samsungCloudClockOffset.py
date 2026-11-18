__artifacts_v2__ = {
    "get_samsung_cloud_clock_offset": {
        "name": "Samsung Cloud Clock Offset",
        "description": "TIME_DIFFERENCE, the value Samsung Cloud keeps in the system settings: the phone's "
                       "clock minus a Samsung Cloud server time, in milliseconds, which the app adjusts when "
                       "the clock is changed.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Device Information",
        "notes": "One row per Android user whose settings_system.xml holds a TIME_DIFFERENCE setting written by package com.samsung.android.scloud (Samsung Cloud). What writes it was read in Samsung Cloud decompiled with jadx, versions 5.6.07.17 (from anne_a15) and 5.5.06.17 (from sharon_a14), where the methods read here are the same; the Samsung Cloud versions on the other images were not read. Class names are obfuscated, so the code is named here by its log strings (tag TimeManager, 'Inside the updateSettingsUsingServer method'). When the app gets a server time (the serverTimestamp of a server reply, or the value its sync code returns), it stores TIME_DIFFERENCE as the phone's clock in milliseconds minus that time, if it differs from the stored value; a server time of zero or less stores 0. The app does not subtract the delay between the server's stamp and its own clock read, so the value includes that delay, and a small positive value is expected from a correct clock. On the android.intent.action.TIME_SET and TIMEZONE_CHANGED broadcasts, when a Samsung account is present on the phone and TIME_DIFFERENCE is already stored, the app adds how far the phone's clock moved against the time since boot since its last stamp. TIME_DIFFERENCE (ms) is the stored value read as a whole number; a value that is not a whole number is shown as stored. The unit is milliseconds because the app subtracts it from a millisecond clock. Phone Clock Against Server reads a positive value as the phone's clock ahead and a negative one as behind, from that subtraction; a stored 0 is shown as '0 stored', because it can also mean no server time was received. No time is reported. The stores do not record when TIME_DIFFERENCE was last set: the app also keeps PREVIOUS_SYS_TIME and PREVIOUS_ELAPSED_TIME in its shared_prefs/SETTINGS.xml, but it stamps both at every boot when a Samsung account is present as well as when it writes TIME_DIFFERENCE, and 3 images held both stamps with no TIME_DIFFERENCE, so they are not read. This was not tested with a clock set to a known offset; the meaning rests on the decompiled code. On the 12 Samsung images checked, 7 held TIME_DIFFERENCE, from -126 to 363,196 ms, all for user 0, so User held 0 on all 7 rows; the settings files of users 150, 1000 and 1001 on those images held none. The SMS Device Clock Gap artifact is a different measurement, against the carrier's service centre, per received message. On samsungs20_a13, TIME_DIFFERENCE was 363,196 ms while its received SMS rows had a median gap of 1.8 s; the stores do not show when the 363,196 ms was set, so the two cannot be placed in time against each other. Not read: Samsung Cloud's other stores. Suggested by an examiner on a mailing list.",
        "sample_data": {
            "anne_a15": "Android 15 | 1 row",
            "cookbook_a11": "Android 11 | 1 row",
            "falken_a326u_a13": "Android 13 | 1 row",
            "samsunga53_a14": "Android 14 | 1 row",
            "samsungs20_a13": "Android 13 | 1 row",
            "sharon_a13": "Android 13 | 1 row",
            "sharon_a14": "Android 14 | 1 row",
            "adams_ss135dl_a13": "Android 13 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | 0 rows",
            "samsung_a166u_a16_known_20261117": "Android 16 | 0 rows",
        },
        "paths": ('*/system/users/*/settings_system.xml',
                  '*/com.samsung.android.scloud/shared_prefs/SETTINGS.xml'),
        "output_types": "standard",
        "artifact_icon": "clock",
    }
}

from scripts.android_setup_flags import user_of
from scripts.artifacts.settingsSecure import parse_settings_root
from scripts.ilapfuncs import artifact_processor

_PACKAGE = 'com.samsung.android.scloud'


def _direction(difference):
    if difference > 0:
        return f'ahead by {difference / 1000:.3f} s'
    if difference < 0:
        return f'behind by {-difference / 1000:.3f} s'
    return '0 stored'


@artifact_processor
def get_samsung_cloud_clock_offset(context):
    data_headers = (('TIME_DIFFERENCE (ms)', 'number'), 'Phone Clock Against Server', 'User')
    readings = {}
    for file_found in sorted(str(f) for f in context.get_files_found()):
        normal = file_found.replace('\\', '/')
        if '/mirror/' in normal:
            continue
        user = user_of(normal)
        if not user:
            continue
        root = parse_settings_root(file_found, 'samsungCloudClockOffset')
        if root is None:
            continue
        for setting in root.iter('setting'):
            if setting.get('name') == 'TIME_DIFFERENCE' and setting.get('package') == _PACKAGE:
                readings.setdefault((user, setting.get('value')), []).append(file_found)
    data_list, sources = [], []
    for (user, value), paths in sorted(readings.items(), key=lambda item: (int(item[0][0]), str(item[0][1]))):
        try:
            difference = int(value)
        except (TypeError, ValueError):
            data_list.append((value, '', user))
        else:
            data_list.append((difference, _direction(difference), user))
        sources.extend(paths)
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))
