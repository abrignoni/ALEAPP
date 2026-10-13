"""Shortcut Service regression tests using synthetic XML and payloads."""

import ast
import hashlib
import io
import json
import sqlite3
import sys
import tempfile
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
        self.assertEqual(len(artifacts), 4)
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

    def test_intent_scopes_array_indices_case_and_unknown_types(self):
        package, shortcut = self.package()
        for value in ('FirstValue', 'SecondValue'):
            extras = ET.SubElement(ET.SubElement(shortcut, 'intent'), 'extras')
            ET.SubElement(extras, 'string', name='CaseSensitiveKey').text = value
        extras = ET.SubElement(shortcut, 'extras')
        array = ET.SubElement(extras, 'string-array', name='OrderedValues', num='2')
        ET.SubElement(array, 'item', value='FirstItem')
        ET.SubElement(array, 'item', value='SecondItem')
        ET.SubElement(extras, 'future-type', name='UnknownKey', value='Preserved')
        self.write('packages/com.example.app.xml', package)
        rows = self.rows('get_shortcut_service_fields')
        texts = [row for row in rows if row['Field'] == '#text']
        self.assertEqual([row['Entry Name (as stored)'] for row in texts],
                         ['CaseSensitiveKey', 'CaseSensitiveKey'])
        self.assertIn('/intent[1]/', texts[0]['XML Path'])
        self.assertIn('/intent[2]/', texts[1]['XML Path'])
        self.assertTrue(any(row['Value'] == 'SecondItem' and '/item[2]' in row['XML Path'] for row in rows))
        self.assertTrue(any(row['Value'] == 'Preserved' and row['Type'] == 'future-type' for row in rows))

    def test_json_is_additional_and_original_is_unchanged(self):
        package, shortcut = self.package()
        payload = '{"a/b":{"~key":[false,null,"MiXeD"]}}'
        extras = ET.SubElement(shortcut, 'extras')
        ET.SubElement(extras, 'string', name='Payload').text = payload
        self.write('packages/com.example.app.xml', package)
        rows = self.rows('get_shortcut_service_fields')
        self.assertTrue(any(row['Value'] == payload and row['Representation'] == 'text' for row in rows))
        self.assertTrue(any(row['JSON Pointer'] == '/a~1b/~0key/2' and row['Value'] == 'MiXeD' for row in rows))
        self.assertTrue(any(row['Type'] == 'boolean' and row['Value'] == 'false' for row in rows))

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
        self.assertTrue(any(field['Value'] == 'TrailingItem'
                            for field in self.rows('get_shortcut_service_fields')))

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
