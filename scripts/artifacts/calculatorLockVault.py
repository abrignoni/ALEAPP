__artifacts_v2__ = {
    "calculatorvault_hidden_files": {
        "name": "Calculator Lock - Hidden Files",
        "description": "Rows from the Hide table of note_contact.db, each pairing a file name "
                       "held in the app's storage folder with a path string, matched where "
                       "possible to the file of that name on external storage",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Calculator Lock",
        "notes": "com.calculator.lock.hide.photo.video presents a working calculator and opens a "
                 "storage area when a stored passcode is entered. note_contact.db is a plaintext "
                 "SQLite database; no decryption is involved. Hide has two columns, hide_name and "
                 "hide_path. On the corpus below hide_name matched a file of the same name under "
                 "Pictures/.Calculator_Lock/Photos and hide_path held a path under "
                 "Download/Imgur. The bytes of the matched file were an unencrypted JPEG, so the "
                 "content is readable without the passcode; this was observed on one file in one "
                 "corpus and is not established for other versions or file types. The five "
                 "storage subfolders (Photos, Videos, Files, Intruder, Recycle_bin) are the "
                 "literals built in class c5.a of base.apk from the same extraction. The Vault "
                 "Path and File Modified Time columns are blank when no file of that name is "
                 "present in the extraction. A move within one volume can preserve a file's "
                 "modification time, so File Modified Time does not establish when the file "
                 "reached the storage folder.",
        "paths": (
            '*/com.calculator.lock.hide.photo.video/databases/note_contact.db*',
            '*/.Calculator_Lock/*',
        ),
        "output_types": "standard",
        "artifact_icon": "eye-off",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.calculator.lock.hide.photo.video | 1 row",
        },
    },
    "calculatorvault_storage_media": {
        "name": "Calculator Lock - Storage Folder Media",
        "description": "Files present under the .Calculator_Lock folder on external storage, with "
                       "the format detected from each file's own bytes, including files the Hide "
                       "table does not name",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Calculator Lock",
        "notes": "Every file found under a .Calculator_Lock folder gets a row, whether or not the "
                 "Hide table names it, so files present on storage without a database row are not "
                 "dropped. Detected Format comes from the leading bytes of each file, not from its "
                 "extension. The Intruder subfolder is one of the five names built in class c5.a "
                 "of base.apk; the app contains a TakePictureActivity and a TAKE_PICTURE "
                 "preference, which was false in the tested corpus. No Intruder file was present "
                 "in that corpus, so this artifact's handling of Intruder, Videos, Files and "
                 "Recycle_bin content is implemented but unexercised. A move within one volume can "
                 "preserve a file's modification time, so File Modified Time does not establish "
                 "when the file reached the storage folder.",
        "paths": (
            '*/.Calculator_Lock/*',
            '*/com.calculator.lock.hide.photo.video/databases/note_contact.db*',
        ),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.calculator.lock.hide.photo.video | 1 row",
        },
    },
    "calculatorvault_notes": {
        "name": "Calculator Lock - Notes",
        "description": "Rows from the Note table of note_contact.db, holding a title, a body and "
                       "a date string",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Calculator Lock",
        "notes": "note_date is stored as text, not as an epoch value. In base.apk from the same "
                 "extraction (version 1.94), apart from the CREATE TABLE statement in class a5.a, "
                 "the only methods whose bytecode names note_date are method x of class a5.a, "
                 "which reads the Note table, and method z of "
                 "com.calculator.lock.hide.photo.video.activity.AddNewNoteActivity. Decompiled "
                 "with jadx 1.5.6, method z formats the current date with a SimpleDateFormat of "
                 "dd-MM-yyyy and writes it to note_date both when it inserts a new Note row and "
                 "when it updates an existing one, so the value is the date of that method's "
                 "latest insert or update, not necessarily the date the note was created. The "
                 "APK's dex files hold 16 strings containing yyyy. dd-MM-yyyy and dd/MM/yyyy are "
                 "the only two with a numeric day and month and the year last, and both are day "
                 "first; the other 14 name the month or start with the year. MM-dd-yyyy and "
                 "MM/dd/yyyy occur in none of the APK's 900 files, read as ASCII or UTF-16. On the "
                 "corpus below the one row stores 04-02-2024, and Joshua Hickman's creation "
                 "document for that image records a note created in the app on 2024-02-04 and "
                 "lists no later action on it, which agrees with the day-first reading. "
                 "Reference: Joshua Hickman, 'Android 14 Image', "
                 "https://thebinaryhick.blog/wp-content/uploads/2024/09/Android14-ImageCreation.pdf, "
                 "page 5. The Note Date column restates that date as 00:00:00 UTC so the row can "
                 "sort and reach the timeline. The record carries no time and no zone, so that "
                 "time component is supplied by this parser and is not from the data; Note Date "
                 "(as stored) holds the original string.",
        "paths": ('*/com.calculator.lock.hide.photo.video/databases/note_contact.db*',),
        "output_types": "standard",
        "artifact_icon": "file-text",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.calculator.lock.hide.photo.video | 1 row",
        },
    },
    "calculatorvault_contacts": {
        "name": "Calculator Lock - Contacts",
        "description": "Rows from the Contact table of note_contact.db, holding a name and a "
                       "number string",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Calculator Lock",
        "notes": "The table has three columns, contact_id, contact_name and contact_number, and "
                 "carries no timestamp. It held no rows in the corpus below, so this artifact is "
                 "implemented but unexercised; an empty table is not evidence the feature was "
                 "unused. A corpus with rows in this table would close that gap.",
        "paths": ('*/com.calculator.lock.hide.photo.video/databases/note_contact.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.calculator.lock.hide.photo.video | 0 rows",
        },
    },
    "calculatorvault_files": {
        "name": "Calculator Lock - Files",
        "description": "Rows from the File table of note_contact.db, holding a title, two path "
                       "strings, a MIME type and a date string",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-09-28",
        "requirements": "none",
        "category": "Calculator Lock",
        "notes": "file_date is stored as text. The pattern dd-MM-yyyy is referenced by "
                 "com.calculator.lock.hide.photo.video.activity.home_activities.FileActivity in "
                 "base.apk from the same extraction. file_extend holds a MIME type, not an "
                 "extension. In that APK (version 1.94), apart from the CREATE TABLE statement, "
                 "only methods s and b of class a5.a name file_extend: s reads the File table, and "
                 "b, decompiled with jadx 1.5.6, writes the MIME type Android's MimeTypeMap "
                 "returns for the extension of file_path, or no value when none is found. The "
                 "MIME Type column reports it as stored. The File Date column restates that date as "
                 "00:00:00 UTC; the record carries no time and no zone, so that time component is "
                 "supplied by this parser. The table held no rows in the corpus below, so this "
                 "artifact is implemented but unexercised, and the meaning of file_path against "
                 "file_org_path is taken from the column names alone and is not otherwise "
                 "established.",
        "paths": ('*/com.calculator.lock.hide.photo.video/databases/note_contact.db*',),
        "output_types": "standard",
        "artifact_icon": "file",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.calculator.lock.hide.photo.video | 0 rows",
        },
    },
    "calculatorvault_deleted_data": {
        "name": "Calculator Lock - Deleted Data",
        "description": "Rows from the Delete_Data table of note_contact.db, pairing a name with a "
                       "date string",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Calculator Lock",
        "notes": "The table has two columns, delete_name and delete_date. The pattern dd/MM/yyyy "
                 "is referenced by "
                 "com.calculator.lock.hide.photo.video.activity.home_activities.RecycleBinActivity "
                 "in base.apk from the same extraction, and Recycle_bin is one of the five storage "
                 "subfolder names built in class c5.a. What the app writes here, and whether a row "
                 "corresponds to a file still present under Recycle_bin, was not established. The "
                 "table held no rows in the corpus below, so this artifact is implemented but "
                 "unexercised.",
        "paths": ('*/com.calculator.lock.hide.photo.video/databases/note_contact.db*',),
        "output_types": "standard",
        "artifact_icon": "trash-2",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.calculator.lock.hide.photo.video | 0 rows",
        },
    },
    "calculatorvault_browser_history": {
        "name": "Calculator Lock - Browser History",
        "description": "Rows from the History table of note_contact.db, whose columns are named "
                       "for a name, a URL, an image and a date",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Calculator Lock",
        "notes": "base.apk from the same extraction (version 1.94) contains a BrowserActivity and "
                 "a RoboWebView under the package's webview namespace, but its dex files name the "
                 "History table and its columns only inside the CREATE TABLE and DROP TABLE "
                 "statements of class a5.a, which opens note_contact.db, so no code that writes "
                 "this table was found in that version, and the Browser History name rests on the "
                 "column names alone. With no writer found, the format of history_date is not "
                 "established. The History Date column is parsed with dd-MM-yyyy and dd/MM/yyyy, "
                 "the only two of the 16 strings containing yyyy in those dex files that have a "
                 "numeric day and month and the year last; both are day first. A value in any "
                 "other form is left unparsed and appears only in History Date (as stored). The "
                 "History table held no rows in the corpus below, so this artifact is implemented "
                 "but unexercised. A separate HISTORY.DB, which class d5.e fills with "
                 "calculator_name and expression rows, is a different file: none was in the "
                 "corpus below, and this module does not read it.",
        "paths": ('*/com.calculator.lock.hide.photo.video/databases/note_contact.db*',),
        "output_types": "standard",
        "artifact_icon": "globe",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.calculator.lock.hide.photo.video | 0 rows",
        },
    },
    "calculatorvault_preferences": {
        "name": "Calculator Lock - Preferences",
        "description": "Preference names and values from the app's shared_prefs file, including "
                       "the PASSWORD entry, which the tested version stores in plain text",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-09-28",
        "requirements": "none",
        "category": "Calculator Lock",
        "notes": "Every entry in com.calculator.lock.hide.photo.video_preferences.xml gets a row, "
                 "so entries added by later versions still appear. The Observed Use column is "
                 "filled for PASSWORD and TAKE_PICTURE, naming every class of base.apk from the "
                 "same extraction (version 1.94) whose bytecode names that preference and, from "
                 "the jadx 1.5.6 decompilation, whether it reads or writes it; l4.b and m4.i are "
                 "obfuscated names from that build. The column is blank for the other names, and "
                 "a blank is not a finding that no class reads them. The PASSWORD entry held a "
                 "plain text value in the corpus below, which is a finding about how the app "
                 "stores that value on that version, not about any other version. Entries "
                 "beginning IABTCF_ follow the IAB Transparency and Consent Framework key naming "
                 "and are not part of the app's own storage feature: of the three in the corpus "
                 "below, base.apk names only IABTCF_gdprApplies, and only in classes under "
                 "com.google.android.gms.",
        "paths": ('*/com.calculator.lock.hide.photo.video/shared_prefs/'
                  'com.calculator.lock.hide.photo.video_preferences.xml',),
        "output_types": "standard",
        "artifact_icon": "key",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.calculator.lock.hide.photo.video | 10 rows",
        },
    },
    "calculatorvault_calculator_history": {
        "name": "Calculator Lock - Calculator History",
        "description": "Rows from the history table of HISTORY.DB, each a calculator entry and the "
                       "result the app computed for it",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-28",
        "last_update_date": "2026-09-28",
        "requirements": "none",
        "category": "Calculator Lock",
        "notes": "HISTORY.DB is a separate database the app keeps beside note_contact.db. Known "
                 "data made on 2026-09-28 with this app, version 1.94, on an Android 15 emulator "
                 "showed the following. The file did not exist until the first entry was saved. "
                 "Two wrong passcodes, a sum and a multiplication, each finished with =, saved "
                 "one row each. The correct passcode, 11223344 (the reset code the app's own "
                 "intro screen names) and an entry ending in an operator, which the calculator "
                 "showed as 0.0, saved nothing. Rows were saved from the calculator the app "
                 "opens on (CalculatorActivity) and from the calculator overlay of the screens "
                 "built on the obfuscated class l4.b, shown when the app was reopened from "
                 "Recents. The decompiled code shows a third screen, "
                 "LockScreenCalculatorActivity, saving the same way; no code in 1.94 starts it "
                 "by class and it was not reached in the test. Each row holds the entry and the "
                 "result the app computed, written as entry = result with the result as a "
                 "decimal (19.0) and the multiplication key saved as *. Entry and Result split "
                 "that text at the first ' = ', and Expression (as stored) keeps it whole. "
                 "calculator_name held STANDARD on every row, the constant the app writes, and "
                 "is not reported. Rows carry no time of their own. Row ID followed the order "
                 "the entries were saved, and in the test the file's own modification time "
                 "moved only when a row was saved, so there it marked the latest saved entry, "
                 "not every row. A row does not establish who typed the entry or whether it was "
                 "meant as a passcode; compare Entry with the PASSWORD value in Calculator Lock "
                 "- Preferences. In 1.94 no code reads these rows back or deletes them "
                 "(decompiled with jadx 1.5.6 and checked against the dex bytecode). Android "
                 "User names the user whose app folder holds the file when the table holds rows "
                 "from more than one user, and is blank otherwise, as in the test. Of the 42 "
                 "registered Android corpora that could be searched, only pixel7a_a14 carries "
                 "the app, and it holds no HISTORY.DB.",
        "paths": ('*/com.calculator.lock.hide.photo.video/databases/HISTORY.DB*',),
        "output_types": "standard",
        "artifact_icon": "hash",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.calculator.lock.hide.photo.video | 0 rows",
        },
    },
}

