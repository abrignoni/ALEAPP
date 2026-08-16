# pylint: disable=W0702
__artifacts_v2__ = {
    "get_mewe_chat": {
        "name": "MeWe - Chat",
        "description": "Parses MeWe chat messages (timestamp, thread, user, message text, direction, type and attachments) from the MeWe chat database (app_database on older builds, app_v3.db on newer ones).",
        "author": "@A-725-K",
        "creation_date": "2021-11-10",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "MeWe",
        "notes": ("Source: MeWe moved its chat store from 'app_database' to 'app_v3.db'; both are read. "
                  "Newer builds leave an empty 'mewe_old' beside it, which is skipped.\n"
                  "Direction: 'Sent' means the account signed in on this device sent the message. "
                  "Its user ID is the suffix of the 'user_info<id>' key in SGSession.xml (see MeWe - "
                  "SGSession), which can be matched against User Id to confirm who the owner is. "
                  "Message Direction is read from the CHAT_MESSAGE 'currentUserMessage' flag; on a "
                  "schema generation that does not carry that column the direction cannot be "
                  "established and Message Direction is blank for every row of that database. In "
                  "the conversation view a blank direction is not attributed to the owner.\n"
                  "Thread Name is the other party on a one-to-one chat, not a group name; a Group Id "
                  "of 'contacts' likewise indicates a direct chat rather than a group.\n"
                  "Deleted: 'YES' is the app's own deletion flag. The row and its text are still "
                  "present here, so a deleted message can remain readable. The flag is read from the "
                  "CHAT_MESSAGE 'deleted' column; where that column is absent the cell is blank "
                  "rather than reported as 'NO'.\n"
                  "Shared locations arrive as an openstreetmap.org URL in Message Text, with the "
                  "coordinates in the mlat/mlon parameters.\n"
                  "Attachment Name is often empty even when Message Type is set (for example PHOTO); "
                  "the absence of a name does not mean the absence of an attachment.\n"
                  "Timestamps are UTC, converted from whole Unix seconds."),
        "paths": ('*/com.mewe/databases/app_database',
                  '*/com.mewe/databases/app_v3.db*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.mewe vc 90017000 | app_v3.db | 13 rows",
            "pixel7a_a14": "Android 14 | com.mewe vc 80116099 | app_v3.db | 18 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Thread Id",
                "conversationLabelColumn": "Thread Name",
                "textColumn": "Message Text",
                "directionColumn": "Message Direction",
                "directionSentValue": "Sent",
                "timeColumn": "Timestamp",
                "senderColumn": "User Name"
            }
        },
    },
    "get_mewe_posts": {
        "name": "MeWe - Posts",
        "description": "Feed posts cached by MeWe, including group, author, text, link, media and poll details.",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "MeWe",
        "notes": ("This is cached feed content, not an authorship record. Rows are posts held in "
                  "the app's POST table, so their presence shows what was cached on the device, "
                  "NOT that the device owner wrote, opened or read any of "
                  "it. In both test images every cached post belongs to someone else "
                  "(currentUserPost = 0 for all 74). Use 'Posted By Device Owner' = Yes to isolate "
                  "the owner's own posts.\n"
                  "A post is stored once per feed it was loaded into, so the same post can appear "
                  "more than once with a different Feed Context. That is reported rather than "
                  "de-duplicated, because which feed surfaced a post is itself informative. Treat "
                  "the Post Id, not the row, as the unit when counting distinct posts.\n"
                  "Poll Votes is the total across all voters, not the owner's vote.\n"
                  "Timestamps are UTC, converted from whole Unix seconds. An Edited value of 0 "
                  "renders blank and means never edited."),
        "paths": ('*/com.mewe/databases/app_database',
                  '*/com.mewe/databases/app_v3.db*'),
        "output_types": "standard",
        "artifact_icon": "news",
        "sample_data": {
            "pixel7a_a14": "Android 14 | app_v3.db | 74 rows",
            "hc_pixel8pro_a16": "Android 16 | app_v3.db | 0 rows (POST empty)",
        },
    },
    "get_mewe_comments": {
        "name": "MeWe - Comments",
        "description": "Comments on MeWe posts, with the text of the post each one replies to.",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-07-26",
        "requirements": "none",
        "category": "MeWe",
        "notes": ("Like MeWe - Posts, this is cached feed content: comments written by other people "
                  "on posts the app downloaded. Presence does not imply the device owner wrote or "
                  "read them. 'By Device Owner' = Yes marks the owner's own comments; in both test "
                  "images none of the 16 cached comments were the owner's.\n"
                  "'On Post By' and 'On Post Text' come from a LEFT JOIN to the cached post. If the "
                  "parent post is no longer cached these are blank, and the comment is still "
                  "reported rather than dropped; use Post Id to correlate.\n"
                  "Timestamps are UTC, from whole Unix seconds."),
        "paths": ('*/com.mewe/databases/app_database',
                  '*/com.mewe/databases/app_v3.db*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "pixel7a_a14": "Android 14 | app_v3.db | 16 rows",
            "hc_pixel8pro_a16": "Android 16 | app_v3.db | 0 rows (COMMENT empty)",
        },
    },
    "get_mewe_post_media": {
        "name": "MeWe - Post Media",
        "description": "Photos and videos attached to MeWe posts.",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-07-26",
        "requirements": "none",
        "category": "MeWe",
        "notes": ("Image URL and Video URL Template are server-side paths on MeWe's CDN "
                  "(for example /api/v2/photo/...), NOT files on the device. Do not expect to find "
                  "a file at that path. Any locally cached copy lives under the app's Glide cache "
                  "(cache/image_manager_disk_cache) under a hashed filename that cannot be "
                  "correlated back to these URLs by name.\n"
                  "Rows describe media attached to cached feed posts, so the same caveat as "
                  "MeWe - Posts applies: this is what was delivered to the device, not what the "
                  "owner posted or viewed.\n"
                  "Post context is a LEFT JOIN; where the parent post is no longer cached the "
                  "Post Created, Post Author and Group Name columns are blank and the media row is "
                  "still reported (3 of 69 rows in the Android 14 test image)."),
        "paths": ('*/com.mewe/databases/app_database',
                  '*/com.mewe/databases/app_v3.db*'),
        "output_types": "standard",
        "artifact_icon": "photo",
        "sample_data": {
            "pixel7a_a14": "Android 14 | app_v3.db | 69 rows",
        },
    },
    "get_mewe_polls": {
        "name": "MeWe - Polls",
        "description": "Poll questions and their options with vote counts, from MeWe posts.",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-07-26",
        "requirements": "none",
        "category": "MeWe",
        "notes": ("One row per poll option, so a poll spans several rows sharing a Post Id and "
                  "Question.\n"
                  "Option Votes and Total Votes are server-reported tallies across all voters. "
                  "Nothing here records how the device owner voted, or whether they voted at all; "
                  "the POST table's pollVoted flag carries that and was 0 for every cached poll in "
                  "the test image.\n"
                  "Counts are a snapshot from when the post was cached, not live values."),
        "paths": ('*/com.mewe/databases/app_database',
                  '*/com.mewe/databases/app_v3.db*'),
        "output_types": "standard",
        "artifact_icon": "chart-bar",
        "sample_data": {
            "pixel7a_a14": "Android 14 | app_v3.db | 30 rows across 3 polls",
        },
    },
    "get_mewe_reactions": {
        "name": "MeWe - Reactions",
        "description": "Emoji reactions on posts, comments and chat messages, including whether the device owner reacted.",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-07-26",
        "requirements": "none",
        "category": "MeWe",
        "notes": ("Reactions are stored as a per-emoji tally, not a list of reactors. A Reaction "
                  "Count of 106 means 106 reactions were reported by the server; it does NOT "
                  "identify, or make identifiable, who reacted. The single exception is "
                  "'Device Owner Reacted' = Yes, which is the only attributable reaction in this "
                  "artifact.\n"
                  "'Reacted To' says which object was reacted to (Post, Comment or Chat Message), "
                  "since the three come from separate tables merged here. Target Author, Target "
                  "Text and Target Created are LEFT JOINed from that object and are blank if it is "
                  "no longer cached.\n"
                  "Counts are a snapshot from when the object was cached, not live values."),
        "paths": ('*/com.mewe/databases/app_database',
                  '*/com.mewe/databases/app_v3.db*'),
        "output_types": "standard",
        "artifact_icon": "mood-smile",
        "sample_data": {
            "pixel7a_a14": "Android 14 | app_v3.db | 240 rows (227 post, 12 comment, 1 chat)",
            "hc_pixel8pro_a16": "Android 16 | app_v3.db | 2 rows (chat)",
        },
    },
    "get_mewe_groups": {
        "name": "MeWe - Groups and Pages",
        "description": "Cached group, page and community records from the MeWe database.",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "MeWe",
        "notes": ("Three tables are merged and the Type column says which one a row came from: "
                  "Group (GROUP_), Page (PAGE) or Community (COMMUNITY). The same entity can appear "
                  "twice, once as a Group or Page and again as a Community, because MeWe caches "
                  "both views; match on Id.\n"
                  "A cached row is not a membership record. A row can be present because the entity "
                  "was merely rendered in a feed. Confirmed is the isConfirmed flag of the GROUP_ / "
                  "COMMUNITY row rendered as Yes, and Role is built from the PAGE isOwner, isAdmin "
                  "and isFollower flags; what the app sets either of them for was not established, "
                  "so neither establishes that the account joined or follows the entity.\n"
                  "Last Opened is converted from milliseconds and reflects the last time the app "
                  "surfaced the entity, which is not necessarily a deliberate visit by the user."),
        "paths": ('*/com.mewe/databases/app_database',
                  '*/com.mewe/databases/app_v3.db*'),
        "output_types": "standard",
        "artifact_icon": "users-group",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | app_v3.db | 4 rows (1 group, 1 page, 2 community)",
            "pixel7a_a14": "Android 14 | app_v3.db | 2 rows",
        },
    },
    "get_mewe_chat_participants": {
        "name": "MeWe - Chat Participants",
        "description": "Members of each MeWe chat thread.",
        "author": "@AlexisBrignoni",
        "creation_date": "2026-07-26",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "MeWe",
        "notes": ("Rows are the participants recorded for a thread in CHAT_THREAD_PARTICIPANT. "
                  "Whether the device owner is listed among them was not established; each test "
                  "image yielded a single participant row in total. Cross-reference Participant Id "
                  "against the 'user_info<id>' key in SGSession.xml to identify the owner where "
                  "one is listed.\n"
                  "Status is the presence value last cached by the app (typically OFFLINE) and "
                  "carries no timestamp, so it should not be read as a state at any particular "
                  "moment.\n"
                  "Only participants present in CHAT_THREAD_PARTICIPANT appear. A thread with no "
                  "rows in that table yields no participants here; why rows are absent for a given "
                  "thread was not established."),
        "paths": ('*/com.mewe/databases/app_database',
                  '*/com.mewe/databases/app_v3.db*'),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | app_v3.db | 1 row",
            "pixel7a_a14": "Android 14 | app_v3.db | 1 row",
        },
    },
    "get_mewe_session": {
        "name": "MeWe - SGSession",
        "description": "Parses MeWe session preferences (key and value) from the SGSession.xml file.",
        "author": "@A-725-K",
        "creation_date": "2021-11-10",
        "last_update_date": "2021-11-10",
        "requirements": "none",
        "category": "MeWe",
        "notes": ("Identifies the account signed in on the device: the key 'user_info<id>' carries "
                  "the owner's MeWe user ID as its suffix, which is the value to match against "
                  "User Id / Sender fields in the other MeWe artifacts to establish who the device "
                  "owner is.\n"
                  "Contains authentication material (user_token, refresh_token) and a token "
                  "expiration time. Handle accordingly.\n"
                  "Keys containing a dot are skipped as framework noise."),
        "paths": ('*/com.mewe/shared_prefs/SGSession.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "key",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.mewe vc 90017000 | 27 rows",
            "pixel7a_a14": "Android 14 | com.mewe vc 80116099 | 25 rows",
        },
    }
}

