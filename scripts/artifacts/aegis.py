__artifacts_v2__ = {
    "aegis_vault": {
        "name": "Aegis - Vault",
        "description": "Reports the state of the Aegis Android 2FA vault, including whether it is encrypted.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Aegis",
        "notes": "One row per aegis.json vault file in the app's files directory. Aegis stores every "
                 "two factor entry in this one JSON vault. The vault can be plaintext or encrypted, "
                 "and this artifact reports which: when the header carries encryption slots the db "
                 "field is a base64 string and the entries cannot be read without the user's password, "
                 "and the Entry Count is reported as unknown for that case; when it is plaintext the "
                 "entries are readable and are listed by the Entries artifact. Aegis encrypts the whole "
                 "vault with a key derived from the password, so an encrypted vault yields no issuers "
                 "or account names from a logical extraction, which is itself the finding rather than "
                 "an absence of 2FA. The Encryption column reports whether slots are present and how "
                 "many, as stored.",
        "paths": ('*/com.beemdevelopment.aegis/files/aegis.json',),
        "output_types": "standard",
        "artifact_icon": "shield-lock"
    },
    "aegis_entries": {
        "name": "Aegis - Entries",
        "description": "Parses the two factor authentication entries stored by the Aegis Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Aegis",
        "notes": "One row per two factor entry in a plaintext aegis.json vault, showing which services "
                 "and accounts the user has set up two factor authentication for. Issuer is the "
                 "service, Name is the account at that service, and the remaining columns are the OTP "
                 "parameters: Type, Algorithm, Digits and Period. Type is one of the values defined by "
                 "the app, totp, hotp, steam, motp or yandex "
                 "(app/src/main/java/com/beemdevelopment/aegis/otp at beemdevelopment/Aegis 17a87a4e); "
                 "any other value is reported as stored. Favorite, Note and Groups are the user's own "
                 "labels; Groups is resolved from the group ids on the entry to the group names in the "
                 "same vault. The shared secret is deliberately not reported: the forensic value here "
                 "is which services have two factor set up, not the secrets that generate the codes. If "
                 "the vault is encrypted this artifact returns nothing, because the entries are not "
                 "readable without the password; the Vault artifact reports that the vault is "
                 "encrypted. The UUID is the entry's own identifier in the vault.",
        "paths": ('*/com.beemdevelopment.aegis/files/aegis.json',),
        "output_types": "standard",
        "artifact_icon": "shield-check"
    }
}

import json
import os

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.artifacts.storagePathViews import unique_files

# OTP type ids defined by the app at beemdevelopment/Aegis 17a87a4e.
OTP_TYPES = {'totp', 'hotp', 'steam', 'motp', 'yandex'}


def _vault_files(context):
    for file_found in unique_files(context):
        file_found = str(file_found).replace('\\', '/')
        if os.path.isdir(file_found) or not file_found.endswith('aegis.json'):
            continue
        try:
            with open(file_found, 'r', encoding='utf-8') as handle:
                loaded = json.load(handle)
        except (OSError, ValueError) as error:
            logfunc(f'Aegis: could not read {file_found}: {error}')
            continue
        if isinstance(loaded, dict):
            yield loaded, file_found


def _is_encrypted(vault):
    """(encrypted, slot_count). The db is a base64 string and slots are set when encrypted."""
    header = vault.get('header') or {}
    slots = header.get('slots')
    db = vault.get('db')
    encrypted = isinstance(db, str) or bool(slots)
    slot_count = len(slots) if isinstance(slots, list) else 0
    return encrypted, slot_count


@artifact_processor
def aegis_vault(context):
    data_list = []
    sources = []
    for vault, file_found in _vault_files(context):
        encrypted, slot_count = _is_encrypted(vault)
        db = vault.get('db')
        entry_count = len(db.get('entries', [])) if isinstance(db, dict) else 'Unknown (encrypted)'
        encryption = f'Encrypted ({slot_count} slots)' if encrypted else 'None (plaintext)'
        data_list.append((
            vault.get('version', ''),
            db.get('version', '') if isinstance(db, dict) else '',
            encryption,
            entry_count,
            context.get_relative_path(file_found),
        ))
        if file_found not in sources:
            sources.append(file_found)

    data_headers = ('Vault Version', 'Database Version', 'Encryption', 'Entry Count',
                    'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def aegis_entries(context):
    data_list = []
    sources = []
    for vault, file_found in _vault_files(context):
        db = vault.get('db')
        if not isinstance(db, dict):
            logfunc(f'Aegis: {file_found} is encrypted, so its entries were not read')
            continue
        group_names = {}
        for group in db.get('groups', []) or []:
            if isinstance(group, dict) and group.get('uuid'):
                group_names[group['uuid']] = group.get('name', '')
        read_any = False
        for entry in db.get('entries', []) or []:
            if not isinstance(entry, dict):
                continue
            info = entry.get('info') or {}
            entry_type = entry.get('type', '')
            groups = entry.get('groups') or []
            group_label = ', '.join(group_names.get(g, g) for g in groups)
            data_list.append((
                entry_type if entry_type in OTP_TYPES else f'{entry_type} (as stored)',
                entry.get('issuer', '') or '',
                entry.get('name', '') or '',
                info.get('algo', '') or '',
                info.get('digits', ''),
                info.get('period', info.get('counter', '')),
                'Yes' if entry.get('favorite') else '',
                entry.get('note', '') or '',
                group_label,
                entry.get('uuid', '') or '',
                context.get_relative_path(file_found),
            ))
            read_any = True
        if read_any and file_found not in sources:
            sources.append(file_found)

    data_headers = ('Type', 'Issuer', 'Name', 'Algorithm', 'Digits', 'Period or Counter',
                    'Favorite', 'Note', 'Groups', 'UUID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
