import json
import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows 
from scripts.parse3 import ParseProto

def get_wellbeingaccount(files_found, report_folder, seeker, wrap_text):
    file_found = str(files_found[0])
    content = ParseProto(file_found)
    
    content_json_dump = json.dumps(content, indent=4, sort_keys=True, ensure_ascii=False)
    parsedContent = str(content_json_dump).encode(encoding='UTF-8',errors='ignore')
    
    report = ArtifactHtmlReport('Wellbeing Account')
    report.start_artifact_report(report_folder, 'Account Data')
    report.add_script()
    data_headers = ('Protobuf Parsed Data', 'Protobuf Data')
    data_list = []
    data_list.append(('<pre id=\"json\">'+str(parsedContent).replace("\\n", "<br>")+'</pre>', str(content)))
    report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
    report.end_artifact_report()
    
    tsvname = f'wellbeing account'
    tsv(report_folder, data_headers, data_list, tsvname)

__artifacts__ = {
        "wellbeingaccount": (
                "Digital Wellbeing",
                ('*/com.google.android.apps.wellbeing/files/AccountData.pb'),
                get_wellbeingaccount)
}