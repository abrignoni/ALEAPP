__artifacts_v2__ = {
    "gmsAdvertisingId": {
        "name": "Google Play Services - Advertising ID",
        "description": "The advertising ID settings file of Google Play services (adid_settings.xml), "
                       "one row per Android user (a copy of a user's file that differs gets its own row): the stored advertising ID, adid_reset_count and "
                       "enable_limit_ad_tracking as stored, and any other keys.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Device Information",
        "notes": "Reads adid_settings.xml in Google Play services' shared_prefs folder (plain XML on every image read), one row per Android user (a copy of a user's file that differs gets its own row). Google describes the advertising ID as a user-resettable and user-deletable ID for advertising provided by Google Play services (https://support.google.com/googleplay/android-developer/answer/6048248, read 2026-11-16), and the AdServices AdId class as device-wide and per-profile, returning 00000000-0000-0000-0000-000000000000 when limit ad tracking is enabled (https://developer.android.com/reference/android/adservices/adid/AdId, read 2026-11-16). Play services is not open source and no Google or AOSP source found names this file's keys, so what each key does comes from known data and a cross-check, not from a specification. Known data on an Android 15 emulator with Play services 24.23.35 and no account (emu_a15_adid_s1_created_known_20261116 to emu_a15_adid_s6_optin_read_known_20261116, steps in the mint log beside the tars): the file did not exist on the fresh device and was written when Settings > Google > Ads was first opened; adid_key held a UUID equal to the ID that screen showed in each of the three states where the two were compared (first written, after the first reset, after reopening); each Reset advertising ID wrote a new UUID and added 1 to adid_reset_count (1, 2, 3); Opt out of Ads Personalization removed adid_key and fake_adid_key from the file and set enable_limit_ad_tracking to true, leaving the count unchanged; turning the opt-out off set it back to false with no adid_key until the screen was reopened, when a new UUID was written and the count went to 4. So on that build adid_reset_count went up by one for each new ID written, the first included, and is reported as stored; other builds were not tested. That build's screen had no Delete advertising ID control, so what deleting the ID writes is not established. On the known-data build, a row with a blank Advertising ID (adid_key) and enable_limit_ad_tracking true matches the opt-out state. A missing file is not evidence that no ID existed: on the known-data build the file was not written until the Ads screen was first opened. No key holds a time, and the file's modification time is not reported. Cross-check with AdServices: on the seven images where AdServices' adservices_msmt.db held a platform_ad_id (adams_ss135dl_a13, anne_a15, falken_a326u_a13, kevin_pocox7_a15, pixel7a_a14, russell_a14, samsunga53_a14) it held one distinct value, equal to user 0's adid_key here on all seven (AOSP describes platform_ad_id as the AdID from an app registration, https://android.googlesource.com/platform/packages/modules/AdServices/+/593832a5beabbc740974dc6c07f3294cd8a3bc6d/adservices/service-core/java/com/android/adservices/service/measurement/registration/AsyncRegistration.java#207). AdServices - Attribution Sources and Attribution Triggers leave that column off their rows. On those seven images it equalled the user 0 Advertising ID reported here. On russell_a14 the value was in both the live and a rollback copy of user 0's database; user 10's copies held no platform_ad_id, so user 10's ID was not cross-checked. Advertising ID (adid_key), adid_reset_count and enable_limit_ad_tracking are those keys as stored; every other key is listed in Other Keys as name (type) = value, so a key a build adds is still shown (a set-valued key would show without its members; none was seen). A file that does not parse as XML gives a row with blank values and the parse error in Other Keys; no image exercised this. Android User is n from data/user/<n>, data/user_de/<n>, userdata/user/<n>, userdata/user_de/<n>, data_mirror/data_ce/<volume>/<n> or data_mirror/data_de/<volume>/<n> (the user_de and data_de shapes were not seen on any image), and 0 under data/data or userdata/data. A file is read when its path ends in one of those roots followed by the Play services folder, so a whole data tree copied inside another folder would be read as that user; any other match is logged and skipped. Byte-identical copies of one user's file (data/data, data/user/0, data_mirror) are read once, and a copy that differs gets its own row (the differing-copy path was not exercised). A folder tree with one file under data/data, data/user/0 and data_mirror, an opted-out file under data/user/10 and a copy of the Play services folder placed inside another app's folder gave exactly two rows, user 0 and user 10, and nothing from that copy. Copies under data/misc_ce/<n>/rollback/ are not read; none was seen. Measured on 20 real-device images (24 rows) and the 21 other emulator images (41 rows), the known data aside: every user's copies were byte-identical; each second user (10 on russell_a14 and russell_pixel6a_a13, 150 on cookbook_a11 and samsungs20_a13, and 10 on every emulator image with two rows) had its own ID; Advertising ID (adid_key) held a UUID on every row; enable_limit_ad_tracking held false on all 65 rows; adid_reset_count held 1 on 19, 2 on 2 and 3 on 3 real-device rows and 1 on every emulator row; Other Keys held enable_debug_logging false, using_cert false and fake_adid_key empty on every row except galaxys10_a10, which had no using_cert key. The 17 emu_a15_oss images and the 3 emu_a15_oss2 images are each one emulator captured several times and share their IDs; the russell, sharon and hc_pixel8pro pairs, registered as the same model in the same series at two Android versions, also held the same user 0 ID. Left out, in the same folder: no other Play services preferences file on those 41 images contained that image's adid_key when searched as text, with and without hyphens (115 to 729 shared_prefs members per image, storage views counted separately); google_ads_flags.xml (gads: flag keys, a few named for adid values, on 54 copies) and herrevad.xml (herrevadId64Bit and lastHerrevadIdGenerationTimeSecs on 3 copies, values whose meaning is not established) are not reported.",
        "paths": ('*/com.google.android.gms/shared_prefs/adid_settings.xml',),
        "output_types": "standard",
        "artifact_icon": "smartphone",
        "sample_data": {
            "cookbook_a11": "Android 11 | 2 rows (users 0, 150)",
            "russell_a14": "Android 14 | 2 rows (users 0, 10)",
            "russell_pixel6a_a13": "Android 13 | 2 rows (users 0, 10)",
            "samsungs20_a13": "Android 13 | 2 rows (users 0, 150)",
            "adams_ss135dl_a13": "Android 13 | 1 row",
            "anne_a15": "Android 15 | 1 row",
            "falken_a326u_a13": "Android 13 | 1 row",
            "galaxys10_a10": "Android 10 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | 1 row",
            "hc_pixel8pro_a17": "Android 17 | 1 row",
            "hickman_a13": "Android 13 | 1 row",
            "kevin_pocox7_a15": "Android 15 | 1 row",
            "pixel3_a11": "Android 11 | 1 row",
            "pixel3_a12": "Android 12 | 1 row",
            "pixel7a_a14": "Android 14 | 1 row",
            "s20fe_a13": "Android 13 | 1 row",
            "samsunga53_a14": "Android 14 | 1 row",
            "sharon_a13": "Android 13 | 1 row",
            "sharon_a14": "Android 14 | 1 row",
            "userb2_a13": "Android 13 | 1 row",
            "emu_a15_kdl_v1": "Android 15 emulator | 1 row",
            "emu_a15_oss2_v1": "Android 15 emulator | 2 rows (users 0, 10)",
            "emu_a15_oss2_v2": "Android 15 emulator | 2 rows (users 0, 10)",
            "emu_a15_oss2_v3": "Android 15 emulator | 2 rows (users 0, 10)",
            "emu_a15_oss_v1": "Android 15 emulator | 2 rows (users 0, 10)",
            "emu_a15_oss_v10": "Android 15 emulator | 2 rows (users 0, 10)",
            "emu_a15_oss_v11": "Android 15 emulator | 2 rows (users 0, 10)",
            "emu_a15_oss_v12": "Android 15 emulator | 2 rows (users 0, 10)",
            "emu_a15_oss_v13": "Android 15 emulator | 2 rows (users 0, 10)",
            "emu_a15_oss_v14": "Android 15 emulator | 2 rows (users 0, 10)",
            "emu_a15_oss_v15": "Android 15 emulator | 2 rows (users 0, 10)",
            "emu_a15_oss_v16": "Android 15 emulator | 2 rows (users 0, 10)",
            "emu_a15_oss_v17": "Android 15 emulator | 2 rows (users 0, 10)",
            "emu_a15_oss_v2": "Android 15 emulator | 2 rows (users 0, 10)",
            "emu_a15_oss_v3": "Android 15 emulator | 2 rows (users 0, 10)",
            "emu_a15_oss_v4": "Android 15 emulator | 2 rows (users 0, 10)",
            "emu_a15_oss_v5": "Android 15 emulator | 2 rows (users 0, 10)",
            "emu_a15_oss_v6": "Android 15 emulator | 2 rows (users 0, 10)",
            "emu_a15_oss_v7": "Android 15 emulator | 2 rows (users 0, 10)",
            "emu_a15_oss_v8": "Android 15 emulator | 2 rows (users 0, 10)",
            "emu_a15_oss_v9": "Android 15 emulator | 2 rows (users 0, 10)",
            "emu_a15_adid_s1_created_known_20261116": "Android 15 emulator | 1 row (known data, file as first written)",
            "emu_a15_adid_s2_reset1_known_20261116": "Android 15 emulator | 1 row (known data, after one Reset)",
            "emu_a15_adid_s3_reset2_known_20261116": "Android 15 emulator | 1 row (known data, after a second Reset)",
            "emu_a15_adid_s4_optout_known_20261116": "Android 15 emulator | 1 row (known data, after Opt out of Ads Personalization; no adid_key)",
            "emu_a15_adid_s5_optin_known_20261116": "Android 15 emulator | 1 row (known data, after opt-out turned off; no adid_key)",
            "emu_a15_adid_s6_optin_read_known_20261116": "Android 15 emulator | 1 row (known data, after the Ads screen was reopened)",
            "adams_ss134dl_a03s_logical": "Android logical extraction | 0 rows (no adid_settings.xml)",
            "hc_pixel8pro_a17_ail": "Android 17 | 0 rows (no adid_settings.xml)",
            "emu_a15_adservices_on_known_20261116": "Android 15 emulator, scoped tar of the AdServices folders only | 0 rows (Play services folder not captured)",
        },
    },
}

