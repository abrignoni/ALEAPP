__artifacts_v2__ = {
    "get_podcasts": {
        "name": "Podcast Addict",
        "description": "Parses the episodes table of the Podcast Addict database.",
        "author": "John Hyla, @AlexisBrignoni, Codex",
        "creation_date": "2023-07-07",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Podcast Addict",
        "notes": "publication_date, playbackDate and downloaded_date are read "
                 "as Unix milliseconds; no source for that unit was found and "
                 "no registered corpus holds this database, so it is not "
                 "established on real data. A date column is left blank when "
                 "the stored value is NULL, 0 or negative. What the app stores "
                 "for an episode that was not played or not downloaded was not "
                 "measured. Only the file named podcastAddict.db is opened; "
                 "its -wal, -shm and -journal files are matched so that they "
                 "are staged beside it. If the query fails for a file, the "
                 "error is written to the run log and that file adds no rows.",
        "paths": ('*/com.bambuna.podcastaddict/databases/podcastAddict.db*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "headphones",
    }
}

import os
import sqlite3

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_human_ts_to_utc, logfunc


@artifact_processor
def get_podcasts(context):
    files_found = context.get_files_found()
    data_list = []
    source_paths = []

    for file_found in files_found:
        file_name = str(file_found)
        if os.path.isdir(file_name) or os.path.basename(file_name) != 'podcastAddict.db':
            continue

        db = open_sqlite_db_readonly(file_name)
        if db is None:
            continue
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT CASE WHEN publication_date > 0 THEN datetime(publication_date/1000, "UNIXEPOCH") END as publication_date,
                CASE WHEN playbackDate > 0 THEN datetime(playbackDate/1000, "UNIXEPOCH") END as playbackDate,
                name,
                duration,
                size,
                CASE WHEN downloaded_date > 0 THEN datetime(downloaded_date/1000, "UNIXEPOCH") END as downloaded_date,
                playing_status,
                position_to_resume,
                download_url
                  FROM episodes
                  ''')
            all_rows = cursor.fetchall()
            source_paths.append(file_name)
        except sqlite3.Error as ex:
            logfunc(f'Podcast Addict: could not read the episodes table in {file_name}: {ex}')
            all_rows = []

        for row in all_rows:
            data_list.append((convert_human_ts_to_utc(row[0]), convert_human_ts_to_utc(row[1]), row[2], row[3], row[4], convert_human_ts_to_utc(row[5]), row[6], row[7], row[8]))

        db.close()

    data_headers = (
        ('publication_date', 'datetime'),
        ('playback_date', 'datetime'),
        'name',
        'duration',
        'size',
        ('downloaded_date', 'datetime'),
        'playing_status',
        'position_to_resume',
        'download_url',
    )
    return data_headers, data_list, '\n'.join(source_paths)