import datetime
import re
import sqlite3
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, logfunc, \
    does_column_exist_in_db, does_table_exist_in_db
from scripts.artifacts.storagePathViews import unique_files

# Module-level constants (kept for backwards-compatibility; snapchat.py imports APP_NAME)
APP_NAME = 'MeWe'
DB_NAME = 'app_database'
# MeWe renamed the chat store to app_v3.db. Both carry the same CHAT_MESSAGE /
# CHAT_THREAD shape, so one query serves both; only the filename changed. Newer
# builds also leave a 'mewe_old' database in place, but it holds no chat tables.
DB_NAME_V3 = 'app_v3.db'
DB_NAMES = (DB_NAME, DB_NAME_V3)
SGSESSION_FILE = 'SGSession.xml'

# Column availability is probed rather than assumed: the two database
# generations were seen in the wild years apart, and only app_v3.db is covered
# by a test image, so a missing column must degrade to a blank cell instead of
# failing the whole artifact.
OPTIONAL_COLUMNS = {
    'threadName': ('CHAT_THREAD', 'name'),
    'groupId': ('CHAT_THREAD', 'groupId'),
    'chatType': ('CHAT_THREAD', 'chatType'),
    'ownerId': ('CHAT_MESSAGE', 'ownerId'),
    'ownerName': ('CHAT_MESSAGE', 'ownerName'),
    'textPlain': ('CHAT_MESSAGE', 'textPlain'),
    'attachmentType': ('CHAT_MESSAGE', 'attachmentType'),
    'attachmentName': ('CHAT_MESSAGE', 'attachmentName'),
    'deleted': ('CHAT_MESSAGE', 'deleted'),
    'currentUserMessage': ('CHAT_MESSAGE', 'currentUserMessage'),
}


