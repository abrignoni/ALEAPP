__artifacts_v2__ = {
    "get_appops": {
        "name": "App Ops Permissions",
        "description": "App op access and reject times from the st records of "
                       "appops.xml (the form written by Android 10 to 13; from "
                       "Android 14 these records are in appops_accesses.xml)",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2021-08-15",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Permissions",
        "notes": "Access Timestamp and Reject Timestamp are the t and r attributes of each st "
                 "record, read as Unix milliseconds; Proxy Package Name and Proxy Package UID are "
                 "its pp and pu attributes and ID is its id attribute where present. Only the "
                 "first appops.xml found is read. Reference: Android Open Source Project. Op "
                 "codes and names: AppOpsManager.java sAppOpInfos at android-14.0.0_r1, "
                 "https://android.googlesource.com/platform/frameworks/base/+/refs/tags/"
                 "android-14.0.0_r1/core/java/android/app/AppOpsManager.java#2347; the table in "
                 "this module names codes 0 to 120 and reports a higher code as its number. The "
                 "st attributes n, t (access time), r (reject time), d, pp and pu: "
                 "AppOpsService.java writeState at android-10.0.0_r1, "
                 "https://android.googlesource.com/platform/frameworks/base/+/refs/tags/"
                 "android-10.0.0_r1/services/core/java/com/android/server/appop/"
                 "AppOpsService.java#3063; no source for the id attribute was read here.",
        "paths": ('*/system/appops.xml',),
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "anne_a15": "Android 15 | 0 rows",
            "galaxys10_a10": "Android 10 | 922 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 1650 rows",
            "sharon_a14": "Android 14 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 2391 rows",
            "userb2_a13": "Android 13 | 1015 rows",
        },
    },
    "get_appops_legacy": {
        "name": "App Ops Permissions - Legacy",
        "description": "App op access times per uid state from the op attributes of appops.xml "
                       "(the form AppOpsService writes at android-9.0.0_r1; no tested image "
                       "exercised it)",
        "author": "@abrignoni, @AlexisBrignoni, Codex",
        "creation_date": "2021-08-15",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Permissions",
        "notes": "Last Access Persistent (tp), Last Access Cached (tc), Last Access Background "
                 "(tb), Last Access Foreground (tf), Last Access Foreground Service (tfs) and "
                 "Last Access Top (tt) are the op element's tp, tc, tb, tf, tfs and tt "
                 "attributes: the last access time, read here as Unix milliseconds, recorded "
                 "under the uid state each header names. Duration is the d attribute. The "
                 "reject time attributes of the same element (rp, rt, rfs, rf, rb, rc) are not "
                 "read. None of the images listed in sample_data holds this form, so the column "
                 "mapping was checked on a constructed file only. Only the first appops.xml "
                 "found is read. "
                 "Reference: Android Open Source Project, AppOpsService.java at "
                 "android-9.0.0_r1: UID_STATE_TIME_ATTRS, "
                 "https://android.googlesource.com/platform/frameworks/base/+/refs/tags/"
                 "android-9.0.0_r1/services/core/java/com/android/server/AppOpsService.java#155; "
                 "the times are System.currentTimeMillis() values, "
                 "https://android.googlesource.com/platform/frameworks/base/+/refs/tags/"
                 "android-9.0.0_r1/services/core/java/com/android/server/AppOpsService.java#1611, "
                 "written by writeState, "
                 "https://android.googlesource.com/platform/frameworks/base/+/refs/tags/"
                 "android-9.0.0_r1/services/core/java/com/android/server/AppOpsService.java#2451. "
                 "Op codes and names: AppOpsManager.java sAppOpInfos at android-14.0.0_r1, "
                 "https://android.googlesource.com/platform/frameworks/base/+/refs/tags/"
                 "android-14.0.0_r1/core/java/android/app/AppOpsManager.java#2347; the table in "
                 "this module names codes 0 to 120 and reports a higher code as its number.",
        "paths": ('*/system/appops.xml',),
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "anne_a15": "Android 15 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
    }
}

import datetime
import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc, abxread, checkabx

INVALID_XML_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
BARE_AMPERSAND = re.compile(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9A-Fa-f]+);)')

