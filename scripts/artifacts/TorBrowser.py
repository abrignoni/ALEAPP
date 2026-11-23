# pylint: disable=W0718
__artifacts_v2__ = {
    "torbrowser_thumbnails": {
        "name": "Tor Browser Tab Thumnails",
        "description": "Files in the Tor Browser cache folder "
                       "mozac_browser_thumbnails/private_thumbnails, with the modification time "
                       "the tool reads from the input for each file.",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}, @AlexisBrignoni, Codex",
        "creation_date": "2025-11-14",
        "last_update_date": "2026-11-23",
        "requirements": "none",
        "category": "Tor Browser",
        "notes": "File Modified is the modification time the tool reads from the input for the "
                 "file as a UTC time, to the whole second, such as from a tar header or a zip "
                 "entry's NTFS or extended timestamp field. When the tool reads no UTC time, File"
                 " Modified is blank and Modified (no zone, as stored) shows the date and time "
                 "the input holds, with no zone conversion. That is the case for a FAT directory "
                 "entry, an exFAT directory entry (its stored UTC offset is not applied or shown "
                 "here) and a zip entry with only its DOS date and time. Both columns are blank "
                 "when the input holds neither, and a recorded time of 0 is treated as no time. "
                 "For a folder or single-file input File Modified is the time the operating "
                 "system reports for that file on the examiner's machine, including any "
                 "conversion it applied, and whatever copied the file there may have set it. The "
                 "staged copy's own time is not reported. File Modified is not read from the "
                 "file's content and depends on the acquisition having kept file times. No sample"
                 " data is recorded for this artifact.",
        "paths": ('*/org.torproject.torbrowser/cache/mozac_browser_thumbnails/private_thumbnails/*.0'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "photo"
    },
    "torbrowser_bookmarks": {
        "name": "Tor Browser - Bookmarks",
        "description": "Parses Tor Browser Bookmarks",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-11-14",
        "last_update_date": "2025-11-14",
        "requirements": "none",
        "category": "Tor Browser",
        "notes": "Run on hc_pixel8pro_a16 (version code 2016164570, 1 row) and "
                 "russell_pixel6a_a13 (version code 2015960779, 0 rows).",
        "paths": ('*/org.torproject.torbrowser/files/places.sqlite*'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "bookmark",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | org.torproject.torbrowser vc 2016164570 | 1 row",
            "russell_pixel6a_a13": "Android 13 | org.torproject.torbrowser vc 2015960779 | 0 rows",
        }
    },
    "torbrowser_usageinfo": {
        "name": "Tor Browser - Usage Info",
        "description": "Parses Tor Browser Usage Information",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}",
        "creation_date": "2025-11-14",
        "last_update_date": "2025-11-14",
        "requirements": "none",
        "category": "Tor Browser",
        "notes": "Reports three keys of fenix_preferences.xml: "
                 "pref_key_last_browse_activity_time, pref_key_times_app_opened and "
                 "pref_key_open_private_tabs_count. The first is read as Unix milliseconds and "
                 "shown in UTC, or as stored where it does not convert; no source for that unit "
                 "is cited here. The other two are reported as stored. Run on hc_pixel8pro_a16 "
                 "(version code 2016164570, 3 rows) and russell_pixel6a_a13 (version code "
                 "2015960779, 1 row).",
        "paths": ('*/org.torproject.torbrowser/shared_prefs/fenix_preferences.xml'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "info-circle",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | org.torproject.torbrowser vc 2016164570 | 3 rows",
            "russell_pixel6a_a13": "Android 13 | org.torproject.torbrowser vc 2015960779 | 1 row",
        }
    },
}

import os
import datetime
import re
from pathlib import Path
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, check_in_media, get_sqlite_db_records, logfunc
from scripts.artifacts.storagePathViews import unique_files

INVALID_XML_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
BARE_AMPERSAND = re.compile(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9A-Fa-f]+);)')


def _parse_xml(file_found):
    """Parse XML, recovering from invalid tokens / unescaped ampersands; empty element if unparseable."""
    try:
        return ET.parse(file_found).getroot()
    except ET.ParseError:
        with open(file_found, encoding='utf-8', errors='replace') as f:
            xml = BARE_AMPERSAND.sub('&amp;', INVALID_XML_CHARS.sub('', f.read()))
        try:
            return ET.fromstring(xml)
        except ET.ParseError as ex:
            logfunc(f'Skipping unparseable XML {file_found}: {ex}')
            return ET.Element('empty')


