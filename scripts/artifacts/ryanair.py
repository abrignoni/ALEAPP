__artifacts_v2__ = {
    "ryanair_user_profile": {
        "name": "Ryanair - User Profile",
        "description": "Parses the myRyanair account profile stored by the Ryanair Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Ryanair",
        "notes": "Read from the user_profile table of the app's Room database. Two schema "
                 "versions were seen across the tested samples and the columns they do not "
                 "share are selected only where the table declares them, so both parse. "
                 "birth_date and member_since are Unix milliseconds. Field mapping was done "
                 "against private samples provided by Mattia; no sample data is recorded "
                 "for them.",
        "paths": ('*/com.ryanair.cheapflights/databases/fr-local-db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user"
    },
    "ryanair_bookings": {
        "name": "Ryanair - Bookings",
        "description": "Parses bookings stored by the Ryanair Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Ryanair",
        "notes": "Each booking row carries a booking_json payload holding the record "
                 "locator, status, currency, balance due and the point of sale location "
                 "code. Server and user modification times come from the booking_timestamps "
                 "table in Unix milliseconds. Status and point of sale values are reported "
                 "as stored. Field mapping was done against private samples provided by "
                 "Mattia; no sample data is recorded for them.",
        "paths": ('*/com.ryanair.cheapflights/databases/fr-local-db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "briefcase"
    },
    "ryanair_flights": {
        "name": "Ryanair - Flights",
        "description": "Parses the flights of each booking stored by the Ryanair Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Ryanair",
        "notes": "The booking payload carries two sets of departure and arrival times. The "
                 "depart and arrive members are UTC and match the flight table's "
                 "departure_time_utc column exactly on the tested sample. The members under "
                 "times carry a Z suffix as well, but hold a time two hours later on a "
                 "sample whose route lay in a UTC+2 summer offset, and that same value is "
                 "the one repeated in the boarding pass key, so they are reported as local "
                 "and left as text rather than converted. Field mapping was done against "
                 "private samples provided by Mattia; no sample data is recorded for them.",
        "paths": ('*/com.ryanair.cheapflights/databases/fr-local-db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "send"
    },
    "ryanair_passengers": {
        "name": "Ryanair - Passengers",
        "description": "Parses the passengers of each booking stored by the Ryanair Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Ryanair",
        "notes": "Passengers come from the booking payload. Passenger type and title are "
                 "reported as stored. Check in status is taken from the payload's checkins "
                 "list, matched to the passenger by passenger number. Field mapping was "
                 "done against private samples provided by Mattia; no sample data is "
                 "recorded for them.",
        "paths": ('*/com.ryanair.cheapflights/databases/fr-local-db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "users"
    },
    "ryanair_boarding_passes": {
        "name": "Ryanair - Boarding Passes",
        "description": "Decrypts and parses boarding passes stored by the Ryanair Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "PyCryptodome",
        "category": "Ryanair",
        "notes": "The boardingpass table stores each pass as an encrypted blob. The key is "
                 "the base64 value under encryptionKeyBase64 in the app's own shared "
                 "preferences file, so both paths are needed. Decryption is AES-256 in CFB "
                 "mode with a 128 bit segment and an all zero initialisation vector, "
                 "established by trying candidate framings against the stored key until one "
                 "produced valid JSON, then confirmed by that JSON agreeing with the "
                 "booking's own record locator, route and times. Rows that do not decrypt "
                 "are reported with their key and an empty payload rather than dropped; "
                 "both tested passes decrypted, so that path was exercised on a constructed "
                 "copy with the key removed rather than on a sample. "
                 "Barcode Data is the string the app encodes into the scannable barcode, "
                 "reported as stored. Times without a UTC suffix are local. The tested "
                 "sample without boarding passes also had no key, so the key is not always "
                 "present. Field mapping was done against private samples provided by "
                 "Mattia; no sample data is recorded for them.",
        "paths": (
            '*/com.ryanair.cheapflights/databases/fr-local-db*',
            '*/com.ryanair.cheapflights/shared_prefs/com.ryanair.cheapflights_preferences.xml',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "credit-card"
    },
    "ryanair_recent_searches": {
        "name": "Ryanair - Recent Searches",
        "description": "Parses flight searches recorded by the Ryanair Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Ryanair",
        "notes": "The database is read twice through SQLite, immutable=1 to ignore the "
                 "write-ahead log and mode=ro to apply it, and the two are compared on the "
                 "row id. Rows present only in the first read are reported with a Source "
                 "View of Pre-checkpoint. On one tested sample the committed state returned "
                 "no rows at all while the file alone returned four, so the log carried "
                 "their removal. Why a row did not survive into the committed state is not "
                 "established here: app removal, a server re-sync and a user deletion all "
                 "produce the same result. The passenger count string is reported as "
                 "stored. Field mapping was done against private samples provided by "
                 "Mattia; no sample data is recorded for them.",
        "paths": ('*/com.ryanair.cheapflights/databases/fr-local-db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "search"
    },
    "ryanair_recent_locations": {
        "name": "Ryanair - Recent Locations",
        "description": "Parses recently used stations and countries from the Ryanair Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Ryanair",
        "notes": "Covers the recent_stations and recent_countries tables, distinguished by "
                 "the Record Type column. The country type integer is undocumented and is "
                 "reported as stored. Both tables use Unix milliseconds. recent_stations "
                 "held no rows in either tested sample. Field mapping was done against "
                 "private samples provided by Mattia; no sample data is recorded for them.",
        "paths": ('*/com.ryanair.cheapflights/databases/fr-local-db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "map-pin"
    },
    "ryanair_day_of_travel": {
        "name": "Ryanair - Day of Travel Content",
        "description": "Parses the day of travel journey content cached by the Ryanair Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Ryanair",
        "notes": "Rows come from the dot_booking_placeholder and dot_booking_product "
                 "tables, which hold the text the app displays for a journey in the "
                 "language it cached, including the purchased bags and equipment summary. "
                 "Text is reported as stored and may contain markup written by the app. "
                 "Placeholder and product identifiers are reported as stored. Field mapping "
                 "was done against private samples provided by Mattia; no sample data is "
                 "recorded for them.",
        "paths": ('*/com.ryanair.cheapflights/databases/fr-local-db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "file-text"
    },
    "ryanair_sessions": {
        "name": "Ryanair - Sessions",
        "description": "Parses session and remember me token claims from the Ryanair Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Ryanair",
        "notes": "The remember me preference holds a JSON Web Token. Its issued at and "
                 "expiry claims are reported as timestamps and the subject, token id and "
                 "issuer as identifiers; the signed token string itself is not written to "
                 "the report. The remaining single letter claims are reported as stored. "
                 "The token is read, not validated, so no claim here is evidence the token "
                 "was accepted by the service. Field mapping was done against private "
                 "samples provided by Mattia; no sample data is recorded for them.",
        "paths": (
            '*/com.ryanair.cheapflights/shared_prefs/MyRyanair_RememberMeToken.xml',
            '*/com.ryanair.cheapflights/shared_prefs/PreferencesBasketSessionKey.xml',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "clock"
    },
}

import base64
import binascii
import json
import os
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from Crypto.Cipher import AES

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    get_sqlite_db_path,
    logfunc,
    open_sqlite_db_readonly,
)

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_DB_NAME = 'fr-local-db'
_PREFS_NAME = 'com.ryanair.cheapflights_preferences.xml'


def _rows(source_path, sql):
    '''Rows for sql, with the write-ahead log applied. Empty on any SQLite error.'''
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    if not db:
        return []
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except sqlite3.Error as ex:
        logfunc(f'Could not query {os.path.basename(source_path)}: {ex}')
        rows = []
    db.close()
    return rows


def _rows_pre_wal(source_path, sql):
    '''Rows for sql as of the file's last checkpoint, ignoring the write-ahead log.

    immutable=1 is strictly read-only. Unlike mode=ro it does not even create a -shm
    sidecar, so no evidence file is altered. Path handling goes through the same
    get_sqlite_db_path() that open_sqlite_db_readonly() uses, so Windows long paths and
    URI-special characters behave identically.
    '''
    if not source_path:
        return []
    try:
        db = sqlite3.connect(f'file:{get_sqlite_db_path(source_path)}?immutable=1', uri=True)
    except sqlite3.Error:
        return []
    cursor = db.cursor()
    try:
        rows = cursor.execute(sql).fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


def _table_columns(source_path, table):
    '''The column names the file's own schema declares for table.'''
    return {row[1] for row in _rows(source_path, f'PRAGMA table_info({table})')}


def _select(source_path, table, columns, tail=''):
    '''A SELECT naming every column, substituting NULL for the ones this schema lacks.

    Two app versions were seen across the tested samples and they do not declare the same
    columns. NULL AS <name> keeps the result shape and the column names identical either
    way, so callers can index by position.
    '''
    present = _table_columns(source_path, table)
    if not present:
        return ''
    select_list = ', '.join(
        f'`{column}`' if column in present else f'NULL AS `{column}`' for column in columns)
    return f'SELECT {select_list} FROM `{table}` {tail}'


def _databases(context):
    '''The fr-local-db files the glob matched, one per storage view.'''
    return [path for path in unique_files(context)
            if os.path.basename(path) == _DB_NAME]


def _ms(value):
    '''A Unix millisecond value as a UTC datetime, or '' when absent or zero.

    Converted here rather than through convert_unix_ts_to_utc because this table stores
    birth dates, and one tested profile holds a 1952 birth date as -550713600000. That
    helper sizes its input with math.log10, which rejects a negative. Adding a timedelta
    to the epoch also avoids datetime.fromtimestamp, which raises on Windows for any
    value before 1970.
    '''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if not value:
        return ''
    return _EPOCH + timedelta(milliseconds=value)


def _iso(value):
    '''An ISO 8601 timestamp string as a UTC datetime, or '' when it will not parse.'''
    if not value or not isinstance(value, str):
        return ''
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return ''
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _booking_payloads(source_path):
    '''(booking id, decoded booking_json) for each booking row that holds valid JSON.'''
    payloads = []
    for booking_id, raw in _rows(source_path, 'SELECT `id`, `booking_json` FROM `booking`'):
        if not raw:
            continue
        try:
            payloads.append((booking_id, json.loads(raw)))
        except (json.JSONDecodeError, TypeError):
            logfunc(f'Could not decode booking_json for booking {booking_id}')
    return payloads


@artifact_processor
def ryanair_user_profile(context):
    columns = ('id', 'first_name', 'last_name', 'second_surname', 'email', 'phone_number',
               'country_calling_code', 'gender', 'birth_date', 'masked_birth_date',
               'nationality_code', 'title_name', 'title_type', 'member_since',
               'customer_state', 'prime_status', 'kyc_verified', 'auth_provider',
               'linked_social_accounts', 'specialAssistance', 'profile_progress',
               'deactivate')
    data_list = []
    sources = []

    for source_path in _databases(context):
        query = _select(source_path, 'user_profile', columns)
        if not query:
            continue
        relative_path = context.get_relative_path(source_path)
        for row in _rows(source_path, query):
            record = dict(zip(columns, row))
            data_list.append((
                _ms(record['member_since']),
                _ms(record['birth_date']),
                record['id'],
                record['first_name'],
                record['last_name'],
                record['second_surname'],
                record['email'],
                record['phone_number'],
                record['country_calling_code'],
                record['gender'],
                record['masked_birth_date'],
                record['nationality_code'],
                record['title_name'],
                record['title_type'],
                record['customer_state'],
                record['prime_status'],
                record['kyc_verified'],
                record['auth_provider'],
                record['linked_social_accounts'],
                record['specialAssistance'],
                record['profile_progress'],
                record['deactivate'],
                relative_path,
            ))
            sources.append(source_path)

    data_headers = (
        ('Member Since', 'datetime'),
        ('Birth Date', 'datetime'),
        'Profile ID',
        'First Name',
        'Last Name',
        'Second Surname',
        'Email',
        ('Phone Number', 'phonenumber'),
        'Country Calling Code',
        'Gender (as stored)',
        'Masked Birth Date (as stored)',
        'Nationality Code',
        'Title Name',
        'Title Type (as stored)',
        'Customer State (as stored)',
        'Prime Status (as stored)',
        'KYC Verified (as stored)',
        'Auth Provider (as stored)',
        'Linked Social Accounts (as stored)',
        'Special Assistance (as stored)',
        'Profile Progress (as stored)',
        'Deactivate (as stored)',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def ryanair_bookings(context):
    data_list = []
    sources = []

    for source_path in _databases(context):
        relative_path = context.get_relative_path(source_path)
        timestamps = {
            row[0]: (row[1], row[2]) for row in
            _rows(source_path, 'SELECT `booking_id`, `modified_utc_server_date`, '
                               '`modified_utc_user_date` FROM `booking_timestamps`')
        }
        for booking_id, payload in _booking_payloads(source_path):
            server_date, user_date = timestamps.get(booking_id, ('', ''))
            flights = payload.get('flights') or []
            routes = ', '.join(
                f"{flight.get('origin', '')}-{flight.get('destination', '')}"
                for flight in flights)
            data_list.append((
                _iso(payload.get('modifiedDate')),
                _ms(server_date),
                _ms(user_date),
                payload.get('recordLocator', ''),
                booking_id,
                payload.get('status', ''),
                routes,
                len(flights),
                len(payload.get('passengers') or []),
                payload.get('balanceDue', ''),
                payload.get('currency', ''),
                (payload.get('pos') or {}).get('locationCode', ''),
                ', '.join(str(ssr.get('code', '')) for ssr in payload.get('ssrs') or []),
                len(payload.get('linkedBookings') or []),
                relative_path,
            ))
            sources.append(source_path)

    data_headers = (
        ('Modified Date', 'datetime'),
        ('Modified UTC Server Date', 'datetime'),
        ('Modified UTC User Date', 'datetime'),
        'Record Locator',
        'Booking ID',
        'Status (as stored)',
        'Routes',
        'Flight Count',
        'Passenger Count',
        'Balance Due',
        'Currency',
        'Point Of Sale Location Code',
        'SSR Codes (as stored)',
        'Linked Booking Count',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def ryanair_flights(context):
    data_list = []
    sources = []

    for source_path in _databases(context):
        relative_path = context.get_relative_path(source_path)
        for booking_id, payload in _booking_payloads(source_path):
            record_locator = payload.get('recordLocator', '')
            for flight in payload.get('flights') or []:
                local_times = flight.get('times') or {}
                segments = flight.get('segments') or []
                cancelled = ', '.join(
                    str(segment.get('isCancelled', '')) for segment in segments)
                data_list.append((
                    _iso(flight.get('depart')),
                    _iso(flight.get('arrive')),
                    _iso(flight.get('checkInOpenUTC')),
                    _iso(flight.get('checkInCloseUTC')),
                    flight.get('flightNumber', ''),
                    flight.get('origin', ''),
                    flight.get('destination', ''),
                    local_times.get('depart', ''),
                    local_times.get('arrive', ''),
                    record_locator,
                    booking_id,
                    flight.get('journeyNum', ''),
                    len(segments),
                    cancelled,
                    relative_path,
                ))
                sources.append(source_path)

    data_headers = (
        ('Departure UTC', 'datetime'),
        ('Arrival UTC', 'datetime'),
        ('Check In Open UTC', 'datetime'),
        ('Check In Close UTC', 'datetime'),
        'Flight Number',
        'Origin',
        'Destination',
        'Departure Local (as stored)',
        'Arrival Local (as stored)',
        'Record Locator',
        'Booking ID',
        'Journey Number',
        'Segment Count',
        'Segment Cancelled (as stored)',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def ryanair_passengers(context):
    data_list = []
    sources = []

    for source_path in _databases(context):
        relative_path = context.get_relative_path(source_path)
        for booking_id, payload in _booking_payloads(source_path):
            checkins = {}
            for checkin in payload.get('checkins') or []:
                checkins.setdefault(checkin.get('paxNum'), []).append(
                    f"journey {checkin.get('journeyNum', '')} "
                    f"segment {checkin.get('segmentNum', '')}: "
                    f"{checkin.get('status', '')}")
            for passenger in payload.get('passengers') or []:
                pax_num = passenger.get('paxNum')
                data_list.append((
                    passenger.get('firstName', ''),
                    passenger.get('middleName', ''),
                    passenger.get('lastName', ''),
                    passenger.get('title', ''),
                    passenger.get('paxType', ''),
                    pax_num,
                    payload.get('recordLocator', ''),
                    booking_id,
                    '; '.join(checkins.get(pax_num, [])),
                    relative_path,
                ))
                sources.append(source_path)

    data_headers = (
        'First Name',
        'Middle Name',
        'Last Name',
        'Title (as stored)',
        'Passenger Type (as stored)',
        'Passenger Number',
        'Record Locator',
        'Booking ID',
        'Check In Status (as stored)',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


def _boarding_pass_key(prefs_paths):
    '''The AES key from encryptionKeyBase64, or None when no preferences file carries it.'''
    for prefs_path in prefs_paths:
        try:
            root = ET.parse(prefs_path).getroot()
        except (ET.ParseError, OSError) as ex:
            logfunc(f'Could not parse {os.path.basename(prefs_path)}: {ex}')
            continue
        for element in root:
            if element.get('name') != 'encryptionKeyBase64':
                continue
            try:
                return base64.b64decode(element.text or '')
            except (binascii.Error, ValueError):
                logfunc('encryptionKeyBase64 was not valid base64')
    return None


def _decrypt_boarding_pass(blob, key):
    '''The boarding pass payload, or None when the blob does not decrypt to JSON.'''
    if not key or not blob:
        return None
    try:
        plaintext = AES.new(key, AES.MODE_CFB, b'\x00' * 16, segment_size=128).decrypt(blob)
        return json.loads(plaintext)
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return None


@artifact_processor
def ryanair_boarding_passes(context):
    files_found = unique_files(context)
    prefs_paths = [path for path in files_found
                   if os.path.basename(path) == _PREFS_NAME]
    key = _boarding_pass_key(prefs_paths)
    if prefs_paths and not key:
        logfunc('Ryanair boarding pass key not found in the app preferences')

    data_list = []
    sources = []

    for source_path in files_found:
        if os.path.basename(source_path) != _DB_NAME:
            continue
        relative_path = context.get_relative_path(source_path)
        for uid, blob in _rows(source_path, 'SELECT `uid`, `body` FROM `boardingpass`'):
            payload = _decrypt_boarding_pass(blob, key)
            if payload is None:
                # Same width as a decrypted row: everything the payload would have filled
                # is blank, and the key stays visible so the row is not silently lost.
                data_list.append(('',) * 20 + (uid, 'Not decrypted', relative_path))
                sources.append(source_path)
                continue
            seat = f"{payload.get('seatRow', '')}{payload.get('seatColumn', '')}"
            flags = ', '.join(name for name, value in sorted(payload.items())
                              if name.startswith('is') and value is True)
            document = payload.get('boardingPassDocument') or {}
            data_list.append((
                _iso(payload.get('departureTimeUTC')),
                _iso(payload.get('arrivalTimeUTC')),
                _iso(payload.get('downloadTime')),
                payload.get('departureTime', ''),
                payload.get('boardingTime', ''),
                f"{payload.get('carrierCode', '')}{payload.get('flightNumber', '')}",
                payload.get('departureStationCode', ''),
                payload.get('arrivalStationCode', ''),
                f"{payload.get('paxFirstName', '')} {payload.get('paxLastName', '')}".strip(),
                payload.get('paxTitle', ''),
                payload.get('paxType', ''),
                seat,
                payload.get('sequenceNumber', ''),
                payload.get('gate', ''),
                payload.get('boardingZone', ''),
                payload.get('reservationNumber', ''),
                payload.get('barcodeData', ''),
                document.get('docNationality', ''),
                document.get('docCountryOfIssue', ''),
                flags,
                uid,
                'Decrypted',
                relative_path,
            ))
            sources.append(source_path)

    data_headers = (
        ('Departure UTC', 'datetime'),
        ('Arrival UTC', 'datetime'),
        ('Download Time', 'datetime'),
        'Departure Local (as stored)',
        'Boarding Time Local (as stored)',
        'Flight',
        'Departure Station',
        'Arrival Station',
        'Passenger Name',
        'Title (as stored)',
        'Passenger Type (as stored)',
        'Seat',
        'Sequence Number',
        'Gate',
        'Boarding Zone (as stored)',
        'Record Locator',
        'Barcode Data (as stored)',
        'Document Nationality',
        'Document Country Of Issue',
        'Flags Set (as stored)',
        'Boarding Pass Key (as stored)',
        'Decryption',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def ryanair_recent_searches(context):
    columns = ('id', 'last_search_date', 'fly_out_date', 'fly_back_date',
               'origin_airport_code', 'destination_airport_code', 'is_return_flight',
               'passengers_count', 'user_id')
    data_list = []
    sources = []

    for source_path in _databases(context):
        query = _select(source_path, 'recent_searches', columns, 'ORDER BY `id`')
        if not query:
            continue
        relative_path = context.get_relative_path(source_path)
        committed = _rows(source_path, query)
        committed_ids = {row[0] for row in committed}
        pre_wal = [row for row in _rows_pre_wal(source_path, query)
                   if row[0] not in committed_ids]

        for view, rows in (('Committed', committed), ('Pre-checkpoint', pre_wal)):
            for row in rows:
                record = dict(zip(columns, row))
                data_list.append((
                    _ms(record['last_search_date']),
                    _ms(record['fly_out_date']),
                    _ms(record['fly_back_date']),
                    record['origin_airport_code'],
                    record['destination_airport_code'],
                    record['is_return_flight'],
                    record['passengers_count'],
                    record['user_id'],
                    record['id'],
                    view,
                    relative_path,
                ))
                sources.append(source_path)

    data_headers = (
        ('Last Search Date', 'datetime'),
        ('Fly Out Date', 'datetime'),
        ('Fly Back Date', 'datetime'),
        'Origin Airport Code',
        'Destination Airport Code',
        'Is Return Flight (as stored)',
        'Passengers Count (as stored)',
        'User ID',
        'Row ID',
        'Source View',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def ryanair_recent_locations(context):
    data_list = []
    sources = []

    for source_path in _databases(context):
        relative_path = context.get_relative_path(source_path)
        for row in _rows(source_path, 'SELECT `last_usage`, `station_code`, '
                                      '`origin_station_code` FROM `recent_stations`'):
            data_list.append((_ms(row[0]), 'Station', row[1], row[2], '', relative_path))
            sources.append(source_path)
        for row in _rows(source_path, 'SELECT `last_used`, `country_code`, `type` '
                                      'FROM `recent_countries`'):
            data_list.append((_ms(row[0]), 'Country', row[1], '', row[2], relative_path))
            sources.append(source_path)

    data_headers = (
        ('Last Used', 'datetime'),
        'Record Type',
        'Code',
        'Origin Station Code',
        'Country Type (as stored)',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def ryanair_day_of_travel(context):
    data_list = []
    sources = []

    for source_path in _databases(context):
        relative_path = context.get_relative_path(source_path)
        modified = {
            (row[0], row[1]): row[2] for row in
            _rows(source_path, 'SELECT `booking_id`, `language`, `modified_date` '
                               'FROM `dot_booking`')
        }
        for row in _rows(source_path,
                         'SELECT `booking_id`, `journey_num`, `language`, `id`, `text` '
                         'FROM `dot_booking_placeholder`'):
            data_list.append((
                _ms(modified.get((row[0], row[2]), '')),
                'Placeholder', row[3], row[4], '', row[0], row[1], '', row[2],
                relative_path))
            sources.append(source_path)
        for row in _rows(source_path,
                         'SELECT `booking_id`, `journey_num`, `language`, `product_id`, '
                         '`text`, `pax_num` FROM `dot_booking_product`'):
            data_list.append((
                _ms(modified.get((row[0], row[2]), '')),
                'Product', row[3], row[4], '', row[0], row[1], row[5], row[2],
                relative_path))
            sources.append(source_path)
        for row in _rows(source_path,
                         'SELECT `booking_id`, `journey_num`, `language`, `id`, '
                         '`is_available` FROM `dot_booking_availability`'):
            data_list.append((
                _ms(modified.get((row[0], row[2]), '')),
                'Availability', row[3], '', row[4], row[0], row[1], '', row[2],
                relative_path))
            sources.append(source_path)

    data_headers = (
        ('Modified Date', 'datetime'),
        'Record Type',
        'Identifier (as stored)',
        'Text (as stored)',
        'Is Available (as stored)',
        'Booking ID',
        'Journey Number',
        'Passenger Number',
        'Language',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


_NAMED_CLAIMS = ('jti', 'iss', 'aud', 'sub', 'iat', 'exp')


def _jwt_claims(token):
    '''The decoded payload of a JSON Web Token, or None when it will not decode.

    The token is read, never verified. No claim returned here is evidence the token was
    accepted by the issuing service.
    '''
    parts = (token or '').split('.')
    if len(parts) != 3:
        return None
    try:
        padded = parts[1] + '=' * (-len(parts[1]) % 4)
        return json.loads(base64.urlsafe_b64decode(padded))
    except (binascii.Error, ValueError, json.JSONDecodeError):
        return None


@artifact_processor
def ryanair_sessions(context):
    data_list = []
    sources = []

    for source_path in unique_files(context):
        relative_path = context.get_relative_path(source_path)
        try:
            root = ET.parse(source_path).getroot()
        except (ET.ParseError, OSError) as ex:
            logfunc(f'Could not parse {os.path.basename(source_path)}: {ex}')
            continue

        for element in root:
            name = element.get('name')
            value = element.get('value') if element.get('value') is not None else element.text
            if not name:
                continue
            claims = _jwt_claims(value)
            if claims is None:
                data_list.append(('', '', name, '', '', '',
                                  'value present, not a JSON Web Token', relative_path))
                sources.append(source_path)
                continue
            other = '; '.join(f'{key}={claims[key]}' for key in sorted(claims)
                              if key not in _NAMED_CLAIMS)
            data_list.append((
                _ms(int(claims['iat']) * 1000) if str(claims.get('iat', '')).isdigit() else '',
                _ms(int(claims['exp']) * 1000) if str(claims.get('exp', '')).isdigit() else '',
                name,
                claims.get('sub', ''),
                claims.get('jti', ''),
                claims.get('iss', ''),
                other,
                relative_path,
            ))
            sources.append(source_path)

    data_headers = (
        ('Issued At', 'datetime'),
        ('Expires At', 'datetime'),
        'Preference Name',
        'Subject',
        'Token ID',
        'Issuer',
        'Other Claims (as stored)',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))
