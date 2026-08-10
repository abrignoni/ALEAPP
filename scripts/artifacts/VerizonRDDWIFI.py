# pylint: disable=W0718
__artifacts_v2__ = {
    "get_rdd_wifi": {
        "name": "VerizonRDD-WIFI",
        "description": "Module Description: Parses Verizon RDD Wifi Data",
        "author": "John Hyla",
        "creation_date": "2023-07-07",
        "last_update_date": "2023-07-07",
        "requirements": "none",
        "category": "Verizon RDD Analytics",
        "notes": "",
        "paths": ('*/com.verizon.mips.services/databases/RDD_WIFI_DATA_DATABASE',),
        "output_types": "standard",
        "artifact_icon": "wifi",
    }
}

import datetime
import json

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


@artifact_processor
def get_rdd_wifi(context):
    files_found = context.get_files_found()

    data_list = []
    source_path = ''
    for file_found in files_found:
        source_path = str(file_found)
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT timestamp, eventid, event, data
                FROM TABLERDDWIFIDATA
            ''')
            all_rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            all_rows = []
        db.close()

        for row in all_rows:
            timestamp = datetime.datetime.fromtimestamp(int(row[0]) / 1000, datetime.timezone.utc) if row[0] else ''
            json_data = json.loads(row[3])
            data_list.append((timestamp, row[1], row[2],
                              json_data.get('wifiinfo').get('bssid'),
                              json_data.get('wifiinfo').get('ssid'),
                              json_data.get('returnedIP'),
                              json_data.get('totalSessionTime'),
                              json_data.get('sessionWifiTx'),
                              json_data.get('sessionWifiRx'),
                              json_data.get('cellId')))

    data_headers = (('Timestamp', 'datetime'), 'Event ID', 'Event', 'BSSID', 'SSID', 'IP', 'SessionTime', 'DataTx', 'DataRx', 'Cell ID')
    return data_headers, data_list, source_path
