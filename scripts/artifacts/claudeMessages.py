__artifacts_v2__ = {
    "claudeMessages": {
        "name": "Claude Messages",
        "description": "Parses Claude Messages with some Conversation info",
        "author": "Brandon Baye",
        "creation_date": "2026-07-21",
        "last_updated_date": "2026-08-06",
        "requirements": "none",
        "category": "Claude",
        "notes": "Join used to provide context of conversation when messages cannot be followed in order by conversation"
                 "Timestamps stored as ISO 8601 combined date-time format and converted for LAVA"
                 "Images used in conversations appear to be temporary and the path folder remains empty"
                 "provide file name in context of which image was used"
                 "json each utilized where AI is reaching out for sources"
                 "each reference url is provided in json as well",
        "paths": ('*/com.anthropic.claude/databases/acc_*_claude_cache.db*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation ID",
                "conversationLabelColumn": "Conversation Name",
                "textColumn": "Message",
                "directionColumn": "Sender",
                "directionSentValue": "human",
                "timeColumn": "Message Created Time",
                "senderColumn": "Sender",
                "Attachment": "Image File Name",
            }
        }
    }
}

from scripts.ilapfuncs import (
    artifact_processor,
    get_file_path,
    get_sqlite_db_records,
    convert_human_ts_to_utc
)

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
	JOIN cachedConversations ON cachedConversations.uuid = cachedMessages.conversation_uuid
	'''
    
    records = get_sqlite_db_records(source_path, query)
    for record in records:
        created_at = convert_human_ts_to_utc(
            record[0].replace('T', ' ').replace('Z', '')
        ) if record[0] else None
        
        data_list.append((
            created_at,
            record[1],
            record[2],
            record[3],
            record[4],
            record[5]
        ))
        
    data_headers = (
        ('Message Created Time', 'datetime'),
        'Message',
        'Image File Name',
        'Sender',
        'Conversation Name',
        'Conversation ID'
    )
    
    return data_headers, data_list, source_path