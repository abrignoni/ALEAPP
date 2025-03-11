__artifacts_v2__ = {
    "appSemloc": {
        "name": "App Semantic Locations",
        "description": "App Semantic Locations",
        "author": "Alexis 'Brigs' Brignoni",
        "version": "1",
        "date": "2024/06/21",
        "requirements": "",
        "category": "App Semantic Locations",
        "notes": "Thanks to Alex Caithness for the ccc_leveldb libraries",
        "paths": (
            '*/com.google.android.gms/app_semanticlocation_rawsignal_db/*'
        ),
        "function": "get_appSemloc"
    }
}
import pathlib
import json
import blackboxprotobuf
from datetime import *
from scripts.ccl import ccl_leveldb


from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, timeline, kmlgen 

def get_appSemloc(files_found, report_folder, seeker, wrap_text):
    
    data_list = []
    in_dirs = set(pathlib.Path(x).parent for x in files_found)
    for in_db_dir in in_dirs:
        leveldb_records = ccl_leveldb.RawLevelDb(in_db_dir)
        
        for record in leveldb_records.iterate_records_raw():
            #print(record.seq, record.user_key, record.value)
            record_sequence = record.seq
            record_key = record.user_key
            record_value = record.value
            origin = str(record.origin_file)
            
            p = str(pathlib.Path(origin).parent.name)
            f = str(pathlib.Path(origin).name)
            pf = f'{p}/{f}'
            
            value = record_value
            value, types = blackboxprotobuf.decode_message(value)
            
            check = value.get('1')
            if check is not None:
                
                latlongrecord = value['1'].get('1')
                if latlongrecord is not None:
                    #print(record_key)
                    #print(latlongrecord)
                    timestamp = value['2']
                    timestamp = datetime.fromtimestamp(timestamp/1000, tz=timezone.utc)
                    latitude = latlongrecord['1']/1e7
                    longitude = latlongrecord['2']/1e7
                    accuracy = latlongrecord['3']/1000
                    
                    data_list.append((timestamp,record_sequence,latitude,longitude,accuracy,pf))
        
    if len(data_list) > 0:
        maindirectory = str(pathlib.Path(in_db_dir).parent)
        description = ''
        report = ArtifactHtmlReport('App Semantic Location')
        report.start_artifact_report(report_folder, 'App Semantic Location', description)
        report.add_script()
        data_headers = ('Timestamp','Rec. Sequence','Latitude','Longitude','Horizontal Acc.','Origin')
        report.write_artifact_data_table(data_headers, data_list, maindirectory)
        report.end_artifact_report()
            
        tsvname = 'App Semantic Location'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'App Semantic Location'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
        kmlactivity = 'App Semantic Location'
        kmlgen(report_folder, kmlactivity, data_list, data_headers)    
    else:
        logfunc('No App Semantic Location Data available')
                        
                
    