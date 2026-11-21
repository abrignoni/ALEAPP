__artifacts_v2__ = {
    "chromeReadingList": {
        "name": "Chrome Reading List",
        "description": "Pages saved to the reading list of Chromium-based browsers, with the "
                       "title and address, when each was added, first read and last updated, "
                       "and its read status.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Chrome",
        "notes": ('Reads the Sync Data/LevelDB folder of Chromium-based browsers: app_chrome/<profile>/Sync'
                  ' Data/LevelDB, and app_opera/Sync Data/LevelDB for Opera, read only when the directory '
                  'directly above app_chrome or app_opera is shaped like a package name, with the store '
                  'reader the Chrome Sync artifacts use (chromeSyncSessions.py), which reads only the '
                  'newest version of each key and skips a key whose newest version is a deletion. The '
                  'storage views one Android extraction can hold for an app data directory are collapsed so'
                  " a store is read once, and a second Android user's store is read as its own. The reading"
                  ' list model writes its entries to this store: ReadingListModelStorageImpl writes each '
                  "entry keyed by the entry's URL as a ReadingListLocal message "
                  '(https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/reading_list/core/reading_list_model_storage_impl.cc#L33-L36),'
                  ' found under the reading_list type in the emulator known data, and decoded with the '
                  'field numbers of reading_list.proto '
                  '(https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/reading_list/core/proto/reading_list.proto#L16-L50).'
                  ' In the emulator known data the entry was added with sync on and remained after '
                  'sign-out; an entry added with sync off was not tested. One row per live entry. Title and'
                  ' URL are title and url as stored. Added, First Read and Updated are creation_time_us, '
                  'first_read_time_us and update_time_us, microseconds since 1970-01-01 UTC '
                  '(https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/reading_list/core/reading_list_entry.cc#L23-L25);'
                  ' a zero is shown blank, as First Read is on an entry not yet read. Status is status '
                  'named with ReadingListEntryStatus, UNREAD (0), READ (1) or UNSEEN (2); the proto says an'
                  ' absent status means UNSEEN, and an absent status is shown blank. Not read: entry_id, '
                  'update_title_time_us, estimated_read_time_seconds and the distillation fields of the '
                  'message (distillation_state, distilled_path, distilled_url, failed_download_counter, '
                  'backoff, distillation_time_us, distillation_size). Of the 53 corpus images listed in '
                  'sample_data, 37 had a Sync Data folder and none held a live reading_list record; 16 had '
                  'no such folder. The artifact is exercised only by the emulator known data from one '
                  "Android 15 emulator with Chrome 124.0.6367.219, where an entry added from a link's Add "
                  'to reading list at 15:16:45 UTC had Added 15:16:45 and Status UNSEEN (2), and after it '
                  'was opened from the reading list at 15:22:48 UTC had First Read and Updated 15:22:48 and'
                  ' Status READ (1); the entry remained after Chrome was signed out with Also clear your '
                  'Chrome data left unchecked.'),
        "paths": ('*/app_chrome/*/Sync Data/LevelDB/*', '*/app_opera/Sync Data/LevelDB/*'),
        "output_types": "standard",
        "artifact_icon": "book",
        "sample_data": {
            "anne_a15": "Android 15 | 0 rows (no live reading_list record in the Sync Data folders)",
            "cookbook_a11": "Android 11 | 0 rows (no live reading_list record in the Sync Data folders)",
            "df020_mavic_pro_android": "0 rows (no Sync Data folder matched)",
            "dfrws2011_case1_a855": "0 rows (no Sync Data folder matched)",
            "dfrws2011_case2_droid_a201": "Android 2.0.1 | 0 rows (no Sync Data folder matched)",
            "emu_a15_chrome_read_known_20261116": "Android 15 | 1 row",
            "emu_a15_chrome_signedin_known_20261116": "Android 15 | 1 row",
            "emu_a15_chrome_signedout_known_20261116": "Android 15 | 1 row",
            "emu_a15_kd_fsapi_k1_embedded_written": "Android 15 | 0 rows (no Sync Data folder matched)",
            "emu_a15_kd_fsapi_k2_embedded_history_cleared": "Android 15 | 0 rows (no Sync Data folder matched)",
            "emu_a15_kd_fsapi_k3_embedded_sitedata_cleared": "Android 15 | 0 rows (no Sync Data folder matched)",
            "emu_a15_kd_fsapi_s1_written": "Android 15 | 0 rows (no Sync Data folder matched)",
            "emu_a15_kd_fsapi_s2_history_cleared": "Android 15 | 0 rows (no Sync Data folder matched)",
            "emu_a15_kd_fsapi_s3_sitedata_cleared": "Android 15 | 0 rows (no Sync Data folder matched)",
            "emu_a15_kd_usage_u1_visit_share": "Android 15 | 0 rows (no Sync Data folder matched)",
            "emu_a15_kd_usage_u2_expired": "Android 15 | 0 rows (no Sync Data folder matched)",
            "emu_a15_kd_usage_u3_history_cleared": "Android 15 | 0 rows (no Sync Data folder matched)",
            "emu_a15_kd_usage_u4_history_cleared_all": "Android 15 | 0 rows (no Sync Data folder matched)",
            "emu_a15_kdl_v1": "Android 15 | 0 rows (no Sync Data folder matched)",
            "emu_a15_oss2_v1": "Android 15 | 0 rows (no Sync Data folder matched)",
            "emu_a15_oss2_v2": "Android 15 | 0 rows (no live reading_list record in the Sync Data folders)",
            "emu_a15_oss2_v3": "Android 15 | 0 rows (no live reading_list record in the Sync Data folders)",
            "emu_a15_oss_v1": "Android 15 | 0 rows (no live reading_list record in the Sync Data folders)",
            "emu_a15_oss_v10": "Android 15 | 0 rows (no live reading_list record in the Sync Data folders)",
            "emu_a15_oss_v11": "Android 15 | 0 rows (no live reading_list record in the Sync Data folders)",
            "emu_a15_oss_v12": "Android 15 | 0 rows (no live reading_list record in the Sync Data folders)",
            "emu_a15_oss_v13": "Android 15 | 0 rows (no live reading_list record in the Sync Data folders)",
            "emu_a15_oss_v14": "Android 15 | 0 rows (no live reading_list record in the Sync Data folders)",
            "emu_a15_oss_v15": "Android 15 | 0 rows (no live reading_list record in the Sync Data folders)",
            "emu_a15_oss_v16": "Android 15 | 0 rows (no live reading_list record in the Sync Data folders)",
            "emu_a15_oss_v17": "Android 15 | 0 rows (no live reading_list record in the Sync Data folders)",
            "emu_a15_oss_v2": "Android 15 | 0 rows (no live reading_list record in the Sync Data folders)",
            "emu_a15_oss_v3": "Android 15 | 0 rows (no live reading_list record in the Sync Data folders)",
            "emu_a15_oss_v4": "Android 15 | 0 rows (no live reading_list record in the Sync Data folders)",
            "emu_a15_oss_v5": "Android 15 | 0 rows (no live reading_list record in the Sync Data folders)",
            "emu_a15_oss_v6": "Android 15 | 0 rows (no live reading_list record in the Sync Data folders)",
            "emu_a15_oss_v7": "Android 15 | 0 rows (no live reading_list record in the Sync Data folders)",
            "emu_a15_oss_v8": "Android 15 | 0 rows (no live reading_list record in the Sync Data folders)",
            "emu_a15_oss_v9": "Android 15 | 0 rows (no live reading_list record in the Sync Data folders)",
            "galaxys10_a10": "Android 10 | 0 rows (no live reading_list record in the Sync Data folders)",
            "hc_pixel8pro_a16": "Android 16 | 0 rows (no live reading_list record in the Sync Data folders)",
            "hc_pixel8pro_a17": "Android 17 | 0 rows (no live reading_list record in the Sync Data folders)",
            "hc_pixel8pro_a17_ail": "Android 17 | 0 rows (no Sync Data folder matched)",
            "hickman_a13": "Android 13 | 0 rows (no live reading_list record in the Sync Data folders)",
            "kevin_pocox7_a15": "Android 15 | 0 rows (no live reading_list record in the Sync Data folders)",
            "pixel3_a11": "Android 11 | 0 rows (no live reading_list record in the Sync Data folders)",
            "pixel3_a12": "Android 12 | 0 rows (no live reading_list record in the Sync Data folders)",
            "pixel7a_a14": "Android 14 | 0 rows (no live reading_list record in the Sync Data folders)",
            "russell_a14": "Android 14 | 0 rows (no live reading_list record in the Sync Data folders)",
            "russell_pixel6a_a13": "Android 13 | 0 rows (no live reading_list record in the Sync Data folders)",
            "s20fe_a13": "Android 13 | 0 rows (no live reading_list record in the Sync Data folders)",
            "samsunga53_a14": "Android 14 | 0 rows (no live reading_list record in the Sync Data folders)",
            "samsungs20_a13": "Android 13 | 0 rows (no live reading_list record in the Sync Data folders)",
            "sharon_a13": "Android 13 | 0 rows (no live reading_list record in the Sync Data folders)",
            "sharon_a14": "Android 14 | 0 rows (no live reading_list record in the Sync Data folders)",
            "userb2_a13": "Android 13 | 0 rows (no live reading_list record in the Sync Data folders)",
        },
    },
}

