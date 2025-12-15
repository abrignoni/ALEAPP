import xml.etree.ElementTree as ET 

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, abxread, checkabx

def get_permissions(files_found, report_folder, seeker, wrap_text):
    
    slash = '\\' if is_platform_windows() else '/' 
    
    for file_found in files_found:
        file_found = str(file_found)
        
        data_list_permission_trees = []
        data_list_permissions = []
        data_list_packages_su = []
        err = 0
        user = ''
        
        parts = file_found.split(slash)
        if 'mirror' in parts:
            user = 'mirror'
        
        if user == 'mirror':
            continue
        else:
            try:
                if (checkabx(file_found)):
                    multi_root = False
                    tree = abxread(file_found, multi_root)
                else:
                    tree = ET.parse(file_found)
                
            except ET.ParseError:
                logfunc('Parse error - Non XML file.') 
                err = 1
                
            if err == 0:
                root = tree.getroot()
                
                for elem in root:
                    #print('TAG LVL 1 '+ elem.tag, elem.attrib)
                    #role = elem.attrib['name']
                    #print()
                    if elem.tag == 'permission-trees':
                        for subelem in elem:
                            #print(elem.tag +' '+ subelem.tag, subelem.attrib)
                            data_list_permission_trees.append((subelem.attrib.get('name', ''), subelem.attrib.get('package', '')))
                    elif elem.tag == 'permissions':
                        for subelem in elem:
                            data_list_permissions.append((subelem.attrib.get('name', ''), subelem.attrib.get('package', ''), subelem.attrib.get('protection', '')))
                            #print(elem.tag +' '+ subelem.tag, subelem.attrib)
                    else:
                        for subelem in elem:
                            if subelem.tag == 'perms':
                                for sub_subelem in subelem:
                                    #print(elem.tag, elem.attrib['name'], sub_subelem.attrib['name'], sub_subelem.attrib['granted'] )
                                    
                                    
                                    data_list_packages_su.append((elem.tag, elem.attrib.get('name', ''), sub_subelem.attrib.get('name', ''), sub_subelem.attrib.get('granted', '')))
    
                if len(data_list_permission_trees) > 0:
                    report = ArtifactHtmlReport('Permission Trees')
                    report.start_artifact_report(report_folder, f'Permission Trees')
                    report.add_script()
                    data_headers = ('Name', 'Package')
                    report.write_artifact_data_table(data_headers, data_list_permission_trees, file_found)
                    report.end_artifact_report()
                    
                    tsvname = f'Permission Trees'
                    tsv(report_folder, data_headers, data_list_permission_trees, tsvname)
                    
                if len(data_list_permissions) > 0:
                    report = ArtifactHtmlReport('Permissions')
                    report.start_artifact_report(report_folder, f'Permissions')
                    report.add_script()
                    data_headers = ('Name', 'Package', 'Protection')
                    report.write_artifact_data_table(data_headers, data_list_permissions, file_found)
                    report.end_artifact_report()
                    
                    tsvname = f'Permissions'
                    tsv(report_folder, data_headers, data_list_permissions, tsvname)
                
                if len(data_list_packages_su) > 0:
                    report = ArtifactHtmlReport('Package and Shared User')
                    report.start_artifact_report(report_folder, f'Package and Shared User')
                    report.add_script()
                    data_headers = ('Type', 'Package', 'Permission', 'Granted?')
                    report.write_artifact_data_table(data_headers, data_list_packages_su, file_found)
                    report.end_artifact_report()
                    
                    tsvname = f'Permissions - Packages and Shared User'
                    tsv(report_folder, data_headers, data_list_packages_su, tsvname)

__artifacts__ = {
        "permissions": (
                "Permissions",
                ('*/system/packages.xml'),
                get_permissions)
}