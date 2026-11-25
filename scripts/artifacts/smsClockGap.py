__artifacts_v2__ = {
    "get_sms_clock_gap": {
        "name": "SMS Device Clock Gap",
        "description": "Received SMS with the stored service-centre time (date_sent) beside the stored receive "
                       "time (date), the difference in seconds and the app that wrote the row. A consistent "
                       "difference across rows can indicate a device clock that read ahead of or behind the "
                       "service centre; see the notes for limits.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-16",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Messaging",
        "notes": "One row per received SMS (sms.type 1, MESSAGE_TYPE_INBOX) whose date and date_sent are "
                 "both greater than zero, ordered by Service Centre Time within each database. In AOSP's "
                 "reference Messaging app, date_sent is written from SmsMessage.getTimestampMillis(), the "
                 "service-centre timestamp carried in the message, and date is the phone's clock when the "
                 "app handled the message. If that clock reads before 18 Sep 2011, the app stores the "
                 "service-centre time in date instead, so the gap is 0. References: "
                 "https://android.googlesource.com/platform/packages/apps/Messaging/+/de315b762312dd1a5d2bbd16e62ef2bd123f61e5/src/com/android/messaging/sms/MmsUtils.java#1035"
                 " , "
                 "https://android.googlesource.com/platform/packages/apps/Messaging/+/de315b762312dd1a5d2bbd16e62ef2bd123f61e5/src/com/android/messaging/sms/MmsUtils.java#1075"
                 " , "
                 "https://android.googlesource.com/platform/packages/apps/Messaging/+/de315b762312dd1a5d2bbd16e62ef2bd123f61e5/src/com/android/messaging/receiver/SmsReceiver.java#208"
                 " , "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/telephony/java/com/android/internal/telephony/SmsMessageBase.java#214"
                 " , "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/core/java/android/provider/Telephony.java#144"
                 " . Creator (as stored) is the provider's creator column, documented as usually the "
                 "package name of the app that wrote the row "
                 "(https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/core/java/android/provider/Telephony.java#280)."
                 " Creator (as stored) held one value on all rows of each image checked "
                 "(com.google.android.apps.messaging on all 53 rows of hc_pixel8pro_a16, "
                 "com.samsung.android.messaging on all 58 rows of cookbook_a11); it is kept because it "
                 "names the app whose behaviour applies. Google Messages and Samsung Messages are closed "
                 "source. For Google Messages this reading rests on the test below. For Samsung Messages "
                 "there is no test with a known clock state, and its rows are reported as stored. Gap "
                 "(Seconds) is date minus date_sent. In the test below a clock set ahead gave a positive "
                 "gap; a clock set behind was not tested and would be expected to give a negative one. The"
                 " gap also includes any time the network held the message before delivery, and date_sent "
                 "was a whole number of seconds on every row measured, so one row is not a clock offset. "
                 "Compare the smallest gaps over a period. A step that persists across later rows is "
                 "consistent with a clock change between the two messages where it starts. A gap near zero"
                 " on a prompt delivery is consistent with a correct clock, not proof of one, and a gap of"
                 " exactly 0 on every row means both columns hold one value and says nothing about the "
                 "clock. Known data: on a Pixel 7a (Android 17, Google Messages) texting itself, the gap "
                 "was 0.7 to 1.6 s (four messages) with the clock correct and 1200.2 and 1200.5 s (two "
                 "messages) with the clock set 20 minutes ahead; that test read the SMS provider on the "
                 "live phone, not an extraction. On the 18 corpus images listed in sample_data (1,944 "
                 "rows; three pairs of images share rows, 1,801 distinct messages), the smallest gap per "
                 "image was between -72.4 and 2.6 s and the median between 1.2 and 7.1 s, except "
                 "cookbook_a11, where all 58 rows were written by Samsung Messages, Gap (Seconds) held 0.0"
                 " on all 58 rows and Service Centre Time (date_sent) and Received (Device Clock) were "
                 "identical on all 58 rows, so that image allows no comparison. 301 rows had a gap over 60"
                 " s and 262 over one hour. 22 rows on 6 images (16 distinct messages) had negative gaps, "
                 "from -72.4 to -0.004 s; 8 were below -1 s. Each mmssms.db found is listed as a source, "
                 "including copies whose sms table held no rows. Sent messages are not reported: date_sent"
                 " was 0 on every sent row of hc_pixel8pro_a16 and of the Pixel 7a test. Not read: MMS, "
                 "Samsung's spam_sms table and RCS messages. Suggested by an examiner on a mailing list.",
        "paths": ('*/com.android.providers.telephony/databases/mmssms*',),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | com.android.providers.telephony | 32 rows",
            "anne_a15": "Android 15 | com.android.providers.telephony | 15 rows",
            "cookbook_a11": "Android 11 | com.android.providers.telephony | 58 rows",
            "falken_a326u_a13": "Android 13 | com.android.providers.telephony | 10 rows",
            "galaxys10_a10": "Android 10 | com.android.providers.telephony | 18 rows",
            "hc_pixel8pro_a16": "Android 16 | com.android.providers.telephony | 53 rows",
            "hc_pixel8pro_a17": "Android 17 | com.android.providers.telephony | 59 rows",
            "kevin_pocox7_a15": "Android 15 | com.android.providers.telephony | 67 rows",
            "pixel3_a11": "Android 11 | com.android.providers.telephony | 26 rows",
            "pixel3_a12": "Android 12 | com.android.providers.telephony | 25 rows",
            "pixel7a_a14": "Android 14 | com.android.providers.telephony | 1031 rows",
            "russell_a14": "Android 14 | com.android.providers.telephony | 117 rows",
            "russell_pixel6a_a13": "Android 13 | com.android.providers.telephony | 11 rows",
            "samsunga53_a14": "Android 14 | com.android.providers.telephony | 41 rows",
            "samsungs20_a13": "Android 13 | com.android.providers.telephony | 33 rows",
            "sharon_a13": "Android 13 | com.android.providers.telephony | 89 rows",
            "sharon_a14": "Android 14 | com.android.providers.telephony | 243 rows",
            "userb2_a13": "Android 13 | com.android.providers.telephony | 16 rows",
        },
    },
}

