__artifacts_v2__ = {
    "appops_accesses": {
        "name": "App Ops Recent Accesses",
        "description": "App op accesses and rejections the platform had persisted, with the package, the op, "
                       "the access and rejection times, the duration, and the process state the app was in.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Permissions",
        "notes": "Read from system/appops_accesses.xml, one row per <st> element. The pattern is not "
                 "anchored on a data/ prefix, because a raw userdata partition image carries the same "
                 "folder without one, as samsungs20_a13 does. The file was ABX binary XML on all 25 "
                 "tested images and a plain XML read is used when the file does not carry the ABX magic, "
                 "a branch no tested image exercised.\nThis is a different file from the two App Ops "
                 "artifacts already in ALEAPP. appops.py reads system/appops.xml and discreteNative.py "
                 "reads system/appops/discrete. Android 14 split the single appops file in two, so from "
                 "that release the access records are here and appops.xml holds the per-op mode state, "
                 "which this artifact does not report. Across the 39 registered Android corpora the file "
                 "was present on all 25 that report Android 14 or later and absent on all 11 that report "
                 "Android 13 or earlier; the other 3 are partial extractions carrying neither this file "
                 "nor the per-user standby file. Reference: AOSP, AppOpsService, the mRecentAccessesFile "
                 "AtomicFile named appops_accesses, "
                 "https://android.googlesource.com/platform/frameworks/base/+/299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368/services/core/java/com/android/server/appop/AppOpsService.java#941\nAccess "
                 "Timestamp and Reject Timestamp are milliseconds since the Unix epoch, rendered in UTC. "
                 "The platform writes each only when it is greater than zero. Of the 29,634 rows across "
                 "the tested images 19,347 carried an access time only, 10,113 a rejection time only and "
                 "174 both, and none carried neither, so a blank in one of those columns is the platform "
                 "having recorded nothing for it. Access Duration is milliseconds and is written only "
                 "when greater than zero.\nApp State At Access and Access Flag are decoded from the <st> "
                 "n attribute, which the platform writes as AppOpsManager.makeKey(uidState, flags), the "
                 "uid state shifted left 31 bits with the flags in the low bits. App State At Access is "
                 "the process state the app was in when the op was noted, so it separates an access made "
                 "while the app was in the foreground from one made while it was cached. TOP, "
                 "FOREGROUND, BACKGROUND, CACHED, FOREGROUND_SERVICE and PERSISTENT all appeared and "
                 "FOREGROUND_SERVICE_LOCATION did not. Access Flag says whether the app performed the op "
                 "itself or through a proxy. Both are reported as stored when the value is outside the "
                 "AOSP set, which no tested image required. Reference: AOSP, AppOpsManager, makeKey and "
                 "the UID_STATE and OP_FLAG constants, "
                 "https://android.googlesource.com/platform/frameworks/base/+/4e43ad12e1b211f15152e9c5b16b0fe88e6b93f3/core/java/android/app/AppOpsManager.java\nPermission "
                 "is the AOSP short name for the Op Code, taken from the ordered sAppOpInfos table where "
                 "the array index is the op code. The codes are the same in the AppOpsManager tables at "
                 "the android-11.0.0_r1, android-13.0.0_r1, android-14.0.0_r1 and android-15.0.0_r1 tags "
                 "and at main, so the names do not depend on the release. They were also checked against "
                 "a running Android 15 device: of 500 package and op-name pairs that dumpsys appops "
                 "printed by name, 495 matched the name this table gives for the code in that device's "
                 "own appops_accesses.xml on an identical millisecond timestamp and none matched a "
                 "different name, the other 5 sharing no timestamp because the file is written on a "
                 "delay and was older than the dumpsys output. Code 96 is a retired placeholder that "
                 "AOSP leaves unnamed and it is not mapped. Codes the table does not define are left "
                 "unnamed, with the number in Op Code, and are not named here because no source for them "
                 "was found: that happened on 598 of 29,634 rows on three images, being 164 and 166 on "
                 "the Android 16 Pixel, 163, 164, 166, 169 and 176 on the Android 17 Pixel, both above "
                 "the highest code AOSP main defines, and 10008, 10020, 10032, 10033, 10037 and 10044 on "
                 "the Android 15 Xiaomi, which are outside the AOSP range entirely. Reference: AOSP, "
                 "AppOpsManager, sAppOpInfos, "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/core/java/android/app/AppOpsManager.java\nOp "
                 "Mode is the parent op element m attribute, which the platform writes only when the "
                 "mode differs from that op's default mode, so it is set on 562 of the 29,634 rows. "
                 "Proxy Package Name, Proxy Attribution Tag and Proxy UID are present only where the op "
                 "was performed on behalf of another package, on 373 rows, and Attribution Tag is set on "
                 "4,133.\nAn op element that carries no <st> child records no access and is not "
                 "reported. There were 6,964 of them across the 25 files, between 18 and 1,147 per "
                 "file.\nThe file is a periodically written snapshot rather than a live view. AOSP "
                 "schedules the write on a delay commented as at most every 30 minutes, so the contents "
                 "reflect the last write and not the state at acquisition. Measured on the tested "
                 "emulator: of the 317 package names in the file, 2 were not installed for either "
                 "Android user, one of them an app removed with pm uninstall, so a package named here "
                 "was not necessarily installed when the device was acquired. The per-user "
                 "app_idle_stats.xml on that same device named only one of those two, so retention after "
                 "a removal differed between the two files. Whether such an entry survives a later write "
                 "was not established. Reference: AOSP, AppOpsService, WRITE_DELAY, "
                 "https://android.googlesource.com/platform/frameworks/base/+/4e43ad12e1b211f15152e9c5b16b0fe88e6b93f3/services/core/java/com/android/server/appop/AppOpsService.java#233\nThe "
                 "path pattern is tolerant, so a second copy of this file in an extraction would add its "
                 "rows again. None of the 39 corpora carried more than one, and the Source File column "
                 "names the file each row came from.",
        "paths": ('*/system/appops_accesses.xml',),
        "output_types": "standard",
        "artifact_icon": "shield",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 0 rows",
            "anne_a15": "Android 15 | 2071 rows",
            "cookbook_a11": "Android 11 | 0 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 320 rows",
            "emu_a15_oss_v10": "Android 15 | 567 rows",
            "emu_a15_oss_v11": "Android 15 | 588 rows",
            "emu_a15_oss_v12": "Android 15 | 628 rows",
            "emu_a15_oss_v13": "Android 15 | 653 rows",
            "emu_a15_oss_v14": "Android 15 | 681 rows",
            "emu_a15_oss_v15": "Android 15 | 735 rows",
            "emu_a15_oss_v16": "Android 15 | 852 rows",
            "emu_a15_oss_v17": "Android 15 | 897 rows",
            "emu_a15_oss_v2": "Android 15 | 360 rows",
            "emu_a15_oss_v3": "Android 15 | 374 rows",
            "emu_a15_oss_v4": "Android 15 | 450 rows",
            "emu_a15_oss_v5": "Android 15 | 484 rows",
            "emu_a15_oss_v6": "Android 15 | 518 rows",
            "emu_a15_oss_v7": "Android 15 | 551 rows",
            "emu_a15_oss_v8": "Android 15 | 552 rows",
            "emu_a15_oss_v9": "Android 15 | 553 rows",
            "falken_a326u_a13": "Android 13 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 2076 rows",
            "hc_pixel8pro_a17": "Android 17 | 2484 rows",
            "hc_pixel8pro_a17_ail": "0 rows",
            "kevin_pocox7_a15": "Android 15 | 3639 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 0 rows",
            "pixel7a_a14": "Android 14 | 2627 rows",
            "russell_a14": "Android 14 | 3122 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 1106 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 2746 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
    },
}

