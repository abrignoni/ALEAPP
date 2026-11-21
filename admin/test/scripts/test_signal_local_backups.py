"""Signal - On-Device Backups: metadata and files readers, snapshot names and storage spellings, on constructed files."""
import datetime
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.artifacts import signalLocalBackups as slb


def varint(value):
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def field(number, value):
    """One protobuf field: an int as a varint, bytes or str as length-delimited."""
    if isinstance(value, int):
        return varint(number << 3) + varint(value)
    data = value.encode() if isinstance(value, str) else value
    return varint((number << 3) | 2) + varint(len(data)) + data


def metadata(version=1):
    return field(1, version) + field(2, field(1, b'\x01' * 12) + field(2, b'\x02' * 16))


def files_member(names):
    out = b''
    for name in names:
        frame = field(1, name)
        out += varint(len(frame)) + frame
    return out


class Context:
    def __init__(self, root, files):
        self.root = Path(root)
        self.files = [str(path) for path in files]

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root)).replace(os.sep, '/')


class ReaderTests(unittest.TestCase):
    def test_metadata_version(self):
        self.assertEqual(slb.metadata_version(metadata()), 1)
        self.assertEqual(slb.metadata_version(metadata(2)), 2)

    def test_metadata_that_is_not_the_message(self):
        self.assertIsNone(slb.metadata_version(b''))
        self.assertIsNone(slb.metadata_version(b'\xff' * 36))
        self.assertIsNone(slb.metadata_version(field(1, b'text')))
        self.assertIsNone(slb.metadata_version(field(2, b'\xff\xff')))
        self.assertIsNone(slb.metadata_version(metadata()[:-3]))

    def test_media_names(self):
        self.assertEqual(slb.media_names(files_member(['aa11', 'bb22'])), ['aa11', 'bb22'])
        self.assertEqual(slb.media_names(b''), [])

    def test_media_names_cut_short(self):
        self.assertIsNone(slb.media_names(files_member(['aa11', 'bb22'])[:-2]))
        self.assertIsNone(slb.media_names(b'\x05\x0a\x03\xff\xfe\xfd'))


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.work = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.work)

    def put(self, relative, data):
        path = self.work / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def snapshot(self, root, name, meta=None, names=('aa11',), main=b'\x00' * 64, folder='SignalBackups'):
        base = f'{root}/{folder}/{name}/'
        return [self.put(base + 'main', main),
                self.put(base + 'metadata', metadata() if meta is None else meta),
                self.put(base + 'files', files_member(names))]

    def test_rows(self):
        files = []
        files += self.snapshot('data/media/0/Backup', 'signal-backup-2026-01-02-03-04-05', names=['a', 'b', 'c'])
        # the same snapshot under a second spelling of user 0's shared storage is one row
        files += self.snapshot('Dump/mnt/pass_through/0/emulated/0/Backup', 'signal-backup-2026-01-02-03-04-05')
        files += self.snapshot('data/media/10/Docs', 'signal-backup-2026-11-21-08-55-00-tmp', meta=b'\xff' * 8)
        files += self.snapshot('storage/1234-ABCD', 'signal-backup-2026-11-19-01-02-03')
        # not a snapshot member, and not a snapshot folder name
        files.append(self.put('data/media/0/Backup/SignalBackups/files/aa/aa11', b'\x00'))
        files += self.snapshot('data/media/0/Other', 'signal-backup-latest')
        # a renamed backup folder, and the other storage root spellings
        files += self.snapshot('storage/emulated/0', 'signal-backup-2026-11-18-00-00-01', folder='Moved')
        files += self.snapshot('mnt/user/0/emulated/11', 'signal-backup-2026-11-17-00-00-02')
        files += self.snapshot('userdata/media/12/X', 'signal-backup-2026-11-16-00-00-03')
        files += self.snapshot('sdcard/Pulled', 'signal-backup-2026-11-15-00-00-04')
        # digits that are not a real date are skipped; sdcard/ below a card root is not a root
        files += self.snapshot('data/media/0/Bad', 'signal-backup-2026-13-01-00-00-00')
        files += self.snapshot('storage/1234-ABCD/sdcard', 'signal-backup-2026-11-14-00-00-05')
        headers, rows, source = slb.signalLocalBackups.__wrapped__(Context(self.work, files))
        names = [h if isinstance(h, str) else h[0] for h in headers]
        self.assertEqual(len(names), len(rows[0]))
        index = {name: position for position, name in enumerate(names)}
        found = {(row[index['Android User']], row[index['Backup Location']],
                  row[index['Snapshot Time']]): row for row in rows}
        self.assertEqual(len(rows), 8)
        utc = datetime.timezone.utc
        first = found[('0', 'Backup/SignalBackups', datetime.datetime(2026, 1, 2, 3, 4, 5, tzinfo=utc))]
        self.assertEqual(first[index['Temporary Name']], 'No')
        self.assertEqual(first[index['Main Size']], 64)
        self.assertEqual(first[index['Metadata Version (as stored)']], 1)
        self.assertEqual(first[index['Media Listed']], 3)
        tmp = found[('10', 'Docs/SignalBackups', datetime.datetime(2026, 11, 21, 8, 55, 0, tzinfo=utc))]
        self.assertEqual(tmp[index['Temporary Name']], 'Yes')
        self.assertEqual(tmp[index['Metadata Version (as stored)']], '')
        card = found[('', 'storage/1234-ABCD/SignalBackups', datetime.datetime(2026, 11, 19, 1, 2, 3, tzinfo=utc))]
        self.assertEqual(card[index['Media Listed']], 1)
        self.assertIn(('0', 'Moved', datetime.datetime(2026, 11, 18, 0, 0, 1, tzinfo=utc)), found)
        self.assertIn(('11', 'SignalBackups', datetime.datetime(2026, 11, 17, 0, 0, 2, tzinfo=utc)), found)
        self.assertIn(('12', 'X/SignalBackups', datetime.datetime(2026, 11, 16, 0, 0, 3, tzinfo=utc)), found)
        self.assertIn(('', 'Pulled/SignalBackups', datetime.datetime(2026, 11, 15, 0, 0, 4, tzinfo=utc)), found)
        self.assertIn(('', 'storage/1234-ABCD/sdcard/SignalBackups',
                       datetime.datetime(2026, 11, 14, 0, 0, 5, tzinfo=utc)), found)
        self.assertNotIn('signal-backup-2026-13-01', source)
        self.assertNotIn('files/aa/aa11', source)
        self.assertNotIn('signal-backup-latest', source)


if __name__ == '__main__':
    unittest.main()
