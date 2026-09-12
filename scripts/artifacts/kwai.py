__artifacts_v2__ = {
    "kwai_watched_videos": {
        "name": "Kwai Watched Videos",
        "description": "Videos Kwai recorded playing, with how long each played where the app recorded it",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Kwai",
        "sample_data": {
            "emu_a15_oss2_v3": "Kwai 13.7.50.646403 | 11 rows",
        },
        "notes": "One row per row of FEED_PHOTO in com.kwai.video/databases/kwai_feed_photo.db, "
                 "which is the app's own record of the videos it played. Video Id is the "
                 "app's PHOTO_ID. The sibling engagement store and the name of a saved video file "
                 "both use it for the same video, which is what joins those to this row.\n"
                 "Started is the PLAY_TIME column, Unix milliseconds reported as UTC. It marks "
                 "playback beginning, which was measured against the device clock rather than "
                 "assumed: across three viewing sessions, seven rows that correspond to a swipe "
                 "were written 258 to 345 milliseconds after the swipe that brought the video up, "
                 "and the video that plays automatically on launch was written 1,314 and 1,979 "
                 "milliseconds after the two measured relaunches.\n"
                 "Session groups rows into one run of the app. It is the SESSION_ID column, and it "
                 "changed on every force stop and relaunch during testing, giving 11 rows under 3 "
                 "session identifiers. Feed is the TYPE column and read hot on every row of the "
                 "tested device, so it is reported as stored.\n"
                 "**Not every video that was watched gets a row, and what decides that was not "
                 "established.** Five swipes produced three rows, four produced two and six "
                 "produced four. It is not a pending write: the table was re-read after 75 seconds "
                 "with the app idle and untouched and neither the row count nor the newest "
                 "Started value moved. An absent row is therefore not evidence a video was not "
                 "watched.\n"
                 "Ended, Watched (ms), Video Length (ms), Pauses and the four interaction columns "
                 "come from the vse table of the sibling store "
                 "com.kwai.video/databases/kwaifeaturecenter.db, joined on content_id equal to "
                 "PHOTO_ID within one app container, so a second Android user's engagement row "
                 "cannot reach the first user's video. That table held 5 of the 11 videos on the tested device and no video "
                 "the watch table did not also hold, so those columns are blank on the rest. Every "
                 "one of its columns is stored as text even where the value is a number or a "
                 "boolean.\n"
                 "**Ended marks the video being left, and Watched (ms) is time actually playing.** "
                 "On four of the five joined rows, Ended minus Started equals Watched (ms) to "
                 "within 425 milliseconds. On the fifth it does not: that row was left on screen "
                 "for about 30 minutes while only 8 minutes of playing was recorded, so the column "
                 "is not wall-clock time on screen.\n"
                 "**Watched (ms) can exceed Video Length (ms)** and did on two rows, by 18,870 "
                 "against 6,450 and by 493,592 against 15,700. So it is not a position within the "
                 "video, and how a value larger than the video's own length is arrived at was not "
                 "established.\n"
                 "**Downloaded did not record a save that happened.** The one video saved to the "
                 "device through the app's own share sheet during testing carries download_status "
                 "false in this table, so a false value is not evidence the video was not saved. "
                 "The Kwai Saved Videos artifact reports the files that were.\n"
                 "Liked, Followed, Commented and Downloaded read false on all five rows that carry "
                 "them and are blank on the other six, so all four are identical across this image "
                 "and none has been seen holding a true value. They are separate columns in the "
                 "store and are reported separately.\n"
                 "Saved Video renders a file in shared storage whose leading digits are exactly this "
                 "video's identifier, where one is present and its bytes really open with an "
                 "ISO base media header. The two must also belong to the same Android user, "
                 "read from the app directory on one side and from the shared storage path on "
                 "the other, so one user's saved file is never shown on another user's row; "
                 "where the shared storage path names no user the code reads it as user 0 and "
                 "a second user's row therefore renders nothing.\n"
                 "LLSID is reported as stored. It repeats across neighbouring rows and its meaning "
                 "was not established. Three vse columns are not reported because nothing "
                 "distinguishes their values on the tested device: page read SELECTED_VIDEO on all "
                 "five rows, play_sound_volume read 5 on all five, and comment_stay_duration_ms read "
                 "0 on all five.\n"
                 "A row is evidence the app played the video, not that a person watched it.",
        "paths": ('*/com.kwai.video/databases/kwai_feed_photo.db*',
                  '*/com.kwai.video/databases/kwaifeaturecenter.db*',
                  '*/DCIM/Camera/*_play.mp4_logo_*'),
        "output_types": "standard",
        "artifact_icon": "player-play",
    },
    "kwai_saved_videos": {
        "name": "Kwai Saved Videos",
        "description": "Video files in shared storage carrying the name shape Kwai gives a saved video",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-11",
        "last_update_date": "2026-09-11",
        "requirements": "none",
        "category": "Kwai",
        "sample_data": {
            "emu_a15_oss2_v3": "Kwai 13.7.50.646403 | 1 rows",
        },
        "notes": "One row per file in the device camera folder whose name carries the app's save "
                 "pattern: a run of digits, then _play.mp4_logo_, then a trailing region code. "
                 "The digit run is required to be 6 to 25 digits long, so a file carrying the "
                 "rest of the shape with a shorter or longer run is not reported. The ids seen "
                 "on the tested device are 19 digits.\n"
                 "**The leading digits are the app's own PHOTO_ID**, which is what joins the file "
                 "back to the Kwai Watched Videos row for the same video. That is a recorded "
                 "identifier rather than a match on size or time. On the tested device one video "
                 "was saved through the app's share sheet and its file name carried the identifier "
                 "of a video already present in the watch table.\n"
                 "**The file name pattern rests on a single observation.** One save was produced "
                 "during testing; a second attempt wrote no file and reported no error, so the "
                 "shape of the name is described from one example and may vary by app version or "
                 "region.\n"
                 "A file is reported because its name matches that shape. Nothing inside the file "
                 "establishes which app wrote it, so a row is a name match and not an "
                 "attribution.\n"
                 "The one saved file measured was written into the device camera folder rather than "
                 "a folder of the app's own, so it sits beside camera output. The store the app keeps for downloaded "
                 "video, OFFLINE_VIDEO_ENTITY in "
                 "com.kwai.video/databases/offline_video.db, stayed empty through that save, so "
                 "the record of a saved video is the file name and not that table.\n"
                 "Video renders the file, and only when its bytes really open with an ISO base media "
                 "header: the name says MP4 and the header is what is checked before the file "
                 "is registered as one, so a row whose Video cell is empty is a file that either "
                 "did not open that way or that the report could not register.\n"
                 "A row is evidence the file is present under a name the app writes, not that "
                 "the app is still installed.",
        "paths": ('*/DCIM/Camera/*_play.mp4_logo_*',),
        "output_types": "standard",
        "artifact_icon": "device-floppy",
    },
}

