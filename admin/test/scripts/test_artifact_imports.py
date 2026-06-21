# pylint: disable=broad-exception-caught
"""Smoke test: every artifact module must import on the current platform.

This is primarily run on Windows in CI to catch OS-specific import/path
breakage that the ubuntu-only lint job cannot. On Windows, extracted file
paths use backslash separators (see scripts/search_files.py), so artifacts
that mishandle separators at import time would fail here.

It validates *importability*, not parsing correctness (which needs sample
data). Modules are loaded by file path -- mirroring scripts/plugin_loader.py
-- so files with dots in their name (e.g. kleinanzeigen.de.py) load correctly.
"""
import importlib.util
import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

ARTIFACTS_DIR = REPO_ROOT / 'scripts' / 'artifacts'


class TestArtifactImports(unittest.TestCase):

    def test_all_artifact_modules_import(self):
        """Import every scripts/artifacts/*.py and fail on any import error."""
        failures = []
        count = 0
        for py_file in sorted(ARTIFACTS_DIR.glob('*.py')):
            if py_file.name.startswith('__'):
                continue
            try:
                spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                count += 1
            except Exception as exc:
                failures.append(f'{py_file.name}: {type(exc).__name__}: {exc}')

        self.assertEqual(failures, [], f'{len(failures)} artifact import failure(s):\n' + '\n'.join(failures))
        self.assertGreater(count, 250, f'Only {count} artifact modules imported - did the search path change?')

    def test_plugin_loader_loads(self):
        """The real PluginLoader must load a healthy number of plugins."""
        from scripts.plugin_loader import PluginLoader
        loader = PluginLoader()
        self.assertGreater(len(loader), 400, f'PluginLoader loaded only {len(loader)} plugins')


if __name__ == '__main__':
    unittest.main()
