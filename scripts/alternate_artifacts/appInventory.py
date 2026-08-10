""" appInventory.py - extraction, app and file inventory for coverage analysis

Developer-only module (see README.md in this folder). It writes three
machine-readable tables into the LAVA SQLite output (_lava_artifacts.db) so
downstream tooling (e.g. batch-leapp) can determine, per extraction, which
installed apps exist, which files belong to each app, and which
extraction/device the data came from. Combined with the
_artifact_search_patterns / _file_path_list / _artifact_pattern_to_file
registry tables the framework already writes, this makes it possible to diff
"apps installed" against "apps parsed by the tooling".

Notes:
- appFileInventory lists EVERY file in the extraction (not only app files) so
  unparsed non-app data can be measured too. It is lava_only to keep the HTML
  report usable.
- Modified Time values are stored as text, not LAVA datetime: zip archives
  record zone-less DOS timestamps, so coercing them to UTC would be wrong.
  Tar and directory sources are recorded in UTC.
- The artifacts are anchored on build.prop / packages.xml (present in
  practically every Android image) because ALEAPP has no 'paths: None'
  always-run convention.
"""

__artifacts_v2__ = {
    "extractionInfo": {
        "name": "Extraction Info",
        "description": "Identifiers for this extraction and parse run: LEAPP version, "
                       "input path, extraction type, Android version and device identifiers "
                       "from build.prop. Written to the LAVA database so batch tooling "
                       "can tell which device/extraction the data came from.",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-08",
        "last_update_date": "2026-07-08",
        "requirements": "none",
        "category": "App Inventory",
        "notes": "",
        "paths": ('*/system/build.prop', '*/vendor/build.prop'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "id",
    },
    "installedAppInventory": {
        "name": "Installed App Inventory",
        "description": "Canonical installed application inventory from packages.xml: "
                       "one row per package with install/update times, installer and "
                       "code path. Handles both plain and Android Binary XML formats.",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-08",
        "last_update_date": "2026-07-08",
        "requirements": "none",
        "category": "App Inventory",
        "notes": "",
        "paths": ('*/system/packages.xml',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "package",
    },
    "appFileInventory": {
        "name": "App File Inventory",
        "description": "Complete file listing of the extraction with each file mapped to "
                       "the app package it belongs to, when applicable. "
                       "Supports coverage analysis of which apps/files the tooling parsed. "
                       "LAVA only due to size.",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-08",
        "last_update_date": "2026-07-08",
        "requirements": "none",
        "category": "App Inventory",
        "notes": "Modified Time is text as recorded in the source (zip timestamps are "
                 "zone-less; tar/directory timestamps are UTC).",
        "paths": ('*/system/packages.xml', '*/system/build.prop', '*/vendor/build.prop'),
        "output_types": "lava_only",
        "artifact_icon": "files",
    },
}

import datetime
import os
import re
import xml.etree.ElementTree as etree

import xmltodict

from scripts.ilapfuncs import artifact_processor, abxread, checkabx, logfunc
from scripts.version_info import leapp_name, leapp_version


# Package-owned locations, checked in order; first match wins. The directory
# name in these locations IS the package name, so no lookup map is needed.
_PKG = r'([A-Za-z0-9_][A-Za-z0-9_.\-]*)'
_LOCATION_PATTERNS = (
    (re.compile(r'Android/data/' + _PKG + r'(?=/|$)'), 'external_data'),
    (re.compile(r'Android/media/' + _PKG + r'(?=/|$)'), 'external_media'),
    (re.compile(r'Android/obb/' + _PKG + r'(?=/|$)'), 'obb'),
    (re.compile(r'data/data/' + _PKG + r'(?=/|$)'), 'data'),
    (re.compile(r'data/user/\d+/' + _PKG + r'(?=/|$)'), 'data'),
    (re.compile(r'data/user_de/\d+/' + _PKG + r'(?=/|$)'), 'device_protected'),
    (re.compile(r'data/app/(?:~~[^/]+/)?' + _PKG + r'-[^/]+(?=/|$)'), 'apk'),
)

# build.prop keys of interest: label -> candidate keys in preference order.
_BUILD_PROP_KEYS = (
    ('Manufacturer', ('ro.product.manufacturer', 'ro.product.vendor.manufacturer',
                      'ro.product.system.manufacturer')),
    ('Brand', ('ro.product.brand', 'ro.product.vendor.brand', 'ro.product.system.brand')),
    ('Model', ('ro.product.model', 'ro.product.vendor.model', 'ro.product.system.model')),
    ('Device', ('ro.product.device', 'ro.product.vendor.device', 'ro.product.system.device')),
    ('Android Version', ('ro.build.version.release', 'ro.system.build.version.release',
                         'ro.vendor.build.version.release')),
    ('SDK Version', ('ro.build.version.sdk', 'ro.system.build.version.sdk',
                     'ro.vendor.build.version.sdk')),
    ('Build ID', ('ro.build.id', 'ro.system.build.id', 'ro.vendor.build.id')),
    ('Build Fingerprint', ('ro.build.fingerprint', 'ro.system.build.fingerprint',
                           'ro.vendor.build.fingerprint')),
    ('Serial Number', ('ro.serialno', 'ro.boot.serialno')),
    ('Time Zone', ('persist.sys.timezone',)),
)


def _seeker_kind(seeker):
    '''Human-readable extraction type from the seeker class name.'''
    kind = type(seeker).__name__
    return {
        'FileSeekerDir': 'directory',
        'FileSeekerTar': 'tar',
        'FileSeekerZip': 'zip',
        'FileSeekerFile': 'single file',
    }.get(kind, kind)


def _input_path(seeker):
    '''Best-effort path of the extraction input for this seeker.'''
    zip_file = getattr(seeker, 'zip_file', None)
    if zip_file is not None:
        return getattr(zip_file, 'filename', '') or ''
    tar_file = getattr(seeker, 'tar_file', None)
    if tar_file is not None:
        return getattr(tar_file, 'name', '') or ''
    return getattr(seeker, 'directory', '') or ''


def _read_build_prop(file_path):
    '''Parse a build.prop file into a key -> value dict.'''
    props = {}
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, _, value = line.partition('=')
                props[key.strip()] = value.strip()
    except OSError as ex:
        logfunc(f'WARNING: could not read {file_path}: {ex}')
    return props


def _read_unix_time_ms(unix_time_ms):
    '''Millisecond epoch (int or hex string) -> aware UTC datetime, or empty string.'''
    if unix_time_ms in (0, None, ''):
        return ''
    try:
        if isinstance(unix_time_ms, str):
            unix_time_ms = float.fromhex(unix_time_ms)
        return (datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
                + datetime.timedelta(seconds=unix_time_ms / 1000))
    except (ValueError, OverflowError, TypeError) as ex:
        logfunc(f'WARNING: could not convert timestamp {unix_time_ms}: {ex}')
        return ''


def _parse_packages_xml(file_path):
    '''Yield package dicts from packages.xml (plain or Android Binary XML).'''
    try:
        if checkabx(file_path):
            tree = abxread(file_path, False)
            xmlstring = etree.tostring(tree.getroot()).decode()
            doc = xmltodict.parse(xmlstring)
        else:
            with open(file_path, encoding='utf-8', errors='replace') as fd:
                doc = xmltodict.parse(fd.read())
    except Exception as ex:  # pylint: disable=broad-except
        logfunc(f'WARNING: could not parse {file_path}: {ex}')
        return []
    packages = doc.get('packages', {}).get('package', [])
    if isinstance(packages, dict):
        packages = [packages]
    return packages


def _format_utc(epoch):
    '''Epoch seconds -> "YYYY-MM-DD HH:MM:SS" UTC text, or empty string.'''
    if not epoch:
        return ''
    try:
        return datetime.datetime.fromtimestamp(
            epoch, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    except (OverflowError, OSError, ValueError):
        return ''


def _iter_extraction_files(seeker):
    '''Yield (path, size, modified_time_text) for every file in the extraction.

    Reads the seeker's existing listings (zip/tar central directory, directory
    walk) without extracting or copying anything.
    '''
    zip_file = getattr(seeker, 'zip_file', None)
    if zip_file is not None:
        for info in zip_file.infolist():
            if info.is_dir() or info.filename.startswith('__MACOSX'):
                continue
            d = info.date_time
            mtime = f'{d[0]:04d}-{d[1]:02d}-{d[2]:02d} {d[3]:02d}:{d[4]:02d}:{d[5]:02d}'
            yield info.filename, info.file_size, mtime
        return
    tar_file = getattr(seeker, 'tar_file', None)
    if tar_file is not None:
        for member in tar_file.getmembers():
            if not member.isfile():
                continue
            yield member.name, member.size, _format_utc(member.mtime)
        return
    all_files = getattr(seeker, '_all_files', None)
    if isinstance(all_files, list):
        directory = getattr(seeker, 'directory', '')
        for item in all_files:
            try:
                if os.path.isdir(item):
                    continue
                stat = os.stat(item)
                size, mtime = stat.st_size, _format_utc(stat.st_mtime)
            except OSError:
                size, mtime = '', ''
            rel = item.replace(directory, '', 1) if directory else item
            yield rel, size, mtime


def _map_path_to_package(path):
    '''Return (package_name, location_type) for an extraction path.'''
    normalized = path.replace('\\', '/')
    for pattern, location in _LOCATION_PATTERNS:
        match = pattern.search(normalized)
        if match:
            return match.group(1), location
    return '', ''


@artifact_processor
def extractionInfo(context):
    '''One row per identifier describing this extraction and parse run.'''
    seeker = context.get_seeker()
    out_params = context.get_output_params()
    data_list = []

    def add(prop, value, source=''):
        if value is not None and value != '':
            data_list.append((prop, str(value), source))

    input_path = _input_path(seeker)
    add('LEAPP Name', leapp_name)
    add('LEAPP Version', leapp_version)
    add('Extraction Type', _seeker_kind(seeker))
    add('Input Path', input_path)
    add('Input Name', os.path.basename(input_path) if input_path else '')
    add('Report Folder', os.path.basename(out_params.output_folder_base))

    # Merge build.prop files, preferring /system/ over /vendor/ (unprefixed keys).
    props = {}
    source_path = ''
    files = sorted((str(f) for f in context.get_files_found()),
                   key=lambda p: 0 if '/system/' in p.replace('\\', '/') else 1)
    for file_found in files:
        if '/mirror/' in file_found.replace('\\', '/'):
            continue
        if not source_path:
            source_path = file_found
        for key, value in _read_build_prop(file_found).items():
            props.setdefault(key, value)

    for label, candidate_keys in _BUILD_PROP_KEYS:
        for key in candidate_keys:
            if props.get(key):
                add(label, props[key], 'build.prop')
                break

    data_headers = ('Property', 'Value', 'Source')
    return data_headers, data_list, source_path or input_path


@artifact_processor
def installedAppInventory(context):
    '''One row per installed package from packages.xml.'''
    data_list = []
    source_path = ''
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if '/mirror/' in file_found.replace('\\', '/') or os.path.isdir(file_found):
            continue
        source_path = file_found
        for package in _parse_packages_xml(file_found):
            data_list.append((
                package.get('@name', ''),
                _read_unix_time_ms(package.get('@it', None)),
                _read_unix_time_ms(package.get('@ut', None)),
                package.get('@installer', ''),
                package.get('@codePath', ''),
                'packages.xml',
            ))
        if data_list:
            break

    logfunc(f'Installed App Inventory: {len(data_list)} package(s) recorded')
    data_headers = ('Package Name', ('Install Time', 'datetime'),
                    ('Update Time', 'datetime'), 'Installer', 'Code Path',
                    'Data Source')
    return data_headers, data_list, source_path


@artifact_processor
def appFileInventory(context):
    '''Every file in the extraction, mapped to its app package when possible.'''
    seeker = context.get_seeker()

    data_list = []
    mapped = 0
    for path, size, mtime in _iter_extraction_files(seeker):
        package, location = _map_path_to_package(path)
        if package:
            mapped += 1
        data_list.append((package, location, path, size, mtime))

    logfunc(f'App File Inventory: {len(data_list)} file(s) listed, '
            f'{mapped} mapped to app packages')
    data_headers = ('Package Name', 'Location Type', 'File Path',
                    'File Size', 'Modified Time')
    return data_headers, data_list, _input_path(seeker)
