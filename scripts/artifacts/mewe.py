import xml.etree.ElementTree as ET

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly

APP_NAME = 'MeWe'
DB_NAME = 'app_database'
SGSESSION_FILE = 'SGSession.xml'
CHAT_MESSAGES_QUERY = '''
    SELECT
        DATETIME(createdAt, 'unixepoch'),
        threadId,
        groupId,
        ownerId,
        ownerName,
        textPlain,
        CASE currentUserMessage
            WHEN 1 THEN "Sent"
            ELSE "Received"
        END currentUserMessage,
        CASE attachmentType
            WHEN "UNSUPPORTED" THEN ''
            ELSE attachmentType
        END attachmentType,
        attachmentName,
        CASE deleted
            WHEN 1 THEN "YES"
            ELSE "NO"
        END deleted
    FROM CHAT_MESSAGE
    JOIN CHAT_THREAD ON threadId = CHAT_THREAD.id
'''

def _perform_query(cursor, query):
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        return len(rows), rows
    except:
        return 0, None


def _make_reports(title, data_headers, data_list, report_folder, db_file_name, tl_bool):
    report = ArtifactHtmlReport(title)
    report.start_artifact_report(report_folder, title)
    report.add_script()
    report.write_artifact_data_table(data_headers, data_list, db_file_name)
    report.end_artifact_report()

    tsv(report_folder, data_headers, data_list, title, db_file_name)

    if tl_bool == True:
        timeline(report_folder, title, data_list, data_headers)


def _parse_xml(xml_file, xml_file_name, report_folder, title, report_name):
    logfunc(f'{title} found')

    tree = ET.parse(xml_file)
    data_headers = ('Key', 'Value')
    data_list = []

    root = tree.getroot()
    for node in root:
        # skip not relevant keys
        if '.' in node.attrib['name']:
            continue

        value = None
        try:
            value = node.attrib['value']
        except:
            value = node.text
            
        data_list.append((node.attrib['name'], value))

    tl_bool = False
    
    _make_reports(f'{APP_NAME} - {report_name}', data_headers, data_list, report_folder, xml_file_name, tl_bool)


def _parse_chat_messages(messages_count, rows, report_folder, db_file_name):
    logfunc(f'{messages_count} messages found')

    data_headers = (
        'Timestamp', 'Thread Id', 'Thread Name', 'User Id', 'User Name',
        'Message Text', 'Message Direction', 'Message Type',
        'Attachment Name', 'Deleted'
    )
    data_list = [(
        row[0], row[1], row[2], row[3], row[4], row[5],
        row[6], row[7], row[8] if row[8] else '', row[9]
    ) for row in rows]

    tl_bool = True

    _make_reports(f'{APP_NAME} - Chat', data_headers, data_list, report_folder, db_file_name, tl_bool)


def _parse_app_database(db_file, db_file_name, report_folder):
    db = open_sqlite_db_readonly(db_file)
    cursor = db.cursor()

    messages_count, rows = _perform_query(cursor, CHAT_MESSAGES_QUERY)
    if messages_count > 0 and rows:
        _parse_chat_messages(messages_count, rows, report_folder, db_file_name)
    else:
        logfunc(f'No {APP_NAME} chat data found')

    cursor.close()
    db.close()


def get_mewe(files_found, report_folder, seeker, wrap_text):
    db_file = None
    db_file_name = None
    xml_file = None
    xml_file_name = None
    
    app_database_processed = False
    sgsession_processed = False

    for ff in files_found:
        if ff.endswith(DB_NAME) and not app_database_processed:
            db_file = ff
            db_file_name = ff.replace(seeker.data_folder, '')
            _parse_app_database(db_file, db_file_name, report_folder)
            app_database_processed = True
        if ff.endswith(SGSESSION_FILE) and not sgsession_processed:
            xml_file = ff
            xml_file_name = ff.replace(seeker.data_folder, '')
            _parse_xml(xml_file, xml_file_name, report_folder, SGSESSION_FILE, 'SGSession')
            sgsession_processed = True
            
    artifacts = [
        app_database_processed, sgsession_processed
    ]
    if not (True in artifacts):
        logfunc(f'{APP_NAME} data not found')

__artifacts__ = {
        "mewe": (
                "MeWe",
                ('*/com.mewe/databases/app_database', '*/com.mewe/shared_prefs/SGSession.xml'),
                get_mewe)
}