def _column_or_null(db_path, key):
    """Qualified column reference if the schema has it, else a NULL placeholder."""
    table, column = OPTIONAL_COLUMNS[key]
    if does_column_exist_in_db(db_path, table, column):
        return f'{table}.{column}'
    return 'NULL'


def _flag_case(column, when_one, when_zero):
    """CASE over an optional 0/1 flag. A missing column, a NULL and any value the flag
    does not define all yield a blank cell: the schema generation that lacks the column
    cannot establish the flag, so no meaning is asserted for it."""
    if column == 'NULL':
        return "''"
    return f"CASE {column} WHEN 1 THEN '{when_one}' WHEN 0 THEN '{when_zero}' ELSE '' END"


def _build_chat_query(db_path):
    """Assemble the chat query for whichever schema generation this database is."""
    threadName = _column_or_null(db_path, 'threadName')
    groupId = _column_or_null(db_path, 'groupId')
    chatType = _column_or_null(db_path, 'chatType')
    ownerId = _column_or_null(db_path, 'ownerId')
    ownerName = _column_or_null(db_path, 'ownerName')
    textPlain = _column_or_null(db_path, 'textPlain')
    attachmentType = _column_or_null(db_path, 'attachmentType')
    attachmentName = _column_or_null(db_path, 'attachmentName')
    deleted = _column_or_null(db_path, 'deleted')
    currentUserMessage = _column_or_null(db_path, 'currentUserMessage')

    return f'''
    SELECT
        CHAT_MESSAGE.createdAt,
        CHAT_MESSAGE.threadId,
        {threadName},
        {groupId},
        {chatType},
        {ownerId},
        {ownerName},
        {textPlain},
        {_flag_case(currentUserMessage, 'Sent', 'Received')},
        CASE {attachmentType} WHEN 'UNSUPPORTED' THEN '' ELSE {attachmentType} END,
        {attachmentName},
        {_flag_case(deleted, 'YES', 'NO')}
    FROM CHAT_MESSAGE
    JOIN CHAT_THREAD ON CHAT_MESSAGE.threadId = CHAT_THREAD.id
    ORDER BY CHAT_MESSAGE.createdAt
'''


