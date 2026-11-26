"""Mastodon account rows carry the token creation time and the two refresh times the app stores
beside the account. The access token itself is not reported. All values here are made up."""
import json
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import mastodon


def account_row(entry):
    with tempfile.TemporaryDirectory() as folder:
        path = pathlib.Path(folder) / 'org.joinmastodon.android/files/accounts.json'
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({'accounts': [entry]}))
        context = SimpleNamespace(get_files_found=lambda: [str(path)])
        headers, rows, _source = mastodon.get_mastodon_accounts.__wrapped__(context)
    names = [h[0] if isinstance(h, tuple) else h for h in headers]
    return dict(zip(names, rows[0])), headers


ENTRY = {'a': {'access_token': 'SECRET-TOKEN', 'token_type': 'Bearer', 'scope': 'read', 'created_at': 1700000000},
         'b': {'acct': 'user', 'created_at': '2023-01-01T00:00:00.000Z'}, 'c': 'example.social',
         'e': 1700000100123, 'l': 1700000200456, 'j': {'alerts': {}}}


class AccountTimes(unittest.TestCase):
    def test_the_three_stored_times_are_reported(self):
        row, _headers = account_row(ENTRY)
        self.assertEqual(row['Token Created'].isoformat(), '2023-11-14T22:13:20+00:00')
        self.assertEqual(row['Account Info Updated'].isoformat(), '2023-11-14T22:15:00.123000+00:00')
        self.assertEqual(row['Filters Updated'].isoformat(), '2023-11-14T22:16:40.456000+00:00')

    def test_the_time_columns_lead_the_row(self):
        _row, headers = account_row(ENTRY)
        self.assertEqual([h[0] for h in headers[:4]], ['Token Created', 'Account Info Updated', 'Filters Updated', 'Created Timestamp'])

    def test_the_access_token_is_not_reported(self):
        row, _headers = account_row(ENTRY)
        self.assertNotIn('SECRET-TOKEN', [str(v) for v in row.values()])

    def test_missing_times_are_blank(self):
        entry = {k: v for k, v in ENTRY.items() if k not in ('a', 'e', 'l')}
        row, _headers = account_row(entry)
        self.assertEqual((row['Token Created'], row['Account Info Updated'], row['Filters Updated']), ('', '', ''))


if __name__ == '__main__':
    unittest.main()
