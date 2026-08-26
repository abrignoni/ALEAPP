__artifacts_v2__ = {
    "spotify_account": {
        "name": "Spotify - Account",
        "description": "The signed-in Spotify account's canonical identifiers, sign-in "
                       "method, selected language and the app's own first-launch time, "
                       "read from the app's main preferences file.",
        "author": "@Gear-I, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-25",
        "requirements": "none",
        "category": "Spotify",
        "notes": "Spotify does not store the account's email address or display name "
                 "anywhere on disk in this extraction confirmed by searching each "
                 "file under the app's data directory, including shared_prefs and the "
                 "per-user settings folder, for both. What is recoverable is the "
                 "account's canonical username (a fixed opaque ID Spotify assigns at "
                 "signup, exposed here as both 'crashlytics_user_id' and "
                 "'event-sender-event-owner', which agree) and that the sign-in method "
                 "was email/password rather than a linked Facebook/Google/Apple "
                 "account. 'App First Launch Time' is when Spotify's preferences were "
                 "first written on this device, which is a reasonable proxy for "
                 "install/first-run time but is not itself an install timestamp from "
                 "the OS or Play Store.",
        "paths": ('*/com.spotify.music/shared_prefs/spotify_preferences.xml',),
        "output_types": ["standard"],
        "artifact_icon": "user",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.spotify.music | 1 row",
        },
    },
    "spotify_playlist_library": {
        "name": "Spotify - Playlist Library Activity",
        "description": "Playlists Spotify's own local usage-tracking file has a "
                       "record for, with the time each one was first interacted with "
                       "and a snapshot of two internal usage counters recorded "
                       "whenever that snapshot changed.",
        "author": "@Gear-I, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-25",
        "requirements": "none",
        "category": "Spotify",
        "notes": "Source is frecency.pb, a per-account file Spotify uses to rank "
                 "'frequent and recent' content; it is not a public format, so this was "
                 "reverse engineered directly against this device's real data rather "
                 "than any documentation. A device with more than one Spotify account "
                 "signed in holds one of these files per account and every one of them "
                 "is read; 'Account Folder' is the name of the per-account directory a "
                 "row's file sits in, reported as stored. On the device this was "
                 "validated against that name is the account's canonical username "
                 "followed by '-user', so it lines up with the Canonical Username "
                 "column of Spotify - Account. Each playlist can appear more than once: "
                 "Spotify appends a new snapshot each time the two counters change, "
                 "so a playlist with several rows shows its usage growing over time, "
                 "and the earliest row's time is effectively when it was first added. "
                 "'Counter A' and 'Counter B' are reported as raw integers because "
                 "their exact meaning (e.g. play count vs. skip count vs. a weighted "
                 "frecency score) could not be confirmed - but they are real values "
                 "that grow with real use: on the device this was validated against, "
                 "one playlist's Counter A went from 1 to 21 and Counter B from 1 to 4 "
                 "across two snapshots roughly six months apart. The large opaque "
                 "integer Spotify stores alongside each snapshot is not included: it "
                 "did not decode to anything recognizable (not a timestamp, not a "
                 "count) and is most likely an internal hash or sort key. This file "
                 "only covers playlists Spotify's frecency tracker has touched; a "
                 "playlist added to the Library but never opened or shuffled again may "
                 "not appear here even though it exists elsewhere on the account.",
        "paths": ('*/com.spotify.music/files/settings/Users/*/frecency.pb',),
        "output_types": ["standard"],
        "artifact_icon": "playlist",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.spotify.music | 3 rows",
        },
    },
    "spotify_playback_activity": {
        "name": "Spotify - Playback Activity",
        "description": "Playback-related events recovered from Spotify's own local "
                       "telemetry log: tracks played, playlists involved in an "
                       "Android Auto session, and whether a session was playing from a "
                       "downloaded local copy rather than streaming.",
        "author": "@Gear-I, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-25",
        "requirements": "none",
        "category": "Spotify",
        "notes": "Source is event-sender.db's Events table, an internal analytics log "
                 "Spotify's client keeps of its own activity; each row's 'fragments' "
                 "column is a schema-less protobuf blob decoded the same way this "
                 "project already decodes undocumented protobuf elsewhere (see "
                 "YouTube.py). The table holds 58 distinct event types on the device "
                 "this was validated against, most of them pure app diagnostics (ad "
                 "errors, cache reports, connection state, audio driver info) with no "
                 "forensic value; this artifact reports only the handful of event "
                 "types confirmed to carry real user-facing content when decoded: "
                 "PlaybackSegments and BoomboxPlaybackSession (a track was played), "
                 "CorePlaybackFinished (a playback session ended), Download (a track "
                 "or playlist download was initiated), AudioFileSelection (what file "
                 "source, e.g. a local offline copy, played audio came from), and "
                 "TrackNotPlayed (a queued track did not play, seen on this device "
                 "only in an Android Auto context). 'Content URI' is populated only "
                 "when the event's decoded fields contained a literal spotify:track:* "
                 "or spotify:playlist:* string; 'Session ID' is an opaque hexadecimal "
                 "value Spotify's own client reuses across the events that belong to "
                 "the same playback session, included so related rows (e.g. a "
                 "Download and the PlaybackSegments rows it fed) can be grouped, not "
                 "because its own meaning is known. 'Notes' surfaces other short "
                 "decoded string fields verbatim (e.g. 'offlined file', 'android-auto', "
                 "'logout') without interpretation; some of what lands there is an "
                 "opaque identifier rather than readable status text, and those are "
                 "reported as stored. Purely numeric fields (byte counts, bitrates, "
                 "internal enum values) are not reported, since there is no public "
                 "schema to confirm what they mean. Where an extraction carries the "
                 "app's data directory more than once, the duplicate storage views of "
                 "one file are collapsed and each genuinely separate copy is read, so "
                 "a second Android user's events are reported alongside the first "
                 "user's with no column separating them; the source paths listed for "
                 "the artifact name every database the rows came from.",
        "paths": ('*/com.spotify.music/databases/event-sender.db*',),
        "output_types": ["standard"],
        "artifact_icon": "player-play",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.spotify.music | 28 rows",
        },
    },
    "spotify_recently_played": {
        "name": "Spotify - Recently Played",
        "description": "Tracks recovered from Spotify's own cached response to its "
                       "'recently played' API call, each with the real timestamp "
                       "Spotify's server recorded for when it was played and the "
                       "playlist it was played from.",
        "author": "@Gear-I, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-25",
        "requirements": "none",
        "category": "Spotify",
        "notes": "Source is the app's HTTP disk cache (cache/http-cache), specifically "
                 "a cached response from the recently-played/v3 endpoint; the response "
                 "body is schema-less protobuf, decoded the same way this project "
                 "already decodes undocumented protobuf elsewhere. 'Played At' is a "
                 "millisecond timestamp embedded directly in that response by "
                 "Spotify's own server, not derived from any local file time. This "
                 "endpoint is requested with a limit of 50 entries, but the cached "
                 "response on the device this was validated against held only one - "
                 "the app's local HTTP cache only ever holds the most recent response "
                 "to a given request URL, so this reflects whatever this list looked "
                 "like the last time the app asked, not a full play history. It should "
                 "be read alongside Spotify - Playback Activity and Spotify - Now "
                 "Playing View, which recover different, independent evidence of "
                 "playback from other local sources.",
        "paths": ('*/com.spotify.music/cache/http-cache/*',),
        "output_types": ["standard"],
        "artifact_icon": "clock",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.spotify.music | 1 row",
        },
    },
    "spotify_now_playing_view": {
        "name": "Spotify - Now Playing View",
        "description": "Tracks recovered from cached responses to the lyrics and "
                       "merchandise API calls Spotify's app makes for whatever track "
                       "is showing on its Now Playing screen, with the first cached "
                       "lyric line for each track.",
        "author": "@Gear-I, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-25",
        "requirements": "none",
        "category": "Spotify",
        "notes": "Source is the app's HTTP disk cache (cache/http-cache): the "
                 "color-lyrics/v2 endpoint, requested for the track on the Now "
                 "Playing screen, and the merch-npv-service/v1 endpoint, requested "
                 "for the same track to populate a merchandise carousel below it. "
                 "The Spotify track ID is read directly from each cached request's "
                 "URL, not guessed at. 'First Lyric Line' is the first line of the "
                 "time-synced lyrics decoded from the cached response body (also "
                 "schema-less protobuf) - it is included, verbatim and without "
                 "interpretation, because it is a real piece of the track's own "
                 "lyrics recoverable from the device and is enough for an examiner "
                 "to identify the song; this project does not maintain a "
                 "track-ID-to-song-name lookup table, since one built from a single "
                 "device would not generalise to any other extraction. 'Response "
                 "Received Time' comes from OkHttp-Received-Millis, a pseudo-header "
                 "OkHttp's own disk cache writes into each cached entry's own "
                 "metadata recording when the client received that response. Unlike "
                 "a filesystem modification time, this value is baked into the "
                 "cached data itself, so it does not change when the evidence is "
                 "re-staged or copied elsewhere, which is what lets this artifact be "
                 "regression-tested. It is a reasonable proxy for when the track was "
                 "on screen but is not itself a playback timestamp. Left blank on any "
                 "entry where that pseudo-header is absent, rather than falling back "
                 "to a filesystem time.",
        "paths": ('*/com.spotify.music/cache/http-cache/*',),
        "output_types": ["standard"],
        "artifact_icon": "microphone",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.spotify.music | 4 rows",
        },
    },
    "spotify_artist_profile_views": {
        "name": "Spotify - Artist Profile Views",
        "description": "Artists recovered from cached responses to the API call "
                       "Spotify's app makes when an artist's profile page is opened, "
                       "with the artist's name and canonical URI as Spotify's own "
                       "server returned them.",
        "author": "@Gear-I, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-25",
        "requirements": "none",
        "category": "Spotify",
        "notes": "Source is the app's HTTP disk cache (cache/http-cache), "
                 "specifically cached responses from the artist-identity-view/v2 "
                 "endpoint, which the app calls when a user opens an artist's "
                 "profile page; the response is plain JSON and 'Artist Name' / "
                 "'Artist URI' are read directly from its own 'name' and "
                 "'artistUri' fields. 'Response Received Time' comes from "
                 "OkHttp-Received-Millis, a pseudo-header OkHttp's own disk cache "
                 "writes into each cached entry's own metadata recording when the "
                 "client received that response. Unlike a filesystem modification "
                 "time, this value is baked into the cached data itself, so it does "
                 "not change when the evidence is re-staged or copied elsewhere, "
                 "which is what lets this artifact be regression-tested. It is a "
                 "reasonable proxy for when the page was opened but is not itself "
                 "confirmation of how long the page was viewed or that each track by "
                 "that artist was played. Left blank on any entry where that "
                 "pseudo-header is absent, rather than falling back to a filesystem "
                 "time.",
        "paths": ('*/com.spotify.music/cache/http-cache/*',),
        "output_types": ["standard"],
        "artifact_icon": "user-circle",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.spotify.music | 4 rows",
        },
    },
}

