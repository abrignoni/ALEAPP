__artifacts_v2__ = {
    "snapchat_saved_location": {
        "name": "Snapchat - Last Saved Location",
        "description": "The last location the Snapchat app saved to its "
                       "MixerLocationStore.proto file: latitude, longitude, accuracy and the "
                       "time of the location fix.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-18",
        "last_update_date": "2026-11-18",
        "requirements": "none",
        "category": "Messaging",
        "notes": "Read from com.snapchat.android/files/MixerLocationStore.proto, a single "
                 "protobuf message decoded with the vendored blackboxprotobuf and the field "
                 "types the app's own message class uses. Sources are the app's decompiled "
                 "code (Snapchat versionCode 319422, the base APK installed on "
                 "dragna_pixel9a_a16, decompiled with jadx; the code is obfuscated and jadx "
                 "reported 617 errors). Field meaning was read from that one version; the "
                 "files on the other 7 tested images have the same four fields and wire "
                 "types, and their app versions were not decompiled. The app builds the file "
                 "from an android.location.Location it saves (classes C19450bt6 and C7209Li6,"
                 " where the task is labelled saveLocation; the write is in C3517Fm6, the "
                 "file name in C35723mU8, wired in C34852lv5); which location source supplies"
                 " that Location was not traced: field 1 is getLatitude(), field 2 "
                 "getLongitude() and field 3 getAccuracy(), written as doubles, and field 4 "
                 "getTime(), written as an int64 (message class CUa). Each save overwrites "
                 "the file, so it holds one location. Android documents getTime() as the Unix"
                 " epoch time of the fix in milliseconds, and says the clock that set it "
                 "depends on the provider and can be the device clock; it documents "
                 "getAccuracy() as the estimated horizontal accuracy radius in meters at 68% "
                 "confidence, valid only when the location has an accuracy "
                 "(android.location.Location). The app does not record whether it had one, so"
                 " 0 can mean none. 'Accuracy (m)' is the stored float in its shortest form. "
                 "'Fix Time' is field 4 shown in UTC, and 'Fix Time (as stored)' keeps the "
                 "integer; LAVA keeps Fix Time in whole seconds, so the milliseconds are only"
                 " in the stored column there. The app reads a record whose time is 0 or less"
                 " as no location, and such a file gives no row here. What makes the app save"
                 " a location (which feature or screen) was not traced. A row shows the "
                 "location the app last saved; it does not establish that the user shared it "
                 "or that Snapchat sent it anywhere. On the 8 images listed in sample_data "
                 "the file held one record with a time above 0 each.",
        "paths": ('*/com.snapchat.android/files/MixerLocationStore.proto',),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | com.snapchat.android versionCode 319422 | 1 row",
            "cookbook_a11": "Android 11 | com.snapchat.android | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android | 1 row",
            "hc_pixel8pro_a17": "Android 17 | com.snapchat.android | 1 row",
            "pixel7a_a14": "Android 14 | com.snapchat.android | 1 row",
            "russell_pixel6a_a13": "Android 13 | com.snapchat.android | 1 row",
            "russell_a14": "Android 14 | com.snapchat.android | 1 row",
            "sharon_a14": "Android 14 | com.snapchat.android | 1 row",
        },
    },
}

import os
import struct
from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import unique_files
from scripts.blackboxprotobuf import decode_message
from scripts.ilapfuncs import artifact_processor, logfunc

# Field numbers and types from the app's own message class (latitude, longitude and accuracy
# written as doubles, the fix time as an int64); see the notes.
_TYPEDEF = {
    '1': {'type': 'double', 'name': ''},
    '2': {'type': 'double', 'name': ''},
    '3': {'type': 'double', 'name': ''},
    '4': {'type': 'int', 'name': ''},
}
_DECODE_ERRORS = (ValueError, KeyError, TypeError, IndexError, EOFError)


def _float32_text(value):
    """getAccuracy() is a float the app widens to a double: show its shortest float form."""
    if not isinstance(value, float):
        return ''
    try:
        packed = struct.pack('<f', value)
    except (OverflowError, struct.error):
        return repr(value)
    if struct.unpack('<f', packed)[0] != value:
        return repr(value)  # not a widened float: keep the double as stored
    for digits in range(1, 10):
        text = f'{value:.{digits}g}'
        if struct.pack('<f', float(text)) == packed:
            return repr(float(text))
    return repr(value)


def _utc_ms(value):
    if not isinstance(value, int) or value <= 0:
        return ''
    try:
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


@artifact_processor
def snapchat_saved_location(context):
    data_headers = (('Fix Time', 'datetime'), 'Fix Time (as stored)', ('Latitude', 'latitude'),
                    ('Longitude', 'longitude'), 'Accuracy (m)')
    data_list, sources = [], []
    for file_found in unique_files(context):
        path = str(file_found)
        if os.path.basename(path) != 'MixerLocationStore.proto':
            continue
        sources.append(path)
        with open(path, 'rb') as handle:
            data = handle.read()
        if not data:
            continue
        try:
            message, _ = decode_message(data, _TYPEDEF)
        except _DECODE_ERRORS as error:
            logfunc(f'Snapchat - Last Saved Location: could not decode the file: '
                    f'{type(error).__name__}')
            continue
        stamp = message.get('4')
        # The app reads a record whose time is 0 or less as no location.
        if not isinstance(stamp, int) or stamp <= 0:
            continue
        accuracy = message.get('3')
        data_list.append((
            _utc_ms(stamp), stamp, message.get('1', ''), message.get('2', ''),
            _float32_text(accuracy),
        ))
    return data_headers, data_list, '\n'.join(sources)
