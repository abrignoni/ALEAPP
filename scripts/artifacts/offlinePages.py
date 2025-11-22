from datetime import *
import email
import os
import pytz

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import timeline, logfunc, tsv, is_platform_windows, media_to_html

def convert_utc_int_to_timezone(utc_time, time_offset): 
    #fetch the timezone information
    timezone = pytz.timezone(time_offset)
    
    #convert utc to timezone
    timezone_time = utc_time.astimezone(timezone)
    
    #return the converted value
    return timezone_time

def get_offlinePages(files_found, report_folder, seeker, wrap_text):
    
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        modified_time = os.path.getmtime(file_found)
        utc_modified_date = datetime.fromtimestamp(modified_time, tz=timezone.utc)
        
        timestamp = convert_utc_int_to_timezone(utc_modified_date, 'UTC')
        

        with open(file_found,'r', errors='replace') as fp:
            message = email.message_from_file(fp)
            sourced = (message['Snapshot-Content-Location'])
            subjectd = (message['Subject'])
            dated = (message['Date'])
            media = media_to_html(file_found, files_found, report_folder)

        data_list.append((timestamp, media, sourced, subjectd, dated, file_found))
        
    if len(data_list) > 0:
        note = 'Source location in extraction found in the report for each item.'
        report = ArtifactHtmlReport('Offline Pages')
        report.start_artifact_report(report_folder, f'Offline Pages')
        report.add_script()
        data_headers = ('Timestamp', 'File', 'Web Source', 'Subject', 'MIME Date', 'Source in Extraction')
        report.write_artifact_data_table(data_headers, data_list, note, html_no_escape=['File'])
        report.end_artifact_report()
        
        tsvname = f'Offline Pages'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Offline Pages'
        timeline(report_folder, tlactivity, data_list, data_headers)

__artifacts__ = {
        "pages": (
                "Offline Pages",
                ('*/*.mhtml', '*/*.mht'),
                get_offlinePages)
}
            