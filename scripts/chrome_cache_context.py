"""Bounded metadata and explicit browser-reference joins for recovered cache media.

No network requests, temporal-nearest joins, filesystem-date fallbacks or viewing
inferences are made here. Cache entries and browser records remain separate facts.
"""

from collections import Counter, defaultdict
import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import sqlite3
import struct
import tempfile
from urllib.parse import parse_qs, urlsplit, urlunsplit
import zlib

from scripts.artifacts.storagePathViews import canonical_path
from scripts.chrome_cache_video import INITIAL_MAGIC, FINAL_MAGIC, cache_spans, file_hash
from scripts.ilapfuncs import open_sqlite_db_readonly
from scripts.snss_parser import SNSSError, read_navigation_entries

MAX_METADATA = 4 * 1024 * 1024
MAX_JSON = 32 * 1024 * 1024
MAX_JSON_NODES = 100000
MAX_CONTEXT_INPUT = 128 * 1024 * 1024
EPOCH = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)
INDEX_MAGIC = 0x656e74657220796f
ENTRY_NAME = re.compile(r"^([0-9a-f]{16})_[01s]$")


def chrome_time(value, seconds=False):
    """A stored Chromium time, without filling absent or invalid dates."""
    try:
        value = int(value)
        return EPOCH + datetime.timedelta(**{("seconds" if seconds else "microseconds"): value}) if value > 0 else ""
    except (ValueError, TypeError, OverflowError):
        return ""


def json_text(value):
    """Serialize structured provenance while retaining UTC offsets."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      default=lambda item: item.isoformat() if isinstance(item, datetime.datetime) else str(item))


def scope(relative):
    """Evidence root, storage class and Android user; never infer a missing user."""
    key, _ = canonical_path(relative)
    match = re.search(r"\x00(ce|de):(\d+)\x00/com\.android\.chrome/", key)
    if match:
        return key[:match.end()], match.group(2)
    # A detached cache can still yield its own metadata, but no cross-directory joins.
    return str(Path(relative).parent), ""


def cache_input(relative):
    """Select cache sources from a combined cache/browser input set."""
    return "/com.android.chrome/cache/" in "/" + relative.replace("\\", "/")


class PickleReader:
    """Chromium base::Pickle fields use little endian and four-byte alignment."""

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


def entry_metadata(path):
    """Read stream 0 from its EOF trailer, without loading a large media body."""
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
              "request_time": "", "response_time": "", "original_response_time": "", "headers": {}}
    try:
        reader = PickleReader(payload)
        payload_size = reader.read("I")
        if payload_size > len(payload) - 4:
            raise ValueError("invalid response pickle size")
        flags = reader.read("I")
        # HttpResponseInfo persistence versions 1..3; unknown layouts stay unresolved.
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
    """Simple Cache index v9, including null times; reject unknown layouts."""
    if Path(path).stat().st_size > MAX_JSON:
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
    reader.read("q")  # cache last modified is not an entry activity time
    return result


def raw_cache_key(path):
    """Obtain an entry's complete key for exact sparse/metadata sibling joins."""
    with Path(path).open("rb") as stream:
        header = stream.read(24)
        if len(header) != 24:
            return ""
        magic, _, size, _, _ = struct.unpack("<QIIII", header)
        if magic != INITIAL_MAGIC or size > MAX_METADATA:
            return ""
        key = stream.read(size)
        return key.decode("utf-8", "strict") if len(key) == size else ""


def _objects(value):
    stack, count = [value], 0
    while stack:
        item = stack.pop()
        count += 1
        if count > MAX_JSON_NODES:
            raise ValueError("JSON node limit")
        if isinstance(item, dict):
            yield item
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)


def _json_bodies(path):
    if Path(path).stat().st_size > MAX_METADATA:
        return
    data = Path(path).read_bytes()
    _, spans, _ = cache_spans(data)
    for span in spans:
        if span.method != "simple_stream1":
            continue
        body = data[span.start:span.end]
        if body.startswith(b"\x1f\x8b"):
            decoder = zlib.decompressobj(31)
            body = decoder.decompress(body, MAX_JSON + 1)
            if len(body) > MAX_JSON or not decoder.eof:
                raise ValueError("compressed JSON size or truncation limit")
        if not body.lstrip().startswith((b"{", b"[")):
            continue
        yield json.loads(body)


