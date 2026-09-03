__artifacts_v2__ = {
    "gmailEmails": {
        "name": "Gmail - App Emails",
        "description": "Parses emails from Gmail",
        "author": "Alexis Brignoni, Patrick Dalla, @stark4n6",
        "creation_date": "2023-01-04",
        "last_update_date": "2026-08-24",
        "requirements": "BeautifulSoup",
        "category": "Email",
        "notes": "Recipient, Reply To, Mailed By, Signed by and Subject Line are read from numbered fields of the zipped message protobuf. Protobuf field positions were established through testing; Mailed By and Signed by reflect stored header values and are not verified against Authentication-Results. Message is the readable text extracted from the stored HTML body (tags, styling and repeated whitespace removed). Each link's place in the text is marked [n], and Links lists the link targets by those numbers, as stored; a repeated target keeps its first number, and a marker with no text beside it is a link that carried none, such as a linked image. The unmodified body stays in the source database. The app keeps one bigTopDataDB.<id> store per signed-in account; every matched store is read, across every Android user of the device, with duplicate storage spellings (data/data, data/user/<n>, data_mirror) collapsed first and stores read in sorted path order. Account ID is the numeric store id as stored. The Account column is filled only when the Java String.hashCode of an address recorded in the same app instance's Gmail.xml equals the store id, which held for every store in the tested images; a store with no matching recorded address keeps a blank Account. A store that cannot be opened or queried is logged and skipped without dropping the other accounts' rows.",
        "paths": ('*/com.google.android.gm/databases/bigTopDataDB.*','*/com.google.android.gm/files/downloads/*/attachments/*/*.*','*/com.google.android.gm/shared_prefs/Gmail.xml'),
        "output_types": "standard",
        "artifact_icon": "inbox",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gm vc 65346694 | 200 rows",
            "cookbook_a11": "Android 11 | com.google.android.gm vc 64291995 | 201 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gm vc 65800239 | 201 rows",
            "hc_pixel8pro_a17": "Android 17 | com.google.android.gm vc 65854395 | 202 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gm vc 65346694 | 206 rows",
            "pixel3_a11": "Android 11 | com.google.android.gm vc 62324124 | 225 rows",
            "pixel3_a12": "Android 12 | com.google.android.gm vc 62900470 | 152 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gm vc 64361093 | 206 rows",
            "s20fe_a13": "Android 13 | com.google.android.gm vc 65854395 | 4 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gm vc 65429598 | 112 rows across 2 account stores",
            "sharon_a14": "Android 14 | com.google.android.gm vc 64719072 | 207 rows",
            "galaxys10_a10": "Android 10 | com.google.android.gm vc 62632206 | 28 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gm vc 65465122 | 109 rows",
            "sharon_a13": "Android 13 | com.google.android.gm vc 63927777 | 100 rows",
            "russell_a14": "Android 14 | com.google.android.gm vc 64738650 | 267 rows across 2 Android users",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gm vc 63927733 | 40 rows across 2 Android users",
            "userb2_a13": "Android 13 | com.google.android.gm vc 64855928 | 186 rows",
        },
    },
    "gmailLabels": {
        "name": "Gmail - Label Details",
        "description": "Parses email label metadata from Gmail",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2023-01-04",
        "last_update_date": "2026-08-24",
        "requirements": "none",
        "category": "Email",
        "notes": "One row per label per account store. Every matched bigTopDataDB.<id> store is read, across every Android user of the device, with duplicate storage spellings collapsed first and stores read in sorted path order. Account ID is the numeric store id as stored; the Account column is resolved from the same app instance's Gmail.xml as described in Gmail - App Emails. Label values are reported as stored.",
        "paths": ('*/com.google.android.gm/databases/bigTopDataDB.*','*/com.google.android.gm/shared_prefs/Gmail.xml'),
        "output_types": ["html","tsv","lava"],
        "artifact_icon": "mail",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gm vc 65346694 | 32 rows",
            "cookbook_a11": "Android 11 | com.google.android.gm vc 64291995 | 31 rows",
            "galaxys10_a10": "Android 10 | com.google.android.gm vc 62632206 | 30 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gm vc 65800239 | 33 rows",
            "hc_pixel8pro_a17": "Android 17 | com.google.android.gm vc 65854395 | 33 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gm vc 65346694 | 32 rows",
            "pixel3_a11": "Android 11 | com.google.android.gm vc 62324124 | 30 rows",
            "pixel3_a12": "Android 12 | com.google.android.gm vc 62900470 | 30 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gm vc 64361093 | 32 rows",
            "s20fe_a13": "Android 13 | com.google.android.gm vc 65854395 | 33 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gm vc 65429598 | 66 rows across 2 account stores",
            "samsungs20_a13": "Android 13 | com.google.android.gm vc 65465122 | 33 rows",
            "sharon_a13": "Android 13 | com.google.android.gm vc 63927777 | 31 rows",
            "sharon_a14": "Android 14 | com.google.android.gm vc 64719072 | 32 rows",
            "russell_a14": "Android 14 | com.google.android.gm vc 64738650 | 64 rows across 2 Android users",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gm vc 63927733 | 62 rows across 2 Android users",
            "userb2_a13": "Android 13 | com.google.android.gm vc 64855928 | 32 rows",
        },
    },
    "gmailDownloadRequests": {
        "name": "Gmail - Download Requests",
        "description": "Parses download requests from Gmail",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2023-01-04",
        "last_update_date": "2026-08-24",
        "requirements": "none",
        "category": "Email",
        "notes": "Every matched downloader.db is read, across every Android user of the device, with duplicate storage spellings collapsed first and stores read in sorted path order.",
        "paths": ('*/com.google.android.gm/databases/downloader.db*'),
        "output_types": "standard",
        "artifact_icon": "download",
        "sample_data": {
            "galaxys10_a10": "Android 10 | com.google.android.gm vc 62632206 | 0 rows",
            "pixel3_a11": "Android 11 | com.google.android.gm vc 62324124 | 0 rows",
            "pixel3_a12": "Android 12 | com.google.android.gm vc 62900470 | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gm vc 64361093 | 0 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gm vc 65429598 | 0 rows",
            "sharon_a13": "Android 13 | com.google.android.gm vc 63927777 | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.gm vc 64719072 | 0 rows",
            "russell_a14": "Android 14 | com.google.android.gm vc 64738650 | 2 rows",
        },
    }
}

