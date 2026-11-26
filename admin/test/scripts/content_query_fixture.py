"""Builds the synthetic extractions used by the Content Query test cases (contentQuery.py).

Every value is invented: phone numbers are +1555 numbers, addresses are under example.com,
packages under com.example, the serial and ANDROID_ID are made up. Only the structure is
taken from the sources: the text the content command prints (AOSP Content.java) and the
folders and file names android_triage (android_triage.sh) and ALEX (alex.py, query_content)
write. These cases are built:

* ``alex``: an ALEX raw text folder, saved with CRLF line endings as Path.write_text does on
  Windows, with multi-line values, a value that holds ', total=', a value that holds the
  name of the next column (', seen='), a value line that starts with 'Row: ', NULL, BLOB
  and empty values, MMS parts, MMS addresses (FROM, TO, CC and BCC rows, a NULL address,
  a msg_id with no MMS row, a type that is not an address field, and an MMS row with no
  address rows), and a file of a URI
  the artifacts do not read;
* ``alex_skipped``: an ALEX folder without sms.txt (what ALEX leaves when a body holds
  'No result found') and without mms_addr.txt, with a call log and MMS rows whose
  addresses are then unknown;
* ``alex_join_incomplete``: MMS rows (one with _id NULL) and an address file that ends
  with a provider error and holds address rows with an empty and a NULL msg_id;
* ``alex_mms_incomplete``: an MMS file that ends with a provider error after its first
  row, and a full address file;
* ``alex_row_edges``: two ALEX folders, one with a single SMS row whose body holds
  ', seen=' (the column list then names seen twice), one with a single SMS row whose
  body holds an error line and an exception line, followed by another column;
* ``triage``: an android_triage folder with LF line endings, 'No result found.', an empty
  file (a failed query, whose error went to the terminal), multi-line values, a contacts
  data dump whose hash_id ends with a line break on every row, the tool's own log and
  provider list, and a file of a URI the artifacts do not read;
* ``triage_stderr``: an android_triage folder whose files hold the error text the content
  command prints on stderr (a SecurityException, an IllegalArgumentException, and rows
  followed by an error). The published script does not capture stderr; the case exercises
  the error statuses of the reader end to end.

Usage: python content_query_fixture.py <output folder>
Writes one zip per case into the folder and prints their names and sizes.
"""
import os
import sys
import zipfile

ZIP_TIME = (2026, 11, 25, 0, 0, 0)
ALEX_ROOT = 'ALEX_SYNTH0001/content_provider_SYNTH0001'
TRIAGE_ROOT = 'a1b2c3d4e5f60718/20261125_10_15_30_contentprovider'


def rows(*records):
    """Content command text for records given as lists of (name, value) pairs."""
    out = []
    for number, record in enumerate(records):
        out.append(f'Row: {number} ' + ', '.join(f'{name}={value}' for name, value in record))
    return '\n'.join(out) + '\n'


