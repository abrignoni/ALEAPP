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

Two ways the check can quietly stop doing its job
-------------------------------------------------
Both are reported rather than hidden, because a check that has silently narrowed its
own scope is worse than no check: it still prints a pass.

* **A stale ALLOWLIST entry** -- one that no longer matches anything. It means the
  description was reworded or the artifact key was renamed, so the entry now shields
  nothing at all, except the next claim that happens to land under that same key. That
  is how an allowlist quietly becomes a dumping ground: entries accumulate, nobody
  rereads them, and each one is a pre-approval for text nobody has seen. Stale entries
  fail the run and must be deleted.

* **A module whose `__artifacts_v2__` is not a static literal** -- its fields cannot be
  read without importing the module, so they are never checked. These are printed as
  NOT CHECKED on every run, not just under `--verbose`, and counted in the summary, so
  the coverage hole stays in front of whoever reads the output.

  As of this writing that is exactly two modules, both structural rather than
  accidental:
    - `scripts/artifacts/artGlobals.py` -- shared globals, declares no
      `__artifacts_v2__` dict at all.
    - `scripts/artifacts/fitbit.py` -- builds its dict through an `_art()` helper, so
      there is no literal for `ast.literal_eval` to read.
  If that list ever drifts from reality, the runtime output is the authority, not this
  docstring.

Usage:
    python admin/scripts/check_claim_language.py           # fail on unallowlisted claims
    python admin/scripts/check_claim_language.py --list    # show every match, allowlisted too
    python admin/scripts/check_claim_language.py --verbose # add coverage and allowlist counts
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
# space. Prefixes without a closing boundary (`\bcomplete`, `\breliable`) are intentional
# so inflections such as "completed" and "reliably" are caught. `\bhabits?\b` is closed on
# purpose: the open stem `\bhabit` used by the sibling iLEAPP implementation also matches
# "habitat", and the closed spelling already covers both inflections that occur in prose.
CLAIM_PATTERN = re.compile(
    r"\ball\b|\bevery\b|\bcomplete|\bfull list\b|\bentire\b|"
    r"\bthe user (?:searched|typed|viewed|visited|opened|selected|deleted|read|sent|"
    r"created|hid|chose)\b|"
    r"\buser[- ](?:created|entered|typed|searched|selected|initiated)\b|"
    r"\b(?:searched|typed|viewed|read|entered|created|sent|opened|selected|deleted|v"
    r"isited|chosen|hidden|initiated) by (?:the |a |an )?(?:user|account holder|device owner|subject|owner)\b|\bmanually\b|"
    r"\bproves?\b|\bdefinitively\b|\balways\b|\breliable|\bvisited\b|\bhabits?\b",
    re.IGNORECASE,
)

# `notes` reaches the examiner too, in the report and in the artifact info modal, so the
# same standard applies to it. It cannot use the same vocabulary, because notes do a job
# name and description do not: they state what was tested. "empty on all 18 copies
# tested" and "NULL for every account tested" are the coverage discipline this project
# asks for, not claims about a person, and the completeness words would fire on every one
# of them. Measured on 2026-08-29: the full vocabulary flags 368 of the 1,477 artifacts
# carrying notes across the five cores, dominated by `every` (190) and `all` (72), almost
# all of them describing a test set.
#
# `read by` comes out for the same reason. In notes it means read by the code, not by a
# person: "columns are read by position", "not read by this artifact". Nineteen hits in
# ALEAPP, all benign.
#
# What is left is attribution and certainty, which mean the same thing in a note as in a
# description, and flag 52 artifacts across the five cores.
NOTES_PATTERN = re.compile(
    r"\bthe user (?:searched|typed|viewed|visited|opened|selected|deleted|read|sent|"
    r"created|hid|chose)\b|"
    r"\buser[- ](?:created|entered|typed|searched|selected|initiated)\b|"
    r"\b(?:searched|typed|viewed|read|entered|created|sent|opened|selected|deleted|v"
    r"isited|chosen|hidden|initiated) by (?:the |a |an )?(?:user|account holder|device owner|subject|owner)\b|\bmanually\b|"
    r"\bproves?\b|\bdefinitively\b|\balways\b|\breliable|\bvisited\b|\bhabits?\b",
    re.IGNORECASE,
)

