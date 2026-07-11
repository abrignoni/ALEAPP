# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_chromeAutofill": {
        "name": "Chrome Autofill - Entries",
        "description": "Parses Chrome autofill entries",
        "author": "",
        "creation_date": "2020-03-19",
        "last_update_date": "2026-07-10",
        "requirements": "none",
        "category": "Chromium",
        "notes": "",
        "paths": ('*/app_chrome/Default/Web Data*', '*/app_sbrowser/Default/Web Data*', '*/data/*/app_opera/Web Data*', '*/app_webview/Default/Web Data*'),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 6 rows",
            "pixel7a_a14": "Android 14 | 4 rows",
            "sharon_a14": "Android 14 | 4 rows",
            "anne_a15": "Android 15 | 2 rows",
            "hc_pixel8pro_a16": "Android 16 | 1 row",
            "kevin_pocox7_a15": "Android 15 | 1 row",
            "samsunga53_a14": "Android 14 | 18 rows",
            "samsungs20_a13": "Android 13 | 4 rows",
        },
    },
    "get_chromeAutofillProfiles": {
        "name": "Chrome Autofill - Profiles",
        "description": "Parses Chrome autofill profiles",
        "author": "",
        "creation_date": "2020-03-19",
        "last_update_date": "2020-03-19",
        "requirements": "none",
        "category": "Chromium",
        "notes": "",
        "paths": ('*/app_chrome/Default/Web Data*', '*/app_sbrowser/Default/Web Data*', '*/data/*/app_opera/Web Data*', '*/app_webview/Default/Web Data*'),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "anne_a15": "Android 15 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 0 rows",
        },
    }
}

import datetime
import os

from scripts.ilapfuncs import logfunc, artifact_processor, open_sqlite_db_readonly
from scripts.artifacts.chrome import get_browser_name


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
def get_chromeAutofill(files_found, report_folder, seeker, wrap_text):
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
        cursor = db.cursor()
        columns = [i[1] for i in cursor.execute('PRAGMA table_info(autofill)')]

        if not columns:
            # Some Web Data databases (e.g. embedded WebViews) have no autofill table
            logfunc(f'No {browser_name} autofill table available in {file_found}')
            db.close()
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
        db.close()

        if len(data_list) > 0:
            all_data.extend([row + (browser_name,) for row in data_list])
        else:
            logfunc(f'No {browser_name} - Autofill - Entries data available')

    return all_data_headers, all_data, report_file


@artifact_processor
def get_chromeAutofillProfiles(files_found, report_folder, seeker, wrap_text):
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
