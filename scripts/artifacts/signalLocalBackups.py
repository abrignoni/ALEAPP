"""Signal (org.thoughtcrime.securesms): on-device backup snapshots in a SignalBackups folder."""

__artifacts_v2__ = {
    "signalLocalBackups": {
        "name": "Signal - On-Device Backups",
        "description": "Snapshots of Signal's on-device backup, with the time in each snapshot's folder name, "
                       "whether the folder still has its temporary name, the size of the encrypted main file "
                       "and the number of media files the snapshot lists. The messages and media are "
                       "encrypted; the Signal - On-Device Backup artifacts read them when the recovery key is given. "
                       "The metadata version and the media list are read without it.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-20",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Messaging",
        "notes": (
            "Layout from Signal-Android tag v8.35.4 (commit b330f4efcf49a0cec87807d18504f07f5df12bf2); "
            "other versions were not checked. File names below are under "
            "app/src/main/java/org/thoughtcrime/securesms/ unless a path is given. The app writes the "
            "backup into a folder it is given as a tree URI (backup/v2/local/ArchiveFileSystem.kt "
            "L65-66; on the test phone a folder chosen in the backup setup), inside a folder it creates "
            "named SignalBackups (L54, L234). Its own comment says that folder may be renamed or "
            "restored under another name (L113-118), so the folder name is not required here: any folder "
            "named signal-backup- and a time formatted yyyy-MM-dd-HH-mm-ss in UTC (createSnapshot, "
            "L274-276), holding the members main, metadata or files (L384-386), is read as one snapshot. "
            "A signal-backup- folder whose name does not carry that time is skipped and named in the run "
            "log, as is one whose digits are not a real date. The time is taken from the phone's clock "
            "when the snapshot folder is created, before its members are written (L275, L283-284): it is "
            "when the backup started, not when it finished. The snapshot is written under the same name "
            "ending in -tmp (L283) and renamed when the backup has been written (finalize, L428-430, "
            "called at jobs/LocalArchiveJob.kt L120). When the job ends, whether or not the backup "
            "finished, it deletes that snapshot's -tmp folder if one is still there (LocalArchiveJob.kt "
            "L133-138), and it deletes any -tmp folder left over before its next backup (L88; "
            "deleteOldTemporaryBackups, ArchiveFileSystem.kt L245-257). After a backup that did not fail "
            "it deletes all but the two snapshots with the newest names (LocalArchiveJob.kt L141; "
            "deleteOldBackups, ArchiveFileSystem.kt L263-268, limit 2). The retention and the -tmp "
            "handling are source-verified only. The one backup folder tested held one snapshot and no "
            "-tmp folder.\n"
            "Snapshot Time is the time in the folder name, read as UTC as the app writes it. Temporary "
            "Name is Yes for a folder whose name ends in -tmp, one the app had neither renamed nor "
            "deleted. Backup Time is backupTimeMs from the backup itself and Recovery Key Result says "
            "whether a key was given and whether it opened the snapshot, shown as Not given, Opened, Did "
            "not open or Not readable; the key is never reported. Not readable means main or metadata is "
            "missing, or the snapshot did not decode. Did not open means the HMAC over main did not "
            "verify, which a wrong key or a changed main file both cause. On the tested backup the "
            "column held Opened with the key, Not given without one and Did not open with a wrong key, "
            "and Backup Time was 1 second after Snapshot Time. Not readable was not run. Main Size is "
            "the size of the main file in bytes. main is written through an encrypting writer with the "
            "account's message backup key (backup/v2/BackupRepository.kt L695-702, called at "
            "backup/v2/local/LocalArchiver.kt L85). The app derives that key from the Account Entropy "
            "Pool, a 64-character value (LENGTH = 64, "
            "core/util-jvm/src/main/java/org/signal/core/models/AccountEntropyPool.kt L21; "
            "deriveMessageBackupKey, L102-103) that the app's backup screen showed as the recovery key "
            "on the test phone. Without that key its messages are not read. Metadata Version (as stored) "
            "is field 1 of the metadata file, a Metadata protobuf message "
            "(lib/archive/src/main/protowire/LocalArchive.proto L8-18, same commit); its field 2 is the "
            "encrypted backup ID and is not reported. A metadata file that does not decode as that "
            "message, or has no field 1, leaves the column empty and is named in the run log (the empty "
            "column was tested on constructed files; the log line was not checked). Media Listed is the "
            "number of media names in the snapshot's files member, which the app writes as "
            "length-prefixed FilesFrame messages, each holding one media name (LocalArchive.proto "
            "L20-24; written at backup/v2/local/LocalArchiver.kt L126-129, read by "
            "lib/archive/src/main/java/org/signal/archive/local/ArchivedFilesReader.kt L36-41). A files "
            "member that does not decode to its last byte leaves the column empty and is named in the "
            "run log (the reader is tested on constructed bytes; the artifact's empty column and log "
            "line for this case were not run). A snapshot folder missing a member still gets a row, with "
            "that member's column empty (not run). With a key given, a snapshot missing main or metadata "
            "shows Not readable. The media themselves are kept, encrypted, in a files folder beside the "
            "snapshots (ArchiveFileSystem.kt L236; backup/v2/local/LocalArchiver.kt L108), shared by all "
            "snapshots, and are not read by this artifact. Signal - On-Device Backup Attachments reads "
            "them. After a backup that did not fail the job deletes the media files no current snapshot "
            "lists (LocalArchiveJob.kt L144; ArchiveFileSystem.kt L324-341), so Media Listed is the "
            "snapshot's own list, not a count of the files on disk.\n"
            "Backup Location is the path from the shared storage root to the folder holding the "
            "snapshot, or the whole path inside the extraction where no storage root is recognised. "
            "Android User is the number that follows the shared storage root in the path "
            "(data/media/<N>, userdata/media/<N>, storage/emulated/<N>, mnt/user/<U>/emulated/<N>, "
            "mnt/pass_through/<U>/emulated/<N>). It is empty for a path that starts with sdcard/, as in "
            "a pull of /sdcard, which names no user, and for a folder outside those roots, such as on a "
            "removable card. The same snapshot seen under several spellings that name the same Android "
            "user is one row; a copy under sdcard/ names no user and is a separate row.\n"
            "Known data (samsung_a166u_signal_backup_pull_known_20261120: an adb pull of the backup "
            "folder from shared storage on the Samsung SM-A166U test phone, Signal 8.35.4, kept under "
            "sdcard/ and not a full extraction): on-device backups were turned on on 2026-11-20 with a "
            "new folder in shared storage. The session record gives the setup window and names one "
            "snapshot folder. The run gave one row with the time in that folder name in Snapshot Time, "
            "Temporary Name No, Main Size 65,600, Metadata Version 1, Media Listed 7 and Backup Location "
            "holding the two folder names below sdcard/; the 7 listed names equal the 7 file names in "
            "its files folder. Temporary Name held No, Metadata Version held 1 and Android User held an "
            "empty value on every row of that run. No full extraction holding a backup was available, so "
            "the seeker is proven on the pull only. Tested only on constructed files: -tmp folders, "
            "several snapshots, a renamed backup folder, one snapshot seen under two spellings, every "
            "storage root spelling above, a folder outside a storage root, a name whose digits are not a "
            "real date, a metadata member that does not decode, and the files reader on bytes that do "
            "not decode."
        ),
        "paths": ("*/signal-backup-*/main", "*/signal-backup-*/metadata", "*/signal-backup-*/files"),
        "output_types": "standard",
        "artifact_icon": "archive",
        "sample_data": {
            "samsung_a166u_signal_backup_pull_known_20261120": "Android 16 | Signal 8.35.4, adb pull of the backup folder | 1 row",
        },
    },
    "signalBackupMessages": {
        "name": "Signal - On-Device Backup Messages",
        "description": "Chat items decrypted from Signal's on-device backup with the account's recovery key: "
                       "times, conversation, direction, sender, text, attachments, delivery status, reactions, "
                       "quotes and edits. Gives no rows without the key.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-20",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Messaging",
        "notes": (
            "Needs the recovery key (--signal_recovery_key_file, --signal_recovery_key_env or the "
            "window's Signal backup recovery key button). See Signal - On-Device Backups for the layout "
            "and sources. Each snapshot is read and its rows are kept apart by Snapshot Time, so the "
            "same message in two snapshots is two rows. A snapshot is the state Signal exported when the "
            "backup ran: it says nothing about messages removed before then. The HMAC over the main file "
            "is checked before any of main is decrypted. When it does not verify, the snapshot gives no "
            "rows and the run log names the snapshot. The key is in no row; the run log records "
            "it at the start of the run. Fields are read from "
            "ChatItem in Backup.proto at Signal-Android commit b330f4efcf49a0cec87807d18504f07f5df12bf2.\n"
            "Times are read as milliseconds since 1970 UTC and shown in whole seconds. On the tested "
            "backup that reading put Backup Time 1 second after the folder-name time and the Note to "
            "Self item within 2 seconds of its logged time. Date Received and Date Server Sent fell 0 to "
            "1 second after Date Sent on the 67 incoming rows. Date Received on an outgoing row is "
            "OutgoingMessageDetails.dateReceived, and it equalled Date Sent on all 68 outgoing rows. "
            "Date Server Sent is filled on incoming rows only. The times in Send Status were not "
            "compared with anything.\n"
            "Sender is the label of the item's author: for a contact the system name, then system "
            "nickname, profile name, username, number, then Recipient and its ID. The account's own "
            "entry is shown as Self, which is the Sender of outgoing rows. Send Status has one line per "
            "recipient: label, state, time; an unset state is shown as pending, as Backup.proto says "
            "(L576-577). Each earlier version of an edited message is its own row, with Revision showing its "
            "place. Whether an earlier version carries its own chat and author ids in a real backup was "
            "not run; if it does not, its Conversation is blank. Text in square brackets is written by "
            "this parser for an item with no text of its own. For simple chat updates and one-to-one "
            "calls it is the enum name from Backup.proto. For contact cards, stickers without an emoji, "
            "viewed view-once items and deleted items it is this parser's own label. Payment, gift "
            "badge, group change and the other update kinds get a Kind and no text. Contact card "
            "contents, poll votes and call times are not reported. When a long text file is missing or "
            "does not verify, Message keeps the short body; the Long text row of Signal - On-Device "
            "Backup Attachments gives its status. Chat Key is the Android user, the snapshot time and "
            "the backup's chat id joined, so chats from different snapshots stay apart. Its last part is "
            "the Chat ID of Signal - On-Device Backup Chats. Sticker packs, ad hoc calls, notification "
            "profiles, chat folders and the favourite sticker list are counted in the run log and not "
            "reported.\n"
            "Known data (samsung_a166u_signal_backup_pull_known_20261120, Signal 8.35.4): 135 chat "
            "items, all standard messages, 68 outgoing and 67 incoming, in two chats. The one Note to "
            "Self item had the session record's text. Its Date Sent is 2 seconds before the logged time "
            "at the whole seconds the report shows (1.7 seconds by the stored milliseconds). The "
            "record's time is to the second. The other 134 items were not compared with a log. "
            "Source-verified only, with no item in the tested backup: every kind other than a standard "
            "message, reactions, quotes, link previews, long text, revisions and groups. On that backup "
            "these held no value on any row: Quoted Message Sent, Expire Start, Reactions, Quoted "
            "Author, Quoted Text, Link Preview, Expires In (ms), Revision and Android User (a pull of "
            "/sdcard names no user). Snapshot Time and Kind held one value on every row. Read and Sealed "
            "Sender are identical on that backup: Yes on all 67 incoming rows and blank on outgoing "
            "rows, where they do not apply."
        ),
        "paths": ("*/signal-backup-*/main", "*/signal-backup-*/metadata", "*/signal-backup-*/files"),
        "output_types": "standard",
        "artifact_icon": "message-square",
        "sample_data": {
            "samsung_a166u_signal_backup_pull_known_20261120": "Android 16 | Signal 8.35.4, with the recovery key | 135 rows",
        },
        "data_views": {
            "conversation": {
                "conversationDiscriminatorColumn": "Chat Key",
                "conversationLabelColumn": "Conversation",
                "textColumn": "Message",
                "directionColumn": "Direction",
                "directionSentValue": "Outgoing",
                "timeColumn": "Date Sent",
                "senderColumn": "Sender",
                "mediaColumn": "Attachments",
            }
        },
    },
    "signalBackupAttachments": {
        "name": "Signal - On-Device Backup Attachments",
        "description": "Attachments named by the chat items of Signal's on-device backup, decrypted with the "
                       "recovery key and checked against the hash the backup records, and the listed media "
                       "files no chat item points to. Gives no rows without the key.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-20",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Messaging",
        "notes": (
            "Needs the recovery key. An attachment's file in the backup's files folder is named from the "
            "SHA-256 of its plaintext hash and its local key "
            "(core/util-jvm/src/main/java/org/signal/core/models/backup/MediaName.kt L21, Signal-Android "
            "commit b330f4efcf49a0cec87807d18504f07f5df12bf2); Media Name is that file name. It is shown "
            "only when the HMAC at the end of the file verifies under the local key and the SHA-256 of "
            "the decrypted bytes equals the pointer's plaintextHash "
            "(lib/libsignal-service/src/main/java/org/whispersystems/signalservice/api/crypto/AttachmentCipherOutputStream.kt "
            "L33-48, same commit). File Name is the name the pointer carries. Status No local key or "
            "plaintext hash, File missing and Did not verify say why a pointer is not shown. "
            "Backup.proto says a missing local key means the attachment was not on the phone when the "
            "backup was made (L849-854). These three values were not seen on the tested backup; Did not "
            "verify was tested on a constructed file.\n"
            "Status Listed, no pointer read is a name in the snapshot's files list that none of the "
            "pointers read here names. Read here are message attachments, long text, link preview "
            "images, stickers, view-once media and story reply long text. Quote thumbnails, contact card "
            "avatars and chat wallpapers are not read. The app lists every attachment that has a file, a "
            "plaintext hash and a local backup key "
            "(app/src/main/java/org/thoughtcrime/securesms/database/AttachmentTable.kt L620-638; "
            "LocalArchiver.kt L85-91). No pointer read here carries the key to such a file, so it is not "
            "decrypted and what it holds is not established. On the tested backup a walk of every frame "
            "with the full schema found only the 2 pointers reported.\n"
            "Known data (samsung_a166u_signal_backup_pull_known_20261120): 2 image attachments verified "
            "and 5 listed names with no pointer read. Date Sent is blank on those 5 rows, since no chat "
            "item gives them a time. On that backup File Name, Caption and Android User held no value on any row, "
            "and Snapshot Time held one value on every row."
        ),
        "paths": ("*/signal-backup-*/main", "*/signal-backup-*/metadata", "*/signal-backup-*/files"),
        "output_types": "standard",
        "artifact_icon": "paperclip",
        "sample_data": {
            "samsung_a166u_signal_backup_pull_known_20261120": "Android 16 | Signal 8.35.4, with the recovery key | 7 rows",
        },
    },
    "signalBackupRecipients": {
        "name": "Signal - On-Device Backup Recipients",
        "description": "Contacts, groups, lists and the account's own entry from Signal's on-device backup, "
                       "decrypted with the recovery key. Gives no rows without the key.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-20",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Messaging",
        "notes": (
            "Needs the recovery key. One row per Recipient frame per snapshot, from Backup.proto at "
            "Signal-Android commit b330f4efcf49a0cec87807d18504f07f5df12bf2. Backup.proto calls "
            "Recipient ID a generated id for reference only within this file (L210), so it should not be "
            "matched across snapshots. Visibility (as stored) is 0 visible, 1 hidden, 2 hidden message "
            "request (Contact.Visibility). A contact's presence here does not establish that the account "
            "exchanged messages with it. Known data (samsung_a166u_signal_backup_pull_known_20261120): 7 "
            "recipients: 4 contacts, 1 self, 1 release notes, 1 distribution list. No group was in the "
            "tested backup. On it Blocked At, Username, Nickname, Note, Group Members and Android User "
            "held no value on any row, and Snapshot Time held one value on every row. Blocked held No on "
            "the 4 contact rows and is blank on kinds that have no blocked field."
        ),
        "paths": ("*/signal-backup-*/main", "*/signal-backup-*/metadata", "*/signal-backup-*/files"),
        "output_types": "standard",
        "artifact_icon": "users",
        "sample_data": {
            "samsung_a166u_signal_backup_pull_known_20261120": "Android 16 | Signal 8.35.4, with the recovery key | 7 rows",
        },
    },
    "signalBackupChats": {
        "name": "Signal - On-Device Backup Chats",
        "description": "Chats in Signal's on-device backup, with their disappearing message timer, archive, pin "
                       "and mute state and the number of items and date range of each. Gives no rows without "
                       "the key.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-20",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Messaging",
        "notes": (
            "Needs the recovery key. One row per Chat frame per snapshot, from Backup.proto at Signal-Android "
            "commit b330f4efcf49a0cec87807d18504f07f5df12bf2. Items, First Item and Last Item are counted here "
            "from the chat items of that snapshot by their sent time. Mute Until shows Muted with no end for "
            "the value Backup.proto defines as always muted. Known data "
            "(samsung_a166u_signal_backup_pull_known_20261120): 2 chats holding 134 and 1 items. On it Disappearing "
            "Timer (ms), Pinned Order, Mute Until and Android User held no value on any row."
        ),
        "paths": ("*/signal-backup-*/main", "*/signal-backup-*/metadata", "*/signal-backup-*/files"),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "samsung_a166u_signal_backup_pull_known_20261120": "Android 16 | Signal 8.35.4, with the recovery key | 2 rows",
        },
    },
    "signalBackupAccount": {
        "name": "Signal - On-Device Backup Account",
        "description": "The account record in Signal's on-device backup: username, profile name, bio and the "
                       "PIN as stored. Gives no rows without the key.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-20",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Messaging",
        "notes": (
            "Needs the recovery key. One row per snapshot from AccountData in Backup.proto at Signal-Android "
            "commit b330f4efcf49a0cec87807d18504f07f5df12bf2. PIN (as stored) is the svrPin field. Backup Time "
            "is backupTimeMs from the backup's BackupInfo. The account's phone number is not a field of "
            "AccountData. The profile key, username link, subscriber data and settings are not reported. "
            "Known data (samsung_a166u_signal_backup_pull_known_20261120): 1 row, on which Username, Family Name, "
            "Bio, Current App Version, First App Version and Android User held no value."
        ),
        "paths": ("*/signal-backup-*/main", "*/signal-backup-*/metadata", "*/signal-backup-*/files"),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "samsung_a166u_signal_backup_pull_known_20261120": "Android 16 | Signal 8.35.4, with the recovery key | 1 row",
        },
    },
}

