import csv

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows

def get_adb_hosts(files_found, report_folder, seeker, wrap_text):
    data_list = []
    file_found = str(files_found[0])
    
    with open(file_found, 'r') as f:
        user_and_host_list = [line.split(" ")[1].rstrip('\n').split('@', 1) for line in f]
        data_list = user_and_host_list
    
    if len(data_list) > 0:
        report = ArtifactHtmlReport('ADB Hosts')
        report.start_artifact_report(report_folder, f'ADB Hosts')
        report.add_script()
        data_headers = ('Username', 'Hostname')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'ADB Hosts'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc(f'No ADB Hosts file available')