def _url(value):
    """URL comparison preserves query tokens and renditions; ignores a fragment."""
    if not isinstance(value, str):
        return ""
    try:
        part = urlsplit(value)
        if part.scheme not in ("http", "https") or not part.netloc:
            return ""
        return urlunsplit((part.scheme, part.netloc, part.path, part.query, ""))
    except ValueError:
        return ""


def _reddit_context(document, request_url, targets):
    """An exact reddit_video URL reference, not just a shared host or media ID."""
    request = urlsplit(request_url)
    if request.hostname not in ("www.reddit.com", "reddit.com"):
        return
    source_ids = parse_qs(request.query).get("source_post_id", [])
    for item in _objects(document):
        if not isinstance(item.get("permalink"), str):
            continue
        post = item.get("id")
        if not isinstance(post, str) or not re.fullmatch(r"[a-z0-9]+", post):
            continue
        link = item["permalink"]
        if not link.startswith("/") or link.startswith("//") or "/comments/" + post + "/" not in link:
            continue
        for media_name in ("secure_media", "media", "preview"):
            media = item.get(media_name)
            if not isinstance(media, dict):
                continue
            for field_name in ("reddit_video", "reddit_video_preview"):
                video = media.get(field_name)
                if not isinstance(video, dict):
                    continue
                for field, value in video.items():
                    matched = targets.get(_url(value), [])
                    for resource in matched:
                        yield resource, {"post_id": post, "title": item.get("title", ""),
                                         "permalink": "https://www.reddit.com" + link,
                                         "media_field": media_name + "." + field_name + "." + field,
                                         "media_url": value, "role": "Scrubber preview" if field == "scrubber_media_url" else "Media reference",
                                         "promoted": item.get("promoted", ""),
                                         "source_post_ids": [p[3:] for p in source_ids if re.fullmatch(r"t3_[a-z0-9]+", p)],
                                         "request_url": request_url}


def _profile(relative):
    match = re.search(r"/app_chrome/([^/]+)/", "/" + relative)
    return match.group(1) if match else ""


def _database_records_from_copy(path, relative, diagnostics):
    db = open_sqlite_db_readonly(str(path))
    if db is None:
        diagnostics["browser_database_unreadable"] += 1
        return []
    records = []
    try:
        db.row_factory = sqlite3.Row
        if Path(path).name == "History":
            diagnostics["history_records_read"] += 0
            query = "SELECT visits.id, visits.visit_time, visits.from_visit, visits.transition, urls.url, urls.title FROM visits JOIN urls ON visits.url=urls.id"
            for row in db.execute(query):
                records.append({"kind": "History visit", "time": chrome_time(row["visit_time"]),
                                "url": row["url"], "title": row["title"], "record_id": str(row["id"]),
                                "details": {"from_visit": row["from_visit"], "transition_as_stored": row["transition"]}})
                diagnostics["history_records_read"] += 1
        else:
            for table, kind in (("playback", "Media History playback"), ("playbackSession", "Media History session")):
                diagnostics["media_history_" + table + "_records_read"] += 0
                try:
                    for row in db.execute("SELECT * FROM " + table):
                        values = dict(row)
                        records.append({"kind": kind, "time": chrome_time(values.get("last_updated_time_s"), seconds=True),
                                        "url": values.get("url", ""), "title": values.get("title", ""),
                                        "record_id": str(values.get("id", values.get("url", ""))), "details": values})
                        diagnostics["media_history_" + table + "_records_read"] += 1
                except sqlite3.Error:
                    diagnostics["media_history_table_unavailable"] += 1
    except sqlite3.Error:
        diagnostics["browser_schema_unavailable"] += 1
    finally:
        db.close()
    for record in records:
        record.update(source=relative, profile=_profile(relative))
    return records


def _database_records(path, relative, diagnostics):
    # Even a read-only WAL connection can create/update a shared-memory file.
    # Read a disposable copy with its sidecars so extraction files stay untouched.
    try:
        with tempfile.TemporaryDirectory(prefix="chrome_context_db_") as temporary:
            staged = Path(temporary) / Path(path).name
            for suffix in ("", "-wal", "-shm", "-journal"):
                source = Path(str(path) + suffix)
                if source.is_file():
                    shutil.copyfile(source, str(staged) + suffix)
            return _database_records_from_copy(staged, relative, diagnostics)
    except OSError:
        diagnostics["browser_database_copy_failed"] += 1
        return []


