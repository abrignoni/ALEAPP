"""
Copyright 2022, CCL Forensics

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
__artifacts_v2__ = {
    "get_fcm_groupme": {
        "name": "FCM - GroupMe Notifications",
        "description": "GroupMe (com.groupme.android) push records from the Firebase Cloud "
                       "Messaging queued-messages store, fcm_queued_messages.ldb. Reports the "
                       "notification text and the fields of the push payload, including the "
                       "message text, its sender, the conversation it belongs to and any "
                       "attachment it carries.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-18",
        "last_update_date": "2026-08-18",
        "requirements": "none",
        "category": "Firebase Cloud Messaging",
        "notes": "Records are attributed to GroupMe by field 5 of the value protobuf's embedded message, "
                 "which holds the package name. The record key names no application: on both tested images "
                 "every key begins with the numeric prefix '0:'. The timestamp in the key is microseconds "
                 "since the Unix epoch and is reported first; Push Timestamp is the payload's own "
                 "push_timestamp value and Message Created is the created_at of the message the payload "
                 "carries.\n"
                 "Each GroupMe entry on both tested images is a value record with a later deletion marker "
                 "for the same key, so they are reported because the reader takes records from the table "
                 "files directly rather than resolving the store to its committed state.\n"
                 "Event, and the payload keys reported as stored, are undocumented here. The payload keys "
                 "observed on pixel7a_a14 are alert, subject, event, user_id, push_timestamp, "
                 "google.c.a.m_l, google.c.a.e, google.c.sender.id and, on one record, title and reaction. "
                 "The older records on pixel3_a12 carry no push_timestamp, so that column is empty there. "
                 "For favorite events the payload nests the message that was reacted to under "
                 "'direct_message' or 'line', so the message columns describe that message and not the "
                 "person who reacted, whose identifier is the payload's own user_id.\n"
                 "Message Sender ID is the payload's sender_id, falling back to the message's own user_id "
                 "where the payload carries no sender_id. Both are present on 15 of the 18 records on "
                 "pixel7a_a14 and agree on all 15; the 5 records on pixel3_a12 carry only user_id.\n"
                 "One record on pixel7a_a14 carries an empty alert. Its payload is a direct message with "
                 "empty text and a location attachment, whose coordinates and place name are reported in the "
                 "Attachments column, and it is reported rather than dropped. No empty alert was observed on "
                 "pixel3_a12.\n"
                 "Media is linked by deriving the GroupMe image cache key from the attachment URL: the cache "
                 "is a libcore DiskLruCache whose key is the Java String.hashCode of the URL and whose file "
                 "is that key followed by the value index. On pixel7a_a14 all 24 cache entries are accounted "
                 "for by that derivation and 13 of them are attributable to image URLs held independently in "
                 "groupme.db, including both URLs the push records reference; the one picture message on "
                 "pixel3_a12 linked the same way. The app also caches '.large' and '.preview' renditions "
                 "under the hash of the suffixed URL; those are used only when the unsuffixed URL is not "
                 "cached, and the rendition used is named in the Attachments column. The separate "
                 "groupme_gif_cache uses a different naming scheme and is not linked.\n"
                 "An extraction can carry the queued-messages store under several storage paths. pixel3_a12 "
                 "holds it at data/data, data/user/0 and data_mirror/data_ce, and the module reports 5 rows "
                 "there rather than the 15 the three copies would otherwise produce.",
        "paths": ('*/fcm_queued_messages.ldb/*',
                  '*/com.groupme.android/cache/groupme_image_cache/*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gms | 0 rows",
            "cookbook_a11": "Android 11 | com.google.android.gms | 0 rows",
            "df020_mavic_pro_android": "Android logical | no fcm_queued_messages.ldb store | 0 rows",
            "galaxys10_a10": "Android 10 | com.google.android.gms | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | com.google.android.gms | 0 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 0 rows",
            "pixel3_a11": "Android 11 | com.google.android.gms | 0 rows",
            "pixel3_a12": "Android 12 | com.google.android.gms | com.groupme.android | 5 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms | com.groupme.android | 18 rows",
            "russell_a14": "Android 14 | com.google.android.gms | 0 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gms | 0 rows",
            "s20fe_a13": "Android 13 | com.google.android.gms | 0 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 0 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 0 rows",
            "sharon_a13": "Android 13 | com.google.android.gms | 0 rows",
            "sharon_a14": "Android 14 | com.google.android.gms | 0 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 0 rows",
        },
    }
}

import datetime
import json
import os
import pathlib

from scripts.ccl.ccl_android_fcm_queued_messages import FcmIterator
from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, check_in_media, logfunc

PACKAGE = 'com.groupme.android'
FCM_STORE_DIR = 'fcm_queued_messages.ldb'
IMAGE_CACHE_DIR = 'groupme_image_cache'

# The renditions the app caches under the hash of the suffixed URL, preferred order. The
# empty entry is the URL the payload actually names.
_RENDITIONS = ('', '.large', '.preview')


def _java_string_hash_code(value):
    """The 32 bit signed hash Java's String.hashCode() produces, which names the cache entry."""
    result = 0
    for character in value:
        result = (31 * result + ord(character)) & 0xFFFFFFFF
    return result - 0x100000000 if result >= 0x80000000 else result