import gzip
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import unique_files
from scripts.blackboxprotobuf import decode_message
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, logfunc

_URI_RE = re.compile(r'^spotify:(track|playlist|album|artist|show|episode):[A-Za-z0-9]+$')
_HEX_ID_RE = re.compile(r'^[0-9a-f]{32,44}$')
_INVALID_XML_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')

_PLAYBACK_EVENT_NAMES = (
    "PlaybackSegments", "BoomboxPlaybackSession", "CorePlaybackFinished",
    "Download", "AudioFileSelection", "TrackNotPlayed",
)

_RECENTLY_PLAYED_RE = re.compile(r'/recently-played/v3/')
_LYRICS_TRACK_RE = re.compile(r'/color-lyrics/v2/track/([A-Za-z0-9]+)')
_MERCH_TRACK_RE = re.compile(r'/merch-npv-service/v1/merch/track/([A-Za-z0-9]+)')
_ARTIST_VIEW_RE = re.compile(r'/artist-identity-view/v2/profile/spotify:artist:')
_ACCOUNT_DIR_RE = re.compile(r'/files/settings/Users/([^/]+)/frecency\.pb$')
_OKHTTP_RECEIVED_MILLIS_RE = re.compile(
    r'^OkHttp-Received-Millis:\s*(\d+)\s*$', re.MULTILINE | re.IGNORECASE,
)


