import sqlite3
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_browserlocation(files_found, report_folder, seeker, wrap_text):

    source_file = ''

    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('-db'):
            source_file = file_found.replace(seeker.data_folder, '')
            continue
  
        source_file = file_found.replace(seeker.data_folder, '')
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        try:
            cursor.execute('''
            SELECT timestamp/1000, latitude, longitude, accuracy FROM CachedPosition;
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
        except:
            usageentries = 0
            
        if usageentries > 0:
            report = ArtifactHtmlReport('Browser Locations')
            report.start_artifact_report(report_folder, 'Browser Locations')
            report.add_script()
            data_headers = ('timestamp','latitude', 'longitude', 'accuracy') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                timestamp = datetime.datetime.utcfromtimestamp(int(row[0])).strftime('%Y-%m-%d %H:%M:%S') 
                data_list.append((timestamp, row[1], row[2], row[3]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Browser Locations'
            tsv(report_folder, data_headers, data_list, tsvname, source_file)
            
        else:
            logfunc('No Browser Locations found')
            
        db.close()
        
__artifacts__ = {
        "Browser Location": (
                "GEO Location",
                ('*/com.android.browser/app_geolocation/CachedGeoposition.db'),
                get_browserlocation)
}
    