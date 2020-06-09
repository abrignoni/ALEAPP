import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows

def get_ChessWithFriendsChats(files_found, report_folder, seeker):
    
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
	chat_messages.chat_message_id,
	users.name,
	users.email_address,
	chat_messages.message,
	chat_messages.created_at
	FROM
	chat_messages
	INNER JOIN
	users
	ON
	chat_messages.user_id=users.user_id
	ORDER BY
	chat_messages.created_at DESC
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Chats')
        report.start_artifact_report(report_folder, 'Chess With Friends Chats')
        report.add_script()
        data_headers = ('Message_ID','User_Name','User_Email','Chat_Message','Chat_Message_Creation' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Chess With Friends Chats'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No Chess With Friends Chats data available')
    
    db.close()
    return

