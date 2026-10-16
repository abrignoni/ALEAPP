# pylint: disable=E0606
__artifacts_v2__ = {
    "get_googleTasks": {
        "name": "GoogleTasks",
        "description": "Parses Google Tasks (created, modified, completed and due times, task name, details and status) from the Google Tasks data.db.",
        "author": "@bolisettynihith, @AlexisBrignoni, Codex",
        "creation_date": "2021-08-21",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Google Tasks",
        "notes": "Protobuf field positions for created/modified/completed times are not "
                 "documented and were assigned by the module from values on data that is not "
                 "recorded here: Created Time is field 11.1, Last Modified Time field 3.1 and "
                 "Completed Time field 2.5.1 of the EffectiveTask blob, each read as Unix "
                 "seconds. No registered image is listed for this artifact. Task Due "
                 "Date is reported as stored in the DueDate column, without "
                 "conversion, unlike Created Time, Last Modified Time and Completed Time, which "
                 "are converted to UTC. Completed Time is read from field 2.5.1 the same way on "
                 "every row. On a row whose Completed column is False the column is blank when "
                 "that field holds no integer; what an integer there marks on such a row is not "
                 "established, and no data holding one was available. The Google Tasks package "
                 "appeared on none of the 44 registered Android images when checked on "
                 "2026-10-04; the conversion on rows whose Completed column is False was "
                 "exercised only on a constructed record.",
        "paths": ('*/com.google.android.apps.tasks/files/tasks-*/data.db*',),
        "output_types": "standard",
        "artifact_icon": "file-text",
    }
}

from datetime import datetime, timezone as dtimezone
from scripts.ilapfuncs import decode_protobuf

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def b2s(a):
    return "".join(list(map(chr, a)))


def protobuf_parse_not_completed(data):
    pb = decode_protobuf(data, 'None')
    completed = pb[0].get('2',{}).get('5',{})
    completed = completed.get('1','') if isinstance(completed, dict) else ''
    if isinstance(completed, int):
        completed = datetime.fromtimestamp(completed, dtimezone.utc)
    else:
        completed = ''
    created = datetime.fromtimestamp(pb[0].get('11',{}).get('1',''), dtimezone.utc)
    modified = datetime.fromtimestamp(pb[0].get('3',{}).get('1',''), dtimezone.utc)
    task = pb[0].get('2',{}).get('2','').decode()
    task_details = b2s(pb[0].get('2',{}).get('3',''))
    timezone = b2s(pb[0].get('9',{}).get('1',{}).get('4',''))
    return task, task_details, created, completed, modified, timezone


def protobuf_parse_completed(data):
    pb = decode_protobuf(data, None)
    task = pb[0].get('2',{}).get('2','').decode()
    task_details = b2s(pb[0].get('2',{}).get('3',''))
    completed = datetime.fromtimestamp(pb[0].get('2',{}).get('5',{}).get('1',''), dtimezone.utc)
    created = datetime.fromtimestamp(pb[0].get('11',{}).get('1',''), dtimezone.utc)
    modified = datetime.fromtimestamp(pb[0].get('3',{}).get('1',''), dtimezone.utc)
    timezone = b2s(pb[0].get('9',{}).get('1',{}).get('4',''))
    return task, task_details, created, completed, modified, timezone


@artifact_processor
def get_googleTasks(context):
    files_found = context.get_files_found()
    all_new_rows = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith(('-wal', '-shm', '-journal')):
            continue
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
        'Task Due Date (as stored)',
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
