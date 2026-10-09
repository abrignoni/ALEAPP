__artifacts_v2__ = {
    "twitterCachedVideos": {
        "name": "Twitter - Cached Videos (ExoPlayer)",
        "description": "Videos held in the X (Twitter) app's two ExoPlayer media caches, one row per video "
                       "media id per cache folder, with the earliest and latest time a cached segment was "
                       "touched, and the rejoined video where exactly one playable file matches. The precache and "
                       "video_cache folders are reported separately.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-26",
        "requirements": "none",
        "category": "Twitter",
        "notes": "Read from cache/precache and cache/video_cache, each an ExoPlayer SimpleCache: "
                 "cached_content_index.exi maps an integer id to the cache key (here the segment URL on "
                 "video.twimg.com) and the span files <id>.<position>.<last touch ms>.v3.exo hold the bytes "
                 "(androidx media3 1.11.0 CachedContentIndex.LegacyStorage and SimpleCacheSpan; the index layout "
                 "is version 2 with per-entry metadata (VERSION = 2 in google/ExoPlayer CachedContentIndex.java "
                 "at tag r2.8.0; tag r2.7.3 has VERSION = 1); older version 0 and 1 indexes, which carry a "
                 "length in place of metadata, are read too; an index whose flags mark it "
                 "encrypted is skipped with a log line, and none was on the tested images). Media Path is the "
                 "host, media folder and id of the URL as stored for the folders amplify_video, ext_tw_video, "
                 "tweet_video, dm_gif and dm_video, for example video.twimg.com/amplify_video/<id>; a key with "
                 "any other shape is reported whole, up to its query string; "
                 "a subtitles/<folder>/<id> URL joins its video's row. The id is the media id in the URL and is "
                 "not resolved to a tweet here. Segments counts the index entries (playlists, video and audio "
                 "segments) under that media path, Span Files and Bytes Cached the span files and their sizes, "
                 "Declared Length the sum of the exo_len metadata values. First and Last Touched are the earliest "
                 "and latest last-touch timestamps in the span file names, which ExoPlayer rewrites when it reads "
                 "a span again only if the app's cache evictor asks for that (SimpleCache.touchSpan); both were "
                 "set on every row of the tested images. Whether a prefetched video in precache "
                 "was watched is not established by this cache. On the 5 tested images holding the app, 61 rows: "
                 "media folders amplify_video (32), ext_tw_video (24), tweet_video (3, whose id is an alphanumeric "
                 "token) and dm_gif (2); one image held only precache, so Cache Folder was uniform there. "
                 "Media is the file ExoPlayer - Rejoined Cached Media joined for this media path (for an HLS video, "
                 "the stream with its audio when the cache holds it), shown only when exactly one playable file in the "
                 "same cache folder matches: 21 of the 61 rows. Of the other 40, 38 are precache rows whose cache "
                 "holds the video's playlists and media segments but not the initialization segment they need, so "
                 "nothing in it plays, and 2 are video_cache rows with two playable files each, both in that "
                 "artifact. "
                 "Android User names the user whose folder the cache is in when the table holds rows from more than "
                 "one user, and is blank when every row comes from one user, as on every tested image.",
        "paths": ('*/com.twitter.android/cache/precache/*', '*/com.twitter.android/cache/video_cache/*'),
        "output_types": "standard",
        "artifact_icon": "film",
        "sample_data": {
            "pixel3_a11": "Android 11 | com.twitter.android | 15 rows",
            "pixel3_a12": "Android 12 | com.twitter.android | 6 rows",
            "pixel7a_a14": "Android 14 | com.twitter.android | 12 rows",
            "samsungs20_a13": "Android 13 | com.twitter.android | 13 rows",
            "sharon_a14": "Android 14 | com.twitter.android | 15 rows",
        },
    },
    "snapchatStreamedMedia": {
        "name": "Snapchat - Media Cache Index Entries (ExoPlayer)",
        "description": "Entries in the Snapchat app's ExoPlayer cache index (files/streaming): "
                       "the content type and content ids the app recorded in the cache index, the "
                       "resolved URL, and the time the cached bytes were last touched.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "Snapchat",
        "notes": "Read from files/streaming/cached_content_index.exi (androidx media3 1.11.0 "
                 "CachedContentIndex.LegacyStorage, version 2; an index marked encrypted is skipped with a log "
                 "line, and none was on the tested images) and the <id>.<position>.<last touch ms>.v3.exo span "
                 "files beside it. Snapchat stores its own metadata on each entry under custom_snap_* names; "
                 "Content Type, Content ID and Content Object ID are those values as stored and are not documented "
                 "by Snap. Last Touched is the latest last-touch timestamp among the entry's span files, which "
                 "ExoPlayer rewrites when it reads a span again only if the app's cache evictor asks for that "
                 "(SimpleCache.touchSpan); 661 of the 801 entries on the tested images have a single "
                 "span file and 138 have two or more (up to 14), and only the latest touch is reported. Bytes "
                 "Cached is the size of the span files; Declared Length the exo_len metadata value. An entry with "
                 "span files records that bytes for that key were written to the cache. Whether the media was "
                 "shown or played is not established by this cache. On the 7 tested images holding entries, "
                 "801 entries (an eighth image held an index with no entries): content types "
                 "discover_story_streaming_snap.discover_story_streaming_snap (530), story_snap.story_snap (265), "
                 "discover_publisher_shows_story_large.discover_publisher_shows_story_large (4) and "
                 "ad_remote_asset.ad_remote_asset (2); 2 entries had no span file, so their Last Touched, Bytes "
                 "Cached and Span Files are blank or zero. There is no Media column: joined back together, "
                 "Snapchat's cached items carry no file signature (all 105 on russell_a14 and all 34 on pixel7a_a14) "
                 "and measured 8.0 bits per byte over their first 64 KiB on pixel7a_a14, so nothing in them plays as "
                 "stored. "
                 "Android User names the user whose folder the cache is in when the table holds rows from more than "
                 "one user, and is blank when every row comes from one user, as on every tested image.",
        "paths": ('*/com.snapchat.android/files/streaming/*',),
        "output_types": "standard",
        "artifact_icon": "film",
        "sample_data": {
            "cookbook_a11": "Android 11 | com.snapchat.android | 39 rows",
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android | 1 row",
            "hc_pixel8pro_a17": "Android 17 | com.snapchat.android | 0 rows",
            "pixel3_a12": "Android 12 | com.snapchat.android | 29 rows",
            "pixel7a_a14": "Android 14 | com.snapchat.android | 35 rows",
            "russell_a14": "Android 14 | com.snapchat.android | 105 rows",
            "russell_pixel6a_a13": "Android 13 | com.snapchat.android | 244 rows",
            "sharon_a14": "Android 14 | com.snapchat.android | 348 rows",
        },
    },
    "instagramCachedVideos": {
        "name": "Instagram - Cached Videos (ExoPlayer)",
        "description": "Videos held in the Instagram app's ExoPlayer cache (cache/ExoPlayerCacheDir/videocache), "
                       "one row per cache key prefix, with the two numeric ids the key starts with and the "
                       "earliest and latest time a cached span was touched, and the rejoined video where the "
                       "row's key prefix names exactly one.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-26",
        "requirements": "none",
        "category": "Instagram",
        "notes": "This artifact reads no index file for this cache: each span file is named "
                 "<key>.<position>.<last touch ms>.v2.exo "
                 "(androidx media3 1.11.0 SimpleCacheSpan CACHE_FILE_PATTERN_V2), so the key is read from the file "
                 "name. Keys start with two numbers joined by an underscore, sometimes followed by a third "
                 "underscore-joined token (15 of the 330 groups on the tested images); Media ID and Second ID are "
                 "those two numbers as stored. On pixel7a_a14 one Media ID equalled a medias.id in the app's "
                 "flash_media database and one Second ID a user_feed_items.id, which is the extent of the "
                 "cross-check. Rows are grouped on that pair (330 groups on the 7 tested images holding the "
                 "cache). First and Last Touched are the earliest and latest last-touch timestamps of the group's "
                 "span files, which ExoPlayer rewrites when it reads a span again only if the app's cache evictor "
                 "asks for that (SimpleCache.touchSpan); Bytes Cached is the size of the span "
                 "files. Media is the video file ExoPlayer - Rejoined Cached Media joined for this key prefix, shown "
                 "only when exactly one video file in the same cache folder matches. The row's "
                 "sound, when the app cached it separately, is its own file in that artifact. On the tested images "
                 "ffmpeg 9.0.1 reported that 14 of the joined files shown (WebM) end prematurely. "
                 "Android User names the user whose folder the cache is in when the table holds rows from more than "
                 "one user, and is blank when every row comes from one user, as on every tested image.",
        "paths": ('*/com.instagram.android/cache/ExoPlayerCacheDir/videocache/*',),
        "output_types": "standard",
        "artifact_icon": "film",
        "sample_data": {
            "galaxys10_a10": "Android 10 | com.instagram.android | 53 rows",
            "hc_pixel8pro_a16": "Android 16 | com.instagram.android | 4 rows",
            "hc_pixel8pro_a17": "Android 17 | com.instagram.android | 4 rows",
            "kevin_pocox7_a15": "Android 15 | com.instagram.android | 249 rows",
            "pixel7a_a14": "Android 14 | com.instagram.android | 4 rows",
            "samsunga53_a14": "Android 14 | com.instagram.android | 3 rows",
            "samsungs20_a13": "Android 13 | com.instagram.android | 13 rows",
        },
    },
    "redditCachedVideos": {
        "name": "Reddit - Cached Videos (ExoPlayer)",
        "description": "Videos held in the Reddit app's ExoPlayer cache (cache/reddit-video), indexed in "
                       "databases/exoplayer_internal.db, one row per v.redd.it video id with the earliest "
                       "and latest time a cached span was touched, and the rejoined video where one file carries "
                       "that id.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-26",
        "requirements": "none",
        "category": "Reddit",
        "notes": "The index is the SQLite storage of ExoPlayer's cache (androidx media3 1.11.0 "
                 "CachedContentIndex.DatabaseStorage, present in google/ExoPlayer "
                 "CachedContentIndex.java at tag r2.10.0 and absent at r2.9.6): the "
                 "ExoPlayerCacheIndex<uid> table maps an id to the cache key (the segment URL) and "
                 "ExoPlayerCacheFileMetadata<uid> records each span file's length and last touch in Unix "
                 "milliseconds. The span files sit in external storage "
                 "(Android/data/com.reddit.frontpage/cache/reddit-video) while the database is in the app's data "
                 "folder, so files are grouped by Android user. Video ID is the path segment after v.redd.it in "
                 "the URL, as stored. Segments counts the index entries under that video id, Span Files and Bytes "
                 "Cached the span files found. On the 3 tested images holding the cache, 77 rows, every one with "
                 "span files. The ExoPlayerDownloads table in the same database was empty on the one public image "
                 "and is not read. Whether a cached video was watched is not established by the cache. Media is "
                 "the file ExoPlayer - Rejoined Cached Media joined for this video id, shown only when exactly one "
                 "playable joined file for the same Android user carries the id in its key: 39 of 42 rows on "
                 "russell_a14, 33 of 34 on russell_pixel6a_a13 and 1 of 1 on pixel7a_a14. Of the other four, two ids "
                 "had two playable joined files each, both in that artifact, and two had none. "
                 "Android User names the user whose folder the cache is in when the table holds rows from more than "
                 "one user, and is blank when every row comes from one user, as on every tested image.",
        "paths": ('*/com.reddit.frontpage/databases/exoplayer_internal.db*',
                  '*/com.reddit.frontpage/cache/reddit-video/*'),
        "output_types": "standard",
        "artifact_icon": "film",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.reddit.frontpage | 1 row",
            "russell_a14": "Android 14 | com.reddit.frontpage | 42 rows",
            "russell_pixel6a_a13": "Android 13 | com.reddit.frontpage | 34 rows",
        },
    },
}

