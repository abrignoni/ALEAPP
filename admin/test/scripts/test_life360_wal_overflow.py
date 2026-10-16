"""Real SQLite overflow payloads, prefix provenance and bounded chain rejection."""
from pathlib import Path
import shutil
import sqlite3
import struct
import tempfile
import unittest
from unittest.mock import patch
from admin.test.scripts.test_life360_wal_schema import COLUMNS
from scripts.artifacts import L360noshowalerts as module


def create_overflow_fixture(root, size=512, length=5000, blob=None, indexed=False):
    blob = bytes(range(256))*20 if blob is None else blob
    target = Path(root)/'data/data/com.life360.android.safetymapd/databases/NoShowAlertRoomDatabase'
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory)/'source.db'
        db = sqlite3.connect(source)
        db.execute(f'PRAGMA page_size={size}')
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('PRAGMA wal_autocheckpoint=0')
        db.execute('CREATE TABLE no_show_alerts ('+','.join(COLUMNS)+')')
        values = ('long', 'type', 1700000000000, '<A>é🧪'+'a'*length, 0,
                  1700000000000000000, 'place', 'observed', 'creator', 'circle', blob)
        db.execute('INSERT INTO no_show_alerts VALUES ('+','.join('?' for _ in COLUMNS)+')', values)
        if indexed:
            db.execute('CREATE INDEX long_text ON no_show_alerts(trigger_condition)')
        db.commit()
        db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
        db.execute('UPDATE no_show_alerts SET trigger_condition=?, last_updated=1700000001000',
                   ('<B>é🧪'+'b'*length,))
        db.commit()
        db.execute('UPDATE no_show_alerts SET last_updated=1700000002000')
        db.commit()
        for suffix in ['', '-wal', '-shm']:
            shutil.copy2(Path(str(source)+suffix), Path(str(target)+suffix))
        db.close()
    return target


