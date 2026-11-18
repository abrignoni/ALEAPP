__artifacts_v2__ = {
    "spotify_store_recently_played": {
        "name": "Spotify - Recently Played (Store)",
        "description": "Item addresses (tracks, episodes, playlists, albums, artists, shows) "
                       "that the Spotify app's own LevelDB store holds under keys beginning "
                       "!rp#trk#, !rp#ctx# and !yl#rpp#, with the integer each record stores "
                       "beside the address.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Spotify",
        "notes": "Ported from iLEAPP's spotify.py, which reads the same store and key "
                 "families on iOS. One row per distinct key, integer and record state among "
                 "the keys beginning !rp#trk#, !rp#ctx# or !yl#rpp# in "
                 "files/spotifycache/Users/<account>-user/primary.ldb under "
                 "Android/data/com.spotify.music, read with the vendored ccl_leveldb. Every "
                 "record is read, superseded ones included, because the store rewrites an "
                 "entry rather than editing it and an older record can carry an earlier "
                 "integer (11 keys on 5 tested images hold more than one); records repeating "
                 "a key, an integer and a state are counted once. Reading these keys as "
                 "recently played comes from the key names; no source for them is cited. "
                 "'Candidate Time Integer (as stored)' is the first top-level integer field "
                 "of the record that falls in the range of Unix seconds from 2008 to 2036, "
                 "found by value and not by field number, and reported without conversion "
                 "because what it records is not established; on the tested images it was "
                 "field 2 in every record that had one. On dragna_pixel9a_a16 it was compared"
                 " with the Played At times in Spotify - Recently Played (the app's cached "
                 "copy of a server response): its 11 entries are 8 distinct track and time "
                 "pairs, 6 of those name a track this store lists, and read as Unix seconds "
                 "the store's integer was 3 s to 87 min earlier than Played At on 5 and 13.7 "
                 "days later on 1, so it is not the same value. 'Item URI' is the address in "
                 "the record, or the one in the key when the record holds none (the Deleted "
                 "row). 'Item Type' comes from the address. 'Key Prefix (as stored)' is the "
                 "first 8 bytes of the key. 'Account' is the per-user folder name without its"
                 " -user suffix. On 3 of the 12 tested images the same storage is also under "
                 "/mnt/pass_through/<n>/emulated/<user>/ beside /data/media/<user>/; those "
                 "paths are read as one store, with the records of every copy combined (on "
                 "russell_a14 the two copies differ). Views that storagePathViews collapses "
                 "(data_mirror) are read once. 'Record State' was Live on every row of the "
                 "tested images but one, a Deleted !rp#ctx# record on kevin_pocox7_a15 whose "
                 "integer is blank, and 'Account' held one value per image. Most records in "
                 "the same store are under !xmeta#cache and !xmeta#cinfo keys that name "
                 "track, episode, album, artist, playlist, image, audio and user addresses; "
                 "those, and the !pl#, !playx#, !yltags#, !res# and !cit# keys, are not "
                 "reported, and what they hold was not established. A row shows the store "
                 "listed the item under one of these keys; it does not establish who played "
                 "it or that it was played on this device.",
        "paths": ('*/com.spotify.music/files/spotifycache/Users/*',),
        "output_types": "standard",
        "artifact_icon": "play-circle",
        "sample_data": {
            "anne_a15": "Android 15 | com.spotify.music | 8 rows",
            "cookbook_a11": "Android 11 | com.spotify.music | 0 rows",
            "dragna_pixel9a_a16": "Android 16 | com.spotify.music versionCode 147078674 | 107 rows",
            "galaxys10_a10": "Android 10 | com.spotify.music | 60 rows",
            "hickman_a13": "Android 13 | com.spotify.music | 65 rows",
            "kevin_pocox7_a15": "Android 15 | com.spotify.music | 161 rows",
            "pixel3_a11": "Android 11 | com.spotify.music | 16 rows",
            "pixel3_a12": "Android 12 | com.spotify.music | 134 rows",
            "pixel7a_a14": "Android 14 | com.spotify.music | 19 rows",
            "russell_a14": "Android 14 | com.spotify.music | 119 rows",
            "russell_pixel6a_a13": "Android 13 | com.spotify.music | 118 rows",
            "samsungs20_a13": "Android 13 | com.spotify.music | 36 rows",
        },
    },
    "spotify_store_saved_items": {
        "name": "Spotify - Saved and Offline Items",
        "description": "Item addresses the Spotify app's LevelDB store holds under keys "
                       "beginning !col# and !xmeta#offlkeys#, each labelled with the key "
                       "prefix as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Spotify",
        "notes": "Ported from iLEAPP's spotify.py. One row per key beginning !col# or "
                 "!xmeta#offlkeys#, newest record per key, in the same store as Spotify - "
                 "Recently Played (Store), when the record or key holds an address. 'Key "
                 "Prefix (as stored)' is the key up to its second #, so the second part is "
                 "shown (art, col, show, ylpin, later, lban and col.albtrk on the tested "
                 "images). Keys whose second part has a dot (art.ar, show.sh, later.ar, "
                 "col.trk, col.alb, col.albtrk on the tested images) give a row only for an "
                 "address no other row of the store lists, so an item is counted once: on "
                 "kevin_pocox7_a15 that adds 66 col.albtrk rows, and on the other images the "
                 "dotted keys named no new address. Reading the keys as a saved collection "
                 "and as offline items comes from the key names; no source for them is cited."
                 " 'Candidate Time Integer (as stored)' is found as in that artifact, and is "
                 "blank on !xmeta#offlkeys# rows, which the module reads no integer from. "
                 "'Item Type' comes from the address and is blank when the address names the "
                 "collection itself. Copies of the store under several storage paths are "
                 "combined, the record with the highest sequence number winning. On the 11 "
                 "tested images with rows 'Record State' held Live on every row and 'Account'"
                 " held one value per image. No !xmeta#offlkeys# key was present on any of "
                 "the 12, so that branch is unexercised on Android.",
        "paths": ('*/com.spotify.music/files/spotifycache/Users/*',),
        "output_types": "standard",
        "artifact_icon": "download",
        "sample_data": {
            "anne_a15": "Android 15 | com.spotify.music | 2 rows",
            "cookbook_a11": "Android 11 | com.spotify.music | 4 rows",
            "dragna_pixel9a_a16": "Android 16 | com.spotify.music versionCode 147078674 | 75 rows",
            "galaxys10_a10": "Android 10 | com.spotify.music | 0 rows",
            "hickman_a13": "Android 13 | com.spotify.music | 17 rows",
            "kevin_pocox7_a15": "Android 15 | com.spotify.music | 138 rows",
            "pixel3_a11": "Android 11 | com.spotify.music | 1 row",
            "pixel3_a12": "Android 12 | com.spotify.music | 17 rows",
            "pixel7a_a14": "Android 14 | com.spotify.music | 70 rows",
            "russell_a14": "Android 14 | com.spotify.music | 93 rows",
            "russell_pixel6a_a13": "Android 13 | com.spotify.music | 93 rows",
            "samsungs20_a13": "Android 13 | com.spotify.music | 12 rows",
        },
    },
    "spotify_store_player_state": {
        "name": "Spotify - Player State",
        "description": "The track, position, flags and times held in the Spotify app's saved "
                       "player state file. A file with no track still gives a row.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Spotify",
        "notes": "Ported from iLEAPP's spotify.py. One row per "
                 "files/spotifycache/Users/<account>-user/context_player_state_restore, "
                 "copies with identical bytes under several storage paths counted once. "
                 "'State Saved' is the number the file begins with (the digits before the "
                 "first #), read as Unix milliseconds, UTC; that reading is not sourced. "
                 "'Playback Reported' is the time inside the saved playback block: 16 digits "
                 "in the JSON form, read as microseconds, and 13 in the protobuf form, read "
                 "as milliseconds, Unix, UTC, not sourced; on the tested images it was equal "
                 "to State Saved or up to 24 minutes later. The file holds JSON on 3 tested "
                 "images (saved in 2020 and 2021) and a protobuf on 9 (saved 2022 to 2026). "
                 "No schema for the protobuf is cited, so the track is found by shape: the "
                 "first message, searched depth first, that has a child carrying a Spotify "
                 "track address. Its time, position and duration come from a sibling block "
                 "whose field 1 is a millisecond time, when there is one; 'Position (as "
                 "stored)' and 'Duration (as stored)' are fields 2 and 3 of that block, blank"
                 " when absent (field 3 is absent on samsungs20_a13), and in the JSON form "
                 "the playback block's own values, with Duration falling back to the duration"
                 " in the track's metadata. Their unit is not sourced. That this is the "
                 "playing track is the module's reading. 'Album', 'Album URI', 'Artist URI', "
                 "'Title', 'Artist' and 'Played From URI' come from the file's own metadata "
                 "keys (album_title, album_uri, artist_uri, title, artist_name, context_uri);"
                 " 'Played From URI' uses play_origin.view_uri in the JSON form when "
                 "context_uri is absent. 'App Version' is play_origin.feature_version in the "
                 "JSON form and the first four-part dotted number found anywhere in the "
                 "protobuf form; what the string marks is not established, and it is not a "
                 "reading of the installed version; it was filled on 3 of the 11 rows. 'Playing', 'Paused', 'Shuffle', 'Repeat "
                 "Context' and 'Repeat Track' are read only from the JSON form and are blank "
                 "in the protobuf form, which does not mean a setting was off; two JSON rows "
                 "(galaxys10_a10, pixel3_a12) read Yes for both Playing and Paused, and what "
                 "that combination means is not established. On pixel3_a11 the JSON file "
                 "holds no track, so Track URI is blank on its row. On dragna_pixel9a_a16 the"
                 " file is the protobuf form, so those five held no value, and 'Artist' held "
                 "no value. On russell_a14 the file holds no track address (only album and "
                 "station addresses), so it gives no row and the run log says the playing "
                 "track was not found. The file can hold other track addresses (up to 88 on "
                 "the tested images); in the JSON form they sit under play_history and "
                 "play_queue. None of them is reported.",
        "paths": ('*/com.spotify.music/files/spotifycache/Users/*',),
        "output_types": "standard",
        "artifact_icon": "music",
        "sample_data": {
            "anne_a15": "Android 15 | com.spotify.music | 1 row",
            "cookbook_a11": "Android 11 | com.spotify.music | 1 row",
            "dragna_pixel9a_a16": "Android 16 | com.spotify.music versionCode 147078674 | 1 row",
            "galaxys10_a10": "Android 10 | com.spotify.music | 1 row",
            "hickman_a13": "Android 13 | com.spotify.music | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.spotify.music | 1 row",
            "pixel3_a11": "Android 11 | com.spotify.music | 1 row",
            "pixel3_a12": "Android 12 | com.spotify.music | 1 row",
            "pixel7a_a14": "Android 14 | com.spotify.music | 1 row",
            "russell_a14": "Android 14 | com.spotify.music | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.spotify.music | 1 row",
            "samsungs20_a13": "Android 13 | com.spotify.music | 1 row",
        },
    },
}

