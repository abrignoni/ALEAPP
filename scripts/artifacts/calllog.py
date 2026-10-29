__artifacts_v2__ = {
    "get_calllog": {
        "name": "Call logs ",
        "description": "Parses the call log (date, number, type, duration, the geocoded location stored for the number and transcription) from the contacts provider calllog.db, with the ICCID of the SIM account each call was placed or received on, where the extraction records the link.",
        "author": "@abrignoni, @AlexisBrignoni, Codex, Claude",
        "creation_date": "2020-03-02",
        "last_update_date": "2026-10-29",
        "requirements": "none",
        "category": "Call Logs",
        "notes": "The Android reference documents the DATE column as milliseconds since epoch and DURATION as seconds, and this parser decodes them that way, so the Call Date column is a converted millisecond timestamp and Duration in Secs is the stored value unchanged. The Type column decodes the AOSP CallLog.Calls codes 1 Incoming, 2 Outgoing, 3 Missed, 4 Voicemail, 5 Rejected, 6 Blocked and 7 Answered Externally. Any other stored value is shown as Unknown. Raw Call Type (as stored) preserves the source value beside the interpreted label. The same codes are applied to the Samsung contacts provider's calllog.db; whether Samsung stores other type values there is not established. Reference: Android Developers, 'CallLog.Calls' API reference, https://developer.android.com/reference/android/provider/CallLog.Calls (read 2026-10-03)\n\nSIM ICCID. CallLog.Calls keeps the call's phone account id in subscription_id and the service that owns the account in subscription_component_name. Both are shown as stored in Phone Account ID (as stored) and Phone Account Component; a NULL is shown blank. In AOSP the SIM phone account id is built by PhoneUtils.makePstnPhoneAccountHandleWithPrefix, which uses the full ICC serial number on the android12-release branch and the subscription id on the android13-release branch. The Android version alone does not tell which form a device stores: the pixel7a_a14 call log holds both forms across the same months, and why is not established. SIM ICCID is filled only from a link the extraction records, and ICCID Resolved Via names it. 'Stored value (matches siminfo)': the stored id equals an icc_id in the siminfo table of the telephony provider's telephony.db. 'Stored value, trailing F removed (matches siminfo)': it equals one once trailing F characters are removed from both values, and only one siminfo value matches that way. AOSP's getFullIccSerialNumber returns the ICC ID including hex digits; on pixel7a_a14 the ICCID-form stored ids carried a trailing F and the siminfo icc_id did not. 'siminfo subscription id': the component is com.android.phone's TelephonyConnectionService and the stored id equals a siminfo _id, which the Telephony provider defines as the subscription id. A subscription id under any other component, an id siminfo does not hold, an _id that maps to two different ICCIDs across telephony.db copies, and an extraction without telephony.db all leave SIM ICCID blank. A blank SIM ICCID means no recorded link was found, not that no SIM was used. On the corpora listed in sample_data every call under the TelephonyConnectionService component resolved. Rows under the com.samsung.android.messaging component (sharon_a14, samsungs20_a13) whose stored id does not match a siminfo icc_id are left blank; the sharon_a14 rows under that component that store a value matching a siminfo icc_id are filled from the stored value. References: Telephony PhoneUtils.java at android12-release commit 7be6599cbdfecbe0c01438478492deb015846fa8 and android13-release commit 838fd09d2f8ddbce1330bfceae8ea24d85cc9182 (https://android.googlesource.com/platform/packages/services/Telephony/+/7be6599cbdfecbe0c01438478492deb015846fa8/src/com/android/phone/PhoneUtils.java, https://android.googlesource.com/platform/packages/services/Telephony/+/838fd09d2f8ddbce1330bfceae8ea24d85cc9182/src/com/android/phone/PhoneUtils.java); frameworks/opt/telephony GsmCdmaPhone.java and uicc/IccRecords.java at android12-release commit 51302ef5e1a2f5c13b4db2650a1c52735ccca992; frameworks/base core/java/android/provider/CallLog.java and Telephony.java (SimInfo) at android14-release commit 6e47c7075b91983ae501114425ea25e6df7690c8 (all read 2026-10-29)",
        "paths": ('*/com.android.providers.contacts/databases/calllog.db*', '*/com.samsung.android.providers.contacts/databases/calllog.db*',
                  '*/user_de/*/com.android.providers.telephony/databases/telephony.db*'),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.providers.contacts | 11 rows",
            "galaxys10_a10": "Android 10 | com.samsung.android.providers.contacts | 24 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.providers.contacts | 705 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.providers.contacts | 12 rows",
            "pixel7a_a14": "Android 14 | com.android.providers.contacts | 2655 rows",
            "samsunga53_a14": "Android 14 | com.samsung.android.providers.contacts | 23 rows",
            "samsungs20_a13": "Android 13 | com.samsung.android.providers.contacts | 12 rows",
            "sharon_a14": "Android 14 | com.samsung.android.providers.contacts | 397 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.providers.contacts | 42 rows",
            "userb2_a13": "Android 13 | com.android.providers.contacts | 0 rows",
        },
        "html_columns": ['Type'],
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import unique_files

TELEPHONY_COMPONENT = 'com.android.phone/com.android.services.telephony.TelephonyConnectionService'

CALL_TYPE_ICONS = {
    'Incoming': ' <i data-feather="phone-incoming" stroke="green"></i>',
    'Outgoing': ' <i data-feather="phone-outgoing" stroke="green"></i>',
    'Missed': ' <i data-feather="phone-missed" stroke="red"></i>',
    'Voicemail': ' <i data-feather="voicemail" stroke="brown"></i>',
    'Rejected': ' <i data-feather="x" stroke="red"></i>',
    'Blocked': ' <i data-feather="phone-off" stroke="red"></i>',
    'Answered Externally': ' <i data-feather="phone-forwarded"></i>',
}


def read_siminfo(files_found):
    """Map each siminfo subscription id to its ICCID, over every telephony.db read."""
    iccids = {}
    read_paths = []
    for file_found in files_found:
        if not file_found.endswith('telephony.db'):
            continue
        try:
            db = open_sqlite_db_readonly(file_found)
            rows = db.execute('SELECT _id, icc_id FROM siminfo').fetchall()
            db.close()
        except Exception as e:  # pylint: disable=broad-exception-caught
            logfunc(f'siminfo not read from {file_found}: {e}')
            continue
        read_paths.append(file_found)
        for sub_id, icc_id in rows:
            if sub_id is not None and icc_id:
                iccids.setdefault(str(sub_id), set()).add(str(icc_id))
    return iccids, read_paths


def resolve_iccid(account_id, component, iccids):
    """The SIM ICCID for a call's phone account id, and how it was found."""
    if account_id is None or str(account_id) == '':
        return '', ''
    account_id = str(account_id)
    known = {icc for values in iccids.values() for icc in values}
    if account_id in known:
        return account_id, 'Stored value (matches siminfo)'
    stripped = account_id.rstrip('Ff')
    if stripped != account_id:
        matches = [icc for icc in known if icc.rstrip('Ff') == stripped]
        if len(matches) == 1:
            return matches[0], 'Stored value, trailing F removed (matches siminfo)'
    if component == TELEPHONY_COMPONENT and len(iccids.get(account_id, ())) == 1:
        return next(iter(iccids[account_id])), 'siminfo subscription id'
    return '', ''


@artifact_processor
def get_calllog(context):
    files_found = [str(file_found) for file_found in unique_files(context)]
    iccids, siminfo_paths = read_siminfo(files_found)

    data_list = []
    source_paths = []
    for file_found in files_found:
        if not file_found.endswith('calllog.db'):
            continue

        source_paths.append(file_found)
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        columns = {row[1] for row in cursor.execute('PRAGMA table_info(calls)')}
        account_id = 'subscription_id' if 'subscription_id' in columns else 'NULL'
        component = 'subscription_component_name' if 'subscription_component_name' in columns else 'NULL'
        cursor.execute(f'''
            SELECT
            date,
            CASE WHEN phone_account_address is NULL THEN ' ' ELSE phone_account_address END as phone_account_address,
            number,
            CASE
                WHEN type = 1 THEN  'Incoming'
                WHEN type = 2 THEN  'Outgoing'
                WHEN type = 3 THEN  'Missed'
                WHEN type = 4 THEN  'Voicemail'
                WHEN type = 5 THEN  'Rejected'
                WHEN type = 6 THEN  'Blocked'
                WHEN type = 7 THEN  'Answered Externally'
                ELSE 'Unknown'
            END as types,
            duration,
            CASE WHEN geocoded_location is NULL THEN ' ' ELSE geocoded_location END as geocoded_location,
            countryiso,
            CASE WHEN _data is NULL THEN ' ' ELSE _data END as _data,
            CASE WHEN mime_type is NULL THEN ' ' ELSE mime_type END as mime_type,
            CASE WHEN transcription is NULL THEN ' ' ELSE transcription END as transcription,
            deleted,
            type,
            {account_id} as subscription_id,
            {component} as subscription_component_name
            FROM calls
        ''')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            call_date = datetime.datetime.fromtimestamp(int(row[0]) / 1000, datetime.timezone.utc) if row[0] else ''
            call_type = row[3]
            call_type_html = call_type + CALL_TYPE_ICONS.get(call_type, '')
            iccid, resolved_via = resolve_iccid(row[12], row[13], iccids)
            data_list.append((call_date, row[1], iccid, resolved_via, row[12] if row[12] is not None else '',
                              row[13] if row[13] is not None else '', row[2], row[11], call_type_html, str(row[4]),
                              row[5], row[6], row[7], row[8], row[9], str(row[10])))

    if any(row[2] for row in data_list):
        source_paths.extend(siminfo_paths)
    data_headers = (('Call Date', 'datetime'), 'Phone Account Address', 'SIM ICCID', 'ICCID Resolved Via',
                    'Phone Account ID (as stored)', 'Phone Account Component', ('Partner', 'phonenumber'),
                    'Raw Call Type (as stored)', 'Type', 'Duration in Secs', 'Partner Location', 'Country ISO', 'Data',
                    'Mime Type', 'Transcription', 'Deleted')
    return data_headers, data_list, '\n'.join(source_paths)
