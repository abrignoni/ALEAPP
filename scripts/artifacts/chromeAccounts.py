__artifacts_v2__ = {
    "chromeAccounts": {
        "name": "Chrome Accounts",
        "description": "Accounts listed in the account_info preference of Chromium-based "
                       "browser profiles, with which one is recorded as the profile's primary "
                       "account, the sync consent and last sync time recorded for it, and its "
                       "stored avatar image.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Browsers",
        "notes": ('Reads Preferences in app_chrome/<profile> of Chromium-based browsers, read only when the'
                  ' directory directly above app_chrome is shaped like a package name; Browser is that '
                  'package and Profile the profile folder. The storage views one Android extraction can '
                  'hold for an app data directory (data/data, data/user/0, data_mirror) are collapsed so a '
                  "profile is read once; a second Android user's profile is read as its own, as on "
                  'russell_a14, russell_pixel6a_a13 and samsungs20_a13. One row per entry of the '
                  'account_info list, which AccountTrackerService registers and saves to that preference '
                  '(https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/signin/internal/identity_manager/account_tracker_service.cc#L146'
                  ' and '
                  'https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/signin/internal/identity_manager/account_tracker_service.cc#L810-L820);'
                  ' Email, GAIA ID, Hosted Domain, Full Name, Given Name and Locale are its email, gaia, '
                  'hd, full_name, given_name and locale keys '
                  '(https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/signin/internal/identity_manager/account_info_util.cc#L58-L71),'
                  ' as stored. On the 2 tested Microsoft Edge rows the gaia key held a 16-character value '
                  'that is not all digits; what Edge stores there is not established. Hosted Domain held '
                  'the literal NO_HOSTED_DOMAIN on 19 of the 24 tested rows and in the emulator known data.'
                  " The entry's account_id key equalled gaia on all 24 tested rows and is not shown. On 4 "
                  'of the 24 tested rows Full Name, Given Name, Hosted Domain and Locale held empty '
                  'strings, 2 of them Microsoft Edge entries, which keep names under their own '
                  'edge_account_ keys; those keys are not read. An entry lists an account the browser knew;'
                  ' it does not by itself show the profile was signed in to it: on the emulator known data '
                  'emu_a15_chrome_signedout_known_20261116, made after Sign out and turn off sync in '
                  "Chrome's settings with Also clear your Chrome data left unchecked and the account still "
                  'on the device, the entry and its avatar remained. Primary Account is Yes when the '
                  "entry's account_id equals google.services.account_id, the preference "
                  'PrimaryAccountManager loads the primary account from, an empty value leaving none '
                  '(https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/signin/internal/identity_manager/primary_account_manager.cc#L271-L280),'
                  ' No when that preference is set to another value or empty, and blank when the file has '
                  'no such preference; it was Yes on 17, No on 1 and blank on 6 of the tested rows. In the '
                  'signed-out known data the preference was an empty string, so the row reads No. Sync '
                  'Consent is google.services.consented_to_sync '
                  '(https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/signin/public/base/signin_pref_names.cc#L83-L85)'
                  ' and Sync Setup Completed is sync.has_setup_completed, whether sync setup was finished '
                  'at least once '
                  '(https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/base/pref_names.h#L33-L37),'
                  ' both shown only on the Primary Account row; Sync Consent was Yes on 9 and No on 4 '
                  'tested rows and Sync Setup Completed Yes on 9, blank otherwise. Last Syncing Account is '
                  "Yes when the entry's gaia equals google.services.last_gaia_id, which the source says is "
                  'not cleared on sign-out '
                  '(https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/signin/public/base/signin_pref_names.cc#L87-L91),'
                  ' and blank when the file has none; it was Yes on 6 tested rows and blank on 18, and the '
                  'signed-out known data kept it. When last_gaia_id names no account_info entry, a row is '
                  'still given from it and google.services.last_username alone; no tested file had that '
                  'case, so that branch is unexercised. Last Synced is sync.last_synced_time, written with '
                  'base::TimeToValue '
                  '(https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/sync/service/glue/sync_transport_data_prefs.cc#L82-L87),'
                  ' microseconds since 1601-01-01 UTC '
                  '(https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/base/json/values_util.cc#L60-L62),'
                  ' read from the sync.transport_data_per_account entry whose key is the base64 SHA-256 of '
                  "the row's gaia "
                  '(https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/signin/public/base/gaia_id_hash.cc#L18-L21'
                  ' and '
                  'https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/signin/public/base/gaia_id_hash.cc#L53-L55),'
                  ' as on 10 tested profiles, or from the top-level sync.last_synced_time when sync.gaia_id'
                  " equals the row's gaia, as Chrome 124.0.6367.219 wrote it in the emulator known data, "
                  'where it decoded to a time inside the capture window, and as 9 tested profiles held it; '
                  'it held a value on 19 tested rows, and was cleared in the signed-out known data. Avatar '
                  "is the file named by the entry's account_id in the profile's Accounts/Avatar Images "
                  'folder '
                  '(https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/signin/internal/identity_manager/account_tracker_service.cc#L50-L54'
                  ' and '
                  'https://github.com/chromium/chromium/blob/5926523bcfedb77ba2533ace1dd93b477673f72a/components/signin/internal/identity_manager/account_tracker_service.cc#L559-L564),'
                  ' present on 20 tested rows. Profile held Default on every tested row. Not read: Local '
                  "State's profile.info_cache, whose Gaia ID and Gaia names were emptied on sign-out in the"
                  ' known data; google.services.last_username except in the branch above and '
                  'google.services.last_signed_in_username; and the entry keys picture_url, '
                  'accountcapabilities, is_supervised_child, is_child_account, '
                  'is_under_advanced_protection, last_downloaded_image_url_with_size and access_point. Run '
                  'on 18 corpus images (24 rows). Compared with known data on three emulator captures from '
                  'one Android 15 emulator with Chrome 124.0.6367.219 and a test Google account: signed in '
                  'with sync on, after a reading list entry was opened, and after sign-out with Also clear '
                  'your Chrome data unchecked.'),
        "paths": ('*/app_chrome/*/Preferences', '*/app_chrome/*/Accounts/Avatar Images/*'),
        "output_types": "standard",
        "artifact_icon": "user-check",
        "sample_data": {
            "anne_a15": "Android 15 | 1 row",
            "cookbook_a11": "Android 11 | 1 row",
            "df020_mavic_pro_android": "0 rows (no Chromium Preferences file matched)",
            "dfrws2011_case1_a855": "0 rows (no Chromium Preferences file matched)",
            "dfrws2011_case2_droid_a201": "Android 2.0.1 | 0 rows (no Chromium Preferences file matched)",
            "emu_a15_chrome_read_known_20261116": "Android 15 | 1 row",
            "emu_a15_chrome_signedin_known_20261116": "Android 15 | 1 row",
            "emu_a15_chrome_signedout_known_20261116": "Android 15 | 1 row",
            "emu_a15_kd_fsapi_k1_embedded_written": "Android 15 | 0 rows (no Chromium Preferences file matched)",
            "emu_a15_kd_fsapi_k2_embedded_history_cleared": "Android 15 | 0 rows (no Chromium Preferences file matched)",
            "emu_a15_kd_fsapi_k3_embedded_sitedata_cleared": "Android 15 | 0 rows (no Chromium Preferences file matched)",
            "emu_a15_kd_fsapi_s1_written": "Android 15 | 0 rows (no Chromium Preferences file matched)",
            "emu_a15_kd_fsapi_s2_history_cleared": "Android 15 | 0 rows (no Chromium Preferences file matched)",
            "emu_a15_kd_fsapi_s3_sitedata_cleared": "Android 15 | 0 rows (no Chromium Preferences file matched)",
            "emu_a15_kd_usage_u1_visit_share": "Android 15 | 0 rows (no Chromium Preferences file matched)",
            "emu_a15_kd_usage_u2_expired": "Android 15 | 0 rows (no Chromium Preferences file matched)",
            "emu_a15_kd_usage_u3_history_cleared": "Android 15 | 0 rows (no Chromium Preferences file matched)",
            "emu_a15_kd_usage_u4_history_cleared_all": "Android 15 | 0 rows (no Chromium Preferences file matched)",
            "emu_a15_kdl_v1": "Android 15 | 0 rows (no Chromium Preferences file matched)",
            "emu_a15_oss2_v1": "Android 15 | 0 rows (no Chromium Preferences file matched)",
            "emu_a15_oss2_v2": "Android 15 | 0 rows (no account in account_info or google.services)",
            "emu_a15_oss2_v3": "Android 15 | 0 rows (no account in account_info or google.services)",
            "emu_a15_oss_v1": "Android 15 | 0 rows (no account in account_info or google.services)",
            "emu_a15_oss_v10": "Android 15 | 0 rows (no account in account_info or google.services)",
            "emu_a15_oss_v11": "Android 15 | 0 rows (no account in account_info or google.services)",
            "emu_a15_oss_v12": "Android 15 | 0 rows (no account in account_info or google.services)",
            "emu_a15_oss_v13": "Android 15 | 0 rows (no account in account_info or google.services)",
            "emu_a15_oss_v14": "Android 15 | 0 rows (no account in account_info or google.services)",
            "emu_a15_oss_v15": "Android 15 | 0 rows (no account in account_info or google.services)",
            "emu_a15_oss_v16": "Android 15 | 0 rows (no account in account_info or google.services)",
            "emu_a15_oss_v17": "Android 15 | 0 rows (no account in account_info or google.services)",
            "emu_a15_oss_v2": "Android 15 | 0 rows (no account in account_info or google.services)",
            "emu_a15_oss_v3": "Android 15 | 0 rows (no account in account_info or google.services)",
            "emu_a15_oss_v4": "Android 15 | 0 rows (no account in account_info or google.services)",
            "emu_a15_oss_v5": "Android 15 | 0 rows (no account in account_info or google.services)",
            "emu_a15_oss_v6": "Android 15 | 0 rows (no account in account_info or google.services)",
            "emu_a15_oss_v7": "Android 15 | 0 rows (no account in account_info or google.services)",
            "emu_a15_oss_v8": "Android 15 | 0 rows (no account in account_info or google.services)",
            "emu_a15_oss_v9": "Android 15 | 0 rows (no account in account_info or google.services)",
            "galaxys10_a10": "Android 10 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | 1 row",
            "hc_pixel8pro_a17": "Android 17 | 1 row",
            "hc_pixel8pro_a17_ail": "Android 17 | 0 rows (no Chromium Preferences file matched)",
            "hickman_a13": "Android 13 | 1 row",
            "kevin_pocox7_a15": "Android 15 | 1 row",
            "pixel3_a11": "Android 11 | 1 row",
            "pixel3_a12": "Android 12 | 1 row",
            "pixel7a_a14": "Android 14 | 2 rows",
            "russell_a14": "Android 14 | 2 rows",
            "russell_pixel6a_a13": "Android 13 | 2 rows",
            "s20fe_a13": "Android 13 | 1 row",
            "samsunga53_a14": "Android 14 | 2 rows",
            "samsungs20_a13": "Android 13 | 3 rows",
            "sharon_a13": "Android 13 | 1 row",
            "sharon_a14": "Android 14 | 1 row",
            "userb2_a13": "Android 13 | 1 row",
        },
    },
}