import hashlib
import json
import os
import pathlib
import re
from datetime import datetime, timedelta, timezone

from scripts.artifacts.storagePathViews import canonical_path, unique_files
from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.vendor.ccl import ccl_leveldb

_UNIX_EPOCH_UTC = datetime(1970, 1, 1, tzinfo=timezone.utc)
_USER_DIR = re.compile(
    r'^(?P<pre>.*)/com\.spotify\.music/files/spotifycache/Users/(?P<acct>[^/]+?)-user/(?P<rest>.+)$')
# /mnt/pass_through/<n>/emulated/<user>/ is another view of /data/media/<user>/ (as in
# exoplayerCachedMedia.py).
_PASS_THROUGH = re.compile(r'(^|/)mnt/pass_through/\d+/emulated/(\d+)/')
_RECENTLY_PLAYED = (b'!rp#trk#', b'!rp#ctx#', b'!yl#rpp#')
_COLLECTION = b'!col#'
_OFFLINE = b'!xmeta#offlkeys#'
_LEVELDB_ERRORS = (OSError, ValueError, KeyError, IndexError, EOFError)


def _store_key(relative):
    """(storage key, account, part under the account folder), or None."""
    path = str(relative).replace('\\', '/')
    path = _PASS_THROUGH.sub(lambda m: f'{m.group(1)}data/media/{m.group(2)}/', path)
    match = _USER_DIR.match(path)
    if not match:
        return None
    key, _rank = canonical_path(match.group('pre') + '/')
    return key, match.group('acct'), match.group('rest')


