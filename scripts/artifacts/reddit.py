__artifacts_v2__ = {
    "get_reddit_chat_messages": {
        "name": "Reddit - Chat Messages",
        "description": "Chat messages from the Matrix session database: message body, "
                       "sender, room and timestamp, joined from timeline_event, event and "
                       "room_member_summary.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Reddit",
        "notes": "Reddit chat is stored in databases/matrix_session_<session id>, whose "
                 "schema follows the Matrix protocol. Rows are the events whose type is "
                 "m.room.message; the body and msgtype come from the event's content JSON, "
                 "and the sender's display name is resolved through room_member_summary "
                 "for the same room, falling back to the raw Matrix user id.\n"
                 "Message Direction compares the event sender against the signed-in "
                 "account, taken from session_params.userId in the matrix_auth database "
                 "(observed as @t2_<reddit id>:reddit.com). Blank when that database is "
                 "absent. Timestamps are Unix milliseconds from originServerTs, reported "
                 "in UTC.\n"
                 "Media. Image messages carry an mxc:// URL and its dimensions rather than "
                 "a local file name, reported here as text. On the tested image neither "
                 "media id appeared in any file name in the extraction, including the "
                 "app's Glide image_manager_disk_cache, so no reproducible link from a "
                 "message to cached bytes was found and none is asserted. A separate "
                 "blurred-image URL the app records is reported alongside.\n"
                 "A message removed through a redaction event keeps its row here; see "
                 "Reddit - Chat Events for the redactions themselves, which name the event "
                 "id they target.\n"
                 "Reference: Arun Kalackattu Hari, 'Forensic Analysis of Reddit App: iOS "
                 "and Android', dfdive.com, 06 April 2026, https://dfdive.com/articles/",
        "paths": ('*/com.reddit.frontpage/databases/matrix_session_*',
                  '*/com.reddit.frontpage/databases/matrix_auth*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "pixel7a_a14": "Android 14 | 15 rows (11 text, 2 image, 2 without a msgtype)",
            "pixel3_a11": "Android 11 | no matrix session database found",
            "pixel3_a12": "Android 12 | no matrix session database found",
            "russell_a14": "Android 14 | no matrix session database found",
            "russell_pixel6a_a13": "Android 13 | no matrix session database found",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Room ID",
                "textColumn": "Message",
                "directionColumn": "Message Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Timestamp",
                "senderColumn": "Sender Display Name",
            }
        },
    },
    "get_reddit_chat_events": {
        "name": "Reddit - Chat Events",
        "description": "Rows from the event table in the Matrix session database, "
                       "covering membership, reaction and redaction events as well as "
                       "messages, with their content JSON as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Reddit",
        "notes": "Every row of the event table, not only chat messages. The Type column "
                 "holds the Matrix event type as stored; on the tested image these "
                 "included m.room.message, m.room.member, m.room.create, m.room.join_rules, "
                 "m.room.history_visibility, m.room.power_levels, m.reaction and "
                 "m.room.redaction, plus the app's own com.reddit.chat.type.\n"
                 "A m.room.redaction row names the event it targets in the Redacts column, "
                 "which is the mechanism behind a message removed from the conversation. "
                 "What a redaction means for the message body on the server is not "
                 "established here.\n"
                 "Content is reported as stored so nothing in the payload is lost to "
                 "interpretation. Timestamps are Unix milliseconds in UTC.\n"
                 "Reference: Arun Kalackattu Hari, 'Forensic Analysis of Reddit App: iOS "
                 "and Android', dfdive.com, 06 April 2026, https://dfdive.com/articles/",
        "paths": ('*/com.reddit.frontpage/databases/matrix_session_*',),
        "output_types": "standard",
        "artifact_icon": "list",
        "sample_data": {
            "pixel7a_a14": "Android 14 | 27 rows (15 messages, 2 redactions, 1 reaction)",
            "pixel3_a11": "Android 11 | no matrix session database found",
            "pixel3_a12": "Android 12 | no matrix session database found",
            "russell_a14": "Android 14 | no matrix session database found",
            "russell_pixel6a_a13": "Android 13 | no matrix session database found",
        },
    },
    "get_reddit_chat_rooms": {
        "name": "Reddit - Chat Rooms",
        "description": "Rooms from the Matrix session database: display name, room type, "
                       "member counts and last activity, as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Reddit",
        "notes": "One row per room in room_summary. Room Type and the direct-chat flag are "
                 "reported as stored; on the tested image a one-to-one chat carried the "
                 "type 'direct' with two joined members. Last Activity is Unix "
                 "milliseconds in UTC.\n"
                 "Reference: Arun Kalackattu Hari, 'Forensic Analysis of Reddit App: iOS "
                 "and Android', dfdive.com, 06 April 2026, https://dfdive.com/articles/",
        "paths": ('*/com.reddit.frontpage/databases/matrix_session_*',),
        "output_types": "standard",
        "artifact_icon": "messages",
        "sample_data": {
            "pixel7a_a14": "Android 14 | 1 row (direct chat)",
            "pixel3_a11": "Android 11 | no matrix session database found",
            "pixel3_a12": "Android 12 | no matrix session database found",
            "russell_a14": "Android 14 | no matrix session database found",
            "russell_pixel6a_a13": "Android 13 | no matrix session database found",
        },
    },
    "get_reddit_chat_members": {
        "name": "Reddit - Chat Room Members",
        "description": "Room participants from room_member_summary: Matrix user id, "
                       "display name and membership state as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Reddit",
        "notes": "The table the message artifact uses to resolve a sender to a display "
                 "name. The Matrix user id embeds the account's Reddit id in the form "
                 "@t2_<reddit id>:reddit.com. Membership state is reported as stored.\n"
                 "Reference: Arun Kalackattu Hari, 'Forensic Analysis of Reddit App: iOS "
                 "and Android', dfdive.com, 06 April 2026, https://dfdive.com/articles/",
        "paths": ('*/com.reddit.frontpage/databases/matrix_session_*',),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "pixel7a_a14": "Android 14 | 2 rows",
            "pixel3_a11": "Android 11 | no matrix session database found",
            "pixel3_a12": "Android 12 | no matrix session database found",
            "russell_a14": "Android 14 | no matrix session database found",
            "russell_pixel6a_a13": "Android 13 | no matrix session database found",
        },
    },
    "get_reddit_users": {
        "name": "Reddit - Users",
        "description": "Users cached in matrix-users-db: Reddit id, Matrix id, name, karma "
                       "and cakeday, with the row's insert timestamp.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Reddit",
        "notes": "RedditUserEntity ties a Reddit id to the Matrix id used in chat, which "
                 "is what allows a chat participant to be named. Blocked and "
                 "accepting-chats flags are reported as stored. Insert Timestamp is when "
                 "the app wrote the row, not when the account was created; Cakeday is the "
                 "account creation value the app cached, in Unix seconds.\n"
                 "Reference: Arun Kalackattu Hari, 'Forensic Analysis of Reddit App: iOS "
                 "and Android', dfdive.com, 06 April 2026, https://dfdive.com/articles/",
        "paths": ('*/com.reddit.frontpage/databases/matrix-users-db*',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "pixel7a_a14": "Android 14 | 6 rows",
            "pixel3_a11": "Android 11 | no matrix-users-db found",
            "pixel3_a12": "Android 12 | no matrix-users-db found",
            "russell_a14": "Android 14 | no matrix-users-db found",
            "russell_pixel6a_a13": "Android 13 | no matrix-users-db found",
        },
    },
    "get_reddit_account": {
        "name": "Reddit - Accounts",
        "description": "Account records cached in the per-user reddit_db store: name, "
                       "account id, creation time, karma totals, premium and contact "
                       "fields as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Reddit",
        "notes": "The database is named reddit_db_<account name>, reported in the Store "
                 "Account column; a reddit_db_anonymous file is the logged-out store and "
                 "is reported the same way. The account table is a cache and is not "
                 "limited to the device owner: on the tested image the store named for "
                 "the local account held two rows, the local account and the account it "
                 "had exchanged chat messages with. Treat Store Account as the account "
                 "the file belongs to and Name as the account the row describes.\n"
                 "Created and Premium Since are Unix seconds. Email and the masked phone "
                 "number are reported as the app stored them.\n"
                 "The Matrix session's signed-in user id is reported by Reddit - Session, "
                 "which is the value chat direction is derived from.\n"
                 "Reference: Arun Kalackattu Hari, 'Forensic Analysis of Reddit App: iOS "
                 "and Android', dfdive.com, 06 April 2026, https://dfdive.com/articles/",
        "paths": ('*/com.reddit.frontpage/databases/reddit_db_*',),
        "output_types": "standard",
        "artifact_icon": "user-circle",
        "sample_data": {
            "russell_a14": "Android 14 | 9 rows",
            "russell_pixel6a_a13": "Android 13 | 7 rows",
            "pixel7a_a14": "Android 14 | 3 rows",
            "pixel3_a11": "Android 11 | 0 rows (account table empty)",
            "pixel3_a12": "Android 12 | 0 rows (account table empty)",
        },
    },
    "get_reddit_session": {
        "name": "Reddit - Session",
        "description": "The Matrix session record: signed-in user id, session id, home "
                       "server and session date.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Reddit",
        "notes": "session_params in the matrix_auth database. The user id is the anchor "
                 "chat direction is derived from, in the form @t2_<reddit id>:reddit.com, "
                 "and the session id matches the matrix_session_<session id> database file "
                 "name. Date is Unix milliseconds in UTC; what event it marks is not "
                 "established here.\n"
                 "The record also holds a credentials JSON containing an access token. "
                 "Only whether the app considered the token valid is reported; the token "
                 "itself is not expanded into the report.\n"
                 "Reference: Arun Kalackattu Hari, 'Forensic Analysis of Reddit App: iOS "
                 "and Android', dfdive.com, 06 April 2026, https://dfdive.com/articles/",
        "paths": ('*/com.reddit.frontpage/databases/matrix_auth*',),
        "output_types": "standard",
        "artifact_icon": "key",
        "sample_data": {
            "pixel7a_a14": "Android 14 | 1 row",
            "russell_a14": "Android 14 | 0 rows (session_params table empty)",
            "pixel3_a11": "Android 11 | no matrix_auth found",
            "pixel3_a12": "Android 12 | no matrix_auth found",
            "russell_pixel6a_a13": "Android 13 | no matrix_auth found",
        },
    },
    "get_reddit_subreddits": {
        "name": "Reddit - Subreddits",
        "description": "Communities cached in the per-user reddit_db store: name, title, "
                       "subscriber count, creation time and type as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Reddit",
        "notes": "The subreddit table holds the communities the app had cached, keyed by "
                 "the t5_ community identifier the article documents as the cross-database "
                 "linking value. Presence of a row records that the app cached the "
                 "community; it does not establish that the user subscribed to it or "
                 "visited it. Created is Unix seconds.\n"
                 "Reference: Arun Kalackattu Hari, 'Forensic Analysis of Reddit App: iOS "
                 "and Android', dfdive.com, 06 April 2026, https://dfdive.com/articles/",
        "paths": ('*/com.reddit.frontpage/databases/reddit_db_*',),
        "output_types": "standard",
        "artifact_icon": "users-group",
        "sample_data": {
            "russell_a14": "Android 14 | 44 rows",
            "russell_pixel6a_a13": "Android 13 | 41 rows",
            "pixel3_a11": "Android 11 | 12 rows",
            "pixel3_a12": "Android 12 | 12 rows",
            "pixel7a_a14": "Android 14 | 10 rows",
        },
    },
    "get_reddit_posts": {
        "name": "Reddit - Cached Posts",
        "description": "Posts cached in the per-user reddit_db store, with author, title, "
                       "community, score and creation time read from each row's stored "
                       "JSON.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Reddit",
        "notes": "The link table stores one JSON document per post, from which the "
                 "author, title, community, permalink, target URL, score, comment count "
                 "and NSFW flag are read; the document holds many more fields than are "
                 "reported. Listing Position and Listing ID are the app's own ordering "
                 "within a cached feed.\n"
                 "A row records that the post was cached on the device, which is not the "
                 "same as the user opening or reading it. Created is Unix seconds.\n"
                 "Reference: Arun Kalackattu Hari, 'Forensic Analysis of Reddit App: iOS "
                 "and Android', dfdive.com, 06 April 2026, https://dfdive.com/articles/",
        "paths": ('*/com.reddit.frontpage/databases/reddit_db_*',),
        "output_types": "standard",
        "artifact_icon": "article",
        "sample_data": {
            "russell_a14": "Android 14 | 1507 rows",
            "russell_pixel6a_a13": "Android 13 | 1170 rows",
            "pixel3_a11": "Android 11 | 56 rows",
            "pixel3_a12": "Android 12 | 56 rows",
            "pixel7a_a14": "Android 14 | 46 rows",
        },
    },
}

