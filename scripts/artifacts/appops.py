import os
import datetime
import xml.etree.ElementTree as ET
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, abxread, checkabx

def get_appops(files_found, report_folder, seeker, wrap_text):

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
            pkg = elem.attrib['n']
            for subelem in elem:
                #print(subelem.attrib)
                for subelem2 in subelem:
                    #print(subelem2.attrib)
                    for subelem3 in subelem2:
                        #print(subelem3.attrib)
                        timesr = subelem3.attrib.get('r')
                        timest = subelem3.attrib.get('t')
                        pp = subelem3.attrib.get('pp')
                        pu = subelem3.attrib.get('pu')
                        n = subelem3.attrib.get('n')
                        id = subelem3.attrib.get('id')
                        if timesr:
                            timestampr = (datetime.datetime.fromtimestamp(int(timesr)/1000).strftime('%Y-%m-%d %H:%M:%S'))
                        else:
                            timestampr = ''
                        if timest:	
                            timestampt = (datetime.datetime.fromtimestamp(int(timest)/1000).strftime('%Y-%m-%d %H:%M:%S'))
                        else:
                            timestampt = ''
                        if not pp:
                            pp = ''
                        if not pu:
                            pu = ''
                        if not n:
                            n = ''
                        if not id:
                            id = ''
                            
                        data_list.append((timestampt, timestampr, pkg, id, pp, pu, n))
                            
                        
        if data_list:
            report = ArtifactHtmlReport('Appops.xml')
            report.start_artifact_report(report_folder, 'Appops.xml')
            report.add_script()
            data_headers = ('Timestamp T', 'Timestamp R', 'PKG', 'ID', 'PP', 'PU', 'N')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Appops.xml data'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Appops.xml data'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No Appops.xml data available')
            
__artifacts__ = {
        "appops": (
                "Permissions",
                ('*/system/appops.xml'),
                get_appops)
}