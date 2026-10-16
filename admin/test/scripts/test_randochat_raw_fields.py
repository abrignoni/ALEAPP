"""Stored sex values survive unknown codes; MAX and person IDs stay source-based."""
import pathlib
import sqlite3
import tempfile
import unittest
from admin.test.scripts.test_sdhms_stat_sources import context
from scripts.artifacts.RandoChat import randochat_account, randochat_contacts

VALUES = ['H', 'M', 'X', None, 0, '', -1, 1.5, 'X']

def make_fixture(root, null_settings=False, empty_contacts=False):
    root = pathlib.Path(root)
    path = root / 'data/data/com.random.chat.app/databases/ramdochatV2.db'
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute('CREATE TABLE configuracao(name,value)')
    con.execute('CREATE TABLE conversa(id_pessoa,apelido,idade,sexo,favorite,bloqueado,images)')
    con.execute("INSERT INTO configuracao VALUES('apelido','Fixture')")
    for key in ['sexo', 'sexo_search']:
        con.executemany('INSERT INTO configuracao VALUES(?,?)', [(key, value) for value in ([None] if null_settings else VALUES)])
    if not empty_contacts:
        for value in VALUES:
            con.execute('INSERT INTO conversa VALUES(1,\'Contact\',20,?,1,0,\'\')', (value,))
    con.commit()
    con.close()
    return path

class RandoChatRawFieldsTest(unittest.TestCase):
    def test_raw_contacts_types_ids_duplicates_and_account_max(self):
        with tempfile.TemporaryDirectory() as folder:
            path = make_fixture(folder)
            ctx = context(folder, [path])
            headers, rows, source = randochat_contacts.__wrapped__(ctx)
            self.assertEqual([row[headers.index('Stored Sex')] for row in rows], VALUES)
            self.assertEqual(rows[2], rows[8])
            self.assertTrue(all(row[0] == 1 for row in rows))
            self.assertEqual(headers[0], 'Stored Person ID')
            self.assertEqual(source, str(path))
            self.assertNotIn('Source File', headers)
            self.assertIsNone(rows[3][3])
            self.assertIsInstance(rows[4][3], int)
            self.assertIsInstance(rows[7][3], float)
            headers, rows, _ = randochat_account.__wrapped__(ctx)
            con = sqlite3.connect(path)
            for name, header in [('sexo', 'Stored Sex'), ('sexo_search', 'Stored Sex Search Value')]:
                expected = con.execute('SELECT MAX(value) FROM configuracao WHERE name LIKE ?', (name,)).fetchone()[0]
                self.assertEqual(rows[0][headers.index(header)], expected)
            con.close()

    def test_null_settings_and_empty_contacts(self):
        with tempfile.TemporaryDirectory() as folder:
            path = make_fixture(folder, null_settings=True, empty_contacts=True)
            ctx = context(folder, [path])
            headers, rows, _ = randochat_account.__wrapped__(ctx)
            self.assertIsNone(rows[0][headers.index('Stored Sex')])
            self.assertIsNone(rows[0][headers.index('Stored Sex Search Value')])
            self.assertEqual(randochat_contacts.__wrapped__(ctx)[1], [])
