__artifacts_v2__ = {
    "bitwarden_account": {
        "name": "Bitwarden - Account",
        "description": "Parses the account profile stored by the Bitwarden Android password manager.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Bitwarden",
        "notes": "One row per reported account setting, read from the plain text preferences file "
                 "shared_prefs/com.x8bit.bitwarden_preferences.xml. Bitwarden encrypts the vault, but "
                 "the signed-in account's own profile is kept unencrypted in this file, inside the JSON "
                 "held under the state key. Reported from that profile: the User ID, the account Email "
                 "and Name, the account Created date, whether the email is verified, whether two factor "
                 "is enabled, the KDF Type and KDF Iterations used to derive the master key, and whether "
                 "a premium subscription applies. Reported from the surrounding keys: the Server URL the "
                 "client is configured for, which distinguishes the hosted service from a self-hosted "
                 "server, the Last Sync time, the Vault Timeout in minutes, and the App Install ID, "
                 "which the app generates and keeps for the installation. Dates in the profile are ISO "
                 "8601 with a Z suffix and are reported as UTC; Last Sync is Unix milliseconds and is "
                 "also reported as UTC. Several values in the same file are deliberately not reported "
                 "because they are credential material rather than evidence of activity: the keyHash "
                 "entry, which is the master password hash, the security stamp, the master password "
                 "unlock salt, the encrypted user keys, and the push notification tokens. KDF Type is "
                 "decoded from the app's own enum, 0 PBKDF2 SHA256 and 1 Argon2id (KdfTypeJson.kt at "
                 "bitwarden/android 59d0faaf1266a03ccddc2809332cfa9c95393f78); any other value is "
                 "reported as stored. A setting the app never wrote is absent rather than empty. The app "
                 "supports more than one signed-in account at a time and keeps a separate profile for "
                 "each, so rows are keyed by User ID and the Active Account column marks the one the app "
                 "was last using; with a single account signed in that column is uniformly Yes, as it "
                 "was on the tested device.",
        "paths": ('*/com.x8bit.bitwarden/shared_prefs/com.x8bit.bitwarden_preferences.xml',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "emu_a15_oss_v3": "Android 15 | com.x8bit.bitwarden vc 21819 | 14 rows; settings for one signed-in account",
        },
    },
    "bitwarden_vault_items": {
        "name": "Bitwarden - Vault Items",
        "description": "Parses the vault item records stored by the Bitwarden Android password manager.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Bitwarden",
        "notes": "One row per entry in the ciphers table of databases/vault_database. Bitwarden is end "
                 "to end encrypted and the contents of a vault item are not recovered here: within each "
                 "row's stored JSON the name, username, password and item key are Bitwarden EncString "
                 "values, which carry an encryption type prefix followed by the initialisation vector, "
                 "ciphertext and MAC, and the key that opens them is derived from the master password, "
                 "which is not in the extraction. Confirmed on the tested device by saving an item with "
                 "a known name and then searching the whole app directory for it, which returned "
                 "nothing. What the same JSON does hold in plain text, and what is reported here, is the "
                 "item's metadata: the Item ID, the owning User ID, the Type, the Created and Last "
                 "Revised dates, whether it is a Favorite, whether the item requires a master password "
                 "reprompt to view, and the Organization ID where the item belongs to an organisation "
                 "rather than the personal vault. That gives an examiner how many items a vault held, of "
                 "what kinds, and when each was created and last changed, without their contents. Type "
                 "is decoded from the app's own enum, 1 login, 2 secure note, 3 card, 4 identity, 5 SSH "
                 "key, 6 bank account, 7 drivers licence, 8 passport (CipherTypeJson.kt at "
                 "bitwarden/android 59d0faaf1266a03ccddc2809332cfa9c95393f78); any other value is "
                 "reported as stored. Dates are ISO 8601 with a Z suffix and are reported as UTC. Three "
                 "sibling tables in the same database are not parsed here and were empty on the tested "
                 "device: folders and collections hold encrypted names only, and sends holds encrypted "
                 "Bitwarden Send records. The database runs in WAL mode and held its rows in the -wal "
                 "sidecar on the tested device, so the sidecar is in the paths and is required.",
        "paths": ('*/com.x8bit.bitwarden/databases/vault_database*',),
        "output_types": "standard",
        "artifact_icon": "lock",
        "sample_data": {
            "emu_a15_oss_v3": "Android 15 | com.x8bit.bitwarden vc 21819 | 1 rows",
        },
    }
}

import json
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

