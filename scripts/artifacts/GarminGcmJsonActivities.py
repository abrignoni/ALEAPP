# pylint: disable=W0613
__artifacts_v2__ = {
    "get_garmin_gcm_json_activities": {
        "name": "GarminGcmJsonActivities",
        "description": "Get JSON information stored in the Garmin GCM database (json_activities table)",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-24",
        "last_update_date": "2023-02-24",
        "requirements": "Python 3.7 or higher and json module",
        "category": "Garmin",
        "notes": "",
        "paths": ('*/com.garmin.android.apps.connectmobile/databases/gcm_cache.db*',),
        "output_types": "standard",
        "artifact_icon": "activity",
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
def get_garmin_gcm_json_activities(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Garmin GCM JSON Activities")
    files_found = [x for x in files_found if not str(x).endswith('wal') and not str(x).endswith('shm') and not str(x).endswith('journal')]
    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        SELECT _id, saved_timestamp, concept_id, data_type, cached_val
        from json_activities
    ''')
    all_rows = cursor.fetchall()
    db.close()
    logfunc(f"Found {len(all_rows)} Garmin GCM JSON Activities")

    data_list = []
    for row in all_rows:
        data_list.append((row[0], _ms_to_utc(row[1]), row[2], row[3], _pretty_json(row[4])))

    data_headers = ('_id', ('saved_timestamp', 'datetime'), 'concept_id', 'data_type', 'json')
    return data_headers, data_list, source_path
