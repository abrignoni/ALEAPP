import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_skout(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('skoutDatabase'):
            
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT 
            strftime('%Y-%m-%d %H:%M:%S.', "timestamp"/1000, 'unixepoch') || ("timestamp"%1000) AS MessageTime,
            
            ifnull(skoutUsersTable.userName,'(local user)') AS SkoutUser,
            
            skoutMessagesTable.message,
            skoutMessagesTable.type,
            skoutMessagesTable.pictureUrl,
            skoutMessagesTable.giftUrl,
            skoutMessagesTable.chatId AS ThreadID
            
            FROM skoutMessagesTable
                LEFT JOIN skoutUsersTable ON skoutMessagesTable.fromUserID = skoutUsersTable.userId
                
                ORDER BY skoutMessagesTable.chatId,
                skoutMessagesTable.timestamp
            ''')
            
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Skout Messages')
                report.start_artifact_report(report_folder, 'Skout Messages')
                report.add_script()
                data_headers = ('Timestamp','User','Message','Type','Picture URL','Gift URL','Thread ID' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
            
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Skout Messages'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Skout Messages'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Skout Messages data available')
        
        
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT 
            strftime('%Y-%m-%d %H:%M:%S.', "lastMessageTimestamp"/1000, 'unixepoch') || ("lastMessageTimestamp"%1000) AS LastMessageTime,
            skoutUsersTable.userName,
            skoutUsersTable.picUrl,
            skoutUsersTable.userId AS UserID
            FROM skoutUsersTable
            ORDER BY skoutUsersTable.lastMessageTimestamp
            ''')
            
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Skout Users')
                report.start_artifact_report(report_folder, 'Skout Users')
                report.add_script()
                data_headers = ('Last Message Timestamp','User','Picture URL','User ID' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3]))
                    
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Skout Users'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Skout Users'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Skout Users data available')
                
        
    db.close()

__artifacts__ = {
        "skout": (
                "Skout",
                ('*/com.skout.android/databases/skoutDatabase*'),
                get_skout)
}