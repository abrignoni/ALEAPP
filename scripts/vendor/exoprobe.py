#!/usr/bin/env python3
"""exoprobe: rejoin the media an Android app cached through ExoPlayer.

One file, pure Python, standard library only. Read-only on the evidence.

ExoPlayer, Google's media library for Android (``com.google.android.exoplayer2``,
now ``androidx.media3``), caches what an app streams in a ``SimpleCache`` folder.
One video is not one file there: it is split into pieces, each named for where it
starts in the video, and the name of the video is kept in a separate index. This
module reads that layout, joins each item's pieces back into the file the app
downloaded, joins a DASH stream's segments in the order its cached manifest lists
them, and can put a DASH video and its audio tracks into one MP4 without
re-encoding anything.

The layout, from androidx/media 1.11.1
(https://github.com/androidx/media/tree/8c6678b657ede1e7883fc164ef73ed483c7796c3,
``libraries/datasource/src/main/java/androidx/media3/datasource/cache``):

* a piece is ``<id>.<position>.<timestamp>.v3.exo`` in a subfolder ``0`` to ``9`` of
  the cache folder (``SimpleCacheSpan.getCacheFile``, ``SimpleCache``
  ``SUBDIRECTORY_COUNT``): ``id`` names the cached item, ``position`` is the byte
  offset the piece starts at, ``timestamp`` is its last-touch time in milliseconds
  (``System.currentTimeMillis``). The name is rewritten on a later touch only when
  the app's evictor asks for touches and the cache keeps no file index; with an
  ``ExoPlayerCacheFileMetadata`` table the new time goes there instead
  (``SimpleCache.touchSpan``). Older caches wrote
  ``<key>.<position>.<timestamp>.v2.exo`` (the key escaped with ``%xx``,
  ``Util.escapeFileName``) or ``.v1.exo`` (not escaped) in the cache folder itself,
  so the key is in the name and no index is needed.
* the index that maps an id to its key, normally the address it was fetched from,
  is either ``cached_content_index.exi`` in the cache folder (``CachedContentIndex``
  legacy storage; ``.exi.bak``, when present, is the valid copy, ``AtomicFile``) or
  a table ``ExoPlayerCacheIndex<uid>`` in a database, by default
  ``exoplayer_internal.db`` (``StandaloneDatabaseProvider``), whose ``<uid>`` is the
  name of the ``<uid>.uid`` file in the cache folder.
* an item's metadata can record its full length (``exo_len``, an 8-byte big-endian
  number) and the address it was redirected to (``exo_redir``, UTF-8)
  (``ContentMetadata``, ``DefaultContentMetadata``).

Pieces are joined from the start of the item until the first gap. Pieces after a
gap are not joined, because without the bytes before them they cannot be placed in
a playable file; they are counted, never silently dropped.

Command line::

    exoprobe scan   <folder>                 # every cache, item, key and state
    exoprobe rejoin <folder> -o <out>        # write the joined media and report.json
    exoprobe mux    <video> <audio>... -o <out.mp4>

MIT licence. https://github.com/abrignoni/exoprobe
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import sqlite3
import struct
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath
from typing import Callable, Iterable, NamedTuple
from urllib.parse import urljoin

__version__ = "0.1.2"

# ---- names ------------------------------------------------------------------

PIECE_V3 = re.compile(r"^(\d+)\.(\d+)\.(-?\d+)\.v3\.exo$")
PIECE_V12 = re.compile(r"^(.+)\.(\d+)\.(-?\d+)\.v([12])\.exo$", re.DOTALL)
UID_FILE = re.compile(r"^[0-9a-f]{1,16}\.uid$")
INDEX_NAME = "cached_content_index.exi"
DB_NAME = "exoplayer_internal.db"
TABLE_PREFIX = "ExoPlayerCacheIndex"

# The largest item joined; anything claiming more is treated as a gap.
MAX_ITEM_BYTES = 2 * 1024 ** 3

_ESCAPED = re.compile(r"%([A-Fa-f0-9]{2})")


def basename(name: str) -> str:
    """The last component of a path with either separator."""
    return str(name).replace("\\", "/").rsplit("/", 1)[-1]


def is_piece_name(name: str) -> bool:
    """True for a cache piece's file name (v1, v2 or v3)."""
    b = basename(name)
    return bool(PIECE_V3.match(b) or PIECE_V12.match(b))


def is_cache_name(name: str) -> bool:
    """True for a file an ExoPlayer cache writes: a piece, the index file or its
    backup, a ``.uid`` file, or the default index database and its journal."""
    b = basename(name)
    return (is_piece_name(b) or b in (INDEX_NAME, INDEX_NAME + ".bak")
            or b in (DB_NAME, DB_NAME + "-wal", DB_NAME + "-journal")
            or bool(UID_FILE.match(b)))


def unescape_key(name: str) -> str | None:
    """``Util.unescapeFileName``: ``%xx`` back to its character, None if malformed."""
    want = len(name) - 2 * name.count("%")
    out = _ESCAPED.sub(lambda m: chr(int(m.group(1), 16)), name)
    return out if len(out) == want else None


class PieceName(NamedTuple):
    version: str          # "v1", "v2" or "v3"
    item: int | str       # the id (v3) or the key (v1, v2)
    position: int
    timestamp: int


