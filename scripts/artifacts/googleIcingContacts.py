__artifacts_v2__ = {
    "gmsIcingContacts": {
        "name": "Icing Contacts",
        "description": "Snapshot of device contacts kept by Google Play services "
                       "(icing_contacts.db, contacts table). Kept independently "
                       "of the Contacts database, so the two may diverge.",
        "author": "",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Contacts",
        "notes": "",
        "paths": ('*/com.google.android.gms/databases/icing_contacts.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gms | 7 rows",
            "galaxys10_a10": "Android 10 | com.google.android.gms vc 210915037 | 3 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 9 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 4 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gms vc 232316044 | 3 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 8 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 5 rows",
            "sharon_a14": "Android 14 | com.google.android.gms vc 242835039 | 19 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 0 rows",
        },
    },
    "gmsIcingContactMethods": {
        "name": "Icing Contact Methods",
        "description": "Individual phone numbers, e-mail addresses and postal addresses "
                       "from the Google Play services contacts index (icing_contacts.db, "
                       "phones/emails/postals tables). The type is stored as a raw integer "
                       "and is reported as-is.",
        "author": "",
        "creation_date": "2026-07-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Contacts",
        "notes": "",
        "paths": ('*/com.google.android.gms/databases/icing_contacts.db*',),
        "output_types": "standard",
        "artifact_icon": "book",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gms | 8 rows",
            "galaxys10_a10": "Android 10 | com.google.android.gms vc 210915037 | 3 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 253830035 | 2 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 19 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 16 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gms vc 232316044 | 4 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 8 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 6 rows",
            "sharon_a14": "Android 14 | com.google.android.gms vc 242835039 | 26 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 0 rows",
        },
    },
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, \
    convert_unix_ts_to_utc, does_column_exist_in_db


def _unique_db_files(context, name_suffix):
    '''Database files matching the suffix, without -journal/-wal/-shm sidecars and
    without the duplicates extractions carry for the same file (data_mirror, and
    /data/data next to /data/user/0).'''
    seen = set()
    result = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith(name_suffix):
            continue
        if 'data_mirror' in file_found:
            continue
        normalized = file_found.replace('\\', '/').replace('/data/data/', '/data/user/0/')
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(file_found)
    return result


@artifact_processor
def gmsIcingContacts(context):
    data_list = []
    source_path = ''

    for file_found in _unique_db_files(context, 'icing_contacts.db'):
        # older Play services versions lack the last_updated_timestamp and starred columns
        updated_column = 'last_updated_timestamp' if does_column_exist_in_db(
            file_found, 'contacts', 'last_updated_timestamp') else "''"
        starred_column = 'starred' if does_column_exist_in_db(
            file_found, 'contacts', 'starred') else "''"
        db_records = get_sqlite_db_records(file_found, f'''
            SELECT {updated_column}, contact_id, display_name, given_names, nickname,
                   organization, note, emails, phone_numbers, postal_address,
                   times_contacted, {starred_column}, lookup_key
            FROM contacts
            ORDER BY display_name
        ''')

        for row in db_records:
            source_path = file_found
            data_list.append((
                convert_unix_ts_to_utc(row[0]) if row[0] else '',
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
                row[7],
                row[8],
                row[9],
                row[10],
                row[11],
                row[12],
            ))

    data_headers = (
        ('Last Updated', 'datetime'),
        'Contact ID',
        'Display Name',
        'Given Names',
        'Nickname',
        'Organization',
        'Note',
        'Emails',
        'Phone Numbers',
        'Postal Address',
        'Times Contacted',
        'Starred',
        'Lookup Key',
    )
    return data_headers, data_list, source_path


@artifact_processor
def gmsIcingContactMethods(context):
    data_list = []
    source_path = ''

    for file_found in _unique_db_files(context, 'icing_contacts.db'):
        db_records = get_sqlite_db_records(file_found, '''
            SELECT m.kind, m.value, m.label, m.type, m.contact_id, c.display_name
            FROM (
                SELECT 'Phone' AS kind, phone AS value, label, type, contact_id FROM phones
                UNION ALL
                SELECT 'Email' AS kind, email AS value, label, type, contact_id FROM emails
                UNION ALL
                SELECT 'Postal' AS kind, postal AS value, label, type, contact_id FROM postals
            ) AS m
            LEFT JOIN contacts AS c ON c.contact_id = m.contact_id
            ORDER BY c.display_name, m.kind
        ''')

        for row in db_records:
            source_path = file_found
            data_list.append((row[5], row[0], row[1], row[2], row[3], row[4]))

    data_headers = (
        'Display Name',
        'Kind',
        'Value',
        'Label',
        'Type',
        'Contact ID',
    )
    return data_headers, data_list, source_path
