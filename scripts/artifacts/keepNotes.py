__artifacts_v2__ = {
    "keepNotes": {
        "name": "Google Keep Notes",
        "description": "Parses Google Keep Notes",
        "author": "Heather Charpentier",
        "version": "0.0.1",
        "date": "2024-12-02",
        "requirements": "none",
        "category": "Google Keep Notes",
        "notes": "",
        "paths": ('*/data/data/com.google.android.keep/databases/keep.db*'),
        "function": "get_keepNotes"
    }
}

import sqlite3
import datetime
import os
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly

def get_table_names(cursor):
    """Get all table names from database"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [row[0] for row in cursor.fetchall()]

def get_column_names(cursor, table_name):
    """Get all column names from a table"""
    try:
        cursor.execute(f"PRAGMA table_info({table_name});")
        return [row[1] for row in cursor.fetchall()]
    except:
        return []

def get_keepNotes(files_found, report_folder, seeker, wrap_text):
    for file_found in files_found:
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        
        if filename.endswith('keep.db'):
            try:
                db = open_sqlite_db_readonly(file_found)
                cursor = db.cursor()
                
                # Get all available tables
                tables = get_table_names(cursor)
                logfunc(f'Available tables in keep.db: {tables}')
                
                all_rows = []
                data_list = []
                
                # Try different query approaches based on available tables
                query_success = False
                
                # Approach 1: Try original query structure
                if 'text_search_note_content_content' in tables and 'tree_entity' in tables:
                    try:
                        logfunc('Attempting original query structure...')
                        cursor.execute('''
                        SELECT 
                            datetime(tree_entity.time_created/1000, 'unixepoch') AS "Time Created",
                            datetime(tree_entity.time_last_updated/1000, 'unixepoch') AS "Time Last Updated",
                            datetime(tree_entity.user_edited_timestamp/1000, 'unixepoch') AS "User Edited Timestamp",
                            tree_entity.title AS Title,
                            text_search_note_content_content.c0text AS "Text",
                            tree_entity.last_modifier_email AS "Last Modifier Email"
                        FROM text_search_note_content_content
                        INNER JOIN tree_entity ON text_search_note_content_content.docid = tree_entity._id
                        ''')
                        all_rows = cursor.fetchall()
                        query_success = True
                        logfunc('Original query structure successful')
                    except Exception as e:
                        logfunc(f'Original query failed: {str(e)}')
                
                # Approach 2: Try alternative structure if Approach 1 failed
                if not query_success and 'Note' in tables:
                    try:
                        logfunc('Attempting Note table query...')
                        columns = get_column_names(cursor, 'Note')
                        logfunc(f'Note table columns: {columns}')
                        
                        cursor.execute('''
                        SELECT 
                            datetime(Note.create_time/1000, 'unixepoch') AS "Time Created",
                            datetime(Note.update_time/1000, 'unixepoch') AS "Time Last Updated",
                            datetime(Note.user_edited_timestamp/1000, 'unixepoch') AS "User Edited Timestamp",
                            Note.title AS Title,
                            Note.content AS "Text",
                            Note.owner_email AS "Last Modifier Email"
                        FROM Note
                        ''')
                        all_rows = cursor.fetchall()
                        query_success = True
                        logfunc('Note table query successful')
                    except Exception as e:
                        logfunc(f'Note table query failed: {str(e)}')
                
                # Approach 3: Try simple tree_entity table
                if not query_success and 'tree_entity' in tables:
                    try:
                        logfunc('Attempting tree_entity table query...')
                        columns = get_column_names(cursor, 'tree_entity')
                        logfunc(f'tree_entity table columns: {columns}')
                        
                        cursor.execute('''
                        SELECT 
                            datetime(time_created/1000, 'unixepoch') AS "Time Created",
                            datetime(time_last_updated/1000, 'unixepoch') AS "Time Last Updated",
                            datetime(user_edited_timestamp/1000, 'unixepoch') AS "User Edited Timestamp",
                            title AS Title,
                            text AS "Text",
                            last_modifier_email AS "Last Modifier Email"
                        FROM tree_entity
                        WHERE type = 1
                        ''')
                        all_rows = cursor.fetchall()
                        query_success = True
                        logfunc('tree_entity table query successful')
                    except Exception as e:
                        logfunc(f'tree_entity table query failed: {str(e)}')
                
                # Approach 4: Query any table with note data
                if not query_success:
                    try:
                        logfunc('Attempting fallback dynamic query...')
                        # Try to find table with title and content columns
                        for table in tables:
                            if table.startswith('sqlite_'):
                                continue
                            columns = get_column_names(cursor, table)
                            if any(col in columns for col in ['title', 'content', 'text']):
                                logfunc(f'Attempting to query table: {table}')
                                cursor.execute(f'SELECT * FROM {table} LIMIT 1')
                                test_row = cursor.fetchone()
                                if test_row:
                                    logfunc(f'Using table: {table}')
                                    cursor.execute(f'SELECT * FROM {table}')
                                    all_rows = cursor.fetchall()
                                    query_success = True
                                    break
                    except Exception as e:
                        logfunc(f'Fallback query failed: {str(e)}')
                
                # If we got data, process it
                if all_rows and len(all_rows) > 0:
                    data_list = list(all_rows)
                    
                    report = ArtifactHtmlReport('Google Keep Notes')
                    report.start_artifact_report(report_folder, 'Google Keep Notes')
                    report.add_script()
                    
                    # Determine headers based on query result structure
                    if len(data_list[0]) == 6:
                        data_headers = ('Time Created', 'Time Last Updated', 'User Edited Timestamp', 'Title', 'Text', 'Last Modifier Email')
                    else:
                        # Use generic headers if structure is different
                        data_headers = tuple(f'Column_{i}' for i in range(len(data_list[0])))
                        logfunc(f'Using generic headers due to non-standard data structure: {data_headers}')
                    
                    report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                    report.end_artifact_report()
                    
                    tsvname = 'Google Keep Notes'
                    tsv(report_folder, data_headers, data_list, tsvname)
                    
                    tlactivity = 'Google Keep Notes'
                    timeline(report_folder, tlactivity, data_list, data_headers)
                    
                    logfunc(f'Found {len(data_list)} Google Keep Notes')
                else:
                    logfunc('No Google Keep Notes data available or unable to parse database')
                
                db.close()
                
            except Exception as e:
                logfunc(f'[!] Error processing keep.db: {str(e)}')