INVALID_XML_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
BARE_AMPERSAND = re.compile(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9A-Fa-f]+);)')


def _parse_xml(file_found):
    """Parse XML, recovering from invalid tokens / unescaped ampersands; empty element if unparseable."""
    try:
        return ET.parse(file_found).getroot()
    except ET.ParseError:
        with open(file_found, encoding='utf-8', errors='replace') as f:
            xml = BARE_AMPERSAND.sub('&amp;', INVALID_XML_CHARS.sub('', f.read()))
        try:
            return ET.fromstring(xml)
        except ET.ParseError as ex:
            logfunc(f'Skipping unparseable XML {file_found}: {ex}')
            return ET.Element('empty')


@artifact_processor
def get_mewe_chat(context):
    files_found = unique_files(context)
    data_list = []
    sources = []
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith(('-wal', '-shm', '-journal')):
            continue
        if not file_found.endswith(DB_NAMES):
            continue
        # Newer installs keep an empty 'mewe_old' alongside app_v3.db, and a
        # database can be present without ever having held a chat.
        if not does_table_exist_in_db(file_found, 'CHAT_MESSAGE'):
            continue

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        try:
            cursor.execute(_build_chat_query(file_found))
            rows = cursor.fetchall()
        except sqlite3.Error as ex:
            logfunc(f'Could not read MeWe chats from {file_found}: {ex}')
            rows = []
        db.close()

        if rows:
            sources.append(file_found)
        for row in rows:
            timestamp = datetime.datetime.fromtimestamp(int(row[0]), datetime.timezone.utc) if row[0] else ''
            # Columns absent from this schema generation come back as NULL; report
            # them as empty cells rather than the string "None".
            values = tuple('' if value is None else value for value in row[1:])
            data_list.append((timestamp,) + values)

    source_path = ', '.join(sources)
    data_headers = (('Timestamp', 'datetime'), 'Thread Id', 'Thread Name', 'Group Id', 'Chat Type',
                    'User Id', 'User Name', 'Message Text', 'Message Direction', 'Message Type',
                    'Attachment Name', 'Deleted')
    return data_headers, data_list, source_path


