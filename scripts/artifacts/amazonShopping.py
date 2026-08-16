__artifacts_v2__ = {
    "get_amazon_account_store": {
        "name": "Amazon Shopping - Account Store",
        "description": "Rows from the accounts, userdata, tokens and device_data tables in "
                       "map_data_storage.db, reported as stored under the app's own key "
                       "names with their per-row timestamps and deleted and dirty flags.",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Amazon Shopping",
        "notes": "Dorai, Hutchinson, Rodriguez and Karabiyik describe the accounts table "
                 "as holding the accounts used with the app and userdata as holding "
                 "per-account details (name, username, account id, device name and "
                 "authentication tokens), with each row flagged for deletion state. On a "
                 "tested sample the userdata keys carried the app's own com.amazon.dcp.sso "
                 "names for username, first name, account id and device name, and the "
                 "tokens table carried cookies and OAuth tokens; values are reported as "
                 "stored and their meaning beyond the key name is not asserted. Timestamps "
                 "are Unix milliseconds. The Account column resolves the row's account id "
                 "to the accounts table's display name where present.\n"
                 "Reference: Gokila Dorai, Shinelle Hutchinson, Beatriz Rodriguez and Umit "
                 "Karabiyik, 'Mobile Commerce - Analysis and Investigation of the Online "
                 "Safety, Privacy, and Data Forensics of Amazon and Etsy Apps', HICSS 2023, "
                 "https://aisel.aisnet.org/hicss-56/in/social_shopping/3/",
        "paths": ('*/com.amazon.mShop.android.shopping/databases/map_data_storage.db*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "anne_a15": "Android 15 | 5 rows",
            "samsungs20_a13": "Android 13 | 45 rows",
        },
    },
    "get_amazon_preferences": {
        "name": "Amazon Shopping - Preferences",
        "description": "Key and value rows from DataStore.xml, account_change_observer.xml "
                       "and MobileGrowthMetricsDataStore.xml, reported as stored.",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Amazon Shopping",
        "notes": "Dorai, Hutchinson, Rodriguez and Karabiyik describe last_seen_account in "
                 "account_change_observer.xml as the account id of the last account signed "
                 "into the app, and MobileGrowthMetricsDataStore.xml as recording the last "
                 "time the app was started. Keys whose name ends in TIME_IN_MS or "
                 "Timestamp and whose value is a 13-digit number are additionally rendered "
                 "as Unix milliseconds beside the stored value; everything else is "
                 "reported as stored.\n"
                 "Reference: Gokila Dorai, Shinelle Hutchinson, Beatriz Rodriguez and Umit "
                 "Karabiyik, 'Mobile Commerce - Analysis and Investigation of the Online "
                 "Safety, Privacy, and Data Forensics of Amazon and Etsy Apps', HICSS 2023, "
                 "https://aisel.aisnet.org/hicss-56/in/social_shopping/3/",
        "paths": ('*/com.amazon.mShop.android.shopping/shared_prefs/DataStore.xml',
                  '*/com.amazon.mShop.android.shopping/shared_prefs/account_change_observer.xml',
                  '*/com.amazon.mShop.android.shopping/shared_prefs/MobileGrowthMetricsDataStore.xml'),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {
            "anne_a15": "Android 15 | 16 rows",
            "samsungs20_a13": "Android 13 | 18 rows",
        },
    },
    "get_amazon_image_cache_registry": {
        "name": "Amazon Shopping - Image Cache Registry",
        "description": "Rows from the FileCacheRegistry table in ssnapImageCacheRegistry.db: "
                       "cached image URL, feature name, file path, size, hit count and "
                       "timestamps as stored.",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Amazon Shopping",
        "notes": "A registry of image files the app cached, keyed by the URL they were "
                 "fetched from; what a cached image was shown for is not established "
                 "here. Timestamps are Unix milliseconds.",
        "paths": ('*/com.amazon.mShop.android.shopping/databases/ssnapImageCacheRegistry.db*',),
        "output_types": "standard",
        "artifact_icon": "photo",
        "sample_data": {
            "anne_a15": "Android 15 | no ssnapImageCacheRegistry.db found",
            "samsungs20_a13": "Android 13 | no ssnapImageCacheRegistry.db found",
        },
    },
    "get_amazon_webview_state": {
        "name": "Amazon Shopping - Web View State",
        "description": "Saved web view fragment states from app_mashWebViewState: the "
                       "URLs held in each state file, with the millisecond timestamp from "
                       "the file's own name.",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Amazon Shopping",
        "notes": "Each file in app_mashWebViewState is named <unix ms>MASHWebFragment<n> "
                 "and holds a base64 wrapped, gzip compressed Android saved-state parcel "
                 "for a web view fragment. The parcel format is not parsed; URLs are "
                 "extracted from the decompressed bytes as found, one row per URL, with "
                 "their order preserved, so a row states that the URL was present in that "
                 "fragment's saved state and nothing more. On a tested sample the states "
                 "included storefront, product and order confirmation page URLs.",
        "paths": ('*/com.amazon.mShop.android.shopping/app_mashWebViewState/*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "anne_a15": "Android 15 | 2 rows",
            "samsungs20_a13": "Android 13 | 3 rows",
        },
    },
}


import base64
import datetime
import gzip
import re
import sqlite3
import xml.etree.ElementTree as ET

from os.path import isfile

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly

_MS_KEY_RE = re.compile(r'(TIME_IN_MS|Timestamp)$', re.IGNORECASE)


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _rows(source_path, sql):
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    if db is None:
        return []
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


