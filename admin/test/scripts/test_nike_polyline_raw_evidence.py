"""Actual SQLite inputs expose decoder assumptions without changing exports."""
import io
import pathlib
import sqlite3
import tempfile
import unittest
import xml.etree.ElementTree as ET
from types import SimpleNamespace
from unittest.mock import patch
import polyline
from PIL import Image
from scripts.artifacts.NikePolyline import get_nike_polyline

POINTS = [(38.5, -120.2), (40.7, -120.95), (43.252, -126.453)]
ENCODED = [polyline.encode(POINTS), polyline.encode([(1.1, 2.2), (1.2, 2.3)], precision=6), '?', '', polyline.encode(POINTS), None]

def create_polyline_fixture(root, empty=False):
    main = pathlib.Path(root) / 'data/data/com.nike.plusgps/databases/com.nike.nrc.room.database'
    main.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(main)
    con.execute('CREATE TABLE activity(as2_sa_id, as2_sa_start_utc_ms, as2_sa_end_utc_ms, as2_sa_active_duration_ms)')
    con.execute('CREATE TABLE activity_polyline(as2_p_activity_id, as2_p_encoded_polyline)')
    if not empty:
        for index, encoded in enumerate(ENCODED):
            identity = 'repeat' if index in (0, 4) else str(index)
            if index != 4:
                con.execute('INSERT INTO activity VALUES (?, ?, ?, ?)', (identity, 1700000000000, 1700000060000, 60000))
            con.execute('INSERT INTO activity_polyline VALUES (?, ?)', (identity, encoded))
    con.commit()
    con.close()
    return main

class NikePolylineEvidenceTest(unittest.TestCase):
    def test_raw_encoding_precision_repeat_and_actual_exports(self):
        with tempfile.TemporaryDirectory() as folder:
            main = create_polyline_fixture(folder)
            exports = []
            def capture(_source, data, name, **_kwargs):
                exports.append((name, data))
                return name
            with patch('scripts.artifacts.NikePolyline.check_in_embedded_media', side_effect=capture):
                headers, rows, source = get_nike_polyline.__wrapped__(SimpleNamespace(get_files_found=lambda: [main]))
            self.assertEqual(len(rows), 5)
            self.assertEqual(source, str(main))
            labels = [h[0] if isinstance(h, tuple) else h for h in headers]
            mapped = [dict(zip(labels, row)) for row in rows]
            self.assertEqual([row['Encoded Polyline'] for row in mapped], ENCODED[:5])
            self.assertTrue(all(row['Decoder Precision Applied'] == 5 for row in mapped))
            self.assertEqual(mapped[0]['First Decoded Latitude'], POINTS[0][0])
            self.assertEqual(mapped[1]['First Decoded Latitude'], 11.0)
            self.assertEqual(mapped[2]['First Decoded Latitude'], '')
            self.assertEqual(mapped[3]['First Decoded Latitude'], '')
            self.assertEqual(rows[0], rows[4])
            self.assertEqual(len(exports), 6)
            for name, data in exports:
                if name.endswith('.png'):
                    image = Image.open(io.BytesIO(data)); image.load()
                    self.assertEqual(image.format, 'PNG')
                else:
                    root = ET.fromstring(data)
                    self.assertIsNotNone(root.find('.//{http://www.opengis.net/kml/2.2}coordinates'))

    def test_empty_source_table(self):
        with tempfile.TemporaryDirectory() as folder:
            main = create_polyline_fixture(folder, empty=True)
            _, rows, source = get_nike_polyline.__wrapped__(SimpleNamespace(get_files_found=lambda: [main]))
            self.assertEqual(rows, [])
            self.assertEqual(source, str(main))