import datetime
import os
import sqlite3

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _s_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(float(value)), datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _rows(source_path, sql):
    if not source_path:
        return []
    db = open_sqlite_db_readonly(source_path)
    if db is None:
        return []
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except sqlite3.Error:
        rows = []
    db.close()
    return rows


def _matching(context, predicate):
    '''Deduplicated files whose base name satisfies predicate.'''
    return [f for f in unique_files(context) if predicate(os.path.basename(str(f)))]


def _session_dbs(context):
    return _matching(context, lambda n: n.startswith('matrix_session_')
                     and not n.endswith(('-wal', '-shm', '-journal')))


def _reddit_dbs(context):
    return _matching(context, lambda n: n.startswith('reddit_db_')
                     and not n.endswith(('-wal', '-shm', '-journal', '.lck')))


def _local_user_id(context):
    '''The signed-in Matrix user id from matrix_auth, or '' when unavailable.'''
    for auth_db in _matching(context, lambda n: n.startswith('matrix_auth')
                             and not n.endswith(('-wal', '-shm', '-journal'))):
        for (user_id,) in _rows(auth_db, 'SELECT userId FROM session_params'):
            if user_id:
                return user_id
    return ''


def _yes_no(value):
    return 'YES' if value else 'NO'


@artifact_processor
def get_reddit_chat_messages(context):
    data_list = []
    source_path = ''
    local_user_id = _local_user_id(context)
    for session_db in _session_dbs(context):
        source_path = source_path or session_db
        source_file = context.get_relative_path(session_db)
        for (timestamp, sender, display_name, body, msgtype, media_url, blurred_url,
             width, height, mimetype, room_id, event_id) in _rows(session_db, """
                SELECT e.originServerTs,
                       e.sender,
                       COALESCE(rms.displayName, te.senderName, e.sender),
                       json_extract(e.content, '$.body'),
                       json_extract(e.content, '$.msgtype'),
                       json_extract(e.content, '$.url'),
                       json_extract(e.content, '$."com.reddit.blurred_url"'),
                       json_extract(e.content, '$.info.w'),
                       json_extract(e.content, '$.info.h'),
                       json_extract(e.content, '$.info.mimetype'),
                       e.roomId,
                       e.eventId
                FROM timeline_event te
                LEFT JOIN event e ON te.eventId = e.eventId
                LEFT JOIN room_member_summary rms
                    ON e.sender = rms.userId AND rms.roomId = te.roomId
                WHERE e.type = 'm.room.message'
                ORDER BY e.originServerTs"""):
            if local_user_id and sender:
                direction = 'Outgoing' if sender == local_user_id else 'Incoming'
            else:
                direction = ''
            dimensions = f'{width}x{height}' if width and height else ''
            data_list.append((
                _ms_to_utc(timestamp), display_name, sender, direction, body, msgtype,
                media_url, blurred_url, dimensions, mimetype, room_id, event_id,
                source_file))

    data_headers = (('Timestamp', 'datetime'), 'Sender Display Name', 'Sender ID',
                    'Message Direction', 'Message', 'Message Type (as stored)',
                    'Media URL (as stored)', 'Blurred Media URL (as stored)',
                    'Media Dimensions', 'Media MIME Type', 'Room ID', 'Event ID',
                    'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def get_reddit_chat_events(context):
    data_list = []
    source_path = ''
    for session_db in _session_dbs(context):
        source_path = source_path or session_db
        source_file = context.get_relative_path(session_db)
        for (timestamp, event_type, sender, display_name, content, redacts, state_key,
             room_id, event_id) in _rows(session_db, """
                SELECT e.originServerTs, e.type, e.sender,
                       COALESCE(rms.displayName, e.sender),
                       e.content, e.redacts, e.stateKey, e.roomId, e.eventId
                FROM event e
                LEFT JOIN room_member_summary rms
                    ON e.sender = rms.userId AND rms.roomId = e.roomId
                ORDER BY e.originServerTs"""):
            data_list.append((
                _ms_to_utc(timestamp), event_type, display_name, sender, content,
                redacts, state_key, room_id, event_id, source_file))

    data_headers = (('Timestamp', 'datetime'), 'Type (as stored)', 'Sender Display Name',
                    'Sender ID', 'Content (as stored)', 'Redacts Event ID',
                    'State Key', 'Room ID', 'Event ID', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def get_reddit_chat_rooms(context):
    data_list = []
    source_path = ''
    for session_db in _session_dbs(context):
        source_path = source_path or session_db
        source_file = context.get_relative_path(session_db)
        for (last_activity, display_name, room_type, is_direct, direct_user, joined,
             invited, topic, unread, room_id) in _rows(session_db, """
                SELECT lastActivityTime, displayName, roomType, isDirect, directUserId,
                       joinedMembersCount, invitedMembersCount, topic,
                       hasUnreadMessages, roomId
                FROM room_summary ORDER BY lastActivityTime"""):
            data_list.append((
                _ms_to_utc(last_activity), display_name, room_type, _yes_no(is_direct),
                direct_user, joined, invited, topic, _yes_no(unread), room_id,
                source_file))

    data_headers = (('Last Activity', 'datetime'), 'Display Name',
                    'Room Type (as stored)', 'Is Direct', 'Direct User ID',
                    'Joined Members', 'Invited Members', 'Topic', 'Has Unread',
                    'Room ID', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def get_reddit_chat_members(context):
    data_list = []
    source_path = ''
    for session_db in _session_dbs(context):
        source_path = source_path or session_db
        source_file = context.get_relative_path(session_db)
        for (display_name, user_id, membership, is_direct, reason, room_id) in _rows(
                session_db, """
                SELECT displayName, userId, membershipStr, isDirect, reason, roomId
                FROM room_member_summary ORDER BY roomId, displayName"""):
            data_list.append((display_name, user_id, membership, _yes_no(is_direct),
                              reason, room_id, source_file))

    data_headers = ('Display Name', 'User ID', 'Membership (as stored)', 'Is Direct',
                    'Reason', 'Room ID', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def get_reddit_users(context):
    data_list = []
    source_path = ''
    for users_db in _matching(context, lambda n: n.startswith('matrix-users-db')
                              and not n.endswith(('-wal', '-shm', '-journal'))):
        source_path = source_path or users_db
        source_file = context.get_relative_path(users_db)
        for (inserted, name, reddit_id, matrix_id, karma, cakeday, is_nsfw, is_blocked,
             accepting, icon) in _rows(users_db, """
                SELECT insertTimestamp, name, redditId, matrixId, totalKarma, cakeday,
                       isNsfw, isBlocked, isAcceptingChats, profileIconUrl
                FROM RedditUserEntity ORDER BY insertTimestamp"""):
            data_list.append((
                _ms_to_utc(inserted), _s_to_utc(cakeday), name, reddit_id, matrix_id,
                karma, _yes_no(is_nsfw), _yes_no(is_blocked), _yes_no(accepting), icon,
                source_file))

    data_headers = (('Insert Timestamp', 'datetime'), ('Cakeday', 'datetime'), 'Name',
                    'Reddit ID', 'Matrix ID', 'Total Karma', 'Is NSFW', 'Is Blocked',
                    'Is Accepting Chats', 'Profile Icon URL', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def get_reddit_account(context):
    data_list = []
    source_path = ''
    for reddit_db in _reddit_dbs(context):
        source_path = source_path or reddit_db
        source_file = context.get_relative_path(reddit_db)
        store_account = os.path.basename(str(reddit_db)).replace('reddit_db_', '', 1)
        for (created, name, account_id, email, verified_email, phone_country, phone,
             link_karma, comment_karma, total_karma, is_premium, premium_since,
             is_mod, is_employee, is_suspended, coins, accept_chats,
             accept_pms) in _rows(reddit_db, """
                SELECT createdUtc, name, accountId, email, hasVerifiedEmail,
                       phoneCountryCode, phoneMaskedNumber, linkKarma, commentKarma,
                       totalKarma, isPremiumSubscriber, premiumSinceUtc, isMod,
                       isEmployee, isSuspended, coins, acceptChats, acceptPrivateMessages
                FROM account"""):
            data_list.append((
                _s_to_utc(created), _s_to_utc(premium_since), name, account_id,
                store_account, email, _yes_no(verified_email), phone_country, phone,
                link_karma, comment_karma, total_karma, _yes_no(is_premium),
                _yes_no(is_mod), _yes_no(is_employee), _yes_no(is_suspended), coins,
                _yes_no(accept_chats), _yes_no(accept_pms), source_file))

    data_headers = (('Created', 'datetime'), ('Premium Since', 'datetime'), 'Name',
                    'Account ID', 'Store Account', 'Email', 'Email Verified',
                    'Phone Country Code', 'Phone (masked, as stored)', 'Link Karma',
                    'Comment Karma', 'Total Karma', 'Is Premium', 'Is Mod',
                    'Is Employee', 'Is Suspended', 'Coins', 'Accepts Chats',
                    'Accepts Private Messages', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def get_reddit_session(context):
    data_list = []
    source_path = ''
    for auth_db in _matching(context, lambda n: n.startswith('matrix_auth')
                             and not n.endswith(('-wal', '-shm', '-journal'))):
        source_path = source_path or auth_db
        source_file = context.get_relative_path(auth_db)
        for (date, user_id, session_id, home_server, token_valid) in _rows(auth_db, """
                SELECT date, userId, sessionId,
                       json_extract(homeServerConnectionConfigJson, '$.homeServerUri'),
                       isTokenValid
                FROM session_params"""):
            data_list.append((_ms_to_utc(date), user_id, session_id, home_server,
                              _yes_no(token_valid), source_file))

    data_headers = (('Session Date', 'datetime'), 'Signed-in User ID', 'Session ID',
                    'Home Server', 'Token Valid', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def get_reddit_subreddits(context):
    data_list = []
    source_path = ''
    for reddit_db in _reddit_dbs(context):
        source_path = source_path or reddit_db
        source_file = context.get_relative_path(reddit_db)
        for (created, name_prefixed, title, subreddit_type, subscribers, active,
             public_description, subreddit_id, kind_with_id) in _rows(reddit_db, """
                SELECT createdUtc, displayNamePrefixed, title, subredditType,
                       subscribers, accountsActive, publicDescription, subredditId,
                       subredditKindWithId
                FROM subreddit ORDER BY displayNamePrefixed"""):
            data_list.append((
                _s_to_utc(created), name_prefixed, title, subreddit_type, subscribers,
                active, public_description, subreddit_id, kind_with_id, source_file))

    data_headers = (('Created', 'datetime'), 'Community', 'Title',
                    'Type (as stored)', 'Subscribers', 'Accounts Active',
                    'Public Description', 'Subreddit ID', 'Kind With ID', 'Source File')
    return data_headers, data_list, source_path


@artifact_processor
def get_reddit_posts(context):
    data_list = []
    source_path = ''
    for reddit_db in _reddit_dbs(context):
        source_path = source_path or reddit_db
        source_file = context.get_relative_path(reddit_db)
        for (created, author, title, community, score, comments, domain, over_18,
             permalink, url, link_id, position, listing_id) in _rows(reddit_db, """
                SELECT json_extract(linkJson, '$.created_utc'),
                       json_extract(linkJson, '$.author'),
                       json_extract(linkJson, '$.title'),
                       json_extract(linkJson, '$.subreddit_name_prefixed'),
                       json_extract(linkJson, '$.score'),
                       json_extract(linkJson, '$.num_comments'),
                       json_extract(linkJson, '$.domain'),
                       json_extract(linkJson, '$.over_18'),
                       json_extract(linkJson, '$.permalink'),
                       json_extract(linkJson, '$.url'),
                       linkId, listingPosition, listingId
                FROM link ORDER BY listingId, listingPosition"""):
            data_list.append((
                _s_to_utc(created), author, title, community, score, comments, domain,
                _yes_no(over_18), permalink, url, link_id, position, listing_id,
                source_file))

    data_headers = (('Created', 'datetime'), 'Author', 'Title', 'Community', 'Score',
                    'Comments', 'Domain', 'Over 18', 'Permalink', 'URL', 'Link ID',
                    'Listing Position', 'Listing ID', 'Source File')
    return data_headers, data_list, source_path