# A note that *denies* a claim uses the same words as one that makes it: "not terms the
# user searched for", "does not establish that the user viewed them", "rather than
# anything the user chose". That denial is the wording this project asks for, so matching
# it and demanding an allowlist entry would tax the correct behaviour and grow the
# allowlist without bound. A match in `notes` preceded by a negation inside the same
# clause is therefore not reported.
#
# The window is deliberately short. A negation two sentences back says nothing about this
# clause, and a long window would swallow real claims. Suppressed matches are counted and
# printed by --list, because a check that narrows its own scope silently is worse than no
# check: the count appears under --verbose whether it is zero or not.
NEGATION_WINDOW = 60
NEGATION_PATTERN = re.compile(
    r"\b(not|no|never|nor|neither|without|cannot|rather than|instead of|"
    r"isn't|doesn't|don't|does not|do not)\b",
    re.IGNORECASE,
)


def negated(text, start):
    """True when a negation appears close enough before `start` to govern it."""
    window = text[max(0, start - NEGATION_WINDOW):start]
    # A sentence boundary ends the clause, so a negation before it does not govern.
    window = window.rsplit('. ', 1)[-1]
    return bool(NEGATION_PATTERN.search(window))


# Fields that reach the examiner through the report and the LAVA manifest, and the
# vocabulary each is matched against.
CHECKED_FIELDS = {
    'name': CLAIM_PATTERN,
    'description': CLAIM_PATTERN,
    'notes': NOTES_PATTERN,
}

# Reviewed exceptions, as (filename, artifact_key, field, term). Each needs a
# reason. The term is part of the key, so an entry silences the one word it was
# granted for and never the next claim added to the same text.
ALLOWLIST = {
    # "habit" and "habits" are Loop Habit Tracker's own product name and the literal name
    # of the Habits table these artifacts read. The app exists to record habits the person
    # defined in it, so naming them is describing the records, not inferring behaviour from
    # unrelated data. The notes state what each column holds and say the check-in records
    # the day a habit was marked, not the time of day the person marked it.
    ('loopHabits.py', 'loop_habits', 'name', 'habit'),
    ('loopHabits.py', 'loop_habits', 'name', 'habits'),
    ('loopHabits.py', 'loop_habits', 'description', 'habit'),
    ('loopHabits.py', 'loop_habits', 'description', 'habits'),
    ('loopHabits.py', 'loop_habits', 'notes', 'habit'),
    ('loopHabits.py', 'loop_habits', 'notes', 'habits'),
    ('loopHabits.py', 'loop_habits_checkins', 'name', 'habit'),
    ('loopHabits.py', 'loop_habits_checkins', 'description', 'habit'),
    ('loopHabits.py', 'loop_habits_checkins', 'notes', 'habit'),
    # "completed" names columns the artifact emits (completed time) and the Google Tasks
    # status value, not a claim that the task list is complete.
    ('googleTasks.py', 'get_googleTasks', 'description', 'complete'),
    # "completedtransfers" is the literal name of the MEGA table being read. The
    # description no longer asserts the transfers themselves completed.
    ('mega_transfers.py', 'get_mega_transfers', 'description', 'complete'),
    # "a page visited and then navigated away from ... can be absent here" is the gap the
    # note is warning about. The sentence states what the artifact misses, not what it proves.
    ('OperaBrowser.py', 'opera_tab_navigation', 'notes', 'visited'),
    # "manually" sits inside the app's own category label, quoted: 272 ('Activity Tracking
    # started manually'). It is Withings' string, not this parser's claim.
    ('WithingsHealthMate.py', 'healthmate_trackings', 'notes', 'manually'),
    # "listing them beside an account reads as things the user chose when the container does
    # not establish that" is the reason the titles are deliberately not enumerated. The
    # denial follows the phrase instead of preceding it, so the negation lookback cannot see it.
    ('disneyPlus.py', 'disneyplus_cached_content', 'notes', 'the user chose'),
}