@artifact_processor
def get_mewe_session(context):
    files_found = unique_files(context)
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith(('-wal', '-shm', '-journal')):
            continue
        if not file_found.endswith(SGSESSION_FILE):
            continue

        source_path = file_found
        root = _parse_xml(file_found)
        for node in root:
            if '.' in node.attrib['name']:
                continue  # skip not relevant keys
            try:
                value = node.attrib['value']
            except:
                value = node.text
            data_list.append((node.attrib['name'], value))

    data_headers = ('Key', 'Value')
    return data_headers, data_list, source_path


# Tables that only exist in the newer app_v3.db generation. Each processor
# checks for its own table so an older database simply yields no rows.
def _chat_databases(files_found):
    """Yield MeWe chat databases, skipping the empty 'mewe_old' left by upgrades."""
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith(('-wal', '-shm', '-journal')):
            continue
        if file_found.endswith(DB_NAMES):
            yield file_found


def _rows(db_path, query):
    """Run a read-only query, logging and swallowing schema mismatches."""
    db = open_sqlite_db_readonly(db_path)
    try:
        return db.cursor().execute(query).fetchall()
    except sqlite3.Error as ex:
        logfunc(f'MeWe: query failed on {db_path}: {ex}')
        return []
    finally:
        db.close()


def _epoch(value):
    """MeWe stores whole seconds; 0 means unset."""
    if not value:
        return ''
    return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)


def _millis(value):
    """A few columns (lastVisit, lastOpenTime) are milliseconds instead."""
    if not value:
        return ''
    return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)


def _feed_context(is_all, is_discovery, is_favorite, in_profile, is_refpost):
    """Name the feed a post row was cached for; the same post can be in several."""
    parts = []
    if is_all:
        parts.append('All Feed')
    if is_discovery:
        parts.append('Discovery')
    if is_favorite:
        parts.append('Favorites')
    if in_profile:
        parts.append('Profile')
    if is_refpost:
        parts.append('Reshared')
    return ', '.join(parts)


def _collect(context, table, query, build, headers):
    """Shared shape: run query against every MeWe database holding `table`."""
    data_list = []
    sources = []
    for db_path in _chat_databases(unique_files(context)):
        if not does_table_exist_in_db(db_path, table):
            continue
        rows = _rows(db_path, query)
        if rows:
            sources.append(db_path)
        for row in rows:
            data_list.append(build(row))
    return headers, data_list, ', '.join(sources)


POSTS_QUERY = '''
    SELECT createdAt, editedAt, ownerName, ownerHandle, groupName, groupId, textPlain,
           currentUserPost, commentsCount, mediasCount, sharesCount, hasLink, linkUrl,
           linkTitle, albumName, pollQuestion, pollVotes, eventName, eventLocation,
           isAllfeed, isDiscoveryFeed, isFavoriteFeed, inProfile, isRefpost, id
    FROM POST ORDER BY createdAt DESC
'''


