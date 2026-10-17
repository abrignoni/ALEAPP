"""The MediaStore external.db and WhatsApp wa.db patterns stage the database's -wal beside it.

Both are WAL-mode SQLite. A pattern that names the database alone leaves the write-ahead
log in the evidence, so the database is read without the records committed only to the
log. These tests pin that each pattern also matches the -wal.
"""
import fnmatch
import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

# pylint: disable=wrong-import-position
from scripts.artifacts import AIChatbotNovaConversations, AIChatbotNovaMediastore, WhatsAppLogFiles
# pylint: enable=wrong-import-position

MEDIASTORE = (
    "/case/data/data/com.google.android.providers.media.module/databases/external.db",
    "/case/data/data/com.android.providers.media/databases/external.db",
)
WA_DB = "/case/data/data/com.whatsapp/databases/wa.db"


def matches(paths, candidate):
    return any(fnmatch.fnmatchcase(candidate, pattern) for pattern in paths)


class WalSidecarPaths(unittest.TestCase):
    def test_nova_patterns_stage_the_mediastore_log(self):
        for module in (AIChatbotNovaMediastore, AIChatbotNovaConversations):
            for name, spec in module.__artifacts_v2__.items():
                for database in MEDIASTORE:
                    with self.subTest(artifact=name, database=database):
                        self.assertTrue(matches(spec["paths"], database))
                        self.assertTrue(matches(spec["paths"], database + "-wal"))

    def test_whatsapp_log_pattern_stages_the_wa_db_log(self):
        paths = WhatsAppLogFiles.__artifacts_v2__["get_WhatsAppLogFiles"]["paths"]
        self.assertTrue(matches(paths, WA_DB))
        self.assertTrue(matches(paths, WA_DB + "-wal"))


if __name__ == "__main__":
    unittest.main()
