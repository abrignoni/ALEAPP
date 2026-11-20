"""Signal (org.thoughtcrime.securesms): on-device backup snapshots in a SignalBackups folder."""

__artifacts_v2__ = {
    "signalLocalBackups": {
        "name": "Signal - On-Device Backups",
        "description": "Snapshots of Signal's on-device backup, with the time in each snapshot's folder name, "
                       "whether the folder still has its temporary name, the size of the encrypted main file "
                       "and the number of media files the snapshot lists. The messages and media are "
                       "encrypted and are not read here; the metadata and the media list are read.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-20",
        "last_update_date": "2026-11-20",
        "requirements": "none",
        "category": "Signal",
        "notes": (
            "Layout from Signal-Android tag v8.35.4 (commit b330f4efcf49a0cec87807d18504f07f5df12bf2); "
            "other versions were not checked. File names below are under app/src/main/java/org/"
            "thoughtcrime/securesms/ unless a path is given. The app writes the backup into a folder the "
            "user picks (backup/v2/local/ArchiveFileSystem.kt L65), inside a folder it creates named "
            "SignalBackups (L54, L234). Its own comment says that folder may be renamed or restored under "
            "another name (L113-118), so the folder name is not required here: any folder named "
            "signal-backup- and a time formatted yyyy-MM-dd-HH-mm-ss in UTC (createSnapshot, L274-276), "
            "holding the members main, metadata or files (L384-386), is read as one snapshot. A "
            "signal-backup- folder whose name does not carry that time is skipped and named in the run "
            "log. The time is taken from the phone's clock when the snapshot folder is created, before "
            "its members are written (L275, L283-284): it is when the backup started, not when it "
            "finished. The snapshot is written under the same name ending in -tmp (L283) and renamed "
            "when the backup has been written (finalize, L428-430, called at jobs/LocalArchiveJob.kt "
            "L120). When the job ends, whether or not the backup finished, it deletes that snapshot's "
            "-tmp folder if one is still there (LocalArchiveJob.kt L133-138), and it deletes any -tmp "
            "folder left over before its next backup (L88; deleteOldTemporaryBackups, "
            "ArchiveFileSystem.kt L245-257). After a backup that did not fail it deletes all but the two "
            "snapshots with the newest names (LocalArchiveJob.kt L141; deleteOldBackups, "
            "ArchiveFileSystem.kt L263-268, limit 2). The retention and the -tmp handling are "
            "source-verified only. The one backup folder tested held one snapshot and no -tmp folder.\n"
            "Snapshot Time is the time in the folder name, read as UTC as the app writes it. Temporary "
            "Name is Yes for a folder whose name ends in -tmp, one the app had neither renamed nor "
            "deleted. Main Size is the size of the main file in bytes. main is encrypted with keys "
            "derived from the Account Entropy Pool, a 64-character value (LENGTH = 64, "
            "core/util-jvm/src/main/java/org/signal/core/models/AccountEntropyPool.kt L21; "
            "deriveMessageBackupKey, L102-103) that the app's backup screen showed as the recovery key on "
            "the test phone. Its messages are not read here. Metadata Version (as stored) is field 1 of "
            "the metadata file, a Metadata protobuf message (lib/archive/src/main/protowire/"
            "LocalArchive.proto L8-18, same commit); its field 2 is the encrypted backup ID and is not "
            "reported. A metadata file that does not decode as that message, or has no field 1, leaves "
            "the column empty and is named in the run log (constructed files only). Media Listed is the "
            "number of media names in the snapshot's files member, which the app writes as "
            "length-prefixed FilesFrame messages, each holding one media name (LocalArchive.proto "
            "L20-24; lib/archive/src/main/java/org/signal/archive/local/ArchivedFilesReader.kt L36-41). "
            "A files member that does not decode to its last byte leaves the column empty and is named in "
            "the run log (constructed files only). The media themselves are kept, encrypted, in a files "
            "folder beside the snapshots (ArchiveFileSystem.kt L236; backup/v2/local/LocalArchiver.kt "
            "L108), shared by all snapshots, and are not read here. After a backup the job deletes the "
            "media files no current snapshot lists (LocalArchiveJob.kt L144; ArchiveFileSystem.kt "
            "L324-341), so Media Listed is the snapshot's own list, not a count of the files on disk.\n"
            "Backup Location is the path from the shared storage root to the folder holding the "
            "snapshot, or the whole path inside the extraction where no storage root is recognised. "
            "Android User is the number that follows the shared storage root in the path "
            "(data/media/<N>, userdata/media/<N>, storage/emulated/<N>, mnt/user/<U>/emulated/<N>, "
            "mnt/pass_through/<U>/emulated/<N>); it is empty for a folder outside those roots, such as on "
            "a removable card. The same snapshot seen under several spellings of shared storage is one "
            "row.\n"
            "Known data (the Samsung SM-A166U test phone, Signal 8.35.4): on-device backups were turned on "
            "on 2026-11-20 with the folder KD_signal_backup in shared storage. The session record places "
            "the setup between 08:39 and 08:44 UTC and names one snapshot folder. An adb pull of that "
            "folder, placed under data/media/0 for the run, gave one row with the time in that folder name "
            "in Snapshot Time, Temporary Name No, Main Size 65,600, Metadata Version 1 and Media Listed 7; "
            "the 7 listed names equal the 7 file names in its files folder. Tested only on constructed "
            "files: -tmp folders, several snapshots, a renamed backup folder, one snapshot seen under two "
            "spellings, every storage root spelling above, a folder outside a storage root, and metadata "
            "and files members that do not decode."
        ),
        "paths": ("*/signal-backup-*/main", "*/signal-backup-*/metadata", "*/signal-backup-*/files"),
        "output_types": "standard",
        "artifact_icon": "archive",
    },
}

