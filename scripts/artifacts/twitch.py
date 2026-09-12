__artifacts_v2__ = {
    "twitch_account": {
        "name": "Twitch - Account and Device",
        "description": "Parses the signed in Twitch account together with the device and "
                       "install identifiers the Android app records.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Twitch",
        "notes": "One row per app data directory. The app holds no databases of its own; "
                 "every value here comes from its preference files and from a single "
                 "identifier file. Account Created is an ISO 8601 value the app stores with "
                 "a trailing Z, reported as the UTC time it states. Device Token Refreshed, "
                 "Amazon Identity Registered and Country Last Updated are Unix "
                 "milliseconds. Country From IP is the country the app recorded from the "
                 "address it connected from, which places the connection rather than the "
                 "device. The account fields are written to two preference files, user.xml "
                 "and twitch_user_prefs.xml, and one row is reported rather than two: on the "
                 "tested device the two agreed on all 21 shared names and the second carried "
                 "only two extra migration flags, so values are read from whichever is "
                 "present and both file names are recorded in the source column. Account "
                 "type, verification and partner flags are reported as stored. The app's "
                 "image cache held four entries whose names are not derivable from any "
                 "address the extraction stores, so they are not linked here. Field mapping "
                 "was done against a private sample provided by Mattia; no sample data is "
                 "recorded for it.",
        "paths": (
            '*/tv.twitch.android.app/shared_prefs/user.xml',
            '*/tv.twitch.android.app/shared_prefs/twitch_user_prefs.xml',
            '*/tv.twitch.android.app/shared_prefs/fused_locale_prefs_file.xml',
            '*/tv.twitch.android.app/shared_prefs/AmazonIdentityPrefs.xml',
            '*/tv.twitch.android.app/shared_prefs/DeviceTokenPreferences.xml',
            '*/tv.twitch.android.app/shared_prefs/twitch_app_prefs.xml',
            '*/tv.twitch.android.app/files/unique_id',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user"
    },
}

import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from scripts.artifacts.storagePathViews import canonical_path, unique_files
from scripts.ilapfuncs import artifact_processor, logfunc

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_PACKAGE = 'tv.twitch.android.app'


def _container(context, path):
    '''A key for the app data directory a matched file belongs to.

    Matched on a path segment equal to the package name rather than on a substring, so a
    directory that merely contains the name cannot be taken for the container. The key is
    canonicalised through storagePathViews, so the /data/data and /data/user/0 spellings
    of one directory collapse to one key while a second Android user stays separate.
    '''
    relative = str(context.get_relative_path(path)).replace('\\', '/')
    parts = relative.split('/')
    for position, part in enumerate(parts):
        if part == _PACKAGE:
            return canonical_path('/'.join(parts[:position + 1]))[0]
    return canonical_path(relative)[0]


def _by_container(context):
    '''{container key: [path]} for the files this artifact matched.'''
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


def _prefs(source_path):
    '''{name: text} for an Android shared preferences file.'''
    values = {}
    try:
        root = ET.parse(source_path).getroot()
    except (ET.ParseError, OSError) as ex:
        logfunc(f'Twitch: could not parse {os.path.basename(source_path)}: {ex}')
        return values
    for element in root:
        name = element.get('name')
        if name is None:
            continue
        values[name] = element.get('value') if element.tag != 'string' else (element.text or '')
    return values


@artifact_processor
def twitch_account(context):
    data_list = []
    source_files = []

    for paths in _by_container(context).values():
        files = {os.path.basename(path): path for path in paths}
        relative_paths = [context.get_relative_path(path) for path in paths]

        # The account fields are written to both preference files. Values are read from
        # whichever is present, preferring the migrated file, rather than emitting a row
        # per file, because the two hold the same account.
        account = {}
        for name in ('user.xml', 'twitch_user_prefs.xml'):
            if name in files:
                for key, value in _prefs(files[name]).items():
                    account.setdefault(key, value)
        if not account:
            continue

        locale = _prefs(files['fused_locale_prefs_file.xml']) if 'fused_locale_prefs_file.xml' in files else {}
        amazon = _prefs(files['AmazonIdentityPrefs.xml']) if 'AmazonIdentityPrefs.xml' in files else {}
        token = _prefs(files['DeviceTokenPreferences.xml']) if 'DeviceTokenPreferences.xml' in files else {}
        app = _prefs(files['twitch_app_prefs.xml']) if 'twitch_app_prefs.xml' in files else {}

        unique_id = ''
        if 'unique_id' in files:
            try:
                with open(files['unique_id'], 'r', encoding='utf-8', errors='replace') as handle:
                    unique_id = handle.read().strip()
            except OSError as ex:
                logfunc(f'Twitch: could not read the install identifier file: {ex}')

        source_files.extend(relative_paths)
        data_list.append((
            _iso(account.get('created_at')),
            _ms(token.get('date_device_token_last_refreshed')),
            _ms(amazon.get('last_register_time_ms')),
            _ms(locale.get('country_code_from_ip_last_updated_timestamp')),
            str(account.get('name', '')),
            str(account.get('DisplayName', '')),
            str(account.get('email', '')),
            str(account.get('userIdInt', '')),
            str(account.get('user_type', '')),
            str(account.get('account_is_verified', '')),
            str(account.get('has_two_factor_authentication_enabled', '')),
            str(account.get('is_partner', '')),
            str(account.get('is_affiliate', '')),
            str(account.get('is_turbo', '')),
            str(account.get('showEmailVerificationBanner', '')),
            str(account.get('is_email_reusable', '')),
            str(account.get('arePushNotificationsEnabled', '')),
            str(account.get('Logo', '')),
            str(locale.get('country_code_from_ip_prefs_key', '')),
            str(amazon.get('user_id_registered', '')),
            unique_id,
            str(app.get('cookieDomain', '')),
            '; '.join(sorted(relative_paths)),
        ))

    data_headers = (
        ('Account Created', 'datetime'),
        ('Device Token Refreshed', 'datetime'),
        ('Amazon Identity Registered', 'datetime'),
        ('Country Last Updated', 'datetime'),
        'User Name',
        'Display Name',
        'Email',
        'User ID',
        'User Type (as stored)',
        'Account Verified (as stored)',
        'Two Factor Authentication (as stored)',
        'Partner (as stored)',
        'Affiliate (as stored)',
        'Turbo (as stored)',
        'Email Verification Banner (as stored)',
        'Email Reusable (as stored)',
        'Push Notifications (as stored)',
        'Profile Picture Address',
        'Country From IP (as stored)',
        'Amazon Registered User ID',
        'Install Identifier',
        'Cookie Domain (as stored)',
        'Source Files',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))
