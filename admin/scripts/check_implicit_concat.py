"""Guard against adjacent string literals whose junction runs two words together.

Python joins adjacent string literals silently, so a wrapped metadata string that
forgets the separating space is valid code with broken prose:

    "description": "Logs information about the app status"
                   "such as launch, open, close, install.",

renders as "app statussuch as launch" in the report and the LAVA manifest, where
an examiner reads it. Nothing else catches this: the module imports, lint passes,
and the value is a perfectly ordinary string.

Only junctions where an alphanumeric character meets an alphanumeric character
with no whitespace on either side are reported. A junction that ends or begins
with a space, a newline, or punctuation is a deliberate join and stays silent, so
a SQL query wrapped as `'select a '  'from b'` is untouched. A long opaque token
deliberately split across literals would trip this; none exists in the tree
today, so there is no allowlist until one is needed.

Junctions are found with the tokenizer, not a regex, and only literals that are
part of one expression are paired: a logical newline between two strings means
two statements, not a concatenation.

Usage:
  check_implicit_concat.py [--root REPO_ROOT]

Exits 1 when anything is found, 0 otherwise.
"""

import argparse
import ast
import io
import os
import sys
import tokenize

STANDARD_NOTE = (
    'End the first literal with a space (or start the second with one) so the '
    'joined string reads as written.'
)


def scan_source(source):
    """(line, left tail, right head) for every run-together junction."""
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except tokenize.TokenError:
        return []
    found = []
    prev = None
    for tok in tokens:
        if tok.type == tokenize.NEWLINE:
            # A logical newline ends the expression; strings across it are
            # separate statements, never an implicit concatenation.
            prev = None
            continue
        if tok.type in (tokenize.NL, tokenize.COMMENT,
                        tokenize.INDENT, tokenize.DEDENT):
            continue
        if tok.type == tokenize.STRING and prev is not None \
                and prev.type == tokenize.STRING:
            try:
                left = ast.literal_eval(prev.string)
                right = ast.literal_eval(tok.string)
            except (ValueError, SyntaxError):
                left = right = None  # f-string or bytes; not checked
            if isinstance(left, str) and isinstance(right, str) \
                    and left and right \
                    and left[-1].isalnum() and right[0].isalnum():
                found.append((tok.start[0], left[-20:], right[:20]))
        prev = tok
    return found


def scan_module(path):
    module = os.path.basename(path)
    try:
        with open(path, encoding='utf-8', errors='replace') as handle:
            source = handle.read()
    except OSError as err:
        return [], f'{module}: could not read ({err})'
    return [(module, line, left, right)
            for line, left, right in scan_source(source)], None


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', default=None, help='repository root')
    args = parser.parse_args()

    root = args.root or os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    artifacts = os.path.join(root, 'scripts', 'artifacts')
    if not os.path.isdir(artifacts):
        print(f'No scripts/artifacts under {root}', file=sys.stderr)
        return 2

    violations, unreadable, modules = [], [], 0
    for name in sorted(os.listdir(artifacts)):
        if not name.endswith('.py'):
            continue
        modules += 1
        found, problem = scan_module(os.path.join(artifacts, name))
        violations.extend(found)
        if problem:
            unreadable.append(problem)

    if violations:
        print(f'Run-together implicit string concatenations ({len(violations)}):')
        for module, line, left, right in violations:
            print(f'  {module}:{line}  ...{left!r} + {right!r}...')
        print()
        print(STANDARD_NOTE)
        return 1

    summary = (f'Checked {modules} artifact module(s): '
               'no run-together implicit concatenation.')
    if unreadable:
        summary += f' {len(unreadable)} module(s) NOT checked.'
    print(summary)
    for problem in unreadable:
        print(f'  {problem}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
