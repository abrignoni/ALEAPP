# Module Description: Parses Tusky timeline, notifications and searches
# Author: @KevinPagano3 (Twitter) / stark4n6@infosec.exchange (Mastodon)
# Date: 2022-12-12
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

def get_tusky(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_name = str(file_found)
        
        if not os.path.basename(file_name) == 'tuskyDB': # skip -journal and other files
            continue
          
        db = open_sqlite_db_readonly(file_name)
        
        #Get Tusky user timeline details
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(TimelineStatusEntity.createdAt/1000,'unixepoch'),
        TimelineAccountEntity.username,
        TimelineAccountEntity.displayName,
        TimelineStatusEntity.url,
        TimelineStatusEntity.content,
        TimelineStatusEntity.attachments,
        TimelineStatusEntity.reblogsCount,
        TimelineStatusEntity.favouritesCount,
        TimelineStatusEntity.repliesCount,
        case TimelineStatusEntity.reblogged
            when 0 then ""
            when 1 then "True"
        end,
        case TimelineStatusEntity.bookmarked
            when 0 then ""
            when 1 then "True"
        end,
        case TimelineStatusEntity.favourited
            when 0 then ""
            when 1 then "True"
        end,
        case TimelineStatusEntity.sensitive
            when 0 then ""
            when 1 then "True"
        end,
        case TimelineStatusEntity.visibility
            when 0 then "Unknown"
            when 1 then "Public"
            when 4 then "Direct"
        end as "Visibility",
        json_extract(TimelineStatusEntity.application, '$.name') as "Application"
        from TimelineStatusEntity
        left join TimelineAccountEntity on TimelineAccountEntity.serverId = TimelineStatusEntity.authorServerId
        where TimelineStatusEntity.createdAt > 0
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            description = 'Timeline details for the current users feed in Tusky'
            report = ArtifactHtmlReport('Tusky - Timeline')
            report.start_artifact_report(report_folder, 'Tusky - Timeline')
            report.add_script()
            data_headers = ('Timestamp','User Name','Display Name','URL','Text Content','Attachments','Boost Count','Favorite Count','Replies Count','User Boosted?','User Bookmarked?','User Favorited?','Sensitive','Visibility','Application')
            data_list = []
            data_list_stripped = []
            for row in all_rows:
                data = json.loads(row[5])
                attachment_list = []
                attachments = ''
                #Iterate attachments
                for x in data:
                    attachment_item = x.get('url','')
                    attachment_list.append(attachment_item)
                    if len(attachment_list) > 0:
                        attachments = '\n'.join(map(str,attachment_list))
                    else:
                        attachments = ''
                data_list.append((row[0],row[1],row[2],row[3],row[4],attachments,row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14]))
            
                soup = ''
                if str(row[4]).startswith('<p>'):
                    soup = BeautifulSoup(row[3], 'html.parser').text
                    
                data_list_stripped.append((row[0],row[1],row[2],row[3],soup,attachment_list,row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14]))                        

            report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Text Content'])
            report.end_artifact_report()
            
            tsvname = f'Tusky - Timeline'
            tsv(report_folder, data_headers, data_list_stripped, tsvname)
            
            tlactivity = f'Tusky - Timeline'
            timeline(report_folder, tlactivity, data_list_stripped, data_headers)
            
        else:
            logfunc('Tusky - Timeline data available') 

        cursor = db.cursor()
        cursor.execute('''
        select
        accountId,
        displayName,
        username,
        domain,
        profilePictureUrl,
        case notificationsEnabled
            when 0 then "False"
            when 1 then "True"
        end,
        case notificationsMentioned
            when 0 then "False"
            when 1 then "True"
        end,
        case notificationsFollowed
            when 0 then "False"
            when 1 then "True"
        end,
        case notificationsFollowRequested
            when 0 then "False"
            when 1 then "True"
        end,
        case notificationsReblogged
            when 0 then "False"
            when 1 then "True"
        end,
        case notificationsFavorited
            when 0 then "False"
            when 1 then "True"
        end,
        case notificationsPolls
            when 0 then "False"
            when 1 then "True"
        end,
        tabPreferences,
        accessToken,
        clientId,
        clientSecret
        from AccountEntity
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            description = 'Account details for the current user in Tusky'
            report = ArtifactHtmlReport('Tusky - Account Details')
            report.start_artifact_report(report_folder, 'Tusky - Account Details')
            report.add_script()
            data_headers = ('Account ID','Display Name','User Name','Instance','Avatar URL','Notifications Enabled','Mentioned Notifications','Followed Notifications','Follow Requested Notifications','Boost Notifications','Favorited Notifications','Polls Notifications','Tab Preferences','Access Token','Client ID','Client Secret')
            data_list = []
            for row in all_rows:
                    
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Tusky - Account Details'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Tusky - Account Details'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('Tusky - Account Details data available')
        
        db.close()

__artifacts__ = {
        "Tusky": (
                "Tusky",
                ('*/com.keylesspalace.tusky/databases/tuskyDB*'),
                get_tusky)
}
