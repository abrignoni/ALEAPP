import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, is_platform_windows

def get_build(files_found, report_folder, seeker):
    data_list = []
    file_found = str(files_found[0])
    with open(file_found, "r") as f:
        for line in f: 
            splits = line.split('=')
            if splits[0] == 'ro.product.vendor.manufacturer':
                key = 'Manufacturer'
                value = splits[1]
            elif splits[0] == 'ro.product.vendor.brand':
                key = 'Brand'
                value = splits[1]
                data_list.append((key, value))
            elif splits[0] == 'ro.product.vendor.model':
                key = 'Model'
                value = splits[1]
                data_list.append((key, value))
            elif splits[0] == 'ro.product.vendor.device':
                key = 'Device'
                value = splits[1]
                data_list.append((key, value))
            elif splits[0] == 'ro.vendor.build.version.release':
                key = 'Android Version'
                value = splits[1]
                data_list.append((key, value))
            elif splits[0] == 'ro.vendor.build.version.sdk':
                key = 'SDK'
                value = splits[1]
                data_list.append((key, value))
            elif splits[0] == 'ro.system.build.version.release':
                key = ''
                value = splits[1]
                data_list.append((key, value))
            elif splits[0] == 'ro.system.build.version.release':
                key = ''
                value = splits[1]
                data_list.append((key, value))
    
    itemqty = len(data_list)
    if itemqty > 0:
        report = ArtifactHtmlReport('Build Info')
        report.start_artifact_report(report_folder, f'Build Info')
        report.add_script()
        data_headers = ('Key', 'Value')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
    else:
        logfunc(f'No Build Info data available')    
   