""""
Developed by Evangelos Dragonas (@theAtropos4n6)

Research for this artifact was conducted by Evangelos Dragonas, Costas Lambrinoudakis and Michael Kotsis. 
For more information read their research paper here: Link_to_be_uploaded

Updated:13-04-2023

Dahua Technology (DMSS) is a well-known app that is used to both remotely access/operate CCTV systems and control IoT security systems. Currently the following information can be interpreted:

-Dahua CCTV - Channels: retrieves info for any available CCTV record channels 
-Dahua CCTV - Info: Information about the CCTV system
-Dahua CCTV - User Created Media: The media files the user created while viewing footage from the CCTV

-Dahua IoT - Registered Sensors (without DMSS account): List of IoT Registered Sensors that are connected with app ('.db' gets populated when the application is used without a DMSS account).
-Dahua IoT - Registered Cloud Devices (without DMSS account): List of IoT Registered Cloud Devices that are connected with app ('.db' gets populated when the application is used without a DMSS account).
-Dahua IoT - Notifications (without DMSS account): Cached notifications of the IoT smart home ('.db' gets populated when the application is used without a DMSS account).

-Dahua IoT - Registered Sensors (-x- DMSS account): List of IoT Registered Sensors that are connected with app ('x-account.db' gets populated when the application is used with the -x- DMSS account).
-Dahua IoT - Registered Cloud Devices (-x- DMSS account): List of IoT Registered Cloud Devices that are connected with app ('x-account.db' gets populated when the application is used with the -x- DMSS account).
-Dahua IoT - Notifications (-x- DMSS account): Cached notifications of the IoT smart home ('x-account.db' gets populated when the application is used with the -x- DMSS account).

"""
import sqlite3
import os
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly,media_to_html

