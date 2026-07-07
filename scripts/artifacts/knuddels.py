# Tested App Version: 6.83, 8.0.3
__artifacts_v2__ = {
    "knuddels_chats": {
        "name": "Knuddels - Chat Messages",
        "description": "Extracts Knuddels chats (text, images/snaps and GIFs) from database files",
        "author": "@annkirpv",
        "creation_date": "2025-05-04",
        "last_update_date": "2026-07-03",
        "requirements": "none",
        "category": "Chats",
        "notes": "",
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
        "last_update_date": "2026-07-03",
        "requirements": "none",
        "category": "Contacts",
        "notes": "",
        "paths": ("*/com.knuddels.android/databases/knuddels*",),
        "output_types": "standard",
        "artifact_icon": "users",
    },
    "knuddels_account": {
        "name": "Knuddels - Account & App Usage",
        "description": "Extracts the local Knuddels account and app-usage info from shared_prefs XML",
        "author": "@annkirpv",
        "creation_date": "2026-06-30",
        "last_update_date": "2026-07-03",
        "requirements": "none",
        "category": "Accounts",
        "notes": "",
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
        owner_nick = os.path.basename(file_found.replace("\\", "/"))
        if owner_nick.lower().startswith("knuddels"):
            owner_nick = owner_nick[len("knuddels"):]
        owner_nick = unquote_plus(owner_nick)

        query = '''
        SELECT
        datetime(thread.timestamp / 1000, "unixepoch"),
        users.nickname,
        thread.message,
        thread.cid,
        thread.sender,
        users.id,
        thread.id,
        CASE WHEN thread.snapExpired = 1 THEN 'Yes' WHEN thread.snapExpired = 0 THEN 'No' END, -- 1 = expired, 0 = not expired
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
            from_me = 1 if nickname == owner_nick else 0

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
        'GIF URL(s)',
        'Snap Expired',
        'Participants',
        'Conversation Key',
        'From Me',  # 1 = sent by owner, 0 = received
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
        CASE WHEN sex = 1 THEN 'Male' WHEN sex = 2 THEN 'Female' END, -- 1 = male, 2 = female
        img_version,
        friedlisttype,
        onlinestatus,
        lastactivetime,
        CASE WHEN profileimagehidden = 1 THEN 'Yes' WHEN profileimagehidden = 0 THEN 'No' END, -- 1 = hidden, 0 = visible
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
            rows = get_sqlite_db_records(db, "SELECT max(timestamp) FROM thread")
            if rows and rows[0] and rows[0][0]:
                last_msg = ms_to_utc(rows[0][0])
        except sqlite3.Error:
            pass

        info = active.get(instance)
        if info and info.get("nickname", "") == nickname:
            data_list.append(active_row(nickname, info, last_msg, [db]))
            matched_instances.add(instance)
        else:
            data_list.append((
                nickname, "No", "", "", "", "", "", "", "", "",
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
        'Password (C13/ROT13 stored)',
        'Password (decoded)',
        ('First Installed', 'datetime'),
        ('Last App Usage', 'datetime'),
        ('First Login This Week', 'datetime'),
        'Last Login Date',
        ('Last Message', 'datetime'),
        'Source File',
    )
    db_count = len(db_files)
    source_note = f"{db_count} Knuddels database{'s' if db_count != 1 else ''} - see Source File column"
    return data_headers, data_list, source_note