__artifacts_v2__ = {
    "dhl_tracked_shipments": {
        "name": "DHL - Tracked Shipments",
        "description": "Parses the shipments recorded in the DHL Android app, with the airway bill number and the "
                       "time it was searched.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-29",
        "requirements": "none",
        "category": "DHL",
        "notes": "One row per row of the TBL_TRACK_SHIPMENT table. Airway Bill is the "
                 "airWayBill column and Search Date is the search_date column, as stored; what "
                 "action writes a row was not established beyond the table and column names. "
                 "The row carries an account identifier; one of the two rows on the tested "
                 "device carried a zero value, whose meaning is not established. Search Date "
                 "is stored as text with no zone; which clock wrote it is not established. The "
                 "module passes the text on as stored. The column is declared as a date and "
                 "time, so where the stored text parses as an ISO date and time the LAVA "
                 "output reads it as UTC, which the store does not establish. A row does not "
                 "show that the account holder is the sender or recipient "
                 "of that shipment. Field mapping was done against a private sample provided "
                 "by Mattia; no sample data is recorded for it.",
        "paths": ('*/com.dhl.exp.dhlmobile/databases/dhledb.db*',),
        "output_types": ["html", "tsv", "timeline", "lava"],
        "artifact_icon": "package"
    },
    "dhl_account": {
        "name": "DHL - Account and Settings",
        "description": "Parses the DHL Android app account identifier and the notification "
                       "and language settings it stores.",
        "author": "@AlexisBrignoni, @mattiaepi (Mattia Epifani), Claude",
        "creation_date": "2026-08-20",
        "last_update_date": "2026-08-20",
        "requirements": "none",
        "category": "DHL",
        "notes": "One row per stored user record. Account ID is the _id column of the "
                 "TBL_USERSETTING row, as stored; whether it equals the user_id on the tracked "
                 "shipment rows was not established. Language and the notification flags are "
                 "the "
                 "settings the record carries, reported as stored. The same database also holds "
                 "a large catalogue of countries, currencies and shipping package types; those "
                 "tables are not "
                 "reported. Field mapping was done against a private sample provided by "
                 "Mattia; no sample data is recorded for it.",
        "paths": ('*/com.dhl.exp.dhlmobile/databases/dhledb.db*',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user"
    },
}

import os

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, logfunc


def _text(value):
    '''A stored value as text, with a stored null read as absent.'''
    return '' if value is None else str(value)


def _databases(context):
    '''Every DHL database in the extraction, duplicate storage views collapsed.'''
    return [str(f) for f in unique_files(context)
            if os.path.basename(str(f)) == 'dhledb.db']


def _rows(path, statement):
    '''The rows a statement returns, or nothing when the table is absent.'''
    try:
        return list(get_sqlite_db_records(path, statement))
    except Exception as error:                   # pylint: disable=broad-except
        logfunc(f'DHL: could not read from dhledb.db: {error}')
        return []


@artifact_processor
def dhl_tracked_shipments(context):
    data_list = []
    source_files = []

    for path in _databases(context):
        relative = context.get_relative_path(path)
        for user_id, airway_bill, search_date in _rows(
                path, 'SELECT user_id, airWayBill, search_date FROM TBL_TRACK_SHIPMENT'):
            source_files.append(relative)
            data_list.append((
                _text(search_date),
                _text(airway_bill),
                _text(user_id),
                relative,
            ))

    data_list.sort(key=lambda r: (str(r[0]), str(r[1])), reverse=True)

    data_headers = (
        ('Search Date', 'datetime'),
        'Airway Bill',
        'Account ID',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))


@artifact_processor
def dhl_account(context):
    data_list = []
    source_files = []

    for path in _databases(context):
        relative = context.get_relative_path(path)
        for row in _rows(path, '''
                SELECT _id, languageCd, notifyShipment, notifyPromotion,
                       notifyInfo
                FROM TBL_USERSETTING'''):
            identifier, language, notify_shipment, notify_promo, notify_info = row
            source_files.append(relative)
            data_list.append((
                _text(identifier),
                _text(language),
                _text(notify_shipment),
                _text(notify_promo),
                _text(notify_info),
                relative,
            ))

    data_headers = (
        'Account ID',
        'Language',
        'Notify Shipment (as stored)',
        'Notify Promotion (as stored)',
        'Notify Info (as stored)',
        'Source File',
    )
    return data_headers, data_list, '; '.join(sorted(set(source_files)))
