__artifacts_v2__ = {
    "breadwallet_transaction_metadata": {
        "name": "BRD (BreadWallet) - Transaction Metadata Records",
        "description": "Transaction metadata records held in the BRD key-value store, giving the "
                       "transaction hash each record is keyed on and when the record was first "
                       "and last written",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "BRD (BreadWallet)",
        "notes": "Read from the kvStoreTable of databases/platform.db, taking the rows whose key "
                 "begins with 'txn2-'.\n"
                 "What these rows are is taken from the application's own code, not inferred. The "
                 "APK carried in the extraction (data/app/com.breadwallet-*/base.apk) names the "
                 "constant TX_META_DATA_KEY_PREFIX, builds these keys in a method named "
                 "getTxMetaDataKey, reads the rows into a class "
                 "com.breadwallet.platform.entities.TxMetaData, contains the query "
                 "\"...where key like 'txn2-%'\", and declares an event whose text begins "
                 "OnTransactionMetaDataUpdated(transactionHash=. The part of the key after the "
                 "prefix is reported under Transaction Hash on that basis; it is 64 hexadecimal "
                 "characters in the tested corpus.\n"
                 "The stored value is encrypted and is NOT decoded. Every value in this table "
                 "begins with a fixed header followed by high-entropy bytes, and no key for it "
                 "was found in the extraction. So the transaction amount, the counterparty, any "
                 "user memo and the comment fields a TxMetaData record can hold are not "
                 "recovered. What this artifact establishes is that a metadata record exists for "
                 "that transaction hash, and when it was written.\n"
                 "The store keeps every version of a key rather than overwriting, so First "
                 "Written and Last Written come from the lowest and highest version of that key "
                 "and Version Count is how many were kept.\n"
                 "The whole of platform.db lived in its write-ahead log on the tested corpus: "
                 "read without the WAL the table has no rows at all. The sidecars are in the "
                 "paths above and must travel with the database.",
        "paths": ('*/com.breadwallet/databases/platform.db*',),
        "output_types": "standard",
        "artifact_icon": "hash",
        "sample_data": {
            "galaxys10_a10": "Android 10 | BRD | 3 rows",
        },
    },
    "breadwallet_kv_store": {
        "name": "BRD (BreadWallet) - Key-Value Store",
        "description": "Records in the BRD key-value store, with the key, the version, when it "
                       "was written and the size of the stored value",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "BRD (BreadWallet)",
        "notes": "Read from the kvStoreTable of databases/platform.db, without filtering, so the "
                 "transaction metadata rows the BRD - Transaction Metadata Records artifact "
                 "reports separately also appear here.\n"
                 "The values are encrypted and are not decoded; only the size is reported. The "
                 "keys are stored in the clear and are what this artifact is for: they name what "
                 "the wallet held records about, and their timestamps show when.\n"
                 "Keys observed on the tested corpus were wallet-info, asset-index, the "
                 "plat-vuex-* application state keys, and the txn2- transaction metadata keys. "
                 "The meaning of the wallet-info and asset-index keys beyond their names is not "
                 "established here; asset-index appears in APK log strings about migrating from "
                 "an earlier token-list-metadata key.\n"
                 "Rows are kept per version rather than overwritten, so the same key appears more "
                 "than once with different versions and times.\n"
                 "The whole of platform.db lived in its write-ahead log on the tested corpus, so "
                 "the sidecars must travel with the database.",
        "paths": ('*/com.breadwallet/databases/platform.db*',),
        "output_types": "standard",
        "artifact_icon": "database",
        "sample_data": {
            "galaxys10_a10": "Android 10 | BRD | 38 rows",
        },
    },
    "breadwallet_app_state": {
        "name": "BRD (BreadWallet) - App State",
        "description": "The BRD account identifier and application state held in shared "
                       "preferences, including the recovery phrase written flag and the wallet "
                       "reward identifier",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "BRD (BreadWallet)",
        "notes": "Read from shared_prefs/MyPrefsFile.xml.\n"
                 "Every value is reported under the preference name the app stored it against, "
                 "with no interpretation added. userId is a UUID the app holds for the install; "
                 "walletRewardId is a four-word value; phraseWritten and rewardsAnimationShown "
                 "are booleans; appForegroundedCount is an integer; secureTime is Unix epoch "
                 "milliseconds.\n"
                 "phraseWritten is reported as the stored boolean. Its name refers to the "
                 "recovery phrase, but what user action sets it is not established by anything "
                 "in the extraction, so no behaviour is asserted from it.\n"
                 "The fcmToken preference is included. It is a push registration identifier for "
                 "this install rather than an account credential: it does not grant access to "
                 "the wallet or to an account, which is why it is treated differently from the "
                 "session tokens deliberately excluded from the Slack - Account artifact. No "
                 "recovery phrase, private key or wallet seed is present in this file, and none "
                 "is reported by this artifact.\n"
                 "The separate crypto_shared_prefs.xml file in the same directory holds "
                 "androidx.security encrypted preferences and a Tink keyset. It is not read by "
                 "this artifact and its contents are not recovered.",
        "paths": ('*/com.breadwallet/shared_prefs/MyPrefsFile.xml',),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {
            "galaxys10_a10": "Android 10 | BRD | 11 rows",
        },
    },
    "breadwallet_exchange_rates": {
        "name": "BRD (BreadWallet) - Cached Exchange Rates",
        "description": "Exchange rates the BRD app had cached, giving the rate stored for each "
                       "crypto asset against each fiat currency",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "BRD (BreadWallet)",
        "notes": "Read from currencyTable_v2 in databases/breadwallet.db.\n"
                 "The table stores a code, a name, a rate and an iso. Reading iso as the crypto "
                 "asset and code as the fiat currency, so that the rate is the value of one unit "
                 "of the asset expressed in that currency, is consistent with the stored values: "
                 "the BTC/USD row holds 55506 and the BCH/USD row 913.48, which are of the right "
                 "order for the dates on the records in the app's key-value store. The columns "
                 "are named on that reading and the raw column names are given alongside.\n"
                 "This table carries no timestamp of its own, so when these rates were fetched is "
                 "not recorded here. They are the rates the client had cached, which is not "
                 "evidence of a transaction at that rate.",
        "paths": ('*/com.breadwallet/databases/breadwallet.db*',),
        "output_types": "standard",
        "artifact_icon": "trending-up",
        "sample_data": {
            "galaxys10_a10": "Android 10 | BRD | 443 rows",
        },
    },
}

