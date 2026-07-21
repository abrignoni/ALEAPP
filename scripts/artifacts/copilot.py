# Microsoft Copilot App (com.microsoft.copilot)
# Author: Dolly Aswin Harahap <dolly.aswin@gmail.com> 
#
# Tested with the following versions:
# 2026-05-09: Android 10, App 30.0.440505001
#
# Requirements: json, xml

__artifacts_v2__ = {
    "copilot_account": {
        "name": "Microsoft Copilot - Account",
        "description": "Existing account in Microsoft Copilot App.",
        "author": "[Nama Anda]",
        "version": "0.1",
        "creation_date": "2026-05-09",
        "last_update_date": "2026-05-09",
        "requirements": "xml, json",
        "category": "Microsoft Copilot",
        "notes": "",
        "paths": ('*/com.microsoft.copilot/shared_prefs/com.microsoft.oneauth.accounts.xml'),
        "output_types": "standard",
        "artifact_icon": "user"
    },
    "copilot_sessions": {
        "name": "Microsoft Copilot - Sessions",
        "description": "List of conversation sessions in Microsoft Copilot App.",
        "author": "[Nama Anda]",
        "version": "0.1",
        "creation_date": "2026-05-09",
        "last_update_date": "2026-05-09",
        "requirements": "json",
        "category": "Microsoft Copilot",
        "notes": "",
        "paths": ('*/com.microsoft.copilot/files/offline_cache/offline_sessions.json'),
        "output_types": "standard",
        "artifact_icon": "list"
    },
    "copilot_messages": {
        "name": "Microsoft Copilot - Messages",
        "description": "Conversation messages from Microsoft Copilot App.",
        "author": "[Nama Anda]",
        "version": "0.1",
        "creation_date": "2026-05-09",
        "last_update_date": "2026-05-09",
        "requirements": "json",
        "category": "Microsoft Copilot",
        "notes": "",
        "paths": ('*/com.microsoft.copilot/files/offline_cache/offline_conv_*.json'),
        "output_types": "standard",
        "artifact_icon": "message-square"
    }
}

import json
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc


# ─────────────────────────────────────────────
#  ARTIFACT 1 — copilot_account
#  Sumber: com.microsoft.oneauth.accounts.xml
# ─────────────────────────────────────────────

@artifact_processor
def copilot_account(files_found, _report_folder, _seeker, _wrap_text):

    # Baca dan parse file XML SharedPreferences
    xml_dict = {}
    with open(files_found[0], 'rb') as xml_file:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for elem in root:
            name = elem.attrib.get('name')
            value = elem.attrib.get('value') if 'value' in elem.attrib else elem.text
            xml_dict[name] = value

    data_list = []

    # Setiap key pada xml_dict adalah satu akun (key = account_id)
    for account_key, account_raw in xml_dict.items():

        # Parse JSON level pertama — data utama akun
        try:
            account_data = json.loads(account_raw)
        except (json.JSONDecodeError, TypeError):
            continue

        # Ekstrak field utama akun
        account_id      = account_data.get('id', '')
        display_name    = account_data.get('display_name', '')
        first_name      = account_data.get('first_name', '')
        last_name       = account_data.get('last_name', '')
        email           = account_data.get('email', '')
        login_name      = account_data.get('login_name', '')
        account_type    = account_data.get('account_type', '')
        birthday        = account_data.get('birthday', '')
        location        = account_data.get('location', '')
        realm_name      = account_data.get('realm_name', '')
        sovereignty     = account_data.get('sovereignty', '')

        # Parse JSON level kedua — additional_properties (berisi token iat & exp)
        token_issued    = ''
        token_expired   = ''
        try:
            additional_props = json.loads(account_data.get('additional_properties', '{}'))
            iat = additional_props.get('iat', '')
            exp = additional_props.get('exp', '')
            if iat:
                token_issued = convert_unix_ts_to_utc(int(iat))
            if exp:
                token_expired = convert_unix_ts_to_utc(int(exp))
        except (json.JSONDecodeError, TypeError, ValueError):
            pass

        data_list.append((
            account_id,
            display_name,
            first_name,
            last_name,
            email,
            login_name,
            account_type,
            birthday,
            location,
            realm_name,
            sovereignty,
            token_issued,
            token_expired
        ))

    data_headers = (
        'Account ID',
        'Display Name',
        'First Name',
        'Last Name',
        'Email',
        'Login Name',
        'Account Type',
        'Birthday',
        'Location',
        'Realm Name',
        'Sovereignty',
        ('Token Issued', 'datetime'),
        ('Token Expired', 'datetime')
    )

    return data_headers, data_list, files_found[0]


# ─────────────────────────────────────────────
#  ARTIFACT 2 — copilot_sessions
#  Sumber: offline_sessions.json
# ─────────────────────────────────────────────

@artifact_processor
def copilot_sessions(files_found, _report_folder, _seeker, _wrap_text):

    data_list = []

    with open(files_found[0], 'r', encoding='utf-8') as json_file:
        raw_data = json.loads(json_file.read())

    sessions = raw_data.get('sessions', [])

    for session in sessions:
        session_id  = session.get('id', '')
        title       = session.get('title', '')
        updated_at  = session.get('updatedAt', '')   # sudah ISO 8601, tidak perlu konversi
        session_type = session.get('type', '')
        is_pinned   = session.get('isPinned', False)

        data_list.append((
            session_id,
            title,
            updated_at,
            session_type,
            is_pinned
        ))

    data_headers = (
        'Session ID',
        'Title',
        'Updated At',
        'Type',
        'Is Pinned'
    )

    return data_headers, data_list, files_found[0]


# ─────────────────────────────────────────────
#  ARTIFACT 3 — copilot_messages
#  Sumber: offline_conv_*.json (multi-file)
# ─────────────────────────────────────────────

@artifact_processor
def copilot_messages(files_found, _report_folder, _seeker, _wrap_text):

    data_list = []

    for file_path in files_found:

        with open(file_path, 'r', encoding='utf-8') as json_file:
            try:
                raw_data = json.loads(json_file.read())
            except (json.JSONDecodeError, TypeError):
                continue

        conversation_id = raw_data.get('conversationId', '')
        messages        = raw_data.get('messages', [])

        for message in messages:
            message_id  = message.get('id', '')
            author      = message.get('author', '')      # 'human' atau 'ai'
            channel     = message.get('channel', '')
            created_at  = message.get('createdAt', '')   # sudah ISO 8601

            # Teks pesan tersimpan di dalam array content[0]['text']
            message_text = ''
            try:
                content = message.get('content', [])
                if content:
                    message_text = content[0].get('text', '')
            except (IndexError, TypeError, AttributeError):
                pass

            data_list.append((
                conversation_id,
                message_id,
                created_at,
                author,
                channel,
                message_text
            ))

    data_headers = (
        'Conversation ID',
        'Message ID',
        'Created At',
        'Author',
        'Channel',
        'Message'
    )

    return data_headers, data_list, files_found[0]
