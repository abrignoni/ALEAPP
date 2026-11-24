"""Checks that hold across all the Android bug report modules together (categories, names, registration, import order)."""
import collections
import importlib
import os
import subprocess
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, REPO_ROOT)

from scripts import dumpstate_reader as reader  # noqa: E402  pylint: disable=wrong-import-position

MODULES = ('bugreportDevice', 'bugreportActivity', 'bugreportPermissions', 'bugreportUsageJobs', 'bugreportNetwork',
           'bugreportRadios', 'bugreportAccountsPower', 'bugreportSensorsMedia', 'bugreportSecurityStorage',
           'bugreportLogsCrash', 'bugreportShortcuts')
CATEGORY = 'Android Bug Report'
PATHS = ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
         '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip')


def all_artifacts():
    for module in MODULES:
        info = importlib.import_module('scripts.artifacts.' + module).__artifacts_v2__
        for key, value in info.items():
            yield module, key, value


class CategoryTests(unittest.TestCase):
    def test_every_artifact_is_in_the_bug_report_category(self):
        count = 0
        for module, key, value in all_artifacts():
            self.assertEqual(value['category'], CATEGORY, (module, key))
            count += 1
        self.assertEqual(count, 160)

    def test_names_and_paths_are_the_same_kind_everywhere(self):
        names = collections.Counter()
        for module, key, value in all_artifacts():
            names[value['name']] += 1
            self.assertTrue(value['name'].startswith('Bug Report - '), (module, key))
            self.assertEqual(value['paths'], PATHS, (module, key))
        self.assertEqual([name for name, count in names.items() if count > 1], [])


class RegistrationTests(unittest.TestCase):
    def test_every_reader_is_registered_once(self):
        self.assertEqual(len(reader.READERS), len(set(reader.READERS)))

    def test_section_index_names_every_reading_artifact(self):
        self.assertEqual(reader.READ_BY[('service', 'package')],
                         'Installed Packages; Package Times; Package Permissions; Permission Definitions')
        self.assertEqual(reader.READ_BY[('service', 'usagestats')],
                         'Usage Events; Usage Intervals; Usage Interval Event Counts; Standby Buckets')
        self.assertEqual(reader.READ_BY[('service', 'knoxguard_service')], 'knoxguard_service Log')
        self.assertEqual(reader.READ_BY[('service', 'knoxcustom')], 'knoxcustom State')
        known = {value['name'][len('Bug Report - '):] for _module, _key, value in all_artifacts()}
        for key, text in reader.READ_BY.items():
            for name in text.split('; '):
                self.assertIn(name, known, (key, name))

    def test_topic_modules_import_in_any_order(self):
        topics = ('dumpstate_permissions', 'dumpstate_usagejobs', 'dumpstate_network', 'dumpstate_radios',
                  'dumpstate_accountspower', 'dumpstate_sensorsmedia', 'dumpstate_securitystorage',
                  'dumpstate_logscrash', 'dumpstate_shortcuts')
        expected = '%d %d' % (len(reader.READERS), len(reader.READ_BY))
        for topic in topics:
            code = ('import scripts.%s; from scripts import dumpstate_reader as r; '
                    'print(len(r.READERS), len(r.READ_BY))' % topic)
            result = subprocess.run([sys.executable, '-c', code], cwd=REPO_ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, (topic, result.stderr[-500:]))
            self.assertEqual(result.stdout.strip(), expected, topic)



if __name__ == '__main__':
    unittest.main()
