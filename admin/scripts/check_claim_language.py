"""Fail CI when an artifact's examiner-facing text claims more than the data shows.

Every artifact module declares an `__artifacts_v2__` dict. The `name` and
`description` fields in that dict are examiner-facing: they are written into the HTML
report and into the LAVA manifest, they are what an examiner reads when deciding what
an artifact is, and they get quoted verbatim in casework and in court. A description
that says a table holds "all searches the user typed" is a statement about a person's
conduct. The parser only knows that rows exist in a table.

The project standard is: never state what data means in the real world unless the data
proves it or a cited source documents it. Describe the record, the table it came from,
and the columns emitted. Leave the inference to the examiner.

A large audit (PR #1015) fixed 553 findings across 320 files. This check exists so the
class does not creep back in one pull request at a time. It parses each artifact
module with `ast`, reads the `__artifacts_v2__` literal, and matches the `name` and
`description` of every entry against a vocabulary of words that tend to carry an
unsupported claim -- completeness ("all", "every", "entire"), attribution to a person
("the user searched", "typed by"), and certainty ("proves", "always", "reliable").

The vocabulary is deliberately blunt. It flags wording that is *usually* a claim, not
wording that is *always* one, so a match is a prompt to look rather than a verdict.

Handling a match
----------------
* **Actual problem** -- reword to what the data shows. "All records from the X table"
  becomes "Records recovered from the X table"; "Frequently visited sites" becomes
  "Parses the frequents table". Name the table and the columns; do not assert what a
  person did. Bump the entry's `last_update_date` while you are there.
* **Legitimate exception** -- add a `(filename, artifact_key, field)` tuple to
  ALLOWLIST with an inline comment saying why the wording is supportable. A vendor's
  own feature name, or text that names a UI path, is not the parser making a claim.
  The allowlist is a deliberate act and every entry is reviewed; it is not a place to
  silence a finding you have not thought about.

Usage:
    python admin/scripts/check_claim_language.py           # fail on unallowlisted claims
    python admin/scripts/check_claim_language.py --list    # show every match, allowlisted too
    python admin/scripts/check_claim_language.py --verbose # also report skipped modules
"""

import argparse
import ast
import os
import re
import sys

# The claim vocabulary. Each alternative is a word or phrase that, in an examiner-facing
# field, usually asserts something the parsed data does not establish:
#
#   completeness  all / every / complete / full list / entire
#   attribution   the user <verb> / user-created / typed by / searched by / manually
#   certainty     proves / definitively / always / reliable
#   inference     visited / habits
#
# Matching is case-insensitive and word-boundary aware -- `\ball\b` must not fire on
# "call log", which is why the boundaries are explicit rather than relying on a trailing
# space. Prefixes without a closing boundary (`\bcomplete`, `\breliable`, `\bhabit`) are
# intentional so inflections such as "completed", "reliably" and "habits" are caught.
CLAIM_PATTERN = re.compile(
    r"\ball\b|\bevery\b|\bcomplete|\bfull list\b|\bentire\b|"
    r"\bthe user (searched|typed|viewed|visited|opened|selected|deleted|read|sent|"
    r"created|hid|chose)\b|"
    r"\buser[- ](created|entered|typed|searched|selected|initiated)\b|"
    r"\bsearched by\b|\btyped by\b|\bviewed by\b|\bread by\b|\bmanually\b|"
    r"\bproves?\b|\bdefinitively\b|\balways\b|\breliable|\bvisited\b|\bhabits?\b",
    re.IGNORECASE,
)

# Fields that reach the examiner through the report and the LAVA manifest.
CHECKED_FIELDS = ('name', 'description')

# Reviewed exceptions, as (filename, artifact_key, field). Each needs a reason.
ALLOWLIST = {
    # "completed" names columns the artifact emits (completed time) and the Google Tasks
    # status value, not a claim that the task list is complete.
    ('googleTasks.py', 'get_googleTasks', 'description'),
    # "completedtransfers" is the literal name of the MEGA table being read. The
    # description no longer asserts the transfers themselves completed.
    ('mega_transfers.py', 'get_mega_transfers', 'description'),
}


def find_artifacts_dict(tree):
    """Return the AST node assigned to __artifacts_v2__, or None."""
    node = None
    for statement in tree.body:
        if not isinstance(statement, ast.Assign):
            continue
        for target in statement.targets:
            if isinstance(target, ast.Name) and target.id == '__artifacts_v2__':
                node = statement.value
    return node


