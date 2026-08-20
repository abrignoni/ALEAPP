__artifacts_v2__ = {
    "get_metamask_addresses": {
        "name": "Metamask - User Addresses",
        "description": "Extract user associated cryptocurrency addresses from the Metamask wallet",
        "author": "CH-Clark",
        "creation_date": "2026-08-10",
        "last_update_date": "2026-08-11",
        "requirements": "none",
        "category": "Cryptocurrency",
        "notes": "",
        "paths": ('*/io.metamask/files/persistStore/persist-AccountsController*',),
        "output_types": "standard",
        "artifact_icon": "currency-bitcoin",
    },
    "get_metamask_contacts": {
        "name": "Metamask - User Contacts",
        "description": "Extract user associated cryptocurrency address contacts from the MetaMask wallet",
        "author": "CH-Clark",
        "creation_date": "2026-08-11",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "Cryptocurrency",
        "notes": "",
        "paths": ('*/io.metamask/files/persistStore/persist-AddressBookController*',),
        "output_types": "standard",
        "artifact_icon": "currency-bitcoin",
    },
}

import json
from scripts.ilapfuncs import artifact_processor

@artifact_processor
def get_metamask_addresses(context):
    files_found = context.get_files_found()

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('persist-AccountsController'):
            continue

    source_path = file_found
    with open(source_path, 'r') as file:
        read_data = file.read()
        json_obj = json.loads(read_data)
        internalAccounts = json_obj['internalAccounts']
        accounts = internalAccounts['accounts']

        for ids in accounts:
            account_data = accounts[ids]
            addresses = account_data.get('address')

            data_list.append((addresses,))

    data_headers = ('User Addresses',)
    return data_headers, data_list, source_path

@artifact_processor
def get_metamask_contacts(context):
    files_found = context.get_files_found()

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('persist-AddressBookController'):
            continue
        
    source_path = file_found
    with open(source_path, 'r') as file:
        read_data = file.read()
        json_obj = json.loads(read_data)
        addressBook = json_obj['addressBook']

        for chain_id in addressBook:
            addresses_for_chain = addressBook[chain_id]

            for address_key in addresses_for_chain:
                details = addresses_for_chain[address_key]

                address = details['address']
                name = details['name']
                memo = details['memo']

                data_list.append((address, name, memo))

    data_headers = ('User Contact Address', 'Name', 'Memo')
    return data_headers, data_list, source_path