"""notification_log.db log table, version 7 and version 5 column sets; values are made up."""
import fnmatch
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

# pylint: disable=wrong-import-position
from scripts.artifacts import notificationLog

MS = 1767225600000  # 2026-01-01 00:00:00 UTC
V7 = ('_id INTEGER PRIMARY KEY AUTOINCREMENT, event_user_id INT, event_type INT, event_time_ms INT, '
      'key TEXT, pkg TEXT, nid INT, tag TEXT, when_ms INT, defaults INT, flags INT, '
      'importance_request INT, importance_final INT, noisy INT, muted INT, demoted INT, category TEXT, '
      'action_count INT, posttime_ms INT, airtime_ms INT, first_expansion_time_ms INT, '
      'expansion_airtime_ms INT, expansion_count INT')


class Context:
    def __init__(self, root):
        self.root = root

    def get_files_found(self):
        return [str(p) for p in sorted(self.root.rglob('*')) if p.is_file()]

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root)).replace('\\', '/')


def make(path, with_undecorated):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute(f"CREATE TABLE log ({V7}{', undecorated INT' if with_undecorated else ''})")
    db.execute("INSERT INTO log (event_user_id, event_type, event_time_ms, key, pkg, nid, when_ms, "
               "importance_request, importance_final, noisy, muted, demoted) "
               "VALUES (0, 1, ?, 'k', 'org.example.app', 7, ?, 4, 3, 1, 1, 1)", (MS, MS))
    db.execute("INSERT INTO log (event_user_id, event_type, event_time_ms, key, pkg, posttime_ms) "
               "VALUES (0, 3, ?, 'k', 'org.example.app', 5000)", (MS + 5000,))
    db.execute("INSERT INTO log (event_user_id, event_type, event_time_ms, pkg) VALUES (0, 9, ?, 'x')",
               (MS + 6000,))
    db.commit()
    db.close()


class NotificationLogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'evidence'

    def tearDown(self):
        self.temp.cleanup()

    def run_artifact(self):
        context = Context(self.root)
        for path in context.get_files_found():
            self.assertTrue(any(fnmatch.fnmatch('root/' + context.get_relative_path(path), p)
                                for p in notificationLog.__artifacts_v2__['notification_log_db']['paths']))
        headers, rows, _ = notificationLog.notification_log_db.__wrapped__(context)
        names = [h[0] if isinstance(h, tuple) else h for h in headers]
        return [dict(zip(names, r)) for r in rows]

    def test_version7_events_are_named_and_timed(self):
        make(self.root / 'data/system/notification_log.db', True)
        rows = self.run_artifact()
        self.assertEqual([r['Event Type'] for r in rows], ['POST', 'REMOVE', 9])
        self.assertEqual(rows[0]['Event Time'], datetime(2026, 1, 1, tzinfo=timezone.utc))
        self.assertEqual((rows[0]['Muted'], rows[0]['Demoted'], rows[1]['Time Since Post (ms)']), (1, 1, 5000))

    def test_version5_database_without_undecorated_is_read(self):
        make(self.root / 'data/system/notification_log.db', False)
        rows = self.run_artifact()
        self.assertEqual((len(rows), rows[0]['Undecorated']), (3, ''))


if __name__ == '__main__':
    unittest.main()