import os
import re
import sqlite3
import zlib
from datetime import datetime, timezone

from bs4 import BeautifulSoup, NavigableString

from scripts.artifacts.gmail import _parse_xml
from scripts.artifacts.storagePathViews import canonical_path, unique_files
from scripts.context import Context
from scripts.ilapfuncs import open_sqlite_db_readonly, check_in_media, get_sqlite_db_records, artifact_processor, \
    decode_protobuf, logfunc

# whitespace plus the invisible padding characters observed in marketing preheaders
_WHITESPACE_RUN = re.compile(r'[\s\u00ad\u034f\u200b\u200c\u200d\ufeff]+')


def body_text_and_links(html_body):
    """The readable text of an HTML body plus the link targets it carries.

    Tags are dropped and whitespace runs (including the zero-width padding marketing
    mail hides its preheader behind) collapse to one space. Each link's place in the
    text is marked [n], and the second value lists the targets by those numbers, as
    stored. A repeated target keeps its first number, and a marker with no text beside
    it is a link that carried none, such as a linked image."""
    if not html_body:
        return '', ''
    soup = BeautifulSoup(html_body, 'html.parser')
    targets = []
    numbers = {}
    for anchor in soup.find_all('a', href=True):
        href = anchor.get('href')
        if not href:
            continue
        if href not in numbers:
            targets.append(href)
            numbers[href] = len(targets)
        anchor.append(NavigableString(f' [{numbers[href]}]'))
    text = _WHITESPACE_RUN.sub(' ', soup.get_text(separator=' ')).strip()
    links = '\n'.join(f'[{number}] {target}' for number, target in enumerate(targets, 1))
    return text, links


def _sort_key(path):
    """Evidence-relative path with one separator, so ordering is platform-independent."""
    return Context.get_relative_path(str(path)).replace('\\', '/')


def _container_of(path):
    """Storage-view aware prefix above the app's own data directory, so files from one
    Android user (or one storage volume) only pair with files from the same one."""
    key, _rank = canonical_path(_sort_key(path))
    return key.split('/com.google.android.gm/', 1)[0]


