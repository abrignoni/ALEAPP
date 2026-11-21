__artifacts_v2__ = {
    "google_contact_keys": {
        "name": "Google Contact Keys",
        "description": "Records of end-to-end encryption keys held by Android's Contact Keys "
                       "provider (com.google.android.contactkeys): the account, device, owning app, update time and verification "
                       "state of each key.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-21",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "Google Contact Keys",
        "notes": "Read from com.google.android.contactkeys/databases/contactkeys_room with its "
                 "write-ahead log. The log matters: on dragna_pixel9a_a16 the 6 contact_keys rows "
                 "are only in the log, and the database file alone holds 2 self_keys rows that the "
                 "log removes, which are not reported. Key Owner is Contact for a contact_keys row "
                 "and Self for a self_keys row. The label names the table only: on anne_a15 and "
                 "kevin_pocox7_a15 one Contact row holds the same key and account as a Self row. "
                 "Account ID, Device ID, Owner App, Time Updated, Display Name, Phone Number, Email "
                 "Address and the verification columns follow the fields of Android's "
                 "E2eeContactKeysManager classes E2eeContactKey and E2eeSelfKey (SDK android.jar, "
                 "API 37.2). Account ID and Device ID are reported as stored. Display Name, Phone "
                 "Number and Email Address come from contact_infos, and a key with several "
                 "contact_infos rows gets one row for each. No key on the seven images in sample_data had more than one. Android "
                 "User is the user whose storage holds the database. Verification values are named "
                 "from the SDK's VERIFICATION_STATE constants: 0 UNVERIFIED, 1 VERIFICATION_FAILED "
                 "and 2 VERIFIED. On the seven images in sample_data (27 rows, 16 Contact), Remote "
                 "Verification held UNVERIFIED (0) on every row and Local Verification held "
                 "UNVERIFIED (0) on every Contact row. Local Verification is blank on Self rows "
                 "because self_keys has no such column. Time Updated is time_updated read as Unix "
                 "milliseconds. The provider also changes it when it updates or resets a "
                 "verification state, so it does not establish when a key was first received. Key "
                 "SHA-256 is computed by this artifact over key_value and is blank when key_value is "
                 "empty (1 row on kevin_pocox7_a15, which also has an empty Device ID). The key "
                 "itself is not reported. Email Address was empty on all 27 rows, Android User held "
                 "0 on all 27 rows, and Owner App held one value, the same one, on the seven images. "
                 "On dragna_pixel9a_a16 Key Owner held Contact on all 6 rows, and Display Name and "
                 "Phone Number were empty on all 6 rows because contact_infos held no rows. A row "
                 "shows that the provider holds a key record for an account under an owner app. It "
                 "does not establish a conversation or that messages were encrypted with that key. "
                 "The verifications, verified_keys, verified_contact_infos, kt_lookup_records, "
                 "kt_self_key_audit_records, self_key_history, package_certificates, settings and "
                 "onboarding_shown tables are not read. They held no rows on the seven images. The "
                 "kt_last_lookup_timestamp and kt_last_self_audit_timestamp columns were NULL where "
                 "present and are not read.",
        "paths": ('*/com.google.android.contactkeys/databases/contactkeys_room*',),
        "output_types": "standard",
        "artifact_icon": "key",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | 6 rows (6 Contact)",
            "kevin_pocox7_a15": "Android 15 | 6 rows (4 Contact, 2 Self)",
            "anne_a15": "Android 15 | 5 rows (4 Contact, 1 Self)",
            "hc_pixel8pro_a17": "Android 17 | 4 rows (2 Contact, 2 Self)",
            "hc_pixel8pro_a16": "Android 16 | 2 rows (2 Self)",
            "samsunga53_a14": "Android 14 | 2 rows (2 Self)",
            "adams_ss135dl_a13": "Android 13 | 2 rows (2 Self)",
        },
    },
}

import hashlib
import sqlite3
from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import android_user, unique_files
from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly

# android.provider.E2eeContactKeysManager.VERIFICATION_STATE_*
_VERIFICATION = {0: 'UNVERIFIED', 1: 'VERIFICATION_FAILED', 2: 'VERIFIED'}
_CONTACT_KEYS = '''
    SELECT k.time_updated, k.account_id, k.device_id, k.owner_package_name, i.display_name,
           i.phone_number, i.email_address, k.local_verification_state,
           k.remote_verification_state, k.key_value
    FROM contact_keys k LEFT JOIN contact_infos i ON i.contact_key_id = k.contact_key_id
    ORDER BY k.time_updated'''
_SELF_KEYS = '''
    SELECT time_updated, account_id, device_id, owner_package_name, NULL, NULL, NULL, NULL,
           remote_verification_state, key_value
    FROM self_keys ORDER BY time_updated'''


def _time(value):
    if not isinstance(value, int) or value <= 0:
        return ''
    try:
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _state(value):
    if value is None:
        return ''
    name = _VERIFICATION.get(value)
    return f'{name} ({value})' if name else str(value)


def _row(kind, user, record):
    updated, account, device, package, name, phone, email, local, remote, key = record
    digest = hashlib.sha256(key).hexdigest() if isinstance(key, bytes) and key else ''
    return (_time(updated), kind, user, account or '', device or '', package or '', name or '',
            phone or '', email or '', _state(local), _state(remote), digest)


@artifact_processor
def google_contact_keys(context):
    data_headers = (('Time Updated', 'datetime'), 'Key Owner', 'Android User', 'Account ID', 'Device ID',
                    'Owner App', 'Display Name', ('Phone Number', 'phonenumber'), 'Email Address',
                    'Local Verification', 'Remote Verification', ('Key SHA-256', 'hash'))
    data_list, sources = [], []
    for file_found in unique_files(context):
        path = str(file_found)
        if not path.endswith('contactkeys_room'):
            continue
        db = open_sqlite_db_readonly(path)
        if db is None:
            continue
        sources.append(path)
        user = android_user(context.get_relative_path(path))
        for kind, query in (('Contact', _CONTACT_KEYS), ('Self', _SELF_KEYS)):
            try:
                data_list.extend(_row(kind, user, record) for record in db.execute(query).fetchall())
            except sqlite3.Error as error:
                logfunc(f'Google Contact Keys: could not read the {kind} keys: {error}')
        db.close()
    data_list.sort(key=lambda row: (row[0] == '', str(row[0])))
    return data_headers, data_list, '\n'.join(sources)