def _parse_xml(file_found):
    """Parse an Android shared_prefs XML file, recovering from stray control
    characters rather than failing outright; returns an empty element if it is
    unparseable even after that recovery.
    """
    try:
        return ET.parse(file_found).getroot()
    except ET.ParseError:
        try:
            with open(file_found, encoding='utf-8', errors='replace') as f:
                cleaned = _INVALID_XML_CHARS.sub('', f.read())
            return ET.fromstring(cleaned)
        except ET.ParseError as ex:
            logfunc(f'Spotify: could not parse {file_found}: {ex}')
            return ET.Element('empty')


def _xml_value(root, name):
    node = root.find(f".//*[@name='{name}']")
    if node is None:
        return None
    return node.get('value', node.text)


def _epoch_ms_to_utc(value):
    try:
        return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc)
    except (TypeError, ValueError, OverflowError):
        return None


def _epoch_s_to_utc(value):
    try:
        return datetime.fromtimestamp(int(value), tz=timezone.utc)
    except (TypeError, ValueError, OverflowError):
        return None


def _decode_bytes(value):
    """blackboxprotobuf returns strings as raw bytes; decode to text when the
    result is clean UTF-8 and printable, otherwise leave it out rather than
    show binary/garbled output.
    """
    if not isinstance(value, bytes):
        return value
    try:
        text = value.decode('utf-8')
    except UnicodeDecodeError:
        return None
    return text if text.isprintable() else None