def get_dmss(files_found, report_folder, seeker, wrap_text):
    media_data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        file_name = os.path.basename(file_found)
        if file_name == 'devicechannel.db':
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            
            #Dahua CCTV - Channels
            cursor.execute('''
                select
                    devices.devicename,
                    num,
                    name,
                    CASE
                        when isfavorite = '1' then 'Yes' 
                        else 'No'
                    end isfavorite
                from channels
                LEFT JOIN devices on did = devices.id
                 ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Dahua CCTV - Channels')
                report.start_artifact_report(report_folder, 'Dahua CCTV - Channels')
                report.add_script()
                data_headers = ('Device Name','Channel No.','Channel Name','Favorite') 
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Dahua CCTV - Channels'
                tsv(report_folder, data_headers, data_list, tsvname)
            
            else:
                logfunc(f'No Dahua CCTV - Channels data available')

            #Dahua CCTV - Info
            cursor.execute('''
                select
                    devicename,
                    channelcount,
                    uid,
                    ip,
                    port,
                    username,
                    password
                from devices
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Dahua CCTV - Info')
                report.start_artifact_report(report_folder, 'Dahua CCTV - Info')
                report.add_script()
                data_headers = ('Name/IP','Channels','UID','IP (Enc.)','Port (Enc.)','Username (Enc.)','Password (Enc.)') 
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Dahua CCTV - Info'
                tsv(report_folder, data_headers, data_list, tsvname)
                
            else:
                logfunc(f'No Dahua CCTV - Info data available')
            db.close()

        if file_name == '.db':
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            
            #-Dahua IoT - Registered Sensors (without DMSS account)
            cursor.execute('''
                select
                    name,
                    model,
                    sn,--sensor sn
                    type,
                    CASE
                        when alarmState='0' then 'Off'
                        when alarmState='1' then 'On'
                    end alarmState,
                    batteryPercent,
                    deviceSn,--Hub
                    disableDelay,
                    enableDelay,
                    CASE
                        when fullDayAlarm='0' then 'Off'
                        when fullDayAlarm='1' then 'On'
                    end fullDayAlarm,-- 24H Protection Zone
                    CASE
                        when sensitivity='1' then 'Low'
                        when sensitivity='2' then 'Medium'
                        when sensitivity='3' then 'High'
                    end sensitivity,
                    sensorCaps, --capabilities
                    tamper,
                    version --Program Version
                from AlarmPartEntity
                ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport(f'Dahua IoT - Registered Sensors (without DMSS account)')
                report.start_artifact_report(report_folder, f'Dahua IoT - Registered Sensors (without DMSS account)')
                report.add_script()
                data_headers = ('Device Name','Device Model','Device SN','Device Type','Alarm State','Battery Percent','Associated Hub SN','Disable Delay','Enable Delay','Full Day Alarm','Sensitivity','Capabilities','Tamper Status','Version') 
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13]))
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Dahua IoT - Registered Sensors (without DMSS account)'
                tsv(report_folder, data_headers, data_list, tsvname)
                
            else:
                logfunc(f'No Dahua IoT - Registered Sensors (without DMSS account) data available')

            #-Dahua IoT - Registered Cloud Devices (without DMSS account)
            cursor.execute('''
                select
                    devicename,
                    deviceModel,
                    channelcount,
                    isOnline,
                    CASE
                        when shareEnable='0' then 'Off'
                        when shareEnable='1' then 'On'
                    end shareEnable,
                    receiveShare,
                    sendShare,
                    username,
                    ability,
                    deviceCaps,
                    port,
                    rtspPort,
                    appVersion
                from CloudDevices
                ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport(f'Dahua IoT - Registered Cloud Devices (without DMSS account)')
                report.start_artifact_report(report_folder, f'Dahua IoT - Registered Cloud Devices (without DMSS account)')
                report.add_script()
                data_headers = ('Device Name','Device Model','Channels','Online','Shared Enabled','Receive Share From','Send Share To','Username','Abilities','Capabilities','Port','RTSP Port','App Version') 
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12]))
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Dahua IoT - Registered Cloud Devices (without DMSS account)'
                tsv(report_folder, data_headers, data_list, tsvname)
                
            else:
                logfunc(f'No Dahua IoT - Registered Cloud Devices (without DMSS account) data available')

             #Dahua IoT - Notifications (without DMSS account)
            cursor.execute('''
                select
                    datetime(alarmTime/1000,'unixepoch'),
                    alarmTimeStr,
                    areaName,
                    nickName,
                    sensorName,
                    alarmDeviceId,--Hub
                    alarmMessageId,--Message ID
                    case
                        when alarmTypeStr = 'gwMsg_ATSFault_Start' then 'ATS fault. Check network connection'
                        when alarmTypeStr = 'gwMsg_ATSFault_Stop' then 'ATS restored'
                        when alarmTypeStr = 'gwMsg_AreaAlarm_AddArea' then '"area name", added by "nickname"'
                        when alarmTypeStr = 'gwMsg_AreaAlarm_AreaDelete' then '"area name", removed by "nickname"'
                        when alarmTypeStr = 'gwMsg_AreaArmModeChange_Remote_DisArm' then '"area name", disarmed by "nickname"'
                        when alarmTypeStr = 'gwMsg_AreaArmModeChange_Remote_Arm_p1' then '"area name", Home mode activated by "nickname"'
                        when alarmTypeStr = 'gwMsg_ArmingFailure' then 'Unsuccessful arming "area name" attempt by "nickname"'
                        when alarmTypeStr = 'gwMsg_AlarmLocal_PassiveInfrared' then 'Motion detected, "device name" in "area name"'
                        when alarmTypeStr = 'gwMsg_AlarmLocal_DoorMagnetism_Start' then 'Opening detected, "device name" in "area name"'
                        when alarmTypeStr = 'gwMsg_AlarmLocal_DoorMagnetism_Stop' then 'Closing detected, "device name" in "area name"'
                        else alarmTypeStr 
                    end alarmTypeStr,
                    case
                        when checked = '1' then 'Yes'
                        when checked = '0' then 'No'
                    end checked
                from GeneralAlarmMessage
                ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Dahua IoT - Notifications (without DMSS account)')
                report.start_artifact_report(report_folder, 'Dahua IoT - Notifications (without DMSS account)')
                report.add_script()
                data_headers = ('Timestamp (UTC)','Timestamp (Local)','Area Name','Nickname','Device Name','Alarm Device ID','Alarm Message ID','Alarm Notification','Checked') 
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Dahua IoT - Notifications (without DMSS account)'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Dahua IoT - Notifications (without DMSS account)'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc(f'No Dahua IoT - Notifications (without DMSS account) data available')           
            db.close()

        if (file_name.startswith("ez") or len(file_name)>25) and file_name.endswith(".db"): 
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            
            #-Dahua IoT - Registered Sensors (-x- DMSS account)
            cursor.execute('''
                select
                    name,
                    model,
                    sn,--sensor sn
                    type,
                    CASE
                        when alarmState='0' then 'Off'
                        when alarmState='1' then 'On'
                    end alarmState,
                    batteryPercent,
                    deviceSn,--Hub
                    disableDelay,
                    enableDelay,
                    CASE
                        when fullDayAlarm='0' then 'Off'
                        when fullDayAlarm='1' then 'On'
                    end fullDayAlarm,-- 24H Protection Zone
                    CASE
                        when sensitivity='1' then 'Low'
                        when sensitivity='2' then 'Medium'
                        when sensitivity='3' then 'High'
                    end sensitivity,
                    sensorCaps, --capabilities
                    tamper,
                    version --Program Version
                from AlarmPartEntity
                ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport(f'Dahua IoT - Registered Sensors (Account- {file_name[:-3]})')
                report.start_artifact_report(report_folder, f'Dahua IoT - Registered Sensors (Account- {file_name[:-3]})')
                report.add_script()
                data_headers = ('Device Name','Device Model','Device SN','Device Type','Alarm State','Battery Percent','Associated Hub SN','Disable Delay','Enable Delay','Full Day Alarm','Sensitivity','Capabilities','Tamper Status','Version') 
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13]))
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Dahua IoT - Registered Sensors (Account- {file_name[:-3]})'
                tsv(report_folder, data_headers, data_list, tsvname)
                
            else:
                logfunc(f'No Dahua IoT - Registered Sensors (Account- {file_name[:-3]}) data available')

            #-Dahua IoT - Registered Cloud Devices (-x- DMSS account)
            cursor.execute('''
                select
                    devicename,
                    deviceModel,
                    channelcount,
                    isOnline,
                    CASE
                        when shareEnable='0' then 'Off'
                        when shareEnable='1' then 'On'
                    end shareEnable,
                    receiveShare,
                    sendShare,
                    username,
                    ability,
                    deviceCaps,
                    port,
                    rtspPort,
                    appVersion
                from CloudDevices
                ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport(f'Dahua IoT - Registered Cloud Devices (Account- {file_name[:-3]})')
                report.start_artifact_report(report_folder, f'Dahua IoT - Registered Cloud Devices (Account- {file_name[:-3]})')
                report.add_script()
                data_headers = ('Device Name','Device Model','Channels','Online','Shared Enabled','Receive Share From','Send Share To','Username','Abilities','Capabilities','Port','RTSP Port','App Version') 
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12]))
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Dahua IoT - Registered Cloud Devices (Account- {file_name[:-3]})'
                tsv(report_folder, data_headers, data_list, tsvname)
                
            else:
                logfunc(f'No Dahua IoT - Registered Cloud Devices (Account- {file_name[:-3]}) data available')

            #-Dahua IoT - Notifications (-x- DMSS account)
            cursor.execute('''
                select
                    datetime(alarmTime/1000,'unixepoch'),
                    alarmTimeStr,
                    areaName,
                    nickName,
                    sensorName,
                    alarmDeviceId,--Hub
                    alarmMessageId,--Message ID
                    case
                        when alarmTypeStr = 'gwMsg_ATSFault_Start' then 'ATS fault. Check network connection'
                        when alarmTypeStr = 'gwMsg_ATSFault_Stop' then 'ATS restored'
                        when alarmTypeStr = 'gwMsg_AreaAlarm_AddArea' then '"area name", added by "nickname"'
                        when alarmTypeStr = 'gwMsg_AreaAlarm_AreaDelete' then '"area name", removed by "nickname"'
                        when alarmTypeStr = 'gwMsg_AreaArmModeChange_Remote_DisArm' then '"area name", disarmed by "nickname"'
                        when alarmTypeStr = 'gwMsg_AreaArmModeChange_Remote_Arm_p1' then '"area name", Home mode activated by "nickname"'
                        when alarmTypeStr = 'gwMsg_ArmingFailure' then 'Unsuccessful arming "area name" attempt by "nickname"'
                        when alarmTypeStr = 'gwMsg_AlarmLocal_PassiveInfrared' then 'Motion detected, "device name" in "area name"'
                        when alarmTypeStr = 'gwMsg_AlarmLocal_DoorMagnetism_Start' then 'Opening detected, "device name" in "area name"'
                        when alarmTypeStr = 'gwMsg_AlarmLocal_DoorMagnetism_Stop' then 'Closing detected, "device name" in "area name"'
                        else alarmTypeStr 
                    end alarmTypeStr,
                    case
                        when checked = '1' then 'Yes'
                        when checked = '0' then 'No'
                    end checked
                from GeneralAlarmMessage
                ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport(f'Dahua IoT - Notifications (Account- {file_name[:-3]})')
                report.start_artifact_report(report_folder, f'Dahua IoT - Notifications (Account- {file_name[:-3]})')
                report.add_script()
                data_headers = ('Timestamp (UTC)','Timestamp (Local)','Area Name','Nickname','Device Name','Alarm Device ID','Alarm Message ID','Alarm Notification','Checked') 
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Dahua IoT - Notifications (Account- {file_name[:-3]})'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Dahua IoT - Notifications (Account- {file_name[:-3]})'
                timeline(report_folder, tlactivity, data_list, data_headers)
                
            else:
                logfunc(f'No Dahua IoT - Notifications (Account- {file_name[:-3]}) data available')
            db.close()

        #Dahua CCTV - User Created Media: - Collecting Files
        if file_name.endswith(".jpg") or file_name.endswith(".mp4") or file_name.endswith(".dav"):
            if ".thumb" not in file_found: 
                if file_name.endswith(".jpg") and "video" in file_found: #we intentionally left out thumbnails of snapshots and video files to reduce media
                    pass
                else:
                    temp_tuple = ()
                    temp_tuple = (file_found,file_name,file_name)
                    media_data_list.append(temp_tuple)
            
    #Dahua CCTV - User Created Media: - Reporting Files
    media_files =  len(media_data_list)
    if media_files > 0:
        report = ArtifactHtmlReport('Dahua CCTV - User Created Media')
        report.start_artifact_report(report_folder, 'Dahua CCTV - User Created Media')
        report.add_script()
        data_headers = ('File Path','File Name', 'File Content') 
        data_list = []
        for mfile in media_data_list:          
            if mfile[2] is not None:
                media = media_to_html(mfile[2], files_found, report_folder)
            data_list.append((mfile[0],mfile[1],media))
        media_files_dir = "*/Android/data/com.mm.android.DMSS/files/Download/snapshot/*" #Generic path of the media files.
        report.write_artifact_data_table(data_headers, data_list, media_files_dir, html_escape = False)
        report.end_artifact_report()

        tsvname = f'Dahua CCTV - User Created Media'
        tsv(report_folder, data_headers, data_list, tsvname)
            
    else:
        logfunc(f'No Dahua CCTV - User Created Media data available')
        
__artifacts__ = {
        "Dahua Technology (DMSS)": (
                "Dahua Technology (DMSS)",
                ('*/com.mm.android.DMSS/databases/*','*/Android/data/com.mm.android.DMSS/files/Download/snapshot/*'),
                get_dmss)
}