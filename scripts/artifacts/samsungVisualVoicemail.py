"""Samsung visual voicemail (com.samsung.vvm): messages, greetings and their audio.

The app keeps messages in databases/VmailProvider.db (Message, with the mailbox each sits
in under Mailbox and its audio described under Attachment), and the audio files in
databases/<account id>.db_att/<attachment id>.
"""

__artifacts_v2__ = {
    "get_samsung_visual_voicemail": {
        "name": "Samsung Visual Voicemail - Messages",
        "description": (
            "Parses the messages in Samsung visual voicemail's VmailProvider.db, from the "
            "Message table and from Message_Deletes where it holds rows, with the message "
            "time, the mailbox it is in, the stored from value (fromList), the stored "
            "duration, read flag and transcription, and the audio file stored for it."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Voicemail",
        "notes": (
            "Read from com.samsung.vvm/databases/VmailProvider.db with its -wal. Timestamp "
            "is the timeStamp column, read as milliseconds since the Unix epoch (on the "
            "known data that reading falls inside the logged setup window) and converted to "
            "UTC in whole seconds. Mailbox is the displayName of the Mailbox row the "
            "message's mailboxKey points to (Greetings, INBOX and Archived on the known "
            "data); when no Mailbox row matches, the mailboxKey number is shown. "
            "Audio is the file databases/<Attachment accountKey>.db_att/<Attachment _id> "
            "for the message's first Attachment row, matched on the two numbers in that "
            "path. The layout is the AOSP Email provider's "
            "(AttachmentUtilities.getAttachmentFilename, platform/packages/apps/Email "
            "commit 9822725da07cc150f2410ad5360549018c3fbb1c); on the known data every id "
            "is 1, so the data does not tell the account id from the attachment id. Rows "
            "from Message_Deletes get no audio lookup. Audio File Found is Yes when the "
            "Attachment row's file was in the extraction; No also covers a message with no "
            "Attachment row. Audio MIME Type and Audio Size (bytes) are Attachment.mimeType "
            "and size as stored; on the known data the stored size equals the file's size. "
            "From (as stored), Duration (as stored), Read (as stored) and Type (as stored) "
            "are fromList, duration, flagRead and type, not decoded. Transcription is the "
            "stored transcription text. Message Row ID is Message._id, not the messageId "
            "column. Android User is taken from the database's path. "
            "Known data (samsung_a166u_a16_known_20261117): the mailbox was set up from the "
            "phone between 14:24 and 14:27:04 UTC (logged), and a voicemail was then left "
            "from a second phone between about 14:27 and 14:31 (reported, not measured). "
            "The one row is in the Greetings mailbox at 14:26:04, inside the logged setup "
            "window, with an AMR audio file of 3,206 bytes (its header reads #!AMR). The "
            "mailbox name and the time are consistent with the greeting recorded at setup; "
            "no stored field links the row to the account's greeting. INBOX held no "
            "message, and no Message row was ever created for the voicemail left afterwards "
            "(the Message id sequence is 1). A received voicemail, a transcription, an "
            "archived or deleted message and the Message_Deletes table (empty on every "
            "image run) are not exercised. "
            "Tables left out: Account and HostAuth (account and server login fields), "
            "Contact, QuickResponse, CdgGroup and the *_Updates tables. "
            "samsung_a166u_a16_known_20261116 and cookbook_a11 hold the database with no "
            "message. No other image registered on 2026-11-17 lists it (member listings of "
            "83 keys)."
        ),
        "paths": (
            "*/com.samsung.vvm/databases/VmailProvider.db*",
            "*/com.samsung.vvm/databases/*.db_att/*",
        ),
        "output_types": "standard",
        "artifact_icon": "voicemail",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.samsung.vvm | 1 row (Greetings mailbox)",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.vvm | Message empty | 0 rows",
            "cookbook_a11": "Android 11 | com.samsung.vvm | Message empty | 0 rows",
        },
    }
}

import os
import re

from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    convert_unix_ts_to_utc,
    does_table_exist_in_db,
    get_sqlite_db_records,
    is_sqlite_sidecar,
)

PACKAGE = "com.samsung.vvm"
_USER_RE = re.compile(r"/(?:user|user_de|data_mirror/data_(?:ce|de)/[^/]+)/(\d+)/")


