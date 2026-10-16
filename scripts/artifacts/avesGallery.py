__artifacts_v2__ = {
    "aves_entries": {
        "name": "Aves Gallery - Catalogued Media",
        "description": "Parses the media catalogue from the Aves Gallery Android app.",
        "author": "@AlexisBrignoni, Claude, @AlexisBrignoni, Codex",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Aves Gallery",
        "sample_data": {
            "emu_a15_oss_v9": "Aves Gallery Libre 1.14.9 | 6 rows",
        },
        "notes": "One row per entry in the entry table of databases/metadata.db, joined to the "
                 "metadata, address, favourites and videoPlayback tables. Aves Gallery is an open "
                 "source gallery, and this table is its index of the media it found on the device, "
                 "so a row records a file the app catalogued rather than anything a person did "
                 "with it. Path, MIME Type, Size, Width and Height describe the file. Date Added "
                 "is Unix seconds and Date Modified and Date Taken are Unix milliseconds, all "
                 "converted from the stored number and shown as UTC. Date Taken is the dateTaken "
                 "table's dateMillis. Aves 1.14.9 fills it from a date in the file's metadata, "
                 "and converts a date that carries no time zone with the device's default time "
                 "zone at the time of cataloguing, so the instant shown is not a reading the "
                 "file itself records. Reference: Aves, MetadataFetchHandler.kt, "
                 "https://github.com/deckerst/aves/blob/5592b0f606379ca1f44e8772007c754456e12cab/android/app/src/main/kotlin/deckers/thibault/aves/channel/calls/"
                 "MetadataFetchHandler.kt#L691-L692 and Helper.kt, "
                 "https://github.com/deckerst/aves/blob/5592b0f606379ca1f44e8772007c754456e12cab/android/app/src/main/kotlin/deckers/thibault/aves/metadata/"
                 "metadataextractor/Helper.kt#L234-L239 and "
                 "https://github.com/deckerst/aves/blob/5592b0f606379ca1f44e8772007c754456e12cab/android/app/src/main/kotlin/deckers/thibault/aves/metadata/"
                 "metadataextractor/Helper.kt#L309-L311 . On emu_a15_oss_v9, whose stored time "
                 "zone setting is America/New_York, the 2 rows carrying a Date Taken were both "
                 "4 hours later than the EXIF DateTimeOriginal in the file, which carries no "
                 "time zone. Where Date Added and Date Modified are taken from was not sourced "
                 "here. Latitude and Longitude are reported as stored, a stored 0 included, and "
                 "are blank where the row carries none. Aves 1.14.9 keeps a coordinate pair "
                 "unless both values are within 1e-9 of 0, so one value of a stored pair can be "
                 "0. Reference: Aves, catalog.dart, "
                 "https://github.com/deckerst/aves/blob/5592b0f606379ca1f44e8772007c754456e12cab/lib/model/metadata/catalog.dart#L46-L57 . On emu_a15_oss_v9 the 4 "
                 "rows with no coordinates held NULL in both columns and the other 2 held no 0. "
                 "Country Code and Country Name are reported as stored; on the tested "
                 "device two "
                 "images carrying known coordinates resolved to IS and US, consistent with the "
                 "app deriving them from the coordinates, and no source for that derivation is "
                 "cited here. The address table also has address line, admin area and locality "
                 "columns which were empty for both tested images, so the geocoding here reached "
                 "country level only. Date Added leads this table and Date Taken is the second "
                 "column; a row can carry no Date Taken, because the dateTaken table is joined "
                 "with a LEFT JOIN. Title is the entry title the app stores and was empty on all "
                 "six; what the app writes there was not sourced here. Favorite is the favourites "
                 "table flag and was set on one of the six tested entries, on which it had been "
                 "marked in the app. Rating is the metadata table's rating value, as stored. "
                 "Resume Position (ms) is the videoPlayback table value for the entry, reported "
                 "as stored, and is blank "
                 "where the table has no row for it. "
                 "KML output is produced from the coordinates. Each KML point is labelled with "
                 "the first filled time column of its row, which is Date Added where the row "
                 "carries one and not Date Taken. A row whose Latitude or Longitude is 0 gets "
                 "no KML point, because the KML writer skips a 0 in either column; the row is "
                 "still in the table. The metadata table's flags column is an "
                 "undocumented bitmask and is not reported. The covers and dynamicAlbums tables "
                 "were empty on the tested device and are not read.",
        "paths": ('*/deckers.thibault.aves*/databases/metadata.db*',),
        "output_types": "all",
        "artifact_icon": "image",
    },
    "aves_trash_vaults": {
        "name": "Aves Gallery - Trash and Vaults",
        "description": "Parses the trash and vaults tables of the Aves Gallery Android app.",
        "author": "@AlexisBrignoni, Claude, @AlexisBrignoni, Codex",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Aves Gallery",
        "sample_data": {
            "emu_a15_oss_v9": "Aves Gallery Libre 1.14.9 | 0 rows, checked: the trash and vaults tables are present and empty",
        },
        "notes": "Rows from the trash and vaults tables of databases/metadata.db, combined in one "
                 "artifact. Kind names which table a row came from. "
                 "A Trash row carries a Path and a Date, as Unix milliseconds reported as UTC. A "
                 "Vault row carries a Name, a Lock Type and an auto-lock flag; the vault's "
                 "contents are not in this table. What the app writes to either table, whether a "
                 "trashed file remains on the device at the Path, and what a vault row "
                 "establishes about a person's intent were not exercised, because both tables "
                 "were empty on the tested device. Lock Type is "
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
    if value in (None, ''):
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