def _browser_records(inputs, diagnostics):
    for path, relative in inputs:
        if "/app_chrome/" not in relative:
            continue
        if path.name in ("History", "Media History"):
            yield from _database_records(path, relative, diagnostics)
        elif path.name.startswith("Tabs_"):
            try:
                for number, entry in enumerate(read_navigation_entries(str(path))):
                    diagnostics["session_records_read"] += 1
                    yield {"kind": "Session navigation", "time": chrome_time(entry.get("timestamp")),
                           "url": entry.get("url", ""), "title": entry.get("title", ""),
                           "record_id": str(number), "source": relative, "profile": _profile(relative),
                           "details": {key: entry.get(key) for key in ("tab_id", "index", "referrer_url", "original_request_url", "transition_type")}}
            except (OSError, SNSSError, ValueError):
                diagnostics["session_unreadable"] += 1


def clip_source_ids(clip):
    """All compressed-sample and initialization sources of one derivative."""
    result = {sample["source"] for track in clip.get("tracks", []) for sample in track["source_samples"]}
    result.update(clip.get("initialization_sources", []))
    if "source" in clip:
        result.add(clip["source"])
    return result


def _resources(manifest):
    resources = {}
    for clip in manifest["clips"]:
        source_ids = clip_source_ids(clip)
        sources = [manifest["sources"][key] for key in sorted(source_ids)]
        group = clip.get("resource_group") or sources[0]["path"]
        canonical, _ = canonical_path(group)
        resource_id = hashlib.sha256(canonical.encode()).hexdigest()
        resource = resources.setdefault(resource_id, {"id": resource_id, "urls": [], "media_sources": [],
                    "clips": [], "metadata": [], "posts": [], "activities": [], "profile_candidates": [],
                    "scope": scope(sources[0]["path"])[0], "android_user": scope(sources[0]["path"])[1],
                    "cache_namespaces": []})
        clip["context_resource_id"] = resource_id
        resource["clips"].append(clip["sha256"])
        resource["media_sources"] = sorted(set(resource["media_sources"]) | {s["path"] for s in sources})
        resource["urls"] = sorted(set(resource["urls"]) | {s["url"] for s in sources if s["url"]})
    return resources


def _attach_metadata(resources, inputs, diagnostics):
    local = {relative: path for path, relative in inputs}
    aliases = {canonical_path(relative)[0]: relative for _, relative in inputs}
    indexes, metadata = {}, {}
    for resource in resources.values():
        seen = set()
        for relative in resource["media_sources"]:
            if relative not in local:
                diagnostics["media_source_exceeds_context_limit"] += 1
                continue
            source = Path(relative)
            try:
                key = raw_cache_key(local[relative])
                urls = re.findall(r"https?://[^\s\x00]+", key)
                if not urls:
                    diagnostics["source_cache_key_unavailable"] += 1
                    continue
                if urls:
                    namespace = (canonical_path(source.parent.as_posix())[0], key.rsplit(urls[-1], 1)[0])
                    if namespace not in resource["cache_namespaces"]:
                        resource["cache_namespaces"].append(namespace)
            except (OSError, UnicodeError, struct.error):
                diagnostics["source_key_unreadable"] += 1
                continue
            match = ENTRY_NAME.fullmatch(source.name)
            name = (match.group(1) + "_0") if match else source.name
            companion = source.with_name(name).as_posix()
            companion = aliases.get(canonical_path(companion)[0], companion)
            if companion in seen:
                continue
            seen.add(companion)
            record = {"cache_key": key, "url": urls[-1] if urls else "", "version": None,
                      "request_time": "", "response_time": "", "original_response_time": "", "headers": {},
                      "status_detail": "HTTP metadata unavailable", "source": relative,
                      "last_used": "", "index_source": "", "join_method": "Cache filename hash and directory; HTTP metadata unavailable"}
            if companion in local:
                try:
                    if companion not in metadata:
                        metadata[companion] = entry_metadata(local[companion])
                    parsed = metadata[companion]
                    if key != parsed["cache_key"]:
                        diagnostics["metadata_cache_key_mismatch"] += 1
                        continue
                    record.update(parsed, source=companion, join_method="Exact cache entry key and directory")
                except (OSError, ValueError, UnicodeError, struct.error):
                    diagnostics["metadata_unreadable"] += 1
            else:
                diagnostics["metadata_companion_missing"] += 1
            index_relative = (source.parent / "index-dir/the-real-index").as_posix()
            index_relative = aliases.get(canonical_path(index_relative)[0], index_relative)
            if index_relative in local and match:
                if index_relative not in indexes:
                    try:
                        indexes[index_relative] = index_times(local[index_relative])
                    except (OSError, ValueError, struct.error):
                        indexes[index_relative] = {}
                        diagnostics["index_unreadable_or_unsupported"] += 1
                record["last_used"] = indexes[index_relative].get(match.group(1), "")
                record["index_source"] = index_relative
            resource["metadata"].append(record)


