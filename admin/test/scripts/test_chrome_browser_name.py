"""get_browser_name reads the package segment, not words elsewhere in the path."""
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts.chrome import get_browser_name  # pylint: disable=wrong-import-position

TAIL = 'data/data/{pkg}/{folder}/Default/History'


def path(root, pkg, folder='app_chrome'):
    return f'{root}/{TAIL.format(pkg=pkg, folder=folder)}'


class BrowserName(unittest.TestCase):
    def test_browsers_by_package(self):
        root = '/cases/case1/report/data'
        self.assertEqual(get_browser_name(path(root, 'com.android.chrome')), 'Chrome')
        self.assertEqual(get_browser_name(path(root, 'com.brave.browser')), 'Brave')
        self.assertEqual(get_browser_name(path(root, 'com.microsoft.emmx')), 'Edge')
        self.assertEqual(get_browser_name(path(root, 'com.opera.browser', 'app_opera')), 'Opera')
        self.assertEqual(get_browser_name(path(root, 'org.cromite.cromite')), 'org.cromite.cromite')

    def test_a_case_folder_name_is_not_read_as_the_browser(self):
        for root in ('/Users/x/Microsoft Fraud 2026/out/data', '/Users/x/Brave Street/out/data',
                     r'C:\Users\x\OneDrive - Microsoft\Opera case\out\data'):
            self.assertEqual(get_browser_name(path(root, 'com.android.chrome')), 'Chrome', root)

    def test_a_webview_is_named_by_its_app(self):
        root = '/cases/case1/report/data'
        self.assertEqual(get_browser_name(path(root, 'com.microsoft.teams', 'app_webview')),
                         'com.microsoft.teams')
        self.assertEqual(get_browser_name(path(root, 'com.example.app', 'app_webview')),
                         'com.example.app')

    def test_a_file_named_app_something_is_not_a_folder(self):
        self.assertEqual(get_browser_name('/r/data/data/com.example.app/databases/app_usage'),
                         'Unknown')


if __name__ == '__main__':
    unittest.main()
