import sqlite3
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def convertGeo(s):
    length = len(s)
    if length > 6:
        return (s[0 : length-6] + "." + s[length-6 : length])
    else:
        return (s)

def get_googlemaplocation(files_found, report_folder, seeker, wrap_text):

    source_file = ''

    for file_found in files_found:
        file_found = str(file_found)
        
        if 'journal' in file_found:
            source_file = file_found.replace(seeker.data_folder, '')
            continue
  
        source_file = file_found.replace(seeker.data_folder, '')
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        try:
            cursor.execute('''
            SELECT time/1000, dest_lat, dest_lng, dest_title, dest_address, 
                   source_lat, source_lng FROM destination_history;
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
        except:
            usageentries = 0
            
        if usageentries > 0:
            report = ArtifactHtmlReport('Google Map Locations')
            report.start_artifact_report(report_folder, 'Google Map Locations')
            report.add_script()
            data_headers = ('timestamp','destination_latitude', 'destination_longitude', 'destination_title','destination_address', 'source_latitude', 'source_longitude') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                timestamp = datetime.datetime.utcfromtimestamp(int(row[0])).strftime('%Y-%m-%d %H:%M:%S') 
                data_list.append((timestamp, convertGeo(str(row[1])), convertGeo(str(row[2])), row[3], row[4], convertGeo(str(row[5])), convertGeo(str(row[6]))))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Google Map Locations'
            tsv(report_folder, data_headers, data_list, tsvname, source_file)
            
        else:
            logfunc('No Google Map Locations found')
            
        db.close()
        
__artifacts__ = {
        "Googlemaplocation": (
                "GEO Location",
                ('*/com.google.android.apps.maps/databases/da_destination_history*'),
                get_googlemaplocation)
}
    