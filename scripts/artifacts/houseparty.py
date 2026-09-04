__artifacts_v2__ = {
    "housepartyMessages": {
        "name": "Houseparty - Direct Messages",
        "description": "Direct messages held in the Houseparty app's Realm store, with the "
                       "time each was sent, the account that sent it, the account it was "
                       "addressed to and the message text.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-02",
        "last_update_date": "2026-09-04",
        "requirements": "none",
        "category": "Houseparty",
        "notes": "Read from class_RealmNote in the app's Realm store with the vendored "
                 "realm_parser. Houseparty was a group video chat app; its publisher removed it "
                 "from the app stores on 9 September 2021 and shut it down in October 2021, so a "
                 "store found now is a residue of earlier use. Reference: Sarah Perez, 'Epic "
                 "Games to shut down Houseparty in October, including the video chat Fortnite "
                 "Mode feature', TechCrunch, "
                 "https://techcrunch.com/2021/09/09/epic-games-to-shut-down-houseparty-in-october-including-the-video-chat-fortnite-mode-feature/ "
                 "Direction is derived by comparing each message's senderId against the account "
                 "id in class_RealmUser, which is the identity the store itself records, and is "
                 "left empty when no account row is present. Sender and Recipient are resolved to "
                 "the user name class_RealmPublicUser records for that id, falling back to the id "
                 "as stored when the store holds no row for it. Media reports what the row's "
                 "facemail link resolves to; a facemail is the app's video message. On the tested "
                 "extraction the link was null on every message and class_RealmFacemail held no "
                 "rows, so Media is empty on all of them and no video message was recovered. Sent "
                 "At is the store's own sentAt value; the same row separately carries "
                 "sentAtSeconds and sentAtNanos, which agree with it, and the newest value "
                 "matches LAST_NOTE_DATE in the app's USERDATA_SHARED_PREFERENCES.xml to the "
                 "millisecond. Conversation names the other account in the exchange, so it holds "
                 "one value wherever the store records messages with a single correspondent, as "
                 "it did on the tested extraction. Read and Hidden are reported as stored.",
        "paths": ('*/com.herzick.houseparty/files/default.realm',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation",
                "conversationLabelColumn": "Conversation",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Sent At",
                "senderColumn": "Sender",
                "mediaColumn": "Media",
            },
        },
        "sample_data": {
            "pixel3_a11": "Android 11 | com.herzick.houseparty vc 49432 | 7 rows",
        },
    },
    "housepartyRooms": {
        "name": "Houseparty - Video Rooms",
        "description": "Video rooms the app recorded, with the time each was created, whether "
                       "it was locked and the media server session it was carried on.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-02",
        "last_update_date": "2026-09-04",
        "requirements": "none",
        "category": "Houseparty",
        "notes": "Read from class_RealmRoom in the app's Realm store, with the session joined "
                 "from class_RealmRoomSession through the row's own realmRoomSession link and the "
                 "server host joined from class_RealmMediaServerEndpoint through the session's "
                 "mediaServerEndpoint link. A room row records that the app held a room, not that "
                 "a call took place or who was in it. Participants are not recoverable from this "
                 "store: the invitedUsers list on every room row and the users list on every "
                 "session row were empty on the tested extraction, and the parser reads list "
                 "columns elsewhere in the same file, so that is an absence in the data rather "
                 "than a decoding limit. Locked, Locking User, Video Tech and Secret Version are "
                 "reported as stored; no room on the tested extraction was locked, so Locking "
                 "User is empty on all of them. The media server host is joined from the "
                 "session's own mediaServerEndpoint link and is the server the app was told to "
                 "use, not an address the device is shown to have reached. Colour is the color "
                 "value the room row carries, a hex RGB string reported as stored.",
        "paths": ('*/com.herzick.houseparty/files/default.realm',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "video",
        "sample_data": {
            "pixel3_a11": "Android 11 | com.herzick.houseparty vc 49432 | 4 rows",
        },
    },
    "housepartyAccount": {
        "name": "Houseparty - Account",
        "description": "The signed-in Houseparty account, with the user name, display name, "
                       "email address, telephone number and birthday the account held, and the "
                       "notification and privacy settings stored alongside it.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-02",
        "last_update_date": "2026-09-04",
        "requirements": "none",
        "category": "Houseparty",
        "notes": "Read from class_RealmUser in the app's Realm store, with the settings joined "
                 "from class_RealmUserSettings through the row's own realmUserSettings link and "
                 "the session dates from class_RealmToken matched on the account id. These are "
                 "values the account held in the app, which the app received from its service; "
                 "they are not verified identifiers. Birthday fell on midnight UTC on the tested "
                 "extraction and is reported as a date rather than a datetime for that reason. "
                 "Session Created and Session Invalidated come from class_RealmToken; an "
                 "invalidated value of the Unix epoch is the store's not-invalidated sentinel and "
                 "is reported as empty. The token string itself is not reported. Relevance Reason "
                 "and Notification Threshold are reported as stored.",
        "paths": ('*/com.herzick.houseparty/files/default.realm',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user",
        "sample_data": {
            "pixel3_a11": "Android 11 | com.herzick.houseparty vc 49432 | 1 row",
        },
    },
    "housepartyContacts": {
        "name": "Houseparty - Contacts",
        "description": "Other Houseparty accounts the app held, with the user name and display "
                       "name each carried, when each was last seen, and the relationship and "
                       "time-together values the app recorded for them.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-02",
        "last_update_date": "2026-09-02",
        "requirements": "none",
        "category": "Houseparty",
        "notes": "Read from class_RealmPublicUser in the app's Realm store, with presence "
                 "joined from class_RealmUserPresence through the row's own userPresence link "
                 "and the relationship, together-minutes and last-interaction values joined "
                 "from class_RealmRelationshipInfo, class_RealmWithSomeoneData and "
                 "class_RealmLocalWithSomeoneData on the account id. The signed-in account "
                 "appears here as well as in the Account artifact, because the store keeps a "
                 "public record for it too. Last Seen and Room Created are values the service "
                 "supplied about that account and are not evidence of activity on this device. "
                 "Presence Type, Relationship Status and Game Type are reported as stored. "
                 "Together Minutes and Local Minutes are the app's own counters, in minutes as "
                 "stored. Notifications Enabled and Ghosting are reported as stored.",
        "paths": ('*/com.herzick.houseparty/files/default.realm',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "users",
        "sample_data": {
            "pixel3_a11": "Android 11 | com.herzick.houseparty vc 49432 | 2 rows",
        },
    },
    "housepartyInteractions": {
        "name": "Houseparty - Interactions",
        "description": "Interactions the app recorded between the signed-in account and "
                       "another account, with the time each happened.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-02",
        "last_update_date": "2026-09-02",
        "requirements": "none",
        "category": "Houseparty",
        "notes": "Read from class_RealmInteraction in the app's Realm store. From and To are "
                 "resolved to the user name class_RealmPublicUser records for that id, falling "
                 "back to the id as stored. Interaction Type is an integer the store does not "
                 "explain and is reported as stored; the app is withdrawn and no published "
                 "definition of these values was found, so no meaning is asserted for it. A row "
                 "records that the app held an interaction, not what was said or done.",
        "paths": ('*/com.herzick.houseparty/files/default.realm',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "activity",
        "sample_data": {
            "pixel3_a11": "Android 11 | com.herzick.houseparty vc 49432 | 1 row",
        },
    },
}

import os
from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.realm_parser import parse_realm_file

# Only a store holding this class is this app's; a file that does not is skipped
# and logged rather than reported under Houseparty's name.
_MARKER_CLASS = 'class_RealmUser'


def _utc(value):
    """A 'YYYY-MM-DD HH:MM:SS UTC' value as an aware datetime, or '' when unusable."""
    text = str(value or '').strip()
    if not text.endswith(' UTC'):
        return ''
    try:
        return datetime.strptime(text[:-4], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    except ValueError:
        return ''


def _date_only(value):
    """The date part of a UTC-marked value, for a value stored at midnight."""
    stamp = _utc(value)
    return stamp.strftime('%Y-%m-%d') if stamp else ''


def _text(value):
    """A displayable scalar. A list is rendered as its members, not its length."""
    if value is None:
        return ''
    if isinstance(value, bool):
        return value
    if isinstance(value, list):
        return ', '.join(str(item) for item in value)
    return value


def _stores(context):
    """Each Realm store that carries this app's marker class, duplicates removed."""
    found = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        # A `paths` match can be a directory: Realm keeps a default.realm.management
        # directory beside the store, and open() on it would end the whole artifact.
        if os.path.isdir(file_found):
            continue
        try:
            parsed = parse_realm_file(file_found)
        except Exception as error:  # pylint: disable=broad-exception-caught
            logfunc(f'Houseparty: {os.path.basename(file_found)} did not parse: {error}')
            continue
        tables = parsed.get('active') or {}
        if _MARKER_CLASS not in tables:
            logfunc(f'Houseparty: {os.path.basename(file_found)} holds no {_MARKER_CLASS}, skipped')
            continue
        if parsed.get('reason'):
            logfunc(f'Houseparty: {os.path.basename(file_found)}: {parsed["reason"]}')
        found.append((file_found, tables))
    return found


def _rows(tables, class_name):
    """Every row of ``class_name`` as a {column_name: value} dict."""
    table = tables.get(class_name)
    if not table:
        return []
    names = table['column_names']
    columns = table['columns']
    out = []
    for i in range(table['row_count']):
        row = {}
        for j, name in enumerate(names):
            values = columns.get(j)
            row[name] = values[i] if values is not None and i < len(values) else None
        out.append(row)
    return out


def _linked(rows, index):
    """The row a link column points at, or None. Links are positional row indexes."""
    if index is None or isinstance(index, bool):
        return None
    try:
        position = int(index)
    except (TypeError, ValueError):
        return None
    return rows[position] if 0 <= position < len(rows) else None


def _name_map(tables):
    """account id -> the user name class_RealmPublicUser records for it."""
    out = {}
    for row in _rows(tables, 'class_RealmPublicUser'):
        if row.get('id'):
            out[str(row['id'])] = row.get('userName') or row.get('fullName') or ''
    return out


def _who(account_id, names):
    """A user name for an account id, falling back to the id as stored."""
    key = str(account_id or '')
    if not key:
        return ''
    return names.get(key) or key


@artifact_processor
def housepartyMessages(context):
    data_headers = (
        ('Sent At', 'datetime'),
        'Direction',
        'Sender',
        'Conversation',
        'Message',
        'Media',
        'Recipient',
        'Read',
        'Hidden',
        'Message ID',
    )
    data_list = []
    sources = []
    for store, tables in _stores(context):
        names = _name_map(tables)
        account = _rows(tables, 'class_RealmUser')
        account_id = str(account[0]['id']) if account and account[0].get('id') else ''
        facemails = _rows(tables, 'class_RealmFacemail')
        read_any = False
        for row in _rows(tables, 'class_RealmNote'):
            sender_id = str(row.get('senderId') or '')
            recipient_id = str(row.get('recipientId') or '')
            if account_id and sender_id:
                direction = 'Outgoing' if sender_id == account_id else 'Incoming'
            else:
                direction = ''
            # The other party names the conversation; on an outgoing message that
            # is the recipient, on an incoming one it is the sender.
            other = recipient_id if direction == 'Outgoing' else sender_id
            media = _linked(facemails, row.get('facemail'))
            data_list.append((
                _utc(row.get('sentAt')),
                direction,
                _who(sender_id, names),
                _who(other, names),
                _text(row.get('content')),
                _text(media.get('id')) if media else '',
                _who(recipient_id, names),
                _text(row.get('isUnread')),
                _text(row.get('isHidden')),
                _text(row.get('id')),
            ))
            read_any = True
        if read_any:
            sources.append(store)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def housepartyRooms(context):
    data_headers = (
        ('Created At', 'datetime'),
        'Room ID',
        'Locked',
        'Locking User',
        'Colour',
        'Media Server',
        'Video Tech (as stored)',
        'Secret Version (as stored)',
        'Session ID',
    )
    data_list = []
    sources = []
    for store, tables in _stores(context):
        names = _name_map(tables)
        sessions = _rows(tables, 'class_RealmRoomSession')
        endpoints = _rows(tables, 'class_RealmMediaServerEndpoint')
        read_any = False
        for row in _rows(tables, 'class_RealmRoom'):
            session = _linked(sessions, row.get('realmRoomSession'))
            endpoint = _linked(endpoints, session.get('mediaServerEndpoint')) if session else None
            # class_RealmMediaServerEndpoint names its columns processId, host, port.
            host = _text(endpoint.get('host')) if endpoint else ''
            data_list.append((
                _utc(row.get('createdAt')),
                _text(row.get('id')),
                _text(row.get('isLocked')),
                _who(row.get('lockingUserId'), names),
                _text(row.get('color')),
                host,
                _text(session.get('videoTech')) if session else '',
                _text(session.get('secretVersion')) if session else '',
                _text(session.get('id')) if session else '',
            ))
            read_any = True
        if read_any:
            sources.append(store)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def housepartyAccount(context):
    data_headers = (
        ('Created At', 'datetime'),
        ('Updated At', 'datetime'),
        ('Session Created', 'datetime'),
        ('Session Invalidated', 'datetime'),
        ('Birthday', 'date'),
        'Username',
        'Display Name',
        'Email',
        'Phone',
        'Account ID',
        'Private Mode',
        'Auto Ghost',
        'Auto Mute',
        'Mute Notifications',
        'Auto Sneak In',
        'Notification Threshold (as stored)',
        'Relevance Reason (as stored)',
    )
    data_list = []
    sources = []
    for store, tables in _stores(context):
        settings_rows = _rows(tables, 'class_RealmUserSettings')
        tokens = _rows(tables, 'class_RealmToken')
        read_any = False
        for row in _rows(tables, 'class_RealmUser'):
            settings = _linked(settings_rows, row.get('realmUserSettings')) or {}
            account_id = str(row.get('id') or '')
            token = next((t for t in tokens if str(t.get('userId') or '') == account_id), {})
            invalidated = _utc(token.get('invalidatedAt'))
            # The store writes the Unix epoch to mean "not invalidated".
            if invalidated and invalidated.year == 1970:
                invalidated = ''
            data_list.append((
                _utc(row.get('createdAt')),
                _utc(row.get('updatedAt')),
                _utc(token.get('createdAt')),
                invalidated,
                _date_only(row.get('birthday')),
                _text(row.get('username')),
                _text(row.get('name')),
                _text(row.get('email')),
                _text(row.get('phone')),
                account_id,
                _text(settings.get('privateMode')),
                _text(settings.get('autoGhost')),
                _text(settings.get('autoMute')),
                _text(settings.get('muteNotifications')),
                _text(settings.get('autoSneakIn')),
                _text(settings.get('notificationThreshold')),
                _text(row.get('relevanceReason')),
            ))
            read_any = True
        if read_any:
            sources.append(store)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def housepartyContacts(context):
    data_headers = (
        ('Last Seen', 'datetime'),
        ('Created At', 'datetime'),
        ('Latest Interaction', 'datetime'),
        ('Last Together', 'datetime'),
        ('Room Created', 'datetime'),
        'Username',
        'Display Name',
        'Account ID',
        'Presence Type (as stored)',
        'On Phone',
        'Room ID',
        'Relationship Status (as stored)',
        'Notifications Enabled',
        'Ghosting',
        'Together Minutes',
        'Local Minutes',
        'Game Type (as stored)',
    )
    data_list = []
    sources = []
    for store, tables in _stores(context):
        presences = _rows(tables, 'class_RealmUserPresence')
        relationships = {str(r.get('userId') or ''): r
                         for r in _rows(tables, 'class_RealmRelationshipInfo')}
        together = {str(r.get('userId') or ''): r
                    for r in _rows(tables, 'class_RealmWithSomeoneData')}
        local = {str(r.get('userId') or ''): r
                 for r in _rows(tables, 'class_RealmLocalWithSomeoneData')}
        read_any = False
        for row in _rows(tables, 'class_RealmPublicUser'):
            account_id = str(row.get('id') or '')
            presence = _linked(presences, row.get('userPresence')) or {}
            relationship = relationships.get(account_id, {})
            with_someone = together.get(account_id, {})
            local_someone = local.get(account_id, {})
            data_list.append((
                _utc(presence.get('lastSeen')),
                _utc(row.get('createdAt')),
                _utc(relationship.get('latestInteractionAt')),
                _utc(with_someone.get('lastWithSomeoneAt')),
                _utc(presence.get('roomCreatedAt')),
                _text(row.get('userName')),
                _text(row.get('fullName')),
                account_id,
                _text(presence.get('type')),
                _text(presence.get('isOnPhone')),
                _text(presence.get('roomId')),
                _text(relationship.get('statusValue')),
                _text(relationship.get('notificationsEnabled')),
                _text(relationship.get('isGhosting')),
                _text(with_someone.get('activeWithSomeoneMinutes')),
                _text(local_someone.get('localMinutes')),
                _text(presence.get('gameTypeInt')),
            ))
            read_any = True
        if read_any:
            sources.append(store)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def housepartyInteractions(context):
    data_headers = (
        ('Happened At', 'datetime'),
        'From',
        'To',
        'Interaction Type (as stored)',
    )
    data_list = []
    sources = []
    for store, tables in _stores(context):
        names = _name_map(tables)
        read_any = False
        for row in _rows(tables, 'class_RealmInteraction'):
            data_list.append((
                _utc(row.get('happenedAt')),
                _who(row.get('fromUserId'), names),
                _who(row.get('toUserId'), names),
                _text(row.get('interactionType')),
            ))
            read_any = True
        if read_any:
            sources.append(store)
    return data_headers, data_list, '\n'.join(sources)
