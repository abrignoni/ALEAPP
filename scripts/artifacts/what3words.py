__artifacts_v2__ = {
    "what3words_saved_places": {
        "name": "what3words - Locations",
        "description": "Rows of the class_LocationRealm table of the what3words Realm store, from the "
                       "active version and, where they differ, the inactive version. Columns include "
                       "the three word address, label, nearestPlace value and the stored lat and lng values",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Locations & Maps",
        "notes": "Read from the class_LocationRealm table of the app's Realm store "
                 "(files/default.realm) using the vendored realm_parser. Latitude and Longitude are the lat and lng values stored in the same row as the address. Modification Time is the modificationTime Realm timestamp, shown as UTC. What sets it is not established. A Realm file header has two version slots, and one bit selects the slot in use (realm-core alloc_slab.hpp, the Header struct at v14.0.0, https://github.com/realm/realm-core/blob/faf9c152af9449b622e28cc144c98ecda5faf656/src/realm/alloc_slab.hpp#L592-L600; it has the same fields at v10.0.0 and v13.0.0). Each commit writes the new version's top ref into the slot not in use and then switches the header to it (realm-core group_writer.cpp: GroupWriter::commit at v10.0.0, https://github.com/realm/realm-core/blob/c29f4347aff5d1f61f7672c05ebf1bfbc1d44d25/src/realm/group_writer.cpp#L898-L947, and at v13.0.0, https://github.com/realm/realm-core/blob/82e57f1d2f1edd2393f2ac10f719c56adcc5aed1/src/realm/group_writer.cpp#L1263-L1319; GroupCommitter::commit at v14.0.0, https://github.com/realm/realm-core/blob/faf9c152af9449b622e28cc144c98ecda5faf656/src/realm/group_writer.cpp#L1374-L1426). The stores read here are file format 20 and 23. The realm-core release inside the app was not read. On that reading the inactive slot points to the version that was current before the last commit. A slot can be empty: the two stores under user 10 hold one version. Realm Version names the version a row comes from: Active for the current one, Inactive for the other. Every row of the active version is reported. An inactive row is reported when no active row of the same store holds the same value in every column of the table, including the columns this artifact does not show. The vendored Realm reader returns modificationTime as a whole second, so Modification Time carries no fraction of a second. modificationTime is the one date column of the table on the four images with rows. Two versions of a row that differ only in that fraction count as matching, and the inactive one is not shown. That case is not exercised on real data: on the four images with rows the stored seconds and nanoseconds are the same in both versions. A stored fraction within about 120 nanoseconds of the next second is returned as the next second. No value on those images is in that range. On hc_pixel8pro_a16, hc_pixel8pro_a17 and sharon_a14 the inactive version holds the same rows as the active one, so only Active rows are shown. The stores on hc_pixel8pro_a16 and hc_pixel8pro_a17 are byte identical. On sharon_a13 it holds one row whose id is not in the active version. That row matches an active row in every other column of the table, so in the report the two rows differ only in id (as stored) and Realm Version. Whether a place deleted in the app shows up as an Inactive row is not tested on real data. id (as stored) is the id value; what it identifies is not established. order (as stored) is the order value; what it means is not established. listIds (as stored) is the listIds list, its values joined with a comma and a space in stored order. It is blank when the reader returns no values for the row, so a blank does not show the list is empty. A row with several values and a blank row are not exercised on real data. On the four images with rows each location row holds one value, and it equals the id (as stored) of a row in what3words - Location Lists. Each of those stores holds one list row, and every location row of that store holds that row's id. What the app records in it is not established from its code. listIdsConcat is not reported: on those rows it holds the same id followed by a vertical bar. The createdAt, isShared and address columns are not reported because no source for what they hold was read. isShared held false on every row on the four images with rows. Location Type Value is the locationType value as stored; its meaning is not established, so a row is not shown to be a saved place by this artifact alone. Each default.realm found whose active version holds either table is read, and the rows are reported together. A file the parser cannot decode gives no rows. Copies of one store under different storage paths are read once. Android User is the user the store's path denotes: 0 for data/data, the number in the path for data/user/<n> and the mirrored layouts, and blank for a path under none of them, which includes a rollback snapshot. No column other than Android User separates two stores. Of the 39 images run, 6 held a store, one each. Four gave rows, all for user 0. The other two sit under user 10, hold no rows in either table, and are the same file, byte for byte. A second store on one image, and a row for a user other than 0, are not exercised on real data.",
        "paths": ('*/com.what3words.android/files/default.realm',),
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.what3words.android | 2 rows",
        },
    },
    "what3words_lists": {
        "name": "what3words - Location Lists",
        "description": "Rows of the class_LocationsListsRealm table of the what3words Realm store, with "
                       "the list label, the stored count and createdBy values, and the createdWhen and "
                       "updatedAt values read as times",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-11-26",
        "requirements": "none",
        "category": "Locations & Maps",
        "notes": "Read from the class_LocationsListsRealm table of the app's Realm store. "
                 "createdBy (as stored) is the createdBy value; what it identifies is not "
                 "established. isSharedList (as stored) is the isSharedList boolean shown as True or False, "
                 "and is blank where the row holds none. The blank case is not exercised on real data. Created and Updated are the createdWhen and updatedAt integers "
                 "shown as UTC. They are read as Unix time, with the unit taken from the size of the number. The epoch and unit are not confirmed from the app's code. On hc_pixel8pro_a16, hc_pixel8pro_a17, sharon_a13 and sharon_a14 (one list row each) createdWhen has 13 digits, read as milliseconds and cut to whole seconds. updatedAt has 10 digits, read as seconds, on three of them and holds no value on sharon_a13. A value of 0 or no value is shown blank. The listTypeId, order, sortBy, collaboratorCount and followerCount columns are not reported because no source for what they hold was read. On the four images with rows, order, collaboratorCount and followerCount held 0 or no value. A Realm file header has two version slots, and one bit selects the slot in use (realm-core alloc_slab.hpp, the Header struct at v14.0.0, https://github.com/realm/realm-core/blob/faf9c152af9449b622e28cc144c98ecda5faf656/src/realm/alloc_slab.hpp#L592-L600; it has the same fields at v10.0.0 and v13.0.0). Each commit writes the new version's top ref into the slot not in use and then switches the header to it (realm-core group_writer.cpp: GroupWriter::commit at v10.0.0, https://github.com/realm/realm-core/blob/c29f4347aff5d1f61f7672c05ebf1bfbc1d44d25/src/realm/group_writer.cpp#L898-L947, and at v13.0.0, https://github.com/realm/realm-core/blob/82e57f1d2f1edd2393f2ac10f719c56adcc5aed1/src/realm/group_writer.cpp#L1263-L1319; GroupCommitter::commit at v14.0.0, https://github.com/realm/realm-core/blob/faf9c152af9449b622e28cc144c98ecda5faf656/src/realm/group_writer.cpp#L1374-L1426). The stores read here are file format 20 and 23. The realm-core release inside the app was not read. On that reading the inactive slot points to the version that was current before the last commit. A slot can be empty: the two stores under user 10 hold one version. Realm Version names the version a row comes from: Active for the current one, Inactive for the other. Every row of the active version is reported. An inactive row is reported when no active row of the same store holds the same value in every column of the table, including the columns this artifact does not show. On those four images the inactive version held the same list row as the active one, so only Active rows are shown. An Inactive row in this artifact is not exercised on real data. count (as stored) is the count value. On the four images with rows it equals the number of Active location rows whose listIds (as stored) holds the list's id. On sharon_a13 an Inactive location row holds it too and is not in the count. What the app counts is not established. color (as stored) is the color value. id (as stored) is the id value of the list row. On the four images with rows each list id is named in listIds (as stored) of the location rows in what3words - Locations. shareType held no value on the four images with rows. Each default.realm found whose active version holds either table is read, and the rows are reported together. A file the parser cannot decode gives no rows. Copies of one store under different storage paths are read once. Android User is the user the store's path denotes: 0 for data/data, the number in the path for data/user/<n> and the mirrored layouts, and blank for a path under none of them, which includes a rollback snapshot. No column other than Android User separates two stores. Of the 39 images run, 6 held a store, one each. Four gave rows, all for user 0. The other two sit under user 10, hold no rows in either table, and are the same file, byte for byte. A second store on one image, and a row for a user other than 0, are not exercised on real data.",
        "paths": ('*/com.what3words.android/files/default.realm',),
        "output_types": "standard",
        "artifact_icon": "list",
        "sample_data": {
            "hc_pixel8pro_a17": "Android 17 | com.what3words.android | 1 row",
        },
    },
}

