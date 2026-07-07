# pylint: disable=W0613
__artifacts_v2__ = {
    "get_Todoist": {
        "name": "Todoist - Items",
        "description": "Todoist - Parses task items",
        "author": "Kevin Pagano (https://startme.stark4n6.com)",
        "creation_date": "2023-04-26",
        "last_update_date": "2023-04-26",
        "requirements": "None",
        "category": "Todoist",
        "notes": "",
        "paths": ('*/com.todoist/databases/database.db*',),
        "output_types": "standard",
        "artifact_icon": "square-check",
    },
    "get_Todoist_notes": {
        "name": "Todoist - Notes",
        "description": "Todoist - Parses notes and attachments",
        "author": "Kevin Pagano (https://startme.stark4n6.com)",
        "creation_date": "2023-04-26",
        "last_update_date": "2023-04-26",
        "requirements": "None",
        "category": "Todoist",
        "notes": "",
        "paths": ('*/com.todoist/databases/database.db*',),
        "output_types": "standard",
        "artifact_icon": "file-text",
    },
    "get_Todoist_projects": {
        "name": "Todoist - Projects",
        "description": "Todoist - Parses projects",
        "author": "Kevin Pagano (https://startme.stark4n6.com)",
        "creation_date": "2023-04-26",
        "last_update_date": "2023-04-26",
        "requirements": "None",
        "category": "Todoist",
        "notes": "",
        "paths": ('*/com.todoist/databases/database.db*',),
        "output_types": "standard",
        "artifact_icon": "folder",
    }
}

import datetime
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _todoist_db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('database.db'):
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
def get_Todoist(files_found, report_folder, seeker, wrap_text):
    source_path = _todoist_db(files_found)
    rows = _run(source_path, '''
        SELECT items.date_added, items.added_by_uid, items.content, items.description, items.due_date,
        items.due_timezone, items.due_string,
        CASE items.due_is_recurring WHEN 0 THEN '' WHEN 1 THEN 'Yes' END,
        items.priority, items.child_order, projects.name, item_labels.label_name, items._id
        FROM items
        LEFT OUTER JOIN projects ON items.project_id = projects._id
        LEFT OUTER JOIN item_labels ON items._id = item_labels.item_id
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12])
                 for r in rows]
    data_headers = (
        ('Timestamp Added', 'datetime'), 'Added By UID', 'Content', 'Description', 'Due Date',
        'Due Timezone', 'Due String', 'Recurring Due Date', 'Priority', 'Child Order', 'Project Name',
        'Label', 'Item ID')
    return data_headers, data_list, source_path


@artifact_processor
def get_Todoist_notes(files_found, report_folder, seeker, wrap_text):
    source_path = _todoist_db(files_found)
    rows = _run(source_path, '''
        SELECT notes.posted, notes.content, note_file_attachments.resource_type,
        note_file_attachments.file_url, note_file_attachments.file_name, note_file_attachments.file_type,
        note_file_attachments.file_size, note_file_attachments.image, note_file_attachments.title,
        note_file_attachments.description, notes._id
        FROM notes
        LEFT OUTER JOIN note_file_attachments ON notes._id = note_file_attachments.note_id
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10]) for r in rows]
    data_headers = (
        ('Timestamp Posted', 'datetime'), 'Content', 'Resource Type', 'File URL', 'File Name', 'File Type',
        'File Size', 'Image', 'Title', 'Description', 'Note ID')
    return data_headers, data_list, source_path


@artifact_processor
def get_Todoist_projects(files_found, report_folder, seeker, wrap_text):
    source_path = _todoist_db(files_found)
    rows = _run(source_path, '''
        SELECT name, color, view_style, child_order,
        CASE collapsed WHEN 0 THEN '' WHEN 1 THEN 'Yes' END,
        CASE shared WHEN 0 THEN '' WHEN 1 THEN 'Yes' END,
        CASE favorite WHEN 0 THEN '' WHEN 1 THEN 'Yes' END, type
        FROM projects
    ''')
    data_headers = ('Project Name', 'Color', 'View Style', 'Child Order', 'Collapsed', 'Shared',
                    'Favorited', 'Type')
    return data_headers, [tuple(r) for r in rows], source_path
