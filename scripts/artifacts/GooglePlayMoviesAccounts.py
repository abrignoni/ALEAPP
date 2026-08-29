__artifacts_v2__ = {
    "google_play_movies_account": {
        "name": "Google Play Movies & TV - Signed-In Accounts",
        "description": "Google accounts recorded by the Google Play Movies & TV app "
                       "(package com.google.android.videos, also branded 'Google TV') in "
                       "the user_data table of purchase_store.db, with whether each "
                       "account also has a row in the app's user_configuration table and "
                       "the country code stored in that row.",
        "author": "@Gear-I, @AlexisBrignoni, Claude",
        "creation_date": "2026-08-28",
        "last_update_date": "2026-08-29",
        "requirements": "blackboxprotobuf",
        "category": "Google Play Movies & TV",
        "notes": "Source is purchase_store.db. On 9 of the 18 database copies tested the "
                 "database file itself holds no tables at all and every row is in the write "
                 "ahead log, so the path pattern collects the sidecars and they must be "
                 "carried alongside the database. user_data holds one row per Google account "
                 "keyed on user_account and carries no timestamp, so it records which "
                 "accounts are present in the store and nothing about when or whether any of "
                 "them was used. user_configuration holds one row per account carrying a "
                 "configuration blob. 'Has Configuration Record' is Yes when a row for that "
                 "account is present in user_configuration and No when it is not; the store "
                 "does not record why a row is absent, and an absent row is not evidence "
                 "about how the account was used. Across the 16 tested images 19 accounts "
                 "are listed and 18 of them have a configuration record, the one exception "
                 "being on samsunga53_a14. The value is left blank if "
                 "user_configuration.config_account cannot be read, so a read failure is not "
                 "reported as a No. The column was readable on all 18 copies tested, so no "
                 "image exercised that branch; it was verified against a constructed copy "
                 "with the table removed, which reported the account with a blank value and "
                 "logged the reason. The country is likewise left blank and the reason "
                 "logged when config_proto is absent, verified the same way against a copy "
                 "carrying the table without that column. 'Country Code' is the first field "
                 "of the user_configuration.config_proto protobuf, reported as stored and "
                 "not validated against a shape. It held a two letter code for every account "
                 "that has a configuration record, and is blank for the one that does not; "
                 "US on 17 of the 18 copies and CH on galaxys10_a10. Three values agree on "
                 "that copy: the field itself, the rating system carried in the same blob "
                 "(FSK/CH, against the TVPG and MPAA/US carried by the US copies), and the "
                 "wifi country code the device's own Android settings record independently "
                 "of this app. What Google uses the field for is not documented and is not "
                 "claimed here. The app's own user_configuration.config_play_country column "
                 "is a different field and was NULL for every account tested. Source File "
                 "carries the evidence relative path of the database each row came from "
                 "rather than a derived profile number, so an account held under a second "
                 "Android user is attributable without inferring anything from the path: "
                 "russell_a14 and russell_pixel6a_a13 each carry a second copy under "
                 "data/user/10 holding a different account from the copy under data/data. "
                 "This artifact reports account identity only. Of the 23 tables in this "
                 "database, 17 were empty on all 18 copies tested, including "
                 "purchased_assets, search_history, wishlist, watch_next_feed, user_assets, "
                 "user_sentiments, assets, bundles, cached_items, posters, screenshots, "
                 "show_banners and show_posters, so no purchase, rental, search or watch "
                 "history was recoverable from any tested image. The only other populated "
                 "tables were android_metadata, video_formats (device decoder capabilities), "
                 "guide_settings (a small per-account blob, 1 row on 7 copies) and "
                 "ExoPlayerVersions, none of which carries user activity. Two schema "
                 "generations were seen, 21 and 23 tables, differing only by "
                 "ExoPlayerDownloads and ExoPlayerVersions; user_data and user_configuration "
                 "are present in both. user_data.sync_snapshot_token was NULL and "
                 "user_configuration.account_links was 0 for every account tested, so "
                 "neither is reported and what a populated value looks like is unconfirmed. "
                 "user_data.wishlist_snapshot_token was populated and held the identical "
                 "value on every account across every tested image, so it is not reported; "
                 "where that value comes from is not established. The rest of config_proto "
                 "holds Google reference configuration, meaning content rating systems, Play "
                 "API endpoints and feature flags, rather than account activity.",
        "paths": ('*/com.google.android.videos/databases/purchase_store.db*',),
        "output_types": ["standard"],
        "artifact_icon": "film",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.videos | 1 row",
            "cookbook_a11": "Android 11 | com.google.android.videos | 1 row",
            "galaxys10_a10": "Android 10 | com.google.android.videos | 1 row",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.videos | 1 row",
            "hc_pixel8pro_a17": "Android 17 | com.google.android.videos | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.google.android.videos | 1 row",
            "pixel3_a11": "Android 11 | com.google.android.videos | 1 row",
            "pixel3_a12": "Android 12 | com.google.android.videos | 1 row",
            "pixel7a_a14": "Android 14 | com.google.android.videos | 1 row",
            "russell_a14": "Android 14 | com.google.android.videos | 2 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.videos | 2 rows",
            "s20fe_a13": "Android 13 | com.google.android.videos not present | 0 rows",
            "samsunga53_a14": "Android 14 | com.google.android.videos | 2 rows",
            "samsungs20_a13": "Android 13 | com.google.android.videos | 1 row",
            "sharon_a13": "Android 13 | com.google.android.videos | 1 row",
            "sharon_a14": "Android 14 | com.google.android.videos | 1 row",
            "userb2_a13": "Android 13 | com.google.android.videos | 1 row",
        },
    },
}

