from datetime import datetime
import os
from pathlib import Path

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows

def get_oldpowerOffReset(files_found, report_folder, seeker, wrap_text):
    data_list = []
    for file_found in files_found:
    
        filename = os.path.basename(file_found)
        location = os.path.dirname(file_found)
    
        with open(file_found, 'r') as f:
            for line in f:
                if '/' in line and len(line) == 18:
                    fecha = line.strip()
                    fecha = (datetime.strptime(fecha,'%y/%m/%d %H:%M:%S'))
                    
                    reason = next(f)
                    reason = reason.split(':')[1].replace('\n','')
                    
                    data_list.append((fecha, reason, filename))
    
    if len(data_list) > 0:
        report = ArtifactHtmlReport('Power Off Reset')
        report.start_artifact_report(report_folder, f'Power Off Reset')
        report.add_script()
        data_headers = ('Timestamp', 'Reason', 'Filename')
        report.write_artifact_data_table(data_headers, data_list, location)
        report.end_artifact_report()
        
        tsvname = f'Power Off Reset'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc(f'Power Off Reset file available')

__artifacts__ = {
        "oldpowerOffReset": (
                "Power Events",
                ('*/log/power_off_reset_reason.txt','*/log/power_off_reset_reason_backup.txt'),
                get_oldpowerOffReset)
}