import datetime

from scripts.artifacts.chromeSyncSessions import _browser, _decoded, _stores
from scripts.artifacts.storagePathViews import android_user
from scripts.ilapfuncs import artifact_processor

# reading_list.proto, ReadingListLocal.ReadingListEntryStatus
_STATUS = {0: 'UNREAD', 1: 'READ', 2: 'UNSEEN'}


def _unix_us(value):
    """Microseconds since 1970-01-01 UTC as a datetime; '' for missing, zero or out of range."""
    try:
        microseconds = int(value)
    except (TypeError, ValueError):
        return ''
    if microseconds <= 0:
        return ''
    try:
        return datetime.datetime.fromtimestamp(microseconds / 1_000_000, tz=datetime.timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _status(value):
    if value is None:
        return ''
    return f'{_STATUS.get(value, "unknown")} ({value})'


@artifact_processor
def chromeReadingList(context):
    label = 'Chrome Reading List'
    data_list = []
    sources = []
    for folder, relative, sync in _stores(context, label):
        browser = _browser(relative)
        parts = relative.split('/')
        profile = parts[parts.index('app_chrome') + 1] if 'app_chrome' in parts else ''
        user = android_user(relative)
        rows = 0
        for _key, entry in _decoded(sync, 'reading_list', 'ReadingListLocal', label, relative):
            data_list.append((
                _unix_us(entry.get('creation_time_us')),
                _unix_us(entry.get('first_read_time_us')),
                _unix_us(entry.get('update_time_us')),
                entry.get('title', ''),
                entry.get('url', ''),
                _status(entry.get('status')),
                user,
                browser,
                profile,
            ))
            rows += 1
        if rows:
            sources.append(folder)
    data_headers = (('Added', 'datetime'), ('First Read', 'datetime'), ('Updated', 'datetime'),
                    'Title', 'URL', 'Status', 'Android User', 'Browser', 'Profile')
    return data_headers, data_list, '\n'.join(sources)
