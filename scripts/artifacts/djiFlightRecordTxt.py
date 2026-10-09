__artifacts_v2__ = {
    'djiFlightRecordTxtRecords': {
        'name': 'DJI Drone - TXT Flight Records',
        'description': 'Reads original DJI GO/Fly TXT flight records offline; one row per binary record.',
        'author': 'Neal (@Blackwater1224)',
        'version': '0.2',
        'creation_date': '2026-10-01',
        'last_update_date': '2026-10-05',
        'requirements': 'none',
        'category': 'DJI Drone',
        'notes': 'Versions 1-6 are plain and 7-12 use local XOR decoding. Version 13+ '
                 'telemetry is encrypted and is not decrypted. See TXT Flight Log Summary. '
                 'Timestamp comes from Custom records in UTC. Other records use the preceding '
                 'Custom timestamp, explicitly labeled; records before it have no timestamp. '
                 'Telemetry is not carried between rows. Height is recorded relative height, '
                 'not terrain clearance or MSL. Unknown payloads are retained as hex. '
                 'Layout: https://github.com/lvauvillier/dji-log-parser (MIT), v0.5.7. '
                 'In DF020, RC Return Button, RC Shutter Button and RC Record Button '
                 'are identical: false on decoded RC records and absent on other record types. '
                 'They remain separate fields because each reads a different stored bit.',
        'paths': ('*/DJI/dji.*/FlightRecord/DJIFlightRecord*.txt',
                  '*/Android/data/dji.go.v4/files/FlightRecord/DJIFlightRecord*.txt',
                  '*/Android/data/dji.pilot/files/FlightRecord/DJIFlightRecord*.txt',
                  '*/Android/data/dji.go.v5/files/FlightRecord/DJIFlightRecord*.txt'),
        'output_types': 'all',
        'artifact_icon': 'map-pin',
        'sample_data': {
            'df020_mavic_pro_android': 'VTO/NIST DF020 Android logical | DJI GO 4 4.2.16 '
                'and DJI GO 3.1.11 | 54655 rows from three TXT logs (v11, v11, v9); '
                '7196 June-flight positions within publisher GPS boundary; two record-trailer warnings',
        },
    },
    'djiFlightRecordTxtSummary': {
        'name': 'DJI Drone - TXT Flight Log Summary',
        'description': 'Reports unencrypted flight metadata, encryption and parsing status.',
        'author': 'Neal (@Blackwater1224)',
        'version': '0.2',
        'creation_date': '2026-10-01',
        'last_update_date': '2026-10-05',
        'requirements': 'none',
        'category': 'DJI Drone',
        'notes': 'Metadata is from Details, locally XOR-decoded from Auxiliary Info on version 13+. '
                 'No network requests, API keys, external executable or CSV import. '
                 'DF020 validation includes two June 2018 logs and one older October 2017 log. '
                 'In these three DF020 logs, Sub Street and City are uniform: Map Loading. '
                 'Street and Area are empty in these three logs. '
                 'These columns retain the source Details location strings when present.',
        'paths': ('*/DJI/dji.*/FlightRecord/DJIFlightRecord*.txt',
                  '*/Android/data/dji.go.v4/files/FlightRecord/DJIFlightRecord*.txt',
                  '*/Android/data/dji.pilot/files/FlightRecord/DJIFlightRecord*.txt',
                  '*/Android/data/dji.go.v5/files/FlightRecord/DJIFlightRecord*.txt'),
        'output_types': ['html', 'tsv', 'lava', 'timeline'],
        'artifact_icon': 'file-text',
        'sample_data': {
            'df020_mavic_pro_android': 'VTO/NIST DF020 Android logical | DJI GO 4 4.2.16 '
                'and DJI GO 3.1.11 | 3 rows; two v11 logs with record-trailer warnings '
                'and one v9 log parsed offline',
        },
    },
}

