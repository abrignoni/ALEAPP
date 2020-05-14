import os
import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows, get_next_unused_name

def get_chromeWebsearch(files_found, report_folder, seeker):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'History': # skip -journal and other files
            continue
        browser_name = 'Chrome'
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'
        elif file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data??

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
            report = ArtifactHtmlReport(f'{browser_name} Search Terms')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{browser_name} Search Terms.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('Search Term','URL', 'Title', 'Visit Count', 'Last Visit Time')
            data_list = []
            for row in all_rows:
                search = row[0].split('search?q=')[1].split('&')[0]
                search = search.replace('+', ' ')
                data_list.append((search, (textwrap.fill(row[0], width=100)),row[1],row[2],row[3]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
        else:
            logfunc(f'No {browser_name} web search terms data available')
        
        db.close()