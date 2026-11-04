__artifacts_v2__ = {
    "sconeCallDataLogs": {
        "name": "Call Data Logs (Scone)",
        "description": "Rows of the CallDataLogs table that the Google app "
                       "com.google.android.apps.scone writes when a call ends: the call's date, type, "
                       "network operator code, roaming state, audio device, disconnect reason and "
                       "call quality fields.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-29",
        "last_update_date": "2026-10-29",
        "requirements": "none",
        "category": "Call Logs",
        "notes": "Reads the CallDataLogs table of call_data_logs.db, in the device-encrypted storage "
                 "(user_de) of the Google app com.google.android.apps.scone. The app is closed source. "
                 "Meanings come from the build installed on pixel7a_a14 (base.apk, SHA-256 "
                 "28c014f45a14f1e7d8ad3fa073d057445aa2d6386fc98a624f4be162460fbc52), decompiled with jadx "
                 "1.5.6; its class names are obfuscated; no other build was decompiled, and the builds on "
                 "the other tested images were not checked. In that build one class inserts a row when a "
                 "call ends (it logs \"Add Call Data for Call End except Bad Quality\") and is the only "
                 "code in the decompile that inserts into the table; a second path updates Call Issue and "
                 "the bad-quality fields of the row with the same Call ID. Call Date is the date when the "
                 "build handled the call's disconnect or end, formatted yyyy/MM/dd with the zone the app "
                 "process took when it loaded its call-data class (a static formatter built with "
                 "ZoneId.systemDefault()), so a zone change is not reflected until the process restarts; "
                 "the report shows it as YYYY-MM-DD. It is a calendar date with no time; the call log and "
                 "other artifacts hold the times. Network Operator is "
                 "TelephonyManager.getNetworkOperator() and Roaming TelephonyManager.isNetworkRoaming(), "
                 "both read at that moment; Audio Device is BT, HEADSET, SPEAKER or EARPIECE from the "
                 "AudioManager state at that moment (Bluetooth SCO on, wired headset on, speakerphone on, "
                 "otherwise earpiece); UNKNOWN is the enum's reset value and is not read from "
                 "AudioManager, and 4 rows on pixel7a_a14 held it. Call Type is CS, VOLTE, VOWIFI, VONR "
                 "or UNKNOWN from the build's own enum; it is CS when the disconnect data did not come "
                 "from IMS, and otherwise is set from the voice network type or by a branch that was not "
                 "traced. Disconnect Reason is the disconnect code as stored: for an IMS call it is "
                 "ImsReasonInfo.getCode(), except that the build stores 510 for code 335 when the IMS "
                 "extra message contains CC_TERM_NOREPLY_TMR_EXPIRED; for any other call it is the "
                 "precise disconnect cause from PhoneStateListener.onCallDisconnectCauseChanged. For "
                 "VOLTE, VOWIFI and VONR rows the code is given the name of the "
                 "android.telephony.ims.ImsReasonInfo constant with that value "
                 "(https://android.googlesource.com/platform/frameworks/base/+/6e47c7075b91983ae501114425ea25e6df7690c8/telephony/java/android/telephony/ims/ImsReasonInfo.java, "
                 "AOSP frameworks/base commit 6e47c7075b91983ae501114425ea25e6df7690c8, "
                 "android14-release); other rows show the number only. Call Issue is BAD_AUDIO, "
                 "CALL_DROP, NO_ISSUE or UNKNOWN from the build's enum; how the build decides a drop was "
                 "not traced. Call ID is a random UUID the build makes for each call; it is not shared "
                 "with the call log, so rows cannot be joined to the call log by it. Roaming and Bad "
                 "Quality are the stored 1 and 0 shown as Yes and No. Start Call Type, Bad Call Type, "
                 "Subscription ID and the as-stored columns are reported as the build writes them; their "
                 "units and codes were not resolved. Not reported: ssid, which held <unknown ssid> or "
                 "nothing on every row of the tested images; signal_level, which this build never writes "
                 "and which was empty on every row; and tx_bad_quality_cause, which held 0 on every row. "
                 "Rows with neither a Call Date nor a Call ID are left out: on the tested images 430 such "
                 "rows on 4 images held the build's reset values (UNKNOWN types and issue, disconnect "
                 "reason 0, no operator, a subscription ID), not call data, and one of them carried a "
                 "Start Call Type. Their origin was not traced. When the date it last checked has "
                 "changed, the build deletes rows dated more than two months back, which never matches a "
                 "row with no date, and then keeps the 1,000 rows with the latest dates, which removes "
                 "undated rows first. The storage views one extraction can hold are read once, and a "
                 "second Android user's database is read as its own; Android User held 0 on every row of "
                 "the tested images. On the tested images: 671 rows on 5 of 22 images (hickman_a13 37, "
                 "pixel3_a12 7, pixel7a_a14 594, russell_a14 13, russell_pixel6a_a13 20); "
                 "call_data_logs.db was also on pixel3_a11, with no rows, and on hc_pixel8pro_a17, whose "
                 "7 rows were all left out as above. One row on pixel7a_a14 had a Call ID and no Call "
                 "Date. Roaming was Yes on 1 row (russell_a14), Audio Device was BT on 2 rows "
                 "(hickman_a13 and pixel3_a12), and Call Issue was CALL_DROP or BAD_AUDIO on 1 row each, "
                 "both on russell_a14. Compared with each image's call log (voicemail entries, type 4, "
                 "left out), by date in the zone of persist.sys.timezone: on russell_pixel6a_a13 the rows "
                 "per date equalled the call log's on all 15 dates (20 and 20); on russell_a14 the call "
                 "log held more over the same span (21 against 13); on pixel7a_a14 and pixel3_a12 the "
                 "table held more rows than the call log on 25 of 47 and 3 of 5 of its dates. Because of "
                 "the deletes above the table is not a complete record of calls. Whether the rows that "
                 "exceed the call log are calls the call log no longer lists was not tested.",
        "paths": ('*/com.google.android.apps.scone/databases/call_data_logs.db*',),
        "output_types": "standard",
        "artifact_icon": "phone-call",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 0 rows",
            "anne_a15": "Android 15 | 0 rows",
            "cookbook_a11": "Android 11 | 0 rows",
            "emu_a15_oss2_v3": "Android 15 | 0 rows",
            "emu_a15_oss_v17": "Android 15 | 0 rows",
            "falken_a326u_a13": "Android 13 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "hickman_a13": "Android 13 | 37 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 7 rows",
            "pixel7a_a14": "Android 14 | 594 rows",
            "russell_a14": "Android 14 | 13 rows",
            "russell_pixel6a_a13": "Android 13 | 20 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 0 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
    }
}

