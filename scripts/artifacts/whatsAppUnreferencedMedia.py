__artifacts_v2__ = {
    "whatsapp_unreferenced_media": {
        "name": "WhatsApp - Media Files With No file_path Entry",
        "description": "Files in WhatsApp's media folder that no file_path in msgstore.db or status.db names",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-26",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Messaging",
        "notes": "Lists files under com.whatsapp's WhatsApp/Media folder (the "
                 "Android/media/com.whatsapp location) whose path after the Media folder matches no "
                 "file_path value in any table of msgstore.db or status.db that has a file_path "
                 "column. On WhatsApp Business 2.26.45.80 those were addon_message_media, "
                 "extended_media_data, message_media, message_quoted_media and sticker_audio_media in "
                 "msgstore.db and media_content in status.db. On the tested com.whatsapp images the "
                 "tables were message_media, message_quoted_media and addon_message_media, with "
                 "extended_media_data on five, and status.db was present on three of eight. On every "
                 "tested input only message_media and message_quoted_media held file_path values. "
                 "status.db held none, so that comparison was not exercised. A media file under "
                 "data/media/<n>, userdata/media/<n>, storage/emulated/<n> or emulated/<n> is compared "
                 "with the databases of Android user n. When its path names no user in one of those "
                 "forms, or that user has no database, it is compared with every database read. "
                 "Matching per user was not exercised with users whose databases differ. A rollback "
                 "copy of a database under data/misc_ce or data/misc_de counts for the user number in "
                 "its path; this was exercised by a unit test only. A path with no readable file "
                 "behind it is skipped, and a recorded time out of range is shown blank. When a "
                 "database cannot be read the log says so and no file is listed; this was not "
                 "exercised. .nomedia files are not listed. A byte-identical copy of the same file "
                 "listed under two storage paths for one user is shown once. File Modified is the UTC "
                 "modified time the zip or tar recorded for the file. It is blank for a folder input, "
                 "whose file times are those of the copy. Modified (no zone, as stored) is filled only "
                 "when the input gave no UTC modified time and recorded a reading with no zone. Folder "
                 "is the part of the path between the Media folder and the file. On the tested "
                 "WhatsApp images the rows were: anne_a15 1 (WhatsApp Images), hc_pixel8pro_a16 8 and "
                 "hc_pixel8pro_a17 8 (.Links), kevin_pocox7_a15 2 (.Links), pixel7a_a14 16 (.Links), "
                 "russell_a14 12 (6 .Links, 5 WhatsApp Images, 1 WhatsApp Video), sharon_a14 7 (3 "
                 ".Links, 4 WhatsApp Images), samsungs20_a13 0. The 8 rows on hc_pixel8pro_a16 and "
                 "hc_pixel8pro_a17 are the same 8 files. samsungs20_a13 held only .nomedia files in "
                 "the Media folder. The 11 listed files in WhatsApp Images and WhatsApp Video "
                 "(anne_a15 1, russell_a14 6, sharon_a14 4) were searched for by file name in every "
                 "column of msgstore.db and wa.db on those images. None was found. No delete test was "
                 "made on com.whatsapp. The known data below is from WhatsApp Business only, read by "
                 "the same code. Known data, emu_a16_w4b_kd_w5_media_delete: the test account sent two "
                 "photos to a chat and deleted both messages for me. The delete dialog offers 'Also "
                 "delete media in this chat from the device gallery'. With it unticked the photo's "
                 "file stayed in the Sent folder and is the one row listed. With it ticked, no file "
                 "for that photo was in the folder at capture, and nothing is listed. Known data, "
                 "emu_a16_w4b_kd_w6_media_received_everyone (made after w5): the test phone sent two "
                 "photos to the test account, which deleted both for me. With the box unticked the "
                 "received photo's file stayed and is listed, and with it ticked, no file for the "
                 "second photo was in the folder at capture. The test account then sent a photo and "
                 "deleted it for everyone with the box unticked, and afterwards the Sent folder held "
                 "no file for it, so that delete left nothing to list. On w6 the two rows are that "
                 "received photo and the Sent photo kept from w5. On the first of the five deletes the "
                 "box opened ticked. On each of the other four it opened in the state chosen at the "
                 "previous delete. What sets its state the first time was not established. A delete "
                 "for everyone with the box ticked, and deletes of media other than photos, were not "
                 "exercised. A row does not establish that a message was deleted. On the tested "
                 "WhatsApp images 43 of 54 rows were files in a .Links folder. What .Links holds was "
                 "not established. Only a Media folder under the package's own folder is read. A "
                 "WhatsApp/Media folder at the top of shared storage is not. On a constructed tree "
                 "with Android users 0 and 10, each user's unreferenced file gave its own row. A copy "
                 "under another package's folder is not matched by the search patterns and gave none. "
                 "The tree's databases were copies of one another, so it does not test matching per "
                 "user. Modified (no zone, as stored) was blank on every tested row. Each zip and tar "
                 "recorded a UTC modified time, so the reading with no zone was not used. Android User "
                 "held 0 on every row from the corpus inputs.",
        "paths": ('*/com.whatsapp/databases/msgstore.db*', '*/com.whatsapp/databases/status.db*',
                  '*/com.whatsapp/WhatsApp/Media/*'),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "image",
        "sample_data": {
            "anne_a15": "Android 15 | com.whatsapp vc 252573000 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.whatsapp vc 262307413 | 8 rows",
            "hc_pixel8pro_a17": "Android 17 | com.whatsapp vc 262907320 | 8 rows",
            "kevin_pocox7_a15": "Android 15 | com.whatsapp vc 252674000 | 2 rows",
            "pixel7a_a14": "Android 14 | com.whatsapp vc 241481004 | 16 rows",
            "russell_a14": "Android 14 | com.whatsapp vc 241676004 | 12 rows",
            "samsungs20_a13": "Android 13 | com.whatsapp vc 253776000 | 0 rows",
            "sharon_a14": "Android 14 | com.whatsapp vc 241676004 | 7 rows",
        },
    },
    "whatsapp_business_unreferenced_media": {
        "name": "WhatsApp Business - Media Files With No file_path Entry",
        "description": "Files in WhatsApp Business's media folder that no file_path in msgstore.db or "
                       "status.db names",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-26",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Messaging",
        "notes": "Lists files under com.whatsapp.w4b's WhatsApp Business/Media folder (the "
                 "Android/media/com.whatsapp.w4b location) whose path after the Media folder matches "
                 "no file_path value in any table of msgstore.db or status.db that has a file_path "
                 "column. On WhatsApp Business 2.26.45.80 those were addon_message_media, "
                 "extended_media_data, message_media, message_quoted_media and sticker_audio_media in "
                 "msgstore.db and media_content in status.db. On every tested input only message_media "
                 "and message_quoted_media held file_path values. status.db held none, so that "
                 "comparison was not exercised. A media file under data/media/<n>, userdata/media/<n>, "
                 "storage/emulated/<n> or emulated/<n> is compared with the databases of Android user "
                 "n. When its path names no user in one of those forms, or that user has no database, "
                 "it is compared with every database read. Matching per user was not exercised with "
                 "users whose databases differ. A rollback copy of a database under data/misc_ce or "
                 "data/misc_de counts for the user number in its path; this was exercised by a unit "
                 "test only. A path with no readable file behind it is skipped, and a recorded time "
                 "out of range is shown blank. When a database cannot be read the log says so and no "
                 "file is listed; this was not exercised. .nomedia files are not listed. A "
                 "byte-identical copy of the same file listed under two storage paths for one user is "
                 "shown once. File Modified is the UTC modified time the zip or tar recorded for the "
                 "file. It is blank for a folder input, whose file times are those of the copy. "
                 "Modified (no zone, as stored) is filled only when the input gave no UTC modified "
                 "time and recorded a reading with no zone. Folder is the part of the path between the "
                 "Media folder and the file. The four earlier emu_a16_w4b_kd keys gave no rows. Known "
                 "data, emu_a16_w4b_kd_w5_media_delete: the test account sent two photos to a chat and "
                 "deleted both messages for me. The delete dialog offers 'Also delete media in this "
                 "chat from the device gallery'. With it unticked the photo's file stayed in the Sent "
                 "folder and is the one row listed. With it ticked, no file for that photo was in the "
                 "folder at capture, and nothing is listed. Known data, "
                 "emu_a16_w4b_kd_w6_media_received_everyone (made after w5): the test phone sent two "
                 "photos to the test account, which deleted both for me. With the box unticked the "
                 "received photo's file stayed and is listed, and with it ticked, no file for the "
                 "second photo was in the folder at capture. The test account then sent a photo and "
                 "deleted it for everyone with the box unticked, and afterwards the Sent folder held "
                 "no file for it, so that delete left nothing to list. On w6 the two rows are that "
                 "received photo and the Sent photo kept from w5. On the first of the five deletes the "
                 "box opened ticked. On each of the other four it opened in the state chosen at the "
                 "previous delete. What sets its state the first time was not established. A delete "
                 "for everyone with the box ticked, and deletes of media other than photos, were not "
                 "exercised. A row does not establish that a message was deleted. On the eight "
                 "com.whatsapp images named in the WhatsApp artifact's notes, run with the same code, "
                 "43 of 54 rows were files in a .Links folder. What .Links holds was not established. "
                 "Only a Media folder under the package's own folder is read. A WhatsApp "
                 "Business/Media folder at the top of shared storage is not. On a constructed tree "
                 "with Android users 0 and 10, each user's unreferenced file gave its own row. A copy "
                 "under another package's folder is not matched by the search patterns and gave none. "
                 "The tree's databases were copies of one another, so it does not test matching per "
                 "user. Modified (no zone, as stored) was blank on every tested row. Each zip and tar "
                 "recorded a UTC modified time, so the reading with no zone was not used. Android User "
                 "held 0 on every row from the corpus inputs.",
        "paths": ('*/com.whatsapp.w4b/databases/msgstore.db*', '*/com.whatsapp.w4b/databases/status.db*',
                  '*/com.whatsapp.w4b/WhatsApp Business/Media/*'),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "image",
        "sample_data": {
            "emu_a16_w4b_kd_w1_channel_followed": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 0 rows",
            "emu_a16_w4b_kd_w2_channel_deleted": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 0 rows",
            "emu_a16_w4b_kd_w3_status_viewed": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 0 rows",
            "emu_a16_w4b_kd_w4_custom_away": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 0 rows",
            "emu_a16_w4b_kd_w5_media_delete": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 1 row",
            "emu_a16_w4b_kd_w6_media_received_everyone": "Android 16 | com.whatsapp.w4b 2.26.45.80 | 2 rows",
        },
    },
}

