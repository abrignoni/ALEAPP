__artifacts_v2__ = {
    "get_whatsapp_business_contacts": {
        "name": "WhatsApp Business - Contacts",
        "description": "Rows of WhatsApp Business's wa.db wa_contacts table (com.whatsapp.w4b), excluding channel (@newsletter) and status@broadcast jids",
        "author": "@prcharan592",
        "creation_date": "2026-10-04",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "WhatsApp Business",
        "notes": "WhatsApp Business (com.whatsapp.w4b) keeps its own databases, separate from WhatsApp's (com.whatsapp), and this artifact reads only com.whatsapp.w4b. Rows come from the query of WhatsApp - Contacts in WhatsApp.py, run against each com.whatsapp.w4b wa.db, so every column is derived as that artifact's notes describe; the counts quoted in those notes were measured on com.whatsapp and say nothing about this artifact. The run log line counting the rows left out is that query's own and names WhatsApp - Contacts. Every com.whatsapp.w4b app container in the extraction is read: one container under several storage paths (data/data, data/user/0, data_mirror) is read once, and the container of a second Android user adds its own rows. Source File is the wa.db each row was read from, so it holds one value when the extraction carries one container. Exercised on constructed databases only (admin/test/cases/testdata.WhatsAppBusiness.json); no real WhatsApp Business extraction is listed in sample_data.",
        "paths": ('*/com.whatsapp.w4b/databases/wa.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "get_whatsapp_business_call_logs": {
        "name": "WhatsApp Business - Call Logs",
        "description": "WhatsApp Business call logs (com.whatsapp.w4b msgstore.db)",
        "author": "@prcharan592",
        "creation_date": "2026-10-04",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "WhatsApp Business",
        "notes": "WhatsApp Business (com.whatsapp.w4b) keeps its own databases, separate from WhatsApp's (com.whatsapp), and this artifact reads only com.whatsapp.w4b. Rows come from the query of WhatsApp - Call Logs in WhatsApp.py, run against each com.whatsapp.w4b msgstore.db with that container's wa.db attached, so every column is derived as that artifact's notes describe. A call whose jid is a LID jid (...@lid) is matched to wa.db contacts through msgstore.db jid_map when that table exists. With no wa.db in the container the query cannot run and that container reports no calls; the run log says so. Call End Timestamp is not stored: it is the call's timestamp plus its duration read as seconds. On an outgoing call Caller reads Self and Caller JID is blank, and no column names the other party of an outgoing call. Every com.whatsapp.w4b app container in the extraction is read: one container under several storage paths (data/data, data/user/0, data_mirror) is read once, and the container of a second Android user adds its own rows. Source File is the msgstore.db each row was read from, so it holds one value when the extraction carries one container. Exercised on constructed databases only (admin/test/cases/testdata.WhatsAppBusiness.json); no real WhatsApp Business extraction is listed in sample_data.",
        "paths": ('*/com.whatsapp.w4b/databases/msgstore.db*', '*/com.whatsapp.w4b/databases/wa.db*'),
        "output_types": "standard",
        "artifact_icon": "phone",
    },
    "get_whatsapp_business_one_to_one_messages": {
        "name": "WhatsApp Business - One To One Messages",
        "description": "WhatsApp Business messages whose recipient_count is 0, outside channel chats (com.whatsapp.w4b msgstore.db)",
        "author": "@prcharan592",
        "creation_date": "2026-10-04",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "WhatsApp Business",
        "notes": "WhatsApp Business (com.whatsapp.w4b) keeps its own databases, separate from WhatsApp's (com.whatsapp), and this artifact reads only com.whatsapp.w4b. Rows come from the query of WhatsApp - One To One Messages in WhatsApp.py, run against each com.whatsapp.w4b msgstore.db with that container's wa.db attached, so every column is derived as that artifact's notes describe. Rows are selected by message.recipient_count = 0, not by the type of the chat's jid. Message Type shows WhatsApp.py's label for message_type 0, 1, 2, 3, 5, 7, 9 and 16; other values are shown as stored and no source for the labels is cited here. A chat keyed by a LID jid (...@lid) is matched to wa.db contacts through msgstore.db jid_map when that table exists. With no wa.db in the container the query cannot run and that container reports no messages; the run log says so. Messages in channel (newsletter) chats are not reported here, and no WhatsApp Business artifact reports channels. Media is the file whose name matches message_media.file_path among the files matched under WhatsApp Business/Media and com.whatsapp.w4b/files/Media. That recorded path names no Android user, so where two containers hold a media file of the same name, the rows of both show the first one found. Every com.whatsapp.w4b app container in the extraction is read: one container under several storage paths (data/data, data/user/0, data_mirror) is read once, and the container of a second Android user adds its own rows. Source File is the msgstore.db each row was read from, so it holds one value when the extraction carries one container. The conversation view groups rows by Other Participant WA User Name across every container read; Source File tells the containers apart. Exercised on constructed databases only (admin/test/cases/testdata.WhatsAppBusiness.json); no real WhatsApp Business extraction is listed in sample_data.",
        "paths": ('*/com.whatsapp.w4b/databases/msgstore.db*', '*/com.whatsapp.w4b/databases/wa.db*',
                  '*/WhatsApp Business/Media/*', '*/com.whatsapp.w4b/files/Media/*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Other Participant WA User Name",
                "textColumn": "Message",
                "directionColumn": "Message Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Message Timestamp",
                "senderColumn": "Other Participant WA User Name",
                "sentMessageStaticLabel": "Local User",
                "mediaColumn": "Media"
            }
        },
    },
    "get_whatsapp_business_group_messages": {
        "name": "WhatsApp Business - Group Messages",
        "description": "WhatsApp Business messages whose recipient_count is 1 or more (com.whatsapp.w4b msgstore.db)",
        "author": "@prcharan592",
        "creation_date": "2026-10-04",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "WhatsApp Business",
        "notes": "WhatsApp Business (com.whatsapp.w4b) keeps its own databases, separate from WhatsApp's (com.whatsapp), and this artifact reads only com.whatsapp.w4b. Rows come from the query of WhatsApp - Group Messages in WhatsApp.py, run against each com.whatsapp.w4b msgstore.db with that container's wa.db attached, so every column is derived as that artifact's notes describe. Rows are selected by message.recipient_count >= 1, not by the type of the chat's jid. Message Type shows WhatsApp.py's label for message_type 0, 1, 2, 3, 5, 7, 9 and 16; other values are shown as stored and no source for the labels is cited here. A sender keyed by a LID jid (...@lid) is matched to wa.db contacts through msgstore.db jid_map when that table exists. On outgoing rows Sending Party reads Self and Sending Party JID is blank. With no wa.db in the container the query cannot run and that container reports no messages; the run log says so. Media is the file whose name matches message_media.file_path among the files matched under WhatsApp Business/Media and com.whatsapp.w4b/files/Media. That recorded path names no Android user, so where two containers hold a media file of the same name, the rows of both show the first one found. Every com.whatsapp.w4b app container in the extraction is read: one container under several storage paths (data/data, data/user/0, data_mirror) is read once, and the container of a second Android user adds its own rows. Source File is the msgstore.db each row was read from, so it holds one value when the extraction carries one container. The conversation view groups rows by Conversation Name across every container read; Source File tells the containers apart. Exercised on constructed databases only (admin/test/cases/testdata.WhatsAppBusiness.json); no real WhatsApp Business extraction is listed in sample_data.",
        "paths": ('*/com.whatsapp.w4b/databases/msgstore.db*', '*/com.whatsapp.w4b/databases/wa.db*',
                  '*/WhatsApp Business/Media/*', '*/com.whatsapp.w4b/files/Media/*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation Name",
                "textColumn": "Message",
                "directionColumn": "Message Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Message Timestamp",
                "senderColumn": "Sending Party",
                "mediaColumn": "Media"
            }
        },
    },
    "get_whatsapp_business_group_details": {
        "name": "WhatsApp Business - Group Details",
        "description": "WhatsApp Business group chats (com.whatsapp.w4b msgstore.db), with the group creator where wa.db records one and the group picture where the app stored one",
        "author": "@prcharan592",
        "creation_date": "2026-10-04",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "WhatsApp Business",
        "notes": "WhatsApp Business (com.whatsapp.w4b) keeps its own databases, separate from WhatsApp's (com.whatsapp), and this artifact reads only com.whatsapp.w4b. Rows come from the query of WhatsApp - Group Details in WhatsApp.py, run against each com.whatsapp.w4b msgstore.db with that container's wa.db attached, so every column is derived as that artifact's notes describe: one row per chat that carries a subject and is not a channel (@newsletter) chat. Group Creation Timestamp is chat.created_timestamp as stored; whether it marks when the group was created or when the chat was created on this device is not established here. Creator JID is wa.db's wa_group_admin_settings.creator_jid for the chat's jid, blank when wa.db lacks that column or is absent. Group Picture and Creator WA Profile Picture are files in the same container's files/Avatars folder named after the jid followed by .j; the file name is the only link between the file and the group or creator. Every com.whatsapp.w4b app container in the extraction is read: one container under several storage paths (data/data, data/user/0, data_mirror) is read once, and the container of a second Android user adds its own rows. Source File is the msgstore.db each row was read from, so it holds one value when the extraction carries one container. Exercised on constructed databases only (admin/test/cases/testdata.WhatsAppBusiness.json); no real WhatsApp Business extraction is listed in sample_data.",
        "paths": ('*/com.whatsapp.w4b/databases/msgstore.db*', '*/com.whatsapp.w4b/databases/wa.db*',
                  '*/com.whatsapp.w4b/files/Avatars/*'),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "get_whatsapp_business_user_profile": {
        "name": "WhatsApp Business - User Profile",
        "description": "Values of five keys in WhatsApp Business's shared_prefs XML files (com.whatsapp.w4b)",
        "author": "@prcharan592",
        "creation_date": "2026-10-04",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "WhatsApp Business",
        "notes": "One row per com.whatsapp.w4b app container holding at least one of the five keys. Name is the push_name key, User Status my_current_status, Country Code cc, Mobile Number ph and Version version, each as stored in com.whatsapp.w4b_preferences_light.xml or startup_prefs.xml in that container's shared_prefs. The same five keys and two files as WhatsApp - User Profile, with the preferences file named for com.whatsapp.w4b. Where both files hold a non-empty value for a key, the one in com.whatsapp.w4b_preferences_light.xml is used. A row combines values from one container only: one container under several storage paths (data/data, data/user/0, data_mirror) is read once, and the container of a second Android user gives its own row. Source Files names the files in that container that held at least one of the keys. A file that is not well-formed XML is skipped and the run log names it. Exercised on constructed files only (admin/test/cases/testdata.WhatsAppBusiness.json); no real WhatsApp Business extraction is listed in sample_data.",
        "paths": ('*/com.whatsapp.w4b/shared_prefs/com.whatsapp.w4b_preferences_light.xml',
                  '*/com.whatsapp.w4b/shared_prefs/startup_prefs.xml'),
        "output_types": "standard",
        "artifact_icon": "user",
    },
}

