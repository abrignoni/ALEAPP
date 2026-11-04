__artifacts_v2__ = {
    "get_chromeAutofill": {
        "name": "Chrome Autofill - Entries",
        "description": "Parses Chrome autofill entries",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2020-03-19",
        "last_update_date": "2026-09-12",
        "requirements": "none",
        "category": "Chromium",
        "notes": "A 'Web Data' database that cannot be read is logged and skipped, and the remaining browsers on the device are still reported. A database whose journal SQLite treats as hot cannot be opened through a read-only handle, because replaying that journal has to write. A non-empty journal is not by itself hot: four non-empty sidecars beside Chromium databases in the registered Android corpora were tested by opening the database read-only, and three of the four opened normally (Reference for the read-only limit: SQLite, 'Result and Error Codes', SQLITE_READONLY_ROLLBACK, https://www.sqlite.org/rescode.html#readonly_rollback). The one that did not is on the pixel3_a12 image, the Gmail WebView copy of 'Web Data' under data_mirror, whose 16-byte sidecar holds the LevelDB text 'MANIFEST-000001' rather than a rollback journal. The storage-view dedupe selects the data/data spelling of that same database, so the unreadable copy is not opened during a normal run on this image; read with its journal ignored it holds no autofill rows.",
        "paths": ('*/app_chrome/Default/Web Data*', '*/app_sbrowser/Default/Web Data*', '*/data/*/app_opera/Web Data*', '*/app_webview/Default/Web Data*'),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "anne_a15": "Android 15 | 2 rows",
            "cookbook_a11": "Android 11 | 10 rows",
            "galaxys10_a10": "Android 10 | 6 rows",
            "hc_pixel8pro_a16": "Android 16 | 1 row",
            "hc_pixel8pro_a17": "Android 17 | 1 row",
            "hickman_a13": "Android 13 | 4 rows",
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
        "description": "Addresses Chrome and other Chromium-based browsers hold for autofill: name, company, street, city, state, zip code, country, email and phone, with the modified and last used times and the use count",
        "author": "Kevin Pagano (@stark4n6), @AlexisBrignoni, Claude",
        "creation_date": "2020-03-19",
        "last_update_date": "2026-11-04",
        "requirements": "none",
        "category": "Chromium",
        "notes": "Chromium has kept saved addresses in three table layouts, and every layout a database holds is read, one row per address. Up to schema version 112 an address is a row of autofill_profiles, with its names, emails and phones in autofill_profile_names, autofill_profile_emails and autofill_profile_phones under the same guid. Version 113 moved addresses saved on the device to local_addresses, and account addresses sat in contact_info from version 107; both keep their values in a type token table (local_addresses_type_tokens, contact_info_type_tokens) of field type and value (Reference: Chromium, 'address_autofill_table.cc', https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/autofill/core/browser/webdata/addresses/address_autofill_table.cc#L975 and https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/autofill/core/browser/webdata/addresses/address_autofill_table.cc#L1009-L1050). Version 134 merged the two into addresses and address_type_tokens and added a record_type column (https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/autofill/core/browser/webdata/addresses/address_autofill_table.cc#L1094-L1105). A layout is read when its tables exist, and a column an older schema lacks is read as empty. Date Modified and Date Last Used are date_modified and use_date, seconds since 1970-01-01 UTC: Chromium writes them with base::Time::ToTimeT (https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/autofill/core/browser/webdata/addresses/address_autofill_table.cc#L379-L396) and reads the autofill_profiles columns with FromTimeT (https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/autofill/core/browser/webdata/addresses/address_autofill_table.cc#L166-L181). A zero is shown blank. Use Count is use_count as stored. Field values are mapped by Chromium's FieldType numbers: First Name is NAME_FIRST (3), Middle Name NAME_MIDDLE (4), Last Name NAME_LAST (5), Email EMAIL_ADDRESS (9), Phone Number PHONE_HOME_WHOLE_NUMBER (14), Company Name COMPANY_NAME (60), Address ADDRESS_HOME_STREET_ADDRESS (77), City ADDRESS_HOME_CITY (33), State ADDRESS_HOME_STATE (34), Zip Code ADDRESS_HOME_ZIP (35), Full Name NAME_FULL (7) and Country ADDRESS_HOME_COUNTRY (36), which holds the stored country code (Reference: Chromium, 'field_types.h', https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/autofill/core/browser/field_types.h#L141-L231 and https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/autofill/core/browser/field_types.h#L171-L175). field_types.h says the list is kept in step with the Autofill server and lists retired numbers as deprecated (https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/autofill/core/browser/field_types.h#L22-L26, https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/autofill/core/browser/field_types.h#L159-L161), so the same map is used for every schema version. autofill_profiles keeps the same values in named columns, mapped to the field types Chromium reads them as (https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/autofill/core/browser/webdata/addresses/address_autofill_table.cc#L166-L181, https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/autofill/core/browser/webdata/addresses/address_autofill_table.cc#L190-L206, https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/autofill/core/browser/webdata/addresses/address_autofill_table.cc#L304-L307, https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/autofill/core/browser/webdata/addresses/address_autofill_table.cc#L321-L324); honorific_prefix and full_name_with_honorific_prefix are named NAME_HONORIFIC_PREFIX and NAME_FULL_WITH_HONORIFIC_PREFIX from their column names, the second shown as 'NAME_FULL_WITH_HONORIFIC_PREFIX (deprecated)', since the current source no longer reads them, and field_types.h marks 117 deprecated (https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/autofill/core/browser/field_types.h#L327). Other Values lists every other non-empty stored value with its field type name, or 'type <n>' for a number this artifact does not name, so each stored name, email, phone and address value is reported once. Where a table holds more than one value for a guid and field type, the values are joined with '; '; that case was exercised on a constructed database only. A value stored as a BLOB is reported by its length and not decoded; no tested value was a BLOB. Record Type is record_type of addresses, named from AutofillProfile::RecordType (https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/autofill/core/browser/data_model/addresses/autofill_profile.h#L57-L100); local_addresses rows are reported as kLocalOrSyncable (0) and contact_info rows as one of the account types, the tables Chromium keeps those record types in (https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/autofill/core/browser/webdata/addresses/address_autofill_table.cc#L340-L352). Record Type is blank for autofill_profiles rows, which have no record type. Table names the table each row came from, so it holds one value on every row of a database with one layout. Measured 2026-11-04 on every 'Web Data' file in the 51 registered Android corpora, 1,894 copies on 40 of them with storage views counted separately (df020_mavic_pro_android, registered outside the Android tree, was listed separately and holds none); one copy, the Gmail WebView database on pixel3_a12 described under Chrome Autofill - Entries, could not be opened read-only. autofill_profiles was present in 352 copies on 10 corpora at schema versions 81 to 113 and held rows on pixel3_a11, pixel3_a12, sharon_a13 and hickman_a13. addresses was present in 76 copies on 15 corpora at versions 134 to 153 and held rows on hc_pixel8pro_a16, hc_pixel8pro_a17 and samsungs20_a13, where Record Type held kLocalOrSyncable (0), kAccount (1), kAccountHome (2) and kAccountNameEmail (4). local_addresses (1,245 copies on 27 corpora, versions 113 to 132) and contact_info (1,294 copies on 29 corpora, versions 107 to 132) held no rows on any, so neither branch is exercised on an Android image. The local_addresses branch was run on the desktop Web Data files of windows11_arm_chromium_autofill_known_20261103 (fictional addresses saved in Chromium 110, Chromium 120, Google Chrome 157 and Microsoft Edge 156 on Windows 11) staged under Android app paths: 7 rows, 2 from autofill_profiles, 2 from local_addresses and 3 from addresses, and every field both artifacts report agreed with DLEAPP's Chromium Autofill Addresses on the same files (DLEAPP has no GUID column and lists first, middle and last name under Other Values), except that this artifact also reports the full_name_with_honorific_prefix column of autofill_profile_names, which DLEAPP does not read. The contact_info branch was exercised on a constructed database only. On the tested Android rows Other Values held NAME_LAST_SECOND on 11 of 15 rows, and NAME_FULL_WITH_HONORIFIC_PREFIX on pixel3_a12, sharon_a13 and hickman_a13; it held no value on pixel3_a11, whose names table has no column past full_name. Middle Name and Company Name held no value on several tested images, Country held one value on all 3 samsungs20_a13 rows, Date Modified and Date Last Used were equal on all 7 known-data rows and on 5 of the 15 Android rows, and Use Count held 1 on all 7 known-data rows, where no address was filled into a form. Not read: server_addresses and server_address_metadata, which version 121 dropped (https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/autofill/core/browser/webdata/addresses/address_autofill_table.cc#L1072-L1077); autofill_profile_addresses and autofill_profile_birthdates; the *_status columns of autofill_profile_names, which Chromium reads as a verification status (https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/autofill/core/browser/webdata/addresses/address_autofill_table.cc#L203), and the origin and disallow_settings_visible_updates columns of autofill_profiles; label, language_code and the verification_status and observations columns of the token tables; and the payment card, IBAN and bank account tables.",
        "paths": ('*/app_chrome/Default/Web Data*', '*/app_sbrowser/Default/Web Data*', '*/data/*/app_opera/Web Data*', '*/app_webview/Default/Web Data*'),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "anne_a15": "Android 15 | 0 rows",
            "cookbook_a11": "Android 11 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 2 rows",
            "hc_pixel8pro_a17": "Android 17 | 2 rows",
            "hickman_a13": "Android 13 | 2 rows",
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
    report_files = []

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'Web Data':  # skip -journal and other files
            continue
        if file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue  # Skip mirror, it should be duplicate data

        browser_name = _browser_for(file_found)

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

        report_files.append(file_found)

        if len(data_list) > 0:
            all_data.extend([row + (browser_name,) for row in data_list])
        else:
            logfunc(f'No {browser_name} - Autofill - Entries data available')

    return all_data_headers, all_data, '\n'.join(report_files)


# Chromium has kept saved addresses in three layouts, and each one a database holds
# is read: autofill_profiles with its autofill_profile_names, _emails and _phones side
# tables up to schema version 112; local_addresses and contact_info, each with a type
# token table, from 113 (contact_info from 107) to 133; and addresses with
# address_type_tokens from 134, which merged the two and added record_type.
# Reference: Chromium, 'address_autofill_table.cc',
# https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4/components/autofill/core/browser/webdata/addresses/address_autofill_table.cc
#
# FieldType values as Chromium stores them in the type column of the token tables:
# components/autofill/core/browser/field_types.h, same commit. Retired values are
# marked deprecated there and not given to another field, so one map reads every
# schema version; 117 is one (line 327), and the Chromium 110 and 120 known data still hold it. Only the
# values an address can hold are named; any other value is reported as "type <n>".
CHROME_FIELD_TYPES = {
    3: 'NAME_FIRST', 4: 'NAME_MIDDLE', 5: 'NAME_LAST', 6: 'NAME_MIDDLE_INITIAL',
    7: 'NAME_FULL', 8: 'NAME_SUFFIX', 9: 'EMAIL_ADDRESS', 10: 'PHONE_HOME_NUMBER',
    11: 'PHONE_HOME_CITY_CODE', 12: 'PHONE_HOME_COUNTRY_CODE',
    13: 'PHONE_HOME_CITY_AND_NUMBER', 14: 'PHONE_HOME_WHOLE_NUMBER',
    30: 'ADDRESS_HOME_LINE1', 31: 'ADDRESS_HOME_LINE2', 32: 'ADDRESS_HOME_APT_NUM',
    33: 'ADDRESS_HOME_CITY', 34: 'ADDRESS_HOME_STATE', 35: 'ADDRESS_HOME_ZIP',
    36: 'ADDRESS_HOME_COUNTRY', 60: 'COMPANY_NAME', 77: 'ADDRESS_HOME_STREET_ADDRESS',
    79: 'ADDRESS_HOME_SORTING_CODE', 81: 'ADDRESS_HOME_DEPENDENT_LOCALITY',
    83: 'ADDRESS_HOME_LINE3', 103: 'ADDRESS_HOME_STREET_NAME',
    104: 'ADDRESS_HOME_HOUSE_NUMBER', 105: 'ADDRESS_HOME_SUBPREMISE',
    106: 'ADDRESS_HOME_OTHER_SUBUNIT', 107: 'NAME_LAST_FIRST', 108: 'NAME_LAST_CONJUNCTION',
    109: 'NAME_LAST_SECOND', 110: 'NAME_HONORIFIC_PREFIX', 114: 'ADDRESS_HOME_ADDRESS',
    115: 'ADDRESS_HOME_ADDRESS_WITH_NAME', 116: 'ADDRESS_HOME_FLOOR',
    117: 'NAME_FULL_WITH_HONORIFIC_PREFIX (deprecated)',
    121: 'PHONE_HOME_CITY_CODE_WITH_TRUNK_PREFIX',
    122: 'PHONE_HOME_CITY_AND_NUMBER_WITHOUT_TRUNK_PREFIX', 123: 'PHONE_HOME_NUMBER_PREFIX',
    124: 'PHONE_HOME_NUMBER_SUFFIX', 133: 'DELIVERY_INSTRUCTIONS', 135: 'ADDRESS_HOME_OVERFLOW',
    136: 'ADDRESS_HOME_LANDMARK', 140: 'ADDRESS_HOME_OVERFLOW_AND_LANDMARK',
    141: 'ADDRESS_HOME_ADMIN_LEVEL2', 142: 'ADDRESS_HOME_STREET_LOCATION',
    143: 'ADDRESS_HOME_BETWEEN_STREETS', 144: 'ADDRESS_HOME_BETWEEN_STREETS_OR_LANDMARK',
    145: 'ADDRESS_HOME_STREET_LOCATION_AND_LOCALITY',
    146: 'ADDRESS_HOME_STREET_LOCATION_AND_LANDMARK',
    150: 'ADDRESS_HOME_DEPENDENT_LOCALITY_AND_LANDMARK', 151: 'ADDRESS_HOME_BETWEEN_STREETS_1',
    152: 'ADDRESS_HOME_BETWEEN_STREETS_2', 153: 'ADDRESS_HOME_HOUSE_NUMBER_AND_APT',
    156: 'ADDRESS_HOME_APT', 157: 'ADDRESS_HOME_APT_TYPE', 163: 'ALTERNATIVE_FULL_NAME',
    164: 'ALTERNATIVE_GIVEN_NAME', 165: 'ALTERNATIVE_FAMILY_NAME', 201: 'ADDRESS_HOME_ZIP_PREFIX',
    202: 'ADDRESS_HOME_ZIP_SUFFIX', 207: 'ADDRESS_HOME_ZIP_AND_CITY',
}

# The field types given a column of their own, in the order the leading columns
# (First Name to Zip Code) and then Full Name and Country take them.
_LEADING_TYPES = (3, 4, 5, 9, 14, 60, 77, 33, 34, 35)
_TRAILING_TYPES = (7, 36)
_SHOWN_TYPES = _LEADING_TYPES + _TRAILING_TYPES

# AutofillProfile::RecordType, components/autofill/core/browser/data_model/addresses/
# autofill_profile.h lines 57-100, same commit.
_RECORD_TYPES = {0: 'kLocalOrSyncable', 1: 'kAccount', 2: 'kAccountHome', 3: 'kAccountWork',
                 4: 'kAccountNameEmail'}

# Metadata table, type token table and the record type its rows have. local_addresses
# holds kLocalOrSyncable profiles and contact_info the account ones
# (GetLegacyProfileMetadataTable, address_autofill_table.cc lines 340-352); addresses
# carries the record type in a column of its own.
_TOKEN_LAYOUTS = (
    ('addresses', 'address_type_tokens', None),
    ('local_addresses', 'local_addresses_type_tokens', 'kLocalOrSyncable (0)'),
    ('contact_info', 'contact_info_type_tokens', 'kAccount or kAccountHome or kAccountWork'),
)

# autofill_profiles columns and the field type Chromium reads each as
# (AddLegacyAutofillProfileDetailsFromStatement, address_autofill_table.cc lines
# 166-181), and the side tables read by guid with theirs (lines 190-206, 304-307,
# 321-324). honorific_prefix and full_name_with_honorific_prefix are named from their
# column names, since the current source no longer reads them.
_LEGACY_PROFILE_COLUMNS = (
    ('company_name', 60), ('street_address', 77), ('dependent_locality', 81), ('city', 33),
    ('state', 34), ('zipcode', 35), ('sorting_code', 79), ('country_code', 36),
)
_LEGACY_SIDE_TABLES = (
    ('autofill_profile_names', (('first_name', 3), ('middle_name', 4), ('last_name', 5),
                                ('full_name', 7), ('honorific_prefix', 110),
                                ('first_last_name', 107), ('conjunction_last_name', 108),
                                ('second_last_name', 109),
                                ('full_name_with_honorific_prefix', 117))),
    ('autofill_profile_emails', (('email', 9),)),
    ('autofill_profile_phones', (('number', 14),)),
)


def _table_columns(cursor, table):
    return [row[1] for row in cursor.execute(f'PRAGMA table_info("{table}")')]


def _value(value):
    """A stored value as text. A BLOB is reported by its length, not decoded."""
    if value is None:
        return ''
    if isinstance(value, bytes):
        return f'[{len(value)} bytes, not decoded]' if value else ''
    return str(value)


def _select(present, wanted):
    """A SELECT list naming each wanted column, NULL where the table lacks it."""
    return ', '.join(f'"{column}"' if column in present else 'NULL' for column in wanted)


def _address_row(date_modified, guid, use_date, use_count, fields, record_type, table):
    """One report row from a profile's {field type: [values]}.

    Values of a field type given no column of its own go to Other Values, so every
    stored value is reported somewhere and none twice.
    """
    def joined(field_type):
        return '; '.join(fields.get(field_type, []))
    other = '; '.join(f'{CHROME_FIELD_TYPES.get(field_type, f"type {field_type}")}: {value}'
                      for field_type in sorted(fields) if field_type not in _SHOWN_TYPES
                      for value in fields[field_type])
    return ((_seconds_to_utc(date_modified), guid)
            + tuple(joined(field_type) for field_type in _LEADING_TYPES)
            + (_seconds_to_utc(use_date), use_count)
            + tuple(joined(field_type) for field_type in _TRAILING_TYPES)
            + (other, record_type, table))


def _token_autofill_profiles(cursor, meta_table, token_table, record_type):
    """Read one metadata table and its type token table, one row per profile."""
    present = _table_columns(cursor, meta_table)
    if not present or not _table_columns(cursor, token_table):
        return []
    tokens = {}
    cursor.execute(f'SELECT guid, type, value FROM "{token_table}" ORDER BY guid, type')
    for guid, field_type, value in cursor.fetchall():
        text = _value(value)
        if text:
            tokens.setdefault(guid, {}).setdefault(field_type, []).append(text)
    cursor.execute(f'SELECT {_select(present, ("guid", "date_modified", "use_date", "use_count", "record_type"))} '
                   f'FROM "{meta_table}"')
    rows = []
    for guid, date_modified, use_date, use_count, stored_type in cursor.fetchall():
        kind = record_type
        if kind is None:
            kind = '' if stored_type is None else \
                f'{_RECORD_TYPES.get(stored_type, "unknown")} ({stored_type})'
        rows.append(_address_row(date_modified, guid, use_date, use_count,
                                 tokens.get(guid, {}), kind, meta_table))
    return rows


def _legacy_autofill_profiles(cursor):
    """Read the autofill_profiles layout, one row per profile.

    Chromium reads a profile from autofill_profiles and then looks up its name,
    email and phone by guid, so a profile with no row in one of those tables is
    still a profile, and a second row for the same guid is not a second profile.
    Every stored value is reported: more than one for a guid is joined with
    '; ' in rowid order. Columns a schema version lacks are read as empty.
    """
    present = _table_columns(cursor, 'autofill_profiles')
    if not present:
        return []
    side = {}
    for table, columns in _LEGACY_SIDE_TABLES:
        side_present = _table_columns(cursor, table)
        wanted = [(column, field_type) for column, field_type in columns if column in side_present]
        if 'guid' not in side_present or not wanted:
            continue
        cursor.execute(f'SELECT guid, {", ".join(column for column, _ in wanted)} '
                       f'FROM "{table}" ORDER BY rowid')
        for record in cursor.fetchall():
            fields = side.setdefault(record[0], {})
            for (_column, field_type), value in zip(wanted, record[1:]):
                text = _value(value)
                if text:
                    fields.setdefault(field_type, []).append(text)
    profile_columns = [column for column, _ in _LEGACY_PROFILE_COLUMNS]
    cursor.execute(f'SELECT {_select(present, ["guid", "date_modified", "use_date", "use_count"] + profile_columns)} '
                   'FROM autofill_profiles')
    rows = []
    for record in cursor.fetchall():
        guid, date_modified, use_date, use_count = record[:4]
        fields = {field_type: list(values) for field_type, values in side.get(guid, {}).items()}
        for (_column, field_type), value in zip(_LEGACY_PROFILE_COLUMNS, record[4:]):
            text = _value(value)
            if text:
                fields.setdefault(field_type, []).append(text)
        rows.append(_address_row(date_modified, guid, use_date, use_count, fields, '',
                                 'autofill_profiles'))
    return rows


@artifact_processor
def get_chromeAutofillProfiles(context):
    files_found = unique_files(context)
    all_data = []
    data_headers = ['Date Modified', 'GUID', 'First Name', 'Middle Name', 'Last Name', 'Email',
                    'Phone Number', 'Company Name', 'Address', 'City', 'State', 'Zip Code',
                    'Date Last Used', 'Use Count', 'Full Name', 'Country', 'Other Values',
                    'Record Type', 'Table']
    lava_data_headers = data_headers.copy()
    lava_data_headers[0] = (lava_data_headers[0], 'datetime')
    lava_data_headers[6] = (lava_data_headers[6], 'phonenumber')
    lava_data_headers[12] = (lava_data_headers[12], 'datetime')
    all_data_headers = lava_data_headers + ['Browser Name']
    report_files = []

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'Web Data':  # skip -journal and other files
            continue
        if file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue  # Skip mirror, it should be duplicate data

        browser_name = _browser_for(file_found)

        db = open_sqlite_db_readonly(file_found)
        if db is None:
            continue

        try:
            cursor = db.cursor()
            data_list = _legacy_autofill_profiles(cursor)
            for meta_table, token_table, record_type in _TOKEN_LAYOUTS:
                data_list.extend(_token_autofill_profiles(cursor, meta_table, token_table, record_type))
        except sqlite3.Error as ex:
            logfunc(f'Unable to read {browser_name} autofill profiles in {file_found}: {ex}')
            continue
        finally:
            db.close()

        report_files.append(file_found)

        if len(data_list) > 0:
            all_data.extend([row + (browser_name,) for row in data_list])
        else:
            logfunc(f'No {browser_name} - Autofill - Profiles data available')

    return all_data_headers, all_data, '\n'.join(report_files)
