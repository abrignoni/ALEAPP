__artifacts_v2__ = {
    "snapchat_client_notifications": {
        "name": "Snapchat - Client Notifications",
        "description": "Notifications the Snapchat app recorded in its "
                       "client_notifications.db, with the server send time, the receive time "
                       "and the title, subtitle and local message keys of the payload when it"
                       " carries them.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Snapchat",
        "notes": "Read from the Notifications table of "
                 "com.snapchat.android/databases/client_notifications.db, with its "
                 "write-ahead log when one is beside it. Column meanings are the ones the "
                 "table's own CREATE TABLE comments give: 'Sent' is timestamp, the time in "
                 "milliseconds the notification was sent by the server; 'Received' is "
                 "receiveTimestampMs, when it was first received from the server; 'Latest "
                 "Announce' is latestAnnounceTimestampMs, the latest attempt to announce it "
                 "to the platform; 'Redrive Attempts' is redriveAttemptCount; 'Suppression "
                 "Reason (as stored)' is suppressionReason, blank when the notification was "
                 "not suppressed or the reason is unknown. 'Conversation ID' is "
                 "groupingConversationId, which the comments call a pre-extracted grouping "
                 "key; when it is blank the payload's arroyo_convo_id is used. That fallback "
                 "did not occur on the tested images, and the two were equal on the 22 rows "
                 "that held both. The comments give the unit of the times and not the epoch; "
                 "read as Unix milliseconds they fall inside each image's acquisition window,"
                 " with receive at or after sent on every row. All times are shown in UTC, "
                 "and a zero or absent time is blank. 'Category', 'State' and 'Source' are "
                 "integers the comments name (notification category, processing state, system"
                 " source) without listing their values, so they are reported as stored. "
                 "'Title', 'Subtitle', 'Local Title', 'Local Message' and 'Recipient User ID'"
                 " are the payload's title, subtitle, local_title, local_message and "
                 "recipient_userid keys; their meaning is taken from the key names and is not"
                 " sourced. 'Other Payload' holds the remaining payload keys as name=value "
                 "after JSON decoding; the payload's n_id, type, sent_ts and arroyo_convo_id "
                 "are left out when they equal the Notification ID, Type, Sent and "
                 "Conversation ID columns, and shown when they differ. The table's "
                 "isRedrivable, skipDedupe, latestRedriveReminderTimestampMs, hasGroupingData"
                 " and groupingBundleId columns are not reported. A row records that the app "
                 "stored the notification; it does not establish that it was shown or read. "
                 "On dragna_pixel9a_a16 (37 rows, 36 map_live_location and 1 "
                 "available_friend_suggestions) 'Subtitle', 'Local Message' and 'Suppression "
                 "Reason (as stored)' held no value on any row, 'Title' and 'Local Title' "
                 "were identical on the 36 rows that carry them (the other row has neither), "
                 "'Category (as stored)' held 1 on every row, and 'Recipient User ID' held "
                 "one value. On hc_pixel8pro_a17 the 21 rows are discover_stories, "
                 "spotlight_feed_subscription_story, try_lenses and ping notifications, and "
                 "no row carries a title, subtitle, local title or local message. On "
                 "hc_pixel8pro_a16 the table holds no rows. On dragna_pixel9a_a16 none of the"
                 " 37 Notification ID values appeared among the n_id values of the 209 "
                 "Snapchat records in ALEAPP's FCM Dump output; those records end on "
                 "2026-09-28 and the 37 notifications are dated 2026-10-15.",
        "paths": ('*/com.snapchat.android/databases/client_notifications.db*',),
        "output_types": "standard",
        "artifact_icon": "bell",
        "sample_data": {
            "dragna_pixel9a_a16": "Android 16 | com.snapchat.android versionCode 319422 | 37 rows",
            "hc_pixel8pro_a16": "Android 16 | com.snapchat.android | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | com.snapchat.android | 21 rows",
        },
    },
}

import json
import os
from datetime import datetime, timezone

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records, logfunc

# Payload keys shown in their own columns; the rest of the payload is in 'Other Payload'.
_SHOWN = ('title', 'subtitle', 'local_title', 'local_message', 'recipient_userid',
          'arroyo_convo_id', 'n_id', 'sent_ts', 'type')

_QUERY = '''
    SELECT timestamp, receiveTimestampMs, latestAnnounceTimestampMs, type, json,
           groupingConversationId, category, state, source, suppressionReason,
           redriveAttemptCount, notificationId
    FROM Notifications
'''


def _utc_ms(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return ''
    if number <= 0:
        return ''
    try:
        return datetime.fromtimestamp(number / 1000, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return ''


def _text(value):
    return '' if value is None else str(value)


@artifact_processor
def snapchat_client_notifications(context):
    data_headers = (
        ('Sent', 'datetime'), ('Received', 'datetime'), ('Latest Announce', 'datetime'),
        'Type', 'Title', 'Subtitle', 'Local Title', 'Local Message', 'Conversation ID',
        'Recipient User ID', 'Category (as stored)', 'State (as stored)',
        'Source (as stored)', 'Suppression Reason (as stored)', 'Redrive Attempts',
        'Notification ID', 'Other Payload')
    data_list, sources = [], []
    for file_found in unique_files(context):
        path = str(file_found)
        if os.path.basename(path) != 'client_notifications.db':
            continue
        sources.append(path)
        for row in get_sqlite_db_records(path, _QUERY):
            (sent, received, announced, kind, payload, grouping, category, state, source,
             suppression, redrives, notification_id) = row
            try:
                fields = json.loads(payload) if payload else {}
            except ValueError:
                logfunc('Snapchat - Client Notifications: a payload is not JSON and is '
                        'reported as stored')
                fields = {'payload': payload}
            if not isinstance(fields, dict):
                fields = {'payload': fields}
            same = {'n_id': notification_id, 'type': kind, 'sent_ts': sent,
                    'arroyo_convo_id': grouping}
            other = '; '.join(
                f'{key}={value}' for key, value in fields.items()
                if key not in _SHOWN or (key in same and str(value) != str(same[key])))
            data_list.append((
                _utc_ms(sent), _utc_ms(received), _utc_ms(announced), _text(kind),
                _text(fields.get('title')), _text(fields.get('subtitle')),
                _text(fields.get('local_title')), _text(fields.get('local_message')),
                _text(grouping or fields.get('arroyo_convo_id')),
                _text(fields.get('recipient_userid')), _text(category), _text(state),
                _text(source), _text(suppression), _text(redrives), _text(notification_id),
                other,
            ))
    return data_headers, data_list, '\n'.join(sources)
