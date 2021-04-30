import codecs
import csv
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, kmlgen, tsv, is_platform_windows

def get_LBC_userlog(files_found, report_folder, seeker, wrap_text):
    
    report = ArtifactHtmlReport('LBC Userlog Data')
    report.start_artifact_report(report_folder, f'LBC Userlog Data')
    report.add_script()
    
    for file_found in files_found:
        file_found = str(file_found)
        
        data_list = []
        counter = 0
        with open(file_found, "r") as f:
            for line in f:
                if counter > 0:
                    data = (line.split(',', 5))
                    timestamp = (data[2].strip('"'))
                    ip = (data[3])
                    data1 = (data[5].rsplit(',', 1))
                    json_data = (data1[0].strip('"'))
                    extra_info = json.loads(json_data) #deserialized data variable
                    try:
                        latitude = extra_info['cookies']['lat']
                        longitude = extra_info['cookies']['lon']
                        location_str = extra_info['cookies']['location_string']
                        country_code = extra_info['cookies']['countrycode']
                    except:
                        latitude = ''
                        longitude = ''
                        location_str = ''
                        country_code = ''
                    
                    data_list.append((timestamp, ip, latitude, longitude, location_str, country_code))
                counter = counter + 1
        
        data_headers = ('Timestamp', 'IP', 'Latitude','Longitude', 'Location', 'Country Code')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        
        data = file_found.split('/')
        username = (data[-2])
        
        tsvname = f'{username}_LBC_userlog'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        kmlactivity = f'{username}_LBC_userlog'
        kmlgen(report_folder, kmlactivity, data_list, data_headers)

    report.end_artifact_report()
        
    