# pylint: disable=W0702
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

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_human_ts_to_utc


@artifact_processor
def get_DocList(context):
    files_found = context.get_files_found()

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
