#!/usr/bin/env python3
"""Runs every committed test case and compares the output to its recorded baseline.

The interactive recorder is admin/test/scripts/test_module.py: it runs a module's
artifacts against the case zips and writes timestamped snapshots (headers plus
full rows) under admin/test/results/<module>/. This script is the other half:
it re-runs the same artifacts through the same machinery and fails when the
output no longer matches the latest snapshot, so the committed cases act as
regression tests in CI.

Baselines are ordinary committed files. To accept a new baseline after a
deliberate parser change, re-record it in the same PR:

    python admin/test/scripts/test_module.py <module> -a all -c all

then commit the new snapshot (and delete the superseded one), so the reviewer
sees the row-level diff next to the code that caused it.

Comparison notes:
- Rows are compared as unordered multisets: SQLite result order without an
  ORDER BY is not stable across platforms and a reorder is not a regression.
- Both sides are normalized before comparison: values are passed through a
  JSON round-trip (matching how snapshots were serialized) and the per-run
  extraction directory admin/test/temp/extract_<name>_<epoch> is replaced by
  a fixed token, since its epoch differs on every run by construction.

Units listed in admin/test/cases/known_failures.json (unit -> reason) run and
report but do not gate, so a unit can be excluded deliberately, with a stated
reason, instead of blocking every PR while it is being repaired. A known
failure that passes again is flagged so the entry gets removed.

--storage-views runs a different comparison from the same case zips. An Android
full file system extraction carries the same app data directory under several
spellings (data/data/<pkg>, data/user/0/<pkg>, ...) and can carry a second
Android user at data/user/<n>/<pkg>. A single-view fixture cannot detect the
two defects that follow, so this mode synthesizes them by restaging the zip's
data/data members and checks the arithmetic per artifact:

- duplicate view (data/user/0): the same file under a second spelling must not
  change the row count. A doubled count means the storage views are not being
  collapsed (storagePathViews.unique_files is the shared fix).
- second tenant (data/user/10): a second Android user's copy must exactly
  double the row count. An unchanged count means the second user's data is
  read into files_found and then silently dropped, which is what a
  first-match-wins accessor does.

Counts are the comparison, not row contents: the two runs extract into
different temp directories and restage mtimes, so content equality would fail
on values legitimately derived from the reported file's own path. A unit whose
base run yields no rows is skipped as uninformative, not passed. Exclusions
use the same known_failures.json with the leg appended to the unit key, e.g.
"galleryVault.galleryvault_folders.pixel7a_a14[second-tenant]".

Exit status is 1 if any non-excluded unit failed, errored, or has no
baseline; 0 otherwise.
"""
import argparse
import json
import os
import re
import sys
import tempfile
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(REPO_ROOT))

CASES_DIR = REPO_ROOT / "admin" / "test" / "cases"
RESULTS_DIR = REPO_ROOT / "admin" / "test" / "results"
TEMP_EXTRACT_RE = re.compile(r"admin/test/temp/extract_[A-Za-z0-9_]+_\d+")
TEMP_TOKEN = "<extract-dir>"
KNOWN_FAILURES_PATH = CASES_DIR / "known_failures.json"
COMPLETION_MARKER = "Test case comparison complete"


def discover_modules():
    """Module names that have a committed case file."""
    return sorted(p.name[len("testdata."):-len(".json")]
                  for p in CASES_DIR.glob("testdata.*.json"))


def latest_baseline(module, artifact, case):
    """Path of the newest snapshot for one (module, artifact, case), or None."""
    pattern = f"{module}.{artifact}.{case}.*.json"
    candidates = sorted((RESULTS_DIR / module).glob(pattern))
    return candidates[-1] if candidates else None


def normalize_rows(rows):
    """Rows as a sorted list of JSON strings, with per-run paths tokenized."""
    normalized = []
    for row in rows:
        text = json.dumps(row, default=str, ensure_ascii=False)
        normalized.append(TEMP_EXTRACT_RE.sub(TEMP_TOKEN, text))
    return sorted(normalized)


def normalize_headers(headers):
    return json.loads(json.dumps(headers, default=str))


