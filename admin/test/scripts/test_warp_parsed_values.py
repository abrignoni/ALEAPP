"""Actual XML scalar fidelity and unchanged storage-view selection."""
from pathlib import Path
import hashlib
import itertools
import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.artifacts import cloudflareWarp as artifact  # pylint: disable=wrong-import-position
# The private helpers are inspected to verify the existing selection contract.
# pylint: disable=protected-access

PACKAGE = 'com.cloudflare.onedotonedotonedotone'
BASENAME = PACKAGE + '_preferences.xml'
SENTINEL = 'TEST-PRIVATE-KEY-NOT-FOR-ARTIFACT-OUTPUT'
LABELS = [
    ('warp_registration_id', 'Registration Id'),
    ('terms_acceptance_date', 'Terms Accepted'),
    ('registration_data_exec_timestamp', 'Registration Executed'),
    ('selected_tunnel_protocol', 'Tunnel Protocol'),
    ('vpn_profile_installed', 'VPN Profile Installed'),
    ('is_service_running', 'Service Running'),
    ('auto_connect', 'Auto Connect'),
    ('installer_package_name', 'Installed By'),
    ('onboardingstatus', 'Onboarding Status (as stored)'),
]


class Context:
    def __init__(self, root, files):
        self.root, self.files = Path(root), files

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


def hashes(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in Path(root).rglob('*') if p.is_file()}


def create_preferences(root, relative='data/data/' + PACKAGE, status='unknown', prefix=''):
    folder = Path(root) / relative / 'shared_prefs'
    folder.mkdir(parents=True, exist_ok=True)
    document = ET.Element('map')
    values = [prefix + '"registration"', '"2026-01-02T03:04:05-04:00"',
              '""2026-02-03T04:05:06+05:30', '""masque"""', '"',
              '""', 'false', '  "installer"  ', status]
    for (key, _), value in zip(LABELS, values):
        ET.SubElement(document, 'string', name=key).text = value
    # Attribute wins over text; the final duplicate wins without changing key order.
    ET.SubElement(document, 'string', name='auto_connect', value=' 0\t\n').text = 'ignored'
    ET.SubElement(document, 'string', name='selected_tunnel_protocol').text = '"final&\u03b1\n\tprotocol"'
    ET.SubElement(document, 'string', name='warp_account').text = json.dumps({
        'id': prefix + 'account', 'account_type': 'free', 'unreported_secret': SENTINEL})
    ET.SubElement(document, 'string', name='warp_private_key').text = SENTINEL
    ET.SubElement(document, 'string', name='unknown_key').text = SENTINEL
    ET.SubElement(document, 'string').text = 'nameless'
    path = folder / BASENAME
    path.write_bytes(ET.tostring(document, encoding='utf-8', xml_declaration=True))
    path.chmod(0o444)
    return path


def direct_rows(root, path):
    values = {}
    for node in ET.parse(path).getroot():
        key = node.attrib.get('name')
        if key:
            values[key] = node.attrib['value'] if 'value' in node.attrib else (node.text or '')
    rows = [(label, values[key], str(Path(path).relative_to(root)))
            for key, label in LABELS if key in values and values[key] != '']
    # These fixture account/key expectations are independent of the artifact decoder.
    account = json.loads(values['warp_account'])
    rows.extend([(label, value, str(Path(path).relative_to(root))) for label, value in [
        ('Account Id', account['id']), ('Account Type', 'free'),
        ('Private Key', 'present in the preferences file, not reported here')]])
    return rows


class TestParsedValues(unittest.TestCase):
    def test_quotes_entities_repeats_and_account_omissions(self):
        with tempfile.TemporaryDirectory() as root:
            path = create_preferences(root)
            before = hashes(root)
            headers, rows, source = artifact.cloudflare_warp_registration.__wrapped__(Context(root, [path]))
            self.assertEqual(headers, ('Item', 'Value (as stored)', 'Source File'))
            self.assertEqual(rows, direct_rows(root, path))
            self.assertEqual(source, str(path))
            self.assertEqual(len(rows), 12)
            self.assertEqual(rows[0][1], '"registration"')
            self.assertEqual(rows[3][1], '"final&\u03b1\n\tprotocol"')
            self.assertEqual(rows[5][1], '""')
            self.assertEqual(rows[6][1], ' 0\t\n')
            self.assertNotIn(SENTINEL, repr(rows))
            self.assertEqual(hashes(root), before)

    def test_onboarding_empty_absent_and_unknown_values(self):
        with tempfile.TemporaryDirectory() as root:
            for index, value in enumerate(['0', '1', 'false', 'true', 'pending', 'unknown', '', None, '""']):
                path = create_preferences(root, str(index) + '/data/data/' + PACKAGE, status=value)
                _, rows, _ = artifact.cloudflare_warp_registration.__wrapped__(Context(root, [path]))
                onboarding = [r for r in rows if r[0] == 'Onboarding Status (as stored)']
                self.assertEqual(onboarding, [] if value in ('', None) else [
                    ('Onboarding Status (as stored)', value, str(path.relative_to(root)))])
                self.assertEqual(rows, direct_rows(root, path))

    def test_attribute_empty_precedence_and_legal_control_entities(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'data/data' / PACKAGE / 'shared_prefs' / BASENAME
            path.parent.mkdir(parents=True)
            path.write_text('<map><string name="onboardingstatus" value="">nonempty</string>'
                            '<string name="warp_registration_id">&quot;&quot;</string>'
                            '<string name="auto_connect" value="&#9;&#10;&#13;&quot;"/>'
                            '<string name="is_service_running"> </string></map>')
            path.chmod(0o444)
            _, rows, _ = artifact.cloudflare_warp_registration.__wrapped__(Context(root, [path]))
            self.assertEqual([(r[0], r[1]) for r in rows], [
                ('Registration Id', '""'), ('Service Running', ' '), ('Auto Connect', '\t\n\r"')])

    def test_equal_conflicting_aliases_distinct_users_and_source_order(self):
        with tempfile.TemporaryDirectory() as root:
            preferred = create_preferences(root, prefix='preferred-')
            alias = create_preferences(root, 'data/user/0/' + PACKAGE, prefix='conflict-')
            equal = create_preferences(root, 'data_mirror/data_ce/null/0/' + PACKAGE, prefix='preferred-')
            user = create_preferences(root, 'data/user/10/' + PACKAGE, prefix='user10-')
            device = create_preferences(root, 'data/user_de/0/' + PACKAGE, prefix='de-')
            self.assertEqual(preferred.read_bytes(), equal.read_bytes())
            initial = hashes(root)
            for order in itertools.permutations([preferred, alias, user, device]):
                context = Context(root, [equal] + list(order))
                selected = artifact._prefs_files(context)
                self.assertEqual(set(selected), {str(preferred), str(user), str(device)})
                _, rows, source = artifact.cloudflare_warp_registration.__wrapped__(context)
                self.assertEqual(source.splitlines(), selected)
                self.assertEqual(rows, [r for p in selected for r in direct_rows(root, p)])
            self.assertEqual(hashes(root), initial)


if __name__ == '__main__':
    unittest.main()
