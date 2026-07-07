# pylint: disable=W0613
__artifacts_v2__ = {
    "get_adidas_goals": {
        "name": "AdidasGoals",
        "description": "Get Information related to user defined goals from the Adidas Running app stored in goals",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-04-21",
        "last_update_date": "2023-04-21",
        "requirements": "Python 3.7 or higher",
        "category": "Adidas-Running",
        "notes": "",
        "paths": ('*/com.runtastic.android/databases/goals*',),
        "output_types": "standard",
        "artifact_icon": "activity",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


def _yyyymmdd(value):
    if value:
        s = str(value)
        return s[:4] + '-' + s[4:6] + '-' + s[6:]
    return ''


@artifact_processor
def get_adidas_goals(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Adidas Goals")
    files_found = [x for x in files_found if not str(x).endswith('-journal')]
    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        Select *
        from goalV2
    ''')
    all_rows = cursor.fetchall()
    db.close()

    data_list = []
    for row in all_rows:
        data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6],
                          _yyyymmdd(row[8]), _yyyymmdd(row[9]), row[10],
                          _ms_to_utc(row[11]), _ms_to_utc(row[12]), _ms_to_utc(row[13])))

    data_headers = ('ID', 'Metric', 'Remote ID', 'User ID', 'Version', 'Target', 'Recurrence', 'Start Date', 'End Date', 'Sport Types', ('Created At', 'datetime'), ('Updated At', 'datetime'), ('Deleted At', 'datetime'))
    return data_headers, data_list, source_path
