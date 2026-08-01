# Tested App Version: 6.83, 8.0.3
__artifacts_v2__ = {
    "knuddels_chats": {
        "name": "Knuddels - Chat Messages",
        "description": "Extracts Knuddels chats (text, images/snaps and GIFs) from database files",
        "author": "@annkirpv",
        "creation_date": "2025-05-04",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Chats",
        "notes": ("From Me is derived from the database file name: the owner's nickname is taken to "
                  "be the part of the name that follows 'knuddels', URL-decoded, and a message is "
                  "marked 1 when its User Name matches that nickname and 0 when it does not. Where "
                  "the file name does not follow that convention the owner cannot be established "
                  "and the column is left blank for every row of that database rather than "
                  "reporting the messages as received.\n"
                  "In the conversation view only rows with From Me set to 1 are shown as sent by "
                  "the device owner; a blank value is not attributed to the owner.\n"
                  "Message Type is derived from markers found in the message text. A message that "
                  "carries the app's marker prefix but no marker this parser recognises is reported "
                  "as 'Unclassified' rather than as Text.\n"
                  "GIF URL(s) (reconstructed by parser) is constructed by this parser: the truncated "
                  "token found in the message text is joined to a base URL "
                  "(https://chat.knuddels.de/pics/) that is hardcoded here. No such URL is stored in "
                  "the message, the database or anywhere else in the data, and the result has not "
                  "been verified to resolve."),
        "paths": (
            "*/com.knuddels.android/databases/knuddels*",
            "*/media/*/Pictures/Knuddels/*",
        ),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Conversation Key",
                "conversationLabelColumn": "Participants",
                "textColumn": "Message",
                "directionColumn": "From Me",
                "directionSentValue": 1,
                "timeColumn": "Timestamp",
                "senderColumn": "User Name",
                "mediaColumn": "Media",
            }
        },
    },
    "knuddels_contacts": {
        "name": "Knuddels - Known Users",
        "description": "Extracts known Knuddels users (chat partners) from the users table",
        "author": "@annkirpv",
        "creation_date": "2026-06-30",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Contacts",
        "notes": ("Sex is decoded from the users.sex column as 1 = Male and 2 = Female. That mapping "
                  "is not documented in the data and was established through testing; any other "
                  "value is reported as stored."),
        "paths": ("*/com.knuddels.android/databases/knuddels*",),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "knuddels_account": {
        "name": "Knuddels - Account & App Usage",
        "description": "Extracts the local Knuddels account and app-usage info from shared_prefs XML",
        "author": "@annkirpv",
        "creation_date": "2026-06-30",
        "last_update_date": "2026-08-01",
        "requirements": "none",
        "category": "Accounts",
        "notes": ("passwordU (as stored) is the raw value of the shared_prefs key 'passwordU'. "
                  "passwordU (ROT13-decoded, unverified) is that same value passed through ROT13 by "
                  "this parser. Nothing in the data records what encoding, if any, was applied to "
                  "the stored value or that it is the account password, and the decoded column has "
                  "not been verified against a known password.\n"
                  "session_timestamp, sites_visited_weekly_time and origins_visited_date are "
                  "reported under their shared_prefs key names because what event each one records "
                  "is not established.\n"
                  "Active Account is Yes only where a User.xml carrying the same nickname was "
                  "collected alongside the database. Where no such file was collected the cell is "
                  "left blank, which does not establish that the account is inactive."),
        "paths": (
            "*/com.knuddels.android/shared_prefs/User.xml",
            "*/com.knuddels.android/shared_prefs/AwOrigin*VisitLoggerPrefs.*",
            "*/com.knuddels.android/shared_prefs/hyb*_prefs_reporting.xml",
            "*/com.knuddels.android/databases/knuddels*",
        ),
        "output_types": "standard",
        "artifact_icon": "user",
    },
}

