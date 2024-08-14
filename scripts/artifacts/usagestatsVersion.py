import csv
import scripts.artifacts.artGlobals 

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, logdevinfo, is_platform_windows

def get_usagestatsVersion(files_found, report_folder, seeker, wrap_text, time_offset):
    data_list = []
    file_found = str(files_found[0])

    with open(file_found, "r") as f:
        for line in f:
            splits = line.split(';')
            totalvalues = len(splits)
            if totalvalues == 3:
                logfunc(f"Android version {str(splits[0])}")
                logdevinfo(f"<b>Android version per Usagestats: </b>{splits[0]}")
                scripts.artifacts.artGlobals.versionf = splits[0]
                data_list.append(('Android Version', splits[0]))
                
                logdevinfo(f"<b>Codename per Usagestats: </b>{splits[1]}")
                data_list.append(('Codename', splits[1]))
                
                logdevinfo(f"<b>Build version per Usagestats: </b>{splits[2]}")
                data_list.append(('Build version', splits[2]))
            if totalvalues == 5:
                logfunc(f"Android version {str(splits[0])}")
                scripts.artifacts.artGlobals.versionf = splits[0]
                logdevinfo(f"<b>Android version per Usagestats: </b>{splits[0]}")
                data_list.append(('Android Version', splits[0]))
                
                logdevinfo(f"<b>Codename per Usagestats: </b>{splits[1]}")
                data_list.append(('Codename', splits[1]))
                
                logdevinfo(f"<b>Country Specific Code per Usagestats: </b>{splits[3]}")
                data_list.append(('Country Specific Code', splits[3]))
                
                logdevinfo(f"<b>Build version per Usagestats: </b>{splits[2]}")
                data_list.append(('Build Version', splits[2]))

    if len(data_list) > 0:
        report = ArtifactHtmlReport('OS Version')
        report.start_artifact_report(report_folder, f'OS Version')
        report.add_script()
        data_headers = ('Key', 'Value')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'OS Version'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc(f'No OS Version file available')

__artifacts__ = {
    "usagestatsVersion": (
        "Usage Stats",
        ('*/system/usagestats/*/version', '*/system_ce/*/usagestats/version'),
        get_usagestatsVersion)
}

__leapp_info__ = {
    "usagestatsVersion": {
        "is_required": True
    }
}