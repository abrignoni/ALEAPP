"""The call's phone account id is resolved to a SIM ICCID only through a recorded link."""
import datetime
import pathlib
import sqlite3
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts.calllog import get_calllog, get_calllog_phone_accounts, TELEPHONY_COMPONENT  # pylint: disable=wrong-import-position

# Synthetic identifiers, not from any device.
ICC_A = '8900000000000000001'
ICC_B = '8900000000000000002'
MESSAGING = 'com.samsung.android.messaging/com.samsung.android.messaging.ui.view.main.WithActivity'
TEAMS = 'com.microsoft.teams/com.microsoft.skype.teams.calling.telecom.TelecomConnectionService'

CALLS = [
    ('1', TELEPHONY_COMPONENT, ICC_A, 'siminfo subscription id'),
    ('2', TELEPHONY_COMPONENT, ICC_B, 'siminfo subscription id'),
    (ICC_A, TELEPHONY_COMPONENT, ICC_A, 'Stored value (matches siminfo)'),
    (ICC_B + 'F', TELEPHONY_COMPONENT, ICC_B, 'Stored value, trailing F removed (matches siminfo)'),
    (ICC_A, MESSAGING, ICC_A, 'Stored value (matches siminfo)'),
    ('1', MESSAGING, '', ''),
    ('9', TELEPHONY_COMPONENT, '', ''),
    ('3', TELEPHONY_COMPONENT, '', ''),
    ('8900000000000000009', TELEPHONY_COMPONENT, '', ''),
    ('0f6b0a8e-0000-0000-0000-000000000000', TEAMS, '', ''),
    (None, None, '', ''),
    ('', TELEPHONY_COMPONENT, '', ''),
]


