# Module Description: Parses Gmail
# Author: @KevinPagano3 (Twitter) / stark4n6@infosec.exchange (Mastodon)
# Date: 2023-01-03
# Artifact version: 0.0.1
# Requirements: BeautifulSoup

import datetime
import json
import os
import sqlite3
import textwrap
from bs4 import BeautifulSoup

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_gmail_mail(files_found, report_folder, seeker, wrap_text):
    
    bigTopDataDB = ''
    
    for file_found in files_found:
        file_found = str(file_found)
        file_name = os.path.basename(file_found)
         
        if file_name.startswith('bigTopDataDB'):
        
            if file_name.endswith('-shm') or file_name.endswith('-wal'):
                continue
            
            else:
                bigTopDataDB = file_found
                source_bigTop = file_found.replace(seeker.directory, '')
                
    db = open_sqlite_db_readonly(bigTopDataDB)
    cursor = db.cursor()

    #Get Gmail label details
    cursor.execute('''
    select
    label_server_perm_id,
    unread_count,
    total_count,
    unseen_count
    from label_counts
    order by label_server_perm_id
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        description = 'Gmail mail labels'
        report = ArtifactHtmlReport('Gmail - Label Details')
        report.start_artifact_report(report_folder, 'Gmail - Label Details')
        report.add_script()
        data_headers = ('Label','Unread Count','Total Count','Unseen Count')
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3]))

        report.write_artifact_data_table(data_headers, data_list, source_bigTop)
        report.end_artifact_report()
        
        tsvname = f'Gmail - Label Details'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc('Gmail - Label Details')

    db.close()
        
__artifacts__ = {
    "GmailMail": (
            "Gmail",
            ('*/com.google.android.gm/databases/bigTopDataDB.*'),
            get_gmail_mail)
}
