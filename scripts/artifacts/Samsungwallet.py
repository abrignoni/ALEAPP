__artifacts_v2__ = {
    "samsung_wallet_cards": {
        "name": "Samsung Wallet - Enrolled Cards",
        "description": "Cards enrolled in Samsung Wallet (formerly Samsung Pay), with each "
                       "card's issuer, enrollment/reference identifiers, when its state was "
                       "last updated, whether it is locked, and identity-verification "
                       "attempt counters.",
        "author": "@Gear-I, Claude",
        "creation_date": "2026-08-26",
        "last_update_date": "2026-08-26",
        "requirements": "none",
        "category": "Samsung Wallet",
        "notes": "Source is spay.db's card table. Samsung Wallet encrypts the fields an "
                 "examiner would most want -- cardLastFour, cardName, tokenLastFour, "
                 "cardBrand, cardHolderName, cardBalance, issuerCountryCode, cardTrType, "
                 "comboCardType and tokenReferenceID all store base64-encoded ciphertext on "
                 "the device this was validated against, and there is no key recoverable "
                 "from the filesystem extraction to decrypt them, so this artifact does not "
                 "attempt to. What is recoverable in plain text: the card's own enrollment, "
                 "token and reference identifiers (stable values Samsung's servers use for "
                 "this specific card enrollment, not the card's actual account number), the "
                 "issuer's name, contact number and URL, when the card's state was last "
                 "updated (cardStateTimestamp, a millisecond epoch value baked into the row "
                 "itself), whether it is locked, whether it is flagged transit-capable, and "
                 "the identity-verification attempt/retry counters Samsung Wallet keeps for "
                 "that card. UI-only fields with no forensic content (reorder position, "
                 "display colors, negated-timestamp sort keys) are left out.",
        "paths": ('*/com.samsung.android.spay/databases/spay.db*',),
        "output_types": ["standard"],
        "artifact_icon": "credit-card",
        "sample_data": {
            "sm_g991u_a11": "Android 11 | com.samsung.android.spay | 1 row",
        },
    },
    "samsung_wallet_receipts": {
        "name": "Samsung Wallet - Receipts",
        "description": "Receipt records Samsung Wallet has stored for card transactions, "
                       "linked back to the enrolled card that made them.",
        "author": "@Gear-I, Claude",
        "creation_date": "2026-08-26",
        "last_update_date": "2026-08-26",
        "requirements": "none",
        "category": "Samsung Wallet",
        "notes": "Source is spay.db's receipt table, the same database as Samsung Wallet - "
                 "Enrolled Cards. Unlike that table, almost everything an examiner would "
                 "want from a receipt is encrypted on the device this was validated against: "
                 "approvalDate, approvalTime, merchant, amount, transactionType, "
                 "currencyCode and transactionStatus are all base64-encoded ciphertext with "
                 "no recoverable key, so none of them are decoded here. What survives in "
                 "plain text is thin: despite its name, receipt.tokenID does not match the "
                 "enrolled card's own tokenID column -- on the device this was validated "
                 "against it holds the card's enrollmentID instead, confirmed by comparing "
                 "both columns directly, so this is reported as 'Card Enrollment ID' (read "
                 "from receipt.tokenID) and joins back to 'Enrollment ID' in Samsung Wallet "
                 "- Enrolled Cards, not to that artifact's own 'Token ID' column. 'Rewards "
                 "Redeemed' / 'Watch Transaction' are plain integer flags. Columns such as "
                 "merchant country/town, bank-transfer sender/receiver IBAN and booking date "
                 "exist in the schema but were NULL on the single receipt this was validated "
                 "against, so whether they are ever stored in plain text on a populated row "
                 "is unconfirmed -- they are read here and left blank rather than assumed "
                 "either way. This artifact mainly documents that a transaction happened and "
                 "which card it belongs to, not its detail.",
        "paths": ('*/com.samsung.android.spay/databases/spay.db*',),
        "output_types": ["standard"],
        "artifact_icon": "receipt",
        "sample_data": {
            "sm_g991u_a11": "Android 11 | com.samsung.android.spay | 1 row",
        },
    },
}

