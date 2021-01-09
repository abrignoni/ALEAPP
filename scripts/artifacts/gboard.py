import blackboxprotobuf
import os
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, does_table_exist

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

def get_gboardCache(files_found, report_folder, seeker):
    
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.find('\\mirror\\') >= 0 or file_found.find('/mirror/') >= 0:
            # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data
            continue

        if file_found.endswith('trainingcachev2.db'):
            read_trainingcachev2(file_found, report_folder, seeker)
        elif file_found.endswith('trainingcache2.db') or file_found.endswith('trainingcache3.db'):
            read_trainingcache2(file_found, report_folder, seeker)

def read_trainingcache2(file_found, report_folder, seeker):
    db = open_sqlite_db_readonly(file_found)
    db.row_factory = sqlite3.Row # For fetching columns by name
    cursor = db.cursor()

    keyboard_events = []
    if does_table_exist(db, 'training_input_events_table'):
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
            
    elif does_table_exist(db, 'tf_table'):
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

        data_headers = ('Id','Text','App','Input Name','Input ID','Event Timestamp')
        data_list = []
        for ke in keyboard_events:
            data_list.append((ke.id, ke.text, ke.app, ke.textbox_name, ke.textbox_id, ke.event_date))

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
    logfunc(f"Skipping f{file_found}, parser not implemented yet!")