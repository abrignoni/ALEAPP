"""Actual SQLite/WAL and JSON field-presence boundaries."""
# pylint: disable=protected-access
from pathlib import Path
import hashlib
import itertools
import json
import math
import shutil
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.artifacts import bitwarden as artifact  # pylint: disable=wrong-import-position


class Context:
    def __init__(self, root, files):
        self.root, self.files = Path(root), files

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


def hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in Path(root).rglob('*') if p.is_file()}


def samples():
    values = [None, False, True, 0, 1, -1, 2, 1.0, -0.0, 10**100, -(10**100),
              '', 'false', 'unicode \u03b1\n\t', [], [False, 0, None, 0], {},
              {'status': 'present', 'json': {'nested': [1, 1.0, None]}},
              float('nan'), float('inf'), -float('inf')]
    raw = [json.dumps(dict(favorite=v, reprompt=values[-i-1],
                           creationDate='2026-01-02T03:04:05Z',
                           revisionDate='2026-02-03T04:05:06Z'))
           for i, v in enumerate(values)]
    raw.extend(['{}', '{"favorite":null}', '{"reprompt":false}',
                '{"favorite":1,"favorite":2,"reprompt":1e400}',
                b'{"favorite":"\\u03b1","reprompt":-0.0}',
                None, '', b'', '{', b'\xff', 0, 4, 1.25,
                'null', 'false', '0', '0.0', '""', '[]'])
    raw.append(raw[2])
    return raw


def create_store(root, relative='data/data/com.x8bit.bitwarden', wal=False, prefix=''):
    folder = Path(root) / relative / 'databases'
    folder.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as work:
        source = Path(work) / 'vault_database'
        connection = sqlite3.connect(source)
        if wal:
            connection.execute('pragma journal_mode=wal')
            connection.execute('pragma wal_autocheckpoint=0')
        connection.execute('CREATE TABLE ciphers(id,user_id,cipher_type,cipher_json,organization_id)')
        connection.commit()
        if wal:
            connection.execute('pragma wal_checkpoint(truncate)')
        rows = [(prefix + str(i).zfill(3), prefix + 'user', '1', raw, None)
                for i, raw in enumerate(samples())]
        rows.append(rows[2])
        connection.executemany('INSERT INTO ciphers VALUES(?,?,?,?,?)', rows)
        connection.commit()
        for item in Path(work).glob('vault_database*'):
            target = folder / item.name
            shutil.copyfile(item, target)
            assert hashlib.sha256(item.read_bytes()).digest() == hashlib.sha256(target.read_bytes()).digest()
            target.chmod(0o444)
        connection.close()
    return folder / 'vault_database'


def direct_rows(path):
    connection = sqlite3.connect('file:' + str(path) + '?mode=ro', uri=True)
    assert connection.execute('pragma integrity_check').fetchall() == [('ok',)]
    assert connection.execute('pragma quick_check').fetchall() == [('ok',)]
    rows = connection.execute('SELECT id,user_id,cipher_type,cipher_json,organization_id FROM ciphers ORDER BY id').fetchall()
    connection.close()
    return rows


def assert_value(test, actual, expected):
    test.assertIs(type(actual), type(expected))
    if isinstance(expected, float):
        if math.isnan(expected):
            test.assertTrue(math.isnan(actual))
        else:
            test.assertEqual(actual, expected)
            if expected == 0:
                test.assertEqual(math.copysign(1, actual), math.copysign(1, expected))
    elif isinstance(expected, list):
        test.assertEqual(len(actual), len(expected))
        for a, b in zip(actual, expected):
            assert_value(test, a, b)
    elif isinstance(expected, dict):
        test.assertEqual(list(actual), list(expected))
        for key in expected:
            assert_value(test, actual[key], expected[key])
    else:
        test.assertEqual(actual, expected)


