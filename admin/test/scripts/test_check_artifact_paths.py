"""Prove the package-anchor audit in check_artifact_paths.py detects what it
exists to detect, and stays silent on what it must not flag.

A pattern with no package id in its non-final segments can match the same-named
file inside a different app's container. The audit fails such a pattern unless
path_anchor_allowlist.json records why it needs no anchor. The negative cases
are pinned too: an anchored pattern, an allowlisted pattern, and a dotted FILE
name (which is not a container anchor) must not trip it, or the check gets
switched off.
"""
import importlib.util
import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
_MODULE_PATH = REPO_ROOT / 'admin' / 'scripts' / 'check_artifact_paths.py'

# admin/scripts is not a package, so load the module from its path.
_spec = importlib.util.spec_from_file_location('check_artifact_paths', _MODULE_PATH)
cap = importlib.util.module_from_spec(_spec)
sys.modules['check_artifact_paths'] = cap
_spec.loader.exec_module(cap)


class IsAnchored(unittest.TestCase):
    def test_package_segment_anchors(self):
        self.assertTrue(cap.is_anchored(
            '*/com.untappdllc.app/shared_prefs/io.invertase.firebase.xml'))

    def test_wildcarded_package_segment_anchors(self):
        self.assertTrue(cap.is_anchored(
            '*/com.sec.android.app.sbrowser*/databases/SBrowser.db*'))

    def test_marker_directory_does_not_anchor(self):
        self.assertFalse(cap.is_anchored('*/app_opera/session_db*'))

    def test_dotted_file_name_does_not_anchor(self):
        # The dots are in the FINAL segment: a file name, not a container.
        self.assertFalse(cap.is_anchored(
            '*/shared_prefs/com.facebook.katana_preferences.xml'))

    def test_shared_storage_does_not_anchor(self):
        self.assertFalse(cap.is_anchored('*/system/build.prop'))


class AnchorFindings(unittest.TestCase):
    ARTIFACTS = [
        ('demo.py', 'demo_ok', ['*/com.vendor.app/databases/store.db*'], False),
        ('demo.py', 'demo_bad', ['*/cache/http-cache/*.1'], False),
        ('demo.py', 'demo_listed', ['*/app_opera/session_db*'], False),
    ]

    def test_flags_unanchored_without_entry(self):
        findings, _stale = cap.anchor_findings(
            self.ARTIFACTS, {'*/app_opera/session_db*': 'distinctive marker'})
        self.assertEqual(findings,
                         [('demo.py', 'demo_bad', '*/cache/http-cache/*.1')])

    def test_allowlisted_pattern_passes(self):
        findings, _stale = cap.anchor_findings(
            self.ARTIFACTS, {'*/app_opera/session_db*': 'distinctive marker',
                             '*/cache/http-cache/*.1': 'reason on record'})
        self.assertEqual(findings, [])

    def test_stale_entry_is_reported_not_fatal(self):
        _findings, stale = cap.anchor_findings(
            self.ARTIFACTS, {'*/app_opera/session_db*': 'distinctive marker',
                             '*/gone/pattern*': 'module was removed'})
        self.assertEqual(stale, ['*/gone/pattern*'])


class SeededAllowlist(unittest.TestCase):
    def test_repo_tree_is_clean_against_the_seed(self):
        import json
        with open(cap.ANCHOR_ALLOWLIST_PATH, encoding='utf-8') as handle:
            allowlist = json.load(handle)
        findings, _stale = cap.anchor_findings(cap.read_artifacts(), allowlist)
        self.assertEqual(findings, [])

    def test_every_seed_entry_carries_a_reason(self):
        import json
        with open(cap.ANCHOR_ALLOWLIST_PATH, encoding='utf-8') as handle:
            allowlist = json.load(handle)
        for pattern, reason in allowlist.items():
            self.assertTrue(reason and isinstance(reason, str), pattern)


if __name__ == '__main__':
    unittest.main()