def parse_piece_name(name: str) -> PieceName | None:
    """What a piece's file name says, or None when it is not a piece's name. A v2
    key that does not unescape cleanly is kept as written."""
    b = basename(name)
    m = PIECE_V3.match(b)
    if m:
        return PieceName("v3", int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = PIECE_V12.match(b)
    if m:
        ver = m.group(4)
        key = m.group(1) if ver == "1" else unescape_key(m.group(1))
        return PieceName(f"v{ver}", key if key is not None else m.group(1),
                         int(m.group(2)), int(m.group(3)))
    return None


def cache_root(logical: str) -> str:
    """The cache folder a file belongs to. A v3 piece sits in ``<cache>/<0-9>/``; the
    index, the uid file and ExoPlayer's own older pieces sit in ``<cache>`` itself.
    A piece of any version in a folder named only by digits belongs to the folder
    above it: Instagram writes v2 pieces in subfolders 0 to 28 of its videocache
    folder, one item's pieces in several of them. On the Android images tested, all
    1,461 older pieces in a digit-named folder were Instagram's, and no v3 piece sat
    in a folder named by more than one digit."""
    logical = str(logical).replace("\\", "/")
    parent = PurePosixPath(logical).parent
    if is_piece_name(logical) and re.fullmatch(r"\d+", parent.name):
        parent = parent.parent
    return str(parent)


def app_folder(root: str) -> str | None:
    """The Android package whose folder holds the cache, read from the path."""
    m = re.search(r"(?:^|/)(?:data/data|data/user(?:_de)?/\d+|Android/data|userdata/data)/([^/]+)/",
                  str(root).replace("\\", "/") + "/")
    return m.group(1) if m else None


# ---- the index ------------------------------------------------------------------

def _java_utf(b: bytes) -> str:
    """A string ``DataOutputStream.writeUTF`` wrote (modified UTF-8)."""
    b = b.replace(b"\xc0\x80", b"\x00")
    try:
        return b.decode("utf-8", "surrogatepass").encode(
            "utf-16", "surrogatepass").decode("utf-16")
    except UnicodeError:
        return b.decode("utf-8", "replace")


def _metadata(data: io.BytesIO) -> dict:
    """``CachedContentIndex.readContentMetadata``: count, then name/length/value."""
    out = {}
    (n,) = struct.unpack(">i", data.read(4))
    for _ in range(n):
        (ln,) = struct.unpack(">H", data.read(2))
        name = _java_utf(data.read(ln))
        (size,) = struct.unpack(">i", data.read(4))
        if size < 0:
            raise ValueError("negative metadata size")
        value = data.read(size)
        if len(value) != size:
            raise ValueError("metadata runs past the end")
        out[name] = value
    return out


def _summary(meta: dict) -> dict:
    """The two keys ExoPlayer itself defines: the item's full length and the
    address it was redirected to."""
    out = {}
    v = meta.get("exo_len")
    if v is not None and len(v) == 8:
        out["length"] = struct.unpack(">q", v)[0]
    v = meta.get("exo_redir")
    if v is not None:
        out["redirected_to"] = v.decode("utf-8", "replace")
    return out


def parse_index_file(data: bytes) -> dict:
    """Read a ``cached_content_index.exi``.

    Returns ``{"state": ..., "entries": {id: {"key", "length"?, "redirected_to"?}}}``.
    ``state`` is ``read`` when every entry parsed and the file ended exactly after
    the trailing hash, ``encrypted`` when the file's flag says the entries are
    AES-encrypted (the key is not in the file), and ``unreadable`` otherwise.
    """
    if len(data) < 8:
        return {"state": "unreadable", "entries": {}}
    version, flags = struct.unpack(">ii", data[:8])
    if version < 0 or version > 2:
        return {"state": "unreadable", "entries": {}}
    if flags & 1:
        return {"state": "encrypted", "entries": {}}
    buf = io.BytesIO(data[8:])
    entries = {}
    try:
        (count,) = struct.unpack(">i", buf.read(4))
        for _ in range(count):
            (cid,) = struct.unpack(">i", buf.read(4))
            (ln,) = struct.unpack(">H", buf.read(2))
            key = _java_utf(buf.read(ln))
            if version < 2:
                (length,) = struct.unpack(">q", buf.read(8))
                info = {"length": length} if length >= 0 else {}
            else:
                info = _summary(_metadata(buf))
            entries[cid] = {"key": key, **info}
        buf.read(4)                                   # the trailing hash
        state = "read" if buf.read(1) == b"" else "unreadable"
    except (struct.error, ValueError):
        state = "unreadable"
    return {"state": state, "entries": entries}


def read_index_tables(db_path) -> dict[str, dict]:
    """``{uid: {id: {"key", ...}}}`` for every ``ExoPlayerCacheIndex<uid>`` table in a
    database. Opens ``db_path`` read-only, which still rewrites a ``-shm`` beside it,
    so pass a copy, never the evidence (:func:`read_index_database` makes one)."""
    out: dict[str, dict] = {}
    con = sqlite3.connect(f"file:{Path(db_path).as_posix()}?mode=ro", uri=True)
    try:
        names = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name LIKE ?",
            (TABLE_PREFIX + "%",))]
        for t in names:
            rows = {}
            for cid, key, blob in con.execute(f'SELECT id, key, metadata FROM "{t}"'):
                info = {}
                if blob:
                    with contextlib.suppress(struct.error, ValueError):
                        info = _summary(_metadata(io.BytesIO(bytes(blob))))
                rows[int(cid)] = {"key": key, **info}
            out[t[len(TABLE_PREFIX):].lower()] = rows
    finally:
        con.close()
    return out


def read_index_database(path, sidecars: Iterable = ()) -> dict[str, dict]:
    """:func:`read_index_tables` on a temporary copy of ``path`` and of any
    ``-wal`` or ``-journal`` beside it (or given in ``sidecars``), so the evidence is
    never opened. Unreadable databases give ``{}``."""
    path = Path(path)
    with tempfile.TemporaryDirectory(prefix="exoprobe-") as td:
        try:
            shutil.copyfile(path, Path(td) / DB_NAME)
            found = {Path(s) for s in sidecars}
            found |= {path.with_name(path.name + x) for x in ("-wal", "-journal")}
            for side in found:
                for suffix in ("-wal", "-journal"):
                    if side.name.endswith(suffix) and side.is_file():
                        shutil.copyfile(side, Path(td) / (DB_NAME + suffix))
            return read_index_tables(Path(td) / DB_NAME)
        except (OSError, sqlite3.DatabaseError):
            return {}


# ---- joining pieces ---------------------------------------------------------

class Piece(NamedTuple):
    """One piece of a cached item. ``opener()`` returns a context manager giving a
    readable binary file; ``tag`` is the caller's own handle for the piece."""
    position: int
    timestamp: int
    size: int
    opener: Callable
    tag: object = None


def _copy_from(fh, out, skip: int) -> int:
    fh.seek(skip)
    n = 0
    while True:
        chunk = fh.read(1 << 20)
        if not chunk:
            return n
        out.write(chunk)
        n += len(chunk)


def join(pieces: Iterable[Piece], out, *, max_bytes: int = MAX_ITEM_BYTES) -> dict:
    """Write ``pieces`` into the binary file ``out`` from position 0 until the first
    gap. Where two pieces start at one position the one with the later last-touch
    time is used: when ExoPlayer touches a piece it renames the file to the new time
    (``CachedContent.setLastTouchTimestamp``) rather than adding one, so a live cache
    holds only one, and the later name is the later state.

    Returns ``{"used": [pieces], "bytes": n, "gap": offset or None, "left_out": n}``:
    the pieces joined, the bytes written, where the first gap is (None when there is
    none) and how many pieces lie past it.
    """
    pieces = sorted(pieces, key=lambda p: (p.position, -p.timestamp))
    end, used, gap = 0, [], None
    for p in pieces:
        size = p.size or 0
        if p.position + size <= end:
            continue                               # nothing this piece adds
        if p.position > end or p.position + size > max_bytes:
            gap = end
            break
        with p.opener() as fh:
            end += _copy_from(fh, out, end - p.position)
        used.append(p)
    chosen = {id(p) for p in used}
    left = [p for p in pieces if id(p) not in chosen and p.position + (p.size or 0) > end]
    return {"used": used, "bytes": end, "gap": gap, "left_out": len(left)}


def item_state(joined: int, length, gap) -> str:
    """``complete``, ``partial``, ``stops at a gap`` or ``length not recorded``."""
    if length is not None and length >= 0:
        if joined >= length:
            return "complete"
        return "stops at a gap" if gap is not None else "partial"
    return "stops at a gap" if gap is not None else "length not recorded"


def is_complete(joined: int, length, gap) -> bool:
    """No gap, and no shortfall against the length the index recorded."""
    return gap is None and (length is None or joined >= length)


# ---- what a joined item is --------------------------------------------------

