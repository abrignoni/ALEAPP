# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_rdd_analytics": {
        "name": "VerizonRDD-Battery",
        "description": "Module Description: Parses Verizon RDD Analytics Battery History",
        "author": "John Hyla",
        "creation_date": "2023-07-07",
        "last_update_date": "2023-07-07",
        "requirements": "none",
        "category": "Verizon RDD Analytics",
        "notes": "",
        "paths": ('*/com.verizon.mips.services/databases/RDD_ANALYTICS_DATABASE',),
        "output_types": "standard",
        "artifact_icon": "battery",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


@artifact_processor
def get_rdd_analytics(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''
    for file_found in files_found:
        source_path = str(file_found)
        db = open_sqlite_db_readonly(source_path)
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT ActualTime, FormattedTime, BatteryLevel, GPS, Charging, ScreenOn, Brightness, BatteryTemp
                FROM TableBatteryHistory
            ''')
            all_rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            all_rows = []
        db.close()

        for row in all_rows:
            actual_time = datetime.datetime.fromtimestamp(int(row[0]) / 1000, datetime.timezone.utc) if row[0] else ''
            data_list.append((actual_time, row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

    data_headers = (('ActualTime', 'datetime'), 'FormattedTime', 'BatteryLevel', 'GPS', 'Charging', 'ScreenOn', 'Brightness', 'BatteryTemp')
    return data_headers, data_list, source_path
