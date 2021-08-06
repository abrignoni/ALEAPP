import os
import shutil
import sqlite3
import textwrap
import scripts.artifacts.artGlobals

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_googleCallScreen(files_found, report_folder, seeker, wrap_text):
    
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
        
        if usageentries > 0:
        
            for row in all_rows:
            
                lm_ts = row[0]
                recording_path = row[1]
                conversation = row[2]
                convo_id = row[3]
                recording_filename = row[4]
                audio_clip = ''
            
                for match in files_found:
                    if recording_filename in match:
                        shutil.copy2(match, report_folder)
                        data_file_name = os.path.basename(match)
                        audio_clip = ''' 
                            <audio controls>
                                <source src={} type="audio/wav">
                                <p>Your browser does not support HTML5 audio elements.</p>
                            </audio> 
                            '''.format(recording_filename)
                            
                data_list.append((row[0],row[1],row[2],row[3],audio_clip))
        
            report = ArtifactHtmlReport('Google Call Screen')
            report.start_artifact_report(report_folder, 'Google Call Screen')
            report.add_script()
            data_headers = ('Timestamp','Recording File Path','Conversation','ID','Audio') # Don't remove the comma, that is required to make this a tuple as there is only 1 element

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Google Call Screen'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Google Call Screen'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Google Call Screen data available')
    
    db.close()
    return
