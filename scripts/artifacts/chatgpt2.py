__artifacts_v2__ = {
    "chatgpt2": {
        "name": "ChatGPT",
        "description": "Android ChatGPT conversations",
        "author": "Alexis Brignoni",
        "version": "0.0.2",
        "creation_date": "2025-07-08",
        "last_updated_date": "2025-09-09",
        "requirements": "none",
        "category": "ChatGPT",
        "notes": "",
        "paths": ('*/data/data/com.openai.chatgpt/databases/*conversations.db*'),
        "html_columns": ['Content'],
        "output_types": "standard",
        "function": "get_chatpgt2",
        "artifact_icon": "loader",
    }
}

import sqlite3
import textwrap
import json
from datetime import datetime, timezone
from collections import defaultdict
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly

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

                chunkdata = message['content']['content'].get('content')
                if chunkdata == None:
                    chunkdata = message['content']['content']

                references = message['content']['content'].get('references')

                # Get conversation title
                conversation_id = message['content'].get('conversation_id')
                conversation_title = conversations.get(conversation_id, 'Unknown Conversation')

                data_list.append((mdt, cdt, conversation_title, chunkdata, references, message_id, conversation_id))

    data_headers = (('Modified Time', 'datetime'), ('Creation Time', 'datetime'), 'Conversation Title', 'Content', 'Content References','Message ID','Conversation ID')

    return data_headers, data_list, source
