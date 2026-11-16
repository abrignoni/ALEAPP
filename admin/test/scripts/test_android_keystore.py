# pylint: disable=protected-access
import unittest

from scripts.artifacts import androidKeystore as ks


def _encode_alias(name):
    '''legacy_blob.rs encode_alias: bytes '0'..'~' kept, others as two characters.'''
    out = []
    for c in name.encode('utf-8'):
        if ord('0') <= c <= ord('~'):
            out.append(chr(c))
        else:
            out.append(chr(ord('+') + (c >> 6)))
            out.append(chr(ord('0') + (c & 0x3F)))
    return ''.join(out)


class DecodeAliasTest(unittest.TestCase):
    def test_round_trip(self):
        for alias in ('plain_alias', 'with space', 'a.b-c', 'café', '中文', ''):
            self.assertEqual(ks._decode_alias(_encode_alias(alias)), alias)

    def test_bad_encoding_is_none(self):
        self.assertIsNone(ks._decode_alias('+'))        # escape with no second character
        self.assertIsNone(ks._decode_alias('+p'))       # second character out of range
        self.assertIsNone(ks._decode_alias('a b'))      # space is never stored unescaped

    def test_file_name_forms(self):
        key = ks._LEGACY_NAME.match('10223_USRPKEY_' + _encode_alias('my key'))
        self.assertEqual((key.group('uid'), key.group('prefix'), key.group('chr'), key.group('c')),
                         ('10223', 'USRPKEY', None, None))
        chars = ks._LEGACY_NAME.match('.10223_chr_USRPKEY_authbound')
        self.assertEqual((chars.group('chr'), chars.group('c'), chars.group('alias')), ('.', 'chr_', 'authbound'))
        self.assertIsNone(ks._LEGACY_NAME.match('.masterkey'))


class OwnerTest(unittest.TestCase):
    def test_fixed_aid_wins_over_shared_packages(self):
        packages = {1000: ['android', 'com.android.settings'], 10144: ['com.example.a', 'com.example.b']}
        self.assertEqual(ks._uid_owner(1000, packages), 'AID system')
        self.assertEqual(ks._uid_owner(1010144, packages), 'com.example.a; com.example.b')   # user 10
        self.assertEqual(ks._uid_owner(10999, packages), '')
        self.assertEqual(ks._uid_owner(None, packages), '')

    def test_ms_to_utc(self):
        self.assertEqual(ks._ms_to_utc(0), '')
        self.assertEqual(ks._ms_to_utc(1000).isoformat(), '1970-01-01T00:00:01+00:00')


if __name__ == '__main__':
    unittest.main()