_EXT_BY_MAGIC = (
    (lambda h: h[4:8] == b"ftyp", ".mp4"),
    (lambda h: h[:4] == b"\x1aE\xdf\xa3", ".webm"),
    (lambda h: h[:3] == b"\xff\xd8\xff", ".jpg"),
    (lambda h: h[:8] == b"\x89PNG\r\n\x1a\n", ".png"),
    (lambda h: h[:6] in (b"GIF87a", b"GIF89a"), ".gif"),
    (lambda h: h[:3] == b"FLV", ".flv"),
    (lambda h: h[:4] == b"RIFF" and h[8:12] == b"WEBP", ".webp"),
)
_KIND_BY_EXT = {".mp4": "video", ".webm": "video", ".flv": "video", ".ts": "video",
                ".jpg": "image", ".png": "image", ".gif": "image", ".webp": "image"}


def is_mpeg_ts(head: bytes) -> bool:
    """An MPEG transport stream: 188-byte packets, each opening with 0x47. HLS serves
    video in these segments; a single 0x47 byte says nothing, three in step do."""
    return len(head) >= 3 * 188 and all(head[i * 188] == 0x47 for i in range(3))


def sniff_ext(head: bytes) -> str:
    """The extension the first bytes (564 are enough) point to, or ``""``."""
    if is_mpeg_ts(head):
        return ".ts"
    for test, ext in _EXT_BY_MAGIC:
        if test(head):
            return ext
    return ""


def sniff(path) -> tuple[str, str]:
    """``(kind, ext)`` of a joined file: ``video``, ``audio``, ``image`` or
    ``other``. An MP4 whose only track is sound is audio (``.m4a``), whatever its
    brand says."""
    with open(path, "rb") as fh:
        ext = sniff_ext(fh.read(3 * 188))
    if ext == ".mp4" and file_handlers(path) == ["soun"]:
        return "audio", ".m4a"
    return _KIND_BY_EXT.get(ext, "other"), ext


# ---- DASH -------------------------------------------------------------------
# A DASH player fetches a stream as an initialization segment and a list of media
# segments, and ExoPlayer caches each one as its own item, keyed (DashUtil
# .resolveCacheKey) by the representation's cache key when the app sets one and
# otherwise by the segment's address resolved against the representation's first
# BaseURL. The manifest (MPD) the app played from is cached beside them under its
# own address, so it says which items make up which stream and in what order. That
# is the only thing a stream is joined from: a key that merely looks similar, such as
# a segment address differing in a signature, is never used to guess membership.

MAX_MANIFEST_BYTES = 4 * 1024 * 1024
MAX_MOOV_BYTES = 16 * 1024 * 1024


def _local(e) -> str:
    return e.tag.rsplit("}", 1)[-1]


def _kids(e, name: str) -> list:
    return [c for c in e if _local(c) == name]


def _base_url(e, parent: str) -> str:
    b = _kids(e, "BaseURL")
    return urljoin(parent, b[0].text.strip()) if b and b[0].text and b[0].text.strip() else parent


def representations(manifest: bytes, manifest_url: str) -> list[dict]:
    """The streams a DASH manifest lists: for each, its attributes and either the
    resolved addresses of its initialization and media segments, in order
    (``init``, ``media``), or the one address the whole stream is fetched from by
    byte range (``single``), which ExoPlayer caches as one item. ``order`` is the
    stream's place in the manifest.

    ``lang`` is the AdaptationSet's, or its ContentComponent's, which are the two
    places ``DashManifestParser.parseAdaptationSet`` reads it (androidx/media
    1.11.1, lines 473 and 505); it is reported as written, never translated.

    A representation described by a SegmentTemplate is not returned. BaseURL is
    resolved at every level, the way ``DashManifestParser`` does, with RFC 3986
    resolution (``UriUtil.resolve``; ``urljoin`` here).
    """
    root = ET.fromstring(manifest)
    out = []
    b0 = _base_url(root, manifest_url)
    for period in _kids(root, "Period"):
        b1 = _base_url(period, b0)
        for aset in _kids(period, "AdaptationSet"):
            b2 = _base_url(aset, b1)
            lang = aset.get("lang") or next((cc.get("lang") for cc in _kids(aset, "ContentComponent")
                                             if cc.get("lang")), None)
            for rep in _kids(aset, "Representation"):
                b3 = _base_url(rep, b2)
                about = {"id": rep.get("id"), "lang": lang, "order": len(out)}
                for name, attr in (("bandwidth", "bandwidth"), ("mime", "mimeType"),
                                   ("codecs", "codecs"), ("width", "width"), ("height", "height")):
                    about[name] = rep.get(attr) or aset.get(attr)   # a Representation inherits
                if _kids(rep, "SegmentTemplate") or _kids(aset, "SegmentTemplate"):
                    continue
                sl = _kids(rep, "SegmentList") or _kids(aset, "SegmentList")
                inits = [x.get("sourceURL") for s in sl[:1]
                         for x in _kids(s, "Initialization") if x.get("sourceURL")]
                media = [urljoin(b3, u.get("media")) for s in sl[:1]
                         for u in _kids(s, "SegmentURL") if u.get("media")]
                if inits and media:
                    out.append({**about, "init": urljoin(b3, inits[0]), "media": media})
                else:
                    # one address fetched by byte range (SegmentBase, or ranges in a
                    # SegmentList): ExoPlayer caches that as one item under the address
                    out.append({**about, "single": b3})
    return out


def _scan_boxes(b: bytes, start: int, end: int):
    """``(type, payload start, box end)`` for each ISO-BMFF box in ``b[start:end]``,
    stopping quietly at a box that cannot be one."""
    i = start
    while i + 8 <= end:
        size, typ = struct.unpack(">I4s", b[i:i + 8])
        hdr = 8
        if size == 1 and i + 16 <= end:
            size, hdr = struct.unpack(">Q", b[i + 8:i + 16])[0], 16
        elif size == 0:
            size = end - i
        if size < hdr:
            return
        yield typ, i + hdr, min(i + size, end)
        i += size


def track_handlers(init: bytes) -> list[str]:
    """The handler type of each track an initialization segment declares
    (``moov/trak/mdia/hdlr``, ISO/IEC 14496-12): ``vide`` for video, ``soun`` for
    audio. The segment's own statement of what it carries, where a manifest's
    contentType is optional and often absent."""
    out = []
    for typ, s0, e0 in _scan_boxes(init, 0, len(init)):
        if typ != b"moov":
            continue
        for t1, s1, e1 in _scan_boxes(init, s0, e0):
            if t1 != b"trak":
                continue
            for t2, s2, e2 in _scan_boxes(init, s1, e1):
                if t2 != b"mdia":
                    continue
                for t3, s3, e3 in _scan_boxes(init, s2, e2):
                    if t3 == b"hdlr" and s3 + 12 <= e3:
                        out.append(init[s3 + 8:s3 + 12].decode("latin-1"))
    return out


def file_handlers(path) -> list[str]:
    """:func:`track_handlers` for a whole file: finds ``moov`` by stepping over the
    top-level boxes, since a file written progressively keeps it after ``mdat``."""
    try:
        with open(path, "rb") as fh:
            size = fh.seek(0, 2)
            pos = 0
            while pos + 8 <= size:
                fh.seek(pos)
                head = fh.read(16)
                box, typ = struct.unpack(">I4s", head[:8])
                hdr = 8
                if box == 1 and len(head) == 16:
                    box, hdr = struct.unpack(">Q", head[8:16])[0], 16
                elif box == 0:
                    box = size - pos
                if box < hdr:
                    return []
                if typ == b"moov":
                    if box > MAX_MOOV_BYTES:
                        return []
                    fh.seek(pos)
                    return track_handlers(fh.read(box))
                pos += box
    except (OSError, struct.error):
        pass
    return []