@artifact_processor
def get_mewe_posts(context):
    headers = (('Created', 'datetime'), ('Edited', 'datetime'), 'Author', 'Author Handle',
               'Group Name', 'Group Id', 'Text', 'Posted By Device Owner', 'Comments',
               'Media Count', 'Shares', 'Link URL', 'Link Title', 'Album Name',
               'Poll Question', 'Poll Votes', 'Event Name', 'Event Location',
               'Feed Context', 'Post Id')

    def build(r):
        return (_epoch(r[0]), _epoch(r[1]), r[2], r[3], r[4], r[5], r[6],
                'Yes' if r[7] else '', r[8], r[9], r[10],
                r[12] if r[11] else '', r[13] if r[11] else '', r[14],
                r[15], r[16] if r[15] else '', r[17], r[18],
                _feed_context(r[19], r[20], r[21], r[22], r[23]), r[24])

    return _collect(context, 'POST', POSTS_QUERY, build, headers)


COMMENTS_QUERY = '''
    SELECT c.createdAt, c.editedAt, c.ownerName, c.ownerHandle, c.textPlain,
           c.currentUserPost, c.repliesCount, c.hasPhoto, c.photoName, c.hasAudio,
           c.audioDuration, c.hasLink, c.linkUrl, c.documentName, c.postId,
           p.textPlain, p.ownerName, c.id
    FROM COMMENT c
    LEFT JOIN POST p ON p.id = c.postId
    ORDER BY c.createdAt DESC
'''


@artifact_processor
def get_mewe_comments(context):
    headers = (('Created', 'datetime'), ('Edited', 'datetime'), 'Author', 'Author Handle',
               'Comment Text', 'By Device Owner', 'Replies', 'Has Photo', 'Photo Name',
               'Has Audio', 'Audio Duration', 'Link URL', 'Document Name',
               'On Post By', 'On Post Text', 'Post Id', 'Comment Id')

    def build(r):
        return (_epoch(r[0]), _epoch(r[1]), r[2], r[3], r[4],
                'Yes' if r[5] else '', r[6], 'Yes' if r[7] else '', r[8],
                'Yes' if r[9] else '', r[10], r[12] if r[11] else '', r[13],
                r[16], r[15], r[14], r[17])

    return _collect(context, 'COMMENT', COMMENTS_QUERY, build, headers)


POST_MEDIA_QUERY = '''
    SELECT m.postId, m.type, m.mime, m.name, m.imageUrl, m.imageWidth, m.imageHeight,
           m.videoUrlTemplate, m.availableVideoResolutions, p.createdAt, p.ownerName,
           p.groupName, m.itemId
    FROM POST_MEDIA m
    LEFT JOIN POST p ON p.id = m.postId
'''


@artifact_processor
def get_mewe_post_media(context):
    headers = (('Post Created', 'datetime'), 'Post Author', 'Group Name', 'Media Type',
               'MIME Type', 'File Name', 'Image URL', 'Width', 'Height',
               'Video URL Template', 'Video Resolutions', 'Post Id', 'Item Id')

    def build(r):
        return (_epoch(r[9]), r[10], r[11], r[1], r[2], r[3], r[4], r[5], r[6],
                r[7], r[8], r[0], r[12])

    return _collect(context, 'POST_MEDIA', POST_MEDIA_QUERY, build, headers)


POLLS_QUERY = '''
    SELECT p.createdAt, p.ownerName, p.groupName, p.pollQuestion, p.pollClosed,
           p.pollEndDate, p.pollVotes, o.text, o.votes, o.position, o.imageUrl, p.id
    FROM POLL_OPTION o
    LEFT JOIN POST p ON p.id = o.postId
    ORDER BY p.createdAt DESC, o.position
'''


@artifact_processor
def get_mewe_polls(context):
    headers = (('Post Created', 'datetime'), 'Author', 'Group Name', 'Question',
               'Option', 'Option Votes', 'Option Position', 'Total Votes', 'Closed',
               ('Ends', 'datetime'), 'Option Image URL', 'Post Id')

    def build(r):
        return (_epoch(r[0]), r[1], r[2], r[3], r[7], r[8], r[9], r[6],
                'Yes' if r[4] else '', _epoch(r[5]), r[10], r[11])

    return _collect(context, 'POLL_OPTION', POLLS_QUERY, build, headers)