PREFS_SUFFIX = 'shared_prefs/com.x8bit.bitwarden_preferences.xml'
DB_SUFFIX = 'databases/vault_database'

# CipherTypeJson.kt and KdfTypeJson.kt at bitwarden/android
# 59d0faaf1266a03ccddc2809332cfa9c95393f78.
CIPHER_TYPES = {
    1: 'Login', 2: 'Secure note', 3: 'Card', 4: 'Identity',
    5: 'SSH key', 6: 'Bank account', 7: 'Drivers licence', 8: 'Passport',
}
KDF_TYPES = {0: 'PBKDF2 SHA256', 1: 'Argon2id'}

PREFIX = 'bwPreferencesStorage:'


def _files(context, suffix):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(suffix)]


def _lookup(table, value):
    # cipher_type is stored as TEXT in the database and kdfType as a JSON number,
    # so normalise to int before looking the label up.
    key = value
    if isinstance(key, str):
        try:
            key = int(key)
        except ValueError:
            pass
    if key in table:
        return table[key]
    return f'{value} (as stored)'


def _iso(value):
    if not value:
        return ''
    return str(value).replace('T', ' ').replace('Z', '+00:00')


def _ms(value):
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value) // 1000)
    except (TypeError, ValueError):
        return ''


def _read_prefs(path):
    values = {}
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError):
        return values
    for node in root:
        name = node.get('name') or ''
        if not name.startswith(PREFIX):
            continue
        raw = node.get('value')
        if raw is None:
            raw = node.text or ''
        values[name[len(PREFIX):]] = raw
    return values


def _json(raw):
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return None


@artifact_processor
def bitwarden_account(context):
    data_list = []
    sources = []
    for prefs_path in _files(context, PREFS_SUFFIX):
        values = _read_prefs(prefs_path)
        state = _json(values.get('state'))
        if not isinstance(state, dict):
            continue
        rel = context.get_relative_path(prefs_path)
        if prefs_path not in sources:
            sources.append(prefs_path)
        accounts = state.get('accounts') or {}
        for user_id, account in accounts.items():
            profile = (account or {}).get('profile') or {}
            settings = (account or {}).get('settings') or {}
            environment = settings.get('environmentUrls') or {}
            reported = [
                ('User ID', user_id),
                ('Email', profile.get('email')),
                ('Name', profile.get('name')),
                ('Account Created', _iso(profile.get('creationDate'))),
                ('Email Verified', profile.get('emailVerified')),
                ('Two Factor Enabled', profile.get('isTwoFactorEnabled')),
                ('KDF Type', _lookup(KDF_TYPES, profile.get('kdfType'))
                 if profile.get('kdfType') is not None else None),
                ('KDF Iterations', profile.get('kdfIterations')),
                ('Premium Personally', profile.get('hasPremiumPersonally')),
                ('Premium From Organization', profile.get('hasPremiumFromOrganization')),
                ('Server URL', environment.get('base')),
                ('Last Sync', _ms(values.get(f'vaultLastSyncTime_{user_id}'))),
                ('Vault Timeout (minutes)', values.get(f'vaultTimeout_{user_id}')),
                ('App Install ID', values.get('appId')),
            ]
            active = 'Yes' if state.get('activeUserId') == user_id else 'No'
            for setting, value in reported:
                if value is None or value == '':
                    continue
                data_list.append((user_id, active, setting, str(value), rel))

    data_headers = ('User ID', 'Active Account', 'Setting', 'Value', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def bitwarden_vault_items(context):
    query = '''SELECT id, user_id, cipher_type, cipher_json, organization_id
               FROM ciphers ORDER BY id'''
    data_list = []
    sources = []
    for db_path in _files(context, DB_SUFFIX):
        records = get_sqlite_db_records(db_path, query)
        rel = context.get_relative_path(db_path)
        counted = False
        for record in records:
            counted = True
            payload = _json(record[3]) or {}
            reprompt = payload.get('reprompt')
            data_list.append((
                _iso(payload.get('creationDate')), _iso(payload.get('revisionDate')),
                record[0] or '', _lookup(CIPHER_TYPES, record[2]),
                'Yes' if payload.get('favorite') else 'No',
                'Yes' if reprompt else 'No',
                record[4] or '', record[1] or '', rel,
            ))
        if counted and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Created', 'datetime'), ('Last Revised', 'datetime'), 'Item ID', 'Type',
        'Favorite', 'Master Password Reprompt', 'Organization ID', 'User ID', 'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)