import datetime
import sqlite3

from scripts.ilapfuncs import (artifact_processor, open_sqlite_db_readonly, does_table_exist_in_db,
                               does_column_exist_in_db)
from scripts.artifacts.storagePathViews import unique_files

# Telephony.TextBasedSmsColumns.MESSAGE_TYPE_INBOX
_TYPE_INBOX = 1

_QUERY = '''
    SELECT _id, thread_id, address, date, date_sent, {creator}
    FROM sms
    WHERE type = 1 AND date > 0 AND date_sent > 0
    ORDER BY date_sent, _id
'''


def _ms_to_utc(value):
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _mmssms_dbs(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('mmssms.db') and '/mirror/' not in file_found.replace('\\', '/'):
            yield file_found


@artifact_processor
def get_sms_clock_gap(context):
    data_list = []
    source_paths = []
    for source_path in _mmssms_dbs(unique_files(context)):
        source_paths.append(source_path)
        if not does_table_exist_in_db(source_path, 'sms'):
            continue
        db = open_sqlite_db_readonly(source_path)
        if db is None:
            continue
        try:
            creator = 'creator' if does_column_exist_in_db(source_path, 'sms', 'creator') else "''"
            rows = db.execute(_QUERY.format(creator=creator)).fetchall()
        except sqlite3.Error:
            rows = []
        finally:
            db.close()
        for msg_id, thread_id, address, date, date_sent, creator_value in rows:
            data_list.append((
                _ms_to_utc(date_sent),
                _ms_to_utc(date),
                round((int(date) - int(date_sent)) / 1000, 3),
                address,
                thread_id,
                msg_id,
                creator_value,
            ))

    data_headers = (
        ('Service Centre Time (date_sent)', 'datetime'),
        ('Received (Device Clock)', 'datetime'),
        ('Gap (Seconds)', 'number'),
        'Address',
        'Thread ID',
        'MSG ID',
        'Creator (as stored)',
    )
    return data_headers, data_list, '\n'.join(source_paths)
