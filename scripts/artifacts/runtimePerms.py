import xml.etree.ElementTree as ET 

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows

def get_runtimePerms(files_found, report_folder, seeker, wrap_text):
    
    run = 0
    slash = '\\' if is_platform_windows() else '/' 
    
    for file_found in files_found:
        file_found = str(file_found)
        
        data_list = []
        run = run + 1
        err = 0
        
        
        parts = file_found.split(slash)
        if 'mirror' in parts:
            user = 'mirror'
        elif 'system' in parts:
            user = parts[-2]
        elif 'misc_de' in parts:
            user = parts[-4]
        
        if user == 'mirror':
            continue
        else:
            try:
                ET.parse(file_found)
            except ET.ParseError:
                logfunc('Parse error - Non XML file.') 
                err = 1
                
            if err == 0:
                tree = ET.parse(file_found)
                root = tree.getroot()

                for elem in root:
                    #print(elem.tag)
                    usagetype = elem.tag
                    name = elem.attrib['name']
                    #print("Usage type: "+usagetype)
                    #print('name')
                    for subelem in elem:
                        permission = subelem.attrib['name']
                        granted = subelem.attrib['granted']
                        flags = subelem.attrib['flags']
                        
                        data_list.append((usagetype, name, permission, granted, flags))
    
                if len(data_list) > 0:
                    report = ArtifactHtmlReport('Runtime Permissions')
                    report.start_artifact_report(report_folder, f'Runtime Permissions_{user}')
                    report.add_script()
                    data_headers = ('Type', 'Name', 'Permission', 'Granted?','Flag')
                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    
                    tsvname = f'Runtime Permissions_{user}'
                    tsv(report_folder, data_headers, data_list, tsvname)
                
__artifacts__ = {
        "runtimePerms": (
                "Permissions",
                ('*/system/users/*/runtime-permissions.xml','*/misc_de/*/apexdata/com.android.permission/runtime-permissions.xml'),
                get_runtimePerms)
}