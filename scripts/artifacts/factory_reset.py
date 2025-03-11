import os
import time
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, logdevinfo

def get_factory_reset(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('factory_reset'):
            continue # Skip all other files
        
        data_list = []
        file_name = 'factory_reset'
        
        modTimesinceEpoc = os.path.getmtime(file_found)

        reset_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(modTimesinceEpoc))
                     
        logdevinfo(f"<b>Factory Reset Timestamp: </b>{reset_time}")
        data_list.append((reset_time, file_name))
                     
        if data_list:
            report = ArtifactHtmlReport('Factory Reset')
            report.start_artifact_report(report_folder, 'Factory Reset')
            report.add_script()
            data_headers = ('Timestamp', 'File Name')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Factory Reset'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Factory Reset'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('No Factory Reset data available')

__artifacts__ = {
        "Factory_reset": (
                "Wipe & Setup",
                ('*/misc/bootstat/factory_reset'),
                get_factory_reset)
}