import os
import re
import sqlite3
import struct
from collections import defaultdict
from datetime import datetime, timezone

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import canonical_path, unique_files
from scripts.artifacts.exoplayerCachedMedia import media_ref, rejoined_records, shown, shows_media

_INDEX_NAME = 'cached_content_index.exi'
_SPAN_V3 = re.compile(r'^(\d+)\.(\d+)\.(\d+)\.v3\.exo$')
_SPAN_V2 = re.compile(r'^(.+)\.(\d+)\.(\d+)\.v2\.exo$', re.S)
_FLAG_ENCRYPTED_INDEX = 1
_VERSION_METADATA_INTRODUCED = 2
_TWITTER_MEDIA = re.compile(r'^https?://([^/]+)/(?:[^/?]+/)*?(amplify_video|ext_tw_video|tweet_video|dm_gif|dm_video)/([^/?.]+)')
_INSTAGRAM_KEY = re.compile(r'^(\d+)_(\d+)[._]')
_REDDIT_VIDEO = re.compile(r'^https?://v\.redd\.it/([^/?]+)')


def _utc_millis(value):
    try:
        return datetime.fromtimestamp(int(value) / 1000, timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _read_utf(data, offset):
    """Java DataInput.readUTF: a big-endian u16 length followed by that many bytes."""
    length = struct.unpack_from('>H', data, offset)[0]
    offset += 2
    return data[offset:offset + length].decode('utf-8', 'replace'), offset + length


def _read_metadata(data, offset):
    """DefaultContentMetadata as CachedContentIndex.readContentMetadata reads it."""
    count = struct.unpack_from('>i', data, offset)[0]
    offset += 4
    metadata = {}
    for _ in range(count):
        name, offset = _read_utf(data, offset)
        size = struct.unpack_from('>i', data, offset)[0]
        offset += 4
        value = data[offset:offset + size]
        offset += size
        if name == 'exo_len' and size == 8:
            metadata[name] = struct.unpack('>q', value)[0]
        else:
            metadata[name] = value.decode('utf-8', 'replace')
    return metadata, offset


def _read_index(path):
    """[(id, key, metadata)] from a legacy cached_content_index.exi, or None when unreadable."""
    try:
        with open(path, 'rb') as handle:
            data = handle.read()
        version, flags, count = struct.unpack_from('>iii', data, 0)
    except (OSError, struct.error):
        return None
    if version < 0 or version > 2:
        return None
    if flags & _FLAG_ENCRYPTED_INDEX:
        logfunc(f'ExoPlayer cache index {os.path.basename(os.path.dirname(path))} is encrypted (flag 1) and was not read')
        return None
    offset = 12
    entries = []
    try:
        for _ in range(count):
            entry_id = struct.unpack_from('>i', data, offset)[0]
            offset += 4
            key, offset = _read_utf(data, offset)
            if version < _VERSION_METADATA_INTRODUCED:
                length = struct.unpack_from('>q', data, offset)[0]
                offset += 8
                metadata = {'exo_len': length}
            else:
                metadata, offset = _read_metadata(data, offset)
            entries.append((entry_id, key, metadata))
    except (struct.error, IndexError):
        logfunc(f'ExoPlayer cache index {path} ended early; {len(entries)} of {count} entries read')
    return entries


_USER_VIEWS = (
    re.compile(r'(?:^|/)data/media/(\d+)/Android/data/'),
    re.compile(r'(?:^|/)data/(data)/'),
    re.compile(r'(?:^|/)data/user(?:_de)?/(\d+)/'),
    re.compile(r'(?:^|/)data_mirror/data_[cd]e/null/(\d+)/'),
    re.compile(r'(?:^|/)misc_[cd]e/(\d+)/'),
)


def _container_key(context, file_found, package):
    """The Android user the file belongs to, so an app's internal data folder and its external
    Android/data folder (where some apps keep the cache) group together, and a second user's copy
    stays separate. Storage-view spellings of one folder collapse through canonical_path."""
    relative = context.get_relative_path(file_found).replace('\\', '/')
    for pattern in _USER_VIEWS:
        match = pattern.search(relative)
        if match:
            return 'user:0' if match.group(1) == 'data' else f'user:{match.group(1)}'
    parts = relative.split('/')
    if package in parts:
        parts = parts[:parts.index(package) + 1]
    return canonical_path('/'.join(parts))[0]


def _folder_of(context, file_found, package, folder_pattern):
    """The cache folder (relative, up to and including the folder the pattern names) or None."""
    relative = context.get_relative_path(file_found).replace('\\', '/')
    match = re.search(rf'/{re.escape(package)}/{folder_pattern}(?:/|$)', relative)
    if not match:
        return None
    return relative[:match.end()].rstrip('/')


def _collect(context, package, folder_pattern):
    """{(container key, cache folder): {'index': path, 'spans': [(basename, path, size)], 'dbs': [paths]}}."""
    groups = {}
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        base = os.path.basename(file_found)
        container = _container_key(context, file_found, package)
        if base.startswith('exoplayer_internal.db') and not base.endswith(('-wal', '-shm', '-journal')):
            groups.setdefault((container, 'databases'), {'index': None, 'spans': [], 'dbs': []})['dbs'].append(file_found)
            continue
        folder = _folder_of(context, file_found, package, folder_pattern)
        if folder is None:
            continue
        group = groups.setdefault((container, folder), {'index': None, 'spans': [], 'dbs': []})
        if base == _INDEX_NAME:
            group['index'] = file_found
        elif base.endswith('.exo'):
            try:
                size = os.path.getsize(file_found)
            except OSError:
                size = 0
            group['spans'].append((base, file_found, size))
    return groups


def _spans_by_id(spans):
    """{entry id: [(position, last touch ms, size, path)]} for version-3 span names."""
    by_id = defaultdict(list)
    for base, path, size in spans:
        match = _SPAN_V3.match(base)
        if match:
            by_id[int(match.group(1))].append((int(match.group(2)), int(match.group(3)), size, path))
    return by_id


def _touch_range(spans):
    times = [t for _pos, t, _size, _path in spans]
    return (_utc_millis(min(times)), _utc_millis(max(times))) if times else ('', '')


def _user_of(relative):
    """The Android user a relative path belongs to ('0' for /data/data), or ''."""
    relative = relative.replace('\\', '/')
    for pattern in _USER_VIEWS:
        match = pattern.search(relative)
        if match:
            return '0' if match.group(1) == 'data' else match.group(1)
    return ''


def _users_column(data_list):
    """Blank the last column (Android User) unless the rows name more than one user: on a
    one-user image it would repeat one value on every row."""
    if len({row[-1] for row in data_list}) > 1:
        return data_list
    return [row[:-1] + ('',) for row in data_list]


def _media_by_folder(context, package, key_of):
    """{(user, cache folder below the package, key_of(key)): [records]} for the rejoined
    files of ``package`` that can be shown inline."""
    found = defaultdict(list)
    for rec in shown(rejoined_records(context)):
        if rec.get('app_folder') != package or not shows_media(rec):
            continue
        folder = rec['cache_folder'].split(f'/{package}/', 1)[-1]
        found[(_user_of(rec['cache_folder']), folder, key_of(rec.get('key') or '', rec))].append(rec)
    return found


def _twitter_path(key):
    match = _TWITTER_MEDIA.match(key)
    return f'{match.group(1)}/{match.group(2)}/{match.group(3)}' if match else key.split('?')[0]


@artifact_processor
def twitterCachedVideos(context):
    data_headers = (
        ('First Touched', 'datetime'),
        ('Last Touched', 'datetime'),
        ('Media', 'media'),
        'Media Path (from URL)',
        'Cache Folder',
        'Segments',
        'Span Files',
        'Bytes Cached',
        'Declared Length',
        'Sample URL',
        'Android User',
    )
    data_list = []
    sources = []
    joined = _media_by_folder(context, 'com.twitter.android', lambda key, _rec: _twitter_path(key))
    for (_container, folder), group in sorted(_collect(context, 'com.twitter.android', r'cache/(?:precache|video_cache)').items()):
        if not group['index']:
            continue
        entries = _read_index(group['index'])
        if entries is None:
            continue
        sources.append(group['index'])
        by_id = _spans_by_id(group['spans'])
        media = defaultdict(lambda: {'segments': 0, 'spans': [], 'length': 0, 'sample': ''})
        for entry_id, key, metadata in entries:
            record = media[_twitter_path(key)]
            record['segments'] += 1
            record['spans'] += by_id.get(entry_id, [])
            record['length'] += metadata.get('exo_len') if isinstance(metadata.get('exo_len'), int) else 0
            record['sample'] = record['sample'] or key
        for path, record in sorted(media.items(), key=lambda item: item[1]['spans'] and max(t for _p, t, _s, _f in item[1]['spans']) or 0):
            first, last = _touch_range(record['spans'])
            user = _user_of(folder)
            found = joined.get((user, folder.split('/com.twitter.android/', 1)[-1], path), [])
            data_list.append((
                first, last, media_ref(found[0]) if len(found) == 1 else '',
                path, folder.rsplit('/', 1)[-1], record['segments'], len(record['spans']),
                sum(s for _p, _t, s, _f in record['spans']), record['length'], record['sample'], user,
            ))
    return data_headers, _users_column(data_list), '\n'.join(context.get_relative_path(p) for p in sources)


@artifact_processor
def snapchatStreamedMedia(context):
    data_headers = (
        ('Last Touched', 'datetime'),
        'Content Type (as stored)',
        'Content ID (as stored)',
        'Content Object ID (as stored)',
        'Resolved URL',
        'Cache Key (as stored)',
        'Declared Length',
        'Bytes Cached',
        'Span Files',
        'Android User',
    )
    data_list = []
    sources = []
    for (_container, folder), group in sorted(_collect(context, 'com.snapchat.android', r'files/streaming').items()):
        if not group['index']:
            continue
        entries = _read_index(group['index'])
        if entries is None:
            continue
        sources.append(group['index'])
        by_id = _spans_by_id(group['spans'])
        for entry_id, key, metadata in entries:
            spans = by_id.get(entry_id, [])
            _first, last = _touch_range(spans)
            data_list.append((
                last,
                metadata.get('custom_snap_content_type', ''),
                metadata.get('custom_snap_content_id', ''),
                metadata.get('custom_snap_content_object_id', ''),
                metadata.get('custom_snap_resolved_url', ''),
                key,
                metadata.get('exo_len', ''),
                sum(s for _p, _t, s, _f in spans),
                len(spans),
                _user_of(folder),
            ))
    data_list.sort(key=lambda row: str(row[0]))
    return data_headers, _users_column(data_list), '\n'.join(context.get_relative_path(p) for p in sources)


@artifact_processor
def instagramCachedVideos(context):
    data_headers = (
        ('First Touched', 'datetime'),
        ('Last Touched', 'datetime'),
        ('Media', 'media'),
        'Media ID (from key)',
        'Second ID (from key)',
        'Span Files',
        'Bytes Cached',
        'Sample Key (as stored)',
        'Android User',
    )
    data_list = []
    sources = []
    joined = _media_by_folder(context, 'com.instagram.android', _instagram_video_pair)
    for (_container, folder), group in sorted(_collect(context, 'com.instagram.android', r'cache/ExoPlayerCacheDir/videocache').items()):
        media = defaultdict(lambda: {'spans': [], 'sample': ''})
        for base, path, size in group['spans']:
            match = _SPAN_V2.match(base)
            if not match:
                continue
            key = match.group(1)
            ids = _INSTAGRAM_KEY.match(key)
            pair = (ids.group(1), ids.group(2)) if ids else (key, '')
            record = media[pair]
            record['spans'].append((int(match.group(2)), int(match.group(3)), size, path))
            record['sample'] = record['sample'] or key
            sources.append(path)
        for (media_id, second_id), record in sorted(media.items(), key=lambda item: max(t for _p, t, _s, _f in item[1]['spans'])):
            first, last = _touch_range(record['spans'])
            user = _user_of(folder)
            found = joined.get((user, folder.split('/com.instagram.android/', 1)[-1], (media_id, second_id)), [])
            data_list.append((
                first, last, media_ref(found[0]) if len(found) == 1 else '',
                media_id, second_id, len(record['spans']),
                sum(s for _p, _t, s, _f in record['spans']), record['sample'], user,
            ))
    return data_headers, _users_column(data_list), '\n'.join(context.get_relative_path(p) for p in sources)


def _instagram_video_pair(key, rec):
    """The (media id, second id) pair of a joined Instagram video; an audio file gets no
    pair, so a row's Media is its one video."""
    ids = _INSTAGRAM_KEY.match(key)
    return (ids.group(1), ids.group(2)) if ids and rec.get('kind') == 'video' else None


def _video_id(key):
    match = _REDDIT_VIDEO.match(key or '')
    return match.group(1) if match else (key or '').split('?')[0]


def _reddit_index(db_path):
    """({id: key}, {span name: (length, last touch ms)}) from exoplayer_internal.db, or (None, None)."""
    db = open_sqlite_db_readonly(db_path)
    if db is None:
        return None, None
    keys = {}
    files = {}
    try:
        tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
        for table in tables:
            if table.startswith('ExoPlayerCacheIndex'):
                for entry_id, key in db.execute(f'SELECT id, key FROM "{table}"'):
                    keys[int(entry_id)] = key
            elif table.startswith('ExoPlayerCacheFileMetadata'):
                for name, length, touched in db.execute(f'SELECT name, length, last_touch_timestamp FROM "{table}"'):
                    files[name] = (length, touched)
    except sqlite3.Error as error:
        logfunc(f'Reddit exoplayer_internal.db: {error}')
    db.close()
    return keys, files


@artifact_processor
def redditCachedVideos(context):
    data_headers = (
        ('First Touched', 'datetime'),
        ('Last Touched', 'datetime'),
        ('Media', 'media'),
        'Video ID (from URL)',
        'Segments',
        'Span Files',
        'Bytes Cached',
        'Sample URL',
        'Android User',
    )
    data_list = []
    sources = []
    groups = _collect(context, 'com.reddit.frontpage', r'cache/reddit-video')
    # the rejoined media for each video id, per Android user; a row shows it only when
    # exactly one file carries that id, since picking among several would be a guess
    media = defaultdict(list)
    for (user, _folder, video), recs in _media_by_folder(
            context, 'com.reddit.frontpage', lambda key, _rec: _video_id(key)).items():
        media[(user, video)] += recs
    by_container = defaultdict(lambda: {'dbs': [], 'spans': []})
    for (container, _folder), group in groups.items():
        by_container[container]['dbs'] += group['dbs']
        by_container[container]['spans'] += group['spans']
    for container, group in sorted(by_container.items()):
        for db_path in group['dbs']:
            keys, files = _reddit_index(db_path)
            if keys is None:
                continue
            sources.append(db_path)
            by_id = defaultdict(list)
            for base, path, size in group['spans']:
                match = _SPAN_V3.match(base)
                if match:
                    length, touched = files.get(base, (size, int(match.group(3))))
                    by_id[int(match.group(1))].append((int(match.group(2)), touched, length, path))
            videos = defaultdict(lambda: {'segments': 0, 'spans': [], 'sample': ''})
            for entry_id, key in keys.items():
                record = videos[_video_id(key)]
                record['segments'] += 1
                record['spans'] += by_id.get(entry_id, [])
                record['sample'] = record['sample'] or key
            for video, record in sorted(videos.items(), key=lambda item: item[1]['spans'] and max(t for _p, t, _s, _f in item[1]['spans']) or 0):
                first, last = _touch_range(record['spans'])
                user = _user_of(context.get_relative_path(db_path))
                found = media.get((user, video), [])
                data_list.append((
                    first, last, media_ref(found[0]) if len(found) == 1 else '',
                    video, record['segments'], len(record['spans']),
                    sum(s for _p, _t, s, _f in record['spans']), record['sample'], user,
                ))
    return data_headers, _users_column(data_list), '\n'.join(context.get_relative_path(p) for p in sources)
