# pylint: disable=W0613
__artifacts_v2__ = {
    "get_garmin_response": {
        "name": "GarminResponse",
        "description": "Get Information related to the Garmin - Responses stored in the database cache",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-24",
        "last_update_date": "2023-02-24",
        "requirements": "Python 3.7 or higher and json",
        "category": "Garmin",
        "notes": "",
        "paths": ('*/com.garmin.android.apps.connectmobile/databases/cache-database*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.garmin.android.apps.connectmobile vc 8806 | 1 row",
        },
    }
}

import datetime
import json

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


def _pretty_json(raw):
    if not raw or raw == '[]':
        return ''
    try:
        s = raw.replace('\\"', '"').replace('"{', '{').replace('}"', '}')
        return json.dumps(json.loads(s), indent=4, sort_keys=True)
    except (ValueError, TypeError):
        return raw


@artifact_processor
def get_garmin_response(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Garmin Response")
    files_found = [x for x in files_found if not str(x).endswith('wal') and not str(x).endswith('shm')]
    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        SELECT requestUrl, response, lastUpdate
        from response_cache
    ''')
    all_rows = cursor.fetchall()
    db.close()
    logfunc(f"Found {len(all_rows)} Garmin Response")

    data_list = []
    for row in all_rows:
        data_list.append((_ms_to_utc(row[2]), row[0], _pretty_json(row[1])))

    data_headers = (('Last Update', 'datetime'), 'Request URL', 'Response')
    return data_headers, data_list, source_path