import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    convert_unix_ts_to_utc,
    get_file_path,
    get_sqlite_db_records,
    logfunc,
)

# Storage subfolder names built in class c5.a of base.apk. Used to label a file by the
# folder it sits in rather than to assert what the app does with each folder.
STORAGE_FOLDERS = ('Photos', 'Videos', 'Files', 'Intruder', 'Recycle_bin')

# dd-MM-yyyy and dd/MM/yyyy: of the 16 strings containing yyyy in the dex files of base.apk
# (version 1.94), the only two with a numeric day and month and the year last. Both are day
# first, so a value parses the same way whichever one wrote it.
DATE_FORMATS = ('%d-%m-%Y', '%d/%m/%Y')

PREFERENCE_HEADERS = (
    'Preference',
    'Value',
    'Stored Type',
    'Observed Use',
)

# For each name, every class of base.apk (version 1.94) whose bytecode names it, found by
# scanning the dex bytecode for the string, with reads and writes told apart in the jadx
# 1.5.6 decompilation; l4.b and m4.i are obfuscated app classes. Names not listed here are
# reported without a use, rather than guessed at.
PREFERENCE_USE = {
    'PASSWORD': 'Read and written by CalculatorActivity, LockScreenCalculatorActivity, '
                'ChangePassword and the obfuscated app class l4.b, and read by the obfuscated '
                'app class m4.i (from app code)',
    'TAKE_PICTURE': 'Written by SettingActivity and read by SettingActivity, CalculatorActivity, '
                    'LockScreenCalculatorActivity and the obfuscated app class l4.b; the app '
                    'also contains a TakePictureActivity and an Intruder storage subfolder '
                    '(from app code)',
}

