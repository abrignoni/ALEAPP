"""Raw moments retain source evidence without guessed actions or units."""
import datetime
import pathlib
import sqlite3
import tempfile
import unittest
from types import SimpleNamespace
from scripts.artifacts.NikeAMoments import get_nike_activMoments

MOMENTS = [('lap', '1'), ('split_km', '1'), ('halt', 'pause'),
           ('halt', 'resume'), ('split_mile', '1'), ('gps_signal', 'lost'),
           ('gps_signal', 'found'), ('unknown', -1), (None, None), ('', ''),
           ('lap', '1')]

def create_moment_fixture(root, empty=False):
    main = pathlib.Path(root) / 'data/data/com.nike.plusgps/databases/com.nike.nrc.room.database'
    main.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(main)
    con.execute('CREATE TABLE activity_moment(as2_m_activity_id, as2_m_timestamp_utc_ms, as2_m_type, as2_m_value)')
    if not empty:
        for index, (kind, value) in enumerate(MOMENTS):
            stamp = None if index == 8 else 0 if index == 9 else 1700000000000
            con.execute('INSERT INTO activity_moment VALUES (?, ?, ?, ?)', ('activity', stamp, kind, value))
    con.commit()
    con.close()
    return main

class NikeMomentRawTest(unittest.TestCase):
    def test_source_fields_unknown_values_repeats_and_order(self):
        with tempfile.TemporaryDirectory() as folder:
            main = create_moment_fixture(folder)
            con = sqlite3.connect(main)
            source_rows = con.execute('SELECT as2_m_activity_id, as2_m_timestamp_utc_ms, as2_m_type, as2_m_value FROM activity_moment ORDER BY as2_m_activity_id, as2_m_timestamp_utc_ms').fetchall()
            con.close()
            expected = [(datetime.datetime.fromtimestamp(stamp / 1000, datetime.timezone.utc) if stamp else '', activity, kind, value)
                        for activity, stamp, kind, value in source_rows]
            headers, rows, source = get_nike_activMoments.__wrapped__(SimpleNamespace(get_files_found=lambda: [main]))
            self.assertEqual(rows, expected)
            self.assertEqual(len(rows), 11)
            self.assertEqual(sum(row[2:] == ('lap', '1') for row in rows), 2)
            self.assertEqual(headers[0], ('Timestamp', 'datetime'))
            self.assertEqual(source, str(main))

    def test_valid_empty_table(self):
        with tempfile.TemporaryDirectory() as folder:
            main = create_moment_fixture(folder, empty=True)
            _, rows, source = get_nike_activMoments.__wrapped__(SimpleNamespace(get_files_found=lambda: [main]))
            self.assertEqual(rows, [])
            self.assertEqual(source, str(main))
