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
           'bugreportRadios', 'bugreportAccountsPower', 'bugreportSensorsMedia')
PREFIX = 'Android Bug Report - '
GROUPS = collections.OrderedDict([
    ('Device and Build', 2), ('Installed Apps', 2), ('Permissions and App Ops', 6), ('Processes and Memory', 6),
    ('App Usage', 4), ('Network', 14), ('Wi-Fi', 6), ('Bluetooth, NFC and USB', 10), ('Telephony', 7),
    ('Battery and Power', 12), ('Location and Sensors', 10), ('Camera and Media', 7),
    ('Accounts, Sync and Backup', 16), ('Notifications', 3), ('Display and Input', 9), ('Alarms and Jobs', 3),
    ('Settings and Config', 2), ('Boot, Crash and Dropbox', 1)])
PATHS = ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
         '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip')


def all_artifacts():
    for module in MODULES:
        info = importlib.import_module('scripts.artifacts.' + module).__artifacts_v2__
        for key, value in info.items():
            yield module, key, value


class CategoryTests(unittest.TestCase):
    def test_every_artifact_is_in_one_of_the_groups(self):
        counts = collections.Counter()
        for module, key, value in all_artifacts():
            category = value['category']
            self.assertTrue(category.startswith(PREFIX), (module, key, category))
            counts[category[len(PREFIX):]] += 1
        self.assertEqual(dict(counts), dict(GROUPS))
        self.assertEqual(sum(counts.values()), 120)

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
        known = {value['name'][len('Bug Report - '):] for _module, _key, value in all_artifacts()}
        for key, text in reader.READ_BY.items():
            for name in text.split('; '):
                self.assertIn(name, known, (key, name))

    def test_topic_modules_import_in_any_order(self):
        topics = ('dumpstate_permissions', 'dumpstate_usagejobs', 'dumpstate_network', 'dumpstate_radios',
                  'dumpstate_accountspower', 'dumpstate_sensorsmedia')
        expected = '%d %d' % (len(reader.READERS), len(reader.READ_BY))
        for topic in topics:
            code = ('import scripts.%s; from scripts import dumpstate_reader as r; '
                    'print(len(r.READERS), len(r.READ_BY))' % topic)
            result = subprocess.run([sys.executable, '-c', code], cwd=REPO_ROOT, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, (topic, result.stderr[-500:]))
            self.assertEqual(result.stdout.strip(), expected, topic)



if __name__ == '__main__':
    unittest.main()