import collections
import datetime
import os
import re
import uuid

from scripts import signal_backup as sb
from scripts.ilapfuncs import artifact_processor, check_in_embedded_media, logfunc

# The roots a shared storage path can be seen under, with the Android user they name.
_STORAGE_ROOTS = (
    re.compile(r'(?:^|/)(?:user)?data/media/(\d+)/'),
    re.compile(r'(?:^|/)mnt/pass_through/\d+/emulated/(\d+)/'),
    re.compile(r'(?:^|/)mnt/user/\d+/emulated/(\d+)/'),
    re.compile(r'(?:^|/)storage/emulated/(\d+)/'),
    # a pull of /sdcard, at the start of the path, names no user
    re.compile(r'^sdcard/()'),
)
_SNAPSHOT = re.compile(
    r'(?:^|/)signal-backup-(\d{4})-(\d{2})-(\d{2})-(\d{2})-(\d{2})-(\d{2})(-tmp)?/(main|metadata|files)$')
_ANY_SNAPSHOT = re.compile(r'(?:^|/)signal-backup-[^/]*/(main|metadata|files)$')


def _varint(data, pos):
    """(value, next position) of a protobuf varint, or (None, pos) when it is not one."""
    value = shift = 0
    index = pos
    while index < len(data) and shift < 64:
        byte = data[index]
        index += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, index
        shift += 7
    return None, pos