SMS = rows(
    [('_id', '12'), ('thread_id', '3'), ('address', '+15550100001'), ('person', 'NULL'),
     ('date', '1767225600000'), ('date_sent', '1767225598000'), ('read', '1'), ('status', '-1'), ('type', '1'),
     ('subject', 'NULL'), ('body', 'See you at 8'), ('seen', '1'), ('sub_id', '1'),
     ('creator', 'com.example.messaging')],
    [('_id', '13'), ('thread_id', '3'), ('address', '+15550100001'), ('person', 'NULL'),
     ('date', '1767229200000'), ('date_sent', '0'), ('read', '1'), ('status', '-1'), ('type', '2'),
     ('subject', ''), ('body', 'First line\nsecond line\n\nRow: 7 of the list\nfifth line after a blank one'),
     ('seen', '1'), ('sub_id', '1'), ('creator', 'com.example.messaging')],
    [('_id', '14'), ('thread_id', '4'), ('address', '+15550100002'), ('person', 'NULL'),
     ('date', '1767232800000'), ('date_sent', '1767232790000'), ('read', '0'), ('status', '-1'), ('type', '1'),
     ('subject', 'NULL'), ('body', 'Order 77 confirmed, total=40 USD'), ('seen', '0'), ('sub_id', '1'),
     ('creator', 'com.example.messaging')],
    [('_id', '15'), ('thread_id', '4'), ('address', '+15550100002'), ('person', 'NULL'),
     ('date', '1767236400000'), ('date_sent', 'NULL'), ('read', '1'), ('status', '-1'), ('type', '9'),
     ('subject', 'NULL'), ('body', 'NULL'), ('seen', '1'), ('sub_id', '-1'), ('creator', '')],
    [('_id', '16'), ('thread_id', '4'), ('address', '+15550100002'), ('person', 'NULL'),
     ('date', '1767240000000'), ('date_sent', '1767239990000'), ('read', '1'), ('status', '-1'), ('type', '2'),
     ('subject', 'NULL'), ('body', 'the form says, seen=yes'), ('seen', '1'), ('sub_id', '1'),
     ('creator', 'com.example.messaging')],
)

MMS = rows(
    [('_id', '7'), ('thread_id', '5'), ('date', '1767243600'), ('date_sent', '1767243590'), ('msg_box', '1'),
     ('read', '1'), ('sub', 'NULL'), ('ct_t', 'application/vnd.wap.multipart.related'), ('m_type', '132'),
     ('seen', '1'), ('sub_id', '1'), ('creator', 'com.example.messaging'), ('text_only', '0')],
    [('_id', '8'), ('thread_id', '5'), ('date', '1767247200'), ('date_sent', '0'), ('msg_box', '2'),
     ('read', '1'), ('sub', 'Holiday\nphotos'), ('ct_t', 'application/vnd.wap.multipart.related'),
     ('m_type', '128'), ('seen', '1'), ('sub_id', '1'), ('creator', 'com.example.messaging'), ('text_only', '1')],
    [('_id', '9'), ('thread_id', '6'), ('date', '1767250800'), ('date_sent', '0'), ('msg_box', '3'),
     ('read', '1'), ('sub', 'NULL'), ('ct_t', 'application/vnd.wap.multipart.related'),
     ('m_type', '128'), ('seen', '1'), ('sub_id', '1'), ('creator', 'com.example.messaging'), ('text_only', '1')],
)

MMS_ADDR = rows(
    [('_id', '30'), ('msg_id', '7'), ('contact_id', 'NULL'), ('address', '+15550100003'), ('type', '137'),
     ('charset', '106'), ('sub_id', '1')],
    [('_id', '31'), ('msg_id', '7'), ('contact_id', 'NULL'), ('address', 'insert-address-token'), ('type', '151'),
     ('charset', '106'), ('sub_id', '1')],
    [('_id', '32'), ('msg_id', '7'), ('contact_id', 'NULL'), ('address', '+15550100004'), ('type', '130'),
     ('charset', '106'), ('sub_id', '1')],
    [('_id', '33'), ('msg_id', '7'), ('contact_id', 'NULL'), ('address', 'test.user@example.com'), ('type', '130'),
     ('charset', '106'), ('sub_id', '1')],
    [('_id', '34'), ('msg_id', '8'), ('contact_id', 'NULL'), ('address', 'insert-address-token'), ('type', '137'),
     ('charset', '106'), ('sub_id', '1')],
    [('_id', '35'), ('msg_id', '8'), ('contact_id', 'NULL'), ('address', '+15550100003'), ('type', '151'),
     ('charset', '106'), ('sub_id', '1')],
    [('_id', '36'), ('msg_id', '8'), ('contact_id', 'NULL'), ('address', 'NULL'), ('type', '129'),
     ('charset', 'NULL'), ('sub_id', '1')],
    [('_id', '37'), ('msg_id', '99'), ('contact_id', 'NULL'), ('address', '+15550100005'), ('type', '137'),
     ('charset', '106'), ('sub_id', '1')],
    [('_id', '38'), ('msg_id', '8'), ('contact_id', 'NULL'), ('address', '+15550100006'), ('type', '140'),
     ('charset', '106'), ('sub_id', '1')],
)

