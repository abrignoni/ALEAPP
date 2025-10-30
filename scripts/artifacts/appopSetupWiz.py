import os
import datetime
import xml.etree.ElementTree as ET
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, abxread, checkabx

def get_appopSetupWiz(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('appops.xml'):
            continue # Skip all other files
        
        data_list = []
        #check if file is abx
        if (checkabx(file_found)):
            multi_root = False
            tree = abxread(file_found, multi_root)
        else:
            tree = ET.parse(file_found)
        root = tree.getroot()
        
        for elem in root.iter('pkg'):
            if elem.attrib['n'] == 'com.google.android.setupwizard':
                pkg = elem.attrib['n']
                for subelem in elem:
                    #print(subelem.attrib)
                    for subelem2 in subelem:
                        #print(subelem2.attrib)
                        for subelem3 in subelem2:
                            test = subelem3.attrib.get('t', 0)
                            if int(test) > 0:
                                timestamp = (datetime.datetime.utcfromtimestamp(int(subelem3.attrib['t'])/1000).strftime('%Y-%m-%d %H:%M:%S'))
                            else:
                                timestamp = ''
                            data_list.append((timestamp, pkg))
        if data_list:
            report = ArtifactHtmlReport('Appops.xml Setup Wizard')
            report.start_artifact_report(report_folder, 'Appops.xml Setup Wizard')
            report.add_script()
            data_headers = ('Timestamp','Package')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Appops Setup Wizard data'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Appops Setup Wizard data'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Appops Setup Wizard data available')

__artifacts__ = {
        "appopSetupWiz": (
                "Wipe & Setup",
                ('*/system/appops.xml'),
                get_appopSetupWiz)
}