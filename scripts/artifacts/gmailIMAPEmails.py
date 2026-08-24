__artifacts_v2__ = {
    "gmailIMAPEmails": {
        "name": "Gmail - IMAP Mailbox Emails",
        "description": "Parses emails from IMAP mailboxes in the Gmail App",
        "author": "ogmini",
        "creation_date": "2025-08-20",
        "last_update_date": "2026-08-24",
        "requirements": "BeautifulSoup",
        "category": "Email",
        "notes": "Every matched EmailProvider store is read, across every Android user of the device, with duplicate storage spellings collapsed first and stores read in sorted path order. The Account column is the emailAddress the store's own Account table records for the row. Body and attachment files are only paired with rows from the same app instance they belong to. Body(HTML) is the readable text extracted from the message's stored HTML body file; Links lists the distinct link targets that body carries, in document order, as stored, and the unmodified body file stays in the report's data folder. No tested image held IMAP data (every EmailProvider.db carried empty Account and Message tables), so row-producing behavior is verified against constructed known data, not a real image.",
        "paths": ('*/com.google.android.gm/databases/EmailProvider.*','*/com.google.android.gm/files/body/0/*/*.*','*/com.google.android.gm/databases/*.db_att/*','*/com.google.android.gm/cache/*.attachment'),
        "output_types": "standard",
        "artifact_icon": "inbox",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gm vc 65346694 | 0 rows",
            "cookbook_a11": "Android 11 | com.google.android.gm vc 64291995 | 0 rows",
            "galaxys10_a10": "Android 10 | com.google.android.gm vc 62632206 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gm vc 65800239 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | com.google.android.gm vc 65854395 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gm vc 65346694 | 0 rows",
            "pixel3_a11": "Android 11 | com.google.android.gm vc 62324124 | 0 rows",
            "pixel3_a12": "Android 12 | com.google.android.gm vc 62900470 | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gm vc 64361093 | 0 rows",
            "s20fe_a13": "Android 13 | com.google.android.gm vc 65854395 | 0 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gm vc 65429598 | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gm vc 65465122 | 0 rows",
            "sharon_a13": "Android 13 | com.google.android.gm vc 63927777 | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.gm vc 64719072 | 0 rows",
            "russell_a14": "Android 14 | com.google.android.gm vc 64738650 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gm vc 63927733 | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.gm vc 64855928 | 0 rows",
        },
    },
    "gmailIMAPAccounts": {
        "name": "Gmail - IMAP Accounts",
        "description": "Parses IMAP Accounts in the Gmail App",
        "author": "ogmini",
        "creation_date": "2025-10-11",
        "last_update_date": "2026-08-24",
        "requirements": "none",
        "category": "Email",
        "notes": "Every matched EmailProvider store is read, across every Android user of the device, with duplicate storage spellings collapsed first and stores read in sorted path order. No tested image held IMAP accounts, so row-producing behavior is verified against constructed known data, not a real image.",
        "paths": ('*/com.google.android.gm/databases/EmailProvider.*'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gm vc 65346694 | 0 rows",
            "cookbook_a11": "Android 11 | com.google.android.gm vc 64291995 | 0 rows",
            "galaxys10_a10": "Android 10 | com.google.android.gm vc 62632206 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gm vc 65800239 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | com.google.android.gm vc 65854395 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gm vc 65346694 | 0 rows",
            "pixel3_a11": "Android 11 | com.google.android.gm vc 62324124 | 0 rows",
            "pixel3_a12": "Android 12 | com.google.android.gm vc 62900470 | 0 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gm vc 64361093 | 0 rows",
            "s20fe_a13": "Android 13 | com.google.android.gm vc 65854395 | 0 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gm vc 65429598 | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gm vc 65465122 | 0 rows",
            "sharon_a13": "Android 13 | com.google.android.gm vc 63927777 | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.gm vc 64719072 | 0 rows",
            "russell_a14": "Android 14 | com.google.android.gm vc 64738650 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gm vc 63927733 | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.gm vc 64855928 | 0 rows",
        },
    }
}

import os
import sqlite3
import urllib.parse