MMS_PART = rows(
    [('_id', '20'), ('mid', '7'), ('seq', '-1'), ('ct', 'application/smil'), ('name', 'NULL'), ('chset', 'NULL'),
     ('cid', '<smil>'), ('cl', 'smil.xml'), ('fn', 'NULL'), ('_data', 'NULL'), ('text', '<smil><body/></smil>')],
    [('_id', '21'), ('mid', '7'), ('seq', '0'), ('ct', 'image/jpeg'), ('name', 'IMG_0001.jpg'), ('chset', 'NULL'),
     ('cid', '<img1>'), ('cl', 'IMG_0001.jpg'), ('fn', 'NULL'),
     ('_data', '/data/user/0/com.android.providers.telephony/app_parts/PART_1767243600000_IMG_0001.jpg'),
     ('text', 'NULL')],
    [('_id', '22'), ('mid', '8'), ('seq', '0'), ('ct', 'text/plain'), ('name', 'NULL'), ('chset', '106'),
     ('cid', '<text_0>'), ('cl', 'text_0.txt'), ('fn', 'NULL'), ('_data', 'NULL'),
     ('text', 'Two lines\nof text')],
)

CALLS = rows(
    [('_id', '1'), ('number', '+15550100001'), ('date', '1767225600000'), ('duration', '74'), ('type', '1'),
     ('name', 'Test Contact'), ('presentation', '1'), ('subscription_id', '1'), ('geocoded_location', 'Example'),
     ('countryiso', 'US')],
    [('_id', '2'), ('number', '+15550100002'), ('date', '1767229200000'), ('duration', '0'), ('type', '3'),
     ('name', 'NULL'), ('presentation', '1'), ('subscription_id', '1'), ('geocoded_location', ''),
     ('countryiso', 'US')],
    [('_id', '3'), ('number', ''), ('date', '1767232800000'), ('duration', '12'), ('type', '2'),
     ('name', 'NULL'), ('presentation', '2'), ('subscription_id', 'NULL'), ('geocoded_location', ''),
     ('countryiso', 'NULL')],
)

CONTACTS = rows(
    [('_id', '1'), ('display_name', 'Test Contact'), ('has_phone_number', '1'), ('starred', '0'),
     ('lookup', '0r1-EXAMPLE'), ('photo_uri', 'NULL'), ('contact_last_updated_timestamp', '1767200000000')],
    [('_id', '2'), ('display_name', 'Second, Example'), ('has_phone_number', '1'), ('starred', '1'),
     ('lookup', '0r2-EXAMPLE'), ('photo_uri', 'NULL'), ('contact_last_updated_timestamp', '1767200100000')],
)

PHONES = rows(
    [('_id', '10'), ('contact_id', '1'), ('raw_contact_id', '1'), ('display_name', 'Test Contact'),
     ('data1', '+1 555-010-0001'), ('data2', '2'), ('data3', 'NULL'), ('data4', '+15550100001'),
     ('data15', 'BLOB'), ('account_type', 'com.example.account'), ('account_name', 'test.user@example.com'),
     ('contact_last_updated_timestamp', '1767200000000'), ('hash_id', 'aGFzaDE=\n')],
    [('_id', '11'), ('contact_id', '2'), ('raw_contact_id', '2'), ('display_name', 'Second, Example'),
     ('data1', '+1 555-010-0002'), ('data2', '0'), ('data3', 'Work, desk'), ('data4', '+15550100002'),
     ('data15', 'NULL'), ('account_type', 'NULL'), ('account_name', 'NULL'),
     ('contact_last_updated_timestamp', '1767200100000'), ('hash_id', 'aGFzaDI=\n')],
)

