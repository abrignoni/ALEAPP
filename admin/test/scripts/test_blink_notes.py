"""Re-derive every checkable claim in BlinkApp's notes and descriptions from its fixture.

The notes on these nine artifacts carry numbers: row counts, a column count, the rows an
unqualified join would have returned, autoincrement values, the gaps between the records the
app wrote at setup. Every one of them was measured once, and nothing stops the module changing
underneath them afterwards. A count written while building is a claim about the code as it was
then.

So each assertion here reads the number back OUT of the shipped field with a regex and compares
it to a value computed from the committed test case. Nothing is hardcoded in between, which
means three different failures all go red: a wrong number in the prose, a number that was right
and went stale, and a sentence reworded until the pattern no longer matches it. That last one
matters most, because a checker whose pattern silently stops matching is a checker that has
quietly retired itself.

The fixture these run against is a sanitized copy of the only Blink data the module has ever
seen. The values the sanitizing deliberately left alone are the ones asserted here.
"""
import ast
import datetime
import os
import re
import sqlite3
import tempfile
import unittest
import zipfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
MODULE = os.path.join(REPO, 'scripts', 'artifacts', 'BlinkApp.py')
CASE_DIR = os.path.join(REPO, 'admin', 'test', 'cases', 'data', 'BlinkApp')
DB_IN_ZIP = 'data/data/com.immediasemi.android.blink/databases/BlinkRoom'


def _artifacts():
    src = open(MODULE, encoding='utf-8').read()
    block = [n for n in ast.walk(ast.parse(src))
             if isinstance(n, ast.Assign)
             and getattr(n.targets[0], 'id', '') == '__artifacts_v2__'][0]
    return ast.literal_eval(block.value), src


def _headers(src, function_name):
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            for sub in ast.walk(node):
                if (isinstance(sub, ast.Assign)
                        and getattr(sub.targets[0], 'id', '') == 'data_headers'):
                    return [h[0] if isinstance(h, tuple) else h
                            for h in ast.literal_eval(sub.value)]
    raise AssertionError(f'no data_headers in {function_name}')