def _attach_posts(resources, inputs, diagnostics):
    targets = defaultdict(lambda: defaultdict(list))
    for resource in resources.values():
        for url in resource["urls"]:
            targets[resource["scope"]][_url(url)].append(resource)
    seen = {}
    for path, relative in inputs:
        current_scope = scope(relative)[0]
        if not cache_input(relative) or not path.name.endswith("_0") or current_scope not in targets:
            continue
        try:
            request = entry_metadata(path)
            namespace = (canonical_path(Path(relative).parent.as_posix())[0],
                         request["cache_key"].rsplit(request["url"], 1)[0] if request["url"] else request["cache_key"])
            for body in _json_bodies(path):
                for resource, post in _reddit_context(body, request["url"], targets[current_scope]):
                    if namespace not in resource["cache_namespaces"]:
                        continue
                    post.update(source=relative, response_time=request["response_time"])
                    field = post.pop("media_field")
                    signature = (resource["id"], relative, post["post_id"], post["media_url"])
                    if signature not in seen:
                        post["media_fields"] = [field]
                        resource["posts"].append(post)
                        seen[signature] = post
                    elif field not in seen[signature]["media_fields"]:
                        seen[signature]["media_fields"].append(field)
                        seen[signature]["media_fields"].sort()
        except (OSError, ValueError, UnicodeError, struct.error, zlib.error, RecursionError):
            diagnostics["cache_context_unreadable"] += 1


def _attach_activities(resources, inputs, diagnostics, profile_inputs):
    profiles = defaultdict(set)
    for _, relative in profile_inputs:
        if _profile(relative):
            profiles[scope(relative)[0]].add(_profile(relative))
    for resource in resources.values():
        resource["profile_candidates"] = sorted(profiles[resource["scope"]])
    for activity in _browser_records(inputs, diagnostics):
        for resource in resources.values():
            if scope(activity["source"])[0] != resource["scope"]:
                continue
            # App-level cache paths do not encode a browser profile. Preserve ambiguity.
            if len(resource["profile_candidates"]) != 1:
                continue
            value, relation = _url(activity["url"]), ""
            if value and value in {_url(url) for url in resource["urls"]}:
                relation = "Exact resource URL"
            elif value and value in {_url(post["permalink"]) for post in resource["posts"]}:
                relation = "Exact media-post permalink"
            else:
                parsed = urlsplit(value)
                if parsed.hostname in ("reddit.com", "www.reddit.com"):
                    match = re.search(r"/comments/([a-z0-9]+)/", parsed.path + "/")
                    ids = {post_id for post in resource["posts"] for post_id in post["source_post_ids"]}
                    if match and match.group(1) in ids:
                        relation = "Post ID in cached request URL"
            if relation:
                resource["activities"].append(dict(activity, relation=relation,
                    profile_match="Sole supplied profile candidate; cache profile unencoded"))
    if any(len(r["profile_candidates"]) > 1 for r in resources.values()):
        diagnostics["ambiguous_browser_profiles_not_joined"] += 1


