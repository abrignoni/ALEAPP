__artifacts_v2__ = {
    "blink_camera_information": {
        "name": "Blink Camera Information",
        "description": "Cameras recorded in the Blink app's local database, with the serial number, model and account timestamps stored for each",
        "author": "Christian Frahm",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Blink",
        "notes": "Rows come from the camera table of the app's Room database, "
                 "data/data/com.immediasemi.android.blink/databases/BlinkRoom. Created Timestamp and "
                 "Updated Timestamp are stored as ISO 8601 text carrying an explicit UTC offset and are "
                 "reported as stored; on the tested file both carried +00:00. What causes either to "
                 "change is not established, so neither should be read as a record of a person viewing "
                 "or operating the camera. Camera Model is the type column as stored; on the tested file "
                 "its value was also the entitlement target used in Blink Camera Entitlements, and the "
                 "full set of model codes is not established. The camera table holds 30 columns and this "
                 "artifact reports 8 of them, including network_id, which names the row in Blink Network "
                 "Information that this camera belongs to. The rest were left out as state at "
                 "acquisition or as internal identifiers; they include armed, battery, wifi_signal, "
                 "lfr_signal, thumbnail and its timestamp, snooze, onboarding and subscription "
                 "identifiers. Measured on one BlinkRoom file supplied by the contributor, who reports "
                 "it came from a Samsung SM-A166U running Android 16: 2 rows. None of the 40 registered "
                 "Android test corpora carry this app, so the module has not been exercised against "
                 "them.",
        "paths": ('*/com.immediasemi.android.blink/databases/BlinkRoom*',),
        "output_types": "standard",
        "artifact_icon": "camera"
    },
    "blink_camera_entitlements": {
        "name": "Blink Camera Entitlements",
        "description": "Per-camera feature entitlements the Blink app recorded, with the status stored for "
"each",
        "author": "Christian Frahm",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Blink",
        "notes": "Each row is one entitlement the entitlement table records against one camera. That "
                 "table's primary key is (target, target_id, name), so target_id alone does not identify "
                 "a device: the join matches entitlement.target_id against camera.id and "
                 "entitlement.target against camera.type, which is the pairing the tested file used. "
                 "Joining on target_id alone returned the same 26 rows on that file because no camera id "
                 "and sync module id collided there, and the table's own primary key is what says such a "
                 "collision is permitted. Entitlement Target, Entitlement Name and Entitlement Status "
                 "are reported as stored; the tested file held the status values ACTIVE, "
                 "SUBSCRIPTION_REQUIRED and NOT_ELIGIBLE, and the full set of values for each of the "
                 "three columns is not established. Entitlement Target held one value on that file "
                 "because the account had a single camera model, and it is kept because it is half of "
                 "the key that ties an entitlement to its device. The same table also holds entitlements "
                 "whose target is the account rather than a device, 4 rows on the tested file, and those "
                 "are reported by neither this artifact nor Blink Syncmodule Entitlements. The join is a "
                 "left join, so a camera carrying no entitlement row is still reported with the "
                 "entitlement columns blank; no tested file exercised that case. Measured on one "
                 "BlinkRoom file supplied by the contributor, who reports it came from a Samsung "
                 "SM-A166U running Android 16: 26 rows, 13 entitlements against each of 2 cameras. None "
                 "of the 40 registered Android test corpora carry this app, so the module has not been "
                 "exercised against them.",
        "paths": ('*/com.immediasemi.android.blink/databases/BlinkRoom*',),
        "output_types": "standard",
        "artifact_icon": "camera"
    },
    "blink_syncmodule_information": {
        "name": "Blink Syncmodule Information",
        "description": "Sync modules recorded in the Blink app's local database, with serial number, status and local storage state",
        "author": "Christian Frahm",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Blink",
        "notes": "Rows come from the syncmodule table of the app's Room database. Network ID names the "
                 "row in Blink Network Information that this sync module belongs to. Created Timestamp "
                 "and Updated Timestamp are stored as ISO 8601 text carrying an explicit UTC offset and "
                 "are reported as stored; on the tested file both carried +00:00. Local Storage "
                 "Compatible and Local Storage Enabled are the local_storage_compatible and "
                 "local_storage_enabled integer columns; Local Storage Status is the separate "
                 "local_storage_status text column. The tested file held a text status of ACTIVE beside "
                 "integer flags of 1, and with a single sync module on that file the relationship "
                 "between the three is not established, so each is reported as stored. Syncmodule Status "
                 "and Local Storage Status are reported as stored and the full set of values either can "
                 "take is not established. Measured on one BlinkRoom file supplied by the contributor, "
                 "who reports it came from a Samsung SM-A166U running Android 16: 1 row. An account with "
                 "one sync module produces one row, so every column holds a single value on that file. "
                 "None of the 40 registered Android test corpora carry this app, so the module has not "
                 "been exercised against them.",
        "paths": ('*/com.immediasemi.android.blink/databases/BlinkRoom*',),
        "output_types": "standard",
        "artifact_icon": "camera"
    },
    "blink_syncmodule_entitlements": {
        "name": "Blink Syncmodule Entitlements",
        "description": "Per-sync-module feature entitlements the Blink app recorded, with the status stored "
"for each",
        "author": "Christian Frahm",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Blink",
        "notes": "Each row is one entitlement the entitlement table records against one sync module. "
                 "That table's primary key is (target, target_id, name), so target_id alone does not "
                 "identify a device: the join matches entitlement.target_id against syncmodule.id and "
                 "entitlement.target against syncmodule.type, which is the pairing the tested file used. "
                 "On that file syncmodule.subtype held a different value and joining on it instead "
                 "returns no rows. Entitlement Target, Entitlement Name and Entitlement Status are "
                 "reported as stored and the full set of values for each is not established. Entitlement "
                 "Target held one value on that file because the account had a single sync module type, "
                 "and it is kept because it is half of the key that ties an entitlement to its device. "
                 "Syncmodule ID and Syncmodule Serial Number hold one value on every row when the "
                 "account has a single sync module, which is what the tested file held; they are kept so "
                 "a row names its own device without a join back to Blink Syncmodule Information. The "
                 "same table also holds entitlements whose target is the account rather than a device "
                 "and those are not reported here. The join is a left join, so a sync module carrying no "
                 "entitlement row is still reported with the entitlement columns blank; no tested file "
                 "exercised that case. Measured on one BlinkRoom file supplied by the contributor, who "
                 "reports it came from a Samsung SM-A166U running Android 16: 4 rows against 1 sync "
                 "module. None of the 40 registered Android test corpora carry this app, so the module "
                 "has not been exercised against them.",
        "paths": ('*/com.immediasemi.android.blink/databases/BlinkRoom*',),
        "output_types": "standard",
        "artifact_icon": "camera"
    },
    "blink_network_information": {
        "name": "Blink Network Information",
        "description": "The Blink network a sync module and its cameras belong to, with the IANA time zone stored for it",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Blink",
        "notes": "Rows come from the network table of the app's Room database. Blink groups a sync "
                 "module and its cameras into a network, which the app presents as one system; "
                 "camera.network_id and syncmodule.network_id name the network a device belongs to and "
                 "both artifacts report that id. Time Zone is an IANA zone name stored on the network "
                 "row. It is not needed to read any timestamp in this database: every stored timestamp "
                 "measured across the tested file carried its own UTC offset or was a Unix epoch value, "
                 "so none of them is ambiguous. What sets the zone, and what the app uses it for, were "
                 "not established. Network Name is the label stored for the system; whether a person "
                 "chose it or the app supplied a default was not established. Daylight Saving, Armed and "
                 "Save All Live Views are integer columns reported as stored and the full set of values "
                 "each can take is not established. Created Timestamp and Updated Timestamp are stored "
                 "as ISO 8601 text carrying an explicit UTC offset and are reported as stored. On the "
                 "tested file the network record's created_at preceded the sync module record's by 8 "
                 "seconds and the two camera records' by about 3 and 5 minutes. What that ordering "
                 "means, and whether it holds generally, were not established. The priority column is "
                 "not reported. Measured on one BlinkRoom file supplied by Christian Frahm, who reports "
                 "it came from a Samsung SM-A166U running Android 16: 1 row. An account with one network "
                 "produces one row, so every column holds a single value on that file. None of the 40 "
                 "registered Android test corpora carry this app, so the module has not been exercised "
                 "against them.",
        "paths": ('*/com.immediasemi.android.blink/databases/BlinkRoom*',),
        "output_types": "standard",
        "artifact_icon": "wifi"
    }
}

