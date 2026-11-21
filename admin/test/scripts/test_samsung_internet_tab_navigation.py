"""Samsung Internet per-tab navigation files decode as Chromium WebContentsState.

The bytes here are built to the format, with synthetic URLs and titles, not taken
from any image.
"""
from pathlib import Path
import struct
import tempfile
import unittest
from types import SimpleNamespace
from scripts.artifacts import samsungInternet


def _pad(buf):
    while len(buf) % 4:
        buf += b'\x00'
    return buf


class _PickleWriter:
    def __init__(self):
        self.buf = b''
    def int(self, value):
        self.buf += struct.pack('<i', value); return self
    def int64(self, value):
        self.buf = _pad(self.buf) + struct.pack('<q', value); return self
    def boolean(self, value):
        return self.int(1 if value else 0)
    def string(self, text):
        raw = text.encode('utf-8')
        self.buf += struct.pack('<i', len(raw)); self.buf = _pad(self.buf + raw); return self
    def string16(self, text):
        raw = text.encode('utf-16-le')
        self.buf += struct.pack('<i', len(text)); self.buf = _pad(self.buf + raw); return self
    def bytes_field(self, data):
        self.buf += struct.pack('<i', len(data)); self.buf = _pad(self.buf + data); return self
    def pickle(self):
        return struct.pack('<I', len(self.buf)) + self.buf


def _entry(index, url, title, transition, timestamp, http_status, referrer=''):
    w = _PickleWriter()
    w.int(index).string(url).string16(title).string('PAGESTATE').int(transition)
    w.int(0)                          # type_mask
    w.string(referrer).int(0)         # referrer + ignored policy
    w.string('').boolean(False)       # original_url + ua override
    w.int64(timestamp).string16('')   # timestamp + search terms
    w.int(http_status)
    return w.pickle()


def _tab_file(off_the_record, current_index, entries):
    outer = _PickleWriter()
    outer.boolean(off_the_record).int(len(entries)).int(current_index)
    for entry in entries:
        outer.bytes_field(entry)
    contents = outer.pickle()
    # 8 header bytes (not read), big-endian contents size, the WebContentsState, a trailer.
    return b'\x00' * 8 + struct.pack('>I', len(contents)) + contents + b'\x00' * 16


# base::Time internal value: microseconds since 1601-01-01 UTC. 2021-01-01 = this.
TS = 13253932800000000


class TestSamsungInternetTabNavigation(unittest.TestCase):
    def parse(self, root, files):
        context = SimpleNamespace(
            get_files_found=lambda: [str(p) for p in files],
            get_relative_path=lambda p: str(Path(p).relative_to(root)),
        )
        return samsungInternet.samsung_internet_tab_navigation.__wrapped__(context)

    def test_two_entry_tab_decodes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tab = root / 'data/data/com.sec.android.app.sbrowser/files/1_tab1'
            tab.parent.mkdir(parents=True, exist_ok=True)
            entries = [
                _entry(0, 'https://a.example/', 'First', 8, TS, 200),
                _entry(1, 'https://b.example/', 'Second', 0x08000000, TS + 1000000, 404,
                       referrer='https://a.example/'),
            ]
            tab.write_bytes(_tab_file(False, 1, entries))
            headers, rows, sources = self.parse(root, [tab])

            self.assertEqual(len(headers), 11)
            self.assertEqual(len(rows), 2)
            # Columns: 0 time, 1 url, 2 title, 3 current, 4 index, 5 transition,
            #          6 http, 7 referrer, 8 original, 9 off_record, 10 source.
            self.assertEqual([r[1] for r in rows], ['https://a.example/', 'https://b.example/'])
            self.assertEqual([r[2] for r in rows], ['First', 'Second'])
            self.assertEqual([r[3] for r in rows], ['No', 'Yes'])     # current index 1
            self.assertEqual(rows[0][5], 'RELOAD')                    # transition 8
            self.assertEqual(rows[1][5], 'LINK (FROM_API)')          # 0x08000000
            self.assertEqual([r[6] for r in rows], [200, 404])
            self.assertEqual(rows[1][7], 'https://a.example/')       # referrer
            self.assertEqual([r[9] for r in rows], ['No', 'No'])     # off the record
            self.assertEqual(rows[0][0].year, 2021)                   # timestamp decoded
            self.assertEqual(sources, str(tab))

    def test_incognito_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tab = root / 'data/data/com.sec.android.app.sbrowser/files/1_tab2'
            tab.parent.mkdir(parents=True, exist_ok=True)
            tab.write_bytes(_tab_file(True, 0, [_entry(0, 'https://x.example/', 'X', 1, TS, 200)]))
            _headers, rows, _ = self.parse(root, [tab])
            self.assertEqual(rows[0][9], 'Yes')                       # off the record

    def test_corrupt_file_is_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            good = root / 'data/data/com.sec.android.app.sbrowser/files/1_tab1'
            good.parent.mkdir(parents=True, exist_ok=True)
            good.write_bytes(_tab_file(False, 0, [_entry(0, 'https://ok.example/', 'Ok', 1, TS, 200)]))
            bad = root / 'data/data/com.sec.android.app.sbrowser/files/1_tab9'
            # A size field that does not match the pickle's own length header: skipped.
            bad.write_bytes(b'\x00' * 8 + struct.pack('>I', 9999) + b'\x10\x00\x00\x00' + b'\x00' * 64)
            _headers, rows, sources = self.parse(root, [good, bad])
            self.assertEqual(len(rows), 1)                            # only the good file
            self.assertEqual(sources, str(good))                     # bad file not in sources


if __name__ == '__main__':
    unittest.main()
