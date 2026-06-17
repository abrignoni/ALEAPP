__artifacts_v2__ = {
    "extract_zepplife_heartrate": {
        "name": "Zepp Life - Heart Rate",
        "description": "Heart rate history from Zepp Life",
        "author": "its5Q",
        "date": "2025-07-28",
        "requirements": "none",
        "category": "Zepp Life",
        "notes": "",
        "paths": ('*/com.xiaomi.hm.health/databases/origin_db*',),
        "output_types": "standard",
        "artifact_icon": "heart",
    }
}

from datetime import datetime, timezone
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly

@artifact_processor
def extract_zepplife_heartrate(files_found, report_folder, seeker, wrap_text):
    data_list = []

    origin = None

    for db_path in files_found:
        db = open_sqlite_db_readonly(db_path)
        cursor = db.cursor()
        cursor.execute('''
        SELECT TIME, HR FROM HEART_RATE;
        ''')

        rows = cursor.fetchall()
        if rows:
            for row in rows:
                row = list(row)
                try:
                    row[0] = datetime.fromtimestamp(row[0], timezone.utc)
                except Exception as ex:
                    logfunc('Error processing timestamp: ', ex)

                data_list.append(row)
            
            origin = db_path
            break


    data_headers = (('Timestamp', 'datetime'), 'Heart Rate')
    return data_headers, data_list, origin
