__artifacts_v2__ = {
    "graphics_stats": {
        "name": "Graphics Stats Per App Per Day",
        "description": "Rendering the platform recorded for an app on one day, with the window it covers and the app version",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Installed Apps",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 30 rows",
            "anne_a15": "38 rows",
            "cookbook_a11": "Android 11 | 9 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "0 rows",
            "emu_a15_oss_v10": "Android 15 | 49 rows",
            "emu_a15_oss_v11": "Android 15 | 55 rows",
            "emu_a15_oss_v12": "Android 15 | 59 rows",
            "emu_a15_oss_v13": "Android 15 | 62 rows",
            "emu_a15_oss_v14": "Android 15 | 63 rows",
            "emu_a15_oss_v15": "Android 15 | 72 rows",
            "emu_a15_oss_v16": "Android 15 | 82 rows",
            "emu_a15_oss_v17": "Android 15 | 90 rows",
            "emu_a15_oss_v2": "Android 15 | 32 rows",
            "emu_a15_oss_v3": "Android 15 | 33 rows",
            "emu_a15_oss_v4": "Android 15 | 51 rows",
            "emu_a15_oss_v5": "Android 15 | 68 rows",
            "emu_a15_oss_v6": "Android 15 | 74 rows",
            "emu_a15_oss_v7": "Android 15 | 62 rows",
            "emu_a15_oss_v8": "Android 15 | 63 rows",
            "emu_a15_oss_v9": "Android 15 | 65 rows",
            "falken_a326u_a13": "Android 13 | 40 rows",
            "galaxys10_a10": "Android 10 | 104 rows",
            "hc_pixel8pro_a16": "Android 16 | 23 rows",
            "hc_pixel8pro_a17": "Android 17 | 24 rows",
            "hc_pixel8pro_a17_ail": "0 rows",
            "kevin_pocox7_a15": "82 rows",
            "pixel3_a11": "Android 11 | 108 rows",
            "pixel3_a12": "Android 12 | 51 rows",
            "pixel7a_a14": "Android 14 | 116 rows",
            "russell_a14": "Android 14 | 24 rows",
            "russell_pixel6a_a13": "Android 13 | 54 rows",
            "s20fe_a13": "Android 13 | 40 rows",
            "samsunga53_a14": "Android 14 | 47 rows",
            "samsungs20_a13": "35 rows",
            "sharon_a13": "Android 13 | 30 rows",
            "sharon_a14": "Android 14 | 17 rows",
            "userb2_a13": "10 rows",
        },
        "notes": "One row per file under system/graphicsstats. The path carries three of the "
                 "columns on its own: the platform stores each record as "
                 "graphicsstats/<bucket>/<package>/<version code>/total, where the bucket folder "
                 "is Unix milliseconds naming a day. It was exactly midnight UTC on all 1,690 "
                 "records across the 33 registered images that carry them. "
                 "Package and Version Code are read from inside the file and reported from there "
                 "rather than from the folder names, and the two agreed on every record checked: "
                 "600 of 600 across ten real device images spanning Android 10 to 17, and 90 of "
                 "90 on the emulator image. That agreement is what makes the folder layout safe "
                 "to read as an index of what rendered on a given day.\n"
                 "The file is the platform's own GraphicsStatsProto behind a four byte "
                 "little-endian header holding the file format version, which was 1 on every one "
                 "of those records. It is read with a reader that takes only the declared fields rather "
                 "than a schema-less decoder, so a nested field is always decoded as the message "
                 "it is declared to be. Reference: Android Open Source Project, "
                 "libs/hwui/service/GraphicsStatsService.cpp, which defines sCurrentFileVersion 1 "
                 "and sHeaderSize 4 and writes the header before the proto, and "
                 "core/proto/android/service/graphicsstats.proto, which declares the fields; read "
                 "from the main branch 2026-09-06.\n"
                 "Stats Start and Stats End are Unix milliseconds reported as UTC. They are not a "
                 "simple session: the same source merges each new profile into the existing file "
                 "and keeps the earliest start and the latest end it has seen for that package, "
                 "version and day, so the pair bounds the rendering the platform folded into that "
                 "file rather than marking one continuous period. Frame counters are the summary "
                 "the platform stores and are reported as given. Pipeline is the declared enum, 0 "
                 "unknown, 1 GL and 2 Vulkan, named from the same proto.\n"
                 "A record survives the app being uninstalled: on a test emulator an app was "
                 "removed and its graphicsstats folder, naming the package and version, was still "
                 "present afterwards. A row is evidence the platform recorded rendering for that "
                 "package on that day. It does not establish that a person was looking at the "
                 "screen, and an absent day is not evidence the app did not run: the platform "
                 "does not keep a folder for every past day, and on the 33 registered images "
                 "carrying these records the number of day folders "
                 "ranged from 1 to 5. The rule that governs that limit was not sourced.",
        "paths": ('*/system/graphicsstats/*/*/*/total',),
        "output_types": "standard",
        "artifact_icon": "activity",
    },
}