def _container(path):
    """(android user, storage area) of the vvm container a path sits in, or None."""
    norm = str(path).replace("\\", "/")
    idx = norm.find(f"/{PACKAGE}/databases/")
    if idx < 0:
        return None
    head = norm[:idx + 1]
    area = "de" if ("/user_de/" in head or "/data_mirror/data_de/" in head) else "ce"
    match = None
    for match in _USER_RE.finditer(head):
        pass
    if match and head.endswith(f"/{match.group(1)}/"):
        return int(match.group(1)), area
    if head.rstrip("/").rsplit("/", 1)[-1] == "data":
        # /data/data/<pkg>, and layouts such as userdata/data/<pkg> that keep user 0 there
        return 0, area
    return None


def _ms(value):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ""
    return convert_unix_ts_to_utc(value) if value > 0 else ""


def _columns(path, table):
    return {row[1] for row in get_sqlite_db_records(path, f"PRAGMA table_info({table})")}


def _attachment_files(files_found):
    """{(container, account id, attachment id): path} for files under <account>.db_att/."""
    index = {}
    for path in files_found:
        norm = str(path).replace("\\", "/")
        match = re.search(r"/databases/(\d+)\.db_att/(\d+)$", norm)
        if not match or not os.path.isfile(str(path)):
            continue
        container = _container(path)
        if container is not None:
            index[(container, int(match.group(1)), int(match.group(2)))] = str(path)
    return index


WANTED = ("timeStamp", "mailboxKey", "fromList", "duration", "flagRead", "transcription",
          "accountKey", "type", "_id")


@artifact_processor
def get_samsung_visual_voicemail(context):
    files_found = context.get_files_found()
    audio_files = _attachment_files(files_found)
    data_list = []
    source_paths = []
    seen = set()
    for path in files_found:
        path = str(path)
        if is_sqlite_sidecar(path) or not path.endswith("VmailProvider.db"):
            continue
        container = _container(path)
        if container is None:
            continue
        source_paths.append(path)
        mailboxes = {}
        if does_table_exist_in_db(path, "Mailbox"):
            for box_id, name in get_sqlite_db_records(path, "SELECT _id, displayName FROM Mailbox"):
                mailboxes[box_id] = name or ""
        attachments = {}
        if does_table_exist_in_db(path, "Attachment"):
            for att_id, message_key, mime, size, account in get_sqlite_db_records(
                    path, "SELECT _id, messageKey, mimeType, size, accountKey FROM Attachment"):
                attachments.setdefault(message_key, []).append((att_id, mime, size, account))
        for table in ("Message", "Message_Deletes"):
            if not does_table_exist_in_db(path, table):
                continue
            cols = _columns(path, table)
            select = ", ".join(c if c in cols else f"NULL AS {c}" for c in WANTED)
            for row in get_sqlite_db_records(path, f"SELECT {select} FROM {table} ORDER BY timeStamp"):
                stamp, box, sender, duration, read, transcript, account, kind, msg_id = row
                key = (container[0], table, msg_id, stamp)
                if key in seen:
                    continue
                seen.add(key)
                media_ref, mime, size, found = "", "", "", "No"
                for att_id, att_mime, att_size, att_account in attachments.get(msg_id, []) \
                        if table == "Message" else []:
                    mime, size = att_mime or "", att_size if att_size is not None else ""
                    audio = audio_files.get((container, att_account, att_id))
                    if audio:
                        media_ref = check_in_media(audio, f"voicemail {msg_id}") or ""
                        found = "Yes"
                        source_paths.append(audio)
                    break
                data_list.append((
                    _ms(stamp), mailboxes.get(box, "" if box is None else str(box)),
                    sender or "", "" if duration is None else duration,
                    "" if read is None else read, transcript or "", media_ref, found, mime,
                    size, table, "" if kind is None else kind, msg_id, container[0],
                ))

    data_headers = (
        ("Timestamp", "datetime"),
        "Mailbox",
        "From (as stored)",
        "Duration (as stored)",
        "Read (as stored)",
        "Transcription",
        ("Audio", "media"),
        "Audio File Found",
        "Audio MIME Type",
        ("Audio Size (bytes)", "number"),
        "Table",
        "Type (as stored)",
        "Message Row ID",
        "Android User",
    )
    return data_headers, data_list, "\n".join(sorted(set(source_paths)))
