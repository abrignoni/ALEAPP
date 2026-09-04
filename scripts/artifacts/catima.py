__artifacts_v2__ = {
    "catima_cards": {
        "name": "Catima - Loyalty Cards",
        "description": "Parses loyalty and membership cards from the Catima Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "Catima",
        "sample_data": {
            "emu_a15_oss_v4": "Catima 2.45.0 | 1 rows",
        },
        "notes": "One row per entry in the cards table of databases/Catima.db. Catima is an open "
                 "source loyalty-card wallet that stores the card numbers and barcodes a person "
                 "adds, entered by scanning or by hand. Each row is a card, with the Store name, a "
                 "Note, the Card ID (the loyalty or membership number, on the tested device "
                 "9876543210123), an optional separate Barcode ID (used when the printed barcode "
                 "value differs from the shown card number, blank when they are the same), the "
                 "Barcode Type (a ZXing format name such as CODE_128), a Balance and its Balance "
                 "Type (blank Balance Type is the app's points default). Last Used is the time the "
                 "card was last opened, stored as Unix seconds (Utils.getUnixTime is "
                 "System.currentTimeMillis()/1000) and reported as UTC; the tested card read "
                 "1788229821, which is 2026-09-01 02:30:21 UTC and matched the 22:30 local save "
                 "time on the America/New_York device. Valid From and Expiry are the card's "
                 "validity dates, stored as Unix milliseconds (Date.getTime) and reported as UTC; "
                 "they were empty on the tested card so the millisecond unit is taken from the "
                 "app's source and not proven on data here. Starred is the favourite flag and "
                 "Archived is the archive flag (LoyaltyCard.java and DBHelper.java at "
                 "CatimaLoyalty/Android tag v2.45.0, "
                 "22193b1872ee0df6efa6111972b90b59a0253c4d). Groups lists the user-named groups "
                 "the card is filed under, from the cardsGroups table, and was empty on the "
                 "tested device. The header colour and zoom columns are display styling and are "
                 "not reported. The fts tables are a full-text search index Catima maintains and "
                 "are not evidence, so they are not parsed.",
        "paths": ('*/me.hackerchick.catima/databases/Catima.db*',),
        "output_types": "standard",
        "artifact_icon": "credit-card",
    },
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/Catima.db'


def _db_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(DB_SUFFIX)]


def _secs(value):
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value))
    except (TypeError, ValueError):
        return ''


def _ms(value):
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value) // 1000)
    except (TypeError, ValueError):
        return ''


def _yesno(value):
    if value in (1, '1'):
        return 'Yes'
    if value in (0, '0', None, ''):
        return 'No'
    return ''


@artifact_processor
def catima_cards(context):
    query = '''SELECT c._id, c.store, c.note, c.cardid, c.barcodeid, c.barcodetype,
                      c.balance, c.balancetype, c.validfrom, c.expiry, c.lastused,
                      c.starstatus, c.archive,
                      (SELECT GROUP_CONCAT(cg.groupId, ', ') FROM cardsGroups cg
                       WHERE cg.cardId = c._id) AS grps
               FROM cards c ORDER BY c._id'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                r[1] or '', r[2] or '', r[3] or '', r[4] or '', r[5] or '',
                r[6] or '', r[7] or '', _ms(r[8]), _ms(r[9]), _secs(r[10]),
                _yesno(r[11]), _yesno(r[12]), r[13] or '',
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        'Store', 'Note', 'Card ID', 'Barcode ID', 'Barcode Type', 'Balance',
        'Balance Type', ('Valid From', 'datetime'), ('Expiry', 'datetime'),
        ('Last Used', 'datetime'), 'Starred', 'Archived', 'Groups', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