EVENTS = rows(
    [('_id', '5'), ('calendar_id', '1'), ('title', 'Dentist'), ('description', 'Bring the X-ray\nand the referral'),
     ('eventLocation', 'Main St 100'), ('dtstart', '1767265200000'), ('dtend', '1767268800000'),
     ('eventTimezone', 'America/New_York'), ('duration', 'NULL'), ('allDay', '0'), ('rrule', 'NULL'),
     ('organizer', 'test.user@example.com'), ('deleted', '0')],
    [('_id', '6'), ('calendar_id', '1'), ('title', 'Weekly\nsync'), ('description', ''),
     ('eventLocation', ''), ('dtstart', '1767358800000'), ('dtend', 'NULL'),
     ('eventTimezone', 'UTC'), ('duration', 'P3600S'), ('allDay', '0'), ('rrule', 'FREQ=WEEKLY;BYDAY=MO'),
     ('organizer', 'test.user@example.com'), ('deleted', '0')],
    [('_id', '7'), ('calendar_id', '2'), ('title', 'Holiday'), ('description', 'NULL'),
     ('eventLocation', 'NULL'), ('dtstart', '1767398400000'), ('dtend', '1767484800000'),
     ('eventTimezone', 'UTC'), ('duration', 'NULL'), ('allDay', '1'), ('rrule', 'NULL'),
     ('organizer', 'holidays@example.com'), ('deleted', '1')],
)

CALENDARS = rows(
    [('_id', '1'), ('account_name', 'test.user@example.com'), ('account_type', 'com.example.account'),
     ('calendar_displayName', 'Test User'), ('ownerAccount', 'test.user@example.com'), ('visible', '1'),
     ('sync_events', '1'), ('deleted', '0')],
    [('_id', '2'), ('account_name', 'test.user@example.com'), ('account_type', 'com.example.account'),
     ('calendar_displayName', 'Holidays'), ('ownerAccount', 'holidays@example.com'), ('visible', '0'),
     ('sync_events', '1'), ('deleted', '0')],
)

MEDIA = rows(
    [('_id', '1001'), ('_data', '/storage/emulated/0/DCIM/Camera/IMG_20260101_120000.jpg'),
     ('_display_name', 'IMG_20260101_120000.jpg'), ('relative_path', 'DCIM/Camera/'),
     ('volume_name', 'external_primary'), ('mime_type', 'image/jpeg'), ('_size', '204800'),
     ('date_added', '1767268800'), ('date_modified', '1767268800'), ('datetaken', '1767268799000'),
     ('owner_package_name', 'com.example.camera'), ('bucket_display_name', 'Camera'), ('is_trashed', '0'),
     ('is_pending', '0')],
    [('_id', '1002'), ('_data', '/storage/emulated/0/Download/invoice.pdf'), ('_display_name', 'invoice.pdf'),
     ('relative_path', 'Download/'), ('volume_name', 'external_primary'), ('mime_type', 'application/pdf'),
     ('_size', '1024'), ('date_added', '1767272400'), ('date_modified', '1767272400'), ('datetaken', 'NULL'),
     ('owner_package_name', 'com.example.browser'), ('bucket_display_name', 'Download'), ('is_trashed', '0'),
     ('is_pending', '0')],
    [('_id', '1003'), ('_data', '/storage/emulated/0/Pictures/.trashed-1768000000-old.png'),
     ('_display_name', '.trashed-1768000000-old.png'), ('relative_path', ''), ('volume_name', 'external_primary'),
     ('mime_type', 'image/png'), ('_size', '512'), ('date_added', '0'), ('date_modified', 'NULL'),
     ('datetaken', 'NULL'), ('owner_package_name', 'NULL'), ('bucket_display_name', 'Pictures'),
     ('is_trashed', '1'), ('is_pending', '0')],
)

