"""Android bug report text: the ShortcutInfo entries of the shortcut service dump."""
import io
import os
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from scripts import dumpstate_reader as reader
from scripts import dumpstate_shortcuts as shortcuts
from scripts.artifacts import bugreportShortcuts as artifacts


class Context:
    def __init__(self, root, files):
        self.root = Path(root)
        self.files = list(map(str, files))

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root)).replace(os.sep, '/')


def entry(shortcut_id='s1', flags='6289', letters='DynIc-fIc-aStrLiv', package='com.example.chat', short='Chat one',
          long_label='null', categories='{android.shortcut.conversation}', persons='[android.app.Person@1a2b3c]',
          rank=0, stamp=1794785387000, intents='[Intent { act=android.intent.action.VIEW }/null]', extras='null',
          splash=None, locus=None, depth=10):
    """One ShortcutInfo entry laid out as ShortcutInfo.toDumpString prints it (fields two spaces deeper)."""
    pad = ' ' * depth
    inner = pad + '  '
    lines = ['%sShortcutInfo {id=%s, flags=0x%s [%s]' % (pad, shortcut_id, flags, letters),
             '%spackageName=%s' % (inner, package),
             '%sactivity=ComponentInfo{%s/%s.Main}' % (inner, package, package),
             '%sshortLabel=%s, resId=0[null]' % (inner, short),
             '%slongLabel=%s, resId=0[null]' % (inner, long_label),
             '%sdisabledMessage=null, resId=0[null]' % inner,
             '%sdisabledReason=[Not disabled]' % inner]
    if splash:
        lines.append('%sSplashScreenThemeResName=%s' % (inner, splash))
    lines += ['%scategories=%s' % (inner, categories),
              '%spersons=%s' % (inner, persons),
              '%sicon=null' % inner,
              '%srank=%d, timestamp=%d' % (inner, rank, stamp),
              '%sintents=%s' % (inner, intents),
              '%sextras=%s' % (inner, extras),
              '%siconRes=0[null], bitmapPath=null, iconUri=null%s}' % (inner, locus or '')]
    return '\n'.join(lines)


def package_block(package, entries):
    return ('      Package: %s  UID: 10200\n        Calls: 0\n        Last known FG: 0\n'
            '        Last reset: [1794826040169] 2026-11-16 05:47:20\n\n        Shortcuts:\n%s\n'
            '        Total bitmap size: 0 (0 B)\n' % (package, '\n'.join(entries)))


def service_text(body, cut=False):
    end = "*** SERVICE 'shortcut' DUMP TIMEOUT (10000ms) EXPIRED ***\n" if cut else \
        '--------- 0.2s was the duration of dumpsys shortcut, ending at: 2026-11-16 16:55:12\n'
    return ('== dumpstate: 2026-11-16 16:55:07\n\n------ DUMPSYS (/system/bin/dumpsys) ------\n'
            'DUMP OF SERVICE shortcut:\nService host process PID: 1234\nNow: [1794851192008] 2026-11-16 16:55:07\n\n'
            '%s\n%s' % (body, end))


def user_block(user, packages):
    return ('  User: %d  Known locales: en-US  Last app scan: [1794851192008] 2026-11-16 12:46:32\n'
            '      Last app scan FP: vendor/device:16/build:user/release-keys\n%s' % (user, ''.join(packages)))


def scan_text(text):
    report = reader.Report(reader.Source('memory', ''))
    reader.scan_lines(reader.iter_lines(io.BytesIO(text.encode('utf-8'))), report)
    report.finish()
    return report


