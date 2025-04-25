import os
import time
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, logdevinfo

def get_last_boot_time(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('last_boot_time_utc'):
            continue # Skip all other files
        
        data_list = []
        file_name = 'last_boot_time_utc'
        
        modTimesinceEpoc = os.path.getmtime(file_found)

        last_boot_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(modTimesinceEpoc))
                     
        logdevinfo(f"<b>Last Boot Timestamp: </b>{last_boot_time}")
        data_list.append((last_boot_time, file_name))
                     
        if data_list:
            report = ArtifactHtmlReport('Last Boot Time')
            report.start_artifact_report(report_folder, 'Last Boot Time')
            report.add_script()
            data_headers = ('Timestamp', 'File Name')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Last Boot Time'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Last Boot Time'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('No Last Boot Time data available')

__artifacts__ = {
        "last_boot_time": (
                "Power Events",
                ('*/misc/bootstat/last_boot_time_utc'),
                get_last_boot_time)
}