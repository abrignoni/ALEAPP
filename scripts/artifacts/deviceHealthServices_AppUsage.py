__artifacts_v2__ = {
    "Turbo_AppUsage": {
        "name": "Turbo_AppUsage",
        "description": "Parses application usage via Device Health Services",
        "author": "@KevinPagano3",
        "version": "0.0.1",
        "date": "2021-06-29",
        "requirements": "none",
        "category": "Device Health Services",
        "notes": "",
        "paths": ('*/com.google.android.apps.turbo/shared_prefs/app_usage_stats.xml'),
        "function": "get_Turbo_AppUsage"
    }
}

import datetime
import struct
import xml.etree.ElementTree as ET

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

def get_Turbo_AppUsage(files_found, report_folder, seeker, wrap_text):
    
    data_list = []
    splits = []
    app_name = ''
    timestamp_split = ''
    
    for file_found in files_found:
        file_name = str(file_found)
        tree = ET.parse(file_found)
        
        for elem in tree.iter(tag='string'):
            splits = elem.text.split('#')
            
            app_name = splits[0]
            timesplitter = splits[1].split(',')
            count = len(timesplitter)

            for i in range(len(timesplitter)):
                timestamp_split = datetime.datetime.utcfromtimestamp(int(timesplitter[i])/1000).strftime('%Y-%m-%d %H:%M:%S.%f')
                timestamp_split = timestamp_split.strip('0')

                data_list.append((timestamp_split, app_name, file_found))
        
    if data_list:
        report = ArtifactHtmlReport('Turbo - Application Usage')
        report.start_artifact_report(report_folder, f'Turbo - Application Usage')
        report.add_script()
        data_headers = ('App Launch Timestamp','App Name','Source')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Turbo - Application Usage'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Turbo - Application Usage'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc(f'No Turbo - Application Usage data available')

