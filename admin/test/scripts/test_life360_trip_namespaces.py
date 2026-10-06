"""Life360 trip inputs retain namespace occurrences and actual row sources."""
import datetime
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.artifacts.life360DriverBehavior import get_TripEvents, get_TripWaypoints  # pylint: disable=wrong-import-position

PACKAGE = 'com.life360.android.safetymapd'
TAIL = PACKAGE + '/files/DriverBehavior/trips/'


def trip(value='same', waypoints=True):
    event = dict(timestamp=1700000000, eventType=value, location=dict(lat=0, lon=-1),
                 speed=0, topSpeed=2, averageSpeed=None, distance=12, tripId='repeated')
    if waypoints:
        event['waypoints'] = [dict(lat=0, lon=-1, accuracy=0)] * 2
    return {'events': [event, event]}


def write_json(root, name, value, pretty=False):
    path = Path(root) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2 if pretty else None), encoding='utf-8')
    return path


def make_files(root):
    names = ['data/user/10/' + TAIL + 'trip.json', 'data/' + TAIL + 'trip.json',
             'data/data/' + TAIL + 'trip.json', 'data/user/0/' + TAIL + 'trip.json',
             'data_mirror/data_ce/null/0/' + TAIL + 'trip.json',
             'data/user_de/0/' + TAIL + 'trip.json',
             'data_mirror/data_de/null/10/' + TAIL + 'nested/trip.json']
    paths = []
    for i, name in enumerate(names):
        paths.append(write_json(root, name, trip('different' if i == 4 else 'same'), pretty=i == 3))
    return paths


def parse(wrapper, paths, root, windows=False):
    return wrapper.__wrapped__(SimpleNamespace(
        get_files_found=lambda: list(map(str, paths)),
        get_relative_path=lambda p: str(Path(p).relative_to(root)).replace('/', '\\')
        if windows else str(Path(p).relative_to(root))))


class Life360TripNamespacesTest(unittest.TestCase):
    def test_all_namespace_occurrences_equal_and_conflicting_aliases(self):
        with tempfile.TemporaryDirectory() as root:
            paths = make_files(root)
            self.assertEqual(paths[1].read_bytes(), paths[2].read_bytes())
            self.assertNotEqual(paths[2].read_bytes(), paths[3].read_bytes())
            self.assertEqual(json.loads(paths[2].read_text(encoding='utf-8')),
                             json.loads(paths[3].read_text(encoding='utf-8')))
            selected = paths + [paths[0]]
            for wrapper, width, per_file in [(get_TripEvents, 12, 2), (get_TripWaypoints, 4, 4)]:
                headers, rows, sources = parse(wrapper, selected, root)
                self.assertEqual(len(headers), width + 1)
                self.assertEqual(headers[-1], 'Source File')
                self.assertEqual(len(rows), len(selected) * per_file)
                self.assertEqual(sources.splitlines(), list(map(str, paths)))
                self.assertEqual([r[-1] for r in rows],
                                 [str(p.relative_to(root)) for p in selected for _ in range(per_file)])
                if wrapper is get_TripEvents:
                    self.assertEqual(rows[0][:-1], (datetime.datetime.fromtimestamp(
                        1700000000, datetime.timezone.utc), 'same', 0, -1, 0, 0.0, 2, 4.47,
                        None, '', 12, 'repeated'))
                    self.assertEqual(rows[8][1], 'different')
                else:
                    self.assertTrue(all(r[:-1] == (0, -1, 0, 'repeated') for r in rows))

    def test_per_wrapper_contributors_empty_files_and_single_source(self):
        with tempfile.TemporaryDirectory() as root:
            first = write_json(root, 'data/' + TAIL + 'A.json', trip())
            second = write_json(root, 'data/user/10/' + TAIL + 'B.json', trip(waypoints=False))
            empty = write_json(root, 'data/user/0/' + TAIL + 'empty.json', {'events': []})
            missing = write_json(root, 'data/user/0/' + TAIL + 'missing.json', {})
            headers, rows, sources = parse(get_TripEvents, [first, second, empty, missing], root)
            self.assertEqual(len(headers), 13)
            self.assertEqual(len(rows), 4)
            self.assertEqual(sources.splitlines(), [str(first), str(second)])
            headers, rows, sources = parse(get_TripWaypoints, [first, second, empty, missing], root)
            self.assertEqual(len(headers), 4)
            self.assertEqual(len(rows), 4)
            self.assertEqual(sources, str(first))
            for wrapper, width in [(get_TripEvents, 12), (get_TripWaypoints, 4)]:
                headers, rows, sources = parse(wrapper, [first, first], root, windows=True)
                self.assertEqual(len(headers), width)
                self.assertEqual(sources, str(first))
                self.assertEqual(len(rows), 4 if width == 12 else 8)
                headers, rows, sources = parse(wrapper, [empty, missing], root)
                self.assertEqual((len(headers), rows, sources), (width, [], ''))

    def test_package_target_namespace_and_harness_boundaries(self):
        with tempfile.TemporaryDirectory() as root:
            invalid = ['data/user/alice/' + TAIL + 'bad.json',
                       'data/user/0/' + TAIL.replace(PACKAGE, PACKAGE + '.evil') + 'bad.json',
                       'data/' + TAIL.replace('/trips/', '/trips2/') + 'bad.json',
                       'unrelated/' + TAIL + 'bad.json',
                       'data/' + TAIL + 'bad.JSON']
            paths = [write_json(root, name, trip()) for name in invalid]
            for wrapper, width in [(get_TripEvents, 12), (get_TripWaypoints, 4)]:
                self.assertEqual(parse(wrapper, paths, root),
                                 (parse(wrapper, [], root)[0], [], ''))
                harness = Path(root) / ('data/' + TAIL + 'harness')
                unrelated = write_json(harness, 'unrelated/trips/file.json', trip())
                self.assertEqual(parse(wrapper, [unrelated], harness),
                                 (parse(wrapper, [], root)[0], [], ''))
                self.assertEqual(len(parse(wrapper, [], root)[0]), width)
