__artifacts_v2__ = {
    "session_account": {
        "name": "Session - Account",
        "description": (
            "Parses account and profile keys from the Session messenger shared preferences file "
            "network.loki.messenger_preferences.xml, including pref_local_number (the Session "
            "Account ID), pref_profile_name, the profile avatar keys and the profile timestamps."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Session Messenger",
        "notes": (
            "Session (network.loki.messenger) is derived from Signal for Android. This artifact reports "
            "plaintext values from the app's shared preferences file only. "
            "SCOPE BOUNDARY: message content is not parsed. The message store databases/signal_v4.db and "
            "the config store databases/session.db are SQLCipher-encrypted; neither carried a SQLite file "
            "header in the tested images. Their passphrase is held in pref_database_encrypted_secret as an "
            "AES-GCM wrapped blob whose unwrapping key is the Android Keystore alias SignalSecret. On the "
            "hardware-backed keystores in these images that key is not exportable, so decryption was "
            "attempted and did not succeed. A published method that recovers the key from 16 bytes at "
            "offset 0x0D of the keystore blob applies to a virtualised device with no hardware keystore. "
            "Reference: Josh Hickman, 'Session on Android: An App Wrapped in Signal', "
            "https://thebinaryhick.blog/2022/07/14/session-on-android-an-app-wrapped-in-signal/ "
            "SESSION ACCOUNT ID: pref_local_number held a 66-character hexadecimal string in the four "
            "tested images, matching the form of the identifier Session documents as the Account ID (its "
            "published example 056c3d9682f167135d4c86b0af24e7aca98949380fa825e01455e788fe3df1d05c has the "
            "same length and 05 prefix). Reference: Session, 'Account IDs and self managed keys', "
            "https://docs.getsession.org/session-network/session-protocol/account-ids-and-self-managed-keys "
            "OPTIONAL KEYS: Session writes a preference key only once it has a value to store, so a blank "
            "column means the key was absent from the file, not that a feature was unused. Of the four "
            "tested images, pref_profile_avatar_url and last_profile_picture_upload were present in two, "
            "pref_last_profile_update_time in two and has_viewed_seed in three (true in two, false in one). "
            "Has Viewed Seed reports the stored boolean as written by the app; this artifact does not "
            "interpret it beyond that. Timestamp keys hold epoch milliseconds; a stored 0 is reported as "
            "blank rather than as 1970."
        ),
        "paths": ('*/network.loki.messenger/shared_prefs/network.loki.messenger_preferences.xml',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "anne_a15": "Android 15 | network.loki.messenger vc 417 | 1 row",
            "kevin_pocox7_a15": "Android 15 | network.loki.messenger vc 419 | 1 row",
            "pixel7a_a14": "Android 14 | network.loki.messenger vc 376 | 1 row",
            "sharon_a14": "Android 14 | network.loki.messenger vc 372 | 1 row",
        },
    },
    "session_preferences": {
        "name": "Session - Preferences",
        "description": (
            "Parses the key/value pairs stored in the Session messenger shared preferences file "
            "network.loki.messenger_preferences.xml, reporting the key name, its declared XML type "
            "and its stored value."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Session Messenger",
        "notes": (
            "A per-key view of the same file parsed by the Session - Account artifact, so the account keys "
            "appear in both. Values are reported as stored; this artifact assigns no meaning to a key "
            "beyond its name. "
            "The 'Value as UTC' column is a convenience conversion, not a statement that a key holds a "
            "timestamp: it is populated only where the XML type is 'long' and the stored number falls "
            "between 1e12 and 4e12, the range an epoch-millisecond value in this era occupies. Read it as "
            "'this number, if it were epoch milliseconds, would be that instant'. Keys outside that range, "
            "including a stored 0, are left blank. "
            "Values are HTML-escaped inside the XML and are unescaped on parse, so the JSON in the "
            "pref_*_encrypted_secret keys is reported in its original form. Those keys hold the wrapped "
            "database, attachment and log passphrases; they are reported because they are plaintext in the "
            "file and are the input to any future decryption, not because this artifact decrypts anything. "
            "See the Session - Account notes for the encryption scope boundary."
        ),
        "paths": ('*/network.loki.messenger/shared_prefs/network.loki.messenger_preferences.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "settings",
        "sample_data": {
            "anne_a15": "Android 15 | network.loki.messenger vc 417 | 22 rows",
            "kevin_pocox7_a15": "Android 15 | network.loki.messenger vc 419 | 33 rows",
            "pixel7a_a14": "Android 14 | network.loki.messenger vc 376 | 30 rows",
            "sharon_a14": "Android 14 | network.loki.messenger vc 372 | 19 rows",
        },
    },
    "session_attachments": {
        "name": "Session - Attachment Files",
        "description": (
            "Lists the files present in the Session messenger app_parts directory, reporting file "
            "name, size in bytes and path. File content is not decoded."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Session Messenger",
        "notes": (
            "A directory listing, not a media artifact. The content of these files is not recovered and no "
            "thumbnail is produced. In the tested images the files carried no recognisable file-format "
            "signature in their first 16 bytes, and the app stores an attachment passphrase in "
            "pref_attachment_encrypted_secret; that passphrase is wrapped by a hardware-backed key that "
            "was not exportable from these images. See the Session - Account notes. "
            "The .mms extension here follows the Signal for Android storage layout Session inherits and is "
            "not by itself an indication of MMS. The app_parts directory name is shared with "
            "com.android.providers.telephony and org.thoughtcrime.securesms, which use it for their own "
            "files; the path pattern is anchored on the network.loki.messenger package directory so only "
            "Session's copy is reported. "
            "No timestamp is reported: the on-disk times available here come from the extraction rather "
            "than from the device. Filenames were observed to embed no timestamp. "
            "A row count of zero means the directory held no files in that image, which is not evidence "
            "that attachments were absent from the account."
        ),
        "paths": ('*/network.loki.messenger/app_parts/*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "paperclip",
        "sample_data": {
            "anne_a15": "Android 15 | network.loki.messenger vc 417 | 2 rows",
            "kevin_pocox7_a15": "Android 15 | network.loki.messenger vc 419 | 6 rows",
            "pixel7a_a14": "Android 14 | network.loki.messenger vc 376 | 3 rows",
            "sharon_a14": "Android 14 | network.loki.messenger vc 372 | 0 rows",
        },
    },
}

import os
import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, logfunc


INVALID_XML_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
BARE_AMPERSAND = re.compile(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9A-Fa-f]+);)')

# Bounds for reading a stored number as epoch milliseconds: 2001-09-09 to 2096-10-02.
# Wide enough to cover any value this app could have written, narrow enough that the
# app's small integers (version codes, registration ids, avatar ids) fall outside it.
EPOCH_MS_MIN = 1_000_000_000_000
EPOCH_MS_MAX = 4_000_000_000_000


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


def _read_prefs(root):
    """Return {key: (xml_type, value)} for the children of a shared_prefs <map>."""
    prefs = {}
    for item in root:
        key = item.attrib.get('name')
        if not key:
            continue
        if 'value' in item.attrib:            # boolean, int, long, float
            value = item.attrib['value']
        elif len(item):                       # set: one <string> child per member
            value = ', '.join((child.text or '') for child in item)
        else:                                 # string
            value = item.text or ''
        prefs[key] = (item.tag, value)
    return prefs


def _value(prefs, key):
    """Stored value for key, or '' when the key is absent."""
    entry = prefs.get(key)
    return entry[1] if entry else ''


def _ms_to_utc(raw):
    """Epoch-milliseconds string to a UTC datetime; '' for absent, zero or non-numeric."""
    try:
        ms = int(raw)
    except (TypeError, ValueError):
        return ''
    if ms <= 0:
        return ''
    return convert_unix_ts_to_utc(ms)


@artifact_processor
def session_account(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    sources = []

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('network.loki.messenger_preferences.xml'):
            continue
        sources.append(file_found)
        prefs = _read_prefs(_parse_xml(file_found))
        if not prefs:
            continue

        data_list.append((
            _ms_to_utc(_value(prefs, 'pref_last_profile_update_time')),
            _ms_to_utc(_value(prefs, 'last_profile_picture_upload')),
            _value(prefs, 'pref_local_number'),
            _value(prefs, 'pref_profile_name'),
            _value(prefs, 'pref_profile_avatar_url'),
            _value(prefs, 'pref_profile_avatar_id'),
            _value(prefs, 'pref_profile_key'),
            _value(prefs, 'pref_local_registration_id'),
            _value(prefs, 'has_viewed_seed'),
            _value(prefs, 'last_version_code'),
        ))

    data_headers = (
        ('Last Profile Update Time', 'datetime'),
        ('Last Profile Picture Upload', 'datetime'),
        'Session Account ID',
        'Profile Name',
        'Profile Avatar URL',
        'Profile Avatar ID',
        'Profile Key',
        'Local Registration ID',
        'Has Viewed Seed (as stored)',
        'App Version Code (as stored)',
    )
    if sources:
        source_path = '\n'.join(sources)
    return data_headers, data_list, source_path


@artifact_processor
def session_preferences(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    sources = []

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('network.loki.messenger_preferences.xml'):
            continue
        sources.append(file_found)
        for key, (xml_type, value) in _read_prefs(_parse_xml(file_found)).items():
            as_utc = ''
            if xml_type == 'long':
                try:
                    number = int(value)
                except (TypeError, ValueError):
                    number = 0
                if EPOCH_MS_MIN <= number <= EPOCH_MS_MAX:
                    as_utc = convert_unix_ts_to_utc(number)
            data_list.append((key, xml_type, value, str(as_utc)))

    data_headers = ('Key', 'XML Type', 'Value', 'Value as UTC (if read as epoch ms)')
    if sources:
        source_path = '\n'.join(sources)
    return data_headers, data_list, source_path


@artifact_processor
def session_attachments(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.isfile(file_found):
            continue
        source_path = os.path.dirname(file_found)
        data_list.append((
            os.path.basename(file_found),
            os.path.getsize(file_found),
            context.get_relative_path(file_found),
        ))

    data_headers = ('File Name', 'File Size (bytes)', 'Path')
    return data_headers, data_list, source_path
