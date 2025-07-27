__artifacts_v2__ = {
    "androidauto": {
        "name": "Android Auto Connected Cars",
        "description": "Android Auto connected cars",
        "author": "its5Q",
        "version": "0.0.1",
        "date": "2025-07-28",
        "requirements": "none",
        "category": "Android Auto",
        "notes": "",
        "paths": ('*/com.google.android.projection.gearhead/databases/carservicedata.db'),
        "output_types": "standard",
        "function": "extract_android_auto",
        "artifact_icon": "truck",
    }
}

import json
from datetime import datetime, timezone
from collections import defaultdict
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly

@artifact_processor
def extract_android_auto(files_found, report_folder, seeker, wrap_text):
    data_list = []

    db_path = files_found[0]
    db = open_sqlite_db_readonly(db_path)
    cursor = db.cursor()
    cursor.execute('''
    SELECT connectiontime, manufacturer, model,
           modelyear, bluetoothaddress, wifissid,
           wifibssid, wifipassword
    FROM allowedcars;
    ''')

    rows = cursor.fetchall()
    for row in rows:
        row = list(row)
        try:
            row[0] = datetime.fromtimestamp(row[0] / 1000, timezone.utc)
        except Exception as ex:
            logfunc('Error processing timestamp: ', ex)

        data_list.append(row)

    data_headers = (('Connection Time', 'datetime'), 'Manufacturer', 'Model', 'Year', 'Bluetooth MAC', 'Wi-Fi SSID', 'Wi-Fi BSSID', 'Wi-Fi Password')

    return data_headers, data_list, db_path
