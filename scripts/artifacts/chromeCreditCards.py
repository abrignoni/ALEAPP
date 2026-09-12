__artifacts_v2__ = {
    "get_chromeCreditCards": {
        "name": "Saved Credit Cards",
        "description": "Parses saved payment card records from Chromium based browsers",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Chromium",
        "notes": "Reads the masked_credit_cards table in Web Data, joined to server_card_metadata on "
                 "id, mirroring the LEFT OUTER JOIN the browser itself uses, so a card with no "
                 "metadata row is still reported with an empty Date Last Used and Use Count. These "
                 "records hold the last four digits only; the tables carry no full card number and "
                 "none is reported. Column sets differ widely between releases (13 distinct shapes "
                 "were seen across the tested images, from 9 to 19 columns), so columns are read by "
                 "name and any the release does not have are left empty rather than failing the "
                 "query. Date Last Used is server_card_metadata.use_date, read as microseconds since "
                 "1601-01-01 UTC: the browser reads that column with "
                 "base::Time::FromDeltaSinceWindowsEpoch(base::Microseconds(...)), and on the one "
                 "tested image carrying a row the value decodes to 2024-01-27 that way while a Unix "
                 "seconds reading is out of representable range. The local credit_cards table uses a "
                 "different epoch (Unix seconds) and is not read by this artifact; it was present but "
                 "empty in every tested image and it stores its number encrypted. Card Network is "
                 "reported as stored. Card Issuer, Virtual Card Enrollment State and Card Creation "
                 "Source are integers decoded through Chromium's own enum definitions, which state "
                 "the numbering is persistent in the database; a value outside the defined set is "
                 "reported as the bare integer. Only Card Issuer and Virtual Card Enrollment State "
                 "were exercised by a real row in the tested images, so the Card Creation Source "
                 "decode is source-verified and not corpus-verified. Rows are driven from "
                 "masked_credit_cards, so a metadata row whose card has been removed is not "
                 "reported. An extraction can hold the same Web Data file under more than one path "
                 "(/data/data, /data/user/0, data_mirror); each file is read once, from the "
                 "/data/data copy where present. A Web Data file left with a hot rollback journal "
                 "cannot be recovered through a read-only handle; such a file is logged and skipped "
                 "so it does not end the run before the other browsers on the device are read. One "
                 "such file was found across the tested images, and it sits at a duplicate path "
                 "that deduplication drops, so no tested image reaches that guard. It was exercised "
                 "instead by staging that same file at an ordinary /data/data path, which logged "
                 "the skip and still reported the card another browser held in the same run. "
                 "Hu and Karabiyik report finding cardholder name, card type, last four "
                 "digits, expiration, use frequency and dates of use in these two tables at "
                 "data/data/com.android.chrome/app_chrome/Default/Web Data after TikTok Shop "
                 "purchases on an Android 11 device without launching Chrome; their attribution of "
                 "that storage to TikTok is stated in the paper as a belief rather than a "
                 "demonstrated mechanism. Reference: Hu and Karabiyik, 'Shopping while Watching: An "
                 "Updated Forensic Analysis of TikTok on Android and iOS', ISNCC 2024, "
                 "https://doi.org/10.1109/ISNCC62547.2024.10759027. Reference: Chromium, "
                 "'payments_autofill_table.cc', "
                 "https://github.com/chromium/chromium/blob/8f4baaae073181e7e0fea1807f8db6ad720dbcb7/components/autofill/core/browser/webdata/payments/payments_autofill_table.cc"
                 " and 'enum_types.mojom', "
                 "https://github.com/chromium/chromium/blob/8f4baaae073181e7e0fea1807f8db6ad720dbcb7/components/autofill/core/browser/data_model/payments/enum_types.mojom",
        "paths": ('*/app_chrome/Default/Web Data*', '*/app_sbrowser/Default/Web Data*',
                  '*/data/*/app_opera/Web Data*', '*/app_webview/Default/Web Data*'),
        "output_types": "standard",
        "artifact_icon": "credit-card",
        "sample_data": {
            "pixel7a_a14": "Android 14 | 1 row",
            "anne_a15": "Android 15 | 0 rows",
            "cookbook_a11": "Android 11 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 0 rows",
            "russell_a14": "Android 14 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 0 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
    }
}

import datetime
import os
import sqlite3

from scripts.ilapfuncs import logfunc, artifact_processor, open_sqlite_db_readonly
from scripts.artifacts.chrome import get_browser_name
from scripts.artifacts.storagePathViews import unique_files

# Integer codes decoded through Chromium's own enum definitions. The file states
# the numbering is persistent in the database and kept in sync with the sync
# proto, so the values are not expected to shift between releases the way a
# build-assigned entity code would.
# Reference: Chromium, 'enum_types.mojom',
# https://github.com/chromium/chromium/blob/8f4baaae073181e7e0fea1807f8db6ad720dbcb7/components/autofill/core/browser/data_model/payments/enum_types.mojom
CARD_ISSUER = {
    0: 'Unknown',
    1: 'Google',
    2: 'External issuer',
}

VIRTUAL_CARD_ENROLLMENT_STATE = {
    0: 'Unspecified',
    1: 'Unenrolled (deprecated value)',
    2: 'Enrolled',
    3: 'Unenrolled and not eligible',
    4: 'Unenrolled and eligible',
}

CARD_CREATION_SOURCE = {
    0: 'Unspecified',
    1: 'Added through Chrome',
    2: 'Added outside of Chrome',
}


def _decode(mapping, value):
    """Return the documented label, or the value as stored when undefined."""
    if value is None or value == '':
        return ''
    try:
        return mapping.get(int(value), str(value))
    except (TypeError, ValueError):
        return str(value)


def _windows_epoch_us_to_utc(value):
    """server_card_metadata.use_date is microseconds since 1601-01-01 UTC."""
    if value in (None, 0, ''):
        return ''
    try:
        return (datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)
                + datetime.timedelta(microseconds=int(value)))
    except (TypeError, ValueError, OverflowError):
        return ''


