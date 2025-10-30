__artifacts_v2__ = {
    "sharedProto": {
        "name": "Shared Proto Data",
        "description": "Shared Proto data from Samsung Browser",
        "author": "@AlexisBrignoni",
        "version": "0.0.1",
        "date": "2024-07-23",
        "requirements": "none",
        "category": "Samsung Browser",
        "notes": "",
        "paths": ('*/data/com.sec.android.app.sbrowser/app_sbrowser/Default/shared_proto_db/*'),
        "function": "get_sharedProto"
    }
}
import pathlib
import sqlite3
import textwrap
import blackboxprotobuf
import traceback
from scripts.ccl import ccl_leveldb
from datetime import datetime, timedelta

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, kmlgen, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_sharedProto(files_found, report_folder, seeker, wrap_text):
    
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
        
            recordkey = record_key.decode()
            #print(record_value)
            protostuff, types = blackboxprotobuf.decode_message(record_value)
            
            data = (protostuff.get('1','nodata'))
            if data == 'nodata':
                pass
            else:
                #print(protostuff)
                
                try:
                    #guid = protostuff['1']['1']
                    #print(guid.decode())
                    #print(protostuff)
                    
                    urlone = protostuff['1']['4']['1']
                    if isinstance(urlone, list):
                        agg = ''
                        for url in urlone:
                            
                            agg = url.decode() + '<br><br>' + agg
                    else:
                        agg = urlone.decode()
                        
                    domain = protostuff['1']['4']['2']
                    urltwo = protostuff['1']['4']['4'].decode()
                    timestamp = protostuff['1']['4'].get('9','')
                    timestamptwo = protostuff['1']['4'].get('16','')
                    if timestamptwo != '':
                        seconds = timestamptwo / 1000
                        
                        # Define the epoch start time (January 1, 1601)
                        epoch_start = datetime(1601, 1, 1)
                        
                        # Calculate the final datetime
                        timestamptwo = epoch_start + timedelta(seconds=seconds)
                    """
                    if isinstance(timestamp, bytes):
                        timestamp = timestamp.decode()
                        timestamp = timestamp.split(' ')
                        
                        year = timestamp[3]
                        day = timestamp[1]
                        time = timestamp[4]
                        month = monthletter(timestamp[2])
                        timestamp = (f'{year}-{month}-{day} {time}')
                    else:
                        pass
                    """
                    content = (protostuff['1']['4']['13'].decode())
                    data_list.append((timestamptwo,timestamp,recordkey,record_sequence,agg,urltwo,domain,content,pf))
                except:
                    pass
                    
                    
        
        
    if len(data_list) > 0:
        maindirectory = str(pathlib.Path(in_db_dir).parent)
        report = ArtifactHtmlReport('Samsung Browser Shared Proto')
        report.start_artifact_report(report_folder, 'Samsung Browser Shared Proto')
        report.add_script()
        data_headers = ('Timestamp','Timestamp B','Record Key','Record Sequence','ULR One','URL Two','Domain','Data','Origin')
        
        report.write_artifact_data_table(data_headers, data_list, maindirectory,html_escape=False)
        report.end_artifact_report()
        
        tsvname = f'Samsung Browser Shared Proto'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Samsung Browser Shared Proto'
        timeline(report_folder, tlactivity, data_list, data_headers)
    
        
    else:
        logfunc('No Samsung Browser Shared Proto data available')
        
    