__artifacts_v2__ = {
    "frosting": {
        "name": "App Updates (Frosting.db)",
        "description": "App updates via the frosting.db",
        "author": "@stark4n6",
        "creation_date": "2022-07-28",
        "last_updated_date": "2025-09-09",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "",
        "paths": ('*/com.android.vending/databases/frosting.db*'),
        "output_types": "standard",
        "artifact_icon": "package"
    }
}    

from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records

@artifact_processor
def frosting(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = get_file_path(files_found, "frosting.db")
    
    query = '''
    select
    case last_updated
        when 0 then ''
        else datetime(last_updated/1000,'unixepoch')
    end	as "Last Updated",
    pk,
    apk_path
    from frosting
    '''

    db_records = get_sqlite_db_records(source_path, query)
    for record in db_records:
        data_list.append((record[0], record[1], record[2]))

    data_headers = (('Last Updated Timestamp','datetime'),'App Package Name','APK Path')
    return data_headers, data_list, source_path