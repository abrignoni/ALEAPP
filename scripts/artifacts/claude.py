__artifacts_v2__ = {
    "claudeAccountInfo": {
        "name": "Claude Account Information",
        "description": "Account information from each cache.json matched for the Claude app, one row per file",
        "author": "Brandon Baye",
        "creation_date": "2026-07-23",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "Claude",
        "notes": "Timestamps stored as ISO 8601 combined date-time format. "
                 "Display Name is reported as stored. An XML file in the app container also "
                 "holds the email address; that file is not read by this artifact. Every "
                 "matched cache.json is read and Source File names the file a row came from. "
                 "The two recorded samples each returned one row; reading more than one file "
                 "was exercised with constructed input only.",
        "paths": ('*/com.anthropic.claude/cache/app_start/acc_*/org_*/cache.json'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "s20fe_a13": "1 row",
            "hc_pixel8pro_a17": "1 row",
        },
    },

    "claudeConversations": {
        "name": "Claude Conversations",
        "description": "Parses Claude Conversations",
        "author": "Brandon Baye, @AlexisBrignoni, Codex",
        "creation_date": "2026-07-22",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "Claude",
        "notes": "Each cachedConversations row holds a JSON object. Conversation Start Time is "
                 "its created_at value, is_temporary (existing rendering) reports its is_temporary value and "
                 "Conversation Starred its is_starred value; a value other than 0 or 1 is shown "
                 "as Unknown. What the app does with is_temporary is not established here. "
                 "Timestamps stored as ISO 8601 combined date-time format and converted for LAVA. "
                 "Every matched cache database is read and Source File names the database a "
                 "row came from.",
        "paths": ('*/com.anthropic.claude/databases/acc_*_claude_cache.db*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "s20fe_a13": "14 rows",
            "hc_pixel8pro_a17": "1 row",
        },
    },

    "claudeMessages": {
        "name": "Claude Messages",
        "description": "Parses Claude Messages with some Conversation info",
        "author": "Brandon Baye, @AlexisBrignoni, Codex",
        "creation_date": "2026-07-21",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "Claude",
        "notes": "Each message is joined to its conversation on the conversation uuid so the "
                 "conversation name appears on the row. Timestamps stored as ISO 8601 combined "
                 "date-time format and converted for LAVA. First Stored File Name is the first file name "
                 "in the message's files list, whatever its type, as stored; later files are not "
                 "reported. The module does not look for the file itself, so whether it is in the "
                 "extraction is not established. Message is the text of the content items of type "
                 "text, joined with spaces; json_each is used to read them and no reference URL "
                 "is reported. Every matched cache database is read and Source File names the "
                 "database a row came from.",
        "paths": ('*/com.anthropic.claude/databases/acc_*_claude_cache.db*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "s20fe_a13": "78 rows",
            "hc_pixel8pro_a17": "8 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation ID",
                "conversationLabelColumn": "Conversation Name",
                "textColumn": "Message",
                "directionColumn": "Sender",
                "directionSentValue": "human",
                "timeColumn": "Message Created Time",
                "senderColumn": "Sender",
            }
        }
    },

    "claudeProjects": {
        "name": "Claude Projects",
        "description": "Parses the project records held in the Claude app's cache database",
        "author": "Brandon Baye",
        "creation_date": "2026-07-24",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "Claude",
        "notes": "Project Creator is the creator.full_name value of the project record, as "
                 "stored. "
                 "Timestamps are ISO 8601 combined date-time format. Every matched cache "
                 "database is read and Source File names the database a row came from.",
        "paths": ('*/com.anthropic.claude/databases/acc_*_claude_cache.db*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "s20fe_a13": "1 row",
            "hc_pixel8pro_a17": "0 rows",
        },
    }
}

import os

from scripts.ilapfuncs import (
    artifact_processor,
    get_sqlite_db_records,
    json,
    logfunc,
    convert_human_ts_to_utc
)
from scripts.artifacts.storagePathViews import unique_files


def _cache_files(context, wanted):
    """Every matched file of one kind, with duplicate storage views of a file collapsed."""
    found = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        name = os.path.basename(file_found)
        if wanted == 'cache.json' and name == 'cache.json':
            found.append(file_found)
        elif wanted == 'db' and name.endswith('_claude_cache.db'):
            found.append(file_found)
    return found

@artifact_processor
def claudeAccountInfo(context):
    data_list = []
    source_paths = []

    for file_found in _cache_files(context, 'cache.json'):
        relative = context.get_relative_path(file_found)
        try:
            with open(file_found, 'r', encoding='utf-8') as f:
                data = json.load(f)
            account = data['response']['account']
        except (OSError, ValueError, KeyError, TypeError) as error:
            logfunc(f'Claude account cache not read: {relative}: {error}')
            continue
        source_paths.append(relative)

        ts = account.get('created_at')
        created_at = convert_human_ts_to_utc(
            ts.replace('T', ' ').replace('Z', '')) if ts else None

        ts = account.get('updated_at')
        updated_at = convert_human_ts_to_utc(
            ts.replace('T', ' ').replace('Z', '')) if ts else None

        data_list.append((
            created_at,
            updated_at,
            account.get('full_name'),
            account.get('display_name'),
            account.get('email_address'),
            relative,
        ))

    data_headers = (
        ('Account Created Time', 'datetime'),
        ('Account Updated Time', 'datetime'),
        'Full Name',
        'Display Name',
        'Email Address',
        'Source File',
    )

    return data_headers, data_list, '\n'.join(source_paths)
    
