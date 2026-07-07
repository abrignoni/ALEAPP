# pylint: disable=W0613
__artifacts_v2__ = {
    "get_cmh": {
        "name": "cmh",
        "description": "",
        "author": "",
        "creation_date": "2020-03-05",
        "last_update_date": "2020-03-05",
        "requirements": "none",
        "category": "Samsung_CMH",
        "notes": "",
        "paths": ('*/cmh.db',),
        "output_types": "all",
        "artifact_icon": "file",
    }
}

import datetime

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _ms_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    return ''


def _sec_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    return ''


@artifact_processor
def get_cmh(files_found, report_folder, seeker, wrap_text):
    source_path = str(files_found[0])
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        SELECT
        images.datetaken, images.date_added, images.date_modified, images.title,
        images.bucket_display_name, images.latitude, images.longitude,
        location_view.address_text, location_view.uri, images._data, images.isprivate
        FROM images
        left join location_view on location_view._id = images._id
    ''')
    all_rows = cursor.fetchall()
    db.close()

    data_list = []
    for r in all_rows:
        data_list.append((_ms_to_utc(r[0]), _sec_to_utc(r[1]), _sec_to_utc(r[2]), r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10]))

    data_headers = (('Timestamp', 'datetime'), ('Date Added', 'datetime'), ('Date Modified', 'datetime'), 'Title', 'Bucket Name', 'Latitude', 'Longitude', 'Address', 'URI', 'Data Location', 'Is Private')
    return data_headers, data_list, source_path
