import os
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly
from scripts.artifacts.chrome import get_browser_name

def get_chromeTopSites(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'Top Sites': # skip -journal and other files
            continue
        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'
        elif file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data??

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        try:
            cursor.execute('''
            select
            url,
            url_rank,
            title,
            redirects
            FROM
            top_sites ORDER by url_rank asc
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
        except:
            usageentries = 0
            
        if usageentries > 0:
            report = ArtifactHtmlReport(f'{browser_name} - Top Sites')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{browser_name} - Top Sites.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('URL','Rank','Title','Redirects')
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'{browser_name} - Top Sites'
            tsv(report_folder, data_headers, data_list, tsvname)
        else:
            logfunc(f'No {browser_name} - Top Sites data available')
        
        db.close()
        
__artifacts__ = {
        "ChromeTopSites": (
                "Chromium",
                ('*/app_chrome/Default/Top Sites*', '*/app_sbrowser/Default/Top Sites*', '*/app_opera/Top Sites*', '*/app_webview/Default/Top Sites*'),
                get_chromeTopSites)
}
