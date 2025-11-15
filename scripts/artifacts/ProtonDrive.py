__artifacts_v2__ = {
    "protondrive_useraccount": {
        "name": "Proton Drive - User Account",
        "description": "Parses Proton Drive User Account Information",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-11-14",
        "last_update_date": "2025-11-14",
        "requirements": "none",
        "category": "Proton Drive",
        "notes": "Tested on version 2.29.1 (Nov 10th, 2025)",
        "paths": ('*/me.proton.android.drive/databases/db-drive'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user"
    },
    "protondrive_fileinfo": {
        "name": "Proton Drive - File Info",
        "description": "Parses Proton Drive File Information",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-11-14",
        "last_update_date": "2025-11-14",
        "requirements": "none",
        "category": "Proton Drive",
        "notes": "Tested on version 2.29.1 (Nov 10th, 2025)",
        "paths": ('*/me.proton.android.drive/databases/db-drive'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "file"
    }   
}

import os
import datetime
from pathlib import Path

from scripts.ilapfuncs import artifact_processor, is_platform_windows, check_in_media, open_sqlite_db_readonly, get_sqlite_db_records, get_file_path, media_to_html, is_platform_windows, logfunc

@artifact_processor
def protondrive_useraccount(files_found, report_folder, seeker, wrap_text):
    data_list = []
    
    def is_sqlite_db(path):
        try:
            with open(path, "rb") as f:
                header = f.read(16)
            return header == b"SQLite format 3\x00"
        except Exception:
            return False

    source_path = None
    for f in files_found:
        p = Path(f)
        if p.name.endswith("-wal") or p.name.endswith("-shm"):
            continue
        if is_sqlite_db(f):
            source_path = str(f)
            break

    if not source_path:
         return (), [], "db-drive not found"
                       
    query = '''
            SELECT
                UserEntity.userId AS 'User ID',
                UserEntity.email AS 'Email Address',
                UserEntity.name AS Username,
                DATETIME((UserEntity.createdAtUTC/1000),'unixepoch') AS 'Created Date (UTC)',
                UserEntity.usedspace/1024/1024 AS 'Used Space (MB)',
                UserEntity.Maxspace/1024/1024 AS 'Max Space (MB)'
            FROM UserEntity;
        '''

    db_records = get_sqlite_db_records(source_path, query)

    for row in db_records:
        user_id         = row[0]  # UserID
        emailaddress    = row[1]  # Email Address
        username        = row[2]  # proton username
        createddate     = row[3]  # account created date
        usedspace       = row[4]  # used space (MB)
        maxspace        = row[5]  # max space (MB)

        data_list.append((user_id,emailaddress,username,createddate,usedspace,maxspace))

    data_headers = ('User ID','Email Address','Username',('Created Date','datetime'),'Used Space (MB)','Max Space (MB)') 
    data_list = get_sqlite_db_records(source_path, query)        
    
    return data_headers, data_list, source_path

@artifact_processor
def protondrive_fileinfo(files_found, report_folder, seeker, wrap_text):

    data_list = []
    
    def is_sqlite_db(path):
        try:
            with open(path, "rb") as f:
                header = f.read(16)
            return header == b"SQLite format 3\x00"
        except Exception:
            return False

    source_path = None
    for f in files_found:
        p = Path(f)

        if p.name.endswith("-wal") or p.name.endswith("-shm"):
            continue
        if is_sqlite_db(f):
            source_path = str(f)
            break

    if not source_path:
        return (), [], "db-drive not found"

    query = '''
        SELECT
            LinkEntity.id,
            LinkEntity.share_id,
            LinkEntity.user_id,
            LinkEntity.parent_id,
            CASE LinkEntity.type
                WHEN 1 THEN 'Folder'
                WHEN 2 THEN 'File'
                ELSE LinkEntity.type
            END AS type,
            LinkEntity.name,
            CASE LinkEntity.state
                WHEN 1 THEN 'Active'
                WHEN 2 THEN 'Trashed'
                ELSE LinkEntity.state
            END AS state,
            datetime(LinkEntity.creation_time, 'unixepoch'),
            datetime(LinkEntity.last_modified, 'unixepoch'),
            datetime(LinkEntity.trashed_time, 'unixepoch'),
            LinkEntity.size,
            LinkEntity.mime_type,
            CASE LinkEntity.is_shared
                WHEN 1 THEN 'YES'
                WHEN 0 THEN 'NO'
                ELSE LinkEntity.is_shared
            END AS is_shared,
            LinkEntity.number_of_accesses
        FROM LinkEntity;
    '''

    db_records = get_sqlite_db_records(source_path, query)

    for row in db_records:
        link_id             = row[0]
        share_id            = row[1]
        user_id             = row[2]
        parent_id           = row[3]
        type_val            = row[4]
        name                = row[5]
        state_val           = row[6]
        creation_time       = row[7]
        last_modified       = row[8]
        trashed_time        = row[9]
        size                = row[10]
        mime_type           = row[11]
        is_shared           = row[12]
        number_of_accesses  = row[13]

        data_list.append((link_id, user_id, type_val, name, state_val, creation_time, last_modified, trashed_time, size, mime_type, is_shared, number_of_accesses))

    data_headers = ('ID','File Owner ID','Type','Name','State',('Creation Time','datetime'),('Last Modified','datetime'),('Trashed Time','datetime'),'Size','MIME Type','Is Shared','Number of Accesses')


    return data_headers, data_list, source_path
