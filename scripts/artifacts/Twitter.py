# Twitter Searches
# Author:  Kevin Pagano (https://startme.stark4n6.com)
# Date 2023-04-26
# Version: 0.1
# Requirements:  None

import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, kmlgen

def get_Twitter(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)  
        if file_found.endswith('-search.db'):
            break
        else:
            continue # Skip all other files
            
    db = open_sqlite_db_readonly(file_found)
    
    cursor = db.cursor()
    cursor.execute('''
    select
    datetime(time/1000,'unixepoch'),
    name,
    query,
    query_id,
    user_search_suggestion,
    topic_search_suggestion,
    latitude,
    longitude,
    radius,
    location,
    priority,
    score
    from search_queries
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Twitter - Searches')
        report.start_artifact_report(report_folder, 'Twitter - Searches')
        report.add_script()
        data_headers = ('Timestamp','Name','Query','Query ID','User Search Suggestion','Topic Search Suggestion','Latitude','Longitude','Radius','Location','Priority','Score')
        
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]))
            
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Twitter - Searches'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Twitter - Searches'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Twitter - Searches data available')
        
    db.close()

__artifacts__ = {
        "twitter": (
                "Twitter",
                ('*/com.twitter.android/databases/*-search.db*'),
                get_Twitter)
}
    