def load_artifacts(path):
    """Return (artifacts_dict, skip_reason). Exactly one of the two is None."""
    try:
        with open(path, 'r', encoding='utf-8') as handle:
            tree = ast.parse(handle.read())
    except (OSError, SyntaxError) as exc:
        return None, f'could not parse: {exc}'

    node = find_artifacts_dict(tree)
    if node is None:
        return None, 'no __artifacts_v2__ assignment'

    # Some modules build the dict with a helper call so the literal is not available
    # statically. Those are skipped rather than guessed at.
    try:
        data = ast.literal_eval(node)
    except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
        return None, '__artifacts_v2__ is not a static literal'

    if not isinstance(data, dict):
        return None, '__artifacts_v2__ is not a dict'
    return data, None


def scan_file(path):
    """Return (matches, skip_reason) for one artifact module."""
    data, skip_reason = load_artifacts(path)
    if skip_reason is not None:
        return [], skip_reason

    filename = os.path.basename(path)
    matches = []
    for artifact_key, entry in data.items():
        if not isinstance(entry, dict):
            continue
        for field in CHECKED_FIELDS:
            value = entry.get(field)
            if not isinstance(value, str):
                continue
            found = sorted({match.group(0).lower() for match in CLAIM_PATTERN.finditer(value)})
            if found:
                allowlisted = (filename, str(artifact_key), field) in ALLOWLIST
                matches.append({
                    'filename': filename,
                    'artifact_key': str(artifact_key),
                    'field': field,
                    'text': value,
                    'terms': found,
                    'allowlisted': allowlisted,
                })
    return matches, None


def artifact_paths(repo_root):
    artifacts_dir = os.path.join(repo_root, 'scripts', 'artifacts')
    return sorted(
        os.path.join(artifacts_dir, name)
        for name in os.listdir(artifacts_dir)
        if name.endswith('.py') and name != '__init__.py'
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--list', action='store_true', dest='list_all',
                        help='print every match including allowlisted ones, then exit 0')
    parser.add_argument('--verbose', action='store_true',
                        help='also report modules that were skipped')
    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    all_matches = []
    skipped = []
    for path in artifact_paths(repo_root):
        matches, skip_reason = scan_file(path)
        if skip_reason is not None:
            skipped.append((os.path.basename(path), skip_reason))
            continue
        all_matches.extend(matches)

    if args.verbose and skipped:
        print(f'Skipped {len(skipped)} module(s):')
        for name, reason in skipped:
            print(f'  {name}: {reason}')
        print()

    if args.list_all:
        for match in sorted(all_matches, key=lambda m: (m['filename'], m['artifact_key'])):
            marker = 'ALLOWLISTED' if match['allowlisted'] else 'FLAGGED    '
            terms = ', '.join(match['terms'])
            print(f"{marker} scripts/artifacts/{match['filename']}:"
                  f"{match['artifact_key']}:{match['field']}: [{terms}] {match['text']}")
        allowed = sum(1 for m in all_matches if m['allowlisted'])
        print(f'\n{len(all_matches)} match(es): {allowed} allowlisted, '
              f'{len(all_matches) - allowed} flagged.')
        return 0

    violations = [match for match in all_matches if not match['allowlisted']]
    if not violations:
        return 0

    print('Unsupported-claim language in examiner-facing artifact fields:\n')
    for match in sorted(violations, key=lambda m: (m['filename'], m['artifact_key'])):
        terms = ', '.join(match['terms'])
        print(f"scripts/artifacts/{match['filename']}:{match['artifact_key']}:{match['field']}: "
              f"{match['text']}")
        print(f"    flagged term(s): {terms}")
    print(
        f'\n{len(violations)} finding(s). The name and description of an artifact are '
        'examiner-facing:\nthey reach the HTML report and the LAVA manifest and get quoted '
        'in casework. Do not\nstate what data means in the real world unless the data proves '
        'it or a cited source\ndocuments it -- describe the records, the table they came from '
        'and the columns emitted.\n\nReword the text, or, if the wording is genuinely '
        'supportable, add a (filename,\nartifact_key, field) tuple to ALLOWLIST in '
        f'{os.path.relpath(__file__, repo_root)} with a comment\nsaying why.'
    )
    return 1


if __name__ == '__main__':
    sys.exit(main())
