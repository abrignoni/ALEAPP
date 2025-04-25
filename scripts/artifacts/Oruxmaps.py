import sqlite3
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_Oruxmaps(files_found, report_folder, seeker, wrap_text):
    file_found = str(files_found[0])
    source_file = file_found.replace(seeker.data_folder, '')
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT poilat, poilon, poialt, poitime/1000, poiname FROM pois
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Oruxmaps POI')
        report.start_artifact_report(report_folder, 'Oruxmaps POI')
        report.add_script()
        data_headers = ('poilat','poilon','poialt', 'poitime', 'poiname') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
                        
        for row in all_rows:
            
            timestamp = datetime.datetime.utcfromtimestamp(int(row[3])).strftime('%Y-%m-%d %H:%M:%S')
            data_list.append((row[0], row[1], row[2], timestamp, row[4]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Oruxmaps POI'
        tsv(report_folder, data_headers, data_list, tsvname, source_file)
        
        tlactivity = f'Oruxmaps POI'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Oruxmaps POI data available')
    
    cursor.execute('''
            SELECT tracks._id, trackname, trackciudad, segname, trkptlat, trkptlon, trkptalt, trkpttime/1000 
              FROM tracks, segments, trackpoints
             where tracks._id = segments.segtrack and segments._id = trackpoints.trkptseg
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Oruxmaps Tracks')
        report.start_artifact_report(report_folder, 'Oruxmaps Tracks')
        report.add_script()
        data_headers = ('track id','track name','track description', 'segment name', 'latitude', 'longitude', 'altimeter', 'datetime') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
                        
        for row in all_rows:
            timestamp = datetime.datetime.utcfromtimestamp(int(row[7])).strftime('%Y-%m-%d %H:%M:%S')
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], timestamp))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Oruxmaps Tracks'
        tsv(report_folder, data_headers, data_list, tsvname, source_file)
        
        tlactivity = f'Oruxmaps Tracks'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Oruxmaps Tracks data available')

    db.close()

__artifacts__ = {
        "Oruxmaps": (
                "GEO Location",
                ('**/oruxmaps/tracklogs/oruxmapstracks.db*'),
                get_Oruxmaps)
}