def _as_list(node):
    if isinstance(node, list):
        return node
    if node is None:
        return []
    return [node]


def _find_named_field(values, name):
    """event-sender.db's decoded fragments store each top-level field as
    {'1': <field name bytes>, '2' or '2-1': <field value>} inside a list under
    key '1'. Walk that list for the entry whose name matches.
    """
    for item in _as_list(values.get('1')):
        if isinstance(item, dict) and item.get('1') == name.encode():
            return item
    return None


def _event_context_time(values):
    item = _find_named_field(values, 'context_time')
    if not item:
        return None
    inner = item.get('2-1')
    if not isinstance(inner, dict):
        return None
    return _epoch_ms_to_utc(inner.get('1'))


def _event_message(values):
    item = _find_named_field(values, 'message')
    if not item:
        return None
    message = item.get('2')
    return message if isinstance(message, dict) else None


def _summarize_message(message):
    """Pull only the evidence directly confirmed against this device's real
    data out of a decoded event message: a Spotify content URI, the
    session-correlation hash, and any other short human-readable status
    strings. Everything else in these messages is an unlabelled numeric
    telemetry value with no public schema, so it is left out.
    """
    uri = ''
    session_id = ''
    notes = []
    for value in message.values():
        if isinstance(value, bytes) and len(value) == 16 and not session_id:
            # Spotify's client encodes the same session-correlation ID as a
            # raw 16-byte value in some event types (e.g. PlaybackSegments,
            # BoomboxPlaybackSession) and as its hex-string form in others
            # (e.g. CorePlaybackFinished); normalising both to hex text is
            # what lets rows from different event types that share one
            # playback session be tied together below.
            session_id = value.hex()
            continue
        text = _decode_bytes(value)
        if not isinstance(text, str) or not text:
            continue
        if _URI_RE.match(text):
            uri = text
        elif _HEX_ID_RE.match(text) and not session_id:
            session_id = text
        elif text.isprintable() and len(text) < 40:
            notes.append(text)
    return uri, session_id, ', '.join(dict.fromkeys(notes))