import datetime
import sqlite3

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import user_files

# android.telephony.ims.ImsReasonInfo CODE_* constants (frameworks/base, android14-release).
_IMS_REASONS = {
    0: 'CODE_UNSPECIFIED',
    101: 'CODE_LOCAL_ILLEGAL_ARGUMENT',
    102: 'CODE_LOCAL_ILLEGAL_STATE',
    103: 'CODE_LOCAL_INTERNAL_ERROR',
    106: 'CODE_LOCAL_IMS_SERVICE_DOWN',
    107: 'CODE_LOCAL_NO_PENDING_CALL',
    108: 'CODE_LOCAL_ENDED_BY_CONFERENCE_MERGE',
    111: 'CODE_LOCAL_POWER_OFF',
    112: 'CODE_LOCAL_LOW_BATTERY',
    121: 'CODE_LOCAL_NETWORK_NO_SERVICE',
    122: 'CODE_LOCAL_NETWORK_NO_LTE_COVERAGE',
    123: 'CODE_LOCAL_NETWORK_ROAMING',
    124: 'CODE_LOCAL_NETWORK_IP_CHANGED',
    131: 'CODE_LOCAL_SERVICE_UNAVAILABLE',
    132: 'CODE_LOCAL_NOT_REGISTERED',
    141: 'CODE_LOCAL_CALL_EXCEEDED',
    142: 'CODE_LOCAL_CALL_BUSY',
    143: 'CODE_LOCAL_CALL_DECLINE',
    144: 'CODE_LOCAL_CALL_VCC_ON_PROGRESSING',
    145: 'CODE_LOCAL_CALL_RESOURCE_RESERVATION_FAILED',
    146: 'CODE_LOCAL_CALL_CS_RETRY_REQUIRED',
    147: 'CODE_LOCAL_CALL_VOLTE_RETRY_REQUIRED',
    148: 'CODE_LOCAL_CALL_TERMINATED',
    149: 'CODE_LOCAL_HO_NOT_FEASIBLE',
    150: 'CODE_LOCAL_IMS_NOT_SUPPORTED_ON_DEVICE',
    201: 'CODE_TIMEOUT_1XX_WAITING',
    202: 'CODE_TIMEOUT_NO_ANSWER',
    203: 'CODE_TIMEOUT_NO_ANSWER_CALL_UPDATE',
    240: 'CODE_CALL_BARRED',
    241: 'CODE_FDN_BLOCKED',
    243: 'CODE_IMEI_NOT_ACCEPTED',
    244: 'CODE_DIAL_MODIFIED_TO_USSD',
    245: 'CODE_DIAL_MODIFIED_TO_SS',
    246: 'CODE_DIAL_MODIFIED_TO_DIAL',
    247: 'CODE_DIAL_MODIFIED_TO_DIAL_VIDEO',
    248: 'CODE_DIAL_VIDEO_MODIFIED_TO_DIAL',
    249: 'CODE_DIAL_VIDEO_MODIFIED_TO_DIAL_VIDEO',
    250: 'CODE_DIAL_VIDEO_MODIFIED_TO_SS',
    251: 'CODE_DIAL_VIDEO_MODIFIED_TO_USSD',
    321: 'CODE_SIP_REDIRECTED',
    331: 'CODE_SIP_BAD_REQUEST',
    332: 'CODE_SIP_FORBIDDEN',
    333: 'CODE_SIP_NOT_FOUND',
    334: 'CODE_SIP_NOT_SUPPORTED',
    335: 'CODE_SIP_REQUEST_TIMEOUT',
    336: 'CODE_SIP_TEMPRARILY_UNAVAILABLE',
    337: 'CODE_SIP_BAD_ADDRESS',
    338: 'CODE_SIP_BUSY',
    339: 'CODE_SIP_REQUEST_CANCELLED',
    340: 'CODE_SIP_NOT_ACCEPTABLE',
    341: 'CODE_SIP_NOT_REACHABLE',
    342: 'CODE_SIP_CLIENT_ERROR',
    343: 'CODE_SIP_TRANSACTION_DOES_NOT_EXIST',
    351: 'CODE_SIP_SERVER_INTERNAL_ERROR',
    352: 'CODE_SIP_SERVICE_UNAVAILABLE',
    353: 'CODE_SIP_SERVER_TIMEOUT',
    354: 'CODE_SIP_SERVER_ERROR',
    361: 'CODE_SIP_USER_REJECTED',
    362: 'CODE_SIP_GLOBAL_ERROR',
    363: 'CODE_EMERGENCY_TEMP_FAILURE',
    364: 'CODE_EMERGENCY_PERM_FAILURE',
    365: 'CODE_SIP_USER_MARKED_UNWANTED',
    366: 'CODE_SIP_METHOD_NOT_ALLOWED',
    367: 'CODE_SIP_PROXY_AUTHENTICATION_REQUIRED',
    368: 'CODE_SIP_REQUEST_ENTITY_TOO_LARGE',
    369: 'CODE_SIP_REQUEST_URI_TOO_LARGE',
    370: 'CODE_SIP_EXTENSION_REQUIRED',
    371: 'CODE_SIP_INTERVAL_TOO_BRIEF',
    372: 'CODE_SIP_CALL_OR_TRANS_DOES_NOT_EXIST',
    373: 'CODE_SIP_LOOP_DETECTED',
    374: 'CODE_SIP_TOO_MANY_HOPS',
    376: 'CODE_SIP_AMBIGUOUS',
    377: 'CODE_SIP_REQUEST_PENDING',
    378: 'CODE_SIP_UNDECIPHERABLE',
    401: 'CODE_MEDIA_INIT_FAILED',
    402: 'CODE_MEDIA_NO_DATA',
    403: 'CODE_MEDIA_NOT_ACCEPTABLE',
    404: 'CODE_MEDIA_UNSPECIFIED',
    501: 'CODE_USER_TERMINATED',
    502: 'CODE_USER_NOANSWER',
    503: 'CODE_USER_IGNORE',
    504: 'CODE_USER_DECLINE',
    505: 'CODE_LOW_BATTERY',
    506: 'CODE_BLACKLISTED_CALL_ID',
    510: 'CODE_USER_TERMINATED_BY_REMOTE',
    511: 'CODE_USER_REJECTED_SESSION_MODIFICATION',
    512: 'CODE_USER_CANCELLED_SESSION_MODIFICATION',
    801: 'CODE_UT_NOT_SUPPORTED',
    802: 'CODE_UT_SERVICE_UNAVAILABLE',
    803: 'CODE_UT_OPERATION_NOT_ALLOWED',
    804: 'CODE_UT_NETWORK_ERROR',
    821: 'CODE_UT_CB_PASSWORD_MISMATCH',
    822: 'CODE_UT_SS_MODIFIED_TO_DIAL',
    823: 'CODE_UT_SS_MODIFIED_TO_USSD',
    824: 'CODE_UT_SS_MODIFIED_TO_SS',
    825: 'CODE_UT_SS_MODIFIED_TO_DIAL_VIDEO',
    901: 'CODE_ECBM_NOT_SUPPORTED',
    902: 'CODE_MULTIENDPOINT_NOT_SUPPORTED',
    1000: 'CODE_REGISTRATION_ERROR',
    1014: 'CODE_ANSWERED_ELSEWHERE',
    1015: 'CODE_CALL_PULL_OUT_OF_SYNC',
    1016: 'CODE_CALL_END_CAUSE_CALL_PULL',
    1017: 'CODE_REJECTED_ELSEWHERE',
    1100: 'CODE_CALL_DROP_IWLAN_TO_LTE_UNAVAILABLE',
    1201: 'CODE_SUPP_SVC_FAILED',
    1202: 'CODE_SUPP_SVC_CANCELLED',
    1203: 'CODE_SUPP_SVC_REINVITE_COLLISION',
    1300: 'CODE_IWLAN_DPD_FAILURE',
    1400: 'CODE_EPDG_TUNNEL_ESTABLISH_FAILURE',
    1401: 'CODE_EPDG_TUNNEL_REKEY_FAILURE',
    1402: 'CODE_EPDG_TUNNEL_LOST_CONNECTION',
    1403: 'CODE_MAXIMUM_NUMBER_OF_CALLS_REACHED',
    1404: 'CODE_REMOTE_CALL_DECLINE',
    1405: 'CODE_DATA_LIMIT_REACHED',
    1406: 'CODE_DATA_DISABLED',
    1407: 'CODE_WIFI_LOST',
    1408: 'CODE_IKEV2_AUTH_FAILURE',
    1500: 'CODE_RADIO_OFF',
    1501: 'CODE_NO_VALID_SIM',
    1502: 'CODE_RADIO_INTERNAL_ERROR',
    1503: 'CODE_NETWORK_RESP_TIMEOUT',
    1504: 'CODE_NETWORK_REJECT',
    1505: 'CODE_RADIO_ACCESS_FAILURE',
    1506: 'CODE_RADIO_LINK_FAILURE',
    1507: 'CODE_RADIO_LINK_LOST',
    1508: 'CODE_RADIO_UPLINK_FAILURE',
    1509: 'CODE_RADIO_SETUP_FAILURE',
    1510: 'CODE_RADIO_RELEASE_NORMAL',
    1511: 'CODE_RADIO_RELEASE_ABNORMAL',
    1512: 'CODE_ACCESS_CLASS_BLOCKED',
    1513: 'CODE_NETWORK_DETACH',
    1514: 'CODE_SIP_ALTERNATE_EMERGENCY_CALL',
    1515: 'CODE_UNOBTAINABLE_NUMBER',
    1516: 'CODE_NO_CSFB_IN_CS_ROAM',
    1517: 'CODE_SESSION_MODIFICATION_FAILED',
    1600: 'CODE_REJECT_UNKNOWN',
    1601: 'CODE_REJECT_ONGOING_CALL_WAITING_DISABLED',
    1602: 'CODE_REJECT_CALL_ON_OTHER_SUB',
    1603: 'CODE_REJECT_1X_COLLISION',
    1604: 'CODE_REJECT_SERVICE_NOT_REGISTERED',
    1605: 'CODE_REJECT_CALL_TYPE_NOT_ALLOWED',
    1606: 'CODE_REJECT_ONGOING_E911_CALL',
    1607: 'CODE_REJECT_ONGOING_CALL_SETUP',
    1608: 'CODE_REJECT_MAX_CALL_LIMIT_REACHED',
    1609: 'CODE_REJECT_UNSUPPORTED_SIP_HEADERS',
    1610: 'CODE_REJECT_UNSUPPORTED_SDP_HEADERS',
    1611: 'CODE_REJECT_ONGOING_CALL_TRANSFER',
    1612: 'CODE_REJECT_INTERNAL_ERROR',
    1613: 'CODE_REJECT_QOS_FAILURE',
    1614: 'CODE_REJECT_ONGOING_HANDOVER',
    1615: 'CODE_REJECT_VT_TTY_NOT_ALLOWED',
    1616: 'CODE_REJECT_ONGOING_CALL_UPGRADE',
    1617: 'CODE_REJECT_CONFERENCE_TTY_NOT_ALLOWED',
    1618: 'CODE_REJECT_ONGOING_CONFERENCE_CALL',
    1619: 'CODE_REJECT_VT_AVPF_NOT_ALLOWED',
    1620: 'CODE_REJECT_ONGOING_ENCRYPTED_CALL',
    1621: 'CODE_REJECT_ONGOING_CS_CALL',
    1622: 'CODE_EMERGENCY_CALL_OVER_WFC_NOT_AVAILABLE',
    1623: 'CODE_WFC_SERVICE_NOT_AVAILABLE_IN_THIS_LOCATION',
    1624: 'CODE_NETWORK_CONGESTION',
    3001: 'CODE_RETRY_ON_IMS_WITHOUT_RTT',
}
_IMS_CALL_TYPES = ('VOLTE', 'VOWIFI', 'VONR')
_COLUMNS = ('log_date', 'call_type', 'call_issue', 'call_disconnect_reason', 'carrier', 'roaming',
            'audio_device', 'start_call_type', 'wifi_signal_level', 'is_bad_quality', 'bad_call_type',
            'bad_call_duration', 'rx_bad_quality_cause', 'sub_id', 'call_id')