class BlinkNotesTest(unittest.TestCase):
    """Every claim below is re-derived; none of these numbers is typed twice."""

    @classmethod
    def setUpClass(cls):
        cls.artifacts, cls.src = _artifacts()
        zips = sorted(f for f in os.listdir(CASE_DIR) if f.endswith('.zip'))
        cls.assertTrue(bool(zips), 'no committed Blink test case to check against')
        cls._tmp = tempfile.TemporaryDirectory()
        with zipfile.ZipFile(os.path.join(CASE_DIR, zips[0])) as archive:
            archive.extract(DB_IN_ZIP, cls._tmp.name)
        path = os.path.join(cls._tmp.name, DB_IN_ZIP)
        cls.db = sqlite3.connect(f'file:{path}?mode=ro', uri=True)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()
        cls._tmp.cleanup()

    def stated(self, key, pattern, field='notes'):
        """The number the shipped prose states. A pattern that matches nothing fails."""
        match = re.search(pattern, self.artifacts[key][field])
        self.assertIsNotNone(
            match, f'{key}.{field} no longer matches {pattern!r}; the claim may have been '
                   f'reworded, which retires this assertion silently unless it fails here')
        return int(match.group(1).replace(',', ''))

    def one(self, sql):
        return self.db.execute(sql).fetchone()[0]

    def test_row_counts_match_the_fixture(self):
        for key, sql in (
                ('blink_camera_information', 'select count(*) from camera'),
                ('blink_camera_entitlements',
                 'select count(*) from camera left join entitlement '
                 'on camera.id=entitlement.target_id and camera.type=entitlement.target'),
                ('blink_syncmodule_information', 'select count(*) from syncmodule'),
                ('blink_syncmodule_entitlements',
                 'select count(*) from syncmodule left join entitlement '
                 'on syncmodule.id=entitlement.target_id and syncmodule.type=entitlement.target'),
                ('blink_network_information', 'select count(*) from network'),
                ('blink_key_value_store', 'select count(*) from key_value_pair'),
                ('blink_subscriptions', 'select count(*) from subscription'),
                ('blink_app_messages', 'select count(*) from message'),
                ('blink_tracking_events', 'select count(*) from tracking_event')):
            with self.subTest(artifact=key):
                self.assertEqual(self.stated(key, r'Android 16: ([\d,]+) rows?'), self.one(sql))

    def test_camera_column_arithmetic(self):
        key = 'blink_camera_information'
        self.assertEqual(self.stated(key, r'camera table holds (\d+) columns'),
                         len(list(self.db.execute('PRAGMA table_info(camera)'))))
        self.assertEqual(self.stated(key, r'artifact reports (\d+) of them'),
                         len(_headers(self.src, key)))

    def test_the_unqualified_join_returns_what_the_notes_say(self):
        # The notes explain that joining on target_id alone happened to be right on this file.
        # If that stops being true the explanation stops making sense.
        self.assertEqual(
            self.stated('blink_camera_entitlements', r'returned the same (\d+) rows'),
            self.one('select count(*) from camera join entitlement '
                     'on camera.id=entitlement.target_id'))

    def test_entitlements_per_camera(self):
        key = 'blink_camera_entitlements'
        per = self.stated(key, r'(\d+) entitlements against')
        cameras = self.stated(key, r'against each of (\d+) cameras')
        measured = [r[0] for r in self.db.execute(
            'select count(*) from camera join entitlement '
            'on camera.id=entitlement.target_id and camera.type=entitlement.target '
            'group by camera.id')]
        self.assertEqual(measured, [per] * cameras)

    def test_account_entitlements_are_counted_correctly(self):
        self.assertEqual(
            self.stated('blink_camera_entitlements', r'rather than a device, (\d+) rows'),
            self.one("select count(*) from entitlement where target='account'"))

    def test_the_status_values_named_are_the_ones_present(self):
        match = re.search(r'status values ([A-Z_, ]+?) and ([A-Z_]+),',
                          self.artifacts['blink_camera_entitlements']['notes'])
        self.assertIsNotNone(match, 'the status-value sentence no longer matches')
        named = {s.strip() for s in f'{match.group(1)},{match.group(2)}'.split(',') if s.strip()}
        self.assertEqual(named, {r[0] for r in
                                 self.db.execute('select distinct status from entitlement')})

    def test_the_subtype_join_really_returns_nothing(self):
        self.assertIn('joining on it instead returns no rows',
                      self.artifacts['blink_syncmodule_entitlements']['notes'])
        self.assertEqual(0, self.one(
            'select count(*) from syncmodule join entitlement '
            'on syncmodule.id=entitlement.target_id and syncmodule.subtype=entitlement.target'))

    def test_the_setup_sequence_gaps(self):
        notes = self.artifacts['blink_network_information']['notes']
        parse = datetime.datetime.fromisoformat
        network = parse(self.one('select created_at from network'))
        syncmodule = parse(self.one('select created_at from syncmodule'))
        self.assertEqual(self.stated('blink_network_information', r'by (\d+) seconds'),
                         (syncmodule - network).total_seconds())
        match = re.search(r'by (\d+) minutes (\d+) seconds and (\d+) minutes (\d+) seconds', notes)
        self.assertIsNotNone(match, 'the camera-offset sentence no longer matches')
        stated = [int(match.group(1)) * 60 + int(match.group(2)),
                  int(match.group(3)) * 60 + int(match.group(4))]
        measured = [(parse(r[0]) - network).total_seconds()
                    for r in self.db.execute('select created_at from camera order by created_at')]
        self.assertEqual(stated, measured)

    def test_the_key_value_store_claims(self):
        notes = self.artifacts['blink_key_value_store']['notes']
        longs = [r[0] for r in
                 self.db.execute("select value from key_value_pair where type='LONG'")]
        words = {'two': 2, 'three': 3, 'four': 4, 'five': 5}
        match = re.search(r'the (\w+) values typed LONG', notes)
        self.assertIsNotNone(match, 'the LONG-value sentence no longer matches')
        self.assertEqual(words[match.group(1)], len(longs))
        # the notes say those three are an epoch in milliseconds, a network id and a zero
        self.assertIn(str(self.one('select id from network')), longs)
        self.assertIn('0', longs)
        self.assertTrue(any(len(v) == 13 and v.isdigit() for v in longs))
        # the local offset that corroborates the zone on the network row
        self.assertIn('-04:00', notes)
        self.assertTrue(self.one(
            "select count(*) from key_value_pair where value like '%-04:00%'"))
        self.assertIn(self.one('select time_zone from network'), notes)
        # keys that embed a camera id, and the ones that begin with a brace
        camera_ids = {str(r[0]) for r in self.db.execute('select id from camera')}
        keys = [r[0] for r in self.db.execute('select key from key_value_pair')]
        self.assertTrue(any(any(i in k for i in camera_ids) for k in keys))
        match = re.search(r'(\w+) on the tested file also began with a brace', notes)
        self.assertIsNotNone(match, 'the brace sentence no longer matches')
        self.assertEqual(words[match.group(1)], len([k for k in keys if k.startswith('{')]))

    def test_the_subscription_points_at_nothing_else_in_the_file(self):
        notes = self.artifacts['blink_subscriptions']['notes']
        others = set()
        for sql in ('select id from camera', 'select id from syncmodule',
                    'select id from network'):
            others |= {r[0] for r in self.db.execute(sql)}
        self.assertNotIn(self.one('select target_id from subscription'), others)
        self.assertNotIn(self.one('select target from subscription'),
                         {r[0] for r in self.db.execute('select distinct target from entitlement')})
        self.assertIn('was zero on both cameras', notes)
        self.assertTrue(all(r[0] == 0 for r in
                            self.db.execute('select subscription_id from camera')))
        self.assertIn("sync module's was empty", notes)
        self.assertIsNone(self.one('select subscription_id from syncmodule'))

    def test_the_message_claims(self):
        notes = self.artifacts['blink_app_messages']['notes']
        self.assertEqual(self.stated('blink_app_messages', r'reached (\d+) with'),
                         self.one('select max(id) from message'))
        # the notes justify the millisecond reading by saying seconds is impossible
        with self.assertRaises((ValueError, OSError, OverflowError)):
            datetime.datetime.fromtimestamp(self.one('select created_at from message'),
                                            datetime.timezone.utc)
        self.assertIn('held an empty string', notes)
        self.assertEqual('', self.one('select sub_message from message'))
        text = self.one('select message from message')
        self.assertTrue(any(r[0] in text for r in self.db.execute('select name from camera')),
                        'the notes say the message text names a camera by its Camera Name')

    def test_the_tracking_claims(self):
        notes = self.artifacts['blink_tracking_events']['notes']
        self.assertEqual(self.stated('blink_tracking_events', r'reached (\d+) with'),
                         self.one('select max(id) from tracking_event'))
        self.assertIn(self.one('select name from tracking_event'), notes)
        columns = {r[1] for r in self.db.execute('PRAGMA table_info(tracking_event)')}
        self.assertFalse(columns & {'camera_id', 'network_id', 'account_id'},
                         'the notes say the table names no camera, network or account')

    def test_every_stored_timestamp_carries_its_own_offset(self):
        # The network notes say the zone is not needed to read anything here, because every
        # stored timestamp is self describing. That is a claim about the whole file.
        self.assertIn('carried its own UTC offset',
                      self.artifacts['blink_network_information']['notes'])
        looks_iso = re.compile(r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}')
        has_offset = re.compile(r'(Z|[+-]\d{2}:?\d{2})$')
        naive = []
        tables = [r[0] for r in self.db.execute(
            "select name from sqlite_master where type='table'")]
        for table in tables:
            rows = self.db.execute(f'select * from "{table}"').fetchall()
            if not rows:
                continue
            names = [r[1] for r in self.db.execute(f'PRAGMA table_info("{table}")')]
            for index, column in enumerate(names):
                for row in rows:
                    value = row[index]
                    if (isinstance(value, str) and looks_iso.match(value)
                            and not has_offset.search(value)):
                        naive.append(f'{table}.{column}={value}')
        self.assertEqual([], naive)

    def test_camera_timestamps_and_model_code(self):
        notes = self.artifacts['blink_camera_information']['notes']
        self.assertIn('+00:00', notes)
        offsets = set()
        for sql in ('select created_at from camera', 'select updated_at from camera'):
            offsets |= {r[0][-6:] for r in self.db.execute(sql)}
        self.assertEqual({'+00:00'}, offsets)
        self.assertIn('was also the entitlement target', notes)
        self.assertLessEqual(
            {r[0] for r in self.db.execute('select distinct type from camera')},
            {r[0] for r in self.db.execute('select distinct target from entitlement')})


if __name__ == '__main__':
    unittest.main()
