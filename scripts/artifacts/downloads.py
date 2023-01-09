# Module Description: Parses native downloads database
# Author: @KevinPagano3 (Twitter) / stark4n6@infosec.exchange (Mastodon)
# Date: 2023-01-09
# Artifact version: 0.0.1

import sqlite3
import os
from datetime import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, timeline, tsv, is_platform_windows, open_sqlite_db_readonly

def get_downloads(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'downloads.db': # skip -journal and other files
            continue           
        
    db = open_sqlite_db_readonly(file_found)
    
    #Get file downloads
    cursor = db.cursor()
    cursor.execute('''
    select
    datetime(lastmod/1000,'unixepoch') as "Modified/Downloaded Timestamp",
    title,
    description,
    uri,
    _data,
    mimetype,
    notificationpackage,
    current_bytes,
    total_bytes,
    status,
    errorMsg,
    etag,
    case is_visible_in_downloads_ui
        when 0 then 'No'
        when 1 then 'Yes'
    end,
    case deleted
        when 0 then ''
        when 1 then 'Yes'
    end
    from downloads
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
                            
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13]))

        description = 'Native downloads'
        report = ArtifactHtmlReport('Native Downloads')
        report.start_artifact_report(report_folder, 'Native Downloads', description)
        report.add_script()
        data_headers = ('Modified/Downloaded Timestamp','Title','Description','Provider URI','Save Location','Mime Type','App Provider Package','Current Bytes','Total Bytes','Status','Error Message','ETAG','Visible in Downloads UI','Deleted')
        report.write_artifact_data_table(data_headers, data_list, file_found,html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'Native Downloads'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Native Downloads'
        timeline(report_folder, tlactivity, data_list, data_headers)
    
    else:
        logfunc('No Native Downloads data available')
    
__artifacts__ = {
        "Downloads": (
                "Downloads",
                ('*/data/com.android.providers.downloads/databases/downloads.db*'),
                get_downloads)
}