import sqlite3
import datetime
import struct
import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_cachelocation(files_found, report_folder, seeker, wrap_text):

    source_file = ''
    
    for file_found in files_found:
        
        file_name = str(file_found)
        source_file = file_found.replace(seeker.data_folder, '')
 
        data_list = []
 
        # code to parse the cache.wifi and cache.cell taken from https://forensics.spreitzenbarth.de/2011/10/28/decoding-cache-cell-and-cache-wifi-files/
        cacheFile = open(str(file_name), 'rb')
        (version, entries) = struct.unpack('>hh', cacheFile.read(4))
        # Check the number of entries * 32 (entry record size) to see if it is bigger then the file, this is a indication the file is malformed or corrupted
        cache_file_size = os.stat(file_name).st_size
        if ((entries * 32) < cache_file_size):            
            i = 0
            while i < entries:
                key = cacheFile.read(struct.unpack('>h', cacheFile.read(2))[0])
                (accuracy, confidence, latitude, longitude, readtime) = struct.unpack('>iiddQ', cacheFile.read(32))
                timestamp = readtime/1000
                i = i + 1
                
                starttime = datetime.datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                data_list.append((accuracy, confidence, latitude, longitude, starttime))
            cacheFile.close()

            report = ArtifactHtmlReport('Cache Locations')
            report.start_artifact_report(report_folder, 'Cache Locations')
            report.add_script()
            data_headers = ('Accuracy', 'Confidence', 'Latitude', 'Longitude', 'Readtime') # Don't remove the comma, that is required to make this a tuple as there is only 1 element

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Cache Locations'
            tsv(report_folder, data_headers, data_list, tsvname, source_file)

            tlactivity = f'Cache Locations'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No Cachelocation Logs found')

__artifacts__ = {
        "Cache Location": (
                "GEO Location",
                ('*/com.google.android.location/files/cache.cell/cache.cell', '*/com.google.android.location/files/cache.wifi/cache.wifi'),
                get_cachelocation)
}