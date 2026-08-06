__artifacts_v2__ = {
    "claudeConversations": {
        "name": "Claude Conversations",
        "description": "Parses Claude Conversations",
        "author": "Brandon Baye",
        "creation_date": "2026-07-22",
        "last_updated_date": "2026-08-06",
        "requirements": "none",
        "category": "Claude",
        "notes": "Data stored as json throughout the database and contained relevant information for overall conversations"
                 "timestamps stored as ISO 8601 combined date-time format and converted for LAVA",
        "paths": ('*/com.anthropic.claude/databases/acc_*_claude_cache.db*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
    }
}

from scripts.ilapfuncs import (
    artifact_processor,
    get_file_path,
    get_sqlite_db_records,
    convert_human_ts_to_utc
)

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