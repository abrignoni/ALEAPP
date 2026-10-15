"""chromiumcacheprobe: read Chromium Simple Cache entries and rebuild cached H.264 video.

Reads the disk cache that Chrome and other Chromium browsers keep on Android
(``cache/Cache`` or ``cache/Cache/Cache_Data``): entry keys, the HTTP response metadata in stream 0, the body
in stream 1, sparse range files (``_s``) and the cache index. From the MP4 fragments
found in those bodies it rebuilds playable MP4 files. Sample bytes are copied as
stored; only the container around them is written. No decoder is run.

Standard library only. Brotli-encoded bodies are decoded when the optional
``brotli`` package is installed and reported as undecodable otherwise.

The recovery engine was written by Forensik.IT GmbH (@ForensikITGmbH) and first
submitted to ALEAPP as abrignoni/ALEAPP#1721.

Format references (Chromium commits as pinned in the README):
  Simple Cache entry layout   net/disk_cache/simple/simple_entry_format.h
  Entry and index file names  net/disk_cache/simple/simple_util.cc, simple_index_file.cc
  Simple Cache index          net/disk_cache/simple/simple_index.cc
  HTTP response metadata      net/http/http_response_info.cc
  ISO BMFF fragments          W3C MSE byte stream format for ISO BMFF

MIT licence. https://github.com/abrignoni/chromiumcacheprobe
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass, field
import datetime
from fractions import Fraction
import hashlib
import json
import mmap
import os
import sys
import tempfile
from pathlib import Path
import re
import struct
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
import zlib

__version__ = "0.1.0"
VERSION = __version__
MAX_CLIP_BYTES = 128 * 1024 * 1024
INITIAL_MAGIC = 0xFCFB6D1BA7725C30
FINAL_MAGIC = 0xF4FA6F45970D41D8
SPARSE_MAGIC = 0xEB97BF016553676B
IDENTITY = (0x10000, 0, 0, 0, 0x10000, 0, 0, 0, 0x40000000)
MAX_BOX_META = 32 * 1024 * 1024


class FormatError(Exception):
    """Messages are fixed diagnostic codes, never input text."""


class Cancelled(Exception):
    pass


def check_stop(stop):
    if stop and stop.is_set():
        raise Cancelled()


def u32(b, p=0):
    return struct.unpack_from(">I", b, p)[0]


def atom(kind, *payload):
    body = b"".join(payload)
    return struct.pack(">I4s", len(body) + 8, kind) + body


def full(kind, version, flags, *payload):
    return atom(kind, bytes([version]) + flags.to_bytes(3, "big"), *payload)


def bounds(data, pos, end=None):
    end = len(data) if end is None else end
    if pos < 0 or pos + 8 > end:
        raise FormatError("box_header_incomplete")
    size, kind = struct.unpack_from(">I4s", data, pos)
    header = 8
    if size == 1:
        if pos + 16 > end:
            raise FormatError("box_header_incomplete")
        size = struct.unpack_from(">Q", data, pos + 8)[0]
        header = 16
    elif size == 0:
        size = end - pos
    if size < header or pos + size > end:
        raise FormatError("box_incomplete")
    return pos, kind, size, header


def boxes(data, start=0, end=None):
    end = len(data) if end is None else end
    while start < end:
        item = bounds(data, start, end)
        yield item
        start += item[2]


def children(data):
    h = bounds(data, 0)[3]
    return list(boxes(data, h))


def child(data, kind):
    for p, t, n, _h in children(data):
        if t == kind:
            return data[p : p + n]
    return None


def read_at(path, offset, size):
    with open(path, "rb") as f:
        f.seek(offset)
        data = f.read(size)
    if len(data) != size:
        raise FormatError("source_changed_or_truncated")
    return data


def file_hash(path, stop=None):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        while data := f.read(1024 * 1024):
            check_stop(stop)
            digest.update(data)
    return digest.hexdigest()


def resource_key(url, path):
    """Conservative grouping: preserve host, rendition and unknown query fields."""
    if url:
        try:
            p = urlsplit(url)
            pathname = re.sub(r"_part\d+(?=\.[^/]+$|$)", "", p.path, flags=re.I)
            query = [
                (k, v)
                for k, v in parse_qsl(p.query, keep_blank_values=True)
                if k.lower() not in {"bytestart", "byteend", "range"}
            ]
            return "url:" + urlunsplit(
                (p.scheme, p.netloc, pathname, urlencode(query), "")
            )
        except ValueError:
            pass
    name = re.sub(r"_part\d+(?=\.[^.]+$|$)", "", path.name, flags=re.I)
    return "file:" + str(path.parent / name)


@dataclass
class Span:
    start: int
    end: int
    method: str
    logical_offset: int = 0


def cache_spans(data):
    """Return structurally bounded payload spans, or a carving fallback."""
    size = len(data)
    if size < 24 or struct.unpack_from("<Q", data, 0)[0] != INITIAL_MAGIC:
        return "", [Span(0, size, "raw_carving")], None
    _, version, keylen, _, _ = struct.unpack_from("<QIIII", data, 0)
    if keylen > 1024 * 1024 or 24 + keylen > size:
        return "", [Span(0, size, "invalid_cache_header_carving")], version
    key = bytes(data[24 : 24 + keylen]).decode("utf-8", "replace")
    # Partitioned keys can contain multiple origins: the last URL is the resource.
    urls = re.findall(r"https?://[^\s\x00]+", key)
    url = urls[-1] if urls else ""
    begin = 24 + keylen
    if begin + 32 <= size and struct.unpack_from("<Q", data, begin)[0] == SPARSE_MAGIC:
        spans = []
        p = begin
        while p + 32 <= size:
            magic, offset, length, _crc, _padding = struct.unpack_from(
                "<QQQII", data, p
            )
            if magic != SPARSE_MAGIC or length > size - p - 32:
                break
            spans.append(Span(p + 32, p + 32 + length, "simple_sparse_range", offset))
            p += 32 + length
        return url, spans, version
    if size >= begin + 48:
        magic, flags, _crc, n0, _padding = struct.unpack_from("<QIIII", data, size - 24)
        if magic == FINAL_MAGIC:
            e1 = size - 24 - (32 if flags & 2 else 0) - n0 - 24
            if begin <= e1 and struct.unpack_from("<Q", data, e1)[0] == FINAL_MAGIC:
                return url, [Span(begin, e1, "simple_stream1")], version
    return url, [Span(begin, size, "cache_payload_carving")], version


@dataclass
class Sample:
    path: Path
    offset: int
    size: int
    dur: int
    dts: int
    flags: int
    cto: int
    source: str
    sync: bool = False
    config: tuple | None = None


@dataclass
class Track:
    tid: int
    timescale: int
    codec: str
    width: int = 0
    height: int = 0
    sps: bytes = b""
    pps: bytes = b""
    nal_length: int = 4
    asc: bytes = b""
    channels: int = 2
    rate: int = 48000
    matrix: tuple = IDENTITY
    defaults: dict = field(default_factory=dict)
    original: bool = False
    handler: str = ""


@dataclass
class Fragment:
    path: Path
    source: str
    group: str
    moof: int
    moof_size: int
    mdat: int
    mdat_size: int
    mdat_header: int
    scales: dict
    digest: str


class Bits:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def get(self, n=1):
        if n < 0 or self.pos + n > len(self.data) * 8:
            raise FormatError("sps_incomplete")
        value = 0
        for _ in range(n):
            value = (value << 1) | (
                (self.data[self.pos // 8] >> (7 - self.pos % 8)) & 1
            )
            self.pos += 1
        return value

    def ue(self):
        n = 0
        while self.get() == 0:
            n += 1
            if n > 31:
                raise FormatError("sps_invalid")
        return (1 << n) - 1 + self.get(n)

    def se(self):
        v = self.ue()
        return (v + 1) // 2 if v & 1 else -(v // 2)


def sps_dimensions(sps):
    if not sps or sps[0] & 31 != 7:
        raise FormatError("sps_missing")
    rbsp = re.sub(b"\x00\x00\x03", b"\x00\x00", sps[1:])
    b = Bits(rbsp)
    profile = b.get(8)
    b.get(16)
    b.ue()
    chroma, separate = 1, 0
    if profile in {100, 110, 122, 244, 44, 83, 86, 118, 128, 138, 139, 134, 135}:
        chroma = b.ue()
        if chroma > 3:
            raise FormatError("sps_chroma_invalid")
        if chroma == 3:
            separate = b.get()
        b.ue()
        b.ue()
        b.get()
        if b.get():
            for i in range(8 if chroma != 3 else 12):
                if b.get():
                    last = nxt = 8
                    for _ in range(16 if i < 6 else 64):
                        if nxt:
                            nxt = (last + b.se() + 256) % 256
                        last = nxt or last
    b.ue()
    order = b.ue()
    if order == 0:
        b.ue()
    elif order == 1:
        b.get()
        b.se()
        b.se()
        count = b.ue()
        if count > 256:
            raise FormatError("sps_invalid")
        for _ in range(count):
            b.se()
    elif order > 2:
        raise FormatError("sps_invalid")
    b.ue()
    b.get()
    w, h = (b.ue() + 1) * 16, (b.ue() + 1) * 16
    frame = b.get()
    if not frame:
        b.get()
    b.get()
    left = right = top = bottom = 0
    if b.get():
        left, right, top, bottom = (b.ue() for _ in range(4))
    chroma_array = 0 if separate else chroma
    subw = 2 if chroma_array in (1, 2) else 1
    subh = 2 if chroma_array == 1 else 1
    cropx = subw if chroma_array else 1
    cropy = subh * (2 - frame) if chroma_array else 2 - frame
    w -= (left + right) * cropx
    h = h * (2 - frame) - (top + bottom) * cropy
    if not (0 < w <= 16384 and 0 < h <= 16384):
        raise FormatError("sps_dimensions_invalid")
    return w, h


def nals(data, length_size=4):
    p, items = 0, []
    while p < len(data):
        if p + length_size > len(data):
            raise FormatError("h264_sample_invalid")
        n = int.from_bytes(data[p : p + length_size], "big")
        p += length_size
        if not n or p + n > len(data):
            raise FormatError("h264_sample_invalid")
        nal = data[p : p + n]
        if nal[0] & 0x80 or not 1 <= (nal[0] & 31) <= 23:
            raise FormatError("h264_sample_invalid")
        items.append(nal)
        p += n
    return items


def parse_sidx(data):
    result = {}
    for p, t, n, h in boxes(data):
        if t != b"sidx":
            continue
        b = data[p + h : p + n]
        if len(b) < 20 or b[0] not in (0, 1):
            raise FormatError("sidx_header_invalid")
        tid, scale = struct.unpack_from(">II", b, 4)
        if scale:
            result[tid] = scale
    return result


def descriptor(tag, data):
    n = len(data)
    seq = [n & 127]
    n >>= 7
    while n:
        seq.insert(0, 128 | (n & 127))
        n >>= 7
    return bytes([tag] + seq) + data


def get_asc(esds):
    def get(data, p):
        tag = data[p]
        p += 1
        size = 0
        for _ in range(4):
            v = data[p]
            p += 1
            size = (size << 7) | (v & 127)
            if not v & 128:
                break
        if p + size > len(data):
            raise FormatError("esds_invalid")
        return tag, data[p : p + size], p + size

    try:
        tag, es, _end = get(esds[12:], 0)
        if tag != 3 or len(es) < 3:
            return b""
        flags, p = es[2], 3
        if flags & 0x80:
            p += 2
        if flags & 0x40:
            p += 1 + es[p]
        if flags & 0x20:
            p += 2
        tag, dec, _end = get(es, p)
        if tag != 4 or len(dec) < 13 or dec[0] != 0x40:
            return b""
        tag, asc, _end = get(dec, 13)
        return asc if tag == 5 else b""
    except (IndexError, FormatError):
        return b""


def parse_init(moov):
    tracks = {}
    defaults = {}
    mvex = child(moov, b"mvex")
    if mvex:
        for p, t, n, h in children(mvex):
            if t == b"trex" and n >= 32:
                tid, _desc, dur, size, flags = struct.unpack_from(
                    ">5I", mvex, p + h + 4
                )
                defaults[tid] = dict(dur=dur, size=size, flags=flags)
    for p, t, n, h in children(moov):
        if t != b"trak":
            continue
        trak = moov[p : p + n]
        tkhd, mdia = child(trak, b"tkhd"), child(trak, b"mdia")
        if not tkhd or not mdia:
            continue
        mdhd, hdlr, minf = (
            child(mdia, b"mdhd"),
            child(mdia, b"hdlr"),
            child(mdia, b"minf"),
        )
        if not mdhd or not hdlr or not minf:
            continue
        tid = u32(tkhd, 28 if tkhd[8] else 20)
        scale = u32(mdhd, 28 if mdhd[8] else 20)
        if not scale:
            continue
        matrix_at = 60 if tkhd[8] else 48
        matrix = struct.unpack_from(">9I", tkhd, matrix_at)
        stbl = child(minf, b"stbl")
        stsd = child(stbl, b"stsd") if stbl else None
        if not stsd or len(stsd) < 24 or u32(stsd, 12) != 1:
            continue
        ep, et, en, _eh = bounds(stsd, 16)
        entry = stsd[ep : ep + en]
        tr = Track(
            tid,
            scale,
            et.decode("ascii", "replace"),
            matrix=matrix,
            defaults=defaults.get(tid, {}),
            original=True,
            handler=hdlr[16:20].decode("ascii", "replace"),
        )
        if et in (b"avc1", b"avc3"):
            tr.width, tr.height = struct.unpack_from(">HH", entry, 32)
            for q, qt, qn, qh in boxes(entry, 86):
                if qt != b"avcC":
                    continue
                avcc = entry[q + qh : q + qn]
                if len(avcc) < 7:
                    continue
                tr.nal_length = (avcc[4] & 3) + 1
                r = 6
                spslist = []
                ppslist = []
                for _ in range(avcc[5] & 31):
                    length = int.from_bytes(avcc[r : r + 2], "big")
                    r += 2
                    spslist.append(avcc[r : r + length])
                    r += length
                count = avcc[r]
                r += 1
                for _ in range(count):
                    length = int.from_bytes(avcc[r : r + 2], "big")
                    r += 2
                    ppslist.append(avcc[r : r + length])
                    r += length
                # Multiple parameter sets require broader sample-description handling.
                if len(spslist) == len(ppslist) == 1:
                    tr.sps, tr.pps = spslist[0], ppslist[0]
                    tr.width, tr.height = sps_dimensions(tr.sps)
        elif et == b"mp4a":
            if len(entry) >= 36 and int.from_bytes(entry[16:18], "big") == 0:
                tr.channels = int.from_bytes(entry[24:26], "big")
                tr.rate = u32(entry, 32) >> 16
                for q, qt, qn, qh in boxes(entry, 36):
                    if qt == b"esds":
                        tr.asc = get_asc(entry[q : q + qn])
        tracks[tid] = tr
    return tracks


def parse_fragment(frag, init):
    data = read_at(frag.path, frag.moof, frag.moof_size)
    result = {}
    sequence = None
    previous_end = frag.moof
    for p, typ, size, hdr in children(data):
        if typ == b"mfhd":
            sequence = u32(data, p + hdr + 4)
        if typ != b"traf":
            continue
        traf = data[p : p + size]
        if any(t in (b"senc", b"saiz", b"saio") for _, t, _, _ in children(traf)):
            raise FormatError("encrypted_or_auxiliary_samples_unsupported")
        tfhd, tfdt = child(traf, b"tfhd"), child(traf, b"tfdt")
        if not tfhd or not tfdt:
            raise FormatError("fragment_header_missing")
        flags = int.from_bytes(tfhd[9:12], "big")
        tid = u32(tfhd, 12)
        if tid in result:
            raise FormatError("multiple_traf_same_track_unsupported")
        default = dict(init[tid].defaults) if tid in init else {}
        r = 16
        if flags & 1:
            raise FormatError("absolute_data_offsets_unsupported")
        if flags & 2:
            if u32(tfhd, r) != 1:
                raise FormatError("sample_description_index_unsupported")
            r += 4
        for bit, name in ((8, "dur"), (16, "size"), (32, "flags")):
            if flags & bit:
                default[name] = u32(tfhd, r)
                r += 4
        dts = struct.unpack_from(">Q" if tfdt[8] else ">I", tfdt, 12)[0]
        base = frag.moof if flags & 0x20000 or not result else previous_end
        cursor = None
        samples = []
        for q, kind, n, _h in children(traf):
            if kind != b"trun":
                continue
            b = traf[q : q + n]
            fl = int.from_bytes(b[9:12], "big")
            count, r = u32(b, 12), 16
            if count > 250000:
                raise FormatError("sample_limit")
            if fl & 1:
                cursor = base + struct.unpack_from(">i", b, r)[0]
                r += 4
            elif cursor is None:
                raise FormatError("implicit_data_offset_unsupported")
            firstflags = None
            if fl & 4:
                firstflags = u32(b, r)
                r += 4
            for i in range(count):
                values = dict(default)
                values["cto"] = 0
                for bit, name in (
                    (0x100, "dur"),
                    (0x200, "size"),
                    (0x400, "flags"),
                    (0x800, "cto"),
                ):
                    if fl & bit:
                        fmt = ">i" if name == "cto" and b[8] == 1 else ">I"
                        values[name] = struct.unpack_from(fmt, b, r)[0]
                        r += 4
                if i == 0 and firstflags is not None:
                    values["flags"] = firstflags
                dur, sz = values.get("dur", 0), values.get("size", 0)
                if not dur or not sz:
                    raise FormatError("sample_defaults_missing")
                if (
                    cursor < frag.mdat + frag.mdat_header
                    or cursor + sz > frag.mdat + frag.mdat_size
                ):
                    raise FormatError("sample_outside_mdat")
                samples.append(
                    Sample(
                        frag.path,
                        cursor,
                        sz,
                        dur,
                        dts,
                        values.get("flags", 0),
                        values["cto"],
                        frag.source,
                    )
                )
                cursor += sz
                dts += dur
            if r != len(b):
                raise FormatError("trun_size_mismatch")
        if not samples:
            raise FormatError("empty_track_fragment")
        previous_end = cursor
        result[tid] = samples
    if not result:
        raise FormatError("no_track_fragments")
    intervals = sorted(
        (s.offset, s.offset + s.size) for ss in result.values() for s in ss
    )
    if any(a[1] > b[0] for a, b in zip(intervals, intervals[1:])):
        raise FormatError("overlapping_sample_ranges")
    return sequence, result


def sample_entry(track):
    if track.codec == "h264":
        sps, pps = track.sps, track.pps
        if len(sps) < 4 or not pps:
            raise FormatError("decoder_parameters_missing")
        avcc = atom(
            b"avcC",
            bytes([1, sps[1], sps[2], sps[3], 0xFC | (track.nal_length - 1), 0xE1]),
            struct.pack(">H", len(sps)),
            sps,
            b"\x01",
            struct.pack(">H", len(pps)),
            pps,
        )
        body = b"\0" * 6 + struct.pack(">H", 1) + b"\0" * 16
        body += struct.pack(">HHII", track.width, track.height, 0x480000, 0x480000)
        body += (
            b"\0" * 4 + struct.pack(">H", 1) + b"\0" * 32 + struct.pack(">Hh", 24, -1)
        )
        return atom(b"avc1", body, avcc)
    dec = descriptor(4, b"\x40\x15" + b"\0" * 11 + descriptor(5, track.asc))
    esds = full(
        b"esds",
        0,
        0,
        descriptor(3, struct.pack(">HB", track.tid, 0) + dec + descriptor(6, b"\x02")),
    )
    body = b"\0" * 6 + struct.pack(">H", 1) + b"\0" * 8
    body += struct.pack(
        ">HHHHI", track.channels, 16, 0, 0, min(track.rate, 65535) << 16
    )
    return atom(b"mp4a", body, esds)


def runs(values):
    result = []
    for value in values:
        if result and result[-1][1] == value:
            result[-1] = (result[-1][0] + 1, value)
        else:
            result.append((1, value))
    return result


def make_moov(track_samples, offsets):
    movie_scale = 1000000
    origin = min(
        Fraction(samples[0].dts, track.timescale) for track, samples in track_samples
    )
    traks, ends = [], []
    for track, samples in track_samples:
        delay = round(
            (Fraction(samples[0].dts, track.timescale) - origin) * movie_scale
        )
        media_dur = sum(s.dur for s in samples)
        present_dur = max(s.dts - samples[0].dts + s.cto + s.dur for s in samples)
        presentation = round(Fraction(present_dur, track.timescale) * movie_scale)
        end = delay + presentation
        ends.append(end)
        if media_dur >= 2**32 or end >= 2**32:
            raise FormatError("clip_duration_limit")
        width, height = (track.width, track.height) if track.codec == "h264" else (0, 0)
        tkhd = full(
            b"tkhd",
            0,
            3,
            struct.pack(">IIIII", 0, 0, track.tid, 0, end),
            b"\0" * 8,
            struct.pack(">hhhH", 0, 0, 0 if track.codec == "h264" else 0x100, 0),
            struct.pack(">9I", *track.matrix),
            struct.pack(">II", width << 16, height << 16),
        )
        edits = []
        if delay:
            edits.append(struct.pack(">IiHH", delay, -1, 1, 0))
        edits.append(struct.pack(">IiHH", presentation, 0, 1, 0))
        edts = atom(b"edts", full(b"elst", 0, 0, struct.pack(">I", len(edits)), *edits))
        mdhd = full(
            b"mdhd",
            0,
            0,
            struct.pack(">IIIIHH", 0, 0, track.timescale, media_dur, 0x55C4, 0),
        )
        hdlr = full(
            b"hdlr",
            0,
            0,
            b"\0" * 4,
            b"vide" if track.codec == "h264" else b"soun",
            b"\0" * 12,
            b"Recovered\0",
        )
        timings = runs(s.dur for s in samples)
        stts = full(
            b"stts",
            0,
            0,
            struct.pack(">I", len(timings)),
            *(struct.pack(">II", *r) for r in timings),
        )
        stsc = full(b"stsc", 0, 0, struct.pack(">4I", 1, 1, 1, 1))
        stsz = full(
            b"stsz",
            0,
            0,
            struct.pack(">II", 0, len(samples)),
            *(struct.pack(">I", s.size) for s in samples),
        )
        positions = offsets[track.tid]
        wide = max(positions) >= 2**32
        stco = full(
            b"co64" if wide else b"stco",
            0,
            0,
            struct.pack(">I", len(positions)),
            *(struct.pack(">Q" if wide else ">I", p) for p in positions),
        )
        extra = []
        if any(s.cto for s in samples):
            version = 1 if any(s.cto < 0 for s in samples) else 0
            ctos = runs(s.cto for s in samples)
            extra.append(
                full(
                    b"ctts",
                    version,
                    0,
                    struct.pack(">I", len(ctos)),
                    *(struct.pack(">Ii" if version else ">II", *r) for r in ctos),
                )
            )
        if track.codec == "h264":
            sync = [i + 1 for i, s in enumerate(samples) if s.sync]
            extra.append(
                full(
                    b"stss",
                    0,
                    0,
                    struct.pack(">I", len(sync)),
                    *(struct.pack(">I", i) for i in sync),
                )
            )
        stbl = atom(
            b"stbl",
            full(b"stsd", 0, 0, struct.pack(">I", 1), sample_entry(track)),
            stts,
            stsc,
            stsz,
            stco,
            *extra,
        )
        dinf = atom(
            b"dinf", full(b"dref", 0, 0, struct.pack(">I", 1), full(b"url ", 0, 1))
        )
        mh = (
            full(b"vmhd", 0, 1, b"\0" * 8)
            if track.codec == "h264"
            else full(b"smhd", 0, 0, b"\0" * 4)
        )
        traks.append(
            atom(
                b"trak",
                tkhd,
                edts,
                atom(b"mdia", mdhd, hdlr, atom(b"minf", mh, dinf, stbl)),
            )
        )
    mvhd = full(
        b"mvhd",
        0,
        0,
        struct.pack(">IIII", 0, 0, movie_scale, max(ends)),
        struct.pack(">IH", 0x10000, 0x100),
        b"\0" * 10,
        struct.pack(">9I", *IDENTITY),
        b"\0" * 24,
        struct.pack(">I", max(t.tid for t, s in track_samples) + 1),
    )
    return atom(b"moov", mvhd, *traks)


def write_mp4(destination, track_samples, stop=None):
    """Write progressive MP4 and independently verify every copied sample byte."""
    tmp = destination.with_suffix(".partial")
    ftyp = atom(b"ftyp", b"isom", struct.pack(">I", 512), b"isomiso2avc1mp41")
    total = sum(s.size for t, ss in track_samples for s in ss)
    if total > MAX_CLIP_BYTES - MAX_BOX_META:
        raise FormatError("clip_size_limit")
    mh = (
        struct.pack(">I4s", total + 8, b"mdat")
        if total + 8 < 2**32
        else struct.pack(">I4sQ", 1, b"mdat", total + 16)
    )
    offsets, expected = {}, {}
    handles = {}
    try:
        with open(tmp, "xb") as out:
            out.write(ftyp)
            out.write(mh)
            for track, samples in track_samples:
                positions, hashes = [], []
                for s in samples:
                    check_stop(stop)
                    if s.path not in handles:
                        # Bound open handles even in a large cache.
                        if len(handles) >= 32:
                            _, old = handles.popitem()
                            old.close()
                        handles[s.path] = open(s.path, "rb")
                    f = handles[s.path]
                    f.seek(s.offset)
                    data = f.read(s.size)
                    if len(data) != s.size:
                        raise FormatError("source_changed_or_truncated")
                    positions.append(out.tell())
                    hashes.append(hashlib.sha256(data).hexdigest())
                    out.write(data)
                offsets[track.tid], expected[track.tid] = positions, hashes
            out.write(make_moov(track_samples, offsets))
        with open(tmp, "rb") as verify:
            for track, samples in track_samples:
                for s, position, digest in zip(
                    samples, offsets[track.tid], expected[track.tid]
                ):
                    check_stop(stop)
                    verify.seek(position)
                    if hashlib.sha256(verify.read(s.size)).hexdigest() != digest:
                        raise FormatError("output_sample_verification_failed")
        tmp.replace(destination)
        return {
            str(t.tid): {"count": len(ss), "sample_sha256": expected[t.tid]}
            for t, ss in track_samples
        }
    finally:
        for f in handles.values():
            f.close()
        if tmp.exists():
            tmp.unlink()


def scan_file(path, source, stats, stop):
    fragments, inits, complete = [], [], []
    with open(path, "rb") as handle:
        if os.fstat(handle.fileno()).st_size == 0:
            return fragments, inits, complete, ""
        with mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ) as data:
            url, spans, version = cache_spans(data)
            if version is not None:
                stats["simple_cache_files"] += 1
            group = str(Path(source).parent) + "\x00" + resource_key(url, Path(source))
            if version is not None:
                key_length = struct.unpack_from("<I", data, 12)[0]
                if 24 + key_length <= len(data):
                    raw_key = bytes(data[24 : 24 + key_length]).decode(
                        "utf-8", "replace"
                    )
                    # Keep cache partitions separate even when the resource URL matches.
                    partition = raw_key.rsplit(url, 1)[0] if url else raw_key
                    group = (
                        str(Path(source).parent)
                        + "\x00"
                        + partition
                        + "\x00"
                        + resource_key(url, Path(source))
                    )
            for span in spans:
                check_stop(stop)
                stats["span_" + span.method] += 1
                # Scan atom signatures, but accept only bounded, structurally parsed boxes.
                found = {b"moof": [], b"moov": [], b"ftyp": [], b"sidx": []}
                for kind in found:
                    at = span.start
                    while True:
                        at = data.find(kind, at, span.end)
                        if at < 0:
                            break
                        check_stop(stop)
                        p = at - 4
                        at += 4
                        if p < span.start:
                            continue
                        try:
                            item = bounds(data, p, span.end)
                            if item[1] == kind and 8 < item[2] <= MAX_BOX_META:
                                found[kind].append(item)
                        except FormatError:
                            if kind == b"moof":
                                stats["incomplete_moof_candidates"] += 1
                valid_inits = {}
                video_inits = set()
                for p, kind, n, _h in found[b"moov"]:
                    try:
                        blob = bytes(data[p : p + n])
                        tracks = parse_init(blob)
                        if tracks:
                            inits.append((group, tracks, source))
                            valid_inits[p] = blob
                            if any(t.handler == "vide" for t in tracks.values()):
                                video_inits.add(p)
                            stats["initialization_boxes"] += 1
                    except (FormatError, struct.error, IndexError, ValueError):
                        stats["invalid_moov"] += 1
                for p, kind, n, _h in found[b"moof"]:
                    try:
                        raw = bytes(data[p : p + n])
                        if not child(raw, b"mfhd") or not child(raw, b"traf"):
                            continue
                        q = p + n
                        while True:
                            md = bounds(data, q, span.end)
                            if md[1] == b"mdat":
                                break
                            if md[1] not in (b"free", b"skip") or md[2] > MAX_BOX_META:
                                raise FormatError("mdat_not_adjacent")
                            q += md[2]
                        scales = {}
                        # Only contiguous sidx chains directly preceding this moof.
                        before = p
                        for x, t, z, _hh in reversed(found[b"sidx"]):
                            if x + z == before:
                                adjacent_scales = parse_sidx(bytes(data[x : x + z]))
                                if any(
                                    tid in scales and scales[tid] != value
                                    for tid, value in adjacent_scales.items()
                                ):
                                    raise FormatError("conflicting_timescales")
                                scales.update(adjacent_scales)
                                before = x
                        digest = hashlib.sha256()
                        for a in range(p, q + md[2], 1024 * 1024):
                            check_stop(stop)
                            digest.update(data[a : min(a + 1024 * 1024, q + md[2])])
                        fragments.append(
                            Fragment(
                                path,
                                source,
                                group,
                                p,
                                n,
                                q,
                                md[2],
                                md[3],
                                scales,
                                digest.hexdigest(),
                            )
                        )
                    except (FormatError, struct.error, IndexError) as error:
                        stats[
                            (
                                str(error)
                                if isinstance(error, FormatError)
                                else "invalid_fragment"
                            )
                        ] += 1
                for p, kind, n, _h in found[b"ftyp"]:
                    q = p
                    types = []
                    last = p
                    movie = None
                    has_video = False
                    try:
                        while q < span.end:
                            x, t, z, _hh = bounds(data, q, span.end)
                            if t not in (
                                b"ftyp",
                                b"moov",
                                b"mdat",
                                b"free",
                                b"skip",
                                b"wide",
                                b"uuid",
                                b"pnot",
                            ):
                                break
                            if t == b"ftyp" and types:
                                break
                            types.append(t)
                            if t == b"moov":
                                movie = valid_inits.get(q)
                                has_video = q in video_inits
                            q += z
                            last = q
                    except FormatError:
                        pass
                    if (
                        movie
                        and has_video
                        and b"mdat" in types
                        and not child(movie, b"mvex")
                    ):
                        complete.append((path, p, last - p, source))
            return fragments, inits, complete, url


def recover_files(files, output_parent, *, progress=None, stop=None, max_file_mb=2048):
    """Recover selected (local_path, extraction_relative_path) pairs.

    Each cache directory and partitioned cache key forms a separate resource
    namespace. Output is created in a new directory outside the input paths.
    Returned source paths are supplied by the caller, not local filesystem paths.
    """
    progress = progress or (lambda message, **data: None)
    files = [
        (Path(path).resolve(), str(source))
        for path, source in files
        if not Path(path).is_symlink()
    ]
    output_parent = Path(output_parent).resolve()
    if max_file_mb < 1:
        raise ValueError("max_file_mb must be positive")
    for path, _ in files:
        if (
            path == output_parent
            or path.parent == output_parent
            or path.parent in output_parent.parents
        ):
            raise ValueError("output must be outside the input directories")
    output_parent.mkdir(parents=True, exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix="chrome_cache_", dir=output_parent))
    (out / "Videos").mkdir()
    stats = Counter()
    fragments, inits, intact, clips = [], [], [], []
    sources, source_paths = {}, {}
    manifest = {
        "format_version": 1,
        "parser_version": VERSION,
        "status": "running",
        "sources": sources,
        "clips": clips,
        "notes": [
            "Outputs are derivatives; cache presence does not establish viewing.",
            "No decoder check is performed by this Python reader.",
            "Audio is included only with an original AAC configuration.",
        ],
    }
    try:
        progress("scanning", output=str(out))
        seen = set()
        for path, relative in files:
            check_stop(stop)
            if path in seen:
                continue
            seen.add(path)
            stats["files_seen"] += 1
            source = f"source_{stats['files_seen']:07d}"
            try:
                if not path.is_file():
                    continue
                size = path.stat().st_size
                if size > max_file_mb * 1024 * 1024:
                    stats["file_size_limit_skipped"] += 1
                    continue
                before = file_hash(path, stop)
                ff, ii, cc, url = scan_file(path, relative, stats, stop)
                for fragment in ff:
                    fragment.source = source
                ii = [(key, tracks, source) for key, tracks, _ in ii]
                cc = [(local, start, size, source) for local, start, size, _ in cc]
                fragments.extend(ff)
                inits.extend(ii)
                intact.extend(cc)
                stats["files_scanned"] += 1
                stats["bytes_scanned"] += size
                if ff or ii or cc:
                    sources[source] = {
                        "path": relative,
                        "size": size,
                        "url": url,
                        "sha256": before,
                    }
                    source_paths[source] = path
            except (OSError, ValueError, struct.error, FormatError):
                stats["file_errors"] += 1
            if stats["files_seen"] % 10 == 0:
                progress(
                    "scanning", files=stats["files_seen"], fragments=len(fragments)
                )
        stats["fragments_found"] = len(fragments)
        groups = defaultdict(list)
        initgroups = defaultdict(list)
        for f in fragments:
            groups[f.group].append(f)
        for key, tracks, source in inits:
            initgroups[key].append((tracks, source))
        stats["resource_groups"] = len(groups)
        progress(
            "parsing_fragments", files=stats["files_seen"], fragments=len(fragments)
        )

        def save_clip(track_samples, key, warnings):
            check_stop(stop)
            index = len(clips) + 1
            dest = out / "Videos" / f"Video_{index:05d}.mp4"
            hashes = write_mp4(dest, track_samples, stop)
            video, ss = track_samples[0]
            record = {
                "file": str(dest.relative_to(out)),
                "resource_group": key,
                "initialization_sources": sorted(init_source_ids),
                "video_frames": len(ss),
                "video_seconds": float(
                    Fraction(sum(s.dur for s in ss), video.timescale)
                ),
                "width": video.width,
                "height": video.height,
                "audio": len(track_samples) > 1,
                "codec": "h264",
                "timescale": video.timescale,
                "warnings": sorted(set(warnings)),
                "decoder_check": "not_performed",
                "sample_bytes_verified": True,
                "sha256": file_hash(dest, stop),
                "samples": hashes,
                "tracks": [
                    {
                        "id": t.tid,
                        "codec": t.codec,
                        "timescale": t.timescale,
                        "original_first_dts": samples[0].dts,
                        "source_samples": [
                            {
                                "source": s.source,
                                "offset": s.offset,
                                "size": s.size,
                                "dts": s.dts,
                                "duration": s.dur,
                                "cto": s.cto,
                            }
                            for s in samples
                        ],
                    }
                    for t, samples in track_samples
                ],
            }
            clips.append(record)
            progress("video_recovered", clip=record, output=str(out), clips=len(clips))

        for key, ff in groups.items():
            check_stop(stop)
            init = {}
            init_source_ids = []
            # Never choose arbitrarily among different original configurations.
            configs = initgroups.get(key, [])
            if configs:
                signatures = {repr(tracks) for tracks, source in configs}
                if len(signatures) == 1:
                    init = configs[0][0]
                    init_source_ids = [source for _, source in configs]
                else:
                    stats["ambiguous_initialization"] += 1
                    continue
            tracksamples = defaultdict(list)
            scales = defaultdict(set)
            dedup = set()
            for f in ff:
                if f.digest in dedup:
                    stats["duplicate_fragments"] += 1
                    continue
                dedup.add(f.digest)
                try:
                    _sequence, parsed = parse_fragment(f, init)
                    for tid, ss in parsed.items():
                        tracksamples[tid].extend(ss)
                    for tid, scale in f.scales.items():
                        scales[tid].add(scale)
                except (FormatError, struct.error, IndexError) as error:
                    stats[
                        (
                            str(error)
                            if isinstance(error, FormatError)
                            else "invalid_fragment"
                        )
                    ] += 1
            for tid, samples in tracksamples.items():
                check_stop(stop)
                original = init.get(tid)
                if original and original.codec not in ("avc1", "avc3"):
                    if original.codec != "mp4a":
                        stats["unsupported_codec_tracks"] += 1
                    continue
                warnings = []
                if len(scales[tid]) > 1:
                    stats["conflicting_timescales"] += 1
                    continue
                if original:
                    scale = original.timescale
                elif scales[tid]:
                    scale = next(iter(scales[tid]))
                else:
                    stats["missing_video_timescale"] += 1
                    continue
                if original and scales[tid] and original.timescale not in scales[tid]:
                    stats["conflicting_timescales"] += 1
                    continue
                # Conflicting samples at the same DTS are removed; never silently interleave them.
                bytime = defaultdict(list)
                for s in samples:
                    bytime[s.dts].append(s)
                ordered = []
                for _dts, ss in sorted(bytime.items()):
                    if len(ss) == 1:
                        ordered.append(ss[0])
                        continue
                    signatures = {
                        (
                            s.dur,
                            s.cto,
                            s.flags,
                            hashlib.sha256(read_at(s.path, s.offset, s.size)).digest(),
                        )
                        for s in ss
                    }
                    if len(signatures) == 1:
                        ordered.append(ss[0])
                        stats["duplicate_samples"] += len(ss) - 1
                    else:
                        stats["conflicting_samples_skipped"] += len(ss)
                current_sps = original.sps if original else b""
                current_pps = original.pps if original else b""
                length_size = original.nal_length if original else 4
                valid = []
                for s in ordered:
                    check_stop(stop)
                    if s.size > MAX_BOX_META:
                        stats["sample_size_limit"] += 1
                        continue
                    try:
                        units = nals(read_at(s.path, s.offset, s.size), length_size)
                        types = [n[0] & 31 for n in units]
                        if not any(t in (1, 5) for t in types):
                            continue
                        for unit in units:
                            if unit[0] & 31 == 7:
                                current_sps = unit
                            elif unit[0] & 31 == 8:
                                current_pps = unit
                        if current_sps and current_pps:
                            dims = sps_dimensions(current_sps)
                            s.sync = 5 in types
                            s.config = (current_sps, current_pps, length_size, *dims)
                            valid.append(s)
                    except (FormatError, struct.error, IndexError):
                        continue
                if not valid:
                    if not original or original.codec != "mp4a":
                        stats["tracks_without_usable_h264"] += 1
                    continue
                if not original:
                    warnings.append("video_header_reconstructed")
                # Start every interval at IDR; gaps, overlaps and config changes split it.
                segments = []
                run = []
                for s in valid:
                    if run and (
                        s.dts != run[-1].dts + run[-1].dur or s.config != run[-1].config
                    ):
                        segments.append(run)
                        run = []
                        stats["video_discontinuities"] += 1
                    # Bound clip sizes and metadata memory at a clean random access point.
                    if run and s.sync and s.dts - run[0].dts >= 300 * scale:
                        segments.append(run)
                        run = []
                    if not run and not s.sync:
                        stats["leading_non_idr_frames_skipped"] += 1
                        continue
                    run.append(s)
                if run:
                    segments.append(run)
                for segment in segments:
                    sps, pps, length, w, h = segment[0].config
                    video = Track(
                        tid,
                        scale,
                        "h264",
                        w,
                        h,
                        sps,
                        pps,
                        length,
                        matrix=original.matrix if original else IDENTITY,
                    )
                    chosen = [(video, segment)]
                    clipwarn = list(warnings)
                    begin = Fraction(segment[0].dts, scale)
                    end = Fraction(segment[-1].dts + segment[-1].dur, scale)
                    for aid, audio_samples in tracksamples.items():
                        if aid == tid:
                            continue
                        config = init.get(aid)
                        if config and config.codec == "mp4a" and config.asc:
                            audio = Track(
                                aid,
                                config.timescale,
                                "aac",
                                asc=config.asc,
                                channels=config.channels,
                                rate=config.rate,
                                original=True,
                            )
                        else:
                            continue
                        # Preserve leading audio from the same source fragment (e.g. 200 ms).
                        sourceids = {s.source for s in segment}
                        aa = [
                            s
                            for s in audio_samples
                            if s.source in sourceids
                            and Fraction(s.dts, audio.timescale) < end
                            and Fraction(s.dts + s.dur, audio.timescale)
                            > begin - Fraction(1, 2)
                        ]
                        aa.sort(key=lambda s: s.dts)
                        if not aa:
                            continue
                        if any(a.dts + a.dur != b.dts for a, b in zip(aa, aa[1:])):
                            clipwarn.append("audio_omitted_discontinuous")
                            continue
                        chosen.append((audio, aa))
                        break
                    if len(chosen) == 1 and len(tracksamples) > 1:
                        clipwarn.append("other_tracks_omitted")
                    try:
                        save_clip(chosen, key, clipwarn)
                    except (FormatError, OSError, struct.error) as error:
                        stats[
                            (
                                str(error)
                                if isinstance(error, FormatError)
                                else "output_error"
                            )
                        ] += 1
        # Already complete progressive MP4s are copied exactly, with no metadata rewrite.
        intact_hashes = set()
        for path, start, size, source in intact:
            check_stop(stop)
            digest = hashlib.sha256()
            with open(path, "rb") as f:
                f.seek(start)
                remaining = size
                while remaining:
                    check_stop(stop)
                    b = f.read(min(1024 * 1024, remaining))
                    if not b:
                        raise FormatError("source_changed_or_truncated")
                    digest.update(b)
                    remaining -= len(b)
            if size > MAX_CLIP_BYTES:
                stats["clip_size_limit"] += 1
                continue
            if digest.hexdigest() in intact_hashes:
                continue
            intact_hashes.add(digest.hexdigest())
            dest = out / "Videos" / f"Video_{len(clips)+1:05d}_original.mp4"
            tmp = dest.with_suffix(".partial")
            with open(path, "rb") as f, open(tmp, "xb") as o:
                f.seek(start)
                remaining = size
                while remaining:
                    check_stop(stop)
                    b = f.read(min(1024 * 1024, remaining))
                    if not b:
                        raise FormatError("source_changed_or_truncated")
                    o.write(b)
                    remaining -= len(b)
            if file_hash(tmp, stop) != digest.hexdigest():
                raise FormatError("copy_verification_failed")
            tmp.replace(dest)
            record = {
                "file": str(dest.relative_to(out)),
                "kind": "complete_mp4_carved",
                "source": source,
                "source_offset": start,
                "size": size,
                "sha256": digest.hexdigest(),
                "byte_copy_verified": True,
                "decoder_check": "not_performed",
                "warnings": [],
            }
            clips.append(record)
            progress("mp4_carved", clip=record, output=str(out), clips=len(clips))
        for source, path in source_paths.items():
            if file_hash(path, stop) != sources[source]["sha256"]:
                for clip in clips:
                    (out / clip["file"]).unlink(missing_ok=True)
                clips.clear()
                raise FormatError("source_changed_during_recovery")
        manifest["status"] = "completed"
    except Cancelled:
        clips.clear()
        manifest["status"] = "cancelled"
    except (
        OSError,
        ValueError,
        struct.error,
        IndexError,
        OverflowError,
        FormatError,
    ) as error:
        clips.clear()
        manifest["status"] = "failed"
        manifest["error"] = (
            str(error) if isinstance(error, FormatError) else type(error).__name__
        )
        stats["fatal_error"] += 1
    finally:
        # Only files in the newly created run directory are eligible for cleanup.
        # Preserve recorded candidates; remove interrupted/unrecorded writes.
        recorded = {c["file"] for c in clips}
        for partial in (out / "Videos").iterdir():
            if (
                partial.suffix == ".partial"
                or str(partial.relative_to(out)) not in recorded
            ):
                try:
                    partial.unlink()
                except OSError:
                    stats["incomplete_output_cleanup_failed"] += 1
        stats["clips_exported"] = len(clips)
        manifest["statistics"] = dict(stats)
        with open(out / "provenance.json", "w", encoding="utf-8") as stream:
            json.dump(manifest, stream, ensure_ascii=False, indent=2)
    progress("completed", output=str(out), status=manifest["status"], clips=len(clips))
    return out, manifest


# ---------------------------------------------------------------------------
# Simple Cache entry metadata, index times and decoded bodies

INDEX_MAGIC = 0x656E74657220796F
MAX_METADATA = 4 * 1024 * 1024
MAX_BODY = 32 * 1024 * 1024
EPOCH = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)
ENTRY_NAME = re.compile(r"^([0-9a-f]{16})_[01s]$")


class BodyError(ValueError):
    """A body that cannot be decoded within the limits, or with this install."""


def chrome_time(value, seconds=False):
    """A stored Chromium time (microseconds, or seconds) since 1601 as UTC, or ''."""
    try:
        value = int(value)
        if value <= 0:
            return ""
        return EPOCH + datetime.timedelta(**{("seconds" if seconds else "microseconds"): value})
    except (ValueError, TypeError, OverflowError):
        return ""


class PickleReader:
    """Chromium base::Pickle fields: little endian, four-byte aligned."""

    def __init__(self, data, offset=0):
        self.data = data
        self.offset = offset

    def read(self, fmt):
        size = struct.calcsize("<" + fmt)
        if self.offset + size > len(self.data):
            raise ValueError("truncated pickle")
        result = struct.unpack_from("<" + fmt, self.data, self.offset)[0]
        self.offset = (self.offset + size + 3) & ~3
        return result

    def string(self):
        size = self.read("i")
        if size < 0 or size > len(self.data) - self.offset:
            raise ValueError("invalid pickle string")
        result = self.data[self.offset:self.offset + size]
        self.offset = (self.offset + size + 3) & ~3
        return result


def raw_cache_key(path):
    """The complete key of a ``_0``, ``_1`` or ``_s`` entry file, or ''."""
    with Path(path).open("rb") as stream:
        header = stream.read(24)
        if len(header) != 24:
            return ""
        magic, _, size, _, _ = struct.unpack("<QIIII", header)
        if magic != INITIAL_MAGIC or size > MAX_METADATA:
            return ""
        key = stream.read(size)
        return key.decode("utf-8", "strict") if len(key) == size else ""


def entry_metadata(path):
    """Key, URL and stream 0 HTTP metadata of a ``_0`` entry file.

    Stream 0 is read from its end-of-stream record, so a large body is never
    loaded. Raises ValueError for a file that is not a Simple Cache entry.
    """
    with Path(path).open("rb") as stream:
        size = Path(path).stat().st_size
        header = stream.read(24)
        if len(header) != 24:
            raise ValueError("short header")
        magic, version, keylen, _, _ = struct.unpack("<QIIII", header)
        if magic != INITIAL_MAGIC or keylen > MAX_METADATA or keylen > size - 72:
            raise ValueError("invalid Simple Cache header")
        raw_key = stream.read(keylen)
        stream.seek(-24, 2)
        magic, flags, _, length, _ = struct.unpack("<QIIII", stream.read(24))
        sha_size = 32 if flags & 2 else 0
        start = size - 24 - sha_size - length
        if magic != FINAL_MAGIC or length > MAX_METADATA or start - 24 < 24 + keylen:
            raise ValueError("invalid stream 0 bounds")
        stream.seek(start - 24)
        if struct.unpack("<Q", stream.read(8))[0] != FINAL_MAGIC:
            raise ValueError("missing stream 1 EOF")
        stream.seek(start)
        payload = stream.read(length)
        if sha_size and stream.read(32) != hashlib.sha256(raw_key).digest():
            raise ValueError("cache key SHA256 mismatch")
    key = raw_key.decode("utf-8", "strict")
    urls = re.findall(r"https?://[^\s\x00]+", key)
    result = {"cache_key": key, "url": urls[-1] if urls else "", "version": version,
              "request_time": "", "response_time": "", "original_response_time": "",
              "status": "", "headers": {}}
    try:
        reader = PickleReader(payload)
        payload_size = reader.read("I")
        if payload_size > len(payload) - 4:
            raise ValueError("invalid response pickle size")
        flags = reader.read("I")
        # HttpResponseInfo persistence versions 1 to 3; other layouts stay unresolved.
        if (flags & 0xff) not in (1, 2, 3):
            raise ValueError("unsupported response pickle version")
        extra = reader.read("I") if flags & (1 << 31) else 0
        request, response = reader.read("q"), reader.read("q")
        original = reader.read("q") if extra & 4 else 0
        lines = reader.string().decode("utf-8", "replace").split("\x00")
        if not lines or not lines[0].startswith("HTTP/"):
            raise ValueError("missing HTTP status")
        result.update(request_time=chrome_time(request), response_time=chrome_time(response),
                      original_response_time=chrome_time(original), status=lines[0])
        for line in lines[1:]:
            name, sep, value = line.partition(":")
            if sep:
                result["headers"].setdefault(name.strip().lower(), []).append(value.strip())
        result["status_detail"] = "HTTP metadata parsed"
    except (ValueError, struct.error):
        result["status_detail"] = "HTTP response metadata unavailable or unsupported"
    return result


def index_times(path):
    """{entry hash: last used time} from a version 9 ``index-dir/the-real-index``."""
    if Path(path).stat().st_size > MAX_BODY:
        raise ValueError("index size limit")
    reader = PickleReader(Path(path).read_bytes(), 8)
    magic, version, count = reader.read("Q"), reader.read("I"), reader.read("Q")
    if magic != INDEX_MAGIC or version != 9 or count > (len(reader.data) - reader.offset) // 24:
        raise ValueError("unsupported or truncated index")
    reader.read("Q")  # cache size
    reader.read("I")  # write reason
    result = {}
    for _ in range(count):
        entry_hash, timestamp = reader.read("Q"), reader.read("q")
        reader.read("Q")  # packed size
        result[f"{entry_hash:016x}"] = chrome_time(timestamp)
    reader.read("q")  # cache last modified, not an entry time
    return result


def decode_body(data, encoding="", limit=MAX_BODY):
    """Decode an HTTP body by its Content-Encoding, within ``limit`` bytes.

    gzip is also recognised by its magic bytes when the header is missing.
    Raises BodyError when the body cannot be decoded here.
    """
    encoding = (encoding or "").strip().lower()
    if encoding in ("", "identity") and bytes(data[:2]) != b"\x1f\x8b":
        if len(data) > limit:
            raise BodyError("body exceeds the size limit")
        return bytes(data)
    if encoding in ("gzip", "x-gzip") or bytes(data[:2]) == b"\x1f\x8b":
        decoder = zlib.decompressobj(31)
    elif encoding == "deflate":
        decoder = zlib.decompressobj(15 if bytes(data[:1]) and data[0] & 0x0F == 8 else -15)
    elif encoding == "br":
        try:
            import brotli  # optional; pylint: disable=import-outside-toplevel
        except ImportError as error:
            raise BodyError("brotli body; the brotli package is not installed") from error
        try:
            decoder = brotli.Decompressor()
            out = decoder.process(bytes(data))
        except brotli.error as error:
            raise BodyError("invalid brotli body") from error
        if len(out) > limit:
            raise BodyError("body exceeds the size limit")
        return out
    else:
        raise BodyError(f"unsupported content encoding: {encoding}")
    try:
        out = decoder.decompress(bytes(data), limit + 1)
    except zlib.error as error:
        raise BodyError(f"invalid {encoding or 'gzip'} body") from error
    if len(out) > limit or not decoder.eof:
        raise BodyError("body exceeds the size limit or is truncated")
    return out


def entry_body(path, limit=MAX_BODY):
    """(decoded stream 1 body, metadata) of a ``_0`` entry, or (None, metadata)."""
    metadata = entry_metadata(path)
    data = Path(path).read_bytes() if Path(path).stat().st_size <= limit + MAX_METADATA else None
    if data is None:
        raise BodyError("entry exceeds the size limit")
    _, spans, _ = cache_spans(data)
    for span in spans:
        if span.method == "simple_stream1":
            encoding = (metadata["headers"].get("content-encoding") or [""])[0]
            return decode_body(data[span.start:span.end], encoding, limit), metadata
    return None, metadata


# ---------------------------------------------------------------------------
# Command line

def _cmd_entries(folder):
    folder = Path(folder)
    times = {}
    index = folder / "index-dir" / "the-real-index"
    if index.is_file():
        try:
            times = index_times(index)
        except (OSError, ValueError, struct.error) as error:
            print(f"# index not read: {error}", file=sys.stderr)
    print("\t".join(("file", "url", "status", "content_type", "request_time",
                     "response_time", "last_used")))
    for path in sorted(folder.iterdir()):
        match = ENTRY_NAME.fullmatch(path.name)
        if not match or not path.is_file():
            continue
        row = {"url": "", "status": "", "content_type": "", "request_time": "", "response_time": ""}
        try:
            if path.name.endswith("_0"):
                meta = entry_metadata(path)
                row.update(url=meta["url"], status=meta["status"],
                           content_type=(meta["headers"].get("content-type") or [""])[0],
                           request_time=meta["request_time"], response_time=meta["response_time"])
            else:
                urls = re.findall(r"https?://[^\s\x00]+", raw_cache_key(path))
                row["url"] = urls[-1] if urls else ""
        except (OSError, ValueError, UnicodeError, struct.error) as error:
            row["status"] = f"unreadable: {error}"
        print("\t".join(str(value) for value in (
            path.name, row["url"], row["status"], row["content_type"], row["request_time"],
            row["response_time"], times.get(match.group(1), ""))))
    return 0


def _cmd_recover(folder, output):
    folder = Path(folder)
    files = [(path, path.relative_to(folder).as_posix()) for path in sorted(folder.rglob("*"))
             if path.is_file() and not path.is_symlink()]
    out, manifest = recover_files(files, output)
    print(json.dumps({"output": str(out), "status": manifest["status"],
                      "clips": [clip["file"] for clip in manifest["clips"]],
                      "statistics": manifest.get("statistics", {})}, indent=2))
    return 0 if manifest["status"] == "completed" else 1


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="chromiumcacheprobe",
        description="Read a Chromium Simple Cache folder and rebuild cached H.264 video.")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    entries = commands.add_parser("entries", help="list the entries of a Cache_Data folder")
    entries.add_argument("folder")
    recover = commands.add_parser("recover", help="rebuild cached MP4 video from a folder")
    recover.add_argument("folder")
    recover.add_argument("-o", "--output", required=True,
                         help="parent folder for the new run folder (outside the input)")
    args = parser.parse_args(argv)
    if args.command == "entries":
        return _cmd_entries(args.folder)
    return _cmd_recover(args.folder, args.output)


if __name__ == "__main__":
    sys.exit(main())
