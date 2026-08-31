__artifacts_v2__ = {
    "samsung_wallet_cards": {
        "name": "Samsung Wallet - Enrolled Cards",
        "description": "Cards enrolled in Samsung Wallet (formerly Samsung Pay), with each "
                       "card's issuer, enrollment/reference identifiers, when its state was "
                       "last updated, whether it is locked, and identity-verification "
                       "attempt counters.",
        "author": "@Gear-I, Claude",
        "creation_date": "2026-08-26",
        "last_update_date": "2026-08-28",
        "requirements": "none",
        "category": "Samsung Wallet",
        "notes": "Source is spay.db's card table. The database file itself was 4 KB on each "
                 "tested extraction and its contents sat in the spay.db-wal write-ahead log, "
                 "so the path pattern takes the sidecars and the file is read with the log "
                 "applied. Samsung Wallet encrypts several of the fields an examiner would "
                 "want: on the tested extraction cardLastFour, cardName, tokenLastFour, "
                 "cardBrand, issuerCountryCode, cardTrType, comboCardType and "
                 "tokenReferenceID held base64-encoded ciphertext. No key for them was "
                 "located in the extraction and this artifact does not attempt to decode "
                 "them. cardHolderName and cardBalance were empty strings on that "
                 "extraction rather than ciphertext. Read in plain text: the card's "
                 "enrollment, token and reference identifiers (values Samsung's servers use "
                 "for this card enrollment, not the card's account number), the issuer's "
                 "name, contact number and URL, the card state timestamp "
                 "(cardStateTimestamp, a millisecond epoch stored as text), the locked "
                 "flag, the transit-capable flag, and the identity-verification attempt and "
                 "retry counters. ID Verification Max Retries held -1 on the tested "
                 "extraction and every counter column is reported as stored. UI-only fields "
                 "with no forensic content (reorder position, display colors, "
                 "negated-timestamp sort keys) are left out. Other tables in spay.db: "
                 "cardArt is reported by Samsung Wallet - Card Art; partner held 2 rows "
                 "repeating the issuer name and link URL already carried here, so it is not "
                 "reported separately; cobadgeCard, clickToPayTokenInfo, idv, inbox_message, "
                 "issuerAccessKey, partnerExtraInfo, push_message_eu, secondaryCard, "
                 "userSign, virtualCardTokenInfo and watchCard were empty on each of the "
                 "four tested extractions.",
        "paths": ('*/com.samsung.android.spay/databases/spay.db*',),
        "output_types": ["standard"],
        "artifact_icon": "credit-card",
        "sample_data": {
            "cookbook_a11": "Android 11 | com.samsung.android.spay | 1 row",
            "anne_a15": "Android | com.samsung.android.spay | 0 rows",
            "sharon_a14": "Android 14 | com.samsung.android.spay | 0 rows",
            "sharon_a13": "Android 13 | com.samsung.android.spay | 0 rows",
        },
    },
    "samsung_wallet_receipts": {
        "name": "Samsung Wallet - Receipts",
        "description": "Receipt records Samsung Wallet has stored for card transactions, "
                       "linked back to the enrolled card that made them.",
        "author": "@Gear-I, Claude",
        "creation_date": "2026-08-26",
        "last_update_date": "2026-08-28",
        "requirements": "none",
        "category": "Samsung Wallet",
        "notes": "Source is spay.db's receipt table, the same database as Samsung Wallet - "
                 "Enrolled Cards. The receipt table declares its relationship to the card "
                 "table in its own schema, as FOREIGN KEY(tokenID) REFERENCES "
                 "card(enrollmentID) ON DELETE CASCADE. So despite the column's name, "
                 "receipt.tokenID carries the card's enrollmentID and not the card's own "
                 "tokenID column. It is reported here as Card Enrollment ID and joins to "
                 "Enrollment ID in Samsung Wallet - Enrolled Cards, not to that artifact's "
                 "Token ID column. The two values also agreed on the tested extraction. "
                 "Almost everything else a receipt carries is encrypted: on that extraction "
                 "approvalDate, approvalTime, merchant, amount, transactionType, "
                 "currencyCode, transactionStatus, tokenNumber, transactionID, "
                 "industryCatgCode, industryCode, stamp, paymentMethod and cardBrand held "
                 "base64-encoded ciphertext with no key located in the extraction, so none "
                 "of them are decoded here. Rewards Redeemed and Watch Transaction are "
                 "plain integer flags. Merchant Country Code, Merchant Town, Booking Date, "
                 "Value Date, Sender IBAN and Receiver IBAN exist in the schema but were "
                 "NULL on the single receipt tested, so whether they are ever stored in "
                 "plain text on a populated row is unconfirmed. They are read here and left "
                 "blank rather than assumed either way. This artifact records that a "
                 "transaction happened and which card it belongs to, not its detail. The "
                 "receipt table's columns vary between Samsung Wallet releases: the "
                 "Android 13 extraction tested carries no isWatchTransaction column, "
                 "which failed the whole read. Each query is compiled against the "
                 "database it will run on, so a column a release does not carry is "
                 "reported empty and the remaining columns are still returned.",
        "paths": ('*/com.samsung.android.spay/databases/spay.db*',),
        "output_types": ["standard"],
        "artifact_icon": "receipt",
        "sample_data": {
            "cookbook_a11": "Android 11 | com.samsung.android.spay | 1 row",
            "anne_a15": "Android | com.samsung.android.spay | 0 rows",
            "sharon_a14": "Android 14 | com.samsung.android.spay | 0 rows",
            "sharon_a13": "Android 13 | com.samsung.android.spay | 0 rows",
        },
    },
    "samsung_wallet_card_art": {
        "name": "Samsung Wallet - Card Art",
        "description": "Card art images Samsung Wallet stored for enrolled cards, "
                       "joined to the card by the enrollment identifier the "
                       "cardArt table records alongside each image.",
        "author": "@Gear-I, @AlexisBrignoni, Claude",
        "creation_date": "2026-08-28",
        "last_update_date": "2026-08-28",
        "requirements": "none",
        "category": "Samsung Wallet",
        "notes": "Source is spay.db's cardArt table together with the PNG files it names "
                 "under the app's files/cardArt directory. cardArt.cardArtUri records the "
                 "on-device path of each image and cardArt.enrollmentId names the card it "
                 "belongs to, so the link between a card and its images is read from the "
                 "database rather than inferred from file names or matched on size and "
                 "timestamp. Four image types were present per card on the tested "
                 "extraction, reported as stored: CARD_ART_TYPE_LOGO, CARD_ART_TYPE_SYMBOL, "
                 "CARD_ART_TYPE_BANK_ICON and CARD_ART_TYPE_BANK_APP_ICON. Where a card's "
                 "own name, brand and last four digits are encrypted, as they were on the "
                 "tested extraction, the logo can be what identifies the issuer and product "
                 "visually. An image named by the database but not present in the "
                 "extraction is reported with its file name and an empty Card Art cell, so "
                 "a missing file is visible rather than dropped. Images are matched only "
                 "within the app container holding the database that named them, so a "
                 "second Android user's copies are not joined to user 0's rows. Card "
                 "Enrollment ID repeats across the rows belonging to one card, so it "
                 "holds a single value on a device with one card enrolled, as the "
                 "tested extraction did. It is kept because it is the column that joins "
                 "an image back to Samsung Wallet - Enrolled Cards.",
        "paths": ('*/com.samsung.android.spay/databases/spay.db*',
                  '*/com.samsung.android.spay/files/cardArt/*'),
        "output_types": ["standard"],
        "artifact_icon": "image",
        "sample_data": {
            "cookbook_a11": "Android 11 | com.samsung.android.spay | 4 rows",
            "anne_a15": "Android | com.samsung.android.spay | 0 rows",
            "sharon_a14": "Android 14 | com.samsung.android.spay | 0 rows",
            "sharon_a13": "Android 13 | com.samsung.android.spay | 0 rows",
        },
    },
}

