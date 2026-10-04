# pylint: disable=W0718
__artifacts_v2__ = {
    "get_line": {
        "name": "Line - Contacts",
        "description": "Parses LINE contacts (user ID and name) from the LINE databases.",
        "author": "@markmckinnon",
        "creation_date": "2021-03-15",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Line",
        "notes": ("One row per row of the contacts table in each naver_line database. The "
                  "duplicate storage views of one database are collapsed first, and where "
                  "the extraction holds more than one database (a second Android user) every "
                  "one is read, with Android User carrying the user number taken from the "
                  "database's path. Every tested image held one Android user, so the two user case was "
                  "checked on a tree built by hand from the pixel3_a12 database, carrying a "
                  "second user whose copy had one contact removed: it returned five rows "
                  "under user 0 and four under user 10, where the code before this change "
                  "returned five rows from one database. "
                  "The table records contacts the app held, which is not the same set as the "
                  "people the account exchanged messages with.\n"
                  "It can be empty on a device that has messages: on the tested Android 14 "
                  "image it held no rows while chat_history held 30, so zero rows here is not "
                  "evidence that the account had no contacts. The tested images held 6, 5 and "
                  "0 rows."),
        "paths": ('*/jp.naver.line.android/databases/**',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "users",
        "sample_data": {
            "pixel3_a11": "Android 11 | jp.naver.line.android | 6 rows",
            "pixel3_a12": "Android 12 | jp.naver.line.android | 5 rows",
            "pixel7a_a14": "Android 14 | jp.naver.line.android vc 141220285 | 0 rows, "
                           "contacts table empty while chat_history holds rows",
        },
    },
    "get_line_messages": {
        "name": "Line - Messages",
        "description": "LINE messages, with any picture the app kept shown on the message's own "
                       "row, plus time, sender, thread, and direction and recipient as the "
                       "store records them.",
        "author": "@markmckinnon",
        "creation_date": "2021-03-15",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Line",
        "notes": ("Direction is decoded from the chat_history 'status' column, 1 read as "
                  "Incoming and 2 as Outgoing, with every other value reported as stored. "
                  "That mapping predates this work and no source for it was found.\n"
                  "In the conversation view only rows carrying the declared sent value, "
                  "Outgoing, are counted as sent and every other row is counted as "
                  "received, which is how LAVA classifies a conversation "
                  "(src/renderer/api/platform.electron.js).\n"
                  "Thread ID is the row's own chat_history.chat_id on every row. To ID is "
                  "filled only for rows recognized as Outgoing whose chat id has rows in the "
                  "membership table, and it holds that table's m_id values for the chat id "
                  "(membership is keyed on id and m_id). On every other row it is blank; a "
                  "chat id is not reported as a recipient. Whether the member list includes "
                  "the account itself was not established. No tested row was Outgoing and "
                  "the membership table was empty on all three tested images, so both were "
                  "checked on a database built by hand from the pixel3_a12 one, with "
                  "membership rows and Outgoing rows added: the three rows whose chat id "
                  "matched membership carried their chat id in Thread ID where the code "
                  "before this change left it blank, the two Outgoing rows in chats with "
                  "membership rows carried the member list in To ID, and an Outgoing row in "
                  "a chat with no membership rows had a blank To ID where the code before "
                  "this change put the chat id.\n"
                  "Nothing in the tested images exercises the Direction mapping. On all three, "
                  "chat_history.status held 3 on every one of the 64 "
                  "reported rows, so no row was labelled Incoming or Outgoing, To ID was "
                  "empty on every row, and the membership table was empty, which means the "
                  "conversation view attributed no message to the device owner. What a "
                  "status of 3 denotes was not established and it is reported as stored. "
                  "from_mid was absent on 29 of those rows and present on 35, and whether "
                  "that distinguishes direction was not established either.\n"
                  "Messages are reported even when the contacts and membership tables are "
                  "empty; on a tested Android 14 image both were empty while chat_history "
                  "held rows, and the previous inner join dropped every message.\n"
                  "Attachment shows the file the app kept for that message, on the message's "
                  "own row. The link is one the app recorded rather than a match on size or "
                  "time: the app writes the file to files/chats/<chat id>/messages/<message "
                  "id>, so the folder is the row's chat_id and the file name is the row's id. "
                  "Every one of the seven attachment files across the tested images sat under "
                  "the chat_id its row names and was named for that row's id.\n"
                  "Those files are not in the app's private storage. On both tested images "
                  "that carry them they sit in the user's external storage, under "
                  "Android/data/jp.naver.line.android/files/chats, while the database sits in "
                  "the app's private storage, so an extraction that collected one and not the "
                  "other will show messages with no picture or files with no message.\n"
                  "A full file and a .thumb sibling can both exist. The full file is the one "
                  "shown; the thumbnail is shown only when the full file is absent, and "
                  "Attachment File names which of the two was used, so a row reading .thumb is "
                  "a row whose full sized file was not in the extraction. That case is real: "
                  "on the tested Android 12 image one row had a thumbnail and no full file.\n"
                  "Attachment Format is read from the file's leading bytes rather than from "
                  "its name, because these files carry no extension. All seven files across "
                  "the tested images were JPEG. A file whose bytes match no known signature is "
                  "reported by name and format so the examiner knows it exists, and is not "
                  "rendered.\n"
                  "Because the two live in different places, a file is paired with a message "
                  "on the Android user both belong to, read from the path: data/data is user "
                  "0, and data/user/<n>, data_mirror, data/media/<n> and storage/emulated/<n> "
                  "name their own. Where no user can be read from a path, nothing is paired "
                  "with it and a line is logged, because a wrong picture on a message is "
                  "worse than no picture.\n"
                  "The app keeps a separate database per Android user and every one of them "
                  "is read, with Android User carrying the one each row came from, rather "
                  "than only the last database the extraction happened to offer. The "
                  "duplicate storage views of one file are collapsed first, so a database is "
                  "not read once per view. Every tested image held one Android user, so the "
                  "two user case was checked on a tree built by hand from one of them, "
                  "carrying a second user whose chat folder held files of the same names "
                  "with different content: the rows doubled to twenty six under each user, "
                  "a message altered in the added copy appeared only against that user, and "
                  "each row resolved to the file in its own user's storage. Read the way it "
                  "was before this change, the same tree returned one user's twenty six "
                  "rows and none of the other's.\n"
                  "Attachment Type and Local URI are reported as stored. No source for the "
                  "type codes was found, so none is named here. The values seen on the "
                  "tested images were 0, 1, 2, 4, 15, 16 and 17; the four rows that resolved "
                  "to a file all carried type 1. Rows with a type of 6 are excluded here and "
                  "calls are reported by the Line - Call Logs artifact from call_history; no "
                  "source for that type reading is named. Local URI held a value on "
                  "one row of one tested image, a content:// MediaStore reference to a video, "
                  "and was null on every other row; it is reported as stored and is not "
                  "resolved to a file here."),
        "paths": ('*/jp.naver.line.android/databases/**',
                  '*/jp.naver.line.android/files/chats/*'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "pixel3_a11": "Android 11 | jp.naver.line.android | 12 rows",
            "pixel3_a12": "Android 12 | jp.naver.line.android | 26 rows",
            "pixel7a_a14": "Android 14 | jp.naver.line.android vc 141220285 | 26 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Thread ID",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Start Time",
                "senderColumn": "From ID",
                "mediaColumn": "Attachment"
            }
        },
    },
    "get_line_calls": {
        "name": "Line - Call Logs",
        "description": "Parses LINE call logs (start and end time, participant IDs, direction and call type) from the LINE databases.",
        "author": "@markmckinnon",
        "creation_date": "2021-03-15",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Line",
        "notes": ("Direction is decoded from the last character of the call_history 'call_type' "
                  "column, O read as Outgoing and I as Incoming, and Call Type from the "
                  "'voip_type' letter, V read as Video, A as Audio and G as a group call whose "
                  "media type is then read from voip_gc_media_type. Those mappings predate this "
                  "work and no source for them was found; every other value is reported as "
                  "stored.\n"
                  "On the tested images call_type ended in O or I on all twelve rows, six of "
                  "each, and voip_type held only A or V, six of each, so those four readings "
                  "are the ones the data exercises and the G branch is code present and "
                  "unexercised.\n"
                  "To ID is filled only for rows recognized as outgoing, and it is read "
                  "from the membership table, so it names the members of a group call and "
                  "is empty for a one to one call. On the tested images direction did "
                  "resolve, two Incoming and two Outgoing on each, and To ID was empty on "
                  "all twelve rows because every tested call was one to one and the "
                  "membership table was empty.\n"
                  "Calls are read from each call_history database that has a naver_line "
                  "database in the same folder, because the query reads the contacts and "
                  "membership tables from it; a call_history with none beside it is not "
                  "read and a line is logged. The duplicate storage views of one database "
                  "are collapsed first, and where the extraction holds more than one (a "
                  "second Android user) every one is read, with Android User carrying the "
                  "user number taken from the database's path. Every tested image held one "
                  "Android user, so the two user case was checked on a tree built by hand from the "
                  "pixel3_a12 databases, carrying a second user whose copy had one call "
                  "removed: it returned four rows under user 0 and three under user 10, "
                  "where the code before this change returned four rows from one "
                  "database. "
                  "Calls are reported even when the contacts and membership tables are empty; "
                  "on a tested Android 14 image both were empty while call_history held rows, "
                  "and the previous inner join dropped every call."),
        "paths": ('*/jp.naver.line.android/databases/**',),
        "output_types": "standard",
        "artifact_icon": "phone-call",
        "sample_data": {
            "pixel3_a11": "Android 11 | jp.naver.line.android | 4 rows",
            "pixel3_a12": "Android 12 | jp.naver.line.android | 4 rows",
            "pixel7a_a14": "Android 14 | jp.naver.line.android vc 141220285 | 4 rows",
        },
    }
}

