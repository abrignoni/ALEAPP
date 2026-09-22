__artifacts_v2__ = {
    "xodo_recent_documents": {
        "name": "Xodo PDF Recent Documents",
        "description": "Documents Xodo recorded having open, with the page it was left on",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Xodo PDF",
        "sample_data": {
            "emu_a15_oss_v16": "Xodo PDF 11.0.1 | 1 row",
        },
        "notes": "One row per entry of the prefs_pdfviewctrl_tab_manager value in "
                 "com.xodo.pdf.reader/shared_prefs/com.xodo.pdf.reader_preferences.xml, which "
                 "the app writes as a JSON object keyed by the document's full path. The app's "
                 "four SQLite databases were all empty on the tested image, so the preferences "
                 "file is where this lives. "
                 "Last Viewed is the entry's tabLastViewedTimestamp and is stored as a local "
                 "time string with no zone, so it is reported exactly as stored rather than "
                 "converted; on the tested device 02:25:17.144 was 06:25 UTC, four hours ahead, "
                 "and treating it as UTC would move the reading by that offset. "
                 "Last Page is the page the document was left on and is the app's own value, "
                 "which was 1 on the tested image for a one page document. Zoom and Page "
                 "Presentation Mode are reported as stored. Document Path is the key of the "
                 "entry, so it is the path as the app recorded it rather than a path resolved in "
                 "the extraction; the file may no longer be present. "
                 "A row is evidence the app had the document open, not that anyone read it. The "
                 "app keeps no count of openings, which was measured rather than assumed: "
                 "opening the same document a second time moved Last Viewed from 02:51:21.703 "
                 "to 09:59:14.308 and added no field, the entry carrying fourteen members and "
                 "none of them a counter. So a row dates the last view and says nothing about "
                 "how many there were. "
                 "The same preferences file also holds prefs_recent_files_N entries, one JSON "
                 "object per recent file, and prefs_favorite_files_refs; those repeat the path "
                 "this artifact already reports without adding a time, so they are not parsed. "
                 "files/recently_used_cache/record.trn holds the same paths in a flattened form "
                 "and is likewise not parsed.",
        "paths": ('*/com.xodo.pdf.reader/shared_prefs/com.xodo.pdf.reader_preferences.xml',),
        "output_types": "standard",
        "artifact_icon": "file-text",
    },
}

import json
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.artifacts.storagePathViews import unique_files

PREFS_SUFFIX = 'com.xodo.pdf.reader/shared_prefs/com.xodo.pdf.reader_preferences.xml'
TAB_MANAGER_KEY = 'prefs_pdfviewctrl_tab_manager'


def _prefs_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(PREFS_SUFFIX)]


def _tab_manager(path):
    """The tab manager JSON object, or {} when the file or the value will not read."""
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as error:
        logfunc(f'Xodo: could not read {path}: {error}')
        return {}
    for node in root.findall('string'):
        if node.get('name') != TAB_MANAGER_KEY:
            continue
        try:
            parsed = json.loads(node.text or '')
        except (TypeError, ValueError) as error:
            logfunc(f'Xodo: {TAB_MANAGER_KEY} did not parse as JSON: {error}')
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


@artifact_processor
def xodo_recent_documents(context):
    data_list = []
    sources = []
    for path in _prefs_files(context):
        entries = _tab_manager(path)
        for document, entry in entries.items():
            if not isinstance(entry, dict):
                continue
            data_list.append((
                entry.get('tabLastViewedTimestamp') or '',
                entry.get('tabTitle') or '',
                document,
                entry.get('fileExtension') or '',
                entry.get('lastPage'),
                entry.get('zoom'),
                entry.get('pagePresentationMode'),
                context.get_relative_path(path)))
        if entries and path not in sources:
            sources.append(path)

    data_list.sort(key=lambda row: row[0], reverse=True)
    data_headers = (
        'Last Viewed (device local, as stored)', 'Title', 'Document Path', 'Extension',
        'Last Page', 'Zoom', 'Page Presentation Mode (as stored)', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