import os

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (artifact_processor, decode_protobuf,
                               does_column_exist_in_db, get_sqlite_db_records, logfunc)

# blackboxprotobuf raises these when a blob does not decode as protobuf.
_PB_ERRORS = (ValueError, TypeError, IndexError, KeyError, AttributeError)


def _purchase_store_databases(files_found):
    """Every purchase_store.db in files_found, sidecars and matched directories excluded.

    A pattern whose last component ends in '*' can match a directory, and open() on
    one aborts the file loop, so directories are skipped before anything is opened.
    A second Android user profile has its own copy of purchase_store.db, so every
    match is read rather than only the first.
    """
    return [file_found for file_found in (str(f) for f in files_found)
            if os.path.basename(file_found) == 'purchase_store.db'
            and not os.path.isdir(file_found)]


def _pb_get(node, key):
    """Read one field out of a blackboxprotobuf dict.

    blackboxprotobuf splits a field whose repeats decode to different typedefs into
    'N-1', 'N-2' keys, so fall back to the first such variant when the plain key is absent.
    """
    if not isinstance(node, dict):
        return None
    if key in node:
        return node[key]
    for name in sorted(node):
        if name.startswith(f'{key}-'):
            return node[name]
    return None


def _config_country(config_proto):
    """Field 1 of a config_proto blob, as stored.

    Reported verbatim rather than validated against a shape, so an unexpected value
    reaches the report instead of being silently dropped. A field that is not a
    scalar, and a blob that does not decode, both yield an empty value.
    """
    if not config_proto:
        return ''
    try:
        message, _ = decode_protobuf(bytes(config_proto))
    except _PB_ERRORS:
        return ''
    value = _pb_get(message, '1')
    if isinstance(value, (bytes, bytearray)):
        value = value.decode('utf-8', 'replace')
    if isinstance(value, (dict, list)):
        return ''
    return '' if value is None else str(value)


def _configured_accounts(db_path, relative_path):
    """(accounts holding a user_configuration row, country by account, readable).

    'readable' is False when the table or its account column cannot be read. That is
    not the same as an account having no row and must not be reported as one.
    """
    if not does_column_exist_in_db(db_path, 'user_configuration', 'config_account'):
        logfunc(f'user_configuration.config_account not readable in {relative_path}; '
                'configuration state left blank for its accounts')
        return set(), {}, False
    if does_column_exist_in_db(db_path, 'user_configuration', 'config_proto'):
        query = "SELECT config_account, config_proto FROM user_configuration"
    else:
        query = "SELECT config_account, NULL FROM user_configuration"
        logfunc(f'user_configuration.config_proto not present in {relative_path}; '
                'country code left blank for its accounts')
    accounts = set()
    countries = {}
    for account, config_proto in get_sqlite_db_records(db_path, query):
        accounts.add(account)
        country = _config_country(config_proto)
        if country:
            countries[account] = country
    return accounts, countries, True


@artifact_processor
def google_play_movies_account(context):
    data_headers = (
        "Google Account Email", "Has Configuration Record", "Country Code", "Source File",
    )

    db_paths = _purchase_store_databases(unique_files(context))
    if not db_paths:
        return data_headers, [], ""

    data_list = []
    source_paths = []
    for db_path in db_paths:
        relative_path = context.get_relative_path(db_path)
        accounts = get_sqlite_db_records(db_path, "SELECT user_account FROM user_data")
        configured, countries, config_readable = _configured_accounts(db_path, relative_path)
        rows_before = len(data_list)
        for (account,) in accounts:
            has_config = ('Yes' if account in configured else 'No') if config_readable else ''
            data_list.append((account or '', has_config,
                              countries.get(account, ''), relative_path))
        if len(data_list) > rows_before:
            source_paths.append(db_path)

    return data_headers, data_list, '\n'.join(source_paths)