import os
from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import canonical_path, unique_files
from scripts.ilapfuncs import (artifact_processor, check_in_media, get_sqlite_db_records,
                              null_absent_columns)

CARD_ART_DIR = '/files/cardArt/'
PACKAGE_SEGMENT = '/com.samsung.android.spay/'


def _epoch_ms_to_utc(value):
    try:
        return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc)
    except (TypeError, ValueError, OverflowError):
        return None


def _spay_databases(files_found):
    """Every spay.db in files_found, sidecars and matched directories excluded.

    A pattern whose last component ends in '*' can match a directory, and open() on
    one aborts the file loop, so directories are skipped before anything is opened.
    A second Android user profile has its own copy of spay.db, so every match is
    read rather than only the first.
    """
    return [file_found for file_found in (str(f) for f in files_found)
            if os.path.basename(file_found) == 'spay.db' and not os.path.isdir(file_found)]


def _container_prefix(context, file_found):
    """The app container holding this file, as a path that one container shares.

    canonical_path replaces the storage view (/data/data, /data/user/<n>,
    data_mirror/...) with the storage class and Android user it denotes, so both
    spellings of one container give the same prefix and two different Android users
    give different ones.
    """
    key, _ = canonical_path(context.get_relative_path(file_found))
    key = str(key).replace('\\', '/')
    index = key.find(PACKAGE_SEGMENT)
    if index == -1:
        return None
    return key[:index + len(PACKAGE_SEGMENT)]


