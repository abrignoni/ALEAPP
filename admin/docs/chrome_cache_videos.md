# Chrome cache video recovery and context

Version 0.4.0 provides one selectable artifact in the Chromium category:
**Chrome Cache - Videos**. One recovery pass produces a readable video table
with cache dates, resource URLs, post titles/permalinks, preview/promotion labels
and related browser URLs. Resource-level timeline events are generated
automatically in the same run; no second artifact is selected.

The helpers are `scripts/chrome_cache_video.py` (unchanged recovery engine) and
`scripts/chrome_cache_context.py`. They use Python's standard library and existing
ALEAPP interfaces. No runtime downloads, subprocesses or additional dependencies
are introduced. FFmpeg is optional for independent tests.

## Input and attribution

Package-anchored patterns cover Chrome's flat `cache/Cache`, direct
`cache/Cache_Data` and nested `cache/Cache/Cache_Data`, plus
`app_chrome/<profile>/History*`, `Media History*` and `Sessions/Tabs_*`.
Other browser packages are outside this artifact's coverage. A detached cache
must retain its app path for ALEAPP's seeker.

`storagePathViews.unique_files` removes duplicate storage views of one user's
files. Evidence roots, Android users and CE/DE storage remain separate.
Paths in rows are extraction-relative, normalized to forward slashes.

Sparse media and HTTP siblings must have the same cache directory and complete
key. JSON references also require the same cache directory and credential/network
isolation prefix. Exact media URL matching preserves renditions and query tokens;
a shared hostname or media ID alone is insufficient.

An app-level cache does not encode its browser profile. Browser Profiles lists
supplied candidates. Browser joins require exactly one supplied profile in the
same evidence root, Android user and storage class, and Profile Match explicitly
labels it a candidate. With multiple supplied profiles no cross-file browser
join is made. Cache-local post references and reconstruction still work.
No association is based on temporal proximity.

## Recovery

The engine reads structurally bounded Simple Cache stream-1 payloads and
individual sparse ranges. A separately counted carving fallback handles unknown
payload boundaries. Original compressed samples are copied, never transcoded;
each copied sample's SHA-256 is checked, then input hashes are checked again.
A separate progressive MP4 is copied byte for byte when recognized.

H.264 needs usable SPS/PPS, an IDR frame and a stored timebase from original
initialization or adjacent `sidx` boxes. No default frame rate or timebase is
guessed. Gaps, conflicting samples and parameter-set changes split clips.
Leading dependent frames are omitted. AAC requires its original configuration.
Encrypted/auxiliary sample structures, unsupported codecs, absolute fragment
data offsets and boxes split across cache ranges are not reconstructed.

Recovery limits: 2 GiB/input, 32 MiB/metadata box or sample, 250,000 samples/trun,
128 MiB/registered derivative. Clips split at an IDR after five minutes; still
oversize clips are skipped. Counters record partial coverage.

**No runtime decoder validation is performed.** Outputs are reconstruction
candidates, not necessarily complete originals or evidence of viewing.
The public DFRWS case uses surviving original initialization. Removing it in a
controlled experiment produced no clips; a separate synthetic case demonstrates
the supported header-reconstruction path.

## Metadata and timestamps

The context reader obtains stream 0 from its EOF trailer without loading large
media bodies. Bounds and the stored cache-key SHA-256, when present, are checked.
Full cache CRC and filename-hash validation are not implemented.
HttpResponseInfo persistence versions 1–3 and Simple Cache index v9 are supported.
Unknown layouts retain unresolved status rather than guessed values.

A missing or unreadable HTTP sibling does not discard a readable index time.
Its relationship is labeled by filename hash and directory, with HTTP metadata
unavailable. A conflicting sibling key is rejected.

| Date/event | Meaning |
| --- | --- |
| Request Time / HTTP request time | Stored request time, possibly a later validation |
| Response Time / HTTP response time | Stored receipt of response headers, possibly a later validation |
| Original HTTP response time | Separately stored original response time, when present |
| Last Used / Cache last used | Entry's last-used value stored in the cache index |
| HTTP Date / Last-Modified | Server header strings, preserved as stored |
| History visit / Session navigation | Browser record's stored time with an explicit URL/post-ID relationship |
| Media History playback/session | Record update time, not labeled as playback start |

