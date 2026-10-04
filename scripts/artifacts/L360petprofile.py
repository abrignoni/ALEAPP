__artifacts_v2__ = {
    'Life360_PetProfile': {
        'name': 'Life360 PetProfile',
        'description': 'Pet profiles stored in the Life360 Android PetProfileRoomDatabase database.',
        'author': 'Heather Charpentier',
        'creation_date': '2026-06-10',
        'last_update_date': '2026-10-04',
        'requirements': 'none',
        'category': 'Life360',
        'notes': (
            'One row per row of the pet_profile table. Created Timestamp and Updated Timestamp are the '
            'createdAt and lastUpdated columns read as Unix milliseconds and shown in UTC. The table '
            'declares createdAt without NOT NULL, so a row that stores none shows a blank Created '
            'Timestamp; no tested row was like that. '
            'Birthdate (as stored) is the birthdate column, an INTEGER, shown as the number the '
            'database holds. The table definition does not state its unit and no source for the unit '
            'was found. Birthdate Read As Days Since 1970-01-01 is that number counted as days from '
            '1970-01-01 and shown as a calendar date in text, with no time and no time zone. That '
            'reading is not established: on hc_pixel8pro_a16 both rows store a five digit number, '
            'which read as days gives a date in 2019, about seven years before the rows were created. '
            'The date is plausible and that is all the measurement shows.'
        ),
        'paths': ('*/com.life360.android.safetymapd/databases/PetProfileRoomDatabase*',),
        'output_types': 'standard',
        'artifact_icon': 'mood-smile',
        'sample_data': {
            'hc_pixel8pro_a16': 'Android 16 | com.life360.android.safetymapd vc 2897710 | 2 rows',
        }
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

        epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)

        for record in db_records:

            created_timestamp = ''
            if record[0] is not None:
                created_timestamp = datetime.fromtimestamp(int(record[0]) / 1000, tz=timezone.utc)
            updated_timestamp = datetime.fromtimestamp(int(record[1]) / 1000, tz=timezone.utc)
            birthdate = ''
            if record[8] is not None:
                try:
                    birthdate = (epoch + timedelta(days=int(record[8]))).strftime('%Y-%m-%d')
                except (ValueError, OverflowError):
                    birthdate = ''

            data_list.append((created_timestamp, updated_timestamp, record[2], record[3], record[4],
                              record[5], record[6], record[7], record[8], birthdate, record[9], record[10],
                              record[11], record[12]))

    except Exception as e:  # pylint: disable=broad-exception-caught
        logfunc(f'Error processing Life360 PetProfile: {e}')

    data_headers = (('Created Timestamp', 'datetime'), ('Updated Timestamp', 'datetime'), 'Type',
                    'Pet Type', 'Breed', 'Color', 'Weight kg', 'Gender', 'Birthdate (as stored)',
                    'Birthdate Read As Days Since 1970-01-01', 'Name', 'Tracker ID', 'Circle ID', 'Avatar')

    return data_headers, data_list, source_path
