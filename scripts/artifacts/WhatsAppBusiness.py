__artifacts_v2__ = {
    "get_whatsapp_business_contacts": {
        "name": "WhatsApp Business - Contacts",
        "description": "Rows of WhatsApp Business's wa.db wa_contacts table (name columns, wa_name, jid, number and status text), excluding channel (@newsletter) and status@broadcast jids",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "WhatsApp Business",
        "notes": "Reads the com.whatsapp.w4b copy of wa.db with the same code as WhatsApp - Contacts, whose notes describe the columns and the rows left out. The two apps keep separate stores, so a device with both installed gives separate rows under each artifact. "
                 "Validation boundary: no WhatsApp Business extraction was available when this was written. The paths (com.whatsapp.w4b/databases/wa.db) follow the app's package name and the code is shared with the tested WhatsApp artifact, but it has been run against constructed databases only. Whether WhatsApp Business writes extra tables or columns here that are not read is not established. Business-only data (business profile, labels, quick replies, catalog) is not parsed.",
        "paths": ('*/com.whatsapp.w4b/databases/wa.db*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {},
    },
    "get_whatsapp_business_call_logs": {
        "name": "WhatsApp Business - Call Logs",
        "description": "WhatsApp Business call logs (msgstore.db)",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "WhatsApp Business",
        "notes": "Reads the com.whatsapp.w4b copies of msgstore.db and wa.db with the same code as WhatsApp - Call Logs, whose notes describe the columns, the jid_map lookup for LID jids and the case of a missing wa.db. "
                 "Validation boundary: no WhatsApp Business extraction was available when this was written; the code is shared with the tested WhatsApp artifact and has been run against constructed databases only.",
        "paths": ('*/com.whatsapp.w4b/databases/msgstore.db*', '*/com.whatsapp.w4b/databases/wa.db*'),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {},
    },
    "get_whatsapp_business_messages": {
        "name": "WhatsApp Business - Messages",
        "description": "WhatsApp Business messages (legacy msgstore.db schema with messages.data)",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "WhatsApp Business",
        "notes": "Reads the com.whatsapp.w4b copies of msgstore.db and wa.db with the same code as WhatsApp - Messages, whose notes describe the legacy schema this reads. A msgstore.db without a messages table that has a data column reports no rows here; the One To One and Group Messages artifacts read the modern schema. "
                 "Validation boundary: no WhatsApp Business extraction was available when this was written; the code is shared with the tested WhatsApp artifact and has been run against constructed databases only.",
        "paths": ('*/com.whatsapp.w4b/databases/msgstore.db*', '*/com.whatsapp.w4b/databases/wa.db*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {},
    },
    "get_whatsapp_business_one_to_one_messages": {
        "name": "WhatsApp Business - One To One Messages",
        "description": "WhatsApp Business messages in chats whose jid is not a group (@g.us) or channel (@newsletter) jid (modern msgstore.db schema)",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "WhatsApp Business",
        "notes": "Reads the com.whatsapp.w4b copies of msgstore.db and wa.db with the same code as WhatsApp - One To One Messages, whose notes describe how rows are selected, the jid_map lookup for chats keyed by a LID jid and the columns. Media is linked from the WhatsApp Business media folders listed in the paths. The location of those folders (Android/media/com.whatsapp.w4b/WhatsApp Business/Media on Android 11 and later, WhatsApp Business/Media on shared storage before that) is taken from the app's folder naming and was not seen in an extraction. "
                 "Validation boundary: no WhatsApp Business extraction was available when this was written; the code is shared with the tested WhatsApp artifact and has been run against constructed databases only.",
        "paths": ('*/com.whatsapp.w4b/databases/msgstore.db*', '*/com.whatsapp.w4b/databases/wa.db*',
                  '*/WhatsApp Business/Media/*', '*/com.whatsapp.w4b/files/Media/*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {},
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Other Participant JID",
                "conversationLabelColumn": "Other Participant WA User Name",
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
        "description": "WhatsApp Business messages in chats whose jid is a group (@g.us) jid (modern msgstore.db schema)",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "WhatsApp Business",
        "notes": "Reads the com.whatsapp.w4b copies of msgstore.db and wa.db with the same code as WhatsApp - Group Messages, whose notes describe how rows are selected, the jid_map lookup for senders recorded as LID jids and the columns. Media is linked from the WhatsApp Business media folders listed in the paths, whose location was not seen in an extraction (see WhatsApp Business - One To One Messages). "
                 "Validation boundary: no WhatsApp Business extraction was available when this was written; the code is shared with the tested WhatsApp artifact and has been run against constructed databases only.",
        "paths": ('*/com.whatsapp.w4b/databases/msgstore.db*', '*/com.whatsapp.w4b/databases/wa.db*',
                  '*/WhatsApp Business/Media/*', '*/com.whatsapp.w4b/files/Media/*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {},
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Group JID",
                "conversationLabelColumn": "Conversation Name",
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
        "description": "WhatsApp Business group chats (chats with a subject in msgstore.db other than channels), with the group creator where wa.db records one and the group picture where the app stored one",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "WhatsApp Business",
        "notes": "Reads the com.whatsapp.w4b copies of msgstore.db and wa.db, and the pictures in com.whatsapp.w4b/files/Avatars, with the same code as WhatsApp - Group Details, whose notes describe the columns, the Chat Created Timestamp and the jid_map lookup for a creator recorded as a LID jid. "
                 "Validation boundary: no WhatsApp Business extraction was available when this was written; the code is shared with the tested WhatsApp artifact and has been run against constructed databases only. That the Avatars folder exists under com.whatsapp.w4b with the same file naming as in com.whatsapp is assumed, not seen.",
        "paths": ('*/com.whatsapp.w4b/databases/msgstore.db*', '*/com.whatsapp.w4b/databases/wa.db*',
                  '*/com.whatsapp.w4b/files/Avatars/*'),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {},
    },
    "get_whatsapp_business_channels": {
        "name": "WhatsApp Business - Channels",
        "description": "WhatsApp Business channels with a row in msgstore.db's newsletter table",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "WhatsApp Business",
        "notes": "Reads the com.whatsapp.w4b copy of msgstore.db with the same code as WhatsApp - Channels, whose notes describe the columns. A msgstore.db without a newsletter table reports no rows. "
                 "Validation boundary: no WhatsApp Business extraction was available when this was written, and whether WhatsApp Business keeps channels in the same newsletter table is not established; the code has been run against constructed databases only.",
        "paths": ('*/com.whatsapp.w4b/databases/msgstore.db*',),
        "output_types": "standard",
        "artifact_icon": "broadcast",
        "sample_data": {},
    },
    "get_whatsapp_business_channel_messages": {
        "name": "WhatsApp Business - Channel Messages",
        "description": "Messages stored in WhatsApp Business channel (newsletter) chats",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "WhatsApp Business",
        "notes": "Reads the com.whatsapp.w4b copy of msgstore.db with the same code as WhatsApp - Channel Messages, whose notes describe the columns. Media is linked from the WhatsApp Business media folders listed in the paths, whose location was not seen in an extraction (see WhatsApp Business - One To One Messages). "
                 "Validation boundary: no WhatsApp Business extraction was available when this was written; the code has been run against constructed databases only.",
        "paths": ('*/com.whatsapp.w4b/databases/msgstore.db*', '*/WhatsApp Business/Media/*',
                  '*/com.whatsapp.w4b/files/Media/*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {},
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Channel Name",
                "textColumn": "Message",
                "directionColumn": "Message Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Message Timestamp",
                "senderColumn": "Channel Name",
                "sentMessageStaticLabel": "Local User",
                "mediaColumn": "Media"
            }
        },
    },
    "get_whatsapp_business_user_profile": {
        "name": "WhatsApp Business - User Profile",
        "description": "Values of five keys in WhatsApp Business's shared_prefs XML files, one row per shared_prefs folder",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-25",
        "last_update_date": "2026-10-25",
        "requirements": "none",
        "category": "WhatsApp Business",
        "notes": "Reads the same five keys as WhatsApp - User Profile (push_name, my_current_status, cc, ph and version), whose notes describe the columns, from the com.whatsapp.w4b shared_prefs files whose names end with preferences_light.xml or startup_prefs.xml. "
                 "Validation boundary: no WhatsApp Business extraction was available when this was written. The file names are matched by their ending because the exact name of the preferences file in com.whatsapp.w4b was not seen, and whether the Business app writes these five keys under the same names is not established; the code has been run against constructed files only. The business profile (business name, address, hours, catalog) is not read.",
        "paths": ('*/com.whatsapp.w4b/shared_prefs/*preferences_light.xml',
                  '*/com.whatsapp.w4b/shared_prefs/startup_prefs.xml'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {},
    }
}

from scripts.ilapfuncs import artifact_processor
from scripts.artifacts.WhatsApp import (
    _user_profile_rows,
    get_whatsapp_call_logs,
    get_whatsapp_channel_messages,
    get_whatsapp_channels,
    get_whatsapp_contacts,
    get_whatsapp_group_details,
    get_whatsapp_group_messages,
    get_whatsapp_messages,
    get_whatsapp_one_to_one_messages,
)

# Each artifact below runs the WhatsApp artifact of the same name through __wrapped__, the
# way justalk.py runs its Kids variants. The Business paths only match com.whatsapp.w4b, so
# files_found never holds a com.whatsapp store and the WhatsApp code reads the Business
# stores on their own.


@artifact_processor
def get_whatsapp_business_contacts(context):
    return get_whatsapp_contacts.__wrapped__(context)


@artifact_processor
def get_whatsapp_business_call_logs(context):
    return get_whatsapp_call_logs.__wrapped__(context)


@artifact_processor
def get_whatsapp_business_messages(context):
    return get_whatsapp_messages.__wrapped__(context)


@artifact_processor
def get_whatsapp_business_one_to_one_messages(context):
    return get_whatsapp_one_to_one_messages.__wrapped__(context)


@artifact_processor
def get_whatsapp_business_group_messages(context):
    return get_whatsapp_group_messages.__wrapped__(context)


@artifact_processor
def get_whatsapp_business_group_details(context):
    return get_whatsapp_group_details.__wrapped__(context)


@artifact_processor
def get_whatsapp_business_channels(context):
    return get_whatsapp_channels.__wrapped__(context)


@artifact_processor
def get_whatsapp_business_channel_messages(context):
    return get_whatsapp_channel_messages.__wrapped__(context)


@artifact_processor
def get_whatsapp_business_user_profile(context):
    data_list, source = _user_profile_rows(context, ('preferences_light.xml', 'startup_prefs.xml'))
    data_headers = ('Version', 'Name', 'User Status', 'Country Code', 'Mobile Number', 'Source Files')
    return data_headers, data_list, source