def _find_all(files_found, suffix):
    """Every matched file whose name ends with `suffix`, not just the first.

    One extraction can hold genuinely separate copies of an app's data: a second
    Android user under data/user/<n>, and, for the per-account settings folder,
    one file per Spotify account signed in on the device. Duplicate spellings of
    a single file are collapsed by unique_files() before this is called, so what
    is left here is separate evidence and every one of them is read.
    """
    return [str(f) for f in files_found if str(f).endswith(suffix)]


def _account_folder(context, path):
    """The per-account directory name a settings file sits in, as stored.

    Read from the evidence-relative path so the report's own extraction folder
    cannot be mistaken for part of the evidence path. Returns '' when the file is
    not under a Users/<account>/ directory.
    """
    relative = str(context.get_relative_path(str(path))).replace('\\', '/')
    match = _ACCOUNT_DIR_RE.search(relative)
    return match.group(1) if match else ''


def _http_cache_pairs(files_found):
    """Android's OkHttp-style disk cache stores each cached exchange as two
    files sharing a base name: '<hash>.0' (the request line, status line and
    headers, as plain text) and '<hash>.1' (the response body, usually
    gzip-compressed). Group them so each pair can be read together.
    """
    pairs = {}
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('.0'):
            pairs.setdefault(file_found[:-2], {})['request'] = file_found
        elif file_found.endswith('.1'):
            pairs.setdefault(file_found[:-2], {})['response'] = file_found
    return pairs


def _read_text(path):
    try:
        with open(path, 'rb') as f:
            return f.read().decode('utf-8', 'replace')
    except OSError as ex:
        logfunc(f"Spotify: could not read {path}: {ex}")
        return ''


def _gunzip_file(path):
    try:
        with open(path, 'rb') as f:
            raw = f.read()
    except OSError as ex:
        logfunc(f"Spotify: could not read {path}: {ex}")
        return b''
    try:
        return gzip.decompress(raw)
    except OSError:
        return raw


def _okhttp_received_time(request_path):
    """OkHttp's disk cache writes each cached exchange's '<hash>.0' metadata
    file with two pseudo-headers of its own, alongside the real HTTP headers:
    OkHttp-Sent-Millis and OkHttp-Received-Millis, epoch-millisecond times the
    client itself recorded for when it sent the request and received the
    response. Unlike the response file's filesystem modification time, these
    are baked into the cached entry's own text and do not change when the
    evidence is re-staged or copied, which is what makes this usable for a
    fixed, regression-tested CI fixture. Returns None when the pseudo-header
    is not present in this entry, rather than falling back to a filesystem
    time.
    """
    match = _OKHTTP_RECEIVED_MILLIS_RE.search(_read_text(request_path))
    if not match:
        return None
    return _epoch_ms_to_utc(match.group(1))


def _lyrics_first_line(body, response_path):
    try:
        values, _typedef = decode_message(body)
    except Exception as ex:  # pylint: disable=broad-exception-caught
        logfunc(f"Spotify: could not decode the cached lyrics response "
                f"{response_path}: {ex}")
        return ''
    container = values.get('1')
    if isinstance(container, list):
        container = container[0] if container else None
    if not isinstance(container, dict):
        return ''
    for line in _as_list(container.get('2')):
        if not isinstance(line, dict):
            continue
        text = _decode_bytes(line.get('2'))
        if text:
            return text
    return ''


