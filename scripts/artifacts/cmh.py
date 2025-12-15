import glob
import json
import os
import shutil
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, kmlgen, is_platform_windows, open_sqlite_db_readonly

def get_cmh(files_found, report_folder, seeker, wrap_text):

    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime(images.datetaken /1000, "unixepoch") as datetaken,
    datetime(images.date_added, "unixepoch") as dateadded,
    datetime(images.date_modified, "unixepoch") as datemodified,
    images.title,
    images.bucket_display_name,
    images.latitude,
    images.longitude,
    location_view.address_text,
    location_view.uri,
    images._data,
    images.isprivate
    FROM images
    left join location_view
    on location_view._id = images._id
    ''')
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Samsung CMH')
        report.start_artifact_report(report_folder, f'Geodata')
        report.add_script()
        data_headers = ('Timestamp', 'Date Added', 'Date Modified', 'Title', 'Bucket Name', 'Latitude', 'Longitude','Address', 'URI', 'Data Location', 'Is Private')
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Samsung CMH Geodata'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Samsung CMH Geodata'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
        kmlactivity = 'Samsung CMH Geodata'
        kmlgen(report_folder, kmlactivity, data_list, data_headers)
        
    else:
        logfunc(f'No Samsung_CMH_GeoData available')    
    db.close()

__artifacts__ = {
        "cmh": (
                "Samsung_CMH",
                ('*/cmh.db'),
                get_cmh)
}