# The Android user whose app folder holds a file: data/data is user 0, and data/user/N and
# data_mirror/data_ce/<volume>/N are user N. Anchored on the package's own folder.
APP_FOLDER_USER = (
    re.compile(r'(?:^|/)data/data/com\.calculator\.lock\.hide\.photo\.video/'),
    re.compile(r'(?:^|/)data/user/(\d+)/com\.calculator\.lock\.hide\.photo\.video/'),
    re.compile(r'(?:^|/)data_mirror/data_ce/[^/]+/(\d+)/com\.calculator\.lock\.hide\.photo\.video/'),
)

# Leading-byte signatures, checked because a file name in this storage folder is not
# evidence of the file's type.
SIGNATURES = (
    (b'\xff\xd8\xff', 'JPEG', 'image/jpeg', 'jpg'),
    (b'\x89PNG\r\n\x1a\n', 'PNG', 'image/png', 'png'),
    (b'GIF87a', 'GIF', 'image/gif', 'gif'),
    (b'GIF89a', 'GIF', 'image/gif', 'gif'),
    (b'BM', 'BMP', 'image/bmp', 'bmp'),
    (b'%PDF', 'PDF', 'application/pdf', 'pdf'),
    (b'OggS', 'OGG', 'audio/ogg', 'ogg'),
    (b'fLaC', 'FLAC', 'audio/flac', 'flac'),
    (b'\x1aE\xdf\xa3', 'Matroska or WebM', 'video/webm', 'webm'),
    (b'\x00\x00\x01\xba', 'MPEG program stream', 'video/mpeg', 'mpg'),
    (b'\x00\x00\x01\xb3', 'MPEG video', 'video/mpeg', 'mpg'),
    (b'ID3', 'MP3', 'audio/mpeg', 'mp3'),
    (b'\xff\xfb', 'MP3', 'audio/mpeg', 'mp3'),
    (b'PK\x03\x04', 'ZIP container', 'application/zip', 'zip'),
    (b'\xd0\xcf\x11\xe0', 'OLE compound file', 'application/x-ole-storage', ''),
)