def _date(text):
    """log_date is the call's date formatted yyyy/MM/dd in the device's time zone; shown as YYYY-MM-DD."""
    try:
        return datetime.datetime.strptime(text, '%Y/%m/%d').date().isoformat()
    except (TypeError, ValueError):
        return text or ''


def _reason(call_type, code):
    if code is None:
        return ''
    if call_type in _IMS_CALL_TYPES and code in _IMS_REASONS:
        return f'{code} ({_IMS_REASONS[code]})'
    return str(code)


def _flag(value):
    return {'1': 'Yes', '0': 'No', 1: 'Yes', 0: 'No'}.get(value, '' if value is None else str(value))


def _as_stored(value):
    return '' if value is None else value


@artifact_processor
def sconeCallDataLogs(context):
    data_list = []
    sources = []
    for path, user in user_files(context, 'call_data_logs.db'):
        db = open_sqlite_db_readonly(path)
        if db is None:
            continue
        try:
            present = {row[1] for row in db.execute('PRAGMA table_info(CallDataLogs)')}
            select = ', '.join(c if c in present else 'NULL' for c in _COLUMNS)
            rows = db.execute(f'SELECT {select} FROM CallDataLogs ORDER BY _id DESC').fetchall()
        except sqlite3.Error as ex:
            logfunc(f'Call Data Logs (Scone): could not read {context.get_relative_path(path)}: {ex}')
            continue
        finally:
            db.close()
        sources.append(path)
        for (log_date, call_type, issue, reason, carrier, roaming, audio, start_type, wifi_level,
             bad, bad_type, bad_duration, rx_cause, sub_id, call_id) in rows:
            if not log_date and not call_id:
                # Rows with neither a date nor a call id held only column defaults on the tested images.
                continue
            data_list.append((_date(log_date), call_type or '', issue or '', _reason(call_type, reason),
                              carrier or '', _flag(roaming), audio or '', start_type or '',
                              _as_stored(wifi_level), _flag(bad), bad_type or '', _as_stored(bad_duration),
                              _as_stored(rx_cause), _as_stored(sub_id), call_id or '',
                              user))

    data_headers = ('Call Date', 'Call Type', 'Call Issue', 'Disconnect Reason',
                    'Network Operator (MCC+MNC)', 'Roaming', 'Audio Device', 'Start Call Type',
                    'Wi-Fi Signal Level (as stored)', 'Bad Quality', 'Bad Call Type',
                    'Bad Call Duration (as stored)', 'RX Bad Quality Cause (as stored)', 'Subscription ID', 'Call ID', 'Android User')
    return data_headers, data_list, '\n'.join(sources)
