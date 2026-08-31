__artifacts_v2__ = {
    "booking_reservations": {
        "name": "Booking - Reservations",
        "description": "Parses accommodation reservations cached by the Booking.com Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "Read from the records table of post_booking_reservation_cache, which holds a "
                 "normalised GraphQL cache. Each row is one cache record; the key names the field "
                 "path and the value is its JSON, with nested objects held as ApolloCacheReference "
                 "strings that the parser follows. Two query shapes were seen across the tested "
                 "samples. The postBookingReservationQuery shape carries the booking number and PIN "
                 "code inside its own key, and the accommodationDetailsQueries shape carries them as "
                 "record fields. Rows from both shapes are merged on the booking number and the "
                 "Query Shapes column says which contributed. reservationCheckinDate.rawDate and "
                 "reservationCheckoutDate.rawDate are Unix seconds; each of the twelve values in the "
                 "tested samples fell on midnight in the timezone the same record stores as "
                 "hotelTimezone, so the calendar date at the property is carried in its own column "
                 "and the datetime columns hold the UTC reading of the stored value. The "
                 "accommodationDetails shape instead stores ISO 8601 strings carrying an offset, and "
                 "those are converted from that offset. Status, travel purpose and accommodation "
                 "type values are reported as stored. Field mapping was done against private samples "
                 "provided by Mattia; no sample data is recorded for them.",
        "paths": ('*/com.booking/databases/post_booking_reservation_cache*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "briefcase"
    },
    "booking_reservation_rooms": {
        "name": "Booking - Reservation Rooms",
        "description": "Parses the rooms of each cached Booking.com Android reservation.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "Read from the roomReservations records of post_booking_reservation_cache and "
                 "joined to the booking number held in the parent record's key. An app version "
                 "seen in the tested samples caches the same booking once per authentication "
                 "key it was fetched with, so one room was held in two records that were "
                 "identical once the key inside their references was set aside; rows are "
                 "reported once per booking number and roomReservationId pair so a room is not "
                 "counted twice. Room type "
                 "identifiers, smoking preference, cancellation type and cancellation bucket are "
                 "reported as stored. The refundable member of the cancellation info record is "
                 "reported as stored; it held 0 on every room in the tested samples and no source "
                 "was found defining its other values. Field mapping was done against private "
                 "samples provided by Mattia; no sample data is recorded for them.",
        "paths": ('*/com.booking/databases/post_booking_reservation_cache*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "bed"
    },
    "booking_account_profile": {
        "name": "Booking - Account Profile",
        "description": "Parses the account profile cached by the Booking.com Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "Read from the records table of account_data_cache, a normalised GraphQL cache "
                 "holding the personalProfile record and, on the app versions that write them, the "
                 "genius and wallet records. Gender and genius level are reported as stored. "
                 "dateOfBirth is passed through as stored because it was null on both tested "
                 "profiles, so no format could be established for it. The travelDocuments and "
                 "coTravellers members are lists and their counts are reported; both were empty on "
                 "the tested profiles. Field mapping was done against private samples provided by "
                 "Mattia; no sample data is recorded for them.",
        "paths": ('*/com.booking/databases/account_data_cache*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user"
    },
    "booking_profile_preferences": {
        "name": "Booking - Profile Preferences",
        "description": "Parses the account profile written to the Booking.com Android preferences.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "Read from the mybooking.xml and remote_profile.xml preference files, which carry "
                 "the same pref3 prefixed profile keys. On the tested samples remote_profile.xml "
                 "held a subset of the keys in mybooking.xml, and the Source File column says which "
                 "file each row came from. Title, gender, smoking preference and travel purpose are "
                 "reported as stored. The google state value is the app's own JSON record of a "
                 "linked Google account and its identifier member is reported as stored. Field "
                 "mapping was done against private samples provided by Mattia; no sample data is "
                 "recorded for them.",
        "paths": (
            '*/com.booking/shared_prefs/mybooking.xml',
            '*/com.booking/shared_prefs/remote_profile.xml',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user-circle"
    },
    "booking_cached_profile": {
        "name": "Booking - Cached Profile Response",
        "description": "Parses cached account profile responses from the Booking.com Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "Read from the app's OkHttp response cache, where each entry is a pair of files "
                 "sharing a name: the .0 file holds the request URL and the response headers and "
                 "the .1 file holds the body. Bodies for this endpoint were gzip compressed on the "
                 "tested samples and are decompressed before parsing. The request time comes from "
                 "the OkHttp-Sent-Millis header OkHttp writes into the cached entry, in Unix "
                 "milliseconds. The response carries a cc_details list for stored payment cards; it "
                 "was empty on both tested samples, so no card data is reported from them. Field "
                 "mapping was done against private samples provided by Mattia; no sample data is "
                 "recorded for them.",
        "paths": ('*/com.booking/cache/okhttp/*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "id"
    },
    "booking_search_query": {
        "name": "Booking - Search Query",
        "description": "Parses the stored search query of the Booking.com Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "Read from the specific_query and general_query keys of "
                 "com.booking_preferences.xml, each holding one JSON search query. The two keys held "
                 "identical values on all four tested samples and both are reported, with the Query "
                 "Key column saying which. Arrival and departure dates are stored as plain date "
                 "strings and are reported as stored, since the file records no timezone for them. "
                 "The location member carries the destination the search was made against; its type "
                 "and source members are reported as stored. Field mapping was done against private "
                 "samples provided by Mattia; no sample data is recorded for them.",
        "paths": ('*/com.booking/shared_prefs/com.booking_preferences.xml',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "search"
    },
    "booking_destination_searches": {
        "name": "Booking - Destination Searches",
        "description": "Parses cached destination autocomplete responses from the Booking.com Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "Read from the app's OkHttp response cache. The text parameter of the cached "
                 "mobile.autocomplete request URL holds the characters the request was made for, and "
                 "the response body holds the destinations returned for it, one row each. The "
                 "request time comes from the OkHttp-Sent-Millis header in Unix milliseconds. "
                 "Coordinates are the latitude and longitude members of each returned destination, "
                 "so a row records a destination offered against those characters and not a place "
                 "the device was. Destination type is reported as stored. Field mapping was done "
                 "against private samples provided by Mattia; no sample data is recorded for them.",
        "paths": ('*/com.booking/cache/okhttp/*',),
        "output_types": "all",
        "artifact_icon": "map-search"
    },
    "booking_destination_info": {
        "name": "Booking - Destination Info",
        "description": "Parses cached destination lookups from the Booking.com Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "Read from the app's OkHttp response cache. The type_and_id parameter of the "
                 "cached mobile.getDestinationInfo request URL names the destination looked up and "
                 "the response body holds its record. The request time comes from the "
                 "OkHttp-Sent-Millis header in Unix milliseconds. Coordinates are the latitude and "
                 "longitude members of the returned destination record, so a row records a place "
                 "the app looked up and not a place the device was. Destination type is reported as "
                 "stored. Field mapping was done against private samples provided by Mattia; no "
                 "sample data is recorded for them.",
        "paths": ('*/com.booking/cache/okhttp/*',),
        "output_types": "all",
        "artifact_icon": "map-pin"
    },
    "booking_deep_links": {
        "name": "Booking - Deep Links",
        "description": "Parses deep links stored and resolved by the Booking.com Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "Two sources are reported and the Record Type column says which each row came "
                 "from. Resolved links come from cached mobile.decodeUniversalLink responses in the "
                 "app's OkHttp response cache, where the url request parameter holds the link "
                 "submitted and the body holds what it resolved to; those rows carry the request "
                 "time from the OkHttp-Sent-Millis header in Unix milliseconds. Stored links come "
                 "from original_link_storage.xml, whose keys are named for the screen each link was "
                 "kept against and which records no timestamp. Link actions and destination types "
                 "are reported as stored. Field mapping was done against private samples provided "
                 "by Mattia; no sample data is recorded for them.",
        "paths": (
            '*/com.booking/cache/okhttp/*',
            '*/com.booking/shared_prefs/original_link_storage.xml',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "link"
    },
    "booking_notifications": {
        "name": "Booking - Notifications",
        "description": "Parses notifications stored by the Booking.com Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "Read from the notification table of notifications.db. time_epoch is Unix seconds; "
                 "the value in the tested samples resolved to a date within the app's installed "
                 "life on that image, which a millisecond reading would not. The viewed, clicked "
                 "and deleted columns are reported as stored, as are their sync counterparts and "
                 "the action identifier. args_json is the notification's own payload and is "
                 "reported as stored. Field mapping was done against private samples provided by "
                 "Mattia; no sample data is recorded for them.",
        "paths": ('*/com.booking/databases/notifications.db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "bell"
    },
    "booking_app_state": {
        "name": "Booking - App State",
        "description": "Parses install, session and attribution state of the Booking.com Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "Read from com.booking_preferences.xml and startup_data.xml. first_use and the "
                 "deep link attribution expiry are Unix milliseconds. The used key is a counter "
                 "rather than a time and is reported as stored. The client IP address and client "
                 "user agent are the values the app recorded for itself, so they describe what the "
                 "service was told and are reported as stored. PRICE_ALERT_SCREEN_LAST_SEEN is an "
                 "ISO 8601 string and held the same value on all four tested samples, which is a "
                 "date preceding the app versions they carry, so it is reported as stored rather "
                 "than read as a time the screen was opened. Field mapping was done against private "
                 "samples provided by Mattia; no sample data is recorded for them.",
        "paths": (
            '*/com.booking/shared_prefs/com.booking_preferences.xml',
            '*/com.booking/shared_prefs/startup_data.xml',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings"
    },
    "booking_cached_requests": {
        "name": "Booking - Cached Requests",
        "description": "Inventories the cached HTTP responses held by the Booking.com Android app.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Booking.com",
        "notes": "One row for each entry in the app's two OkHttp response caches, okhttp and "
                 "saba-http-cache. The request and response times come from the OkHttp-Sent-Millis "
                 "and OkHttp-Received-Millis headers OkHttp writes into the cached entry, in Unix "
                 "milliseconds, and the served date is the response's own date header reported as "
                 "stored. The device identifier, app version and language are read from the request "
                 "URL's own parameters. This artifact reports the entries and their metadata; the "
                 "bodies of the profile, autocomplete, destination and universal link endpoints are "
                 "parsed by the other artifacts in this module. Field mapping was done against "
                 "private samples provided by Mattia; no sample data is recorded for them.",
        "paths": (
            '*/com.booking/cache/okhttp/*',
            '*/com.booking/cache/saba-http-cache/*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cloud-download"
    },
}

import gzip
import json
import os
import re
import sqlite3
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

import pytz

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    logfunc,
    open_sqlite_db_readonly,
)

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_REFERENCE = re.compile(r'^ApolloCacheReference\{(.*)\}$', re.DOTALL)
_RESERVATION_DB = 'post_booking_reservation_cache'
_ACCOUNT_DB = 'account_data_cache'
_NOTIFICATION_DB = 'notifications.db'
_POST_BOOKING_ROOT = 'postBookingReservationQuery('
_ACCOMMODATION_ROOT = 'accommodationDetailsQueries.accommodationDetails('


def _files(context, names=None, suffix=None):
    '''The matched files, duplicate storage views removed, filtered by name or suffix.'''
    selected = []
    for path in unique_files(context):
        base = os.path.basename(path)
        if names is not None and base not in names:
            continue
        if suffix is not None and not base.endswith(suffix):
            continue
        selected.append(path)
    return selected


def _ms(value):
    '''A Unix millisecond value as a UTC datetime, or '' when absent or zero.

    Adding a timedelta to the epoch rather than calling convert_unix_ts_to_utc, which
    sizes its input with math.log10 and so rejects any value before 1970, and rather than
    datetime.fromtimestamp, which raises on Windows for the same values.
    '''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if not value:
        return ''
    return _EPOCH + timedelta(milliseconds=value)


def _seconds(value):
    '''A Unix second value as a UTC datetime, or '' when absent or zero.'''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if not value:
        return ''
    return _EPOCH + timedelta(seconds=value)


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


def _local_date(moment, zone_name):
    '''The calendar date of moment in zone_name, or '' when either is missing.

    The reservation records store a check in and check out value that fell on midnight in
    the timezone the same reservation records as hotelTimezone, so the date a reader wants
    is the one in that zone rather than the one the UTC rendering shows.
    '''
    if not isinstance(moment, datetime) or not zone_name:
        return ''
    try:
        zone = pytz.timezone(str(zone_name))
    except pytz.exceptions.Error:
        return ''
    return moment.astimezone(zone).strftime('%Y-%m-%d')


def _text(value):
    '''A cache value rendered for a report cell, leaving absent values empty.'''
    if value is None:
        return ''
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return value


def _cache_records(source_path):
    '''The key to decoded JSON map held by a normalised GraphQL cache database.

    post_booking_reservation_cache and account_data_cache share one records table whose
    key names a field path and whose record holds that path's JSON.
    '''
    db = open_sqlite_db_readonly(source_path)
    if not db:
        return {}
    records = {}
    try:
        rows = db.cursor().execute('SELECT `key`, `record` FROM `records`').fetchall()
    except sqlite3.Error as ex:
        logfunc(f'Could not query {os.path.basename(source_path)}: {ex}')
        db.close()
        return {}
    db.close()
    for key, raw in rows:
        try:
            records[key] = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            logfunc(f'Could not decode a cache record in {os.path.basename(source_path)}')
    return records


def _resolve(records, value):
    '''The record a cache value points at, or the value itself when it points at nothing.'''
    if isinstance(value, str):
        match = _REFERENCE.match(value)
        if match:
            return records.get(match.group(1))
    return value


def _field(records, record, name, default=None):
    '''Field name of record with any cache reference followed.'''
    if not isinstance(record, dict):
        return default
    if name not in record:
        return default
    resolved = _resolve(records, record.get(name))
    return default if resolved is None else resolved


def _key_input(key):
    '''The JSON input object a postBookingReservationQuery cache key carries, or {}.

    The key spells the whole query, so the booking number and PIN code the reservation was
    fetched with are inside it rather than in any record field.
    '''
    start = key.find('(')
    end = key.find(')', start)
    if start < 0 or end < 0:
        return {}
    try:
        arguments = json.loads(key[start + 1:end])
    except (json.JSONDecodeError, TypeError):
        return {}
    if not isinstance(arguments, dict):
        return {}
    query_input = arguments.get('input')
    return query_input if isinstance(query_input, dict) else {}


def _root_keys(records, prefix):
    '''The cache keys naming a whole record of the given query, not one of its fields.'''
    roots = []
    for key in records:
        if not key.startswith(prefix):
            continue
        end = key.find(')')
        if end < 0 or key[end + 1:]:
            continue
        roots.append(key)
    return sorted(roots)


def _prefs(source_path):
    '''The name to value map an Android preferences file holds, or {} when it will not parse.

    Scalar preferences carry their value in a value attribute and strings carry it as
    element text, so both spellings are read.
    '''
    try:
        root = ET.parse(source_path).getroot()
    except (ET.ParseError, OSError) as ex:
        logfunc(f'Could not parse {os.path.basename(source_path)}: {ex}')
        return {}
    values = {}
    for element in root:
        name = element.get('name')
        if not name:
            continue
        if element.get('value') is not None:
            values[name] = element.get('value')
        elif element.tag == 'set':
            values[name] = ', '.join((child.text or '') for child in element)
        else:
            values[name] = element.text or ''
    return values


def _okhttp_entries(context, directory=None):
    '''(metadata path, request URL, headers, decoded body) for each cached response.

    An OkHttp disk cache entry is a pair of files sharing a name: the .0 file holds the
    request line, the request headers, the status line and the response headers, and the
    .1 file holds the body. OkHttp writes its own OkHttp-Sent-Millis and
    OkHttp-Received-Millis headers into the entry, which is where the times come from.
    '''
    entries = []
    for meta_path in _files(context, suffix='.0'):
        if directory is not None and os.path.basename(os.path.dirname(meta_path)) != directory:
            continue
        try:
            with open(meta_path, 'r', encoding='utf-8', errors='replace') as handle:
                lines = handle.read().split('\n')
        except OSError as ex:
            logfunc(f'Could not read {os.path.basename(meta_path)}: {ex}')
            continue
        if len(lines) < 3:
            continue
        url = lines[0]
        headers = {}
        status = ''
        try:
            index = 3 + int(lines[2])
            status = lines[index]
            for header in lines[index + 2:index + 2 + int(lines[index + 1])]:
                if ':' in header:
                    name, _, value = header.partition(':')
                    headers[name.strip().lower()] = value.strip()
        except (ValueError, IndexError):
            logfunc(f'Could not read the headers of {os.path.basename(meta_path)}')
        body_path = meta_path[:-2] + '.1'
        body = None
        try:
            with open(body_path, 'rb') as handle:
                raw = handle.read()
            if raw[:2] == b'\x1f\x8b':
                raw = gzip.decompress(raw)
            body = json.loads(raw)
        except (OSError, ValueError, EOFError):
            body = None
        entries.append((meta_path, url, status, headers, body))
    return entries


def _query(url, name):
    '''One named parameter of a request URL, or '' when the URL does not carry it.'''
    try:
        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    except ValueError:
        return ''
    return parsed.get(name, [''])[0]


def _endpoint(url):
    '''The endpoint a cached request URL names.'''
    return url.split('?')[0].rsplit('/', 1)[-1]


def _reservation_from_post_booking(records, key):
    '''The reservation fields the postBookingReservationQuery shape carries.'''
    record = records.get(key) or {}
    query_input = _key_input(key)
    identity = _field(records, record, 'identity') or {}
    booking_number = query_input.get('bookingNumber') or identity.get('reservationId') or ''
    pin_code = query_input.get('pinCode') or identity.get('pinCode') or ''
    prop = _field(records, record, 'property') or {}
    checkin = _field(records, record, 'reservationCheckinDate') or {}
    checkout = _field(records, record, 'reservationCheckoutDate') or {}
    hotel_checkin = _field(records, prop, 'hotelCheckin') or {}
    hotel_checkout = _field(records, prop, 'hotelCheckout') or {}
    page_property = _field(records, record, 'hotelPageProperty') or {}
    location = _field(records, page_property, 'location') or {}
    payment = _field(records, record, 'payment') or {}
    zone = prop.get('hotelTimezone') or ''
    check_in = _seconds(checkin.get('rawDate'))
    check_out = _seconds(checkout.get('rawDate'))
    return {
        'booking_number': str(booking_number),
        'pin_code': str(pin_code),
        'check_in': check_in,
        'check_out': check_out,
        'check_in_local': _local_date(check_in, zone),
        'check_out_local': _local_date(check_out, zone),
        'reservation_status': _text(record.get('reservationStatus')),
        'confirmed_status': _text(record.get('confirmedStatus')),
        'cancelled_status': _text(record.get('cancelledStatus')),
        'is_no_show': _text(record.get('isNoShow')),
        'travel_purpose': _text(record.get('travelPurpose')),
        'property_name': _text((_field(records, prop, 'hotelName') or {}).get('translation')),
        'property_address': _text((_field(records, prop, 'hotelAddress') or {}).get('rawValue')),
        'property_city': _text((_field(records, prop, 'hotelCity') or {}).get('rawValue')),
        'property_zip': _text(prop.get('hotelZip')),
        'property_country': _text((_field(records, prop, 'country') or {}).get('translation')),
        'property_country_code': _text(prop.get('hotelCountryCode')),
        'property_timezone': _text(zone),
        'property_telephone': _text(prop.get('telephone')),
        'property_email': _text(prop.get('hotelEmail')),
        'property_url': _text(prop.get('url')),
        'property_id': _text(prop.get('hotelId')),
        'accommodation_type_id': _text(prop.get('accommodationTypeId')),
        'formatted_address': _text(location.get('formattedAddress')),
        'property_check_in_time': _time_range(hotel_checkin),
        'property_check_out_time': _time_range(hotel_checkout),
        'paid_through_booking': _text(payment.get('isPayByBooking')),
        'shape': 'postBookingReservationQuery',
    }


def _reservation_from_accommodation(records, key):
    '''The reservation fields the accommodationDetailsQueries shape carries.'''
    record = _field(records, records.get(key) or {}, 'reservation') or {}
    identifiers = _field(records, record, 'identifiers') or {}
    prop = _field(records, record, 'property') or {}
    start = _iso(record.get('startDateTime'))
    end = _iso(record.get('endDateTime'))
    return {
        'booking_number': str(identifiers.get('hotelReservationId') or ''),
        'pin_code': str(record.get('pinCode') or ''),
        'check_in': start,
        'check_out': end,
        'check_in_local': _offset_date(record.get('startDateTime')),
        'check_out_local': _offset_date(record.get('endDateTime')),
        'reservation_status': _text(record.get('reservationStatus')),
        'property_name': _text(prop.get('name')),
        'shape': 'accommodationDetailsQueries',
    }


def _offset_date(value):
    '''The calendar date an ISO 8601 string names in its own offset, or ''.'''
    if not value or not isinstance(value, str):
        return ''
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')).strftime('%Y-%m-%d')
    except ValueError:
        return ''


def _time_range(record):
    '''A from and until pair rendered as a range, or '' when neither is present.'''
    if not isinstance(record, dict):
        return ''
    start = record.get('from') or ''
    until = record.get('until') or ''
    if not start and not until:
        return ''
    return f'{start} - {until}'.strip(' -')


@artifact_processor
def booking_reservations(context):
    data_list = []
    sources = []

    for source_path in _files(context, names={_RESERVATION_DB}):
        relative_path = context.get_relative_path(source_path)
        records = _cache_records(source_path)
        merged = {}
        order = []
        for key in _root_keys(records, _POST_BOOKING_ROOT):
            reservation = _reservation_from_post_booking(records, key)
            identity = reservation['booking_number'] or key
            if identity not in merged:
                merged[identity] = {'shapes': []}
                order.append(identity)
            merged[identity].update(
                {name: value for name, value in reservation.items()
                 if name != 'shape' and value not in ('', None)})
            merged[identity]['shapes'].append(reservation['shape'])
        for key in _root_keys(records, _ACCOMMODATION_ROOT):
            reservation = _reservation_from_accommodation(records, key)
            identity = reservation['booking_number'] or key
            if identity not in merged:
                merged[identity] = {'shapes': []}
                order.append(identity)
            for name, value in reservation.items():
                if name == 'shape' or value in ('', None):
                    continue
                merged[identity].setdefault(name, value)
            merged[identity]['shapes'].append(reservation['shape'])

        for identity in order:
            reservation = merged[identity]
            data_list.append((
                reservation.get('check_in', ''),
                reservation.get('check_out', ''),
                reservation.get('check_in_local', ''),
                reservation.get('check_out_local', ''),
                reservation.get('booking_number', ''),
                reservation.get('pin_code', ''),
                reservation.get('reservation_status', ''),
                reservation.get('confirmed_status', ''),
                reservation.get('cancelled_status', ''),
                reservation.get('is_no_show', ''),
                reservation.get('travel_purpose', ''),
                reservation.get('property_name', ''),
                reservation.get('property_address', ''),
                reservation.get('property_city', ''),
                reservation.get('property_zip', ''),
                reservation.get('property_country', ''),
                reservation.get('property_country_code', ''),
                reservation.get('property_timezone', ''),
                reservation.get('property_telephone', ''),
                reservation.get('property_email', ''),
                reservation.get('property_url', ''),
                reservation.get('property_id', ''),
                reservation.get('accommodation_type_id', ''),
                reservation.get('formatted_address', ''),
                reservation.get('property_check_in_time', ''),
                reservation.get('property_check_out_time', ''),
                reservation.get('paid_through_booking', ''),
                ', '.join(dict.fromkeys(reservation.get('shapes', []))),
                relative_path,
            ))
            sources.append(source_path)

    data_headers = (
        ('Check In', 'datetime'),
        ('Check Out', 'datetime'),
        'Check In Date At Property',
        'Check Out Date At Property',
        'Booking Number',
        'PIN Code',
        'Reservation Status (as stored)',
        'Confirmed Status (as stored)',
        'Cancelled Status (as stored)',
        'Is No Show (as stored)',
        'Travel Purpose (as stored)',
        'Property Name',
        'Property Address',
        'Property City',
        'Property ZIP',
        'Property Country',
        'Property Country Code',
        'Property Timezone',
        'Property Telephone',
        'Property Email',
        'Property URL',
        'Property ID',
        'Accommodation Type ID (as stored)',
        'Formatted Address',
        'Property Check In Time',
        'Property Check Out Time',
        'Paid Through Booking (as stored)',
        'Query Shapes',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def booking_reservation_rooms(context):
    data_list = []
    sources = []
    room_key = re.compile(r'^(?P<root>.*\))\.roomReservations\.(?P<index>\d+)$')

    for source_path in _files(context, names={_RESERVATION_DB}):
        relative_path = context.get_relative_path(source_path)
        records = _cache_records(source_path)
        seen = set()
        for key in sorted(records):
            match = room_key.match(key)
            if not match:
                continue
            room_reservation = records.get(key) or {}
            if not isinstance(room_reservation, dict):
                continue
            booking_number = _key_input(match.group('root')).get('bookingNumber', '')
            room_reservation_id = room_reservation.get('roomReservationId')
            identity = (str(booking_number), str(room_reservation_id))
            if room_reservation_id is not None:
                if identity in seen:
                    continue
                seen.add(identity)
            room = _field(records, room_reservation, 'room') or {}
            occupancy = _field(records, room, 'roomOccupancy') or {}
            payment_term = _field(records, room_reservation, 'paymentTerm') or {}
            cancellation = _field(records, payment_term, 'cancellation') or {}
            cancellation_info = _field(records, cancellation, 'info') or {}
            data_list.append((
                str(booking_number),
                match.group('index'),
                _text(room_reservation.get('roomReservationId')),
                _text(room.get('roomId')),
                _text(room.get('roomName')),
                _text(room.get('roomTypeId')),
                _text(room_reservation.get('guestNumber')),
                _text(occupancy.get('maxPersons')),
                _text(occupancy.get('maxChildren')),
                _text(room_reservation.get('smokingPreference')),
                _text(room_reservation.get('isCancelled')),
                _text(cancellation.get('type')),
                _text(cancellation.get('typeTranslation')),
                _text(cancellation.get('bucket')),
                _text(cancellation.get('description')),
                _text(cancellation_info.get('refundable')),
                relative_path,
            ))
            sources.append(source_path)

    data_headers = (
        'Booking Number',
        'Room Index',
        'Room Reservation ID',
        'Room ID',
        'Room Name',
        'Room Type ID (as stored)',
        'Guest Number',
        'Max Persons',
        'Max Children',
        'Smoking Preference (as stored)',
        'Is Cancelled (as stored)',
        'Cancellation Type (as stored)',
        'Cancellation Type Translation',
        'Cancellation Bucket (as stored)',
        'Cancellation Description',
        'Refundable (as stored)',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def booking_account_profile(context):
    data_list = []
    sources = []

    for source_path in _files(context, names={_ACCOUNT_DB}):
        relative_path = context.get_relative_path(source_path)
        records = _cache_records(source_path)
        profile = records.get('personalProfile')
        if profile is None:
            continue
        personal = _field(records, profile, 'personalData') or {}
        email = _field(records, profile, 'contactEmail') or {}
        phone = _field(records, profile, 'contactPhone') or {}
        address = _field(records, profile, 'address') or {}
        avatar = _field(records, profile, 'avatar') or {}
        genius = _field(records, records.get('geniusGuestData') or {}, 'userInfo') or {}
        wallet = records.get('walletSummary') or {}
        attributes = _field(records, wallet, 'attributes') or {}
        balance = _field(records, wallet, 'balance') or {}
        wallet_credits = _field(records, balance, 'credits') or {}
        credits_total = _field(records, wallet_credits, 'total') or {}
        vouchers = _field(records, balance, 'vouchers') or {}
        travel_documents = profile.get('travelDocuments')
        co_travellers = profile.get('coTravellers')
        data_list.append((
            _text(personal.get('firstName')),
            _text(personal.get('lastName')),
            _text(personal.get('displayName')),
            _text(personal.get('gender')),
            _text(personal.get('dateOfBirth')),
            _text(personal.get('citizenshipCountry')),
            _text(email.get('address')),
            _text(email.get('isVerified')),
            _text(phone.get('number') if isinstance(phone, dict) else phone),
            _text(address.get('address')),
            _text(address.get('city')),
            _text(address.get('region')),
            _text(address.get('postcode')),
            _text(address.get('country')),
            _text(avatar.get('type')),
            _text(genius.get('level')),
            _text(attributes.get('hasWallet')),
            _text(credits_total.get('prettified')),
            _text(vouchers.get('count') if isinstance(vouchers, dict) else ''),
            len(travel_documents) if isinstance(travel_documents, list) else '',
            len(co_travellers) if isinstance(co_travellers, list) else '',
            relative_path,
        ))
        sources.append(source_path)

    data_headers = (
        'First Name',
        'Last Name',
        'Display Name',
        'Gender (as stored)',
        'Date Of Birth (as stored)',
        'Citizenship Country',
        'Email Address',
        'Email Is Verified (as stored)',
        'Contact Phone',
        'Address',
        'City',
        'Region',
        'Postcode',
        'Country',
        'Avatar Type (as stored)',
        'Genius Level (as stored)',
        'Has Wallet (as stored)',
        'Wallet Credits',
        'Wallet Voucher Count',
        'Travel Document Count',
        'Co Traveller Count',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def booking_profile_preferences(context):
    data_list = []
    sources = []

    for source_path in _files(context, names={'mybooking.xml', 'remote_profile.xml'}):
        values = _prefs(source_path)
        if not values:
            continue
        relative_path = context.get_relative_path(source_path)
        google_state = {}
        try:
            parsed = json.loads(values.get('pref3googlestate') or '{}')
            if isinstance(parsed, dict):
                google_state = parsed
        except (json.JSONDecodeError, TypeError):
            google_state = {}
        data_list.append((
            values.get('pref3uid', ''),
            values.get('pref3firstname', ''),
            values.get('pref3lastname', ''),
            values.get('pref3email', ''),
            values.get('pref3phone', ''),
            values.get('pref3_title', ''),
            values.get('pref3gender', ''),
            values.get('pref3address', ''),
            values.get('pref3city', ''),
            values.get('pref3zipcode', ''),
            values.get('pref3country', ''),
            values.get('pref3_private_country', ''),
            values.get('pref3company_name', ''),
            values.get('pref3vat_number', ''),
            values.get('pref3bs_street', ''),
            values.get('pref3bs_city', ''),
            values.get('pref3bs_zip', ''),
            values.get('pref3bs_country', ''),
            values.get('pref3bs_phone', ''),
            values.get('pref3travel_purpose', ''),
            values.get('pref3smoking', ''),
            values.get('genius_level', ''),
            values.get('pref3isgenius', ''),
            values.get('is_genius_vip', ''),
            values.get('has_wallet', ''),
            values.get('has_rewards', ''),
            values.get('has_booking_pay', ''),
            values.get('pref3subscribed', ''),
            values.get('mybooking_login_type', ''),
            _text(google_state.get('id')),
            _text(google_state.get('hasBookingPassword')),
            values.get('email details', ''),
            values.get('cotravellers', ''),
            values.get('user_identities', ''),
            relative_path,
        ))
        sources.append(source_path)

    data_headers = (
        'User ID',
        'First Name',
        'Last Name',
        'Email',
        'Phone',
        'Title (as stored)',
        'Gender (as stored)',
        'Address',
        'City',
        'Zip Code',
        'Country',
        'Private Country',
        'Company Name',
        'VAT Number',
        'Business Street',
        'Business City',
        'Business Zip',
        'Business Country',
        'Business Phone',
        'Travel Purpose (as stored)',
        'Smoking Preference (as stored)',
        'Genius Level (as stored)',
        'Is Genius (as stored)',
        'Is Genius VIP (as stored)',
        'Has Wallet (as stored)',
        'Has Rewards (as stored)',
        'Has Booking Pay (as stored)',
        'Subscribed (as stored)',
        'Login Type (as stored)',
        'Google State ID (as stored)',
        'Google State Has Booking Password (as stored)',
        'Email Details (as stored)',
        'Co Travellers (as stored)',
        'User Identities (as stored)',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def booking_cached_profile(context):
    data_list = []
    sources = []

    for meta_path, url, _status, headers, body in _okhttp_entries(context, 'okhttp'):
        if _endpoint(url) != 'mobile.getProfile' or not isinstance(body, dict):
            continue
        account = body.get('account_details')
        account = account if isinstance(account, dict) else {}
        avatar = body.get('avatar_details')
        avatar = avatar if isinstance(avatar, dict) else {}
        cards = body.get('cc_details')
        data_list.append((
            _ms(headers.get('okhttp-sent-millis')),
            _text(body.get('uid')),
            _text(body.get('first_name')),
            _text(body.get('last_name')),
            _text(body.get('email_address')),
            _text(body.get('phone')),
            _text(body.get('title')),
            _text(body.get('gender')),
            _text(body.get('street')),
            _text(body.get('city')),
            _text(body.get('zipcode')),
            _text(body.get('country')),
            _text(body.get('cc1_address')),
            _text(body.get('company_name')),
            _text(body.get('vat_number')),
            _text(body.get('is_genius')),
            _text(body.get('detailed_genius_status')),
            _text(body.get('has_wallet')),
            _text(body.get('smoke_preference')),
            _text(account.get('has_email')),
            _text(account.get('has_confirmed_phone')),
            _text(avatar.get('available')),
            len(cards) if isinstance(cards, list) else '',
            _text(body.get('direct_partner_chat_available')),
            _query(url, 'device_id'),
            _query(url, 'user_version'),
            context.get_relative_path(meta_path),
        ))
        sources.append(meta_path)

    data_headers = (
        ('Request Time', 'datetime'),
        'User ID',
        'First Name',
        'Last Name',
        'Email Address',
        'Phone',
        'Title (as stored)',
        'Gender (as stored)',
        'Street',
        'City',
        'Zip Code',
        'Country',
        'Address Country Code',
        'Company Name',
        'VAT Number',
        'Is Genius (as stored)',
        'Detailed Genius Status (as stored)',
        'Has Wallet (as stored)',
        'Smoking Preference (as stored)',
        'Has Email (as stored)',
        'Has Confirmed Phone (as stored)',
        'Avatar Available (as stored)',
        'Stored Card Count',
        'Direct Partner Chat Available (as stored)',
        'Device ID',
        'App Version',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def booking_search_query(context):
    data_list = []
    sources = []

    for source_path in _files(context, names={'com.booking_preferences.xml'}):
        values = _prefs(source_path)
        relative_path = context.get_relative_path(source_path)
        for name in ('specific_query', 'general_query'):
            raw = values.get(name)
            if not raw:
                continue
            try:
                query = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                logfunc(f'Could not decode {name} in {os.path.basename(source_path)}')
                continue
            if not isinstance(query, dict):
                continue
            location = query.get('location')
            location = location if isinstance(location, dict) else {}
            sort = query.get('sort')
            sort = sort if isinstance(sort, dict) else {}
            children = query.get('children_ages')
            data_list.append((
                _text(query.get('arrival_date')),
                _text(query.get('departure_date')),
                name,
                _text(location.get('name')),
                _text(location.get('city')),
                _text(location.get('type')),
                _text(location.get('id')),
                _text(location.get('country_code')),
                _text(location.get('location_source')),
                _text(query.get('adult_count')),
                len(children) if isinstance(children, list) else '',
                _text(children),
                _text(query.get('room_count')),
                _text(sort.get('id')),
                _text(query.get('travel_purpose')),
                relative_path,
            ))
            sources.append(source_path)

    data_headers = (
        'Arrival Date (as stored)',
        'Departure Date (as stored)',
        'Query Key',
        'Location Name',
        'Location City',
        'Location Type (as stored)',
        'Location ID',
        'Location Country Code',
        'Location Source (as stored)',
        'Adult Count',
        'Children Count',
        'Children Ages (as stored)',
        'Room Count',
        'Sort (as stored)',
        'Travel Purpose (as stored)',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


def _destination_rows(entry, endpoint):
    '''The destination records a cached response body holds, as a list.'''
    _meta_path, url, _status, _headers, body = entry
    if _endpoint(url) != endpoint:
        return []
    if isinstance(body, list):
        return [item for item in body if isinstance(item, dict)]
    if isinstance(body, dict):
        return [body]
    return []


@artifact_processor
def booking_destination_searches(context):
    data_list = []
    sources = []

    for entry in _okhttp_entries(context, 'okhttp'):
        meta_path, url, _status, headers, _body = entry
        rows = _destination_rows(entry, 'mobile.autocomplete')
        if not rows:
            continue
        relative_path = context.get_relative_path(meta_path)
        requested = _query(url, 'text')
        for position, destination in enumerate(rows):
            data_list.append((
                _ms(headers.get('okhttp-sent-millis')),
                requested,
                position,
                _text(destination.get('name')),
                _text(destination.get('label')),
                _text(destination.get('city_name')),
                _text(destination.get('region')),
                _text(destination.get('country')),
                _text(destination.get('cc1')),
                _text(destination.get('dest_type')),
                _text(destination.get('type')),
                _text(destination.get('latitude')),
                _text(destination.get('longitude')),
                _text(destination.get('timezone')),
                _text(destination.get('nr_hotels')),
                _query(url, 'device_id'),
                relative_path,
            ))
            sources.append(meta_path)

    data_headers = (
        ('Request Time', 'datetime'),
        'Requested Text',
        'Result Position',
        'Name',
        'Label',
        'City Name',
        'Region',
        'Country',
        'Country Code',
        'Destination Type (as stored)',
        'Type (as stored)',
        'Latitude',
        'Longitude',
        'Timezone',
        'Number Of Hotels',
        'Device ID',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def booking_destination_info(context):
    data_list = []
    sources = []

    for entry in _okhttp_entries(context, 'okhttp'):
        meta_path, url, _status, headers, _body = entry
        rows = _destination_rows(entry, 'mobile.getDestinationInfo')
        if not rows:
            continue
        relative_path = context.get_relative_path(meta_path)
        requested = _query(url, 'type_and_id')
        for destination in rows:
            data_list.append((
                _ms(headers.get('okhttp-sent-millis')),
                requested,
                _text(destination.get('name')),
                _text(destination.get('label')),
                _text(destination.get('city_name')),
                _text(destination.get('region')),
                _text(destination.get('country')),
                _text(destination.get('cc1')),
                _text(destination.get('dest_type')),
                _text(destination.get('dest_id')),
                _text(destination.get('latitude')),
                _text(destination.get('longitude')),
                _text(destination.get('nr_hotels')),
                _query(url, 'device_id'),
                relative_path,
            ))
            sources.append(meta_path)

    data_headers = (
        ('Request Time', 'datetime'),
        'Requested Destination',
        'Name',
        'Label',
        'City Name',
        'Region',
        'Country',
        'Country Code',
        'Destination Type (as stored)',
        'Destination ID',
        'Latitude',
        'Longitude',
        'Number Of Hotels',
        'Device ID',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def booking_deep_links(context):
    data_list = []
    sources = []

    for meta_path, url, _status, headers, body in _okhttp_entries(context, 'okhttp'):
        if _endpoint(url) != 'mobile.decodeUniversalLink':
            continue
        body = body if isinstance(body, dict) else {}
        additional = body.get('additional_parameters')
        additional = additional if isinstance(additional, dict) else {}
        data_list.append((
            _ms(headers.get('okhttp-sent-millis')),
            'Resolved link',
            _query(url, 'url'),
            _text(body.get('booking_url')),
            _text(body.get('dest_type')),
            _text(body.get('dest_id')),
            _text(body.get('aid')),
            _text(body.get('label')),
            _text(additional.get('landing_page_subheader_copy')),
            context.get_relative_path(meta_path),
        ))
        sources.append(meta_path)

    for source_path in _files(context, names={'original_link_storage.xml'}):
        values = _prefs(source_path)
        relative_path = context.get_relative_path(source_path)
        action = values.get('link_action', '')
        for name, value in sorted(values.items()):
            if not name.startswith('original_link-') or not value:
                continue
            data_list.append((
                '',
                'Stored link',
                value,
                '',
                name[len('original_link-'):] or '(no screen)',
                '',
                '',
                action,
                '',
                relative_path,
            ))
            sources.append(source_path)

    data_headers = (
        ('Request Time', 'datetime'),
        'Record Type',
        'Link',
        'Resolved Booking URL',
        'Destination Type (as stored)',
        'Destination ID',
        'Affiliate ID',
        'Label (as stored)',
        'Landing Page Subheader',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def booking_notifications(context):
    data_list = []
    sources = []

    for source_path in _files(context, names={_NOTIFICATION_DB}):
        db = open_sqlite_db_readonly(source_path)
        if not db:
            continue
        try:
            rows = db.cursor().execute(
                'SELECT `time_epoch`, `server_id`, `action_id`, `title`, `body`, `is_viewed`, '
                '`is_clicked`, `is_deleted`, `sync_is_viewed`, `sync_is_clicked`, `thumb_url`, '
                '`icon`, `args_json` FROM `notification`').fetchall()
        except sqlite3.Error as ex:
            logfunc(f'Could not query {os.path.basename(source_path)}: {ex}')
            db.close()
            continue
        db.close()
        relative_path = context.get_relative_path(source_path)
        for row in rows:
            data_list.append((
                _seconds(row[0]), row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                row[8], row[9], row[10], row[11], row[12], relative_path,
            ))
            sources.append(source_path)

    data_headers = (
        ('Time', 'datetime'),
        'Server ID',
        'Action ID (as stored)',
        'Title',
        'Body',
        'Is Viewed (as stored)',
        'Is Clicked (as stored)',
        'Is Deleted (as stored)',
        'Sync Is Viewed (as stored)',
        'Sync Is Clicked (as stored)',
        'Thumbnail URL',
        'Icon (as stored)',
        'Arguments (as stored)',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def booking_app_state(context):
    data_list = []
    sources = []
    preferences = {}

    for source_path in _files(context, names={'com.booking_preferences.xml', 'startup_data.xml'}):
        directory = os.path.dirname(source_path)
        preferences.setdefault(directory, {})[os.path.basename(source_path)] = source_path

    for directory in sorted(preferences):
        files = preferences[directory]
        main_path = files.get('com.booking_preferences.xml')
        startup_path = files.get('startup_data.xml')
        main = _prefs(main_path) if main_path else {}
        startup = _prefs(startup_path) if startup_path else {}
        reported = main_path or startup_path
        data_list.append((
            _ms(main.get('first_use')),
            _ms(startup.get('deeplinking_aid_exp_time')),
            main.get('used', ''),
            main.get('app_version', ''),
            main.get('locale', ''),
            main.get('currency', ''),
            main.get('GENERATED_DEVICE_ID', ''),
            main.get('preference_new_user', ''),
            main.get('preference_onboarded', ''),
            main.get('pref_key_user_logged_in_at_least_once_v2', ''),
            main.get('pref_key_last_login_source_ordinal_v2', ''),
            main.get('IABTCF_gdprApplies', ''),
            main.get('PRICE_ALERT_SCREEN_LAST_SEEN', ''),
            startup.get('client_ip_address', ''),
            startup.get('client_user_agent', ''),
            startup.get('deeplinking_aid', ''),
            startup.get('deeplinking_aid_type', ''),
            startup.get('deeplinking_label', ''),
            startup.get('partner_id', ''),
            startup.get('channel_id', ''),
            startup.get('source', ''),
            startup.get('medium', ''),
            startup.get('full_referrer', ''),
            startup.get('booking_owned', ''),
            context.get_relative_path(reported) if reported else '',
        ))
        sources.extend(path for path in (main_path, startup_path) if path)

    data_headers = (
        ('First Use', 'datetime'),
        ('Deep Link Attribution Expiry', 'datetime'),
        'Times Used (as stored)',
        'App Version',
        'Locale',
        'Currency (as stored)',
        'Generated Device ID',
        'Is New User (as stored)',
        'Is Onboarded (as stored)',
        'Logged In At Least Once (as stored)',
        'Last Login Source Ordinal (as stored)',
        'GDPR Applies (as stored)',
        'Price Alert Screen Last Seen (as stored)',
        'Client IP Address (as stored)',
        'Client User Agent (as stored)',
        'Deep Link Affiliate ID',
        'Deep Link Affiliate Type (as stored)',
        'Deep Link Label (as stored)',
        'Partner ID',
        'Channel ID (as stored)',
        'Source (as stored)',
        'Medium (as stored)',
        'Full Referrer (as stored)',
        'Booking Owned (as stored)',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))


@artifact_processor
def booking_cached_requests(context):
    data_list = []
    sources = []

    for cache in ('okhttp', 'saba-http-cache'):
        for meta_path, url, status, headers, body in _okhttp_entries(context, cache):
            data_list.append((
                _ms(headers.get('okhttp-sent-millis')),
                _ms(headers.get('okhttp-received-millis')),
                headers.get('date', ''),
                cache,
                _endpoint(url),
                url,
                status,
                headers.get('content-type', ''),
                headers.get('content-length', ''),
                'Yes' if body is not None else 'No',
                _query(url, 'device_id'),
                _query(url, 'user_version'),
                _query(url, 'user_os'),
                _query(url, 'languagecode'),
                _query(url, 'network_type'),
                context.get_relative_path(meta_path),
            ))
            sources.append(meta_path)

    data_headers = (
        ('Request Time', 'datetime'),
        ('Response Time', 'datetime'),
        'Served Date (as stored)',
        'Cache',
        'Endpoint',
        'Request URL',
        'Status (as stored)',
        'Content Type',
        'Content Length',
        'Body Decoded',
        'Device ID',
        'App Version',
        'OS Version (as stored)',
        'Language Code',
        'Network Type (as stored)',
        'Source File',
    )
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))
