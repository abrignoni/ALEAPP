"""Samsung Find (com.samsung.android.app.find): devices, locations and the address cache.

The Samsung Find app keeps the devices on the signed-in account, their last reported
locations and battery levels, and a cache of addresses it looked up, in
databases/app-database.db, a Room database.
"""

__artifacts_v2__ = {
    "get_samsung_find_devices": {
        "name": "Samsung Find - Devices",
        "description": (
            "Parses the devices listed by the Samsung Find app in app-database.db, one row per "
            "device, with the registration time stored for it, the model, owner type and "
            "device type, the favourite flag and the last stored battery reading."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Samsung Find",
        "notes": (
            "Read from com.samsung.android.app.find/databases/app-database.db with its "
            "-wal. Known data: samsung_a166u_a16_known_20261117, where the Samsung Find app "
            "was opened for the first time, its consent accepted and this phone located "
            "between about 14:18 and 14:22 UTC (logged during the session); no other device "
            "or tag is on the account. samsung_a166u_a16_known_20261116 holds the database "
            "with every table empty (the app had not been opened), and no other registered "
            "image holds it. "
            "Registered is devices.regDate, milliseconds since the Unix epoch stored as "
            "text, converted to UTC; it was 14:19:14 on the known data, inside the logged "
            "window after the consent was accepted. Battery (%) and Battery Updated are the "
            "newest battery row for the device (battery.hashId equals devices.hashId), "
            "timeUpdated converted the same way; 100 at 14:20:45 on the known data. Model "
            "Name, Model Code, Brand Name, Device Type and Owner Type are stored text "
            "(Owner Type ME for this phone). Favorite (as stored) is managed_data.favorite, "
            "1 on the one device; it is not decoded. "
            "Left out: subType (empty on the known data), saDeviceId, hashId and userId "
            "(identifiers), product_info (one entry per model with image and download fields), user_order, notice (five app notices with their own dates, not device "
            "data), and the users, item, tag, sharing, safe-place, geofencing, family-share "
            "and history tables, which were empty on the known data, so tags, shared "
            "devices, safe places and location history are not exercised. The app showed no "
            "device location history screen during the session. "
            "On the known data the one device row held Android User 0."
        ),
        "paths": ("*/com.samsung.android.app.find/databases/app-database.db*",),
        "output_types": "standard",
        "artifact_icon": "smartphone",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.samsung.android.app.find | 1 row",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.app.find | tables empty | 0 rows",
        },
    },
    "get_samsung_find_locations": {
        "name": "Samsung Find - Locations",
        "description": (
            "Parses the device locations stored by the Samsung Find app in the location table "
            "of app-database.db, with the time, coordinates, address and source stored for "
            "each, and the model of the device they belong to."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Samsung Find",
        "notes": (
            "Read from com.samsung.android.app.find/databases/app-database.db with its "
            "-wal. Known data: samsung_a166u_a16_known_20261117, where the Samsung Find app "
            "was opened for the first time, its consent accepted and this phone located "
            "between about 14:18 and 14:22 UTC (logged during the session); no other device "
            "or tag is on the account. samsung_a166u_a16_known_20261116 holds the database "
            "with every table empty (the app had not been opened), and no other registered "
            "image holds it. "
            "Timestamp is location.timestamp, milliseconds since the Unix epoch stored as "
            "text, converted to UTC; Latitude and Longitude are stored as text and "
            "converted to numbers; Address is stored text. On the known data the one row "
            "(14:22:29) is the phone's own position: Device Model joins location.deviceId "
            "to devices.deviceId. Source (as stored) held FUSED and Is Encrypted (as "
            "stored) held 0; neither is decoded, and a row with Is Encrypted other than 0 "
            "is not exercised, so its coordinates may not be readable as numbers. One position was present; whether the app keeps more than one per device is not established. Output includes KML. "
            "The units column was empty on the known data and is not reported."
        ),
        "paths": ("*/com.samsung.android.app.find/databases/app-database.db*",),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.samsung.android.app.find | 1 row",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.app.find | tables empty | 0 rows",
        },
    },
    "get_samsung_find_address_cache": {
        "name": "Samsung Find - Address Cache",
        "description": (
            "Parses the address_cache table of the Samsung Find app's app-database.db: each "
            "pair of coordinates with the address stored for it and the stored expiry time."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Samsung Find",
        "notes": (
            "Read from com.samsung.android.app.find/databases/app-database.db with its "
            "-wal. Known data: samsung_a166u_a16_known_20261117, where the Samsung Find app "
            "was opened for the first time, its consent accepted and this phone located "
            "between about 14:18 and 14:22 UTC (logged during the session); no other device "
            "or tag is on the account. samsung_a166u_a16_known_20261116 holds the database "
            "with every table empty (the app had not been opened), and no other registered "
            "image holds it. "
            "address_cache holds coordinates with the address returned for them. Expires is "
            "expire, milliseconds since the Unix epoch, converted to UTC; it is not the "
            "time of the lookup. On the known data each of the five Expires values was "
            "exactly 7 days after a time inside the logged Find session (14:19:21 to "
            "14:22:29), and the last equalled the location row's timestamp to the second, "
            "so the coordinates here are positions the app looked up during the session; "
            "whether every cached position was this phone's own is not established. Output "
            "includes KML. "
            "On the known data Language held US and Android User held 0 on all five rows."
        ),
        "paths": ("*/com.samsung.android.app.find/databases/app-database.db*",),
        "output_types": "all",
        "artifact_icon": "map",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.samsung.android.app.find | 5 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.app.find | tables empty | 0 rows",
        },
    },
}

