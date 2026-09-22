__artifacts_v2__ = {
    "get_atomic_wallet_addresses": {
        "name": "Atomic Wallet - User Addresses",
        "description": "Extract user associated cryptocurrency addresses from the Atomic wallet",
        "author": "CH-Clark",
        "creation_date": "2026-08-13",
        "last_update_date": "2026-08-13",
        "requirements": "none",
        "category": "Cryptocurrency",
        "notes": "",
        "paths": ('*/io.atomicwallet/app_webview/Default/Local Storage/leveldb/*',),
        "output_types": "standard",
        "artifact_icon": "currency-bitcoin",
    },
}

import json
import pathlib
from scripts.ilapfuncs import artifact_processor
from ccl_chromium_reader import ccl_chromium_localstorage

@artifact_processor
def get_atomic_wallet_addresses(context):
    files_found = context.get_files_found()
    data_list = []
    source_path = ''

    leveldb_dir = None
    for file_found in files_found:
        if file_found.endswith('.ldb') or file_found.endswith(".log"):
            file_path = pathlib.Path(file_found)
            leveldb_dir = file_path.parent
            break

    if leveldb_dir:
        
        # Create the LocalStoreDb object which is used to access the data
        with ccl_chromium_localstorage.LocalStoreDb(leveldb_dir) as local_storage:
            for storage_key in local_storage.iter_storage_keys():
            
                for record in local_storage.iter_records_for_storage_key(storage_key):
                    # we can attempt to associate this record with a batch, which may
                    # provide an approximate timestamp (withing 5-60 seconds) for this
                    # record.
                    batch = local_storage.find_batch(record.leveldb_seq_number)
                    timestamp = batch.timestamp if batch else None

                    if 'addresses' in record.script_key:
                        json_obj = json.loads(record.value)

                        for item in json_obj:
                            ticker = item['id']
                            address = item['address']
                            data_list.append((ticker, address,))

    data_headers = ('ID', 'Address',)
    return data_headers, data_list, source_path