def _key_timestamp(value):
    if isinstance(value, datetime.datetime):
        return value.replace(tzinfo=datetime.timezone.utc) if value.tzinfo is None else value
    return ''


def _iso_to_utc(value):
    """push_timestamp is an ISO 8601 string ending in Z, which 3.10 will not parse as is."""
    if not value:
        return ''
    try:
        parsed = datetime.datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except ValueError:
        return value
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    return parsed.astimezone(datetime.timezone.utc)


def _seconds_to_utc(value):
    try:
        return datetime.datetime.fromtimestamp(int(value), datetime.timezone.utc)
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _split_paths(files_found):
    """The FCM store directories and the image cache files the globs matched."""
    store_dirs, cache_files = set(), []
    for file_found in files_found:
        path = pathlib.Path(str(file_found))
        if path.parent.name == FCM_STORE_DIR:
            store_dirs.add(path.parent)
        elif path.parent.name == IMAGE_CACHE_DIR:
            cache_files.append(str(file_found))
    return sorted(store_dirs), cache_files


def _message_object(subject):
    """The message a payload carries, which a favorite event nests a level down."""
    if not isinstance(subject, dict):
        return {}
    for nested in ('direct_message', 'line'):
        if isinstance(subject.get(nested), dict):
            return subject[nested]
    return subject


def _describe_attachments(message):
    """Attachment and location text, and the image URLs worth looking for in the cache."""
    described, urls = [], []
    for attachment in message.get('attachments') or []:
        if not isinstance(attachment, dict):
            continue
        kind = attachment.get('type')
        if kind == 'location':
            described.append(f"location {attachment.get('lat')}, {attachment.get('lng')}"
                             f" ({attachment.get('name')})")
        else:
            url = attachment.get('url')
            described.append(f"{kind} {url}" if url else str(kind))
            if url:
                urls.append(url)
    if not described:
        location = message.get('location')
        if isinstance(location, dict) and location.get('lat'):
            described.append(f"location {location.get('lat')}, {location.get('lng')}"
                             f" ({location.get('name')})")
    return described, urls


def _cache_index(cache_files):
    """Cache entry file name to path, so a derived key can be looked up directly."""
    return {os.path.basename(path): path for path in cache_files}


def _check_in_cached_image(url, index):
    """The cached bytes for an image URL, plus the rendition they came from."""
    for rendition in _RENDITIONS:
        key = _java_string_hash_code(url + rendition)
        for name in (f'{key}0', f'{key}.0'):
            path = index.get(name)
            if not path:
                continue
            reference = check_in_media(path, os.path.basename(url) + rendition)
            if reference:
                return reference, rendition
    return '', None


def _rows(store_dirs, cache_files):
    index = _cache_index(cache_files)
    rows = []
    for store_dir in store_dirs:
        try:
            with FcmIterator(store_dir) as record_iterator:
                for record in record_iterator:
                    if record.package != PACKAGE:
                        continue
                    try:
                        rows.append(_row(record, index))
                    except (KeyError, ValueError, TypeError) as exc:
                        logfunc(f'GroupMe FCM: could not parse record {record.key}: {exc}')
        except Exception as exc:  # pylint: disable=W0718
            logfunc(f'GroupMe FCM: error reading {store_dir}: {exc}')
    rows.sort(key=lambda row: str(row[0]))
    return rows


def _row(record, index):
    values = record.key_values
    try:
        subject = json.loads(values.get('subject') or '{}')
    except ValueError:
        subject = {}
    message = _message_object(subject)
    described, urls = _describe_attachments(message)

    media = ''
    for url in urls:
        media, rendition = _check_in_cached_image(url, index)
        if media:
            described.append(f"cached as {url}{rendition}" if rendition else 'cached')
            break

    return (_key_timestamp(record.timestamp),
            _iso_to_utc(values.get('push_timestamp')),
            _seconds_to_utc(message.get('created_at')),
            values.get('event', ''),
            message.get('name', ''),
            message.get('sender_id') or message.get('user_id') or '',
            message.get('group_id', ''),
            message.get('chat_id', ''),
            message.get('id', ''),
            values.get('user_id', ''),
            values.get('alert', ''),
            message.get('text', ''),
            '; '.join(described),
            media,
            record.key)


@artifact_processor
def get_fcm_groupme(context):
    store_dirs, cache_files = _split_paths(unique_files(context))
    data_headers = (('FCM Timestamp', 'datetime'),
                    ('Push Timestamp', 'datetime'),
                    ('Message Created', 'datetime'),
                    'Event (as stored)',
                    'Message Sender',
                    'Message Sender ID',
                    'Group ID',
                    'Chat ID',
                    'Message ID',
                    'User ID',
                    'Alert Text',
                    'Message Text',
                    'Attachments',
                    ('Media', 'media'),
                    'FCM Key')
    source_files = ' '.join(str(x) for x in store_dirs)
    return data_headers, _rows(store_dirs, cache_files), source_files
