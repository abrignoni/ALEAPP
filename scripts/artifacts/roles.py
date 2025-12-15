import xml.etree.ElementTree as ET 

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows

def get_roles(files_found, report_folder, seeker, wrap_text):
    
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
        elif 'users' in parts:
            user = parts[-2]
            ver = 'Android 10'
        elif 'misc_de' in parts:
            user = parts[-4]
            ver = 'Android 11'
        
        if user == 'mirror':
            continue
        else:
            try:
                ET.parse(file_found)
            except ET.ParseError:
                print('Parse error - Non XML file.') #change to logfunc
                err = 1
                
            if err == 0:
                tree = ET.parse(file_found)
                root = tree.getroot()

                for elem in root:
                    holder = ''
                    role = elem.attrib['name']
                    for subelem in elem:
                        holder = subelem.attrib['name']
                        
                    data_list.append((role, holder))
                
                if len(data_list) > 0:
                    report = ArtifactHtmlReport('App Roles')
                    report.start_artifact_report(report_folder, f'{ver} Roles_{user}')
                    report.add_script()
                    data_headers = ('Role', 'Holder')
                    report.write_artifact_data_table(data_headers, data_list, file_found)
                    report.end_artifact_report()
                    
                    tsvname = f'App Roles_{user}'
                    tsv(report_folder, data_headers, data_list, tsvname)

__artifacts__ = {
        "roles": (
                "App Roles",
                ('*/system/users/*/roles.xml','*/misc_de/*/apexdata/com.android.permission/roles.xml'),
                get_roles)
}
            