"""Synthetic odlh-storage.db segments: activity columns and path points read from the wire format."""
import sqlite3
import struct
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.artifacts import googleOdlh as module


class Context:
    def __init__(self, root, files):
        self.root = Path(root)
        self.files = list(map(str, files))

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


def varint(value):
    out = b''
    while True:
        byte = value & 0x7F
        value >>= 7
        out += bytes([byte | (0x80 if value else 0)])
        if not value:
            return out


def key(number, wire_type):
    return varint(number << 3 | wire_type)


def message(number, body):
    return key(number, 2) + varint(len(body)) + body


def fixed32(number, value, fmt='<i'):
    return key(number, 5) + struct.pack(fmt, value)


def e7_pair(number, lat, lon):
    return message(number, fixed32(1, round(lat * 1e7)) + fixed32(2, round(lon * 1e7)))


def times(start, end):
    return message(1, key(1, 0) + varint(start)) + message(2, key(1, 0) + varint(end))


START = 1771437600
VISIT = times(START, START + 600) + message(3, message(1, message(4, e7_pair(5, 42.5, -73.75))))
ACTIVITY = times(START + 600, START + 1500) + message(3, message(2,
    e7_pair(1, 42.5, -73.75) + e7_pair(2, 42.6, -73.85) + fixed32(3, 12345.5, '<f')
    + fixed32(4, 0.75, '<f') + message(6, key(1, 0) + varint(29) + fixed32(2, 0.5, '<f'))))


def path_segment(lats, lons, offsets):
    body = (message(4, b''.join(struct.pack('<i', round(v * 1e7)) for v in lats))
            + message(5, b''.join(struct.pack('<i', round(v * 1e7)) for v in lons)))
    if offsets is not None:
        body += message(6, b''.join(varint(v) for v in offsets))
    return times(START + 1500, START + 3300) + message(3, message(3, body))


PATH = path_segment([42.6, 42.61, -33.5], [-73.85, -73.86, 151.25], [0, 7, 30])
# 0x0A 0x02 0x08 0x01 reads as a valid nested message (field 1 holding field 1 = 1), so a
# type-guessing decoder can take these packed latitudes for a message; the wire reader must not
PATH_LOOKS_LIKE_MESSAGE = times(START, START + 60) + message(3, message(3,
    message(4, bytes([0x0A, 0x02, 0x08, 0x01])) + message(5, struct.pack('<i', -737500000))
    + message(6, varint(1))))
PATH_NO_OFFSETS = path_segment([1.0], [2.0], None)


class OdlhActivitiesPathsTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        root = Path(self.temp_dir.name)
        db_path = root / 'data/data/com.google.android.gms/databases/odlh-storage.db'
        db_path.parent.mkdir(parents=True)
        db = sqlite3.connect(db_path)
        try:
            with db:
                db.execute('CREATE TABLE semantic_segment_table (_id INTEGER PRIMARY KEY, segment_id TEXT, '
                           'semantic_segment BLOB, obfuscated_gaia_id TEXT, shown_in_timeline INTEGER, '
                           'is_finalized INTEGER, start_timestamp_seconds INTEGER, '
                           'end_timestamp_seconds INTEGER, segment_type INTEGER, hierarchy_level INTEGER)')
                rows = [('visit', VISIT, START, START + 600, 1), ('activity', ACTIVITY, START + 600, START + 1500, 2),
                        ('path', PATH, START + 1500, START + 3300, 3),
                        ('tricky', PATH_LOOKS_LIKE_MESSAGE, START, START + 60, 3),
                        ('no-offsets', PATH_NO_OFFSETS, START + 1500, START + 3300, 3)]
                for sid, blob, start, end, kind in rows:
                    db.execute('INSERT INTO semantic_segment_table (segment_id, semantic_segment, obfuscated_gaia_id, '
                               'start_timestamp_seconds, end_timestamp_seconds, segment_type) VALUES (?,?,?,?,?,?)',
                               (sid, blob, 'gaia', start, end, kind))
        finally:
            db.close()                                 # Windows cannot delete an open file
        self.context = Context(root, [db_path])

    def segments(self):
        headers, rows, _ = module.gmsOdlhSemanticSegments.__wrapped__(self.context)
        names = [h[0] if isinstance(h, tuple) else h for h in headers]
        return {row[names.index('Segment ID')]: dict(zip(names, row)) for row in rows}

    def test_activity_columns(self):
        activity = self.segments()['activity']
        self.assertEqual((activity['Latitude'], activity['Longitude']), ('', ''))
        self.assertAlmostEqual(activity['Activity Start Latitude'], 42.5)
        self.assertAlmostEqual(activity['Activity Start Longitude'], -73.75)
        self.assertAlmostEqual(activity['Activity End Latitude'], 42.6)
        self.assertAlmostEqual(activity['Activity End Longitude'], -73.85)
        self.assertEqual(activity['Activity Distance (as stored)'], 12345.5)
        self.assertEqual(activity['Activity Type (as stored)'], 29)
        self.assertEqual(activity['Activity Type Probability (as stored)'], 0.5)
        self.assertEqual(activity['Activity Probability (as stored)'], 0.75)

    def test_visit_and_path_rows(self):
        segments = self.segments()
        self.assertAlmostEqual(segments['visit']['Latitude'], 42.5)
        self.assertEqual(segments['visit']['Activity Start Latitude'], '')
        self.assertEqual(segments['visit']['Path Point Count'], '')
        self.assertEqual(segments['path']['Path Point Count'], 3)
        self.assertEqual(segments['tricky']['Path Point Count'], 1)

    def test_path_points(self):
        headers, rows, _ = module.gmsOdlhPathPoints.__wrapped__(self.context)
        names = [h[0] if isinstance(h, tuple) else h for h in headers]
        points = [dict(zip(names, row)) for row in rows]
        by_segment = {}
        for p in points:
            by_segment.setdefault(p['Segment ID'], []).append(p)
        path_points = by_segment['path']
        self.assertEqual([p['Point Number'] for p in path_points], [1, 2, 3])
        self.assertEqual([p['Minute Offset (as stored)'] for p in path_points], [0, 7, 30])
        self.assertEqual([p['Point Time'] for p in path_points],
                         [datetime.fromtimestamp(START + 1500 + m * 60, tz=timezone.utc) for m in (0, 7, 30)])
        self.assertAlmostEqual(path_points[2]['Latitude'], -33.5)        # negative values kept
        self.assertAlmostEqual(path_points[2]['Longitude'], 151.25)

    def test_packed_bytes_that_parse_as_a_message(self):
        _, rows, _ = module.gmsOdlhPathPoints.__wrapped__(self.context)
        tricky = [row for row in rows if row[8] == 'tricky']
        self.assertEqual(len(tricky), 1)
        self.assertAlmostEqual(tricky[0][3], struct.unpack('<i', bytes([0x0A, 0x02, 0x08, 0x01]))[0] / 1e7)
        self.assertAlmostEqual(tricky[0][4], -73.75)
        self.assertEqual(tricky[0][5], 1)

    def test_point_without_offset_has_no_time(self):
        _, rows, _ = module.gmsOdlhPathPoints.__wrapped__(self.context)
        no_offsets = [row for row in rows if row[8] == 'no-offsets']
        self.assertEqual(len(no_offsets), 1)
        self.assertEqual(no_offsets[0][0], '')
        self.assertEqual(no_offsets[0][5], '')


if __name__ == '__main__':
    unittest.main()
