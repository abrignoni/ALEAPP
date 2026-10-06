"""Hosts aliases remain physical-line evidence, without network-event inference."""
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from admin.test.scripts.test_sdhms_stat_sources import context
from scripts.artifacts import etc_hosts as parser


class HostsLineRetentionTest(unittest.TestCase):
    def test_bytes_alias_occurrences_default_pairs_and_later_healthy(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(parser, 'logfunc') as logger:
            root = pathlib.Path(folder)
            path = root/'system/etc/hosts'
            path.parent.mkdir(parents=True)
            physical = [b'\xef\xbb\xbf127.0.0.1 localhost added added\r\n', b'  # comment\r\n',
                        b'\n', b'::1 ip6-localhost other # trailing ignored\n', b'lonely\n',
                        b'192.0.2.1 first second\\ # no continuation\n', b'continued\n',
                        b'192.0.2.2 invalid\xff\n', b'192.0.2.3 final']
            path.write_bytes(b''.join(physical))
            headers, rows, source = parser.get_etc_hosts.__wrapped__(context(root, [path]))
            self.assertEqual(headers[:2], ('IP Address', 'Hostname'))
            self.assertEqual(source, str(path))
            self.assertEqual([r[:4] for r in rows], [
                ('127.0.0.1','added',1,2), ('127.0.0.1','added',1,3), ('::1','other',4,2),
                ('lonely','',5,None), ('192.0.2.1','first',6,1), ('192.0.2.1','second\\',6,2),
                ('continued','',7,None), ('192.0.2.2','invalid\ufffd',8,1), ('192.0.2.3','final',9,1)])
            for row in rows:
                self.assertEqual(bytes.fromhex(row[-1]), physical[row[2]-1])
                self.assertEqual(row[-2], physical[row[2]-1].decode('utf-8', errors='replace').rstrip('\r\n'))
            self.assertEqual(rows[-2][4], 'Stored alias; replacement UTF-8 display')
            self.assertEqual(logger.call_count, 2)

    def test_single_selected_input_repeats_and_literal_replacement_character(self):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            first = root/'first';second = root/'second'
            first.write_bytes('not-an-ip token token\nnot-an-ip \ufffd\n'.encode())
            second.write_text('192.0.2.2 excluded\n')
            _, rows, source = parser.get_etc_hosts.__wrapped__(context(root, [first, second]))
            self.assertEqual(len(rows), 3)
            self.assertEqual([r[1] for r in rows], ['token','token','\ufffd'])
            self.assertEqual(rows[-1][4], 'Stored alias')
            self.assertEqual(source, str(first))


if __name__ == '__main__':
    unittest.main()
