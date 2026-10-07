"""Exact stored default tuples preserve account-grain rows across XML and ABX."""
import itertools
import pathlib
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from types import SimpleNamespace
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from admin.test.scripts.test_android_user_indexes import write_abx
from scripts.artifacts import telecomPhoneAccounts as parser


def context(root, paths):
    return SimpleNamespace(get_files_found=lambda: paths,
                           get_relative_path=lambda p: str(pathlib.Path(p).relative_to(root)))


def text(parent, name, value):
    ET.SubElement(parent, name).text = value


def handle(parent, key, inner_serial=None):
    node = ET.SubElement(ET.SubElement(parent, 'account_handle'), 'phone_account_handle')
    text(node, 'component_name', key[0]);text(node, 'id', key[1])
    text(node, 'user_serial_number', key[2] if inner_serial is None else inner_serial)


def fixture_xml(keys, defaults, missing_accounts=(), missing_defaults=(), nested=()):
    root = ET.Element('phone_account_registrar_state')
    outgoing = ET.SubElement(root, 'default_outgoing')
    for index, key in enumerate(defaults):
        node = ET.SubElement(outgoing, 'default_outgoing_phone_account_handle')
        if index not in missing_defaults:handle(node, key, 'inner-not-used')
        text(node, 'user_serial_number', key[2])
    for key in nested:
        node = ET.SubElement(ET.SubElement(root, 'unrelated'), 'default_outgoing_phone_account_handle')
        handle(node, key);text(node, 'user_serial_number', key[2])
    accounts = ET.SubElement(root, 'accounts')
    for index, key in enumerate(keys):
        node = ET.SubElement(accounts, 'phone_account')
        if index not in missing_accounts:handle(node, key)
        for name, value in [('label', f'Account {index}'), ('handle', 'tel:%2B12025550123'),
                            ('subscription_number', 'tel:%2B12025550124'), ('short_description', 'stored'),
                            ('enabled', 'true'), ('capabilities', '12'), ('highlight_color', '-1'),
                            ('supported_audio_routes', '5')]:text(node, name, value)
        schemes = ET.SubElement(node, 'supported_uri_schemes')
        for value in ['tel', '', 'sip']:text(schemes, 'value', value)
    return ET.tostring(root, encoding='unicode')


def write(root, relative, xml, binary=False):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if binary:return str(write_abx(path, xml))
    path.write_text(xml, encoding='utf-8')
    return str(path)


class TelecomDefaultTupleTest(unittest.TestCase):
    def test_actual_xml_abx_multiuser_duplicates_and_all_native_cells(self):
        keys = [('component', 'id', '0'), ('component', 'id', '10'), ('other', 'id', '10'), ('', '', '')]
        defaults = [keys[0], keys[1], keys[1], ('', '', '')]
        xml = fixture_xml(keys, defaults, missing_accounts=(3,), nested=(keys[2],))
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            for binary in [False, True]:
                path = write(root, str(binary)+'/phone-account-registrar-state.xml', xml, binary)
                headers, rows, source = parser.telecom_phone_accounts.__wrapped__(context(root, [path]))
                self.assertEqual(len(headers), 14)
                self.assertEqual(len(rows), 4)
                self.assertEqual(source, path)
                relative = str(pathlib.Path(path).relative_to(root))
                for index, (key, row) in enumerate(zip(keys, rows)):
                    self.assertEqual(row, (f'Account {index}', 'tel:+12025550123', 'tel:+12025550124', 'stored', *key, 'true', index<2, 'tel, sip', '12', '-1', '5', relative))
                    self.assertIs(type(row[8]), bool)

    def test_partial_empty_and_missing_inner_no_wildcards(self):
        keys = list(itertools.product(['', 'component'], ['', 'id'], ['', '10']))
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            for default in keys:
                path = write(root, 'data/phone-account-registrar-state.xml', fixture_xml(keys, [default]))
                _, rows, _ = parser.telecom_phone_accounts.__wrapped__(context(root, [path]))
                self.assertEqual([r[8] for r in rows], [key==default and any(default) for key in keys])
            path = write(root, 'data/phone-account-registrar-state.xml', fixture_xml(keys, [('', '', '10')], missing_defaults=(0,)))
            _, rows, _ = parser.telecom_phone_accounts.__wrapped__(context(root, [path]))
            self.assertTrue(all(not r[8] for r in rows))
            path = write(root, 'data/phone-account-registrar-state.xml', fixture_xml(keys, []))
            _, rows, _ = parser.telecom_phone_accounts.__wrapped__(context(root, [path]))
            self.assertTrue(all(not r[8] for r in rows))
            key = ('component', 'id', '10')
            tree = ET.fromstring(fixture_xml([key], []))
            second = ET.fromstring(fixture_xml([], [(' component ', ' id ', ' 10 ')]))
            tree.append(second.find('default_outgoing'))
            path = write(root, 'data/phone-account-registrar-state.xml', ET.tostring(tree, encoding='unicode'), True)
            _, rows, _ = parser.telecom_phone_accounts.__wrapped__(context(root, [path]))
            self.assertTrue(rows[0][8])
            tree = ET.fromstring(fixture_xml([('component', 'id', '')], [('component', 'id', '')]))
            default = tree.find('default_outgoing/default_outgoing_phone_account_handle')
            default.remove(default.find('user_serial_number'))
            path = write(root, 'data/phone-account-registrar-state.xml', ET.tostring(tree, encoding='unicode'))
            _, rows, _ = parser.telecom_phone_accounts.__wrapped__(context(root, [path]))
            self.assertTrue(rows[0][8])

    def test_files_stay_local_and_repeated_account_rows_remain(self):
        key = ('component', 'id', '0')
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            first = write(root, 'first/phone-account-registrar-state.xml', fixture_xml([key, key], [key, key]))
            last = write(root, 'last/phone-account-registrar-state.xml', fixture_xml([key], []), True)
            _, rows, source = parser.telecom_phone_accounts.__wrapped__(context(root, [first, last]))
            self.assertEqual([r[8] for r in rows], [True, True, False])
            self.assertEqual(source, first+'\n'+last)
            self.assertEqual([r[-1] for r in rows], ['first/phone-account-registrar-state.xml']*2+['last/phone-account-registrar-state.xml'])


if __name__ == '__main__':
    unittest.main()
