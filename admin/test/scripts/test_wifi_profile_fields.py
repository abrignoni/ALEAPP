"""Wi-Fi profiles report the stored creator, updater, MAC and connection fields, the store each
profile came from, and the Passpoint providers. All values here are made up."""
import base64
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import wifiProfiles

NETWORK = '''<Network>
<WifiConfiguration>
<string name="ConfigKey">&quot;Example&quot;WPA_PSK</string>
<string name="SSID">&quot;Example&quot;</string>
<boolean name="HiddenSSID" value="true" />
<int name="CreatorUid" value="1000" />
<string name="CreatorName">android.uid.system:1000</string>
<int name="LastUpdateUid" value="10123" />
<string name="LastUpdateName">com.example.app</string>
<string name="RandomizedMacAddress">aa:bb:cc:dd:ee:ff</string>
<int name="MacRandomizationSetting" value="3" />
</WifiConfiguration>
<NetworkStatus>
<boolean name="HasEverConnected" value="true" />
</NetworkStatus>
</Network>'''

PASSWORD = base64.b64encode(b'secret').decode() + '\n'
PROVIDER = f'''<Provider>
<int name="CreatorUID" value="1010" />
<string name="PackageName">com.example.provider</string>
<boolean name="HasEverConnected" value="false" />
<Configuration>
<long name="SubscriptionCreationTime" value="-9223372036854775808" />
<long name="SubscriptionExpirationTime" value="1700000000000" />
<HomeSP>
<string name="FQDN">example.com</string>
<string name="FriendlyName">Example Provider</string>
</HomeSP>
<Credential>
<long name="CreationTime" value="1600000000000" />
<long name="ExpirationTime" value="-9223372036854775808" />
<string name="Realm">example.com</string>
<UserCredential>
<string name="Username">user</string>
<string name="Password">{PASSWORD}</string>
</UserCredential>
</Credential>
<SubscriptionUpdate>
<string name="Username">update-user</string>
<string name="Password">dXBkYXRl</string>
</SubscriptionUpdate>
</Configuration>
</Provider>'''

SIM_PROVIDER = '''<Provider>
<Configuration>
<HomeSP><string name="FQDN">sim.example</string></HomeSP>
<Credential><SimCredential><string name="IMSI">123456*</string></SimCredential></Credential>
</Configuration>
</Provider>'''


def store(body):
    return f'<WifiConfigData><NetworkList>{body}</NetworkList></WifiConfigData>'


def passpoint(body):
    return f'<WifiConfigData><PasspointConfigData><ProviderList>{body}</ProviderList></PasspointConfigData></WifiConfigData>'


def run(artifact, files):
    """Headers and rows for {relative path: xml text}."""
    with tempfile.TemporaryDirectory() as folder:
        root = pathlib.Path(folder)
        found = []
        for relative, text in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
            found.append(str(path))
        context = SimpleNamespace(get_files_found=lambda: found,
                                  get_relative_path=lambda p: str(pathlib.Path(p).relative_to(root)))
        headers, rows, _source = getattr(wifiProfiles, artifact).__wrapped__(context)
    names = [h[0] if isinstance(h, tuple) else h for h in headers]
    return [dict(zip(names, row)) for row in rows]


SHARED = 'data/misc/apexdata/com.android.wifi/WifiConfigStore.xml'
USER = 'data/misc_ce/10/apexdata/com.android.wifi/WifiConfigStore.xml'


class NetworkFields(unittest.TestCase):
    def test_stored_fields_are_reported(self):
        row = run('get_wifiProfiles', {SHARED: store(NETWORK)})[0]
        self.assertEqual(row['HiddenSSID'], 'true')
        self.assertEqual(row['HasEverConnected'], 'true')
        self.assertEqual(row['CreatorName'], 'android.uid.system:1000')
        self.assertEqual(row['CreatorUid'], '1000')
        self.assertEqual(row['LastUpdateName'], 'com.example.app')
        self.assertEqual(row['LastUpdateUid'], '10123')
        self.assertEqual(row['RandomizedMacAddress'], 'aa:bb:cc:dd:ee:ff')
        self.assertEqual(row['MacRandomizationSetting'], '3 (auto)')

    def test_an_unknown_randomization_value_is_shown_as_stored(self):
        row = run('get_wifiProfiles', {SHARED: store(NETWORK.replace('value="3"', 'value="7"'))})[0]
        self.assertEqual(row['MacRandomizationSetting'], '7')

    def test_store_names_shared_or_user(self):
        rows = run('get_wifiProfiles', {SHARED: store(NETWORK), USER: store(NETWORK)})
        self.assertEqual(sorted(r['Store'] for r in rows), ['Shared', 'User 10'])