import re

from scripts.ilapfuncs import (
    artifact_processor,
    convert_unix_ts_to_utc,
    does_table_exist_in_db,
    get_sqlite_db_records,
    is_sqlite_sidecar,
)

PACKAGE = "com.samsung.android.app.find"
_USER_RE = re.compile(r"/(?:user|user_de|data_mirror/data_(?:ce|de)/[^/]+)/(\d+)/")


def _container(path):
    """(android user, storage area) of the Find container a path sits in, or None."""
    norm = str(path).replace("\\", "/")
    idx = norm.find(f"/{PACKAGE}/databases/")
    if idx < 0:
        return None
    head = norm[:idx + 1]
    area = "de" if ("/user_de/" in head or "/data_mirror/data_de/" in head) else "ce"
    match = None
    for match in _USER_RE.finditer(head):
        pass
    if match and head.endswith(f"/{match.group(1)}/"):
        return int(match.group(1)), area
    if head.rstrip("/").rsplit("/", 1)[-1] == "data":
        # /data/data/<pkg>, and layouts such as userdata/data/<pkg> that keep user 0 there
        return 0, area
    return None


def _databases(files_found):
    for path in files_found:
        path = str(path)
        if is_sqlite_sidecar(path) or not path.endswith("app-database.db"):
            continue
        container = _container(path)
        if container is not None:
            yield path, container


