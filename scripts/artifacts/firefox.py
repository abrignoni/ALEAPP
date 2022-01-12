import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_firefox(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'places.sqlite': # skip -journal and other files
            continue
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(moz_places.last_visit_date_local/1000, 'unixepoch') AS LastVisitDate,
        moz_places.url AS URL,
        moz_places.title AS Title,
        moz_historyvisits.id AS VisitID,
        moz_places.visit_count_local AS VisitCount,
        moz_places_metadata.total_view_time AS TotalViewTime,
        moz_places.description AS Description,
        moz_historyvisits.from_visit AS FromVisitID,
        CASE
            WHEN moz_historyvisits.visit_type = 1 THEN 'TRANSITION_LINK'
            WHEN moz_historyvisits.visit_type = 2 THEN 'TRANSITION_TYPED'
            WHEN moz_historyvisits.visit_type = 3 THEN 'TRANSITION_BOOKMARK'
            WHEN moz_historyvisits.visit_type = 4 THEN 'TRANSITION_EMBED'
            WHEN moz_historyvisits.visit_type = 5 THEN 'TRANSITION_REDIRECT_PERMANENT'
            WHEN moz_historyvisits.visit_type = 6 THEN 'TRANSITION_REDIRECT_TEMPORARY'
            WHEN moz_historyvisits.visit_type = 7 THEN 'TRANSITION_DOWNLOAD'
            WHEN moz_historyvisits.visit_type = 8 THEN 'TRANSITION_FRAMED_LINK'
            WHEN moz_historyvisits.visit_type = 9 THEN 'TRANSITION_RELOAD'
        END AS VisitType,
        CASE
            WHEN moz_places.hidden = 0 THEN 'No'
            WHEN moz_places.hidden = 1 THEN 'Yes'
        END AS Hidden,
        CASE
            WHEN moz_places.typed = 0 THEN 'No'
            WHEN moz_places.typed = 1 THEN 'Yes'
        END AS Typed,
        moz_places.frecency AS Frecency,
        moz_places.preview_image_url AS PreviewImageURL
        FROM
        moz_places
        INNER JOIN moz_historyvisits ON moz_places.origin_id = moz_historyvisits.id
        INNER JOIN moz_places_metadata ON moz_places.id = moz_places_metadata.id
        ORDER BY
        moz_places.last_visit_date_local ASC  
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Firefox History')
            report.start_artifact_report(report_folder, 'Firefox History')
            report.add_script()
            data_headers = ('Last Visit Date','URL','Title','Visit ID','Visit Count','Total View Time','Description','From Visit ID','Visit Type','Hidden','Typed','Frecency','Preview Image URL') 
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Firefox History'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Firefox History'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Firefox History data available')
        
        db.close()