Cache times do not establish viewing. One entry can cover multiple byte ranges;
its timestamp does not date each fragment independently. Media DTS/duration
units remain separate from wall-clock dates. There is no filesystem-mtime
fallback, timestamp-plus-DTS playback calculation or inferred watch event.

Several distinct dates for one resource leave the scalar video-table date blank;
all records remain in Cache Metadata. LAVA's typed datetime fields use the
existing integer-second representation. Full UTC precision is preserved in
Cache Metadata, Activity Context, the event JSON and context JSON; TSV and `tl.db` retain the
aware UTC timestamp strings.

## Post and browser context

Bounded cached Reddit JSON, including gzip, is searched for exact references in
`reddit_video` / `reddit_video_preview` objects. Post IDs, titles, permalinks,
media field names and stored `promoted` values are retained.
`scrubber_media_url` is labeled Scrubber preview. Repeated secure_media/media
references merge their field names. Other sites' application JSON and arbitrary
HTML/JavaScript are not currently interpreted.

History, Media History and SNSS records are retained only for explicit
relationships: exact resource URL, referenced media-post permalink, or the Reddit
post ID in the cached request's `source_post_id`.
A source-post visit relates to the feed request; it does not prove that an
embedded video or ad was displayed or played. Repeated visits retain their own
times and are not all assigned to the earlier media request.

SQLite reads use disposable copies with WAL/SHM/journal sidecars and the existing
read-only helper. This prevents shared-memory writes to extraction files.
Missing schemas and unreadable files are counted. Android `app_tabs` binary state
is not newly decoded by this module.

Context limits: 128 MiB/ancillary input, 4 MiB/HTTP metadata or compressed JSON
input, 32 MiB/decompressed JSON or index, 100,000 JSON traversal nodes. Limits or
unsupported structures retain diagnostics/unresolved status. Contributing context
files and inspected browser files have SHA-256 records, including sidecars.
A source change before/during context analysis aborts that artifact.

## Outputs and execution

The video table starts with typed media, Response Time, Request Time, Last Used,
Resource URLs, Post Titles, Post URLs, Media Role, Promoted (as stored), Related
Browser URLs and Browser Relationship. Android User ID and candidate Browser
Profiles follow. Recovery details and Resource ID remain available, followed by
Cache Metadata, Post Context, Activity Context and Context Source Files.
Source File identifies compressed-sample and initialization evidence separately
from context sources. Progressive copies have blank stream details because no
decoder inspects them. Post Titles/Post URLs are independently deduplicated
summaries; exact title/URL/promotion pairs remain in Post Context. Missing
promotion flags are displayed as Not recorded rather than inferred as false.

There is one HTML/TSV/LAVA artifact table. The parser also calls the standard
public timeline helper with separate event rows, writing _Timeline/tl.db.
The declared output_types intentionally excludes the decorator's generic
timeline output: copying clip rows there would duplicate resource events.
There is no extra event artifact or second LAVA table. The same input is recovered
once, and timeline generation has no dependency on artifact execution order.

Timeline records contain Timestamp, Event Type, Resource IDs, Resource URLs,
Clip SHA256, Android User ID, URL, Title, Record ID, Event Source File,
Relationship, Profile Match, Event Details and Source File. One event can link
several clips/resources; a shared History record remains one row. Cache entries
have separate time-type events even when their times coincide. Event Source
File distinguishes the event producer from the entire evidence chain.

The Chromium report directory contains:

- chromeCacheVideos_provenance.json: recovery hashes, offsets, sample times,
  initialization sources, counters and context resource IDs.
- chromeCacheVideos_context.json: contextual evidence, source hashes and diagnostics.
- chromeCacheVideos_events.json: the complete automatically generated event list.

Resource IDs/output hashes link video rows, contextual evidence and timeline
records. Typed LAVA date fields retain integer seconds; Cache Metadata and
Activity Context preserve full UTC precision in that same video row.

## Fixtures

Three cases each include a ZIP and committed video-table baseline; unit and
ZIP integration checks additionally inspect the generated timeline:

1. Four synthetic H.264 fragment entries without HTTP pickle dates: one video,
   zero events. Separate synthetic initialization supplies AAC in unit tests.