def _sniff(head):
    """Return (label, mime, extension) read from a file's leading bytes."""
    for magic, label, mime, extension in SIGNATURES:
        if head.startswith(magic):
            return label, mime, extension
    if head[4:8] == b'ftyp':
        brand = head[8:12]
        if brand.startswith(b'qt'):
            return 'QuickTime', 'video/quicktime', 'mov'
        if brand[:3] in (b'hei', b'mif', b'msf'):
            return 'HEIF', 'image/heic', 'heic'
        if brand[:3] == b'3gp':
            return '3GP', 'video/3gpp', '3gp'
        return 'MP4', 'video/mp4', 'mp4'
    if head[:4] == b'RIFF':
        if head[8:12] == b'WEBP':
            return 'WebP', 'image/webp', 'webp'
        if head[8:12] == b'AVI ':
            return 'AVI', 'video/x-msvideo', 'avi'
        if head[8:12] == b'WAVE':
            return 'WAV', 'audio/wav', 'wav'
        return 'RIFF container', '', ''
    return '', '', ''


def _read_head(path, length=32):
    try:
        with open(path, 'rb') as handle:
            return handle.read(length)
    except OSError as error:
        logfunc(f'Calculator Lock: could not read {path}: {error}')
        return b''


def _app_date(value):
    """Restate a day-first text date as midnight UTC, or return '' when it does not parse.

    The stored value carries no time and no zone. The time component below is supplied
    here so the row sorts and reaches the timeline; it is not from the record.
    """
    if not value:
        return ''
    text = str(value).strip()
    for date_format in DATE_FORMATS:
        try:
            parsed = datetime.strptime(text, date_format)
        except ValueError:
            continue
        return parsed.replace(tzinfo=timezone.utc)
    return ''


