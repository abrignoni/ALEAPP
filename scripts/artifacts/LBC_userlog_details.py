import codecs
import csv
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, kmlgen, tsv, is_platform_windows

def get_LBC_userlog_details(files_found, report_folder, seeker, wrap_text):
    
    report = ArtifactHtmlReport('LBC Userlog Details Data')
    report.start_artifact_report(report_folder, f'LBC Userlog Details Data')
    report.add_script()
    
    for file_found in files_found:
        file_found = str(file_found)
        
        data_list = []
        counter = 0
        inner_counter = 0
        with open(file_found, "r") as f:
            for line in f:
                if counter > 0:
                    if inner_counter == 0:
                        data_a = (line.split(',', 4))
                        timestamp = (data_a[0].strip('"')) #Timestamp
                        ip = (data_a[2]) #IP
                    if inner_counter == 7: #this could be done better for sure. Done in a hurry.
                        data_b = (line.split(',', 4))
                        data_b = (data_b[4].split(',', 1))
                        data_b = (data_b[1].strip('"'))
                        json_data = (data_b[0:-2])
                        try:
                            extra_info = json.loads(json_data)
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
                        inner_counter = 0
                        continue
                    inner_counter = inner_counter + 1
                
                counter = counter +1
                    
        
        data_headers = ('Timestamp', 'IP', 'Latitude','Longitude', 'Location', 'Country Code')
        report.write_artifact_data_table(data_headers, data_list, file_found)
        
        data = file_found.split('/')
        username = (data[-2])
        
        tsvname = f'{username}_LBC_userlog_details'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        kmlactivity = f'{username}_LBC_userlog_details'
        kmlgen(report_folder, kmlactivity, data_list, data_headers)

    report.end_artifact_report()
        
    