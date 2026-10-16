"""Stored call types survive independently of the existing CASE labels and icons."""
import ast
import datetime
import pathlib
import sqlite3
import shutil
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts.calllog import get_calllog, CALL_TYPE_ICONS, __artifacts_v2__  # pylint: disable=wrong-import-position

TYPES = [1,2,3,4,5,6,7,0,8,None,-1,'1','unknown',1.5,1.0,0.0,'<b>unknown</b>']


def query_text():
    tree = ast.parse(pathlib.Path(sys.modules[get_calllog.__module__].__file__).read_text(encoding='utf-8'))
    return next(n.args[0].value for n in ast.walk(tree) if isinstance(n, ast.Call) and
                isinstance(n.func, ast.Attribute) and n.func.attr=='execute')


def make_database(root):
    path = pathlib.Path(root) / 'data/data/com.android.providers.contacts/databases/calllog.db'
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute('CREATE TABLE calls(date,phone_account_address,number,type,duration,'
                'geocoded_location,countryiso,_data,mime_type,transcription,deleted)')
    rows = [(1700000000123, None, '+15551234567', value, 12, None, 'US', None, None, None, 0)
            for value in TYPES]
    rows.extend([rows[0], (None, 'account', 'partner', None, 0, 'place', None, 'data', 'mime', 'text', 1),
                 (0, '', '', 0, 0, '', '', '', '', '', 0)])
    con.executemany('INSERT INTO calls VALUES(?,?,?,?,?,?,?,?,?,?,?)', rows)
    con.commit()
    assert con.execute('PRAGMA quick_check').fetchone()[0]=='ok'
    con.close()
    return path, rows


class CalllogRawTypeTest(unittest.TestCase):
    def test_native_types_case_mapping_icons_duplicates_and_old_cells(self):
        with tempfile.TemporaryDirectory() as root:
            path, inputs = make_database(root)
            context = SimpleNamespace(get_files_found=lambda:[str(path)],
                                      get_relative_path=lambda p:str(pathlib.Path(p).relative_to(root)))
            headers, rows, source = get_calllog.__wrapped__(context)
            con = sqlite3.connect(path)
            selected = con.execute(query_text()).fetchall()
            con.close()
            self.assertEqual(len(rows),len(inputs))
            self.assertEqual(source,str(path))
            self.assertEqual(headers[0],('Call Date','datetime'))
            self.assertEqual(headers[3:5],('Raw Call Type (as stored)','Type'))
            self.assertNotIn('Source File',headers)
            self.assertEqual(__artifacts_v2__['get_calllog']['html_columns'],['Type'])
            for actual, sqlrow, original in zip(rows,selected,inputs):
                self.assertEqual((type(actual[3]),actual[3]),(type(original[3]),original[3]))
                date = datetime.datetime.fromtimestamp(int(sqlrow[0])/1000,datetime.timezone.utc) if sqlrow[0] else ''
                old = (date,sqlrow[1],sqlrow[2],sqlrow[3]+CALL_TYPE_ICONS.get(sqlrow[3],''),
                       str(sqlrow[4]),sqlrow[5],sqlrow[6],sqlrow[7],sqlrow[8],sqlrow[9],str(sqlrow[10]))
                self.assertEqual(actual[:3]+actual[4:],old)
            self.assertEqual(rows[0],rows[len(TYPES)])
            self.assertEqual(rows[11][4],'Unknown')  # Text '1' stays subject to existing SQL comparison.
            self.assertEqual(rows[14][4],'Incoming'+CALL_TYPE_ICONS['Incoming'])  # Real 1.0.
            self.assertEqual(rows[16][3],'<b>unknown</b>')

    def test_existing_alias_selection_and_independent_source_rows(self):
        with tempfile.TemporaryDirectory() as root:
            main, inputs = make_database(root)
            paths = [main]
            for user in [0,10]:
                target = pathlib.Path(root) / ('data/user/' + str(user)) / 'com.android.providers.contacts/databases/calllog.db'
                target.parent.mkdir(parents=True)
                shutil.copy2(main,target)
                paths.append(target)
            context = SimpleNamespace(get_files_found=lambda:list(map(str,paths)),
                                      get_relative_path=lambda p:str(pathlib.Path(p).relative_to(root)))
            headers, rows, sources = get_calllog.__wrapped__(context)
            self.assertEqual(len(rows),len(inputs)*2)
            self.assertEqual(rows[:len(inputs)],rows[len(inputs):])
            self.assertEqual(sources.splitlines(),list(map(str,[main,paths[-1]])))
            self.assertNotIn('Source File',headers)
