# pylint: disable=W0613,W0718
__artifacts_v2__ = {
    "get_googleCallScreen": {
        "name": "Google Call Screen",
        "description": "Transcripts and recordings from Google Assistant's Call Screen feature",
        "author": "",
        "creation_date": "2021-08-06",
        "last_update_date": "2021-08-06",
        "requirements": "none",
        "category": "Google Call Screen",
        "notes": "",
        "paths": ('*/com.google.android.dialer/databases/callscreen_transcripts*',
                  '*/com.google.android.dialer/files/callscreenrecordings/*.*'),
        "output_types": "standard",
        "artifact_icon": "phone",
    }
}

import datetime
import os

import blackboxprotobuf

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, check_in_media

PB_TYPES = {'1': {'type': 'message', 'message_typedef': {
    '1': {'name': 'timestamp1', 'type': 'int'},
    '2': {'name': '', 'type': 'int'},
    '3': {'name': 'convo_text', 'type': 'str'},
    '4': {'name': '', 'type': 'int'},
    '5': {'name': '', 'type': 'int'},
    '6': {'name': '', 'type': 'bytes'},
    '7': {'name': '', 'type': 'int'},
    '9': {'name': '', 'type': 'int'}}, 'name': ''}}


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


@artifact_processor
def get_googleCallScreen(files_found, report_folder, seeker, wrap_text):
    source_path = ''
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('callscreen_transcripts'):
            continue
        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
            SELECT lastModifiedMillis, audioRecordingFilePath, conversation, id,
            replace(audioRecordingFilePath, rtrim(audioRecordingFilePath, replace(audioRecordingFilePath, '/', '')), '')
            FROM Transcript
        ''')
        rows = cursor.fetchall()
        db.close()

        for row in rows:
            recording_filename = row[4]
            # Decode the transcript protobuf into a plain-text conversation
            conversation = ''
            try:
                data, _ = blackboxprotobuf.decode_message(row[2], PB_TYPES)
                messages = data.get('1', [])
                if isinstance(messages, dict):
                    messages = [messages]
                lines = []
                for message in messages:
                    msg_time = _ms_to_utc(message.get('timestamp1'))
                    stamp = msg_time.strftime('%Y-%m-%d %H:%M:%S') if msg_time else ''
                    lines.append(f"{stamp}: {message.get('convo_text', '')}")
                conversation = '\n'.join(lines)
            except Exception:
                conversation = ''

            # The screened-call audio recording
            audio = ''
            if recording_filename:
                match = next((str(f) for f in files_found if str(recording_filename) in str(f)), None)
                if match:
                    audio = check_in_media(match, os.path.basename(match))

            data_list.append((_ms_to_utc(row[0]), row[1], conversation, audio))

    data_headers = (('Timestamp', 'datetime'), 'Recording File Path', 'Conversation', ('Audio', 'media'))
    return data_headers, data_list, source_path