import base64
import hashlib
import json
import os
import re

from scripts.artifacts.storagePathViews import android_user, canonical_path
from scripts.chromium_sync_data import webkit_time
from scripts.ilapfuncs import artifact_processor, check_in_media, logfunc

# A profile's Preferences sits in app_chrome/<profile>, and the app package directory
# directly above app_chrome is the only part of the path that names the browser, as in
# chromeSyncSessions.
_PREFS = re.compile(r'(?:^|/)([A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)+)/app_chrome/([^/]+)/'
                    r'Preferences$')
_AVATAR = re.compile(r'(?:^|/)([A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)+)/app_chrome/([^/]+)/'
                     r'Accounts/Avatar Images/([^/]+)$')


def _profile_key(relative, package, profile):
    """The storage-view independent key of one profile folder."""
    head = relative[:relative.rindex(f'{package}/app_chrome/{profile}/')]
    return canonical_path(f'{head}{package}/app_chrome/{profile}/')[0]


def _gaia_hash(gaia):
    """base64 of the SHA-256 of a Gaia ID, the key of sync.transport_data_per_account."""
    return base64.b64encode(hashlib.sha256(gaia.encode('utf-8')).digest()).decode('ascii')


def _yes_no(value):
    if value is None:
        return ''
    return 'Yes' if value else 'No'