# Box types that can open an ISO-BMFF file (ISO/IEC 14496-12 top-level boxes).
_FIRST_BOXES = {b"ftyp", b"styp", b"moov", b"moof", b"mdat", b"free", b"skip", b"wide",
                b"sidx", b"pdin", b"meta", b"uuid", b"emsg", b"prft"}


def mp4_layout(path) -> dict | None:
    """The top-level shape of an ISO-BMFF (MP4) file, read from its box headers only:
    ``moov`` (a movie header is present), ``mvex`` (that header declares fragments, as
    a DASH initialization segment does), ``moof`` (a fragment follows) and ``cut`` (a
    top-level box runs past the end of the file, so the file stops inside it). None
    when the file does not open with a top-level box type.

    A ``moov`` with ``mvex`` and no ``moof`` is an initialization segment on its own:
    it describes a track and carries no samples, so nothing in it can play."""
    out = {"moov": False, "mvex": False, "moof": False, "cut": False}
    try:
        with open(path, "rb") as fh:
            size = fh.seek(0, 2)
            pos = 0
            while pos + 8 <= size:
                fh.seek(pos)
                head = fh.read(16)
                box, typ = struct.unpack(">I4s", head[:8])
                hdr = 8
                if box == 1 and len(head) == 16:
                    box, hdr = struct.unpack(">Q", head[8:16])[0], 16
                elif box == 0:
                    box = size - pos
                if pos == 0 and typ not in _FIRST_BOXES:
                    return None
                if box < hdr:
                    return {**out, "cut": True}
                if typ == b"moov":
                    out["moov"] = True
                    if box <= MAX_MOOV_BYTES:
                        fh.seek(pos + hdr)
                        body = fh.read(box - hdr)
                        out["mvex"] = any(t == b"mvex" for t, _s, _e in _scan_boxes(body, 0, len(body)))
                elif typ == b"moof":
                    out["moof"] = True
                if pos + box > size:
                    out["cut"] = True
                pos += box
    except (OSError, struct.error):
        return None
    return out


def is_audio_stream(stream: dict) -> bool:
    """True for a planned DASH stream whose initialization segment declares only sound."""
    return stream["handlers"] == ["soun"]


def plan_dash(items: dict) -> tuple[list[dict], dict]:
    """Which joined items make up DASH streams, from the manifests among them.

    ``items`` maps the caller's name for each joined item to
    ``{"key": its cache key or None, "path": the joined file, "complete": bool}``.

    Returns ``(streams, pairs)``. ``streams`` holds, for every cached manifest, the
    streams whose initialization segment and first media segment are both cached and
    complete, with the media segments that follow in the manifest's order up to the
    first one missing or incomplete; one stream per initialization segment, and where
    several manifests list it the longest run wins. Each is ``{"manifest",
    "manifest_key", "rep", "init", "segs", "listed", "handlers"}``.

    ``pairs`` maps each item that is a whole stream by itself (one address fetched by
    byte range) to the manifest that lists it and the other cached whole streams that
    manifest lists, in the manifest's order, so a silent video can say where its
    audio is: ``{"manifest", "manifest_key", "rep", "with"}``.
    """
    by_key = {rec["key"]: ident for ident, rec in items.items() if rec.get("key")}
    best: dict = {}
    pairs: dict = {}
    for ident, rec in items.items():
        key = rec.get("key") or ""
        if not re.match(r"https?://", key):
            continue
        try:
            if os.path.getsize(rec["path"]) > MAX_MANIFEST_BYTES:
                continue
            with open(rec["path"], "rb") as fh:
                data = fh.read(MAX_MANIFEST_BYTES)
        except OSError:
            continue
        if b"<MPD" not in data[:1024]:
            continue
        try:
            reps = representations(data, key)
        except ET.ParseError:
            continue
        singles = [(by_key[r["single"]], r) for r in reps
                   if "single" in r and r["single"] in by_key]
        for ident_s, r in singles:
            pairs.setdefault(ident_s, {"manifest": ident, "manifest_key": key, "rep": r,
                                       "with": [o for o, _ in singles if o != ident_s]})
        for r in reps:
            if "single" in r:
                continue
            init = by_key.get(r["init"])
            if init is None or not items[init].get("complete"):
                continue
            segs = []
            for u in r["media"]:
                s = by_key.get(u)
                if s is None or not items[s].get("complete"):
                    break
                segs.append(s)
            if segs and (init not in best or len(segs) > len(best[init]["segs"])):
                with open(items[init]["path"], "rb") as fh:
                    handlers = track_handlers(fh.read(MAX_MANIFEST_BYTES))
                best[init] = {"manifest": ident, "manifest_key": key, "rep": r, "init": init,
                              "segs": segs, "listed": len(r["media"]), "handlers": handlers}
    return list(best.values()), pairs


def write_stream(paths: Iterable, dest) -> int:
    """An initialization segment and its media segments, in order, into one file:
    DASH defines a representation that way, and fragmented MP4 is built to be read
    that way. Returns the bytes written."""
    total = 0
    with open(dest, "wb") as out:
        for p in paths:
            with open(p, "rb") as fh:
                total += _copy_from(fh, out, 0)
    return total


# ---- putting a video and its audio in one MP4 ---------------------------------
# Put a video-only MP4 and one or more audio-only MP4s into one file, without
# re-encoding.
#
# DASH serves a video and its sound as separate streams, so the ExoPlayer cache holds
# a silent video and a picture-less audio track. This joins them the way a muxer
# would, by rewriting the ISO base media file boxes (ISO/IEC 14496-12) that describe
# the tracks and copying every sample's bytes unchanged:
#
# * **Fragmented** (the ``moov`` holds an ``mvex``, as a DASH initialization segment
#   does): one ``moov`` with every track and every ``trex`` box, an audio track
#   renumbered when it shares another track's id, followed by every ``moof`` + ``mdat``
#   of every input, interleaved by decode time (``tfdt`` over the track's ``mdhd``
#   timescale). A ``trun`` offset counts from its ``moof`` unless ``tfhd`` carries an
#   absolute ``base_data_offset``, which is rewritten; ``mfhd`` sequence numbers are
#   renumbered in the new order. ``styp``, ``sidx`` and the other per-segment boxes
#   are left out: a ``sidx`` indexes one stream's fragments at their old offsets.
# * **Progressive** (a ``moov`` with sample tables): one ``moov`` with every track,
#   then one ``mdat`` holding every input file whole. Each track's chunk offsets
#   (``stco``, rewritten as ``co64``) are shifted by where its file now starts, so
#   they still point at the same bytes. The input ``moov`` boxes ride along inside the
#   ``mdat`` unread, which costs their size and nothing else.
#
# Durations that are counted in the movie timescale (``tkhd``, ``elst``) are moved to
# the video's. Encrypted tracks (a ``sinf`` box) and inputs with more than one track
# are refused: a key cannot be carried over, and which track to take would be a guess.


class MuxError(ValueError):
    """The two inputs cannot be combined; the message says why."""