def _java_string_hash(text):
    """Java String.hashCode, the scheme the store filename suffixes follow on tested images."""
    value = 0
    for char in text:
        value = (31 * value + ord(char)) & 0xFFFFFFFF
    return value - 0x100000000 if value >= 0x80000000 else value


def _accounts_by_store_id(files_found):
    """{(container, store id): account address} from each container's Gmail.xml.

    Gmail.xml records the signed-in account addresses (the active-account value and
    the <address>-account-alias keys). A store is attributed to an address only when
    the Java String.hashCode of a recorded address equals the store's own numeric
    filename suffix; a store with no matching recorded address stays unresolved.
    """
    mapping = {}
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.basename(file_found) != 'Gmail.xml':
            continue
        addresses = set()
        for child in _parse_xml(file_found):
            name = child.attrib.get('name', '')
            if name == 'active-account' and child.text:
                addresses.add(child.text)
            elif name.endswith('-account-alias') and '@' in name:
                addresses.add(name[:-len('-account-alias')])
        container = _container_of(file_found)
        for address in addresses:
            mapping[(container, str(_java_string_hash(address)))] = address
    return mapping


def _gmail_stores(files_found, basename_prefix):
    """The matched database files, one per account store, in sorted path order."""
    stores = []
    for file_found in files_found:
        file_found = str(file_found)
        base = os.path.basename(file_found)
        if file_found.endswith(('-wal', '-shm', '-journal')) or base.startswith('.'):
            continue
        if file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue  # Skip mirror, it should be duplicate data
        if base.startswith(basename_prefix):
            stores.append(file_found)
    stores.sort(key=_sort_key)
    return stores


