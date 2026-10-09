# DJI TXT artifact draft

Module: `scripts/artifacts/djiFlightRecordTxt.py`.

This is an initial ALEAPP contribution prepared for maintainer review. It follows
the current `__artifacts_v2__` / `@artifact_processor` conventions used by
ALEAPP's existing DJI DAT module. DIRK remains separate.

## Implemented

- Direct reading of original `DJIFlightRecord*.txt` binary evidence.
- Plain records for versions 1–6; local XOR decoding for versions 7–12.
- One row per binary record, including record type, byte offset and source path.
- OSD: latitude, longitude, relative height, component and horizontal speeds,
  heading, pitch, roll, GPS satellites, battery percentage and flight time.
- Gimbal: pitch, roll and yaw. Custom: UTC timestamp, speed and distance.
- Home: recorded home coordinates, altitude, home-recorded flag and return
  height. Home coordinates are kept separate from aircraft track coordinates.
- RC: raw stick/gimbal controls and return, shutter and record button flags.
- Smart Battery: useful time, voltage and percentage. Camera: single-photo,
  recording and SD flags, and mode/record time when present. Missing extension
  fields stay blank; they are not invented as zeroes.
- App tips and warnings, plus decoded hex for other payloads.
- Separate summary: flight start time, initial position, duration, distance,
  maximum heights/speeds, location strings, parsing warnings and encryption status.
- Versions 13–14: local Auxiliary Info decoding for metadata, with an explicit
  statement that encrypted telemetry requires DJI's keychain and was not decoded.
- No executables, third-party parser dependency, network access, keys, CSV import,
  replay viewer, media extraction or photo correlation.
- Rows returned to ALEAPP's report pipeline for HTML, TSV, timeline, LAVA and KML.

## Evidence interpretation

Custom timestamps are Unix milliseconds interpreted as UTC. Records without an
intrinsic timestamp use only a preceding valid Custom timestamp, labeled in the
Timestamp Basis column. Before the first Custom timestamp, the timestamp is blank.
An invalid Custom timestamp clears the preceding timestamp. No dates are inferred
from filenames, file modification times or the log's overall start time.

Telemetry is not carried between records: a gimbal row has gimbal fields, not a
position borrowed from an OSD record. Heading is stored yaw, not GPS course.
Horizontal speed for OSD is sqrt(speed_x² + speed_y²). Recorded altitude is
relative height, not established terrain clearance or altitude above sea level.
Unavailable, nonfinite, out-of-range or 0,0 coordinates are blank for mapping;
the underlying decoded bytes remain in the record's payload column.

Damaged record framing stops parsing and flags a partial parse. No heuristic
resynchronization silently creates records from arbitrary trailing bytes.
Unknown framed types are retained with decoded payload hex and an explicit
fields-not-implemented status. Versions outside 1–14 are unsupported.

## Validation so far

- 22 focused unit tests pass, including CRC's published reference vector,
  XOR versions 7–12, offset layouts, units, timestamp attribution, damaged data,
  unknown payloads and encrypted auxiliary metadata with a recovered record offset.
- Six ALEAPP fixture comparisons pass: synthetic legacy records, a public
  encrypted version 14 example and three original DF020 logs. Fixture provenance
  and licensing accompany the zips.
- DIRK's existing local version 14 log was checked locally for metadata-only
  handling. It is not included in the contribution fixtures.
- DF020 archive MD5 matches the publisher value. All 54,655 decoded payloads
  were checked against an independent decoder. All implemented OSD fields,
  gimbal angles, Custom timestamps, home coordinates, RC stick controls,
  battery data and camera recording fields agree with independent record readers.
  RC button flags and the camera single-photo enum follow the MIT Rust layout
  and targeted binary tests; the Python reference simplifies some of those fields.
- All 7,196 positions from the two June 19, 2018 flights fall within the polygon
  formed by the publisher's four GPS boundary coordinates and have the stated
  UTC date. The older October 2017 log is not claimed as a June salted flight;
  113 of its 3,207 positions are outside that June polygon.
- Two June logs carry four trailing bytes `39 30 00 00` immediately before Details.
  They do not match normal record framing. These are explicitly reported as a
  partial parse at offsets 555307 and 630036; no bytes are silently interpreted
  or discarded as a known end marker. All preceding framed records are retained.