def _table_exists(cursor, table):
    cursor.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cursor.fetchone() is not None


def _rows_as_dicts(cursor, table):
    """Read a whole table into dicts keyed by column name.

    Releases carry very different column sets here, so reading by name and
    letting absent columns come back empty keeps one query working across all
    of them without naming a column the release does not have.
    """
    cursor.execute(f'SELECT * FROM {table}')
    columns = [description[0] for description in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


@artifact_processor
def get_chromeCreditCards(context):
    files_found = unique_files(context)
    all_data = []
    data_headers = [
        ('Date Last Used', 'datetime'), 'Name on Card', 'Card Network (as stored)',
        'Last Four Digits', 'Expiration Month', 'Expiration Year', 'Use Count',
        'Bank Name', 'Nickname', 'Product Description', 'Card Issuer ID', 'Card Issuer',
        'Virtual Card Enrollment State', 'Card Creation Source', 'Billing Address ID',
        'Instrument ID', 'Card Art URL', 'Server ID', 'Browser Name']
    report_file = 'Unknown'

    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'Web Data':  # skip -journal and other files
            continue
        if file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue  # Skip mirror, it should be duplicate data

        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'

        db = open_sqlite_db_readonly(file_found)
        if db is None:
            continue

        # One unreadable database must not end the artifact. A Web Data file
        # left with a hot rollback journal cannot be recovered through a
        # read-only handle, and a device carries one of these files per app
        # that embeds a WebView.
        cards = []
        metadata = {}
        try:
            cursor = db.cursor()
            if not _table_exists(cursor, 'masked_credit_cards'):
                continue
            cards = _rows_as_dicts(cursor, 'masked_credit_cards')
            if _table_exists(cursor, 'server_card_metadata'):
                metadata = {row.get('id'): row
                            for row in _rows_as_dicts(cursor, 'server_card_metadata')}
        except sqlite3.Error as ex:
            logfunc(f'Unable to read {browser_name} card tables in {file_found}: {ex}')
            continue
        finally:
            db.close()

        if not cards:
            logfunc(f'No {browser_name} - Saved Credit Cards data available')
            continue

        report_file = file_found if report_file == 'Unknown' else report_file + ', ' + file_found

        for card in cards:
            meta = metadata.get(card.get('id'), {})
            all_data.append((
                _windows_epoch_us_to_utc(meta.get('use_date')),
                card.get('name_on_card', ''),
                card.get('network', ''),
                card.get('last_four', ''),
                card.get('exp_month', ''),
                card.get('exp_year', ''),
                meta.get('use_count', ''),
                card.get('bank_name', ''),
                card.get('nickname', ''),
                card.get('product_description', ''),
                card.get('card_issuer_id', ''),
                _decode(CARD_ISSUER, card.get('card_issuer')),
                _decode(VIRTUAL_CARD_ENROLLMENT_STATE, card.get('virtual_card_enrollment_state')),
                _decode(CARD_CREATION_SOURCE, card.get('card_creation_source')),
                meta.get('billing_address_id', ''),
                card.get('instrument_id', ''),
                card.get('card_art_url', ''),
                card.get('id', ''),
                browser_name,
            ))

    return data_headers, all_data, report_file
