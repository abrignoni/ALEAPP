import os
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, convert_local_to_utc

def get_errp(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('eRR.p'):
            continue # Skip all other files
        
        data_list = []
        timestamp = event = code = details = ''
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
                    if(len(line) == 1):
                        timestamp = line[0].strip()
                        timestamp_utc = str(convert_local_to_utc(timestamp))
                        event = ''
                        code = ''
                        details = ''
                    elif(len(line) == 2):
                        timestamp = line[0].strip()
                        timestamp_utc = str(convert_local_to_utc(timestamp))
                        event = line[1].strip()
                        code = ''
                        details = ''                  
                    elif(len(line) == 3):
                        timestamp = line[0].strip()
                        timestamp_utc = str(convert_local_to_utc(timestamp))
                        event = line[1].strip()                
                        code = line[2].strip()
                        details = ''
                    elif(len(line) == 4):
                        timestamp = line[0].strip()
                        timestamp_utc = str(convert_local_to_utc(timestamp))
                        event = line[1].strip()
                        code = line[2].strip()
                        details = line[3].strip()
                    
                    data_list.append((timestamp_utc,timestamp,event,code,details))
                    timestamp = event = code = details = ''
                            
        if data_list:
            report = ArtifactHtmlReport('Samsung eRR.p')
            report.start_artifact_report(report_folder, 'Samsung eRR.p')
            report.add_script()
            data_headers = ('Timestamp','Timestamp (Local)','Event','Code','Details')
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
                ('*/system/users/service/eRR.p'),
                get_errp)
}