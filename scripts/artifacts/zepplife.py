# pylint: disable=E1121,W0718
__artifacts_v2__ = {
    "extract_zepplife_heartrate": {
        "name": "Zepp Life - Heart Rate",
        "description": "Heart rate records (HEART_RATE table) from the matched Zepp Life origin_db databases; TIME is reported as stored",
        "author": "its5Q, @AlexisBrignoni, Codex",
        "creation_date": "2025-07-28",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Zepp Life",
        "notes": "TIME is reported as text because its epoch and unit have not been established. "
                 "All matched origin_db files are read; SQLite sidecars are excluded.",
        "paths": ('*/com.xiaomi.hm.health/databases/origin_db*',),
        "output_types": "standard",
        "artifact_icon": "heart",
    }
}

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly

@artifact_processor
def extract_zepplife_heartrate(context):
    files_found = unique_files(context)
    data_list = []

    sources = []

    for db_path in files_found:
        if str(db_path).endswith(("-wal", "-shm", "-journal")):
            continue
        db = open_sqlite_db_readonly(db_path)
        if not db:
            continue
        cursor = db.cursor()
        cursor.execute('''
        SELECT TIME, HR FROM HEART_RATE;
        ''')

        rows = cursor.fetchall()
        db.close()
        if rows:
            sources.append(str(db_path))
            for stamp, heart_rate in rows:
                data_list.append((str(stamp) if stamp is not None else '', heart_rate,
                                  context.get_relative_path(db_path)))

    data_headers = ('TIME (as stored)', 'Heart Rate', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