@artifact_processor
def gmailEmails(context):
    files_found = unique_files(context)
    data_list = []
    source_paths = set()
    accounts = _accounts_by_store_id(files_found)

    for bigTopDataDB in _gmail_stores(files_found, 'bigTopDataDB'):
        store_name = os.path.basename(bigTopDataDB)
        account_id = store_name.split('bigTopDataDB.', 1)[1] if '.' in store_name else ''
        account = accounts.get((_container_of(bigTopDataDB), account_id), '')
        source_file = Context.get_relative_path(bigTopDataDB)

        db = open_sqlite_db_readonly(bigTopDataDB)
        if db is None:
            continue
        try:
            cursor = db.cursor()
            cursor.execute('''
            select *
            from item_messages
            left join item_message_attachments on item_messages.row_id = item_message_attachments.item_messages_row_id
            ''')
            all_rows = cursor.fetchall()

            cursor.execute('''PRAGMA table_info(item_messages);''')
            columns_info = cursor.fetchall()
        except sqlite3.Error as ex:
            # One unreadable or drifted store must not cost the other accounts their rows
            logfunc(f'Unable to read Gmail store {source_file}: {ex}')
            continue
        finally:
            db.close()

        source_paths.add(bigTopDataDB)
        proto_col = ''
        for col_info in columns_info:
            if col_info[1] == "zipped_message_proto":
                proto_col = col_info[0]

        for row in all_rows:
            proto_blob = row[proto_col]
            if proto_blob is not None:
                arreglo = bytearray(proto_blob)
                arreglo = arreglo[1:]
                decompressed_data = zlib.decompress(arreglo)
                message, _typedef = decode_protobuf(decompressed_data)

                timestamp = (datetime.fromtimestamp(message['17'] / 1000, timezone.utc))
            else:
                continue

            serverid = row[1]
            attachname = row[15]
            attachhash = row[16]
            attachment = ''

            to = (message.get('1', '')).get('2', '') if '1' in message and '2' in message['1'] else '' #receiver
            if isinstance(to, bytes):
                to = to.decode()

            toname = (message.get('1', '')).get('3', '') if '1' in message and '3' in message['1'] else '' #receiver name
            if isinstance(toname, bytes):
                toname = toname.decode()

            replyto = (message['11'].get('17', '')) if '11' in message and '17' in message['11'] else '' #reply email
            if isinstance(replyto, bytes):
                replyto = replyto.decode()

            replytoname = (message['11'].get('15', b'')) #reply name
            if '11' in message and '15' in message['11'] and isinstance(message['11'].get('15', b''), bytes):
                replytoname = replytoname.decode()
            else:
                replytoname = (message['11'].get('15', ''))

            subjectline = (message.get('5', '')) #Subject line
            if subjectline != '':
                if isinstance(subjectline, bytes):
                    subjectline = subjectline.decode()
                else:
                    subjectline = ''

            messagehtml = ''
            messagetest = (message.get('6', '')) #HTML message
            if messagetest != '':
                messagetest = message['6'].get('2','')
                if messagetest != '':
                    try:
                        if isinstance(message['6']['2'], list):
                            for x in message['6']['2']:
                                messagehtml = messagehtml + (x['3']['2'].decode())
                        else:
                            messagehtml = (message['6']['2']['3']['2'].decode())
                    except (AttributeError, KeyError, TypeError, IndexError):
                        # The body node nesting varies between app versions
                        logfunc(f'Unrecognized Gmail message body structure for server id {serverid}; body omitted')

            mailedby = (message.get('11', {}).get('8', b'')) #mailed by
            if isinstance(message.get('11', {}).get('8', ''), bytes):
                mailedby = mailedby.decode()
            else:
                mailedby = ''

            signedby = (message.get('11', {}).get('9', b'')) #signed by
            if isinstance(message.get('11', {}).get('9', ''), bytes):
                signedby = signedby.decode()
            else:
                signedby = ''

            if attachname == 'noname':
                attachname = ''
            elif attachname is None:
                attachname = ''
            elif attachhash is None:
                attachhash = ''
            else:
                for attachpath in files_found:
                    attachpath = str(attachpath)
                    if attachhash in attachpath:
                        if attachpath.endswith(attachname):
                            attachment = check_in_media(attachpath, name=attachname) or ''

            message_text, message_links = body_text_and_links(messagehtml)
            data_list.append((timestamp,account,account_id,serverid,message_text,message_links,attachment,attachname,to,toname,replyto,replytoname,subjectline,mailedby,signedby,source_file))

    data_headers = (('Timestamp','datetime'),'Account','Account ID','Email ID','Message','Links',('Attachment','media'),'Attachment Name','Recipient','Recipient Name','Reply To','Reply To Name','Subject Line','Mailed By','Signed by','Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))

@artifact_processor
def gmailLabels(context):
    files_found = unique_files(context)
    data_list = []
    source_paths = set()
    accounts = _accounts_by_store_id(files_found)

    for bigTopDataDB in _gmail_stores(files_found, 'bigTopDataDB'):
        store_name = os.path.basename(bigTopDataDB)
        account_id = store_name.split('bigTopDataDB.', 1)[1] if '.' in store_name else ''
        account = accounts.get((_container_of(bigTopDataDB), account_id), '')
        source_file = Context.get_relative_path(bigTopDataDB)
        source_paths.add(bigTopDataDB)

        query = '''
        select
        label_server_perm_id,
        unread_count,
        total_count,
        unseen_count
        from label_counts
        order by label_server_perm_id
        '''

        db_records = get_sqlite_db_records(bigTopDataDB, query)

        for record in db_records:
            data_list.append((account,account_id,record[0],record[1],record[2],record[3],source_file))

    data_headers = ('Account','Account ID','Label','Unread Count','Total Count','Unseen Count','Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))

@artifact_processor
def gmailDownloadRequests(context):
    files_found = unique_files(context)
    data_list = []
    source_paths = set()

    for downloaderDB in _gmail_stores(files_found, 'downloader.db'):
        source_file = Context.get_relative_path(downloaderDB)
        source_paths.add(downloaderDB)

        #Get Gmail download requests
        query = '''
        select
        datetime(request_time_ms/1000,'unixepoch'),
        account_name,
        type,
        caller_id,
        url,
        target_file_path,
        target_file_size,
        priority
        from download_requests
        '''

        db_records = get_sqlite_db_records(downloaderDB, query)

        for record in db_records:
            data_list.append((record[0],record[1],record[2],record[3],record[4],record[5],record[6],record[7],source_file))

    data_headers = (('Timestamp Requested','datetime'),'Account Name','Download Type','Caller ID','URL','Target File Path','Target File Size','Priority','Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))
