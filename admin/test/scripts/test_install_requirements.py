"""Checks admin/scripts/install_requirements.py: it drops only the mister_skinnylegs line, and refuses an old Brotli."""
import os
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO_ROOT, 'admin', 'scripts'))

import install_requirements as install  # noqa: E402  pylint: disable=wrong-import-position,import-error


class InstallRequirementsTests(unittest.TestCase):
    def test_only_the_mister_skinnylegs_line_is_left_out(self):
        with open(install.REQUIREMENTS, encoding='utf-8') as handle:
            text = handle.read()
        trimmed = install.without_mister_skinnylegs(text)
        dropped = set(text.splitlines()) - set(trimmed.splitlines())
        self.assertEqual(len(dropped), 1)
        self.assertTrue(dropped.pop().startswith('mister_skinnylegs @ git+'))

    def test_the_lock_pins_what_was_left_out(self):
        with open(install.MSL_LOCK, encoding='utf-8') as handle:
            lock = handle.read()
        self.assertRegex(lock, r'(?m)^mister_skinnylegs @ git\+\S+@[0-9a-f]{40}$')
        self.assertRegex(lock, r'(?m)^Brotli==1\.2\.[1-9]')

    def test_requirements_without_the_line_are_refused(self):
        with self.assertRaises(SystemExit):
            install.without_mister_skinnylegs('bcrypt==5.0.0\nfolium==0.14.0\n')

    def test_lock_sets_the_readers_and_brotli_and_fills_in_the_rest(self):
        with open(install.MSL_LOCK, encoding='utf-8') as handle:
            lock = handle.read()
        already = {'zstd': '1.5.7.2', 'Brotli': '1.2.0', 'lz4': '4.3.3'}
        lines = install.lock_lines(lock, already.get)
        names = [line.split()[0].split('==')[0] for line in lines]
        self.assertIn('Brotli', names)                        # always, even over an installed 1.2.0
        self.assertNotIn('zstd', names)                       # kept as installed
        self.assertNotIn('lz4', names)
        self.assertTrue(all(name in names for name in ('mister_skinnylegs', 'ccl_chromium_reader',
                                                       'ccl_mozilla_reader', 'ccl_simplesnappy')))
        fresh = [line.split()[0].split('==')[0] for line in install.lock_lines(lock, lambda name: None)]
        self.assertIn('zstd', fresh)                          # nothing installed: the whole lock
        self.assertIn('lz4', fresh)

    def test_brotli_older_than_1_2_1_is_refused(self):
        for version in ('1.2.0', '1.1.0', '1.0.9'):
            with self.assertRaises(SystemExit):
                install.check_brotli(version)
        for version in ('1.2.1', '1.2.10', '1.3.0', '2.0'):
            install.check_brotli(version)


if __name__ == '__main__':
    unittest.main()
