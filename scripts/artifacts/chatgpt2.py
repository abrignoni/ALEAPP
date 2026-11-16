# pylint: disable=E0606,E1120,E1123,W0611,W0702,W0718
__artifacts_v2__ = {
    "get_chatpgt2": {
        "name": "ChatGPT - Conversations",
        "description": "Messages rebuilt from the DBMessageChunk table of the ChatGPT conversations database, each with its conversation title",
        "author": "@AlexisBrignoni, @Rugikex, Claude",
        "creation_date": "2025-07-08",
        "last_update_date": "2026-11-11",
        "requirements": "none",
        "category": "ChatGPT",
        "notes": "Role, Creation Time, Modified Time and Conversation ID are read from the top "
                 "level of the message JSON, and Content is the message's content.content text. "
                 "Role falls back to author.role when the top-level key is missing; that path was "
                 "not exercised on anne_a15. On anne_a15 Role held User, Assistant, System and "
                 "ImageGen; the LAVA conversation view groups rows by Conversation ID and shows a "
                 "row as sent when Role is 'User'. Creation Time is empty on 3 of 12 rows and "
                 "Modified Time on 2, because those messages carry no created_date or "
                 "modification_date key. Content is empty on 4 System rows, where content.content "
                 "is an empty string. A message with no content.content key shows its whole "
                 "content object as JSON: on anne_a15 one Assistant row whose content holds only a "
                 "type value ending in UnsupportedContent, and one ImageGen row whose content.parts "
                 "holds an image asset_pointer, which this module does not resolve to a local "
                 "file. Content References is the message's content.references value, as JSON; it "
                 "held an empty list on 9 rows and had no key on 3, so a populated list is "
                 "unexercised. The top-level content_references key is not read. Conversation "
                 "Title reads 'Unknown Conversation' when the conversation record or its title is "
                 "missing; that did not occur on anne_a15.",
        "paths": ('*/data/com.openai.chatgpt/databases/*conversations.db*'),
        "html_columns": ['Content'],
        "output_types": "standard",
        "artifact_icon": "loader",
        "sample_data": {
            "anne_a15": "Android 15 | com.openai.chatgpt vc 2525902 | 12 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation ID",
                "conversationLabelColumn": "Conversation Title",
                "textColumn": "Content",
                "directionColumn": "Role",
                "directionSentValue": "User",
                "timeColumn": "Creation Time",
                "senderColumn": "Role",
            }
        },
    }
}

import sqlite3
import json
from datetime import datetime, timezone
from collections import defaultdict
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly
from scripts.html_safe import safe_source


def as_text(value):
    """Text values unchanged; objects and lists as the JSON the chunk stored."""
    if value is None:
        return ''
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


@artifact_processor
def get_chatpgt2(context):
    files_found = context.get_files_found()

    data_list = []
    # The HTML report shows Content escaped; LAVA and the TSV keep the text unescaped
    data_list_html = []

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
                creationdate = message.get('created_date','')
                if creationdate:
                    try:
                        cdt = datetime.strptime(creationdate, "%Y-%m-%dT%H:%M:%S.%fZ")
                    except:
                        cdt = datetime.strptime(creationdate, "%Y-%m-%dT%H:%M:%SZ")
                    cdt = cdt.replace(tzinfo=timezone.utc)
                else:
                    cdt = creationdate

                modificationdate = message.get('modification_date','')
                if modificationdate:
                    try:
                        mdt = datetime.strptime(modificationdate, "%Y-%m-%dT%H:%M:%S.%fZ")
                    except:
                        mdt = datetime.strptime(modificationdate, "%Y-%m-%dT%H:%M:%SZ")
                    mdt = mdt.replace(tzinfo=timezone.utc)

                # The message text is content.content. A message with no text
                # field (content holding only parts or a type) keeps the object.
                content = message.get('content')
                if isinstance(content, dict):
                    chunkdata = content.get('content')
                    if chunkdata is None:
                        chunkdata = content
                    references = content.get('references')
                else:
                    chunkdata = content
                    references = ''

                # Get conversation title
                conversation_id = message.get('conversation_id')
                conversation_title = conversations.get(conversation_id, 'Unknown Conversation')

                role = message.get('role')
                if role is None and isinstance(message.get('author'), dict):
                    role = message['author'].get('role')
                role = role or ''
                text = as_text(chunkdata)
                references = as_text(references)

                data_list.append((cdt, mdt, role, conversation_title, text, references, message_id, conversation_id))
                data_list_html.append((cdt, mdt, role, conversation_title, safe_source(text), references, message_id, conversation_id))

    data_headers = (('Creation Time', 'datetime'), ('Modified Time', 'datetime'), 'Role', 'Conversation Title', 'Content', 'Content References', 'Message ID', 'Conversation ID')

    return data_headers, (data_list, data_list_html), source