# Author: Neal (@Blackwater1224), https://github.com/Blackwater1224
# Developed with AI assistance from OpenAI Codex for Python implementation,
# test development, and validation.
# Record layouts and XOR key derivation adapted from dji-log-parser v0.5.7.
# Copyright (c) Luc Vauvillier and other contributors (MIT).
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import datetime
import math
import os
import struct
from functools import lru_cache

from scripts.ilapfuncs import artifact_processor, logfunc


def _utc(milliseconds):
    try:
        value = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(milliseconds=milliseconds)
        return value if 2010 < value.year < 2100 else None
    except (OverflowError, ValueError):
        return None


def _crc64(value, data):
    """CRC64/Jones reflected recurrence, caller-supplied seed, no final XOR."""
    for byte in data:
        value ^= byte
        for _ in range(8):
            value = (value >> 1) ^ (0x95AC9329AC4BC9B5 if value & 1 else 0)
    return value


@lru_cache(maxsize=65536)
def _xor_key(record_type, first):
    magic = (0x123456789ABCDEF0 * first) & 0xFFFFFFFFFFFFFFFF
    return _crc64((first + record_type) & 255, struct.pack('<Q', magic)).to_bytes(8, 'little')


def _xor(record_type, payload):
    if not payload:
        raise ValueError('XOR payload lacks key byte')
    key = _xor_key(record_type, payload[0])
    return bytes(byte ^ key[i % 8] for i, byte in enumerate(payload[1:]))


def _decode(record_type, payload, version):
    if version <= 6:
        return payload
    if len(payload) < 2:
        raise ValueError('XOR payload lacks framing bytes')
    return _xor(record_type, payload[:-1])


def _number(value):
    return value if math.isfinite(value) else None