def _boxes(b: bytes, start: int = 0, end: int | None = None):
    """``(type, start, header length, end)`` for each box in ``b[start:end]``."""
    end = len(b) if end is None else end
    i = start
    while i + 8 <= end:
        size, typ = struct.unpack(">I4s", b[i:i + 8])
        hdr = 8
        if size == 1:
            if i + 16 > end:
                raise MuxError("box header runs past the end")
            size, hdr = struct.unpack(">Q", b[i + 8:i + 16])[0], 16
        elif size == 0:
            size = end - i
        if size < hdr or i + size > end:
            raise MuxError(f"box {typ!r} runs past the end")
        yield typ, i, hdr, i + size
        i += size


def _box(typ: bytes, payload: bytes) -> bytes:
    if len(payload) + 8 <= 0xFFFFFFFF:
        return struct.pack(">I4s", len(payload) + 8, typ) + payload
    return struct.pack(">I4sQ", 1, typ, len(payload) + 16) + payload


def _child(b: bytes, parent, typ: bytes):
    _, s, h, e = parent
    for box in _boxes(b, s + h, e):
        if box[0] == typ:
            return box
    return None


def _path(b: bytes, parent, *types: bytes):
    box = parent
    for t in types:
        box = _child(b, box, t)
        if box is None:
            return None
    return box


def _payload(b: bytes, box) -> bytes:
    return b[box[1] + box[2]:box[3]]


def _top(b: bytes, typ: bytes):
    return next((x for x in _boxes(b) if x[0] == typ), None)


class _Movie:
    """The ``moov`` of one input, with the facts the mux needs."""

    def __init__(self, data: bytes) -> None:
        self.data = data
        self.moov = _top(data, b"moov")
        if self.moov is None:
            raise MuxError("no moov box")
        traks = [x for x in _boxes(data, self.moov[1] + self.moov[2], self.moov[3]) if x[0] == b"trak"]
        if len(traks) != 1:
            raise MuxError(f"{len(traks)} tracks; one was expected")
        self.trak = traks[0]
        if _find_deep(data, self.trak, b"sinf"):
            raise MuxError("the track is encrypted")
        mvhd = _child(data, self.moov, b"mvhd")
        p = _payload(data, mvhd)
        self.timescale = struct.unpack(">I", p[20:24] if p[0] == 1 else p[12:16])[0]
        self.fragmented = _child(data, self.moov, b"mvex") is not None
        tkhd = _child(data, self.trak, b"tkhd")
        tp = _payload(data, tkhd)
        self.track_id = struct.unpack(">I", tp[20:24] if tp[0] == 1 else tp[12:16])[0]
        mdhd = _path(data, self.trak, b"mdia", b"mdhd")
        mp = _payload(data, mdhd)
        self.media_timescale = struct.unpack(">I", mp[20:24] if mp[0] == 1 else mp[12:16])[0]
        hdlr = _path(data, self.trak, b"mdia", b"hdlr")
        self.handler = _payload(data, hdlr)[8:12] if hdlr else b""


def _find_deep(b: bytes, parent, typ: bytes) -> bool:
    containers = {b"trak", b"mdia", b"minf", b"stbl", b"stsd", b"encv", b"enca", b"sinf"}
    _, s, h, e = parent
    start = s + h
    if parent[0] == b"stsd":
        start += 8
    elif parent[0] in (b"encv", b"enca"):
        return True
    try:
        for box in _boxes(b, start, e):
            if box[0] == typ:
                return True
            if box[0] in containers and _find_deep(b, box, typ):
                return True
    except MuxError:
        return False
    return False


# ---- rewriting the boxes that name a track or count in the movie timescale --

def _rescale(v: int, src: int, dst: int) -> int:
    return v if src == dst or src == 0 else v * dst // src


def _tkhd(p: bytes, track_id: int, src_ts: int, dst_ts: int,
          group: int | None = None, enabled: bool | None = None) -> bytes:
    """``tkhd`` renumbered, its duration moved to ``dst_ts``, and optionally put in
    alternate ``group`` and marked enabled or not (flag 0x1)."""
    p = bytearray(p)
    if enabled is not None:
        flags = int.from_bytes(p[1:4], "big")
        p[1:4] = ((flags | 0x1) if enabled else (flags & ~0x1)).to_bytes(3, "big")
    if group is not None:
        g = (36 if p[0] == 1 else 24) + 8 + 2          # after duration, reserved[2] and layer
        p[g:g + 2] = struct.pack(">h", group)
    if p[0] == 1:
        p[20:24] = struct.pack(">I", track_id)
        (d,) = struct.unpack(">Q", p[28:36])
        p[28:36] = struct.pack(">Q", _rescale(d, src_ts, dst_ts))
    else:
        p[12:16] = struct.pack(">I", track_id)
        (d,) = struct.unpack(">I", p[20:24])
        if d != 0xFFFFFFFF:
            p[20:24] = struct.pack(">I", min(_rescale(d, src_ts, dst_ts), 0xFFFFFFFE))
    return bytes(p)


def _elst(p: bytes, src_ts: int, dst_ts: int) -> bytes:
    p = bytearray(p)
    (n,) = struct.unpack(">I", p[4:8])
    wide = p[0] == 1
    step = 20 if wide else 12
    for k in range(n):
        o = 8 + k * step
        if wide:
            (d,) = struct.unpack(">Q", p[o:o + 8])
            p[o:o + 8] = struct.pack(">Q", _rescale(d, src_ts, dst_ts))
        else:
            (d,) = struct.unpack(">I", p[o:o + 4])
            p[o:o + 4] = struct.pack(">I", min(_rescale(d, src_ts, dst_ts), 0xFFFFFFFF))
    return bytes(p)


def _rebuild(b: bytes, box, fix) -> bytes:
    """``box`` re-serialised, with ``fix(type, payload)`` given the chance to replace
    any descendant: None keeps it, a payload replaces the payload, a ``(type,
    payload)`` pair replaces both."""
    typ, s, h, e = box
    containers = {b"trak", b"mdia", b"minf", b"stbl", b"edts", b"dinf", b"mvex", b"moov", b"moof", b"traf"}
    got = fix(typ, b[s + h:e])
    if isinstance(got, tuple):
        return _box(*got)
    if got is not None:
        return _box(typ, got)
    if typ not in containers:
        return b[s:e]
    return _box(typ, b"".join(_rebuild(b, c, fix) for c in _boxes(b, s + h, e)))


def _co64(typ: bytes, p: bytes, shift: int) -> tuple[bytes, bytes]:
    """An ``stco`` or ``co64`` payload as a ``co64`` with every offset moved by ``shift``."""
    (n,) = struct.unpack(">I", p[4:8])
    fmt, width = (">Q", 8) if typ == b"co64" else (">I", 4)
    offs = (struct.unpack(fmt, p[8 + k * width:8 + (k + 1) * width])[0] for k in range(n))
    return b"co64", bytes(4) + struct.pack(">I", n) + b"".join(struct.pack(">Q", o + shift) for o in offs)


