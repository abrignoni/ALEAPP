import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows

def get_chromeWebsearch(files_found, report_folder, seeker):
    
    file_found = str(files_found[0])
    db = sqlite3.connect(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
        url,
        title,
        visit_count,
        datetime(last_visit_time / 1000000 + (strftime('%s', '1601-01-01')), "unixepoch")
    FROM urls
    WHERE url like '%search?q=%'
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Chrome Search Terms')
        report.start_artifact_report(report_folder, 'Chrome Search Terms')
        report.add_script()
        data_headers = ('Search Term','URL', 'Title', 'Visit Count', 'Last Visit Time' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            search = row[0].split('search?q=')[1].split('&')[0]
            search = search.replace('+', ' ')
            data_list.append((search, (textwrap.fill(row[0], width=100)),row[1],row[2],row[3]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
    else:
        logfunc('No web search terms data available')
    
    db.close()
    return