def _storage_folder(path):
    """Name the .Calculator_Lock subfolder a file sits in, or '' when it is not one."""
    parent = os.path.basename(os.path.dirname(str(path)))
    return parent if parent in STORAGE_FOLDERS else ''


def _file_times(seeker, path):
    """Return the extraction's recorded (creation, modification) times for a file."""
    info = seeker.file_infos.get(path) if seeker else None
    if info:
        return convert_unix_ts_to_utc(info.creation_date) or '', \
            convert_unix_ts_to_utc(info.modification_date) or ''
    try:
        return '', convert_unix_ts_to_utc(int(os.path.getmtime(path)))
    except OSError:
        return '', ''


def _storage_files(files_found):
    """Index the files under any .Calculator_Lock folder by their file name."""
    by_name = {}
    for file_found in files_found:
        path = str(file_found)
        if '.Calculator_Lock' not in path or not os.path.isfile(path):
            continue
        by_name.setdefault(os.path.basename(path), path)
    return by_name


def _database(files_found):
    return get_file_path(files_found, 'note_contact.db')


def _table_exists(db_path, table):
    # get_sqlite_db_records hands back a cursor, so the rows have to be pulled out of it.
    rows = list(get_sqlite_db_records(
        db_path,
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'",
    ))
    return len(rows) > 0