def compare(fresh_headers, fresh_rows, baseline):
    """Returns a list of difference descriptions; empty means match."""
    problems = []
    base_headers = normalize_headers(baseline.get("headers", []))
    if normalize_headers(fresh_headers) != base_headers:
        problems.append(f"headers differ: now {normalize_headers(fresh_headers)!r}, "
                        f"recorded {base_headers!r}")
    now = normalize_rows(fresh_rows)
    recorded = normalize_rows(baseline.get("data", []))
    if now != recorded:
        now_set, rec_set = set(now), set(recorded)
        gained = sorted(now_set - rec_set)
        lost = sorted(rec_set - now_set)
        problems.append(f"rows differ: now {len(now)}, recorded {len(recorded)}; "
                        f"{len(gained)} new, {len(lost)} missing")
        for label, rows in (("new", gained), ("missing", lost)):
            for row in rows[:2]:
                problems.append(f"  {label}: {row[:160]}")
    return problems


def make_view_variant(src_zip, dst_zip, view):
    """Copy the case zip, restaging each data/data member under a second view.

    Returns the number of members added. Zero means the fixture holds nothing
    under a data/data spelling, so no variant can be synthesized from it.
    """
    added = 0
    with zipfile.ZipFile(src_zip) as zin, \
            zipfile.ZipFile(dst_zip, 'w', zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            payload = zin.read(info.filename)
            zout.writestr(info, payload)
            anchored = '/' + info.filename
            if '/data/data/' in anchored:
                alt = anchored.replace('/data/data/', view, 1)[1:]
                zout.writestr(alt, payload)
                added += 1
    return added


def count_rows(test_module, zip_path, module, artifact, case_data):
    """Fresh row count for one artifact against one zip."""
    os_version = case_data.get("image_info", {}).get("os_version")
    headers, rows, _elapsed, _commit, _media, _embedded = test_module.process_artifact(
        zip_path, module, artifact, case_data["artifacts"][artifact],
        target_os_version=os_version)
    _headers, rows = test_module.process_data(headers, rows)
    return len(rows)


def run_storage_views(test_module, module, artifact, case, case_data):
    """Runs the two storage-view checks; returns [(unit suffix, status, detail)].

    Base and variants are all fresh runs of the same tool version, so the
    comparison cannot be skewed by a stale baseline.
    """
    zip_path = CASES_DIR / "data" / module / f"testdata.{module}.{artifact}.{case}.zip"
    if not zip_path.exists():
        return [("", "BROKEN", f"case declares files but zip is missing: {zip_path}")]
    try:
        base = count_rows(test_module, zip_path, module, artifact, case_data)
    except Exception as ex:  # pylint: disable=broad-except
        return [("", "ERROR", f"base run: {type(ex).__name__}: {ex}")]
    if base == 0:
        return [("", "SKIP", "base run has 0 rows; the arithmetic cannot discriminate")]

    (CASES_DIR.parent / 'temp').mkdir(parents=True, exist_ok=True)
    results = []
    legs = (("[duplicate-view]", '/data/user/0/', base,
             "a duplicate storage view of the same container must not change the count"),
            ("[second-tenant]", '/data/user/10/', 2 * base,
             "a second Android user's copy must exactly double the count"))
    for suffix, view, expected, rule in legs:
        handle = tempfile.NamedTemporaryFile(
            suffix='.zip', dir=str(CASES_DIR.parent / 'temp'), delete=False)
        variant = Path(handle.name)
        handle.close()
        try:
            added = make_view_variant(zip_path, variant, view)
            if not added:
                results.append((suffix, "SKIP", "no data/data members to restage"))
                continue
            got = count_rows(test_module, variant, module, artifact, case_data)
        except Exception as ex:  # pylint: disable=broad-except
            results.append((suffix, "ERROR", f"{type(ex).__name__}: {ex}"))
            continue
        finally:
            variant.unlink(missing_ok=True)
        if got == expected:
            results.append((suffix, "PASS", f"{base} rows -> {got} rows"))
        else:
            results.append((suffix, "FAIL",
                            f"{base} rows -> {got} rows, expected {expected}: {rule}"))
    return results


def run_one(test_module, module, artifact, case, case_data):
    """Runs one artifact against one case zip; returns (status, detail)."""
    zip_path = CASES_DIR / "data" / module / f"testdata.{module}.{artifact}.{case}.zip"
    if not zip_path.exists():
        return "BROKEN", f"case declares files but zip is missing: {zip_path}"
    baseline_path = latest_baseline(module, artifact, case)
    if baseline_path is None:
        return "NO_BASELINE", ("no recorded snapshot; record one with "
                               f"test_module.py {module} -a {artifact} -c {case}")
    try:
        os_version = case_data.get("image_info", {}).get("os_version")
        headers, rows, _elapsed, _commit, _media, _embedded = test_module.process_artifact(
            zip_path, module, artifact, case_data["artifacts"][artifact],
            target_os_version=os_version)
        headers, rows = test_module.process_data(headers, rows)
    except Exception as ex:  # pylint: disable=broad-except
        return "ERROR", f"{type(ex).__name__}: {ex}"
    with open(baseline_path, encoding="utf-8") as f:
        baseline = json.load(f)
    problems = compare(headers, rows, baseline)
    if problems:
        return "FAIL", "\n    ".join([f"vs {baseline_path.name}"] + problems)
    return "PASS", f"{len(rows)} rows match {baseline_path.name}"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--module", action="append",
                        help="limit to this module (repeatable; default: all)")
    parser.add_argument("--list", action="store_true", help="list runnable units and exit")
    parser.add_argument("--strict", action="store_true",
                        help="ignore known_failures.json and gate on everything")
    parser.add_argument("--storage-views", action="store_true",
                        help="synthesize a duplicate storage view and a second "
                             "Android user from each case zip and check the "
                             "row-count arithmetic instead of the baselines")
    args = parser.parse_args(argv)

    known = {}
    if KNOWN_FAILURES_PATH.exists() and not args.strict:
        with open(KNOWN_FAILURES_PATH, encoding="utf-8") as f:
            known = json.load(f)

    os.chdir(REPO_ROOT)
    import test_module  # noqa: E402  imported late so sys.path is set

    modules = args.module or discover_modules()
    counts = {}
    failures = []
    for module in modules:
        cases_file = CASES_DIR / f"testdata.{module}.json"
        if not cases_file.exists():
            print(f"{module}: no case file", flush=True)
            failures.append((module, "BROKEN", "case file missing"))
            continue
        with open(cases_file, encoding="utf-8") as f:
            cases = json.load(f)
        for case, case_data in sorted(cases.items()):
            for artifact, artifact_data in sorted(case_data.get("artifacts", {}).items()):
                if artifact_data.get("file_count", 0) == 0:
                    continue
                if args.list:
                    print(f"{module} {artifact} {case}")
                    continue
                if args.storage_views:
                    results = run_storage_views(test_module, module, artifact,
                                                case, case_data)
                else:
                    results = [("",) + run_one(test_module, module, artifact,
                                               case, case_data)]
                for suffix, status, detail in results:
                    unit = f"{module}.{artifact}.{case}{suffix}"
                    if unit in known and status not in ("PASS", "SKIP"):
                        print(f"[KNOWN_FAIL ] {unit}: {status}; excluded: {known[unit]}",
                              flush=True)
                        counts["KNOWN_FAIL"] = counts.get("KNOWN_FAIL", 0) + 1
                        continue
                    counts[status] = counts.get(status, 0) + 1
                    if unit in known and status == "PASS":
                        detail += " (listed in known_failures.json; remove its entry)"
                    print(f"[{status:11s}] {unit}: {detail}", flush=True)
                    if status not in ("PASS", "SKIP"):
                        failures.append((unit, status, detail))
    if args.list:
        return 0

    print()
    print(f"{COMPLETION_MARKER}: " +
          ", ".join(f"{k}={v}" for k, v in sorted(counts.items())) if counts else "nothing ran")
    if failures:
        print(f"\n{len(failures)} unit(s) need attention:")
        for unit, status, _detail in failures:
            print(f"  {status:11s} {unit}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