2. Sixteen unmodified public DFRWS 2021 Samsung S10 files: five recovery sources,
   three HTTP siblings, one index, three cached Reddit JSON responses, History,
   empty Media History and two SNSS files. Expected: 12 videos, 16 events.
3. Nine entirely synthetic files: four fragments with HTTP metadata, index,
   gzip Reddit JSON, History, Media History and SNSS. Expected: one video,
   17 events, including synthetic playback/session updates.

Every ZIP is below 10 MB. `dfrws2021_sources.json` contains all 16 public source
hashes and 12 derivative hashes. No private case media is distributed.

The synthetic content has 60 H.264 samples at 96x64, a 90,000-unit timebase,
181,920 duration units (2.021333333333333 seconds), and 95 AAC samples when its
initialization is supplied. Original fixture parameters: testsrc2 96x64/30 fps,
440-Hz/48-kHz sine, two seconds, libx264 ultrafast/yuv420p, GOP 30, no B frames,
repeated parameter sets, AAC stereo, video timebase 90000,
frag_keyframe+empty_moov+default_base_moof, fragment duration 500000 microseconds.
FFmpeg is not required to run the committed fixtures.

## Validation

Tested against ALEAPP `285fe70b7e3e83f37bdfdb2ede69a4ee62d0670b`,
Python 3.12 on Linux x86_64. Actual ZIP input supplies all 871 public Chrome
cache files plus four browser files. It produces 12 HTML/TSV/LAVA videos,
12 media items/references and 16 automatically generated timeline events:
3 request, 3 response, 3 last-used, 4 History visits and 3 session navigations.
All derivative hashes match the previously independently decoded outputs.

These are three 170x96 scrubber-preview resources, 170 video samples/seconds in
total without audio; one post is explicitly promoted. No direct visits to their
media-post permalinks or Media History playback records were found. Related page
visits retain their actual weaker relationship.

Controlled user-10 duplication plus a duplicate user-0 alias produces exactly
24 video rows and 32 timeline rows, with six distinct resources.
LAVA deduplicates identical derivative bytes into 12 items with 24 references.
This is controlled duplication, not an independently acquired second user.
The strict report checker confirms exact doubling with no findings.

Run checks sequentially: the repository fixture harness uses shared temporary
paths, so concurrent normal/storage-view runs can collide.

```text
python -m unittest discover -s admin/test/scripts -p 'test_chrome_cache_*.py'
python admin/test/scripts/run_test_cases.py --module chromeCacheVideos --strict
python admin/test/scripts/run_test_cases.py --module chromeCacheVideos --storage-views --strict
```

The validation JSON records complete suite, fixture, lint, report and clean-source
checks. Tests exercise rendition/query/partition boundaries, user/storage/root
separation, ambiguous profiles, missing siblings, unknown indexes, gzip limits,
source mutation, original WAL integrity and event deduplication.

The user confirmed successful GUI and ALEAPP tests of v0.2.0. This v0.4.0 unified
context/timeline update is locally tested; its native Windows/macOS build and the user's
full FFS run remain to be checked. Public member CRCs/local hashes were checked,
but the publisher's full 15-GB archive hash was not verified here.

## Integration and references

Copy the complete `scripts/` and `admin/` trees into the ALEAPP root, preserving
paths. Select Chrome Cache - Videos or load `chrome_cache_videos.alprofile`.
Static imports are visible to the existing packaging system. No shared ALEAPP
core, dependency or packaging configuration changes are needed.

Format sources: Chromium's pinned
[Simple Cache structures](https://chromium.googlesource.com/chromium/src/+/1bf6fdabfac5220b788324a5bf064f0a60457328/net/disk_cache/simple/simple_entry_format.h),
[HttpResponseInfo](https://chromium.googlesource.com/chromium/src/+/refs/tags/90.0.4430.91/net/http/http_response_info.cc),
[Simple Cache index](https://chromium.googlesource.com/chromium/src/+/refs/tags/90.0.4430.91/net/disk_cache/simple/simple_index.cc)
and the W3C
[ISO BMFF byte-stream format](https://www.w3.org/TR/2024/NOTE-mse-byte-stream-format-isobmff-20240723/).

