import sqlite3
import textwrap
import json
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows

def get_sbrowserBookmarks(files_found, report_folder, seeker):
    
    file_found = str(files_found[0])
    with open(file_found, "r") as f:
        dataa = json.load(f)
    report = ArtifactHtmlReport('Browser Bookmarks')
    report.start_artifact_report(report_folder, 'Browser Bookmarks')
    report.add_script()
    data_headers = ('URL','Added Date','Name', 'Parent', 'Type') 
    data_list = []
    for x, y in dataa.items():
        flag = 0
        if isinstance(y,dict):
            for key, value in y.items():
                #print(key, '->', value)
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
                            data_list.append((url, dateaddconv, name, parent, typed))

    report.write_artifact_data_table(data_headers, data_list, file_found)
    report.end_artifact_report()
    #else:
    #    logfunc('No Chrome Login Data available')
    
   
    return

