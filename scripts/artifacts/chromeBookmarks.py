import datetime
import json
import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, get_next_unused_name

def get_chromeBookmarks(files_found, report_folder, seeker):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'Bookmarks': # skip -journal and other files
            continue
        elif file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data??
        browser_name = 'Chrome'
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'

        with open(file_found, "r") as f:
            dataa = json.load(f)
        data_list = []
        for x, y in dataa.items():
            flag = 0
            if isinstance(y,dict):
                for key, value in y.items():
                    if isinstance(value,dict):
                        for keyb, valueb in value.items():
                            if keyb == 'children':
                                if len(valueb) > 0:
                                    url = valueb[0]['url']
                                    dateadd = valueb[0]['date_added']
                                    dateaddconv = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=int(dateadd))
                                    name = valueb[0]['name']
                                    typed = valueb[0]['type']
                                    flag = 1
                            if keyb == 'name' and flag == 1:
                                flag = 0
                                parent = valueb
                                data_list.append((dateaddconv, url, name, parent, typed))
        num_entries = len(data_list)
        if num_entries > 0:
            report = ArtifactHtmlReport(f'{browser_name} Bookmarks')
            #check for existing and get next name for report file, so report from another file does not get overwritten
            report_path = os.path.join(report_folder, f'{browser_name} Bookmarks.temphtml')
            report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            data_headers = ('Added Date', 'URL', 'Name', 'Parent', 'Type') 
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'{browser_name} Bookmarks'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'{browser_name} Bookmarks'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Browser Bookmarks data available')