import os
import re

from scripts.ilapfuncs import artifact_processor, check_in_media, convert_unix_ts_to_utc, \
    get_sqlite_db_records, logfunc
from scripts.artifacts.storagePathViews import canonical_path, unique_files

FEED_DB = 'databases/kwai_feed_photo.db'
VSE_DB = 'databases/kwaifeaturecenter.db'
PACKAGE = 'com.kwai.video'
# <PHOTO_ID>_play.mp4_logo_<REGION>.mp4, observed once during testing. The digit run is
# bounded so an unrelated file that happens to carry the rest of the shape is not reported
# under a video id that cannot be one: the ids seen are 19 digits.
SAVED_NAME = re.compile(r'^(\d{6,25})_play\.mp4_logo_[^/]*$', re.IGNORECASE)
# The Android user whose shared storage a file sits in, so a saved video is never joined
# to another user's watch row.
SHARED_USER = re.compile(r'(?:^|/)(?:data/media|storage/emulated|sdcard)/(\d+)/')


def _files(context, suffix):
    """Matched files ending in suffix, storage-view duplicates collapsed, directories skipped.

    An Android extraction carries the app's private directory under data/data, data/user/0
    and data_mirror, so the seeker's own list would open each database three times.
    """
    out = []
    for found in unique_files(context):
        path = str(found).replace('\\', '/')
        if path.endswith(suffix) and not os.path.isdir(found):
            out.append(found)
    return out


def _app_user(context, path):
    """The Android user of the app container a file sits in, or 0 when there is none.

    A value read from one container is only ever joined to values from the same one, so a
    second Android user's engagement row cannot be attached to the first user's video.
    """
    key, _ = canonical_path(context.get_relative_path(path))
    parts = str(key).split('\x00')
    tenant = parts[1] if len(parts) == 3 else ''
    return tenant.split(':')[1] if ':' in tenant else '0'


