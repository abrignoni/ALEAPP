# ALEAPP ZIP literal prefilter: validation

This ports the same conservative ZIP search optimization as [iLEAPP PR #2801](https://github.com/abrignoni/iLEAPP/pull/2801). The production change adds **19 lines and changes two lines** in `scripts/search_files.py`, plus separate fabricated regression tests and this note. Other seekers, `peek`, parsers and dependencies are unchanged.

## Matching and regression checks

A normalized pattern without brackets must contain every literal segment between `*` and `?`. The longest segment is used as a necessary-substring check before the existing wildcard matcher. Filenames retain the existing normalized `root/` prefix. Any bracket syntax, including malformed classes, or an empty literal retains the original matcher path. No retained filename index is added.

The new helper and ZIP search method have the same AST as the tested iLEAPP implementation. Nine new tests cover 24,008 generated POSIX/Windows-normalization comparisons, real ZIP staging/order/bytes, bracket fallback, sidecars/directories, cached first-hit behavior, forced re-staging, no matches, corrupt-member continuation and reduced matcher calls.

- macOS arm64, Python 3.14.6 baseline: 2,641 tests, zero failures/errors, 14 skips.
- Candidate: **2,650 tests, zero failures/errors, 14 skips**, including the nine new tests.
- Native Windows 11 ARM64: **35 fabricated ZIP/filter/repeated-member/Windows-name tests passed on both Python 3.11.9 and 3.12.10**, with zero failures/errors/skips. Existing isolated interpreters were used without dependency updates; source copies were verified unchanged. A full Windows suite and native Windows corpus/performance run were not performed for this port.

## Corpus profile comparison

A hash-verified local ZIP input was read without modification. Source size and mtime remained unchanged afterward. Baseline/candidate used the same code apart from the search method, input, profile, `--hash`, output naming and instrumentation. The saved original method was compiled before the baseline run. All eight fresh-process outputs were retained: unmeasured baseline/candidate warm-ups, then B1, C1, C2, B2, B3, C3. Medians exclude warm-ups. VMs were running but native tests, unit suites and other benchmark jobs had finished before these serial timing runs. These are warm shared-machine results, not cold or isolated-hardware measurements.

All eight outputs matched in ordered search fingerprints, cache flags, match/staged counts, typed/ordered evidence database contents and relationships, manifest, artifact HTML tables, media, exports, staged paths/bytes and non-SHM filesystem mtimes. Database integrity checks passed. Artifact execution timestamps/output folders and process-local framework file IDs were canonicalized; evidence dates and artifact-row order were retained. Framework file-ID records/relations preserve full record identity and multiplicity. Runtime SHM filesystem mtimes and export SQLite storage sidecars are excluded, with logical database contents read normally. No parser-error markers were found. Detailed reports and raw logs are retained locally.

| Focused measurement | Baseline | Candidate |
| --- | ---: | ---: |
| Wall median (range), seconds | 2.370791 (2.366377–2.470289) | 1.396213 (1.365191–1.420267) |
| Search median, seconds | 1.174262 | 0.225520 |
| Peak RSS median, MiB | 358.70 | 355.61 |

The input had 82,679 eligible members. Positive output comparison covered 58 rows across 5 artifact outputs, 10 database tables, 80 staged files and 7 exports. The profile selected `contacts`, `get_calllog`, `get_sms_mms_combined`, `get_chromeAutofill`.

The measured focused workload was **1.70x faster**, a **41.1% elapsed reduction**. This is a four-artifact profile, not a full all-artifact Android speedup claim.

Small RSS differences are not claimed as memory savings.

## Controlled large-name scan

This separate enumeration-only probe used the actual baseline/candidate methods with an already-staged identity mapping. No archive extraction or corpus payload is involved. There are 250,000 fabricated cache paths plus three known matches, for **250,003 names**. Each pattern has three warm repetitions with alternating version order. Every ordered result matched both the other method and an independent `fnmatchcase` result.

| Pattern | Matches | Baseline median, seconds | Candidate median, seconds |
| --- | ---: | ---: | ---: |
| `*/databases/History` | 1 | 0.065805 | 0.033536 |
| `*/databases/contacts2.db` | 1 | 0.064778 | 0.032752 |
| `*/settings/*.json` | 1 | 0.164981 | 0.035488 |
| `*/not-present/file.db` | 0 | 0.064961 | 0.036658 |
| `*[ab].db` | 0 | 0.142146 | 0.144281 |
| `*` | 250,003 | 0.073606 | 0.076941 |

For the four selective patterns, the sum of per-pattern medians fell from **0.360525 to 0.138434 seconds**, or **2.60x**. This is a controlled search-stage result, not a complete extraction/report speedup.

Bracket-fallback and match-all controls can pay overhead; their exact medians are included above rather than claiming every pattern improves. Larger member lists and selective literals benefit most. The change adds no second retained filename collection.

## Provenance and reproduction

- Baseline commit: `e8c5bb4c6ca9ada7b3fe2766a52c74f26c051916`.
- Original search module SHA256: `f2782127f816a5d08bfbab32b2e59004dcd57716e45ba3840efb31edc2064707`.
- Candidate SHA256: `747cf10ecb5a66a83457af67f5e7c81d2b064b6c52ba364c89bc9ed99099f4d1`.

Run the same input/profile/options in separate baseline and candidate output directories, warm both versions, alternate order and retain all repetitions. The private corpus payload is not part of this PR. A profile uses `leapp: "aleapp"`, `format_version: 1` and a `plugins` array of artifact IDs.

```sh
python3 -B aleapp.py -t zip -i /path/to/image.zip -o /path/to/new-output \
  -m /path/to/profile.ilprofile --hash --custom_output_folder report
python3 -B -m unittest discover -s admin/test/scripts -p 'test_seeker_zip_literal_filter.py'
python3 -B -m unittest discover -s admin/test/scripts -p 'test_*.py'
```

The filter-only implementation is a small change with workload-dependent speed benefits. Validation supports review without extending claims to other inputs, untested runtimes or unrelated parser behavior.
