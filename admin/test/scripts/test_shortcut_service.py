"""Shortcut Service regression tests using synthetic XML and payloads."""

import ast
import hashlib
import io
import json
import sqlite3
import struct
import sys
import tempfile
import types
import unittest
import xml.etree.ElementTree as ET
from contextlib import ExitStack, contextmanager, redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from scripts.artifacts import shortcut_service
from scripts.context import Context
from scripts import ilapfuncs, lavafuncs
from scripts.search_files import FileInfo


@contextmanager
def isolated_output():
    context_state = {name: value for name, value in vars(Context).items()
                     if name.startswith('_') and not name.startswith('__')
                     and not isinstance(value, staticmethod)}
    with ExitStack() as stack:
        stack.enter_context(patch.multiple(Context, **context_state))
        stack.enter_context(patch.multiple(lavafuncs, lava_data=None, lava_db=None, lava_db_path=None))
        for name in ('screen_output_file_path', 'screen_output_file_path_devinfo'):
            stack.enter_context(patch.object(ilapfuncs.OutputParameters, name, '', create=True))
        stack.enter_context(patch.multiple(ilapfuncs.GuiWindow, window_handle=None, message_queue=None))
        writer = ilapfuncs.ScreenLogWriter()
        stack.enter_context(patch.object(ilapfuncs, '_screen_log', writer))
        stack.enter_context(patch.multiple(ilapfuncs, icons={}, html_tables_held_back=[]))
        stack.enter_context(redirect_stdout(io.StringIO()))
        try:
            Context.clear()
            Context.set_output_params(None)
            yield
        finally:
            if lavafuncs.lava_db is not None:
                lavafuncs.lava_db.close()
            writer.close()


class ShortcutServiceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        stack = ExitStack()
        self.addCleanup(stack.close)
        stack.enter_context(isolated_output())
        Context.set_data_folder(str(self.root))
        self.files = []

    def write(self, name, content, user='0'):
        path = self.root / 'data' / 'system_ce' / user / 'shortcut_service' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, ET.Element):
            ET.ElementTree(content).write(path, encoding='utf-8', xml_declaration=True)
        else:
            path.write_bytes(content)
        self.files.append(str(path))
        Context.set_files_found(self.files)
        return path

    def rows(self, name):
        headers, rows, _ = getattr(shortcut_service, name).__wrapped__(Context)
        names = [header[0] if isinstance(header, tuple) else header for header in headers]
        self.assertTrue(all(len(row) == len(headers) for row in rows))
        return [dict(zip(names, row)) for row in rows]

    def package(self, name='com.example.app', identifier='shortcut-1'):
        package = ET.Element('package', name=name)
        shortcut = ET.SubElement(package, 'shortcut', {
            'id': identifier, 'timestamp': '1700000000123', 'title': 'MiXeD Label',
        })
        return package, shortcut

    def discord(self, pairs, num=None):
        package, shortcut = self.package('com.discord')
        extras = ET.SubElement(ET.SubElement(shortcut, 'intent'), 'extras')
        array = ET.SubElement(extras, 'string-array', {
            'name': 'discord_shortcut_data', 'num': str(num if num is not None else len(pairs) * 2),
        })
        for key, value in pairs:
            ET.SubElement(array, 'item', value=key)
            ET.SubElement(array, 'item', value=value)
        return package, array

    def test_metadata_is_static_and_all_functions_are_registered(self):
        tree = ast.parse(Path(shortcut_service.__file__).read_text(encoding='utf-8'))
        metadata = next(node.value for node in tree.body if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name) and target.id == '__artifacts_v2__'
                                for target in node.targets))
        artifacts = ast.literal_eval(metadata)
        self.assertEqual(set(artifacts), {'get_shortcut_service', 'get_shortcut_service_discord', 'get_shortcut_service_files'})
        for name, info in artifacts.items():
            self.assertTrue(hasattr(getattr(shortcut_service, name), '__wrapped__'))
            self.assertIn('lava', info['output_types'])
            self.assertTrue(all('/shortcut_service/' in pattern for pattern in info['paths']))

    def test_legacy_document_keeps_packages_separate(self):
        root = ET.Element('user')
        for name in ('com.example.one', 'com.example.two'):
            package, _ = self.package(name, 'shared-id')
            root.append(package)
        self.write('shortcuts.xml', root)
        rows = self.rows('get_shortcut_service')
        self.assertEqual([row['Package'] for row in rows], ['com.example.one', 'com.example.two'])
        self.assertEqual(len({row['XML Path'] for row in rows}), 2)

    def test_user_profiles_with_same_shortcut_are_not_merged(self):
        for user in ('0', '10'):
            package, _ = self.package()
            self.write('packages/com.example.app.xml', package, user=user)
        rows = self.rows('get_shortcut_service')
        self.assertEqual([row['Android User'] for row in rows], ['0', '10'])

    def test_repeated_input_path_is_read_once(self):
        package, _ = self.package()
        path = self.write('packages/com.example.app.xml', package)
        Context.set_files_found([str(path), str(path)])
        self.assertEqual(len(self.rows('get_shortcut_service')), 1)

    def test_backup_versions_remain_separate(self):
        for extension, label in (('.xml', 'NewLabel'), ('.xml.bak', 'OldLabel')):
            package, shortcut = self.package()
            shortcut.set('title', label)
            self.write('packages/com.example.app' + extension, package)
        self.assertEqual({row['Short Label'] for row in self.rows('get_shortcut_service')},
                         {'NewLabel', 'OldLabel'})

    def test_empty_abx_is_not_reported_as_corruption(self):
        self.write('packages/com.example.app.xml', bytes.fromhex('414258001011'))
        rows = self.rows('get_shortcut_service_files')
        self.assertEqual(rows[0]['Parse Status'], 'Empty ABX document')
        self.assertEqual(rows[0]['Shortcut Count'], 0)
        self.assertEqual(self.rows('get_shortcut_service'), [])

    def test_bad_file_does_not_hide_valid_file(self):
        self.write('packages/com.example.bad.xml', b'<package>')
        package, _ = self.package()
        self.write('packages/com.example.app.xml', package)
        self.assertEqual(len(self.rows('get_shortcut_service')), 1)
        self.assertEqual({row['Parse Status'] for row in self.rows('get_shortcut_service_files')},
                         {'Parse error', 'Parsed'})

    def test_invalid_abx_is_inventoried(self):
        self.write('packages/com.example.app.xml', b'ABX\x00\x12')
        row = self.rows('get_shortcut_service_files')[0]
        self.assertEqual(row['File Format'], 'ABX')
        self.assertEqual(row['Parse Status'], 'Parse error')

    def test_io_errors_do_not_publish_absolute_local_paths(self):
        package, _ = self.package()
        path = self.write('packages/com.example.app.xml', package)
        error = PermissionError(13, 'Synthetic denial', str(path))
        with patch.object(shortcut_service.ET, 'parse', side_effect=error):
            row = self.rows('get_shortcut_service_files')[0]
        self.assertEqual(row['Parse Status'], 'Parse error')
        self.assertNotIn(str(self.root), row['Error'])
        self.assertIn(row['Source File'], row['Error'])

    def test_empty_package_and_source_hash_are_retained(self):
        path = self.write('packages/com.example.app.xml', ET.Element('package', name='com.example.app'))
        row = self.rows('get_shortcut_service_files')[0]
        self.assertEqual(row['Package Count'], 1)
        self.assertEqual(row['Shortcut Count'], 0)
        self.assertEqual(row['SHA-256'], hashlib.sha256(path.read_bytes()).hexdigest())

    def test_timestamp_unit_precision_and_source_path(self):
        package, _ = self.package()
        self.write('packages/com.example.app.xml', package)
        row = self.rows('get_shortcut_service')[0]
        self.assertEqual(row['Shortcut Updated (UTC)'],
                         datetime(2023, 11, 14, 22, 13, 20, 123000, tzinfo=timezone.utc))
        self.assertEqual(row['Shortcut Timestamp (ms, as stored)'], '1700000000123')
        self.assertFalse(Path(row['Source File']).is_absolute())
        self.assertEqual(row['Short Label'], 'MiXeD Label')



    def test_discord_keeps_extra_and_author_identities_separate(self):
        message = json.dumps({'id': 'message-json', 'channel_id': 'channel-json',
                              'content': 'JSON content', 'timestamp': '2023-10-01T12:00:00.123+02:00',
                              'author': {'id': 'author-json', 'username': 'StoredAuthor', 'global_name': 'DisplayName'}})
        package, _ = self.discord([('user_username', 'StoredExtra'), ('user_id', 'user-extra'),
                                   ('message_id', 'message-extra'), ('message_content', 'Extra content'),
                                   ('message', message)])
        self.write('packages/com.discord.xml', package)
        row = self.rows('get_shortcut_service_discord')[0]
        self.assertEqual(row['Username (extra)'], 'StoredExtra')
        self.assertEqual(row['Author Username (JSON)'], 'StoredAuthor')
        self.assertEqual(row['User ID (extra)'], 'user-extra')
        self.assertEqual(row['Author ID (JSON)'], 'author-json')
        self.assertEqual(row['Message ID (extra)'], 'message-extra')
        self.assertEqual(row['Message ID (JSON)'], 'message-json')
        self.assertEqual(row['Message Content (extra)'], 'Extra content')
        self.assertEqual(row['Message Content (JSON)'], 'JSON content')
        self.assertEqual(row['Message Time (UTC)'], datetime(2023, 10, 1, 10, 0, 0, 123000, tzinfo=timezone.utc))
        self.assertEqual(row['Message JSON (as stored)'], message)

    def test_non_discord_array_is_not_treated_as_discord(self):
        package, _ = self.discord([('user_username', 'StoredExtra')])
        package.set('name', 'com.example.app')
        self.write('packages/com.example.app.xml', package)
        self.assertEqual(self.rows('get_shortcut_service_discord'), [])

    def test_multiple_discord_payloads_are_not_merged(self):
        package, shortcut = self.package('com.discord')
        for identifier in ('first-message', 'second-message'):
            extras = ET.SubElement(ET.SubElement(shortcut, 'intent'), 'extras')
            ET.SubElement(extras, 'string', name='message_id').text = identifier
        self.write('packages/com.discord.xml', package)
        rows = self.rows('get_shortcut_service_discord')
        self.assertEqual([row['Message ID (extra)'] for row in rows], ['first-message', 'second-message'])
        self.assertEqual(len({row['Payload XML Path'] for row in rows}), 2)

    def test_duplicate_discord_keys_and_odd_arrays_are_visible(self):
        package, array = self.discord([('user_username', 'FirstAlias'), ('user_username', 'SecondAlias')])
        ET.SubElement(array, 'item', value='TrailingItem')
        self.write('packages/com.discord.xml', package)
        row = self.rows('get_shortcut_service_discord')[0]
        self.assertEqual(row['Username (extra)'], 'FirstAlias')
        self.assertIn('Duplicate keys', row['Decode Status'])
        self.assertIn('Odd array length', row['Decode Status'])
        self.assertIn('SecondAlias', row['Payload Pairs (JSON)'])
        self.assertIn('TrailingItem', self.rows('get_shortcut_service')[0]['Intents (JSON)'])

    def test_malformed_message_json_keeps_other_values(self):
        package, _ = self.discord([('user_username', 'StoredExtra'), ('message', '{broken')])
        self.write('packages/com.discord.xml', package)
        row = self.rows('get_shortcut_service_discord')[0]
        self.assertEqual(row['Username (extra)'], 'StoredExtra')
        self.assertEqual(row['Message JSON (as stored)'], '{broken')
        self.assertIn('not a JSON object', row['Decode Status'])

    def test_missing_timezone_is_not_guessed(self):
        package, _ = self.discord([('message', '{"timestamp":"2023-10-01T12:00:00"}')])
        self.write('packages/com.discord.xml', package)
        row = self.rows('get_shortcut_service_discord')[0]
        self.assertEqual(row['Message Time (UTC)'], '')
        self.assertEqual(row['Message Time (as stored)'], '2023-10-01T12:00:00')

    def test_sources_are_not_modified(self):
        package, _ = self.package()
        path = self.write('packages/com.example.app.xml', package)
        before = path.read_bytes()
        for name in shortcut_service.__artifacts_v2__:
            self.rows(name)
        self.assertEqual(path.read_bytes(), before)

    @staticmethod
    def png():
        output = io.BytesIO()
        shortcut_service.Image.new('RGB', (2, 2), 'blue').save(output, format='PNG')
        return output.getvalue()

    def bitmap(self, stored_path, user='0', package='com.example.app', source_prefix=''):
        root, shortcut = self.package(package)
        shortcut.set('bitmap-path', stored_path)
        self.write(source_prefix + 'packages/' + package + '.xml', root, user=user)
        return root, shortcut

    def test_bitmap_is_matched_by_full_path_and_preserves_case(self):
        stored = '/data/system_ce/0/shortcut_service/bitmaps/com.example.app/MiXeD.png'
        self.bitmap(stored)
        image = self.write('bitmaps/com.example.app/MiXeD.png', self.png())
        self.write('bitmaps/com.example.other/MiXeD.png', self.png())
        with patch.object(shortcut_service, 'check_in_media', return_value='media-reference') as check:
            row = self.rows('get_shortcut_service')[0]
        self.assertEqual(row['Bitmap Path (as stored)'], stored)
        self.assertEqual(row['Bitmap Status'], 'Matched')
        self.assertEqual(row['Shortcut Image'], 'media-reference')
        self.assertEqual(row['Bitmap Source File'], Context.get_relative_path(str(image)))
        self.assertEqual(check.call_args.args[0], str(image))

    def test_missing_bitmap_does_not_fall_back_to_matching_basename(self):
        self.bitmap('/data/system_ce/0/shortcut_service/bitmaps/com.example.app/shared.png')
        self.write('bitmaps/com.example.other/shared.png', self.png())
        with patch.object(shortcut_service, 'check_in_media') as check:
            row = self.rows('get_shortcut_service')[0]
        self.assertEqual(row['Bitmap Status'], 'Bitmap file missing')
        self.assertEqual(row['Shortcut Image'], '')
        check.assert_not_called()

    def test_bitmap_from_another_extraction_tree_is_not_matched(self):
        self.bitmap('/data/system_ce/0/shortcut_service/bitmaps/com.example.app/image.png')
        image = self.write('bitmaps/com.example.app/image.png', self.png())
        foreign = self.root / 'second-extraction' / image.relative_to(self.root)
        foreign.parent.mkdir(parents=True)
        image.rename(foreign)
        Context.set_files_found([str(foreign) if item == str(image) else item for item in self.files])
        self.assertEqual(self.rows('get_shortcut_service')[0]['Bitmap Status'], 'Bitmap file missing')

    def test_bitmap_path_case_is_not_normalized(self):
        self.bitmap('/data/system_ce/0/shortcut_service/bitmaps/com.example.app/MiXeD.png')
        self.write('bitmaps/com.example.app/mixed.png', self.png())
        self.assertEqual(self.rows('get_shortcut_service')[0]['Bitmap Status'], 'Bitmap file missing')

    def test_same_bitmap_name_in_two_profiles_is_not_merged(self):
        for user in ('0', '10'):
            self.bitmap(f'/data/system_ce/{user}/shortcut_service/bitmaps/com.example.app/shared.png',
                        user=user)
            self.write('bitmaps/com.example.app/shared.png', self.png(), user=user)
        with patch.object(shortcut_service, 'check_in_media', side_effect=lambda path, *_a, **_k: path):
            rows = self.rows('get_shortcut_service')
        self.assertEqual({row['Bitmap Status'] for row in rows}, {'Matched'})
        self.assertNotEqual(rows[0]['Shortcut Image'], rows[1]['Shortcut Image'])
        for row in rows:
            self.assertIn('/system_ce/' + row['Android User'] + '/', row['Bitmap Source File'])

    def test_bitmap_reference_to_another_profile_is_not_matched(self):
        self.bitmap('/data/system_ce/10/shortcut_service/bitmaps/com.example.app/shared.png')
        self.write('bitmaps/com.example.app/shared.png', self.png(), user='10')
        self.assertEqual(self.rows('get_shortcut_service')[0]['Bitmap Status'], 'Android user mismatch')

    def test_bitmap_reference_to_another_package_is_not_matched(self):
        self.bitmap('/data/system_ce/0/shortcut_service/bitmaps/com.example.other/shared.png')
        self.write('bitmaps/com.example.other/shared.png', self.png())
        self.assertEqual(self.rows('get_shortcut_service')[0]['Bitmap Status'], 'Package mismatch')

    def test_relative_bitmap_path_is_supported_without_guessing_basenames(self):
        self.bitmap('bitmaps/com.example.app/image.png')
        self.write('bitmaps/com.example.app/image.png', self.png())
        with patch.object(shortcut_service, 'check_in_media', return_value='media-reference'):
            self.assertEqual(self.rows('get_shortcut_service')[0]['Bitmap Status'], 'Matched')

    def test_bitmap_paths_cannot_traverse_directories(self):
        self.bitmap('/data/system_ce/0/shortcut_service/bitmaps/com.example.app/../other.png')
        self.assertEqual(self.rows('get_shortcut_service')[0]['Bitmap Status'], 'Invalid bitmap path')

    def test_corrupt_bitmap_is_not_registered_as_media(self):
        self.bitmap('/data/system_ce/0/shortcut_service/bitmaps/com.example.app/image.png')
        self.write('bitmaps/com.example.app/image.png', b'\x89PNG\r\n\x1a\ncorrupt')
        with patch.object(shortcut_service, 'check_in_media') as check:
            self.assertEqual(self.rows('get_shortcut_service')[0]['Bitmap Status'],
                             'Invalid or unreadable image')
        check.assert_not_called()







    def test_media_outputs_register_exact_evidence_path_and_copy_original_bytes(self):
        self.bitmap('/data/system_ce/0/shortcut_service/bitmaps/com.example.app/image.png')
        image = self.write('bitmaps/com.example.app/image.png', self.png())
        seeker = types.SimpleNamespace(file_infos={
            path: FileInfo(Context.get_relative_path(path), 0, 0) for path in self.files})
        params = ilapfuncs.OutputParameters(str(self.root / 'report'), 'media-integration')
        Context.set_output_params(params)
        Context.set_data_folder(str(self.root))
        output = Path(params.output_folder_base)
        report = output / '_HTML' / 'Shortcut Service'
        report.mkdir(parents=True)
        lavafuncs.initialize_lava(str(self.root), str(output), 'fs')
        processor = vars(shortcut_service)['get_shortcut_service']
        processor(self.files, str(report), seeker, False)
        row = lavafuncs.lava_db.execute(
            'SELECT bitmap_status, shortcut_image FROM get_shortcut_service').fetchone()
        self.assertEqual(row[0], 'Matched')
        self.assertTrue(row[1])
        item = lavafuncs.lava_db.execute(
            'SELECT source_path, extraction_path FROM _lava_media_items').fetchone()
        self.assertEqual(item[0], Context.get_relative_path(str(image)))
        self.assertEqual((output / item[1]).read_bytes(), image.read_bytes())
        html = next(report.glob('*.temphtml')).read_text(encoding='utf-8')
        self.assertIn('<img ', html)
        self.assertIn('max-width:80px;max-height:80px', html)
        self.assertNotIn(str(self.root), html)


    def test_unknown_types_case_and_original_json_remain_in_shortcuts(self):
        package, shortcut = self.package()
        raw = '{"MiXeD":[false,null,"StoredValue"]}'
        for value in ('FirstValue', 'SecondValue'):
            extras = ET.SubElement(ET.SubElement(shortcut, 'intent'), 'extras')
            ET.SubElement(extras, 'string', name='CaseSensitiveKey').text = value
        extras = ET.SubElement(shortcut, 'extras')
        ET.SubElement(extras, 'future-type', name='UnknownKey', value='Preserved')
        ET.SubElement(extras, 'string', name='Payload').text = raw
        self.write('packages/com.example.app.xml', package)
        row = self.rows('get_shortcut_service')[0]
        self.assertIn('FirstValue', row['Intents (JSON)'])
        self.assertIn('SecondValue', row['Intents (JSON)'])
        self.assertIn('CaseSensitiveKey', row['Intents (JSON)'])
        nodes = json.loads(row['Extras (JSON)'])[0]['children']
        self.assertEqual(nodes[0]['attributes']['value'], 'Preserved')
        self.assertEqual(nodes[1]['text'], raw)

    def test_identical_copies_are_inventoried_without_repeated_shortcuts(self):
        package, _ = self.package()
        self.write('packages/com.example.app.xml', package)
        for suffix in ('.bak', '.backup', '.reservecopy', '.fallback'):
            self.write('packages/com.example.app.xml' + suffix, package)
        self.assertEqual(len(self.rows('get_shortcut_service')), 1)
        files = self.rows('get_shortcut_service_files')
        copies = [row for row in files if row['Copy Comparison'] == 'Identical to main']
        self.assertEqual(len(copies), 4)
        self.assertTrue(all(row['Shortcut Count'] == 1 and row['Reported Shortcut Count'] == 0
                            for row in copies))
        self.assertTrue(all(row['Main Source File'].endswith('com.example.app.xml') for row in copies))

    def test_126_identical_reserve_entries_do_not_double_the_rows(self):
        package = ET.Element('package', name='com.example.app')
        for index in range(126):
            ET.SubElement(package, 'shortcut', id=str(index), title=f'Shortcut {index}')
        self.write('packages/com.example.app.xml', package)
        self.write('packages/com.example.app.xml.reservecopy', package)
        self.assertEqual(len(self.rows('get_shortcut_service')), 126)
        files = self.rows('get_shortcut_service_files')
        self.assertEqual(sum(row['Reported Shortcut Count'] for row in files), 126)
        self.assertEqual(sum(row['Shortcut Count'] for row in files), 252)

    @staticmethod
    def binary_xml(root):
        data = bytearray(b'ABX\x00\x10')
        strings = {}

        def string(value, intern=False):
            if intern and value in strings:
                data.extend(struct.pack('>h', strings[value]))
                return
            if intern:
                data.extend(b'\xff\xff')
                strings[value] = len(strings)
            value = value.encode('utf-8')
            data.extend(struct.pack('>h', len(value)))
            data.extend(value)

        def node(element):
            data.append(0x32)
            string(element.tag, True)
            for key, value in element.attrib.items():
                data.append(0x2f)
                string(key, True)
                string(value)
            for child in element:
                node(child)
            data.append(0x33)
            string(element.tag, True)

        node(root)
        data.append(0x11)
        return bytes(data)

    def test_abx_fallback_is_compared_by_content_with_xml_main(self):
        root = ET.Element('user')
        package, _ = self.package()
        root.append(package)
        self.write('shortcuts.xml', root)
        self.write('shortcuts.xml.fallback', self.binary_xml(root))
        self.assertEqual(len(self.rows('get_shortcut_service')), 1)
        files = self.rows('get_shortcut_service_files')
        fallback = next(row for row in files if row['Source Kind'] == 'Vendor fallback')
        self.assertEqual(fallback['File Format'], 'ABX')
        self.assertEqual(fallback['Copy Comparison'], 'Identical to main')

    def test_different_abx_fallback_retains_its_shortcut(self):
        root = ET.Element('user')
        package, shortcut = self.package()
        root.append(package)
        self.write('shortcuts.xml', root)
        shortcut.set('title', 'FallbackLabel')
        self.write('shortcuts.xml.fallback', self.binary_xml(root))
        self.assertEqual({row['Short Label'] for row in self.rows('get_shortcut_service')},
                         {'MiXeD Label', 'FallbackLabel'})

    def test_formatting_only_changes_do_not_repeat_a_backup(self):
        self.write('packages/com.example.app.xml',
                   b'<package name="com.example.app"><shortcut id="one" title="Label" /></package>')
        self.write('packages/com.example.app.xml.backup',
                   b'<package name="com.example.app">\n  <shortcut title="Label" id="one" />\n</package>')
        self.assertEqual(len(self.rows('get_shortcut_service')), 1)
        files = self.rows('get_shortcut_service_files')
        self.assertNotEqual(files[0]['SHA-256'], files[1]['SHA-256'])
        self.assertEqual(files[1]['Copy Comparison'], 'Identical to main')

    def test_changed_backup_keeps_its_previous_alias(self):
        package, shortcut = self.package()
        self.write('packages/com.example.app.xml', package)
        shortcut.set('title', 'PreviousAlias')
        self.write('packages/com.example.app.xml.backup', package)
        self.assertEqual({row['Short Label'] for row in self.rows('get_shortcut_service')},
                         {'MiXeD Label', 'PreviousAlias'})
        self.assertEqual(self.rows('get_shortcut_service_files')[1]['Copy Comparison'],
                         'Differs from main')

    def test_copies_without_main_files_are_retained(self):
        for index, suffix in enumerate(('.bak', '.backup', '.reservecopy', '.fallback')):
            package, _ = self.package('com.example.app' + str(index))
            self.write('packages/com.example.app' + str(index) + '.xml' + suffix, package)
        self.assertEqual(len(self.rows('get_shortcut_service')), 4)
        self.assertEqual({row['Copy Comparison'] for row in self.rows('get_shortcut_service_files')},
                         {'Main file absent'})

    def test_identical_copies_do_not_repeat_discord_payloads(self):
        package, _ = self.discord([('user_username', 'StoredExtra'), ('guild_id', 'stored-guild')])
        self.write('packages/com.discord.xml', package)
        self.write('packages/com.discord.xml.reservecopy', package)
        rows = self.rows('get_shortcut_service_discord')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['Guild ID (extra)'], 'stored-guild')

    def test_second_user_150_and_its_copies_remain_separate(self):
        for user in ('0', '150'):
            package, _ = self.package()
            self.write('packages/com.example.app.xml', package, user=user)
            self.write('packages/com.example.app.xml.reservecopy', package, user=user)
        self.assertEqual([row['Android User'] for row in self.rows('get_shortcut_service')], ['0', '150'])
        self.assertEqual(len(self.rows('get_shortcut_service_files')), 4)

    def test_xml_declaration_only_is_not_a_parse_error(self):
        declaration = b"<?xml version='1.0' encoding='utf-8' standalone='yes' ?>\n"
        self.assertEqual(len(declaration), 57)
        for index, data in enumerate((declaration, b'\xef\xbb\xbf' + declaration,
                                     '<?xml version="1.0" encoding="utf-16"?>'.encode('utf-16'))):
            self.write(f'packages/com.example.empty{index}.xml', data)
        rows = self.rows('get_shortcut_service_files')
        self.assertEqual({row['Parse Status'] for row in rows}, {'XML declaration only'})
        self.assertEqual({row['Error'] for row in rows}, {''})
        self.assertEqual(self.rows('get_shortcut_service'), [])

    def test_incomplete_declaration_remains_a_parse_error(self):
        self.write('packages/com.example.bad.xml', b'<?xml version="1.0"')
        self.assertEqual(self.rows('get_shortcut_service_files')[0]['Parse Status'], 'Parse error')

    def test_combined_flags_and_disabled_reason_are_decoded_beside_raw_values(self):
        package, shortcut = self.package()
        shortcut.set('flags', '16387')
        shortcut.set('disabled-reason', '102')
        self.write('packages/com.example.app.xml', package)
        row = self.rows('get_shortcut_service')[0]
        self.assertEqual(row['Flags (as stored)'], '16387')
        self.assertEqual(row['Flags (decoded)'], 'dynamic; pinned; cached_notifications')
        self.assertEqual(row['Disabled Reason (as stored)'], '102')
        self.assertEqual(row['Disabled Reason (decoded)'], 'signature_mismatch')

    def test_unknown_bits_and_unknown_disabled_reason_are_visible(self):
        package, shortcut = self.package()
        shortcut.set('flags', str((1 << 20) | 32))
        shortcut.set('disabled-reason', '999')
        self.write('packages/com.example.app.xml', package)
        row = self.rows('get_shortcut_service')[0]
        self.assertEqual(row['Flags (decoded)'], 'manifest; unknown_bits(0x100000)')
        self.assertEqual(row['Disabled Reason (decoded)'], 'unknown(999)')

    def test_invalid_flags_are_visible_and_do_not_hide_the_shortcut(self):
        package, shortcut = self.package()
        shortcut.set('flags', 'invalid')
        self.write('packages/com.example.app.xml', package)
        self.assertEqual(self.rows('get_shortcut_service')[0]['Flags (decoded)'], 'Unrecognized value')

    def test_signed_flags_preserve_unknown_high_bits(self):
        package, shortcut = self.package()
        shortcut.set('flags', '-2147483648')
        self.write('packages/com.example.app.xml', package)
        self.assertEqual(self.rows('get_shortcut_service')[0]['Flags (decoded)'],
                         'unknown_bits(0x80000000)')

    def test_missing_codes_are_not_assigned_default_values(self):
        package, _ = self.package()
        self.write('packages/com.example.app.xml', package)
        row = self.rows('get_shortcut_service')[0]
        self.assertEqual(row['Flags (decoded)'], '')
        self.assertEqual(row['Disabled Reason (decoded)'], '')

    def test_dumps_are_inventoried_without_payload_cells_or_shortcut_rows(self):
        package, _ = self.package()
        xml = self.write('shortcut_dump/backup-1-payload.txt', package)
        self.write('shortcut_dump/restore-0-start.txt', b'Start time: 1700000000123\n')
        self.write('shortcut_dump/binary.dat', b'\xff\xfe\x00')
        self.write('shortcut_dump/empty.txt', b'')
        self.write('shortcut_dump/restore-1-payload.xml', b'<broken>')
        self.assertEqual(self.rows('get_shortcut_service'), [])
        self.assertEqual(self.rows('get_shortcut_service_discord'), [])
        rows = self.rows('get_shortcut_service_files')
        self.assertEqual(len(rows), 5)
        self.assertEqual({row['Parse Status'] for row in rows},
                         {'Parsed', 'Text dump', 'Binary dump', 'Empty file', 'Parse error'})
        self.assertTrue(all(row['Reported Shortcut Count'] == 0 for row in rows))
        self.assertNotIn('Content (UTF-8)', rows[0])
        saved = next(row for row in rows if row['Source File'].endswith('backup-1-payload.txt'))
        self.assertEqual(saved['SHA-256'], hashlib.sha256(xml.read_bytes()).hexdigest())

    def test_decorated_outputs_preserve_names_and_raw_timestamps(self):
        message = {'timestamp': '2023-10-01T12:00:00.123Z',
                   'author': {'username': 'StoredAuthor'}}
        package, _ = self.discord([('user_username', 'StoredExtra'),
                                   ('message', json.dumps(message))])
        self.write('packages/com.discord.xml', package)
        params = ilapfuncs.OutputParameters(str(self.root / 'report'), 'integration')
        Context.set_output_params(params)
        Context.set_data_folder(str(self.root))
        output = Path(params.output_folder_base)
        report = output / '_HTML' / 'Shortcut Service'
        report.mkdir(parents=True)
        lavafuncs.initialize_lava(str(self.root), str(output), 'fs')
        for name in ('get_shortcut_service', 'get_shortcut_service_discord'):
            processor = vars(shortcut_service)[name]
            processor(self.files, str(report), None, False)
        row = lavafuncs.lava_db.execute(
            'SELECT short_label, shortcut_timestamp_ms_as_stored, '
            'shortcut_updated_utc, source_file FROM get_shortcut_service').fetchone()
        self.assertEqual(row[0], 'MiXeD Label')
        self.assertEqual(row[1], '1700000000123')
        self.assertEqual(row[2], int(row[1]) // 1000)
        self.assertFalse(Path(row[3]).is_absolute())
        row = lavafuncs.lava_db.execute(
            'SELECT username_extra, author_username_json, message_time_as_stored '
            'FROM get_shortcut_service_discord').fetchone()
        self.assertEqual(row, ('StoredExtra', 'StoredAuthor', message['timestamp']))
        self.assertEqual([entry['record_count'] for entry in
                          lavafuncs.lava_data['artifacts']['Shortcut Service']], [1, 1])
        with sqlite3.connect(output / '_Timeline' / 'tl.db') as db:
            timeline = db.execute('SELECT key, activity, datalist FROM data').fetchall()
        self.assertEqual(len(timeline), 2)
        self.assertEqual({key for key, _, _ in timeline}, {'2023-11-14 22:13:20.123000+00:00'})
        for _, _, values in timeline:
            self.assertEqual(json.loads(values)['Shortcut Timestamp (ms, as stored)'], '1700000000123')
        self.assertEqual(len(list((output / '_TSV Exports').glob('*.tsv'))), 2)
        self.assertEqual(len(list(report.glob('*.temphtml'))), 2)

    def test_processing_failure_restores_global_state(self):
        package, _ = self.package()
        self.write('packages/com.example.app.xml', package)
        original_context = {name: value for name, value in vars(Context).items()
                            if name.startswith('_') and not name.startswith('__')
                            and not isinstance(value, staticmethod)}
        connection = sqlite3.connect(':memory:')
        self.addCleanup(connection.close)
        lavafuncs.lava_db = connection
        lavafuncs.lava_data = {'sentinel': True}
        ilapfuncs.OutputParameters.screen_output_file_path = 'sentinel'
        ilapfuncs.icons['sentinel'] = {'value': 'unchanged'}
        previous_stdout = sys.stdout
        with self.assertRaisesRegex(RuntimeError, 'synthetic failure'):
            with isolated_output():
                Context.set_data_folder('replacement')
                lavafuncs.initialize_lava(str(self.root), str(self.root), 'fs')
                with patch.object(shortcut_service, '_documents', side_effect=RuntimeError('synthetic failure')):
                    processor = vars(shortcut_service)['get_shortcut_service']
                    processor(self.files, str(self.root), None, False)
        self.assertIs(lavafuncs.lava_db, connection)
        self.assertEqual(connection.execute('SELECT 1').fetchone(), (1,))
        self.assertEqual(lavafuncs.lava_data, {'sentinel': True})
        self.assertEqual(ilapfuncs.OutputParameters.screen_output_file_path, 'sentinel')
        self.assertEqual(ilapfuncs.icons, {'sentinel': {'value': 'unchanged'}})
        self.assertIs(sys.stdout, previous_stdout)
        for name, value in original_context.items():
            self.assertIs(getattr(Context, name), value)


if __name__ == '__main__':
    unittest.main()