class ReaderTests(unittest.TestCase):
    def only(self, report):
        found = shortcuts.rows_of(report)
        self.assertEqual(len(found), 1, found)
        return found[0]

    def test_registration_in_the_shared_reader(self):
        self.assertIn(shortcuts.ShortcutReader, reader.readers_by_section()[('service', 'shortcut')])
        self.assertEqual(reader.READ_BY[('service', 'shortcut')], 'Shortcuts')

    def test_fields_of_one_entry(self):
        report = scan_text(service_text(user_block(0, [package_block('com.example.chat', [entry()])])))
        row = self.only(report)
        self.assertEqual(row.user, 0)
        self.assertEqual(row.package, 'com.example.chat')
        self.assertEqual(row.shortcut_id, 's1')
        self.assertEqual(row.short_label, 'Chat one')
        self.assertEqual(row.long_label, '')
        self.assertEqual(row.flags_hex, '6289')
        self.assertEqual(row.flag_letters, 'DynIc-fIc-aStrLiv')
        self.assertEqual(row.kinds, 'dynamic, long lived, cached for notifications')
        self.assertEqual(row.unknown_letters, '')
        self.assertEqual(row.activity, 'com.example.chat/com.example.chat.Main')
        self.assertEqual(row.categories, '{android.shortcut.conversation}')
        self.assertEqual(row.person_count, 1)
        self.assertEqual(row.rank, 0)
        self.assertEqual(row.timestamp_text, '1794785387000')
        self.assertEqual(row.intents, '[Intent { act=android.intent.action.VIEW }/null]')
        self.assertEqual(row.extras, '')
        self.assertEqual(row.disabled_reason, 'Not disabled')

    def test_ids_and_labels_that_hold_the_separators(self):
        text = entry(shortcut_id='a, flags=b', short='Name, resId=x')
        report = scan_text(service_text(user_block(0, [package_block('com.example.chat', [text])])))
        row = self.only(report)
        self.assertEqual(row.shortcut_id, 'a, flags=b')
        self.assertEqual(row.short_label, 'Name, resId=x')

    def test_a_label_with_a_line_break_continues_the_field(self):
        text = entry(short='First line\nsecond line')
        report = scan_text(service_text(user_block(0, [package_block('com.example.chat', [text])])))
        row = self.only(report)
        self.assertEqual(row.short_label, 'First line second line')
        self.assertEqual(row.package, 'com.example.chat')

    def test_optional_fields_and_locus_id(self):
        text = entry(splash='com.example:style/Splash', locus='locusId=LocusId[12_chars]')
        report = scan_text(service_text(user_block(0, [package_block('com.example.chat', [text])])))
        row = self.only(report)
        self.assertEqual(row.extras, '')
        self.assertEqual(row.timestamp_text, '1794785387000')

    def test_person_counts(self):
        self.assertIsNone(shortcuts.person_count('null'))
        self.assertEqual(shortcuts.person_count('[]'), 0)
        self.assertEqual(shortcuts.person_count('[android.app.Person@1, android.app.Person@2]'), 2)
        self.assertIsNone(shortcuts.person_count('[something else]'))

    def test_kind_is_decoded_from_the_bits_and_the_launcher_letter(self):
        self.assertEqual(shortcuts.kind_text(0x1a4, ['Im', 'Man', 'Ic-r', 'Str']), 'manifest, immutable')
        self.assertEqual(shortcuts.kind_text(0x6080, ['Str', 'Liv']), 'long lived, cached for notifications')
        self.assertEqual(shortcuts.kind_text((1 << 30) | (1 << 29) | 0x2, []),
                         'pinned, cached for bubbles, cached for people tile')
        self.assertEqual(shortcuts.kind_text(0x41, ['Dis', 'Dyn', 'Hid-L']), 'dynamic, disabled, excluded from launcher')
        self.assertEqual(shortcuts.kind_text(None, []), '')

    def test_letters_are_split_and_unknown_ones_kept(self):
        self.assertEqual(shortcuts.split_letters('DynIc-fIc-aStrLiv'), (['Dyn', 'Ic-f', 'Ic-a', 'Str', 'Liv'], ''))
        self.assertEqual(shortcuts.split_letters('DynZzz'), (['Dyn'], 'Zzz'))

    def test_users_packages_and_the_parts_after_the_entries(self):
        body = (user_block(0, [package_block('com.example.chat', [entry('a'), entry('b')]),
                               package_block('com.example.mail', [entry('c', package='com.example.mail')])])
                + user_block(10, [package_block('com.example.chat', [entry('d')])])
                + '** SHORTCUT MANAGER UID STATES (dumpsys shortcut -n -u)\n    UID=1001 state=0  last FG=1\n'
                + '** SHORTCUT MANAGER FILES (dumpsys shortcut -n -f)\n' + entry('not-an-entry'))
        report = scan_text(service_text(body))
        found = [(row.user, row.package, row.shortcut_id) for row in shortcuts.rows_of(report)]
        self.assertEqual(found, [(0, 'com.example.chat', 'a'), (0, 'com.example.chat', 'b'),
                                 (0, 'com.example.mail', 'c'), (10, 'com.example.chat', 'd')])

    def test_an_entry_cut_by_the_end_of_the_section_is_kept(self):
        text = '\n'.join(entry().split('\n')[:8])
        report = scan_text(service_text(user_block(0, [package_block('com.example.chat', [text])]), cut=True))
        row = self.only(report)
        self.assertEqual(row.short_label, 'Chat one')
        self.assertEqual(row.timestamp_text, '')


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        reader.clear_cache()
        self.work = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.work)
        self.addCleanup(reader.clear_cache)

    def write(self, name, text):
        path = Path(self.work) / name
        path.write_text(text, encoding='utf-8')
        return path

    def run_artifact(self, *paths):
        return artifacts.bugreport_shortcuts.__wrapped__(Context(self.work, paths))

    def test_rows_and_time(self):
        path = self.write('bugreport-test-2026-11-16-16-55-07.txt', service_text(
            user_block(0, [package_block('com.example.chat', [entry(), entry('s2', stamp=0)])])))
        headers, found, source = self.run_artifact(path)
        self.assertEqual(len(headers), len(found[0]))
        self.assertEqual(found[0][0], datetime(2026, 11, 15, 23, 29, 47, tzinfo=timezone.utc))
        self.assertEqual(found[0][15], '0x6289 [DynIc-fIc-aStrLiv]')
        self.assertIsNone(found[1][0])
        self.assertEqual(found[1][1], '0')
        self.assertEqual(source, str(path))

    def test_a_report_without_the_service_says_so(self):
        path = self.write('bugreport-none-2026-11-16-16-55-07.txt',
                          '== dumpstate: 2026-11-16 16:55:07\n\n------ DUMPSYS (/system/bin/dumpsys) ------\n')
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append):
            _headers, found, _source = self.run_artifact(path)
        self.assertEqual(found, [])
        self.assertTrue(any('no shortcut service dump' in message for message in messages), messages)

    def test_a_cut_dump_is_logged(self):
        path = self.write('bugreport-cut-2026-11-16-16-55-07.txt', service_text(
            user_block(0, [package_block('com.example.chat', [entry()])]), cut=True))
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append):
            _headers, found, _source = self.run_artifact(path)
        self.assertEqual(len(found), 1)
        self.assertTrue(any('timeout' in message for message in messages), messages)


if __name__ == '__main__':
    unittest.main()
