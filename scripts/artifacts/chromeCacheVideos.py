"""Rebuild H.264 video from the Android Chrome cache and link it to its cached context."""

__artifacts_v2__ = {
    "get_chromeCacheVideos": {
        "name": "Chrome Cache - Videos",
        "description": "H.264 video rebuilt from MP4 fragments in the Android Chrome cache, with the "
                       "HTTP and cache times of each video and the cached Reddit post that references it.",
        "author": "@ForensikITGmbH, @AlexisBrignoni, Claude",
        "creation_date": "2026-10-02",
        "last_update_date": "2026-10-15",
        "requirements": "none",
        "category": "Chromium",
        "notes": (
            "Video is rebuilt by the vendored chromiumcacheprobe from MP4 fragments in the "
            "cache's _0 and sparse _s files. Sample bytes are copied as stored and only the "
            "container is written; no decoder is run. Recovery Method says whether a clip was "
            "rebuilt or was a complete MP4 copied byte for byte. The file "
            "chromeCacheVideos_provenance.json in the report's Chromium folder lists the source "
            "file hashes and the offset and size of every sample. "
            "Response Time and Request Time are the HTTP exchange times Chrome stored with the "
            "cache entry, and Last Used is the entry's time in the cache index. They are not "
            "playback times, and cached video does not show it was watched. A time is blank "
            "when a video's entries disagree; all values are in Cache Metadata. "
            "A Reddit post is linked only when a cached Reddit JSON response stores the exact "
            "video URL in a reddit_video field. Promoted (as stored) is that post's promoted "
            "value. Browser History visits and tab session entries are linked by the exact "
            "video URL, the exact post permalink, or the post ID Reddit sent as source_post_id "
            "with the listing request. That last link names the page that was open when the "
            "listing was fetched, which can be a different post from the video's own; Browser "
            "Relationship says which link was used. Browser records are linked only when the "
            "same Android user's storage holds one Chrome profile, because the cache does not "
            "record its profile. No link is made by time. Brotli-compressed responses are read "
            "only when the brotli package is installed."
        ),
        "paths": (
            "*/com.android.chrome/cache/[Cc]ache/*",
            "*/com.android.chrome/cache/[Cc]ache_[Dd]ata/*",
            "*/com.android.chrome/app_chrome/*/History*",
            "*/com.android.chrome/app_chrome/*/Media History*",
            "*/com.android.chrome/app_chrome/*/Sessions/Tabs_*",
        ),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "video",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 12 rows",
        },
    },
}

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import shutil
import sqlite3
import struct
import tempfile
from urllib.parse import parse_qs, urlsplit, urlunsplit

from scripts.artifacts.storagePathViews import canonical_path, unique_files
from scripts.ilapfuncs import artifact_processor, check_in_embedded_media, logfunc, \
    open_sqlite_db_readonly
from scripts.snss_parser import SNSSError, read_navigation_entries
from scripts.vendor import chromiumcacheprobe as ccp

MAX_CONTEXT_INPUT = 128 * 1024 * 1024
MAX_JSON_NODES = 100000
PROVENANCE = "chromeCacheVideos_provenance.json"


# ---------------------------------------------------------------- scope

def _scope(relative):
    """Evidence root, storage class and Android user; a missing user is never inferred."""
    key, _ = canonical_path(relative)
    match = re.search(r"\x00(ce|de):(\d+)\x00/com\.android\.chrome/", key)
    if match:
        return key[:match.end()], match.group(2)
    # A detached cache still yields its own metadata, but no cross-directory joins.
    return str(Path(relative).parent), ""


def _cache_input(relative):
    return "/com.android.chrome/cache/" in "/" + relative.replace("\\", "/")


def _profile(relative):
    match = re.search(r"/app_chrome/([^/]+)/", "/" + relative)
    return match.group(1) if match else ""


def _url(value):
    """URL compared with its query and rendition kept and its fragment dropped."""
    if not isinstance(value, str):
        return ""
    try:
        part = urlsplit(value)
        if part.scheme not in ("http", "https") or not part.netloc:
            return ""
        return urlunsplit((part.scheme, part.netloc, part.path, part.query, ""))
    except ValueError:
        return ""


def _json_text(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      default=lambda item: item.isoformat() if hasattr(item, "isoformat") else str(item))


# ---------------------------------------------------------------- cached site context

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


def _reddit_posts(document, request_url, targets):
    """Posts whose reddit_video fields store a recovered video's exact URL."""
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
                    for resource in targets.get(_url(value), []):
                        yield resource, {
                            "post_id": post, "title": item.get("title", ""),
                            "permalink": "https://www.reddit.com" + link,
                            "media_field": media_name + "." + field_name + "." + field,
                            "media_url": value,
                            "role": "Scrubber preview" if field == "scrubber_media_url" else "Media reference",
                            "promoted": item.get("promoted", ""),
                            "source_post_ids": [p[3:] for p in source_ids if re.fullmatch(r"t3_[a-z0-9]+", p)],
                            "request_url": request_url}


