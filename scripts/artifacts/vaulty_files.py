__artifacts_v2__ = {
    "get_vaulty_files": {
        "name": "vaulty_files",
        "description": "Vaulty (com.theronrogers.vaultyfree) media database. Research at https://kibaffo33.data.blog/2022/03/05/decoding-vaulty/",
        "author": "@kibaffo33",
        "creation_date": "2022-02-23",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Vaulty",
        "notes": "Column names in media.db do not describe their contents: date_added holds the "
                 "creation timestamp of the file and date_modified holds the timestamp the file "
                 "was added to the vault, per the research linked above. The headers below are "
                 "named for the contents, not for the source column. The two values are also "
                 "decoded with different epochs, date_added as seconds and date_modified as "
                 "milliseconds, as set by that original research; the divergence has not been "
                 "re-verified against a test image.",
        "paths": ('*/com.theronrogers.vaultyfree/databases/media.db',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "lock",
    }
}

from scripts.ilapfuncs import artifact_processor, convert_human_ts_to_utc, open_sqlite_db_readonly


@artifact_processor
def get_vaulty_files(context):
    files_found = context.get_files_found()

    # Data results
    # Headers name what each value holds, not the column it comes from: date_added
    # holds the file's creation time and date_modified the added-to-vault time.
    data_headers = (
        'ID',
        ('Date Created', 'datetime'),
        ('Date Added', 'datetime'),
        'Original Path',
        'Vault Path',
    )
    data_list = []

    # Media database
    db_filepath = str(files_found[0])
    conn = open_sqlite_db_readonly(db_filepath)
    if not conn:
        return data_headers, data_list, db_filepath

    c = conn.cursor()
    # date_added is stored in seconds, date_modified in milliseconds; see notes above.
    sql = """SELECT Media._id, datetime(Media.date_added, 'unixepoch'), datetime(Media.date_modified / 1000, 'unixepoch'), Media.path, Media._data FROM Media"""
    c.execute(sql)
    results = c.fetchall()
    conn.close()

    data_list = [(r[0], convert_human_ts_to_utc(r[1]), convert_human_ts_to_utc(r[2]), r[3], r[4]) for r in results]

    return data_headers, data_list, db_filepath