def parse_txt(data):
    """Return (summary dictionary, record dictionaries). Never consult external keys.

    Stop at damaged framing: scanning for a plausible next record would risk
    reporting random bytes as evidence. Earlier valid records remain available.
    """
    if len(data) < 12:
        raise ValueError('Truncated DJI TXT prefix')
    detail_offset, detail_length, version = struct.unpack_from('<QHB', data)
    if not 1 <= version <= 14:
        raise ValueError(f'Unsupported DJI TXT version {version}')
    start = 12 if version < 6 else 100 if version < 12 else 536 if version == 12 else detail_offset
    end = detail_offset if version < 12 else len(data)
    details = detail_offset if version < 12 else 100
    if version >= 13:
        if len(data) < 104 or data[100] != 0:
            raise ValueError('Missing Auxiliary Info; records are encrypted')
        size = struct.unpack_from('<H', data, 101)[0]
        aux_end = 103 + size
        if aux_end > len(data):
            raise ValueError('Truncated Auxiliary Info; records are encrypted')
        auxiliary = _xor(0, data[103:aux_end])
        if len(auxiliary) < 5:
            raise ValueError('Short Auxiliary Info; records are encrypted')
        info_length = struct.unpack_from('<H', auxiliary, 1)[0]
        if 3 + info_length + 2 > len(auxiliary):
            raise ValueError('Truncated auxiliary Details; records are encrypted')
        detail_data = auxiliary[3:3 + info_length]
        if start == 0:
            if aux_end + 3 > len(data) or data[aux_end] != 1:
                raise ValueError('Missing Auxiliary Version; records are encrypted')
            start = aux_end + 3 + struct.unpack_from('<H', data, aux_end + 1)[0]
        if start < aux_end:
            raise ValueError('Records overlap Auxiliary Info; records are encrypted')
    else:
        detail_data = data[details:len(data) if version < 12 else start]
    # Require the known metadata prefix; never pad damaged evidence with zeros.
    detail_end = len(data) if version < 12 else start
    if not (12 <= details <= detail_end <= len(data)) or len(detail_data) < 139:
        raise ValueError('Invalid or truncated DJI Details section')
    if not (start <= end <= len(data)) or (version >= 6 and start < 100):
        raise ValueError('Invalid DJI record bounds')
    if version < 12 and start > details:
        raise ValueError('Records overlap Details section')
    summary = {'version': version, 'detail_length': detail_length,
               'timestamp': _utc(struct.unpack_from('<q', detail_data, 91)[0]),
               'status': 'Encrypted records; DJI keychain required; telemetry not decoded' if version >= 13 else 'Parsed offline',
               'record_count': 0, 'timestamped_count': 0, 'warnings': []}
    for name, offset in (('sub_street', 0), ('street', 20), ('city', 40), ('area', 60)):
        summary[name] = detail_data[offset:offset + 20].split(b'\0')[0].decode('utf-8', errors='replace')
    lon, lat, distance, duration, height, hs, vs = struct.unpack_from('<ddfifff', detail_data, 99)
    summary.update(latitude=_number(lat) if abs(lat) <= 90 else None,
                   longitude=_number(lon) if abs(lon) <= 180 else None,
                   distance_m=_number(distance), duration_s=duration / 1000,
                   max_height_m=_number(height), max_horizontal_speed_ms=_number(hs),
                   max_vertical_speed_ms=_number(vs))
    if summary['timestamp'] is None:
        summary['warnings'].append('Invalid Details start timestamp')
    rows = []
    if version >= 13:
        return summary, rows
    pos, timestamp = start, None
    names = {1: 'OSD', 2: 'Home', 3: 'Gimbal', 4: 'RC', 5: 'Custom',
             7: 'Center Battery', 8: 'Smart Battery', 9: 'App Tip', 10: 'App Warning',
             11: 'RC GPS', 13: 'Recover', 14: 'App GPS', 15: 'Firmware',
             19: 'MC Parameters', 22: 'Smart Battery Group', 24: 'App Serious Warning',
             25: 'Camera', 40: 'Component Serial', 49: 'OFDM', 62: 'RC Display'}
    while pos < end:
        # Embedded JPEGs have separate framing, not the binary record length.
        if data[pos:pos + 2] == b'\xff\xd8':
            jpeg_end = data.find(b'\xff\xd9', pos + 2, end)
            if jpeg_end < 0:
                summary['warnings'].append(f'Truncated JPEG at offset {pos}')
                break
            rows.append({'offset': pos, 'type': 255, 'name': 'Embedded JPEG',
                         'timestamp': timestamp, 'timestamp_basis': 'Preceding Custom record' if timestamp else 'Unavailable',
                         'status': 'Image retained in source; not extracted'})
            pos = jpeg_end + 2
            continue
        if pos + 3 > end:
            summary['warnings'].append(f'Truncated record header at offset {pos}')
            break
        kind, length = data[pos:pos + 2]
        next_pos = pos + 3 + length
        if next_pos > end or data[next_pos - 1] != 255:
            summary['warnings'].append(f'Invalid record length or terminator at offset {pos}; stopped')
            break
        row = {'offset': pos, 'type': kind, 'name': names.get(kind, 'Unknown'),
               'timestamp': timestamp, 'timestamp_basis': 'Preceding Custom record' if timestamp else 'Unavailable',
               'status': 'Decoded', 'payload_hex': ''}
        try:
            payload = _decode(kind, data[pos + 2:next_pos - 1], version)
            row['payload_hex'] = payload.hex()
            if kind == 1:
                if len(payload) < 50:
                    raise ValueError('Short OSD payload')
                lon, lat, altitude, sx, sy, sz, pitch, roll, yaw = struct.unpack_from('<dd7h', payload)
                lon, lat = math.degrees(lon), math.degrees(lat)
                valid = math.isfinite(lat) and math.isfinite(lon) and abs(lat) <= 90 and abs(lon) <= 180 and (lat != 0 or lon != 0)
                row.update(latitude=lat if valid else None, longitude=lon if valid else None,
                           altitude=altitude / 10, speed=math.hypot(sx, sy) / 10,
                           speed_x=sx / 10, speed_y=sy / 10, speed_z=sz / 10,
                           pitch=pitch / 10, roll=roll / 10, heading=yaw / 10,
                           satellites=payload[36], battery=payload[40], flight_time=struct.unpack_from('<H', payload, 42)[0] / 10)
                if not valid:
                    row['status'] = 'Decoded; position unavailable or invalid'
            elif kind == 3:
                if len(payload) < 6:
                    raise ValueError('Short Gimbal payload')
                p, r, y = struct.unpack_from('<3h', payload)
                row.update(gimbal_pitch=p / 10, gimbal_roll=r / 10, gimbal_yaw=y / 10)
            elif kind == 2:
                if len(payload) < 24:
                    raise ValueError('Short Home payload')
                lon, lat, altitude = struct.unpack_from('<ddf', payload)
                lon, lat = math.degrees(lon), math.degrees(lat)
                valid = math.isfinite(lat) and math.isfinite(lon) and abs(lat) <= 90 and abs(lon) <= 180 and (lat != 0 or lon != 0)
                row.update(home_latitude=lat if valid else None, home_longitude=lon if valid else None,
                           home_altitude=_number(altitude / 10), home_recorded=bool(payload[20] & 1),
                           return_height=struct.unpack_from('<H', payload, 22)[0])
            elif kind == 4:
                if len(payload) < 13:
                    raise ValueError('Short RC payload')
                a, e, t, r, g = struct.unpack_from('<5H', payload)
                row.update(rc_aileron=a, rc_elevator=e, rc_throttle=t, rc_rudder=r, rc_gimbal=g,
                           rc_return=bool(payload[11] & 8), rc_shutter=bool(payload[12] & 64),
                           rc_record=bool(payload[12] & 128))
            elif kind == 8:
                if len(payload) < 27:
                    raise ValueError('Short Smart Battery payload')
                row.update(battery_time=struct.unpack_from('<H', payload)[0],
                           battery_voltage=struct.unpack_from('<H', payload, 24)[0] / 1000,
                           battery=payload[26])
            elif kind == 25:
                if len(payload) < 2:
                    raise ValueError('Short Camera payload')
                # Photo state is a multibit enum: only state 1 means single photo.
                row.update(camera_photo=((payload[0] & 56) >> 3) == 1,
                           camera_recording=bool(payload[0] & 192), camera_sd=bool(payload[1] & 2))
                if len(payload) >= 24:
                    row.update(camera_mode=payload[4], camera_record_time=struct.unpack_from('<H', payload, 21)[0])
            elif kind == 5:
                if len(payload) < 18:
                    raise ValueError('Short Custom payload')
                hs, distance, ms = struct.unpack_from('<ffq', payload, 2)
                timestamp = _utc(ms)
                row.update(timestamp=timestamp, timestamp_basis='Custom record UTC' if timestamp else 'Invalid Custom timestamp',
                           speed=_number(hs), distance=_number(distance))
                if timestamp is None:
                    row['status'] = 'Invalid Custom timestamp'
            elif kind in (9, 10, 24):
                row['message'] = payload.decode('utf-8', errors='replace').rstrip('\0')
            else:
                row['status'] = 'Payload retained; fields not yet implemented'
        except (ValueError, struct.error) as exc:
            row['status'] = str(exc)
            if kind == 5:
                timestamp = None
                row.update(timestamp=None, timestamp_basis='Invalid Custom record')
        rows.append(row)
        pos = next_pos
    summary['record_count'] = len(rows)
    summary['timestamped_count'] = sum(row.get('timestamp') is not None for row in rows)
    if summary['warnings']:
        summary['status'] = 'Partial parse; see warnings'
    return summary, rows