def _query(db_path, table, query):
    """Run a query only when its table is present, so other schemas stay quiet."""
    if not db_path or not _table_exists(db_path, table):
        return []
    return get_sqlite_db_records(db_path, query)


@artifact_processor
def calculatorvault_hidden_files(context):
    files_found = context.get_files_found()
    db_path = _database(files_found)
    on_storage = _storage_files(files_found)
    seeker = context.get_seeker()
    data_list = []

    query = 'SELECT hide_name, hide_path FROM Hide ORDER BY hide_name'
    for hide_name, hide_path in _query(db_path, 'Hide', query):
        located = on_storage.get(hide_name or '')
        modified = ''
        media = ''
        detected = ''
        size = ''
        storage_path = ''
        if located:
            _, modified = _file_times(seeker, located)
            label, mime, extension = _sniff(_read_head(located))
            detected = label
            size = os.path.getsize(located)
            storage_path = context.get_relative_path(located)
            media = check_in_media(located, hide_name,
                                   force_type=mime or None,
                                   force_extension=extension or None) or ''

        data_list.append((
            modified,
            media,
            hide_name or '',
            hide_path or '',
            os.path.basename(hide_path or ''),
            _storage_folder(located) if located else '',
            detected,
            size,
            storage_path,
            'Yes' if located else 'No',
        ))

    data_headers = (
        ('File Modified Time', 'datetime'),
        ('Hidden File', 'media'),
        'Hidden File Name',
        'Recorded Path',
        'Recorded File Name',
        'Storage Subfolder',
        'Detected Format',
        'File Size (bytes)',
        'Storage Path',
        'File Located In Extraction',
    )
    return data_headers, data_list, db_path or ''


@artifact_processor
def calculatorvault_storage_media(context):
    files_found = context.get_files_found()
    db_path = _database(files_found)
    seeker = context.get_seeker()
    data_list = []
    source_path = ''

    recorded = {}
    query = 'SELECT hide_name, hide_path FROM Hide'
    for hide_name, hide_path in _query(db_path, 'Hide', query):
        recorded[hide_name or ''] = hide_path or ''

    for name, path in sorted(_storage_files(files_found).items()):
        source_path = source_path or os.path.dirname(path)
        _, modified = _file_times(seeker, path)
        label, mime, extension = _sniff(_read_head(path))
        media = check_in_media(path, name,
                               force_type=mime or None,
                               force_extension=extension or None) or ''
        data_list.append((
            modified,
            media,
            name,
            _storage_folder(path),
            label,
            os.path.getsize(path),
            recorded.get(name, ''),
            'Yes' if name in recorded else 'No',
            context.get_relative_path(path),
        ))

    data_headers = (
        ('File Modified Time', 'datetime'),
        ('File', 'media'),
        'File Name',
        'Storage Subfolder',
        'Detected Format',
        'File Size (bytes)',
        'Recorded Path From Hide Table',
        'Named In Hide Table',
        'Storage Path',
    )
    return data_headers, data_list, source_path


@artifact_processor
def calculatorvault_notes(context):
    db_path = _database(context.get_files_found())
    data_list = []

    query = '''
    SELECT note_date, note_title, note_data, note_id
    FROM Note
    ORDER BY note_id
    '''
    for note_date, title, body, note_id in _query(db_path, 'Note', query):
        data_list.append((_app_date(note_date), note_date or '', title or '', body or '', note_id))

    data_headers = (
        ('Note Date', 'datetime'),
        'Note Date (as stored)',
        'Title',
        'Note',
        'Note ID',
    )
    return data_headers, data_list, db_path or ''


@artifact_processor
def calculatorvault_contacts(context):
    db_path = _database(context.get_files_found())
    data_list = []

    query = '''
    SELECT contact_name, contact_number, contact_id
    FROM Contact
    ORDER BY contact_id
    '''
    for name, number, contact_id in _query(db_path, 'Contact', query):
        data_list.append((name or '', number or '', contact_id))

    data_headers = (
        'Contact Name',
        'Contact Number',
        'Contact ID',
    )
    return data_headers, data_list, db_path or ''