PERMISSION_OP = {
    "0": "COARSE_LOCATION", "1": "FINE_LOCATION", "2": "GPS", "3": "VIBRATE", "4": "READ_CONTACTS",
    "5": "WRITE_CONTACTS", "6": "READ_CALL_LOG", "7": "WRITE_CALL_LOG", "8": "READ_CALENDAR",
    "9": "WRITE_CALENDAR", "10": "WIFI_SCAN", "11": "POST_NOTIFICATION", "12": "NEIGHBORING_CELLS",
    "13": "CALL_PHONE", "14": "READ_SMS", "15": "WRITE_SMS", "16": "RECEIVE_SMS", "17": "RECEIVE_EMERGENCY_SMS",
    "18": "RECEIVE_MMS", "19": "RECEIVE_WAP_PUSH", "20": "SEND_SMS", "21": "READ_ICC_SMS", "22": "WRITE_ICC_SMS",
    "23": "WRITE_SETTINGS", "24": "SYSTEM_ALERT_WINDOW", "25": "ACCESS_NOTIFICATIONS", "26": "CAMERA",
    "27": "RECORD_AUDIO", "28": "PLAY_AUDIO", "29": "READ_CLIPBOARD", "30": "WRITE_CLIPBOARD",
    "31": "TAKE_MEDIA_BUTTONS", "32": "TAKE_AUDIO_FOCUS", "33": "AUDIO_MASTER_VOLUME", "34": "AUDIO_VOICE_VOLUME",
    "35": "AUDIO_RING_VOLUME", "36": "AUDIO_MEDIA_VOLUME", "37": "AUDIO_ALARM_VOLUME", "38": "AUDIO_NOTIFICATION_VOLUME",
    "39": "AUDIO_BLUETOOTH_VOLUME", "40": "WAKE_LOCK", "41": "MONITOR_LOCATION", "42": "MONITOR_HIGH_POWER_LOCATION",
    "43": "GET_USAGE_STATS", "44": "MUTE_MICROPHONE", "45": "TOAST_WINDOW", "46": "PROJECT_MEDIA", "47": "ACTIVATE_VPN",
    "48": "WRITE_WALLPAPER", "49": "ASSIST_STRUCTURE", "50": "ASSIST_SCREENSHOT", "51": "READ_PHONE_STATE",
    "52": "ADD_VOICEMAIL", "53": "USE_SIP", "54": "PROCESS_OUTGOING_CALLS", "55": "USE_FINGERPRINT",
    "56": "BODY_SENSORS", "57": "READ_CELL_BROADCASTS", "58": "MOCK_LOCATION", "59": "READ_EXTERNAL_STORAGE",
    "60": "WRITE_EXTERNAL_STORAGE", "61": "TURN_SCREEN_ON", "62": "GET_ACCOUNTS", "63": "RUN_IN_BACKGROUND",
    "64": "AUDIO_ACCESSIBILITY_VOLUME", "65": "READ_PHONE_NUMBERS", "66": "REQUEST_INSTALL_PACKAGES",
    "67": "ENTER_PICTURE_IN_PICTURE_ON_HIDE", "68": "INSTANT_APP_START_FOREGROUND", "69": "ANSWER_PHONE_CALLS",
    "70": "OP_RUN_ANY_IN_BACKGROUND", "71": "OP_CHANGE_WIFI_STATE", "72": "OP_REQUEST_DELETE_PACKAGES",
    "73": "OP_BIND_ACCESSIBILITY_SERVICE", "74": "ACCEPT_HANDOVER", "75": "MANAGE_IPSEC_TUNNELS",
    "76": "START_FOREGROUND", "77": "BLUETOOTH_SCAN", "78": "BIOMETRIC", "79": "ACTIVITY_RECOGNITION",
    "80": "SMS_FINANCIAL_TRANSACTIONS", "81": "READ_MEDIA_AUDIO", "82": "WRITE_MEDIA_AUDIO", "83": "READ_MEDIA_VIDEO",
    "84": "WRITE_MEDIA_VIDEO", "85": "READ_MEDIA_IMAGES", "86": "WRITE_MEDIA_IMAGES", "87": "LEGACY_STORAGE",
    "88": "ACCESS_ACCESSIBILITY", "89": "READ_DEVICE_IDENTIFIERS", "90": "ACCESS_MEDIA_LOCATION", "91": "QUERY_ALL_PACKAGES",
    "92": "MANAGE_EXTERNAL_STORAGE", "93": "INTERACT_ACROSS_PROFILES", "94": "ACTIVATE_PLATFORM_VPN",
    "95": "LOADER_USAGE_STATS", "96": "deprecated", "97": "AUTO_REVOKE_PERMISSIONS_IF_UNUSED",
    "98": "OP_AUTO_REVOKE_MANAGED_BY_INSTALLER", "99": "NO_ISOLATED_STORAGE", "100": "OP_PHONE_CALL_MICROPHONE",
    "101": "OP_PHONE_CALL_CAMERA", "102": "RECORD_AUDIO_HOTWORD", "103": "MANAGE_ONGOING_CALLS",
    "104": "MANAGE_CREDENTIALS", "105": "USE_ICC_AUTH_WITH_DEVICE_IDENTIFIER", "106": "RECORD_AUDIO_OUTPUT",
    "107": "SCHEDULE_EXACT_ALARM", "108": "OP_FINE_LOCATION_SOURCE", "109": "OP_COARSE_LOCATION_SOURCE",
    "110": "MANAGE_MEDIA", "111": "OP_BLUETOOTH_CONNECT", "112": "OP_UWB_RANGING", "113": "OP_ACTIVITY_RECOGNITION_SOURCE",
    "114": "OP_BLUETOOTH_ADVERTISE", "115": "OP_RECORD_INCOMING_PHONE_AUDIO", "116": "OP_NEARBY_WIFI_DEVICES",
    "117": "OP_ESTABLISH_VPN_SERVICE", "118": "OP_ESTABLISH_VPN_MANAGER", "119": "OP_ACCESS_RESTRICTED_SETTINGS",
    "120": "RECEIVE_SOUNDTRIGGER_AUDIO",
}


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


