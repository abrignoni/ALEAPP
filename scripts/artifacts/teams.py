import os
import sqlite3
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly

def get_teams(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('SkypeTeams.db'):
            continue # Skip all other files

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime("arrivalTime"/1000, 'unixepoch'),
        userDisplayName,
        content,
        displayName,
        datetime("deleteTime"/1000, 'unixepoch'),
        Message.conversationId,
        messageId
        FROM Message
        left join Conversation
        on Message.conversationId = Conversation.conversationId
        ORDER BY  Message.conversationId, arrivalTime
        ''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Teams Messages')
            report.start_artifact_report(report_folder, 'Teams Messages')
            report.add_script()
            data_headers = ('Timestamp','User Display Name','Content','Topic Name','Delete Time','Conversation ID','Message ID')
            data_list=[]
            for row in all_rows:
                timeone = row[0]
                timetwo = row[4]
                if timeone == '1970-01-01 00:00:00':
                    timeone = ''
                if timetwo == '1970-01-01 00:00:00':
                    timetwo = ''
                data_list.append((timeone, row[1], row[2], row[3], timetwo, row[5], row[6]))
            report.write_artifact_data_table(data_headers, data_list, file_found) #, html_escape=False
            report.end_artifact_report()
            
            tsvname = 'Teams Messages'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Teams Messages'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('No Teams Messages data available')
    
        cursor.execute('''
        SELECT
        datetime("lastSyncTime"/1000, 'unixepoch'),
        givenName,
        surname,
        displayName,
        email,
        secondaryEmail,
        alternativeEmail,
        telephoneNumber,
        homeNumber,
        accountEnabled,
        type,
        userType,
        isSkypeTeamsUser,
        isPrivateChatEnabled
        from
        User
        ''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Teams Users')
            report.start_artifact_report(report_folder, 'Teams Users')
            report.add_script()
            data_headers = ('Last Sync','Given Name','Surname','Display Name','Email','Secondary Email','Alt. Email','Telephone Number','Home Number','Account Enabled?','Type','User Type','Is Teams User?','Is Private Chat Enabled?')
            data_list=[]
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13]))
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()
            
            tsvname = 'Teams Users'
            tsv(report_folder, data_headers, data_list, tsvname)
            
        else:
            logfunc('No Teams Users data available')

        cursor.execute('''
        SELECT
        datetime(json_extract(attributeValue, '$.connectTimeMillis') /1000, 'unixepoch') as connectTimeMillis,
        datetime(json_extract(attributeValue, '$.endTimeMillis') /1000, 'unixepoch') as endTimeMillis,
        json_extract(attributeValue, '$.callState') as callState,
        json_extract(attributeValue, '$.callType') as callType,
        json_extract(attributeValue, '$.originatorDisplayName') as originator,
        json_extract(attributeValue, '$.callDirection') as callDirection,
        User.givenName as targetparticipantName,
        json_extract(attributeValue, '$.sessionType') as sessionType,
        json_extract(attributeValue, '$.callId') as callId,
        json_extract(attributeValue, '$.target') as target
        from MessagePropertyAttribute, User
        where propertyId = 'CallLog' and target = User.mri
        ''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Teams Call Log')
            report.start_artifact_report(report_folder, 'Teams Call Log')
            report.add_script()
            data_headers = ('Connect Time','End Time','Call State','Call Type','Originator','Call Direction','Target Participant Name','Session Type')
            data_list=[]
            for row in all_rows:
                timeone = row[0]
                timetwo = row[1]
                if timeone == '1970-01-01 00:00:00':
                    timeone = ''
                if timetwo == '1970-01-01 00:00:00':
                    timetwo = ''
                data_list.append((timeone, timetwo, row[2], row[3], row[4], row[5], row[6], row[7]))
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()
            
            tsvname = 'Teams Call Log'
            tsv(report_folder, data_headers, data_list, tsvname)
            
        else:
            logfunc('No Teams Call Log data available')
    
    
        cursor.execute('''
        SELECT
        datetime("activityTimestamp"/1000, 'unixepoch') as activityTimestamp,
        sourceUserImDisplayName,
        messagePreview,
        activityType,
        activitySubtype,
        isRead
        FROM ActivityFeed
        ''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Teams Activity Feed')
            report.start_artifact_report(report_folder, 'Teams Activity Feed')
            report.add_script()
            data_headers = ('Timestamp','Display Name','Message Preview','Activity Type','Activity Subtype','Is read?')
            data_list=[]
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()
            
            tsvname = 'Teams Activity Feed'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Teams Activity Feed'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('No Teams Activity Feed data available')
        
        cursor.execute('''
        SELECT
        lastModifiedTime,
        fileName,
        type,
        objectUrl,
        isFolder,
        lastModifiedBy
        FROM FileInfo
        ''')
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Teams File Info')
            report.start_artifact_report(report_folder, 'Teams File Info')
            report.add_script()
            data_headers = ('Timestamp','File Name','Type','Object URL','Is Folder?','Last Modified By')
            data_list=[]
            for row in all_rows:
                mtime = row[0].replace('T', ' ')
                data_list.append((mtime, row[1], row[2], row[3], row[4], row[5]))
            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()
            
            tsvname = 'Teams File Info'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Teams File Info'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('No Teams File Info data available')
            
    db.close()

__artifacts__ = {
        "teams": (
                "Teams",
                ('*/com.microsoft.teams/databases/SkypeTeams.db*'),
                get_teams)
}
    