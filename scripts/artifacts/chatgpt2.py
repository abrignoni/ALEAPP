__artifacts_v2__ = {
    "chatgpt2": {
        "name": "ChatGPT",
        "description": "Android ChatGPT conversations",
        "author": "Alexis Brignoni",
        "version": "0.0.1",
        "date": "2025-07-08",
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
            cursor.execute('''
            SELECT messageId,
            chunkIndex, 
            chunk 
            FROM DBMessageChunk
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
                #print(f"Message ID: {message_id}\nJSON:\n{json.dumps(message, indent=2)}")
                
                creationdate = message['content'].get('created_date')
                if creationdate is not None:
                    try:
                        cdt = datetime.strptime(creationdate, "%Y-%m-%dT%H:%M:%S.%fZ")
                    except:
                        cdt = datetime.strptime(creationdate, "%Y-%m-%dT%H:%M:%S:%fZ")
                    cdt = cdt.replace(tzinfo=timezone.utc)
                else:
                    cdt = creationdate
                    
                modificatondate = message['content']['modification_date']
                try:
                    mdt = datetime.strptime(modificatondate, "%Y-%m-%dT%H:%M:%S.%fZ")
                except:
                    mdt = datetime.strptime(modificatondate, "%Y-%m-%dT%H:%M:%S:%fZ")
                mdt = mdt.replace(tzinfo=timezone.utc)
                
                chunkdata = message['content']['content'].get('content')
                if chunkdata == None:
                    chunkdata = message['content']['content']
            
                refereces = message['content']['content'].get('references')
                
                data_list.append((mdt,cdt,chunkdata,refereces))
                
    data_headers = (('Modified Time', 'datetime'), ('Creation Time', 'datetime'), 'Content', 'Content References')
    
    return data_headers, data_list, source