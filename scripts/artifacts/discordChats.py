import sqlite3
import textwrap
import sys
import json
from datetime import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, kmlgen

def get_discordChats(files_found, report_folder, seeker, wrap_text):
    
    # build a table mapping all non-printable characters to None
    NOPRINT_TRANS_TABLE = {
        i: None for i in range(0, sys.maxunicode + 1) if not chr(i).isprintable()
    }
    
    def make_printable(s):
        """Replace non-printable characters in a string."""
        
        # the translate method on str removes characters
        # that map to None from the string
        return s.translate(NOPRINT_TRANS_TABLE)
    
    for file_found in files_found:
        file_name = str(file_found)
        if file_found.endswith('a'):
            break # Skip all other files
    
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
        SELECT
        * 
        from messages0
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Discord Chats')
        report.start_artifact_report(report_folder, 'Discord Chats')
        report.add_script()
        data_headers = ('Timestamp','Channel ID','ID','Username','Content','Attachment Filename','Attachment URL','Attachment Proxy URL','Mentions','Mention Roles','Pinned','Avatar','Edited Timestamp')
        data_list = []

        for row in all_rows:
            data = (row[6].decode())
            
            jsontext = make_printable(data)	
            
            data = json.loads(jsontext)
            #print(data)
            datatimestamp = (data['message']['timestamp'])
            channelid = (data['channelId'])
            dataid = (data['id'])
            #print(data['message'])
            username = (data['message']['author']['username'])
            content = (data['message']['content'])
            attachments = (data['message']['attachments'])
            if len(attachments) > 0:
                attachementfilename = (attachments[0]['filename'])
                attachementurl = (attachments[0]['url'])
                attachmentproxyurl = (attachments[0]['proxy_url'])
            else:
                attachementfilename = attachementurl = attachmentproxyurl = ''
            mentions = (data['message']['mentions'])
            mentionroles = (data['message']['mention_roles'])
            pinned = (data['message']['pinned'])
            avatar = (data['message']['author']['avatar'])
            editedtimestamp = (data['message']['edited_timestamp'])
            
            data_list.append((datatimestamp,channelid,dataid,username,content,attachementfilename,attachementurl,attachmentproxyurl,mentions,mentionroles,pinned,avatar,editedtimestamp))
            
            
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Discord Chats'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Discord Chats'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Discord Chats data available')
        
    db.close()

__artifacts__ = {
        "discordChats": (
                "Discord Chats",
                ('*/data/com.discord/files/kv-storage/*/a*'),
                get_discordChats)
}
