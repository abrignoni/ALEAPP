__artifacts_v2__ = {
    "get_moonpay_addresses": {
        "name": "Moonpay - User Addresses",
        "description": "Extract user associated cryptocurrency addresses from Moonpay wallet",
        "author": "CH-Clark",
        "creation_date": "2026-08-17",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Cryptocurrency",
        "notes": "",
        "paths": ('*/com.moonpay/files/mmkv/mmkv-storage*',),
        "output_types": "standard",
        "artifact_icon": "currency-bitcoin",
    },
}

import json
from scripts.mmkv_parser import read_dict, MMKVError
from scripts.ilapfuncs import artifact_processor

CHAIN_NAME_MAP = {
    'bitcoinAddress': 'Bitcoin',
    'evmAddress': 'EVM',
    'solanaAddress': 'Solana',
    'rippleAddress': 'Ripple',
    'tronAddress': 'TRON',
}

@artifact_processor
def get_moonpay_addresses(context):
    files_found = context.get_files_found()

    data_list = []
    source_path = ''

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('mmkv-storage'):
            continue

        try:
            source_path = file_found
            data = read_dict(file_found)

        except MMKVError as e:
            print(e)
            continue

    user_info = data.get('REACT_QUERY_OFFLINE_CACHE')
    if user_info is not None:
        json_obj = json.loads(user_info)
        clientState = json_obj['clientState']
        queries = clientState['queries']

        for items in queries:
            state = items.get('state',{})
            data_field = state.get('data')

            if isinstance(data_field, dict) and 'moonpayWallets' in data_field:
                datatest = data_field['moonpayWallets']
            
                if isinstance(datatest, dict):
                    for key, value in datatest.items():
                        label = CHAIN_NAME_MAP.get(key, key)
                        data_list.append((label, value))

    data_headers = ('Type', 'Address')
    return data_headers, data_list, source_path