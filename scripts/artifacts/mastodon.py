# Module Description: Parses Mastodon timeline, notifications and searches
# Author: @KevinPagano3 (Twitter) / stark4n6@infosec.exchange (Mastodon)
# Date: 2022-12-07
# Artifact version: 0.0.3
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

def get_mastodon(files_found, report_folder, seeker, wrap_text):
    
    account_db = ''
    account_json = ''
    source_file_account_db = ''
    source_file_account_json = ''
    
    for file_found in files_found:
        file_name = str(file_found)
        
        if file_name.lower().endswith('.db'):
           accout_db = str(file_found)
           source_file_account_db = file_found.replace(seeker.data_folder, '')

        if file_name.lower().endswith('accounts.json'):
           account_json = str(file_found)
           source_file_account_json = file_found.replace(seeker.data_folder, '')
           
        if file_name.lower().endswith('.json') and file_name.lower().startswith('instance'):
           instance_json = str(file_found)
           source_file_instance_json = file_found.replace(seeker.data_folder, '')
           
    db = open_sqlite_db_readonly(accout_db)
    cursor = db.cursor()
    
    #Get Mastodon user search details for hashtags
    cursor.execute('''
    select
    datetime(time,'unixepoch') as "Search Timestamp",
    json_extract(recent_searches.json, '$.hashtag.name') as "Hashtag Name",
    json_extract(recent_searches.json, '$.hashtag.url') as "Hashtag URL"
    from recent_searches
    where id like 'tag%'
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        description = 'Hashtag searches from the current user in Mastodon'
        report = ArtifactHtmlReport('Mastodon - Hashtag Searches')
        report.start_artifact_report(report_folder, 'Mastodon - Hashtag Searches')
        report.add_script()
        data_headers = ('Timestamp','Hashtag Name','Hashtag URL')
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2]))

        report.write_artifact_data_table(data_headers, data_list, source_file_account_db)
        report.end_artifact_report()
        
        tsvname = f'Mastodon - Hashtag Searches'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Mastodon - Hashtag Searches'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('Mastodon - Hashtag Searches')

    #Get Mastodon user search details for accounts
    cursor = db.cursor()
    cursor.execute('''
    select
    datetime(time,'unixepoch') as "Search Timestamp",
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
        description = 'Account searches from the current user in Mastodon'
        report = ArtifactHtmlReport('Mastodon - Account Searches')
        report.start_artifact_report(report_folder, 'Mastodon - Account Searches')
        report.add_script()
        data_headers = ('Timestamp','Username','Display Name','URL','ID')
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4]))

        report.write_artifact_data_table(data_headers, data_list, source_file_account_db)
        report.end_artifact_report()
        
        tsvname = f'Mastodon - Account Searches'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Mastodon - Account Searches'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('Mastodon - Account Searches')

    #Get Mastodon user notification details
    cursor = db.cursor()
    cursor.execute('''
    select 
    json_extract(notifications_all.json, '$.created_at') as "Notification Created Timestamp",
    json_extract(notifications_all.json, '$.account.acct') as "Notification From",
    case type
        when 0 then "Follow"
        when 2 then "Mention"
        when 3 then "Boost"
        when 4 then "Favorite"
    end as "Notification Type",
    json_extract(notifications_all.json, '$.status.url') as "Reference URL",
    json_extract(notifications_all.json, '$.status.content') as "Text Content",
    json_extract(notifications_all.json, '$.status.visibility') as "Visibility",
    json_extract(notifications_all.json, '$.status.created_at') as "Status Created Timestamp",
    id
    from notifications_all
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        description = 'Notification details for the current user in Mastodon'
        report = ArtifactHtmlReport('Mastodon - Notifications')
        report.start_artifact_report(report_folder, 'Mastodon - Notifications')
        report.add_script()
        data_headers = ('Notification Created Timestamp','Notification From','Notification Type','Reference URL','Text Content','Visibility','Status Created Timestamp','ID')
        data_list = []
        data_list_stripped = []
        for row in all_rows:
            
            notification_timestamp = ''
            status_timestamp = ''
        
            notification_timestamp = row[0].replace('T', ' ').replace('Z', '')
            if row[6] != None:
                status_timestamp = row[6].replace('T', ' ').replace('Z', '')
            else:
                status_timestamp = ''
                
            data_list.append((notification_timestamp,row[1],row[2],row[3],row[4],row[5],status_timestamp,row[7]))
            
            if row[4] != None:
                soup = BeautifulSoup(row[4], 'html.parser').text
                data_list_stripped.append((notification_timestamp,row[1],row[2],row[3],soup,row[5],status_timestamp,row[7]))
            else:
                data_list_stripped.append((notification_timestamp,row[1],row[2],row[3],row[4],row[5],status_timestamp,row[7]))
                
        report.write_artifact_data_table(data_headers, data_list, source_file_account_db, html_no_escape=['Text Content'])
        report.end_artifact_report()
        
        tsvname = f'Mastodon - Notifications'
        tsv(report_folder, data_headers, data_list_stripped, tsvname)
        
        tlactivity = f'Mastodon - Notifications'
        timeline(report_folder, tlactivity, data_list_stripped, data_headers)
        
    else:
        logfunc('Mastodon - Notifications data available')
    
    #Get Mastodon user timeline details
    cursor = db.cursor()
    cursor.execute('''
    select
    json_extract(home_timeline.json, '$.created_at') as "Created Timestamp",
    json_extract(home_timeline.json, '$.account.acct') as "Account Name",
    json_extract(home_timeline.json, '$.application.name') as "App Name",
    json_extract(home_timeline.json, '$.content') as "Content",
    json_extract(home_timeline.json, '$.url') as "URL",
    json_extract(home_timeline.json, '$.reblog.account.acct') as "Boosted Account Name",
    json_extract(home_timeline.json, '$.reblog.content') as "Boosted Content",
    json_extract(home_timeline.json, '$.reblog.url') as "Boosted URL",
    json_extract(home_timeline.json, '$.replies_count') as "Replies Count",
    json_extract(home_timeline.json, '$.reblogs_count') as "Boosted Count",
    json_extract(home_timeline.json, '$.favourites_count') as "Favorites Count",
    json_extract(home_timeline.json, '$.visibility') as "Visibility",
    id,
    json
    from home_timeline
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        description = 'Timeline details for the current users feed in Mastodon'
        report = ArtifactHtmlReport('Mastodon - Timeline')
        report.start_artifact_report(report_folder, 'Mastodon - Timeline')
        report.add_script()
        data_headers = ('Timestamp','Account Name','App Name','Text Content','Attachment URL','URL','Boosted Account Name','Boosted Content','Boosted URL','Replies Count','Boosted Count','Favorites Count','Visibility','ID')
        data_list = []
        data_list_stripped = []
        for row in all_rows:
            data = json.loads(row[13])
            attachment_list = []
            attachments = ''
            for x in data['media_attachments']:
                attachment_item = x.get('url','')
                attachment_list.append(attachment_item)
                if len(attachment_list) > 0:
                    attachments = '\n'.join(map(str,attachment_list))
                else:
                    attachments = ''
        
            notification_timestamp = row[0].replace('T', ' ').replace('Z', '')
        
            data_list.append((notification_timestamp,row[1],row[2],row[3],attachments,row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12]))
            
            if row[3] and row[6] != None:
                data_list_stripped.append((notification_timestamp,row[1],row[2],row[3],attachment_list,row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12]))
                
            else:
                soup1 = ''
                soup2 = ''
                if str(row[3]).startswith('<p>'):
                    soup1 = BeautifulSoup(row[3], 'html.parser').text
                elif str(row[6]).startswith('<p>'):
                    soup2 = BeautifulSoup(row[6], 'html.parser').text
                    
                data_list_stripped.append((notification_timestamp,row[1],row[2],soup1,attachment_list,row[4],soup2,row[6],row[7],row[8],row[9],row[10],row[11],row[12]))                      

        report.write_artifact_data_table(data_headers, data_list, source_file_account_db, html_no_escape=['Text Content','Boosted Content'])
        report.end_artifact_report()
        
        tsvname = f'Mastodon - Timeline'
        tsv(report_folder, data_headers, data_list_stripped, tsvname)
        
        tlactivity = f'Mastodon - Timeline'
        timeline(report_folder, tlactivity, data_list_stripped, data_headers)
        
    else:
        logfunc('Mastodon - Timeline data available')   
    
    db.close()
    
    #Get Mastodon account user details
    with open(account_json, encoding = 'utf-8', mode = 'r') as f:
        data = json.loads(f.read())
    data_list_json = []
    
    for x in data['accounts']:
        account_created_ts = str(x['b'].get('created_at','')).replace('T', ' ').replace('Z', '')
        account_name = x['b'].get('acct','')
        account_username = x['b'].get('username','')
        account_display_name = x['b'].get('display_name','')
        account_url = x['b'].get('url','')
        account_id = x['b'].get('id','')
        followers_count = x['b'].get('followers_count','')
        following_count = x['b'].get('following_count','')
        account_bio = x['b'].get('note','')
        if str(account_bio).startswith('<p>'):
            account_bio = BeautifulSoup(account_bio, 'html.parser').text
            
        account_avatar = x['b'].get('avatar','')
        instance_name = x.get('c','')
        
        alert_favorite = str(x['j']['alerts'].get('favourite','')).title()
        alert_follow = str(x['j']['alerts'].get('follow','')).title()
        alert_mention = str(x['j']['alerts'].get('mention','')).title()
        alert_poll = str(x['j']['alerts'].get('poll','')).title()
        alert_reblog = str(x['j']['alerts'].get('reblog','')).title()
        
        flag_bot = str(x['b'].get('bot','')).title()
        flag_discoverable = str(x['b'].get('discoverable','')).title()
        flag_locked = str(x['b'].get('locked','')).title()
        flag_suspended = str(x['b'].get('suspended','')).title()
        
        data_list_json.append((account_created_ts,account_name,account_username,account_display_name,account_url,account_id,followers_count,following_count,account_bio,account_avatar,instance_name,alert_favorite,alert_follow,alert_mention,alert_poll,alert_reblog,flag_bot,flag_discoverable,flag_locked,flag_suspended))

    num_entries = len(data_list_json)
    if num_entries > 0:
        description = 'Account details for the current Mastodon user.'
        report = ArtifactHtmlReport('Mastodon - Account Details')
        report.start_artifact_report(report_folder, 'Mastodon - Account Details', description)
        report.add_script()
        data_headers = ('Created Timestamp','Name','User Name','Display Name','URL','ID','Followers Count','Following Count','Bio','Avatar URL','Instance Name','Favorite Alerts','Follow Alerts','Mention Alerts','Poll Alerts','Boost Alerts','Is Bot','Is Discoverable','Is Locked','Is Suspended')

        report.write_artifact_data_table(data_headers, data_list_json, file_found)
        report.end_artifact_report()
        
        tsvname = f'Mastodon - Account Details'
        tsv(report_folder, data_headers, data_list_json, tsvname)
        
        tlactivity = f'Mastodon - Account Details'
        timeline(report_folder, tlactivity, data_list_json, data_headers)
    else:
        logfunc('No Mastodon - Account Details data available')
        
        
    #Get Mastodon instance details    
    with open(file_found, encoding = 'utf-8', mode = 'r') as f:
        data = json.loads(f.read())
    
    data_list_instance_json = []

    instance_updated_ts = datetime.datetime.utcfromtimestamp(int(data.get('last_updated',''))/1000).strftime('%Y-%m-%d %H:%M:%S')
    instance_uri = data['instance'].get('uri','')
    instance_title = data['instance'].get('title','')
    instance_description = data['instance'].get('description','')
    instance_version = data['instance'].get('version','')
    instance_user_count = data['instance']['stats'].get('user_count','')
    instance_status_count = data['instance']['stats'].get('status_count','')
    instance_invites = str(data['instance'].get('invites_enabled','')).title()
    instance_registrations = str(data['instance'].get('registrations','')).title()
    instance_email = data['instance'].get('email','')
    instance_contact = data['instance']['contact_account'].get('url','')
    instance_thumbnail = data['instance'].get('thumbnail','')

    data_list_instance_json.append((instance_updated_ts,instance_uri,instance_title,instance_description,instance_version,instance_user_count,instance_status_count,instance_invites,instance_registrations,instance_email,instance_contact,instance_thumbnail))

    num_entries = len(data_list_instance_json)
    if num_entries > 0:
        description = 'Details for the instance of Mastodon the user has joined.'
        report = ArtifactHtmlReport('Mastodon - Instance Details')
        report.start_artifact_report(report_folder, 'Mastodon - Instance Details', description)
        report.add_script()
        data_headers = ('Last Updated Timestamp','URI','Title','Description','Version','User Count','Status Count','Invites Enable','Registrations Enabled','Admin Contact Email','Owner','Thumbnail')

        report.write_artifact_data_table(data_headers, data_list_instance_json, file_found)
        report.end_artifact_report()
        
        tsvname = f'Mastodon - Instance Details'
        tsv(report_folder, data_headers, data_list_instance_json, tsvname)
        
        tlactivity = f'Mastodon - Instance Details'
        timeline(report_folder, tlactivity, data_list_instance_json, data_headers)
    else:
        logfunc('No Mastodon - Instance Details data available')

__artifacts__ = {
        "mastodon": (
                "Mastodon",
                ('*/org.joinmastodon.android/databases/*.db*','*/org.joinmastodon.android/files/*.json'),
                get_mastodon)
}