def _files(context):
    for path in dict.fromkeys(str(p) for p in context.get_files_found()):
        if not os.path.basename(path).startswith('DJIFlightRecord') or not path.lower().endswith('.txt'):
            continue
        relative = str(context.get_relative_path(path)).replace('\\', '/')
        try:
            with open(path, 'rb') as handle:
                summary, rows = parse_txt(handle.read())
            yield path, relative, summary, rows
        except (OSError, ValueError, struct.error) as exc:
            logfunc(f'DJI TXT: {relative}: {exc}')
            yield path, relative, {'status': f'Could not parse: {exc}'}, []


@artifact_processor
def djiFlightRecordTxtRecords(context):
    fields = ('timestamp', 'latitude', 'longitude', 'altitude', 'speed', 'heading',
              'gimbal_pitch', 'gimbal_roll', 'gimbal_yaw', 'speed_x', 'speed_y', 'speed_z',
              'pitch', 'roll', 'satellites', 'battery', 'flight_time', 'distance',
              'home_latitude', 'home_longitude', 'home_altitude', 'home_recorded', 'return_height',
              'rc_aileron', 'rc_elevator', 'rc_throttle', 'rc_rudder', 'rc_gimbal',
              'rc_return', 'rc_shutter', 'rc_record', 'battery_voltage', 'battery_time',
              'camera_photo', 'camera_recording', 'camera_sd', 'camera_mode', 'camera_record_time',
              'type', 'name', 'offset', 'timestamp_basis', 'status', 'message', 'payload_hex')
    headers = (('Timestamp', 'datetime'), 'Latitude', 'Longitude', 'Relative Height (m)',
               'Horizontal Speed (m/s)', 'Heading (degrees)', 'Gimbal Pitch (degrees)',
               'Gimbal Roll (degrees)', 'Gimbal Yaw (degrees)', 'Speed X (m/s)', 'Speed Y (m/s)',
               'Speed Z (m/s)', 'Pitch (degrees)', 'Roll (degrees)', 'GPS Satellites',
               'Battery (%)', 'Flight Time (s)', 'Distance (m)',
               'Home Latitude', 'Home Longitude', 'Home Altitude (m, recorded)', 'Home Recorded', 'Return Height (m)',
               'RC Aileron (raw)', 'RC Elevator (raw)', 'RC Throttle (raw)', 'RC Rudder (raw)', 'RC Gimbal (raw)',
               'RC Return Button', 'RC Shutter Button', 'RC Record Button', 'Battery Voltage (V)', 'Battery Useful Time (s)',
               'Camera Single Photo', 'Camera Recording', 'Camera SD Present', 'Camera Mode (raw)', 'Camera Record Time (s)',
               'Record Type', 'Record Name',
               'Record Offset', 'Timestamp Basis', 'Decode Status', 'Message', 'Decoded Payload Hex',
               'Log Version', 'Source File')
    output, sources = [], []
    for path, relative, summary, rows in _files(context):
        sources.append(path)
        output.extend(tuple(row.get(field) for field in fields)
                      + (summary['version'], relative) for row in rows)
    return headers, output, '\n'.join(sources)


@artifact_processor
def djiFlightRecordTxtSummary(context):
    fields = ('timestamp', 'version', 'status', 'record_count', 'timestamped_count',
              'latitude', 'longitude', 'distance_m', 'duration_s', 'max_height_m',
              'max_horizontal_speed_ms', 'max_vertical_speed_ms', 'sub_street', 'street', 'city', 'area')
    headers = (('Timestamp', 'datetime'), 'Log Version', 'Status', 'Record Count', 'Timestamped Records',
               'Start Latitude', 'Start Longitude', 'Total Distance (m)', 'Total Time (s)',
               'Maximum Relative Height (m)', 'Maximum Horizontal Speed (m/s)',
               'Maximum Vertical Speed (m/s)', 'Sub Street', 'Street', 'City', 'Area', 'Warnings', 'Source File')
    output, sources = [], []
    for path, relative, summary, _ in _files(context):
        sources.append(path)
        output.append(tuple(summary.get(field) for field in fields)
                      + ('; '.join(summary.get('warnings', [])), relative))
    return headers, output, '\n'.join(sources)