SETTINGS = rows([('_id', '1'), ('name', 'example_setting'), ('value', '1')])

SECURITY_ERROR = ('Error while accessing provider:com.android.contacts\n'
                  'java.lang.SecurityException: Permission Denial: opening provider '
                  'com.android.providers.contacts.ContactsProvider2 from (null) (pid=12345, uid=2000) requires '
                  'android.permission.READ_CONTACTS or android.permission.WRITE_CONTACTS\n'
                  '\tat android.os.Parcel.createExceptionOrNull(Parcel.java:3011)\n'
                  '\tat android.os.Parcel.createException(Parcel.java:2995)\n')
ARGUMENT_ERROR = ('Error while accessing provider:com.android.calendar\n'
                  'java.lang.IllegalArgumentException: Unknown URL content://com.android.calendar/calendars\n'
                  '\tat android.os.Parcel.createExceptionOrNull(Parcel.java:3017)\n')
ROWS_THEN_ERROR = MEDIA.split('Row: 2 ')[0] + ('Error while accessing provider:media\n'
                                                'java.lang.IllegalStateException: Couldn\'t read row 2, col 0 from '
                                                'CursorWindow\n'
                                                '\tat android.database.CursorWindow.nativeGetLong(Native Method)\n')


def crlf(text):
    return text.replace('\n', '\r\n')


def provider_error(authority, exception):
    return (f'Error while accessing provider:{authority}\n{exception}\n'
            '\tat android.os.Parcel.createExceptionOrNull(Parcel.java:3011)\n')


# MMS rows 7, 8 and 9 as above, and a fourth row with no usable _id (the text NULL).
MMS_WITH_NULL_ID = MMS + ('Row: 3 _id=NULL, thread_id=7, date=1767254400, date_sent=0, msg_box=1, read=1, '
                          'sub=NULL, ct_t=application/vnd.wap.multipart.related, m_type=132, seen=1, sub_id=1, '
                          'creator=com.example.messaging, text_only=1\n')
# Address rows for message 7, one with an empty msg_id and one with msg_id NULL, then a provider
# error: a list that is not complete.
MMS_ADDR_THEN_ERROR = rows(
    [('_id', '30'), ('msg_id', '7'), ('contact_id', 'NULL'), ('address', '+15550100003'), ('type', '137'),
     ('charset', '106'), ('sub_id', '1')],
    [('_id', '31'), ('msg_id', ''), ('contact_id', 'NULL'), ('address', '+15550100007'), ('type', '151'),
     ('charset', '106'), ('sub_id', '1')],
    [('_id', '32'), ('msg_id', 'NULL'), ('contact_id', 'NULL'), ('address', '+15550100008'), ('type', '151'),
     ('charset', '106'), ('sub_id', '1')],
) + provider_error('mms', "java.lang.IllegalStateException: Couldn't read row 3, col 0 from CursorWindow")
# MMS rows for message 7 only, then a provider error.
MMS_THEN_ERROR = MMS.split('Row: 1 ')[0] + provider_error(
    'mms', "java.lang.IllegalStateException: Couldn't read row 1, col 0 from CursorWindow")
# One SMS row whose body holds ', seen=' for the next column: the column list names seen twice.
SMS_ONE_ROW_REPEATED = rows([('_id', '40'), ('address', '+15550100009'), ('date', '1767258000000'),
                             ('type', '1'), ('body', 'the form says, seen=yes'), ('seen', '1')])
# One SMS row whose body holds an error line and an exception line, followed by more columns.
SMS_ERROR_TEXT_IN_BODY = rows([('_id', '41'), ('address', '+15550100010'), ('date', '1767261600000'),
                               ('type', '1'),
                               ('body', 'line one\nError while accessing provider:sms\n'
                                        'java.lang.SecurityException: fake text'),
                               ('read', '1')])