import os
import re
import codecs
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.parse import unquote_plus

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, check_in_media
from scripts.context import Context
from scripts.filetype import guess_mime

SNAP_START = "\u00b0>{Snap}"
GIF_START = "\u00b0>"
GIF_END = "<\u00b0"
GIF_BASE_URL = "https://chat.knuddels.de/pics/"


def ms_to_utc(value):
    if value in (None, ""):
        return ""
    try:
        ms = int(str(value).strip())
    except (TypeError, ValueError):
        return ""
    if ms <= 0:
        return ""
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def rot13(text):
    if not text:
        return ""
    try:
        return codecs.decode(text, "rot_13")
    except (TypeError, UnicodeError):
        return text


def parse_shared_prefs_xml(path):
    result = {}
    if not path:
        return result
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        return result
    for elem in root:
        name = elem.get("name")
        if not name:
            continue
        if elem.tag == "string":
            result[name] = elem.text or ""
        elif elem.tag in ("int", "long", "float", "boolean"):
            result[name] = elem.get("value", "")
        elif elem.tag == "set":
            result[name] = [child.text or "" for child in elem]
    return result


def classify_message(message):
    if not message:
        return "Text"
    if SNAP_START in message:
        return "Image (Snap)"
    if GIF_START in message and GIF_END in message:
        return "GIF"
    if GIF_START in message:
        # Carries the app's in-message marker prefix but no marker recognised here.
        # Reporting it as plain text would assert a classification not established.
        return "Unclassified"
    return "Text"


def reconstruct_gif_urls(message):
    urls = []
    for segment in re.findall(r"(sm_abo[^<]*?)(?=<>|<\u00b0)", message):
        m = re.match(r"(sm_abo[^.]*)\.\.\.(.*)", segment)
        if not m:
            continue
        prefix, tail = m.group(1), m.group(2)
        if "." not in tail:
            continue
        ext = re.sub(r"[^A-Za-z0-9].*$", "", tail.rsplit(".", 1)[1])
        if ext:
            urls.append(f"{GIF_BASE_URL}{prefix}.{ext}")
    seen, out = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


