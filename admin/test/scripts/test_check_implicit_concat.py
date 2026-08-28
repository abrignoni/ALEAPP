"""Prove the implicit-concatenation checker detects run-together junctions only.

check_implicit_concat.py fails when two adjacent string literals join with an
alphanumeric character on both sides of the junction, because the joined value
renders run-together words in examiner-facing prose.

The negative cases are the point: deliberate joins with a space at the junction,
strings that are separate statements, and strings that are separate items in a
collection must all stay silent, or the check gets switched off.
"""
import importlib.util
import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
_MODULE_PATH = REPO_ROOT / 'admin' / 'scripts' / 'check_implicit_concat.py'

# admin/scripts is not a package, so load the module from its path.
_spec = importlib.util.spec_from_file_location('check_implicit_concat', _MODULE_PATH)
cic = importlib.util.module_from_spec(_spec)
sys.modules['check_implicit_concat'] = cic
_spec.loader.exec_module(cic)


class RunTogether(unittest.TestCase):
    def test_flags_alnum_junction(self):
        found = cic.scan_source(
            'x = ("Logs information about the app status"\n'
            '     "such as launch, open, close, install.")\n')
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0][1][-6:], 'status')
        self.assertEqual(found[0][2][:7], 'such as')

    def test_flags_metadata_dict_value(self):
        found = cic.scan_source(
            '__artifacts_v2__ = {\n'
            '    "demo": {\n'
            '        "description": "Parses checkin events including user and beer info"\n'
            '                       "as well as location information",\n'
            '    }\n'
            '}\n')
        self.assertEqual(len(found), 1)


class StaysSilent(unittest.TestCase):
    def test_ignores_space_at_junction(self):
        self.assertEqual(cic.scan_source(
            'q = ("select a "\n     "from b")\n'), [])
        self.assertEqual(cic.scan_source(
            'q = ("select a"\n     " from b")\n'), [])

    def test_ignores_separate_statements(self):
        # A docstring followed by a string statement is two statements,
        # never a concatenation.
        self.assertEqual(cic.scan_source(
            '"""Module docstring"""\n"another string"\n'), [])

    def test_ignores_collection_items(self):
        self.assertEqual(cic.scan_source(
            'paths = ("a/b", "c/d")\n'), [])

    def test_ignores_punctuation_junction(self):
        self.assertEqual(cic.scan_source(
            'x = ("first sentence."\n     " second sentence")\n'), [])

    def test_ignores_fstrings(self):
        self.assertEqual(cic.scan_source(
            'x = f"{a}" f"{b}"\n'), [])


if __name__ == '__main__':
    unittest.main()