@artifact_processor
def claudeConversations(context):
    data_list = []
    source_paths = []
    
    query = '''
    SELECT
        json_extract(cachedConversations.conversation_json, '$.created_at') as 'Conversation Start Time',
        json_extract(cachedConversations.conversation_json, '$.updated_at') as 'Conversation Updated Time',
        cachedConversations.uuid AS 'Conversation ID',
        json_extract(cachedConversations.conversation_json, '$.name') as 'Conversation Name',
        json_extract(cachedConversations.conversation_json, '$.model') as 'Model',
        CASE json_extract(cachedConversations.conversation_json, '$.is_temporary')
            WHEN 0 THEN 'False'
            WHEN 1 THEN 'True'
            ELSE 'Unknown'
            END AS 'is_temporary',
        CASE json_extract(cachedConversations.conversation_json, '$.is_starred')
            WHEN 0 THEN 'False'
            WHEN 1 THEN 'True'
            ELSE 'Unknown'
            END AS 'Conversation Starred'
    FROM cachedConversations
    '''
    
    records = []
    for db_path in _cache_files(context, 'db'):
        relative = context.get_relative_path(db_path)
        source_paths.append(relative)
        for db_record in get_sqlite_db_records(db_path, query):
            records.append((*db_record, relative))
    for record in records:
        created_at = convert_human_ts_to_utc(
            record[0].replace('T', ' ').replace('Z', '')
            ) if record[0] else None
            
        updated_at = convert_human_ts_to_utc(
            record[1].replace('T', ' ').replace('Z', '')
            ) if record[1] else None
        
        data_list.append((
            created_at,
            updated_at,
            record[2],
            record[3],
            record[4],
            record[5],
            record[6],
            record[-1]
        ))
        
    data_headers = (
        ('Conversation Start Time', 'datetime'),
        ('Conversation Updated Time', 'datetime'),
        'Conversation ID',
        'Conversation Name',
        'Model',
        'is_temporary (existing rendering)',
        'Conversation Starred',
        'Source File'
    )
    
    return data_headers, data_list, '\n'.join(source_paths)
    
@artifact_processor
def claudeMessages(context):
    data_list = []
    source_paths = []
    
    query = '''
	SELECT
        json_extract(cachedMessages.message_json, '$.created_at') as 'Message Created Time',
		(		
			SELECT group_concat(json_extract(je.value, '$.text'), ' ')
			FROM json_each(cachedMessages.message_json, '$.content') je
			WHERE json_extract(je.value, '$.type') = 'text'
		) as 'Message',
        json_extract(CachedMessages.message_json, '$.files[0].file_name') as 'First Stored File Name',
        json_extract(cachedMessages.message_json, '$.sender') as 'Sender',
        json_extract(cachedConversations.conversation_json, '$.name') as 'Conversation Name',
        cachedConversations.uuid AS 'Conversation ID'
	FROM cachedMessages
	LEFT JOIN cachedConversations ON cachedConversations.uuid = cachedMessages.conversation_uuid
	'''
    
    records = []
    for db_path in _cache_files(context, 'db'):
        relative = context.get_relative_path(db_path)
        source_paths.append(relative)
        for db_record in get_sqlite_db_records(db_path, query):
            records.append((*db_record, relative))
    for record in records:
        created_at = convert_human_ts_to_utc(
            record[0].replace('T', ' ').replace('Z', '')
        ) if record[0] else None
        
        data_list.append((
            created_at,
            record[3],
            record[4],
            record[1],
            record[2],
            record[5],
            record[-1],
        ))
        
    data_headers = (
        ('Message Created Time', 'datetime'),
        'Sender',
        'Conversation Name',
        'Message',
        'First Stored File Name',
        'Conversation ID',
        'Source File',
    )
    
    return data_headers, data_list, '\n'.join(source_paths)

@artifact_processor
def claudeProjects(context):
    data_list = []
    source_paths = []
    
    query = '''
    SELECT
        json_extract(cachedProjects.project_json, '$.created_at') as 'Project Created Time',
        json_extract(cachedProjects.project_json, '$.updated_at') as 'Project Updated Time',
        json_extract(cachedProjects.project_json, '$.name') as 'Project Name',
        json_extract(cachedProjects.project_json, '$.description') as 'Project Description',
        json_extract(cachedProjects.project_json, '$.creator.full_name') as 'Project Creator',
        CASE json_extract(cachedProjects.project_json, '$.is_starred') 
            WHEN 0 THEN 'False'
            WHEN 1 THEN 'True'
            ELSE 'Unknown'
        END AS 'Project Starred',
        json_extract(cachedProjects.project_json, '$.docs_count') as 'Number of Documents',
        json_extract(cachedProjects.project_json, '$.files_count') as 'Number of Files'
    FROM cachedProjects
    '''
    
    records = []
    for db_path in _cache_files(context, 'db'):
        relative = context.get_relative_path(db_path)
        source_paths.append(relative)
        for db_record in get_sqlite_db_records(db_path, query):
            records.append((*db_record, relative))
    for record in records:
        created_at = convert_human_ts_to_utc(
            record[0].replace('T', ' ').replace('Z', '')
            ) if record[0] else None
            
        updated_at = convert_human_ts_to_utc(
            record[1].replace('T', ' ').replace('Z', '')
            ) if record[1] else None
        
        data_list.append((
            created_at,
            updated_at,
            record[2],
            record[3],
            record[4],
            record[5],
            record[6],
            record[7],
            record[-1]
        ))
        
    data_headers = (
        ('Project Created Time', 'datetime'),
        ('Project Updated Time', 'datetime'),
        'Project Name',
        'Project Description',
        'Project Creator',
        'Project Starred',
        'Number of Documents',
        'Number of Files',
        'Source File'
    )
    
    return data_headers, data_list, '\n'.join(source_paths)
