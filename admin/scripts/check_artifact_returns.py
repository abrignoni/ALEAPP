"""Guard artifact functions against returning None instead of the result triple.

An artifact returns `(data_headers, data_list, source_path)`. The wrapper unpacks
that unconditionally:

    data_headers, data_list, source_path = func(Context)

so a function that ends a branch with `return` or `return None` does not report
"nothing found". It raises

    TypeError: cannot unpack non-iterable NoneType object

and the artifact fails on every device where the app is installed but that branch
runs, which for a "no records" branch is the normal state of a fresh install. The
crash is easy to miss in development because the extraction used to build the
module has records by construction.

The shape to write instead keeps the headers and the source path and hands back an
empty list:

    return data_headers, [], source_path

Only returns belonging to the decorated function itself are checked. A nested
helper may return None freely; that is an ordinary early exit, not a result
triple.

Usage:
  check_artifact_returns.py [--root REPO_ROOT]

Exits 1 when anything is found, 0 otherwise.
"""

import argparse
import ast
import os
import sys

DECORATORS = {'artifact_processor', 'artifact_processor_streaming'}

STANDARD_NOTE = (
    "Return the triple on every branch: 'return data_headers, [], source_path' "
    "when nothing was found. The wrapper unpacks three values unconditionally."
)


def decorator_names(node):
    names = []
    for dec in node.decorator_list:
        if isinstance(dec, ast.Name):
            names.append(dec.id)
        elif isinstance(dec, ast.Attribute):
            names.append(dec.attr)
        elif isinstance(dec, ast.Call):
            func = dec.func
            names.append(func.id if isinstance(func, ast.Name)
                         else getattr(func, 'attr', ''))
    return names


def own_returns(func):
    """Return nodes belonging to func itself, not to functions nested inside it."""
    found = []

    def walk(node):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                continue
            if isinstance(child, ast.Return):
                found.append(child)
            walk(child)

    walk(func)
    return found


def scan_function(func):
    """(line, spelling) for every return that hands the wrapper None."""
    found = []
    for ret in own_returns(func):
        if ret.value is None:
            found.append((ret.lineno, 'return'))
        elif isinstance(ret.value, ast.Constant) and ret.value.value is None:
            found.append((ret.lineno, 'return None'))
    return found


def scan_module(path):
    module = os.path.basename(path)
    try:
        with open(path, encoding='utf-8', errors='replace') as handle:
            tree = ast.parse(handle.read())
    except SyntaxError as err:
        return [], f'{module}: could not parse ({err})'
    violations = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not DECORATORS.intersection(decorator_names(node)):
            continue
        for line, spelling in scan_function(node):
            violations.append((module, node.name, line, spelling))
    return violations, None


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
        print(f'Artifact functions returning None ({len(violations)}):')
        for module, func, line, spelling in violations:
            print(f'  {module}:{line}  {func}()  {spelling}')
        print()
        print(STANDARD_NOTE)
        return 1

    summary = (f'Checked {modules} artifact module(s): '
               'no artifact function returns None.')
    if unreadable:
        summary += f' {len(unreadable)} module(s) NOT checked.'
    print(summary)
    for problem in unreadable:
        print(f'  {problem}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
