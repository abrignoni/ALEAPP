# pylint: disable=E0606,E1120,E1123,W0611,W0613,W0702,W0718
__artifacts_v2__ = {
    "get_chatpgt2": {
        "name": "ChatGPT - Conversations",
        "description": "Android ChatGPT conversations",
        "author": "Alexis Brignoni",
        "creation_date": "2025-07-08",
        "last_update_date": "2026-07-10",
        "requirements": "none",
        "category": "ChatGPT",
        "notes": "",
        "paths": ('*/data/com.openai.chatgpt/databases/*conversations.db*'),
        "html_columns": ['Content'],
        "output_types": "standard",
        "artifact_icon": "loader",
        "sample_data": {
            "anne_a15": "Android 15 | com.openai.chatgpt vc 2525902 | 12 rows",
        },
    }
}

import sqlite3
import textwrap
import json
from datetime import datetime, timezone
from collections import defaultdict
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly
from scripts.html_safe import safe_source

@artifact_processor
def get_chatpgt2(files_found, report_folder, seeker, wrap_text):

    data_list = []

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('conversations.db'):
            source = file_found
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()

            # Fetch conversations
            cursor.execute('''
            SELECT id, conversation FROM DBConversation
            ''')
            conversations = {}
            for row in cursor.fetchall():
                conversation_id = row[0]
                conversation_data = json.loads(row[1])
                conversations[conversation_id] = conversation_data.get('title', 'Unknown Conversation')

            # Fetch message chunks
            cursor.execute('''
            SELECT messageId, chunkIndex, chunk FROM DBMessageChunk
            ''')
            rows = cursor.fetchall()

            # Group and sort chunks by messageId
            message_chunks = defaultdict(list)
            for message_id, chunk_index, chunk_blob in rows:
                try:
                    # Decode BLOB to text (assuming UTF-8 encoding)
                    chunk_str = chunk_blob.decode('utf-8')
                    message_chunks[message_id].append((chunk_index, chunk_str))
                except Exception as e:
                    print(f"Decoding error for message {message_id}, chunk {chunk_index}: {e}")

            # Reconstruct and parse JSON
            reconstructed_messages = {}

            for message_id, chunks in message_chunks.items():
                # Sort by chunkIndex
                sorted_chunks = sorted(chunks, key=lambda x: x[0])
                # Concatenate chunk strings
                full_json_str = ''.join(chunk for _, chunk in sorted_chunks)

                try:
                    reconstructed_messages[message_id] = json.loads(full_json_str)
                except json.JSONDecodeError as e:
                    print(f"JSON parse error for message {message_id}: {e}")
                    reconstructed_messages[message_id] = full_json_str  # Or skip/log/etc.

            # Print one result as a check
            for message_id, message in list(reconstructed_messages.items()):
                if not isinstance(message, dict) or not isinstance(message.get('content'), dict):
                    logfunc(f'Skipping ChatGPT message {message_id}: unrecognized message structure')
                    continue
                cdt = ''
                mdt = ''
                creationdate = message['content'].get('created_date','')
                if creationdate:
                    try:
                        cdt = datetime.strptime(creationdate, "%Y-%m-%dT%H:%M:%S.%fZ")
                    except:
                        cdt = datetime.strptime(creationdate, "%Y-%m-%dT%H:%M:%SZ")
                    cdt = cdt.replace(tzinfo=timezone.utc)
                else:
                    cdt = creationdate

                modificationdate = message['content'].get('modification_date','')
                if modificationdate:
                    try:
                        mdt = datetime.strptime(modificationdate, "%Y-%m-%dT%H:%M:%S.%fZ")
                    except:
                        mdt = datetime.strptime(modificationdate, "%Y-%m-%dT%H:%M:%SZ")
                    mdt = mdt.replace(tzinfo=timezone.utc)

                # The nested content value is a dict in most messages but can
                # also be a plain string (e.g. some tool/voice messages)
                content = message['content'].get('content')
                if isinstance(content, dict):
                    chunkdata = content.get('content')
                    if chunkdata == None:
                        chunkdata = content
                    references = content.get('references')
                else:
                    chunkdata = content
                    references = ''

                # Get conversation title
                conversation_id = message['content'].get('conversation_id')
                conversation_title = conversations.get(conversation_id, 'Unknown Conversation')

                data_list.append((mdt, cdt, conversation_title, safe_source(chunkdata), references, message_id, conversation_id))

    data_headers = (('Modified Time', 'datetime'), ('Creation Time', 'datetime'), 'Conversation Title', 'Content', 'Content References','Message ID','Conversation ID')

    return data_headers, data_list, source