def check_document(test, raw, field, text):
    # Reject nonstandard outer numeric constants even though inner text may contain them.
    def reject(value):
        raise AssertionError(value)
    document = json.loads(text, parse_constant=reject)
    if raw is None:
        expected = 'sql_null_input'
    elif not isinstance(raw, (str, bytes, bytearray)):
        expected = 'unsupported_json_input_type'
    elif len(raw) == 0:
        expected = 'empty_input'
    else:
        try:
            parsed = json.loads(raw)
        except (TypeError, ValueError):
            expected = 'invalid_json'
        else:
            if not isinstance(parsed, dict):
                expected = 'decoded_non_object'
                test.assertEqual(set(document), {'status', 'root_kind'})
                test.assertEqual(document['root_kind'], {
                    type(None): 'null', bool: 'boolean', int: 'integer',
                    float: 'float', str: 'string', list: 'array'}[type(parsed)])
            elif field not in parsed:
                expected = 'missing_key'
            else:
                expected = 'present'
                test.assertEqual(set(document), {'status', 'json'})
                test.assertIsInstance(document['json'], str)
                assert_value(test, json.loads(document['json']), parsed[field])
    test.assertEqual(document['status'], expected)
    if expected not in ('present', 'decoded_non_object'):
        test.assertEqual(set(document), {'status'})


class TestFieldPresence(unittest.TestCase):
    def check_store(self, root, path):
        initial = hashes(root)
        headers, rows, source = artifact.bitwarden_vault_items.__wrapped__(Context(root, [path]))
        records = direct_rows(path)
        self.assertEqual(len(rows), len(records))
        self.assertEqual(len(headers), 9)
        self.assertEqual(source, str(path))
        for row, record in zip(rows, records):
            for index, field in [(4, 'favorite'), (5, 'reprompt')]:
                check_document(self, record[3], field, row[index])
        self.assertEqual(hashes(root), initial)

    def test_actual_sqlite_status_types_roundtrip_duplicates(self):
        with tempfile.TemporaryDirectory() as root:
            self.check_store(root, create_store(root))
        self.assertEqual(artifact._field_document('{"favorite":null}', 'favorite'),
                         '{"status":"present","json":"null"}')
        self.assertEqual(artifact._field_document('{}', 'favorite'), '{"status":"missing_key"}')
        self.assertTrue(issubclass(UnicodeDecodeError, ValueError))

    def test_complete_wal_and_main_only_control(self):
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as control:
            path = create_store(root, wal=True)
            self.assertGreater(Path(str(path) + '-wal').stat().st_size, 0)
            self.check_store(root, path)
            target = Path(control) / 'vault_database'
            shutil.copyfile(path, target)
            target.chmod(0o444)
            self.assertEqual(direct_rows(target), [])

    def test_truthy_nonobject_helper_only_never_exports_root_value(self):
        for raw in ['["unrelated-secret"]', '"unrelated-secret"', 'true', '42', '1.25']:
            check_document(self, raw, 'favorite', artifact._field_document(raw, 'favorite'))
            self.assertNotIn('unrelated-secret', artifact._field_document(raw, 'favorite'))

    def test_alias_ranking_distinct_users_and_encounter_order(self):
        with tempfile.TemporaryDirectory() as root:
            preferred = create_store(root, prefix='preferred-')
            alias = create_store(root, 'data/user/0/com.x8bit.bitwarden', prefix='conflict-')
            equal_alias = create_store(root, 'data_mirror/data_ce/null/0/com.x8bit.bitwarden',
                                       prefix='preferred-')
            self.assertEqual(preferred.read_bytes(), equal_alias.read_bytes())
            user = create_store(root, 'data/user/10/com.x8bit.bitwarden', prefix='user10-')
            device = create_store(root, 'data/user_de/0/com.x8bit.bitwarden', prefix='de-')
            for order in itertools.permutations([alias, preferred, user, device]):
                files = [equal_alias] + list(order)
                selected = artifact._files(Context(root, files), artifact.DB_SUFFIX)
                self.assertNotIn(str(alias), selected)
                self.assertNotIn(str(equal_alias), selected)
                self.assertEqual(set(selected), {str(preferred), str(user), str(device)})
                _, rows, source = artifact.bitwarden_vault_items.__wrapped__(Context(root, files))
                self.assertEqual(source.splitlines(), selected)
                self.assertEqual([r[8] for r in rows], [str(Path(p).relative_to(root))
                                 for p in selected for _ in direct_rows(p)])


if __name__ == '__main__':
    unittest.main()