@artifact_processor
def samsung_wallet_cards(context):
    data_headers = (
        ("Card State Updated", "datetime"), "Enrollment ID", "Token ID",
        "Card Reference ID", "Issuer Name", "Issuer Contact Number", "Issuer URL",
        "Payment Ready", "Card Locked", "Transit Support",
        "ID Verification Max Requests", "ID Verification Request Count",
        "ID Verification Max Retries", "ID Verification Retry Count",
    )

    db_paths = _spay_databases(unique_files(context))
    if not db_paths:
        return data_headers, [], ""

    data_list = []
    source_paths = []
    for db_path in db_paths:
        query = ("SELECT enrollmentID, tokenID, cardReferenceID, issuerName, "
                 "issuerContactNumber, issuerURL, cardStateTimestamp, payReadyFlag, "
                 "isLocked, transitSupport, idvMaxRequest, idvRequestCount, "
                 "idvMaxRetry, idvRetryCount FROM card")
        rows = get_sqlite_db_records(db_path, null_absent_columns(db_path, query))
        rows_before = len(data_list)
        for row in rows:
            (enrollment_id, token_id, card_reference_id, issuer_name,
             issuer_contact_number, issuer_url, card_state_timestamp,
             pay_ready_flag, is_locked, transit_support, idv_max_request,
             idv_request_count, idv_max_retry, idv_retry_count) = row
            data_list.append((
                _epoch_ms_to_utc(card_state_timestamp), enrollment_id or '',
                token_id or '', card_reference_id or '', issuer_name or '',
                issuer_contact_number or '', issuer_url or '', pay_ready_flag,
                is_locked, transit_support or '', idv_max_request, idv_request_count,
                idv_max_retry, idv_retry_count,
            ))
        if len(data_list) > rows_before:
            source_paths.append(db_path)

    data_list.sort(key=lambda row: (row[0] is None, row[0]))
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def samsung_wallet_receipts(context):
    data_headers = (
        "Receipt ID", "Card Enrollment ID", "Rewards Redeemed", "Watch Transaction",
        "Merchant Country Code", "Merchant Town", "Booking Date", "Value Date",
        "Sender IBAN", "Receiver IBAN",
    )

    db_paths = _spay_databases(unique_files(context))
    if not db_paths:
        return data_headers, [], ""

    data_list = []
    source_paths = []
    for db_path in db_paths:
        query = ("SELECT _id, tokenID, pwpredeemflag, isWatchTransaction, "
                 "merchantCountryCode, merchantTown, bookingDate, valueDate, "
                 "senderIBAN, receiverIBAN FROM receipt")
        rows = get_sqlite_db_records(db_path, null_absent_columns(db_path, query))
        rows_before = len(data_list)
        for row in rows:
            (receipt_id, card_enrollment_id, pwp_redeem_flag, is_watch_transaction,
             merchant_country_code, merchant_town, booking_date, value_date,
             sender_iban, receiver_iban) = row
            data_list.append((
                receipt_id, card_enrollment_id or '', pwp_redeem_flag, is_watch_transaction,
                merchant_country_code or '', merchant_town or '', booking_date or '',
                value_date or '', sender_iban or '', receiver_iban or '',
            ))
        if len(data_list) > rows_before:
            source_paths.append(db_path)

    data_list.sort(key=lambda row: row[0] if row[0] is not None else -1)
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def samsung_wallet_card_art(context):
    data_headers = (
        "Card Enrollment ID", "Art Type", ("Card Art", "media"), "File Name",
    )

    files_found = unique_files(context)
    db_paths = _spay_databases(files_found)
    if not db_paths:
        return data_headers, [], ""

    # (container, file name) -> staged path. The container is part of the key so one
    # Android user's images can never be joined to another user's database rows.
    art_index = {}
    for file_found in (str(f) for f in files_found):
        if CARD_ART_DIR not in file_found.replace('\\', '/') or os.path.isdir(file_found):
            continue
        prefix = _container_prefix(context, file_found)
        if prefix:
            art_index[(prefix, os.path.basename(file_found))] = file_found

    data_list = []
    source_paths = []
    for db_path in db_paths:
        query = "SELECT enrollmentId, cardArtType, cardArtUri FROM cardArt"
        rows = get_sqlite_db_records(db_path, null_absent_columns(db_path, query))
        prefix = _container_prefix(context, db_path)
        rows_before = len(data_list)
        for enrollment_id, art_type, art_uri in rows:
            file_name = os.path.basename(str(art_uri).replace('\\', '/')) if art_uri else ''
            staged = art_index.get((prefix, file_name)) if file_name else None
            media_ref = check_in_media(staged, file_name) if staged else None
            data_list.append((
                enrollment_id or '', art_type or '', media_ref or '', file_name,
            ))
        if len(data_list) > rows_before:
            source_paths.append(db_path)

    data_list.sort(key=lambda row: (row[0], row[1]))
    return data_headers, data_list, '\n'.join(source_paths)
