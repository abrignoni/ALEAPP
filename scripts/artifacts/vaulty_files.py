# pylint: disable=W0613
__artifacts_v2__ = {
    "get_vaulty_files": {
        "name": "vaulty_files",
        "description": "Vaulty (com.theronrogers.vaultyfree) media database. Research at https://kibaffo33.data.blog/2022/03/05/decoding-vaulty/",
        "author": "",
        "creation_date": "2022-02-23",
        "last_update_date": "2022-02-23",
        "requirements": "none",
        "category": "Vaulty",
        "notes": "",
        "paths": ('*/com.theronrogers.vaultyfree/databases/media.db',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "lock",
    }
}

import sqlite3

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_vaulty_files(files_found, report_folder, seeker, wrap_text):

    # Media database
    db_filepath = str(files_found[0])
    conn = sqlite3.connect(db_filepath)
    c = conn.cursor()
    sql = """SELECT Media._id, datetime(Media.date_added, 'unixepoch'), datetime(Media.date_modified / 1000, 'unixepoch'), Media.path, Media._data FROM Media"""
    c.execute(sql)
    results = c.fetchall()
    conn.close()

    # Data results
    data_headers = (
        'ID',
        ('Date Created', 'datetime'),
        ('Date Added', 'datetime'),
        'Original Path',
        'Vault Path',
    )
    data_list = results

    return data_headers, data_list, db_filepath
