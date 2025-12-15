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
        moz_places.visit_count_local AS VisitCount,
        moz_places.description AS Description,
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
            report = ArtifactHtmlReport('Firefox - Web History')
            report.start_artifact_report(report_folder, 'Firefox - Web History')
            report.add_script()
            data_headers = ('Last Visit Date','URL','Title','Visit Count','Description','Hidden','Typed','Frecency','Preview Image URL') 
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Firefox - Web History'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Firefox - Web History'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Firefox - Web History data available')
            
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(moz_historyvisits.visit_date/1000, 'unixepoch') AS VisitDate,
        moz_places.url AS URL,
        moz_places.title AS Title,
        moz_historyvisits.id AS VisitID,
        moz_historyvisits.from_visit AS FromVisitID,
        CASE moz_historyvisits.visit_type
            WHEN 1 THEN 'TRANSITION_LINK'
            WHEN 2 THEN 'TRANSITION_TYPED'
            WHEN 3 THEN 'TRANSITION_BOOKMARK'
            WHEN 4 THEN 'TRANSITION_EMBED'
            WHEN 5 THEN 'TRANSITION_REDIRECT_PERMANENT'
            WHEN 6 THEN 'TRANSITION_REDIRECT_TEMPORARY'
            WHEN 7 THEN 'TRANSITION_DOWNLOAD'
            WHEN 8 THEN 'TRANSITION_FRAMED_LINK'
            WHEN 9 THEN 'TRANSITION_RELOAD'
        END AS VisitType,
        CASE
            WHEN moz_places.typed = 0 THEN 'No'
            WHEN moz_places.typed = 1 THEN 'Yes'
        END AS Typed
        FROM
        moz_historyvisits
        INNER JOIN moz_places ON moz_places.id = moz_historyvisits.place_id
        ORDER BY
        moz_historyvisits.visit_date ASC  
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Firefox - Web Visits')
            report.start_artifact_report(report_folder, 'Firefox - Web Visits')
            report.add_script()
            data_headers = ('Visit Date','URL','Title','Visit ID','From Visit ID','Visit Type','Typed') 
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Firefox - Web Visits'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Firefox - Web Visits'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Firefox - Web Visits data available')
        
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        datetime(moz_bookmarks.dateAdded/1000,'unixepoch'),
        datetime(moz_bookmarks.lastModified/1000,'unixepoch'),
        moz_bookmarks.title,
        moz_places.url,
        CASE moz_bookmarks.type
            WHEN 1 THEN 'URL'
            WHEN 2 THEN 'Folder'
            WHEN 3 THEN 'Separator'
        END,
        moz_bookmarks.id,
        moz_bookmarks.parent,
        moz_bookmarks.position,
        moz_bookmarks.syncStatus
        FROM moz_bookmarks
        LEFT JOIN moz_places ON moz_bookmarks.fk = moz_places.id
        ORDER BY moz_bookmarks.id ASC
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Firefox - Bookmarks')
            report.start_artifact_report(report_folder, 'Firefox - Bookmarks')
            report.add_script()
            data_headers = ('Added Timestamp','Modified Timestamp','Title','URL','Bookmark Type','ID','Parent','Position','Sync Status') 
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Firefox - Bookmarks'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Firefox - Bookmarks'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Firefox - Bookmarks data available')
            
        cursor = db.cursor()
        cursor.execute('''
        SELECT
        id AS 'ID',
        term AS 'Search Term'
        FROM moz_places_metadata_search_queries
        ORDER BY id ASC
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Firefox - Search Terms')
            report.start_artifact_report(report_folder, 'Firefox - Search Terms')
            report.add_script()
            data_headers = ('ID','Search Term') 
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Firefox - Search Terms'
            tsv(report_folder, data_headers, data_list, tsvname)
            
        else:
            logfunc('No Firefox - Search Terms data available')
        
        db.close()
    
__artifacts__ = {
        "Firefox": (
                "Firefox",
                ('*/org.mozilla.firefox/files/places.sqlite*'),
                get_firefox)
}