def _shared_user(context, path):
    """The Android user whose shared storage a file sits in, or 0 when the path says none."""
    relative = str(context.get_relative_path(path)).replace('\\', '/')
    match = SHARED_USER.search(relative)
    return match.group(1) if match else '0'


def _is_mp4(path):
    """True when the file really opens with an ISO base media container header."""
    try:
        with open(path, 'rb') as handle:
            head = handle.read(12)
    except OSError as error:
        logfunc(f'Kwai: could not read {os.path.basename(str(path))}: {error}')
        return False
    return len(head) >= 12 and head[4:8] == b'ftyp'


def _saved_files(context):
    """(Android user, video id, path) for every file carrying the app's save-name pattern."""
    out = []
    for found in unique_files(context):
        path = str(found).replace('\\', '/')
        if os.path.isdir(found):
            continue
        match = SAVED_NAME.match(os.path.basename(path))
        if match:
            out.append((_shared_user(context, found), match.group(1), found))
    return out


def _ms(value):
    """Unix milliseconds to UTC. Blank for absent, unparsable and non-positive values."""
    if value in (None, ''):
        return ''
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    try:
        return convert_unix_ts_to_utc(value / 1000)
    except (OverflowError, OSError, ValueError):
        return ''


def _int(value):
    """The vse table stores every column as text. Return the number, or the raw value."""
    if value in (None, ''):
        return ''
    try:
        return int(value)
    except (TypeError, ValueError):
        return value


def _flag(value):
    """vse stores its booleans as the strings true and false. Anything else is reported as is."""
    if value in (None, ''):
        return ''
    text = str(value).strip().lower()
    if text in ('true', 'false'):
        return text.capitalize()
    return str(value)


def _vse_by_video(context):
    """(Android user, content_id) -> the engagement row, from the feature-centre store."""
    out = {}
    query = '''SELECT content_id, timestamp, played_duration_ms, total_duration_ms,
                      click_pause_count, like_status, follow_status, comment_status,
                      download_status
               FROM vse'''
    for db_path in _files(context, VSE_DB):
        user = _app_user(context, db_path)
        for row in get_sqlite_db_records(db_path, query):
            if row[0]:
                out[(user, str(row[0]))] = row
    return out


@artifact_processor
def kwai_watched_videos(context):
    engagement = _vse_by_video(context)
    saved = {(user, video_id): path for user, video_id, path in _saved_files(context)}
    query = '''SELECT PHOTO_ID, PLAY_TIME, TYPE, SESSION_ID, LLSID
               FROM FEED_PHOTO ORDER BY PLAY_TIME DESC'''
    data_list = []
    sources = []
    for db_path in _files(context, FEED_DB):
        user = _app_user(context, db_path)
        records = get_sqlite_db_records(db_path, query)
        for video_id, play_time, feed, session, llsid in records:
            key = str(video_id) if video_id is not None else ''
            v = engagement.get((user, key))
            media = ''
            staged = saved.get((user, key))
            if staged and _is_mp4(staged):
                media = check_in_media(staged, os.path.basename(str(staged)),
                                       force_type='video/mp4', force_extension='mp4') or ''
            data_list.append((
                _ms(play_time), _ms(v[1]) if v else '', key, feed or '',
                _int(v[2]) if v else '', _int(v[3]) if v else '',
                _int(v[4]) if v else '',
                _flag(v[5]) if v else '', _flag(v[6]) if v else '',
                _flag(v[7]) if v else '', _flag(v[8]) if v else '',
                media, session or '', llsid or '',
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Started', 'datetime'), ('Ended', 'datetime'), 'Video Id', 'Feed',
        'Watched (ms)', 'Video Length (ms)', 'Pauses', 'Liked', 'Followed', 'Commented',
        'Downloaded', ('Saved Video', 'media'), 'Session', 'LLSID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def kwai_saved_videos(context):
    data_list = []
    sources = []
    for _, video_id, path in sorted(_saved_files(context), key=lambda entry: entry[2]):
        name = os.path.basename(str(path))
        media = ''
        if _is_mp4(path):
            media = check_in_media(path, name, force_type='video/mp4',
                                   force_extension='mp4') or ''
        try:
            size = os.path.getsize(path)
        except OSError as error:
            logfunc(f'Kwai: could not size {name}: {error}')
            size = ''
        data_list.append((media, video_id, name, size, context.get_relative_path(path)))
        if path not in sources:
            sources.append(path)

    data_headers = (
        ('Video', 'media'), 'Video Id', 'File Name', 'Size (bytes)', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
