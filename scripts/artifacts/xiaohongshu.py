__artifacts_v2__ = {
    "xiaohongshu_play_history": {
        "name": "Xiaohongshu (RED) - Play History",
        "description": "Entries in the Xiaohongshu play history store, with the note identifier, "
                       "the note title and description as stored, the note author's display name "
                       "and the recorded timestamp",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Xiaohongshu",
        "notes": "Read from the historyRecord table of the PlayHistoryRecordDB Room store in "
                 "com.xingin.xhs (Xiaohongshu, also published as RED and as Little Red Book).\n"
                 "Column meanings are taken from the column names the app declares. user_id is "
                 "the local account the row is filed under and is reported as Account User ID; "
                 "user_name is the note author's display name, which is a different party, so the "
                 "two are reported under distinct headers to keep them from being read as the "
                 "same person. author_id existed in the tested corpus but was an empty string on "
                 "every row, so it is reported as stored rather than dropped.\n"
                 "The timestamp is Unix epoch milliseconds. What the app records in this table is "
                 "an entry per note; the table is named a play history by the app, and this "
                 "artifact reports its rows without asserting how much of a note was played or "
                 "that the account holder saw any particular part of it.\n"
                 "Note Title and Note Description are stored by the app as the note's own text "
                 "and are reported as stored, in their original language, hashtags included. The "
                 "title was empty on some rows in the tested corpus while the description was "
                 "populated.\n"
                 "Scope: this is the only Xiaohongshu store in the tested corpora that could be "
                 "read. See the module notes on the encrypted stores.",
        "paths": ('*/com.xingin.xhs/databases/PlayHistoryRecordDB*',),
        "output_types": "standard",
        "artifact_icon": "play-circle",
        "sample_data": {
            "kevin_pocox7_a15": "Android 15 | Xiaohongshu | 45 rows",
            "sharon_a14": "Android 14 | Xiaohongshu | 0 rows (store not present)",
        },
    },
}

# What this module does not cover, and why.
#
# Xiaohongshu keeps its messages in databases/msgDB and its contact relations in
# databases/localRelationDB. In both tested corpora those files carry no SQLite
# header and measured Shannon entropy of 8.00 over the sampled bytes, while their
# -wal sidecars carry the standard SQLite WAL magic. That combination is
# consistent with page-level encryption of the main database, such as SQLCipher.
# A search of the app's shared_prefs found no key. They are therefore not parsed
# here, and no claim is made about their contents.
#
# The same applies to xhs_common_demotion_cache.db, which is the largest store in
# the package at about 11 MB.
#
# databases/cg.db and databases/dim.db are readable SQLite but hold base64 blobs
# under single-letter column names, which in the tested corpus decoded to SDK
# configuration rather than user data, so they are not reported.

from scripts.ilapfuncs import (artifact_processor, convert_unix_ts_to_utc, get_file_path,
                               get_sqlite_db_records, does_table_exist_in_db)


@artifact_processor
def xiaohongshu_play_history(context):
    source_path = get_file_path(context.get_files_found(), 'PlayHistoryRecordDB')
    data_list = []

    if source_path and does_table_exist_in_db(source_path, 'historyRecord'):
        query = '''
        SELECT timestamp, note_title, note_desc, user_name, note_id, author_id, user_id
        FROM historyRecord
        ORDER BY timestamp
        '''
        for record in get_sqlite_db_records(source_path, query):
            data_list.append((
                convert_unix_ts_to_utc(record[0]) if record[0] else '',
                record[1],
                record[2],
                record[3],
                record[4],
                record[5],
                record[6],
            ))

    data_headers = (
        ('Timestamp', 'datetime'),
        'Note Title',
        'Note Description',
        'Note Author Name',
        'Note ID',
        'Note Author ID (as stored)',
        'Account User ID',
    )
    return data_headers, data_list, source_path
