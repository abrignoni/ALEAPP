# pylint: disable=W0718
__artifacts_v2__ = {
    "get_chromeAutofill": {
        "name": "Chrome Autofill - Entries",
        "description": "Parses Chrome autofill entries",
        "author": "@stark4n6",
        "creation_date": "2020-03-19",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Chromium",
        "notes": "A 'Web Data' database that cannot be read is logged and skipped, and the remaining browsers on the device are still reported. SQLite treats a non-empty '-journal' sidecar as a hot journal and begins a recovery that has to write, which a read-only handle cannot do. The pixel3_a12 image carries one file in that state, the Gmail WebView copy under data_mirror, whose sidecar holds 16 bytes of LevelDB text rather than a rollback journal. The storage-view dedupe selects the data/data spelling of that same database, so the unreadable copy is not opened during a normal run on this image; read with its journal ignored it holds no autofill rows.",
        "paths": ('*/app_chrome/Default/Web Data*', '*/app_sbrowser/Default/Web Data*', '*/data/*/app_opera/Web Data*', '*/app_webview/Default/Web Data*'),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "anne_a15": "Android 15 | 2 rows",
            "cookbook_a11": "Android 11 | 10 rows",
            "galaxys10_a10": "Android 10 | 6 rows",
            "hc_pixel8pro_a16": "Android 16 | 1 row",
            "hc_pixel8pro_a17": "Android 17 | 1 row",
            "kevin_pocox7_a15": "Android 15 | 1 row",
            "pixel3_a11": "Android 11 | 2 rows",
            "pixel3_a12": "Android 12 | 3 rows",
            "pixel7a_a14": "Android 14 | 4 rows",
            "russell_a14": "Android 14 | 8 rows",
            "russell_pixel6a_a13": "Android 13 | 8 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 6 rows",
            "samsungs20_a13": "Android 13 | 4 rows",
            "sharon_a13": "Android 13 | 3 rows",
            "sharon_a14": "Android 14 | 4 rows",
            "userb2_a13": "Android 13 | 6 rows",
        },
    },
    "get_chromeAutofillProfiles": {
        "name": "Chrome Autofill - Profiles",
        "description": "Parses Chrome autofill profiles",
        "author": "@stark4n6",
        "creation_date": "2020-03-19",
        "last_update_date": "2026-08-08",
        "requirements": "none",
        "category": "Chromium",
        "notes": "Chrome stores autofill address profiles in two layouts and both are read. Older releases use autofill_profiles joined to autofill_profile_names, _emails and _phones. Current releases use a single addresses table whose field values live in address_type_tokens, keyed by Chromium's FieldType enum; the values read are 3 NAME_FIRST, 4 NAME_MIDDLE, 5 NAME_LAST, 9 EMAIL_ADDRESS, 14 PHONE_HOME_WHOLE_NUMBER, 33 ADDRESS_HOME_CITY, 34 ADDRESS_HOME_STATE, 35 ADDRESS_HOME_ZIP, 60 COMPANY_NAME and 77 ADDRESS_HOME_STREET_ADDRESS. Field types outside that set are not reported rather than labelled, so a later Chrome field cannot reach the report under a guessed column; ADDRESS_HOME_COUNTRY and NAME_FULL are present in tested samples and are among those not reported. A third spelling, local_addresses, was seen empty on two tested images and is not read. Reference: Chromium, 'components/autofill/core/browser/field_types.h', https://github.com/chromium/chromium/blob/e90fec8693b4bd68806f3a5addec6722c0bc3939/components/autofill/core/browser/field_types.h",
        "paths": ('*/app_chrome/Default/Web Data*', '*/app_sbrowser/Default/Web Data*', '*/data/*/app_opera/Web Data*', '*/app_webview/Default/Web Data*'),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "anne_a15": "Android 15 | 0 rows",
            "cookbook_a11": "Android 11 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 2 rows",
            "hc_pixel8pro_a17": "Android 17 | 2 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "pixel3_a11": "Android 11 | 2 rows",
            "pixel3_a12": "Android 12 | 2 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "russell_a14": "Android 14 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 3 rows",
            "sharon_a13": "Android 13 | 2 rows",
            "sharon_a14": "Android 14 | 0 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
    }
}

