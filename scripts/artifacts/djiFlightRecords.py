__artifacts_v2__ = {
    "djiFlightRecordDatGps": {
        "name": "DJI Drone - Flight GPS Track (MCDatFlightRecords)",
        "description": "Decodes the aircraft flight-controller DAT logs the DJI GO / DJI "
                       "Pilot apps cache on the mobile device and reports the recorded GPS "
                       "track: one row per positional record with its UTC timestamp, latitude "
                       "and longitude.",
        "author": "@riasramadan, @AlexisBrignoni, Claude",
        "creation_date": "2026-08-10",
        "last_update_date": "2026-08-10",
        "requirements": "none",
        "category": "DJI Drone",
        "notes": "Source files: */DJI/<app>/FlightRecord/MCDatFlightRecords/*.DAT, the flight "
                 "controller logs the DJI mobile apps copy from the aircraft. The container is "
                 "the DJI DAT format: a 'BUILD' header, then records framed by a 0x55 start "
                 "byte, a length byte, a type and a per-record ticket number, each closed by a "
                 "CRC-16 the parser verifies before trusting the record. Records begin at "
                 "offset 256 when the header carries the 'DJI_LOG_V3' marker and at 128 "
                 "otherwise. Positional records (type 2096) carry their payload XOR-obfuscated "
                 "by the low byte of the record ticket number; after that step the first 16 "
                 "bytes are the GPS date, GPS time, longitude and latitude as 1e7-scaled "
                 "integers. The remaining payload bytes hold further telemetry that this "
                 "artifact does not decode.\n"
                 "Timestamp is the GPS date and time from the record, reported as UTC (the "
                 "value the satellites provide); it is not adjusted to any local zone. "
                 "Latitude and Longitude are the stored integers divided by 1e7.\n"
                 "The DAT record framing, CRC and positional layout follow the DJI DAT format "
                 "documented by the CsvView / DatCon community tooling, carried here from the "
                 "closed contribution in ALEAPP PR #660.\n"
                 "Validation: decoded against the VTO Labs / NIST CFReDS drone dataset DF020 "
                 "(DJI Mavic Pro). Every decoded position for the 2018-06-19 flights falls "
                 "inside the data sheet's stated GPS boundary in Colorado and on the stated "
                 "flight date, so timestamp and coordinate decoding are corpus-verified against "
                 "known ground truth.\n"
                 "The paired DJIFlightRecord *.txt files in the same FlightRecord folder are a "
                 "separate, later container; their positional records are encrypted from format "
                 "version 11 onward and are not recoverable offline, so this artifact reads the "
                 "DAT logs, which are not encrypted.",
        "paths": ('*/DJI/*/FlightRecord/MCDatFlightRecords/*.DAT',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "df020_mavic_pro_android": "VTO/NIST DF020 DJI Mavic Pro | 4159 rows from 2 MCDat "
                                       "flight logs; every position on the stated flight date "
                                       "and within the dataset's Colorado GPS boundary",
        },
    }
}

import datetime
import os
import struct

from scripts.ilapfuncs import artifact_processor, logfunc

# CRC-16 lookup used to validate each DAT record. From the DJI DAT format as
# documented by the CsvView / DatCon community tooling (ALEAPP PR #660).
_CRC_TABLE = (
    0x0000, 0x1189, 0x2312, 0x329B, 0x4624, 0x57AD, 0x6536, 0x74BF, 0x8C48, 0x9DC1, 0xAF5A, 0xBED3, 0xCA6C, 0xDBE5, 0xE97E, 0xF8F7,
    0x1081, 0x0108, 0x3393, 0x221A, 0x56A5, 0x472C, 0x75B7, 0x643E, 0x9CC9, 0x8D40, 0xBFDB, 0xAE52, 0xDAED, 0xCB64, 0xF9FF, 0xE876,
    0x2102, 0x308B, 0x0210, 0x1399, 0x6726, 0x76AF, 0x4434, 0x55BD, 0xAD4A, 0xBCC3, 0x8E58, 0x9FD1, 0xEB6E, 0xFAE7, 0xC87C, 0xD9F5,
    0x3183, 0x200A, 0x1291, 0x0318, 0x77A7, 0x662E, 0x54B5, 0x453C, 0xBDCB, 0xAC42, 0x9ED9, 0x8F50, 0xFBEF, 0xEA66, 0xD8FD, 0xC974,
    0x4204, 0x538D, 0x6116, 0x709F, 0x0420, 0x15A9, 0x2732, 0x36BB, 0xCE4C, 0xDFC5, 0xED5E, 0xFCD7, 0x8868, 0x99E1, 0xAB7A, 0xBAF3,
    0x5285, 0x430C, 0x7197, 0x601E, 0x14A1, 0x0528, 0x37B3, 0x263A, 0xDECD, 0xCF44, 0xFDDF, 0xEC56, 0x98E9, 0x8960, 0xBBFB, 0xAA72,
    0x6306, 0x728F, 0x4014, 0x519D, 0x2522, 0x34AB, 0x0630, 0x17B9, 0xEF4E, 0xFEC7, 0xCC5C, 0xDDD5, 0xA96A, 0xB8E3, 0x8A78, 0x9BF1,
    0x7387, 0x620E, 0x5095, 0x411C, 0x35A3, 0x242A, 0x16B1, 0x0738, 0xFFCF, 0xEE46, 0xDCDD, 0xCD54, 0xB9EB, 0xA862, 0x9AF9, 0x8B70,
    0x8408, 0x9581, 0xA71A, 0xB693, 0xC22C, 0xD3A5, 0xE13E, 0xF0B7, 0x0840, 0x19C9, 0x2B52, 0x3ADB, 0x4E64, 0x5FED, 0x6D76, 0x7CFF,
    0x9489, 0x8500, 0xB79B, 0xA612, 0xD2AD, 0xC324, 0xF1BF, 0xE036, 0x18C1, 0x0948, 0x3BD3, 0x2A5A, 0x5EE5, 0x4F6C, 0x7DF7, 0x6C7E,
    0xA50A, 0xB483, 0x8618, 0x9791, 0xE32E, 0xF2A7, 0xC03C, 0xD1B5, 0x2942, 0x38CB, 0x0A50, 0x1BD9, 0x6F66, 0x7EEF, 0x4C74, 0x5DFD,
    0xB58B, 0xA402, 0x9699, 0x8710, 0xF3AF, 0xE226, 0xD0BD, 0xC134, 0x39C3, 0x284A, 0x1AD1, 0x0B58, 0x7FE7, 0x6E6E, 0x5CF5, 0x4D7C,
    0xC60C, 0xD785, 0xE51E, 0xF497, 0x8028, 0x91A1, 0xA33A, 0xB2B3, 0x4A44, 0x5BCD, 0x6956, 0x78DF, 0x0C60, 0x1DE9, 0x2F72, 0x3EFB,
    0xD68D, 0xC704, 0xF59F, 0xE416, 0x90A9, 0x8120, 0xB3BB, 0xA232, 0x5AC5, 0x4B4C, 0x79D7, 0x685E, 0x1CE1, 0x0D68, 0x3FF3, 0x2E7A,
    0xE70E, 0xF687, 0xC41C, 0xD595, 0xA12A, 0xB0A3, 0x8238, 0x93B1, 0x6B46, 0x7ACF, 0x4854, 0x59DD, 0x2D62, 0x3CEB, 0x0E70, 0x1FF9,
    0xF78F, 0xE606, 0xD49D, 0xC514, 0xB1AB, 0xA022, 0x92B9, 0x8330, 0x7BC7, 0x6A4E, 0x58D5, 0x495C, 0x3DE3, 0x2C6A, 0x1EF1, 0x0F78,
)