def _last_synced(sync, gaia):
    """sync.last_synced_time recorded for this Gaia ID, or ''."""
    per_account = sync.get('transport_data_per_account')
    if isinstance(per_account, dict) and gaia:
        entry = per_account.get(_gaia_hash(gaia))
        if isinstance(entry, dict) and 'sync.last_synced_time' in entry:
            return webkit_time(entry.get('sync.last_synced_time'))
    if gaia and sync.get('gaia_id') == gaia:
        return webkit_time(sync.get('last_synced_time'))
    return ''


@artifact_processor
def chromeAccounts(context):
    profiles = {}
    avatars = {}
    for found in context.get_files_found():
        path = str(found)
        if not os.path.isfile(path):
            continue
        relative = str(context.get_relative_path(path)).replace('\\', '/')
        match = _PREFS.search(relative)
        if match:
            package, profile = match.group(1), match.group(2)
            key, rank = canonical_path(relative)
            held = profiles.get(key)
            if held is None or rank < held[0]:
                profiles[key] = (rank, path, relative, package, profile)
            continue
        match = _AVATAR.search(relative)
        if match:
            package, profile, account_id = match.groups()
            key = (_profile_key(relative, package, profile), account_id)
            rank = canonical_path(relative)[1]
            held = avatars.get(key)
            if held is None or rank < held[0]:
                avatars[key] = (rank, path)

    data_list = []
    sources = []
    for _rank, path, relative, package, profile in sorted(profiles.values(),
                                                          key=lambda item: item[2]):
        try:
            with open(path, 'rb') as handle:
                prefs = json.loads(handle.read().decode('utf-8'))
        except (OSError, UnicodeDecodeError, ValueError) as ex:
            logfunc(f'Chrome Accounts: could not read {relative}: {ex}')
            continue
        if not isinstance(prefs, dict):
            continue
        accounts = [a for a in (prefs.get('account_info') or []) if isinstance(a, dict)]
        services = (prefs.get('google') or {}).get('services') or {}
        sync = prefs.get('sync') or {}
        if not isinstance(services, dict):
            services = {}
        if not isinstance(sync, dict):
            sync = {}
        primary = services.get('account_id')
        last_gaia = services.get('last_gaia_id')
        last_username = services.get('last_username')
        profile_key = _profile_key(relative, package, profile)
        user = android_user(relative)
        rows = 0
        listed = set()
        for account in accounts:
            account_id = account.get('account_id', '')
            gaia = account.get('gaia', '')
            listed.add(gaia)
            is_primary = None if primary is None else bool(primary) and primary == account_id
            avatar = ''
            held = avatars.get((profile_key, account_id))
            if held:
                avatar = check_in_media(held[1], f'{account_id}.png')
            data_list.append((
                _last_synced(sync, gaia),
                account.get('email', ''),
                account.get('full_name', ''),
                account.get('given_name', ''),
                gaia,
                _yes_no(is_primary),
                _yes_no(services.get('consented_to_sync')) if is_primary else '',
                _yes_no(sync.get('has_setup_completed')) if is_primary else '',
                '' if last_gaia is None else _yes_no(bool(gaia) and last_gaia == gaia),
                account.get('hd', ''),
                account.get('locale', ''),
                avatar,
                user,
                package,
                profile,
            ))
            rows += 1
        if last_gaia and last_gaia not in listed:
            # The last syncing account is kept after sign-out; when the account list no
            # longer holds it, it is still reported, from those two preferences alone.
            data_list.append((
                _last_synced(sync, last_gaia), last_username or '', '', '', last_gaia,
                _yes_no(bool(primary) and primary == last_gaia) if primary is not None else '',
                '', '', 'Yes', '', '', '', user, package, profile,
            ))
            rows += 1
        if rows:
            sources.append(path)
    data_headers = (('Last Synced', 'datetime'), 'Email', 'Full Name', 'Given Name', 'GAIA ID',
                    'Primary Account', 'Sync Consent', 'Sync Setup Completed',
                    'Last Syncing Account', 'Hosted Domain', 'Locale', ('Avatar', 'media'),
                    'Android User', 'Browser', 'Profile')
    return data_headers, data_list, '\n'.join(sources)
