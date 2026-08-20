__artifacts_v2__ = {
    "hinge_account": {
        "name": "Hinge - Account Profile",
        "description": "Parses the account holder's own Hinge profile, including the name, "
                       "email address, home town and the stored location with its "
                       "coordinates.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Hinge",
        "notes": "One row per app data directory. The values come from the app's own "
                 "basic_choices table, which holds one row per profile attribute with the "
                 "chosen value marked selected. Birthday is Unix milliseconds. Latitude and "
                 "Longitude are the coordinates the app stored for the account's location "
                 "alongside the place name; the table also records that the location came "
                 "from a geocoding provider, reported here as stored, so the coordinates "
                 "describe the place the account is set to rather than an observed device "
                 "position. The remaining attributes are integer codes and are reported as "
                 "stored: the same table's display column repeats the numeric identifier "
                 "instead of a label, and the extraction carries no app binary, so no "
                 "mapping from those codes to their meanings could be sourced. Field "
                 "mapping was done against a private sample provided by Mattia; no sample "
                 "data is recorded for it.",
        "paths": (
            '*/co.hinge.app/databases/db*',
        ),
        "output_types": ["html", "tsv", "lava", "kml"],
        "artifact_icon": "user"
    },
    "hinge_account_preferences": {
        "name": "Hinge - Account Preferences",
        "description": "Parses the match preferences the Hinge account holder selected, "
                       "including which of them are marked as deal breakers.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Hinge",
        "notes": "One row per selected preference. The preference_choices table holds every "
                 "option the app offers and marks the chosen ones, so only the selected rows "
                 "are reported; on the tested device that was 22 of 89. Values are reported "
                 "as stored, because the table's display column repeats the numeric "
                 "identifier rather than naming the option and the extraction carries no app "
                 "binary to source a mapping from. A value of -1 is the value the app stores "
                 "for an attribute the account holder left open, which is why several rows "
                 "carry it. Deal Breaker is the flag the row carries. Field mapping was done "
                 "against a private sample provided by Mattia; no sample data is recorded "
                 "for it.",
        "paths": (
            '*/co.hinge.app/databases/db*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "sliders"
    },
    "hinge_profiles": {
        "name": "Hinge - Profiles",
        "description": "Parses the profiles of other people that the Hinge Android app "
                       "cached, including age, home town, location and the profile "
                       "attributes each person recorded.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Hinge",
        "notes": "One row per cached profile. These are profiles the app held locally, which "
                 "records that the app received them rather than that the account holder "
                 "looked at any particular one. Row Created and Row Updated are Unix "
                 "milliseconds and record when the app wrote the row: on the tested device "
                 "all 36 rows were written inside one 65 second span, so they date the "
                 "app's own caching rather than the profile. Most attributes are integer "
                 "codes and are reported as stored, because the app's basic_choices table "
                 "repeats the numeric identifier in its display column instead of naming the "
                 "option and the extraction carries no app binary to source a mapping from. "
                 "State is likewise reported as stored. The app's matches, chat_messages and "
                 "match_messages tables exist in this schema and held no rows on the tested "
                 "device, so no match or message content was available to report. Field "
                 "mapping was done against a private sample provided by Mattia; no sample "
                 "data is recorded for it.",
        "paths": (
            '*/co.hinge.app/databases/db*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "users"
    },
    "hinge_media": {
        "name": "Hinge - Profile Media",
        "description": "Parses the photo and video entries the Hinge Android app cached for "
                       "the account holder's own profile and for other people's profiles.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Hinge",
        "notes": "One row per media entry. Owner separates the account holder's own media "
                 "from media belonging to a cached profile, and carries the profile's user "
                 "id in the second case. Row Created is Unix milliseconds and records when "
                 "the app wrote the row. The rows carry the address of the image on the "
                 "app's media host rather than the bytes; the app's image cache is reported "
                 "separately and only one of its entries could be tied back to a stored "
                 "address, so no media column is offered here. Location is the value the "
                 "media row carries, which is a place name rather than coordinates. Field "
                 "mapping was done against a private sample provided by Mattia; no sample "
                 "data is recorded for it.",
        "paths": (
            '*/co.hinge.app/databases/db*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "image"
    },
    "hinge_answers": {
        "name": "Hinge - Prompt Answers",
        "description": "Parses the written prompt answers the Hinge Android app cached for "
                       "the account holder and for other people's profiles.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Hinge",
        "notes": "One row per answer. Owner separates the account holder's own answers from "
                 "answers belonging to a cached profile, and carries the profile's user id "
                 "in the second case. Answer is the text the answer record carries, taken "
                 "from the response field of its stored document; where the record holds a "
                 "different shape the document is reported as stored instead, so no answer "
                 "is dropped for not matching the expected form. Answer Type is the value "
                 "the row carries, which was text, poll or video on the tested device. Row "
                 "Created and Row Modified are Unix milliseconds and record when the app "
                 "wrote the row. The question the answer responds to is identified only by "
                 "its identifier in this table, and is reported as stored. Field mapping was "
                 "done against a private sample provided by Mattia; no sample data is "
                 "recorded for it.",
        "paths": (
            '*/co.hinge.app/databases/db*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "message-square"
    },
    "hinge_activity": {
        "name": "Hinge - Activity",
        "description": "Parses the in app events the Hinge Android app recorded, with the "
                       "event time, the event name and the session it belongs to.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Hinge",
        "notes": "One row per recorded event. Timestamp is an ISO 8601 value stored with a "
                 "trailing Z, reported as the UTC time it states. Event names are the "
                 "app's own labels, as stored. Subject is the profile identifier the event "
                 "names where it carries one, which lets an event be tied to a cached "
                 "profile. Event Data is the record's own document, as stored, because its "
                 "fields vary by event name. These are events the app queued for its own "
                 "reporting, so the set present is what had not yet been cleared rather than "
                 "a complete history of app use. Field mapping was done against a private "
                 "sample provided by Mattia; no sample data is recorded for it.",
        "paths": (
            '*/co.hinge.app/databases/db*',
        ),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "activity"
    },
    "hinge_cached_images": {
        "name": "Hinge - Cached Images",
        "description": "Parses the images held in the Hinge Android app's image cache, with "
                       "the times the app requested and received each one.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Hinge",
        "notes": "One row per cache entry. The cache is a libcore.io.DiskLruCache in which "
                 "each entry is a pair of files, a metadata file holding the response "
                 "headers and a payload file holding the bytes; the bytes are checked in and "
                 "rendered. The metadata file leads with the response status code, then the "
                 "times the request was sent and the response received as Unix "
                 "milliseconds, then a header count, then the headers; the three leading "
                 "values are read by position because each is a bare number on its own "
                 "line. The remaining columns are the response headers as stored. Source "
                 "Address is filled only where the entry name is the SHA-256 of an image "
                 "address the app also stored in its database, which on the tested device "
                 "was 1 of 20 entries; the other 19 were served as WebP and their request "
                 "address is not recorded anywhere in the extraction, so they could not be "
                 "tied to a profile. Hashing every address the database holds, and a sweep "
                 "of size and format variations of those addresses, produced no further "
                 "match. The entry name is reported so the check can be repeated. Field "
                 "mapping was done against a private sample provided by Mattia; no sample "
                 "data is recorded for it.",
        "paths": (
            '*/co.hinge.app/cache/coil3_disk_cache/*',
            '*/co.hinge.app/databases/db*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "image"
    },
}

import hashlib
import json
import os
import re
import sqlite3
from datetime import datetime, timedelta, timezone

from scripts.artifacts.storagePathViews import canonical_path, unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    get_sqlite_db_path,
    logfunc,
    open_sqlite_db_readonly,
)

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_PACKAGE = 'co.hinge.app'
_DATABASE = 'db'

# Leading bytes to (label, mime, extension). Cache payloads carry no extension, so the
# type comes from the bytes rather than from the name.
_IMAGE_MAGIC = (
    (b'\xff\xd8\xff', 'JPEG', 'image/jpeg', 'jpg'),
    (b'\x89PNG\r\n\x1a\n', 'PNG', 'image/png', 'png'),
    (b'GIF8', 'GIF', 'image/gif', 'gif'),
)


def _container(context, path):
    '''A key for the app data directory a matched file belongs to.

    Matched on a path segment equal to the package name rather than on a substring, so a
    directory that merely contains the name cannot be taken for the container. The key is
    canonicalised through storagePathViews, so the /data/data and /data/user/0 spellings
    of one directory collapse to one key while a second Android user stays separate. Every
    index this module builds is keyed on it, because an index keyed on a bare cache entry
    name would merge two app data directories into one.
    '''
    relative = str(context.get_relative_path(path)).replace('\\', '/')
    parts = relative.split('/')
    for position, part in enumerate(parts):
        if part == _PACKAGE:
            return canonical_path('/'.join(parts[:position + 1]))[0]
    return canonical_path(relative)[0]


def _by_container(context):
    '''{container key: [path]} for the files this artifact matched.

    Every caller iterates the containers rather than taking the first database that
    opens, so a second app data directory contributes its own rows instead of being
    dropped.
    '''
    grouped = {}
    for file_found in unique_files(context):
        grouped.setdefault(_container(context, file_found), []).append(str(file_found))
    return grouped


def _ms(value):
    '''A Unix millisecond value as a UTC datetime, or '' when absent or zero.'''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if not value:
        return ''
    return _EPOCH + timedelta(milliseconds=value)


def _iso(value):
    '''An ISO 8601 value stored with a trailing Z as a UTC datetime, or ''.

    The fraction is padded to six digits before parsing, because releases before 3.11
    accept only three or six and the app writes a longer one.
    '''
    if not value or not isinstance(value, str):
        return ''
    text = value.strip().replace('Z', '+00:00')
    match = re.match(r'^(.*\.)(\d+)(.*)$', text)
    if match:
        text = f'{match.group(1)}{match.group(2)[:6]:0<6}{match.group(3)}'
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return ''


def _databases(paths):
    '''[(source path, open database)] for each Hinge database in one container.'''
    opened = []
    for path in paths:
        if os.path.basename(path) != _DATABASE:
            continue
        try:
            database = open_sqlite_db_readonly(get_sqlite_db_path(path))
        except sqlite3.Error as ex:
            logfunc(f'Hinge: could not open {_DATABASE}: {ex}')
            continue
        opened.append((path, database))
    return opened


def _rows(database, statement):
    '''The rows a statement returns, or nothing when the table is absent.

    A table absent from an older or newer release is logged and yields nothing, so a
    schema change costs the artifact that table rather than every row it would have
    returned.
    '''
    try:
        cursor = database.cursor()
        cursor.execute(statement)
        return cursor.fetchall()
    except sqlite3.Error as ex:
        logfunc(f'Hinge: could not read from the database: {ex}')
        return []


def _document(text):
    '''The JSON document held in a column, or None when it does not parse.'''
    try:
        return json.loads(text)
    except (TypeError, ValueError):
        return None


def _chosen(values, attribute, api_id=None):
    '''One selected basic_choices value, as text, or ''.

    A module level helper rather than a closure over the loop variables, so the container
    a value is read for is the one passed in rather than whichever the loop last bound.
    '''
    key = (attribute, api_id) if api_id is not None else attribute
    value = values.get(key, '')
    return '' if value is None else value


def _answer_text(stored):
    '''The written answer a record carries, or the record as stored.

    The app wraps the response in a per type envelope. Where the envelope is not one this
    reader knows, the document is returned unchanged rather than dropped, so an answer is
    never lost for having an unexpected shape.
    '''
    document = _document(stored)
    if not isinstance(document, dict):
        return stored or ''
    for value in document.values():
        if isinstance(value, dict) and isinstance(value.get('response'), str):
            return value['response']
    return stored or ''


@artifact_processor
def hinge_account(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        for source_path, database in _databases(paths):
            relative = context.get_relative_path(source_path)
            chosen = {}
            for attribute, api_id, display, selected in _rows(
                    database, 'SELECT attribute, apiId, display, selected FROM basic_choices'):
                if selected:
                    chosen[(str(attribute), str(api_id))] = display
                    chosen.setdefault(str(attribute), display)
            if not chosen:
                database.close()
                continue

            source_files.append(relative)
            data_list.append((
                _ms(_chosen(chosen, 'age', 'birthday')),
                _chosen(chosen, 'name', 'firstName'),
                _chosen(chosen, 'name', 'lastName'),
                _chosen(chosen, 'email', 'name'),
                _chosen(chosen, 'location', 'name'),
                _chosen(chosen, 'location', 'latitude'),
                _chosen(chosen, 'location', 'longitude'),
                _chosen(chosen, 'location', 'adminArea2'),
                _chosen(chosen, 'location', 'adminArea1Long'),
                _chosen(chosen, 'location', 'countryShort'),
                _chosen(chosen, 'location', 'metroAreaV2'),
                _chosen(chosen, 'location', 'source'),
                _chosen(chosen, 'hometown', 'name'),
                _chosen(chosen, 'height', 'height'),
                _chosen(chosen, 'jobTitle', 'name'),
                _chosen(chosen, 'employment', 'name'),
                _chosen(chosen, 'education'),
                str(_chosen(chosen, 'genders')),
                str(_chosen(chosen, 'genderIdentities')),
                str(_chosen(chosen, 'sexualOrientations')),
                str(_chosen(chosen, 'ethnicities')),
                str(_chosen(chosen, 'religion')),
                str(_chosen(chosen, 'politics')),
                str(_chosen(chosen, 'datingIntention')),
                str(_chosen(chosen, 'relationshipType')),
                str(_chosen(chosen, 'children')),
                str(_chosen(chosen, 'familyPlans')),
                str(_chosen(chosen, 'smoking')),
                str(_chosen(chosen, 'drinking')),
                str(_chosen(chosen, 'drugs')),
                str(_chosen(chosen, 'marijuana')),
                str(_chosen(chosen, 'educationAttained')),
                relative,
            ))
            database.close()

    data_headers = (
        ('Birthday', 'datetime'),
        'First Name',
        'Last Name',
        'Email',
        'Location',
        'Latitude',
        'Longitude',
        'Location Admin Area 2',
        'Location Admin Area 1',
        'Location Country',
        'Location Metro Area',
        'Location Source (as stored)',
        'Home Town',
        'Height (as stored)',
        'Job Title',
        'Employment',
        'Education',
        'Gender (as stored)',
        'Gender Identity (as stored)',
        'Sexual Orientation (as stored)',
        'Ethnicity (as stored)',
        'Religion (as stored)',
        'Politics (as stored)',
        'Dating Intention (as stored)',
        'Relationship Type (as stored)',
        'Children (as stored)',
        'Family Plans (as stored)',
        'Smoking (as stored)',
        'Drinking (as stored)',
        'Drugs (as stored)',
        'Marijuana (as stored)',
        'Education Attained (as stored)',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def hinge_account_preferences(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        for source_path, database in _databases(paths):
            relative = context.get_relative_path(source_path)
            for attribute, api_id, display, deal_breaker, gendered, sort_order in _rows(
                    database,
                    'SELECT attribute, apiId, display, dealBreaker, '
                    'genderedAttributePreference, sortOrder FROM preference_choices '
                    'WHERE selected = 1'):
                source_files.append(relative)
                data_list.append((
                    str(attribute or ''),
                    str(api_id if api_id is not None else ''),
                    str(display if display is not None else ''),
                    str(deal_breaker if deal_breaker is not None else ''),
                    str(gendered or ''),
                    str(sort_order if sort_order is not None else ''),
                    relative,
                ))
            database.close()

    data_headers = (
        'Preference',
        'Value (as stored)',
        'Display (as stored)',
        'Deal Breaker',
        'Applies To',
        'Sort Order',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def hinge_profiles(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        for source_path, database in _databases(paths):
            relative = context.get_relative_path(source_path)
            media_counts = {}
            for user_id, count in _rows(
                    database, 'SELECT userId, COUNT(*) FROM subject_media GROUP BY userId'):
                media_counts[user_id] = count
            answer_counts = {}
            for user_id, count in _rows(
                    database, 'SELECT userId, COUNT(*) FROM subject_answers GROUP BY userId'):
                answer_counts[user_id] = count

            for row in _rows(database, '''
                    SELECT created, updated, firstName, lastName, age, height, hometown,
                           location, jobTitle, jobTitleText, educationHistory,
                           educationHistoryText, employmentHistory, gender, genderIdentity,
                           genderIdentityId, pronouns, sexualOrientations, ethnicity,
                           ethnicitiesText, religion, religionText, politics, politicsText,
                           datingIntention, datingIntentionText, relationshipType,
                           relationshipTypeText, kids, familyPlans, smoking, drinking, drugs,
                           marijuana, pet, zodiacSign, covidVax, languagesSpoken,
                           languagesSpokenText, educationAttained, selfieVerified,
                           compatibility, lastActiveStatusId, didJustJoin, state, userId
                    FROM profiles'''):
                (created, updated, first_name, last_name, age, height, hometown, location,
                 job_title, job_title_text, education, education_text, employment, gender,
                 gender_identity, gender_identity_id, pronouns, orientations, ethnicity,
                 ethnicity_text, religion, religion_text, politics, politics_text,
                 intention, intention_text, relationship, relationship_text, kids,
                 family_plans, smoking, drinking, drugs, marijuana, pet, zodiac, covid_vax,
                 languages, languages_text, education_attained, selfie_verified,
                 compatibility, last_active, just_joined, state, user_id) = row
                source_files.append(relative)
                data_list.append((
                    _ms(created),
                    _ms(updated),
                    first_name or '',
                    last_name or '',
                    str(age if age is not None else ''),
                    str(height if height is not None else ''),
                    hometown or '',
                    location or '',
                    job_title_text or job_title or '',
                    education_text or education or '',
                    employment or '',
                    str(gender if gender is not None else ''),
                    gender_identity or str(gender_identity_id or ''),
                    str(pronouns if pronouns is not None else ''),
                    str(orientations if orientations is not None else ''),
                    ethnicity_text or str(ethnicity if ethnicity is not None else ''),
                    religion_text or str(religion if religion is not None else ''),
                    politics_text or str(politics if politics is not None else ''),
                    intention_text or str(intention if intention is not None else ''),
                    relationship_text or str(relationship if relationship is not None else ''),
                    str(kids if kids is not None else ''),
                    str(family_plans if family_plans is not None else ''),
                    str(smoking if smoking is not None else ''),
                    str(drinking if drinking is not None else ''),
                    str(drugs if drugs is not None else ''),
                    str(marijuana if marijuana is not None else ''),
                    str(pet if pet is not None else ''),
                    str(zodiac if zodiac is not None else ''),
                    str(covid_vax if covid_vax is not None else ''),
                    languages_text or str(languages if languages is not None else ''),
                    str(education_attained if education_attained is not None else ''),
                    str(selfie_verified if selfie_verified is not None else ''),
                    str(compatibility if compatibility is not None else ''),
                    str(last_active if last_active is not None else ''),
                    str(just_joined if just_joined is not None else ''),
                    str(state if state is not None else ''),
                    media_counts.get(user_id, 0),
                    answer_counts.get(user_id, 0),
                    str(user_id or ''),
                    relative,
                ))
            database.close()

    data_headers = (
        ('Row Created', 'datetime'),
        ('Row Updated', 'datetime'),
        'First Name',
        'Last Name',
        'Age',
        'Height (as stored)',
        'Home Town',
        'Location',
        'Job Title',
        'Education',
        'Employment',
        'Gender (as stored)',
        'Gender Identity (as stored)',
        'Pronouns (as stored)',
        'Sexual Orientation (as stored)',
        'Ethnicity (as stored)',
        'Religion (as stored)',
        'Politics (as stored)',
        'Dating Intention (as stored)',
        'Relationship Type (as stored)',
        'Children (as stored)',
        'Family Plans (as stored)',
        'Smoking (as stored)',
        'Drinking (as stored)',
        'Drugs (as stored)',
        'Marijuana (as stored)',
        'Pet (as stored)',
        'Zodiac Sign (as stored)',
        'Covid Vaccination (as stored)',
        'Languages Spoken (as stored)',
        'Education Attained (as stored)',
        'Selfie Verified (as stored)',
        'Compatibility (as stored)',
        'Last Active Status (as stored)',
        'Just Joined (as stored)',
        'State (as stored)',
        'Media Entries',
        'Answers',
        'User ID',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def hinge_media(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        for source_path, database in _databases(paths):
            relative = context.get_relative_path(source_path)
            names = {}
            for user_id, first_name in _rows(
                    database, 'SELECT userId, firstName FROM profiles'):
                names[user_id] = first_name or ''

            entries = []
            for row in _rows(database, '''
                    SELECT created, userId, position, photoUrl, thumbnailUrl, videoUrl,
                           width, height, source, description, location, mediaPromptText,
                           cdnId, contentId
                    FROM subject_media'''):
                entries.append((row, False))
            for row in _rows(database, '''
                    SELECT created, NULL, position, photoUrl, thumbnailUrl, videoUrl,
                           width, height, source, description, location, mediaPromptText,
                           cdnId, contentId
                    FROM player_media'''):
                entries.append((row, True))

            for row, is_account in entries:
                (created, user_id, position, photo_url, thumbnail_url, video_url, width,
                 height, media_source, description, location, prompt_text, cdn_id,
                 content_id) = row
                if is_account:
                    owner = 'Account Holder'
                else:
                    label = names.get(user_id, '')
                    owner = f'{label} ({user_id})' if label else str(user_id or '')
                source_files.append(relative)
                data_list.append((
                    _ms(created),
                    owner,
                    str(position if position is not None else ''),
                    photo_url or '',
                    thumbnail_url or '',
                    video_url or '',
                    f'{width}x{height}' if width and height else '',
                    str(media_source or ''),
                    description or '',
                    location or '',
                    prompt_text or '',
                    str(cdn_id or ''),
                    str(content_id or ''),
                    relative,
                ))
            database.close()

    data_headers = (
        ('Row Created', 'datetime'),
        'Owner',
        'Position',
        'Photo Address',
        'Thumbnail Address',
        'Video Address',
        'Dimensions',
        'Source (as stored)',
        'Description',
        'Location',
        'Prompt Text',
        'CDN ID',
        'Content ID',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def hinge_answers(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        for source_path, database in _databases(paths):
            relative = context.get_relative_path(source_path)
            names = {}
            for user_id, first_name in _rows(
                    database, 'SELECT userId, firstName FROM profiles'):
                names[user_id] = first_name or ''

            entries = []
            for row in _rows(database, '''SELECT created, modified, userId, type, questionId,
                                                 position, answerData FROM subject_answers'''):
                entries.append((row, False))
            for row in _rows(database, '''SELECT created, modified, NULL, type, questionId,
                                                 position, answerData FROM player_answers'''):
                entries.append((row, True))

            for row, is_account in entries:
                created, modified, user_id, answer_type, question_id, position, stored = row
                if is_account:
                    owner = 'Account Holder'
                else:
                    label = names.get(user_id, '')
                    owner = f'{label} ({user_id})' if label else str(user_id or '')
                source_files.append(relative)
                data_list.append((
                    _ms(created),
                    _ms(modified),
                    owner,
                    _answer_text(stored),
                    str(answer_type or ''),
                    str(position if position is not None else ''),
                    str(question_id or ''),
                    relative,
                ))
            database.close()

    data_headers = (
        ('Row Created', 'datetime'),
        ('Row Modified', 'datetime'),
        'Owner',
        'Answer',
        'Answer Type (as stored)',
        'Position',
        'Question ID',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def hinge_activity(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        for source_path, database in _databases(paths):
            relative = context.get_relative_path(source_path)
            names = {}
            for user_id, first_name in _rows(
                    database, 'SELECT userId, firstName FROM profiles'):
                names[user_id] = first_name or ''

            for row in _rows(database, '''
                    SELECT ts, eventType, subjectId, referrerId, data, sessionId,
                           authenticated, crmAttributionId, id
                    FROM metrics'''):
                (stamp, event_type, subject_id, referrer_id, data, session_id,
                 authenticated, attribution_id, event_id) = row
                subject = ''
                if subject_id:
                    label = names.get(subject_id, '')
                    subject = f'{label} ({subject_id})' if label else str(subject_id)
                source_files.append(relative)
                data_list.append((
                    _iso(stamp),
                    str(event_type or ''),
                    subject,
                    str(referrer_id or ''),
                    data or '',
                    str(session_id or ''),
                    str(authenticated if authenticated is not None else ''),
                    str(attribution_id or ''),
                    str(event_id or ''),
                    relative,
                ))
            database.close()

    data_list.sort(key=lambda row: (str(row[0]), row[8]), reverse=True)

    data_headers = (
        ('Timestamp', 'datetime'),
        'Event',
        'Subject',
        'Referrer ID',
        'Event Data (as stored)',
        'Session ID',
        'Authenticated (as stored)',
        'Attribution ID',
        'Event ID',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def hinge_cached_images(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        # Addresses are collected inside this container only, so one app data directory
        # cannot supply another's image address.
        addresses = {}
        for _, database in _databases(paths):
            for statement in ('SELECT photoUrl FROM subject_media',
                              'SELECT thumbnailUrl FROM subject_media',
                              'SELECT photoUrl FROM player_media',
                              'SELECT videoUrl FROM subject_media'):
                for (address,) in _rows(database, statement):
                    if address:
                        addresses[hashlib.sha256(address.encode()).hexdigest()] = address
            database.close()

        for path in paths:
            if not path.endswith('.0') or 'coil3_disk_cache' not in path.replace('\\', '/'):
                continue
            payload = path[:-2] + '.1'
            if payload not in paths:
                continue
            try:
                with open(path, 'r', encoding='utf-8', errors='replace') as handle:
                    lines = handle.read().split('\n')
            except OSError as ex:
                logfunc(f'Hinge: could not read a cache metadata file: {ex}')
                continue

            # The metadata file leads with the response status code, then the times the
            # request was sent and the response received, then a header count, then the
            # headers themselves. Positions are read rather than guessed at, because the
            # status code and a timestamp are both bare numbers on their own line.
            status = sent = received = ''
            headers = {}
            if len(lines) > 0 and lines[0].strip().isdigit():
                status = lines[0].strip()
            if len(lines) > 1 and lines[1].strip().isdigit():
                sent = lines[1].strip()
            if len(lines) > 2 and lines[2].strip().isdigit():
                received = lines[2].strip()
            for line in lines[3:]:
                line = line.strip()
                if ':' in line:
                    name, _, value = line.partition(':')
                    headers[name.strip().lower()] = value.strip()

            entry = os.path.basename(path)[:-2]
            try:
                with open(payload, 'rb') as handle:
                    magic = handle.read(16)
            except OSError:
                magic = b''
            label = extension = ''
            mime = headers.get('content-type', '')
            for prefix, name, media_type, suffix in _IMAGE_MAGIC:
                if magic.startswith(prefix):
                    label, extension = name, suffix
                    mime = mime or media_type
                    break
            if not label and magic[:4] == b'RIFF' and magic[8:12] == b'WEBP':
                label, extension = 'WebP', 'webp'
                mime = mime or 'image/webp'

            media_ref = check_in_media(payload, entry, force_type=mime or None,
                                       force_extension=extension or None)
            source_files.append(context.get_relative_path(path))
            data_list.append((
                _ms(sent),
                _ms(received),
                media_ref,
                status,
                label or 'unrecognised',
                addresses.get(entry, ''),
                headers.get('content-type', ''),
                headers.get('content-length', ''),
                headers.get('cache-control', ''),
                headers.get('x-cache-status', ''),
                headers.get('date', ''),
                entry,
                context.get_relative_path(payload),
            ))

    data_list.sort(key=lambda row: (str(row[0]), row[10]), reverse=True)

    data_headers = (
        ('Sent', 'datetime'),
        ('Received', 'datetime'),
        ('Image', 'media'),
        'Response Status (as stored)',
        'Detected Format',
        'Source Address',
        'Content Type (as stored)',
        'Content Length (as stored)',
        'Cache Control (as stored)',
        'Cache Status (as stored)',
        'Response Date (as stored)',
        'Cache Entry Name',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))
