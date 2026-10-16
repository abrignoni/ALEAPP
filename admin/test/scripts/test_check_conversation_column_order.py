"""Keep unconverted date companions near dates without assigning a timezone."""
import importlib.util
from pathlib import Path
import unittest

_PATH = Path(__file__).resolve().parents[2] / 'scripts' / 'check_conversation_column_order.py'
_SPEC = importlib.util.spec_from_file_location('conversation_column_order', _PATH)
_CHECK = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_CHECK)


class TestStoredDateOrder(unittest.TestCase):
    def test_raw_timestamp_companion_precedes_message_roles(self):
        names = ['Timestamp', 'Timestamp (as stored)', 'Direction', 'Message']
        kinds = ['datetime', 'text', 'text', 'text']
        view = {'timeColumn': 'Timestamp', 'directionColumn': 'Direction', 'textColumn': 'Message'}
        self.assertEqual(_CHECK.expected(names, kinds, view), [0, 1, 2, 3])

    def test_unrelated_stored_values_stay_after_message_roles(self):
        names = ['Timestamp', 'Identifier (as stored)', 'Direction', 'Message']
        kinds = ['datetime', 'text', 'text', 'text']
        view = {'timeColumn': 'Timestamp', 'directionColumn': 'Direction', 'textColumn': 'Message'}
        self.assertEqual(_CHECK.expected(names, kinds, view), [0, 2, 3, 1])

    def test_misplaced_companion_is_reordered(self):
        names = ['Timestamp', 'Direction', 'Message', 'Timestamp (as stored)']
        kinds = ['datetime', 'text', 'text', 'text']
        view = {'timeColumn': 'Timestamp', 'directionColumn': 'Direction', 'textColumn': 'Message'}
        self.assertEqual(_CHECK.expected(names, kinds, view), [0, 3, 1, 2])


if __name__ == '__main__':
    unittest.main()