def _fields(data):
    """[(field number, wire type, value)] of a protobuf message, or None when it does not decode
    to its last byte. Only the wire types the Signal local backup messages use are accepted:
    varint (0) and length-delimited (2)."""
    out = []
    pos = 0
    while pos < len(data):
        tag, nxt = _varint(data, pos)
        if tag is None or tag >> 3 == 0:
            return None
        pos = nxt
        wire = tag & 7
        if wire == 0:
            value, nxt = _varint(data, pos)
            if value is None:
                return None
        elif wire == 2:
            size, nxt = _varint(data, pos)
            if size is None or nxt + size > len(data):
                return None
            value = data[nxt:nxt + size]
            nxt += size
        else:
            return None
        out.append((tag >> 3, wire, value))
        pos = nxt
    return out


def metadata_version(data):
    """Field 1 (version) of a LocalArchive.proto Metadata message, or None when the bytes do not
    decode as one: field 1 a varint and field 2, when present, a message."""
    fields = _fields(data)
    if not fields:
        return None
    version = None
    for number, wire, value in fields:
        if number == 1:
            if wire != 0:
                return None
            version = value
        elif number == 2:
            if wire != 2 or _fields(value) is None:
                return None
    return version


def media_names(data):
    """The media names of a snapshot's files member (length-prefixed FilesFrame messages), or
    None when it does not decode to its last byte."""
    names = []
    pos = 0
    while pos < len(data):
        size, nxt = _varint(data, pos)
        if size is None or nxt + size > len(data):
            return None
        fields = _fields(data[nxt:nxt + size])
        if fields is None:
            return None
        for number, wire, value in fields:
            if number == 1 and wire == 2:
                try:
                    names.append(value.decode('utf-8'))
                except UnicodeDecodeError:
                    return None
        pos = nxt + size
    return names


