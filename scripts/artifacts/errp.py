import os
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

def get_errp(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('eRR.p'):
            continue # Skip all other files
        
        data_list =[]
        timestamp = status = info_one = info_two = ''
        with open(file_found, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('\n'):
                    pass
                elif line.startswith('LOGM'):
                    pass
                elif line == '':
                    pass
                else:	
                    line = line.split('|')
                    timestamp = line[0]
                    status = line[1]
                    info_one = line[2]
                    info_two = line[3]
                    data_list.append((timestamp, status, info_one, info_two))
                    timestamp = status = info_one = info_two = ''
                            
                        
        if data_list:
            report = ArtifactHtmlReport('Samsung eRR.p')
            report.start_artifact_report(report_folder, 'Samsung eRR.p')
            report.add_script()
            data_headers = ('Timestamp', 'Status', 'Info Field', 'Info Field')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Samsung Samsung eRR.p'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Samsung Samsung eRR.p'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Samsung Samsung eRR.p data available')
            
__artifacts__ = {
        "Errp": (
                "Wipe & Setup",
                ('*/data/system/users/service/eRR.p'),
                get_errp)
}