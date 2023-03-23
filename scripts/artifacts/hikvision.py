""""
Developed by Evangelos D. (@theAtropos4n6)

Research for this artifact was conducted by Evangelos Dragonas, Costas Lambrinoudakis and Michael Kotsis. 
For more information read their research paper here: Link_to_be_uploaded

Updated:23-03-2023

Hikvision is a well-known app that is used to remotely access/operate CCTV systems. Currently the following information can be interpreted:

-Hikvision - CCTV Channels: retrieves info for the available CCTV record channels 
-Hikvision - CCTV Info: Information about the CCTV system
-Hikvision - CCTV Activity: User Interaction with the app. Unfortunately it is not easy to attribute user actions but indirectly can indicate remote live view/play back from CCTV footage.
-Hikvision - User Created Media: The media files the user created while viewing footage from the CCTV

"""
import sqlite3
import os
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly,media_to_html

def get_hikvision(files_found, report_folder, seeker, wrap_text):
    separator = '/'
    for file_found in files_found:
        file_found = str(file_found)
        file_name = os.path.basename(file_found)
        if file_name == 'database.hik':
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            
            #CCTV Available Channels
            cursor.execute('''
                select 
                nDeviceID,
                nChannelNo,
                chChannelName,
                case  nEnable
                    when '0' then 'Disabled'
                    when '1' then 'Enabled'
                end
                from channelinfo  
                ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Hikvision - CCTV Channels')
                report.start_artifact_report(report_folder, 'Hikvision - CCTV Channels')
                report.add_script()
                data_headers = ('Device ID','Channel No.','Channel Name','Status') 
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Hikvision - CCTV Channels'
                tsv(report_folder, data_headers, data_list, tsvname)
            
            else:
                logfunc(f'No Hikvision - CCTV Channels data available')

            #CCTV Info
            cursor.execute('''
                select 
                nDeviceID,
                chDeviceName,
                chDeviceSerialNo,
                nDevicePort,
                nChannelNum,
                nStartChan,
                nIPChannelNum,
                nStartIPChan,
                chDDNSAddress,
                nDDNSPort

                from deviceinfo
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Hikvision - CCTV Info')
                report.start_artifact_report(report_folder, 'Hikvision - CCTV Info')
                report.add_script()
                data_headers = ('ID','Name/IP','Serial Number','Port','Channels','1st Channel',' IP Channels','1st IP Channel','DDNS Address','DDNS Port') 
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Hikvision - CCTV Info'
                tsv(report_folder, data_headers, data_list, tsvname)
                
            else:
                logfunc(f'No Hikvision - CCTV Info data available')
            db.close()

        if file_name == 'ezvizlog.db':
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            
            #CCTV Activity
            cursor.execute('''
                SELECT
                datetime(time/1000,'unixepoch'),
                datetime(time/1000,'unixepoch','localtime'),
                systemName as 'Record Type',
                content
                FROM event 
                ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Hikvision - CCTV Activity')
                report.start_artifact_report(report_folder, 'Hikvision - CCTV Activity')
                report.add_script()
                data_headers = ('Timestamp (UTC)','Timestamp (Local)','Record Type','Activity') 
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Hikvision - CCTV Activity'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Hikvision - CCTV Activity'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc(f'No Hikvision - CCTV Activity data available')
            
            db.close()

        if file_name == 'image.db':
                    db = open_sqlite_db_readonly(file_found)
                    cursor = db.cursor()
                    
                    #CCTV - User Created Media
                    cursor.execute('''
                        select
                        datetime(createdTime/1000,'unixepoch'),
                        cameraID,
                        deviceID,
                        case type
                            when '0' then 'Image'
                            when '1' then 'Video'
                        end as 'Media Type',
                        filePath,
                        thumbPath,
                        user,
                        folderName,
                        videoStartTime,
                        videoStopTime

                        from images 
                        ''')

                    all_rows = cursor.fetchall()
                    usageentries = len(all_rows)
                    if usageentries > 0:
                        report = ArtifactHtmlReport('Hikvision - User Created Media')
                        report.start_artifact_report(report_folder, 'Hikvision - User Created Media')
                        report.add_script()
                        data_headers = ('Creation Timestamp (UTC)','Camera ID','Device ID','Type','File Path','Thumbnail Path','User','Folder Name','Video Start Time','Video End Time') 
                        data_list = []
                        for row in all_rows:
                            if row[4] is not None:
                                mediaident = row[4].split(separator)[-1]
                                media = media_to_html(mediaident, files_found, report_folder)
                            else:
                                media = row[4]
                            if row[5] is not None:
                                thumbident = row[5].split(separator)[-1]
                                thumb = media_to_html(thumbident, files_found, report_folder)
                            else:
                                thumb = row[5]
                            data_list.append((row[0],row[1],row[2],row[3],media,thumb,row[6],row[7],row[8],row[9]))

                        report.write_artifact_data_table(data_headers, data_list, file_found,html_escape = False)
                        report.end_artifact_report()
                        
                        tsvname = f'Hikvision - User Created Media'
                        tsv(report_folder, data_headers, data_list, tsvname)
                        
                        tlactivity = f'Hikvision - User Created Media'
                        timeline(report_folder, tlactivity, data_list, data_headers)
                    else:
                        logfunc(f'No Hikvision - User Created Media data available')

                    db.close()

__artifacts__ = {
        "hikvision": (
                "Hikvision",
                ('*/com.connect.enduser/databases/database.hik*','*/com.connect.enduser/databases/ezvizlog.db',
                 '*/com.connect.enduser/databases/image.db*','*/0/Pictures/Hik-Connect Album/*'),
                get_hikvision)
}