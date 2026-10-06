"""Missing fields do not collide with stored strings or falsy values."""
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
from scripts.artifacts import AIChatbotNovaSharedPrefs as nova
from admin.test.scripts.test_history_doclist_all_sources import Context


def create_adapty_fixture(root):
    path = Path(root)/'data/data/com.scaleup.chatai/shared_prefs/AdaptySDKPrefs.xml'
    path.parent.mkdir(parents=True, exist_ok=True)
    xml = ET.Element('map')
    for attrs in [{}, {'is_test_user': None, 'total_revenue_usd': 0,
                       'custom_attributes': {'oldAppInstanceId': 'None', 'paywallType': False}},
                  {'is_test_user': False, 'total_revenue_usd': '',
                   'custom_attributes': {'oldAppInstanceId': ' ', 'paywallType': 'None'}}]:
        ET.SubElement(xml, 'string', name='PROFILE').text = json.dumps({'attributes': attrs})
    ET.SubElement(xml, 'string', name='LAST_SENT_INSTALLATION_META').text = json.dumps({'unchanged': None})
    ET.ElementTree(xml).write(path, encoding='utf-8')
    return [path]


class TestAdaptyMissingValues(unittest.TestCase):
    def test_missing_null_falsy_and_literal_values(self):
        with tempfile.TemporaryDirectory() as directory:
            files = create_adapty_fixture(directory)
            _, rows, _ = nova.get_nova_adapty_prefs.__wrapped__(Context(directory, files))
            self.assertEqual([row[2] for row in rows],
                             ['', '', '', '', '', 'None', '0', 'False',
                              'False', ' ', '', 'None', 'None'])
            self.assertEqual(rows[-1][:2], ('Installation Meta', 'unchanged'))
