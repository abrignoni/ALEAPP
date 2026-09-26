__artifacts_v2__ = {
    "exoplayerCachedMedia": {
        "name": "ExoPlayer - Rejoined Cached Media",
        "description": "Video and audio that Android apps cached through ExoPlayer: each cached item's "
                       "pieces joined in order up to the first missing one, a DASH stream's segments joined in "
                       "the order its cached manifest lists them, and a DASH video put in one file with its "
                       "cached audio.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-26",
        "last_update_date": "2026-09-26",
        "requirements": "none",
        "category": "ExoPlayer Cache",
        "notes": "Read with the vendored exoprobe (scripts/vendor/exoprobe.py, "
                 "https://github.com/abrignoni/exoprobe) from the ExoPlayer SimpleCache folders the extraction "
                 "holds, whatever the app, found by their file names: pieces named <id>.<position>.<time>.v3.exo, or"
                 " the older <key>.<position>.<time>.v2.exo and .v1.exo, which carry the key in the name. A v3 id is"
                 " named by cached_content_index.exi (its .bak copy first, as ExoPlayer's AtomicFile restores it) or"
                 " by an ExoPlayerCacheIndex<uid> table in exoplayer_internal.db matched through the cache's "
                 "<uid>.uid file (androidx/media 1.11.1 SimpleCacheSpan and CachedContentIndex); Key From says "
                 "which. Key is the cache key as stored: the key the app set for the request, or the address fetched"
                 " when it set none (CacheKeyFactory.DEFAULT). Pieces are joined from position 0 up to the first "
                 "gap. State is complete when the joined bytes reach the length the index recorded (exo_len), "
                 "partial when they fall short with no gap, stops at a gap when a piece is missing, and length not "
                 "recorded when the index gives no length, so whether such a file is whole is not established. An "
                 "item with no piece at position 0 is not reported. A DASH stream is joined only from a cached "
                 "manifest: its initialization segment, then its media segments in the manifest's order up to the "
                 "first one missing or incomplete; its segments are not reported again one by one. A DASH video is "
                 "also written as one file with every cached audio stream its manifest lists, one track each in the "
                 "manifest's order, and only the first enabled when there are several; no sample is re-encoded, and "
                 "that combined file takes the place of its silent video and its audio in this table. Audio Tracks "
                 "gives each track's language as the manifest writes it; Audio Tracks is filled only for a combined "
                 "file, so it is empty on the seven tested images with none. A complete whole-file video a manifest "
                 "lists is combined the same way with each complete whole-file audio that manifest lists; an audio "
                 "file that is not complete is left out. Only items whose bytes open as video, audio or an image are"
                 " reported (an MP4 whose only track is sound is audio; no image was found on the tested images): "
                 "manifests, playlists and content that none of exoprobe's signatures matches are not. Only 3 rows "
                 "come from Snapchat, whose own artifact reports 800 cache entries on the same images; on "
                 "russell_a14 all 105 of its joined items matched none of those signatures. An MP4 whose movie "
                 "header declares fragments and has no fragment after it is an initialization segment cached on its "
                 "own; What says so and no media is offered, since it holds no samples (61 rows). What also says "
                 "when a file stops inside its last box (51 rows). Last Touched is the latest time in the names of "
                 "the pieces joined, on the device clock: when ExoPlayer wrote a piece, or read it again where the "
                 "app's evictor asks for that and the cache keeps no file index. A cache with an "
                 "ExoPlayerCacheFileMetadata table records later reads there and leaves the name alone "
                 "(SimpleCache.touchSpan), so Last Touched does not establish when the item was last viewed. "
                 "/mnt/pass_through/<n>/emulated/<user>/ is read as the same folder as /data/media/<user>/: on the "
                 "two tested images carrying both, every ExoPlayer file had the same name, size and CRC in each; "
                 "where the two differ the larger copy is read. Different keys can hold identical bytes (a video "
                 "cached under two addresses, for example), and each is its own row showing the same media: 32 rows "
                 "repeat a media file an earlier row shows. The joined files shown here are also kept in the "
                 "report's _ExoPlayer Rejoined folder. On the 10 tested images, 631 rows from 19 apps. ffmpeg 9.0.1 "
                 "decoded all 41 combined files and every other MP4 video that is neither cut nor an initialization "
                 "segment without error. It reported errors on 38 of the 47 cut MP4 videos, 32 of 40 WebM videos, 1 "
                 "of 19 MPEG transport streams, and 26 of 96 audio files, 22 of them xHE-AAC and the other 4 cut. "
                 "Every combined file on the tested images carried one audio track, so several audio tracks are "
                 "exercised by exoprobe's own tests only. The Grok and Pinterest artifacts show their caches' pieces"
                 " themselves; the Twitter, Snapchat, Instagram and Reddit artifacts report the cache entries.",
        "paths": ('*.exo', '*/cached_content_index.exi*', '*.uid', '*/exoplayer_internal.db*'),
        "output_types": "standard",
        "artifact_icon": "film",
        "sample_data": {
            "anne_a15": "Android 15 | 40 rows",
            "cookbook_a11": "Android 11 | 14 rows",
            "galaxys10_a10": "Android 10 | 100 rows",
            "pixel3_a11": "Android 11 | 59 rows",
            "pixel3_a12": "Android 12 | 29 rows",
            "pixel7a_a14": "Android 14 | 56 rows",
            "russell_a14": "Android 14 | 136 rows",
            "russell_pixel6a_a13": "Android 13 | 97 rows",
            "samsungs20_a13": "Android 13 | 92 rows",
            "sharon_a14": "Android 14 | 8 rows",
        },
    },
}

