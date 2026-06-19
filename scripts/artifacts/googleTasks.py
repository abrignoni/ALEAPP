# pylint: disable=E0606,W0613
__artifacts_v2__ = {
    "get_googleTasks": {
        "name": "GoogleTasks",
        "description": "",
        "author": "",
        "creation_date": "2021-08-21",
        "last_update_date": "2021-08-21",
        "requirements": "none",
        "category": "Google Tasks",
        "notes": "",
        "paths": ('*/com.google.android.apps.tasks/files/tasks-*/data.db',),
        "output_types": "standard",
        "artifact_icon": "file-text",
    }
}

from datetime import datetime
import blackboxprotobuf

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def b2s(a):
    return "".join(list(map(chr, a)))


def protobuf_parse_not_completed(data):
    pb = blackboxprotobuf.decode_message(data, 'None')
    completed = pb[0].get('2',{}).get('5',{}).get('1','')
    created = datetime.utcfromtimestamp(pb[0].get('11',{}).get('1','')).strftime('%Y-%m-%d %H:%M:%S')
    modified = datetime.utcfromtimestamp(pb[0].get('3',{}).get('1','')).strftime('%Y-%m-%d %H:%M:%S')
    task = pb[0].get('2',{}).get('2','').decode()
    task_details = b2s(pb[0].get('2',{}).get('3',''))
    timezone = b2s(pb[0].get('9',{}).get('1',{}).get('4',''))
    return task, task_details, created, completed, modified, timezone


def protobuf_parse_completed(data):
    pb = blackboxprotobuf.decode_message(data, None)
    task = pb[0].get('2',{}).get('2','').decode()
    task_details = b2s(pb[0].get('2',{}).get('3',''))
    completed = datetime.utcfromtimestamp(pb[0].get('2',{}).get('5',{}).get('1','')).strftime('%Y-%m-%d %H:%M:%S')
    created = datetime.utcfromtimestamp(pb[0].get('11',{}).get('1','')).strftime('%Y-%m-%d %H:%M:%S')
    modified = datetime.utcfromtimestamp(pb[0].get('3',{}).get('1','')).strftime('%Y-%m-%d %H:%M:%S')
    timezone = b2s(pb[0].get('9',{}).get('1',{}).get('4',''))
    return task, task_details, created, completed, modified, timezone


@artifact_processor
def get_googleTasks(files_found, report_folder, seeker, wrap_text):
    all_new_rows = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        source_path = file_found

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute('''
            SELECT
            TaskId, TaskListId, TaskRecurrenceId, EffectiveTask, Completed, HasDirtyState, DueDate
            FROM
            Tasks;
        ''')

        all_rows = cursor.fetchall()
        for row in all_rows:
            if(row[4] == 0):
                task, task_details, created, completed, modified, timezone = protobuf_parse_not_completed(row[3])
            elif(row[4] == 1):
                task, task_details, created, completed, modified, timezone = protobuf_parse_completed(row[3])
            new_data = (created, modified, completed, row[6], timezone, row[0], row[1], row[2], task, task_details, 'True' if row[4]==1 else 'False', 'True' if row[5]==1 else 'False')
            all_new_rows.append(new_data)

        db.close()

    data_headers = (
        ('Created Time', 'datetime'),
        ('Last Modified Time', 'datetime'),
        ('Completed Time', 'datetime'),
        'Task Due Date',
        'Time Zone',
        'Task ID',
        'Task List ID',
        'Task Recurrence Id',
        'Task Name',
        'Task Details',
        'Completed',
        'Has Dirty State',
    )
    return data_headers, all_new_rows, source_path
