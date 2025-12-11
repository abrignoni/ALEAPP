import xml.etree.ElementTree as ET  
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import timeline, tsv, is_platform_windows, open_sqlite_db_readonly


def get_usageHistory(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('usage-history.xml'):
            break

    data_list = []

    tree = ET.parse(file_found)
    root = tree.getroot()

    for elem in root:
        for subelem in elem:
            pkg = elem.attrib['name']
            subitem = subelem.attrib['name']
            time = subelem.attrib['lrt']
            if time != ' ':
                time = int(time)
                time = datetime.datetime.utcfromtimestamp(time/1000)
            data_list.append((time, pkg, subitem))

    if len(data_list) > 0:

        description = 'Usage History'
        report = ArtifactHtmlReport('Usage History')
        report.start_artifact_report(report_folder, 'Usage History', description)
        report.add_script()
        data_headers = ('Timestamp', 'Package', 'Subitem', )
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()

        tsvname = 'Usage History'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = 'Usage History'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('Usage History data available')

__artifacts__ = {
        "Usagehistory": (
                "App Interaction",
                ('*/usage-history.xml'),
                get_usageHistory)
}