import hashlib
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from scripts.ilapfuncs import artifact_processor, check_in_embedded_media, logfunc
from scripts.artifacts.storagePathViews import unique_files
from scripts.vendor import exoprobe

OUT_FOLDER = '_ExoPlayer Rejoined'
MEDIA_KINDS = ('video', 'audio', 'image')
# A joined file is handed to the report as bytes, so one larger than this is reported
# without inline media rather than read into memory.
MAX_MEDIA_BYTES = 1024 ** 3
_FORCE_TYPE = {'.m4a': 'audio/mp4', '.ts': 'video/mp2t'}

# (report output folder, cache folder) -> records, so a cache is rejoined once per run
# however many artifacts read it
_REJOINED = {}


# /mnt/pass_through/<viewer>/emulated/<user>/ is another view of /data/media/<user>/: on the
# tested images with a second Android user, both carried the same names (2,313 and 4,372
# files) and all but one or two the same size and CRC.
_PASS_THROUGH = re.compile(r'(^|/)mnt/pass_through/\d+/emulated/(\d+)/')


def _cache_files(context):
    """(evidence path, staged path) for every ExoPlayer cache file this artifact found. A
    pass-through file whose /data/media counterpart was also found is read once, under the
    /data/media name, from whichever copy is larger."""
    found = {}
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found) or not exoprobe.is_cache_name(file_found):
            continue
        found[context.get_relative_path(file_found).replace('\\', '/')] = file_found
    pairs = {}
    for logical, real in found.items():
        folded = _PASS_THROUGH.sub(r'\1data/media/\2/', logical)
        if folded == logical or folded not in found:
            pairs.setdefault(logical, real)
            continue
        pairs[folded] = max((real, found[folded]), key=_size)
    return list(pairs.items())


