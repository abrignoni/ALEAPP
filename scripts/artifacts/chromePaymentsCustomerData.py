__artifacts_v2__ = {
    "get_chromePaymentsCustomerData": {
        "name": "Payments Customer Data",
        "description": "Parses the payments customer data record from Chromium based browsers",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-16",
        "last_update_date": "2026-08-16",
        "requirements": "none",
        "category": "Chromium",
        "notes": "Reads the payments_customer_data table in Web Data. The table is created with a "
                 "single VARCHAR column, customer_id, and the browser writes it by deleting every "
                 "row and then inserting at most one, so a profile stores at most one value here. "
                 "Chromium describes the struct backing this table as the Google Payments customer "
                 "data and describes customer_id as the identifier by which a Google Payments "
                 "account is identified; what account that is, and whose it is, is not recorded in "
                 "this table and is not asserted here. The value is reported as stored. Chromium "
                 "clears this table alongside the other server sourced payment tables in "
                 "ClearAllServerData, so it is grouped with server data rather than with locally "
                 "entered payment details. An empty table is reported as no rows; that is not "
                 "evidence about whether an account exists, only that no record was stored in this "
                 "file. Across the 17 tested images carrying Web Data, 524 of 525 such files were "
                 "readable, 383 of those carried the table and 141 did not, so the table is checked "
                 "for rather than assumed; three files held a row, one row each, all three in the "
                 "Chrome package. A Web Data file left with a hot rollback journal cannot be "
                 "recovered through a read-only handle; such a file is logged and skipped so it "
                 "does not end the run before the other browsers on the device are read. One such "
                 "file was found in the tested images, at a data_mirror path that the storage "
                 "view dedupe excludes before opening, so the skip was exercised by staging "
                 "that same file at an "
                 "ordinary path, where it was logged and the run went on to report another "
                 "browser's row. Extractions carry the same database at more than one path "
                 "(data_mirror, and /data/data next to /data/user/0), so files are deduplicated on "
                 "the evidence-relative path before reading; one tested image carries the Chrome "
                 "database at all three of those paths. Reference: Chromium, "
                 "'payments_autofill_table.cc', "
                 "https://github.com/chromium/chromium/blob/8f4baaae073181e7e0fea1807f8db6ad720dbcb7/components/autofill/core/browser/webdata/payments/payments_autofill_table.cc"
                 " and 'payments_customer_data.h', "
                 "https://github.com/chromium/chromium/blob/8f4baaae073181e7e0fea1807f8db6ad720dbcb7/components/autofill/core/browser/payments/payments_customer_data.h",
        "paths": ('*/app_chrome/Default/Web Data*', '*/app_sbrowser/Default/Web Data*',
                  '*/data/*/app_opera/Web Data*', '*/app_webview/Default/Web Data*'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "id",
        "sample_data": {
            "cookbook_a11": "Android 11 | 1 row",
            "pixel7a_a14": "Android 14 | 1 row",
            "sharon_a14": "Android 14 | 1 row",
            "anne_a15": "Android 15 | 0 rows",
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
            "userb2_a13": "Android 13 | 0 rows",
        },
    }
}

import os
import sqlite3

from scripts.ilapfuncs import logfunc, artifact_processor, open_sqlite_db_readonly
from scripts.artifacts.chrome import get_browser_name
from scripts.artifacts.storagePathViews import unique_files


def _table_exists(cursor, table):
    cursor.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cursor.fetchone() is not None


def _unique_web_data(context):
    '''The context's Web Data files, one copy per duplicate storage view, skipping
    .magisk mirror copies.'''
    kept = []
    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.basename(file_found) != 'Web Data':  # skip -journal and other files
            continue
        relative = str(context.get_relative_path(file_found)).replace('\\', '/')
        if '.magisk' in relative and 'mirror' in relative:
            continue
        kept.append(file_found)
    return unique_files(context, kept)


@artifact_processor
def get_chromePaymentsCustomerData(context):
    all_data = []
    data_headers = ['Customer ID', 'Browser Name']
    report_file = 'Unknown'

    for file_found in _unique_web_data(context):
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
        rows = []
        try:
            cursor = db.cursor()
            if not _table_exists(cursor, 'payments_customer_data'):
                continue
            cursor.execute('SELECT customer_id FROM payments_customer_data')
            rows = cursor.fetchall()
        except sqlite3.Error as ex:
            logfunc(f'Unable to read {browser_name} payments customer data in {file_found}: {ex}')
            continue
        finally:
            db.close()

        if not rows:
            continue

        report_file = file_found if report_file == 'Unknown' else report_file + ', ' + file_found

        for row in rows:
            all_data.append((row[0], browser_name))

    return data_headers, all_data, report_file