import datetime
import os
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import abxread, artifact_processor, checkabx, logfunc

# Op code to AOSP short name, extracted from the ordered AppOpsManager.sAppOpInfos table, where
# the array index is the op code, at main 1cdfff555f4a21f71ccc978290e2e212e2f8b168. Code 96 is a
# retired placeholder that carries no name and is left out. Checked against the sOpNames arrays
# at the android-11.0.0_r1 and android-13.0.0_r1 tags and the sAppOpInfos arrays at
# android-14.0.0_r1 and android-15.0.0_r1: the codes are the same in all of them.
APP_OP_NAMES = {
    0: "COARSE_LOCATION", 1: "FINE_LOCATION", 2: "GPS",
    3: "VIBRATE", 4: "READ_CONTACTS", 5: "WRITE_CONTACTS",
    6: "READ_CALL_LOG", 7: "WRITE_CALL_LOG", 8: "READ_CALENDAR",
    9: "WRITE_CALENDAR", 10: "WIFI_SCAN", 11: "POST_NOTIFICATION",
    12: "NEIGHBORING_CELLS", 13: "CALL_PHONE", 14: "READ_SMS",
    15: "WRITE_SMS", 16: "RECEIVE_SMS", 17: "RECEIVE_EMERGENCY_BROADCAST",
    18: "RECEIVE_MMS", 19: "RECEIVE_WAP_PUSH", 20: "SEND_SMS",
    21: "READ_ICC_SMS", 22: "WRITE_ICC_SMS", 23: "WRITE_SETTINGS",
    24: "SYSTEM_ALERT_WINDOW", 25: "ACCESS_NOTIFICATIONS", 26: "CAMERA",
    27: "RECORD_AUDIO", 28: "PLAY_AUDIO", 29: "READ_CLIPBOARD",
    30: "WRITE_CLIPBOARD", 31: "TAKE_MEDIA_BUTTONS", 32: "TAKE_AUDIO_FOCUS",
    33: "AUDIO_MASTER_VOLUME", 34: "AUDIO_VOICE_VOLUME", 35: "AUDIO_RING_VOLUME",
    36: "AUDIO_MEDIA_VOLUME", 37: "AUDIO_ALARM_VOLUME", 38: "AUDIO_NOTIFICATION_VOLUME",
    39: "AUDIO_BLUETOOTH_VOLUME", 40: "WAKE_LOCK", 41: "MONITOR_LOCATION",
    42: "MONITOR_HIGH_POWER_LOCATION", 43: "GET_USAGE_STATS", 44: "MUTE_MICROPHONE",
    45: "TOAST_WINDOW", 46: "PROJECT_MEDIA", 47: "ACTIVATE_VPN",
    48: "WRITE_WALLPAPER", 49: "ASSIST_STRUCTURE", 50: "ASSIST_SCREENSHOT",
    51: "READ_PHONE_STATE", 52: "ADD_VOICEMAIL", 53: "USE_SIP",
    54: "PROCESS_OUTGOING_CALLS", 55: "USE_FINGERPRINT", 56: "BODY_SENSORS",
    57: "READ_CELL_BROADCASTS", 58: "MOCK_LOCATION", 59: "READ_EXTERNAL_STORAGE",
    60: "WRITE_EXTERNAL_STORAGE", 61: "TURN_SCREEN_ON", 62: "GET_ACCOUNTS",
    63: "RUN_IN_BACKGROUND", 64: "AUDIO_ACCESSIBILITY_VOLUME", 65: "READ_PHONE_NUMBERS",
    66: "REQUEST_INSTALL_PACKAGES", 67: "PICTURE_IN_PICTURE", 68: "INSTANT_APP_START_FOREGROUND",
    69: "ANSWER_PHONE_CALLS", 70: "RUN_ANY_IN_BACKGROUND", 71: "CHANGE_WIFI_STATE",
    72: "REQUEST_DELETE_PACKAGES", 73: "BIND_ACCESSIBILITY_SERVICE", 74: "ACCEPT_HANDOVER",
    75: "MANAGE_IPSEC_TUNNELS", 76: "START_FOREGROUND", 77: "BLUETOOTH_SCAN",
    78: "USE_BIOMETRIC", 79: "ACTIVITY_RECOGNITION", 80: "SMS_FINANCIAL_TRANSACTIONS",
    81: "READ_MEDIA_AUDIO", 82: "WRITE_MEDIA_AUDIO", 83: "READ_MEDIA_VIDEO",
    84: "WRITE_MEDIA_VIDEO", 85: "READ_MEDIA_IMAGES", 86: "WRITE_MEDIA_IMAGES",
    87: "LEGACY_STORAGE", 88: "ACCESS_ACCESSIBILITY", 89: "READ_DEVICE_IDENTIFIERS",
    90: "ACCESS_MEDIA_LOCATION", 91: "QUERY_ALL_PACKAGES", 92: "MANAGE_EXTERNAL_STORAGE",
    93: "INTERACT_ACROSS_PROFILES", 94: "ACTIVATE_PLATFORM_VPN", 95: "LOADER_USAGE_STATS",
    97: "AUTO_REVOKE_PERMISSIONS_IF_UNUSED", 98: "AUTO_REVOKE_MANAGED_BY_INSTALLER", 99: "NO_ISOLATED_STORAGE",
    100: "PHONE_CALL_MICROPHONE", 101: "PHONE_CALL_CAMERA", 102: "RECORD_AUDIO_HOTWORD",
    103: "MANAGE_ONGOING_CALLS", 104: "MANAGE_CREDENTIALS", 105: "USE_ICC_AUTH_WITH_DEVICE_IDENTIFIER",
    106: "RECORD_AUDIO_OUTPUT", 107: "SCHEDULE_EXACT_ALARM", 108: "FINE_LOCATION_SOURCE",
    109: "COARSE_LOCATION_SOURCE", 110: "MANAGE_MEDIA", 111: "BLUETOOTH_CONNECT",
    112: "UWB_RANGING", 113: "ACTIVITY_RECOGNITION_SOURCE", 114: "BLUETOOTH_ADVERTISE",
    115: "RECORD_INCOMING_PHONE_AUDIO", 116: "NEARBY_WIFI_DEVICES", 117: "ESTABLISH_VPN_SERVICE",
    118: "ESTABLISH_VPN_MANAGER", 119: "ACCESS_RESTRICTED_SETTINGS", 120: "RECEIVE_SOUNDTRIGGER_AUDIO",
    121: "RECEIVE_EXPLICIT_USER_INTERACTION_AUDIO", 122: "RUN_USER_INITIATED_JOBS", 123: "READ_MEDIA_VISUAL_USER_SELECTED",
    124: "SYSTEM_EXEMPT_FROM_SUSPENSION", 125: "SYSTEM_EXEMPT_FROM_DISMISSIBLE_NOTIFICATIONS", 126: "READ_WRITE_HEALTH_DATA",
    127: "FOREGROUND_SERVICE_SPECIAL_USE", 128: "SYSTEM_EXEMPT_FROM_POWER_RESTRICTIONS", 129: "SYSTEM_EXEMPT_FROM_HIBERNATION",
    130: "SYSTEM_EXEMPT_FROM_ACTIVITY_BG_START_RESTRICTION", 131: "CAPTURE_CONSENTLESS_BUGREPORT_ON_USERDEBUG_BUILD", 132: "DEPRECATED_2",
    133: "USE_FULL_SCREEN_INTENT", 134: "CAMERA_SANDBOXED", 135: "RECORD_AUDIO_SANDBOXED",
    136: "RECEIVE_SANDBOX_TRIGGER_AUDIO", 137: "DEPRECATED_3", 138: "CREATE_ACCESSIBILITY_OVERLAY",
    139: "MEDIA_ROUTING_CONTROL", 140: "ENABLE_MOBILE_DATA_BY_USER", 141: "OP_RESERVED_FOR_TESTING",
    142: "RAPID_CLEAR_NOTIFICATIONS_BY_LISTENER", 143: "READ_SYSTEM_GRAMMATICAL_GENDER", 144: "DEPRECATED_4",
    145: "ARCHIVE_ICON_OVERLAY", 146: "UNARCHIVAL_CONFIRMATION", 147: "EMERGENCY_LOCATION",
    148: "RECEIVE_SENSITIVE_NOTIFICATIONS", 149: "READ_HEART_RATE", 150: "READ_SKIN_TEMPERATURE",
    151: "RANGING", 152: "READ_OXYGEN_SATURATION", 153: "WRITE_SYSTEM_PREFERENCES",
    154: "CONTROL_AUDIO", 155: "CONTROL_AUDIO_PARTIAL",
}

