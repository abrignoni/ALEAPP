import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, kmlgen

def get_waze(files_found, report_folder, seeker, wrap_text):
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    
    cursor = db.cursor()
    cursor.execute('''
    select
    datetime(PLACES.created_time, 'unixepoch'),
    datetime(RECENTS.access_time, 'unixepoch'),
    RECENTS.name,
    PLACES.name as "Address",
    round(PLACES.latitude*.000001,6),
    round(PLACES.longitude*.000001,6)
    from PLACES
    join RECENTS on PLACES.id = RECENTS.place_id
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Waze - Recently Searched Locations')
        report.start_artifact_report(report_folder, 'Waze - Recently Searched Locations')
        report.add_script()
        data_headers = ('Created Timestamp','Accessed Timestamp','Location Name','Address','Latitude','Longitude')
        data_headers_kml = ('Timestamp','Accessed Timestamp','Location Name','Address','Latitude','Longitude')
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5]))
            
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Waze - Recently Searched Locations'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Waze - Recently Searched Locations'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
        kmlactivity = 'Waze - Recently Searched Locations'
        kmlgen(report_folder, kmlactivity, data_list, data_headers_kml)
        
    else:
        logfunc('No Waze - Recently Searched Locations data available')
        
    db.close()

__artifacts__ = {
        "waze": (
                "Waze",
                ('*/com.waze/user.db*'),
                get_waze)
}
    