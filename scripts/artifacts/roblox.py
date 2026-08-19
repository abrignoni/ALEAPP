__artifacts_v2__ = {
    "roblox_account": {
        "name": "Roblox - Account",
        "description": "Parses the signed in Roblox account recorded by the Roblox Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Roblox",
        "notes": "Read from the LocalStorage appStorage.json key value store, with the user id, username "
                 "and display name cross-checked against shared_prefs prefs.xml, where the app keeps a "
                 "second copy under userid_long, username and displayName. On the one device tested the "
                 "two stores agreed on all three. Age and account fields come from the "
                 "PlayerHydrationBlob value in the same store. Two timestamp units appear inside that "
                 "one blob: originalAccountCreationTimestampMs is Unix milliseconds and lastPerformed in "
                 "the same object is Unix seconds, so each is converted on its own. "
                 "MobileAdvertisingIdCacheTime, WebViewUserAgentCacheTime and "
                 "PushUpsellSysPromptShownTimestamp are Unix seconds. ContactImporterSyncTimestamp is "
                 "stored as a colon followed by Unix milliseconds, so the value is split on the colon "
                 "before conversion. Membership, gender and age bracket are reported as stored. No "
                 "mapping for the membership integer was recoverable, because the tested extraction is "
                 "app data only and carries no APK to source one from. The under 13 flag is reported "
                 "from both stores it appears in so a disagreement stays visible. Field mapping was done "
                 "against a single private sample; no sample data is recorded for it. A blank contact "
                 "importer opted in list is reported rather than dropped, because an empty list beside a "
                 "populated sync timestamp is itself the finding.",
        "paths": ('*/com.roblox.client/files/appData/LocalStorage/appStorage.json',
                  '*/com.roblox.client/shared_prefs/prefs.xml'),
        "output_types": "standard",
        "artifact_icon": "user"
    },
    "roblox_previous_accounts": {
        "name": "Roblox - Previous Accounts",
        "description": "Parses the account picker list kept by the Roblox Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Roblox",
        "notes": "Read from the PreviousAccountsList value of appStorage.json, which the "
                 "app keys by user id. signOutTimestamp is Unix seconds, unlike the "
                 "millisecond account creation value in the same file. An entry records an "
                 "account the client held credentials for and does not by itself establish "
                 "who used it. The display name stored in this list is the one held when the "
                 "entry was written, so it can differ from the current display name: on the "
                 "one device tested the two differed, which is what a display name change "
                 "looks like here. Field mapping was done against a single private sample; "
                 "no sample data is recorded for it.",
        "paths": ('*/com.roblox.client/files/appData/LocalStorage/appStorage.json',),
        "output_types": "standard",
        "artifact_icon": "users"
    },
    "roblox_app_launches": {
        "name": "Roblox - App Launches",
        "description": "Parses the per launch client log files written by the Roblox Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Roblox",
        "notes": "One row per Player log file in files/appData/logs. The client names each file with the "
                 "client version, a UTC timestamp, the log type, and a short identifier, and the "
                 "timestamp is read from that name. The first log line carries its own timestamp and is "
                 "reported beside it so the two can be compared. That one file equals one launch is data "
                 "proven on the one device tested rather than assumed: the rate_me_maybe launch counter "
                 "read 83, and exactly 83 log files were dated at or after that file's absolute first "
                 "launch value, the earliest of them one second after it. Most files hold only start up "
                 "lines. A log file records that the client started, not that a person opened it, since "
                 "a background start also writes one. Field mapping was done against a single private "
                 "sample; no sample data is recorded for it. Log type held one value on every row of the "
                 "sample tested and is kept because a client that wrote another kind of log would change "
                 "it. The file name suffix and the short identifier are not reported as their own "
                 "columns: the first was constant and the second is undocumented, and the log file name "
                 "column carries both.",
        "paths": ('*/com.roblox.client/files/appData/logs/*.log',),
        "output_types": "standard",
        "artifact_icon": "clock"
    },
    "roblox_game_activity": {
        "name": "Roblox - Game Activity",
        "description": "Parses experience joins and game server connections from the Roblox Android client logs.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Roblox",
        "notes": "Read from the client logs in files/appData/logs. A join is assembled from the join "
                 "line, which carries the game job id, the place id and the server address, the "
                 "game_join_loadtime report line, which carries the play session id, the user id, the "
                 "universe id, the place id and a referral page, and the analytics session id line. The "
                 "two lines that both carry a place id agreed on the one join present in the sample "
                 "tested, and the play session id from the report line equalled the analytics session "
                 "id. Roblox's own vocabulary is kept: a place id identifies a place, a universe id "
                 "identifies the experience that contains it, and a game job id identifies the running "
                 "server instance. Line timestamps are ISO 8601 UTC as written by the client; clienttime "
                 "on the report line is Unix seconds and is reported separately so the two can be "
                 "compared. The referral page value is reported as stored. Server addresses are reported "
                 "as logged and are the addresses the client connected to, not the user's own address. "
                 "Field mapping was done against a single private sample; no sample data is recorded for "
                 "it. The sample tested held one join, so pairing a repeated join to the same place with "
                 "its own report line, and reporting a report line that no join line covered, were "
                 "exercised against a constructed log rather than against real data. No linkable media "
                 "was found to render beside a join: the rbx-storage content cache directory held no "
                 "files, its index recorded a single eight byte non media entry, and a magic byte scan "
                 "of the whole extraction found no image or video file at all, so the asset ids seen in "
                 "the logs cannot be resolved to bytes here.",
        "paths": ('*/com.roblox.client/files/appData/logs/*.log',),
        "output_types": "standard",
        "artifact_icon": "player-play"
    },
    "roblox_push_notifications": {
        "name": "Roblox - Push Notifications Received",
        "description": "Parses the received push notification ids recorded by the Roblox Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Roblox",
        "notes": "Read from the notification_id table of the roblox-database-default Room database. "
                 "last_received_timestamp_ms is Unix milliseconds, as the column name states. The table "
                 "is read twice, once with its write ahead log applied and once ignoring it, and rows "
                 "present in only one read are reported with the read they came from in the Source Read "
                 "column. Comparing the two by primary key rather than by row count is what makes that "
                 "work: on the one device tested both reads held exactly 100 rows and four of them "
                 "differed, so a count comparison would have reported the two reads as identical. The "
                 "four rows only in the pre checkpoint read are older receipts that a normal read does "
                 "not return; a row missing from the committed read may have been aged out of a capped "
                 "table, so the observation is reported without a cause. The table records that a "
                 "notification arrived and when, not what it said or who sent it. A notification type is "
                 "available only where the analytic_event table still holds the matching event, which is "
                 "joined on the notification id; that value is reported as stored. Field mapping was "
                 "done against a single private sample; no sample data is recorded for it. No chat, "
                 "message or conversation store was found anywhere in the tested extraction, and no "
                 "friends or contacts store either: every store was enumerated and the words chat, "
                 "conversation, friend and message appeared only inside server delivered configuration "
                 "and experiment values, never as content. The contact importer opted in list in "
                 "appStorage.json was empty. So no messaging artifact is offered here, and this table is "
                 "the nearest record of inbound activity rather than a record of what was said. The "
                 "notification type column is populated only where the matching analytic_event row "
                 "survives, which was one row of 104 on the sample tested.",
        "paths": ('*/com.roblox.client/databases/roblox-database-default*',),
        "output_types": "standard",
        "artifact_icon": "bell"
    },
    "roblox_marketplace_searches": {
        "name": "Roblox - Marketplace Searches",
        "description": "Parses the recent marketplace search terms kept by the Roblox Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Roblox",
        "notes": "Read from the AXMarketplaceRecentSearches value of appStorage.json, which "
                 "holds a user id and a list of terms. The value carries no timestamp, so no "
                 "date is reported and the order of the list is preserved as stored rather "
                 "than being described as most recent first. The store holds terms the client "
                 "recorded as recent searches and is not a download of server suggestions: it "
                 "carries no ranking or score column and no cache version or fetch time "
                 "preference names it, unlike the app settings and experiment values in the "
                 "same file. Field mapping was done against a single private sample; no "
                 "sample data is recorded for it.",
        "paths": ('*/com.roblox.client/files/appData/LocalStorage/appStorage.json',),
        "output_types": "standard",
        "artifact_icon": "search"
    },
    "roblox_user_game_settings": {
        "name": "Roblox - User Game Settings",
        "description": "Parses the in experience settings saved by the Roblox Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Roblox",
        "notes": "One row per property of the UserGameSettings item in "
                 "files/appData/GlobalBasicSettings_13.xml, which the client writes in Roblox's own XML "
                 "model format. The property name, its declared XML type and its value are reported as "
                 "stored; the file records the settings the client saved and the artifact does not "
                 "assert which of them a person changed, since defaults are written to the same file. "
                 "The trailing number in the file name is matched with a wildcard so a later settings "
                 "revision is still picked up. The engine and debug settings in the sibling "
                 "GlobalSettings file are not reported here. Field mapping was done against a single "
                 "private sample; no sample data is recorded for it. Values are stripped of the "
                 "surrounding whitespace the XML carries, so a property the file stores empty is "
                 "reported empty rather than as indentation. The item holds engine and accessibility "
                 "settings next to ones a person changes in the app, so the artifact reports the "
                 "property names as the file spells them rather than sorting them into user changed and "
                 "default.",
        "paths": ('*/com.roblox.client/files/appData/GlobalBasicSettings*.xml',),
        "output_types": "standard",
        "artifact_icon": "settings"
    },
    "roblox_account_policy": {
        "name": "Roblox - Account Policy",
        "description": "Parses the cached account policy response held by the Roblox Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Roblox",
        "notes": "Read from the PolicyServiceHttpResponse value of appStorage.json. This is a "
                 "server response the client cached, so it records the policy the service "
                 "returned for the account rather than a choice the user made. The value "
                 "carries no timestamp of its own, so no date is reported. Setting names and "
                 "values are reported as stored. Field mapping was done against a single "
                 "private sample; no sample data is recorded for it.",
        "paths": ('*/com.roblox.client/files/appData/LocalStorage/appStorage.json',),
        "output_types": "standard",
        "artifact_icon": "shield"
    },
    "roblox_app_state": {
        "name": "Roblox - Application State",
        "description": "Parses install, launch count and notification state preferences of the Roblox Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Roblox",
        "notes": "One row per preference from the app's small shared_prefs files. "
                 "AppFirstLaunchTime and PREF_TIME_OF_ABSOLUTE_FIRST_LAUNCH are Unix "
                 "milliseconds and are converted; every other value is reported as stored. "
                 "The two are not the same event and did not agree on the device tested: "
                 "AppFirstLaunchTime matched the earliest activity in the extraction, while "
                 "the rate prompt library's absolute first launch value sat months later, at "
                 "the client version change, alongside a launch count that had restarted. The "
                 "large cached_app_settings_prefs.xml and the feature flag entries that make "
                 "up most of prefs.xml are server delivered configuration and are not reported "
                 "by this module. Field mapping was done against a single private sample; no "
                 "sample data is recorded for it.",
        "paths": ('*/com.roblox.client/shared_prefs/DeviceInstallPreferences.xml',
                  '*/com.roblox.client/shared_prefs/FirstRunPrefs.xml',
                  '*/com.roblox.client/shared_prefs/rate_me_maybe.xml',
                  '*/com.roblox.client/shared_prefs/NotificationPreferences.xml',
                  '*/com.roblox.client/shared_prefs/LocaleSettingsPreferences.xml'),
        "output_types": "standard",
        "artifact_icon": "device-mobile"
    },
}

