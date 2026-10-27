#!/usr/bin/env python3
"""Install ALEAPP's requirements with the mister_skinnylegs chain taken from requirements-msl-lock.txt.

mister_skinnylegs names its ccl readers as unversioned git URLs, so a plain
``pip install -r requirements.txt`` installs whatever their default branches hold that day, and
fails for everyone the day one of them pushes a broken commit. The commits pinned in the lock still
declare Brotli<=1.2.0, so letting pip resolve them would also bring back Brotli 1.2.0, which the
1.2.1 decoder fix replaces.

So this installs requirements.txt without its mister_skinnylegs line, then the lock with --no-deps
(as packaging/build.py does over a regular install), then refuses a Brotli older than MIN_BROTLI.
Any arguments are passed to both pip installs, for example
``--only-binary=:all: --no-binary=mister-skinnylegs,ccl-chromium-reader,ccl-mozilla-reader,ccl-simplesnappy``.
pip check reports the Brotli<=1.2.0 metadata of the pinned readers as a conflict; that is the cap
this script overrides, so pip check is not run.

Usage: python admin/scripts/install_requirements.py [pip options]
"""
import importlib.metadata
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REQUIREMENTS = os.path.join(ROOT, 'requirements.txt')
MSL_LOCK = os.path.join(ROOT, 'requirements-msl-lock.txt')
MIN_BROTLI = (1, 2, 1)


def without_mister_skinnylegs(text):
    """requirements.txt with the mister_skinnylegs line left out; fails if there is no such line."""
    kept = [line for line in text.splitlines() if not re.match(r'\s*mister[-_]skinnylegs\b', line, re.I)]
    if len(kept) == len(text.splitlines()):
        raise SystemExit('requirements.txt names no mister_skinnylegs line; nothing for the lock to replace')
    return '\n'.join(kept) + '\n'


def version_tuple(text):
    return tuple(int(part) for part in re.findall(r'\d+', text)[:3])


def check_brotli(version):
    """Exit unless the installed Brotli is at least MIN_BROTLI."""
    if version_tuple(version) < MIN_BROTLI:
        raise SystemExit(f'Brotli {version} is installed; {".".join(map(str, MIN_BROTLI))} or later is required')


def main(pip_options):
    pip = [sys.executable, '-m', 'pip', 'install'] + pip_options
    with open(REQUIREMENTS, encoding='utf-8') as handle:
        text = without_mister_skinnylegs(handle.read())
    # The file stays in the repository root so the relative whl_files/ paths in it resolve.
    with tempfile.NamedTemporaryFile('w', suffix='.txt', dir=ROOT, delete=False, encoding='utf-8') as handle:
        handle.write(text)
        trimmed = handle.name
    try:
        subprocess.run(pip + ['-r', trimmed], cwd=ROOT, check=True)
    finally:
        os.remove(trimmed)
    subprocess.run(pip + ['--no-deps', '-r', MSL_LOCK], cwd=ROOT, check=True)
    version = importlib.metadata.version('Brotli')
    check_brotli(version)
    print(f'Installed with {os.path.basename(MSL_LOCK)}; Brotli {version}')


if __name__ == '__main__':
    main(sys.argv[1:])
