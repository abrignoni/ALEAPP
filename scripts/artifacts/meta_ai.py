# Meta AI - Android companion app (com.facebook.stella)

import json
import os
import re
import sqlite3
import xml.etree.ElementTree as ET
from html import unescape

from scripts.context import Context
from scripts.ilapfuncs import (
    artifact_processor,
    logfunc,
    open_sqlite_db_readonly,
)

__artifacts_v2__ = {
    "meta_ai_user_profile": {
        "name": "Meta AI - User Profile",
        "description": "User profile data from the Meta AI companion app local database",
        "author": "Shishir Panta",
        "creation_date": "2026-04-12",
        "last_update_date": "2026-06-15",
        "requirements": "none",
        "category": "Meta AI",
        "notes": "",
        "paths": ("*/databases/StellaDatabase*",),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "user",
        "html_columns": ["Profile Picture URI"],
    },
    "meta_ai_paired_devices_db": {
        "name": "Meta AI - Paired Devices (Database)",
        "description": "Ray-Ban device pairing history derived from the capture table",
        "author": "Shishir Panta",
        "creation_date": "2026-04-12",
        "last_update_date": "2026-06-15",
        "requirements": "none",
        "category": "Meta AI",
        "notes": "",
        "paths": ("*/databases/StellaDatabase*",),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "bluetooth",
    },
    "meta_ai_media_timeline": {
        "name": "Meta AI - Media Timeline",
        "description": "Captured media items with GPS, device, and import timestamps",
        "author": "Shishir Panta",
        "creation_date": "2026-04-12",
        "last_update_date": "2026-06-15",
        "requirements": "none",
        "category": "Meta AI",
        "notes": "",
        "paths": ("*/databases/StellaDatabase*",),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "image",
    },
    "meta_ai_paired_devices": {
        "name": "Meta AI - Paired Devices (Detailed)",
        "description": "Hardware details for paired Ray-Ban glasses from SharedPreferences",
        "author": "Shishir Panta",
        "creation_date": "2026-04-12",
        "last_update_date": "2026-06-15",
        "requirements": "none",
        "category": "Meta AI",
        "notes": "",
        "paths": ("*/app_light_prefs/com.facebook.stella/*",),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "bluetooth",
    },
    "meta_ai_linked_accounts": {
        "name": "Meta AI - Linked Accounts",
        "description": "Meta platform accounts linked to the companion app",
        "author": "Shishir Panta",
        "creation_date": "2026-04-12",
        "last_update_date": "2026-06-15",
        "requirements": "none",
        "category": "Meta AI",
        "notes": "",
        "paths": ("*/app_light_prefs/com.facebook.stella/*",),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "link",
    },
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _read_xml_key_value(file_path):
    """Reads key-value pairs from an XML SharedPreferences file."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return {child.attrib.get('name', 'unknown'): child.text for child in root}
    except (ET.ParseError, FileNotFoundError, KeyError) as e:
        logfunc(f"[Meta AI] Could not parse XML file {os.path.basename(file_path)}: {e}")
        return {}


def _parse_binary_prefs(file_path):
    """Parses binary SharedPreferences files (non-XML format)."""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()

        text = content.decode('utf-8', errors='ignore')
        text = text.replace('\x00', ' ').replace('\r', ' ').replace('\n', ' ')
        text = ' '.join(text.split())

        data = {}

        extractions = [
            ('device_serial',                ['device_frame_color_name', 'soc_build']),
            ('device_uuid',                  ['cloud_ota_error', 'build_flags_key']),
            ('btc_address',                  ['device_frame_type', 'device_identifier']),
            ('device_identifier',            ['device_lens_color_name', 'feature_key']),
            ('device_frame_type_short_name', ['device_lens_color']),
            ('device_frame_color_name',      ['soc_build', 'mcu_build', 'build_flavor']),
            ('device_lens_color_name',       ['feature_key', 'sku_code']),
            ('mcu_build',                    ['device_type']),
            ('soc_build',                    ['build_flavor']),
            ('device_type',                  ['device_hardware_type']),
            ('device_hardware_type',         ['device_uuid']),
        ]

        for key, terminators in extractions:
            key_pos = text.find(key)
            if key_pos == -1:
                continue
            value_start = key_pos + len(key)
            value_end = len(text)
            for terminator in terminators:
                term_pos = text.find(terminator, value_start)
                if term_pos != -1 and term_pos < value_end:
                    value_end = term_pos
            value = text[value_start:value_end].strip()
            if value.startswith('$'):
                value = value[1:]
            parts = value.split()
            value = parts[0] if len(parts) == 1 else ' '.join(parts[:4])
            if value:
                data[key] = value

        return data

    except Exception as e:
        logfunc(f"[Meta AI] Could not parse binary prefs file {os.path.basename(file_path)}: {e}")
        return {}


def _ms_to_unix(timestamp_ms):
    """Converts a millisecond timestamp to Unix seconds (float) for LAVA datetime columns."""
    if not timestamp_ms:
        return None
    try:
        return int(timestamp_ms) / 1000.0
    except (ValueError, TypeError):
        return None


def _parse_device_files():
    """
    Parses app_light_prefs files using the Context filename lookup map for
    O(1) access by filename rather than iterating the full file list.
    Returns (paired_devices dict, meta_accounts list).
    """
    lookup = Context.get_filename_lookup_map()
    paired_devices = {}
    meta_accounts  = []

    # connectivity_metadata.xml — direct lookup
    for file_path in lookup.get('connectivity_metadata.xml', []):
        data = _read_xml_key_value(file_path)
        mac = data.get('DEVICE-METADATA-ID', 'Unknown')
        paired_devices.setdefault(mac, {})
        paired_devices[mac]['mac']    = mac
        paired_devices[mac]['serial'] = data.get('serialNumber', '')

    # device_system_info_<mac> — variable suffix, scan map keys once
    for filename, paths in lookup.items():
        if not filename.startswith('device_system_info_'):
            continue
        mac = filename.replace('device_system_info_', '')
        paired_devices.setdefault(mac, {})
        for file_path in paths:
            data = _parse_binary_prefs(file_path)
            if data:
                paired_devices[mac]['mac']         = data.get('device_identifier', mac)
                paired_devices[mac]['btc']         = data.get('btc_address', '')
                paired_devices[mac]['serial']      = data.get('device_serial', '')
                paired_devices[mac]['uuid']        = data.get('device_uuid', '')
                paired_devices[mac]['frame']       = data.get('device_frame_type_short_name', '')
                paired_devices[mac]['frame_color'] = data.get('device_frame_color_name', '')
                paired_devices[mac]['lens']        = data.get('device_lens_color_name', '')
                paired_devices[mac]['mcu_build']   = data.get('mcu_build', '')
                paired_devices[mac]['soc_build']   = data.get('soc_build', '')

    # meta_fx_cache — direct lookup
    for file_path in lookup.get('meta_fx_cache', []):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            for account in cache_data.get('accounts', []):
                meta_accounts.append((
                    account.get('platform', 'Unknown'),
                    account.get('username', account.get('email', '')),
                    account.get('account_id', ''),
                ))
        except (json.JSONDecodeError, UnicodeDecodeError):
            try:
                with open(file_path, 'r', encoding='latin-1', errors='ignore') as f:
                    content = f.read()
                account_ids = re.findall(r'"account_id"\s*:\s*"?(\d+)"?', content)
                platforms   = re.findall(r'"account_type"\s*:\s*"([^"]+)"', content)
                usernames   = re.findall(r'"(?:username|email)"\s*:\s*"([^"]+)"', content)
                for i, account_id in enumerate(account_ids):
                    meta_accounts.append((
                        platforms[i] if i < len(platforms) else 'Unknown',
                        usernames[i] if i < len(usernames) else 'N/A',
                        account_id,
                    ))
            except Exception as e:
                logfunc(f"[Meta AI] Could not parse meta_fx_cache: {e}")

    return paired_devices, meta_accounts


# ---------------------------------------------------------------------------
# Artifact processors
# ---------------------------------------------------------------------------

@artifact_processor
def meta_ai_user_profile(context):
    data_headers = (
        ('Profile Fetched (UTC)', 'datetime'),
        'User ID',
        'Display Name',
        'Profile Picture URI',
        'Meta AI Eligible',
    )
    data_list   = []
    source_path = ''

    for source_path in context.get_files_found():
        if source_path.endswith(('-wal', '-shm', '-journal')):
            continue
        db = open_sqlite_db_readonly(source_path)
        if db is None:
            continue
        try:
            cursor = db.cursor()
            cursor.execute('''
                SELECT fetch_timestamp_ms, user_id, user_name,
                       profile_picture_uri, eligible_for_c50
                FROM user_profile
            ''')
            for fetch_ms, user_id, user_name, pic_uri, eligible in cursor.fetchall():
                pic_link = (
                    f'<a href="{pic_uri}" target="_blank">'
                    f'{pic_uri[:80]}{"..." if len(pic_uri or "") > 80 else ""}</a>'
                ) if pic_uri else ''
                data_list.append((
                    _ms_to_unix(fetch_ms),
                    user_id,
                    user_name,
                    pic_link,
                    'Yes' if eligible == 1 else 'No',
                ))
        except sqlite3.OperationalError as e:
            logfunc(f"[Meta AI] User Profile query failed: {e}")
        finally:
            db.close()

    return data_headers, data_list, source_path


@artifact_processor
def meta_ai_paired_devices_db(context):
    data_headers = (
        ('Last Capture (UTC)', 'datetime'),
        'Pairing ID (MAC)',
        'Serial Number',
        ('First Capture (UTC)', 'datetime'),
    )
    data_list   = []
    source_path = ''

    for source_path in context.get_files_found():
        if source_path.endswith(('-wal', '-shm', '-journal')):
            continue
        db = open_sqlite_db_readonly(source_path)
        if db is None:
            continue
        try:
            cursor = db.cursor()
            cursor.execute('''
                SELECT pairing_id, device_serial,
                       MIN(capture_timestamp_ms) AS first_ms,
                       MAX(capture_timestamp_ms) AS last_ms
                FROM capture
                WHERE pairing_id != ''
                GROUP BY pairing_id, device_serial
                ORDER BY last_ms DESC
            ''')
            for pairing_id, device_serial, first_ms, last_ms in cursor.fetchall():
                data_list.append((
                    _ms_to_unix(last_ms),
                    pairing_id,
                    device_serial,
                    _ms_to_unix(first_ms),
                ))
        except sqlite3.OperationalError as e:
            logfunc(f"[Meta AI] Paired Devices (DB) query failed: {e}")
        finally:
            db.close()

    return data_headers, data_list, source_path


@artifact_processor
def meta_ai_media_timeline(context):
    data_headers = (
        ('Captured (UTC)', 'datetime'),
        'Device Serial',
        'Pairing ID (MAC)',
        'Username',
        'Media Type',
        'GPS Coordinates',
        ('Imported to Phone (UTC)', 'datetime'),
        'File Path',
    )
    data_list   = []
    source_path = ''

    for source_path in context.get_files_found():
        if source_path.endswith(('-wal', '-shm', '-journal')):
            continue
        db = open_sqlite_db_readonly(source_path)
        if db is None:
            continue
        try:
            cursor = db.cursor()
            cursor.execute('''
                SELECT
                    cap.capture_timestamp_ms,
                    cap.device_serial,
                    cap.pairing_id,
                    up.user_name,
                    cap.type,
                    loc.latitude,
                    loc.longitude,
                    mi.import_completed_timestamp_ms,
                    mf.uri
                FROM capture AS cap
                LEFT JOIN media_item AS mi
                    ON cap.capture_id = mi.capture_id
                LEFT JOIN media_item_display AS mid
                    ON mi.media_item_id = mid.media_item_id AND mid.is_current_version = 1
                LEFT JOIN media_file AS mf
                    ON mid.display_full_media_file_id = mf.media_file_id
                LEFT JOIN media_item_location AS loc
                    ON mi.media_item_id = loc.media_item_id
                CROSS JOIN user_profile AS up
                WHERE mf.uri IS NOT NULL
                ORDER BY cap.capture_timestamp_ms DESC
            ''')
            for row in cursor.fetchall():
                cap_ms, serial, pairing_id, username, media_type, lat, lon, import_ms, uri = row
                gps = f"{lat}, {lon}" if lat is not None else ''
                data_list.append((
                    _ms_to_unix(cap_ms),
                    serial,
                    pairing_id,
                    username,
                    media_type,
                    gps,
                    _ms_to_unix(import_ms),
                    uri,
                ))
        except sqlite3.OperationalError as e:
            logfunc(f"[Meta AI] Media Timeline query failed: {e}")
        finally:
            db.close()

    return data_headers, data_list, source_path


@artifact_processor
def meta_ai_paired_devices(context):
    data_headers = (
        'Device ID (MAC)',
        'Bluetooth Address',
        'Serial Number',
        'Device UUID',
        'Frame & Color',
        'Lens Type',
        'MCU Build',
        'SoC Build',
    )

    paired_devices, _ = _parse_device_files()
    source_path = context.get_files_found()[0] if context.get_files_found() else ''

    data_list = []
    for mac, info in paired_devices.items():
        frame_color = (info.get('frame', '') + ' - ' + info.get('frame_color', '')).strip(' -')
        data_list.append((
            info.get('mac', mac),
            info.get('btc', ''),
            info.get('serial', ''),
            info.get('uuid', ''),
            frame_color,
            info.get('lens', ''),
            info.get('mcu_build', ''),
            info.get('soc_build', ''),
        ))

    return data_headers, data_list, source_path


@artifact_processor
def meta_ai_linked_accounts(context):
    data_headers = (
        'Platform',
        'Username / Email',
        'Account ID',
    )

    _, meta_accounts = _parse_device_files()
    source_path = context.get_files_found()[0] if context.get_files_found() else ''

    return data_headers, list(meta_accounts), source_path

