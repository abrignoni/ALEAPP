__artifacts_v2__ = {
    "aves_entries": {
        "name": "Aves Gallery - Catalogued Media",
        "description": "Parses the media catalogue from the Aves Gallery Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Aves Gallery",
        "notes": "One row per entry in the entry table of databases/metadata.db, joined to the "
                 "metadata, address, favourites and videoPlayback tables. Aves Gallery is an open "
                 "source gallery, and this table is its index of the media it found on the device, "
                 "so a row records a file the app catalogued rather than anything a person did "
                 "with it. Path, MIME Type, Size, Width and Height describe the file. Date Added "
                 "is Unix seconds and Date Modified and Date Taken are Unix milliseconds, all "
                 "reported as UTC; Date Taken comes from the file's own capture metadata while the "
                 "other two come from the media store. "
                 "Latitude and Longitude are read from the file's embedded location and are blank "
                 "where it carries none. Country Code and Country Name are the app's own reverse "
                 "geocoding of those coordinates, so they are the app's derived answer rather than "
                 "anything recorded in the file; on the tested device two images carrying known "
                 "coordinates resolved to IS and US. The address table also has address line, "
                 "admin area and locality columns which were empty for both tested images, so the "
                 "geocoding here reached country level only. "
                 "Date Added leads this table rather than Date Taken because the media store "
                 "records it for every entry while Date Taken comes from the file's own capture "
                 "metadata and is absent from videos and from images that carry none: it was "
                 "filled on 2 of the 6 tested entries. Title is the entry title the app stores "
                 "and was empty on all six, because these files carry no embedded title and the "
                 "app falls back to the file name shown in Path. "
                 "Favorite is Yes when the person marked the item in the app, which is a "
                 "deliberate act, and was set on one of the six tested entries. Rating is the "
                 "star rating. Resume Position (ms) is how far into a video playback stopped, "
                 "from the "
                 "videoPlayback table, and is present only for a video that was played part way. "
                 "KML output is produced from the coordinates. "
                 "The metadata table's flags column is an undocumented bitmask and is not "
                 "reported. The covers and dynamicAlbums tables hold album cover choices and "
                 "saved filter definitions and were empty on the tested device.",
        "paths": ('*/deckers.thibault.aves*/databases/metadata.db*',),
        "output_types": "all",
        "artifact_icon": "image",
    },
    "aves_trash_vaults": {
        "name": "Aves Gallery - Trash and Vaults",
        "description": "Parses binned items and encrypted vaults from the Aves Gallery Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Aves Gallery",
        "notes": "Rows from the trash and vaults tables of databases/metadata.db, combined because "
                 "both describe media the app is deliberately keeping out of the main collection. "
                 "Kind names which table a row came from. "
                 "A Trash row is an item the person deleted inside Aves, which moves the file to "
                 "the app's own bin rather than removing it: the Path column gives where the file "
                 "now sits, so the media is still on the device and recoverable, and Date is when "
                 "it was binned, as Unix milliseconds reported as UTC. That makes a trash row a "
                 "record of an intentional deletion together with the means to recover what was "
                 "deleted. "
                 "A Vault row is an encrypted vault the person created to hide media, with its "
                 "Name, the Lock Type it uses and whether it auto locks. The vault's contents are "
                 "not in this table; the row records that a vault exists, which is itself worth "
                 "knowing because it means media was deliberately concealed. Lock Type is "
                 "reported as stored. "
                 "Both tables were present and empty on the tested device, where nothing was "
                 "binned and no vault was created, so this artifact is a checked absence there "
                 "and the columns are described from the schema rather than from decoded rows.",
        "paths": ('*/deckers.thibault.aves*/databases/metadata.db*',),
        "output_types": "standard",
        "artifact_icon": "trash-2",
    },
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/metadata.db'


def _db_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(DB_SUFFIX)]


def _ms(value):
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value) // 1000)
    except (TypeError, ValueError):
        return ''


def _secs(value):
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value))
    except (TypeError, ValueError):
        return ''


def _coord(value):
    if value in (None, '', 0):
        return ''
    return value


@artifact_processor
def aves_entries(context):
    query = '''SELECT e.dateAddedSecs, e.dateModifiedMillis, d.dateMillis, e.path,
                      e.sourceMimeType, e.sizeBytes, e.width, e.height, e.title,
                      m.latitude, m.longitude, a.countryCode, a.countryName,
                      m.rating, v.resumeTimeMillis,
                      CASE WHEN f.id IS NULL THEN 'No' ELSE 'Yes' END,
                      e.uri, e.id
               FROM entry e
               LEFT JOIN metadata m ON m.id = e.id
               LEFT JOIN address a ON a.id = e.id
               LEFT JOIN dateTaken d ON d.id = e.id
               LEFT JOIN favourites f ON f.id = e.id
               LEFT JOIN videoPlayback v ON v.id = e.id
               ORDER BY e.id'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                _secs(r[0]), _ms(r[2]), _ms(r[1]), r[3] or '', r[4] or '', r[5],
                r[6], r[7], r[8] or '', _coord(r[9]), _coord(r[10]),
                r[11] or '', r[12] or '', r[13], r[14], r[15], r[16] or '', r[17],
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Date Added', 'datetime'), ('Date Taken', 'datetime'),
        ('Date Modified', 'datetime'), 'Path', 'MIME Type', 'Size (bytes)', 'Width',
        'Height', 'Title', 'Latitude', 'Longitude', 'Country Code', 'Country Name',
        'Rating', 'Resume Position (ms)', 'Favorite', 'URI', 'Entry ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def aves_trash_vaults(context):
    trash_query = 'SELECT dateMillis, path, id FROM trash ORDER BY dateMillis DESC'
    vault_query = 'SELECT name, lockType, autoLock, useBin FROM vaults ORDER BY name'
    data_list = []
    sources = []
    for db_path in _db_files(context):
        seen = False
        for r in get_sqlite_db_records(db_path, trash_query):
            seen = True
            data_list.append(('Trash', _ms(r[0]), r[1] or '', '', '', '', r[2],
                              context.get_relative_path(db_path)))
        for r in get_sqlite_db_records(db_path, vault_query):
            seen = True
            data_list.append(('Vault', '', '', r[0] or '', r[1] or '', r[2], '',
                              context.get_relative_path(db_path)))
        if seen and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        'Kind', ('Date', 'datetime'), 'Path', 'Vault Name', 'Lock Type (as stored)',
        'Auto Lock', 'Entry ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