from scripts.artifacts.gmailEmails import body_links, body_text
from scripts.artifacts.storagePathViews import canonical_path, unique_files
from scripts.ilapfuncs import open_sqlite_db_readonly, artifact_processor, convert_unix_ts_to_utc, logfunc, check_in_media
from scripts.context import Context


def _sort_key(path):
    """Evidence-relative path with one separator, so ordering is platform-independent."""
    return Context.get_relative_path(str(path)).replace('\\', '/')


def _container_of(path):
    """Storage-view aware prefix above the app's own data directory, so files from one
    Android user (or one storage volume) only pair with files from the same one."""
    key, _rank = canonical_path(_sort_key(path))
    return key.split('/com.google.android.gm/', 1)[0]


@artifact_processor
def gmailIMAPEmails(context):
    emailProviderDB_found = []

    data_list = []

    bodyTxt_list = []
    bodyHtml_list = []

    attachRecv_list = []
    attachSent_list = []

    for file_found in unique_files(context):
        file_found = str(file_found)

        if file_found.endswith(('-wal','-shm','-journal')):
            continue
        elif os.path.basename(file_found).startswith('.'):
            continue
        elif file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue  # Skip mirror, it should be duplicate data
        if os.path.basename(file_found).startswith('EmailProvider'):
            emailProviderDB_found.append(file_found)
        if file_found.endswith(('.txt')):
            bodyTxt_list.append(file_found)
        if file_found.endswith(('.html')):
            bodyHtml_list.append(file_found)
        if os.path.basename(os.path.dirname(file_found)).endswith(('.db_att')):
            attachRecv_list.append(file_found)
        if file_found.endswith(('.attachment')):
            attachSent_list.append(file_found)

    emailProviderDB_found.sort(key=_sort_key)

    for emailProviderDB in emailProviderDB_found:
        container = _container_of(emailProviderDB)

        db = open_sqlite_db_readonly(emailProviderDB)
        if db is None:
            continue
        try:
            cursor = db.cursor()
            cursor.execute('''
            select M.timeStamp, M._id, M.snippet, M.toList, M.replyToList, M.subject, M.fromList, M.displayName, M.flagRead, M.flagAttachment,
            A._id as AccountID,
            MB.displayName,
            A.emailAddress
            from Message as M
            inner join Account as A on A._id = M.AccountKey
            inner join Mailbox as MB on M.mailboxKey = MB._id
            ''')

            all_rows = cursor.fetchall()
            for row in all_rows:
                row = list(row)
                try:
                    row[0] = convert_unix_ts_to_utc(row[0])
                except (TypeError, ValueError, OverflowError, OSError) as ex:
                    logfunc(f'Error Timestamp conversion: {ex}')

                # BODY Files - Full message is found elsewhere */data/com.google.android.gm/files/body/[ParentFolder]/[_idFolder]
                # TXT Body
                tBody = ''
                for txtBody in bodyTxt_list:
                    if _container_of(txtBody) != container:
                        continue
                    if ((os.path.basename(txtBody)) == (str(row[1]) + '.txt')):
                        with open(txtBody, "r", encoding="utf-8") as f:
                            tBody = f.read()

                # HTML Body
                hBody = ''
                for htmlBody in bodyHtml_list:
                    if _container_of(htmlBody) != container:
                        continue
                    if ((os.path.basename(htmlBody)) == (str(row[1]) + '.html')):
                        with open(htmlBody, "r", encoding="utf-8") as f:
                            hBody = f.read()

                # ATTACHMENTS - Files can be stored in two different locations depending if they are sent or received.
                AttachmentPaths = []
                if (row[9] == 1):
                    cursor_attach = db.cursor()
                    cursor_attach.execute('''
                    select A.accountKey, A._id, A.fileName, A.mimeType, A.cachedFile
                    from Attachment as A
                    where messageKey = ?
                    ''', (row[1],))

                    attach_rows = cursor_attach.fetchall()
                    for row_a in attach_rows:
                        row_a = list(row_a)
                        accountID = row_a[0]
                        attachmentID = row_a[1]

                        if (row_a[4] is None):
                            # Received Attachment */data/com.google.android.gm/databases/*.db_att/*.*
                            for rAttach in attachRecv_list:
                                if _container_of(rAttach) != container:
                                    continue
                                if (os.path.isfile(rAttach) and ((os.path.basename(rAttach)) == f'{attachmentID}') and ((os.path.basename(os.path.dirname(rAttach))) == f'{accountID}.db_att')):
                                    ref = check_in_media(rAttach, row_a[2])
                                    if ref:
                                        AttachmentPaths.append(ref)
                        else:
                            # Sent Attachment /data/com.google.android.gm/cache/*.attachment
                            uri = row_a[4]
                            fileName = ''
                            parsedUri = urllib.parse.urlparse(uri)

                            queryParams = urllib.parse.parse_qs(parsedUri.query)
                            filePathEncoded = queryParams.get("filePath", [None])[0]

                            if filePathEncoded:
                                filePath = urllib.parse.unquote(filePathEncoded)
                                fileName = os.path.basename(filePath).replace(":", "_")

                                for sAttach in attachSent_list:
                                    if _container_of(sAttach) != container:
                                        continue
                                    if (os.path.isfile(sAttach) and ((os.path.basename(sAttach)) == fileName)):
                                        ref = check_in_media(sAttach, row_a[2])
                                        if ref:
                                            AttachmentPaths.append(ref)

                # Collapse to a bare ref for a single attachment, list for several, and
                # '' when none resolved -- mirrors the other media artifacts. The None
                # guards above keep any unresolved ref (which the LAVA viewer chokes on)
                # out of the list.
                if len(AttachmentPaths) == 1:
                    attachment_cell = AttachmentPaths[0]
                elif AttachmentPaths:
                    attachment_cell = AttachmentPaths
                else:
                    attachment_cell = ''
                data_list.append((row[0], row[12], row[10], row[1], row[2], tBody, body_text(hBody), body_links(hBody), row[3], row[4], row[5], row[6], row[7], row[8], row[9], attachment_cell, row[11], Context.get_relative_path(emailProviderDB)))
        except sqlite3.Error as ex:
            # One unreadable or drifted store must not cost the other accounts their rows
            logfunc(f'Unable to read Gmail EmailProvider store {Context.get_relative_path(emailProviderDB)}: {ex}')
            continue
        finally:
            db.close()

    data_headers = (('Timestamp','datetime'),'Account','Account ID','_id','Snippet', 'Body(TXT)', 'Body(HTML)', 'Links', 'Recipient','Reply To','Subject Line','From','Display Name', 'Read', 'AttachmentFlag', ('Attachments', 'media'), 'Mailbox Folder', 'Source File')
    return data_headers, data_list, 'See source file(s) below:'

