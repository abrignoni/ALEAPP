"""Image Type carries the name of the AOSP icon type it equals, and a data icon's stored bitmap
bytes are checked in as media. All values here are made up."""
# pylint: disable=no-member
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import notificationHistory
from scripts.artifacts.notification_history_pb import notificationhistory_pb2 as pb

PNG = b'\x89PNG\r\n\x1a\n' + b'\x00' * 24


def report_row(build, raw_icon=None):
    """The artifact's one row as {header: cell}, and the media check-in calls it made. raw_icon is
    an Icon message's bytes appended to the record as field 12, for values the schema cannot set."""
    history = pb.NotificationHistoryProto()
    record = history.notification.add()
    record.package = 'example.package'
    build(record)
    if raw_icon is not None:
        record.MergeFromString(bytes([0x62, len(raw_icon)]) + raw_icon)
    calls = []

    def check_in(source_file, data, name='', **_kwargs):
        calls.append((source_file, data, name))
        return 'media-ref'

    with tempfile.TemporaryDirectory() as folder:
        path = pathlib.Path(folder) / '1700000000000'
        path.write_bytes(history.SerializeToString())
        context = SimpleNamespace(get_files_found=lambda: [str(path)])
        with patch.object(notificationHistory, 'check_in_embedded_media', side_effect=check_in):
            headers, rows, _source = notificationHistory.get_notificationHistory.__wrapped__(context)
    names = [h[0] if isinstance(h, tuple) else h for h in headers]
    return dict(zip(names, rows[0])), calls, headers


def data_icon(data, offset, length):
    def build(record):
        record.icon.image_type = 3
        record.icon.image_data = data
        record.icon.image_data_offset = offset
        record.icon.image_data_length = length
    return build


class ImageType(unittest.TestCase):
    def test_each_aosp_type_is_named(self):
        for number, name in ((1, 'bitmap'), (2, 'resource'), (3, 'data'), (4, 'uri'),
                             (5, 'adaptive bitmap'), (6, 'uri adaptive bitmap')):
            with self.subTest(number):
                row, _calls, _headers = report_row(lambda r: None, raw_icon=bytes([0x08, number]))
                self.assertEqual(row['Image Type'], f'{number} ({name})')

    def test_a_number_the_schema_does_not_name_is_shown_as_stored(self):
        row, _calls, _headers = report_row(lambda r: None, raw_icon=bytes([0x08, 99]))
        self.assertEqual(row['Image Type'], 99)

    def test_an_icon_with_no_stored_type_is_blank(self):
        row, _calls, _headers = report_row(lambda r: setattr(r.icon, 'image_uri', 'content://x'))
        self.assertIsNone(row['Image Type'])

    def test_no_icon_is_blank(self):
        row, _calls, _headers = report_row(lambda r: None)
        self.assertIsNone(row['Image Type'])


class DataIcon(unittest.TestCase):
    def test_the_bitmap_bytes_are_checked_in(self):
        row, calls, headers = report_row(data_icon(PNG, 0, len(PNG)))
        self.assertEqual(row['Icon Image'], 'media-ref')
        self.assertEqual(calls[0][1], PNG)
        self.assertIn(('Icon Image', 'media'), headers)

    def test_only_the_offset_and_length_slice_is_checked_in(self):
        stored = b'XXXX' + PNG + b'YYYY'
        _row, calls, _headers = report_row(data_icon(stored, 4, len(PNG)))
        self.assertEqual(calls[0][1], PNG)

    def test_a_slice_past_the_stored_bytes_is_not_checked_in(self):
        row, calls, _headers = report_row(data_icon(PNG, 4, len(PNG)))
        self.assertEqual((row['Icon Image'], calls), ('', []))

    def test_a_resource_icon_has_no_image(self):
        def build(record):
            record.icon.image_type = 2
            record.icon.image_resource_id = 123
        row, calls, _headers = report_row(build)
        self.assertEqual((row['Icon Image'], calls), ('', []))


class Layout(unittest.TestCase):
    def test_the_file_name_time_follows_the_posted_time(self):
        _row, _calls, headers = report_row(lambda r: None)
        self.assertEqual([h[0] for h in headers[:2]], ['Posted Time', 'Timestamp From Protobuf File Name'])

    def test_every_history_folder_is_named_in_the_source_path(self):
        history = pb.NotificationHistoryProto()
        history.notification.add().package = 'example.package'
        with tempfile.TemporaryDirectory() as folder:
            found = []
            for user in ('0', '10'):
                path = pathlib.Path(folder) / user / 'history' / '1700000000000'
                path.parent.mkdir(parents=True)
                path.write_bytes(history.SerializeToString())
                found.append(str(path))
            context = SimpleNamespace(get_files_found=lambda: found)
            _headers, _rows, source = notificationHistory.get_notificationHistory.__wrapped__(context)
            self.assertEqual(source.split('\n'), [str(pathlib.Path(f).parent) for f in found])


if __name__ == '__main__':
    unittest.main()
