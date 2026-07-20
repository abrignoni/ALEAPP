# pylint: disable=W0718
__artifacts_v2__ = {
    "get_smyFiles": {
        "name": "My Files - Download History",
        "description": "Parses Samsung My Files download history (timestamp, name, full path, hidden and trashed flags and source) from the My Files database.",
        "author": "",
        "creation_date": "2020-12-17",
        "last_update_date": "2020-12-17",
        "requirements": "none",
        "category": "My Files",
        "notes": "",
        "paths": ('*/com.sec.android.app.myfiles/databases/MyFiles*.db*', '*/com.sec.android.app.myfiles/databases/myfiles.db*'),
        "output_types": "standard",
        "artifact_icon": "download",
    },
    "get_smyFiles_legacy": {
        "name": "My Files - Download History (Legacy)",
        "description": "Pre-Android 12 download_history schema",
        "author": "",
        "creation_date": "2020-12-17",
        "last_update_date": "2020-12-17",
        "requirements": "none",
        "category": "My Files",
        "notes": "",
        "paths": ('*/com.sec.android.app.myfiles/databases/MyFiles*.db*', '*/com.sec.android.app.myfiles/databases/myfiles.db*'),
        "output_types": "standard",
        "artifact_icon": "download",
    },
    "get_smyFiles_recent": {
        "name": "My Files - Recent Files (MyFiles DB)",
        "description": "Parses Samsung My Files recent files (timestamp, name, full path, hidden and trashed flags and source) from the My Files database.",
        "author": "",
        "creation_date": "2020-12-17",
        "last_update_date": "2020-12-17",
        "requirements": "none",
        "category": "My Files",
        "notes": "",
        "paths": ('*/com.sec.android.app.myfiles/databases/MyFiles*.db*', '*/com.sec.android.app.myfiles/databases/myfiles.db*'),
        "output_types": "standard",
        "artifact_icon": "file",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


def _myfiles_db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('.db'):
            return file_found
    return ''


def _query(source_path, sql):
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except Exception as e:
        logfunc(str(e))
        rows = []
    db.close()
    return rows


@artifact_processor
def get_smyFiles(context):
    files_found = context.get_files_found()
    source_path = _myfiles_db(files_found)
    rows = _query(source_path, '''
        select mDate, mName, mFullPath, mIsHidden, mTrashed, _source, _description, _from_s_browser
        from download_history
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6], r[7]) for r in rows]
    data_headers = (('Timestamp', 'datetime'), 'Name', 'Full Path', 'Is Hidden', 'Trashed?', 'Source', 'Description', 'From S Browser?')
    return data_headers, data_list, source_path


@artifact_processor
def get_smyFiles_legacy(context):
    files_found = context.get_files_found()
    source_path = _myfiles_db(files_found)
    rows = _query(source_path, '''
        select date, name, size, _data, _source, _description, _from_s_browser
        from download_history
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6]) for r in rows]
    data_headers = (('Timestamp', 'datetime'), 'Name', 'Size', 'Data', 'Source', 'Description', 'From S Browser?')
    return data_headers, data_list, source_path


@artifact_processor
def get_smyFiles_recent(context):
    files_found = context.get_files_found()
    source_path = _myfiles_db(files_found)
    rows = _query(source_path, '''
        select mDate, mName, mFullPath, mIsHidden, mTrashed, _source, _description, _from_s_browser
        from recent_files
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6], r[7]) for r in rows]
    data_headers = (('Timestamp', 'datetime'), 'Name', 'Full Path', 'Is Hidden', 'Trashed?', 'Source', 'Description', 'From S Browser?')
    return data_headers, data_list, source_path
