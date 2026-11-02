__artifacts_v2__ = {
    "instagramPendingMedia": {
        "name": "Instagram - Pending Media",
        "description": "Photos and videos Instagram on Android kept in its pending media store for upload, with "
                       "upload status, share type, times and the source photo where it is still in the extraction.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-01",
        "last_update_date": "2026-11-01",
        "requirements": "none",
        "category": "Instagram",
        "notes": "Reads <account id>_pending_media.json from Instagram's files folder (com.instagram.android/files). Instagram is closed source; what is said here comes from its own code, decompiled with jadx from the APK on sharon_a14 (version 344.1.0.42.92). The file is written by com.instagram.pendingmedia.store.PendingMediaStoreSerializer and named after the user ID of the Instagram account the session belongs to, followed by _pending_media.json; each entry is one pending media object. Account ID (file name) is that user ID, taken from the file name. Created is the entry's time_created, which the app sets from the device clock in milliseconds when it builds the object, shown in UTC. Last User Interaction and Last Upload Attempt are lastUserInteractionTime and lastUploadAttemptTime as stored, read as milliseconds since 1970 (the unit comes from the values' length, not from the code), and are blank when missing, 0 or negative. Server Status (as stored) and Target Status (as stored) are serverStatus and targetStatus, names from the app's status list (UNINITIALIZED, DRAFT, NOT_UPLOADED, CREATED_MEDIA, UPLOADED_DECOR_IMAGE, UPLOADED_VIDEO, UPLOADED, CONFIGURING_MULTIPLE_TARGETS, CONFIGURED, CONFIGURED_CLOUD_DRAFT); the constructor that takes an upload id starts an object as NOT_UPLOADED, and the no-argument one starts it as UNINITIALIZED. What moves an entry from one status to another, and when the app removes entries from the file, was not traced, so a NOT_UPLOADED entry is not by itself evidence that a post was abandoned. Share Type (as stored) is share_type as stored; the code starts a new object as UNINITIALIZED, and UNKNOWN, which the tested files hold, is another stored value whose writer was not traced. Media Type is mediaType and Instagram Media ID is ig_media_id, as stored. Media shows the photo found in the extraction at the first of originalImageMediaPath, originalImageFilePath and imageFilePath that is present (in the tested files the first pointed to shared storage and the other two into the app's own data folder); Media Shown From names that field. Source Media Path is originalImageMediaPath, or originalImageFilePath when there is none. Video entries in the tested files held no file path, so no video is shown. The entry's other fields (edits, story and reel settings, upload counters) are not reported, and no tested entry had a caption or location set. Not tested on a device: no known-data case was made, because that needs an Instagram account. Android User is the Android user whose app data directory holds the file, read from its path; the storage views one extraction can hold for an app data directory (data/data, data/user/0, data_mirror) are read once, and the files read are listed in the report's source paths. On the tested images: 15 rows on 6 of 20 images (galaxys10_a10 1, hc_pixel8pro_a16 2, hc_pixel8pro_a17 2, pixel7a_a14 2, samsungs20_a13 4, sharon_a14 4); hc_pixel8pro_a16 and hc_pixel8pro_a17 hold the same account file with the same entries. Server Status (as stored) and Target Status (as stored) held the same value on every row: UPLOADED on the 4 rows of sharon_a14 and NOT_UPLOADED on the 11 others, so each held one value on every row of every image. Last User Interaction and Last Upload Attempt were empty on the 11 NOT_UPLOADED rows and set on the 4 UPLOADED rows, where Last Upload Attempt held one value on all 4. Instagram Media ID was set on the 4 UPLOADED rows and empty on the 11 NOT_UPLOADED rows, so it was empty on every row of the other five images. Media Type: photo 9, video 6; Media Type held photo on every row of sharon_a14. Share Type (as stored): UNKNOWN 9, FOLLOWERS_SHARE 4, REEL_SHARE_AND_DIRECT_STORY_SHARE 1, and empty on the one row of galaxys10_a10; Share Type (as stored) held FOLLOWERS_SHARE on every row of sharon_a14. Media showed the photo on 8 of the 9 photo rows, from originalImageMediaPath on all 8, so Media Shown From held originalImageMediaPath wherever it was set, including every row of sharon_a14; Media and Media Shown From were empty on the 6 video rows and on one photo row of pixel7a_a14, whose source file is not in that extraction. Source Media Path was empty on the 6 video rows. Account ID (file name) held one value on every row of each image except samsungs20_a13, which has two files. Android User held 0 on every row.",
        "paths": ('*/com.instagram.android/files/*_pending_media.json',),
        "output_types": "standard",
        "artifact_icon": "upload",
        "sample_data": {
            "anne_a15": "Android 15 | 0 rows",
            "cookbook_a11": "Android 11 | 0 rows",
            "emu_a15_oss2_v3": "Android 15 | 0 rows",
            "emu_a15_oss_v17": "Android 15 | 0 rows",
            "galaxys10_a10": "Android 10 | 1 rows",
            "hc_pixel8pro_a16": "Android 16 | 2 rows",
            "hc_pixel8pro_a17": "Android 17 | 2 rows",
            "hickman_a13": "Android 13 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 0 rows",
            "pixel7a_a14": "Android 14 | 2 rows",
            "russell_a14": "Android 14 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 4 rows",
            "sharon_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 4 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
    },
}

import datetime
import json
import re

from scripts.artifacts.storagePathViews import android_user, unique_files
from scripts.ilapfuncs import artifact_processor, check_in_media, logfunc

_FILE = re.compile(r'(?:^|/)(\d+)_pending_media\.json$')
_SHARED = re.compile(r'^/storage/emulated/(\d+)/(.+)$')
_APP_DATA = re.compile(r'^/data/(?:user/\d+|data)/(com\.instagram\.android/.+)$')


def _ms(value):
    """A millisecond Unix time as a UTC datetime; '' for a missing, zero or negative value."""
    try:
        millis = int(value)
    except (TypeError, ValueError):
        return ''
    return datetime.datetime.fromtimestamp(millis / 1000, tz=datetime.timezone.utc) if millis > 0 else ''


def _pattern(path):
    """A seeker pattern for a device path: shared storage is media/<user>/ in an extraction, app files are under the
    package folder. '[' is escaped because the seeker matches with fnmatch."""
    shared = _SHARED.match(path)
    if shared:
        tail = f'media/{shared.group(1)}/{shared.group(2)}'
    else:
        app = _APP_DATA.match(path)
        if not app:
            return None
        tail = app.group(1)
    return '*/' + tail.replace('[', '[[]')


def _media(context, entry):
    """(media reference, which path it came from) for the first of the entry's photo paths found in the extraction."""
    seeker = context.get_seeker()
    for key in ('originalImageMediaPath', 'originalImageFilePath', 'imageFilePath'):
        path = entry.get(key)
        if not isinstance(path, str) or not path.startswith('/') or path.endswith('/'):
            continue
        pattern = _pattern(path)
        found = seeker.search(pattern, return_on_first_hit=True) if pattern else None
        if isinstance(found, str) and found:  # a real seeker returns a path string
            reference = check_in_media(found, path.rsplit('/', 1)[-1])
            if reference:
                return reference, key
    return '', ''


@artifact_processor
def instagramPendingMedia(context):
    data_headers = (('Created', 'datetime'), ('Last User Interaction', 'datetime'), ('Last Upload Attempt', 'datetime'),
                    'Server Status (as stored)', 'Target Status (as stored)', 'Media Type', 'Share Type (as stored)',
                    'Instagram Media ID', ('Media', 'media'), 'Media Shown From', 'Source Media Path',
                    'Account ID (file name)', 'Android User')
    data_list, sources = [], []
    for file_found in unique_files(context):
        file_found = str(file_found)
        name = _FILE.search(file_found.replace('\\', '/'))
        if not name:
            continue
        relative = context.get_relative_path(file_found)
        sources.append(file_found)
        try:
            with open(file_found, 'rb') as handle:
                entries = json.loads(handle.read().decode('utf-8', 'replace'))
        except (OSError, ValueError) as ex:
            logfunc(f'Instagram - Pending Media: could not read {relative}: {type(ex).__name__}')
            continue
        if not isinstance(entries, list):
            logfunc(f'Instagram - Pending Media: {relative} does not hold a list; skipped')
            continue
        user = android_user(relative)
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            media, shown_from = _media(context, entry)
            source = entry.get('originalImageMediaPath') or entry.get('originalImageFilePath') or ''
            data_list.append((_ms(entry.get('time_created')), _ms(entry.get('lastUserInteractionTime')),
                              _ms(entry.get('lastUploadAttemptTime')), entry.get('serverStatus', ''),
                              entry.get('targetStatus', ''), entry.get('mediaType', ''), entry.get('share_type', ''),
                              entry.get('ig_media_id') or '', media, shown_from, source, name.group(1), user))
    return data_headers, data_list, '\n'.join(sources)
