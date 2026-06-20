# pylint: disable=W0613
__artifacts_v2__ = {
    "get_ChessComAccount": {
        "name": "Chess.com Account",
        "description": "Parses Chess.com account credentials and session data",
        "author": "",
        "creation_date": "2022-03-27",
        "last_update_date": "2022-03-27",
        "requirements": "none",
        "category": "Chess.com",
        "notes": "",
        "paths": ('*/com.chess/shared_prefs/com.chess.app.login_credentials.xml', '*/data/com.chess/shared_prefs/com.chess.app.session_preferences.xml'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "grid",
    }
}

import datetime
import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc


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


@artifact_processor
def get_ChessComAccount(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''

    credentials_file = ''
    session_file = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('login_credentials.xml'):
            credentials_file = file_found
        elif file_found.endswith('session_preferences.xml'):
            session_file = file_found

    # Login credentials
    if credentials_file:
        source_path = credentials_file
        cred_root = _parse_xml(credentials_file)
        for item in cred_root.findall("string"):
            key = item.attrib.get("name")
            value = item.text
            if key in ["pref_username_or_email", "pref_password"]:
                data_list.append((key, value))

    # Session
    if session_file:
        if not source_path:
            source_path = session_file
        sesh_root = _parse_xml(session_file)
        for item in sesh_root.findall("string"):
            key = item.attrib.get("name")
            value = item.text
            if key in ["pref_username", "pref_email", "pref_member_since"]:
                if key == "pref_member_since" and value:
                    value = datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc).isoformat(sep=" ", timespec="seconds")
                data_list.append((key, value))

    data_headers = ('Key', 'Value')
    return data_headers, data_list, source_path
