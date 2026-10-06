__artifacts_v2__ = {
    "protondrive_useraccount": {
        "name": "Proton Drive - User Account",
        "description": "Parses Proton Drive User Account Information",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}, @AlexisBrignoni, Codex",
        "creation_date": "2025-11-14",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Proton Drive",
        "notes": "Field mapping was written against app version 2.29.1; no "
                 "sample data is recorded for it. createdAtUTC is read as "
                 "Unix milliseconds. Used and Max Space are the stored byte "
                 "counts divided to whole megabytes. Every distinct main database state is read. "
                 "Known canonical aliases collapse only if main/WAL/journal bytes agree; "
                 "conflicts remain separate. Combined inputs carry per-row evidence sources.",
        "paths": ('*/me.proton.android.drive/databases/db-drive'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "user"
    },
    "protondrive_fileinfo": {
        "name": "Proton Drive - File Info",
        "description": "Parses the LinkEntity table of the Proton Drive database. The column headed Stored User ID is LinkEntity.user_id; whether that is the owner of the item or the account the row was cached under is not established. Creation, last modified and trashed times are read as Unix seconds.",
        "author": "Damien Attoe {damien.attoe@spyderforensics.com}, @AlexisBrignoni, Codex",
        "creation_date": "2025-11-14",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Proton Drive",
        "notes": "Field mapping was written against app version 2.29.1; no sample data is "
                 "recorded for it. Every distinct main state is read, with known aliases collapsed "
                 "only when main/WAL/journal bytes agree; combined inputs carry per-row "
                 "evidence sources. Stored User ID is user_id, without an ownership assertion. Reference: Proton Drive Android, 'LinkDto (TYPE_FOLDER=1, "
                 "TYPE_FILE=2, TYPE_ALBUM=3; STATE_DRAFT=0, ACTIVE=1, TRASHED=2, DELETED=3, "
                 "RESTORING=4)', "
                 "https://github.com/ProtonDriveApps/android-drive/blob/e34735ace07f3c7da13e289d2653bd46537441e0/drive/link/data/src/main/kotlin/me/proton/core/drive/link/data/api/entity/LinkDto.kt",
        "paths": ('*/me.proton.android.drive/databases/db-drive'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "file"
    }
}

import hashlib
from pathlib import Path

from scripts.artifacts.storagePathViews import canonical_path

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, logfunc


def _proton_sources(context):
    """Collapse known aliases only when main and logical sidecar bytes agree."""
    paths = []
    seen = set()
    for candidate in context.get_files_found():
        path = str(candidate)
        if Path(path).name != 'db-drive':
            continue
        try:
            with open(path, "rb") as source:
                if source.read(16) != b"SQLite format 3\x00":
                    logfunc(f'Proton Drive: invalid SQLite header in {context.get_relative_path(path)}; skipping source')
                    continue
            state = []
            for suffix in ('', '-wal', '-journal'):
                try:
                    with open(path + suffix, 'rb') as source:
                        digest = hashlib.sha256()
                        for chunk in iter(lambda source=source: source.read(1024 * 1024), b''):
                            digest.update(chunk)
                    state.append(digest.hexdigest())
                except FileNotFoundError:
                    if not suffix:
                        raise
                    state.append(None)
            identity = (canonical_path(context.get_relative_path(path))[0], tuple(state))
        except OSError as error:
            logfunc(f'Proton Drive: skipping unreadable database {context.get_relative_path(path)}: {error}')
            continue
        if identity not in seen:
            seen.add(identity)
            paths.append(path)
    return paths


@artifact_processor
def protondrive_useraccount(context):
    source_paths = _proton_sources(context)
    multiple_sources = len(source_paths) > 1
    reported_sources = set()
    data_list = []

    query = '''
            SELECT
                UserEntity.userId AS 'User ID',
                UserEntity.email AS 'Email Address',
                UserEntity.name AS Username,
                DATETIME((UserEntity.createdAtUTC/1000),'unixepoch') AS 'Created Date (UTC)',
                UserEntity.usedspace/1024/1024 AS 'Used Space (MB)',
                UserEntity.Maxspace/1024/1024 AS 'Max Space (MB)'
            FROM UserEntity;
        '''

    data_headers = (('Created Date', 'datetime'), 'User ID', 'Email Address', 'Username',
                    'Used Space (MB)', 'Max Space (MB)')
    for source_path in source_paths:
        rows = get_sqlite_db_records(source_path, query)
        for row in rows:
            reported_sources.add(source_path)
            record = (row[3],) + tuple(row[:3]) + tuple(row[4:])
            if multiple_sources:
                record += (context.get_relative_path(source_path),)
            data_list.append(record)

    if multiple_sources:
        data_headers += ('Source File',)
    return data_headers, data_list, '\n'.join(sorted(reported_sources))


@artifact_processor
def protondrive_fileinfo(context):
    source_paths = _proton_sources(context)
    multiple_sources = len(source_paths) > 1
    reported_sources = set()
    data_list = []

    query = '''
        SELECT
            LinkEntity.id,
            LinkEntity.share_id,
            LinkEntity.user_id,
            LinkEntity.parent_id,
            CASE LinkEntity.type
                WHEN 1 THEN 'Folder'
                WHEN 2 THEN 'File'
                WHEN 3 THEN 'Album'
                ELSE LinkEntity.type
            END AS type,
            LinkEntity.name,
            CASE LinkEntity.state
                WHEN 0 THEN 'Draft'
                WHEN 1 THEN 'Active'
                WHEN 2 THEN 'Trashed'
                WHEN 3 THEN 'Deleted'
                WHEN 4 THEN 'Restoring'
                ELSE LinkEntity.state
            END AS state,
            datetime(LinkEntity.creation_time, 'unixepoch'),
            datetime(LinkEntity.last_modified, 'unixepoch'),
            datetime(LinkEntity.trashed_time, 'unixepoch'),
            LinkEntity.size,
            LinkEntity.mime_type,
            CASE LinkEntity.is_shared
                WHEN 1 THEN 'YES'
                WHEN 0 THEN 'NO'
                ELSE LinkEntity.is_shared
            END AS is_shared,
            LinkEntity.number_of_accesses
        FROM LinkEntity;
    '''

    for source_path in source_paths:
        db_records = get_sqlite_db_records(source_path, query)

        for row in db_records:
            reported_sources.add(source_path)
            link_id = row[0]
            user_id = row[2]
            type_val = row[4]
            name = row[5]
            state_val = row[6]
            creation_time = row[7]
            last_modified = row[8]
            trashed_time = row[9]
            size = row[10]
            mime_type = row[11]
            is_shared = row[12]
            number_of_accesses = row[13]

            data_list.append(
                (link_id, user_id, type_val, name, state_val, creation_time, last_modified,
                 trashed_time, size, mime_type, is_shared, number_of_accesses))
            if multiple_sources:
                data_list[-1] += (context.get_relative_path(source_path),)

    data_headers = (('Creation Time', 'datetime'), ('Last Modified', 'datetime'),
                    ('Trashed Time', 'datetime'), 'ID', 'Stored User ID', 'Type', 'Name', 'State', 'Size', 'MIME Type',
                    'Is Shared', 'Number of Accesses')

    data_list = [row[5:8] + row[:5] + row[8:] for row in data_list]
    if multiple_sources:
        data_headers += ('Source File',)
    return data_headers, data_list, '\n'.join(sorted(reported_sources))