def _location(relative):
    """(Android user, path from the storage root to the folder holding the snapshot) of an
    evidence-relative member path."""
    head = relative.rsplit('/', 2)[0]
    for pattern in _STORAGE_ROOTS:
        match = None
        for match in pattern.finditer(head):
            pass
        if match:
            return match.group(1), head[match.end():]
    return '', head.lstrip('/')


def _find_snapshots(context):
    """The snapshots among the files found, oldest name first."""
    snapshots = {}
    skipped = set()
    for file_found in context.get_files_found():
        file_found = str(file_found)
        relative = str(context.get_relative_path(file_found)).replace('\\', '/')
        if not os.path.isfile(file_found) or not _ANY_SNAPSHOT.search(relative):
            continue
        match = _SNAPSHOT.search(relative)
        when = None
        if match:
            try:
                when = datetime.datetime(*(int(part) for part in match.groups()[:6]),
                                         tzinfo=datetime.timezone.utc)
            except ValueError:
                when = None
        if when is None:
            folder = relative.rsplit('/', 1)[0]
            if folder not in skipped:
                skipped.add(folder)
                logfunc(f'Signal on-device backup: folder name carries no snapshot time, skipped: {folder}')
            continue
        user, location = _location(relative)
        name = relative.rsplit('/', 2)[-2]
        entry = snapshots.setdefault((user, location, name), {
            'name': name, 'user': user, 'location': location, 'when': when,
            'tmp': bool(match.group(7)), 'members': {}})
        entry['members'].setdefault(match.group(8), (file_found, relative))
    return [snapshots[key] for key in sorted(snapshots, key=lambda item: item[2])]