@artifact_processor
def gmailIMAPAccounts(context):
    emailProviderDB_found = []

    data_list = []

    for file_found in unique_files(context):
        file_found = str(file_found)

        if file_found.endswith(('-wal','-shm','-journal')):
            continue
        elif os.path.basename(file_found).startswith('.'):
            continue
        elif file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue  # Skip mirror, it should be duplicate data
        if os.path.basename(file_found).startswith('EmailProvider'):
            emailProviderDB_found.append(file_found)

    emailProviderDB_found.sort(key=_sort_key)

    for emailProviderDB in emailProviderDB_found:
        db = open_sqlite_db_readonly(emailProviderDB)
        if db is None:
            continue
        try:
            cursor = db.cursor()
            cursor.execute('''
            select A._id, A.displayName, A.emailAddress, A.senderName, H.login, H.password, H.address, H.port
            from Account as A
            inner join HostAuth as H on (A.hostAuthKeyRecv  = H._id) or (A.hostAuthKeySend = H._id)
            ''')

            all_rows = cursor.fetchall()
            for row in all_rows:
                row = list(row)

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], Context.get_relative_path(emailProviderDB)))
        except sqlite3.Error as ex:
            # One unreadable or drifted store must not cost the other accounts their rows
            logfunc(f'Unable to read Gmail EmailProvider store {Context.get_relative_path(emailProviderDB)}: {ex}')
            continue
        finally:
            db.close()

    data_headers = ('_id', 'displayName', 'emailAddress', 'senderName', 'login','password','address','port', 'Source File')
    return data_headers, data_list, 'See source file(s) below:'