# AppOpsManager UID_STATE constants, at android-15.0.0_r1.
UID_STATES = {
    100: 'PERSISTENT',
    200: 'TOP',
    300: 'FOREGROUND_SERVICE_LOCATION',
    400: 'FOREGROUND_SERVICE',
    500: 'FOREGROUND',
    600: 'BACKGROUND',
    700: 'CACHED',
}

# AppOpsManager OP_FLAG constants, a bit mask, at android-15.0.0_r1.
OP_FLAGS = (
    (0x1, 'SELF'),
    (0x2, 'TRUSTED_PROXY'),
    (0x4, 'UNTRUSTED_PROXY'),
    (0x8, 'TRUSTED_PROXIED'),
    (0x10, 'UNTRUSTED_PROXIED'),
)

# AppOpsManager MODE constants, at android-15.0.0_r1.
OP_MODES = {
    '0': 'ALLOWED',
    '1': 'IGNORED',
    '2': 'ERRORED',
    '3': 'DEFAULT',
    '4': 'FOREGROUND',
}

# AppOpsManager.makeKey shifts the uid state left by UID_STATE_OFFSET and ors in the flags.
UID_STATE_OFFSET = 31
FLAGS_MASK = 0xFFFFFFFF


def _root(path):
    """The XML root, reading ABX binary XML or plain XML."""
    if checkabx(path):
        try:
            return abxread(path, False).getroot()
        except Exception:  # pylint: disable=broad-except
            return abxread(path, True).getroot()
    return ET.parse(path).getroot()