# Reactions live in three parallel tables, one per reactable object.
REACTION_SOURCES = (
    ('EMOJI_POST', 'Post', '''
        SELECT e.key, e.count, e.userReacted, e.postId, p.ownerName, p.textPlain, p.createdAt
        FROM EMOJI_POST e LEFT JOIN POST p ON p.id = e.postId'''),
    ('EMOJI_COMMENT', 'Comment', '''
        SELECT e.key, e.count, e.userReacted, e.commentId, c.ownerName, c.textPlain, c.createdAt
        FROM EMOJI_COMMENT e LEFT JOIN COMMENT c ON c.id = e.commentId'''),
    ('EMOJI_CHAT_MESSAGE', 'Chat Message', '''
        SELECT e.key, e.count, e.userReacted, e.chatMessageId, m.ownerName, m.textPlain, m.createdAt
        FROM EMOJI_CHAT_MESSAGE e LEFT JOIN CHAT_MESSAGE m ON m.id = e.chatMessageId'''),
)


@artifact_processor
def get_mewe_reactions(context):
    headers = (('Target Created', 'datetime'), 'Reacted To', 'Emoji', 'Reaction Count',
               'Device Owner Reacted', 'Target Author', 'Target Text', 'Target Id')
    data_list = []
    sources = []

    for db_path in _chat_databases(unique_files(context)):
        found_any = False
        for table, label, query in REACTION_SOURCES:
            if not does_table_exist_in_db(db_path, table):
                continue
            for row in _rows(db_path, query):
                found_any = True
                data_list.append((_epoch(row[6]), label, row[0], row[1],
                                  'Yes' if row[2] else '', row[4], row[5], row[3]))
        if found_any:
            sources.append(db_path)

    return headers, data_list, ', '.join(sources)


@artifact_processor
def get_mewe_groups(context):
    headers = (('Last Opened', 'datetime'), 'Type', 'Name', 'Description', 'Access',
               'Role', 'Public', 'Confirmed', 'Verified', 'Followers', 'Public URL Id',
               'Owner Id', 'Id')
    data_list = []
    sources = []

    for db_path in _chat_databases(unique_files(context)):
        found_any = False

        if does_table_exist_in_db(db_path, 'GROUP_'):
            for r in _rows(db_path, '''SELECT lastOpenTime, name, descriptionPlain,
                    groupAccessType, roleEnum, isPublic, isConfirmed, publicUrlId,
                    ownerId, _id FROM GROUP_'''):
                found_any = True
                data_list.append((_millis(r[0]), 'Group', r[1], r[2], r[3], r[4],
                                  'Yes' if r[5] else '', 'Yes' if r[6] else '', '',
                                  '', r[7], r[8], r[9]))

        if does_table_exist_in_db(db_path, 'PAGE'):
            for r in _rows(db_path, '''SELECT name, description, categoryName, followers,
                    isVerified, isFollower, isOwner, isAdmin, urlId, id FROM PAGE'''):
                found_any = True
                role = ', '.join(n for n, f in
                                 (('Owner', r[6]), ('Admin', r[7]), ('Follower', r[5])) if f)
                data_list.append(('', 'Page', r[0], r[1], r[2], role, '', '',
                                  'Yes' if r[4] else '', r[3], r[8], '', r[9]))

        if does_table_exist_in_db(db_path, 'COMMUNITY'):
            for r in _rows(db_path, '''SELECT lastVisit, name, type, isConfirmed,
                    isVerified, id FROM COMMUNITY'''):
                found_any = True
                data_list.append((_millis(r[0]), f'Community ({r[2]})', r[1], '', '', '',
                                  '', 'Yes' if r[3] else '', 'Yes' if r[4] else '',
                                  '', '', '', r[5]))

        if found_any:
            sources.append(db_path)

    return headers, data_list, ', '.join(sources)


PARTICIPANTS_QUERY = '''
    SELECT p.name, p.handle, p.status, p.isOwner, p.isAdmin, p.fingerprint,
           t.name, t.chatType, p.chatThreadId, p.id
    FROM CHAT_THREAD_PARTICIPANT p
    LEFT JOIN CHAT_THREAD t ON t.id = p.chatThreadId
'''


@artifact_processor
def get_mewe_chat_participants(context):
    headers = ('Thread Name', 'Chat Type', 'Participant', 'Handle', 'Status',
               'Is Owner', 'Is Admin', 'Fingerprint', 'Thread Id', 'Participant Id')

    def build(r):
        return (r[6], r[7], r[0], r[1], r[2], 'Yes' if r[3] else '',
                'Yes' if r[4] else '', r[5], r[8], r[9])

    return _collect(context, 'CHAT_THREAD_PARTICIPANT', PARTICIPANTS_QUERY, build, headers)
