"""Actual History SQLite and WAL tests for admitted search substrings."""
import hashlib
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

from scripts.artifacts import chrome

SAFE_CASES = [
    ('https://example/search?q=a%2Bb', 'a+b'),
    ('https://example/search?q=a+b', 'a b'),
    ('https://example/search?q=a%20b', 'a b'),
    ('https://example/search?q=%252B', '%2B'),
    ('https://example/search?q=x%26y&other=z', 'x&y'),
    ('https://example/search?q=first&q=second', 'first'),
    ('https://example/search?q=&q=second', ''),
    ('https://example/search?q=firstsearch?q=second', 'first'),
    ('https://example/search?q=value#fragment', 'value#fragment'),
    ('https://example/search?q=value&other=z#fragment', 'value'),
    ('https://example/İ/search?q=caf%C3%A9%2Btea', 'café+tea'),
    ('https://example/#search?q=fragment+text', 'fragment text'),
    ('https://example/search?q=%zz+%2B', '%zz +'),
    ('https://example/search?q=a%2Bb', 'a+b'),
]
UPPER_CASES = [
    ('https://example/SEARCH?Q=a%2Bb', 'a+b'),
    ('https://example/SeArCh?Q=first&q=second', 'first'),
    ('https://example/İ/SEARCH?Q=caf%C3%A9%2Btea', 'café+tea'),
    ('https://example/SEARCH?Q=firstSeArCh?Q=second', 'first'),
]
REJECTED = ['https://example/search?x=1&q=not-first',
            'https://example/search%3Fq%3Dencodedmarker', None, '', 'other',
            'https://example/ſearch?q=unicode-long-s']
TIMESTAMP = 13300000000000000


def write_history(path, cases=None):
    cases = SAFE_CASES if cases is None else cases
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE urls(url,title,visit_count,last_visit_time)')
    entries = [(url, f'title-{i}', str(i) if i % 2 else i, TIMESTAMP + i)
               for i, (url, _) in enumerate(cases)]
    entries += [(url, 'rejected', 0, TIMESTAMP) for url in REJECTED]
    db.executemany('INSERT INTO urls VALUES (?,?,?,?)', entries)
    db.commit()
    db.close()
    return path


class FileContext:
    def __init__(self, root, files):
        self.root = Path(root)
        self.files = files

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


class ChromeSearchDecoding(unittest.TestCase):
    def check_cases(self, cases):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = write_history(root / 'evidence/com.android.chrome/app_chrome/Default/History', cases)
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            headers, rows, source = chrome.get_chromeSearchTerms.__wrapped__(FileContext(root, [str(path)]))
            self.assertEqual(len(headers), 6)
            self.assertEqual([row[1] for row in rows], [expected for _, expected in cases])
            self.assertEqual([row[2] for row in rows], [url for url, _ in cases])
            self.assertEqual([row[4] for row in rows], [str(i) if i % 2 else i for i in range(len(cases))])
            self.assertTrue(all(row[5] == 'Chrome' for row in rows))
            self.assertEqual(source, str(path))
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)
            return rows

    def test_actual_sqlite_safe_admission_and_single_decoding(self):
        rows = self.check_cases(SAFE_CASES)
        self.assertEqual(rows[0][1], rows[-1][1])
        self.assertNotEqual(rows[0][3], rows[-1][3])

    def test_uppercase_admitted_rows_new_only(self):
        # These actual SQLite-admitted URLs are never sent to the known-crashing baseline.
        self.check_cases(UPPER_CASES)

    def test_actual_wal_effective_rows_and_protected_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            live = write_history(root / 'live/History', SAFE_CASES[:1])
            db = sqlite3.connect(live)
            db.execute('pragma journal_mode=WAL')
            db.execute('pragma wal_autocheckpoint=0')
            db.execute('UPDATE urls SET url=? WHERE title=?', (SAFE_CASES[3][0], 'title-0'))
            db.execute('INSERT INTO urls SELECT * FROM urls WHERE title=?', ('title-0',))
            db.commit()
            dest = root / 'evidence/com.android.chrome/app_chrome/Default/History'
            dest.parent.mkdir(parents=True)
            before = {}
            for suffix in ['', '-wal', '-shm']:
                shutil.copy2(str(live) + suffix, str(dest) + suffix)
                file = Path(str(dest) + suffix)
                file.chmod(0o444)
                before[suffix] = hashlib.sha256(file.read_bytes()).hexdigest()
            _, rows, _ = chrome.get_chromeSearchTerms.__wrapped__(FileContext(root, [str(dest)]))
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0], rows[1])
            self.assertEqual(rows[0][1], '%2B')
            for suffix, digest in before.items():
                self.assertEqual(hashlib.sha256(Path(str(dest) + suffix).read_bytes()).hexdigest(), digest)
            db.close()


if __name__ == '__main__':
    unittest.main()
