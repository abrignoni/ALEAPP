import glob
import json
import os
import shutil
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

def get_cmh(files_found, report_folder, seeker):

    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
        datetime(datetaken /1000, "unixepoch") as times,
        latitude,
        longitude,
        address_text,
        uri,
        _data
    FROM location_view
    ''')
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Samsung CMH')
        report.start_artifact_report(report_folder, f'Geodata')
        report.add_script()
        data_headers = ('Data Taken', 'Latitude', 'Longitude','Address', 'URI', 'Data Location')
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5]))
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Samsung CMH Geodata'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Samsung CMH Geodata'
        timeline(report_folder, tlactivity, data_list)
    else:
        logfunc(f'No Samsung_CMH_GeoData available')    
    db.close()
    return