def _trak(m: _Movie, track_id: int, dst_ts: int, offset_shift: int | None = None,
          group: int | None = None, enabled: bool | None = None) -> bytes:
    """``m``'s track, renumbered to ``track_id``, its movie-timescale durations moved
    to ``dst_ts``, and with ``offset_shift`` its chunk offsets moved as a ``co64``."""
    def fix(typ: bytes, p: bytes):
        if typ == b"tkhd":
            return _tkhd(p, track_id, m.timescale, dst_ts, group, enabled)
        if typ == b"elst":
            return _elst(p, m.timescale, dst_ts)
        if offset_shift is not None and typ in (b"stco", b"co64"):
            return _co64(typ, p, offset_shift)
        return None

    return _rebuild(m.data, m.trak, fix)


def _mvhd(m: _Movie, next_id: int, duration: int | None = None) -> bytes:
    p = bytearray(_payload(m.data, _child(m.data, m.moov, b"mvhd")))
    p[-4:] = struct.pack(">I", next_id)
    if duration is not None:
        if p[0] == 1:
            p[24:32] = struct.pack(">Q", duration)
        else:
            p[16:20] = struct.pack(">I", min(duration, 0xFFFFFFFF))
    return _box(b"mvhd", bytes(p))


def _duration(m: _Movie, dst_ts: int) -> int:
    p = _payload(m.data, _child(m.data, m.moov, b"mvhd"))
    d = struct.unpack(">Q", p[24:32])[0] if p[0] == 1 else struct.unpack(">I", p[16:20])[0]
    return _rescale(d, m.timescale, dst_ts)


# ---- the two layouts --------------------------------------------------------

def _fragments(m: _Movie, track_id: int) -> list[tuple[float, bytes, int]]:
    """``(decode time in seconds, moof+mdat bytes, where the moof started)`` per fragment,
    the ``tfhd`` already naming ``track_id``."""
    out = []
    boxes = list(_boxes(m.data))
    for i, box in enumerate(boxes):
        if box[0] != b"moof":
            continue
        mdat = boxes[i + 1] if i + 1 < len(boxes) and boxes[i + 1][0] == b"mdat" else None
        if mdat is None:
            raise MuxError("a moof with no mdat after it")
        traf = _child(m.data, box, b"traf")
        tfdt = _child(m.data, traf, b"tfdt") if traf else None
        t = 0.0
        if tfdt:
            p = _payload(m.data, tfdt)
            v = struct.unpack(">Q", p[4:12])[0] if p[0] == 1 else struct.unpack(">I", p[4:8])[0]
            t = v / m.media_timescale
        def fix(typ: bytes, p: bytes):
            if typ == b"tfhd":
                return p[:4] + struct.pack(">I", track_id) + p[8:]
            return None

        out.append((t, _rebuild(m.data, box, fix) + m.data[mdat[1]:mdat[3]], box[1]))
    return out


def _renumber(chunk: bytes, seq: int, new_start: int, old_start: int) -> bytes:
    moof = next(_boxes(chunk))

    def fix(typ: bytes, p: bytes):
        if typ == b"mfhd":
            return p[:4] + struct.pack(">I", seq)
        if typ == b"tfhd":
            (fl,) = struct.unpack(">I", b"\x00" + p[1:4])
            if fl & 0x1:
                (base,) = struct.unpack(">Q", p[8:16])
                return p[:8] + struct.pack(">Q", base - old_start + new_start) + p[16:]
        return None

    out = _rebuild(chunk, moof, fix)
    return out + chunk[moof[3]:]


def mux(video: str | Path, audio, dest: str | Path) -> dict:
    """Write ``video``'s track and the track of each file in ``audio`` (one path or a
    list) into ``dest``. Returns what was done: the layout, the track ids in the
    output, the fragments or the bytes carried. Raises :class:`MuxError` when the
    inputs cannot be combined.

    Several audio tracks are alternatives, one language each: they are put in one
    alternate group and only the first is enabled, so a player starts on it and
    offers the others, the way ffmpeg marks them (checked with ffmpeg 9.0.1: two audio
    tracks, alternate group 1 on both, track flags 0x3 then 0x2, and ffprobe then
    shows the first as the default).
    """
    paths = [audio] if isinstance(audio, (str, Path)) else list(audio)
    if not paths:
        raise MuxError("no audio input")
    v = _Movie(Path(video).read_bytes())
    auds = [_Movie(Path(a).read_bytes()) for a in paths]
    if v.handler != b"vide" or any(a.handler != b"soun" for a in auds):
        raise MuxError("the first input must be video and the second audio")
    if any(a.fragmented != v.fragmented for a in auds):
        raise MuxError("one input is fragmented and the other is not")
    vid = v.track_id
    ids, used = [], {vid}
    for a in auds:
        tid = a.track_id if a.track_id not in used else max(used) + 1
        used.add(tid)
        ids.append(tid)
    next_id = max(used) + 1
    group = 1 if len(auds) > 1 else None

    def atrak(k: int, shift: int | None = None) -> bytes:
        return _trak(auds[k], ids[k], v.timescale, shift, group,
                     (k == 0) if group else None)

    ftyp = _top(v.data, b"ftyp")
    head = v.data[ftyp[1]:ftyp[3]] if ftyp else b""
    dest = Path(dest)
    if v.fragmented:
        trex = []
        for m, tid in [(v, vid), *zip(auds, ids)]:
            box = _path(m.data, m.moov, b"mvex", b"trex")
            if box is None:
                raise MuxError("an mvex with no trex")
            p = bytearray(_payload(m.data, box))
            p[4:8] = struct.pack(">I", tid)
            trex.append(_box(b"trex", bytes(p)))
        mvex = _box(b"mvex", b"".join(trex))
        extra = b"".join(v.data[x[1]:x[3]] for x in _boxes(v.data, v.moov[1] + v.moov[2], v.moov[3])
                         if x[0] not in (b"mvhd", b"trak", b"mvex"))
        moov = _box(b"moov", _mvhd(v, next_id) + _trak(v, vid, v.timescale)
                    + b"".join(atrak(k) for k in range(len(auds))) + mvex + extra)
        frags = [(t, 0, c, s) for t, c, s in _fragments(v, vid)]
        for k, (a, tid) in enumerate(zip(auds, ids), 1):
            frags += [(t, k, c, s) for t, c, s in _fragments(a, tid)]
        frags.sort(key=lambda f: (f[0], f[1]))
        if not frags:
            raise MuxError("no fragments")
        pos = len(head) + len(moov)
        with open(dest, "wb") as out:
            out.write(head)
            out.write(moov)
            for seq, (_t, _which, chunk, old) in enumerate(frags, 1):
                chunk = _renumber(chunk, seq, pos, old)
                out.write(chunk)
                pos += len(chunk)
        return {"layout": "fragmented", "video_track": vid, "audio_tracks": ids,
                "fragments": len(frags), "bytes": pos}
    # progressive: sizes first, since the offsets depend on where the mdat starts
    extra = b"".join(v.data[x[1]:x[3]] for x in _boxes(v.data, v.moov[1] + v.moov[2], v.moov[3])
                     if x[0] not in (b"mvhd", b"trak"))
    duration = max([_duration(v, v.timescale)] + [_duration(a, v.timescale) for a in auds])

    def build(shifts: list[int]) -> bytes:
        return _box(b"moov", _mvhd(v, next_id, duration) + _trak(v, vid, v.timescale, shifts[0])
                    + b"".join(atrak(k, shifts[k + 1]) for k in range(len(auds))) + extra)

    size = len(build([0] * (len(auds) + 1)))
    starts, at = [], len(head) + size + 16              # a 64-bit mdat header
    for m in [v, *auds]:
        starts.append(at)
        at += len(m.data)
    moov = build(starts)
    if len(moov) != size:
        raise MuxError("the header changed size")
    with open(dest, "wb") as out:
        out.write(head)
        out.write(moov)
        out.write(struct.pack(">I4sQ", 1, b"mdat", 16 + sum(len(m.data) for m in [v, *auds])))
        for src in [video, *paths]:
            with open(src, "rb") as fh:
                shutil.copyfileobj(fh, out, 1 << 20)
    return {"layout": "progressive", "video_track": vid, "audio_tracks": ids, "bytes": at}


