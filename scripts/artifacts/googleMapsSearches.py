import blackboxprotobuf
from datetime import *
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, convert_utc_human_to_timezone, kmlgen, timeline

def get_googleMapsSearches(files_found, report_folder, seeker, wrap_text):
    data_list = []
    
    typess = {'1': {'type': 'message', 'message_typedef': {'2': {'type': 'int', 'name': ''}, '4': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}, '2': {'type': 'bytes', 'name': ''}, '3': {'type': 'bytes', 'name': ''}, '4': {'type': 'bytes', 'name': ''}, '5': {'type': 'message', 'message_typedef': {'3': {'type': 'double', 'name': ''}, '4': {'type': 'double', 'name': ''}}, 'name': ''}, '10': {'type': 'int', 'name': ''}, '11': {'type': 'bytes', 'name': ''}, '12': {'type': 'int', 'name': ''}, '13': {'type': 'int', 'name': ''}, '14': {'type': 'int', 'name': ''}, '17': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}, '3': {'type': 'bytes', 'name': ''}, '4': {'type': 'message', 'message_typedef': {'3': {'type': 'fixed64', 'name': ''}, '4': {'type': 'fixed64', 'name': ''}}, 'name': ''}, '5': {'type': 'bytes', 'name': ''}, '6': {'type': 'bytes', 'name': ''}, '8': {'type': 'fixed32', 'name': ''}, '9': {'type': 'int', 'name': ''}, '10': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}, '2': {'type': 'bytes', 'name': ''}}, 'name': ''}, '11': {'type': 'int', 'name': ''}, '13': {'type': 'message', 'message_typedef': {'4': {'type': 'bytes', 'name': ''}, '5': {'type': 'message', 'message_typedef': {'3': {'type': 'int', 'name': ''}, '4': {'type': 'int', 'name': ''}, '5': {'type': 'int', 'name': ''}, '6': {'type': 'int', 'name': ''}}, 'name': ''}}, 'name': ''}, '14': {'type': 'bytes', 'name': ''}, '16': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {}, 'name': ''}}, 'name': ''}, '21': {'type': 'bytes', 'name': ''}, '24': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'bytes', 'name': ''}, '4': {'type': 'bytes', 'name': ''}, '5': {'type': 'bytes', 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}}, 'name': ''}, '6': {'type': 'message', 'message_typedef': {'1': {'type': 'message', 'message_typedef': {'1': {'type': 'double', 'name': ''}, '2': {'type': 'double', 'name': ''}, '3': {'type': 'double', 'name': ''}}, 'name': ''}, '3': {'type': 'message', 'message_typedef': {'1': {'type': 'int', 'name': ''}, '2': {'type': 'int', 'name': ''}}, 'name': ''}, '4': {'type': 'fixed32', 'name': ''}}, 'name': ''}, '16': {'type': 'int', 'name': ''}}, 'name': ''}, '9': {'type': 'int', 'name': ''}, '1': {'type': 'bytes', 'name': ''}, '11': {'type': 'bytes', 'name': ''}}, 'name': ''}, '2': {'type': 'bytes', 'name': ''}}
    counter = 0
    for file_found in files_found:
        counter = counter + 1
        with open(file_found, 'rb') as f:
            data = f.read()
            arreglo = (data)
            pb = arreglo[8:]
            values, types = blackboxprotobuf.decode_message(pb, typess)
        latitude = ''
        longitude = ''
        for x, y in values.items():
            if x == '1':
                if isinstance(y, list):
                    for things in y:
                        timeofsearch = things['2']
                        place = things.get('4','')
                        if place != '':
                            if things['4'].get('5', '') != '':
                                latitude = (things['4']['5']['3'])
                                longitude = (things['4']['5']['4'])
                            elif things['4'].get('6','') != '':	
                                latitude = (things['4']['6']['1']['3'])
                                longitude = (things['4']['6']['1']['2'])
                            else:
                                latitude = ''
                                longitude = ''
                                
                        url = things.get('11', 'No URL')
                        timeofsearch = datetime.fromtimestamp(timeofsearch/1000000, tz=timezone.utc)
                        timeofsearch = convert_utc_human_to_timezone(timeofsearch, 'UTC')
                        if isinstance(place, str):
                            pass
                        else:
                            place = (place['1'].decode())
                        
                        if isinstance(url, str):
                            pass
                        else:
                            url = url.decode()
                        
                        data_list.append((timeofsearch,place,latitude,longitude,url))
                        latitude = ''
                        longitude = ''
                elif isinstance(y, dict):
                    timeofsearch = y['2']
                    place = y.get('4','')
                    if place != '':
                        if y['4'].get('5', '') != '':
                            latitude = (y['4']['5']['3'])
                            longitude = (y['4']['5']['4'])
                        elif things['4'].get('6','') != '':	
                            latitude = (y['4']['6']['1']['3'])
                            longitude = (y['4']['6']['1']['2'])
                        else:
                            latitude = ''
                            longitude = ''
                            
                    url = y.get('11', 'No URL')
                    timeofsearch = datetime.fromtimestamp(timeofsearch/1000000, tz=timezone.utc)
                    timeofsearch = convert_utc_human_to_timezone(timeofsearch, 'UTC')
                    if isinstance(place, str):
                        pass
                    else:
                        place = (place['1'].decode())
                        
                    if isinstance(url, str):
                        pass
                    else:
                        url = url.decode()
                        
                    data_list.append((timeofsearch,place,latitude,longitude,url))
                    latitude = ''
                    longitude = ''
                        
                        
                        
        if len(data_list) > 0:
            report = ArtifactHtmlReport('Google Maps Searches')
            report.start_artifact_report(report_folder, f'Google Maps Searches - {counter}')
            report.add_script()
            data_headers = ('Timestamp', 'Place','Latitude','Longitude','URL')
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Google Maps Searches - {counter}'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Google Maps Searches - {counter}'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
            kmlactivity = f'Google Maps Searches - {counter}'
            kmlgen(report_folder, kmlactivity, data_list, data_headers)
            
        else:
            logfunc(f'No Google Maps Searches available')

__artifacts__ = {
        "googleMapsSearches": (
                "GEO Location",
                ('*/com.google.android.apps.maps/files/new_recent_history_cache_search.cs'),
                get_googleMapsSearches)
}