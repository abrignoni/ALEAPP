# pylint: disable=W0718
__artifacts_v2__ = {
    "get_smyfilesRecents": {
        "name": "My Files - Recent Files",
        "description": "Parses Samsung My Files recent files (modified timestamp, name, size, path, extension and source) from the My Files database.",
        "author": "",
        "creation_date": "2020-03-21",
        "last_update_date": "2020-03-21",
        "requirements": "none",
        "category": "My Files",
        "notes": "",
        "paths": ('*/com.sec.android.app.myfiles/databases/myfiles.db*', '*/com.sec.android.app.myfiles/databases/FileInfo.db*'),
        "output_types": "standard",
        "artifact_icon": "file",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.app.myfiles vc 1520402000 | 0 rows",
            "galaxys10_a10": "Android 10 | com.sec.android.app.myfiles vc 1150303551 | 13 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.app.myfiles vc 1520402000 | 0 rows",
            "samsungs20_a13": "Android 13 | com.sec.android.app.myfiles | 0 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.myfiles vc 1500405000 | 0 rows",
        },
    },
    "get_smyfilesRecents_fileinfo": {
        "name": "My Files - Recent Files (FileInfo)",
        "description": "Parses Samsung My Files recent files (recent and modified timestamps, file ID, package, path, size and download, hidden and trashed flags) from the My Files FileInfo database.",
        "author": "",
        "creation_date": "2020-03-21",
        "last_update_date": "2020-03-21",
        "requirements": "none",
        "category": "My Files",
        "notes": "",
        "paths": ('*/com.sec.android.app.myfiles/databases/myfiles.db*', '*/com.sec.android.app.myfiles/databases/FileInfo.db*'),
        "output_types": "standard",
        "artifact_icon": "file",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.app.myfiles vc 1520402000 | 97 rows",
            "galaxys10_a10": "Android 10 | com.sec.android.app.myfiles vc 1150303551 | 0 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.app.myfiles vc 1520402000 | 0 rows",
            "samsungs20_a13": "Android 13 | com.sec.android.app.myfiles | 0 rows",
            "sharon_a14": "Android 14 | com.sec.android.app.myfiles vc 1500405000 | 102 rows",
        },
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


@artifact_processor
def get_smyfilesRecents(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = _myfiles_db(files_found)
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        try:
            cursor.execute('''
                select date_modified, name, size, _data, ext, _source, _description, recent_date
                from recent_files
            ''')
            all_rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            all_rows = []
        db.close()
        for row in all_rows:
            data_list.append((_ms_to_utc(row[0]), row[1], row[2], row[3], row[4], row[5], row[6], _ms_to_utc(row[7])))

    data_headers = (('Timestamp', 'datetime'), 'Name', 'Size', 'Data', 'Ext.', 'Source', 'Description', ('Recent Timestamp', 'datetime'))
    return data_headers, data_list, source_path


@artifact_processor
def get_smyfilesRecents_fileinfo(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = _myfiles_db(files_found)
    if source_path:
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT
                recent_files.recent_date,
                recent_files.date_modified,
                recent_files.file_id,
                recent_files.package_name,
                recent_files.path,
                recent_files.size,
                case recent_files.is_download WHEN '1' THEN "True" WHEN '0' THEN "False" end,
                case recent_files.is_hidden WHEN '1' THEN "True" WHEN '0' THEN "False" end,
                case recent_files.is_trashed WHEN '1' then "True" when '0' then "False" end
                from recent_files
            ''')
            all_rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            all_rows = []
        db.close()
        for row in all_rows:
            data_list.append((_ms_to_utc(row[0]), _ms_to_utc(row[1]), row[2], row[3], row[4], row[5], row[6], row[7], row[8]))

    data_headers = (('Recent Timestamp', 'datetime'), ('Modified Timestamp', 'datetime'), 'File ID', 'Package Name',
                    'Path', 'Size', 'Is Downloaded?', 'Is Hidden?', 'Is Trashed?')
    return data_headers, data_list, source_path