from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records


def _epoch_ms_to_utc(value):
    try:
        return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc)
    except (TypeError, ValueError, OverflowError):
        return None


def _find_all(files_found, suffix):
    """Every file_found ending in suffix, in order. A second Android user
    profile has its own copy of spay.db, so every match is read rather than
    only the first.
    """
    return [file_found for file_found in (str(f) for f in files_found)
            if file_found.endswith(suffix)]


@artifact_processor
def samsung_wallet_cards(context):
    data_headers = (
        "Enrollment ID", "Token ID", "Card Reference ID", "Issuer Name",
        "Issuer Contact Number", "Issuer URL", ("Card State Updated", "datetime"),
        "Payment Ready", "Card Locked", "Transit Support",
        "ID Verification Max Requests", "ID Verification Request Count",
        "ID Verification Max Retries", "ID Verification Retry Count",
    )

    files_found = unique_files(context)
    db_paths = _find_all(files_found, 'spay.db')
    if not db_paths:
        return data_headers, [], ""

    data_list = []
    source_paths = []
    for db_path in db_paths:
        rows = get_sqlite_db_records(
            db_path,
            "SELECT enrollmentID, tokenID, cardReferenceID, issuerName, "
            "issuerContactNumber, issuerURL, cardStateTimestamp, payReadyFlag, "
            "isLocked, transitSupport, idvMaxRequest, idvRequestCount, "
            "idvMaxRetry, idvRetryCount FROM card",
        )
        for row in rows:
            source_paths.append(db_path)
            (enrollment_id, token_id, card_reference_id, issuer_name,
             issuer_contact_number, issuer_url, card_state_timestamp,
             pay_ready_flag, is_locked, transit_support, idv_max_request,
             idv_request_count, idv_max_retry, idv_retry_count) = row
            data_list.append((
                enrollment_id or '', token_id or '', card_reference_id or '',
                issuer_name or '', issuer_contact_number or '', issuer_url or '',
                _epoch_ms_to_utc(card_state_timestamp), pay_ready_flag, is_locked,
                transit_support or '', idv_max_request, idv_request_count,
                idv_max_retry, idv_retry_count,
            ))

    data_list.sort(key=lambda row: (row[6] is None, row[6]))
    source_path = '\n'.join(source_paths)
    return data_headers, data_list, source_path


@artifact_processor
def samsung_wallet_receipts(context):
    data_headers = (
        "Receipt ID", "Card Enrollment ID", "Rewards Redeemed", "Watch Transaction",
        "Merchant Country Code", "Merchant Town", "Booking Date", "Value Date",
        "Sender IBAN", "Receiver IBAN",
    )

    files_found = unique_files(context)
    db_paths = _find_all(files_found, 'spay.db')
    if not db_paths:
        return data_headers, [], ""

    data_list = []
    source_paths = []
    for db_path in db_paths:
        rows = get_sqlite_db_records(
            db_path,
            "SELECT _id, tokenID, pwpredeemflag, isWatchTransaction, "
            "merchantCountryCode, merchantTown, bookingDate, valueDate, "
            "senderIBAN, receiverIBAN FROM receipt",
        )
        for row in rows:
            source_paths.append(db_path)
            (receipt_id, card_enrollment_id, pwp_redeem_flag, is_watch_transaction,
             merchant_country_code, merchant_town, booking_date, value_date,
             sender_iban, receiver_iban) = row
            data_list.append((
                receipt_id, card_enrollment_id or '', pwp_redeem_flag, is_watch_transaction,
                merchant_country_code or '', merchant_town or '', booking_date or '',
                value_date or '', sender_iban or '', receiver_iban or '',
            ))

    data_list.sort(key=lambda row: row[0] if row[0] is not None else -1)
    source_path = '\n'.join(source_paths)
    return data_headers, data_list, source_path