# ---- caches in a folder ---------------------------------------------------------

class Cache:
    """One cache folder: its pieces grouped by item, and what its index says.

    ``root`` is the folder's path as the evidence names it; ``items`` maps an item
    (an id for v3, a key for v1 and v2) to its :class:`Piece` list; ``index_from``
    says which index named the items and ``entries`` what it said.
    """

    def __init__(self, root: str) -> None:
        self.root = root
        self.version: str | None = None
        self.items: dict = {}
        self.index_files: list = []
        self.uids: list[str] = []
        self.index_from = "no index found"
        self.entries: dict = {}

    def key(self, item):
        """The cache key of ``item``, normally the address it was fetched from."""
        if self.version in ("v1", "v2"):
            return item
        return (self.entries.get(item) or {}).get("key")

    def entry(self, item) -> dict:
        return {} if self.version in ("v1", "v2") else (self.entries.get(item) or {})


def _file_opener(path) -> Callable:
    return lambda: open(path, "rb")


def _resolve_index(c: Cache, tables: dict) -> tuple[str, dict]:
    if c.version in ("v1", "v2"):
        return "file names", {}
    encrypted = False
    # the .bak first: when it exists, AtomicFile restores it over the other
    for logical, real in sorted(c.index_files, key=lambda f: not f[0].endswith(".bak")):
        try:
            got = parse_index_file(Path(real).read_bytes())
        except OSError:
            continue
        if got["state"] == "read":
            return basename(logical), got["entries"]
        if got["state"] == "encrypted":
            encrypted = True
            break
    for uid in c.uids:
        if uid in tables:
            return f"{DB_NAME} table {TABLE_PREFIX}{uid}", tables[uid]
    return ("index encrypted" if encrypted else "no index found"), {}


def group_caches(files: Iterable) -> list[Cache]:
    """The caches among ``files``, an iterable of ``(logical path, real path)``
    pairs: the path the evidence gives a file, and where to read it. Index files and
    index databases among them are read (a database through a temporary copy)."""
    caches: dict = {}
    dbs = []
    for logical, real in files:
        logical = str(logical).replace("\\", "/")
        b = basename(logical)
        if b == DB_NAME:
            dbs.append(real)
            continue
        if b.startswith(DB_NAME) or not is_cache_name(b):
            continue
        root = cache_root(logical)
        c = caches.setdefault(root, Cache(root))
        pn = parse_piece_name(b)
        if pn:
            c.version = "v3" if pn.version == "v3" else (c.version or pn.version)
            try:
                size = os.path.getsize(real)
            except OSError:
                continue
            c.items.setdefault(pn.item, []).append(
                Piece(pn.position, pn.timestamp, size, _file_opener(real), logical))
        elif b in (INDEX_NAME, INDEX_NAME + ".bak"):
            c.index_files.append((logical, real))
        elif UID_FILE.match(b):
            c.uids.append(b[:-4].lower())
    tables: dict = {}
    for real in dbs:
        tables.update(read_index_database(real))
    out = [c for c in caches.values() if c.items]
    for c in out:
        c.index_from, c.entries = _resolve_index(c, tables)
    return sorted(out, key=lambda c: c.root)


def find_caches(folder) -> list[Cache]:
    """:func:`group_caches` over every file under ``folder``, each named by its path
    relative to ``folder``."""
    folder = Path(folder)
    pairs = []
    for dirpath, _dirs, names in os.walk(folder):
        for n in names:
            if is_cache_name(n):
                full = Path(dirpath) / n
                pairs.append((full.relative_to(folder).as_posix(), full))
    return group_caches(pairs)


# ---- rejoining one cache ------------------------------------------------------

def _stem(item) -> str:
    return f"exoplayer_{item}" if isinstance(item, int) else \
        "exoplayer_" + hashlib.sha1(str(item).encode("utf-8", "surrogatepass")).hexdigest()[:12]


def _track(rep: dict, name: str, segments: str | None = None) -> dict:
    t = {"file": name, "lang": rep.get("lang"), "bandwidth": rep.get("bandwidth")}
    if segments:
        t["segments"] = segments
    return {k: v for k, v in t.items() if v}


