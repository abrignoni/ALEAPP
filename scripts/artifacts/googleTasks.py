import os
import textwrap
from datetime import datetime
import blackboxprotobuf

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

is_windows = is_platform_windows()
slash = '\\' if is_windows else '/' 

def b2s(a):
    return "".join(list(map(chr, a))) 

def protobuf_parse_not_completed(data):
    pb = blackboxprotobuf.decode_message(data, 'None')
    completed = pb[0].get('2',{}).get('5',{}).get('1','')
    created = datetime.utcfromtimestamp(pb[0].get('11',{}).get('1','')).strftime('%Y-%m-%d %H:%M:%S')
    modified = datetime.utcfromtimestamp(pb[0].get('3',{}).get('1','')).strftime('%Y-%m-%d %H:%M:%S')
    task = pb[0].get('2',{}).get('2','').decode()
    task_details = b2s(pb[0].get('2',{}).get('3',''))
    # duetime = pb[0].get('9',{}).get('1',{}).get('6',{}).get('1','')
    # duetime = datetime.utcfromtimestamp(duetime).strftime('%Y-%m-%d %H:%M:%S') # TypeError: an integer is required (got type str)
    timezone = b2s(pb[0].get('9',{}).get('1',{}).get('4',''))
    return task, task_details, created, completed, modified, timezone

def protobuf_parse_completed(data):
    pb = blackboxprotobuf.decode_message(data, None)
    task = pb[0].get('2',{}).get('2','').decode()
    task_details = b2s(pb[0].get('2',{}).get('3',''))
    completed = datetime.utcfromtimestamp(pb[0].get('2',{}).get('5',{}).get('1','')).strftime('%Y-%m-%d %H:%M:%S')
    created = datetime.utcfromtimestamp(pb[0].get('11',{}).get('1','')).strftime('%Y-%m-%d %H:%M:%S')
    modified = datetime.utcfromtimestamp(pb[0].get('3',{}).get('1','')).strftime('%Y-%m-%d %H:%M:%S')
    # duetime = pb[0].get('9',{}).get('1',{}).get('6',{}).get('1','')
    # duetime = datetime.utcfromtimestamp(duetime).strftime('%Y-%m-%d %H:%M:%S') # TypeError: an integer is required (got type str)
    timezone = b2s(pb[0].get('9',{}).get('1',{}).get('4',''))
    return task, task_details, created, completed, modified, timezone

def get_googleTasks(files_found, report_folder, seeker, wrap_text):
    for file_found in files_found:
        file_found = str(file_found)

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT
            TaskId, TaskListId, TaskRecurrenceId, EffectiveTask, Completed, HasDirtyState, DueDate
            FROM
            Tasks;
        ''')

        all_rows = cursor.fetchall()
        all_new_rows = []

        for row in all_rows:
            if(row[4] == 0):
                task, task_details, created, completed, modified, timezone = protobuf_parse_not_completed(row[3])
            elif(row[4] == 1):
                task, task_details, created, completed, modified, timezone = protobuf_parse_completed(row[3])
            new_data = (created, modified, completed, row[6], timezone, row[0], row[1], row[2], task, task_details, 'True' if row[4]==1 else 'False', 'True' if row[5]==1 else 'False')
            all_new_rows.append(new_data)

        usageentries = len(all_new_rows)
        if(usageentries > 0):
            report = ArtifactHtmlReport('Google Tasks')
            report.start_artifact_report(report_folder,"Google Tasks")
            report.add_script()

            data_headers=('Created Time', 'Last Modified Time', 'Completed Time', 'Task Due Date', 'Time Zone','Task ID', 'Task List ID', 'Task Recurrence Id', 'Task Name', 'Task Details', 'Completed', 'Has Dirty State')

            data_list = all_new_rows

            report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
            report.end_artifact_report()

            tsvname = "Google Tasks"
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = "Google Tasks"
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No Google Tasks found')

        
        db.close()
        
__artifacts__ = {
        "GoogleTasks": (
                "Google Tasks",
                ('*/com.google.android.apps.tasks/files/tasks-*/data.db'),
                get_googleTasks)
}