"""Recover supported MP4 payloads from Android Chrome Simple Cache files."""

__artifacts_v2__ = {
    "get_chromeCacheVideos": {
        "name": "Chrome Cache - Videos",
        "description": "Rebuilds supported cached MP4 clips and links their HTTP timestamps, Reddit references and related browser records.",
        "author": "@ForensikITGmbH",
        "creation_date": "2026-10-02",
        "last_update_date": "2026-10-15",
        "requirements": "none",
        "category": "Chromium",
        "notes": (
            "Cached media does not establish viewing or a complete original video. "
            "Rebuilt containers preserve copied sample bytes; no decoder check is performed. "
            "A sequence starts at an H.264 IDR frame; gaps and configuration changes split it. "
            "Timing requires original initialization metadata or adjacent sidx boxes. "
            "Audio is included only with an original AAC configuration. Encrypted media, "
            "other codecs and fragments split across cache ranges are not reconstructed. "
            "Recovery Method distinguishes rebuilt clips from byte copies. The per-run "
            "provenance JSON records source hashes, packet offsets, raw decode/composition "
            "times, warnings and skipped-data counters. Sample times are media units; "
            "Response Time, Request Time and Last Used are separate cache-entry UTC dates, "
            "not playback times. Multiple distinct dates stay in the context JSON; "
            "a scalar date is blank when the resource has conflicting values. "
            "Reddit references require an exact stored media URL. Browser records require "
            "an explicit URL/post-ID relationship and one supplied profile in the same "
            "evidence root, Android user and CE/DE storage class. The app cache does not "
            "encode its browser profile, so Browser Profiles lists candidates, not an "
            "authenticated profile assignment. No match is based on time proximity. "
            "DFRWS 2021 produced 12 clips from three "
            "low-resolution resources, using surviving original initialization data. "
            "Recovery Method, Width, Height, Audio, Video Timebase and Warnings "
            "were uniform in that run: rebuilt H.264 MP4, 170, 96, No, 16384 and [] "
            "respectively. Those fields are retained to distinguish configurations "
            "and skipped-track warnings on other caches. For progressive MP4 byte "
            "copies, Video Frames, Video Seconds, Width, Height, Audio and Video "
            "Timebase are empty because no decoder is used to inspect the copied "
            "stream. All three resources were Scrubber preview references; one post "
            "was promoted. Browser Profiles, Android User ID and Metadata Status were "
            "uniform: [Default], 0 and HTTP metadata parsed respectively. "
            "Media Role and Browser Relationship were uniform: Scrubber preview "
            "and Post ID in cached request URL respectively. Post Titles and Post URLs "
            "are independently deduplicated summaries; exact pairs remain in Post Context. "
            "Promoted (as stored) says Not recorded when the field is absent. "
            "Source File retains per-file sample provenance alongside Resource ID "
            "to distinguish contributing files from contextual sources. Cache Metadata "
            "preserves full stored UTC precision and HTTP headers; typed LAVA datetime "
            "fields use the framework's integer-second representation. The provenance and context files "
            "are chromeCacheVideos_provenance.json and chromeCacheVideos_context.json "
            "in the Chromium report directory."
            " Resource-level events are written automatically to the standard "
            "_Timeline/tl.db through the timeline helper using separate event rows. "
            "The video table is not copied into the timeline. One source record/time "
            "type can link several clips or resources. Event times describe HTTP/cache "
            "activity, stored History/session navigation, or Media History record "
            "updates, not playback start. Full event records are also retained in "
            "chromeCacheVideos_events.json. There is one selectable artifact and one "
            "recovery pass; no second artifact needs to be enabled."
        ),
        "paths": (
            "*/com.android.chrome/cache/[Cc]ache/*",
            "*/com.android.chrome/cache/[Cc]ache_[Dd]ata/*",
            "*/com.android.chrome/app_chrome/*/History*",
            "*/com.android.chrome/app_chrome/*/Media History*",
            "*/com.android.chrome/app_chrome/*/Sessions/Tabs_*",
        ),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "video",
        "sample_data": {
            "synthetic_h264": "Synthetic H.264 pattern | 1 row: video only, 96x64, 60 samples and 2.021333 seconds from four cache entries; no initialization header supplied.",
            "galaxys10_a10": "DFRWS 2021 public subset | 12 rows: rebuilt video-only clips from three scrubber-preview resources, 170 samples/seconds at 170x96; HTTP/index times, Reddit references and related History visits; Media History empty; surviving initialization used; full archive hash not verified.",
        },
    },

}

