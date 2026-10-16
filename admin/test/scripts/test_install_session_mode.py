"""Raw install-session mode is retained without changing existing session evidence."""
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.artifacts.installSessions import install_sessions  # pylint: disable=wrong-import-position
from scripts.ilapfuncs import convert_unix_ts_to_utc  # pylint: disable=wrong-import-position
from admin.test.scripts.test_appops_raw_sources import write_abx  # pylint: disable=wrong-import-position

MODES = [None, '', '0', '1', '2', '-1', 'unknown', '0002', ' 2 ', '<unknown&é>']


def fixture_xml():
    root = ET.Element('sessions')
    for mode in MODES:
        attributes = dict(createdMillis='1700000000123', updatedMillis='1700000001123',
                          committedMillis='1700000002123', appPackageName='package', appLabel='label',
                          installerPackageName='installer', installInitiatingPackageName='initiator',
                          updateOwnererPackageName='owner', updateOwnerPackageName='ignored-owner',
                          userId='10', originatingUid='11', installerUid='12', sessionId='13',
                          parentSessionId='14', sizeBytes='-1', sessionStageDir='/stage',
                          installRason='15', installReason='ignored-reason', installLocation='16',
                          packageSource='17', isApplied='false', isFailed='unknown', errorMessage='error')
        if mode is not None:
            attributes['mode'] = mode
        ET.SubElement(root, 'session', attributes)
    nested = ET.SubElement(root[-1], 'session', dict(mode='nested', sessionId='13'))
    ET.SubElement(nested, 'session', dict(mode='0', sessionId='13'))
    return ET.tostring(root, encoding='unicode')


def make_files(root):
    root = Path(root)
    first = root / 'plain/system/install_sessions.xml'
    first.parent.mkdir(parents=True, exist_ok=True)
    first.write_text(fixture_xml(), encoding='utf-8')
    second = write_abx(root / 'binary/system/install_sessions.xml', fixture_xml(), typed=True)
    third = root / 'multi/system/install_sessions.xml'
    third.parent.mkdir(parents=True, exist_ok=True)
    third.write_text('<?xml version="1.0"?><session mode="first"/><session mode="second"/>',
                     encoding='utf-8')
    return [first, second, third]


def parse(paths, root):
    return install_sessions.__wrapped__(SimpleNamespace(
        get_files_found=lambda: list(map(str, paths)),
        get_relative_path=lambda p: str(Path(p).relative_to(root))))


class InstallSessionModeTest(unittest.TestCase):
    def test_plain_mode_text_and_every_existing_cell(self):
        with tempfile.TemporaryDirectory() as root:
            paths = make_files(root)
            headers, rows, sources = parse(paths[:1], root)
            self.assertEqual(len(headers), 23)
            self.assertEqual(headers[:3], (('Created', 'datetime'), ('Updated', 'datetime'),
                                          ('Committed', 'datetime')))
            self.assertEqual(headers[11:15], ('Session ID', 'Parent Session ID',
                                            'Mode (as stored)', 'Size Bytes'))
            self.assertEqual([r[13] for r in rows], [m or '' for m in MODES] + ['nested', '0'])
            expected = tuple(convert_unix_ts_to_utc(n) for n in
                             [1700000000123, 1700000001123, 1700000002123]) + (
                'package', 'label', 'installer', 'initiator', 'owner', '10', '11', '12', '13',
                '14', '-1', '/stage', '15', '16', '17', 'false', 'unknown', 'error',
                'plain/system/install_sessions.xml')
            for row in rows[:len(MODES)]:
                self.assertEqual(row[:13] + row[14:], expected)
            self.assertEqual(sources, str(paths[0]))

    def test_actual_typed_abx_and_plain_roots_agree(self):
        with tempfile.TemporaryDirectory() as root:
            paths = make_files(root)
            _, plain, _ = parse(paths[:1], root)
            _, binary, _ = parse(paths[1:2], root)
            self.assertTrue(paths[1].read_bytes().startswith(b'ABX\0'))
            self.assertEqual([r[:-1] for r in binary], [r[:-1] for r in plain])
            self.assertTrue(all(isinstance(r[13], str) for r in binary))

    def test_input_preorder_multiple_roots_duplicates_and_source_selection(self):
        with tempfile.TemporaryDirectory() as root:
            paths = make_files(root)
            irrelevant = Path(root) / 'other.xml'
            irrelevant.write_text('<session mode="ignored"/>', encoding='utf-8')
            headers, rows, sources = parse([irrelevant, Path(root)] + paths, root)
            expected = [m or '' for m in MODES] + ['nested', '0']
            self.assertEqual([r[13] for r in rows], expected + expected + ['first', 'second'])
            self.assertEqual(sources.splitlines(), list(map(str, paths)))
            self.assertEqual(headers[-1], 'Source File')
            self.assertEqual([r[11] for r in rows[:len(expected)]], ['13'] * len(expected))
