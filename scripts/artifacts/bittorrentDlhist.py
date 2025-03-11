import bencoding
import hashlib
import datetime
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows 

def timestampcalc(timevalue):
    timestamp = (datetime.datetime.utcfromtimestamp(int(timevalue)/1000).strftime('%Y-%m-%d %H:%M:%S'))
    return timestamp

def get_bittorrentDlhist(files_found, report_folder, seeker, wrap_text):

    data_list = []
    for file_found in files_found:
        file_found = str(file_found)

        with open(file_found, 'rb') as f:
            decodedDict = bencoding.bdecode(f.read())
        
        for key, value in decodedDict.items():
            if key.decode() == 'records':
                for x in value:
                    time = timestampcalc(x[b'a'])
                    filename = x[b'n'].decode()
                    filepath = x[b's'].decode()
                    print(filepath)
                data_list.append((time,filename,filepath,textwrap.fill(file_found.strip(), width=25)))

    # Reporting
    title = "BitTorrent Download Info"
    report = ArtifactHtmlReport(title)
    report.start_artifact_report(report_folder, title)
    report.add_script()
    data_headers = ('Record Timestamp', 'Filename', 'Download File Path', 'Source File')
    report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Data'])
    report.end_artifact_report()
    
    tsv(report_folder, data_headers, data_list, title)

__artifacts__ = {
    "bittorrentDlhist": (
        "BitTorrent",
        ('*/dlhistory*.config.bak','*/dlhistory*.config'),
        get_bittorrentDlhist)
}