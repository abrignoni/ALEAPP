"""An unset notification field is blank only where the AOSP writer would not have stored it."""
# pylint: disable=no-member
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import notificationHistory
from scripts.artifacts.notification_history_pb import notificationhistory_pb2 as pb

INDEX_HEADERS = ('Package Index', 'Channel Name Index', 'Channel ID Index', 'Conversation ID Index')
INDEX_FIELDS = ('package_index', 'channel_name_index', 'channel_id_index', 'conversation_id_index')
TYPE_RESOURCE, TYPE_DATA, TYPE_URI = 2, 3, 4


def report_row(build):
    """The artifact's one row, as {header: cell}, for a record that build fills in."""
    history = pb.NotificationHistoryProto()
    record = history.notification.add()
    record.package = 'example.package'
    build(record)
    with tempfile.TemporaryDirectory() as folder:
        path = pathlib.Path(folder) / '1700000000000'
        path.write_bytes(history.SerializeToString())
        context = SimpleNamespace(get_files_found=lambda: [str(path)])
        headers, rows, _source = notificationHistory.get_notificationHistory.__wrapped__(context)
    names = [h[0] if isinstance(h, tuple) else h for h in headers]
    assert len(rows) == 1
    return dict(zip(names, rows[0]))


class IndexColumns(unittest.TestCase):
    def test_absent_index_is_blank(self):
        row = report_row(lambda r: None)
        for header in INDEX_HEADERS:
            self.assertIsNone(row[header], header)

    def test_stored_index_is_shown(self):
        def build(record):
            for number, field in enumerate(INDEX_FIELDS, 1):
                setattr(record, field, number)
        row = report_row(build)
        self.assertEqual([row[h] for h in INDEX_HEADERS], [1, 2, 3, 4])

    def test_stored_zero_index_is_shown(self):
        def build(record):
            for field in INDEX_FIELDS:
                setattr(record, field, 0)
        row = report_row(build)
        self.assertEqual([row[h] for h in INDEX_HEADERS], [0, 0, 0, 0])


class AlwaysWrittenFields(unittest.TestCase):
    def test_unset_uid_and_user_id_read_as_zero(self):
        row = report_row(lambda r: None)
        self.assertEqual((row['UID'], row['User ID']), (0, 0))


class IconColumns(unittest.TestCase):
    def test_no_icon_leaves_every_icon_column_blank(self):
        row = report_row(lambda r: None)
        for header in ('Image Type', 'Image Resource ID', 'Image Data Length', 'Image Data Offset'):
            self.assertIsNone(row[header], header)

    def test_data_icon_keeps_an_omitted_zero_offset(self):
        def build(record):
            record.icon.image_type = TYPE_DATA
            record.icon.image_data_length = 512
        row = report_row(build)
        self.assertEqual((row['Image Data Length'], row['Image Data Offset']), (512, 0))
        self.assertIsNone(row['Image Resource ID'])

    def test_resource_icon_keeps_an_omitted_zero_id(self):
        def build(record):
            record.icon.image_type = TYPE_RESOURCE
        row = report_row(build)
        self.assertEqual(row['Image Resource ID'], 0)
        self.assertIsNone(row['Image Data Length'])
        self.assertIsNone(row['Image Data Offset'])

    def test_field_stored_on_another_icon_type_is_shown(self):
        def build(record):
            record.icon.image_type = TYPE_URI
            record.icon.image_data_length = 7
            record.icon.image_data_offset = 0
            record.icon.image_resource_id = 9
        row = report_row(build)
        self.assertEqual((row['Image Data Length'], row['Image Data Offset'], row['Image Resource ID']), (7, 0, 9))

    def test_field_absent_on_another_icon_type_is_blank(self):
        def build(record):
            record.icon.image_type = TYPE_URI
        row = report_row(build)
        for header in ('Image Data Length', 'Image Data Offset', 'Image Resource ID'):
            self.assertIsNone(row[header], header)


if __name__ == '__main__':
    unittest.main()
