import os
import datetime
import pathlib
import xml.etree.ElementTree as ET
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, abxread, checkabx, logdevinfo

def oplist(opvalue):
    thisdict = {
        "26": "Camera",
        "1": "Location",
        "27": "Microphone"
    }
    
    result = thisdict.get(opvalue)
    if result is None:
        result = opvalue
    else:
        return result
    
def timestampcalc(timevalue):
    timestamp = (datetime.datetime.utcfromtimestamp(int(timevalue)/1000).strftime('%Y-%m-%d %H:%M:%S'))
    return timestamp

def get_discreteNative(files_found, report_folder, seeker, wrap_text):
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        filename = str(pathlib.Path(file_found).name)
        
        if os.path.isfile(file_found):
            #check if file is abx
            if (checkabx(file_found)):
                multi_root = False
                tree = abxread(file_found, multi_root)
            else:
                tree = ET.parse(file_found)
            root = tree.getroot()
        
            for elem in root:
                for subelem1 in elem:
                    ptag = subelem1.tag
                    ptagattrib = subelem1.attrib
                    ptagattrib = ptagattrib["pn"]
                    for subelem2 in subelem1:
                        otag = subelem2.tag
                        otagattrib = subelem2.attrib
                        otagattrib = otagattrib['op']
                        for subelem3 in subelem2:
                            atag = subelem3.tag
                            atagattrib = subelem3.attrib
                            atagattrib = atagattrib.get('at', '')
                            
                            for subelem4 in subelem3:
                                etag = subelem4.tag
                                etagattrib = subelem4.attrib
                                ntattrib = etagattrib.get('nt')
                                ndattrib = etagattrib.get('nd')
                                if ndattrib is None:
                                    ndattrib = ''
                                else:
                                    ndattrib = round(int(ndattrib) / 1000, 1)
                        data_list.append((timestampcalc(ntattrib), ptagattrib, atagattrib, oplist(otagattrib), ndattrib, filename ))
                    
    if data_list:
        report = ArtifactHtmlReport('Privacy Dashboard')
        report.start_artifact_report(report_folder, 'Privacy Dashboard')
        report.add_script()
        data_headers = ('Timestamp', 'Bundle', 'Module', 'Operation', 'Usage in Seconds', 'Source Filename')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Privacy Dashboard'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Privacy Dashboard'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Privacy Dashboard data available')
        
__artifacts__ = {
        "DiscreteNative": (
                "Privacy Dashboard",
                ('*/system/appops/discrete/**'),
                get_discreteNative)
}