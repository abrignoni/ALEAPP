__artifacts_v2__ = {
    "beats_devices": {
        "name": "Beats - Devices",
        "description": "Beats headphones and earbuds the Beats app (com.apple.bnd) keeps a "
                       "record of, with serial numbers, firmware, the stored "
                       "DISCONNECTION_TIME value and the phone location the app saved for the"
                       " device.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Smart Home & Connected Devices",
        "notes": "Read from the Room table table_property_model in "
                 "com.apple.bnd/databases/device_database; the write-ahead log is read when "
                 "it is beside the database. The table stores each property as a name, a "
                 "Bluetooth address and a text value; this artifact gives one report row per "
                 "Bluetooth address. The tested image holds one device, reported as one row. "
                 "Property names are the app's own "
                 "(com.apple.vienna.v5.data.database.Property in the app's decompiled code, "
                 "versionCode 28132, the APK installed on dragna_pixel9a_a16, decompiled with"
                 " jadx). The code is obfuscated and jadx reported 82 errors; the methods "
                 "named below that it could not decompile were read in jadx fallback mode, "
                 "and a writer in another undecompiled method can still be missed. "
                 "'Disconnection Time' is DISCONNECTION_TIME. The app's code sets a device "
                 "field named disconnection_time to the current time in Unix milliseconds "
                 "(new Date().getTime()) in its disconnect callback "
                 "(com.apple.vienna.v4.application.managers i.java) and when it selects the "
                 "current device (n.java); the code that writes that field to this table was "
                 "not found, so the match is by name. The value is 13 digits on the tested "
                 "image and is converted as Unix milliseconds, shown in UTC. 'Last Time "
                 "Connected (as stored)' is LAST_TIME_CONNECTED, which the app sets to the "
                 "current time in Unix milliseconds when it saves a location for the device "
                 "(BeatsDevice.D, called from the saveLocation coroutine in w91.java); on the"
                 " tested image it is about 56 days earlier than CREATION_TIMESTAMP, which no"
                 " code read explains, so it is reported as stored. 'Creation Timestamp (as "
                 "stored)' is CREATION_TIMESTAMP as stored; no writer of it was found. "
                 "'Latitude (as stored)' and 'Longitude (as stored)' are LATITUDE and "
                 "LONGITUDE as stored, from which the app builds a map coordinate for the "
                 "device (rj1.java). Two code paths set them. One reads the phone's last "
                 "known location from Android's LocationManager and stores its latitude and "
                 "longitude for the device, when the device disconnects and on a Find My "
                 "update, if the app holds location permission (BeatsDevice.saveLocation, "
                 "w91.java and jo2.java). The other is a dialog with two text fields whose "
                 "layout is named find_my_debug_dialog (vj1.java, opened from n6.java). The "
                 "stored value does not record which path wrote it. A value from the first "
                 "path is the phone's location, not a position reported by the headphones. "
                 "They are not written to KML. 'Connection State' is the stored "
                 "CONNECTION_STATE text. 'Other Properties (as stored)' holds every other "
                 "property as name=value (firmware pending version, feature list, button and "
                 "tone settings, color, product id and others). The Bluetooth address can be "
                 "compared with the Nearby - Fast Pair Devices and Bluetooth Connections "
                 "artifacts. Tested on one image; the member listings of the 22 other Android"
                 " corpus keys searched hold no com.apple.bnd folder.",
        "paths": ('*/com.apple.bnd/databases/device_database*',),
        "output_types": "standard",
        "artifact_icon": "headphones",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | com.apple.bnd versionCode 28132 | 1 row",
        },
    },
}

import os
from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records

# Property names shown in their own columns; every other property is reported as stored in
# 'Other Properties (as stored)'.
_SHOWN = ('DISCONNECTION_TIME', 'LAST_TIME_CONNECTED', 'CREATION_TIMESTAMP', 'PRODUCT_NAME',
          'NAME', 'SERIAL_NUMBER', 'SERIAL_NUMBER_LEFT', 'SERIAL_NUMBER_RIGHT',
          'FIRMWARE_VERSION', 'CONNECTION_STATE', 'LATITUDE', 'LONGITUDE')


def _utc_ms(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return ''
    if number <= 0:
        return ''
    try:
        return datetime.fromtimestamp(number / 1000, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


@artifact_processor
def beats_devices(context):
    data_headers = (
        ('Disconnection Time', 'datetime'), 'Last Time Connected (as stored)',
        'Creation Timestamp (as stored)', 'Bluetooth Address', 'Product Name', 'Name',
        'Serial Number', 'Serial Number Left', 'Serial Number Right', 'Firmware Version',
        'Connection State', 'Latitude (as stored)', 'Longitude (as stored)',
        'Other Properties (as stored)')
    data_list, sources = [], []
    for file_found in unique_files(context):
        path = str(file_found)
        if os.path.basename(path) != 'device_database':
            continue
        rows = get_sqlite_db_records(
            path, 'SELECT bluetooth_address, name, value FROM table_property_model '
                  'ORDER BY bluetooth_address, name')
        if rows is None:
            continue
        sources.append(path)
        devices = {}
        for address, name, value in rows:
            devices.setdefault(address, {})[name] = value
        for address, props in devices.items():
            other = '; '.join(f'{name}={value}' for name, value in props.items()
                              if name not in _SHOWN)
            data_list.append((
                _utc_ms(props.get('DISCONNECTION_TIME')),
                props.get('LAST_TIME_CONNECTED', ''), props.get('CREATION_TIMESTAMP', ''),
                address, props.get('PRODUCT_NAME', ''), props.get('NAME', ''),
                props.get('SERIAL_NUMBER', ''), props.get('SERIAL_NUMBER_LEFT', ''),
                props.get('SERIAL_NUMBER_RIGHT', ''), props.get('FIRMWARE_VERSION', ''),
                props.get('CONNECTION_STATE', ''), props.get('LATITUDE', ''),
                props.get('LONGITUDE', ''), other,
            ))
    return data_headers, data_list, '\n'.join(sources)
