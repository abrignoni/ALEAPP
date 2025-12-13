import os
import datetime
import xml.etree.ElementTree as ET
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, abxread, checkabx

def get_appops(files_found, report_folder, seeker, wrap_text):

    permission_op = {
    "0":"COARSE_LOCATION",
    "1":"FINE_LOCATION",
    "2":"GPS",
    "3":"VIBRATE",
    "4":"READ_CONTACTS",
    "5":"WRITE_CONTACTS",
    "6":"READ_CALL_LOG",
    "7":"WRITE_CALL_LOG",
    "8":"READ_CALENDAR",
    "9":"WRITE_CALENDAR",
    "10":"WIFI_SCAN",
    "11":"POST_NOTIFICATION",
    "12":"NEIGHBORING_CELLS",
    "13":"CALL_PHONE",
    "14":"READ_SMS",
    "15":"WRITE_SMS",
    "16":"RECEIVE_SMS",
    "17":"RECEIVE_EMERGECY_SMS",
    "18":"RECEIVE_MMS",
    "19":"RECEIVE_WAP_PUSH",
    "20":"SEND_SMS",
    "21":"READ_ICC_SMS",
    "22":"WRITE_ICC_SMS",
    "23":"WRITE_SETTINGS",
    "24":"SYSTEM_ALERT_WINDOW",
    "25":"ACCESS_NOTIFICATIONS",
    "26":"CAMERA",
    "27":"RECORD_AUDIO",
    "28":"PLAY_AUDIO",
    "29":"READ_CLIPBOARD",
    "30":"WRITE_CLIPBOARD",
    "31":"TAKE_MEDIA_BUTTONS",
    "32":"TAKE_AUDIO_FOCUS",
    "33":"AUDIO_MASTER_VOLUME",
    "34":"AUDIO_VOICE_VOLUME",
    "35":"AUDIO_RING_VOLUME",
    "36":"AUDIO_MEDIA_VOLUME",
    "37":"AUDIO_ALARM_VOLUME",
    "38":"AUDIO_NOTIFICATION_VOLUME",
    "39":"AUDIO_BLUETOOTH_VOLUME",
    "40":"WAKE_LOCK",
    "41":"MONITOR_LOCATION",
    "42":"MONITOR_HIGH_POWER_LOCATION",
    "43":"GET_USAGE_STATS",
    "44":"MUTE_MICROPHONE",
    "45":"TOAST_WINDOW",
    "46":"PROJECT_MEDIA",
    "47":"ACTIVATE_VPN",
    "48":"WRITE_WALLPAPER",
    "49":"ASSIST_STRUCTURE",
    "50":"ASSIST_SCREENSHOT",
    "51":"READ_PHONE_STATE",
    "52":"ADD_VOICEMAIL",
    "53":"USE_SIP",
    "54":"PROCESS_OUTGOING_CALLS",
    "55":"USE_FINGERPRINT",
    "56":"BODY_SENSORS",
    "57":"READ_CELL_BROADCASTS",
    "58":"MOCK_LOCATION",
    "59":"READ_EXTERNAL_STORAGE",
    "60":"WRITE_EXTERNAL_STORAGE",
    "61":"TURN_SCREEN_ON",
    "62":"GET_ACCOUNTS",
    "63":"RUN_IN_BACKGROUND",
    "64":"AUDIO_ACCESSIBILITY_VOLUME",
    "65":"READ_PHONE_NUMBERS",
    "66":"REQUEST_INSTALL_PACKAGES",
    "67":"ENTER_PICTURE_IN_PICTURE_ON_HIDE",
    "68":"INSTANT_APP_START_FOREGROUND",
    "69":"ANSWER_PHONE_CALLS",
    "70":"OP_RUN_ANY_IN_BACKGROUND",
    "71":"OP_CHANGE_WIFI_STATE",
    "72":"OP_REQUEST_DELETE_PACKAGES",
    "73":"OP_BIND_ACCESSIBILITY_SERVICE",
    "74":"ACCEPT_HANDOVER",
    "75":"MANAGE_IPSEC_HANDOVERS",
    "76":"START_FOREGROUND",
    "77":"BLUETOOTH_SCAN",
    "78":"BIOMETRIC",
    "79":"ACTIVITY_RECOGNITION",
    "80":"SMS_FINANCIAL_TRANSACTIONS",
    "81":"READ_MEDIA_AUDIO",
    "82":"WRITE_MEDIA_AUDIO",
    "83":"READ_MEDIA_VIDEO",
    "84":"WRITE_MEDIA_VIDEO",
    "85":"READ_MEDIA_IMAGES",
    "86":"WRITE_MEDIA_IMAGES",
    "87":"LEGACY_STORAGE",
    "88":"ACCESS_ACCESSIBILITY",
    "89":"READ_DEVICE_IDENTIFIERS",
    "90":"ACCESS_MEDIA_LOCATION",
    "91":"QUERY_ALL_PACKAGES",
    "92":"MANAGE_EXTERNAL_STORAGE",
    "93":"NTERACT_ACROSS_PROFILES",
    "94":"ACTIVATE_PLATFORM_VPN",
    "95":"LOADER_USAGE_STATS",
    "96":"deprecated",
    "97":"AUTO_REVOKE_PERMISSIONS_IF_UNUSED",
    "98":"OP_AUTO_REVOKE_MANAGED_BY_INSTALLER",
    "99":"NO_ISOLATED_STORAGE",
    "100":"OP_PHONE_CALL_MICROPHONE",
    "101":"OP_PHONE_CALL_CAMERA",
    "102":"RECORD_AUDIO_HOTWORD",
    "103":"MANAGE_ONGOING_CALLS",
    "104":"MANAGE_CREDENTIALS",
    "105":"USE_ICC_AUTH_WITH_DEVICE_IDENTIFIER",
    "106":"RECORD_AUDIO_OUTPUT",
    "107":"SCHEDULE_EXACT_ALARM",
    "108":"OP_FINE_LOCATION_SOURCE",
    "109":"OP_COARSE_LOCATION_SOURCE",
    "110":"MANAGE_MEDIA",
    "111":"OP_BLUETOOTH_CONNECT",
    "112":"OP_UWB_RANGING",
    "113":"OP_ACTIVITY_RECOGNITION_SOURCE",
    "114":"OP_BLUETOOTH_ADVERTISE",
    "115":"OP_RECORD_INCOMING_PHONE_AUDIO",
    "116":"OP_NEARBY_WIFI_DEVICES",
    "117":"OP_ESTABLISH_VPN_SERVICE",
    "118":"OP_ESTABLISH_VPN_MANAGER",
    "119":"OP_ACCESS_RESTRICTED_SETTINGS",
    "120":"RECEIVE_SOUNDTRIGGER_AUDIO",
    }

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('appops.xml'):
            continue # Skip all other files
        
        data_list = []
        #check if file is abx
        if (checkabx(file_found)):
            multi_root = False
            tree = abxread(file_found, multi_root)
        else:
            tree = ET.parse(file_found)
        root = tree.getroot()
        
        for elem in root.iter('pkg'):
            pkg = elem.attrib['n']
            for subelem in elem:
                for subelem2 in subelem:
                    op_n = subelem2.attrib.get('n')
                    permission = ''
                    for key, value in permission_op.items():
                        if op_n == key:
                            permission = value
                            break
                        else: permission = op_n
                    
                    for subelem3 in subelem2:
                        timesr = subelem3.attrib.get('r')
                        timest = subelem3.attrib.get('t')
                        pp = subelem3.attrib.get('pp')
                        pu = subelem3.attrib.get('pu')
                        id = subelem3.attrib.get('id')
                        if timesr:
                            timestampr = (datetime.datetime.utcfromtimestamp(int(timesr)/1000).strftime('%Y-%m-%d %H:%M:%S'))
                        else:
                            timestampr = ''
                        if timest:	
                            timestampt = (datetime.datetime.utcfromtimestamp(int(timest)/1000).strftime('%Y-%m-%d %H:%M:%S'))
                        else:
                            timestampt = ''
                        if not pp:
                            pp = ''
                        if not pu:
                            pu = ''
                        if not id:
                            id = ''
                            
                        data_list.append((timestampt, timestampr, pkg, id, pp, pu, permission))            
        
        if data_list:
            report = ArtifactHtmlReport('Appops.xml')
            report.start_artifact_report(report_folder, 'Appops.xml')
            report.add_script()
            data_headers = ('Access Timestamp', 'Reject Timestamp', 'Package Name', 'ID', 'Proxy Package Name', 'Proxy Package UID', 'Permission')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Appops.xml data'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Appops.xml data'
            timeline(report_folder, tlactivity, data_list, data_headers)
        
        else: #Android 9 and below (?)
            for elem in root.iter('pkg'):
                pkg = elem.attrib['n']
                
                #print(pkg)
                for subelem in elem:
                    for subelem2 in subelem:
                        times_tp = subelem2.attrib.get('tp')
                        times_tc = subelem2.attrib.get('tc')
                        times_tb = subelem2.attrib.get('tb')
                        times_tf = subelem2.attrib.get('tf')
                        times_tfs = subelem2.attrib.get('tfs')
                        times_tt = subelem2.attrib.get('tt')
                        pp = subelem2.attrib.get('pp')
                        pu = subelem2.attrib.get('pu')
                        n = subelem2.attrib.get('n')
                        permission = ''
                        for key, value in permission_op.items():
                            if n == key:
                                permission = value
                                break
                            else: permission = n
                        
                        d = subelem2.attrib.get('d')
                        if times_tp:
                            timestamp_tp = (datetime.datetime.utcfromtimestamp(int(times_tp)/1000).strftime('%Y-%m-%d %H:%M:%S'))
                        else:
                            timestamp_tp = ''
                        if times_tc:
                            timestamp_tc = (datetime.datetime.utcfromtimestamp(int(times_tc)/1000).strftime('%Y-%m-%d %H:%M:%S'))
                        else:
                            timestamp_tc = ''
                        if times_tb:
                            timestamp_tb = (datetime.datetime.utcfromtimestamp(int(times_tb)/1000).strftime('%Y-%m-%d %H:%M:%S'))
                        else:
                            timestamp_tb = ''
                        if times_tf:
                            timestamp_tf = (datetime.datetime.utcfromtimestamp(int(times_tf)/1000).strftime('%Y-%m-%d %H:%M:%S'))
                        else:
                            timestamp_tf = '' 
                        if times_tfs:
                            timestamp_tfs = (datetime.datetime.utcfromtimestamp(int(times_tfs)/1000).strftime('%Y-%m-%d %H:%M:%S'))
                        else:
                            timestamp_tfs = ''
                        if times_tt:
                            timestamp_tt = (datetime.datetime.utcfromtimestamp(int(times_tt)/1000).strftime('%Y-%m-%d %H:%M:%S'))
                        else:
                            timestamp_tt = ''                
                        if not pp:
                            pp = ''
                        if not pu:
                            pu = ''
                        if not n:
                            n = ''
                        if not d:
                            d = ''
                        
                        data_list.append((timestamp_tp, timestamp_tc, timestamp_tb, timestamp_tf, timestamp_tfs, timestamp_tt, pkg, d, pp, pu, permission))
                
                if data_list:
                    report = ArtifactHtmlReport('Appops.xml')
                    report.start_artifact_report(report_folder, 'Appops.xml')
                    report.add_script()
                    data_headers = ('Timestamp TP', 'Timestamp TC', 'Timestamp TB', 'Timestamp TF', 'Timestamp TFS', 'Timestamp TT',  'Package Name', 'Duration', 'Proxy Package Name', 'Proxy Package UID', 'Permission')
                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    
                    tsvname = f'Appops.xml data'
                    tsv(report_folder, data_headers, data_list, tsvname)
                    
                    tlactivity = f'Appops.xml data'
                    timeline(report_folder, tlactivity, data_list, data_headers)
                
                else:
                    logfunc('No Appops.xml data available')
            
__artifacts__ = {
        "appops": (
                "Permissions",
                ('*/system/appops.xml'),
                get_appops)
}