import datetime
import os
import re

from scripts import filetype
from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (artifact_processor, attach_sqlite_db_readonly, check_in_media,
                               logfunc, open_sqlite_db_readonly)


def _sec_to_utc(value):
    if value:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    return ''


# The app writes a message's attachment to files/chats/<chat id>/messages/<message id>, with a
# ".thumb" sibling for the thumbnail, so the file itself carries the link the app recorded.
_CHATS = '/jp.naver.line.android/files/chats/'
# The database sits in the app's private storage and the chat files in the user's external
# storage, so the two share no directory and are paired on the Android user instead. Ordered
# with the views that name a user first; data/data is user 0 by definition.
_USER_VIEWS = (
    re.compile(r'(?:^|/)data/user/(\d+)/jp\.naver\.line\.android/'),
    re.compile(r'(?:^|/)data/user_de/(\d+)/jp\.naver\.line\.android/'),
    re.compile(r'(?:^|/)data_mirror/data_[cd]e/[^/]+/(\d+)/jp\.naver\.line\.android/'),
    re.compile(r'(?:^|/)data/media/(\d+)/Android/data/jp\.naver\.line\.android/'),
    re.compile(r'(?:^|/)storage/emulated/(\d+)/Android/data/jp\.naver\.line\.android/'),
)
_USER_ZERO = re.compile(r'(?:^|/)data/data/jp\.naver\.line\.android/')


