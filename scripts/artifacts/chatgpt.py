__artifacts_v2__ = {
    "get_chatgpt": {
        "name": "ChatGPT - Conversations Metadata",
        "description": "Metadata related to the user's ChatGPT conversations. Validated up to app 1.2024.177.",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-09",
        "last_update_date": "2024-07-09",
        "requirements": "",
        "category": "ChatGPT",
        "notes": "",
        "paths": ('**/com.openai.chatgpt/databases/*_conversations.db*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
    },
    "get_chatgpt_conversations": {
        "name": "ChatGPT - Messages (Legacy)",
        "description": "User messages with ChatGPT, older DBMessage.messageNode schema (see ChatGPT - Conversations / chatgpt2 for the newer DBMessageChunk schema)",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-09",
        "last_update_date": "2024-07-09",
        "requirements": "",
        "category": "ChatGPT",
        "notes": "",
        "paths": ('**/com.openai.chatgpt/databases/*_conversations.db*',),
        "output_types": "standard",
        "artifact_icon": "message-circle",
    },
    "get_chatgpt_user": {
        "name": "ChatGPT - User",
        "description": "ChatGPT user preferences (user.preferences_pb)",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-09",
        "last_update_date": "2024-07-09",
        "requirements": "",
        "category": "ChatGPT",
        "notes": "",
        "paths": ('**/com.openai.chatgpt/files/datastore/*_user.preferences_pb',),
        "output_types": "standard",
        "artifact_icon": "user",
    },
    "get_chatgpt_accountstatus": {
        "name": "ChatGPT - Account Status",
        "description": "ChatGPT account status preferences (accountstatus.preferences_pb)",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-09",
        "last_update_date": "2024-07-09",
        "requirements": "",
        "category": "ChatGPT",
        "notes": "",
        "paths": ('**/com.openai.chatgpt/files/datastore/*_accountstatus.preferences_pb',),
        "output_types": "standard",
        "artifact_icon": "user-check",
    },
    "get_chatgpt_accountuserstate": {
        "name": "ChatGPT - Account User State",
        "description": "ChatGPT account user state preferences (accountuser_state.preferences_pb)",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-09",
        "last_update_date": "2024-07-09",
        "requirements": "",
        "category": "ChatGPT",
        "notes": "",
        "paths": ('**/com.openai.chatgpt/files/datastore/*_accountuser_state.preferences_pb',),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "get_chatgpt_custominstructions": {
        "name": "ChatGPT - Custom Instructions",
        "description": "User-provided custom instructions for ChatGPT (custom_instructions.preferences_pb)",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-09",
        "last_update_date": "2024-07-09",
        "requirements": "",
        "category": "ChatGPT",
        "notes": "",
        "paths": ('**/com.openai.chatgpt/files/datastore/*_custom_instructions.preferences_pb',),
        "output_types": "standard",
        "artifact_icon": "edit",
    },
    "get_chatgpt_usersettings": {
        "name": "ChatGPT - User Settings",
        "description": "ChatGPT user settings (user_settings.preferences_pb)",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-09",
        "last_update_date": "2024-07-09",
        "requirements": "",
        "category": "ChatGPT",
        "notes": "",
        "paths": ('**/com.openai.chatgpt/files/datastore/*_user_settings.preferences_pb',),
        "output_types": "standard",
        "artifact_icon": "settings",
    },
    "get_chatgpt_analytics": {
        "name": "ChatGPT - User Analytics",
        "description": "ChatGPT analytics user/device traits (analytics-android-oai.xml)",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-09",
        "last_update_date": "2024-07-09",
        "requirements": "",
        "category": "ChatGPT",
        "notes": "",
        "paths": ('**/com.openai.chatgpt/shared_prefs/analytics-android-oai.xml',),
        "output_types": "standard",
        "artifact_icon": "bar-chart-2",
    },
    "get_chatgpt_media": {
        "name": "ChatGPT - Media Uploads",
        "description": "Images uploaded to / cached by ChatGPT",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "creation_date": "2024-07-09",
        "last_update_date": "2024-07-09",
        "requirements": "",
        "category": "ChatGPT",
        "notes": "",
        "paths": ('**/com.openai.chatgpt/cache/files/*',),
        "output_types": "standard",
        "artifact_icon": "image",
    }
}

import datetime
import json
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

import blackboxprotobuf
from PIL import Image, UnidentifiedImageError

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly, check_in_media


def _iso_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(datetime.timezone.utc)
    except (ValueError, TypeError, AttributeError):
        return ''


def _sec_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _account(file_name, suffix):
    return file_name[:-len(suffix)] if file_name.endswith(suffix) else file_name


def _pb_json(file_found):
    '''Decode a *.preferences_pb file and return the embedded JSON dict (or None).'''
    try:
        with open(file_found, 'rb') as f:
            values, _ = blackboxprotobuf.decode_message(f.read())
        if isinstance(values, dict):
            pb = values.get('1', {}).get('2', {}).get('5', b'{}')
            return json.loads(pb.decode('utf-8'))
    except (ValueError, KeyError, TypeError, AttributeError, UnicodeDecodeError) as ex:
        logfunc(f'ChatGPT: error parsing {os.path.basename(file_found)} protobuf: {ex}')
    return None


def _is_image(file_path):
    try:
        with Image.open(file_path):
            return True
    except (UnidentifiedImageError, OSError):
        return False


@artifact_processor
def get_chatgpt(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('_conversations.db'):
            continue
        source_path = file_found
        account = _account(os.path.basename(file_found), '_conversations.db')
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
            SELECT id, json_extract(conversation, '$.id'), json_extract(conversation, '$.remote_id'),
            json_extract(conversation, '$.creation_date'), json_extract(conversation, '$.modification_date'),
            json_extract(conversation, '$.title'), json_extract(conversation, '$.moderation_results'),
            json_extract(conversation, '$.gizmo_id'),
            CASE WHEN json_extract(conversation, '$.has_title') = true THEN 'Yes' ELSE 'No' END
            FROM DBConversation
        ''')
        for row in cursor.fetchall():
            data_list.append((account, _iso_to_utc(row[3]), _iso_to_utc(row[4]), row[5], row[6], row[7],
                              row[0], row[1], row[2]))
        db.close()

    data_headers = ('Account', ('Creation Date', 'datetime'), ('Modification Date', 'datetime'), 'Title',
                    'Custom Instructions', 'Model', 'ID', 'Conversation ID', 'Remote ID')
    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def get_chatgpt_conversations(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('_conversations.db'):
            continue
        source_path = file_found
        account = _account(os.path.basename(file_found), '_conversations.db')
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
            SELECT DBMessage.id, DBMessage.conversationId,
            json_extract(DBConversation.conversation, '$.title'),
            json_extract(DBMessage.messageNode, '$.content.role'),
            json_extract(DBMessage.messageNode, '$.content.content.content'),
            json_extract(DBMessage.messageNode, '$.content.date'),
            json_extract(DBMessage.messageNode, '$.content.role_name'),
            json_extract(DBMessage.messageNode, '$.content.attachments'),
            json_extract(DBMessage.messageNode, '$.content.model'),
            CASE WHEN json_extract(DBMessage.messageNode, '$.content.is_complete') = true THEN 'Yes' ELSE 'No' END,
            CASE WHEN json_extract(DBMessage.messageNode, '$.content.is_blocked') = true THEN 'Yes' ELSE 'No' END,
            CASE WHEN json_extract(DBMessage.messageNode, '$.content.is_flagged') = true THEN 'Yes' ELSE 'No' END,
            CASE WHEN json_extract(DBMessage.messageNode, '$.content.is_interrupted') = true THEN 'Yes' ELSE 'No' END,
            CASE WHEN json_extract(DBMessage.messageNode, '$.content.is_user_system_message') = true THEN 'Yes' ELSE 'No' END,
            CASE WHEN json_extract(DBMessage.messageNode, '$.content.is_voice_message') = true THEN 'Yes' ELSE 'No' END
            FROM DBMessage JOIN DBConversation ON DBMessage.conversationId = DBConversation.id
        ''')
        for row in cursor.fetchall():
            data_list.append((account, _iso_to_utc(row[5]), row[0], row[1], row[2], row[3], row[4], row[6],
                              row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14]))
        db.close()

    data_headers = ('Account', ('Message Date', 'datetime'), 'Message ID', 'Conversation ID', 'Title', 'Role',
                    'Content', 'Role Name', 'Attachments', 'Model', 'Complete', 'Blocked', 'Flagged',
                    'Interrupted', 'User System Message', 'Voice Message')
    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def get_chatgpt_user(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('_user.preferences_pb'):
            continue
        source_path = file_found
        info = _pb_json(file_found)
        if info:
            data_list.append((info.get('id'), info.get('email', ''), info.get('name', ''),
                              _sec_to_utc(info.get('created', 0)), info.get('picture', '')))

    data_headers = ('User-ID', 'Email', 'Name', ('Account Creation Time', 'datetime'), 'Picture')
    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def get_chatgpt_accountstatus(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('_accountstatus.preferences_pb'):
            continue
        source_path = file_found
        info = _pb_json(file_found)
        for key, account in (info or {}).get('accounts', {}).items():
            subscription = account.get('subscription', {})
            data_list.append((key, account.get('account_id'), account.get('account_user_id'),
                              subscription.get('plan', ''), account.get('plan_type', ''),
                              subscription.get('purchase_origin', ''), subscription.get('will_renew', False),
                              account.get('structure', ''), account.get('is_deactivated', False)))

    data_headers = ('Account', 'Account-ID', 'Account-User-ID', 'Subscription Plan', 'Plan Type',
                    'Subscription Purchase Origin', 'Subscription Will Renew', 'Structure', 'Is Deactivated')
    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def get_chatgpt_accountuserstate(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('_accountuser_state.preferences_pb'):
            continue
        source_path = file_found
        info = _pb_json(file_found)
        if not info:
            continue
        active_account_id = info.get('active_account_id')
        for entry in info.get('available_account_users', []):
            account = entry.get('account', {})
            user = entry.get('user', {})
            subscription = account.get('subscription', {})
            data_list.append((
                'Yes' if active_account_id == account.get('account_id') else 'No',
                account.get('account_id'), user.get('id'), account.get('account_user_id'),
                user.get('email', ''), user.get('name', ''), _sec_to_utc(user.get('created', 0)),
                subscription.get('plan', ''), account.get('plan_type', ''),
                subscription.get('purchase_origin', ''), subscription.get('will_renew', False),
                subscription.get('expiration_date', ''), account.get('structure', ''),
                account.get('is_deactivated', False), user.get('picture', '')))

    data_headers = ('Is Active Account', 'Account-ID', 'User-ID', 'Account-User-ID', 'Email', 'Name',
                    ('Account Creation Time', 'datetime'), 'Subscription Plan', 'Plan Type',
                    'Subscription Purchase Origin', 'Subscription Will Renew', 'Plan Expiration Date',
                    'Structure', 'Is Deactivated', 'Picture')
    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def get_chatgpt_custominstructions(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('_custom_instructions.preferences_pb'):
            continue
        source_path = file_found
        info = _pb_json(file_found)
        if info:
            data_list.append((info.get('enabled', False), info.get('about_user_message', ''),
                              info.get('about_model_message', '')))

    data_headers = ('Are Enabled', 'About User Message', 'About Model Message')
    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def get_chatgpt_usersettings(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('_user_settings.preferences_pb'):
            continue
        source_path = file_found
        info = _pb_json(file_found)
        if info:
            data_list.append((info.get('history_disabled', False),
                              info.get('seen_custom_instructions_introduction', False),
                              info.get('has_seen_voice_intro', False),
                              info.get('has_seen_voice_selection', False)))

    data_headers = ('Chat History Disabled', 'Seen Custom Instructions Intro', 'Seen Voice Intro',
                    'Seen Voice Selection')
    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def get_chatgpt_analytics(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if os.path.basename(file_found) != 'analytics-android-oai.xml':
            continue
        source_path = file_found
        try:
            root = ET.parse(file_found).getroot()
        except ET.ParseError:
            with open(file_found, 'r', encoding='utf-8', errors='replace') as f:
                text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', f.read())
            try:
                root = ET.fromstring(text)
            except ET.ParseError:
                continue
        prefs = {elem.get('name'): elem.text for elem in root.findall('string')}
        try:
            traits = json.loads(prefs['segment.traits'])
            data_list.append((prefs.get('segment.userId'), prefs.get('segment.anonymousId'),
                              traits.get('email'), prefs.get('segment.device.id'), traits.get('workspace_id'),
                              traits.get('account_has_plus'), traits.get('plan_type'),
                              traits.get('has_active_subscription'), prefs.get('segment.app.version')))
        except (KeyError, ValueError, TypeError) as ex:
            logfunc(f'ChatGPT: error parsing analytics XML: {ex}')

    data_headers = ('User-ID', 'Anonymous-ID', 'Email', 'Device-ID', 'Workspace-ID', 'Account Has Plus',
                    'Plan Type', 'Has Active Subscription', 'App Version')
    return data_headers, data_list, context.get_relative_path(source_path)


@artifact_processor
def get_chatgpt_media(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.isfile(file_found) or not ('cache' in file_found and 'files' in file_found):
            continue
        if not _is_image(file_found):
            continue
        name = os.path.basename(file_found)
        source_path = str(Path(file_found).parents[1])
        data_list.append((check_in_media(file_found, name), name, context.get_relative_path(file_found)))

    data_headers = (('Thumbnail', 'media'), 'Filename', 'Location')
    return data_headers, data_list, context.get_relative_path(source_path)
