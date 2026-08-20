__artifacts_v2__ = {
    "blinkCameraInformation": {
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

    }
}

from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records

@artifact_processor
def blinkCameraInformation(context):
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
