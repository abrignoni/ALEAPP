"""Samsung Find (com.samsung.android.app.find): devices, locations and the address cache.

The Samsung Find app keeps a devices table, a location table, battery readings and an
address cache in databases/app-database.db, a Room database.
"""

__artifacts_v2__ = {
    "get_samsung_find_devices": {
        "name": "Samsung Find - Devices",
        "description": (
            "Parses the devices table of the Samsung Find app's app-database.db, one row "
            "per device and Android user, with the regDate time stored for it, the model, "
            "owner type and device type, the favorite flag and the last stored battery "
            "reading."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Samsung Find",
        "notes": (
            "Read from com.samsung.android.app.find/databases/app-database.db with its "
            "-wal; on the known data every row was in the -wal. Known data: "
            "samsung_a166u_a16_known_20261117. The log has the app opened at 06:38 UTC with "
            "its consent screen left unaccepted, then the consent accepted and this phone "
            "located between about 14:18 and 14:22 UTC. The devices table held one row, "
            "this phone, and the item tables were empty. samsung_a166u_a16_known_20261116 "
            "holds the database with every app table empty, and no Find session is logged "
            "before that extraction; no other image in the Android registry holds it (83 "
            "listed). Rows were exercised at schema version 43 only. "
            "Reg Date is devices.regDate, stored as text and read as milliseconds since the "
            "Unix epoch, converted to UTC in whole seconds. It was 14:19:14 on the known "
            "data, inside the logged 14:18 to 14:21 window in which the consent was "
            "accepted; what the app registers at that time is not established. "
            "Battery (%) and Battery Updated come from the battery row with the highest "
            "timeUpdated for the device (battery.hashId equals devices.hashId); timeUpdated "
            "is an integer read as milliseconds since the Unix epoch. On the known data "
            "there was one battery row: 100 at 14:20:45, and the app's device sheet showed "
            "100% (logged). battery.units was NULL, so the percent unit comes from the "
            "screen, not the store. "
            "Model Name, Model Code, Brand Name, Device Type and Owner Type are stored text "
            "(Owner Type ME for this phone). Favorite (as stored) is managed_data.favorite, "
            "1 on the one device; it is not decoded. Android User is taken from the "
            "container path; it was 0 on the known data. "
            "Left out: subType (empty on the known data), saDeviceId, hashId, userId and "
            "modelId (identifiers), parentId (empty), supportFeatures (an integer, not "
            "decoded), managed_data.order, product_info (one row on the known data, with "
            "model, image and download fields), user_order, notice (five app notices with "
            "their own dates, not device data), and the users, sa_users, item_*, "
            "*_share_data, lba_*, recommended_safe_place_location, geofencing, "
            "family_share, history, remote_consent and tracking_session tables, which were "
            "empty on the known data. These tables are not parsed, and what they hold when "
            "populated is not established. The app showed no device location history screen "
            "during the session."
        ),
        "paths": ("*/com.samsung.android.app.find/databases/app-database.db*",),
        "output_types": "standard",
        "artifact_icon": "smartphone",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.samsung.android.app.find | 1 row",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.app.find | app tables empty | 0 rows",
        },
    },
    "get_samsung_find_locations": {
        "name": "Samsung Find - Locations",
        "description": (
            "Parses the device locations stored by the Samsung Find app in the location "
            "table of app-database.db, with the time, coordinates, address and source "
            "stored for each, and the model of the device they belong to."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Samsung Find",
        "notes": (
            "Read from com.samsung.android.app.find/databases/app-database.db with its "
            "-wal; on the known data every row was in the -wal. Known data: "
            "samsung_a166u_a16_known_20261117. The log has the app opened at 06:38 UTC with "
            "its consent screen left unaccepted, then the consent accepted and this phone "
            "located between about 14:18 and 14:22 UTC. The devices table held one row, "
            "this phone, and the item tables were empty. samsung_a166u_a16_known_20261116 "
            "holds the database with every app table empty, and no Find session is logged "
            "before that extraction; no other image in the Android registry holds it (83 "
            "listed). Rows were exercised at schema version 43 only. "
            "Timestamp is location.timestamp, stored as text and read as milliseconds since "
            "the Unix epoch, converted to UTC in whole seconds; whether it is the time of "
            "the fix or of the fetch is not established. Latitude and Longitude are stored "
            "as text and converted to numbers; Address is stored text. "
            "On the known data the one row (14:22:29) belongs to this phone's device row: "
            "location.deviceId equals devices.deviceId, which is how Device Model is "
            "filled. The coordinates were not compared with an independent record of the "
            "phone's position. Source (as stored) held FUSED and Is Encrypted (as stored) "
            "held 0; neither is decoded. A row with Is Encrypted other than 0 is not "
            "exercised; if its coordinates do not parse as numbers, Latitude and Longitude "
            "are left empty and the stored text is not shown. One position was present; "
            "whether the app keeps more than one per device is not established. Output "
            "includes KML. "
            "The units and unitId columns were empty on the known data and are not "
            "reported."
        ),
        "paths": ("*/com.samsung.android.app.find/databases/app-database.db*",),
        "output_types": "all",
        "artifact_icon": "map-pin",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.samsung.android.app.find | 1 row",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.app.find | app tables empty | 0 rows",
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
            "-wal; on the known data every row was in the -wal. Known data: "
            "samsung_a166u_a16_known_20261117. The log has the app opened at 06:38 UTC with "
            "its consent screen left unaccepted, then the consent accepted and this phone "
            "located between about 14:18 and 14:22 UTC. The devices table held one row, "
            "this phone, and the item tables were empty. samsung_a166u_a16_known_20261116 "
            "holds the database with every app table empty, and no Find session is logged "
            "before that extraction; no other image in the Android registry holds it (83 "
            "listed). Rows were exercised at schema version 43 only. "
            "address_cache holds coordinates with an address stored for each. Expires is "
            "expire, milliseconds since the Unix epoch, converted to UTC in whole seconds; "
            "it is not the time of a lookup. On the known data each of the five Expires "
            "values, less 7 days, falls between 14:19:21 and 14:22:29, after the logged "
            "start of the Find session (14:18) and before the next logged action on another "
            "app (14:23:07); the 7 day lifetime is inferred from this, not sourced. The "
            "last, less 7 days, is 5 ms before the location row's timestamp, and its "
            "coordinates and address equal that row's. This is consistent with addresses "
            "cached during the session; it does not establish it, and whether every cached "
            "position was this phone's own is not established. "
            "Output includes KML, whose point names carry the Expires time, not a time the "
            "position was recorded. The rows are not written to the timeline, since Expires "
            "is a future time. "
            "On the known data Language (as stored) held US and Android User held 0 on all "
            "five rows."
        ),
        "paths": ("*/com.samsung.android.app.find/databases/app-database.db*",),
        "output_types": ["html", "tsv", "lava", "kml"],
        "artifact_icon": "map",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.samsung.android.app.find | 5 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.app.find | app tables empty | 0 rows",
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
        ("Reg Date", "datetime"),
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
        "Language (as stored)",
        "Android User",
    )
    return data_headers, data_list, "\n".join(sorted(set(source_paths)))