import os
from xml.parsers.expat import ExpatError

import xmltodict

from scripts.artifacts import WhatsApp
from scripts.artifacts.storagePathViews import canonical_path, unique_files
from scripts.ilapfuncs import artifact_processor, logfunc

_PACKAGE_SEGMENT = '/com.whatsapp.w4b/'

# The preference files read for the user profile, in the order their values are preferred.
_PROFILE_FILES = ('com.whatsapp.w4b_preferences_light.xml', 'startup_prefs.xml')
_PROFILE_KEYS = ('push_name', 'my_current_status', 'version', 'ph', 'cc')


def _container(context, file_found):
    """The com.whatsapp.w4b app container holding this file, as a key, or None.

    canonical_path replaces the storage view (data/data, data/user/<n>, data_mirror/...)
    with the storage class and Android user it denotes, so both spellings of one
    container give the same key and two different Android users give different ones.
    """
    key, _ = canonical_path(context.get_relative_path(str(file_found)))
    key = str(key).replace('\\', '/')
    index = key.find(_PACKAGE_SEGMENT)
    if index == -1:
        return None
    return key[:index + len(_PACKAGE_SEGMENT)]


def _containers(context):
    """The artifact's files grouped by app container, duplicate storage views removed."""
    containers = {}
    for file_found in unique_files(context):
        key = _container(context, file_found)
        if key is not None:
            containers.setdefault(key, []).append(file_found)
    return containers