import hashlib
import os
import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc

_PACKAGE = 'com.google.android.gms'
# The package folder must sit directly under an app data root, so a copy of the same layout
# nested inside another app's folder is not read.
_ROOTS = (
    (re.compile(r'(?:^|/)data/data/' + re.escape(_PACKAGE) + r'/shared_prefs/adid_settings\.xml$'), None),
    (re.compile(r'(?:^|/)userdata/data/' + re.escape(_PACKAGE) + r'/shared_prefs/adid_settings\.xml$'), None),
    (re.compile(r'(?:^|/)data/user(?:_de)?/(\d+)/' + re.escape(_PACKAGE) + r'/shared_prefs/adid_settings\.xml$'), 1),
    (re.compile(r'(?:^|/)userdata/user(?:_de)?/(\d+)/' + re.escape(_PACKAGE) + r'/shared_prefs/adid_settings\.xml$'), 1),
    (re.compile(r'(?:^|/)data_mirror/data_(?:ce|de)/[^/]+/(\d+)/' + re.escape(_PACKAGE) +
                r'/shared_prefs/adid_settings\.xml$'), 1),
)
_SHOWN = ('adid_key', 'adid_reset_count', 'enable_limit_ad_tracking')


def _norm(path):
    return path.replace(os.sep, '/').replace('\\', '/')


