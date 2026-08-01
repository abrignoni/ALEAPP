# pylint: disable=no-member,protected-access
import os
import tempfile
import unittest

from scripts.artifacts import recentactivity, usagestats
from scripts.artifacts.recentactivity_pb import task_snapshot_pb2
from scripts.artifacts.usagestats_pb import (
    usagestatsservice_pb2,
    usagestatsservice_v2_pb2,
)


class UsageStatsModernizationTests(unittest.TestCase):
    def test_event_type_31_and_standby_value_are_decoded(self):
        self.assertEqual(usagestats._event_type_name(31), 'APP_COMPONENT_USED')
        self.assertEqual(usagestats._standby_parts((40 << 16) | 7), (40, 7))

    def test_v1_protobuf_exposes_package_and_event_details(self):
        with tempfile.TemporaryDirectory() as folder:
            daily = os.path.join(folder, 'daily')
            os.mkdir(daily)
            interval_begin = 1_700_000_000_000
            stats = usagestatsservice_pb2.IntervalStatsProto()
            stats.stringpool.strings.extend([
                'com.example', 'MainActivity', 'channel', 'com.root', 'RootActivity', 'locus'
            ])
            package = stats.packages.add()
            package.package_index = 1
            package.last_time_active_ms = 1000
            package.total_time_active_ms = 5000
            package.last_time_service_used_ms = 2000
            package.total_time_service_used_ms = 3000
            package.last_time_visible_ms = 2500
            package.total_time_visible_ms = 3500
            package.last_time_component_used_ms = 2750
            package.app_launch_count = 2
            event = stats.event_log.add()
            event.package_index = 1
            event.class_index = 2
            event.time_ms = 4000
            event.type = 31
            event.flags = 1
            event.standby_bucket = (40 << 16) | 7
            event.notification_channel_index = 3
            event.instance_id = 99
            event.task_root_package_index = 4
            event.task_root_class_index = 5
            event.locus_id_index = 6
            with open(os.path.join(daily, str(interval_begin)), 'wb') as output:
                output.write(stats.SerializeToString())

            rows = usagestats.process_usagestats(folder, '0', 1)

        package_row = next(row for row in rows if row[2] == 'packages')
        event_row = next(row for row in rows if row[2] == 'event-log')
        self.assertEqual(package_row[6], 3000)
        self.assertEqual(package_row[8], 3500)
        self.assertTrue(package_row[9])
        self.assertEqual(event_row[12], 'APP_COMPONENT_USED')
        self.assertEqual(event_row[14], 'FLAG_IS_PACKAGE_INSTANT_APP')
        self.assertEqual(event_row[16:18], (40, 7))
        self.assertEqual(event_row[18:23], ('channel', 99, 'com.root', 'RootActivity', 'locus'))

    def test_v2_tokens_are_resolved(self):
        with tempfile.TemporaryDirectory() as folder:
            daily = os.path.join(folder, 'daily')
            os.mkdir(daily)
            interval_begin = 1_700_000_000_000
            mappings = usagestatsservice_v2_pb2.ObfuscatedPackagesProto()
            app = mappings.packages_map.add()
            app.package_token = 1
            app.strings.extend([
                'com.example', 'MainActivity', 'shortcut', 'channel', 'locus',
                'button', 'tap'
            ])
            root = mappings.packages_map.add()
            root.package_token = 2
            root.strings.extend(['com.root', 'RootActivity'])
            with open(os.path.join(folder, 'mappings'), 'wb') as output:
                output.write(mappings.SerializeToString())

            stats = usagestatsservice_v2_pb2.IntervalStatsObfuscatedProto()
            event = stats.event_log.add()
            event.package_token = 1
            event.class_token = 2
            event.time_ms = 4000
            event.type = 31
            event.shortcut_id_token = 3
            event.notification_channel_id_token = 4
            event.instance_id = 42
            event.task_root_package_token = 2
            event.task_root_class_token = 2
            event.locus_id_token = 5
            event.interaction_extras.category_token = 6
            event.interaction_extras.action_token = 7
            with open(os.path.join(daily, str(interval_begin)), 'wb') as output:
                output.write(stats.SerializeToString())

            rows = usagestats.process_usagestats(folder, '0', 2)

        event_row = next(row for row in rows if row[2] == 'event-log')
        self.assertEqual(event_row[12], 'APP_COMPONENT_USED')
        self.assertEqual(event_row[15], 'shortcut')
        self.assertEqual(event_row[18:23], ('channel', 42, 'com.root', 'RootActivity', 'locus'))
        self.assertEqual(event_row[23:25], ('button', 'tap'))


class RecentActivityModernizationTests(unittest.TestCase):
    def test_snapshot_proto_metadata_is_exposed(self):
        with tempfile.TemporaryDirectory() as folder:
            snapshots = os.path.join(folder, 'snapshots')
            os.mkdir(snapshots)
            snapshot = task_snapshot_pb2.TaskSnapshotProto(
                id=1_700_000_000_000,
                top_activity_component='com.example/.MainActivity',
                is_real_snapshot=True,
                orientation=1,
                rotation=1,
                task_width=1080,
                task_height=2400,
                inset_left=1,
                inset_top=2,
                inset_right=3,
                inset_bottom=4,
            )
            with open(os.path.join(snapshots, '7.proto'), 'wb') as output:
                output.write(snapshot.SerializeToString())

            details = recentactivity._snapshot_metadata(folder, '7')

        self.assertEqual(details[2], 1_700_000_000_000)
        self.assertEqual(details[4], 'com.example/.MainActivity')
        self.assertEqual(details[5], 'Yes')
        self.assertEqual(details[6:9], ('Portrait', '90°', '1080 × 2400'))
        self.assertEqual(details[11], '1, 2, 3, 4')


if __name__ == '__main__':
    unittest.main()