@artifact_processor
def calculatorvault_files(context):
    db_path = _database(context.get_files_found())
    data_list = []

    query = '''
    SELECT file_date, file_title, file_path, file_org_path, file_extend, file_id
    FROM File
    ORDER BY file_id
    '''
    for file_date, title, path, org_path, extend, file_id in _query(db_path, 'File', query):
        data_list.append((
            _app_date(file_date), file_date or '', title or '', path or '',
            org_path or '', extend or '', file_id,
        ))

    data_headers = (
        ('File Date', 'datetime'),
        'File Date (as stored)',
        'Title',
        'Recorded Path',
        'Recorded Original Path',
        'MIME Type',
        'File ID',
    )
    return data_headers, data_list, db_path or ''


@artifact_processor
def calculatorvault_deleted_data(context):
    db_path = _database(context.get_files_found())
    data_list = []

    query = 'SELECT delete_date, delete_name FROM Delete_Data ORDER BY delete_name'
    for delete_date, delete_name in _query(db_path, 'Delete_Data', query):
        data_list.append((_app_date(delete_date), delete_date or '', delete_name or ''))

    data_headers = (
        ('Delete Date', 'datetime'),
        'Delete Date (as stored)',
        'Name',
    )
    return data_headers, data_list, db_path or ''


@artifact_processor
def calculatorvault_browser_history(context):
    db_path = _database(context.get_files_found())
    data_list = []

    query = '''
    SELECT history_date, history_name, history_url, history_image, history_id
    FROM History
    ORDER BY history_id
    '''
    for history_date, name, url, image, history_id in _query(db_path, 'History', query):
        data_list.append((
            _app_date(history_date), history_date or '', name or '', url or '',
            image or '', history_id,
        ))

    data_headers = (
        ('History Date', 'datetime'),
        'History Date (as stored)',
        'Name',
        'URL',
        'Image',
        'History ID',
    )
    return data_headers, data_list, db_path or ''


@artifact_processor
def calculatorvault_preferences(context):
    prefs_path = get_file_path(context.get_files_found(),
                               'com.calculator.lock.hide.photo.video_preferences.xml')
    data_list = []
    if not prefs_path:
        return PREFERENCE_HEADERS, data_list, ''

    try:
        root = ET.parse(prefs_path).getroot()
    except (OSError, ET.ParseError) as error:
        logfunc(f'Calculator Lock: could not parse {prefs_path}: {error}')
        return PREFERENCE_HEADERS, data_list, prefs_path

    for entry in root:
        name = entry.get('name', '')
        if entry.tag == 'set':
            value = ', '.join((child.text or '') for child in entry)
        elif entry.tag == 'string':
            value = entry.text or ''
        else:
            value = entry.get('value', '')
        data_list.append((name, value, entry.tag, PREFERENCE_USE.get(name, '')))

    data_list.sort(key=lambda row: row[0])
    return PREFERENCE_HEADERS, data_list, prefs_path


def _android_user(relative_path):
    """The Android user whose app folder holds a file, or '' when the path shows none."""
    path = str(relative_path).replace('\\', '/')
    for pattern in APP_FOLDER_USER:
        match = pattern.search(path)
        if match:
            return match.group(1) if pattern.groups else '0'
    return ''


@artifact_processor
def calculatorvault_calculator_history(context):
    data_list = []
    source_paths = []
    for file_found in unique_files(context):
        path = str(file_found)
        if os.path.basename(path) != 'HISTORY.DB' or not os.path.isfile(path):
            continue
        source_paths.append(path)
        user = _android_user(context.get_relative_path(path))
        query = 'SELECT rowid, expression FROM history ORDER BY rowid'
        for row_id, expression in _query(path, 'history', query):
            text = expression or ''
            entry, separator, result = text.partition(' = ')
            if not separator:
                entry, result = text, ''
            data_list.append((row_id, entry, result, text, user))

    # One user's rows would repeat one value on every row, so the column is kept blank then.
    if len({row[-1] for row in data_list}) < 2:
        data_list = [row[:-1] + ('',) for row in data_list]

    data_headers = (
        'Row ID',
        'Entry',
        'Result',
        'Expression (as stored)',
        'Android User',
    )
    return data_headers, data_list, '\n'.join(source_paths)
