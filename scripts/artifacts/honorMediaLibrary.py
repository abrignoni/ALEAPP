__artifacts_v2__ = {
    "honorMediaLibrary": {
        "name": "HONOR - Media Library (Gallery)",
        "description": "Parses file metadata from HONOR's gallery.db",
        "author": "@bitpwny",
        "creation_date": "2026-06-20",
        "last_update_date": "2026-06-20",
        "requirements": "none",
        "category": "HONOR",
        "notes": "",
        "paths": ('*/com.hihonor.medialibrary/databases/gallery.db*',),
        "output_types": "standard",
        "artifact_icon": "file"
    }
}

from scripts.ilapfuncs import (
    artifact_processor,
    get_file_path,
    get_sqlite_db_records,
    convert_unix_ts_to_utc
)

@artifact_processor
def honorMediaLibrary(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "gallery.db")
    data_list = []

    query = '''
    SELECT
        date_added                              AS added_timestamp,
        date_modified                           AS modified_timestamp,
        datetaken                               AS taken_timestamp,
        _data                                   AS path,
        title                                   AS title,
        _display_name                           AS display_name,
        _size                                   AS file_size,
        latitude                                AS latitude,
        longitude                               AS longitude,
        json_extract(expand, '$.time_zone')     AS time_zone,
        bucket_display_name                     AS bucket_display_name,
        NULLIF(duration, 0)                     AS duration,
        resolution                              AS resolution,
        hash                                    AS md5,
        CASE
            -- recycleFlag: All values other than 0 treated as recycled (based on observations)
            WHEN recycleFlag = 0 THEN NULL
            ELSE 'Yes (flag = ' || recycleFlag || ')'
        END                                     AS recycled,
        NULLIF(recycledTime, 0)                 AS recycled_timestamp,
        sourcePath                              AS source_file_path,
        sourceFileName                          AS source_file_name
    FROM gallery_media
    '''

    records = get_sqlite_db_records(source_path, query)
    for record in records:
        data_list.append((
            convert_unix_ts_to_utc(record[0]),  #added_timestamp
            convert_unix_ts_to_utc(record[1]),  #modified_timestamp
            convert_unix_ts_to_utc(record[2]),  #taken_timestamp
            record[3],                          #path
            record[4],                          #title
            record[5],                          #display_name
            record[6],                          #file_size
            record[7],                          #latitude
            record[8],                          #longitude
            record[9],                          #time_zone
            record[10],                         #bucket_display_name
            record[11],                         #duration
            record[12],                         #resolution
            record[13],                         #md5
            record[14],                         #recycled
            convert_unix_ts_to_utc(record[15]), #recycled_timestamp
            record[16],                         #source_file_path
            record[17],                         #source_file_name
        ))

    data_headers = (
        ('Added Timestamp', 'datetime'),
        ('Modified Timestamp', 'datetime'),
        ('Taken Timestamp', 'datetime'),
        'Path',
        'Title',
        'Display Name',
        ('File Size', 'bytes'),
        'Latitude',
        'Longitude',
        'Time Zone',
        'Bucket Display Name',
        'Duration',
        'Resolution',
        'MD5',
        'Recycled?',
        ('Recycled Timestamp', 'datetime'),
        'Source File Path',
        'Source File Name',
    )
    return data_headers, data_list, source_path