- Original fixture bytes, hashes, row counts, source paths and comparison results
  are recorded in `admin/docs/df020_txt_validation.json`.
- A real ALEAPP CLI run restricted to the two new artifacts completed:
  TSV and LAVA contain 54,655 records and 3 summaries; KML contains 10,403
  positional points; the timeline contains 54,658 rows. Both HTML pages are
  generated. ALEAPP's default 50,000-row limit omits the large record table from
  its HTML page, pointing instead to complete TSV/LAVA outputs. JSON report
  checks are in `admin/docs/df020_txt_report_checks.json`.
- `sample_data` counts agree with the official emitter's full-archive run on
  October 5, 2026: 54,655 record rows and 3 summary rows, exit code 0 and zero
  errors. Its 56 warnings concern pre-existing artifact metadata elsewhere in
  ALEAPP, not this module. The previously missing optional SQLCipher and browser
  dependencies were installed only in the isolated testing environment.
  App version bytes in source Details are 4.2.16 for `dji.go.v4` and 3.1.11
  for `dji.pilot` (DJI GO). The contributed module adds no parser dependencies.

Commands from the ALEAPP root, using a Python environment with its dependencies:

```text
python -m unittest admin.test.scripts.test_dji_txt_parser -v
python admin/test/scripts/run_test_cases.py --module djiFlightRecordTxt
```

Record new baselines with `TZ=UTC` before running `test_module.py` as described
in ALEAPP's contribution guide.

## Review limitations

1. Less common record types and unused field extensions retain decoded payload
   hex rather than guessing their meaning. RC values are raw controls, not
   normalized percentages. Home altitude is labeled as recorded, without claiming
   an independently established vertical datum.
2. The two June record trailers remain unexplained. The MIT format source and
   the published Live555 record parser do not establish `39 30 00 00` as a known
   end marker. Parsing stops at the invalid framing and preserves a warning.
   The four bytes also form integer 12345 in little endian; that observation
   alone is not evidence of a sentinel's meaning.
3. Real corpus validation covers versions 9 and 11, plus a public metadata-only
   version 14 log. Other supported layouts are covered by synthetic tests.
4. No pull request has been published; the local review bundle is ready.

## October 5 final guide audit

Compared with the LEAPP module guide updated September 14, 2026. Missing values
now return None, and the shared DJI folder pattern is anchored to `dji.*` packages.
Both icons are present in ALEAPP's bundled Tabler CSS. Eleven available format
checks pass; the article's `check_container_markers.py` is not in this ALEAPP
checkout. Both new Python files pass pylint with zero warnings/errors under
CI's `--disable=C,R` settings and `PYTHONPATH=.`. A line-specific protected-access
exception allows the focused test of the private CRC primitive's reference vector.
All 22 unit tests and six fixture comparisons pass with updated record snapshots.

The fresh original-archive report uses a 60,000 HTML row limit and contains the
full record table. Its TSV, KML, timeline and LAVA counts are verified in
`df020_txt_final_report_checks.json`. Opening the project in LAVA to confirm its
displayed category/columns remains a manual check before submission. Automated
checks do not establish that application-level visual result. The beginner fork/PR
walkthrough is delivered separately as `ALEAPP_FORK_AND_PULL_REQUEST_GUIDE.md`.

## Sources

- [ALEAPP contribution guide](https://github.com/abrignoni/ALEAPP#contributing-artifact-plugins),
  checkout `62414e2601319c08f7f5e9a625de081f2c175140`.
- [dji-log-parser](https://github.com/lvauvillier/dji-log-parser), MIT,
  version 0.5.7 source bundled with DIRK: prefix, record, auxiliary and Details layouts.
  Copyright/license notice is retained inside the module.
- [crc64 crate](https://github.com/badboy/crc64-rs): Jones reference vector.
- [pydjirecord](https://github.com/rembish/pydjirecord), MIT: independent XOR
  key check and public encrypted-log fixture, not a runtime dependency.
- [VTO/NIST drone dataset](https://cfreds-archive.nist.gov/drone-images.html).
