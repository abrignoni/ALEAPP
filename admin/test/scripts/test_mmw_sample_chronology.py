"""Timestamp ordering preserves all samples without rowid/schema assumptions."""
import io
import json
import pathlib
import sqlite3
import tempfile
import unittest
import xml.etree.ElementTree as ET
from types import SimpleNamespace
from unittest.mock import patch
from PIL import Image
from scripts.artifacts.MMWActivities import get_mmw_activities, _timestamp, _typed_value

SAFE = [(1700000060000, 500, 4, 38.5, -120.2),
        (1700000000000, 100, 2, 40.7, -120.95),
        (1700000030000, None, None, 43.252, -126.453),
        (1700000030000, 50, 3, 43.252, -126.453),
        (1700000030000, 50, 3, 43.252, -126.453)]
BOUNDARIES = [('10', 10, 1, 1.1, 2.2), ('2', 2, 1, 1.2, 2.3),
              (0, 0, 1, 1.3, 2.4), (-1000, -1, 1, 1.4, 2.5),
              (None, None, 1, 1.5, 2.6), ('', 5, 1, 1.6, 2.7),
              ('invalid', 8, 1, 1.7, 2.8), ('9' * 400, 9, 1, 1.8, 2.9),
              (float('inf'), 12, 1, 1.9, 3.0), (b'undated', 13, 1, 2.0, 3.1)]

def create_fixture(root, groups=None, reverse=False, without_rowid=False):
    main = pathlib.Path(root) / 'data/data/com.mapmywalk.android2/databases/workout.db'
    main.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(main)
    ending = ', PRIMARY KEY(localId, sequence)) WITHOUT ROWID' if without_rowid else ')'
    con.execute('CREATE TABLE timeSeries(localId, sequence, timestamp, distance, speed, latitude, longitude' + ending)
    for identity, points in (groups or {}).items():
        ordered = list(reversed(points)) if reverse else points
        for sequence, point in enumerate(ordered):
            con.execute('INSERT INTO timeSeries VALUES(?,?,?,?,?,?,?)', (identity, sequence, *point))
    con.commit()
    con.close()
    return main

def run_parser(main):
    exports = {}
    def capture(_source, data, name, **_kwargs):
        exports[name] = data
        return name
    with patch('scripts.artifacts.MMWActivities.check_in_embedded_media', side_effect=capture):
        headers, rows, source = get_mmw_activities.__wrapped__(SimpleNamespace(get_files_found=lambda: [main]))
    labels = [header[0] if isinstance(header, tuple) else header for header in headers]
    return [dict(zip(labels, row)) for row in rows], exports, source

class MMWChronologyTest(unittest.TestCase):
    def test_shuffled_ties_repeats_without_rowid_and_route_order(self):
        with tempfile.TemporaryDirectory() as folder:
            first = create_fixture(pathlib.Path(folder) / 'first', {'A': SAFE})
            second = create_fixture(pathlib.Path(folder) / 'second', {'A': SAFE}, reverse=True, without_rowid=True)
            left, media_left, _ = run_parser(first)
            right, media_right, _ = run_parser(second)
            self.assertEqual({k: v for k, v in left[0].items() if k != 'Raw Samples JSON'},
                             {k: v for k, v in right[0].items() if k != 'Raw Samples JSON'})
            self.assertEqual(media_left['A_route.png'], media_right['A_route.png'])
            namespace = './/{http://www.opengis.net/kml/2.2}coordinates'
            self.assertEqual(ET.fromstring(media_left['A_route.kml']).find(namespace).text,
                             ET.fromstring(media_right['A_route.kml']).find(namespace).text)
            self.assertEqual(left[0]['Last Ordered Distance (as stored)'], 500)
            self.assertEqual(left[0]['Duration (min)'], 1.0)
            inventory = json.loads(left[0]['Raw Samples JSON'])
            self.assertEqual(len(inventory), 5)
            self.assertEqual(sorted(item['query_position'] for item in inventory), list(range(5)))
            self.assertEqual(sum(item['fields']['distance'] == {'type': 'integer', 'value': 50} for item in inventory), 2)
            kml = ET.fromstring(media_left['A_route.kml'])
            coordinates = kml.find('.//{http://www.opengis.net/kml/2.2}coordinates').text.strip().split()
            self.assertEqual([float(value) for value in coordinates[0].split(',')[:2]], [-120.95, 40.7])
            image = Image.open(io.BytesIO(media_left['A_route.png'])); image.load()
            self.assertEqual(image.format, 'PNG')

    def test_timestamp_boundaries_raw_types_and_undated_group(self):
        with tempfile.TemporaryDirectory() as folder:
            main = create_fixture(folder, {'A': BOUNDARIES, 'B': BOUNDARIES[4:]})
            rows, _, source = run_parser(main)
            self.assertEqual(source, str(main))
            inventory = json.loads(rows[0]['Raw Samples JSON'])
            self.assertEqual([item['interpreted_timestamp_ms'] for item in inventory[:4]], [-1000, 0, 2, 10])
            self.assertEqual(len(inventory), len(BOUNDARIES))
            self.assertTrue(all(item['timestamp_status'] != 'eligible' for item in inventory[4:]))
            self.assertEqual(rows[1]['Start Time'], '')
            self.assertEqual(rows[1]['End Time'], '')
            self.assertEqual(rows[1]['Duration (min)'], '')
            self.assertIn({'type': 'blob', 'base64': 'dW5kYXRlZA=='}, [item['fields']['timestamp'] for item in inventory])
            self.assertEqual(_typed_value(float('-inf')), {'type': 'real', 'hex': '-inf'})
            self.assertEqual(_timestamp(1.9)[0], 1)
            self.assertEqual(_timestamp('1.9')[2], 'nonnumeric')

    def test_valid_empty_table(self):
        with tempfile.TemporaryDirectory() as folder:
            main = create_fixture(folder)
            rows, exports, _ = run_parser(main)
            self.assertEqual(rows, [])
            self.assertEqual(exports, {})
