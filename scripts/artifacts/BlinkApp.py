__artifacts_v2__ = {
    "blink_camera_information": {
        "name": "Blink Camera Information",
        "description": "Cameras recorded in the Blink app's local database, with the serial number, model and the timestamps stored on each record",
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
                 "it came from a Samsung SM-A166U running Android 16: 2 rows. That is the only data this "
                 "module has been run against, and a sanitized copy of it is committed as the module's "
                 "test case; a second Blink extraction would be the first test of any of this against "
                 "another account.",
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
                 "SM-A166U running Android 16: 26 rows, 13 entitlements against each of 2 cameras. That "
                 "is the only data this module has been run against, and a sanitized copy of it is "
                 "committed as the module's test case; a second Blink extraction would be the first test "
                 "of any of this against another account.",
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
                 "That is the only data this module has been run against, and a sanitized copy of it is "
                 "committed as the module's test case; a second Blink extraction would be the first test "
                 "of any of this against another account.",
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
                 "module. That is the only data this module has been run against, and a sanitized copy "
                 "of it is committed as the module's test case; a second Blink extraction would be the "
                 "first test of any of this against another account.",
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
                 "seconds and the two camera records' by 2 minutes 43 seconds and 5 minutes 32 seconds. "
                 "What that ordering means, and whether it holds generally, were not established. The "
                 "priority column is not reported. Measured on one BlinkRoom file supplied by Christian "
                 "Frahm, who reports it came from a Samsung SM-A166U running Android 16: 1 row. An "
                 "account with one network produces one row, so every column holds a single value on "
                 "that file. That is the only data this module has been run against, and a sanitized "
                 "copy of it is committed as the module's test case; a second Blink extraction would be "
                 "the first test of any of this against another account.",
        "paths": ('*/com.immediasemi.android.blink/databases/BlinkRoom*',),
        "output_types": "standard",
        "artifact_icon": "wifi"
    },
    "blink_key_value_store": {
        "name": "Blink App Key Value Store",
        "description": "Values the Blink app stored in its own key and value table",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Blink",
        "notes": "Rows come from the key_value_pair table of the app's Room database, which is a key and "
                 "value store the app writes. Value is reported as stored because Value Type does not "
                 "say whether a value is a timestamp: on the tested file the three values typed LONG "
                 "were a Unix millisecond timestamp, a network id and a zero. Two keys on that file held "
                 "an ISO 8601 timestamp typed STRING, and one of those carried a -04:00 offset, which is "
                 "the offset America/New_York was on for that value's date and is the zone the network "
                 "row records. Some keys embed a camera id, and two on the tested file also began with a "
                 "brace character. What each key means, and the full set of keys the app can write, are "
                 "not established. Measured on one BlinkRoom file supplied by Christian Frahm, who "
                 "reports it came from a Samsung SM-A166U running Android 16: 15 rows. That is the only "
                 "data this module has been run against, and a sanitized copy of it is committed as the "
                 "module's test case; a second Blink extraction would be the first test of any of this "
                 "against another account.",
        "paths": ('*/com.immediasemi.android.blink/databases/BlinkRoom*',),
        "output_types": "standard",
        "artifact_icon": "settings"
    },
    "blink_subscriptions": {
        "name": "Blink Subscriptions",
        "description": "Subscription records the Blink app stored, with the plan, trial window and cycle dates",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Blink",
        "notes": "Rows come from the subscription table of the app's Room database. Target and Target ID "
                 "name what a subscription is attached to, and that vocabulary is not the one the "
                 "entitlement table uses: on the tested file the single subscription's target did not "
                 "appear as an entitlement target, and its target id matched no camera, sync module or "
                 "network id in the same file, so what it points at is not established. "
                 "camera.subscription_id was zero on both cameras and the sync module's was empty, so "
                 "nothing in that file tied a device to this subscription. Subscription Type, Source, "
                 "Active, Attached, Cycle State, Cycle Action and Trial Period are reported as stored "
                 "and the full set of values each can take is not established. The five timestamp "
                 "columns are stored as ISO 8601 text carrying an explicit UTC offset and are reported "
                 "as stored; Cycle Timestamp, Trial Starts Timestamp and Trial Ends Timestamp are "
                 "nullable in the schema and were filled on the tested file. An account with one "
                 "subscription produces one row, so every column holds a single value on that file. "
                 "Measured on one BlinkRoom file supplied by Christian Frahm, who reports it came from a "
                 "Samsung SM-A166U running Android 16: 1 row. That is the only data this module has been "
                 "run against, and a sanitized copy of it is committed as the module's test case; a "
                 "second Blink extraction would be the first test of any of this against another "
                 "account.",
        "paths": ('*/com.immediasemi.android.blink/databases/BlinkRoom*',),
        "output_types": "standard",
        "artifact_icon": "credit-card"
    },
    "blink_app_messages": {
        "name": "Blink App Messages",
        "description": "Notices the Blink app raised in its own interface, with the network they belong to",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Blink",
        "notes": "Rows come from the message table of the app's Room database, which holds notices the "
                 "app raised in its own interface. The table has no sender or recipient column, so "
                 "nothing in it records a message a person sent or received. Created Timestamp is stored "
                 "as a Unix value in milliseconds and is converted here rather than passed to a helper "
                 "that infers the unit: read as seconds, the single value on the tested file gives a "
                 "year outside the range a date can represent, which is what rules that unit out. "
                 "Network ID names the row in Blink Network Information the message belongs to. Sub "
                 "Message held an empty string on the tested file's single row; it is reported because "
                 "it is a separate column of the message record, and whether the app ever fills it was "
                 "not established. Priority and Dismiss Until are reported as stored; Dismiss Until is "
                 "an integer that was zero on the tested file and whether it is a timestamp is not "
                 "established. The message text on that file named a camera by the same name Blink "
                 "Camera Information reports. Message ID is an autoincrement value that reached 11 with "
                 "1 row held, so the table does not hold every message ever written; whether the app "
                 "removes them or the supplied file was edited is not established. Measured on one "
                 "BlinkRoom file supplied by Christian Frahm, who reports it came from a Samsung "
                 "SM-A166U running Android 16: 1 row. That is the only data this module has been run "
                 "against, and a sanitized copy of it is committed as the module's test case; a second "
                 "Blink extraction would be the first test of any of this against another account.",
        "paths": ('*/com.immediasemi.android.blink/databases/BlinkRoom*',),
        "output_types": "standard",
        "artifact_icon": "bell"
    },
    "blink_tracking_events": {
        "name": "Blink Tracking Events",
        "description": "App events the Blink app recorded with a timestamp, reported by the name it stored",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Blink",
        "notes": "Rows come from the tracking_event table of the app's Room database. Timestamp is "
                 "stored as ISO 8601 text carrying a Z offset and is reported as stored. Event Name is "
                 "reported as stored and the full set of names the app can write is not established; the "
                 "single row on the tested file carried the name SESSION_BACKGROUNDED. Event ID is an "
                 "autoincrement value that reached 5274 with 1 row held, so the table does not hold "
                 "every event ever written; whether the app removes them or the supplied file was edited "
                 "is not established. Nothing in the table names a camera, a network or an account. "
                 "Measured on one BlinkRoom file supplied by Christian Frahm, who reports it came from a "
                 "Samsung SM-A166U running Android 16: 1 row. That is the only data this module has been "
                 "run against, and a sanitized copy of it is committed as the module's test case; a "
                 "second Blink extraction would be the first test of any of this against another "
                 "account.",
        "paths": ('*/com.immediasemi.android.blink/databases/BlinkRoom*',),
        "output_types": "standard",
        "artifact_icon": "activity"
    }
}

