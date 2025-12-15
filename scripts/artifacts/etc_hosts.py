import codecs
import csv

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows

def get_etc_hosts(files_found, report_folder, seeker, wrap_text):
    data_list = []
    file_found = str(files_found[0])
    
    with codecs.open(file_found, 'r', 'utf-8-sig') as csvfile:
        for row in csvfile:
            sline = '\t'.join(row.split())
            sline = sline.split('\t')
            sline_one = sline[0]
            sline_two = sline[1]
            if (sline_one == '127.0.0.1' and sline_two == 'localhost') or \
                (sline_one == '::1' and sline_two == 'ip6-localhost'):
                pass # Skipping the defaults, so only anomaly entries are seen
            else:
                 data_list.append((sline_one, sline_two))

    if len(data_list) > 0:
        report = ArtifactHtmlReport('Etc Hosts')
        report.start_artifact_report(report_folder, f'Etc Hosts')
        report.add_script()
        data_headers = ('IP Address', 'Hostname')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Etc Hosts'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc(f'No etc hosts file available, or nothing significant found.')
        
__artifacts__ = {
        "Etc_hosts": (
                "Etc Hosts",
                ('*/system/etc/hosts'),
                get_etc_hosts)
}