def _ms(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ""
    return convert_unix_ts_to_utc(value) if value > 0 else ""


def _columns(path, table):
    return {row[1] for row in get_sqlite_db_records(path, f"PRAGMA table_info({table})")}


def _select(path, table, wanted, alias=None):
    present = _columns(path, table)
    prefix = f"{alias}." if alias else ""
    return ", ".join(f'{prefix}"{c}"' if c in present else f'NULL AS "{c}"' for c in wanted)


def _float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return ""


@artifact_processor
def get_samsung_find_devices(context):
    data_list = []
    source_paths = []
    seen = set()
    for path, container in _databases(context.get_files_found()):
        source_paths.append(path)
        if not does_table_exist_in_db(path, "devices"):
            continue
        cols = _select(path, "devices", ("regDate", "modelName", "modelCode", "brandName",
                                         "deviceType", "ownerType", "deviceId",
                                         "hashId"), "d")
        favorite = "m.favorite" if does_table_exist_in_db(path, "managed_data") else "NULL"
        join = ("LEFT JOIN managed_data m ON m.deviceId = d.deviceId"
                if favorite != "NULL" else "")
        battery = ("(SELECT b.value FROM battery b WHERE b.hashId = d.hashId "
                   "ORDER BY b.timeUpdated DESC LIMIT 1), "
                   "(SELECT b.timeUpdated FROM battery b WHERE b.hashId = d.hashId "
                   "ORDER BY b.timeUpdated DESC LIMIT 1)"
                   if does_table_exist_in_db(path, "battery") else "NULL, NULL")
        query = f"SELECT {cols}, {favorite}, {battery} FROM devices d {join}"
        for row in get_sqlite_db_records(path, query):
            (registered, model, model_code, brand, device_type, owner, device_id,
             _hash_id, fav, battery_value, battery_time) = row
            key = (container[0], device_id, registered)
            if key in seen:
                continue
            seen.add(key)
            data_list.append((
                _ms(registered), _ms(battery_time), model or "", model_code or "",
                brand or "", device_type or "", owner or "",
                "" if fav is None else fav, "" if battery_value is None else battery_value,
                device_id or "", container[0],
            ))

    data_headers = (
        ("Registered", "datetime"),
        ("Battery Updated", "datetime"),
        "Model Name",
        "Model Code",
        "Brand Name",
        "Device Type",
        "Owner Type",
        "Favorite (as stored)",
        ("Battery (%)", "number"),
        ("Device ID", "hash"),
        "Android User",
    )
    return data_headers, data_list, "\n".join(sorted(set(source_paths)))


@artifact_processor
def get_samsung_find_locations(context):
    data_list = []
    source_paths = []
    seen = set()
    for path, container in _databases(context.get_files_found()):
        source_paths.append(path)
        if not does_table_exist_in_db(path, "location"):
            continue
        cols = _select(path, "location", ("timestamp", "latitude", "longitude", "address",
                                          "source", "isEncrypted", "deviceId", "id"),
                       "l")
        model = "d.modelName" if does_table_exist_in_db(path, "devices") else "NULL"
        join = "LEFT JOIN devices d ON d.deviceId = l.deviceId" if model != "NULL" else ""
        query = f"SELECT {cols}, {model} FROM location l {join} ORDER BY l.timestamp"
        for row in get_sqlite_db_records(path, query):
            (stamp, lat, lon, address, source, encrypted, device_id, row_id,
             model_name) = row
            key = (container[0], row_id, stamp, device_id)
            if key in seen:
                continue
            seen.add(key)
            data_list.append((
                _ms(stamp), _float(lat), _float(lon), address or "", source or "",
                "" if encrypted is None else encrypted, model_name or "",
                device_id or "", container[0],
            ))

    data_headers = (
        ("Timestamp", "datetime"),
        ("Latitude", "latitude"),
        ("Longitude", "longitude"),
        "Address",
        "Source (as stored)",
        "Is Encrypted (as stored)",
        "Device Model",
        ("Device ID", "hash"),
        "Android User",
    )
    return data_headers, data_list, "\n".join(sorted(set(source_paths)))


@artifact_processor
def get_samsung_find_address_cache(context):
    data_list = []
    source_paths = []
    seen = set()
    for path, container in _databases(context.get_files_found()):
        source_paths.append(path)
        if not does_table_exist_in_db(path, "address_cache"):
            continue
        cols = _select(path, "address_cache", ("expire", "lat", "lng", "address", "language"))
        for expire, lat, lon, address, language in get_sqlite_db_records(
                path, f"SELECT {cols} FROM address_cache ORDER BY expire"):
            key = (container[0], lat, lon, language, expire)
            if key in seen:
                continue
            seen.add(key)
            data_list.append((_ms(expire), _float(lat), _float(lon), address or "",
                              language or "", container[0]))

    data_headers = (
        ("Expires", "datetime"),
        ("Latitude", "latitude"),
        ("Longitude", "longitude"),
        "Address",
        "Language",
        "Android User",
    )
    return data_headers, data_list, "\n".join(sorted(set(source_paths)))