import datetime
import os
import re

from scripts.ilapfuncs import artifact_processor, logfunc

# The roots a shared storage path can be seen under, with the Android user they name.
_STORAGE_ROOTS = (
    re.compile(r'(?:^|/)(?:user)?data/media/(\d+)/'),
    re.compile(r'(?:^|/)mnt/pass_through/\d+/emulated/(\d+)/'),
    re.compile(r'(?:^|/)mnt/user/\d+/emulated/(\d+)/'),
    re.compile(r'(?:^|/)storage/emulated/(\d+)/'),
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


@artifact_processor
def signalLocalBackups(context):
    snapshots = {}
    skipped = set()
    for file_found in context.get_files_found():
        file_found = str(file_found)
        relative = str(context.get_relative_path(file_found)).replace('\\', '/')
        if not os.path.isfile(file_found) or not _ANY_SNAPSHOT.search(relative):
            continue
        match = _SNAPSHOT.search(relative)
        if not match:
            folder = relative.rsplit('/', 1)[0]
            if folder not in skipped:
                skipped.add(folder)
                logfunc(f'Signal on-device backup: folder name carries no snapshot time, skipped: {folder}')
            continue
        user, location = _location(relative)
        name = relative.rsplit('/', 2)[-2]
        key = (user, location, name)
        entry = snapshots.setdefault(key, {'time': match.groups()[:6], 'tmp': bool(match.group(7)),
                                           'members': {}})
        entry['members'].setdefault(match.group(8), (file_found, relative))

    data_list = []
    source_paths = []
    for (user, location, name), entry in sorted(snapshots.items(), key=lambda item: item[0][2]):
        members = entry['members']
        year, month, day, hour, minute, second = (int(part) for part in entry['time'])
        try:
            when = datetime.datetime(year, month, day, hour, minute, second, tzinfo=datetime.timezone.utc)
        except ValueError:
            when = ''
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
        source_paths.extend(members[member][0] for member in ('main', 'metadata', 'files') if member in members)
        data_list.append((when, 'Yes' if entry['tmp'] else 'No', main_size, version, listed,
                          location, user))

    data_headers = (('Snapshot Time', 'datetime'), 'Temporary Name', ('Main Size', 'number'),
                    'Metadata Version (as stored)', ('Media Listed', 'number'), 'Backup Location',
                    'Android User')
    return data_headers, data_list, '\n'.join(source_paths)