def main_snapshot(main, size=512):
    image = bytearray(main.read_bytes())
    root = 2
    origins = {number: f'main payload offset {(number-1)*size+4}'
               for number in range(1, len(image)//size+1)}
    page = image[(root-1)*size:root*size]
    return page, (image, size, size, origins, {1, root})


def refresh_checksums(data):
    """Create structurally damaged fixtures whose WAL frame checksums remain valid."""
    endian = '<' if int.from_bytes(data[:4], 'big') == 0x377f0682 else '>'
    first, second = struct.unpack('>2I', data[24:32])
    size = int.from_bytes(data[8:12], 'big')
    for offset in range(32, len(data), size+24):
        content = data[offset:offset+8]+data[offset+24:offset+24+size]
        words = struct.unpack(endian+str(len(content)//4)+'I', content)
        for index in range(0, len(words), 2):
            first = (first+words[index]+second) & 0xffffffff
            second = (second+words[index+1]+first) & 0xffffffff
        data[offset+16:offset+24] = struct.pack('>2I', first, second)


class TestLife360WalOverflow(unittest.TestCase):
    def test_long_text_blob_and_precise_prefix_origins(self):
        with tempfile.TemporaryDirectory() as root:
            for size, length in [(512, 5000), (65536, 80000)]:
                main = create_overflow_fixture(Path(root)/str(size), size, length)
                with patch.object(module, 'logfunc'):
                    rows = module.recover_wal_observations(main, Path(str(main)+'-wal'))
                self.assertEqual(len(rows), 2)
                self.assertEqual(rows[-1]['trigger_condition'], '<B>é🧪'+'b'*length)
                self.assertEqual(rows[-1]['daily'], bytes(range(256))*20)
                self.assertTrue(rows[0]['_overflow_pages'])
                self.assertTrue(any('main payload offset' in s for s in rows[0]['_overflow_sources']))
                self.assertTrue(any('WAL frame' in s for s in rows[-1]['_overflow_sources']))
                # First leaf precedes updated overflow bytes, so its prefix is intentionally mixed.
                self.assertNotEqual(rows[0]['trigger_condition'], rows[-1]['trigger_condition'])

    def test_index_overflow_is_not_mistaken_for_table_payload(self):
        with tempfile.TemporaryDirectory() as root:
            main = create_overflow_fixture(root, indexed=True)
            with patch.object(module, 'logfunc'):
                records = module.recover_wal_observations(main, Path(str(main)+'-wal'))
            self.assertEqual(len(records), 2)
            self.assertEqual(records[-1]['trigger_condition'], '<B>é🧪'+'b'*5000)
            connection = sqlite3.connect(main.as_uri()+'?mode=ro', uri=True)
            index_root = connection.execute("SELECT rootpage FROM sqlite_master "
                                            "WHERE name='long_text'").fetchone()[0]
            connection.close()
            self.assertNotIn(index_root, records[-1]['_overflow_pages'])
            self.assertEqual(main.read_bytes()[(index_root-1)*512], 10)

    def test_corrupt_incomplete_and_btree_chains_are_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            main = create_overflow_fixture(root)
            page, snapshot = main_snapshot(main)
            records, failures = module.parse_leaf_records(page, COLUMNS, 512, snapshot=snapshot)
            self.assertFalse(failures)
            self.assertEqual(records[0]['trigger_condition'], '<A>é🧪'+'a'*5000)
            chain = records[0]['_overflow_pages']
            self.assertGreater(len(chain), 2)
            image, size, usable, origins, forbidden = snapshot
            for label in ['cycle', 'extra', 'short', 'unavailable', 'btree', 'outside']:
                damaged = bytearray(image)
                available = dict(origins)
                if label == 'cycle':
                    damaged[(chain[0]-1)*size:(chain[0]-1)*size+4] = chain[0].to_bytes(4, 'big')
                elif label == 'extra':
                    damaged[(chain[-1]-1)*size:(chain[-1]-1)*size+4] = chain[0].to_bytes(4, 'big')
                elif label == 'short':
                    damaged[(chain[0]-1)*size:(chain[0]-1)*size+4] = bytes(4)
                elif label == 'unavailable':
                    available.pop(chain[1])
                elif label == 'btree':
                    damaged[(chain[0]-1)*size:(chain[0]-1)*size+4] = (2).to_bytes(4, 'big')
                else:
                    damaged[(chain[0]-1)*size:(chain[0]-1)*size+4] = (99999).to_bytes(4, 'big')
                bad = (damaged, size, usable, available, forbidden)
                rows, errors = module.parse_leaf_records(page, COLUMNS, 512, snapshot=bad)
                self.assertEqual(rows, [], label)
                self.assertTrue(errors, label)

    def test_valid_checksum_wal_with_corrupt_overflow_chain(self):
        with tempfile.TemporaryDirectory() as root:
            main = create_overflow_fixture(root)
            wal = Path(str(main)+'-wal')
            with patch.object(module, 'logfunc'):
                healthy = module.recover_wal_observations(main, wal)
            first_overflow = healthy[-1]['_overflow_pages'][0]
            data = bytearray(wal.read_bytes())
            changed = False
            for offset in range(32, len(data), 536):
                if int.from_bytes(data[offset:offset+4], 'big') == first_overflow:
                    data[offset+24:offset+28] = first_overflow.to_bytes(4, 'big')
                    changed = True
                    break
            self.assertTrue(changed)
            refresh_checksums(data)
            wal.write_bytes(data)
            with patch.object(module, 'logfunc') as log:
                records = module.recover_wal_observations(main, wal)
            self.assertEqual(len(records), 1)
            messages = ' '.join(call.args[0] for call in log.call_args_list)
            self.assertIn('cyclic', messages)
            self.assertNotIn('checksum mismatch', messages)
            self.assertEqual(records[0]['_wal_frame'], healthy[0]['_wal_frame'])

    def test_sqlite_generated_inline_overflow_boundary(self):
        with tempfile.TemporaryDirectory() as root:
            for target_payload in [477, 478]:
                length = 400
                for attempt in range(2):
                    main = create_overflow_fixture(Path(root)/f'{target_payload}-{attempt}',
                                                   length=length, blob=b'')
                    page, snapshot = main_snapshot(main)
                    ptr = int.from_bytes(page[8:10], 'big')
                    payload, index = 0, ptr
                    while True:
                        byte = page[index]
                        payload = (payload << 7) | (byte & 127)
                        index += 1
                        if byte < 128:
                            break
                    if payload == target_payload:
                        break
                    length += target_payload - payload
                self.assertEqual(payload, target_payload)
                rows, failures = module.parse_leaf_records(page, COLUMNS, 512, snapshot=snapshot)
                self.assertFalse(failures)
                self.assertEqual(rows[0]['trigger_condition'], '<A>é🧪'+'a'*length)
                self.assertEqual(bool(rows[0]['_overflow_pages']), target_payload > 477)

    def test_invalid_cell_partial_chain_still_reserves_shared_pages(self):
        with tempfile.TemporaryDirectory() as root:
            main = create_overflow_fixture(root)
            page, snapshot = main_snapshot(main)
            image, size, usable, origins, tree = snapshot
            ptr = int.from_bytes(page[8:10], 'big')
            payload, end = 0, ptr
            while True:
                byte = page[end]
                payload = (payload << 7) | (byte & 127)
                end += 1
                if byte < 128:
                    break
            oversized = payload + ((module.MAX_RECORD_PAYLOAD-payload)//508+1)*508
            for invalid_payload in [payload+508, payload-508, oversized]:
                # A private second leaf reuses the actual chain with an invalid size.
                # Adding/subtracting one overflow capacity retains the local bytes.
                encoded, value = [invalid_payload & 127], invalid_payload >> 7
                while value:
                    encoded.append((value & 127) | 128)
                    value >>= 7
                encoded.reverse()
                cell = bytes(encoded)+bytes(page[end:])
                other = bytearray(page)
                new_ptr = size-len(cell)
                other[new_ptr:] = cell
                other[8:10] = new_ptr.to_bytes(2, 'big')
                copied = bytearray(image)
                number = len(copied)//size+1
                copied.extend(other)
                available = dict(origins)
                available[number] = 'private malformed fixture leaf'
                bad = (copied, size, usable, available, tree | {number})
                invalid_rows, errors = module.parse_leaf_records(
                    other, COLUMNS, usable, snapshot=bad)
                self.assertEqual(invalid_rows, [])
                self.assertTrue(errors)
                shared = module.shared_overflow_pages(bad)
                self.assertTrue(shared)
                guarded = (copied, size, usable, available, tree | {number} | shared)
                valid_rows, failures = module.parse_leaf_records(
                    page, COLUMNS, usable, snapshot=guarded)
                self.assertEqual(valid_rows, [])
                self.assertTrue(failures)

    def test_shared_cell_chains_are_ambiguous(self):
        with tempfile.TemporaryDirectory() as root:
            main = create_overflow_fixture(root)
            page, snapshot = main_snapshot(main)
            page = bytearray(page)
            page[3:5] = (3).to_bytes(2, 'big')
            page[10:12] = page[8:10]
            page[12:14] = page[8:10]
            image, size, usable, origins, tree = snapshot
            image[512:1024] = page
            shared = module.shared_overflow_pages((image, size, usable, origins, tree))
            self.assertTrue(shared)
            rows, failures = module.parse_leaf_records(page, COLUMNS, 512, snapshot=snapshot)
            self.assertEqual(rows, [])
            self.assertTrue(any('shared' in message for message in failures))


if __name__ == '__main__':
    unittest.main()