def _source_file(context, path):
    return context.get_relative_path(str(path)).replace('\\', '/')


class _ContainerContext:
    """The artifact's context with get_files_found() narrowed to one app container.

    The WhatsApp.py artifact bodies read the first msgstore.db and wa.db they are
    handed, so each is given one container's files at a time.
    """

    def __init__(self, context, files_found):
        self._context = context
        self._files_found = files_found

    def get_files_found(self):
        return self._files_found

    def __getattr__(self, name):
        return getattr(self._context, name)


def _per_container(context, whatsapp_artifact, store):
    """Run a WhatsApp.py artifact's body once per container that holds `store`.

    Each row gains a Source File column naming the database it was read from.
    """
    body = whatsapp_artifact.__wrapped__
    data_headers, data_list, sources = None, [], []
    for files in _containers(context).values():
        if not any(os.path.basename(str(f)) == store for f in files):
            continue
        data_headers, rows, source = body(_ContainerContext(context, files))
        source_file = _source_file(context, source)
        data_list.extend(tuple(row) + (source_file,) for row in rows)
        sources.append(source)
    if data_headers is None:
        # No container holds the store: the body, given no files, still names its columns.
        data_headers, _rows, _source = body(_ContainerContext(context, []))
    return tuple(data_headers) + ('Source File',), data_list, '\n'.join(sources)


