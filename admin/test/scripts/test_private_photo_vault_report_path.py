"""Private Photo Vault media and login rows are checked through the artifact functions and, for Login
Records, through the report outputs: timeline, KML and LAVA. All values are made up."""
# pylint: disable=protected-access
import io
import json
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from contextlib import ExitStack, contextmanager, redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import PrivatePhotoVault as ppv
from scripts.context import Context
from scripts import ilapfuncs, lavafuncs

DB = 'data/data/com.enchantedcloud.photovault/databases/ppv.db'
BASE = {'creation_date': "'2024-01-01T00:00:00.000+00:00'", 'bucket_id': "'albums'", 'file_path': "'f'",
        'thumbnail_path': "'t'", 'mime_type': "'image/jpeg'", 'is_favourite': '0', 'is_deleted': '0',
        'encryption_key': "'k'", 'local_iv': "'iv'"}
OPTIONAL = {'image_width': '640', 'image_height': '480', 'view_count': '3',
            'deleted_time': "'2024-01-02T00:00:00.000Z'", 'trashed_date': "'2024-01-03T00:00:00.000Z'",
            'favourite_date': "'2024-01-04T00:00:00.000Z'", 'uploaded_date': "'2024-01-05T00:00:00.000Z'"}
HEADER = {'image_width': 'Image Width', 'image_height': 'Image Height', 'view_count': 'View Count',
          'deleted_time': 'Deleted Time (As Stored)', 'trashed_date': 'Trashed Date (As Stored)',
          'favourite_date': 'Favourite Date (As Stored)', 'uploaded_date': 'Uploaded Date (As Stored)'}


def _media_row(present):
    columns = dict(BASE, **{c: OPTIONAL[c] for c in present})
    with tempfile.TemporaryDirectory() as folder:
        path = pathlib.Path(folder) / DB
        path.parent.mkdir(parents=True)
        db = sqlite3.connect(path)
        db.execute(f'CREATE TABLE MediaFile ({", ".join(columns)})')
        db.execute(f'INSERT INTO MediaFile VALUES ({", ".join(columns.values())})')
        db.commit()
        db.close()
        context = SimpleNamespace(get_files_found=lambda: [str(path)],
                                  get_relative_path=lambda p: str(pathlib.Path(p).relative_to(folder)))
        headers, rows, _source = ppv.private_photo_vault_media.__wrapped__(context)
    names = [h[0] if isinstance(h, tuple) else h for h in headers]
    assert len(rows) == 1
    return dict(zip(names, rows[0]))


def _stored(column):
    value = OPTIONAL[column]
    return value.strip("'") if value.startswith("'") else int(value)


class MediaOptionalColumns(unittest.TestCase):
    def test_every_optional_column_present_keeps_every_value(self):
        row = _media_row(OPTIONAL)
        for column, header in HEADER.items():
            with self.subTest(column):
                self.assertEqual(row[header], _stored(column))

    def test_only_the_missing_columns_are_blank(self):
        present = ('image_width', 'view_count', 'trashed_date')
        row = _media_row(present)
        for column, header in HEADER.items():
            with self.subTest(column):
                self.assertEqual(row[header], _stored(column) if column in present else None)
        self.assertEqual((row['MIME Type'], row['File Path']), ('image/jpeg', 'f'))


@contextmanager
def _isolated_output():
    state = {name: value for name, value in vars(Context).items()
             if name.startswith('_') and not name.startswith('__') and not isinstance(value, staticmethod)}
    with ExitStack() as stack:
        stack.enter_context(patch.multiple(Context, **state))
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


class LoginRecordOutputs(unittest.TestCase):
    """One dated row with coordinates, one row with no date, and one dated row on latitude 0."""

    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        root = pathlib.Path(cls.temporary.name) / 'evidence'
        path = root / DB
        path.parent.mkdir(parents=True)
        db = sqlite3.connect(path)
        db.execute('CREATE TABLE LoginRecord (uid TEXT, orig_file_path TEXT, date TEXT, type INTEGER, '
                   'latitude REAL, longitude REAL)')
        db.executemany('INSERT INTO LoginRecord VALUES (?, ?, ?, ?, ?, ?)', [
            ('u1', '/p/1.jpg', '2024-01-02T03:04:05.000Z', 1, 40.5, -73.25),
            ('u2', '/p/2.jpg', None, 2, 10.0, 20.0),
            ('u3', '/p/3.jpg', '2024-01-03T00:00:00.000Z', 1, 0.0, 5.0),
        ])
        db.commit()
        db.close()
        with _isolated_output():
            Context.set_data_folder(str(root))
            params = ilapfuncs.OutputParameters(str(pathlib.Path(cls.temporary.name) / 'report'), 'ppv-login')
            Context.set_output_params(params)
            output = pathlib.Path(params.output_folder_base)
            report = output / '_HTML' / 'Device Activity'
            report.mkdir(parents=True)
            lavafuncs.initialize_lava(str(root), str(output), 'fs')
            vars(ppv)['private_photo_vault_login_records']([str(path)], str(report), None, False)
            cls.lava = lavafuncs.lava_db.execute(
                'SELECT uid, date, date_as_stored, latitude, longitude FROM private_photo_vault_login_records '
                'ORDER BY uid').fetchall()
        with sqlite3.connect(output / '_Timeline' / 'tl.db') as tl:
            cls.timeline = {json.loads(values)['UID']: (key, json.loads(values))
                            for key, _activity, values in tl.execute('SELECT key, activity, datalist FROM data')}
        kml_folder = output / '_KML Exports'
        with sqlite3.connect(kml_folder / '_latlong.db') as kml:
            cls.latlong = (kml.execute('SELECT timestamp, latitude, longitude FROM data').fetchall())
        cls.kml = next(kml_folder.glob('*.kml')).read_text(encoding='utf-8')

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_lava_keeps_the_stored_dates_and_coordinates(self):
        self.assertEqual(self.lava, [
            ('u1', 1704164645, '2024-01-02T03:04:05.000Z', 40.5, -73.25),
            ('u2', None, None, 10, 20),
            ('u3', 1704240000, '2024-01-03T00:00:00.000Z', 0, 5),
        ])

    def test_the_timeline_has_every_row_and_a_blank_date_has_no_time(self):
        self.assertEqual(set(self.timeline), {'u1', 'u2', 'u3'})
        self.assertEqual(self.timeline['u1'][0], '2024-01-02 03:04:05+00:00')
        self.assertEqual(self.timeline['u1'][1]['Date (as stored)'], '2024-01-02T03:04:05.000Z')
        self.assertEqual(self.timeline['u2'][0], '')
        self.assertEqual(self.timeline['u2'][1]['Date (as stored)'], '')

    def test_kml_has_the_rows_with_two_nonzero_coordinates(self):
        self.assertEqual({(lat, lon) for _time, lat, lon in self.latlong}, {('10.0', '20.0'), ('40.5', '-73.25')})
        self.assertIn('N/A', {time for time, _lat, _lon in self.latlong})
        self.assertEqual(self.kml.count('<Placemark'), 2)
        self.assertIn('<name>N/A</name>', self.kml)
        self.assertIn('<name>2024-01-02 03:04:05+00:00</name>', self.kml)
        self.assertIn('-73.25,40.5', self.kml)


if __name__ == '__main__':
    unittest.main()