@artifact_processor
def knuddels_chats(context):
    files_found = context.get_files_found()
    data_list = []

    db_files, image_files = [], []
    for file_found in files_found:
        file_found = str(file_found)
        norm = file_found.replace("\\", "/").lower()
        if "/pictures/knuddels/" in norm:
            image_files.append(file_found)
        elif guess_mime(file_found) == 'application/x-sqlite3':
            db_files.append(file_found)

    media_index = {}
    for img_path in image_files:
        bare_id = os.path.basename(img_path).split(".", 1)[0]
        media_index.setdefault(bare_id, []).append(img_path)

    for file_found in db_files:
        # The owner's nickname is only recoverable from the file name. When the name does
        # not follow the 'knuddels<nickname>' convention, or carries no nickname at all,
        # the owner is unknown and From Me is left blank instead of reading as received.
        db_basename = os.path.basename(file_found.replace("\\", "/"))
        owner_nick = None
        if db_basename.lower().startswith("knuddels"):
            owner_nick = unquote_plus(db_basename[len("knuddels"):]) or None

        query = '''
        SELECT
        datetime(thread.timestamp / 1000, "unixepoch"),
        users.nickname,
        thread.message,
        thread.cid,
        thread.sender,
        users.id,
        thread.id,
        CASE
            WHEN thread.snapExpired = 1 THEN 'Yes'
            WHEN thread.snapExpired = 0 THEN 'No'
        END, -- 1 = expired, 0 = not expired
        conversations.participants
        FROM thread
        JOIN users ON users.id = thread.sender
        LEFT JOIN conversations ON conversations.id = thread.cid
        '''
        db_records = get_sqlite_db_records(file_found, query)

        for row in db_records:
            (timestamp, nickname, message, cid, sender, user_id, message_id,
             snap_expired, participants) = row
            msg_type = classify_message(message)

            media_cell = ""
            if msg_type == "Image (Snap)":
                refs = []
                for img_path in media_index.get(str(message_id), []):
                    ref = check_in_media(img_path, name=f"knuddels_{message_id}")
                    if ref:
                        refs.append(ref)
                if refs:
                    media_cell = refs if len(refs) > 1 else refs[0]

            gif_cell = ""
            if msg_type == "GIF":
                gif_cell = " | ".join(reconstruct_gif_urls(message))

            db_name = file_found.split("databases")[1].split("knuddels")[1]
            conversation_key = "chat_" + str(cid) + "_" + db_name
            from_me = '' if owner_nick is None else (1 if nickname == owner_nick else 0)

            data_list.append((
                timestamp, nickname, message, msg_type, media_cell, gif_cell,
                snap_expired, participants,
                conversation_key, from_me, Context.get_relative_path(file_found), message_id, sender, user_id,
            ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'User Name',
        'Message',
        'Message Type',
        ('Media', 'media'),
        'GIF URL(s) (reconstructed by parser)',
        'Snap Expired',
        'Participants',
        'Conversation Key',
        'From Me',  # 1 = sent by owner, 0 = received, blank = owner not established
        'Source File',
        'Message ID',
        'Thread Table UID',
        'Users Table UID',
    )

    db_count = len(db_files)
    source_note = f"{db_count} Knuddels database{'s' if db_count != 1 else ''} - see Source File column"
    return data_headers, data_list, source_note


@artifact_processor
def knuddels_contacts(context):
    files_found = context.get_files_found()
    data_list = []
    db_count = 0

    for file_found in files_found:
        file_found = str(file_found)
        if guess_mime(file_found) != 'application/x-sqlite3':
            continue
        db_count += 1

        query = '''
        SELECT
        nickname,
        uid,
        id,
        age,
        -- 1 = male, 2 = female, established through testing; any other value reported as stored
        CASE WHEN sex = 1 THEN 'Male' WHEN sex = 2 THEN 'Female' ELSE sex END,
        img_version,
        friedlisttype,
        onlinestatus,
        lastactivetime,
        CASE
            WHEN profileimagehidden = 1 THEN 'Yes'
            WHEN profileimagehidden = 0 THEN 'No'
        END, -- 1 = hidden, 0 = visible
        distance
        FROM users
        '''
        db_records = get_sqlite_db_records(file_found, query)

        for row in db_records:
            (nickname, uid, internal_id, age, sex, img_version, friendlist_type,
             onlinestatus, lastactivetime, profileimagehidden, distance) = row
            data_list.append((
                nickname,
                uid,
                internal_id,
                age,
                sex,
                img_version,
                friendlist_type,
                onlinestatus,
                ms_to_utc(lastactivetime),
                profileimagehidden,
                distance,
                Context.get_relative_path(file_found),
            ))

    data_headers = (
        'Nickname',
        'User ID (uid)',
        'Internal ID',
        'Age',
        'Sex',
        'Profile Image Version',
        'Friendlist Type',
        'Online Status',
        ('Last Active Time', 'datetime'),
        'Profile Image Hidden',
        'Distance',
        'Source File',
    )
    source_note = f"{db_count} Knuddels database{'s' if db_count != 1 else ''} - see Source File column"
    return data_headers, data_list, source_note


@artifact_processor
def knuddels_account(context):
    files_found = context.get_files_found()
    prefs_by_instance = {}
    db_files = []
    for f in files_found:
        f = str(f)
        norm = f.replace("\\", "/")
        if "/shared_prefs/" in norm.lower():
            instance = norm.split("/shared_prefs/")[0]
            prefs_by_instance.setdefault(instance, {})[os.path.basename(norm).lower()] = f
        elif guess_mime(f) == 'application/x-sqlite3':
            db_files.append(f)

    active = {}
    for instance, files in prefs_by_instance.items():
        user = parse_shared_prefs_xml(files.get("user.xml", ""))
        aworigin = next((p for n, p in files.items() if n.startswith("aworigin")), "")
        hybrid = next((p for n, p in files.items()
                       if n.startswith("hybrid_prefs_reporting")
                       or n.startswith("hybid_prefs_reporting")), "")
        origin = parse_shared_prefs_xml(aworigin)
        report = parse_shared_prefs_xml(hybrid)

        alias = user.get("aliasNicks", "")
        if isinstance(alias, list):
            alias = ", ".join(alias)

        active[instance] = {
            "nickname": user.get("nickname", ""),
            "alias": alias,
            "age": user.get("age", ""),
            "gender": {"1": "Male", "2": "Female"}.get(str(user.get("gender", "")), user.get("gender", "")),
            "uuid": user.get("uuid", ""),
            "autologin": user.get("autologin", ""),
            "isloggedin": user.get("isLoggedIn", ""),
            "pw": user.get("passwordU", ""),
            "pw_dec": rot13(user.get("passwordU", "")),
            "first_install": ms_to_utc(report.get("app_first_installed", "")),
            "last_usage": ms_to_utc(report.get("session_timestamp", "")),
            "first_login_week": ms_to_utc(origin.get("sites_visited_weekly_time", "")),
            "last_login_date": origin.get("origins_visited_date", ""),
            "sources": [p for p in (files.get("user.xml", ""), aworigin, hybrid) if p],
        }

    def active_row(nickname, info, last_msg, extra_sources):
        sources = " | ".join(Context.get_relative_path(s) for s in extra_sources + info.get("sources", []))
        return (
            nickname, "Yes", info["alias"], info["age"], info["gender"], info["uuid"],
            info["autologin"], info["isloggedin"], info["pw"], info["pw_dec"],
            info["first_install"], info["last_usage"], info["first_login_week"],
            info["last_login_date"], last_msg, sources,
        )

    data_list = []
    matched_instances = set()
    for db in db_files:
        norm = db.replace("\\", "/")
        instance = norm.split("/databases/")[0]
        nickname = os.path.basename(norm)
        if nickname.lower().startswith("knuddels"):
            nickname = nickname[len("knuddels"):]
        nickname = unquote_plus(nickname)

        last_msg = ""
        try:
            rows = list(get_sqlite_db_records(db, "SELECT max(timestamp) FROM thread"))
            if rows and rows[0] and rows[0][0]:
                last_msg = ms_to_utc(rows[0][0])
        except sqlite3.Error:
            pass

        info = active.get(instance)
        if info and info.get("nickname", "") == nickname:
            data_list.append(active_row(nickname, info, last_msg, [db]))
            matched_instances.add(instance)
        else:
            # No User.xml carrying this nickname was collected, so whether the account is
            # active cannot be established; the cell is left blank rather than reading 'No'.
            data_list.append((
                nickname, "", "", "", "", "", "", "", "", "",
                "", "", "", "", last_msg, Context.get_relative_path(db),
            ))

    for instance, info in active.items():
        if instance not in matched_instances and info.get("nickname", ""):
            data_list.append(active_row(info["nickname"], info, "", []))

    data_headers = (
        'Nickname',
        'Active Account',
        'Alias Nicks',
        'Age',
        'Gender',
        'UUID',
        'Auto Login',
        'Is Logged In',
        'passwordU (as stored)',
        'passwordU (ROT13-decoded, unverified)',
        ('First Installed', 'datetime'),
        ('session_timestamp', 'datetime'),
        ('sites_visited_weekly_time', 'datetime'),
        'origins_visited_date',
        ('Last Message', 'datetime'),
        'Source File',
    )
    db_count = len(db_files)
    source_note = f"{db_count} Knuddels database{'s' if db_count != 1 else ''} - see Source File column"
    return data_headers, data_list, source_note
