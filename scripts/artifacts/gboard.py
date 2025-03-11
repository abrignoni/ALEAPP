# Update 2023-05-01 from @KevinPagano3 (https://startme.stark4n6.com)
# Added support for parsing gboard_clipboard.db database

import blackboxprotobuf
import os
import shutil
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, does_table_exist_in_db, media_to_html

class keyboard_event:
    def __init__(self, id, app, text, textbox_name, textbox_id, event_date, start_date='', end_date=''):
        self.id = id
        self.app = app
        self.text = text
        self.textbox_name = textbox_name
        self.textbox_id = textbox_id
        self.event_date = event_date
        self.start_date = start_date
        self.end_date = end_date

def get_gboardCache(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.find('\\mirror\\') >= 0 or file_found.find('/mirror/') >= 0:
            # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data
            continue

        if file_found.endswith('trainingcachev2.db'):
            read_trainingcachev2(file_found, report_folder, seeker)
        elif file_found.endswith('trainingcache2.db') or file_found.endswith('trainingcache3.db'):
            read_trainingcache2(file_found, report_folder, seeker)
        elif file_found.endswith('trainingcachev3.db'):
            read_trainingcachev3_sessions(file_found, report_folder, seeker)
        elif file_found.endswith('gboard_clipboard.db'):
            read_gboard_clipboard(file_found, files_found, report_folder, seeker)
            
        else:
            continue
            
def read_gboard_clipboard(file_found, files_found, report_folder, seeker):
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select
    datetime(timestamp/1000,'unixepoch'),
    text,
    html_text,
    uri,
    case item_type
        when 0 then ''
        when 1 then 'Pinned'
        else item_type
    end as "Item Type",
    case entity_type
        when 0 then ''
        when 1 then 'Link'
        else entity_type
    end as "Entity Type",
    _id,
    replace(uri, rtrim(uri, replace(uri, '/', '')), '')
    from clips''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    data_list = []
    thumb = ''
    if usageentries > 0:
        for row in all_rows:
            fileNameKey = str(row[7])
            if fileNameKey != '':
                for match in files_found:
                    if fileNameKey in match:
                        thumb = media_to_html(match, files_found, report_folder)
            else:
                thumb = ''
            data_list.append((row[0],row[1],row[2],row[3],thumb,row[4],row[5],row[6]))
        
        report = ArtifactHtmlReport('Gboard - Clipboard')
        report.start_artifact_report(report_folder, 'Gboard - Clipboard')
        report.add_script()
        data_headers = ('Timestamp','Text','HTML Text','URI','Image','Item Type','Entity Type','ID')
        
        report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Image'])
        report.end_artifact_report()
        
        tsvname = 'Gboard - Clipboard'
        tsv(report_folder, data_headers, data_list, tsvname, file_found)
        
        tlactivity = 'Gboard - Clipboard'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Gboard - Clipboard data available')
    
    db.close()
            
    

def read_trainingcache2(file_found, report_folder, seeker):
    db = open_sqlite_db_readonly(file_found)
    db.row_factory = sqlite3.Row # For fetching columns by name
    cursor = db.cursor()

    keyboard_events = []
    if does_table_exist_in_db(file_found, 'training_input_events_table'):
        try:
            cursor.execute('''
                SELECT _id, _payload, f2 as app, f4 as textbox_name, f5 as textbox_id, datetime(f9/1000, "unixepoch") as ts
                FROM training_input_events_table 
            ''')
            pb_types = {'7': {'type': 'message', 'message_typedef': 
                            {
                            '2': {'type': 'message', 'message_typedef': 
                                    {
                                    '1': {'name': '', 'type': 'bytes'}
                                    }
                                }
                            } }
                        }
            all_rows = cursor.fetchall()
            for row in all_rows:
                pb = row['_payload']
                data, actual_types = blackboxprotobuf.decode_message(pb, pb_types)
                texts = data.get('7', {}).get('2', [])
                text_typed = ''
                if texts:
                    if isinstance(texts, list):
                        for t in texts:
                            text_typed += t.get('1', b'').decode('utf8', 'ignore')
                    else:
                        text_typed = texts.get('1', b'').decode('utf8', 'ignore')

                # Not filtering out blanks for now
                textbox_name = row['textbox_name']
                textbox_id = row['textbox_id']
                if len(textbox_id) > len(textbox_name):
                    textbox_id = textbox_id[len(textbox_name) + 4:]
                keyboard_events.append(keyboard_event(row['_id'], row['app'], text_typed, row['textbox_name'], row['textbox_id'], row['ts']))
        except (sqlite3.Error, TypeError, ValueError) as ex:
            logfunc(f'read_trainingcache2 had an error reading {file_found} ' + str(ex))
            
    elif does_table_exist_in_db(file_found, 'tf_table'):
        try:
            cursor.execute('''
                SELECT s._id, ts, f3_concat as text_entered, s.f7 as textbox_name, s.f8 as app, s.f9, 
                datetime(s.f10/1000, 'unixepoch') as start_ts, datetime(s.f11/1000, 'unixepoch') as end_ts
                FROM 
                (select datetime(_timestamp/1000, 'unixepoch') as ts, f1,
                group_concat(f3, '') as f3_concat 
                FROM tf_table GROUP BY f1) x
                LEFT JOIN s_table s on s.f1=x.f1
            ''')

            all_rows = cursor.fetchall()
            for row in all_rows:
                keyboard_events.append(keyboard_event(row['_id'], row['app'], row['text_entered'], row['textbox_name'], '', row['ts'], row['start_ts'], row['end_ts']))
        except (sqlite3.Error, TypeError, ValueError) as ex:
            logfunc(f'read_trainingcache2 had an error reading {file_found} ' + str(ex))

    file_name = os.path.basename(file_found)
    if keyboard_events:
        description = "Keystrokes typed by the user in various input fields of apps, that have been temporarily cached by the Gboard keyboard app are seen here."
        report = ArtifactHtmlReport(f'Gboard Keystroke cache - {file_name}')
        report.start_artifact_report(report_folder, f'{file_name}', description)
        report.add_script()

        data_headers = ('Event Timestamp','ID','Text','App','Input Name','Input ID')
        data_list = []
        for ke in keyboard_events:
            data_list.append((ke.event_date, ke.id, ke.text, ke.app, ke.textbox_name, ke.textbox_id))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Gboard Keystroke cache - {file_name}'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Gboard Keystroke cache - {file_name}'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc(f'No Gboard data available in {file_name}')
    
    db.close()

def read_trainingcachev2(file_found, report_folder, seeker):
    db = open_sqlite_db_readonly(file_found)
    db.row_factory = sqlite3.Row # For fetching columns by name
    cursor = db.cursor()
    keyboard_events = []
    try:
        cursor.execute('''
            SELECT i._payload as data_proto,  s._payload as desc_proto, 
            datetime(i._timestamp/1000, 'unixepoch') as ts1, datetime(s._timestamp/1000, 'unixepoch') as ts2
            , s._id as session, i._id as id
            FROM input_action_table i LEFT JOIN session_table s ON s._session_id=i._session_id
        ''')

        all_rows = cursor.fetchall()
        last_session = None
        ke = None
        for row in all_rows:
            session = row['session']
            if last_session != session:
                # write out last_session
                if ke and ke.text:
                    keyboard_events.append(ke)
                last_session = session
                ke = keyboard_event(row['id'], '', '', '', '', row['ts2'], row['ts1'], row['ts1'])
                desc_proto = row['desc_proto']
                if desc_proto:
                    desc, actual_types = blackboxprotobuf.decode_message(desc_proto, None)
                    try:
                        ke.textbox_name = desc.get('6', b'').decode('utf8', 'ignore')
                    except AttributeError:
                        pass
                    try:
                        ke.app = desc.get('7', b'').decode('utf8', 'ignore')
                    except AttributeError:
                        pass
            ke.end_date = row['ts1']
            data_proto = row['data_proto']
            if data_proto:
                data, actual_types = blackboxprotobuf.decode_message(data_proto, None)
                input_dict = data.get('6', None) # It's either an input or an output (suggested words) proto type
                if input_dict:
                    index = input_dict.get('1', {}).get('1', -1)
                    chars_items = input_dict.get('4', {})
                    chars = ''
                    if isinstance(chars_items, list):
                        for item in chars_items:
                            try:
                                chars += item.get('1', b'').decode('utf8', 'ignore')
                            except AttributeError:
                                pass
                    else:
                        try:
                            chars = chars_items.get('1', b'').decode('utf8', 'ignore')
                        except AttributeError:
                            pass
                    ke.text += chars
        if ke and ke.text: # write out last event
            keyboard_events.append(ke)
    except (sqlite3.Error, TypeError, ValueError) as ex:
        logfunc(f'read_trainingcache2 had an error reading {file_found} ' + str(ex))

    file_name = os.path.basename(file_found)
    if keyboard_events:
        description = "Keystrokes typed by the user in various input fields of apps, that have been temporarily cached by the Gboard keyboard app are seen here."
        report = ArtifactHtmlReport(f'Gboard Keystroke cache - {file_name}')
        report.start_artifact_report(report_folder, f'{file_name}', description)
        report.add_script()

        data_headers = ('Event Timestamp','ID','Text','App','Input Name','Input ID')
        data_list = []
        for ke in keyboard_events:
            data_list.append((ke.event_date, ke.id, ke.text, ke.app, ke.textbox_name, ke.textbox_id))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Gboard Keystroke cache - {file_name}'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Gboard Keystroke cache - {file_name}'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc(f'No Gboard data available in {file_name}')
    
    db.close()


def read_trainingcachev3_sessions(file_found, report_folder, seeker):

    title = "Gboard - Sessions"

    # Connect to database
    conn = open_sqlite_db_readonly(file_found)
    cursor = conn.cursor()

    # Sessions
    sql = """
        SELECT
            datetime(session._session_id / 1000, 'unixepoch') AS Start,
            datetime(session._timestamp_ / 1000, 'unixepoch') AS Finish,
            session._session_id AS Session,
            session.package_name AS Application 
        FROM 
            session
        """
    cursor.execute(sql)
    results = cursor.fetchall()

    if results:
        data_headers = ("Start", "Finish", "Session ID", "Application")
        data_list = results

        description = "GBoard Sessions"
        report = ArtifactHtmlReport(title)
        report.start_artifact_report(report_folder, title, description)
        report.add_script()
        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
        report.end_artifact_report()

        tsv(report_folder, data_headers, data_list, title)
        
        timeline(report_folder, title, data_list, data_headers)

    # Close
    conn.close()

__artifacts__ = {
        "GboardCache": (
                "Gboard Keyboard",
                ('*/com.google.android.inputmethod.latin/databases/trainingcache*.db','*/com.google.android.inputmethod.latin/databases/gboard_clipboard.db*','*/com.google.android.inputmethod.latin/files/clipboard_image/*'),
                get_gboardCache)
}