def _android_user(path):
    """The Android user a Line file belongs to, or '' when the path does not name one."""
    path = str(path).replace('\\', '/')
    for pattern in _USER_VIEWS:
        match = pattern.search(path)
        if match:
            return match.group(1)
    return '0' if _USER_ZERO.search(path) else ''


def _attachment_files(files_found, user):
    """{(chat id, message id): {'full': path, 'thumb': path}} for one Android user.

    Only files belonging to the same Android user as the database are paired, so a second
    user's copy of the app cannot supply a picture for this one's message. When the user
    cannot be read from a path nothing is paired with it, because a wrong picture on a
    message is worse than no picture.
    """
    found = {}
    for file_found in files_found:
        path = str(file_found).replace('\\', '/')
        if _CHATS not in path or os.path.isdir(path):
            continue
        if not user or _android_user(path) != user:
            continue
        parts = path.split(_CHATS, 1)[1].split('/')
        if len(parts) < 3 or parts[1] != 'messages':
            continue
        chat_id, name = parts[0], parts[-1]
        kind = 'thumb' if name.endswith('.thumb') else 'full'
        message_id = name[:-len('.thumb')] if kind == 'thumb' else name
        found.setdefault((chat_id, message_id), {})[kind] = file_found
    return found


def _attachment(pair):
    """(media reference, file name shown, format) for the best file of a message.

    The full sized file is preferred and the thumbnail is used only when it is absent, so a
    row naming a ".thumb" file is one whose full sized file was not in the extraction. The
    format is read from the leading bytes rather than from the name, because these files
    carry no extension, and a file whose bytes match no known signature is reported by name
    and not rendered.
    """
    path = pair.get('full') or pair.get('thumb')
    if not path:
        return '', '', ''
    name = os.path.basename(str(path).replace('\\', '/'))
    try:
        kind = filetype.guess(str(path))
    except Exception as ex:                      # pylint: disable=broad-except
        logfunc(f'Line: could not read {name}: {ex}')
        kind = None
    if not kind:
        return '', name, 'unrecognised'
    reference = check_in_media(str(path), name, force_type=kind.mime,
                               force_extension=kind.extension)
    return reference or '', name, kind.mime