def _appops_root(file_found):
    if checkabx(file_found):
        return abxread(file_found, False).getroot()
    try:
        return ET.parse(file_found).getroot()
    except ET.ParseError:
        with open(file_found, encoding='utf-8', errors='replace') as f:
            xml = BARE_AMPERSAND.sub('&amp;', INVALID_XML_CHARS.sub('', f.read()))
        try:
            return ET.fromstring(xml)
        except ET.ParseError as ex:
            logfunc(f'Skipping unparseable XML {file_found}: {ex}')
            return ET.Element('empty')


def _appops_file(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('appops.xml'):
            return file_found
    return ''


@artifact_processor
def get_appops(context):
    files_found = context.get_files_found()
    source_path = _appops_file(files_found)
    data_list = []
    if source_path:
        root = _appops_root(source_path)
        for elem in root.iter('pkg'):
            pkg = elem.attrib['n']
            for subelem in elem:
                for op in subelem:
                    permission = PERMISSION_OP.get(op.attrib.get('n'), op.attrib.get('n'))
                    for entry in op:
                        access = _ms_to_utc(entry.attrib.get('t'))
                        reject = _ms_to_utc(entry.attrib.get('r'))
                        data_list.append((access, reject, pkg, entry.attrib.get('id', ''),
                                          entry.attrib.get('pp', ''), entry.attrib.get('pu', ''), permission))

    data_headers = (('Access Timestamp', 'datetime'), ('Reject Timestamp', 'datetime'), 'Package Name', 'ID', 'Proxy Package Name', 'Proxy Package UID', 'Permission')
    return data_headers, data_list, source_path


@artifact_processor
def get_appops_legacy(context):
    files_found = context.get_files_found()
    source_path = _appops_file(files_found)
    data_list = []
    if source_path:
        root = _appops_root(source_path)
        for elem in root.iter('pkg'):
            pkg = elem.attrib['n']
            for subelem in elem:
                for op in subelem:
                    a = op.attrib
                    # legacy rows carry the tp/tc/tb/tf/tfs/tt time attributes directly on the op element
                    if not any(a.get(k) for k in ('tp', 'tc', 'tb', 'tf', 'tfs', 'tt')):
                        continue
                    permission = PERMISSION_OP.get(a.get('n'), a.get('n'))
                    data_list.append((_ms_to_utc(a.get('tp')), _ms_to_utc(a.get('tc')), _ms_to_utc(a.get('tb')),
                                      _ms_to_utc(a.get('tf')), _ms_to_utc(a.get('tfs')), _ms_to_utc(a.get('tt')),
                                      pkg, a.get('d', ''), a.get('pp', ''), a.get('pu', ''), permission))

    data_headers = (('Last Access Persistent (tp)', 'datetime'), ('Last Access Cached (tc)', 'datetime'), ('Last Access Background (tb)', 'datetime'), ('Last Access Foreground (tf)', 'datetime'), ('Last Access Foreground Service (tfs)', 'datetime'), ('Last Access Top (tt)', 'datetime'), 'Package Name', 'Duration', 'Proxy Package Name', 'Proxy Package UID', 'Permission')
    return data_headers, data_list, source_path
