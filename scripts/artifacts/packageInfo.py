import datetime
import os
import xmltodict
import xml.etree.ElementTree as etree
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, abxread, checkabx

is_windows = is_platform_windows()
slash = '\\' if is_windows else '/' 

class Package:
    # Represents an app
    def __init__(self, name, ft, install_time, update_time, install_originator, installer, code_path, public_flags, private_flags):
        self.name = name
        self.ft = ft
        self.install_time = install_time
        self.update_time = update_time
        self.install_originator = install_originator
        self.installer = installer
        self.code_path = code_path
        self.public_flags = public_flags
        self.private_flags = private_flags

def ReadUnixTimeMs(unix_time_ms): # Unix timestamp is time epoch beginning 1970/1/1
    '''Returns datetime object, or empty string upon error'''
    if unix_time_ms not in ( 0, None, ''):
        try:
            if isinstance(unix_time_ms, str):
                unix_time_ms = float.fromhex(unix_time_ms)
            return datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=unix_time_ms/1000)
        except (ValueError, OverflowError, TypeError) as ex:
            logfunc("ReadUnixTimeMs() Failed to convert timestamp from value " + str(unix_time_ms) + " Error was: " + str(ex))
    return ''

def get_package_info(files_found, report_folder, seeker, wrap_text):
    packages = []
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.find('{0}mirror{0}'.format(slash)) >= 0:
            # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data
            continue
        elif os.path.isdir(file_found): # skip folders (there shouldn't be any)
            continue
        
        file_name = os.path.basename(file_found)
        if (checkabx(file_found)):
            multi_root = False
            tree = abxread(file_found, multi_root)
            xlmstring = (etree.tostring(tree.getroot()).decode())
            doc = xmltodict.parse(xlmstring)
        else:
            with open(file_found) as fd:
                doc = xmltodict.parse(fd.read())
        
        package_dict = doc.get('packages', {}).get('package', {})
        for package in package_dict:
            name = package.get('@name', '')
            ft = ReadUnixTimeMs(package.get('@ft', None))
            it = ReadUnixTimeMs(package.get('@it', None))
            ut = ReadUnixTimeMs(package.get('@ut', None))
            install_originator = package.get('@installOriginator', '')
            installer = package.get('@installer', '')
            code_path = package.get('@codePath', '')
            public_flags  = hex(int(package.get('@publicFlags', 0)) & (2**32-1))
            private_flags = hex(int(package.get('@privateFlags', 0)) & (2**32-1))
            package = Package(name, ft, it, ut, install_originator, installer, code_path, public_flags, private_flags)
            packages.append(package)
        
        if len(packages):
            break

    if report_folder[-1] == slash: 
        folder_name = os.path.basename(report_folder[:-1])
    else:
        folder_name = os.path.basename(report_folder)
    entries = len(packages)
    if entries > 0:
        description = "All packages (user installed, oem installed and system) appear here. Many of these are not user apps"
        report = ArtifactHtmlReport('Packages')
        report.start_artifact_report(report_folder, 'Packages', description)
        report.add_script()
        data_headers = ('ft','Name', 'Install Time', 'Update Time', 'Install Originator', 'Installer', 'Code Path', 'Public Flags', 'Private Flags')
        data_list = []
        for p in packages:
            data_list.append( (p.ft, p.name, p.install_time, p.update_time, p.install_originator, p.installer, p.code_path, p.public_flags, p.private_flags) )

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Packages'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Packages'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No package data available')            

__artifacts__ = {
        "package_info": (
                "Installed Apps",
                ('*/system/packages.xml'),
                get_package_info)
}