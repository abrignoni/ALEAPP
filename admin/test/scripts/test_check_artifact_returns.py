"""Prove the return-shape checker still detects the defect it exists to detect.

check_artifact_returns.py fails when an @artifact_processor function returns None
on any branch, because the wrapper unpacks three values unconditionally and the
"no records" branch is the normal state of a fresh install.

The negative cases matter as much as the positive ones. A nested helper returning
None is an ordinary early exit (dropbox.py carries one), and a checker that flags
it gets switched off.
"""
import importlib.util
import pathlib
import sys
import tempfile
import textwrap
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
_MODULE_PATH = REPO_ROOT / 'admin' / 'scripts' / 'check_artifact_returns.py'

# admin/scripts is not a package, so load the module from its path.
_spec = importlib.util.spec_from_file_location('check_artifact_returns', _MODULE_PATH)
car = importlib.util.module_from_spec(_spec)
sys.modules['check_artifact_returns'] = car
_spec.loader.exec_module(car)


def findings_for(source):
    with tempfile.TemporaryDirectory() as folder:
        path = pathlib.Path(folder) / 'sample.py'
        path.write_text(textwrap.dedent(source), encoding='utf-8')
        violations, problem = car.scan_module(str(path))
    if problem:
        raise AssertionError(problem)
    return violations


class ReturnsNone(unittest.TestCase):
    def test_flags_return_none(self):
        found = findings_for('''
            @artifact_processor
            def demo(context):
                if not data_list:
                    return None
                return data_headers, data_list, source_path
        ''')
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0][3], 'return None')

    def test_flags_bare_return(self):
        found = findings_for('''
            @artifact_processor
            def demo(context):
                if not data_list:
                    return
                return data_headers, data_list, source_path
        ''')
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0][3], 'return')


class StaysSilent(unittest.TestCase):
    def test_ignores_nested_helper_returning_none(self):
        # dropbox.py's shape: an inner accumulator with an early exit.
        found = findings_for('''
            @artifact_processor
            def demo(context):
                def _record(prop, value):
                    if not value:
                        return
                    matched[prop] = value
                return data_headers, data_list, source_path
        ''')
        self.assertEqual(found, [])

    def test_ignores_undecorated_function(self):
        found = findings_for('''
            def helper(x):
                if not x:
                    return None
                return x
        ''')
        self.assertEqual(found, [])

    def test_ignores_complete_triples(self):
        found = findings_for('''
            @artifact_processor
            def demo(context):
                if not data_list:
                    return data_headers, [], source_path
                return data_headers, data_list, source_path
        ''')
        self.assertEqual(found, [])


if __name__ == '__main__':
    unittest.main()