def rejoin(cache: Cache, out_dir, *, combine: bool = True,
           max_bytes: int = MAX_ITEM_BYTES) -> list[dict]:
    """Join every item of ``cache`` into ``out_dir`` and return one record per item.

    * An item is joined from position 0 until the first gap (:func:`join`); one with
      no piece at position 0 has nothing that can open and is recorded, not written.
    * The items a cached DASH manifest lists as one stream are joined into that
      stream's file (:func:`plan_dash`) instead of being written one by one.
    * With ``combine``, a DASH video is also written with every cached audio stream
      its manifest lists, in one MP4 (:func:`mux`): one audio track, or several
      marked as alternatives with the first one enabled. A whole-file video that is
      cut short is not combined, and a whole-file audio cut short is left out.

    Each record carries ``status`` (``written`` or ``no start``), ``file`` (the name
    in ``out_dir``), ``kind``, ``item``, ``key``, ``key_from``, the join's numbers
    and ``last_touched_ms``, plus ``dash`` or ``combined`` where they apply.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    joined: dict = {}
    for item, pieces in cache.items.items():
        stem = _stem(item)
        entry = cache.entry(item)
        base = {"item": item, "key": cache.key(item),
                "key_from": cache.index_from if cache.key(item) is not None or cache.version != "v3"
                else f"{cache.index_from}; no entry for this id",
                "pieces_total": len(pieces), "cache_folder": cache.root,
                "app_folder": app_folder(cache.root)}
        if not any(p.position == 0 for p in pieces):
            records.append({**base, "status": "no start"})
            continue
        tmp = out_dir / f"{stem}.part"
        with open(tmp, "wb") as out:
            j = join(pieces, out, max_bytes=max_bytes)
        length = entry.get("length")
        joined[item] = {"key": base["key"], "path": tmp, "stem": stem, "base": base,
                        "complete": is_complete(j["bytes"], length, j["gap"]),
                        "pieces": pieces, "j": j, "entry": entry}
    streams, pairs = plan_dash(joined)
    consumed = {i for st in streams for i in [st["init"], *st["segs"]]}
    files: dict = {}
    for st in streams:
        audio = is_audio_stream(st)
        parts = [st["init"], *st["segs"]]
        name = f"{joined[st['init']]['stem']}_dash{'.m4a' if audio else '.mp4'}"
        total = write_stream([joined[i]["path"] for i in parts], out_dir / name)
        files[id(st)] = out_dir / name
        r = st["rep"]
        records.append({
            **joined[st["init"]]["base"], "status": "written", "file": name,
            "kind": "audio" if audio else "video", "key": st["manifest_key"],
            "key_from": f"DASH manifest, cache item {st['manifest']}",
            "dash": {"representation": {k: r[k] for k in
                                        ("id", "lang", "bandwidth", "mime", "codecs", "width", "height")
                                        if r.get(k)},
                     "items": parts, "segments_joined": len(st["segs"]),
                     "segments_listed": st["listed"]},
            "bytes": total,
            "state": "complete" if len(st["segs"]) == st["listed"] else "partial",
            "last_touched_ms": max(p.timestamp for i in parts for p in joined[i]["pieces"]),
        })
    if combine:
        for st in streams:
            if is_audio_stream(st):
                continue
            sound = sorted((o for o in streams if o["manifest"] == st["manifest"]
                            and is_audio_stream(o)), key=lambda o: o["rep"].get("order", 0))
            if not sound:
                continue
            name = f"{joined[st['init']]['stem']}_av.mp4"
            _combine_into(records, out_dir / name, files[id(st)], [files[id(a)] for a in sound], {
                **joined[st["init"]]["base"], "key": st["manifest_key"],
                "key_from": f"DASH manifest, cache item {st['manifest']}",
                "combined": {"video": files[id(st)].name,
                             "video_segments": f"{len(st['segs'])} of {st['listed']}",
                             "audio_tracks": [_track(a["rep"], files[id(a)].name,
                                                     f"{len(a['segs'])} of {a['listed']}")
                                              for a in sound]},
                "last_touched_ms": max(p.timestamp for x in [st, *sound]
                                       for i in [x["init"], *x["segs"]] for p in joined[i]["pieces"]),
            })
    for item, rec in joined.items():
        if item in consumed:
            with contextlib.suppress(OSError):
                rec["path"].unlink()
            continue
        kind, ext = sniff(rec["path"])
        dest = rec["path"].with_name(rec["stem"] + ext)
        rec["path"].replace(dest)
        rec["path"], rec["kind"] = dest, kind
        j, length = rec["j"], rec["entry"].get("length")
        r = {**rec["base"], "status": "written", "file": dest.name, "kind": kind,
             "pieces_joined": len(j["used"]), "pieces_left_out": j["left_out"],
             "bytes": j["bytes"], "length_recorded": length, "gap_at": j["gap"],
             "state": item_state(j["bytes"], length, j["gap"]),
             "last_touched_ms": max(p.timestamp for p in j["used"])}
        if rec["entry"].get("redirected_to"):
            r["redirected_to"] = rec["entry"]["redirected_to"]
        if item in pairs:
            pr = pairs[item]
            r["manifest_key"] = pr["manifest_key"]
            r["representation"] = {k: v for k, v in pr["rep"].items()
                                   if k in ("id", "lang", "bandwidth", "mime", "codecs", "width", "height") and v}
        records.append(r)
    if combine:
        for item, rec in joined.items():
            if item in consumed or rec.get("kind") != "video" or item not in pairs:
                continue
            sound = [o for o in pairs[item]["with"] if joined[o].get("kind") == "audio"]
            if not sound:
                continue
            whole = [o for o in sound if joined[o]["complete"]]
            if not rec["complete"] or not whole:
                continue
            _combine_into(records, out_dir / f"{rec['stem']}_av.mp4", rec["path"],
                          [joined[o]["path"] for o in whole], {
                              **rec["base"], "key": pairs[item]["manifest_key"],
                              "key_from": f"DASH manifest, cache item {pairs[item]['manifest']}",
                              "combined": {"video": rec["path"].name,
                                           "audio_tracks": [_track(pairs[o]["rep"], joined[o]["path"].name)
                                                            for o in whole],
                                           "audio_left_out": len(sound) - len(whole)},
                              "last_touched_ms": max(p.timestamp for i in (item, *whole)
                                                     for p in joined[i]["pieces"]),
                          })
    return records


def _combine_into(records: list, dest: Path, video: Path, audios: list, record: dict) -> None:
    try:
        done = mux(video, audios, dest)
    except (MuxError, OSError, struct.error) as exc:
        with contextlib.suppress(OSError):
            dest.unlink()
        records.append({**record, "status": "not combined", "reason": str(exc)})
        return
    record["combined"]["layout"] = done["layout"]
    records.append({**record, "status": "written", "file": dest.name, "kind": "video",
                    "bytes": done["bytes"]})


# ---- command line ---------------------------------------------------------------

def _when(ms) -> str:
    import datetime
    try:
        return datetime.datetime.fromtimestamp(ms / 1000, datetime.timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S UTC")
    except (TypeError, OverflowError, OSError, ValueError):
        return ""


def _cmd_scan(args) -> int:
    caches = find_caches(args.folder)
    for c in caches:
        print(f"{c.root}  ({c.version}, {len(c.items)} items, index: {c.index_from})")
        for item, pieces in sorted(c.items.items(), key=lambda kv: str(kv[0])):
            e = c.entry(item)
            size = sum(p.size for p in pieces)
            start = "" if any(p.position == 0 for p in pieces) else "  [no piece at position 0]"
            length = f" of {e['length']:,}" if e.get("length") is not None else ""
            print(f"  {item}: {len(pieces)} piece(s), {size:,} bytes{length}, key {c.key(item)}{start}")
    if not caches:
        print("no ExoPlayer cache found")
    return 0


def _cmd_rejoin(args) -> int:
    out = Path(args.output)
    report = []
    for c in find_caches(args.folder):
        tag = hashlib.sha1(c.root.encode("utf-8", "surrogatepass")).hexdigest()[:10]
        recs = rejoin(c, out / tag, combine=not args.no_combine)
        for r in recs:
            r["folder"] = tag
        report += recs
        written = sum(r["status"] == "written" for r in recs)
        print(f"{c.root} -> {tag}/: {written} file(s) written, "
              f"{sum(r['status'] == 'no start' for r in recs)} item(s) with no start")
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(json.dumps(report, indent=1, default=str), encoding="utf-8")
    print(f"report: {out / 'report.json'}")
    return 0


def _cmd_mux(args) -> int:
    try:
        done = mux(args.video, args.audio, args.output)
    except MuxError as exc:
        print(f"cannot combine: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(done))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="exoprobe", description=__doc__.split("\n\n")[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", action="version", version=f"exoprobe {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("scan", help="list every cache, item, key and state under a folder")
    p.add_argument("folder")
    p.set_defaults(func=_cmd_scan)
    p = sub.add_parser("rejoin", help="write every cache's joined media and a report.json")
    p.add_argument("folder")
    p.add_argument("-o", "--output", required=True, help="a folder to write into")
    p.add_argument("--no-combine", action="store_true", help="do not put video and audio in one file")
    p.set_defaults(func=_cmd_rejoin)
    p = sub.add_parser("mux", help="put a video-only MP4 and one or more audio-only MP4s in one file")
    p.add_argument("video")
    p.add_argument("audio", nargs="+")
    p.add_argument("-o", "--output", required=True)
    p.set_defaults(func=_cmd_mux)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
