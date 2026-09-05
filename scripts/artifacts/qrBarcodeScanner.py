__artifacts_v2__ = {
    "qr_barcode_scanner_history": {
        "name": "QR and Barcode Scanner History",
        "description": "Codes scanned or generated in Gamma Play's QR and Barcode Scanner",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "sample_data": {
            "emu_a15_oss_v11": "QR & Barcode Scanner 2.2.224 | 9 rows",
        },
        "requirements": "none",
        "category": "QR and Barcode Scanner",
        "notes": "One row per row of the history table in "
                 "com.gamma.scan/databases/barcode_scanner_history.db. Timestamp is Unix "
                 "milliseconds and is reported as UTC. Source separates the two ways a row gets "
                 "there, from the table's own created column: 0 is a code the app read, and 1 is "
                 "one the app generated from text typed into it. Both were produced on the tested "
                 "device, eight read and one generated, so that mapping is proven by known data "
                 "rather than inferred. Content is the payload exactly as encoded, which is what "
                 "carries the scheme: MECARD for a contact, WIFI with the network name, security "
                 "type and passphrase, geo with a latitude and longitude, mailto, tel and SMSTO. "
                 "Display is the app's own readable rendering of that same payload and is kept "
                 "beside it because the two differ. Details holds text the app attached to the "
                 "row afterwards; on the tested device it was filled on one row of nine, and on "
                 "that row it held the title of the web page the scanned URL points at, so a "
                 "populated Details is a record that the device fetched that address rather than "
                 "merely decoded it. Format is the barcode symbology the decoder reported. Every "
                 "code on the tested device was QR_CODE, since only QR images were used, and the "
                 "column is what tells a QR code apart from a scanned product barcode. Favorite "
                 "was 0 and Name was empty on every row, because nothing was starred or renamed "
                 "there; Name is a label a user can attach to a saved code. Sort Order is the "
                 "table's own sorting_order. It held the same value as Row ID on every row of the "
                 "tested image, because the history was never reordered there, so the two agreeing "
                 "is a property of that sample and not one column derived from the other. It is "
                 "kept because a Sort Order that departs from Row ID is what shows the list was "
                 "rearranged by hand. Scanning does not "
                 "require the code to have been on the device: an image in the gallery, a printed "
                 "code, or a screen can all produce a row, so a row is evidence the app decoded "
                 "the payload and not evidence of where the code came from.",
        "paths": ('*/com.gamma.scan/databases/barcode_scanner_history.db*',),
        "output_types": "standard",
        "artifact_icon": "maximize",
    }
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/barcode_scanner_history.db'

# Proven by known data on the tested device: eight rows the app read carried 0 and the one
# row it generated from typed text carried 1. The app is closed source, so nothing else in
# this column is named.
SOURCES = {0: 'Scanned', 1: 'Created in app'}


def _db_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(DB_SUFFIX)]


def _ms(value):
    if not value:
        return ''
    try:
        value = int(value)
        if value < 0:
            return ''
        return convert_unix_ts_to_utc(value // 1000)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _source(value):
    if value is None:
        return ''
    if value in SOURCES:
        return f'{SOURCES[value]} ({value})'
    return f'As stored ({value})'


@artifact_processor
def qr_barcode_scanner_history(context):
    query = '''SELECT timestamp, text, display, format, created, details, name,
                      favorite, sorting_order, id
               FROM history
               ORDER BY timestamp'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                _ms(r[0]), r[1] or '', r[2] or '', r[3] or '', _source(r[4]),
                r[5] or '', r[6] or '', 'Yes' if r[7] else 'No',
                r[8] if r[8] is not None else '', r[9],
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Timestamp', 'datetime'), 'Content', 'Display', 'Format', 'Source',
        'Details', 'Name', 'Favorite', 'Sort Order', 'Row ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