import json
from pathlib import Path

from scripts.chrome_cache_video import MAX_CLIP_BYTES, recover_files
from scripts.chrome_cache_context import (
    build_context, cache_input, clip_source_ids, context_sources, json_text, resource_events,
)
from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, check_in_embedded_media, logfunc, timeline


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


def _write_events(context, enriched):
    """Write resource events, rather than duplicating one cache event per clip."""
    events = resource_events(enriched)
    folder = Path(context.get_report_folder())
    (folder / "chromeCacheVideos_events.json").write_text(json_text(events), encoding="utf-8")
    if not events:
        return
    headers = ("Timestamp", "Event Type", "Resource IDs", "Resource URLs", "Clip SHA256",
               "Android User ID", "URL", "Title", "Record ID", "Event Source File",
               "Relationship", "Profile Match", "Event Details", "Source File")
    rows = [(event["time"], event["kind"], json_text(event["resource_ids"]),
             json_text(event["resource_urls"]), json_text(event["clip_hashes"]),
             event["android_user"], event["url"], event["title"], event["record_id"], event["source"],
             event["relation"], event["profile_match"], json_text(event["details"]),
             json_text(event["source_files"])) for event in events]
    # The standard helper locates the run root two parents above a category folder.
    # Standalone/test callers may supply an arbitrary folder: keep all their output
    # inside that folder rather than writing into a shared ancestor directory.
    anchor = folder if folder.parent.name == "_HTML" else folder / "_HTML" / "Chromium"
    timeline(str(anchor), "Chrome Cache - Videos", rows, headers)
    logfunc(f"Chrome Cache: {len(events)} resource-level timeline events")


@artifact_processor
def get_chromeCacheVideos(context):
    data_headers = (
        ("Video", "media"),
        ("Response Time", "datetime"),
        ("Request Time", "datetime"),
        ("Last Used", "datetime"),
        "Resource URLs",
        "Post Titles",
        "Post URLs",
        "Media Role",
        "Promoted (as stored)",
        "Related Browser URLs",
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
    output, manifest = recover_files([(p, r) for p, r in inputs if cache_input(r)], context.get_report_folder())
    enriched = build_context(inputs, manifest)
    (Path(context.get_report_folder()) / "chromeCacheVideos_context.json").write_text(
        json_text(enriched), encoding="utf-8")
    provenance = "chromeCacheVideos_provenance.json"
    manifest["output_directory"] = output.name
    (Path(context.get_report_folder()) / provenance).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    local_sources = {relative: path for path, relative in inputs}
    sources = manifest["sources"]
    for clip in manifest["clips"]:
        source_ids = clip_source_ids(clip)
        resource = enriched["resources"][clip["context_resource_id"]]
        paths = sorted({sources[source]["path"] for source in source_ids})
        if not paths:
            continue
        destination = output / clip["file"]
        if destination.stat().st_size > MAX_CLIP_BYTES:
            logfunc("Chrome Cache: output exceeded the media registration limit")
            continue
        ref = check_in_embedded_media(
            local_sources[paths[0]],
            destination.read_bytes(),
            name=destination.name,
            force_type="video/mp4",
            force_extension=".mp4",
        )
        if not ref:
            logfunc("Chrome Cache: media registration failed")
            continue
        copied = clip.get("kind") == "complete_mp4_carved"
        data_list.append(
            (
                ref,
                _unique_time(resource, "response_time"),
                _unique_time(resource, "request_time"),
                _unique_time(resource, "last_used"),
                json_text(resource["urls"]),
                _summary(resource["posts"], "title"),
                _summary(resource["posts"], "permalink"),
                _summary(resource["posts"], "role"),
                _promotion(resource),
                _summary(resource["activities"], "url"),
                _summary(resource["activities"], "relation"),
                resource["android_user"],
                json_text(resource["profile_candidates"]),
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
                "; ".join(sorted({record["status_detail"] for record in resource["metadata"]})) or "Metadata unavailable",
                json_text(resource["metadata"]),
                json_text(resource["posts"]),
                json_text(resource["activities"]),
                json_text(context_sources(resource)),
            )
        )
    _write_events(context, enriched)
    logfunc(
        f"Chrome Cache: {len(data_list)} videos exported; status {manifest['status']}; "
        f"statistics {json.dumps(manifest['statistics'], sort_keys=True)}; "
        f"provenance {provenance}"
    )
    return data_headers, data_list, "\n".join(str(path) for path, _ in inputs)

