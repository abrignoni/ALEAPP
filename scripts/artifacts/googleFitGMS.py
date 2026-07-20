__artifacts_v2__ = {
    "googleFitGMS": {
        "name": "Google Fit (GMS) - Activity Sessions",
        "description": "parses the Google Fit database found in com.google.android.gms/databases",
        "author": "Josh Hickman (josh@thebinaryhick.blog)",
        "creation_date": "2021-02-05",
        "last_update_date": "2025-09-09",
        "requirements": "none",
        "category": "Google Fit",
        "notes": "This module only parses the Google Fit database found in com.google.android.gms/databases",
        "paths": ('*/com.google.android.gms/databases/fitness.db.*'),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "galaxys10_a10": "Android 10 | com.google.android.gms vc 210915037 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 33 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 0 rows",
        },
    }
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records

@artifact_processor
def googleFitGMS(context):
    files_found = context.get_files_found()
    data_list = []
    
    for file_found in files_found:
        if str(file_found).endswith(('-wal','-shm')):
            continue
        else:
            query = '''
            SELECT
            datetime(Sessions.start_time/1000,'unixepoch') AS "Activity Start Time",
            datetime(Sessions.end_time/1000,'unixepoch') AS "Activity End Time",
            Sessions.app_package AS "Contributing App",
            CASE
            WHEN Sessions.activity=7 THEN "Walking"
            WHEN Sessions.activity=8 THEN "Running"
            WHEN Sessions.activity=72 THEN "Sleeping"
            ELSE Sessions.activity
            END AS "Activity Type",
            Sessions.name AS "Activity Name",
            Sessions.description AS "Activity Description"
            FROM
            Sessions
            ORDER BY "Activity Start Time" ASC
            '''
            
            db_records = get_sqlite_db_records(file_found, query)

            for record in db_records:
                data_list.append((record[0],record[1],record[2],record[3],record[4],record[5],context.get_relative_path(file_found)))

    data_headers = (('Activity Start Time','datetime'),('Activity End Time','datetime'),'Contributing App','Activity Type','Activity Name','Activity Description','Source File') 
    return data_headers, data_list, 'See source file(s) below'