import datetime
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


@artifact_processor
def blink_key_value_store(context):
    source_paths = _blink_databases(context)
    data_list = []

    query = """
    SELECT
    key_value_pair.key,
    key_value_pair.value,
    key_value_pair.type,
    key_value_pair.client_options
    FROM key_value_pair
    ORDER BY key_value_pair.key"""

    for source_path in source_paths:
        for record in get_sqlite_db_records(source_path, query):
            data_list.append((record[0],  # Key, as stored
                              record[1],  # Value, as stored, unit not given by the type column
                              record[2],  # Value Type, as stored
                              record[3],  # client_options, integer flag
                              ))

    data_headers = (
        'Key',
        'Value (as stored)',
        'Value Type (as stored)',
        'Client Options (as stored)',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def blink_subscriptions(context):
    source_paths = _blink_databases(context)
    data_list = []

    query = """
    SELECT
    subscription.created_at,
    subscription.updated_at,
    subscription.cycle_at,
    subscription.cycle_trial_starts_at,
    subscription.cycle_trial_ends_at,
    subscription.plan_name,
    subscription.plan_interval,
    subscription.type,
    subscription.id,
    subscription.target,
    subscription.target_id,
    subscription.source,
    subscription.active,
    subscription.attached,
    subscription.cycle_state,
    subscription.cycle_action,
    subscription.cycle_trial_period
    FROM subscription
    ORDER BY subscription.created_at"""

    for source_path in source_paths:
        for record in get_sqlite_db_records(source_path, query):
            data_list.append(tuple(record))

    data_headers = (
        ('Created Timestamp', 'datetime'),
        ('Updated Timestamp', 'datetime'),
        ('Cycle Timestamp', 'datetime'),
        ('Trial Starts Timestamp', 'datetime'),
        ('Trial Ends Timestamp', 'datetime'),
        'Plan Name',
        'Plan Interval',
        'Subscription Type',
        'Subscription ID',
        'Target (as stored)',
        'Target ID',
        'Source',
        'Active (as stored)',
        'Attached (as stored)',
        'Cycle State (as stored)',
        'Cycle Action (as stored)',
        'Trial Period (as stored)',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def blink_app_messages(context):
    source_paths = _blink_databases(context)
    data_list = []

    query = """
    SELECT
    message.created_at,
    message.message,
    message.sub_message,
    message.id,
    message.network_id,
    message.priority,
    message.dismiss_until
    FROM message
    ORDER BY message.created_at"""

    for source_path in source_paths:
        for record in get_sqlite_db_records(source_path, query):
            # Stored in milliseconds. Converted here rather than through a helper that infers
            # the unit from the value's magnitude, because the column's unit is known.
            created = datetime.datetime.fromtimestamp(int(record[0]) / 1000,
                                                      datetime.timezone.utc)
            data_list.append((created,     # Created Timestamp
                              record[1],   # Message text
                              record[2],   # Sub message text
                              record[3],   # Message ID, autoincrement
                              record[4],   # Network ID, joins to the network table
                              record[5],   # priority, as stored
                              record[6],   # dismiss_until, as stored
                              ))

    data_headers = (
        ('Created Timestamp', 'datetime'),
        'Message',
        'Sub Message',
        'Message ID',
        'Network ID',
        'Priority (as stored)',
        'Dismiss Until (as stored)',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def blink_tracking_events(context):
    source_paths = _blink_databases(context)
    data_list = []

    query = """
    SELECT
    tracking_event.timestamp,
    tracking_event.name,
    tracking_event.id
    FROM tracking_event
    ORDER BY tracking_event.timestamp"""

    for source_path in source_paths:
        for record in get_sqlite_db_records(source_path, query):
            data_list.append((record[0],  # Timestamp, ISO 8601 with a Z offset
                              record[1],  # Event Name, as stored
                              record[2],  # Event ID, autoincrement
                              ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Event Name',
        'Event ID',
    )
    return data_headers, data_list, '\n'.join(source_paths)
