Suggested title: Recover Chrome cache videos with HTTP metadata and timeline context

## What this changes

Adds recovery of supported cached MP4 clips, with HTTP/index timestamps, exact cached Reddit media references and related browser records. One selectable artifact produces a readable video table with context in LAVA and automatically writes deduplicated resource-level events to `tl.db` in the same recovery pass.

## For a new or changed artifact

- [x] Ran the tool against a real extraction and confirmed the row counts, not just that it imports.
- [x] Ran `python admin/scripts/check_artifact_output.py <report folder>` on that report and fixed or documented every finding.
- [ ] Checked it against a second app data directory where the platform provides one (a second user, account, or container). `--compare <multi-container report>` reads the scaling for you: it should be exactly double.
- [x] `notes`, `description` and `sample_data` say only what the data shows, and the numbers were re-derived from the finished run.

## Anything reviewers should know

The ZIP-input run used 871 public DFRWS 2021 Chrome cache files plus four browser files: 12 clips from three resources, and 16 events (three each for request, response and last-used times, four History visits and three session navigations). The cached JSON identifies these as scrubber-preview resources, including one promoted post. Cache presence and related page visits are not reported as playback. Media History is empty in this sample.

An independently acquired second user was unavailable. Controlled user-10 duplication plus a duplicate user-0 storage view produced exactly 24 videos and 32 events, with no strict report-checker findings; this is the available storage-isolation check, not an independent second case. All twelve derivative hashes match the previously independently decoded outputs.

Includes three fixture cases and three baselines, using public or explicitly synthetic data; every ZIP is under 10 MB. Local checks: 1,306 unit tests (10 skips), all 108 fixture comparisons, the global storage-view checks (130 passes, 52 uninformative skips and two existing known failures in other modules), and no new Pylint warnings. A single-selection ZIP integration check verifies readable overview columns, one LAVA artifact table, one recovery pass, and the independently structured timeline events. The complete validation record is included.

The recovery engine is pure Python and needs no runtime FFmpeg. It does not support every codec or missing-header layout. The public case uses surviving initialization. LAVA's typed date fields retain its integer-second format; full stored UTC precision is also present in structured metadata. App-level cache paths do not encode a browser profile, so browser relationships are qualified as a sole supplied profile candidate and withheld for multiple supplied profiles.

Tests here used Python 3.12/Linux and public extraction subsets, not a publisher-hash-verified download of the entire 15-GB archive. The user confirmed the earlier GUI/ALEAPP recovery build; the updated context/timeline build has not yet been independently tested by the user or a maintainer. No CI or native Windows/macOS build result is claimed.