import xml.etree.ElementTree as ET

from scripts.ilapfuncs import (artifact_processor, convert_unix_ts_to_utc, does_table_exist_in_db,
                               get_file_path, get_sqlite_db_records, logfunc)

# Named TX_META_DATA_KEY_PREFIX in the application's own code; see the artifact notes.
TX_META_DATA_KEY_PREFIX = 'txn2-'


def _ms(value):
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value) / 1000)
    except (TypeError, ValueError):
        return ''


@artifact_processor
def breadwallet_transaction_metadata(context):
    source_path = get_file_path(context.get_files_found(), 'platform.db')
    data_list = []

    if source_path and does_table_exist_in_db(source_path, 'kvStoreTable'):
        records = {}
        query = ('SELECT key, version, thetime, deleted, length(value) '
                 "FROM kvStoreTable WHERE key LIKE 'txn2-%'")
        for record in get_sqlite_db_records(source_path, query):
            key = record[0]
            entry = records.setdefault(key, [])
            entry.append((record[1], record[2], record[3], record[4]))

        for key, versions in records.items():
            versions.sort(key=lambda item: item[0])
            first, last = versions[0], versions[-1]
            data_list.append((
                _ms(first[1]),
                key[len(TX_META_DATA_KEY_PREFIX):],
                _ms(last[1]),
                len(versions),
                last[0],
                'Yes' if last[2] else 'No',
                last[3],
                key,
            ))

    data_headers = (
        ('First Written', 'datetime'),
        'Transaction Hash',
        ('Last Written', 'datetime'),
        'Version Count',
        'Latest Version',
        'Deleted',
        'Encrypted Value Size',
        'Key (as stored)',
    )
    return data_headers, data_list, source_path


@artifact_processor
def breadwallet_kv_store(context):
    source_path = get_file_path(context.get_files_found(), 'platform.db')
    data_list = []

    if source_path and does_table_exist_in_db(source_path, 'kvStoreTable'):
        query = ('SELECT thetime, key, version, remote_version, deleted, length(value) '
                 'FROM kvStoreTable ORDER BY thetime')
        for record in get_sqlite_db_records(source_path, query):
            data_list.append((
                _ms(record[0]),
                record[1],
                record[2],
                record[3],
                'Yes' if record[4] else 'No',
                record[5],
            ))

    data_headers = (
        ('Written', 'datetime'),
        'Key',
        'Version',
        'Remote Version',
        'Deleted',
        'Encrypted Value Size',
    )
    return data_headers, data_list, source_path


@artifact_processor
def breadwallet_app_state(context):
    source_path = get_file_path(context.get_files_found(), 'MyPrefsFile.xml')
    data_list = []

    if source_path:
        try:
            root = ET.parse(source_path).getroot()
        except (ET.ParseError, OSError) as error:
            logfunc(f'BRD: could not read {source_path}: {error}')
            root = None
        if root is not None:
            for child in root:
                name = child.get('name') or ''
                value = child.get('value')
                if value is None:
                    value = child.text or ''
                readable = _ms(value) if name == 'secureTime' else ''
                data_list.append((name, value, child.tag, readable))

    data_headers = (
        'Preference Name',
        'Value',
        'Stored Type',
        ('Value As Timestamp', 'datetime'),
    )
    return data_headers, data_list, source_path


@artifact_processor
def breadwallet_exchange_rates(context):
    source_path = get_file_path(context.get_files_found(), 'breadwallet.db')
    data_list = []

    if source_path and does_table_exist_in_db(source_path, 'currencyTable_v2'):
        query = 'SELECT iso, code, rate, name FROM currencyTable_v2 ORDER BY iso, code'
        for record in get_sqlite_db_records(source_path, query):
            data_list.append((
                record[0],
                record[1],
                record[2],
                record[3],
            ))

    data_headers = (
        'Asset (iso column)',
        'Currency (code column)',
        'Rate',
        'Name (name column)',
    )
    return data_headers, data_list, source_path
