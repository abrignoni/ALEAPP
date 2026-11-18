__artifacts_v2__ = {
  
    "snotes": {
        "name": "Samsung Notes",
        "description": "Rows of the sdoc table in each Samsung Notes sdoc.db found, with the note's title, text, stored times and the media files kept in the note's own media folder.",
        "author": "Marco Neumann {kalinko@be-binary.de}, @AlexisBrignoni, Codex, Claude",
        "creation_date": "2026-01-17",
        "last_update_date": "2026-11-18",
        "requirements": "os",
        "category": "Notes",
        "notes": (
            "Every sdoc.db matched is read. On the tested images that is one per Android user that "
            "holds the app. Android User is the user of the app data folder the database is in, taken "
            "from its path (data/data is user 0); it is not a stored value. It is blank when the "
            "database is not under an app data folder, such as a rollback snapshot. No tested image has "
            "that case. On samsung_a166u_a16_known_20261117 the 4 rows from data/data show 0 and the 1 "
            "row from the user 150 (Secure Folder) database shows 150. Where an extraction holds the "
            "same database under more than one storage path, one copy is read. On samsungs20_a13 two "
            "databases are present: the one under user 150 holds the 7 rows and the other holds none. "
            "Creation Time, Last Modification Time, Recycle Bin Time Moved, First Opened Time, Second "
            "Opened Time and Last Opened Time are the columns createdAt, lastModifiedAt, "
            "recycle_bin_time_moved, firstOpendAt, secondOpenedAt and lastOpenedAt, read as Unix "
            "milliseconds and shown in UTC. A stored 0 is shown blank. On the six tested images (23 "
            "rows) recycle_bin_time_moved is 0 on the 19 rows whose isDeleted is 0. It is filled on the "
            "4 other rows: 2 with isDeleted 1 on samsungs20_a13 and 1 with isDeleted 2 on each "
            "samsung_a166u image. secondOpenedAt is 0 on 21 rows and lastOpenedAt on 22. The filled "
            "ones are on cookbook_a11. isDeleted is shown as stored. No source for what the app records "
            "in isDeleted, recycle_bin_time_moved or the three opened columns was found, so the headers "
            "repeat the column names and assert nothing more. Media lists the files in the media folder "
            "of the SDocData folder named by the last part of the row's filePath, under the same "
            "Android user as the database that was read, leaving out names ending in dat or spi. On the "
            "tested images that is one PDF file on each of two samsungs20_a13 rows and one JPEG file on "
            "the cookbook_a11 user 150 row. The declared media path matches only under a user folder, "
            "so media is not collected for a database reached only through a data/data path. On "
            "samsung_a166u_a16_known_20261117 First Opened Time, Second Opened Time, Last Opened Time "
            "and Media were blank on all 5 rows. The opened columns held 0. The archive's note media "
            "folders held only files ending in dat (5 files), and the 4 under data/data are not matched "
            "by the media path."
        ),
        "output_types": ["standard"],
        "paths": (  '*/com.samsung.android.app.notes/databases/sdoc.db*',
                    '*/user/*/com.samsung.android.app.notes/SDocData/*/media/*'),
        "artifact_icon": "edit",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | com.samsung.android.app.notes | 5 rows (4 user 0, 1 user 150)",
            "samsung_a166u_a16_known_20261116": "Android 16 | com.samsung.android.app.notes | 4 rows",
            "cookbook_a11": "Android 11 | com.samsung.android.app.notes | 4 rows (3 user 0, 1 user 150)",
            "anne_a15": "Android 15 | com.samsung.android.app.notes vc 443081000 | 2 rows",
            "samsungs20_a13": "Android 13 | com.samsung.android.app.notes vc 442923000 | 7 rows",
            "sharon_a14": "Android 14 | com.samsung.android.app.notes vc 441305000 | 1 row",
        }
    }

}

