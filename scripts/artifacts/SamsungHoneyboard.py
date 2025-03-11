__artifacts_v2__ = {
    "Samsung Honeyboard Clipboard Historty": {
        "name": "Samsung Honeyboard - Clipboard History",
        "description": "Parses the text clipboard History.",
        "author": "@segumarc",
        "version": "0.0.1",
        "date": "2024-05-30",
        "requirements": "",
        "category": "Clipboard",
        "notes": ".",
        "paths": ('*/com.samsung.android.honeyboard/databases/ClipItem*'),
        "function": "get_Honeyboard_Clipboard"
    },
    "Samsung Honeyboard Clipboard Screenshot": {
        "name": "Samsung Honeyboard - Clipboard Screenshot",
        "description": "Parses the Samsung honeyboard clipboard Screenshot.",
        "author": "@segumarc",
        "version": "0.0.1",
        "date": "2024-05-30",
        "requirements": "",
        "category": "Clipboard",
        "notes": ".",
        "paths": ('*/com.samsung.android.honeyboard/clipboard/*/clip'),
        "function": "get_honeyboard_screenshot"
    }
}
import os
from datetime import *
from PIL import Image

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, media_to_html, convert_utc_human_to_timezone


def get_Honeyboard_Clipboard(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Samsung Honeyboard - Clipboard History")
 
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    data_list = []
    for file_found in files_found:
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
            SELECT time_stamp, id, type, text, caller_app_uid
            FROM clip_table
        ''')
        data_rows = cursor.fetchall()
        for row in data_rows:
                timestamp = row[0]
                id = row[1]
                type = row[2]
                text = row[3]
                caller_app_uid = row[4]
                timestamp = datetime.fromtimestamp(timestamp/1000, tz=timezone.utc)
                timestamp = convert_utc_human_to_timezone(timestamp, 'UTC')
                data_list.append((timestamp,id,type,text,caller_app_uid))
        
        if len(data_list):
            logfunc(f"Found {len(data_rows)} Samsung Honeyboard - Clipboard History")

            description = f"Samsung Honeyboard - Clipboard History"
            report = ArtifactHtmlReport('Samsung Honeyboard - Clipboard History')
            report.start_artifact_report(report_folder, 'Samsung Honeyboard - Clipboard History', description)
            report.add_script()
            data_headers = ('Timestamp', 'ID', 'Type', 'Clipboard Content', 'Application UID')                         
            tableID = 'SamsungHoneyboard_ClipboardHistory'

            report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
            report.end_artifact_report()

            tsvname = f'Samsung Honeyboard - Clipboard Historys'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = f'Samsung Honeyboard - Clipboard History'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No entries found for Samsung Honeyboard - Clipboard History.')

        db.close()

def get_honeyboard_screenshot(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Samsung Honeyboard - Clipboard Screenshot")
    data_list = []

    for file_found in files_found:
        file_found = str(file_found)
        
        modifiedtime = os.path.getmtime(file_found)
        modifiedtime = (datetime.utcfromtimestamp(int(modifiedtime)).strftime('%Y-%m-%d %H:%M:%S'))
        
        filename = os.path.basename(file_found)
        dirname = os.path.basename(os.path.dirname(file_found))
        
        if dirname == "remote_send":
            continue

        newfilename = dirname + '_' + filename + '.png'
        savepath = os.path.join(report_folder, newfilename)

        img = Image.open(file_found) 
        img.save(savepath,'png')
        medialist = (savepath,)
        thumb = media_to_html(savepath, medialist, report_folder)
        
        data_list.append((modifiedtime, thumb, file_found))
        path_to_files = os.path.dirname(os.path.dirname(file_found))


    if data_list:
        description = 'Samsung Honeyboard - Clipboard Screenshots'
        report = ArtifactHtmlReport('Samsung Honeyboard - Clipboard Screenshots')
        report.start_artifact_report(report_folder, 'Samsung Honeyboard - Clipboard Screenshots', description)
        report.add_script()
        data_headers = ('File Modified Time','Thumbnail','Screenshot Path' )
        report.write_artifact_data_table(data_headers, data_list, path_to_files, html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'Samsung Honeyboard - Clipboard Screenshots'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Samsung Honeyboard - Clipboard Screenshots'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Samsung Honeyboard - Clipboard Screenshots data available')
        