def _file_times(seeker, path):
    """(UTC seconds, reading with no zone) the input records for a staged file.

    The staged copy's own time is not used: for a FAT, exFAT or DOS-only zip reading it is
    that reading placed in the examiner's time zone.
    """
    infos = getattr(seeker, 'file_infos', None) or {}
    windows = str(path).replace('/', '\\')
    bare = windows.removeprefix('\\\\?\\')
    info = next((infos[name] for name in (str(path), windows, bare, '\\\\?\\' + bare)
                 if name in infos), None)
    times = getattr(info, 'times', None)
    for value in (getattr(times, 'modified', None), getattr(info, 'modification_date', None)):
        if isinstance(value, (int, float)) and value:
            return value, ''
    return None, getattr(times, 'modified_no_zone', None) or ''


@artifact_processor
def torbrowser_thumbnails(context):
    files_found = unique_files(context)
    data_list = []
    source_paths = set()

    for file_found in files_found:
        media_path = Path(file_found)

        if not media_path.is_file():
            continue
        if media_path.suffix.lower() != '.0':
            continue

        source_paths.add(str(file_found))
        filename = media_path.name
        location = context.get_relative_path(str(media_path.parent))

        modified_ts, no_zone = _file_times(context.get_seeker(), file_found)
        try:
            modifiedtime = (datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
                            + datetime.timedelta(seconds=int(modified_ts))
                            ).strftime('%Y-%m-%d %H:%M:%S') if modified_ts else ''
        except OverflowError:
            modifiedtime = ''

        media_item = check_in_media(filename)

        if media_item:
            data_list.append((modifiedtime, no_zone, media_item, filename, location))

    data_headers = (('File Modified', 'datetime'), 'Modified (no zone, as stored)', ('Thumbnail', 'media'), 'File Name', 'Location')

    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def torbrowser_bookmarks(context):
    files_found = unique_files(context)
    data_list = []
    source_path = ''
    for source_path in files_found:
        source_path = str(source_path)
        if source_path.endswith('.sqlite'):
            break

    query = '''
        SELECT
            child.id,
            CASE
                WHEN child.parent = 1 THEN 'PlacesRoot'
                ELSE parent.title
            END AS "Parent Container",
            CASE
                WHEN child.id = 1 THEN 'PlacesRoot'
                ELSE child.title
            END AS Title,
            moz_places.url AS URL,
            moz_places.description AS Description,
            DATETIME((child.dateAdded / 1000), 'unixepoch') AS 'Date Added (UTC)',
            DATETIME((child.lastModified / 1000), 'unixepoch') AS 'Date Last Modified (UTC)'
        FROM moz_bookmarks AS child
        LEFT JOIN moz_places ON child.fk = moz_places.id
        LEFT JOIN moz_bookmarks AS parent ON child.parent = parent.id
        WHERE child.type = 1;
        '''

    data_headers = ('Bookmark ID', 'Parent Folder', 'Title', 'URL', 'Description',
                    ('Date Added', 'datetime'), ('Last Modified', 'datetime'))
    data_list = list(get_sqlite_db_records(source_path, query))

    return data_headers, data_list, source_path


@artifact_processor
def torbrowser_usageinfo(context):
    files_found = unique_files(context)

    usage_keys = {
        "pref_key_last_browse_activity_time",
        "pref_key_times_app_opened",
        "pref_key_open_private_tabs_count"
    }

    data_list = []
    source_path = ""

    for fp in files_found:
        source_path = str(fp)
        if not source_path.lower().endswith(".xml"):
            continue
        if not os.path.isfile(source_path):
            continue

        root = _parse_xml(source_path)

        filename = Path(source_path).name
        path = context.get_relative_path(source_path)

        for elem in root.iter():
            key_name = elem.get("name")
            if key_name not in usage_keys:
                continue

            value_raw = elem.text.strip() if elem.text else elem.get("value", "").strip()

            value_out = value_raw
            if key_name == "pref_key_last_browse_activity_time":
                try:
                    ts = int(value_raw)
                    dt = datetime.datetime.fromtimestamp(ts / 1000.0, datetime.timezone.utc)
                    value_out = dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    pass

            data_list.append((key_name, value_out, filename, path))

    data_headers = ("Key", "Value", "File Name", "Path")

    return data_headers, data_list, source_path