# Each matcher reads one decoded JSON response and yields (resource, post) pairs for
# posts that store a recovered video's exact URL. Add a site by adding a matcher.
POST_MATCHERS = (_reddit_posts,)


# ---------------------------------------------------------------- browser records

def _database_records_from_copy(path, relative, diagnostics):
    db = open_sqlite_db_readonly(str(path))
    if db is None:
        diagnostics["browser_database_unreadable"] += 1
        return []
    records = []
    try:
        db.row_factory = sqlite3.Row
        if Path(path).name == "History":
            query = ("SELECT visits.id, visits.visit_time, visits.from_visit, visits.transition, "
                     "urls.url, urls.title FROM visits JOIN urls ON visits.url=urls.id")
            for row in db.execute(query):
                records.append({"kind": "History visit", "time": ccp.chrome_time(row["visit_time"]),
                                "url": row["url"], "title": row["title"], "record_id": str(row["id"]),
                                "details": {"from_visit": row["from_visit"],
                                            "transition_as_stored": row["transition"]}})
                diagnostics["history_records_read"] += 1
        else:
            for table, kind in (("playback", "Media History playback"),
                                ("playbackSession", "Media History session")):
                try:
                    for row in db.execute("SELECT * FROM " + table):
                        values = dict(row)
                        records.append({"kind": kind,
                                        "time": ccp.chrome_time(values.get("last_updated_time_s"), seconds=True),
                                        "url": values.get("url", ""), "title": values.get("title", ""),
                                        "record_id": str(values.get("id", values.get("url", ""))),
                                        "details": values})
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
    # A read-only connection to a WAL database can still write its -shm file, so read
    # a disposable copy with its sidecars and leave the staged files untouched.
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
                    yield {"kind": "Session navigation", "time": ccp.chrome_time(entry.get("timestamp")),
                           "url": entry.get("url", ""), "title": entry.get("title", ""),
                           "record_id": str(number), "source": relative, "profile": _profile(relative),
                           "details": {key: entry.get(key) for key in (
                               "tab_id", "index", "referrer_url", "original_request_url", "transition_type")}}
            except (OSError, SNSSError, ValueError):
                diagnostics["session_unreadable"] += 1


# ---------------------------------------------------------------- resources

def _clip_source_ids(clip):
    """Every sample and initialization source of one clip."""
    result = {sample["source"] for track in clip.get("tracks", []) for sample in track["source_samples"]}
    result.update(clip.get("initialization_sources", []))
    if "source" in clip:
        result.add(clip["source"])
    return result


def _resources(manifest):
    resources = {}
    for clip in manifest["clips"]:
        sources = [manifest["sources"][key] for key in sorted(_clip_source_ids(clip))]
        group = clip.get("resource_group") or sources[0]["path"]
        resource_id = hashlib.sha256(canonical_path(group)[0].encode()).hexdigest()
        scope, user = _scope(sources[0]["path"])
        resource = resources.setdefault(resource_id, {
            "id": resource_id, "urls": [], "media_sources": [], "clips": [], "metadata": [],
            "posts": [], "activities": [], "profile_candidates": [], "scope": scope,
            "android_user": user, "cache_namespaces": []})
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
                key = ccp.raw_cache_key(local[relative])
            except (OSError, UnicodeError, struct.error):
                diagnostics["source_key_unreadable"] += 1
                continue
            urls = re.findall(r"https?://[^\s\x00]+", key)
            if not urls:
                diagnostics["source_cache_key_unavailable"] += 1
                continue
            namespace = (canonical_path(source.parent.as_posix())[0], key.rsplit(urls[-1], 1)[0])
            if namespace not in resource["cache_namespaces"]:
                resource["cache_namespaces"].append(namespace)
            match = ccp.ENTRY_NAME.fullmatch(source.name)
            companion = source.with_name((match.group(1) + "_0") if match else source.name).as_posix()
            companion = aliases.get(canonical_path(companion)[0], companion)
            if companion in seen:
                continue
            seen.add(companion)
            record = {"cache_key": key, "url": urls[-1], "version": None, "request_time": "",
                      "response_time": "", "original_response_time": "", "headers": {},
                      "status_detail": "HTTP metadata unavailable", "source": relative,
                      "last_used": "", "index_source": "",
                      "join_method": "Cache filename hash and directory; HTTP metadata unavailable"}
            if companion in local:
                try:
                    if companion not in metadata:
                        metadata[companion] = ccp.entry_metadata(local[companion])
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
                        indexes[index_relative] = ccp.index_times(local[index_relative])
                    except (OSError, ValueError, struct.error):
                        indexes[index_relative] = {}
                        diagnostics["index_unreadable_or_unsupported"] += 1
                record["last_used"] = indexes[index_relative].get(match.group(1), "")
                record["index_source"] = index_relative
            resource["metadata"].append(record)


