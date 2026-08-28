__artifacts_v2__ = {
    "google_play_movies_account": {
        "name": "Google Play Movies & TV - Signed-In Accounts",
        "description": "The Google account(s) the Google Play Movies & TV app (package "
                       "com.google.android.videos, also branded 'Google TV') knows about on "
                       "this device, and whether each one has an active configuration synced "
                       "from Google's Play backend.",
        "author": "@Gear-I, Claude",
        "creation_date": "2026-08-28",
        "last_update_date": "2026-08-28",
        "requirements": "none",
        "category": "Google Play Movies & TV",
        "notes": "Source is purchase_store.db. user_data.user_account lists every Google "
                 "account this app instance has ever been used with; a matching row in "
                 "user_configuration.config_account means that account currently has an "
                 "active, synced configuration from Google's Play backend, reported here as "
                 "'Play Config Synced'. On the Samsung device this was validated against, two "
                 "different Google accounts were both listed in user_data but only one had a "
                 "config row -- evidence that a second account was added to the app without "
                 "becoming (or after ceasing to be) the one actively used, a distinction this "
                 "column exists to surface. This artifact reports identity only, not activity: "
                 "purchased_assets, search_history, wishlist and watch_next_feed were all "
                 "completely empty on both real devices this was validated against, so no "
                 "purchase, rental, search or watch history survives in this database despite "
                 "its file carrying substantial WAL activity -- that activity turned out to be "
                 "the app re-syncing static reference data (content-rating systems, API "
                 "endpoints), not user activity, confirmed by reading it directly. "
                 "user_data.sync_snapshot_token and user_configuration.config_play_country "
                 "were NULL for every account on both devices, and "
                 "user_configuration.account_links was 0 for every account on both devices, so "
                 "none of the three are reported -- what a populated value looks like is "
                 "unconfirmed. user_data.wishlist_snapshot_token was populated but held the "
                 "identical value on every account tested, across both devices, despite "
                 "different accounts and different install histories, so it reads as a static "
                 "default baked into the app rather than a real per-account sync cursor and is "
                 "also not reported. A second Android user profile has its own copy of "
                 "purchase_store.db, so every copy found is read, not only the first.",
        "paths": ('*/com.google.android.videos/databases/purchase_store.db*',),
        "output_types": ["standard"],
        "artifact_icon": "film",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.google.android.videos | 1 row",
            "samsunga53_a14": "Android 14 | com.google.android.videos | 2 rows",
        },
    },
}

import os

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records


def _purchase_store_databases(files_found):
    """Every purchase_store.db in files_found, sidecars and matched directories excluded.

    A pattern whose last component ends in '*' can match a directory, and open() on
    one aborts the file loop, so directories are skipped before anything is opened.
    A second Android user profile has its own copy of purchase_store.db, so every
    match is read rather than only the first.
    """
    return [file_found for file_found in (str(f) for f in files_found)
            if os.path.basename(file_found) == 'purchase_store.db' and not os.path.isdir(file_found)]


@artifact_processor
def google_play_movies_account(context):
    data_headers = (
        "Google Account Email", "Play Config Synced",
    )

    db_paths = _purchase_store_databases(unique_files(context))
    if not db_paths:
        return data_headers, [], ""

    data_list = []
    source_paths = []
    for db_path in db_paths:
        accounts = get_sqlite_db_records(db_path, "SELECT user_account FROM user_data")
        configured = {row[0] for row in
                      get_sqlite_db_records(db_path, "SELECT config_account FROM user_configuration")}
        rows_before = len(data_list)
        for (account,) in accounts:
            data_list.append((account or '', 'Yes' if account in configured else 'No'))
        if len(data_list) > rows_before:
            source_paths.append(db_path)

    return data_headers, data_list, '\n'.join(source_paths)