def build_context(inputs, manifest):
    """Enrich only recovered resources, retaining unresolved evidence explicitly."""
    inputs = [(Path(path), relative.replace("\\", "/")) for path, relative in inputs]
    profile_inputs = inputs
    supplied_count = len(inputs)
    # Bound ancillary evidence reads separately from the recovery engine's limits.
    inputs = [(path, relative) for path, relative in inputs if path.stat().st_size <= MAX_CONTEXT_INPUT]
    before = {relative: file_hash(path) for path, relative in inputs}
    for source in manifest["sources"].values():
        if source.get("sha256") and source["path"] in before and source["sha256"] != before[source["path"]]:
            raise ValueError("recovery source changed before context analysis")
    resources = _resources(manifest)
    diagnostics = Counter()
    if supplied_count != len(inputs):
        diagnostics["oversized_context_inputs_skipped"] = supplied_count - len(inputs)
    _attach_metadata(resources, inputs, diagnostics)
    _attach_posts(resources, inputs, diagnostics)
    _attach_activities(resources, inputs, diagnostics, profile_inputs)
    used = {source for resource in resources.values() for source in context_sources(resource)}
    browser_sources = [relative for _, relative in inputs if "/app_chrome/" in relative]
    used.update(browser_sources)
    # WAL/SHM sidecars can supply browser rows even when the base DB did not change.
    used.update(relative for _, relative in inputs
                if any(relative == source + suffix for source in tuple(used) for suffix in ("-wal", "-shm", "-journal")))
    hashes = {}
    for path, relative in inputs:
        if relative in used:
            if file_hash(path) != before[relative]:
                raise ValueError("cache context source changed during analysis")
            hashes[relative] = before[relative]
    return {"format_version": 1, "resources": resources, "source_sha256": hashes,
            "browser_sources_inspected": browser_sources, "diagnostics": dict(diagnostics),
            "notes": ["Cache, request and response times are not playback times.",
                      "Server Date and Last-Modified headers are reported as stored, not user activity.",
                      "A cached reference or related page visit does not establish display or playback.",
                      "Browser joins require one supplied profile in the same evidence root, user and storage class.",
                      "No temporal-nearest matches or filesystem timestamp fallbacks are used."]}


def context_sources(resource):
    result = set(resource["media_sources"])
    for record in resource["metadata"]:
        result.add(record["source"])
        if record["index_source"]:
            result.add(record["index_source"])
    result.update(post["source"] for post in resource["posts"])
    result.update(activity["source"] for activity in resource["activities"])
    return sorted(result)


def resource_events(context):
    """One stored event per source record/time type, with all associated resources."""
    events = {}
    for resource in context["resources"].values():
        candidates = []
        for metadata in resource["metadata"]:
            for field, kind in (("request_time", "HTTP request time"), ("response_time", "HTTP response time"),
                                ("original_response_time", "Original HTTP response time"), ("last_used", "Cache last used")):
                if metadata[field]:
                    source = metadata["index_source"] if field == "last_used" else metadata["source"]
                    candidates.append({"time": metadata[field], "kind": kind, "source": source,
                                       "record_id": metadata["source"], "url": metadata["url"], "title": "",
                                       "relation": metadata["join_method"], "profile_match": "Cache profile unencoded",
                                       "details": {"meaning": "Cache metadata; does not establish playback", "headers_as_stored": metadata["headers"]}})
        candidates.extend(resource["activities"])
        for candidate in candidates:
            if not candidate["time"]:
                continue
            key = (candidate["kind"], candidate["source"], candidate["record_id"], candidate["time"])
            event = events.setdefault(key, dict(candidate, details=dict(candidate["details"], timestamp_utc=candidate["time"].isoformat()),
                                               resource_ids=set(), clip_hashes=set(), resource_urls=set(), source_files=set(), android_user=resource["android_user"]))
            event["resource_ids"].add(resource["id"])
            event["clip_hashes"].update(resource["clips"])
            event["resource_urls"].update(resource["urls"])
            event["source_files"].update(context_sources(resource))
            event["source_files"].add(candidate["source"])
    return [dict(event, resource_ids=sorted(event["resource_ids"]), clip_hashes=sorted(event["clip_hashes"]),
                 resource_urls=sorted(event["resource_urls"]), source_files=sorted(event["source_files"]))
            for _, event in sorted(events.items(), key=lambda item: (item[0][3], item[0][:3]))]
