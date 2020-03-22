import sqlite3
import textwrap
import json
from scripts.parse3 import ParseProto

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows

def get_googleNowPlaying(files_found, report_folder, seeker):
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    Select
    CASE
        timestamp 
        WHEN
            "0" 
        THEN
            "0" 
        ELSE
            datetime(timestamp / 1000, "unixepoch")
    END AS "timestamp",
    history_entry
    FROM
    recognition_history
    ''')
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Now Playing')
        report.start_artifact_report(report_folder, 'Now Playing')
        report.add_script()
        data_headers = ('Timestamp','Timezone','Song Title','Artist','Duration','Full Data' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []

        for row in all_rows: 
            binfile = open(report_folder + "binfile.bin", "wb")
            binfile.write(row[1])
            binfile.close()
        
            data = ParseProto(report_folder + "binfile.bin")
            #print(data)
            try:
                timezones = (data["07:00:string"])
            except:
                timezones = ''

            try:
                songtitle = (data["09:01:embedded message"]["03:02:string"])
            except:
                songtitle = ''

            try:
                artist = (data["09:01:embedded message"]["04:03:string"]) 
            except:
                artist = ''
            try:
                durationinsecs = (data["09:01:embedded message"]["06:04:64-bit"]) 
            except:
                durationinsecs = ''
            
            
            data_list.append((row[0],timezones,songtitle,artist,durationinsecs,str(data)))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
    else:
        print('No Music history')

    db.close()
    return

