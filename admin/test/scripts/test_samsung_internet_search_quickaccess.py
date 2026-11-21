"""Samsung Internet search history and quick access read their own tables.

The URLs, titles and terms here are synthetic, not taken from any image.
"""
from pathlib import Path
import sqlite3
import tempfile
import unittest
from types import SimpleNamespace
from scripts.artifacts import samsungInternet


def _context(root, files):
    return SimpleNamespace(
        get_files_found=lambda: [str(p) for p in files],
        get_relative_path=lambda p: str(Path(p).relative_to(root)),
    )


class TestSamsungInternetSearchQuickAccess(unittest.TestCase):
    def _search_db(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(path)
        con.execute('CREATE TABLE `history` (`_ID` INTEGER PRIMARY KEY AUTOINCREMENT, '
                    '`KEYWORD` TEXT NOT NULL, `DATETIME` TEXT NOT NULL)')
        con.executemany('INSERT INTO history (KEYWORD, DATETIME) VALUES (?,?)', [
            ('second term', '2021-01-01 09:00:05'),
            ('first term', '2021-01-01 08:00:00'),
        ])
        con.commit()
        con.close()

    def _quick_db(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(path)
        con.execute('CREATE TABLE `quickaccess_item` (`id` INTEGER PRIMARY KEY, `title` TEXT, '
                    '`url` TEXT, `position` INTEGER, `touchIcon` BLOB, `touchIconUrl` TEXT, '
                    '`dominant` INTEGER, `type` INTEGER, `itemId` INTEGER, `titleState` INTEGER, '
                    '`deviceName` TEXT, `deviceId` TEXT, `dirty` INTEGER, `deleted` INTEGER, '
                    '`accountName` TEXT, `accountType` TEXT, `sync1` TEXT)')
        con.executemany(
            'INSERT INTO quickaccess_item (id,title,url,position,type,deviceName,deviceId,dirty,'
            'deleted,accountName,accountType) VALUES (?,?,?,?,?,?,?,?,?,?,?)', [
                (1, 'Default', 'https://default.example/', 1, 1, 'Dev', 'DID', 1, 0, 'a@x', 'google'),
                (2, 'Added', 'https://added.example/', 0, 0, 'Dev', 'DID', 1, 0, 'a@x', 'google'),
            ])
        con.commit()
        con.close()

    def test_search_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root / 'data/data/com.sec.android.app.sbrowser/databases/SearchHistory.db'
            self._search_db(db)
            headers, rows, sources = samsungInternet.samsung_internet_search_history.__wrapped__(
                _context(root, [db]))
            self.assertEqual(headers[0], 'DATETIME (as stored)')
            self.assertEqual(headers[-1], 'Android User')
            self.assertEqual(len(rows), 2)
            # Sorted by DATETIME ascending, so the 08:00 row comes first.
            self.assertEqual([r[0] for r in rows], ['2021-01-01 08:00:00', '2021-01-01 09:00:05'])
            self.assertEqual([r[1] for r in rows], ['first term', 'second term'])
            self.assertEqual([r[3] for r in rows], ['0', '0'])      # Android User
            self.assertEqual(sources, str(db))

    def test_quick_access(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root / 'data/data/com.sec.android.app.sbrowser/databases/quickaccess.db'
            self._quick_db(db)
            headers, rows, _ = samsungInternet.samsung_internet_quick_access.__wrapped__(
                _context(root, [db]))
            self.assertEqual(len(headers), 11)
            self.assertEqual(headers[-1], 'Android User')
            self.assertEqual(len(rows), 2)
            # Sorted by position, so the position-0 user-added row comes first.
            self.assertEqual([r[0] for r in rows], ['Added', 'Default'])
            self.assertEqual([r[1] for r in rows], ['https://added.example/', 'https://default.example/'])
            self.assertEqual([r[3] for r in rows], [0, 1])          # Type
            self.assertEqual([r[4] for r in rows], [0, 0])          # Deleted
            self.assertEqual([r[8] for r in rows], ['a@x', 'a@x'])  # Account Name
            self.assertEqual([r[10] for r in rows], ['0', '0'])     # Android User

    def test_android_user_from_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root / 'data/user/150/com.sec.android.app.sbrowser/databases/SearchHistory.db'
            self._search_db(db)
            _headers, rows, _ = samsungInternet.samsung_internet_search_history.__wrapped__(
                _context(root, [db]))
            self.assertEqual([r[3] for r in rows], ['150', '150'])

    def test_missing_table_yields_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root / 'data/data/com.sec.android.app.sbrowser/databases/SearchHistory.db'
            db.parent.mkdir(parents=True, exist_ok=True)
            con = sqlite3.connect(db)
            con.execute('CREATE TABLE android_metadata (locale TEXT)')  # no history table
            con.commit()
            con.close()
            _headers, rows, sources = samsungInternet.samsung_internet_search_history.__wrapped__(
                _context(root, [db]))
            self.assertEqual(rows, [])
            self.assertEqual(sources, str(db))      # the file is still named as read


if __name__ == '__main__':
    unittest.main()
