# pylint: disable=W0612,W0613
__artifacts_v2__ = {
    "get_cachelocation": {
        "name": "Cache Location",
        "description": "",
        "author": "",
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
def get_cachelocation(files_found, report_folder, seeker, wrap_text):

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