def _epoch_ms(value):
    """A datetime from milliseconds since the Unix epoch, in UTC, or '' when absent."""
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError):
        return value


def _decode_key(value):
    """The uid state name and the flag names packed into the <st> n attribute. Values outside
    the AOSP sets are returned as stored."""
    if value is None:
        return '', ''
    try:
        key = int(value)
    except ValueError:
        return value, ''
    state = key >> UID_STATE_OFFSET
    flags = key & FLAGS_MASK
    state_name = UID_STATES.get(state, str(state))
    names = [name for bit, name in OP_FLAGS if flags & bit]
    remainder = flags & ~sum(bit for bit, _ in OP_FLAGS)
    if remainder:
        names.append(str(remainder))
    return state_name, ' | '.join(names)


@artifact_processor
def appops_accesses(context):
    data_headers = (
        ('Access Timestamp', 'datetime'),
        ('Reject Timestamp', 'datetime'),
        'Package Name',
        'UID',
        'Permission',
        'Op Code',
        'Attribution Tag',
        'App State At Access',
        'Access Flag',
        'Access Duration (ms)',
        'Op Mode',
        'Proxy Package Name',
        'Proxy Attribution Tag',
        'Proxy UID',
        'Source File',
    )
    data_list = []
    sources = []

    for file_found in sorted(context.get_files_found()):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        if os.path.basename(file_found) != 'appops_accesses.xml':
            continue
        try:
            root = _root(file_found)
        except Exception as error:  # pylint: disable=broad-except
            logfunc(f'App Ops Recent Accesses: could not read {os.path.basename(file_found)}: {error}')
            continue
        relative_path = context.get_relative_path(file_found)
        rows = 0
        for pkg in root.iter('pkg'):
            package = pkg.get('n', '')
            for uid in pkg.iter('uid'):
                uid_value = uid.get('n', '')
                for op in uid.iter('op'):
                    code = op.get('n', '')
                    try:
                        permission = APP_OP_NAMES.get(int(code), '')
                    except ValueError:
                        permission = ''
                    mode = op.get('m')
                    mode_name = OP_MODES.get(mode, mode) if mode is not None else ''
                    for st in op.iter('st'):
                        state_name, flag_names = _decode_key(st.get('n'))
                        data_list.append((
                            _epoch_ms(st.get('t')),
                            _epoch_ms(st.get('r')),
                            package,
                            uid_value,
                            permission,
                            code,
                            st.get('id', ''),
                            state_name,
                            flag_names,
                            st.get('d', ''),
                            mode_name,
                            st.get('pp', ''),
                            st.get('pc', ''),
                            st.get('pu', ''),
                            relative_path,
                        ))
                        rows += 1
        if rows:
            sources.append(file_found)

    return data_headers, data_list, '\n'.join(sources)
