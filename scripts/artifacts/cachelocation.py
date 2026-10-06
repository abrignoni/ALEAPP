__artifacts_v2__ = {
    "get_cachelocation": {
        "name": "Cache Location",
        "description": "Parses the records of the Google location cache files cache.cell and cache.wifi: accuracy, confidence, latitude, longitude and a time read as Unix milliseconds. The record layout follows the forensic blog post 'Decoding cache.cell and cache.wifi files' (forensics.spreitzenbarth.de, 28 October 2011), which describes cache.wifi as a Wi-Fi router database with the MAC and GPS position of the router and cache.cell as a database of mobile cells and their GPS position. Each record is keyed in the file by an identifier reported as reversible hex. The coordinates are reported as stored and are not established here as positions of the device.",
        "author": "@markmckinnon, @AlexisBrignoni, Codex",
        "creation_date": "2021-03-17",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "GEO Location",
        "notes": "Key (hex) retains the length-prefixed bytes without identifier interpretation. "
                 "The existing entries*32 < file size guard is retained; it is not a full format validation. "
                 "Short records are diagnosed and already decoded records retained. No version-specific layout claim is added.",
        "paths": ('*/com.google.android.location/files/cache.cell/cache.cell', '*/com.google.android.location/files/cache.wifi/cache.wifi'),
        "output_types": "standard",
        "artifact_icon": "map-pin",
    }
}

import datetime
import os
import struct

from scripts.ilapfuncs import artifact_processor, logfunc


@artifact_processor
def get_cachelocation(context):
    files_found = context.get_files_found()
    data_list = []
    sources = []
    row_sources = []
    for file_found in files_found:
        file_name = str(file_found)
        source = context.get_relative_path(file_name)
        first_row = len(data_list)
        # Existing layout follows the Spreitzenbarth research cited above.
        try:
            with open(file_name, 'rb') as cache_file:
                header = cache_file.read(4)
                if len(header) != 4:
                    logfunc(f'Cache Location: short header in {source}')
                    continue
                _version, entries = struct.unpack('>hh', header)
                cache_file_size = os.stat(file_name).st_size
                if not (entries * 32) < cache_file_size:
                    logfunc(f'Cache Location: skipped by size guard in {source}: '
                            f'entries={entries}, size={cache_file_size}')
                    continue
                for index in range(entries):
                    length = cache_file.read(2)
                    if len(length) != 2:
                        logfunc(f'Cache Location: short key length in {source}, record {index + 1}')
                        break
                    key_length = struct.unpack('>h', length)[0]
                    if key_length < 0:
                        logfunc(f'Cache Location: negative key length in {source}, record {index + 1}')
                        break
                    key = cache_file.read(key_length)
                    if len(key) != key_length:
                        logfunc(f'Cache Location: short key in {source}, record {index + 1}')
                        break
                    body = cache_file.read(32)
                    if len(body) != 32:
                        logfunc(f'Cache Location: short body in {source}, record {index + 1}')
                        break
                    accuracy, confidence, latitude, longitude, readtime = struct.unpack('>iiddQ', body)
                    readtime_utc = datetime.datetime.fromtimestamp(readtime / 1000, datetime.timezone.utc)
                    data_list.append((readtime_utc, key.hex(), accuracy, confidence, latitude, longitude))
                    row_sources.append(source)
        except OSError as error:
            logfunc(f'Cache Location: could not read {source}: {error}')
        if len(data_list) > first_row and file_name not in sources:
            sources.append(file_name)
    data_headers = (('Readtime', 'datetime'), 'Key (hex)', 'Accuracy', 'Confidence', 'Latitude', 'Longitude')
    if len(sources) > 1:
        data_headers += ('Source File',)
        data_list = [row + (source,) for row, source in zip(data_list, row_sources)]
    return data_headers, data_list, '\n'.join(sources)
