# pylint: disable=W0613
__artifacts_v2__ = {
    "get_googleKeepNotes": {
        "name": "Google Keep - Notes",
        "description": "Google Keep notes",
        "author": "",
        "creation_date": "2021-05-17",
        "last_update_date": "2021-05-17",
        "requirements": "none",
        "category": "Google Keep",
        "notes": "",
        "paths": ('*/com.google.android.keep/databases/keep.db*',),
        "output_types": "standard",
        "artifact_icon": "file-text",
    },
    "get_googleKeepNotes_sharing": {
        "name": "Google Keep - Notes Sharing",
        "description": "Google Keep note sharing",
        "author": "",
        "creation_date": "2021-05-17",
        "last_update_date": "2021-05-17",
        "requirements": "none",
        "category": "Google Keep",
        "notes": "",
        "paths": ('*/com.google.android.keep/databases/keep.db*',),
        "output_types": "standard",
        "artifact_icon": "share-2",
    }
}

import datetime
import os
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _keep_db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.basename(file_found) == 'keep.db':
            return file_found
    return ''


def _run(source_path, sql):
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


@artifact_processor
def get_googleKeepNotes(files_found, report_folder, seeker, wrap_text):
    source_path = _keep_db(files_found)
    rows = _run(source_path, '''
        SELECT list_item.time_created, list_item.time_last_updated, list_parent_id, name, title, text,
        synced_text, list_item.is_deleted, last_modifier_email
        FROM account
        INNER JOIN list_item ON account._id == list_item.account_id
        INNER JOIN tree_entity ON tree_entity._id == list_item._id
    ''')
    data_list = [(_ms_to_utc(r[0]), _ms_to_utc(r[1]), r[2], r[3], r[4], r[5], r[6],
                  'True' if r[7] == 1 else 'False', r[8]) for r in rows]
    data_headers = (('Notes Creation Time', 'datetime'), ('Notes Last Modified Time', 'datetime'),
                    'List Parent ID', 'Creator Email', 'Title', 'Text', 'Synced Text', 'Is deleted',
                    'Last Modifier Email')
    return data_headers, data_list, source_path


@artifact_processor
def get_googleKeepNotes_sharing(files_found, report_folder, seeker, wrap_text):
    source_path = _keep_db(files_found)
    rows = _run(source_path, '''
        SELECT tree_entity.shared_timestamp, list_item.list_parent_id, account.name, sharing.email,
        title, text, sync_status, sharing.is_deleted
        FROM account
        INNER JOIN list_item ON list_item.account_id == account._id
        INNER JOIN tree_entity ON tree_entity._id == list_item._id
        INNER JOIN sharing ON list_item._id == sharing.tree_entity_id
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5],
                  'Synced' if r[6] == 1 else 'Not Synced', 'True' if r[7] == 1 else 'False') for r in rows]
    data_headers = (('Notes Shared Timestamp', 'datetime'), 'List Parent ID', 'Creator Email', 'Shared Email',
                    'Title', 'Text', 'Sync Status', 'Is deleted')
    return data_headers, data_list, source_path
