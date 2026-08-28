"""Guard against an artifact declaring a path pattern a sibling already covers.

`aleapp.py` searches an artifact's `paths` one pattern at a time and accumulates the
results::

    for artifact_search_regex in search_regexes:
        found = seeker.search(artifact_search_regex)
        ...
        files_found.extend(found)

There is no de-duplication across patterns, and `paths` uses stock `fnmatch`, where `*`
crosses `/`. So a broad pattern usually covers a narrower sibling completely, and every
file the narrow one names is appended to `files_found` twice. An artifact that iterates
that list then reads the file twice and reports its rows twice.

The failure is quiet. Nothing errors, the rows are real, and the count is simply double
what the evidence holds. It also travels into `sample_data`, so a recorded count taken
before the redundant pattern was noticed stays wrong after it is removed.

Measured on 2026-08-27: `installedappsGass` declared both
`*/com.google.android.gms/databases/gass.db*` and
`*/user/*/com.google.android.gms/databases/gass.db*`. The second names nothing the first
does not, so on an image carrying three storage views the store was read four times, not
three, and its recorded counts for two corpora were inflated accordingly.

`storagePathViews.unique_files` masks this, because an exact repeat shares a canonical
key. Artifacts using it are still reported, since the redundant pattern is worth removing
and its recorded counts are still suspect, but they are annotated as protected.

Subsumption is decided on literal runs rather than by sampling, so a reported pair is a
real superset relation and not a guess. Patterns using `?` or a character class are
skipped rather than guessed at. Partial overlap, where two patterns share some matches
without either covering the other, is NOT reported: it is common and usually harmless.
`imagemngCache` is the known instance (`*/*.cnt` and
`*/cache/image_manager_disk_cache/*.*` both match a `.cnt` file in that directory).

Usage::

    python3 admin/scripts/check_artifact_paths.py

Exit status is 1 when an artifact outside ALLOWED declares a subsumed pattern.
"""
import ast
import itertools
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ARTIFACTS_DIR = os.path.join(REPO_ROOT, 'scripts', 'artifacts')

# Known at the time this check was added. Each is a redundant pattern that should be
# removed rather than kept; the entry exists so the check can fail on anything NEW.
# Empty: every subsumed pattern known at the time this check was added was removed in
# the same change. A new entry here should be a deliberate, explained exception.
ALLOWED = set()

STANDARD_NOTE = (
    'Remove the narrower pattern: it names nothing the broader one does not, and every\n'
    'file it matches is appended to files_found twice. If the narrow pattern is meant to\n'
    'reach something the broad one misses, the broad one is wider than intended and it\n'
    'is the one to tighten.'
)


def runs(pattern):
    """Literal runs of a `*`-only glob, or None if it uses syntax we do not decide."""
    if '?' in pattern or '[' in pattern:
        return None
    return pattern.split('*')


def subsumes(broad, narrow):
    """True if every string matching `narrow` also matches `broad`.

    Decided on literal runs. A string matching `narrow` is its literal runs in order with
    arbitrary text between them, so `broad`'s literals must each sit wholly inside one of
    `narrow`'s runs, in order: text spanning a `*` of `narrow` is not guaranteed to be
    present. Anchoring is handled by requiring `broad`'s prefix and suffix to sit inside
    `narrow`'s first and last runs.
    """
    a, b = runs(broad), runs(narrow)
    if a is None or b is None or broad == narrow:
        return False

    a_prefix, a_suffix, a_middle = a[0], a[-1], a[1:-1]
    if len(a) == 1:                      # `broad` has no wildcard: only an exact twin
        return False
    if not b[0].startswith(a_prefix):    # anchored start must be covered by narrow's start
        return False
    if not b[-1].endswith(a_suffix):     # anchored end must be covered by narrow's end
        return False

    # Walk narrow's runs, consuming broad's middle literals in order.
    run_index, offset = 0, len(a_prefix)
    if len(b) == 1:
        # narrow is a bare literal; broad's prefix and suffix must not overlap in it
        if len(a_prefix) + len(a_suffix) > len(b[0]):
            return False
    limit = lambda i: len(b[i]) - (len(a_suffix) if i == len(b) - 1 else 0)
    for literal in a_middle:
        if not literal:
            continue
        while run_index < len(b):
            hit = b[run_index].find(literal, offset, max(offset, limit(run_index)))
            if hit != -1:
                offset = hit + len(literal)
                break
            run_index += 1
            offset = 0
        else:
            return False
    return True


def read_artifacts():
    """[(module, key, paths, uses_unique_files)] for every v2 artifact."""
    out = []
    for name in sorted(os.listdir(ARTIFACTS_DIR)):
        if not name.endswith('.py'):
            continue
        path = os.path.join(ARTIFACTS_DIR, name)
        try:
            with open(path, 'r', encoding='utf-8') as handle:
                source = handle.read()
            tree = ast.parse(source)
        except (OSError, SyntaxError) as ex:
            print(f'  WARNING  could not parse {name}: {ex}')
            continue
        protected = 'unique_files' in source
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            if not any(isinstance(t, ast.Name) and t.id == '__artifacts_v2__'
                       for t in node.targets):
                continue
            try:
                block = ast.literal_eval(node.value)
            except ValueError:
                continue
            if not isinstance(block, dict):
                continue
            for key, info in block.items():
                paths = (info or {}).get('paths')
                if isinstance(paths, str):
                    paths = (paths,)
                if paths and len(paths) > 1:
                    out.append((name, key, list(paths), protected))
    return out


def main():
    artifacts = read_artifacts()
    findings = []
    for module, key, paths, protected in artifacts:
        for broad, narrow in itertools.permutations(paths, 2):
            if subsumes(broad, narrow):
                findings.append((module, key, broad, narrow, protected))
                break

    new = [f for f in findings if (f[0], f[1]) not in ALLOWED]
    known = len(findings) - len(new)

    if new:
        print(f'Artifacts declaring a path pattern a sibling already covers ({len(new)} new):')
        for module, key, broad, narrow, protected in new:
            guard = 'unique_files present' if protected else 'NOT protected by unique_files'
            print(f'  {module}:{key}  ({guard})')
            print(f'      covered by  {broad}')
            print(f'      redundant   {narrow}')
        print()
        print(STANDARD_NOTE)
        return 1

    print(f'Checked {len(artifacts)} artifact(s) declaring more than one path pattern: '
          f'no new subsumed patterns. {known} known case(s) allowlisted.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
