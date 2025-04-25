import blackboxprotobuf
import os
import shutil
import sqlite3
import textwrap
import scripts.artifacts.artGlobals
from datetime import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_googleCallScreen(files_found, report_folder, seeker, wrap_text):
    
    is_windows = is_platform_windows()
    slash = '\\' if is_windows else '/'
    
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('callscreen_transcripts'):
            continue # Skip all other files
    
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(lastModifiedMillis/1000,'unixepoch'),
        audioRecordingFilePath,
        conversation,
        id,
        replace(audioRecordingFilePath, rtrim(audioRecordingFilePath, replace(audioRecordingFilePath, '/', '')), '') as 'File Name'
        from Transcript
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        data_list = []
        
        pb_types = {'1': {'type': 'message', 'message_typedef':
                    {   
                        '1': {'name': 'timestamp1', 'type': 'int'},
                        '2': {'name': '', 'type': 'int'},
                        '3': {'name': 'convo_text', 'type': 'str'},
                        '4': {'name': '', 'type': 'int'},
                        '5': {'name': '', 'type': 'int'},
                        '6': {'name': '', 'type': 'bytes'},
                        '7': {'name': '', 'type': 'int'},
                        '9': {'name': '', 'type': 'int'}},
                    'name': '',
                    'type': 'message'}}
        
        if report_folder[-1] == slash: 
            folder_name = os.path.basename(report_folder[:-1])
        else:
            folder_name = os.path.basename(report_folder)
        
        if usageentries > 0:
            for row in all_rows:
            
                lm_ts = row[0]
                recording_path = row[1]
                pb = row[2]
                convo_id = row[3]
                recording_filename = row[4]
                audio_clip = ''
                conversation = ''
                
                data, actual_types = blackboxprotobuf.decode_message(pb, pb_types)
                
                for x in data['1']:
    
                    convo_timestamp = str(datetime.utcfromtimestamp(x['timestamp1']/1000)) + '<br>'
                    convo_transcript = x['convo_text'] + '<br><br>'
                    conversation += convo_timestamp + convo_transcript
                    
                for match in files_found:
                    if str(recording_filename) in match:
                        shutil.copy2(match, report_folder)
                        audio_clip = f'<audio controls><source src="{folder_name}/{recording_filename}"></audio>'
                                
                data_list.append((lm_ts,recording_path,conversation,audio_clip))
        
            description = 'Transcripts and recordings from the use of Google Assistant\'s Call Screen feature. '\
                          'Timestamps found in the Conversation column are in the local timezone offset.'
            report = ArtifactHtmlReport('Google Call Screen')
            report.start_artifact_report(report_folder, 'Google Call Screen', description)
            report.add_script()
            data_headers = ('Timestamp','Recording File Path','Conversation','Audio') # Don't remove the comma, that is required to make this a tuple as there is only 1 element

            report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Audio','Conversation'])
            report.end_artifact_report()
            
            tsvname = f'Google Call Screen'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Google Call Screen'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Google Call Screen data available')
    
        db.close()

__artifacts__ = {
        "GoogleCallScreen": (
                "Google Call Screen",
                ('*/com.google.android.dialer/databases/callscreen_transcripts*','*/com.google.android.dialer/files/callscreenrecordings/*.*'),
                get_googleCallScreen)
}
