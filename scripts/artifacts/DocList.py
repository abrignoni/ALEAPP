# pylint: disable=W0613,W0702
__artifacts_v2__ = {
    "get_DocList": {
        "name": "DocList",
        "description": "Parses Google Drive file metadata (name, owner, type, created/modified/opened dates, URIs, MD5 and size) from the DocList.db database.",
        "author": "",
        "creation_date": "2020-12-21",
        "last_update_date": "2020-12-21",
        "requirements": "none",
        "category": "Google Drive",
        "notes": "",
        "paths": ('*/com.google.android.apps.docs/databases/DocList.db*',),
        "output_types": "standard",
        "artifact_icon": "file",
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_human_ts_to_utc


@artifact_processor
def get_DocList(files_found, report_folder, seeker, wrap_text):

    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    try:
        cursor.execute('''
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
        ''')
        all_rows = cursor.fetchall()
    except:
        all_rows = []

    data_list = []
    for row in all_rows:
        data_list.append((convert_human_ts_to_utc(row[0]),row[1],row[2],convert_human_ts_to_utc(row[3]),convert_human_ts_to_utc(row[4]),row[5],row[6],row[7],row[8],row[9],row[10],row[11],))

    db.close()

    data_headers = (
        ('Created Date', 'datetime'), 'File Name', 'Owner', ('Modified Date', 'datetime'),
        ('Opened Date', 'datetime'), 'Last Modifier Account Alias', 'Last Modifier Account Name',
        'File Type', 'Shareable URI', 'HTML URI', 'MD5 Checksum', 'Size',
    )
    return data_headers, data_list, source_path