def _android_user(rel_path):
    '''The user whose app data folder holds the file, or None when the path is not under one.'''
    norm = _norm(rel_path)
    for pattern, group in _ROOTS:
        match = pattern.search(norm)
        if match:
            return int(match.group(group)) if group else 0
    return None


def _value(element):
    value = element.get('value')
    if value is None:
        value = element.text or ''
    return value


@artifact_processor
def gmsAdvertisingId(context):
    candidates = []
    for path in context.get_files_found():
        rel = context.get_relative_path(path)
        user = _android_user(rel)
        if user is None:
            if _norm(path).endswith('/adid_settings.xml'):
                logfunc(f'Google Play Services - Advertising ID: not under an app data folder, skipped: {rel}')
            continue
        candidates.append((user, _norm(rel), path, rel))
    # data/data first, so its path is the one reported when byte-identical views collapse.
    candidates.sort(key=lambda c: (c[0], '/data/data/' not in '/' + c[1], c[1]))

    data_list = []
    sources = []
    seen = set()
    for user, _, path, rel in candidates:
        try:
            with open(path, 'rb') as handle:
                raw = handle.read()
        except OSError as ex:
            logfunc(f'Google Play Services - Advertising ID: could not read {rel}: {ex}')
            continue
        # Byte-identical storage views of one user's file (data/data, data/user/0, data_mirror) are read once.
        key = (user, hashlib.sha256(raw).hexdigest())
        if key in seen:
            continue
        seen.add(key)
        sources.append(path)
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as ex:
            logfunc(f'Google Play Services - Advertising ID: could not parse {rel}: {ex}')
            data_list.append((user, '', '', '', f'(file did not parse as XML: {ex})'))
            continue
        values = {}
        other = []
        for element in root:
            name = element.get('name')
            if name is None:
                continue
            if name in _SHOWN and name not in values:
                values[name] = _value(element)
            else:
                other.append(f'{name} ({element.tag}) = {_value(element)}')
        data_list.append((user, values.get('adid_key', ''), values.get('adid_reset_count', ''),
                          values.get('enable_limit_ad_tracking', ''), '\n'.join(other)))

    data_headers = ('Android User', ('Advertising ID (adid_key)', 'hash'), 'adid_reset_count',
                    'enable_limit_ad_tracking', 'Other Keys')
    return data_headers, data_list, '\n'.join(sources)
