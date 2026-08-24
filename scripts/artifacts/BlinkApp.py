__artifacts_v2__ = {
    "blink_camera_information": {
        "name": "Blink Camera Information",
        "description": "Extracts and parses camera data from Blink Camera app",
        "author": "Christian Frahm",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "WiFi Cameras",
        "notes": "",
        "paths": ('*/com.immediasemi.android.blink/databases/BlinkRoom'),
        "output_types": "standard",
        "artifact_icon": "camera"

    },

    "blink_camera_entitlements": {
        "name": "Blink Camera Entitlements",
        "description": "Extracts and parses camera entitlements from Blink Camera app",
        "author": "Christian Frahm",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "WiFi Cameras",
        "notes": "",
        "paths": ('*/com.immediasemi.android.blink/databases/BlinkRoom'),
        "output_types": "standard",
        "artifact_icon": "camera"
    },
    "blink_syncmodule_information": {
            "name": "Blink Syncmodule Information",
            "description": "Extracts and parses Syncmodule data from Blink Camera app",
            "author": "Christian Frahm",
            "creation_date": "2026-08-20",
            "last_update_date": "2026-08-20",
            "requirements": "none",
            "category": "WiFi Cameras",
            "notes": "",
            "paths": ('*/com.immediasemi.android.blink/databases/BlinkRoom'),
            "output_types": "standard",
            "artifact_icon": "camera"
    },
    "blink_syncmodule_entitlements": {
            "name": "Blink Syncmodule Entitlements",
            "description": "Extracts and parses Syncmodule entitlements from Blink Camera app",
            "author": "Christian Frahm",
            "creation_date": "2026-08-20",
            "last_update_date": "2026-08-20",
            "requirements": "none",
            "category": "WiFi Cameras",
            "notes": "",
            "paths": ('*/com.immediasemi.android.blink/databases/BlinkRoom'),
            "output_types": "standard",
            "artifact_icon": "camera"
    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records

@artifact_processor
def blink_camera_information(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "BlinkRoom")
    data_list = []

    query = """
    SELECT 
    camera.created_at, 
    camera.updated_at, 
    camera.name, 
    camera.serial_number,
    camera.network_type,
    camera.type
    FROM camera"""

    records = get_sqlite_db_records(source_path, query)
    for record in records:
        data_list.append((record[0], #Created TS
                            record[1], #Updated TS
                            record[2], #Camera Name
                            record[3], #Camera Serial Number
                            record[4], #Network Type
                            record[5], #Camera Model
                          ))

    data_headers = (
        'Created Timestamp', #Timestamps are stored human-readable 
        'Updated Timestamp',
        'Camera Name',
        'Camera Serial Number',
        'Network Type',
        'Camera Model',
    )
    return data_headers, data_list, source_path

@artifact_processor
def blink_camera_entitlements(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "BlinkRoom")
    data_list = []

    query = """
        SELECT 
        camera.name, 
        camera.serial_number,
        camera.id,
        entitlement.name,
        entitlement.status,
        entitlement.subscription_required
        FROM camera
        LEFT JOIN entitlement on camera.id = entitlement.target_id
        ORDER BY entitlement.target_id DESC"""
    
    records = get_sqlite_db_records(source_path, query)
    for record in records:
        data_list.append((record[0], #Camera Name
                            record[1], #Camera Serial Number
                            record[2], #Camera ID (Unique, Primary key for JOIN)
                            record[3], #Entitlement Name
                            record[4], #Entitlement Status
                            record[5], #Subscription Requirement
                        ))
    

    data_headers = (
        'Camera Name',
        'Camera Serial Number',
        'Camera ID',
        'Entitlement Name',
        'Entitlement Status',
        'Subscription Required',
    )
    return data_headers, data_list, source_path

@artifact_processor
def blink_syncmodule_information(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "BlinkRoom")
    data_list = []

    query= """
    SELECT
    syncmodule.id,
    syncmodule.serial,
    syncmodule.created_at,
    syncmodule.updated_at,
    syncmodule.status,
    syncmodule.local_storage_status
    FROM syncmodule
    """
    records = get_sqlite_db_records(source_path, query)
    for record in records:
        data_list.append((record[0], #Syncmodule ID (Unique, Primary Key)
                            record[1], #Syncmodule Serial Number
                            record[2], #Syncmodule created TS
                            record[3], #Syncmodule updated TS
                            record[4], #Syncmodule Status
                            record[5], #Syncmodule local storage status
                              ))

    data_headers = (
         "Syncmodule ID",
         "Syncmodule Serial Number",
         "Created Timestamp",
         "Updated Timestamp",
         "Syncmodule Status",
         "Syncmodule Local Storage Status"
    )

    return data_headers, data_list, source_path

@artifact_processor
def blink_syncmodule_entitlements(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "BlinkRoom")
    data_list = []

    query = """
    SELECT
    syncmodule.id,
    syncmodule.status,
    syncmodule.serial,
    syncmodule.local_storage_enabled,
	entitlement.name,
	entitlement.status,
	entitlement.subscription_required
    FROM syncmodule
	LEFT JOIN entitlement ON syncmodule.id = entitlement.target_id
    """

    records = get_sqlite_db_records(source_path, query)
    for record in records:
            data_list.append((record[0], #Syncmodule ID (Unique, Primary Key)
                                record[1], #Syncmodule Status
                                record[2], #Syncmodule Serial Number
                                record[3], #Syncmodule Local Storage Status
                                record[4], #Entitlement name
                                record[5], #Entitlement status
                                record[6], #Subscription requirement
                                  ))

    data_headers = (
          "Syncmodule ID",
          "Syncmodule Status",
          "Syncmodule Serial Number",
          "Syncmodule Local Storage Status",
          "Entitlement Name",
          "Entitlement Status",
          "Subscription Required"
    )

    return data_headers, data_list, source_path
