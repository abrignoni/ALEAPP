"""Pin the Enabled Accessibility Services artifact (scripts/artifacts/enabledAccessibilityServices.py).

The setting attributes follow those an Android 15 emulator wrote; the component
names are made up.
"""
import os
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

# pylint: disable=wrong-import-position
from scripts.artifacts import enabledAccessibilityServices as ea
# pylint: enable=wrong-import-position

XML = '''<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<settings version="-1">
  <setting id="1" name="enabled_accessibility_services" value="com.x.a/com.x.a.Svc::com.y.b/.Other" package="com.android.shell" />
  <setting id="2" name="accessibility_enabled" value="1" package="android" defaultValue="1" defaultSysSet="true" />
  <setting id="3" name="android_id" value="abc" package="android" />
</settings>
'''


class Artifact(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)

    def write(self, rel, text):
        path = os.path.join(self.folder.name, *rel.split('/'))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as handle:
            handle.write(text)
        return path

    def run_artifact(self, found):
        context = mock.Mock()
        context.get_files_found.return_value = found
        return ea.enabledAccessibilityServices.__wrapped__(context)

    def test_rows(self):
        path = self.write('data/system/users/10/settings_secure.xml', XML)
        headers, rows, located = self.run_artifact([path])
        self.assertEqual(len(headers), 6)
        self.assertEqual(rows, [('10', 'com.x.a/com.x.a.Svc', 'com.x.a', '1', 'com.android.shell', 'android'),
                                ('10', 'com.y.b/.Other', 'com.y.b', '1', 'com.android.shell', 'android')])
        self.assertEqual(located, path)

    def test_absent_setting_and_skipped_folders(self):
        none = self.write('data/system/users/0/settings_secure.xml',
                          '<settings><setting id="1" name="android_id" value="a" package="android" /></settings>')
        mirror = self.write('data/system/mirror/users/0/settings_secure.xml', XML)
        notuser = self.write('data/system/users/abc/settings_secure.xml', XML)
        with mock.patch('scripts.artifacts.settingsSecure.logfunc'):
            _h, rows, located = self.run_artifact([none, mirror, notuser])
        self.assertEqual(rows, [])
        self.assertEqual(located, none)


    def test_value_base64(self):
        path = self.write('data/system/users/0/settings_secure.xml',
                          '<settings><setting id="1" name="enabled_accessibility_services" '
                          'valueBase64="Y29tLnovLlM=" package="com.android.settings" /></settings>')
        _h, rows, _l = self.run_artifact([path])
        self.assertEqual(rows, [('0', 'com.z/.S', 'com.z', '', 'com.android.settings', '')])


if __name__ == '__main__':
    unittest.main()