@artifact_processor
def get_whatsapp_business_contacts(context):
    return _per_container(context, WhatsApp.get_whatsapp_contacts, 'wa.db')


@artifact_processor
def get_whatsapp_business_call_logs(context):
    return _per_container(context, WhatsApp.get_whatsapp_call_logs, 'msgstore.db')


@artifact_processor
def get_whatsapp_business_one_to_one_messages(context):
    return _per_container(context, WhatsApp.get_whatsapp_one_to_one_messages, 'msgstore.db')


@artifact_processor
def get_whatsapp_business_group_messages(context):
    return _per_container(context, WhatsApp.get_whatsapp_group_messages, 'msgstore.db')


@artifact_processor
def get_whatsapp_business_group_details(context):
    return _per_container(context, WhatsApp.get_whatsapp_group_details, 'msgstore.db')


def _profile_strings(file_found):
    """The <string> entries of a shared_prefs file, or None when it cannot be parsed."""
    try:
        with open(file_found, encoding='utf-8') as fd:
            xml_dict = xmltodict.parse(fd.read())
    except (OSError, ValueError, ExpatError) as exc:
        logfunc(f'WhatsApp Business - User Profile: {os.path.basename(str(file_found))} not read, {exc}')
        return None
    strings = (xml_dict.get('map') or {}).get('string') or []
    if isinstance(strings, dict):
        strings = [strings]
    return [entry for entry in strings if isinstance(entry, dict)]


@artifact_processor
def get_whatsapp_business_user_profile(context):
    data_list, sources = [], []
    for files in _containers(context).values():
        prefs = [f for f in files if os.path.basename(str(f)) in _PROFILE_FILES and os.path.isfile(f)]
        prefs.sort(key=lambda f: _PROFILE_FILES.index(os.path.basename(str(f))))
        data = dict.fromkeys(_PROFILE_KEYS, '')
        read = []
        for file_found in prefs:
            entries = _profile_strings(file_found)
            if entries is None:
                continue
            held = False
            for entry in entries:
                name = entry.get('@name')
                if name in data:
                    held = True
                    if not data[name]:
                        data[name] = entry.get('#text', '')
            if held:
                read.append(file_found)
        if any(data.values()):
            data_list.append((data['version'], data['push_name'], data['my_current_status'], data['cc'],
                              data['ph'], '; '.join(_source_file(context, f) for f in read)))
            sources.extend(read)

    data_headers = ('Version', 'Name', 'User Status', 'Country Code', 'Mobile Number', 'Source Files')
    return data_headers, data_list, '\n'.join(sources)
