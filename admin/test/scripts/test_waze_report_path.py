"""Waze favourite, shared place and account rows are checked through the artifact functions, so a
call site that stops using the zero-time or Last Name helper fails here. All values are made up."""
# pylint: disable=protected-access
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import waze

TIME = 1700000000
TIME_UTC = '2023-11-14T22:13:20+00:00'


def _context(folder, files, artifact):
    def source(name):
        return str(files[name]) if name in files else None
    return SimpleNamespace(
        get_source_file_path=source,
        get_seeker=lambda: SimpleNamespace(data_folder=folder),
        get_artifact_name=lambda: artifact,
        get_relative_path=lambda p: str(pathlib.Path(p).relative_to(folder)))


def _rows(headers_and_rows):
    headers, rows = headers_and_rows[0], headers_and_rows[1]
    if isinstance(rows, tuple):
        rows = rows[0]
    names = [h[0] if isinstance(h, tuple) else h for h in headers]
    return [dict(zip(names, row)) for row in rows]


def _user_db(folder):
    path = pathlib.Path(folder) / 'data/data/com.waze/user.db'
    path.parent.mkdir(parents=True)
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE PLACES (id INTEGER, name TEXT, house TEXT, street TEXT, city TEXT, state TEXT, '
               'country TEXT, latitude INTEGER, longitude INTEGER, venue_id TEXT)')
    db.execute('CREATE TABLE FAVORITES (id INTEGER, place_id INTEGER, access_time INTEGER, type INTEGER, '
               'name TEXT, created_time INTEGER, modified_time INTEGER, waypoint_access_time INTEGER, '
               'rank INTEGER, server_id TEXT)')
    db.execute('CREATE TABLE SHARED_PLACES (id INTEGER, place_id INTEGER, share_time INTEGER, name TEXT, '
               'created_time INTEGER, modified_time INTEGER, access_time INTEGER, owner_id TEXT)')
    db.execute("INSERT INTO PLACES VALUES (1, 'P', '1', 'S', 'C', 'ST', 'CO', 1000000, 2000000, 'v')")
    db.execute("INSERT INTO FAVORITES VALUES (1, 1, 0, 1, 'zero', 0, 0, 0, 1, 's')")
    db.execute(f"INSERT INTO FAVORITES VALUES (2, 1, {TIME}, 2, 'dated', {TIME}, {TIME}, {TIME}, 2, 's')")
    db.execute("INSERT INTO SHARED_PLACES VALUES (1, 1, 0, 'zero', 0, 0, 0, 'o')")
    db.execute(f"INSERT INTO SHARED_PLACES VALUES (2, 1, {TIME}, 'dated', {TIME}, {TIME}, {TIME}, 'o')")
    db.commit()
    db.close()
    return path


def _field(number, payload):
    """One length-delimited protobuf field."""
    return bytes([number << 3 | 2, len(payload)]) + payload


def _cached_data(folder, last_name):
    profile = _field(1, b'Ann') + _field(2, last_name)
    path = pathlib.Path(folder) / 'data/data/com.waze/cached_data'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(_field(1, _field(1, profile)))
    return path


class StoredZeroTimes(unittest.TestCase):
    def test_favourites(self):
        with tempfile.TemporaryDirectory() as folder:
            context = _context(folder, {'user.db': _user_db(folder)}, 'waze_favorite_locations')
            rows = _rows(waze.waze_favorite_locations.__wrapped__(context))
        by_name = {r['Name']: r for r in rows}
        columns = ('Last Access', 'Created', 'Modified', 'Last Waypoint Access')
        self.assertEqual([by_name['zero'][c] for c in columns], ['', '', '', ''])
        self.assertEqual([by_name['dated'][c].isoformat() for c in columns], [TIME_UTC] * 4)

    def test_shared_places(self):
        with tempfile.TemporaryDirectory() as folder:
            context = _context(folder, {'user.db': _user_db(folder)}, 'waze_shared_locations')
            rows = _rows(waze.waze_shared_locations.__wrapped__(context))
        by_name = {r['Name']: r for r in rows}
        columns = ('Shared', 'Created', 'Modified', 'Last Access')
        self.assertEqual([by_name['zero'][c] for c in columns], ['', '', '', ''])
        self.assertEqual([by_name['dated'][c].isoformat() for c in columns], [TIME_UTC] * 4)


class AccountLastName(unittest.TestCase):
    def setUp(self):
        waze.WAZE_CACHED_DATA.update(data=None, path=None)

    tearDown = setUp

    def _account(self, last_name):
        with tempfile.TemporaryDirectory() as folder:
            context = _context(folder, {'cached_data': _cached_data(folder, last_name)}, 'waze_account')
            rows = _rows(waze.waze_account.__wrapped__(context))
        self.assertEqual(len(rows), 1)
        return rows[0]

    def test_a_nested_message_gives_a_blank_last_name(self):
        row = self._account(bytes([9 << 3, 7]))
        self.assertEqual((row['First Name'], row['Last Name']), ('Ann', ''))

    def test_a_stored_last_name_is_kept(self):
        row = self._account(b'Doe')
        self.assertEqual((row['First Name'], row['Last Name']), ('Ann', 'Doe'))


if __name__ == '__main__':
    unittest.main()