import datetime
import os
import sqlite3

from scripts.ilapfuncs import logfunc, artifact_processor, open_sqlite_db_readonly
from scripts.artifacts.chrome import get_browser_name
from scripts.artifacts.storagePathViews import unique_files


def _seconds_to_utc(value):
    if value in (None, 0, ''):
        return ''
    return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)


def _browser_for(file_found):
    browser_name = get_browser_name(file_found)
    if file_found.find('app_sbrowser') >= 0:
        browser_name = 'Browser'
    return browser_name


@artifact_processor
def get_chromeAutofill(context):
    files_found = unique_files(context)
    all_data = []
    data_headers = ['Date Created', 'Field', 'Value', 'Date Last Used', 'Count']
    lava_data_headers = data_headers.copy()
    lava_data_headers[0] = (lava_data_headers[0], 'datetime')
    lava_data_headers[3] = (lava_data_headers[3], 'datetime')
    all_data_headers = lava_data_headers + ['Browser Name']
    report_file = 'Unknown'

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'Web Data':  # skip -journal and other files
            continue
        if file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue  # Skip mirror, it should be duplicate data

        browser_name = _browser_for(file_found)
        report_file = file_found if report_file == 'Unknown' else report_file + ', ' + file_found

        db = open_sqlite_db_readonly(file_found)
        if db is None:
            continue

        # One unreadable database must not end the artifact. A Web Data file left
        # with a non-empty rollback journal cannot be read through a read-only
        # handle, because SQLite has to write to replay and clear the journal.
        # Without this guard such a file ends the loop and every browser already
        # collected is dropped with it.
        data_list = []
        try:
            cursor = db.cursor()
            columns = [i[1] for i in cursor.execute('PRAGMA table_info(autofill)')]

            if not columns:
                # Some Web Data databases (e.g. embedded WebViews) have no autofill table
                logfunc(f'No {browser_name} autofill table available in {file_found}')
                continue

            if 'date_created' in columns:
                cursor.execute('select date_created, name, value, date_last_used, count from autofill')
                rows = cursor.fetchall()
                data_list = [(_seconds_to_utc(r[0]), r[1], r[2], _seconds_to_utc(r[3]), r[4]) for r in rows]
            else:
                cursor.execute('''
                    select autofill_dates.date_created, autofill.name, autofill.value, autofill.count
                    from autofill
                    join autofill_dates on autofill_dates.pair_id = autofill.pair_id
                ''')
                rows = cursor.fetchall()
                data_list = [(_seconds_to_utc(r[0]), r[1], r[2], '', r[3]) for r in rows]
        except sqlite3.Error as ex:
            logfunc(f'Unable to read {browser_name} autofill entries in {file_found}: {ex}')
            continue
        finally:
            db.close()

        if len(data_list) > 0:
            all_data.extend([row + (browser_name,) for row in data_list])
        else:
            logfunc(f'No {browser_name} - Autofill - Entries data available')

    return all_data_headers, all_data, report_file


# Chrome retired the autofill_profiles / autofill_profile_* join in favour of a
# single addresses table whose field values live in address_type_tokens, keyed by
# the FieldType enum. Both layouts are read, so one parser covers both generations.
# The type numbers are Chromium's own, checked against the pinned blob below.
# Reference: Chromium, 'components/autofill/core/browser/field_types.h',
# https://github.com/chromium/chromium/blob/e90fec8693b4bd68806f3a5addec6722c0bc3939/components/autofill/core/browser/field_types.h
CHROME_FIELD_TYPES = {
    'first_name': 3,     # NAME_FIRST
    'middle_name': 4,    # NAME_MIDDLE
    'last_name': 5,      # NAME_LAST
    'email': 9,          # EMAIL_ADDRESS
    'phone': 14,         # PHONE_HOME_WHOLE_NUMBER
    'city': 33,          # ADDRESS_HOME_CITY
    'state': 34,         # ADDRESS_HOME_STATE
    'zip': 35,           # ADDRESS_HOME_ZIP
    'company': 60,       # COMPANY_NAME
    'street': 77,        # ADDRESS_HOME_STREET_ADDRESS
}


