import os
import sqlite3
import textwrap

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, is_platform_windows, open_sqlite_db_readonly

def get_mastodon(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('.db'):
            continue
           
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        
        cursor.execute('''
        select
        datetime(time,'unixepoch'),
        json_extract(recent_searches.json, '$.hashtag.name') as "Hashtag Name",
        json_extract(recent_searches.json, '$.hashtag.url') as "Hashtag URL"
        from recent_searches
        where id like 'tag%'
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Mastodon - Hashtag Searches')
            report.start_artifact_report(report_folder, 'Mastodon - Hashtag Searches')
            report.add_script()
            data_headers = ('Timestamp','Hashtag Name','Hashtag URL')
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Mastodon - Hashtag Searches'
            tsv(report_folder, data_headers, data_list, tsvname)
            
        else:
            logfunc('Mastodon - Hashtag Searches')

        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(time,'unixepoch'),
        json_extract(recent_searches.json, '$.account.username') as "Username",
        json_extract(recent_searches.json, '$.account.display_name') as "Display Name",
        json_extract(recent_searches.json, '$.account.url') as "URL",
        json_extract(recent_searches.json, '$.account.id') as "ID"
        from recent_searches
        where id like 'acc%'
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Mastodon - Account Searches')
            report.start_artifact_report(report_folder, 'Mastodon - Account Searches')
            report.add_script()
            data_headers = ('Timestamp','Username','Display Name','URL','ID')
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Mastodon - Account Searches'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Mastodon - Account Searches'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('Mastodon - Account Searches')

        cursor = db.cursor()
        cursor.execute('''
        select 
        json_extract(notifications_all.json, '$.status.created_at') as "Timestamp",
        json_extract(notifications_all.json, '$.account.acct') as "Notification From",
        case type
            when 2 then "Reply"
            when 4 then "Favorite"
        end,
        json_extract(notifications_all.json, '$.status.url') as "Reference URL",
        json_extract(notifications_all.json, '$.status.visibility') as "Visibility",
        json_extract(notifications_all.json, '$.status.content') as "Content",
        id
        from notifications_all
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Mastodon - Notifications')
            report.start_artifact_report(report_folder, 'Mastodon - Notifications')
            report.add_script()
            data_headers = ('Timestamp','Notification From','Notification Type','Reference URL','Visibility','Content','ID')
            data_list = []
            for row in all_rows:
            
                notification_timestamp = row[0].replace('T', ' ').replace('Z', '')
            
                data_list.append((notification_timestamp,row[1],row[2],row[3],row[4],row[5],row[6]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Mastodon - Notifications'
            tsv(report_folder, data_headers, data_list, tsvname)
            
        else:
            logfunc('Mastodon - Notifications data available')

        db.close()

__artifacts__ = {
        "mastodon": (
                "Mastodon",
                ('*/org.joinmastodon.android/databases/*.db*'),
                get_mastodon)
}