def _message_dbs(files_found):
    """Every naver_line the extraction carries, one per Android user after the views collapse.

    The app keeps a separate database per Android user, so taking one of them drops the
    other user's messages with no error.
    """
    found = []
    for file_found in files_found:
        path = str(file_found)
        if path.lower().endswith('naver_line') and path not in found:
            found.append(path)
    return found


def _call_dbs(files_found):
    """(call_history, the naver_line beside it or '') for every call_history found.

    The two databases of one Android user sit in the same databases folder, so the pair is
    made on the folder and one user's calls are never read against another user's tables.
    """
    beside = {os.path.dirname(path.replace('\\', '/')): path
              for path in _message_dbs(files_found)}
    found = []
    for file_found in files_found:
        path = str(file_found)
        if path.lower().endswith('call_history') and path not in [pair[0] for pair in found]:
            found.append((path, beside.get(os.path.dirname(path.replace('\\', '/')), '')))
    return found


@artifact_processor
def get_line(context):
    # One naver_line per Android user survives the collapse of the storage views, and every
    # one is read.
    files_found = unique_files(context)
    data_list = []
    read = []
    for msg_db in _message_dbs(files_found):
        user = _android_user(msg_db)
        db = open_sqlite_db_readonly(msg_db)
        cursor = db.cursor()
        try:
            cursor.execute('SELECT m_id, server_name FROM contacts')
            all_rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            all_rows = []
        db.close()
        if all_rows:
            read.append(msg_db)
        for row in all_rows:
            data_list.append((row[0], row[1], user))

    data_headers = ('user_id', 'user_name', 'Android User')
    return data_headers, data_list, '\n'.join(read)


