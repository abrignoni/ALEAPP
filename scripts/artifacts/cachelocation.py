# pylint: disable=W0612
__artifacts_v2__ = {
    "get_cachelocation": {
        "name": "Cache Location",
        "description": "Parses the records of the Google location cache files cache.cell and cache.wifi: accuracy, confidence, latitude, longitude and a time read as Unix milliseconds. The record layout follows the forensic blog post 'Decoding cache.cell and cache.wifi files' (forensics.spreitzenbarth.de, 28 October 2011), which describes cache.wifi as a Wi-Fi router database with the MAC and GPS position of the router and cache.cell as a database of mobile cells and their GPS position. Each record is keyed in the file by an identifier this artifact does not report. The coordinates are reported as stored and are not established here as positions of the device.",
        "author": "@markmckinnon",
        "creation_date": "2021-03-17",
        "last_update_date": "2021-03-17",
        "requirements": "none",
        "category": "GEO Location",
        "notes": "",
        "paths": ('*/com.google.android.location/files/cache.cell/cache.cell', '*/com.google.android.location/files/cache.wifi/cache.wifi'),
        "output_types": "standard",
        "artifact_icon": "map-pin",
    }
}

import datetime
import os
import struct

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_cachelocation(context):
    files_found = context.get_files_found()

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_name = str(file_found)
        source_path = file_name

        # code to parse the cache.wifi and cache.cell taken from
        # https://forensics.spreitzenbarth.de/2011/10/28/decoding-cache-cell-and-cache-wifi-files/
        with open(file_name, 'rb') as cacheFile:
            (version, entries) = struct.unpack('>hh', cacheFile.read(4))
            # Check entries * 32 (entry record size) against file size to detect malformed/corrupt files
            cache_file_size = os.stat(file_name).st_size
            if (entries * 32) < cache_file_size:
                i = 0
                while i < entries:
                    key = cacheFile.read(struct.unpack('>h', cacheFile.read(2))[0])
                    (accuracy, confidence, latitude, longitude, readtime) = struct.unpack('>iiddQ', cacheFile.read(32))
                    readtime_utc = datetime.datetime.fromtimestamp(readtime / 1000, datetime.timezone.utc)
                    i = i + 1
                    data_list.append((accuracy, confidence, latitude, longitude, readtime_utc))

    data_headers = ('Accuracy', 'Confidence', 'Latitude', 'Longitude', ('Readtime', 'datetime'))
    return data_headers, data_list, source_path
