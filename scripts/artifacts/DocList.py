__artifacts_v2__ = {
    "get_DocList": {
        "name": "DocList",
        "description": "Parses the EntryView rows of the Google Drive DocList.db database (title, owner, kind, creation, last modified and last opened times, URIs, MD5 and size). Reads distinct matched main DocList.db and reports the row source. Missing projected columns in an otherwise compatible EntryView are blank; query/open failures are logged by source and do not stop other databases.",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2020-12-21",
        "last_update_date": "2026-10-05",
        "requirements": "none",
        "category": "Google Drive",
        "notes": "Original parser: Kevin Pagano (@stark4n6). The inspected Anne and Pixel8Pro EntryView schemas contain no rows and omit owner, lastModifierAccountAlias, lastModifierAccountName and shareableUri; these columns are blank rather than mapped to unrelated fields. A valid empty view is not a query error.",
        "paths": ('*/com.google.android.apps.docs/databases/DocList.db*',),
        "output_types": "standard",
        "artifact_icon": "file",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.apps.docs vc 214164863 | 0 rows",
            "galaxys10_a10": "Android 10 | com.google.android.apps.docs vc 211210540 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.apps.docs vc 214512167 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.apps.docs vc 214173331 | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.apps.docs vc 213440084 | 0 rows",
            "samsunga53_a14": "Android 14 | com.google.android.apps.docs vc 214258185 | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.apps.docs vc 214207580 | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.apps.docs vc 213692448 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.apps.docs vc 213183212 | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.apps.docs vc 213806576 | 0 rows",
        },
    }
}

from pathlib import Path
import sqlite3

from scripts.ilapfuncs import (artifact_processor, open_sqlite_db_readonly, convert_human_ts_to_utc,
                              null_absent_columns, logfunc)
from scripts.artifacts.storagePathViews import unique_files


@artifact_processor
def get_DocList(context):
    data_list = []
    source_paths = []
    query = '''
        select
            case creationTime
                when 0 then ''
                else datetime("creationTime"/1000, 'unixepoch')
            end as creationTime,
            title,
            owner,
            case lastModifiedTime
                when 0 then ''
                else datetime("lastModifiedTime"/1000, 'unixepoch')
            end as lastModifiedTime,
            case lastOpenedTime
                when 0 then ''
                else datetime("lastOpenedTime"/1000, 'unixepoch')
            end as lastOpenedTime,
            lastModifierAccountAlias,
            lastModifierAccountName,
            kind,
            shareableUri,
            htmlUri,
            md5Checksum,
            size
        from EntryView
        '''
    for source_path in unique_files(context):
        if Path(source_path).name != 'DocList.db':
            continue
        relative = context.get_relative_path(source_path)
        source_paths.append(relative)
        db = None
        try:
            db = open_sqlite_db_readonly(source_path)
            if db is None:
                logfunc(f'DocList database unavailable: {relative}')
                continue
            rows = db.execute(null_absent_columns(source_path, query)).fetchall()
        except sqlite3.Error as error:
            logfunc(f'DocList query error for {relative}: {error}')
            continue
        finally:
            if db is not None:
                db.close()
        for row in rows:
            dates = [convert_human_ts_to_utc(row[index]) if row[index] else None
                     for index in (0, 3, 4)]
            data_list.append((*dates, row[1], row[2], *row[5:], relative))

    data_headers = (
        ('Created Date', 'datetime'), ('Modified Date', 'datetime'), ('Opened Date', 'datetime'),
        'File Name', 'Owner', 'Last Modifier Account Alias', 'Last Modifier Account Name',
        'File Type', 'Shareable URI', 'HTML URI', 'MD5 Checksum', 'Size', 'Source File',
    )
    return data_headers, data_list, '\n'.join(source_paths)