def _stores(context):
    """{(storage key, account): {'ldb': [dirs], 'state': [files]}} with every view kept."""
    stores = {}
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        parts = _store_key(context.get_relative_path(file_found))
        if not parts:
            continue
        key, account, rest = parts
        entry = stores.setdefault((key, account), {'ldb': [], 'state': [], 'account': account})
        if rest.startswith('primary.ldb/'):
            directory = os.path.dirname(file_found)
            if directory not in entry['ldb']:
                entry['ldb'].append(directory)
        elif rest == 'context_player_state_restore':
            entry['state'].append(file_found)
    return stores


def _text(value):
    return '' if value is None else str(value)


def _unix_to_utc(value):
    if value in (None, '', 0):
        return ''
    try:
        return _UNIX_EPOCH_UTC + timedelta(seconds=float(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _varint(data, offset):
    number, shift = 0, 0
    while offset < len(data):
        byte = data[offset]
        number |= (byte & 0x7f) << shift
        shift += 7
        offset += 1
        if not byte & 0x80:
            return number, offset
        if shift > 63:
            return None, offset
    return None, offset


def _field_list(data, start=0, end=None):
    """Every protobuf field between two offsets, or None when the bytes do not parse."""
    end = len(data) if end is None else end
    out, offset = [], start
    while offset < end:
        tag, offset = _varint(data, offset)
        if tag is None or tag >> 3 == 0:
            return None
        number, wire = tag >> 3, tag & 7
        if wire == 2:
            length, offset = _varint(data, offset)
            if length is None or offset + length > end:
                return None
            out.append((number, data[offset:offset + length]))
            offset += length
        elif wire == 0:
            value, offset = _varint(data, offset)
            if value is None:
                return None
            out.append((number, value))
        elif wire == 5:
            offset += 4
            out.append((number, None))
        elif wire == 1:
            offset += 8
            out.append((number, None))
        else:
            return None
    return out


def _uri_and_time(value):
    """The item address and the candidate time a store record holds, by what each field holds."""
    uri, stamp = '', None
    for _, item in (_field_list(value) or []):
        if isinstance(item, bytes) and item.startswith(b'spotify:') and not uri:
            uri = item.decode('utf8', 'replace')
        elif isinstance(item, int) and stamp is None and 1_200_000_000 < item < 2_100_000_000:
            stamp = item
    return uri, stamp


def _uri_from_key(key):
    match = re.search(rb'(spotify:[a-z]+:[0-9A-Za-z]+)', key)
    return match.group(1).decode() if match else ''


def _item_type(uri):
    parts = uri.split(':')
    return parts[1].title() if len(parts) > 2 and parts[0] == 'spotify' else ''


def _records(directories):
    """Every record of every copy of one LevelDB, as [(key, seq, state, value)]."""
    out = []
    for directory in directories:
        try:
            database = ccl_leveldb.RawLevelDb(pathlib.Path(directory))
        except _LEVELDB_ERRORS as error:
            logfunc(f'Spotify: could not open a primary.ldb copy: {type(error).__name__}')
            continue
        try:
            for record in database.iterate_records_raw():
                out.append((bytes(record.user_key), record.seq,
                            str(record.state).rsplit('.', 1)[-1], bytes(record.value)))
        except _LEVELDB_ERRORS as error:
            logfunc(f'Spotify: could not read all of a primary.ldb copy: {type(error).__name__}')
        finally:
            database.close()
    return out


def _app_version(blob):
    match = re.search(rb'\b(\d+\.\d+\.\d+\.\d+)\b', blob)
    return match.group(1).decode() if match else ''


def _pairs(blob):
    """The key and value strings a repeated pair message carries, named by the file itself."""
    out = {}
    for _, item in (_field_list(blob) or []):
        if not isinstance(item, bytes):
            continue
        pair = _field_list(item) or []
        if len(pair) == 2 and all(isinstance(part, bytes) for _, part in pair):
            out[pair[0][1].decode('utf8', 'replace')] = pair[1][1].decode('utf8', 'replace')
    return out


def _protobuf_state(blob, depth=0):
    """The playing track a protobuf saved state carries, found by shape, or None."""
    parsed = _field_list(blob)
    if parsed is None or depth > 8:
        return None
    track, meta = '', {}
    for _, item in parsed:
        if not isinstance(item, bytes):
            continue
        inner = _field_list(item)
        if inner is None:
            continue
        for _, value in inner:
            if isinstance(value, bytes) and value.startswith(b'spotify:track:'):
                track = value.decode('utf8', 'replace')
        if track:
            meta = _pairs(item)
            break
    if track:
        playback = {}
        for _, item in parsed:
            if not isinstance(item, bytes):
                continue
            fields = {}
            for number, value in (_field_list(item) or []):
                if isinstance(value, int):
                    fields.setdefault(number, value)
            first = fields.get(1)
            if first is not None and 1_200_000_000_000 < first < 2_100_000_000_000 \
                    and len(fields) >= 2:
                playback = {'timestamp': first * 1000, 'position': fields.get(2),
                            'duration': fields.get(3)}
                break
        return {'track': track, 'meta': meta, 'playback': playback}
    for _, item in parsed:
        if isinstance(item, bytes) and len(item) > 8:
            found = _protobuf_state(item, depth + 1)
            if found:
                return found
    return None


def _player_state(path):
    """(saved seconds, the saved state) from one context_player_state_restore, or None."""
    try:
        with open(path, 'rb') as handle:
            raw = handle.read()
    except OSError as error:
        logfunc(f'Spotify: could not read a saved player state: {type(error).__name__}')
        return None
    stamp, _, body = raw.partition(b'#')
    saved = int(stamp) / 1000 if stamp.isdigit() else None
    if body[:1] == b'{':
        try:
            return saved, json.loads(body.decode('utf8', 'replace')), raw
        except ValueError:
            logfunc('Spotify: could not read a saved player state in JSON form')
            return None
    found = _protobuf_state(body)
    if not found:
        logfunc('Spotify: could not find the playing track in a saved player state')
        return None
    state = {'player_model': {'session_queue': {'active': {
        'track': {'uri': found['track'], 'metadata': {'overrides': found['meta']}},
        'playback_state': found['playback'],
        'play_origin': {'view_uri': found['meta'].get('context_uri', ''),
                        'feature_version': _app_version(body)}}}}}
    return saved, state, raw


def _flag(holder, key):
    if not isinstance(holder, dict) or key not in holder or holder[key] is None:
        return ''
    return 'Yes' if holder[key] else 'No'


def _sources(context, paths):
    return '\n'.join(sorted({context.get_relative_path(path) for path in paths}))


@artifact_processor
def spotify_store_recently_played(context):
    data_headers = ('Candidate Time Integer (as stored)', 'Item Type', 'Item URI',
                    'Key Prefix (as stored)', 'Record State', 'Account')
    data_list, sources = [], []
    for store in _stores(context).values():
        if not store['ldb']:
            continue
        sources.extend(os.path.join(d, 'CURRENT') for d in store['ldb'])
        seen = set()
        for key, _seq, state, value in _records(store['ldb']):
            if not key.startswith(_RECENTLY_PLAYED):
                continue
            uri, stamp = _uri_and_time(value)
            uri = uri or _uri_from_key(key)
            if (key, stamp, state) in seen:
                continue
            seen.add((key, stamp, state))
            data_list.append((_text(stamp), _item_type(uri), uri, key[:8].decode(),
                              state, store['account']))
    sources = [p for p in sources if os.path.exists(p)]
    return data_headers, data_list, _sources(context, sources)


@artifact_processor
def spotify_store_saved_items(context):
    data_headers = ('Candidate Time Integer (as stored)', 'Key Prefix (as stored)', 'Item Type',
                    'Item URI', 'Record State', 'Account')
    data_list, sources = [], []
    for store in _stores(context).values():
        if not store['ldb']:
            continue
        sources.extend(os.path.join(d, 'CURRENT') for d in store['ldb'])
        latest = {}
        for key, seq, state, value in _records(store['ldb']):
            if key not in latest or seq > latest[key][0]:
                latest[key] = (seq, state, value)
        plain, dotted = [], []
        for key, (_seq, state, value) in sorted(latest.items()):
            if key.startswith(_COLLECTION):
                uri, stamp = _uri_and_time(value)
                uri = uri or _uri_from_key(key)
                part = key.split(b'#')[1]
                kind = (_COLLECTION + part + b'#').decode('utf8', 'replace')
                (dotted if b'.' in part else plain).append((stamp, kind, uri, state))
            elif key.startswith(_OFFLINE):
                plain.append((None, _OFFLINE.decode(), _uri_from_key(key), state))
        listed = {uri for _, _, uri, _ in plain}
        for stamp, kind, uri, state in plain + [row for row in dotted if row[2] not in listed]:
            if not uri:
                continue
            listed.add(uri)
            data_list.append((_text(stamp), kind, _item_type(uri), uri, state, store['account']))
    sources = [p for p in sources if os.path.exists(p)]
    return data_headers, data_list, _sources(context, sources)


@artifact_processor
def spotify_store_player_state(context):
    data_headers = (
        ('State Saved', 'datetime'), ('Playback Reported', 'datetime'), 'Title', 'Artist',
        'Album', 'Track URI', 'Played From URI', 'Position (as stored)', 'Duration (as stored)',
        'Playing', 'Paused', 'Shuffle', 'Repeat Context', 'Repeat Track', 'App Version',
        'Album URI', 'Artist URI', 'Account')
    data_list, sources = [], []
    for store in _stores(context).values():
        seen = set()
        for path in store['state']:
            parsed = _player_state(path)
            if not parsed:
                continue
            saved, state, raw = parsed
            digest = hashlib.sha256(raw).hexdigest()
            if digest in seen:
                continue
            seen.add(digest)
            sources.append(path)
            model = state.get('player_model', {}) if isinstance(state, dict) else {}
            active = (model.get('session_queue', {}) or {}).get('active', {}) or {}
            track = active.get('track', {}) or {}
            meta = (track.get('metadata', {}) or {}).get('overrides', {}) or {}
            playback = active.get('playback_state', {}) or {}
            origin = active.get('play_origin', {}) or {}
            options = model.get('options', {}) or {}
            stamp = playback.get('timestamp')
            data_list.append((
                _unix_to_utc(saved),
                _unix_to_utc(stamp / 1_000_000) if isinstance(stamp, (int, float)) and stamp else '',
                _text(meta.get('title')), _text(meta.get('artist_name')),
                _text(meta.get('album_title')), _text(track.get('uri')),
                _text(meta.get('context_uri') or origin.get('view_uri')),
                _text(playback.get('position')),
                _text(playback.get('duration') or meta.get('duration')),
                _flag(active, 'is_playing'), _flag(active, 'is_paused'),
                _flag(options, 'shuffling_context'), _flag(options, 'repeating_context'),
                _flag(options, 'repeating_track'), _text(origin.get('feature_version')),
                _text(meta.get('album_uri')), _text(meta.get('artist_uri')), store['account'],
            ))
    return data_headers, data_list, _sources(context, sources)
