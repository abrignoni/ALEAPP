import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_FilesByGoogle_SearchHistory(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('search_history_database'):
            continue # Skip all other files
    
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        select
            searched_term,
            case timestamp
                when 0 then ''
                else datetime(timestamp/1000,'unixepoch')
            end as timestamp
        from search_history_content
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('File by Google - Search History')
            report.start_artifact_report(report_folder, 'Files By Google - Search History')
            report.add_script()
            data_headers = ('Search Term','Timestamp') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Files By Google - Search History'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Files By Google - Search History'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Files By Google - Search History data available')
    
    db.close()
    return
