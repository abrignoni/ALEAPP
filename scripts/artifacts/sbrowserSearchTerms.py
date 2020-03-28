import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows

def get_sbrowserSearchTerms(files_found, report_folder, seeker):
    
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
        url_id,
        term,
        id,
        url,
        datetime(last_visit_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
    FROM keyword_search_terms, urls
    WHERE url_id = id
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Keyword Search Terms')
        report.start_artifact_report(report_folder, 'Browser Search Terms')
        report.add_script()
        data_headers = ('Term','URL','Last Visit Time' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[1],(textwrap.fill(row[3], width=100)),row[4]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
    else:
        logfunc('No keyword search terms data available')
    
    db.close()
    return