def _member_sources(snapshot):
    return [snapshot['members'][member][0] for member in ('main', 'metadata', 'files')
            if member in snapshot['members']]


def _open_snapshot(snapshot, key):
    """(state, BackupInfo, frames). State is Opened, Did not open or Not readable."""
    members = snapshot['members']
    if 'main' not in members or 'metadata' not in members:
        return 'Not readable', None, None
    try:
        info, frames = sb.open_snapshot(members['main'][0], members['metadata'][0], key)
    except sb.BackupKeyError:
        logfunc(f'Signal on-device backup: the recovery key did not open {snapshot["name"]}')
        return 'Did not open', None, None
    except (sb.BackupFormatError, OSError) as error:
        logfunc(f'Signal on-device backup: {snapshot["name"]} not read: {error if isinstance(error, sb.BackupFormatError) else type(error).__name__}')
        return 'Not readable', None, None
    return 'Opened', info, frames


def _opened_snapshots(context):
    """(snapshot, BackupInfo, frames) of each snapshot the recovery key opens."""
    key = sb.get_recovery_key()
    snapshots = _find_snapshots(context)
    if snapshots and not key:
        logfunc('Signal on-device backup: no recovery key given, so its contents were not read')
        return
    for snapshot in snapshots:
        state, info, frames = _open_snapshot(snapshot, key)
        if state == 'Opened':
            yield snapshot, info, frames