import filecmp
import os
import re
import sqlite3
from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import android_user, unique_files
from scripts.ilapfuncs import artifact_processor, check_in_media, is_sqlite_sidecar, logfunc, \
    open_sqlite_db_readonly

_ROLLBACK_USER = re.compile(r'(?:^|/)(?:user)?data/misc_(?:ce|de)/(\d+)/rollback/\d+/')
_MEDIA_USER = re.compile(r'(?:^|/)(?:(?:user)?data/media|storage/emulated|emulated)/(\d+)/')


def _usable(value):
    """Whether a recorded time is a nonzero, finite number."""
    return isinstance(value, (int, float)) and value != 0 and value == value and abs(value) != float('inf')


def _file_times(seeker, path):
    """(UTC seconds, reading with no zone) the input records for a staged file, never the copy's own time."""
    infos = getattr(seeker, 'file_infos', None) or {}
    windows = str(path).replace('/', '\\')
    bare = windows.removeprefix('\\\\?\\')
    info = next((infos[name] for name in (str(path), windows, bare, '\\\\?\\' + bare) if name in infos), None)
    times = getattr(info, 'times', None)
    modified = getattr(times, 'modified', None)
    if _usable(modified):
        return modified, ''
    reading = getattr(times, 'modified_no_zone', None)
    if reading:
        return None, reading
    # modification_date is not used: a folder input records only the time of the examiner's copy there.
    return None, ''


