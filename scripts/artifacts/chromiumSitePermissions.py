__artifacts_v2__ = {
    "chromiumSitePermissions": {
        "name": "Chromium Site Permissions",
        "description": "The per-site permission settings (location, camera, microphone and others) stored in a Chromium "
                       "profile's Preferences on Android, with when each was last changed, where the browser stored that time.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-01",
        "last_update_date": "2026-11-01",
        "requirements": "none",
        "category": "Chromium",
        "notes": "Reads the Preferences file of a Chromium profile on Android (any <package>/app_*/Default/Preferences: Chrome, Brave, Edge, Samsung Internet and app WebViews). Format and meanings come from Chromium at commit 77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784. Times are stored as microseconds since 1601-01-01 UTC, written as a string (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/base/json/values_util.cc#L22-L23, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/base/json/values_util.cc#L45, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/base/json/values_util.cc#L60-L61), and are shown in UTC. Browser is Chrome, Brave, Edge or Opera for those browsers' packages and the package name for any other Chromium build; for an app WebView it is the app that holds it. Android User is the Android user whose app data directory holds the file, read from its path; the storage views one extraction can hold for an app data directory (data/data, data/user/0, data_mirror) are read once, and a second Android user's file is read as its own. The files read are listed in the report's source paths. A file that does not parse as JSON is skipped and named in the run log. Each row is one per-site exception in profile.content_settings.exceptions for these permission types: geolocation, notifications, media_stream_camera, media_stream_mic, automatic_downloads, clipboard, vr and ar. Other exception types (site engagement, client hints, cookie and tracker data and the like) are not reported here; of those with an allow or block value, the tested images held only Samsung Internet's anti_tracking list and a 3pcd_support entry. Each exception is keyed by its site pattern pair; Site is the first pattern and Embedding Site the second as stored, * meaning any. Setting (as stored) is the number and Setting its name: 0 Default, 1 Allow, 2 Block, 3 Ask, 4 Session only (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/components/content_settings/core/common/content_settings.h#L26-L33). Last Modified, Expiration and Last Visit are the exception's last_modified, expiration and last_visit values (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/components/content_settings/core/browser/content_settings_pref.cc#L45-L51, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/components/content_settings/core/browser/content_settings_pref.cc#L536-L560); Expiration is blank when stored as 0. When a setting is reset the browser removes the entry's keys (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/components/content_settings/core/browser/content_settings_pref.cc#L526-L535) and then the entry itself if nothing is left in it (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/components/content_settings/core/browser/content_settings_pref.cc#L575-L578). A row records the stored setting and when it was last changed, not who changed it: on the tested images 14 of the 17 geolocation rows were for a Google search host, and whether any of those was set by a person or by the browser for its search engine was not established. Known data (Chrome 124.0.6367.219 on an Android 15 emulator, no Google account, a local test page at http://localhost:8765): a fresh profile held no permission entries. Allowing location wrote a geolocation row with Setting Allow and a GRANTED prompt action shown as MODAL_DIALOG; blocking the camera wrote a media_stream_camera row with Setting Block and a DENIED action; dismissing the microphone prompt with the back key wrote a DISMISSED action and a prompt count row with a dismiss count of 1, and no media_stream_mic row; allowing notifications wrote a GRANTED action and no notifications row, because Chrome on Android keeps a site's notification permission as an Android notification channel (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/chrome/browser/notifications/notification_channels_provider_android.h#L52-L54), with a channel id that starts with web: (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/chrome/browser/notifications/android/java/src/org/chromium/chrome/browser/notifications/channels/SiteChannelsManager.java#L36), not in this file. Clearing browsing data for the last hour with Chrome's default boxes (browsing history, cookies and site data, cached files; Site settings left unticked) emptied every prompt action list and removed the prompt count row, and left the location and camera rows. Other Chrome versions were not tested this way. On the tested images: 26 rows on 10 of 20 images: geolocation 17 (14 for a Google search host), media_stream_camera 4, media_stream_mic 4 and automatic_downloads 1 (for a Google search host). Setting held Allow on every row, so Setting (as stored) held 1. Expiration was empty on every row (absent on 21, stored as 0 on 5) and Last Visit was empty on every row but 2. Last Modified was blank on 4 rows: 2 stored no last_modified and 2 stored it as 0. Embedding Site held * on every row but 2, both on pixel3_a11, where Site and Embedding Site held the same site on both rows. Browser: Chrome 15, Brave 5, Samsung Internet 4 (shown by its package name) and Edge 2; Browser held one value on every row of 2 images (galaxys10_a10 and samsunga53_a14). Android User held 0 on every row of 8 of the 10 images; russell_a14 and russell_pixel6a_a13 also had user 10.",
        "paths": ('*/app_*/Default/Preferences',),
        "output_types": "standard",
        "artifact_icon": "shield",
        "sample_data": {
            "anne_a15": "Android 15 | 2 rows",
            "cookbook_a11": "Android 11 | 2 rows",
            "emu_a15_oss2_v3": "Android 15 | 0 rows",
            "emu_a15_oss_v17": "Android 15 | 0 rows",
            "galaxys10_a10": "Android 10 | 1 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "hickman_a13": "Android 13 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "pixel3_a11": "Android 11 | 2 rows",
            "pixel3_a12": "Android 12 | 2 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "russell_a14": "Android 14 | 3 rows",
            "russell_pixel6a_a13": "Android 13 | 3 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 1 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 4 rows",
            "sharon_a14": "Android 14 | 6 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
    },
    "chromiumPermissionActions": {
        "name": "Chromium Permission Prompt Actions",
        "description": "How a Chromium browser on Android recorded permission prompts being answered (granted, denied, "
                       "dismissed or ignored), by permission and time, from the profile's Preferences.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-01",
        "last_update_date": "2026-11-01",
        "requirements": "none",
        "category": "Chromium",
        "notes": "Reads the Preferences file of a Chromium profile on Android (any <package>/app_*/Default/Preferences: Chrome, Brave, Edge, Samsung Internet and app WebViews). Format and meanings come from Chromium at commit 77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784. Times are stored as microseconds since 1601-01-01 UTC, written as a string (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/base/json/values_util.cc#L22-L23, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/base/json/values_util.cc#L45, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/base/json/values_util.cc#L60-L61), and are shown in UTC. Browser is Chrome, Brave, Edge or Opera for those browsers' packages and the package name for any other Chromium build; for an app WebView it is the app that holds it. Android User is the Android user whose app data directory holds the file, read from its path; the storage views one extraction can hold for an app data directory (data/data, data/user/0, data_mirror) are read once, and a second Android user's file is read as its own. The files read are listed in the report's source paths. A file that does not parse as JSON is skipped and named in the run log. Each row is one entry of profile.content_settings.permission_actions, the browser's record of how permission prompts were answered (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/components/permissions/permission_actions_history.cc#L30-L45). An entry holds no site: it records the permission, the action, how the prompt was shown and the time (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/components/permissions/permission_actions_history.cc#L149-L178). Permission is the list's key as stored, for example geolocation, camera_stream, mic_stream or notifications (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/components/permissions/request_type.cc#L533, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/components/permissions/request_type.cc#L545, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/components/permissions/request_type.cc#L561, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/components/permissions/request_type.cc#L571). Action is the PermissionAction name for Action (as stored): 0 GRANTED, 1 DENIED, 2 DISMISSED, 3 IGNORED, 4 REVOKED, 5 GRANTED_ONCE (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/components/permissions/permission_uma_constants.h#L13-L19). Prompt Shown As is the PermissionPromptDisposition name for Prompt Disposition (as stored) (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/components/permissions/permission_uma_constants.h#L214-L277); entries written before Chrome 96 have none (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/components/permissions/permission_actions_history.cc#L43-L45). The browser drops entries older than 90 days each time it records one (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/components/permissions/permission_actions_history.cc#L59, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/components/permissions/permission_actions_history.cc#L162-L168) and has a call that removes the entries in a time range (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/components/permissions/permission_actions_history.cc#L181-L200); which browsing data choices reach it was not traced. Known data (Chrome 124.0.6367.219 on an Android 15 emulator, no Google account, a local test page at http://localhost:8765): a fresh profile held no permission entries. Allowing location wrote a geolocation row with Setting Allow and a GRANTED prompt action shown as MODAL_DIALOG; blocking the camera wrote a media_stream_camera row with Setting Block and a DENIED action; dismissing the microphone prompt with the back key wrote a DISMISSED action and a prompt count row with a dismiss count of 1, and no media_stream_mic row; allowing notifications wrote a GRANTED action and no notifications row, because Chrome on Android keeps a site's notification permission as an Android notification channel (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/chrome/browser/notifications/notification_channels_provider_android.h#L52-L54), with a channel id that starts with web: (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/chrome/browser/notifications/android/java/src/org/chromium/chrome/browser/notifications/channels/SiteChannelsManager.java#L36), not in this file. Clearing browsing data for the last hour with Chrome's default boxes (browsing history, cookies and site data, cached files; Site settings left unticked) emptied every prompt action list and removed the prompt count row, and left the location and camera rows. Other Chrome versions were not tested this way. On the tested images: 32 rows on 11 of 20 images: notifications 15, geolocation 9, camera_stream 4 and mic_stream 4; GRANTED 25, IGNORED 3, DENIED 2 and DISMISSED 2. Prompt Shown As held MODAL_DIALOG on 25 rows, MESSAGE_UI on 3 and NONE_VISIBLE on 1, and was empty on 3 rows (galaxys10_a10 and pixel3_a12) whose entries had no prompt_disposition, where Prompt Disposition (as stored) was empty too. Permission held one value on every row of 6 of the 11 images. Browser: Chrome 28 and Brave 4; Browser held Chrome on every row of 9 of the 11 images. Android User held 0 on every row of 9 of the 11 images; russell_a14 and russell_pixel6a_a13 also had user 10.",
        "paths": ('*/app_*/Default/Preferences',),
        "output_types": "standard",
        "artifact_icon": "check-square",
        "sample_data": {
            "anne_a15": "Android 15 | 5 rows",
            "cookbook_a11": "Android 11 | 1 rows",
            "emu_a15_oss2_v3": "Android 15 | 0 rows",
            "emu_a15_oss_v17": "Android 15 | 0 rows",
            "galaxys10_a10": "Android 10 | 2 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "hickman_a13": "Android 13 | 2 rows",
            "kevin_pocox7_a15": "Android 15 | 5 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 1 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "russell_a14": "Android 14 | 3 rows",
            "russell_pixel6a_a13": "Android 13 | 3 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 1 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 4 rows",
            "sharon_a14": "Android 14 | 5 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
    },
    "chromiumPermissionPromptCounts": {
        "name": "Chromium Permission Prompt Counts",
        "description": "Per site and permission, how many times a Chromium browser on Android counted its permission prompt "
                       "as dismissed or ignored, from the profile's Preferences.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-01",
        "last_update_date": "2026-11-01",
        "requirements": "none",
        "category": "Chromium",
        "notes": "Reads the Preferences file of a Chromium profile on Android (any <package>/app_*/Default/Preferences: Chrome, Brave, Edge, Samsung Internet and app WebViews). Format and meanings come from Chromium at commit 77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784. Times are stored as microseconds since 1601-01-01 UTC, written as a string (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/base/json/values_util.cc#L22-L23, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/base/json/values_util.cc#L45, https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/base/json/values_util.cc#L60-L61), and are shown in UTC. Browser is Chrome, Brave, Edge or Opera for those browsers' packages and the package name for any other Chromium build; for an app WebView it is the app that holds it. Android User is the Android user whose app data directory holds the file, read from its path; the storage views one extraction can hold for an app data directory (data/data, data/user/0, data_mirror) are read once, and a second Android user's file is read as its own. The files read are listed in the report's source paths. A file that does not parse as JSON is skipped and named in the run log. Each row is one permission of one site in the permission_autoblocking_data exception (registered at https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/components/content_settings/core/browser/website_settings_registry.cc#L164-L165 and stored with underscores), whose keys record how often a site's permission prompt was dismissed or ignored (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/components/permissions/permission_decision_auto_blocker.cc#L217-L234). Site is the first pattern of the exception. Permission (as stored) is the stored key, for example Notifications, AudioCapture or FederatedIdentityApi. Dismiss Count and Ignore Count are the dismiss_count and ignore_count values; Other Values (as stored) holds the entry's remaining keys, such as ignore_count_quiet_ui and dismissal_embargo_days. Last Modified is the exception's last_modified value and is shared by every permission of that site. Known data (Chrome 124.0.6367.219 on an Android 15 emulator, no Google account, a local test page at http://localhost:8765): a fresh profile held no permission entries. Allowing location wrote a geolocation row with Setting Allow and a GRANTED prompt action shown as MODAL_DIALOG; blocking the camera wrote a media_stream_camera row with Setting Block and a DENIED action; dismissing the microphone prompt with the back key wrote a DISMISSED action and a prompt count row with a dismiss count of 1, and no media_stream_mic row; allowing notifications wrote a GRANTED action and no notifications row, because Chrome on Android keeps a site's notification permission as an Android notification channel (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/chrome/browser/notifications/notification_channels_provider_android.h#L52-L54), with a channel id that starts with web: (https://github.com/chromium/chromium/blob/77a2fd4e2e4c2937b5fc24e5f5e88f9e2f999784/chrome/browser/notifications/android/java/src/org/chromium/chrome/browser/notifications/channels/SiteChannelsManager.java#L36), not in this file. Clearing browsing data for the last hour with Chrome's default boxes (browsing history, cookies and site data, cached files; Site settings left unticked) emptied every prompt action list and removed the prompt count row, and left the location and camera rows. Other Chrome versions were not tested this way. On the tested images: 13 rows on 4 of 20 images: Notifications 8 and FederatedIdentityApi 5. Dismiss Count was set on 8 rows and Ignore Count on 5; Ignore Count was empty on every row of 3 of the 4 images. Other Values (as stored) was set on 9 rows and empty on 4 (3 on kevin_pocox7_a15 and the one row of anne_a15). Browser held Chrome and Android User held 0 on every row.",
        "paths": ('*/app_*/Default/Preferences',),
        "output_types": "standard",
        "artifact_icon": "x-square",
        "sample_data": {
            "anne_a15": "Android 15 | 1 rows",
            "cookbook_a11": "Android 11 | 1 rows",
            "emu_a15_oss2_v3": "Android 15 | 0 rows",
            "emu_a15_oss_v17": "Android 15 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "hickman_a13": "Android 13 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 10 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 0 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "russell_a14": "Android 14 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 1 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
    },
}

import datetime
import json

from scripts.artifacts.chrome import get_browser_name
from scripts.artifacts.storagePathViews import android_user, unique_files
from scripts.ilapfuncs import artifact_processor, logfunc

# Permission exception types reported by Chromium Site Permissions (see the notes).
_PERMISSION_TYPES = ('geolocation', 'notifications', 'media_stream_camera', 'media_stream_mic', 'automatic_downloads',
                     'clipboard', 'vr', 'ar')
_SETTINGS = {0: 'Default', 1: 'Allow', 2: 'Block', 3: 'Ask', 4: 'Session only'}
_ACTIONS = {0: 'GRANTED', 1: 'DENIED', 2: 'DISMISSED', 3: 'IGNORED', 4: 'REVOKED', 5: 'GRANTED_ONCE'}
_DISPOSITIONS = {
    0: 'NOT_APPLICABLE', 1: 'ANCHORED_BUBBLE', 2: 'LOCATION_BAR_RIGHT_STATIC_ICON', 3: 'LOCATION_BAR_RIGHT_ANIMATED_ICON',
    4: 'MODAL_DIALOG', 5: 'MINI_INFOBAR', 6: 'LOCATION_BAR_LEFT_CHIP', 7: 'NONE_VISIBLE', 8: 'CUSTOM_MODAL_DIALOG',
    9: 'LOCATION_BAR_LEFT_QUIET_CHIP', 10: 'MESSAGE_UI', 11: 'LOCATION_BAR_LEFT_QUIET_ABUSIVE_CHIP',
    12: 'LOCATION_BAR_LEFT_CHIP_AUTO_BUBBLE', 13: 'ELEMENT_ANCHORED_BUBBLE', 15: 'MESSAGE_UI_LOUD',
    16: 'LOCATION_BAR_LEFT_QUIET_ICON'}
_EPOCH_1601 = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)


def _time(value):
    """A Chromium time value (microseconds since 1601, as a string or a number) as a UTC datetime; '' for 0 or none."""
    try:
        micros = int(value)
    except (TypeError, ValueError):
        return ''
    return _EPOCH_1601 + datetime.timedelta(microseconds=micros) if micros > 0 else ''


def _profiles(context, label):
    """[(path, content_settings dict, Browser, Android User)] for each Preferences file, storage views collapsed."""
    profiles = []
    for path in unique_files(context):
        path = str(path)
        if path.replace('\\', '/').rsplit('/', 1)[-1] != 'Preferences':
            continue
        relative = context.get_relative_path(path)
        try:
            with open(path, 'rb') as handle:
                preferences = json.loads(handle.read().decode('utf-8', 'replace'))
        except (OSError, ValueError) as ex:
            logfunc(f'{label}: could not read {relative}: {type(ex).__name__}')
            continue
        profile = preferences.get('profile') if isinstance(preferences, dict) else None
        settings = profile.get('content_settings') if isinstance(profile, dict) else None
        profiles.append((path, settings if isinstance(settings, dict) else {}, get_browser_name(path),
                         android_user(relative)))
    return profiles


def _exceptions(settings, kind):
    exceptions = settings.get('exceptions')
    sites = exceptions.get(kind) if isinstance(exceptions, dict) else None
    return sites.items() if isinstance(sites, dict) else ()


def _patterns(key):
    primary, _, secondary = str(key).partition(',')
    return primary, secondary


@artifact_processor
def chromiumSitePermissions(context):
    data_headers = (('Last Modified', 'datetime'), ('Expiration', 'datetime'), ('Last Visit', 'datetime'), 'Site',
                    'Embedding Site', 'Permission', 'Setting', 'Setting (as stored)', 'Browser', 'Android User')
    data_list, sources = [], []
    for path, settings, browser, user in _profiles(context, 'Chromium Site Permissions'):
        sources.append(path)
        for kind in _PERMISSION_TYPES:
            for key, value in _exceptions(settings, kind):
                if not isinstance(value, dict):
                    continue
                site, embedding = _patterns(key)
                setting = value.get('setting')
                data_list.append((_time(value.get('last_modified')), _time(value.get('expiration')),
                                  _time(value.get('last_visit')), site, embedding, kind,
                                  _SETTINGS.get(setting, '') if isinstance(setting, int) else '',
                                  '' if setting is None else str(setting), browser, user))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def chromiumPermissionActions(context):
    data_headers = (('Time', 'datetime'), 'Permission', 'Action', 'Action (as stored)', 'Prompt Shown As',
                    'Prompt Disposition (as stored)', 'Browser', 'Android User')
    data_list, sources = [], []
    for path, settings, browser, user in _profiles(context, 'Chromium Permission Prompt Actions'):
        sources.append(path)
        actions = settings.get('permission_actions')
        for kind, entries in (actions.items() if isinstance(actions, dict) else ()):
            for entry in (entries if isinstance(entries, list) else ()):
                if not isinstance(entry, dict):
                    continue
                action, shown = entry.get('action'), entry.get('prompt_disposition')
                data_list.append((_time(entry.get('time')), kind,
                                  _ACTIONS.get(action, '') if isinstance(action, int) else '',
                                  '' if action is None else str(action),
                                  _DISPOSITIONS.get(shown, '') if isinstance(shown, int) else '',
                                  '' if shown is None else str(shown), browser, user))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def chromiumPermissionPromptCounts(context):
    data_headers = (('Last Modified', 'datetime'), 'Site', 'Permission (as stored)', 'Dismiss Count', 'Ignore Count',
                    'Other Values (as stored)', 'Browser', 'Android User')
    data_list, sources = [], []
    for path, settings, browser, user in _profiles(context, 'Chromium Permission Prompt Counts'):
        sources.append(path)
        for key, value in _exceptions(settings, 'permission_autoblocking_data'):
            counts = value.get('setting') if isinstance(value, dict) else None
            if not isinstance(counts, dict):
                continue
            site, _ = _patterns(key)
            for kind, entry in counts.items():
                if not isinstance(entry, dict):
                    continue
                other = ', '.join(f'{name}={entry[name]}' for name in entry if name not in ('dismiss_count', 'ignore_count'))
                data_list.append((_time(value.get('last_modified')), site, kind, entry.get('dismiss_count', ''),
                                  entry.get('ignore_count', ''), other, browser, user))
    return data_headers, data_list, '\n'.join(sources)