import datetime
import json
import os
import re
import sqlite3
import xml.etree.ElementTree as ET
from urllib.parse import parse_qsl

from scripts.ilapfuncs import artifact_processor, logfunc, get_sqlite_db_path
from scripts.artifacts.storagePathViews import unique_files

APP_STORAGE = 'appData/LocalStorage/appStorage.json'
ROBLOX_DB = 'roblox-database-default'

# 2.702.0.632_20260112T133051Z_Player_0a72b_last.log
LOG_NAME = re.compile(r'^(?P<version>\d+(?:\.\d+)+)_(?P<stamp>\d{8}T\d{6}Z)_'
                      r'(?P<kind>[A-Za-z]+)_(?P<ident>[0-9a-fA-F]+)_(?P<suffix>.+)\.log$')
LOG_LINE_TIME = re.compile(r'^(?P<stamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z),')
JOIN_LINE = re.compile(r"! Joining game '(?P<jobid>[^']*)' place (?P<placeid>\d+) at (?P<server>\S+)")
SESSION_LINE = re.compile(r'AnalyticsSessionId is (?P<sid>[0-9a-fA-F-]+)')
UDMUX_LINE = re.compile(r'UDMUX Address = (?P<udmux>[^,]+), Port = (?P<udmux_port>\d+)'
                        r' \| RCC Server Address = (?P<rcc>[^,]+), Port = (?P<rcc_port>\d+)')