_GPS_RECORD_TYPE = 2096


def _record_crc(chunk):
    value = 13970
    for byte in chunk:
        value = (value >> 8) ^ _CRC_TABLE[(byte ^ value) & 0xFF]
    return value


def _iter_gps_records(data):
    """Yield (gps_date, gps_time, longitude, latitude) for each positional record.

    date and time are the integers YYYYMMDD and HHMMSS as stored; longitude and
    latitude are already divided by 1e7.
    """
    if data[16:21] != b'BUILD':
        return
    pos = 256 if data[242:252] == b'DJI_LOG_V3' else 128
    end = len(data)
    while pos < end:
        if data[pos] != 0x55:
            nxt = data.find(0x55, pos + 1)
            if nxt == -1:
                return
            pos = nxt
            continue
        record_len = data[pos + 1]
        if record_len < 10 or pos + record_len > end:
            nxt = data.find(0x55, pos + 1)
            if nxt == -1:
                return
            pos = nxt
            continue
        crc = _record_crc(data[pos:pos + record_len - 2])
        if crc & 0xFF != data[pos + record_len - 2] or crc >> 8 != data[pos + record_len - 1]:
            nxt = data.find(0x55, pos + 1)
            if nxt == -1:
                return
            pos = nxt
            continue
        record_type = (data[pos + 5] << 8) + data[pos + 4]
        if record_type == _GPS_RECORD_TYPE:
            ticket = struct.unpack('<I', data[pos + 6:pos + 10])[0]
            payload = bytes(b ^ (ticket % 256) for b in data[pos + 10:pos + record_len - 2])
            if len(payload) >= 16:
                gps_date, gps_time, lon, lat = struct.unpack('<IIii', payload[:16])
                yield gps_date, gps_time, lon / 1e7, lat / 1e7
        pos += record_len


def _to_utc(gps_date, gps_time):
    """Combine the stored YYYYMMDD / HHMMSS integers into an aware UTC datetime."""
    try:
        year, month, day = gps_date // 10000, (gps_date // 100) % 100, gps_date % 100
        hour, minute, second = gps_time // 10000, (gps_time // 100) % 100, gps_time % 100
        return datetime.datetime(year, month, day, hour, minute, second,
                                 tzinfo=datetime.timezone.utc)
    except ValueError:
        return ''


@artifact_processor
def djiFlightRecordDatGps(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.lower().endswith('.dat'):
            continue
        source_path = file_found
        try:
            with open(file_found, 'rb') as handle:
                data = handle.read()
        except OSError as exc:
            logfunc(f'DJI flight record - could not read {file_found}: {exc}')
            continue

        relative = context.get_relative_path(file_found)
        name = os.path.basename(file_found)
        for gps_date, gps_time, lon, lat in _iter_gps_records(data):
            # A record with no fix stores zeroes; drop it rather than plot 0,0.
            if not lat and not lon:
                continue
            data_list.append((_to_utc(gps_date, gps_time), lat, lon, name, relative))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Latitude',
        'Longitude',
        'Flight File',
        'Source File',
    )
    return data_headers, data_list, source_path