def _table_exists(cursor, table):
    cursor.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cursor.fetchone() is not None


def _modern_autofill_profiles(cursor):
    """Read the addresses / address_type_tokens layout.

    Field types the map does not name are left out rather than guessed, so a
    later Chrome field cannot reach the report under an invented column.
    """
    tokens = {}
    cursor.execute('SELECT guid, type, value FROM address_type_tokens')
    for guid, field_type, value in cursor.fetchall():
        tokens.setdefault(guid, {})[field_type] = value

    cursor.execute('SELECT guid, date_modified, use_date, use_count FROM addresses')
    rows = []
    for guid, date_modified, use_date, use_count in cursor.fetchall():
        field = tokens.get(guid, {})
        rows.append((date_modified, guid) + tuple(
            field.get(CHROME_FIELD_TYPES[name], '') for name in
            ('first_name', 'middle_name', 'last_name', 'email', 'phone',
             'company', 'street', 'city', 'state', 'zip')) + (use_date, use_count))
    return rows


@artifact_processor
def get_chromeAutofillProfiles(context):
    files_found = unique_files(context)
    all_data = []
    data_headers = ['Date Modified', 'GUID', 'First Name', 'Middle Name', 'Last Name', 'Email',
                    'Phone Number', 'Company Name', 'Address', 'City', 'State', 'Zip Code',
                    'Date Last Used', 'Use Count']
    lava_data_headers = data_headers.copy()
    lava_data_headers[0] = (lava_data_headers[0], 'datetime')
    lava_data_headers[6] = (lava_data_headers[6], 'phonenumber')
    lava_data_headers[12] = (lava_data_headers[12], 'datetime')
    all_data_headers = lava_data_headers + ['Browser Name']
    report_file = 'Unknown'

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'Web Data':  # skip -journal and other files
            continue
        if file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue  # Skip mirror, it should be duplicate data

        browser_name = _browser_for(file_found)
        report_file = file_found if report_file == 'Unknown' else report_file + ', ' + file_found

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        try:
            if _table_exists(cursor, 'autofill_profiles'):
                cursor.execute('''
                    select
                        date_modified,
                        autofill_profiles.guid,
                        autofill_profile_names.first_name,
                        autofill_profile_names.middle_name,
                        autofill_profile_names.last_name,
                        autofill_profile_emails.email,
                        autofill_profile_phones.number,
                        autofill_profiles.company_name,
                        autofill_profiles.street_address,
                        autofill_profiles.city,
                        autofill_profiles.state,
                        autofill_profiles.zipcode,
                        use_date,
                        autofill_profiles.use_count
                    from autofill_profiles
                    inner join autofill_profile_emails ON autofill_profile_emails.guid = autofill_profiles.guid
                    inner join autofill_profile_phones ON autofill_profiles.guid = autofill_profile_phones.guid
                    inner join autofill_profile_names ON autofill_profile_phones.guid = autofill_profile_names.guid
                ''')
                rows = cursor.fetchall()
            elif _table_exists(cursor, 'addresses'):
                # Chrome release without the legacy tables
                rows = _modern_autofill_profiles(cursor)
            else:
                rows = []
        except Exception as e:
            logfunc(str(e))
            rows = []
        db.close()

        data_list = []
        for r in rows:
            data_list.append((_seconds_to_utc(r[0]), r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8],
                              r[9], r[10], r[11], _seconds_to_utc(r[12]), r[13]))

        if len(data_list) > 0:
            all_data.extend([row + (browser_name,) for row in data_list])
        else:
            logfunc(f'No {browser_name} - Autofill - Profiles data available')

    return all_data_headers, all_data, report_file