def _unique_files(context, suffix):
    '''The context's files matching suffix, without the duplicate paths extractions carry
    for the same file (data_mirror, and /data/data next to /data/user/0), keyed on the
    evidence-relative path so the report's own data folder cannot be rewritten instead.'''
    seen = set()
    result = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if not file_found.endswith(suffix):
            continue
        relative = str(context.get_relative_path(file_found)).replace('\\', '/')
        if 'data_mirror' in relative:
            continue
        normalized = re.sub(r'(^|/)data/data/', r'\1data/user/0/', relative)
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(file_found)
    return result


def _yes_no(value):
    return 'YES' if value else 'NO'


@artifact_processor
def get_amazon_account_store(context):
    data_list = []
    source_path = ''
    for file_found in _unique_files(context, 'map_data_storage.db'):
        source_path = source_path or file_found
        source_file = context.get_relative_path(file_found)
        display_names = {row[0]: row[1] or '' for row in _rows(
            file_found, 'SELECT directed_id, display_name FROM accounts')}

        for directed_id, display_name, timestamp, deleted, dirty in _rows(file_found, '''
                SELECT directed_id, display_name, account_timestamp, account_deleted,
                       account_dirty FROM accounts'''):
            data_list.append((
                _ms_to_utc(timestamp), 'accounts', display_name or '', directed_id,
                'display_name', display_name, _yes_no(deleted), _yes_no(dirty),
                source_file))
        for table, account_col, key_col, value_col, ts_col in (
                ('userdata', 'userdata_account_id', 'userdata_key', 'userdata_value',
                 'userdata_timestamp'),
                ('tokens', 'token_account_id', 'token_key', 'token_value',
                 'token_timestamp'),
                ('device_data', 'device_data_namespace', 'device_data_key',
                 'device_data_value', 'device_data_timestamp')):
            deleted_col = table.rstrip('s') + '_deleted' if table != 'device_data' else 'device_data_deleted'
            dirty_col = table.rstrip('s') + '_dirty' if table != 'device_data' else 'device_data_dirty'
            for account, key, value, timestamp, deleted, dirty in _rows(file_found, f'''
                    SELECT {account_col}, {key_col}, {value_col}, {ts_col},
                           {deleted_col}, {dirty_col} FROM {table}'''):
                data_list.append((
                    _ms_to_utc(timestamp), table, display_names.get(account, ''),
                    account, key, value, _yes_no(deleted), _yes_no(dirty), source_file))

    data_headers = (('Timestamp', 'datetime'), 'Table', 'Account', 'Account ID / Namespace',
                    'Key', 'Value (as stored)', 'Deleted', 'Dirty', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def get_amazon_preferences(context):
    data_list = []
    source_path = ''
    for suffix in ('DataStore.xml', 'account_change_observer.xml',
                   'MobileGrowthMetricsDataStore.xml'):
        for file_found in _unique_files(context, suffix):
            source_path = source_path or file_found
            source_file = context.get_relative_path(file_found)
            try:
                root = ET.parse(file_found).getroot()
            except (ET.ParseError, OSError, ValueError):
                continue
            for node in root:
                name = node.attrib.get('name', '')
                value = node.attrib.get('value', node.text)
                if value is None:
                    continue
                value = str(value)
                rendered = ''
                if _MS_KEY_RE.search(name) and value.isdigit() and len(value) == 13:
                    rendered = _ms_to_utc(value)
                data_list.append((rendered, name, value, source_file))

    data_headers = (('Rendered Timestamp', 'datetime'), 'Key', 'Value (as stored)',
                    'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def get_amazon_image_cache_registry(context):
    data_list = []
    source_path = ''
    for file_found in _unique_files(context, 'ssnapImageCacheRegistry.db'):
        source_path = source_path or file_found
        source_file = context.get_relative_path(file_found)
        for (url, feature, size, file_path, last_accessed, expiry, last_modified,
             hits) in _rows(file_found, '''
                SELECT url, featureName, size, filePath, lastAccessed, expiryDate,
                       lastModified, numHits FROM FileCacheRegistry
                ORDER BY lastAccessed'''):
            data_list.append((
                _ms_to_utc(last_accessed), _ms_to_utc(last_modified), _ms_to_utc(expiry),
                url, feature, file_path, size, hits, source_file))

    data_headers = (('Last Accessed', 'datetime'), ('Last Modified', 'datetime'),
                    ('Expiry', 'datetime'), 'URL', 'Feature Name', 'File Path',
                    'Size (bytes)', 'Hit Count', 'Source File')
    return data_headers, data_list, source_path


_STATE_NAME_RE = re.compile(r'^(\d{13})MASHWebFragment')
_URL_RE = re.compile(rb'https?://[\x20-\x7e]{4,500}')


@artifact_processor
def get_amazon_webview_state(context):
    data_list = []
    source_path = ''
    for file_found in _unique_files(context, ''):
        name = file_found.replace('\\', '/').rsplit('/', 1)[-1]
        match = _STATE_NAME_RE.match(name)
        if not match or not isfile(file_found):
            continue
        source_path = source_path or file_found
        source_file = context.get_relative_path(file_found)
        try:
            with open(file_found, 'rb') as handle:
                data = gzip.decompress(base64.b64decode(handle.read()))
        except (OSError, ValueError, gzip.BadGzipFile):
            continue
        urls = []
        for raw_url in _URL_RE.findall(data):
            url = raw_url.decode('ascii', 'replace').rstrip('"')
            if url not in urls:
                urls.append(url)
        for position, url in enumerate(urls, 1):
            data_list.append((
                _ms_to_utc(match.group(1)), name, position, url, source_file))

    data_headers = (('State Timestamp', 'datetime'), 'State File', 'URL Order', 'URL',
                    'Source File')
    return data_headers, data_list, source_path