def _size(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return -1


def rejoined_records(context):
    """exoprobe's records for every cache among this artifact's files, each with ``path``
    (the joined file), ``anchor`` (the staged first piece it starts with) and
    ``sources`` (the index files it was named by)."""
    pairs = _cache_files(context)
    real = dict(pairs)
    dbs = [r for logical, r in pairs if exoprobe.basename(logical) == exoprobe.DB_NAME]
    out_base = Path(context.get_report_folder()).parents[1] / OUT_FOLDER
    records = []
    for cache in exoprobe.group_caches(pairs):
        key = (str(out_base), cache.root)
        if key not in _REJOINED:
            tag = hashlib.sha1(cache.root.encode('utf-8', 'surrogatepass')).hexdigest()[:10]
            folder = out_base / tag
            recs = exoprobe.rejoin(cache, folder)
            index = [r for logical, r in cache.index_files if cache.index_from == exoprobe.basename(logical)]
            if cache.index_from.startswith(exoprobe.DB_NAME):
                app = exoprobe.app_folder(cache.root)
                index += [d for d in dbs if exoprobe.app_folder(context.get_relative_path(d)) == app]
            for rec in recs:
                if rec.get('file'):
                    rec['path'] = folder / rec['file']
                starts = [p for p in cache.items.get(rec['item'], []) if p.position == 0]
                if starts:
                    rec['anchor'] = real.get(max(starts, key=lambda p: p.timestamp).tag)
                rec['sources'] = index
            # only the media the report shows is kept; the rest (manifests, playlists,
            # content no signature names, and the streams a combined file already
            # carries) is deleted again, so the folder holds what the table points to
            keep = {r['path'] for r in shown(recs)}
            for rec in recs:
                if rec.get('path') and rec['path'] not in keep:
                    try:
                        rec['path'].unlink()
                    except OSError:
                        pass
            _REJOINED[key] = recs
        records += _REJOINED[key]
    return records


def shown(records):
    """The written media records, leaving out a stream or file that went into a combined
    file, since the combined file carries it."""
    inside = set()
    for rec in records:
        if rec['status'] == 'written' and rec.get('combined'):
            folder = rec['path'].parent
            inside.add(folder / rec['combined']['video'])
            inside.update(folder / t['file'] for t in rec['combined']['audio_tracks'])
    return [r for r in records if r['status'] == 'written' and r.get('kind') in MEDIA_KINDS
            and r['path'] not in inside]


def _layout(rec):
    if 'layout' not in rec:
        rec['layout'] = exoprobe.mp4_layout(rec['path']) if rec.get('path') else None
    return rec['layout']


def _init_only(rec):
    layout = _layout(rec)
    return bool(layout and layout['moov'] and layout['mvex'] and not layout['moof'])


def media_ref(rec):
    """The joined file checked in as media, attributed to the piece it starts with. An
    initialization segment on its own holds no samples, so it is not offered as media."""
    path = rec.get('path')
    if not path or not rec.get('anchor') or _init_only(rec):
        return ''
    try:
        if os.path.getsize(path) > MAX_MEDIA_BYTES:
            logfunc(f'ExoPlayer: {rec["file"]} is larger than {MAX_MEDIA_BYTES:,} bytes and is not shown inline')
            return ''
        data = Path(path).read_bytes()
    except OSError as error:
        logfunc(f'ExoPlayer: could not read {rec.get("file")}: {error}')
        return ''
    return check_in_embedded_media(rec['anchor'], data, f"{Path(path).parent.name}_{rec['file']}",
                                   force_type=_FORCE_TYPE.get(Path(path).suffix)) or ''


def _utc(ms):
    try:
        return datetime.fromtimestamp(int(ms) / 1000, timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _what(rec):
    return _shape(rec) + _cut(rec)


def _cut(rec):
    layout = _layout(rec)
    return ', the file stops inside its last box' if layout and layout['cut'] else ''


def _shape(rec):
    if _init_only(rec):
        return 'an initialization segment on its own: it describes the track and holds no samples'
    if rec.get('combined'):
        return f"DASH video with {len(rec['combined']['audio_tracks'])} audio track(s)"
    if rec.get('dash'):
        d = rec['dash']
        return f"DASH {rec['kind']} stream, {d['segments_joined']} of {d['segments_listed']} listed segments"
    if rec.get('manifest_key'):
        return 'cached item, a whole stream a DASH manifest lists'
    return 'cached item'


def _tracks(rec):
    out = []
    for n, t in enumerate((rec.get('combined') or {}).get('audio_tracks', []), 1):
        bits = [f"language {t['lang']} (as the manifest gives it)" if t.get('lang') else 'no language in the manifest']
        if str(t.get('bandwidth') or '').isdigit():
            bits.append(f"{int(t['bandwidth']):,} bit/s")
        if t.get('segments'):
            bits.append(f"segments {t['segments']}")
        out.append(f"{n}: " + ', '.join(bits))
    return '; '.join(out)


@artifact_processor
def exoplayerCachedMedia(context):
    data_headers = (
        ('Last Touched', 'datetime'),
        ('Media', 'media'),
        'App',
        'Kind',
        'What',
        'State',
        'Bytes',
        'Length Recorded',
        'Pieces Joined',
        'Audio Tracks',
        'Key (as stored)',
        'Key From',
        'Cache Folder',
    )
    data_list = []
    sources = []
    records = rejoined_records(context)
    for rec in shown(records):
        pieces = f"{rec['pieces_joined']} of {rec['pieces_total']}" if 'pieces_joined' in rec else ''
        data_list.append((
            _utc(rec.get('last_touched_ms')),
            media_ref(rec),
            rec.get('app_folder') or '',
            rec['kind'],
            _what(rec),
            rec.get('state', ''),
            rec.get('bytes', ''),
            rec.get('length_recorded', '') if rec.get('length_recorded') is not None else '',
            pieces,
            _tracks(rec),
            rec.get('key') or '',
            rec.get('key_from') or '',
            rec.get('cache_folder') or '',
        ))
        for p in [*rec.get('sources', []), rec.get('anchor')]:
            if p and p not in sources:
                sources.append(p)
    data_list.sort(key=lambda row: str(row[0]))
    written = sum(r['status'] == 'written' for r in records)
    logfunc(f'ExoPlayer: {len(records)} cache record(s), {written} file(s) written, {len(data_list)} shown')
    return data_headers, data_list, '\n'.join(context.get_relative_path(p) for p in sources)
