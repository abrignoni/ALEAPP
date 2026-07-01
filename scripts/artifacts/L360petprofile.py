__artifacts_v2__ = {
    'Life360_PetProfile': {
        'name': 'Life360 PetProfile',
        'description': 'Parses Life360 PetProfile',
        'author': 'Heather Charpentier',
        'creation_date': '2026-06-10',
        'last_update_date': '2026-06-10',
        'requirements': 'none',
        'category': 'Life360',
        'notes': '',
        'paths': ('*/com.life360.android.safetymapd/databases/PetProfileRoomDatabase*',),
        'output_types': 'standard',
        'artifact_icon': 'smile'
    }
}

from datetime import datetime, timezone, timedelta
from scripts.ilapfuncs import (
    artifact_processor,
    get_file_path,
    get_sqlite_db_records,
    logfunc
)

@artifact_processor
def Life360_PetProfile(context):

    data_list = []

    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'PetProfileRoomDatabase')

    query = '''
    SELECT 
        createdAt AS "Created Timestamp",
        lastUpdated AS "Updated Timestamp",
        type AS "Type",
        petType AS "Pet Type",
        breed AS "Breed",
        color AS "Color",
        weightInKg AS "Weight kg", 
        gender AS "Gender",
        birthdate AS "Birthdate",
        name AS "Name",
        trackerId AS "Tracker ID",
        primaryCircleId AS "Circle ID",
        avatarBaseUrl AS "Avatar"
    FROM pet_profile
    '''

    try:
        db_records = get_sqlite_db_records(source_path, query)

        logfunc(f'Life360_PetProfile: Records found = {len(db_records)}')
        
        epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)

        for record in db_records:

            created_timestamp = datetime.fromtimestamp(int(record[0]) / 1000, tz=timezone.utc)
            updated_timestamp = datetime.fromtimestamp(int(record[1]) / 1000, tz=timezone.utc)
            birthdate = None
            if record[8] is not None:
                birthdate = epoch + timedelta(days=int(record[8]))

            data_list.append((created_timestamp, updated_timestamp, record[2], record[3], record[4], record[5], record[6], record[7], birthdate, record[9], record[10], record[11], record[12]))

    except Exception as e:  # pylint: disable=broad-exception-caught
        logfunc(f'Error processing Life360 PetProfile: {e}')

    data_headers = (('Created Timestamp', 'datetime'), ('Updated Timestamp', 'datetime'), 'Type', 'Pet Type', 'Breed', 'Color', 'Weight kg', 'Gender', ('Birthdate', 'datetime'), 'Name', 'Tracker ID', 'Circle ID', 'Avatar')

    return data_headers, data_list, source_path