@artifact_processor
def spotify_account(context):
    data_headers = (
        "Canonical Username", "Event Owner ID", "Auth Source", "Language",
        ("App First Launch Time", "datetime"), "Installation ID",
    )

    files_found = [str(f) for f in unique_files(context)]

    data_list = []
    source_paths = set()
    for prefs_path in _find_all(files_found, 'spotify_preferences.xml'):
        root = _parse_xml(prefs_path)
        username = _xml_value(root, 'crashlytics_user_id') or ''
        event_owner = _xml_value(root, 'event-sender-event-owner') or ''
        if not username and not event_owner:
            continue
        source_paths.add(prefs_path)
        data_list.append((
            username,
            event_owner,
            _xml_value(root, 'ADAPTIVE_AUTH_METADATA_AUTH_SOURCE') or '',
            _xml_value(root, 'user-selected-language') or '',
            _epoch_ms_to_utc(_xml_value(root, 'key_date_first_launch')),
            _xml_value(root, 'installation_id') or '',
        ))

    logfunc(f"Spotify Account: {len(data_list)} account(s) recovered from "
            f"{len(source_paths)} preferences file(s).")
    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def spotify_playlist_library(context):
    data_headers = (
        ("Snapshot Time", "datetime"), "Account Folder", "Playlist URI",
        "Counter A (raw)", "Counter B (raw)",
    )

    files_found = [str(f) for f in unique_files(context)]

    data_list = []
    source_paths = set()
    for frecency_path in _find_all(files_found, 'frecency.pb'):
        with open(frecency_path, 'rb') as f:
            raw = f.read()
        try:
            values, _typedef = decode_message(raw)
        except Exception as ex:  # pylint: disable=broad-exception-caught
            logfunc(f"Spotify: could not decode {frecency_path}: {ex}")
            continue
        source_paths.add(frecency_path)
        account = _account_folder(context, frecency_path)
        for entry in _as_list(values.get('1')):
            if not isinstance(entry, dict):
                continue
            playlist_uri = _decode_bytes(entry.get('1')) or ''
            for snapshot in _as_list(entry.get('2')):
                if not isinstance(snapshot, dict):
                    continue
                data_list.append((
                    _epoch_s_to_utc(snapshot.get('4')), account, playlist_uri,
                    snapshot.get('2'), snapshot.get('3'),
                ))

    data_list.sort(key=lambda row: (row[0] is None, row[0]))
    logfunc(f"Spotify Playlist Library Activity: {len(data_list)} snapshot(s) "
            f"recovered from {len(source_paths)} frecency.pb file(s).")
    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def spotify_playback_activity(context):
    data_headers = (
        ("Event Time", "datetime"), "Event Type", "Content URI", "Session ID", "Notes",
    )

    files_found = [str(f) for f in unique_files(context)]

    # get_sqlite_db_records() takes a plain query string with no bound-parameter
    # support, so the whitelist is inlined directly; it is a fixed internal
    # tuple, never user input, so this is safe.
    name_list = ', '.join(f"'{name}'" for name in _PLAYBACK_EVENT_NAMES)

    data_list = []
    source_paths = set()
    for db_path in _find_all(files_found, 'event-sender.db'):
        rows = get_sqlite_db_records(
            db_path,
            f"SELECT eventName, fragments FROM Events "
            f"WHERE eventName IN ({name_list}) ORDER BY id",
        )
        source_paths.add(db_path)
        for event_name, fragments in rows:
            try:
                values, _typedef = decode_message(fragments)
            except Exception as ex:  # pylint: disable=broad-exception-caught
                logfunc(f"Spotify: could not decode a {event_name} event: {ex}")
                continue
            event_time = _event_context_time(values)
            message = _event_message(values)
            if message is None:
                continue
            uri, session_id, notes = _summarize_message(message)
            data_list.append((event_time, event_name, uri, session_id, notes))

    data_list.sort(key=lambda row: (row[0] is None, row[0]))
    logfunc(f"Spotify Playback Activity: {len(data_list)} event(s) recovered "
            f"from {len(source_paths)} event-sender.db file(s).")
    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def spotify_recently_played(context):
    data_headers = (
        ("Played At", "datetime"), "Track URI", "Playlist Context URI",
    )

    files_found = [str(f) for f in unique_files(context)]
    pairs = _http_cache_pairs(files_found)

    data_list = []
    source_paths = set()
    for paths in pairs.values():
        request_path = paths.get('request')
        response_path = paths.get('response')
        if not request_path or not response_path:
            continue
        if not _RECENTLY_PLAYED_RE.search(_read_text(request_path)):
            continue
        source_paths.add(request_path)
        body = _gunzip_file(response_path)
        try:
            values, _typedef = decode_message(body)
        except Exception as ex:  # pylint: disable=broad-exception-caught
            logfunc(f"Spotify: could not decode a recently-played response: {ex}")
            continue
        for entry in _as_list(values.get('1')):
            if not isinstance(entry, dict):
                continue
            track_uri = _decode_bytes(entry.get('3')) or ''
            if not track_uri:
                continue
            playlist_uri = _decode_bytes(entry.get('1')) or ''
            played_at = _epoch_ms_to_utc(entry.get('2'))
            data_list.append((played_at, track_uri, playlist_uri))

    data_list.sort(key=lambda row: (row[0] is None, row[0]))
    logfunc(f"Spotify Recently Played: {len(data_list)} "
            f"entr{'y' if len(data_list) == 1 else 'ies'} recovered.")
    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def spotify_now_playing_view(context):
    data_headers = (
        "Track ID", "First Lyric Line", "Merch Shown For Track",
        ("Response Received Time", "datetime"),
    )

    files_found = [str(f) for f in unique_files(context)]
    pairs = _http_cache_pairs(files_found)

    merch_requests = {}
    lyrics_entries = []
    for paths in pairs.values():
        request_path = paths.get('request')
        response_path = paths.get('response')
        if not request_path or not response_path:
            continue
        url = _read_text(request_path)
        merch_match = _MERCH_TRACK_RE.search(url)
        if merch_match:
            merch_requests[merch_match.group(1)] = request_path
            continue
        lyrics_match = _LYRICS_TRACK_RE.search(url)
        if lyrics_match:
            lyrics_entries.append((lyrics_match.group(1), response_path, request_path))

    data_list = []
    source_paths = set()
    for track_id, response_path, request_path in lyrics_entries:
        source_paths.add(request_path)
        merch_request = merch_requests.get(track_id)
        if merch_request:
            source_paths.add(merch_request)
        data_list.append((
            track_id,
            _lyrics_first_line(_gunzip_file(response_path), response_path),
            "Yes" if merch_request else "",
            _okhttp_received_time(request_path),
        ))

    data_list.sort(key=lambda row: (row[3] is None, row[3]))
    logfunc(f"Spotify Now Playing View: {len(data_list)} track(s) recovered "
            f"from cached lyrics/merch responses.")
    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def spotify_artist_profile_views(context):
    data_headers = (
        "Artist Name", "Artist URI", ("Response Received Time", "datetime"),
    )

    files_found = [str(f) for f in unique_files(context)]
    pairs = _http_cache_pairs(files_found)

    data_list = []
    source_paths = set()
    for paths in pairs.values():
        request_path = paths.get('request')
        response_path = paths.get('response')
        if not request_path or not response_path:
            continue
        if not _ARTIST_VIEW_RE.search(_read_text(request_path)):
            continue
        body = _gunzip_file(response_path)
        try:
            data = json.loads(body)
        except (ValueError, UnicodeDecodeError) as ex:
            logfunc(f"Spotify: could not parse an artist-identity-view response: {ex}")
            continue
        name = data.get('name', '') or ''
        artist_uri = data.get('artistUri', '') or ''
        if not name and not artist_uri:
            continue
        source_paths.add(request_path)
        data_list.append((name, artist_uri, _okhttp_received_time(request_path)))

    data_list.sort(key=lambda row: (row[2] is None, row[2]))
    logfunc(f"Spotify Artist Profile Views: {len(data_list)} view(s) recovered "
            f"from cached artist-identity-view responses.")
    return data_headers, data_list, '\n'.join(sorted(source_paths))