def _json_document(path, diagnostics):
    """(decoded JSON body or None, entry metadata) for a ``_0`` entry."""
    try:
        body, metadata = ccp.entry_body(path)
    except ccp.BodyError:
        diagnostics["cache_body_not_decoded"] += 1
        return None, None
    if body is None or body.lstrip()[:1] not in (b"{", b"["):
        return None, metadata
    try:
        return json.loads(body), metadata
    except (ValueError, RecursionError):
        diagnostics["cache_json_unreadable"] += 1
        return None, metadata


def _attach_posts(resources, inputs, diagnostics):
    targets = defaultdict(lambda: defaultdict(list))
    for resource in resources.values():
        for url in resource["urls"]:
            targets[resource["scope"]][_url(url)].append(resource)
    seen = {}
    for path, relative in inputs:
        current_scope = _scope(relative)[0]
        if not _cache_input(relative) or not path.name.endswith("_0") or current_scope not in targets:
            continue
        try:
            document, request = _json_document(path, diagnostics)
        except (OSError, ValueError, UnicodeError, struct.error):
            diagnostics["cache_entry_unreadable"] += 1
            continue
        if document is None:
            continue
        namespace = (canonical_path(Path(relative).parent.as_posix())[0],
                     request["cache_key"].rsplit(request["url"], 1)[0] if request["url"] else request["cache_key"])
        try:
            for matcher in POST_MATCHERS:
                for resource, post in matcher(document, request["url"], targets[current_scope]):
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
        except ValueError:
            diagnostics["cache_json_node_limit"] += 1


def _attach_activities(resources, inputs, diagnostics, profile_inputs):
    profiles = defaultdict(set)
    for _, relative in profile_inputs:
        if _profile(relative):
            profiles[_scope(relative)[0]].add(_profile(relative))
    for resource in resources.values():
        resource["profile_candidates"] = sorted(profiles[resource["scope"]])
    for activity in _browser_records(inputs, diagnostics):
        for resource in resources.values():
            if _scope(activity["source"])[0] != resource["scope"]:
                continue
            # The app cache does not record its browser profile. Keep the ambiguity.
            if len(resource["profile_candidates"]) != 1:
                continue
            value, relation = _url(activity["url"]), ""
            if value and value in {_url(url) for url in resource["urls"]}:
                relation = "Exact video URL"
            elif value and value in {_url(post["permalink"]) for post in resource["posts"]}:
                relation = "Exact permalink of the video's post"
            else:
                parsed = urlsplit(value)
                if parsed.hostname in ("reddit.com", "www.reddit.com"):
                    match = re.search(r"/comments/([a-z0-9]+)/", parsed.path + "/")
                    ids = {post_id for post in resource["posts"] for post_id in post["source_post_ids"]}
                    if match and match.group(1) in ids:
                        relation = "Page open when the Reddit listing was fetched (source_post_id)"
            if relation:
                resource["activities"].append(dict(
                    activity, relation=relation,
                    profile_match="Sole Chrome profile in this user's storage; cache profile not recorded"))
    if any(len(resource["profile_candidates"]) > 1 for resource in resources.values()):
        diagnostics["ambiguous_browser_profiles_not_joined"] += 1


def _build_context(inputs, manifest):
    """Context for the recovered resources only; unresolved evidence stays unresolved."""
    profile_inputs = inputs
    supplied = len(inputs)
    inputs = [(path, relative) for path, relative in inputs if path.stat().st_size <= MAX_CONTEXT_INPUT]
    before = {relative: ccp.file_hash(path) for path, relative in inputs}
    for source in manifest["sources"].values():
        if source.get("sha256") and source["path"] in before and source["sha256"] != before[source["path"]]:
            raise ValueError("recovery source changed before context analysis")
    resources = _resources(manifest)
    diagnostics = Counter()
    if supplied != len(inputs):
        diagnostics["oversized_context_inputs_skipped"] = supplied - len(inputs)
    _attach_metadata(resources, inputs, diagnostics)
    _attach_posts(resources, inputs, diagnostics)
    _attach_activities(resources, inputs, diagnostics, profile_inputs)
    for path, relative in inputs:
        if ccp.file_hash(path) != before[relative]:
            raise ValueError("cache context source changed during analysis")
    return resources, diagnostics


def _context_sources(resource):
    result = set(resource["media_sources"])
    for record in resource["metadata"]:
        result.add(record["source"])
        if record["index_source"]:
            result.add(record["index_source"])
    result.update(post["source"] for post in resource["posts"])
    result.update(activity["source"] for activity in resource["activities"])
    return sorted(result)


