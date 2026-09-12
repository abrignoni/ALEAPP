__artifacts_v2__ = {
    "get_bitcoincom_addresses": {
        "name": "Bitcoin.com - User Addresses",
        "description": "Extract user associated cryptocurrency addresses from the Bitcoin.com wallet",
        "author": "CH-Clark",
        "creation_date": "2026-08-13",
        "last_update_date": "2026-08-13",
        "requirements": "",
        "category": "Cryptocurrency",
        "notes": """This script dumps extended public keys from the Bitcoin.com wallet, these could be derived 
                using the 'bip_utils' module, but i think its best not to add too many requirements and the associated
                addresses can be derived at iancoleman.io/bip39/.""",
        "paths": ('*/com.bitcoin.mwallet/databases/com.bitcoin.mwallet.wallet-db*',),
        "output_types": "standard",
        "artifact_icon": "currency-bitcoin",
    },
    "get_bitcoincom_mnemonics": {
        "name": "Bitcoin.com - Wallet Mnemonics",
        "description": "Extract user associated cryptocurrency wallet mnemonics from the Bitcoin.com wallet",
        "author": "CH-Clark",
        "creation_date": "2026-08-13",
        "last_update_date": "2026-08-13",
        "requirements": "",
        "category": "Cryptocurrency",
        "notes": """""",
        "paths": ('*/com.bitcoin.mwallet/databases/com.bitcoin.mwallet.wallet-db*',),
        "output_types": "standard",
        "artifact_icon": "currency-bitcoin",
    },
}

import json
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly

@artifact_processor
def get_bitcoincom_addresses(context):
    files_found = context.get_files_found()

    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('com.bitcoin.mwallet.wallet-db'):
            continue

        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute('''
            SELECT
                x.public_key AS xpub,
                a.ticker     AS ticker,
                a.name       AS name
            FROM wallet w
            JOIN address_source_xpub x
                ON w.address_source_id = x.id_id
            JOIN asset_info a
                ON UPPER(w.coin) = a.ticker
        ''')

        all_rows = cursor.fetchall()
        db.close()

    for item in all_rows:
        data_list.append((item))

    data_headers = ('Extended Public key (XPUB)', 'Asset ID', 'Asset Name')
    return data_headers, data_list, source_path


@artifact_processor
def get_bitcoincom_mnemonics(context):
    files_found = context.get_files_found()

    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('com.bitcoin.mwallet.wallet-db'):
            continue
        
        source_path = file_found
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()

        cursor.execute('''
            SELECT credential_mnemonic.mnemonic
            From credential_mnemonic
        ''')

        all_rows = cursor.fetchall()
        db.close()

    for row in all_rows:
        raw_json = row[0]
        parsed = json.loads(raw_json)
        mnemonic = parsed['value']

        data_list.append((mnemonic,))

    data_headers = ('mnemonic',)
    return data_headers, data_list, source_path