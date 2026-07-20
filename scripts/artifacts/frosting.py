# pylint: disable=W0613
__artifacts_v2__ = {
    "frosting": {
        "name": "App Updates (Frosting.db)",
        "description": "App updates via the frosting.db",
        "author": "@stark4n6",
        "creation_date": "2022-07-28",
        "last_update_date": "2025-09-09",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "",
        "paths": ('*/com.android.vending/databases/frosting.db*'),
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "anne_a15": "Android 15 | com.android.vending vc 84801930 | 555 rows",
            "galaxys10_a10": "Android 10 | com.android.vending vc 82481710 | 445 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.vending vc 85180930 | 428 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.vending vc 84812830 | 464 rows",
            "pixel7a_a14": "Android 14 | com.android.vending vc 84191730 | 407 rows",
            "samsunga53_a14": "Android 14 | com.android.vending vc 84913330 | 527 rows",
            "samsungs20_a13": "Android 13 | com.android.vending vc 84962330 | 507 rows",
            "sharon_a14": "Android 14 | com.android.vending vc 84222730 | 541 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.vending vc 83631220 | 324 rows",
            "userb2_a13": "Android 13 | com.android.vending vc 84371930 | 333 rows",
        }
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
