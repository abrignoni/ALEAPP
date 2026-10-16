__artifacts_v2__ = {
    "breadwallet_transaction_metadata": {
        "name": "BRD (BreadWallet) - Transaction Metadata Records",
        "description": "Transaction metadata records held in the BRD key-value store, giving the "
                       "transaction hash each record is keyed on and the thetime value, read as "
                       "Unix milliseconds, of the lowest and highest version of each record",
        "author": "@AlexisBrignoni, Claude, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-10-04",
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
                 "The stored value is NOT decoded. On the tested corpus every value in this table "
                 "began with the same leading bytes followed by high-entropy bytes, and no key for "
                 "it was found in the extraction, so it is treated as encrypted. So the "
                 "transaction amount, the counterparty, any user memo and the comment fields a "
                 "TxMetaData record can hold are not recovered. What this artifact establishes is "
                 "that a metadata record exists for that transaction hash, with the thetime values "
                 "of its versions.\nThe store holds more than one version of a key, so Lowest "
                 "Version Time (thetime) and Highest Version Time (thetime) are the thetime "
                 "values, read as Unix milliseconds, of the lowest and highest version of that "
                 "key and Version Count is how many are present. Value Size (bytes) is the "
                 "length of the stored value of the highest version; the artifact does not test "
                 "whether the value is encrypted.\n"
                 "In the app's published source the store sets thetime from "
                 "System.currentTimeMillis() when it writes a row locally, and passes the "
                 "remote record's time when it stores a value fetched during sync, so thetime "
                 "is not in every case the time the row was written on the device. Reference: "
                 "https://github.com/breadwallet/breadwallet-android/blob/dfbbfbfc92dae054e47f245e1ce2ac8a39e65e57/"
                 "app/src/main/java/com/platform/kvstore/ReplicatedKVStore.java#L265-L279 and "
                 "#L679 in the same file. Which app version wrote the tested store was not "
                 "compared with that commit. On galaxys10_a10 all 38 thetime values read as "
                 "milliseconds fall on 2021-04-18.\n"
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
        "description": "Records in the BRD key-value store, with the key, the version, the "
                       "thetime value and the size of the stored value",
        "author": "@AlexisBrignoni, Claude, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "BRD (BreadWallet)",
        "notes": "Read from the kvStoreTable of databases/platform.db, without filtering, so the "
                 "transaction metadata rows the BRD - Transaction Metadata Records artifact "
                 "reports separately also appear here.\n"
                 "The values are treated as encrypted, on the basis given in the BRD - Transaction "
                 "Metadata Records notes, and are not decoded; only the size is reported. The keys "
                 "are stored in the clear and are what this artifact is for: they are reported as "
                 "stored, with the thetime value of each row read as Unix milliseconds in the "
                 "Time (thetime) column. What thetime can hold is described, with its source, "
                 "in the BRD - Transaction Metadata Records notes. Value Size (bytes) is the "
                 "length of the stored value; the artifact does not test whether it is "
                 "encrypted.\n"
                 "Keys observed on the tested corpus were wallet-info, asset-index, the "
                 "plat-vuex-* application state keys, and the txn2- transaction metadata keys. "
                 "The meaning of the wallet-info and asset-index keys beyond their names is not "
                 "established here; asset-index appears in APK log strings about migrating from "
                 "an earlier token-list-metadata key.\n"
                 "The same key appears more "
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
        "description": "The userId value and application state held in shared "
                       "preferences, including the recovery phrase written flag and the wallet "
                       "reward identifier",
        "author": "@AlexisBrignoni, Claude, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "BRD (BreadWallet)",
        "notes": "Read from shared_prefs/MyPrefsFile.xml.\n"
                 "Every value is reported under the preference name the app stored it against, "
                 "with no interpretation added. userId is a UUID as stored; walletRewardId is a "
                 "four-word value; phraseWritten and rewardsAnimationShown are booleans; "
                 "appForegroundedCount is an integer. secureTime is read as Unix epoch "
                 "milliseconds in the Value As Timestamp column; what it records is not "
                 "established here.\nphraseWritten is reported as the stored boolean. Its name "
                 "refers to the recovery phrase, but what user action sets it is not established "
                 "by anything in the extraction, so no behaviour is asserted from it.\nThe "
                 "fcmToken preference is included and is reported as stored; it is a push "
                 "messaging registration token and is not a wallet key. No recovery phrase, "
                 "private key or wallet seed was present in this file on the tested corpus. The "
                 "artifact reports every preference in the file without filtering.\n"
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
        "description": "Exchange rates the BRD app had cached, giving the iso, code, rate and name "
                       "stored on each row",
        "author": "@AlexisBrignoni, Claude, @AlexisBrignoni, Codex",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "BRD (BreadWallet)",
        "notes": "Read from currencyTable_v2 in databases/breadwallet.db.\n"
                 "The table stores a code, a name, a rate and an iso. Reading iso as the crypto "
                 "asset and code as the fiat currency, so that the rate is the value of one unit "
                 "of the asset expressed in that currency, is consistent with the stored values: "
                 "the BTC/USD row holds 55506 and the BCH/USD row 913.48, which are of the right "
                 "order for the dates on the records in the app's key-value store. The app's "
                 "published source comments the iso column as 'iso for the currency of exchange "
                 "(BTC, BCH, ETH)'. Reference: "
                 "https://github.com/breadwallet/breadwallet-android/blob/dfbbfbfc92dae054e47f245e1ce2ac8a39e65e57/"
                 "app-core/src/main/java/com/breadwallet/tools/sqlite/BRSQLiteHelper.java#L81 "
                 "The columns are reported under the stored column names (iso, code, rate, "
                 "name) and the reading is not applied to the headers.\n"
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
        ('Lowest Version Time (thetime)', 'datetime'),
        'Transaction Hash',
        ('Highest Version Time (thetime)', 'datetime'),
        'Version Count',
        'Latest Version',
        'Deleted',
        'Value Size (bytes)',
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
        ('Time (thetime)', 'datetime'),
        'Key',
        'Version',
        'Remote Version',
        'Deleted',
        'Value Size (bytes)',
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
        'iso',
        'code',
        'rate',
        'name',
    )
    return data_headers, data_list, source_path
