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
                 "server, the Last Sync time, the Vault Timeout in minutes, and the App Install "
                 "ID as stored. Dates in the profile are ISO "
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
                 "was on the tested device. For an examiner with lawful authority to attempt offline "
                 "recovery of the vault: where KDF Type is PBKDF2 SHA256, the Master Key is derived from "
                 "the master password with PBKDF2-SHA256, using the account email as the salt and the "
                 "KDF Iterations reported here (the white paper gives 600,000 as the default); that key "
                 "is stretched with HKDF and used to encrypt a randomly generated symmetric key, which "
                 "the white paper calls the main key associated with the user, so that key is wrapped "
                 "by, not derived from, the master password. The stored master password hash is a "
                 "further PBKDF2-SHA256 pass over the Master Key (Bitwarden Security Whitepaper, "
                 "https://bitwarden.com/help/bitwarden-security-white-paper/). At bitwarden/android "
                 "59d0faaf1266a03ccddc2809332cfa9c95393f78 the app writes the keyHash and "
                 "localUserDataKey entries with a plain putString call (AuthDiskSourceImpl.kt lines 522 "
                 "and 275), so both are present in this preferences file as stored. This artifact does "
                 "not output that material, but it can be read directly from the same preferences file: "
                 "the master password hash is the keyHash_<user id> entry, the unlock salt is under "
                 "masterPasswordUnlock.salt in the profile, and a wrapped key is stored in the "
                 "localUserDataKey_<user id> entry. The app source names it the local user data key, and "
                 "what it wraps was not established here. The encrypted items are in "
                 "databases/vault_database, and the account Email reported above serves as the KDF salt. "
                 "Those values, assembled "
                 "into the input format expected by password-recovery tooling such as John the Ripper "
                 "(bitwarden2john), are what such a tool consumes; recovering plaintext still requires "
                 "the master password or a successful attack against that material.",
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
        "author": "@AlexisBrignoni, Claude, Codex",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Bitwarden",
        "notes": "One row per entry in the ciphers table of databases/vault_database. Bitwarden is end "
                 "to end encrypted and the contents of a vault item are not recovered here: within each "
                 "row's stored JSON the name, username, password and item key are Bitwarden EncString "
                 "values, whose layout is not sourced here, and the key that opens them is a randomly "
                 "generated key that is itself encrypted under a key derived from the master password "
                 "(Bitwarden Security Whitepaper, "
                 "https://bitwarden.com/help/bitwarden-security-white-paper/); this artifact does not "
                 "recover the master password. On the tested device an item was saved with a known name "
                 "and the whole app directory was then searched for that name, which returned nothing. "
                 "What the same JSON does hold in plain text, and what is reported here, is the item's "
                 "metadata: the Item ID, the owning User ID, the Type, the Created and Last Revised "
                 "dates, the favorite and reprompt fields as compact status documents with their parsed "
                 "values encoded as JSON text, and the Organization ID where the item belongs to an organisation rather than "
                 "the personal vault. That gives an examiner how many items a vault held, of what kinds, "
                 "and when each was created and last changed, without their contents. Type is decoded "
                 "from the app's own enum, 1 login, 2 secure note, 3 card, 4 identity, 5 SSH key, 6 bank "
                 "account, 7 drivers licence, 8 passport (CipherTypeJson.kt at bitwarden/android "
                 "59d0faaf1266a03ccddc2809332cfa9c95393f78); any other value is reported as stored. "
                 "Dates are ISO 8601 with a Z suffix and are reported as UTC. Field documents distinguish "
                 "missing keys, explicit null, false, zero, invalid input and non-object roots; non-object "
                 "documents contain only the root kind. Inner JSON text follows Python JSON semantics, "
                 "including NaN and Infinity extensions. It preserves parsed values rather than original "
                 "bytes, number spelling or duplicate object keys. No favorite or reprompt enum meaning is "
                 "assigned. Truthy non-object roots remain unsupported by the existing row projection. "
                 "Three sibling tables in "
                 "the same database are not parsed here and were empty on the tested device: folders, "
                 "collections and sends; what they hold was not measured. The database runs in WAL mode "
                 "and held its rows in the -wal "
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


def _field_document(raw, field):
    """Report one parsed JSON field without conflating absence with false."""
    if raw is None:
        document = {'status': 'sql_null_input'}
    elif not isinstance(raw, (str, bytes, bytearray)):
        document = {'status': 'unsupported_json_input_type'}
    elif len(raw) == 0:
        document = {'status': 'empty_input'}
    else:
        try:
            root = json.loads(raw)
        except (TypeError, ValueError):
            document = {'status': 'invalid_json'}
        else:
            if isinstance(root, dict):
                if field in root:
                    document = {'status': 'present', 'json': json.dumps(
                        root[field], ensure_ascii=True, separators=(',', ':'))}
                else:
                    document = {'status': 'missing_key'}
            else:
                kinds = {type(None): 'null', bool: 'boolean', int: 'integer',
                         float: 'float', str: 'string', list: 'array'}
                document = {'status': 'decoded_non_object', 'root_kind': kinds[type(root)]}
    return json.dumps(document, ensure_ascii=True, separators=(',', ':'), allow_nan=False)


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
            data_list.append((
                _iso(payload.get('creationDate')), _iso(payload.get('revisionDate')),
                record[0] or '', _lookup(CIPHER_TYPES, record[2]),
                _field_document(record[3], 'favorite'),
                _field_document(record[3], 'reprompt'),
                record[4] or '', record[1] or '', rel,
            ))
        if counted and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Created', 'datetime'), ('Last Revised', 'datetime'), 'Item ID', 'Type',
        'favorite (typed JSON)', 'reprompt (typed JSON)', 'Organization ID', 'User ID', 'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)