CASES = {
    'alex': {
        f'{ALEX_ROOT}/sms/sms.txt': crlf(SMS),
        f'{ALEX_ROOT}/mms/mms.txt': crlf(MMS),
        f'{ALEX_ROOT}/mms/mms_part.txt': crlf(MMS_PART),
        f'{ALEX_ROOT}/mms/mms_addr.txt': crlf(MMS_ADDR),
        f'{ALEX_ROOT}/call_log/call_log_calls.txt': crlf(CALLS),
        f'{ALEX_ROOT}/com.android.contacts/com.android.contacts_contacts.txt': crlf(CONTACTS),
        f'{ALEX_ROOT}/com.android.contacts/com.android.contacts_data_phones.txt': crlf(PHONES),
        f'{ALEX_ROOT}/com.android.calendar/com.android.calendar_event_entities.txt': crlf(EVENTS),
        f'{ALEX_ROOT}/com.android.calendar/com.android.calendar_calendars.txt': crlf(CALENDARS),
        f'{ALEX_ROOT}/media/media_external_file.txt': crlf(MEDIA),
        f'{ALEX_ROOT}/settings/settings_secure.txt': crlf(SETTINGS),
    },
    'alex_skipped': {
        f'{ALEX_ROOT}/call_log/call_log_calls.txt': CALLS,
        f'{ALEX_ROOT}/mms/mms.txt': MMS,
    },
    'triage': {
        f'{TRIAGE_ROOT}/20261125_10_15_30_contentprovider.txt': '[*] Content Provider Acquisition started\n',
        f'{TRIAGE_ROOT}/content_providers_list.txt': 'Published single-user content providers (by class):\n',
        f'{TRIAGE_ROOT}/contacts_contacts.txt': 'No result found.\n',
        f'{TRIAGE_ROOT}/contacts_data_phones.txt': PHONES,
        f'{TRIAGE_ROOT}/calendar_events.txt': EVENTS,
        f'{TRIAGE_ROOT}/calendar_event_entities.txt': '',
        f'{TRIAGE_ROOT}/calendar_calendars.txt': CALENDARS,
        f'{TRIAGE_ROOT}/media_external_file.txt': MEDIA,
        f'{TRIAGE_ROOT}/settings_secure.txt': SETTINGS,
    },
    'alex_join_incomplete': {
        f'{ALEX_ROOT}/mms/mms.txt': MMS_WITH_NULL_ID,
        f'{ALEX_ROOT}/mms/mms_addr.txt': MMS_ADDR_THEN_ERROR,
    },
    'alex_mms_incomplete': {
        f'{ALEX_ROOT}/mms/mms.txt': MMS_THEN_ERROR,
        f'{ALEX_ROOT}/mms/mms_addr.txt': MMS_ADDR,
    },
    'alex_row_edges': {
        'ALEX_SYNTH0002/content_provider_SYNTH0002/sms/sms.txt': SMS_ONE_ROW_REPEATED,
        'ALEX_SYNTH0003/content_provider_SYNTH0003/sms/sms.txt': SMS_ERROR_TEXT_IN_BODY,
    },
    'triage_stderr': {
        f'{TRIAGE_ROOT}/contacts_contacts.txt': SECURITY_ERROR,
        f'{TRIAGE_ROOT}/contacts_data_phones.txt': SECURITY_ERROR,
        f'{TRIAGE_ROOT}/calendar_calendars.txt': ARGUMENT_ERROR,
        f'{TRIAGE_ROOT}/media_external_file.txt': ROWS_THEN_ERROR,
    },
}


def main(folder):
    os.makedirs(folder, exist_ok=True)
    for case, files in CASES.items():
        path = os.path.join(folder, f'content_query_synthetic_{case}.zip')
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
            for name, text in files.items():
                info = zipfile.ZipInfo(name, ZIP_TIME)
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, text.encode('utf-8'))
        print(os.path.basename(path), os.path.getsize(path))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