def _database_user(relative_path):
    """The Android user of a database path, including the user number of a rollback copy."""
    user = android_user(relative_path)
    if user:
        return user
    match = _ROLLBACK_USER.search(str(relative_path).replace('\\', '/'))
    return match.group(1) if match else ''


def _utc(seconds):
    """A recorded time as a UTC datetime, or blank when it is out of range."""
    if not seconds:
        return ''
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _after_media(path):
    """The part of a path after its Media/ folder, the form msgstore.db stores file_path in."""
    path = str(path).replace('\\', '/')
    index = path.find('/Media/')
    if index >= 0:
        return path[index + len('/Media/'):]
    return path[len('Media/'):] if path.startswith('Media/') else None


def _referenced(context, path):
    """Every file_path value in the tables of one msgstore.db or status.db that have that column.

    None when the database cannot be read, so a file is never listed for want of a database that could not be read.
    """
    names = set()
    db = open_sqlite_db_readonly(path)
    if db is None:
        logfunc(f'WhatsApp media: could not open {context.get_relative_path(path)}')
        return None
    try:
        tables = [row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        for table in tables:
            columns = [row[1] for row in db.execute(f'PRAGMA table_info("{table}")')]
            if 'file_path' not in columns:
                continue
            for (value,) in db.execute(f'SELECT file_path FROM "{table}" WHERE file_path IS NOT NULL'):
                rest = _after_media(value)
                if rest:
                    names.add(rest)
    except sqlite3.Error as error:
        logfunc(f'WhatsApp media: could not read {context.get_relative_path(path)}: {error}')
        return None
    finally:
        db.close()
    return names


def _report(context, marker):
    data_headers = (('File Modified', 'datetime'), 'Modified (no zone, as stored)', ('File', 'media'), 'Folder',
                    'File Name', ('Size (bytes)', 'number'), 'Android User', 'Location')
    files = [str(path) for path in unique_files(context)]
    by_user, everything = {}, set()
    databases = []
    for path in files:
        name = os.path.basename(path)
        if name in ('msgstore.db', 'status.db') and not is_sqlite_sidecar(path):
            databases.append(path)
            names = _referenced(context, path)
            if names is None:
                logfunc('WhatsApp media: no files listed, because a database could not be read')
                return data_headers, [], '\n'.join(databases)
            everything |= names
            user = _database_user(context.get_relative_path(path))
            if user:
                by_user.setdefault(user, set()).update(names)
    if not databases:
        return data_headers, [], ''
    data_list, sources = [], list(databases)
    seeker = context.get_seeker()
    shown = {}
    for path in files:
        relative = context.get_relative_path(path).replace('\\', '/')
        index = relative.find(marker)
        # A link whose target is outside the input is returned with no staged file behind it.
        if index < 0 or os.path.basename(path) == '.nomedia' or not os.path.isfile(path):
            continue
        rest = relative[index + len(marker):]
        match = _MEDIA_USER.search(relative)
        user = match.group(1) if match else ''
        names = by_user.get(user, everything) if user in by_user else everything
        if rest in names:
            continue
        # The same folder can be listed under two storage paths (data/media/<n> and an emulated/<n> view).
        # A byte-identical copy at the same place under the Media folder, for the same user, is shown once.
        copies = shown.setdefault((user, rest), [])
        if any(filecmp.cmp(earlier, path, shallow=False) for earlier in copies):
            continue
        copies.append(path)
        modified, no_zone = _file_times(seeker, path)
        folder = rest.rsplit('/', 1)[0] if '/' in rest else ''
        sources.append(path)
        when = _utc(modified)
        data_list.append((when, no_zone, check_in_media(path, name=os.path.basename(path)) or '', folder,
                          os.path.basename(path), os.path.getsize(path), user,
                          os.path.dirname(relative)))
    data_list.sort(key=lambda row: (row[6], row[3], row[4]))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def whatsapp_unreferenced_media(context):
    return _report(context, 'WhatsApp/Media/')


@artifact_processor
def whatsapp_business_unreferenced_media(context):
    return _report(context, 'WhatsApp Business/Media/')
