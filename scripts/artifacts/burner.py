# pylint: disable=W0613
__artifacts_v2__ = {
    "get_burner": {
        "name": "Burner - Numbers",
        "description": "Burner phone number information",
        "author": "Josh Hickman (josh@thebinaryhick.blog)",
        "creation_date": "2021-02-05",
        "last_update_date": "2021-02-05",
        "requirements": "None",
        "category": "Burner",
        "notes": "",
        "paths": ('*/com.adhoclabs.burner/databases/burners.db',),
        "output_types": "standard",
        "artifact_icon": "shield",
    },
    "get_burner_communications": {
        "name": "Burner - Communications",
        "description": "Burner calls and text messages",
        "author": "Josh Hickman (josh@thebinaryhick.blog)",
        "creation_date": "2021-02-05",
        "last_update_date": "2026-07-03",
        "requirements": "None",
        "category": "Burner",
        "notes": "",
        "paths": ('*/com.adhoclabs.burner/databases/burners.db',),
        "output_types": "standard",
        "artifact_icon": "message",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Other Party Number",
                "conversationLabelColumn": "Other Party Contact Name",
                "textColumn": "Message",
                "directionColumn": "Communication Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Communication Time",
                "senderColumn": "Other Party Contact Name",
                "sentMessageStaticLabel": "Local User"
            }
        },
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


def _db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('burners.db'):
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
def get_burner(files_found, report_folder, seeker, wrap_text):
    source_path = _db(files_found)
    rows = _run(source_path, '''
        SELECT date_created, name, phone_number_id, last_updated_date, expiration_date,
        total_minutes, remaining_minutes, total_texts, remaining_texts
        FROM burners
        ORDER BY date_created ASC
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], _ms_to_utc(r[3]), _ms_to_utc(r[4]),
                  r[5], r[6], r[7], r[8]) for r in rows]
    data_headers = (('Number Creation Time', 'datetime'), 'Number Name', 'Number',
                    ('Number Time Last Updated', 'datetime'), ('Number Expiration Time', 'datetime'),
                    'Phone Minutes Allotment', 'Phone Minutes Remaining', 'Text Messages Allotment',
                    'Text Messages Remaining')
    return data_headers, data_list, source_path


@artifact_processor
def get_burner_communications(files_found, report_folder, seeker, wrap_text):
    source_path = _db(files_found)
    rows = _run(source_path, '''
        SELECT messages.date_created, messages.contact_phone_number, contacts.name,
        CASE WHEN messages.direction=1 THEN 'Incoming' WHEN messages.direction=2 THEN 'Outgoing'
        ELSE messages.direction END,
        CASE WHEN messages.message_type=1 THEN 'Call' WHEN messages.message_type=2 THEN 'Text Message'
        ELSE messages.message_type END,
        messages.message, messages.asset_url, messages.duration
        FROM messages
        JOIN contacts ON contacts.phone_number=messages.contact_phone_number
        ORDER BY messages.date_created ASC
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6], r[7]) for r in rows]
    data_headers = (('Communication Time', 'datetime'), 'Other Party Number', 'Other Party Contact Name',
                    'Communication Direction', 'Communication Type', 'Message',
                    'Message Attachment (URL)', 'Approximate Call Duration (minutes)')
    return data_headers, data_list, source_path
