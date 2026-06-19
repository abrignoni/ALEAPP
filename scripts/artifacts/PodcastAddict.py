# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_podcasts": {
        "name": "Podcast Addict",
        "description": "Parses Podcast Addict Episode Database",
        "author": "John Hyla",
        "creation_date": "2023-07-07",
        "last_update_date": "2023-07-07",
        "requirements": "none",
        "category": "Podcast Addict",
        "notes": "",
        "paths": ('*/com.bambuna.podcastaddict/databases/podcastAddict.db',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "headphones",
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_human_ts_to_utc


@artifact_processor
def get_podcasts(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_name = str(file_found)
        source_path = file_name

        db = open_sqlite_db_readonly(file_name)
        cursor = db.cursor()
        try:
            cursor.execute('''
                SELECT datetime(publication_date/1000, "UNIXEPOCH") as publication_date,
                datetime(playbackDate/1000, "UNIXEPOCH") as playbackDate,
                name,
                duration,
                size,
                datetime(downloaded_date/1000, "UNIXEPOCH") as downloaded_date,
                playing_status,
                position_to_resume,
                download_url
                  FROM episodes
                  ''')
            all_rows = cursor.fetchall()
        except Exception:
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
    return data_headers, data_list, source_path
