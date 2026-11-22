"""Netstats identity columns: blank when the version lacks a field, No when it stores false."""
import io
import pathlib
import re
import struct
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.artifacts.netstats import (  # noqa: E402
    ConnectionType, NetworkIdentitySet, format_rat_type, identity_columns)


def optional_string(value):
    if value is None:
        return b'\x00'
    encoded = value.encode('utf-8')
    return b'\x01' + struct.pack('>H', len(encoded)) + encoded


def identity_bytes(version, rat_type=13, roaming=False, metered=False, default_network=False,
                   sub_id=3, network='network'):
    """One identity written with the fields its set version stores."""
    data = b''
    if version <= NetworkIdentitySet.IDENT_VERSION_INIT:
        data += struct.pack('>i', 0)
    data += struct.pack('>ii', ConnectionType.TYPE_MOBILE, rat_type)
    data += optional_string('subscriber')
    if version >= NetworkIdentitySet.IDENT_VERSION_ADD_NETWORK_ID:
        data += optional_string(network)
    if version >= NetworkIdentitySet.IDENT_VERSION_ADD_ROAMING:
        data += bytes([roaming])
    if version >= NetworkIdentitySet.IDENT_VERSION_ADD_METERED:
        data += bytes([metered])
    if version >= NetworkIdentitySet.IDENT_VERSION_ADD_DEFAULT_NETWORK:
        data += bytes([default_network])
    if version >= NetworkIdentitySet.IDENT_VERSION_ADD_OEM_MANAGED_NETWORK:
        data += struct.pack('>i', -1)
    if version >= NetworkIdentitySet.IDENT_VERSION_ADD_SUB_ID:
        data += struct.pack('>i', sub_id)
    if version >= NetworkIdentitySet.IDENT_VERSION_ADD_TRANSPORT_TYPES:
        data += struct.pack('>q', 0)
    return data


def columns(version, *identities):
    stream = io.BytesIO(struct.pack('>ii', version, len(identities)) + b''.join(identities))
    parsed = NetworkIdentitySet.read(stream)
    assert stream.read() == b''
    return identity_columns(parsed.identities)


class NetstatsIdentityColumns(unittest.TestCase):
    def test_each_field_starts_at_its_version(self):
        expected = {
            1: ('', '', '', ''), 2: ('No', '', '', ''), 3: ('No', '', '', ''),
            4: ('No', 'No', '', ''), 5: ('No', 'No', 'No', ''), 6: ('No', 'No', 'No', ''),
            7: ('No', 'No', 'No', '3'), 8: ('No', 'No', 'No', '3')}
        for version, (roaming, metered, default_network, sub_id) in expected.items():
            with self.subTest(version=version):
                row = columns(version, identity_bytes(version))
                self.assertEqual((row[1], row[2], row[3], row[5]),
                                 (roaming, metered, default_network, sub_id))

    def test_stored_true_is_yes(self):
        row = columns(8, identity_bytes(8, roaming=True, metered=True, default_network=True))
        self.assertEqual(row[1:4], ('Yes', 'Yes', 'Yes'))

    def test_rat_type_labels_and_unknown_value(self):
        self.assertEqual(format_rat_type(-2), '5G_NSA (-2)')
        self.assertEqual(format_rat_type(-1), 'ALL (-1)')
        self.assertEqual(format_rat_type(0), 'UNKNOWN (0)')
        self.assertEqual(format_rat_type(20), 'NR (20)')
        self.assertEqual(format_rat_type(99), '99')

    def test_several_identities_keep_their_order(self):
        row = columns(7,
                      identity_bytes(7, rat_type=13, roaming=True, sub_id=1),
                      identity_bytes(7, rat_type=20, metered=True, sub_id=2))
        self.assertEqual(row[0], 'TYPE_MOBILE: subscriber network | TYPE_MOBILE: subscriber network')
        self.assertEqual(row[1], 'Yes | No')
        self.assertEqual(row[2], 'No | Yes')
        self.assertEqual(row[4], 'LTE (13) | NR (20)')
        self.assertEqual(row[5], '1 | 2')

    def test_blank_field_keeps_its_position(self):
        row = columns(6, identity_bytes(6), identity_bytes(6))
        self.assertEqual(row[5], ' | ')

    def test_stored_trailing_space_is_kept(self):
        row = columns(7, identity_bytes(7, network='net '), identity_bytes(7))
        self.assertEqual(row[0], 'TYPE_MOBILE: subscriber net  | TYPE_MOBILE: subscriber network')

    def test_separator_inside_a_value_is_escaped(self):
        row = columns(7, identity_bytes(7, network='a | b'), identity_bytes(7, network='c\\d'))
        self.assertEqual(row[0], 'TYPE_MOBILE: subscriber a \\| b | TYPE_MOBILE: subscriber c\\\\d')
        unescaped = [len(re.findall(r'(?<!\\) \| ', value)) for value in row]
        self.assertEqual(unescaped, [1] * 6)

    def test_one_identity_stays_as_stored(self):
        row = columns(7, identity_bytes(7, network='a | b\\c '))
        self.assertEqual(row[0], 'TYPE_MOBILE: subscriber a | b\\c  ')

    def test_one_identity_has_no_separator(self):
        row = columns(8, identity_bytes(8))
        self.assertNotIn('|', ''.join(row))


if __name__ == '__main__':
    unittest.main()