def _time(milliseconds):
    if not milliseconds:
        return ''
    try:
        return datetime.datetime.fromtimestamp(milliseconds / 1000, datetime.timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _time_text(milliseconds):
    value = _time(milliseconds)
    return value.strftime('%Y-%m-%d %H:%M:%S UTC') if value else ''


def _join(*parts):
    return ' '.join(part for part in parts if part)


def _uuid(value):
    return str(uuid.UUID(bytes=value)) if len(value) == 16 else value.hex()


def _recipient_kind(recipient):
    return sb.which(recipient, ('contact', 'group', 'distributionList', 'self', 'releaseNotes', 'callLink'))


def _recipient_label(recipient):
    kind = _recipient_kind(recipient)
    if kind == 'contact':
        contact = recipient.contact
        return (_join(contact.systemGivenName, contact.systemFamilyName) or contact.systemNickname
                or _join(contact.profileGivenName, contact.profileFamilyName) or contact.username
                or (f'+{contact.e164}' if contact.e164 else '') or f'Recipient {recipient.id}')
    if kind == 'group':
        return recipient.group.snapshot.title.title or f'Group {recipient.id}'
    if kind == 'distributionList':
        return recipient.distributionList.distributionList.name or f'Distribution list {recipient.id}'
    return {'self': 'Self', 'releaseNotes': 'Release Notes', 'callLink': 'Call Link'}.get(kind, f'Recipient {recipient.id}')


class _Media:
    """The encrypted files of one backup folder, read once each."""

    def __init__(self, context, snapshot):
        self.files = {}
        relative = next(iter(snapshot['members'].values()))[1]
        folder = re.sub(r'([*?\[])', r'[\1]', relative.rsplit('/', 2)[0])
        seeker = context.get_seeker()
        found = seeker.search(f'*/{folder}/files/*/*') if seeker else []
        for path in found or []:
            path = str(path)
            if os.path.isfile(path):
                self.files.setdefault(os.path.basename(path), path)
        self.results = {}

    def read(self, pointer):
        """(bytes or None, status, path) of a FilePointer."""
        info = pointer.locatorInfo
        if not info.localKey or not info.plaintextHash:
            return None, 'No local key or plaintext hash', ''
        name = sb.media_file_name(info.plaintextHash, info.localKey)
        if name not in self.results:
            path = self.files.get(name)
            if not path:
                self.results[name] = (None, 'File missing', '')
            else:
                with open(path, 'rb') as handle:
                    plain = sb.decrypt_media(handle.read(), info.localKey, info.size, info.plaintextHash)
                self.results[name] = (plain, 'Verified' if plain is not None else 'Did not verify', path)
        return self.results[name]

    def check_in(self, pointer):
        """(media reference or None, status)."""
        plain, status, path = self.read(pointer)
        if plain is None:
            return None, status
        return check_in_embedded_media(path, plain, name=pointer.fileName or ''), status


_ITEM_KINDS = {
    'standardMessage': 'Message', 'contactMessage': 'Contact Card', 'stickerMessage': 'Sticker',
    'remoteDeletedMessage': 'Remote Deleted', 'updateMessage': 'Update', 'paymentNotification': 'Payment Notification',
    'giftBadge': 'Gift Badge', 'viewOnceMessage': 'View Once', 'directStoryReplyMessage': 'Story Reply',
    'poll': 'Poll', 'adminDeletedMessage': 'Admin Deleted',
}
# Enum names from Backup.proto (SimpleChatUpdate.Type, IndividualCall.Type, .Direction, .State)
_SIMPLE_UPDATES = {
    1: 'JOINED_SIGNAL', 2: 'IDENTITY_UPDATE', 3: 'IDENTITY_VERIFIED', 4: 'IDENTITY_DEFAULT', 5: 'CHANGE_NUMBER',
    6: 'RELEASE_CHANNEL_DONATION_REQUEST', 7: 'END_SESSION', 8: 'CHAT_SESSION_REFRESH', 9: 'BAD_DECRYPT',
    10: 'PAYMENTS_ACTIVATED', 11: 'PAYMENT_ACTIVATION_REQUEST', 12: 'UNSUPPORTED_PROTOCOL_MESSAGE',
    13: 'REPORTED_SPAM', 14: 'BLOCKED', 15: 'UNBLOCKED', 16: 'MESSAGE_REQUEST_ACCEPTED',
}
_CALL_TYPES = {0: 'UNKNOWN_TYPE', 1: 'AUDIO_CALL', 2: 'VIDEO_CALL'}
_CALL_DIRECTIONS = {0: 'UNKNOWN_DIRECTION', 1: 'INCOMING', 2: 'OUTGOING'}
_CALL_STATES = {0: 'UNKNOWN_STATE', 1: 'ACCEPTED', 2: 'NOT_ACCEPTED', 3: 'MISSED', 4: 'MISSED_NOTIFICATION_PROFILE'}
_SEND_STATES = ('pending', 'sent', 'delivered', 'read', 'viewed', 'skipped', 'failed')
_UPDATES = ('simpleUpdate', 'groupChange', 'expirationTimerChange', 'profileChange', 'threadMerge',
            'sessionSwitchover', 'individualCall', 'groupCall', 'learnedProfileChange', 'pollTerminate',
            'pinMessage')


def _item_content(item):
    """(kind, text, [(role, FilePointer)], reactions, Quote or None, link preview text)."""
    name = sb.which(item, tuple(_ITEM_KINDS))
    kind = _ITEM_KINDS.get(name, 'Unknown')
    text = ''
    pointers = []
    reactions = []
    quote = None
    links = ''
    if name == 'standardMessage':
        message = item.standardMessage
        text = message.text.body
        reactions = message.reactions
        quote = message.quote if message.HasField('quote') else None
        pointers = [('Attachment', attachment.pointer) for attachment in message.attachments]
        if message.HasField('longText'):
            pointers.append(('Long text', message.longText))
        for preview in message.linkPreview:
            if preview.HasField('image'):
                pointers.append(('Link preview image', preview.image))
        links = '\n'.join(_join(preview.url, preview.title) for preview in message.linkPreview)
    elif name == 'contactMessage':
        reactions = item.contactMessage.reactions
        text = '[Contact card]'
    elif name == 'stickerMessage':
        reactions = item.stickerMessage.reactions
        text = item.stickerMessage.sticker.emoji or '[Sticker]'
        if item.stickerMessage.sticker.HasField('data'):
            pointers = [('Sticker', item.stickerMessage.sticker.data)]
    elif name == 'viewOnceMessage':
        reactions = item.viewOnceMessage.reactions
        if item.viewOnceMessage.HasField('attachment'):
            pointers = [('View once', item.viewOnceMessage.attachment.pointer)]
        else:
            text = '[View once, no attachment]'
    elif name == 'directStoryReplyMessage':
        reply = item.directStoryReplyMessage
        reactions = reply.reactions
        text = reply.emoji or reply.textReply.text.body
        if reply.textReply.HasField('longText'):
            pointers = [('Long text', reply.textReply.longText)]
    elif name == 'poll':
        reactions = item.poll.reactions
        text = _join(item.poll.question, '/'.join(option.option for option in item.poll.options))
    elif name == 'updateMessage':
        update = sb.which(item.updateMessage, _UPDATES)
        kind = f'Update: {update}' if update else 'Update'
        if update == 'simpleUpdate':
            value = item.updateMessage.simpleUpdate.type
            text = f'[{_SIMPLE_UPDATES.get(value, value)}]'
        elif update == 'individualCall':
            call = item.updateMessage.individualCall
            text = (f'[{_CALL_TYPES.get(call.type, call.type)}, {_CALL_DIRECTIONS.get(call.direction, call.direction)}, '
                    f'{_CALL_STATES.get(call.state, call.state)}]')
    elif name in ('remoteDeletedMessage', 'adminDeletedMessage'):
        text = f'[{kind}]'
    return kind, text, pointers, reactions, quote, links


def _direction(item):
    name = sb.which(item, ('incoming', 'outgoing', 'directionless'))
    return {'incoming': 'Incoming', 'outgoing': 'Outgoing', 'directionless': 'None'}.get(name, '')


def _send_status(item, labels):
    lines = []
    for status in item.outgoing.sendStatus:
        state = sb.which(status, _SEND_STATES) or 'pending'
        lines.append(_join(f'{labels.get(status.recipientId, status.recipientId)}:', state,
                           _time_text(status.timestamp)))
    return '\n'.join(lines)


def _message_row(item, snapshot, labels, chats, media, revision):
    kind, text, pointers, reactions, quote, links = _item_content(item)
    references = []
    for role, pointer in pointers:
        if role == 'Long text':
            plain = media.read(pointer)[0]
            if plain is not None:
                try:
                    text = plain.decode('utf-8')
                except UnicodeDecodeError:
                    logfunc('Signal on-device backup: a long text attachment is not UTF-8; kept the short text')
            continue
        reference = media.check_in(pointer)[0]
        if reference:
            references.append(reference)
    incoming = item.incoming if item.HasField('incoming') else None
    received = incoming.dateReceived if incoming else item.outgoing.dateReceived if item.HasField('outgoing') else 0
    chat = chats.get(item.chatId)
    stamp = snapshot['when'].strftime('%Y%m%d%H%M%S')
    return (
        _time(item.dateSent), _time(received), _time(incoming.dateServerSent) if incoming else '',
        _time(quote.targetSentTimestamp) if quote else '', _time(item.expireStartDate), snapshot['when'],
        _direction(item), labels.get(item.authorId, item.authorId), labels.get(chat.recipientId, '') if chat else '',
        text, references or '', kind, _send_status(item, labels) if item.HasField('outgoing') else '',
        ('Yes' if incoming.read else 'No') if incoming else '', ('Yes' if incoming.sealedSender else 'No') if incoming else '',
        '\n'.join(_join(reaction.emoji, labels.get(reaction.authorId, str(reaction.authorId)),
                        _time_text(reaction.sentTimestamp)) for reaction in reactions),
        labels.get(quote.authorId, quote.authorId) if quote else '', quote.text.body if quote else '', links,
        item.expiresInMs if item.HasField('expiresInMs') else '', revision,
        f'{snapshot["user"]}/{stamp}/{item.chatId}', snapshot['user'],
    )


@artifact_processor
def signalLocalBackups(context):
    key = sb.get_recovery_key()
    data_list = []
    source_paths = []
    for snapshot in _find_snapshots(context):
        members = snapshot['members']
        main_size = os.path.getsize(members['main'][0]) if 'main' in members else ''
        version = ''
        if 'metadata' in members:
            with open(members['metadata'][0], 'rb') as handle:
                parsed = metadata_version(handle.read())
            if parsed is None:
                logfunc(f'Signal on-device backup: metadata not decoded: {members["metadata"][1]}')
            else:
                version = parsed
        listed = ''
        if 'files' in members:
            with open(members['files'][0], 'rb') as handle:
                names = media_names(handle.read())
            if names is None:
                logfunc(f'Signal on-device backup: files list not decoded: {members["files"][1]}')
            else:
                listed = len(names)
        state, backup_time = 'Not given', ''
        if key:
            state, info, _frames = _open_snapshot(snapshot, key)
            if info is not None:
                backup_time = _time(info.backupTimeMs)
        source_paths.extend(_member_sources(snapshot))
        data_list.append((snapshot['when'], backup_time, 'Yes' if snapshot['tmp'] else 'No', state, main_size,
                          version, listed, snapshot['location'], snapshot['user']))

    data_headers = (('Snapshot Time', 'datetime'), ('Backup Time', 'datetime'), 'Temporary Name', 'Recovery Key Result',
                    ('Main Size', 'number'), 'Metadata Version (as stored)', ('Media Listed', 'number'),
                    'Backup Location', 'Android User')
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def signalBackupMessages(context):
    data_list = []
    source_paths = []
    for snapshot, _info, frames in _opened_snapshots(context):
        source_paths.extend(_member_sources(snapshot))
        media = _Media(context, snapshot)
        labels = {}
        chats = {}
        unread = collections.Counter()
        for frame in frames:
            if frame.HasField('recipient'):
                labels[frame.recipient.id] = _recipient_label(frame.recipient)
            elif frame.HasField('chat'):
                chats[frame.chat.id] = frame.chat
            elif frame.HasField('chatItem'):
                item = frame.chatItem
                total = len(item.revisions)
                for index, revision in enumerate(item.revisions, 1):
                    data_list.append(_message_row(revision, snapshot, labels, chats, media,
                                                  f'Earlier version {index} of {total}'))
                data_list.append(_message_row(item, snapshot, labels, chats, media,
                                              f'Latest of {total + 1}' if total else ''))
            else:
                unread[sb.which(frame, tuple(sb.frame_names())) or 'unset'] += 1
        if unread:
            logfunc('Signal on-device backup: frames not reported here: '
                    + ', '.join(f'{name} {count}' for name, count in sorted(unread.items())))
    data_headers = (
        ('Date Sent', 'datetime'), ('Date Received', 'datetime'), ('Date Server Sent', 'datetime'),
        ('Quoted Message Sent', 'datetime'), ('Expire Start', 'datetime'), ('Snapshot Time', 'datetime'),
        'Direction', 'Sender', 'Conversation', 'Message', ('Attachments', 'media'), 'Kind', 'Send Status', 'Read',
        'Sealed Sender', 'Reactions', 'Quoted Author', 'Quoted Text', 'Link Preview',
        ('Expires In (ms)', 'number'), 'Revision', 'Chat Key', 'Android User')
    return data_headers, data_list, '\n'.join(source_paths)


def _attachment_rows(item, revision_note, snapshot, labels, chats, media, pointed):
    """One row per FilePointer of a chat item. Adds the file names it points to to pointed."""
    rows = []
    chat = chats.get(item.chatId)
    for role, pointer in _item_content(item)[2]:
        info = pointer.locatorInfo
        if info.localKey and info.plaintextHash:
            pointed.add(sb.media_file_name(info.plaintextHash, info.localKey))
        reference, status = media.check_in(pointer)
        rows.append((
            _time(item.dateSent), snapshot['when'], labels.get(chat.recipientId, '') if chat else '',
            labels.get(item.authorId, item.authorId), _join(role, revision_note), reference,
            pointer.contentType, pointer.fileName, pointer.caption, info.size if info.size else '',
            info.plaintextHash.hex(), status,
            sb.media_file_name(info.plaintextHash, info.localKey) if info.localKey and info.plaintextHash else '',
            snapshot['user']))
    return rows


@artifact_processor
def signalBackupAttachments(context):
    data_list = []
    source_paths = []
    for snapshot, _info, frames in _opened_snapshots(context):
        source_paths.extend(_member_sources(snapshot))
        media = _Media(context, snapshot)
        labels = {}
        chats = {}
        pointed = set()

        for frame in frames:
            if frame.HasField('recipient'):
                labels[frame.recipient.id] = _recipient_label(frame.recipient)
            elif frame.HasField('chat'):
                chats[frame.chat.id] = frame.chat
            elif frame.HasField('chatItem'):
                for revision in frame.chatItem.revisions:
                    data_list.extend(_attachment_rows(revision, '(earlier version)', snapshot, labels, chats,
                                                      media, pointed))
                data_list.extend(_attachment_rows(frame.chatItem, '', snapshot, labels, chats, media, pointed))
        if 'files' in snapshot['members']:
            with open(snapshot['members']['files'][0], 'rb') as handle:
                names = media_names(handle.read()) or []
            for name in names:
                if name not in pointed:
                    data_list.append(('', snapshot['when'], '', '', '', None, '', '', '', '', '',
                                      'Listed, no pointer read', name, snapshot['user']))
    data_headers = (('Date Sent', 'datetime'), ('Snapshot Time', 'datetime'), 'Conversation', 'Sender', 'Role',
                    ('Attachment', 'media'), 'Content Type', 'File Name', 'Caption', ('Size', 'number'),
                    ('Plaintext SHA-256', 'hash'), 'Status', ('Media Name', 'hash'), 'Android User')
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def signalBackupRecipients(context):
    data_list = []
    source_paths = []
    for snapshot, _info, frames in _opened_snapshots(context):
        source_paths.extend(_member_sources(snapshot))
        for frame in frames:
            if not frame.HasField('recipient'):
                continue
            recipient = frame.recipient
            kind = _recipient_kind(recipient)
            contact = recipient.contact if kind == 'contact' else None
            group = recipient.group if kind == 'group' else None
            blocked_at = contact.blockedAtTimestamp if contact else group.blockedAtTimestamp if group else 0
            # only contacts and groups have a blocked field
            blocked = ('Yes' if (contact or group).blocked else 'No') if contact or group else ''
            data_list.append((
                snapshot['when'], _time(blocked_at),
                _time(contact.notRegistered.unregisteredTimestamp) if contact else '',
                recipient.id, kind, _recipient_label(recipient),
                f'+{contact.e164}' if contact and contact.e164 else '', contact.username if contact else '',
                _uuid(contact.aci) if contact and contact.aci else '', _uuid(contact.pni) if contact and contact.pni else '',
                _join(contact.profileGivenName, contact.profileFamilyName) if contact else '',
                _join(contact.systemGivenName, contact.systemFamilyName) if contact else '',
                _join(contact.nickname.given, contact.nickname.family) if contact else '',
                contact.note if contact else '', blocked,
                contact.visibility if contact else '',
                len(group.snapshot.members) if group else '', snapshot['user']))
    data_headers = (('Snapshot Time', 'datetime'), ('Blocked At', 'datetime'), ('Unregistered At', 'datetime'),
                    'Recipient ID', 'Kind', 'Display Name', ('Phone Number', 'phonenumber'), 'Username', 'ACI', 'PNI',
                    'Profile Name', 'System Name', 'Nickname', 'Note', 'Blocked', 'Visibility (as stored)',
                    ('Group Members', 'number'), 'Android User')
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def signalBackupChats(context):
    data_list = []
    source_paths = []
    for snapshot, _info, frames in _opened_snapshots(context):
        source_paths.extend(_member_sources(snapshot))
        labels = {}
        chats = {}
        stats = {}
        for frame in frames:
            if frame.HasField('recipient'):
                labels[frame.recipient.id] = _recipient_label(frame.recipient)
            elif frame.HasField('chat'):
                chats[frame.chat.id] = frame.chat
            elif frame.HasField('chatItem'):
                sent = frame.chatItem.dateSent
                count, first, last = stats.get(frame.chatItem.chatId, (0, sent, sent))
                stats[frame.chatItem.chatId] = (count + 1, min(first, sent), max(last, sent))
        for chat_id, chat in chats.items():
            count, first, last = stats.get(chat_id, (0, 0, 0))
            mute = 'Muted with no end' if chat.muteUntilMs == 2 ** 63 - 1 else _time_text(chat.muteUntilMs)
            data_list.append((
                _time(first), _time(last), snapshot['when'], chat_id, labels.get(chat.recipientId, chat.recipientId),
                count, chat.expirationTimerMs if chat.HasField('expirationTimerMs') else '',
                'Yes' if chat.archived else 'No', chat.pinnedOrder if chat.HasField('pinnedOrder') else '',
                mute, 'Yes' if chat.markedUnread else 'No', snapshot['user']))
    data_headers = (('First Item', 'datetime'), ('Last Item', 'datetime'), ('Snapshot Time', 'datetime'), 'Chat ID',
                    'Conversation', ('Items', 'number'), ('Disappearing Timer (ms)', 'number'), 'Archived',
                    'Pinned Order', 'Mute Until', 'Marked Unread', 'Android User')
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def signalBackupAccount(context):
    data_list = []
    source_paths = []
    for snapshot, info, frames in _opened_snapshots(context):
        source_paths.extend(_member_sources(snapshot))
        for frame in frames:
            if frame.HasField('account'):
                account = frame.account
                data_list.append((
                    _time(info.backupTimeMs), snapshot['when'], account.username, account.givenName, account.familyName,
                    _join(account.bioEmoji, account.bioText), account.svrPin, info.currentAppVersion,
                    info.firstAppVersion, snapshot['user']))
                break
    data_headers = (('Backup Time', 'datetime'), ('Snapshot Time', 'datetime'), 'Username', 'Given Name',
                    'Family Name', 'Bio', 'PIN (as stored)', 'Current App Version', 'First App Version', 'Android User')
    return data_headers, data_list, '\n'.join(source_paths)
