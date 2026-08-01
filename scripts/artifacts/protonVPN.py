__artifacts_v2__ = {
    "get_protonvpn_device_info": {
        "name": "ProtonVPN - Device Info",
        "description": "Parses ProtonVPN device and server-list-updater information (key and value) from the ServerListUpdater.xml preferences.",
        "author": "",
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
        "description": "Parses ProtonVPN connection history (server address and timestamp) from the ProtonVPN Data.log.",
        "author": "",
        "creation_date": "2022-09-04",
        "last_update_date": "2026-07-31",
        "requirements": "none",
        "category": "ProtonVPN",
        "notes": "The server address is reported exactly as recorded in Data.log. Earlier versions "
                 "resolved the hostname to an IP address at parse time; that lookup was removed "
                 "because it generated network traffic from the examiner's workstation and the "
                 "resolved address reflected DNS at the time of analysis, not the logged connection.",
        "paths": ('*/ch.protonvpn.android/log/Data.log',),
        "output_types": "standard",
        "artifact_icon": "user",
    },
    "get_protonvpn_user_info": {
        "name": "ProtonVPN - User Info",
        "description": "Parses the ProtonVPN user account (email, name, username, display name and account state) from the ProtonVPN database.",
        "author": "",
        "creation_date": "2022-09-04",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "ProtonVPN",
        "notes": "Each UserEntity row is matched to its AccountEntity row on the user id column the two "
                 "tables share. If a database is met whose schema exposes no shared user id, the rows "
                 "are paired by result order instead, and an unequal number of rows on either side "
                 "would then attribute an account to the wrong user. Values inside each row are read "
                 "by position; that mapping was established against the app version this parser was "
                 "written for and may not hold on other versions.",
        "paths": ('*/ch.protonvpn.android/databases/db',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "user",
    }
}

import re
import datetime
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, device_info, checkabx, abxread, convert_human_ts_to_utc, logfunc


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

            regex = re.compile(r"node.+\.protonvpn\.net")
            for entry in log_entries:
                initial_connect = entry.find('to:')
                if initial_connect != -1:
                    timestamp = convert_human_ts_to_utc(entry[:entry.find('|')-1].split('.')[0].replace('T', ' '))
                    server_hostname = regex.search(entry)
                    if server_hostname:
                        data_list.append((server_hostname[0], timestamp))

    data_headers = ('Server Address', ('Timestamp', 'datetime'))
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