class PasspointProviders(unittest.TestCase):
    def test_provider_fields_are_reported(self):
        row = run('get_wifiPasspointProviders', {USER: passpoint(PROVIDER)})[0]
        self.assertEqual(row['FQDN'], 'example.com')
        self.assertEqual(row['FriendlyName'], 'Example Provider')
        self.assertEqual(row['Realm'], 'example.com')
        self.assertEqual(row['PackageName'], 'com.example.provider')
        self.assertEqual(row['CreatorUID'], '1010')
        self.assertEqual(row['HasEverConnected'], 'false')
        self.assertEqual(row['Store'], 'User 10')

    def test_the_user_credential_is_read_not_the_update_server_login(self):
        row = run('get_wifiPasspointProviders', {USER: passpoint(PROVIDER)})[0]
        self.assertEqual(row['Username'], 'user')
        self.assertEqual(row['Password (as stored)'], PASSWORD)
        self.assertEqual(row['Password (Base64 decoded)'], 'secret')

    def test_unset_times_are_blank_and_set_times_are_utc(self):
        row = run('get_wifiPasspointProviders', {USER: passpoint(PROVIDER)})[0]
        self.assertEqual(row['Credential CreationTime'].year, 2020)
        self.assertEqual(row['Credential ExpirationTime'], '')
        self.assertEqual(row['SubscriptionCreationTime'], '')
        self.assertEqual(row['SubscriptionExpirationTime'].year, 2023)

    def test_a_sim_credential_gives_its_imsi(self):
        row = run('get_wifiPasspointProviders', {USER: passpoint(SIM_PROVIDER)})[0]
        self.assertEqual(row['IMSI'], '123456*')
        self.assertEqual((row['Username'], row['Password (Base64 decoded)']), ('', ''))

    def test_a_password_that_is_not_base64_is_not_decoded(self):
        row = run('get_wifiPasspointProviders', {USER: passpoint(PROVIDER.replace(PASSWORD, 'not base64!'))})[0]
        self.assertEqual(row['Password (as stored)'], 'not base64!')
        self.assertEqual(row['Password (Base64 decoded)'], '')

    def test_no_provider_gives_no_rows(self):
        self.assertEqual(run('get_wifiPasspointProviders', {SHARED: store(NETWORK)}), [])



MIRROR = 'data_mirror/misc_ce/null/10/apexdata/com.android.wifi/WifiConfigStore.xml'


class MirrorCopies(unittest.TestCase):
    def test_an_identical_mirror_copy_is_read_once(self):
        rows = run('get_wifiPasspointProviders', {USER: passpoint(PROVIDER), MIRROR: passpoint(PROVIDER)})
        self.assertEqual([r['Store'] for r in rows], ['User 10'])

    def test_a_mirror_copy_that_differs_is_read(self):
        rows = run('get_wifiPasspointProviders', {USER: passpoint(PROVIDER), MIRROR: passpoint(SIM_PROVIDER)})
        self.assertEqual(sorted(r['FQDN'] for r in rows), ['example.com', 'sim.example'])
        self.assertEqual({r['Store'] for r in rows}, {'User 10'})

    def test_a_mirror_under_another_evidence_root_is_read(self):
        rows = run('get_wifiPasspointProviders', {f'one/{USER}': passpoint(PROVIDER), f'two/{MIRROR}': passpoint(PROVIDER)})
        self.assertEqual(len(rows), 2)

    def test_a_mirror_beside_its_live_copy_under_a_root_is_read_once(self):
        rows = run('get_wifiPasspointProviders', {f'one/{USER}': passpoint(PROVIDER), f'one/{MIRROR}': passpoint(PROVIDER)})
        self.assertEqual(len(rows), 1)

    def test_a_mirror_copy_alone_is_read_and_names_its_user(self):
        rows = run('get_wifiPasspointProviders', {MIRROR: passpoint(PROVIDER)})
        self.assertEqual([r['Store'] for r in rows], ['User 10'])


if __name__ == '__main__':
    unittest.main()
