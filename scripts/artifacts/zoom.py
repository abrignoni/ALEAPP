__artifacts_v2__ = {
    "zoom_meeting_folders": {
        "name": "Zoom - Meeting Folders",
        "description": "Parses the per meeting folders the Zoom Android app created, whose "
                       "names carry the date, the time and the meeting title.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Zoom",
        "notes": "One row per meeting folder. The evidence here is the folder name, not its "
                 "contents: on the tested device all 21 folders were empty, and the app's own "
                 "databases are encrypted, so the names are the only record of these "
                 "meetings the extraction carries. A name is the date, the time and the "
                 "meeting title, and the date and time are reported separately from the "
                 "title. Meeting Date is reported as a date and Meeting Time as stored, "
                 "because the name records no time zone and nothing in the extraction "
                 "establishes which one the app used, so the values are not converted and "
                 "are not offered as a UTC datetime. Files In Folder counts the entries the "
                 "extraction holds inside the folder, which was zero on the tested device; a "
                 "folder can be present without a recording. A folder records that the app "
                 "created it for a meeting, which is not by itself proof that a recording "
                 "was made or that the account holder attended. Names that do not begin with "
                 "a date and a time are reported with the whole name in the title column "
                 "rather than being dropped. Field mapping was done against three private "
                 "samples provided by Mattia; no sample data is recorded for them.",
        "paths": (
            '*/us.zoom.videomeetings/data/Zoom/*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "video"
    },
    "zoom_account": {
        "name": "Zoom - Account and Encrypted Stores",
        "description": "Parses the Zoom account identifier the Android app records in its "
                       "own file and folder names, and counts the encrypted stores it holds.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-08-19",
        "requirements": "none",
        "category": "Zoom",
        "notes": "One row per app data directory. The account identifier is read from the "
                 "names the app gives its own per account folder and preference files, "
                 "because the stores themselves are encrypted; where no such name is present "
                 "the column is empty and the counts still report what the directory holds. "
                 "Encrypted Databases counts files whose name marks them as encrypted and "
                 "which do not begin with the SQLite magic, and Encrypted Preference Files "
                 "counts the preference files the app names with its encrypted prefix. "
                 "Neither is recoverable from a file system extraction: the preference files "
                 "are AndroidX EncryptedSharedPreferences, whose entry names and values are "
                 "both encrypted under a Tink keyset that is itself wrapped by an Android "
                 "Keystore key the extraction does not contain, and the app separately "
                 "records that it uses RSA for that wrapping. The counts are reported so an "
                 "examiner can see how much is present and unreadable rather than being left "
                 "to infer it from an empty report. Field mapping was done against three "
                 "private samples provided by Mattia; no sample data is recorded for them.",
        "paths": (
            '*/us.zoom.videomeetings/data/*',
            '*/us.zoom.videomeetings/shared_prefs/*.xml',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user"
    },
}

import os
import re

from scripts.artifacts.storagePathViews import canonical_path, unique_files
from scripts.ilapfuncs import artifact_processor

_PACKAGE = 'us.zoom.videomeetings'
# A folder name begins with the date and the time the app recorded for the meeting, then
# the title. The separators the app uses between the time parts are read from the name
# rather than assumed, because they are not the ones used in the date.
_FOLDER_NAME = re.compile(r'^(\d{4}-\d{2}-\d{2})[ T](\d{2}[.:]\d{2}[.:]\d{2})\s*(.*)$')
_ACCOUNT = re.compile(r'([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]*xmpp\.zoom\.us)')


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
    '''{container key: [(relative path, path)]} for the files this artifact matched.'''
    grouped = {}
    for file_found in unique_files(context):
        path = str(file_found)
        relative = str(context.get_relative_path(path)).replace('\\', '/')
        grouped.setdefault(_container(context, path), []).append((relative, path))
    return grouped


def _folder_of(relative):
    '''The meeting folder component of a path under the app's Zoom directory, or None.

    The declared pattern matches the folder itself and, because a pattern segment spans
    separators, anything beneath it as well. Taking the first component after the Zoom
    directory groups both onto one row rather than reporting a folder once per file.
    '''
    parts = relative.split('/')
    for position, part in enumerate(parts):
        if part == 'Zoom' and position + 1 < len(parts):
            return parts[position + 1]
    return None


@artifact_processor
def zoom_meeting_folders(context):
    data_list = []
    source_files = []

    for entries in _by_container(context).values():
        folders = {}
        for relative, _ in entries:
            name = _folder_of(relative)
            if not name:
                continue
            counted, _ = folders.get(name, (0, relative))
            # The folder's own entry is not a file inside it, so it is not counted.
            is_folder_itself = relative.rstrip('/').endswith('/' + name)
            folders[name] = (counted + (0 if is_folder_itself else 1), relative)

        for name, (count, relative) in folders.items():
            match = _FOLDER_NAME.match(name)
            if match:
                date, moment, title = match.group(1), match.group(2), match.group(3)
            else:
                date, moment, title = '', '', name
            source_files.append(relative)
            data_list.append((
                date,
                moment,
                title,
                count,
                name,
                relative,
            ))

    data_list.sort(key=lambda row: (str(row[0]), str(row[1]), str(row[4])), reverse=True)

    data_headers = (
        ('Meeting Date', 'date'),
        'Meeting Time (as stored)',
        'Meeting Title',
        'Files In Folder',
        'Folder Name',
        'Source Path',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def zoom_account(context):
    data_list = []
    source_files = []

    for entries in _by_container(context).values():
        account = ''
        encrypted_databases = 0
        encrypted_preferences = 0
        seen_databases = set()
        relative_paths = []

        for relative, path in entries:
            name = os.path.basename(relative)
            if not account:
                match = _ACCOUNT.search(relative)
                if match:
                    account = match.group(1)
            if name.startswith('enc_') and name.endswith('.xml'):
                encrypted_preferences += 1
                relative_paths.append(relative)
            elif '.enc' in name and name.endswith('.db') and relative not in seen_databases:
                # A store is counted as encrypted only when its bytes are not a SQLite
                # file, so a name that merely carries the marker is not assumed.
                try:
                    with open(path, 'rb') as handle:
                        magic = handle.read(16)
                except OSError:
                    magic = b''
                if magic and not magic.startswith(b'SQLite format 3\x00'):
                    encrypted_databases += 1
                    seen_databases.add(relative)
                    relative_paths.append(relative)

        if not account and not encrypted_databases and not encrypted_preferences:
            continue

        source_files.extend(relative_paths[:50])
        data_list.append((
            account,
            encrypted_databases,
            encrypted_preferences,
            '; '.join(sorted(relative_paths)[:5]),
        ))

    data_headers = (
        'Account Identifier',
        'Encrypted Databases',
        'Encrypted Preference Files',
        'Source Files',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))