LOADTIME_LINE = re.compile(r'Report game_join_loadtime: (?P<body>.+)$')
ISO_FRACTION = re.compile(
    r'(?P<head>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})\.(?P<fraction>\d+)(?P<tail>.*)$')


def _utc(seconds):
    """A UTC datetime from Unix seconds, or '' when the value cannot be one."""
    try:
        return datetime.datetime.fromtimestamp(float(seconds), datetime.timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _utc_ms(value):
    """A UTC datetime from Unix milliseconds, or '' when the value cannot be one."""
    if value in (None, ''):
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _iso_utc(text):
    """A UTC datetime from the ISO 8601 stamp the client writes, or '' when it does not parse.

    The fraction is padded to six digits first. Before Python 3.11 fromisoformat accepts
    only three or six fractional digits, so a client writing any other precision would
    parse here and be dropped on the oldest supported runtime.
    """
    if not text:
        return ''
    text = text.replace('Z', '+00:00')
    match = ISO_FRACTION.match(text)
    if match:
        fraction = match.group('fraction')[:6].ljust(6, '0')
        text = f"{match.group('head')}.{fraction}{match.group('tail')}"
    try:
        return datetime.datetime.fromisoformat(text)
    except ValueError:
        return ''


def _app_storage(files_found):
    """(parsed appStorage.json, its path) for the first one that reads, else ({}, '')."""
    for file_found in files_found:
        file_found = str(file_found).replace('\\', '/')
        if not file_found.endswith(APP_STORAGE):
            continue
        try:
            with open(file_found, 'r', encoding='utf-8') as handle:
                loaded = json.load(handle)
        except (OSError, ValueError) as error:
            logfunc(f'Roblox: could not read {file_found}: {error}')
            continue
        if isinstance(loaded, dict):
            return loaded, file_found
    return {}, ''


def _nested(store, key):
    """A JSON value stored as a string inside appStorage.json, or None."""
    raw = store.get(key)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except ValueError:
        logfunc(f'Roblox: {key} in appStorage.json is not the JSON expected, skipped')
        return None


def _prefs(path):
    """{name: value} for an Android shared_prefs XML file, or {} when it does not parse."""
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as error:
        logfunc(f'Roblox: could not read {path}: {error}')
        return {}
    values = {}
    for entry in root:
        name = entry.get('name')
        if name is None:
            continue
        if entry.get('value') is not None:
            values[name] = entry.get('value')
        else:
            values[name] = entry.text if entry.text is not None else ''
    return values


@artifact_processor
def roblox_account(context):
    files_found = unique_files(context)
    store, source_path = _app_storage(files_found)

    prefs = {}
    for file_found in files_found:
        if str(file_found).replace('\\', '/').endswith('shared_prefs/prefs.xml'):
            prefs = _prefs(str(file_found))
            break

    data_list = []
    if store or prefs:
        hydration = _nested(store, 'PlayerHydrationBlob') or {}
        contact_sync = str(store.get('ContactImporterSyncTimestamp', ''))
        # Stored as a colon followed by Unix milliseconds on the sample tested.
        contact_ms = contact_sync.rsplit(':', 1)[-1] if contact_sync else ''

        data_list.append((
            _utc_ms(hydration.get('originalAccountCreationTimestampMs')),
            _utc(hydration.get('lastPerformed')) if hydration.get('lastPerformed') else '',
            _utc(store['MobileAdvertisingIdCacheTime']) if store.get('MobileAdvertisingIdCacheTime') else '',
            _utc_ms(contact_ms),
            store.get('UserId', '') or prefs.get('userid_long', ''),
            store.get('Username', '') or prefs.get('username', ''),
            store.get('DisplayName', '') or prefs.get('displayName', ''),
            store.get('IsUnder13', ''),
            prefs.get('under13', ''),
            hydration.get('ageBracket', ''),
            hydration.get('gender', ''),
            store.get('Membership', ''),
            store.get('LastSuccessfulSignInMethod', ''),
            store.get('CredentialValue', ''),
            store.get('CountryCode', ''),
            store.get('RobloxLocaleId', ''),
            store.get('GameLocaleId', ''),
            store.get('AuthenticatedTheme', ''),
            hydration.get('os', ''),
            hydration.get('platform', ''),
            hydration.get('isOriginalUser', ''),
            store.get('BrowserTrackerId', ''),
            store.get('AppInstallationId', ''),
            store.get('MobileAdvertisingId', ''),
            store.get('ContactImporterOptedInUsers', ''),
        ))

    data_headers = (
        ('Account Created Timestamp', 'datetime'),
        ('Hydration Last Performed Timestamp', 'datetime'),
        ('Advertising ID Cached Timestamp', 'datetime'),
        ('Contact Importer Sync Timestamp', 'datetime'),
        'User ID', 'Username', 'Display Name',
        'Is Under 13 (appStorage)', 'Under 13 (prefs.xml)',
        'Age Bracket (as stored)', 'Gender (as stored)', 'Membership (as stored)',
        'Last Successful Sign In Method (as stored)', 'Credential Value',
        'Country Code', 'Roblox Locale ID', 'Game Locale ID', 'Authenticated Theme',
        'OS (as stored)', 'Platform (as stored)', 'Is Original User',
        'Browser Tracker ID', 'App Installation ID', 'Mobile Advertising ID',
        'Contact Importer Opted In Users',
    )
    return data_headers, data_list, source_path


@artifact_processor
def roblox_previous_accounts(context):
    files_found = unique_files(context)
    store, source_path = _app_storage(files_found)
    accounts = _nested(store, 'PreviousAccountsList') or {}

    data_list = []
    if isinstance(accounts, dict):
        for key, entry in accounts.items():
            if not isinstance(entry, dict):
                logfunc('Roblox: a PreviousAccountsList entry was not an object, skipped')
                continue
            data_list.append((
                _utc(entry.get('signOutTimestamp')) if entry.get('signOutTimestamp') else '',
                str(entry.get('userId', '') or key),
                entry.get('username', ''),
                entry.get('displayName', ''),
                entry.get('userIdentifier', ''),
                entry.get('showInAccountPicker', ''),
                key,
            ))

    data_headers = (
        ('Sign Out Timestamp', 'datetime'),
        'User ID', 'Username', 'Display Name (as stored in list)',
        'User Identifier', 'Show In Account Picker', 'List Key',
    )
    return data_headers, data_list, source_path


@artifact_processor
def roblox_app_launches(context):
    files_found = unique_files(context)
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        name = os.path.basename(file_found.replace('\\', '/'))
        match = LOG_NAME.match(name)
        if not match:
            logfunc(f'Roblox: log file name not in the expected form, skipped: {name}')
            continue
        source_path = file_found

        try:
            stamp = datetime.datetime.strptime(match.group('stamp'), '%Y%m%dT%H%M%SZ')
            stamp = stamp.replace(tzinfo=datetime.timezone.utc)
        except ValueError:
            logfunc(f'Roblox: log file name carried an unreadable timestamp, skipped: {name}')
            continue

        first_line_time = ''
        line_count = 0
        try:
            with open(file_found, 'r', encoding='utf-8', errors='replace') as handle:
                for line in handle:
                    line_count += 1
                    if line_count == 1:
                        found = LOG_LINE_TIME.match(line)
                        if found:
                            first_line_time = _iso_utc(found.group('stamp'))
        except OSError as error:
            logfunc(f'Roblox: could not read {file_found}: {error}')
            continue

        data_list.append((
            stamp,
            first_line_time,
            match.group('version'),
            match.group('kind'),
            line_count,
            name,
        ))

    data_list.sort(key=lambda row: row[0])

    data_headers = (
        ('Launch Timestamp (from file name)', 'datetime'),
        ('First Log Line Timestamp', 'datetime'),
        'Client Version', 'Log Type', 'Log Line Count', 'Log File Name',
    )
    return data_headers, data_list, source_path


def _activity_row(stamp, report, place_id, job_id, server, context_fields):
    """One Game Activity row from a join line, its report line, and the log's own fields."""
    return (
        stamp,
        _utc(report['clienttime']) if report.get('clienttime') else '',
        place_id,
        report.get('universeid', ''),
        job_id,
        report.get('sid', '') or context_fields['session_id'],
        context_fields['session_id'],
        report.get('userid', ''),
        report.get('referral_page', ''),
        report.get('join_time', ''),
        server,
        context_fields['udmux'],
        context_fields['rcc'],
        context_fields['log_name'],
    )


@artifact_processor
def roblox_game_activity(context):
    files_found = unique_files(context)
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        name = os.path.basename(file_found.replace('\\', '/'))
        if not LOG_NAME.match(name):
            continue

        try:
            with open(file_found, 'r', encoding='utf-8', errors='replace') as handle:
                lines = handle.readlines()
        except OSError as error:
            logfunc(f'Roblox: could not read {file_found}: {error}')
            continue

        session_id = ''
        udmux = udmux_port = rcc = rcc_port = ''
        joins = []
        reports = {}

        for line in lines:
            stamp = ''
            found_time = LOG_LINE_TIME.match(line)
            if found_time:
                stamp = _iso_utc(found_time.group('stamp'))

            found = SESSION_LINE.search(line)
            if found:
                session_id = found.group('sid')

            found = UDMUX_LINE.search(line)
            if found:
                udmux = found.group('udmux').strip()
                udmux_port = found.group('udmux_port')
                rcc = found.group('rcc').strip()
                rcc_port = found.group('rcc_port')

            found = JOIN_LINE.search(line)
            if found:
                joins.append({'stamp': stamp, 'jobid': found.group('jobid'),
                              'placeid': found.group('placeid'), 'server': found.group('server')})

            found = LOADTIME_LINE.search(line)
            if found:
                fields = {}
                for part in found.group('body').split(','):
                    if ':' not in part:
                        continue
                    key, _, value = part.partition(':')
                    fields[key.strip()] = value.strip()
                if fields.get('placeid'):
                    fields['stamp'] = stamp
                    # A log can hold more than one join to the same place, so keep them
                    # in order rather than letting a later report replace an earlier one.
                    reports.setdefault(fields['placeid'], []).append(fields)

        servers = {'session_id': session_id, 'log_name': name,
                   'udmux': f'{udmux}:{udmux_port}' if udmux else '',
                   'rcc': f'{rcc}:{rcc_port}' if rcc else ''}

        for join in joins:
            pending = reports.get(join['placeid']) or []
            report = pending.pop(0) if pending else {}
            data_list.append(_activity_row(join['stamp'], report, join['placeid'],
                                           join['jobid'], join['server'], servers))

        # A report line no join line covered still evidences a join, so it gets its own
        # row, timed by the log line that carried it rather than by a repeated value.
        leftover = 0
        for place_id, pending in reports.items():
            for report in pending:
                leftover += 1
                data_list.append(_activity_row(report.get('stamp', ''), report,
                                               place_id, '', '', servers))
        if leftover:
            logfunc(f'Roblox: {leftover} game join report line(s) in {name} had no matching '
                    f'join line and are reported on their own row')

        if data_list:
            source_path = file_found

    data_list.sort(key=lambda row: str(row[0]))

    data_headers = (
        ('Join Timestamp', 'datetime'),
        ('Client Reported Join Timestamp', 'datetime'),
        'Place ID', 'Universe ID', 'Game Job ID', 'Play Session ID', 'Analytics Session ID',
        'User ID', 'Referral Page (as stored)', 'Join Time Seconds',
        'Join Server Address', 'UDMUX Address', 'RCC Server Address', 'Log File Name',
    )
    return data_headers, data_list, source_path


def _notification_types(path):
    """{notification id: type as stored} from analytic_event rows that carry one."""
    types = {}
    for uri in (f'file:{get_sqlite_db_path(path)}?mode=ro', f'file:{get_sqlite_db_path(path)}?immutable=1'):
        try:
            db = sqlite3.connect(uri, uri=True)
            rows = db.execute('select serialized_event from analytic_event').fetchall()
            db.close()
        except sqlite3.Error:
            continue
        for (event,) in rows:
            if not event:
                continue
            fields = dict(parse_qsl(str(event), keep_blank_values=True))
            if fields.get('notificationId') and fields.get('notificationType'):
                types.setdefault(fields['notificationId'], fields['notificationType'])
    return types


@artifact_processor
def roblox_push_notifications(context):
    files_found = unique_files(context)
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.replace('\\', '/').endswith(ROBLOX_DB):
            continue
        source_path = file_found

        reads = {}
        for label, uri in (('Committed', f'file:{get_sqlite_db_path(file_found)}?mode=ro'),
                           ('Pre-checkpoint', f'file:{get_sqlite_db_path(file_found)}?immutable=1')):
            try:
                db = sqlite3.connect(uri, uri=True)
                reads[label] = dict(db.execute(
                    'select notification_id, last_received_timestamp_ms from notification_id'))
                db.close()
            except sqlite3.Error as error:
                logfunc(f'Roblox: {label} read of {file_found} failed: {error}')
                reads[label] = {}

        committed = reads.get('Committed', {})
        precheckpoint = reads.get('Pre-checkpoint', {})
        only_pre = set(precheckpoint) - set(committed)
        if only_pre:
            logfunc(f'Roblox: {len(only_pre)} notification rows were present only in the '
                    f'pre-checkpoint read of {os.path.basename(file_found)}')

        types = _notification_types(file_found)

        for identifier in set(committed) | set(precheckpoint):
            if identifier in committed and identifier in precheckpoint:
                where = 'Both'
            elif identifier in committed:
                where = 'Committed only'
            else:
                where = 'Pre-checkpoint only'
            stamp = committed.get(identifier, precheckpoint.get(identifier))
            data_list.append((
                _utc_ms(stamp),
                identifier,
                types.get(identifier, ''),
                where,
                stamp,
            ))

    data_list.sort(key=lambda row: str(row[0]))

    data_headers = (
        ('Received Timestamp', 'datetime'),
        'Notification ID', 'Notification Type (as stored)', 'Source Read',
        'Received Timestamp (raw ms)',
    )
    return data_headers, data_list, source_path


@artifact_processor
def roblox_marketplace_searches(context):
    files_found = unique_files(context)
    store, source_path = _app_storage(files_found)
    searches = _nested(store, 'AXMarketplaceRecentSearches') or {}

    data_list = []
    if isinstance(searches, dict):
        terms = searches.get('terms')
        if isinstance(terms, list):
            for position, term in enumerate(terms, start=1):
                data_list.append((position, str(term), str(searches.get('userId', ''))))
        elif terms is not None:
            logfunc('Roblox: AXMarketplaceRecentSearches terms was not a list, skipped')

    data_headers = ('Position In Stored List', 'Search Term', 'User ID')
    return data_headers, data_list, source_path


@artifact_processor
def roblox_user_game_settings(context):
    files_found = unique_files(context)
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        try:
            root = ET.parse(file_found).getroot()
        except (OSError, ET.ParseError) as error:
            logfunc(f'Roblox: could not read {file_found}: {error}')
            continue
        source_path = file_found

        for item in root.iter('Item'):
            if item.get('class') != 'UserGameSettings':
                continue
            properties = item.find('Properties')
            if properties is None:
                continue
            for prop in properties:
                data_list.append((
                    prop.get('name', ''),
                    prop.tag,
                    prop.text.strip() if prop.text is not None else '',
                    item.get('referent', ''),
                ))

    data_headers = ('Setting Name', 'Stored Type', 'Value (as stored)', 'Item Referent')
    return data_headers, data_list, source_path


@artifact_processor
def roblox_account_policy(context):
    files_found = unique_files(context)
    store, source_path = _app_storage(files_found)
    policy = _nested(store, 'PolicyServiceHttpResponse') or {}

    data_list = []
    if isinstance(policy, dict):
        for name in sorted(policy):
            value = policy[name]
            if isinstance(value, list):
                data_list.append((name, ', '.join(str(item) for item in value), f'list of {len(value)}'))
            else:
                data_list.append((name, str(value), type(value).__name__))

    data_headers = ('Policy Setting', 'Value (as stored)', 'Stored Type')
    return data_headers, data_list, source_path


# name -> the unit its value carries, for the preferences this module converts.
_MS_PREFERENCES = {'AppFirstLaunchTime', 'PREF_TIME_OF_ABSOLUTE_FIRST_LAUNCH'}


@artifact_processor
def roblox_app_state(context):
    files_found = unique_files(context)
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        values = _prefs(file_found)
        if not values:
            continue
        source_path = file_found
        name = os.path.basename(file_found.replace('\\', '/'))
        for key in sorted(values):
            raw = values[key]
            data_list.append((
                _utc_ms(raw) if key in _MS_PREFERENCES else '',
                key,
                raw,
                name,
            ))

    data_headers = (
        ('Converted Timestamp', 'datetime'),
        'Preference Name', 'Value (as stored)', 'Preferences File',
    )
    return data_headers, data_list, source_path
