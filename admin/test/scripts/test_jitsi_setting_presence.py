"""Present Jitsi settings retain raw values without inventing missing keys."""
import json
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from admin.test.scripts.test_sdhms_stat_sources import context
from scripts.artifacts import jitsiMeet as parser


def make_db(root, namespace, pairs):
    path = root / namespace / 'org.jitsi.meet/databases/RKStorage'
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE catalystLocalStorage(key TEXT, value)')
    db.executemany('INSERT INTO catalystLocalStorage VALUES(?,?)', pairs)
    db.commit()
    db.close()
    return path


class JitsiSettingPresenceTest(unittest.TestCase):
    def test_presence_and_sql_vs_json_types_and_valid_order(self):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            files = []
            for index, value in enumerate(['', None, False, 0, [], {}, 'null']):
                files.append(make_db(root, str(index), [
                    (parser.SETTINGS_KEY, json.dumps({'displayName': value})),
                    (parser.INSTALL_ID_KEY, None), (parser.CALLSTATS_KEY, 'null'),
                    (parser.DOMAINS_KEY, '[]')]))
            files.append(make_db(root, 'last', [(parser.SETTINGS_KEY, '{"displayName":"valid","email":"email"}'),
                                              (parser.INSTALL_ID_KEY, 'id'), (parser.CALLSTATS_KEY, 'call'),
                                              (parser.DOMAINS_KEY, '["one","two"]')]))
            headers, rows, sources = parser.jitsi_meet_settings.__wrapped__(context(root, files))
            self.assertEqual(headers[-1], 'Source File')
            self.assertEqual(len(rows), 33)
            self.assertEqual(sources.splitlines(), list(map(str, files)))
            for index, value in enumerate(['', None, False, 0, [], {}, 'null']):
                group = rows[index*4:index*4+4]
                self.assertEqual(json.loads(group[0][3]), value)
                self.assertEqual(group[0][4], json.dumps({'displayName': value}))
                self.assertEqual(group[1][2], 'SQL NULL')
                self.assertEqual(json.loads(group[2][3]), {'storage_kind': 'text', 'value': 'null'})
                self.assertEqual(group[3][2], 'Empty list')
                self.assertNotIn('Email', [r[0] for r in group])
            self.assertEqual([r[:2] for r in rows[-5:]], [('Display Name','valid'), ('Email','email'),
                             ('Install ID','id'), ('Call Stats Username','call'), ('Known Domains','one, two')])

    def test_bad_roots_blobs_mixed_domains_and_later_healthy(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(parser, 'logfunc') as logger:
            root = pathlib.Path(folder)
            files = [make_db(root, str(i), [(parser.SETTINGS_KEY, raw)])
                     for i, raw in enumerate([None, '', 'null', '[]', '7', b'\xff'])]
            files.append(make_db(root, 'mixed', [(parser.DOMAINS_KEY, '[0,null,"x"]')]))
            files.append(make_db(root, 'missing', [('other', 'anything')]))
            files.append(make_db(root, 'healthy', [(parser.SETTINGS_KEY, '{"email":"later"}')]))
            _, rows, _ = parser.jitsi_meet_settings.__wrapped__(context(root, files))
            self.assertEqual(len(rows), 8)
            self.assertEqual([r[0] for r in rows[:6]], ['Settings Document']*6)
            self.assertEqual(json.loads(rows[0][3]), {'storage_kind':'null','value':None})
            self.assertEqual(json.loads(rows[2][3]), None)
            self.assertEqual(json.loads(rows[5][3]), {'storage_kind':'blob','hex':'ff'})
            self.assertEqual(json.loads(rows[5][4]), {'storage_kind':'blob','hex':'ff'})
            self.assertEqual(json.loads(rows[6][3]), [0, None, 'x'])
            self.assertEqual(rows[-1][0:2], ('Email', 'later'))
            self.assertEqual(logger.call_count, 7)


if __name__ == '__main__':
    unittest.main()