@artifact_processor
def get_line_messages(context):
    # The duplicate storage views of one file are collapsed first, so a database is not read
    # once per view. What survives is one database per Android user, and every one is read.
    files_found = unique_files(context)
    data_list = []
    read = []
    for msg_db in _message_dbs(files_found):
        user = _android_user(msg_db)
        if not user:
            logfunc('Line: the Android user could not be read from the database path, '
                    'so no attachment is paired with a message')
        attachments = _attachment_files(files_found, user)
        db = open_sqlite_db_readonly(msg_db)
        cursor = db.cursor()
        try:
            # LEFT JOIN from chat_history: newer app versions leave the contacts
            # and membership tables empty while chat_history still holds rows,
            # and an inner join against that empty contact book dropped every
            # message. COALESCE keeps the chat id for rows with no match, and
            # guards the type filter against a NULL attachement_type.
            cursor.execute('''
                SELECT COALESCE(contact_book_w_groups.id, messages.chat_id),
                       contact_book_w_groups.members, messages.from_mid,
                       messages.content, messages.created_time/1000, messages.attachement_type,
                       messages.attachement_local_uri,
                       case messages.status when 1 then "Incoming" when 2 then "Outgoing" else messages.status end status,
                       messages.id, messages.chat_id
                FROM   chat_history AS messages
                       LEFT JOIN (SELECT id, Group_concat(M.m_id) AS members
                                  FROM   membership AS M GROUP BY id
                                  UNION
                                  SELECT m_id, NULL FROM contacts) AS contact_book_w_groups
                              ON messages.chat_id = contact_book_w_groups.id
                WHERE  COALESCE(messages.attachement_type, -1) != 6
            ''')
            all_rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            all_rows = []
        db.close()
        if all_rows:
            read.append(msg_db)

        for row in all_rows:
            # Thread ID is the row's own chat_id on every row. To ID is the membership
            # table's member list for that chat id and nothing else: a chat id is not
            # reported as a recipient.
            thread_id = row[9]
            to_id = row[1] if row[7] == "Outgoing" else None
            # The pairing is on the row's own chat_id and id, which is where the app wrote the
            # file, not on the chat the join resolved, so an unmatched contact cannot move it.
            media, media_name, media_format = _attachment(
                attachments.get((str(row[9]), str(row[8])), {}))
            created_time = _sec_to_utc(row[4])
            data_list.append((created_time, row[7], row[2], row[3], media, media_name,
                              media_format, row[5], row[6], to_id, thread_id, user))

    data_headers = (('Start Time', 'datetime'), 'Direction', 'From ID', 'Message',
                    ('Attachment', 'media'), 'Attachment File', 'Attachment Format',
                    'Attachment Type (as stored)', 'Local URI (as stored)', 'To ID', 'Thread ID',
                    'Android User')
    return data_headers, data_list, '\n'.join(read)


@artifact_processor
def get_line_calls(context):
    # One call_history per Android user survives the collapse of the storage views, and
    # every one is read, against the naver_line in the same folder.
    files_found = unique_files(context)
    data_list = []
    read = []
    for call_db, msg_db in _call_dbs(files_found):
        if not msg_db:
            logfunc('Line: no naver_line database beside a call_history database, '
                    'so its calls are not read')
            continue
        user = _android_user(call_db)
        db = open_sqlite_db_readonly(call_db)
        cursor = db.cursor()
        cursor.execute(attach_sqlite_db_readonly(msg_db, 'naver_line'))
        try:
            cursor.execute('''
                SELECT case Substr(calls.call_type, -1) when "O" then "Outgoing" when "I" then "Incoming" else Substr(calls.call_type, -1) end AS direction,
                       calls.start_time/1000 AS start_time, calls.end_time/1000 AS end_time,
                       case when Substr(calls.call_type, -1) = "O" then contact_book_w_groups.members else null end AS group_members,
                       calls.caller_mid,
                       case calls.voip_type when "V" then "Video" when "A" then "Audio" when "G" then calls.voip_gc_media_type else calls.voip_type end AS call_type
                FROM   call_history AS calls
                       LEFT JOIN (SELECT id, Group_concat(M.m_id) AS members
                                  FROM   membership AS M GROUP BY id
                                  UNION
                                  SELECT m_id, NULL FROM naver_line.contacts) AS contact_book_w_groups
                              ON calls.caller_mid = contact_book_w_groups.id
            ''')
            all_rows = cursor.fetchall()
        except Exception as e:
            logfunc(str(e))
            all_rows = []
        db.close()
        if all_rows:
            read.append(call_db)

        for row in all_rows:
            data_list.append((_sec_to_utc(row[1]), _sec_to_utc(row[2]), row[3], row[4], row[0], row[5], user))

    data_headers = (('Start Time', 'datetime'), ('End Time', 'datetime'), 'To ID', 'From ID', 'Direction', 'Call Type',
                    'Android User')
    return data_headers, data_list, '\n'.join(read)