import datetime
import os
import struct

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, logfunc

HEADER_SIZE = 4
PIPELINE = {0: 'Unknown', 1: 'GL', 2: 'Vulkan'}
# Field numbers from core/proto/android/service/graphicsstats.proto
F_PACKAGE, F_VERSION, F_START, F_END, F_SUMMARY, F_PIPELINE, F_UID = 1, 2, 3, 4, 5, 8, 9
SUMMARY_FIELDS = (
    (1, 'total_frames'), (2, 'janky_frames'), (3, 'missed_vsync'),
    (4, 'high_input_latency'), (5, 'slow_ui_thread'), (6, 'slow_bitmap_upload'),
    (7, 'slow_draw'), (8, 'missed_deadline'),
)


def _varint(buf, pos):
    result = shift = 0
    while pos < len(buf):
        byte = buf[pos]
        pos += 1
        result |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return result, pos
        shift += 7
        if shift > 63:
            break
    raise ValueError('truncated varint')


def _fields(buf, want):
    """Decode only the wanted field numbers, skipping every other field by its length."""
    out = {}
    pos = 0
    while pos < len(buf):
        key, pos = _varint(buf, pos)
        num, wire = key >> 3, key & 7
        if wire == 0:
            value, pos = _varint(buf, pos)
        elif wire == 2:
            length, pos = _varint(buf, pos)
            value, pos = buf[pos:pos + length], pos + length
            if len(value) != length:
                raise ValueError('truncated length delimited field')
        elif wire == 5:
            value, pos = buf[pos:pos + 4], pos + 4
        elif wire == 1:
            value, pos = buf[pos:pos + 8], pos + 8
        else:
            raise ValueError(f'unsupported wire type {wire}')
        if num in want:
            out[num] = value
    return out


def _ms(value):
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value) / 1000)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _day(bucket):
    """The bucket folder name as a plain date. It is Unix milliseconds naming the day."""
    if not bucket or not bucket.isdigit():
        return ''
    try:
        moment = datetime.datetime.fromtimestamp(int(bucket) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError):
        return ''
    return moment.strftime('%Y-%m-%d')


@artifact_processor
def graphics_stats(context):
    data_headers = (
        ('Day', 'date'), ('Stats Start', 'datetime'), ('Stats End', 'datetime'),
        'Package', 'Version Code', 'Total Frames', 'Janky Frames', 'Missed Vsync',
        'High Input Latency', 'Slow UI Thread', 'Slow Bitmap Upload', 'Slow Draw',
        'Missed Deadline', 'Pipeline', 'UID', 'File Version', 'Source File')
    data_list = []
    sources = []

    for file_found in sorted(context.get_files_found()):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        if os.path.basename(file_found) != 'total':
            continue
        parts = file_found.replace('\\\\', '/').split('/')
        bucket = parts[-4] if len(parts) >= 4 else ''
        try:
            with open(file_found, 'rb') as handle:
                raw = handle.read()
        except OSError as error:
            logfunc(f'Graphics Stats: could not read {file_found}: {error}')
            continue
        if len(raw) <= HEADER_SIZE:
            logfunc(f'Graphics Stats: {file_found} is too short to hold a record')
            continue
        version = struct.unpack('<I', raw[:HEADER_SIZE])[0]
        try:
            top = _fields(raw[HEADER_SIZE:],
                          {F_PACKAGE, F_VERSION, F_START, F_END, F_SUMMARY, F_PIPELINE, F_UID})
        except ValueError as error:
            logfunc(f'Graphics Stats: {file_found} did not decode: {error}')
            continue
        summary = {}
        if isinstance(top.get(F_SUMMARY), (bytes, bytearray)):
            try:
                summary = _fields(top[F_SUMMARY], {n for n, _ in SUMMARY_FIELDS})
            except ValueError as error:
                logfunc(f'Graphics Stats: {file_found} summary did not decode: {error}')
        package = top.get(F_PACKAGE, b'')
        if isinstance(package, (bytes, bytearray)):
            package = package.decode('utf-8', 'replace')
        pipeline = top.get(F_PIPELINE)
        data_list.append((
            _day(bucket),
            _ms(top.get(F_START)), _ms(top.get(F_END)),
            package, top.get(F_VERSION, ''),
            *[summary.get(n, '') for n, _ in SUMMARY_FIELDS],
            PIPELINE.get(pipeline, pipeline if pipeline is not None else ''),
            top.get(F_UID, ''), version,
            context.get_relative_path(file_found),
        ))
        if file_found not in sources:
            sources.append(file_found)

    return data_headers, data_list, '\n'.join(sources)