from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import android_user, unique_files
from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc
from scripts.realm_parser import parse_realm_file, realm_rows


def _realm_ts(value):
    """The vendored realm_parser renders Realm date columns as 'YYYY-MM-DD HH:MM:SS UTC';
    turn that into a timezone-aware datetime so it sorts and timelines correctly."""
    if not value or not isinstance(value, str):
        return value
    try:
        return datetime.strptime(value.replace(' UTC', ''), '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
    except ValueError:
        return value


def _is_what3words_realm(path):
    """Guard: the default.realm name is used by several apps, so confirm this Realm
    actually carries what3words classes before reporting rows."""
    tables = parse_realm_file(path).get("active", {})
    return 'class_LocationRealm' in tables or 'class_LocationsListsRealm' in tables


def _joined(values):
    """A Realm list column as stored, its values joined in stored order; blank when empty."""
    return ', '.join(str(value) for value in values) if values else ''


def _row_key(value):
    """A hashable form of a row or column value, equal for equal values, so a row can be looked up."""
    if isinstance(value, dict):
        return ('dict', tuple(sorted((k, _row_key(v)) for k, v in value.items())))
    if isinstance(value, (list, tuple)):
        return tuple(_row_key(v) for v in value)
    try:
        hash(value)
    except TypeError:
        return (type(value).__name__, repr(value))
    return value


def _version_rows(path, class_name):
    """Each row of the active version, then each inactive row that no active row matches in every column."""
    active = set()
    for row in realm_rows(path, class_name):
        active.add(_row_key(row))
        yield 'Active', row
    for row in realm_rows(path, class_name, section='inactive'):
        if _row_key(row) not in active:
            yield 'Inactive', row


def _realm_paths(context):
    """Each what3words store, one per Android user and storage view."""
    return [str(path) for path in unique_files(context)
            if str(path).endswith('default.realm') and _is_what3words_realm(str(path))]


@artifact_processor
def what3words_saved_places(context):
    source_paths = _realm_paths(context)
    data_list = []

    for source_path in source_paths:
        user = android_user(context.get_relative_path(source_path))
        for version, row in _version_rows(source_path, 'class_LocationRealm'):
            data_list.append((
                _realm_ts(row.get('modificationTime')),
                row.get('threeWordAddress'),
                row.get('label'),
                row.get('nearestPlace'),
                row.get('lat'),
                row.get('lng'),
                row.get('countryCode'),
                row.get('language'),
                row.get('locationType'),
                row.get('order'),
                row.get('id'),
                _joined(row.get('listIds')),
                version,
                user,
            ))

    data_headers = (
        ('Modification Time', 'datetime'),
        'Three Word Address',
        'Label',
        'Nearest Place',
        'Latitude',
        'Longitude',
        'Country Code',
        'Language',
        'Location Type Value',
        'order (as stored)',
        'id (as stored)',
        'listIds (as stored)',
        'Realm Version',
        'Android User',
    )
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def what3words_lists(context):
    source_paths = _realm_paths(context)
    data_list = []

    for source_path in source_paths:
        user = android_user(context.get_relative_path(source_path))
        for version, row in _version_rows(source_path, 'class_LocationsListsRealm'):
            created_when = row.get('createdWhen')
            updated_at = row.get('updatedAt')
            data_list.append((
                convert_unix_ts_to_utc(created_when) if created_when else '',
                convert_unix_ts_to_utc(updated_at) if updated_at else '',
                row.get('label'),
                row.get('count'),
                row.get('createdBy'),
                row.get('color'),
                '' if row.get('isSharedList') is None else str(row.get('isSharedList')),
                row.get('shareType'),
                row.get('sharedListId'),
                row.get('id'),
                version,
                user,
            ))

    data_headers = (
        ('Created', 'datetime'),
        ('Updated', 'datetime'),
        'Label',
        'count (as stored)',
        'createdBy (as stored)',
        'color (as stored)',
        'isSharedList (as stored)',
        'Share Type',
        'Shared List ID',
        'id (as stored)',
        'Realm Version',
        'Android User',
    )
    return data_headers, data_list, '\n'.join(source_paths)
