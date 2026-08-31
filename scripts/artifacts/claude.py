__artifacts_v2__ = {
    "claudeAccountInfo": {
        "name": "Claude Account Information",
        "description": "Parses the account information for the Claude app",
        "author": "Brandon Baye",
        "creation_date": "2026-07-23",
        "last_update_date": "2026-08-09",
        "requirements": "none",
        "category": "Claude",
        "notes": "Timestamps stored as ISO 8601 combined date-time format. "
                 "Display name is what the AI addresses the user as. "
                 "Email address is also stored in additional XML, which does not contain any other account info.",
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
        "author": "Brandon Baye",
        "creation_date": "2026-07-22",
        "last_update_date": "2026-08-09",
        "requirements": "none",
        "category": "Claude",
        "notes": "Data stored as json throughout the database and contained relevant information for overall conversations. "
                 "Timestamps stored as ISO 8601 combined date-time format and converted for LAVA.",
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
        "author": "Brandon Baye",
        "creation_date": "2026-07-21",
        "last_update_date": "2026-08-09",
        "requirements": "none",
        "category": "Claude",
        "notes": "Join used to provide context of conversation when messages cannot be followed in order by conversation. "
                 "Timestamps stored as ISO 8601 combined date-time format and converted for LAVA. "
                 "Images used in conversations appear to be temporary and the path folder remains empty; "
                 "the file name is provided for context of which image was used. "
                 "json_each is utilized where the AI is reaching out for sources; "
                 "each reference url is provided in json as well.",
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
        "description": "Parses projects made within Claude",
        "author": "Brandon Baye",
        "creation_date": "2026-07-24",
        "last_update_date": "2026-08-09",
        "requirements": "none",
        "category": "Claude",
        "notes": "Projects can include document and file uploads to each separate project. "
                 "The user can add conversations to a project to keep context for usage. "
                 "Project creator is stored as the full name in the profile. "
                 "Timestamps are ISO 8601 combined date-time format.",
        "paths": ('*/com.anthropic.claude/databases/acc_*_claude_cache.db*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "s20fe_a13": "1 row",
            "hc_pixel8pro_a17": "0 rows",
        },
    }
}

from scripts.ilapfuncs import (
    artifact_processor,
    get_file_path,
    get_sqlite_db_records,
    json,
    convert_human_ts_to_utc
)

@artifact_processor
def claudeAccountInfo(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'cache.json')
    data_list = []
    
    with open(source_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    account = data['response']['account']
    
    ts = account['created_at']
    ts = ts.replace('T', ' ').replace('Z', '')
    created_at = convert_human_ts_to_utc(ts)
    
    ts = account['updated_at']
    ts = ts.replace('T', ' ').replace('Z', '')
    updated_at = convert_human_ts_to_utc(ts)
    
    full_name = account['full_name']
    display_name = account['display_name']
    email = account['email_address']
    
        
    data_list.append((
        created_at,
        updated_at,
        full_name,
        display_name,
        email,
    ))
        
    data_headers = (
        ('Account Created Time', 'datetime'),
        ('Account Updated Time', 'datetime'),
        'Full Name',
        'Display Name',
        'Email Address',
    )
    
    return data_headers, data_list, source_path
    
@artifact_processor
def claudeConversations(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, '*_claude_cache.db')
    data_list = []
    
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
            END AS 'Incognito Conversation',
        CASE json_extract(cachedConversations.conversation_json, '$.is_starred')
            WHEN 0 THEN 'False'
            WHEN 1 THEN 'True'
            ELSE 'Unknown'
            END AS 'Conversation Starred'
    FROM cachedConversations
    '''
    
    records = get_sqlite_db_records(source_path, query)
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
            record[6]
        ))
        
    data_headers = (
        ('Conversation Start Time', 'datetime'),
        ('Conversation Updated Time', 'datetime'),
        'Conversation ID',
        'Conversation Name',
        'Model',
        'Incognito Conversation',
        'Conversation Starred'
    )
    
    return data_headers, data_list, source_path
    
@artifact_processor
def claudeMessages(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, '*_claude_cache.db')
    data_list = []
    
    query = '''
	SELECT
        json_extract(cachedMessages.message_json, '$.created_at') as 'Message Created Time',
		(		
			SELECT group_concat(json_extract(je.value, '$.text'), ' ')
			FROM json_each(cachedMessages.message_json, '$.content') je
			WHERE json_extract(je.value, '$.type') = 'text'
		) as 'Message',
        json_extract(CachedMessages.message_json, '$.files[0].file_name') as 'Image File Name',
        json_extract(cachedMessages.message_json, '$.sender') as 'Sender',
        json_extract(cachedConversations.conversation_json, '$.name') as 'Conversation Name',
        cachedConversations.uuid AS 'Conversation ID'
	FROM cachedMessages
	LEFT JOIN cachedConversations ON cachedConversations.uuid = cachedMessages.conversation_uuid
	'''
    
    records = get_sqlite_db_records(source_path, query)
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
        ))
        
    data_headers = (
        ('Message Created Time', 'datetime'),
        'Sender',
        'Conversation Name',
        'Message',
        'Image File Name',
        'Conversation ID',
    )
    
    return data_headers, data_list, source_path

@artifact_processor
def claudeProjects(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, '*_claude_cache.db')
    data_list = []
    
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
    
    records = get_sqlite_db_records(source_path, query)
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
            record[7]
        ))
        
    data_headers = (
        ('Project Created Time', 'datetime'),
        ('Project Updated Time', 'datetime'),
        'Project Name',
        'Project Description',
        'Project Creator',
        'Project Starred',
        'Number of Documents',
        'Number of Files'
    )
    
    return data_headers, data_list, source_path
