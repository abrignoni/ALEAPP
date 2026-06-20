# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_teams": {
        "name": "Teams - Messages",
        "description": "",
        "author": "",
        "creation_date": "2021-04-29",
        "last_update_date": "2021-04-29",
        "requirements": "none",
        "category": "Teams",
        "notes": "",
        "paths": ('*/com.microsoft.teams/databases/SkypeTeams.db*',),
        "output_types": "standard",
        "artifact_icon": "message-square",
    },
    "get_teams_users": {
        "name": "Teams - Users",
        "description": "",
        "author": "",
        "creation_date": "2021-04-29",
        "last_update_date": "2021-04-29",
        "requirements": "none",
        "category": "Teams",
        "notes": "",
        "paths": ('*/com.microsoft.teams/databases/SkypeTeams.db*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "users",
    },
    "get_teams_calllog": {
        "name": "Teams - Call Log",
        "description": "",
        "author": "",
        "creation_date": "2021-04-29",
        "last_update_date": "2021-04-29",
        "requirements": "none",
        "category": "Teams",
        "notes": "",
        "paths": ('*/com.microsoft.teams/databases/SkypeTeams.db*',),
        "output_types": "standard",
        "artifact_icon": "phone-call",
    },
    "get_teams_activity": {
        "name": "Teams - Activity Feed",
        "description": "",
        "author": "",
        "creation_date": "2021-04-29",
        "last_update_date": "2021-04-29",
        "requirements": "none",
        "category": "Teams",
        "notes": "",
        "paths": ('*/com.microsoft.teams/databases/SkypeTeams.db*',),
        "output_types": "standard",
        "artifact_icon": "activity",
    },
    "get_teams_fileinfo": {
        "name": "Teams - File Info",
        "description": "",
        "author": "",
        "creation_date": "2021-04-29",
        "last_update_date": "2021-04-29",
        "requirements": "none",
        "category": "Teams",
        "notes": "",
        "paths": ('*/com.microsoft.teams/databases/SkypeTeams.db*',),
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


def _teams_db(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('SkypeTeams.db'):
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
    except Exception as e:
        logfunc(str(e))
        rows = []
    db.close()
    return rows


@artifact_processor
def get_teams(files_found, report_folder, seeker, wrap_text):
    source_path = _teams_db(files_found)
    rows = _run(source_path, '''
        SELECT arrivalTime, userDisplayName, content, displayName, deleteTime,
        Message.conversationId, messageId
        FROM Message
        left join Conversation on Message.conversationId = Conversation.conversationId
        ORDER BY Message.conversationId, arrivalTime
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], _ms_to_utc(r[4]), r[5], r[6]) for r in rows]
    data_headers = (('Timestamp', 'datetime'), 'User Display Name', 'Content', 'Topic Name', ('Delete Time', 'datetime'), 'Conversation ID', 'Message ID')
    return data_headers, data_list, source_path


@artifact_processor
def get_teams_users(files_found, report_folder, seeker, wrap_text):
    source_path = _teams_db(files_found)
    rows = _run(source_path, '''
        SELECT lastSyncTime, givenName, surname, displayName, email, secondaryEmail, alternativeEmail,
        telephoneNumber, homeNumber, accountEnabled, type, userType, isSkypeTeamsUser, isPrivateChatEnabled
        from User
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13]) for r in rows]
    data_headers = (('Last Sync', 'datetime'), 'Given Name', 'Surname', 'Display Name', 'Email', 'Secondary Email', 'Alt. Email', ('Telephone Number', 'phonenumber'), ('Home Number', 'phonenumber'), 'Account Enabled?', 'Type', 'User Type', 'Is Teams User?', 'Is Private Chat Enabled?')
    return data_headers, data_list, source_path


@artifact_processor
def get_teams_calllog(files_found, report_folder, seeker, wrap_text):
    source_path = _teams_db(files_found)
    rows = _run(source_path, '''
        SELECT
        json_extract(attributeValue, '$.connectTimeMillis'),
        json_extract(attributeValue, '$.endTimeMillis'),
        json_extract(attributeValue, '$.callState'),
        json_extract(attributeValue, '$.callType'),
        json_extract(attributeValue, '$.originatorDisplayName'),
        json_extract(attributeValue, '$.callDirection'),
        User.givenName,
        json_extract(attributeValue, '$.sessionType')
        from MessagePropertyAttribute, User
        where propertyId = 'CallLog' and json_extract(attributeValue, '$.target') = User.mri
    ''')
    data_list = [(_ms_to_utc(r[0]), _ms_to_utc(r[1]), r[2], r[3], r[4], r[5], r[6], r[7]) for r in rows]
    data_headers = (('Connect Time', 'datetime'), ('End Time', 'datetime'), 'Call State', 'Call Type', 'Originator', 'Call Direction', 'Target Participant Name', 'Session Type')
    return data_headers, data_list, source_path


@artifact_processor
def get_teams_activity(files_found, report_folder, seeker, wrap_text):
    source_path = _teams_db(files_found)
    rows = _run(source_path, '''
        SELECT activityTimestamp, sourceUserImDisplayName, messagePreview, activityType, activitySubtype, isRead
        FROM ActivityFeed
    ''')
    data_list = [(_ms_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5]) for r in rows]
    data_headers = (('Timestamp', 'datetime'), 'Display Name', 'Message Preview', 'Activity Type', 'Activity Subtype', 'Is read?')
    return data_headers, data_list, source_path


@artifact_processor
def get_teams_fileinfo(files_found, report_folder, seeker, wrap_text):
    source_path = _teams_db(files_found)
    rows = _run(source_path, '''
        SELECT lastModifiedTime, fileName, type, objectUrl, isFolder, lastModifiedBy
        FROM FileInfo
    ''')
    data_list = []
    for r in rows:
        mtime = r[0].replace('T', ' ') if r[0] else ''
        data_list.append((mtime, r[1], r[2], r[3], r[4], r[5]))
    data_headers = ('Timestamp', 'File Name', 'Type', 'Object URL', 'Is Folder?', 'Last Modified By')
    return data_headers, data_list, source_path