import os

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records


def _blink_databases(context):
    """Every BlinkRoom database the extraction holds, one per app data directory.

    unique_files collapses the duplicate storage views of a single file, so a second
    Android user's container is still read while no file is read twice. The basename
    test drops the -wal and -shm sidecars the glob also matches: they belong beside the
    database for the read-only open to apply them, not in this list.
    """
    return [file_found for file_found in unique_files(context)
            if os.path.basename(str(file_found)) == 'BlinkRoom'
            and os.path.isfile(file_found)]


@artifact_processor
def blink_camera_information(context):
    source_paths = _blink_databases(context)
    data_list = []

    query = """
    SELECT
    camera.created_at,
    camera.updated_at,
    camera.name,
    camera.id,
    camera.network_id,
    camera.serial_number,
    camera.type,
    camera.network_type
    FROM camera"""

    for source_path in source_paths:
        for record in get_sqlite_db_records(source_path, query):
            data_list.append((record[0],  # Created TS, ISO 8601 with offset
                              record[1],  # Updated TS, ISO 8601 with offset
                              record[2],  # Camera Name
                              record[3],  # Camera ID, the entitlement target_id
                              record[4],  # Network ID, joins to the network table
                              record[5],  # Camera Serial Number
                              record[6],  # Camera Model, the entitlement target
                              record[7],  # Network Type
                              ))

    data_headers = (
        ('Created Timestamp', 'datetime'),
        ('Updated Timestamp', 'datetime'),
        'Camera Name',
        'Camera ID',
        'Network ID',
        'Camera Serial Number',
        'Camera Model',
        'Network Type',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def blink_camera_entitlements(context):
    source_paths = _blink_databases(context)
    data_list = []

    # entitlement's primary key is (target, target_id, name), so target_id alone does not
    # identify a device. camera.type carries the same value as entitlement.target, which is
    # what keeps a sync module's entitlements out of a camera's row when the two ids collide.
    query = """
    SELECT
    camera.name,
    camera.id,
    camera.serial_number,
    entitlement.target,
    entitlement.name,
    entitlement.status,
    entitlement.subscription_required
    FROM camera
    LEFT JOIN entitlement
        ON camera.id = entitlement.target_id
        AND camera.type = entitlement.target
    ORDER BY camera.id, entitlement.name"""

    for source_path in source_paths:
        for record in get_sqlite_db_records(source_path, query):
            data_list.append((record[0],  # Camera Name
                              record[1],  # Camera ID
                              record[2],  # Camera Serial Number
                              record[3],  # Entitlement Target, as stored
                              record[4],  # Entitlement Name, as stored
                              record[5],  # Entitlement Status, as stored
                              record[6],  # Subscription Requirement
                              ))

    data_headers = (
        'Camera Name',
        'Camera ID',
        'Camera Serial Number',
        'Entitlement Target',
        'Entitlement Name',
        'Entitlement Status',
        'Subscription Required',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def blink_syncmodule_information(context):
    source_paths = _blink_databases(context)
    data_list = []

    query = """
    SELECT
    syncmodule.created_at,
    syncmodule.updated_at,
    syncmodule.serial,
    syncmodule.id,
    syncmodule.network_id,
    syncmodule.status,
    syncmodule.local_storage_compatible,
    syncmodule.local_storage_enabled,
    syncmodule.local_storage_status
    FROM syncmodule"""

    for source_path in source_paths:
        for record in get_sqlite_db_records(source_path, query):
            data_list.append((record[0],  # Created TS, ISO 8601 with offset
                              record[1],  # Updated TS, ISO 8601 with offset
                              record[2],  # Syncmodule Serial Number
                              record[3],  # Syncmodule ID, the entitlement target_id
                              record[4],  # Network ID, joins to the network table
                              record[5],  # Syncmodule Status, as stored
                              record[6],  # local_storage_compatible, integer flag
                              record[7],  # local_storage_enabled, integer flag
                              record[8],  # local_storage_status, separate text column
                              ))

    data_headers = (
        ('Created Timestamp', 'datetime'),
        ('Updated Timestamp', 'datetime'),
        'Syncmodule Serial Number',
        'Syncmodule ID',
        'Network ID',
        'Syncmodule Status',
        'Local Storage Compatible',
        'Local Storage Enabled',
        'Local Storage Status',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def blink_syncmodule_entitlements(context):
    source_paths = _blink_databases(context)
    data_list = []

    # Same composite key as the camera entitlements above. syncmodule.type carries the
    # entitlement target; syncmodule.subtype does not and joining on it returns nothing.
    query = """
    SELECT
    syncmodule.serial,
    syncmodule.id,
    entitlement.target,
    entitlement.name,
    entitlement.status,
    entitlement.subscription_required
    FROM syncmodule
    LEFT JOIN entitlement
        ON syncmodule.id = entitlement.target_id
        AND syncmodule.type = entitlement.target
    ORDER BY syncmodule.id, entitlement.name"""

    for source_path in source_paths:
        for record in get_sqlite_db_records(source_path, query):
            data_list.append((record[0],  # Syncmodule Serial Number
                              record[1],  # Syncmodule ID
                              record[2],  # Entitlement Target, as stored
                              record[3],  # Entitlement Name, as stored
                              record[4],  # Entitlement Status, as stored
                              record[5],  # Subscription Requirement
                              ))

    data_headers = (
        'Syncmodule Serial Number',
        'Syncmodule ID',
        'Entitlement Target',
        'Entitlement Name',
        'Entitlement Status',
        'Subscription Required',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def blink_network_information(context):
    source_paths = _blink_databases(context)
    data_list = []

    query = """
    SELECT
    network.created_at,
    network.updated_at,
    network.name,
    network.id,
    network.time_zone,
    network.dst,
    network.armed,
    network.save_all_liveviews
    FROM network"""

    for source_path in source_paths:
        for record in get_sqlite_db_records(source_path, query):
            data_list.append((record[0],  # Created TS, ISO 8601 with offset
                              record[1],  # Updated TS, ISO 8601 with offset
                              record[2],  # Network Name
                              record[3],  # Network ID, joined by camera and syncmodule
                              record[4],  # IANA time zone stored on the network row
                              record[5],  # dst, integer flag
                              record[6],  # armed, integer flag
                              record[7],  # save_all_liveviews, integer flag
                              ))

    data_headers = (
        ('Created Timestamp', 'datetime'),
        ('Updated Timestamp', 'datetime'),
        'Network Name',
        'Network ID',
        'Time Zone',
        'Daylight Saving (as stored)',
        'Armed (as stored)',
        'Save All Live Views (as stored)',
    )
    return data_headers, data_list, '\n'.join(source_paths)