def make_calllog(path, with_account_columns=True, dates=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    extra = ',subscription_id,subscription_component_name' if with_account_columns else ''
    con.execute('CREATE TABLE calls(date,phone_account_address,number,type,duration,geocoded_location,'
                f'countryiso,_data,mime_type,transcription,deleted{extra})')
    for index, (account_id, component, _, _) in enumerate(CALLS):
        values = [dates[index] if dates else 1700000000123, None, '+15551234567', 1, 5, None, 'US', None, None, None, 0]
        if with_account_columns:
            values += [account_id, component]
        con.execute(f'INSERT INTO calls VALUES({",".join("?" * len(values))})', values)
    con.commit()
    con.close()


def make_telephony(path, siminfo):
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    if siminfo is not None:
        con.execute('CREATE TABLE siminfo(_id INTEGER PRIMARY KEY, icc_id TEXT)')
        con.executemany('INSERT INTO siminfo VALUES(?,?)', siminfo)
    else:
        con.execute('CREATE TABLE carriers(_id INTEGER PRIMARY KEY)')
    con.commit()
    con.close()


def run(root, paths, artifact=get_calllog):
    context = SimpleNamespace(get_files_found=lambda: list(map(str, paths)),
                              get_relative_path=lambda p: str(pathlib.Path(p).relative_to(root)))
    return artifact.__wrapped__(context)


class CalllogSimIccidTest(unittest.TestCase):
    def test_resolution_paths_and_refusals(self):
        with tempfile.TemporaryDirectory() as root:
            base = pathlib.Path(root)
            calllog = base / 'data/data/com.android.providers.contacts/databases/calllog.db'
            telephony = base / 'data/user_de/0/com.android.providers.telephony/databases/telephony.db'
            second = base / 'data/user_de/10/com.android.providers.telephony/databases/telephony.db'
            make_calllog(calllog)
            # Subscription 3 maps to two different ICCIDs across the two files, so it is ambiguous.
            make_telephony(telephony, [(1, ICC_A), (2, ICC_B), (3, ICC_A)])
            make_telephony(second, [(3, ICC_B)])
            headers, rows, source = run(root, [calllog, telephony, second])
            self.assertEqual(headers[2:4], ('SIM ICCID', 'Phone Account Package'))
            self.assertEqual(len(rows), len(CALLS))
            for row, (_, component, iccid, _) in zip(rows, CALLS):
                self.assertEqual(row[2:4], (iccid, component.split('/')[0] if component else ''))
            self.assertEqual(source.splitlines(), [str(calllog), str(telephony), str(second)])

            headers, accounts, account_source = run(root, [calllog, telephony, second], get_calllog_phone_accounts)
            self.assertEqual(headers[2:7], ('SIM ICCID', 'ICCID Resolved Via', 'Phone Account ID (as stored)',
                                            'Phone Account Component', 'Calls'))
            expected = {}
            for account_id, component, iccid, via in CALLS:
                key = ('' if account_id is None else account_id, '' if component is None else component)
                count = expected.get(key, (iccid, via, 0))[2]
                expected[key] = (iccid, via, count + 1)
            self.assertEqual({(row[4], row[5]): (row[2], row[3], row[6]) for row in accounts}, expected)
            self.assertEqual(len(accounts), len(expected))
            self.assertEqual(sum(row[6] for row in accounts), len(CALLS))
            self.assertEqual(account_source, source)

    def test_no_siminfo_resolves_nothing_and_cites_no_telephony_db(self):
        with tempfile.TemporaryDirectory() as root:
            base = pathlib.Path(root)
            calllog = base / 'data/data/com.android.providers.contacts/databases/calllog.db'
            telephony = base / 'data/user_de/0/com.android.providers.telephony/databases/telephony.db'
            make_calllog(calllog)
            make_telephony(telephony, None)
            _, rows, source = run(root, [calllog, telephony])
            self.assertEqual(len(rows), len(CALLS))
            self.assertEqual({row[2] for row in rows}, {''})
            self.assertEqual(source, str(calllog))

    def test_table_without_account_columns_keeps_its_rows(self):
        with tempfile.TemporaryDirectory() as root:
            base = pathlib.Path(root)
            calllog = base / 'data/data/com.android.providers.contacts/databases/calllog.db'
            telephony = base / 'data/user_de/0/com.android.providers.telephony/databases/telephony.db'
            make_calllog(calllog, with_account_columns=False)
            make_telephony(telephony, [(1, ICC_A)])
            _, rows, source = run(root, [calllog, telephony])
            self.assertEqual(len(rows), len(CALLS))
            self.assertEqual({row[2:4] for row in rows}, {('', '')})
            self.assertEqual(source, str(calllog))

    def test_accounts_first_last_and_order(self):
        with tempfile.TemporaryDirectory() as root:
            base = pathlib.Path(root)
            calllog = base / 'data/data/com.android.providers.contacts/databases/calllog.db'
            second_user = base / 'data/user/10/com.android.providers.contacts/databases/calllog.db'
            telephony = base / 'data/user_de/0/com.android.providers.telephony/databases/telephony.db'
            dates = [1700000000000 + 1000 * (len(CALLS) - index) for index in range(len(CALLS))]
            dates[0] = 0  # A missing date is counted but does not set First Call or Last Call.
            make_calllog(calllog, dates=dates)
            make_calllog(second_user, dates=[1600000000000] * len(CALLS))
            make_telephony(telephony, [(1, ICC_A), (2, ICC_B)])
            _, accounts, _ = run(root, [calllog, second_user, telephony], get_calllog_phone_accounts)
            self.assertEqual(sum(row[6] for row in accounts), 2 * len(CALLS))
            firsts = [row[0] for row in accounts]
            self.assertEqual(firsts, sorted(firsts))
            subscription_one = next(row for row in accounts if (row[4], row[5]) == ('1', TELEPHONY_COMPONENT))
            utc = datetime.timezone.utc
            self.assertEqual(subscription_one[0], datetime.datetime.fromtimestamp(1600000000, utc))
            self.assertEqual(subscription_one[1], datetime.datetime.fromtimestamp(1600000000, utc))
            self.assertEqual(subscription_one[6], 2)

    def test_telephony_db_alone_returns_nothing(self):
        with tempfile.TemporaryDirectory() as root:
            telephony = pathlib.Path(root) / 'data/user_de/0/com.android.providers.telephony/databases/telephony.db'
            make_telephony(telephony, [(1, ICC_A)])
            _, rows, source = run(root, [telephony])
            self.assertEqual((rows, source), ([], ''))


if __name__ == '__main__':
    unittest.main()
