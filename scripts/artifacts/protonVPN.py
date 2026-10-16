__artifacts_v2__ = {
    "get_protonvpn_device_info": {
        "name": "ProtonVPN - Device Info",
        "description": "Parses ProtonVPN device and server-list-updater information (key and value) from the ServerListUpdater.xml preferences.",
        "author": "@nxb1t, @AlexisBrignoni, Codex",
        "creation_date": "2022-09-04",
        "last_update_date": "2022-09-04",
        "requirements": "none",
        "category": "ProtonVPN",
        "notes": "",
        "paths": ('*/ch.protonvpn.android/shared_prefs/ServerListUpdater.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "user",
    },
    "get_protonvpn_connection_history": {
        "name": "ProtonVPN - Connection History",
        "description": "Lines of the ProtonVPN Data.log that contain 'to:' and a node server name, with the line's timestamp and the server name.",
        "author": "@nxb1t, @AlexisBrignoni, Codex",
        "creation_date": "2022-09-04",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "ProtonVPN",
        "notes": "A row is a log line that contains 'to:' and a name that starts with 'node' and ends with "
                 "'.protonvpn.net'. Server Address is the first such name on the line, made only of "
                 "letters, digits, dots and hyphens, with no lookup; a line naming a server under "
                 "any other form of name is not reported. The app writes 'Connect to:' as a scan "
                 "result event before it starts a connection "
                 "(https://github.com/ProtonVPN/android-app/blob/"
                 "5febdcb04a0917a373a44660beed88e39dc83fbf/app/src/main/java/com/protonvpn/android/"
                 "vpn/ProtonVpnBackendProvider.kt#L153), so a row does not by itself establish that "
                 "a connection was made. Timestamp is the text before the first ' | ' of the line, "
                 "read as UTC only when it is a date and time ending in Z. The app writes that field "
                 "in UTC at the six release tags read from 3.2 to 5.20.57.0 "
                 "(https://github.com/ProtonVPN/android-app/blob/"
                 "5febdcb04a0917a373a44660beed88e39dc83fbf/app/src/main/java/com/protonvpn/android/"
                 "logging/ProtonLoggerImpl.kt#L85 and "
                 "https://github.com/ProtonVPN/android-app/blob/"
                 "fd1cb1dd108888e57b36ce8d7cc1dcdc25517c61/app/src/main/java/com/protonvpn/android/"
                 "logging/ProtonLoggerImpl.kt#L86-L87). Releases 2.8 and 2.11.90.17 wrote only a "
                 "time of day with no date "
                 "(https://github.com/ProtonVPN/android-app/blob/"
                 "624de2ac857138b83622aa600cecb88aa863c450/app/src/main/java/com/protonvpn/android/"
                 "utils/ProtonLoggerImpl.kt#L63); for a line in that or any other form Timestamp is "
                 "blank and Time As Logged holds the time text at the start of the line as stored, "
                 "with no time zone applied. No registered corpus holds this log (44 Android corpora checked on "
                 "2026-10-04), so the reading was tested on constructed lines only. Earlier versions "
                 "resolved the hostname to an IP address at parse time; that lookup was removed "
                 "because it generated network traffic from the examiner's workstation and the "
                 "resolved address reflected DNS at the time of analysis, not the logged connection.",
        "paths": ('*/ch.protonvpn.android/log/Data.log',),
        "output_types": "standard",
        "artifact_icon": "user",
    },
    "get_protonvpn_user_info": {
        "name": "ProtonVPN - User Info",
        "description": "Parses UserEntity and AccountEntity rows of the ProtonVPN database. The Email, Name, Username, Display Name and Account State columns are read by column position.",
        "author": "@nxb1t, @AlexisBrignoni, Codex",
        "creation_date": "2022-09-04",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "ProtonVPN",
        "notes": "Each UserEntity row is matched to its AccountEntity row on the user id column the two "
                 "tables share. If a database is met whose schema exposes no shared user id, the rows "
                 "are paired by result order instead, and an unequal number of rows on either side "
                 "would then attribute an account to the wrong user. Values inside each row are read "
                 "by position; that mapping was written against one app version, which is not "
                 "recorded here, and may not hold on other versions.",
        "paths": ('*/ch.protonvpn.android/databases/db',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "user",
    }
}

import re
import datetime
from datetime import timezone
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, device_info, checkabx, abxread, logfunc


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
def get_protonvpn_device_info(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('ServerListUpdater.xml'):
            source_path = file_found

            if (checkabx(file_found)):
                multi_root = False
                root = abxread(file_found, multi_root).getroot()
            else:
                root = _parse_xml(file_found)


            for elem in root.iter():
                if elem.attrib.get('name') is not None:
                    if elem.text is not None:
                        data_list.append((elem.attrib.get('name'), elem.text))
                    elif elem.attrib.get('value') is not None:
                        data_list.append((elem.attrib.get('name'), elem.attrib.get('value')))

                    if (elem.attrib.get('name')) == 'ipAddress':
                        device_info("ProtonVPN", "IP Address", elem.text, source_path)

                    if (elem.attrib.get('name')) == 'lastKnownIsp':
                        device_info("ProtonVPN", "ISP", elem.text, source_path)

                    if (elem.attrib.get('name')) == 'lastKnownCountry':
                        device_info("ProtonVPN", "Country", elem.text, source_path)

                    if (elem.attrib.get('name')) == 'ipAddressCheckTimestamp':
                        timestamp = datetime.datetime.fromtimestamp(int(elem.attrib.get("value"))/1000, datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')
                        device_info("ProtonVPN", "Last IP Check Time", timestamp, source_path)

    data_headers = ('Key', 'Value')
    return data_headers, data_list, source_path


# ProtonVPN 3.2 and later start a log line with a UTC date and time ending in Z, then ' | '.
LOG_UTC_TIME = re.compile(r'(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})(?:\.\d+)?Z$')


def _log_line_time(entry):
    """Return (UTC datetime, '') for a line led by a UTC time, else ('', the line's start as stored)."""
    lead = entry.split(' | ', 1)[0].strip() if ' | ' in entry else ''
    match = LOG_UTC_TIME.match(lead)
    if match:
        try:
            parsed = datetime.datetime.strptime(f'{match[1]} {match[2]}', '%Y-%m-%d %H:%M:%S')
            return parsed.replace(tzinfo=timezone.utc), ''
        except ValueError:
            pass
    if not lead:
        time_of_day = re.match(r'\d{2}:\d{2}:\d{2}[^\s:]*', entry)
        lead = time_of_day[0] if time_of_day else ''
    return '', lead[:40]


@artifact_processor
def get_protonvpn_connection_history(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('Data.log'):
            source_path = file_found

            with open(file_found, 'r', encoding='utf-8') as protonvpn_log:
                log_entries = protonvpn_log.readlines()

            regex = re.compile(r"node[A-Za-z0-9.-]*?\.protonvpn\.net")
            for entry in log_entries:
                initial_connect = entry.find('to:')
                if initial_connect != -1:
                    server_hostname = regex.search(entry)
                    if server_hostname:
                        timestamp, time_as_logged = _log_line_time(entry)
                        data_list.append((timestamp, server_hostname[0], time_as_logged))

    data_headers = (('Timestamp', 'datetime'), 'Server Address', 'Time As Logged')
    return data_headers, data_list, source_path


@artifact_processor
def get_protonvpn_user_info(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('db'):
            source_path = file_found
            db = open_sqlite_db_readonly(file_found)

            # Cursor for User Data
            cursor = db.cursor()
            cursor.execute('SELECT * FROM main.UserEntity')
            user_columns = [column[0] for column in cursor.description]
            user_data_rows = cursor.fetchall()

            # Cursor for Account Data
            cursor = db.cursor()
            cursor.execute('SELECT * FROM main.AccountEntity')
            account_columns = [column[0] for column in cursor.description]
            account_data_rows = cursor.fetchall()

            # Match each user to its own account on the id column both tables carry. Pairing the two
            # result sets by row order attributes an account to another user as soon as the row
            # counts or the row order differ.
            key = next((column for column in user_columns
                        if column.lower() in ('userid', 'user_id') and column in account_columns), None)
            if key:
                accounts_by_user = {row[account_columns.index(key)]: row for row in account_data_rows}
                paired_rows = [(user_row, accounts_by_user.get(user_row[user_columns.index(key)]))
                               for user_row in user_data_rows]
            else:
                logfunc(f'No shared user id column in {file_found}; '
                        'UserEntity and AccountEntity rows are paired by result order')
                paired_rows = list(zip(user_data_rows, account_data_rows))

            for user_row, account_row in paired_rows:
                data_list.append((user_row[1], user_row[2], account_row[1] if account_row else '',
                                  user_row[3], account_row[5] if account_row else ''))

            db.close()

    data_headers = ('Email', 'Name', 'Username', 'Display Name', 'Account State')
    return data_headers, data_list, source_path