# Android Samsung Notes App (com.samsung.android.app.notes)
# Author:  Marco Neumann (kalinko@be-binary.de)
# Tested Version: 4.4.30.91
import os
from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records, check_in_media
from scripts.artifacts.storagePathViews import canonical_path, unique_files


def _ms_to_utc(value):
    # The time columns hold Unix milliseconds, and 0 where the app stored no time.
    # A stored 0 or NULL is reported blank rather than passed to a datetime column.
    if not value:
        return ''
    return convert_unix_ts_to_utc(int(value)/1000)


@artifact_processor
def snotes(context):
    files_found = unique_files(context)

    main_dbs = []
    medias = {}

    for file_found in files_found:
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        key = canonical_path(context.get_relative_path(file_found))[0].replace('\\', '/')
        name = os.path.basename(file_found)

        if name == 'sdoc.db':
            main_dbs.append((file_found, key))
        elif key.split('/')[-2:-1] == ['media']:
            if not name.endswith('dat') and not name.endswith('spi'):
                medias.setdefault(key.rsplit('/', 1)[0], []).append(file_found)

    query = ('''
        SELECT
        sd.createdAt,
        sd.lastModifiedAt,
        sd.title,
        sd.content,
        sd.isDeleted ,
        sd.recycle_bin_time_moved,
        sd.firstOpendAt,
        sd.secondOpenedAt,
        sd.lastOpenedAt,
        sd.filePath
        FROM sdoc sd
    ''')

    data_list = []
    sources = []

    def android_user(key):
        # canonical_path puts "<storage>:<user>" between two NULs for an app data path.
        parts = key.split('\x00')
        return parts[1].rsplit(':', 1)[-1] if len(parts) >= 3 else ''

    for main_db, db_key in main_dbs:
        db_records = get_sqlite_db_records(main_db, query)
        source = context.get_relative_path(main_db)
        sources.append(source)
        # The app's data folder, two levels above databases/sdoc.db, in the same
        # form the media keys are in, so a note only takes media from its own
        # Android user's copy of the app.
        container = db_key.rsplit('/', 2)[0]
        user = android_user(db_key)

        for row in db_records:
            created = _ms_to_utc(row[0])
            last_modified = _ms_to_utc(row[1])
            title = row[2]
            content = row[3]
            if isinstance(content, bytes):
                content = content.decode('utf-8', errors='replace')
            is_deleted = row[4]
            bin_moved = _ms_to_utc(row[5])
            first_opened = _ms_to_utc(row[6])
            second_opened = _ms_to_utc(row[7])
            last_opened = _ms_to_utc(row[8])
            file_path = row[9]

            # Only the files in this note's own media folder, matched on the whole
            # folder name. Only truthy refs are kept so no None lands in the media
            # list -- a None serialized to null in the json.dumps'd media cell
            # crashes the LAVA viewer on hover.
            media_refs = []
            note_folder = os.path.basename(str(file_path or '').replace('\\', '/').rstrip('/'))
            if note_folder:
                media_folder = f'{container}/SDocData/{note_folder}/media'
                for media_path in medias.get(media_folder, []):
                    ref = check_in_media(media_path, os.path.basename(media_path))
                    if ref:
                        media_refs.append(ref)
            if len(media_refs) == 1:
                media = media_refs[0]
            elif media_refs:
                media = media_refs
            else:
                media = ''

            data_list.append((  created,
                                last_modified,
                                title,
                                content,
                                is_deleted,
                                bin_moved,
                                first_opened,
                                second_opened,
                                last_opened,
                                media,
                                user)
                            )

    data_headers = (
                        ('Creation Time', 'datetime'),
                        ('Last Modification Time', 'datetime'),
                        'Title',
                        'Text Content',
                        'isDeleted',
                        ('Recycle Bin Time Moved', 'datetime'),
                        ('First Opened Time', 'datetime'),
                        ('Second Opened Time', 'datetime'),
                        ('Last Opened Time', 'datetime'),
                        ('Media', 'media'),
                        'Android User'
                    )

    return data_headers, data_list, '\n'.join(sources)
