__artifacts_v2__ = {
    "zoom_meeting_folders": {
        "name": "Zoom - Meeting Folders",
        "description": "Parses the folders under the Zoom app's data/Zoom directory, whose "
                       "names begin with a date and a time followed by a title.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Zoom",
        "notes": "One row per distinct folder name under data/Zoom in an app container. "
                 "A leading date-shaped segment, time-shaped segment and remaining suffix are "
                 "reported as text under Folder Date Text, Folder Time Text and Folder Suffix. "
                 "Their event meaning and time zone are not established by the folder name. "
                 "Names that do not match the pattern are preserved in Folder Suffix. Files In "
                 "Folder counts matched entries below the folder. The private sample described "
                 "by the original contributor held 21 empty folders; no registered sample is "
                 "recorded for that observation. A folder is not by itself proof that a meeting "
                 "took place, that a recording was made or that the account holder attended. "
                 "Field mapping was done against three private samples provided by Mattia; "
                 "no sample data is recorded for them.",
        "paths": (
            '*/us.zoom.videomeetings/data/Zoom/*',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "video"
    },
    "zoom_account": {
        "name": "Zoom - Account and Encrypted Stores",
        "description": "Reports matching xmpp.zoom.us substrings from selected Zoom paths and the existing "
                       "store-marker counts per app data directory.",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-08-19",
        "last_update_date": "2026-10-07",
        "requirements": "none",
        "category": "Zoom",
        "notes": "One row per app data directory that holds an account name or at least one counted store."
                 " The First xmpp.zoom.us Path Match column preserves the existing first matching "
                 "substring from the selected paths. That substring alone does not establish an account "
                 "identity. The xmpp.zoom.us Path Matches (JSON) column retains the existing pattern's "
                 "non-overlapping finditer matches from every retained path, each paired with that "
                 "normalized evidence-relative path, in retained path encounter order and then "
                 "left-to-right match order. It is read from names because the stores themselves are "
                 "encrypted; where no such name is present the column is empty and the counts still report"
                 " what the directory holds. Encrypted Databases counts files whose name marks them as "
                 "encrypted and which do not begin with the SQLite magic, and Encrypted Preference Files "
                 "counts the preference files the app names with its encrypted prefix. Neither was "
                 "recoverable from the tested extractions. The preference files are named with an enc_ "
                 "prefix and were not readable on the tested extractions. Whether they follow AndroidX "
                 "EncryptedSharedPreferences, which the AndroidX reference describes as an implementation "
                 "of SharedPreferences that encrypts keys and values "
                 "(https://developer.android.com/reference/androidx/security/crypto/EncryptedSharedPreferences),"
                 " was not established here, and the module reads none of the key material. The counts are"
                 " reported so an examiner can see how much is present and unreadable rather than being "
                 "left to infer it from an empty report. Field mapping was done against three private "
                 "samples provided by Mattia; no sample data is recorded for them. The appended field is "
                 "compact JSON text containing an ordered list of objects with match and path string "
                 "members; repetitions within and across retained paths remain. An emitted "
                 "counted-store-only row with no matching name holds [] in this field. Existing canonical "
                 "alias selection can remove paths before matching; this field does not recover excluded "
                 "aliases or original path bytes. All four prior native values, row grain, marker/magic "
                 "counts, first-five sorted display and first-fifty encounter-order source cap are "
                 "unchanged. Account-only rows can still have empty Source Files and artifact source; "
                 "candidate paths in the JSON field provide their own scoped path association, without "
                 "changing that source policy. enc_ XML names and nonempty non-SQLite prefixes are the "
                 "existing count tests and do not independently prove encryption, unreadability or "
                 "completeness. Private-sample, AndroidX, library and name-derived identity assertions "
                 "above remain historical and unverified by this correction. Original contribution "
                 "credited to @AlexisBrignoni, @mattiaepi (Mattia Epifani) and Claude. No key material is "
                 "read or decrypted.",
        "paths": (
            '*/us.zoom.videomeetings/data/*',
            '*/us.zoom.videomeetings/shared_prefs/*.xml',
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user"
    },
}

import os
import json
import re

from scripts.artifacts.storagePathViews import canonical_path, unique_files
from scripts.ilapfuncs import artifact_processor

_PACKAGE = 'us.zoom.videomeetings'
# Split a date-shaped prefix, time-shaped prefix and suffix without asserting their event meaning. The separators the app uses between the time parts are read from the name
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
        'Folder Date Text (as stored)',
        'Folder Time Text (as stored)',
        'Folder Suffix (as stored)',
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
        path_matches = []
        encrypted_databases = 0
        encrypted_preferences = 0
        seen_databases = set()
        relative_paths = []

        for relative, path in entries:
            name = os.path.basename(relative)
            for candidate_match in _ACCOUNT.finditer(relative):
                path_matches.append({'match': candidate_match.group(1), 'path': relative})
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
            json.dumps(path_matches, ensure_ascii=True, separators=(',', ':')),
        ))

    data_headers = (
        'First xmpp.zoom.us Path Match',
        'Encrypted Databases',
        'Encrypted Preference Files',
        'Source Files',
        'xmpp.zoom.us Path Matches (JSON)',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))
