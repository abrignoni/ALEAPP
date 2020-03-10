import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc 

def get_calllog(files_found, report_folder):
    
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    CASE
        WHEN phone_account_address is NULL THEN ' '
        ELSE phone_account_address
        end as phone_account_address,
    number,
    datetime(date /1000, 'unixepoch') as date,
    CASE
        WHEN type = 1 THEN  'Incoming'
        WHEN type = 2 THEN  'Outgoing'
        WHEN type = 3 THEN  'Missed'
        WHEN type = 4 THEN  'Voicemail'
        WHEN type = 5 THEN  'Rejected'
        WHEN type = 6 THEN  'Blocked'
        WHEN type = 7 THEN  'Answered Externally'
        ELSE 'Unknown'
        end as types,
    duration,
    CASE
        WHEN geocoded_location is NULL THEN ' '
        ELSE geocoded_location
        end as geocoded_location,
    countryiso,
    CASE
        WHEN _data is NULL THEN ' '
        ELSE _data
        END as _data,
    CASE
        WHEN mime_type is NULL THEN ' '
        ELSE mime_type
        END as mime_type,
    CASE
        WHEN transcription is NULL THEN ' '
        ELSE transcription
        END as transcription,
    deleted
    FROM
    calls
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Call logs')
        report.start_artifact_report(report_folder, 'Call logs')
        report.add_script()
        data_headers = ('Phone Account Address', 'Partner', 'Call Date','Type','Duration in Secs','Partner Location','Country ISO','Data','Mime Type','Transcription','Deleted')
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], str(row[4]), row[5], row[6], row[7], row[8], row[9], str(row[10])))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
    else:
        logfunc('No Call Log data available')
    
    db.close()
    return