# ---------------------------------------------------------------- artifact

def _inputs(context):
    return [(Path(path), context.get_relative_path(path).replace("\\", "/"))
            for path in sorted(set(unique_files(context)))
            if Path(path).is_file() and not Path(path).is_symlink()]


def _unique_time(resource, name):
    values = {record[name] for record in resource["metadata"] if record[name]}
    return next(iter(values)) if len(values) == 1 else ""


def _summary(records, field):
    return "\n".join(sorted({str(record[field]) for record in records if record.get(field) not in (None, "")}))


def _promotion(resource):
    values = {"Yes" if post.get("promoted") is True else "No" if post.get("promoted") is False
              else "Not recorded" for post in resource["posts"]}
    return "\n".join(sorted(values)) if values else "Not recorded"


@artifact_processor
def get_chromeCacheVideos(context):
    data_headers = (
        ("Response Time", "datetime"),
        ("Request Time", "datetime"),
        ("Last Used", "datetime"),
        ("Video", "media"),
        "Resource URLs",
        "Post Titles",
        "Post URLs",
        "Media Role",
        "Promoted (as stored)",
        "Linked Browser URLs",
        "Browser Relationship",
        "Android User ID",
        "Browser Profiles",
        "Output SHA256",
        "Recovery Method",
        "Video Frames",
        "Video Seconds",
        "Width",
        "Height",
        "Audio",
        "Video Timebase",
        "Warnings",
        "Source File",
        "Resource ID",
        "Metadata Status",
        "Cache Metadata",
        "Post Context",
        "Activity Context",
        "Context Source Files",
    )
    inputs = _inputs(context)
    data_list = []
    if not inputs:
        return data_headers, data_list, ""
    local_sources = {relative: path for path, relative in inputs}
    with tempfile.TemporaryDirectory(prefix="chrome_cache_videos_") as temporary:
        # The probe writes each clip once, here; the report keeps the media manager's copy.
        output, manifest = ccp.recover_files([(p, r) for p, r in inputs if _cache_input(r)], temporary)
        resources, diagnostics = _build_context(inputs, manifest)
        for clip in manifest["clips"]:
            resource = resources[clip["context_resource_id"]]
            paths = sorted({manifest["sources"][source]["path"] for source in _clip_source_ids(clip)})
            destination = output / clip.pop("file")
            if not paths or destination.stat().st_size > ccp.MAX_CLIP_BYTES:
                logfunc("Chrome Cache: a clip was over the media size limit and was not added")
                continue
            ref = check_in_embedded_media(local_sources[paths[0]], destination.read_bytes(),
                                          name=destination.name, force_type="video/mp4",
                                          force_extension=".mp4")
            if not ref:
                logfunc("Chrome Cache: a clip could not be added to the report media")
                continue
            copied = clip.get("kind") == "complete_mp4_carved"
            data_list.append((
                _unique_time(resource, "response_time"),
                _unique_time(resource, "request_time"),
                _unique_time(resource, "last_used"),
                ref,
                _json_text(resource["urls"]),
                _summary(resource["posts"], "title"),
                _summary(resource["posts"], "permalink"),
                _summary(resource["posts"], "role"),
                _promotion(resource),
                _summary(resource["activities"], "url"),
                _summary(resource["activities"], "relation"),
                resource["android_user"],
                _json_text(resource["profile_candidates"]),
                clip["sha256"],
                "Progressive MP4 byte copy" if copied else "Rebuilt H.264 MP4",
                clip.get("video_frames", ""),
                clip.get("video_seconds", ""),
                clip.get("width", ""),
                clip.get("height", ""),
                "" if copied else ("Yes" if clip["audio"] else "No"),
                clip.get("timescale", ""),
                json.dumps(clip["warnings"], ensure_ascii=False),
                json.dumps(paths, ensure_ascii=False),
                resource["id"],
                "; ".join(sorted({record["status_detail"] for record in resource["metadata"]}))
                or "Metadata unavailable",
                _json_text(resource["metadata"]),
                _json_text(resource["posts"]),
                _json_text(resource["activities"]),
                _json_text(_context_sources(resource)),
            ))
    manifest["context_diagnostics"] = dict(diagnostics)
    (Path(context.get_report_folder()) / PROVENANCE).write_text(_json_text(manifest), encoding="utf-8")
    logfunc(f"Chrome Cache: {len(data_list)} videos; status {manifest['status']}; "
            f"statistics {json.dumps(manifest.get('statistics', {}), sort_keys=True)}; "
            f"context {json.dumps(dict(diagnostics), sort_keys=True)}")
    return data_headers, data_list, "\n".join(str(path) for path, _ in inputs)