def unallowlisted(filename, artifact_key, field, terms):
    """The terms no ALLOWLIST entry covers for this field.

    An entry is keyed on the term it was granted for, so allowlisting one word does
    not pre-approve the next claim somebody adds to the same text.
    """
    return [term for term in terms
            if (filename, str(artifact_key), field, term) not in ALLOWLIST]


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
    """Return (matches, skip_reason, negated_count) for one artifact module."""
    data, skip_reason = load_artifacts(path)
    if skip_reason is not None:
        return [], skip_reason, 0

    filename = os.path.basename(path)
    matches = []
    negated_counts = []
    for artifact_key, entry in data.items():
        if not isinstance(entry, dict):
            continue
        for field, pattern in CHECKED_FIELDS.items():
            value = entry.get(field)
            if not isinstance(value, str):
                continue
            hits = list(pattern.finditer(value))
            suppressed = 0
            if field == 'notes':
                kept = [hit for hit in hits if not negated(value, hit.start())]
                suppressed = len(hits) - len(kept)
                hits = kept
            found = sorted({hit.group(0).lower() for hit in hits})
            if suppressed:
                negated_counts.append(suppressed)
            if found:
                remaining = unallowlisted(filename, artifact_key, field, found)
                allowlisted = not remaining
                matches.append({
                    'filename': filename,
                    'artifact_key': str(artifact_key),
                    'field': field,
                    'text': value,
                    'terms': remaining or found,
                    'all_terms': found,
                    'allowlisted': allowlisted,
                })
    return matches, None, sum(negated_counts)


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
                        help='also report coverage and allowlist counts')
    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    all_matches = []
    skipped = []
    # Every (filename, artifact_key, field) the pattern actually fired on this run,
    # allowlisted or not. An ALLOWLIST entry missing from this set matches nothing.
    fired = set()
    checked = 0
    negated_total = 0
    for path in artifact_paths(repo_root):
        matches, skip_reason, negated_here = scan_file(path)
        negated_total += negated_here
        if skip_reason is not None:
            skipped.append((os.path.basename(path), skip_reason))
            continue
        checked += 1
        for match in matches:
            for term in match['all_terms']:
                fired.add((match['filename'], match['artifact_key'],
                           match['field'], term))
        all_matches.extend(matches)

    stale = sorted(ALLOWLIST - fired)

    # A module whose __artifacts_v2__ cannot be evaluated statically is a real coverage
    # hole -- its examiner-facing fields are never read. Print it on every run.
    if skipped:
        print(f'NOT CHECKED -- {len(skipped)} module(s) have no statically readable '
              f'__artifacts_v2__:')
        for name, reason in skipped:
            print(f'  scripts/artifacts/{name}: {reason}')
        print()

    if args.verbose:
        print(f'Scanned {checked + len(skipped)} module(s); {checked} checked, '
              f'{len(skipped)} not checked.')
        allowed_count = sum(1 for match in all_matches if match['allowlisted'])
        print(f'Allowlist holds {len(ALLOWLIST)} entr(ies); {allowed_count} fired this run.')
        print(f'{negated_total} match(es) in notes were preceded by a negation and not reported.')
        print()

    # A stale entry shields nothing except the next claim that lands under that key.
    if stale:
        print(f'Stale ALLOWLIST entr(ies) ({len(stale)}) -- these no longer match anything '
              f'and should be deleted:')
        for entry in stale:
            print(f'  {entry[0]}:{entry[1]}:{entry[2]}  [{entry[3]}]')
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
        if stale:
            print('Remove the stale entr(ies) above from ALLOWLIST in '
                  f'{os.path.relpath(__file__, repo_root)}.')
            return 1
        allowed_count = sum(1 for match in all_matches if match['allowlisted'])
        summary = (f'Checked {checked} artifact module(s): no unsupported claim language '
                   f'({allowed_count} reviewed exception(s) allowlisted).')
        if skipped:
            summary += f' {len(skipped)} module(s) NOT checked, listed above.'
        print(summary)
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
