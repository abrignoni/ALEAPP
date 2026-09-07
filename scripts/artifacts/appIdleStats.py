__artifacts_v2__ = {
    "app_idle_stats": {
        "name": "App Standby Buckets",
        "description": "The App Standby bucket the platform recorded for a package under an Android user, the "
                       "reason for that bucket, and the usage times it keeps alongside them, which "
                       "are not wall-clock dates.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Usage Stats",
        "notes": "Read from the per-user app_idle_stats.xml under the system users folder, one row per "
                 "package element, with User ID taken from the folder the file sits in. The pattern is "
                 "not anchored on a data/ prefix, because a raw userdata partition image carries the "
                 "same folder without one, as samsungs20_a13 does. The file was plain XML on all 58 "
                 "tested files and an ABX binary XML read is used when the file carries the ABX magic, a "
                 "branch no tested image exercised. Of the 39 registered Android corpora 36 produced "
                 "rows, 22 of them holding a second Android user; the other 3 are partial extractions "
                 "that do not carry the file.\nStandby Bucket is the bucket the platform had the app in, "
                 "from the UsageStatsManager STANDBY_BUCKET constants, and all seven of EXEMPTED, "
                 "ACTIVE, WORKING_SET, FREQUENT, RARE, RESTRICTED and NEVER appeared across the tested "
                 "images. ACTIVE through RARE run from more recent to less recent use in the AOSP "
                 "descriptions, RESTRICTED adds that the app has also been misbehaving in some manner, "
                 "and NEVER is the value AOSP gives for an app that has never been used. EXEMPTED is not "
                 "a recency value: AOSP describes it as the app being exempted for some reason with the "
                 "bucket unable to change, and it was the second most common bucket across the tested "
                 "images. Bucket Reason is decoded from the stored value, which the platform writes as "
                 "hexadecimal without a prefix, as a main reason in the high byte and a sub reason in "
                 "the low byte. The sub reason is scoped to its main reason, so the same low byte means "
                 "different things under different main reasons, and for the two forced main reasons the "
                 "low byte is a set of bit flags rather than a single value. Bucket Reason (as stored) "
                 "carries the raw value, and a value whose main reason is outside the AOSP set is "
                 "reported as stored: that happened on 3 of 19,629 rows, all carrying main reason 0x700 "
                 "with the RESTRICTED bucket on two Samsung images, and it is not named here because no "
                 "source for it was found. Reference: AOSP, UsageStatsManager, the STANDBY_BUCKET, "
                 "REASON_MAIN and REASON_SUB constants and reasonToString, "
                 "https://android.googlesource.com/platform/frameworks/base/+/4e43ad12e1b211f15152e9c5b16b0fe88e6b93f3/core/java/android/app/usage/UsageStatsManager.java\nThe "
                 "columns marked device-on ms and screen-on ms are not wall-clock times and must not be "
                 "read as dates. AOSP records them on a timebase that accumulates device-on time across "
                 "boots, computed as elapsed realtime minus a snapshot plus a stored duration, so a "
                 "value is an offset within that accumulator and not milliseconds since the epoch. The "
                 "largest seen across the tested images was 34,487,884,500, about 399 days of device-on "
                 "time, which read as milliseconds since the epoch would decode to 1971-02-04 rather "
                 "than to any time the device existed. Converting them would need the mScreenOnDuration "
                 "and mElapsedDuration pair the platform keeps in the separate system/screen_on_time "
                 "file, which this artifact does not read. They are reported as stored, and within one "
                 "extraction they still order packages by how recently each was used. The platform "
                 "never-used sentinel, Integer.MIN_VALUE, is left blank, which is why Last Used is "
                 "populated on 5,202 of the 19,629 rows; small negative values are real and are kept, as "
                 "on the Android 10 image. Reference: AOSP, AppIdleHistory, getElapsedTime and the "
                 "attribute constants with their timebase comments, "
                 "https://android.googlesource.com/platform/frameworks/base/+/4e43ad12e1b211f15152e9c5b16b0fe88e6b93f3/apex/jobscheduler/service/java/com/android/server/usage/AppIdleHistory.java\nNext "
                 "Estimated App Launch is the one wall-clock value in the file, milliseconds since the "
                 "Unix epoch, rendered in UTC. AOSP describes it as the next estimated launch time for "
                 "the app, so it is a value the platform wrote forward and not a record that the app was "
                 "launched. Across the tested images it was present on 2,230 of 19,629 rows and ranged "
                 "from 2023-03-28 to 2027-09-06, so it carried dates both before and after the "
                 "extraction dates and the column is blank on most rows.\nBucket Expiry folds two schema "
                 "generations into one column: AOSP version 1 of this file writes expiryTimes item "
                 "elements, and the version before it wrote activeTimeoutTime and workingSetTimeoutTime "
                 "attributes, both of which are read here. 52 of the 58 files read were version 1 and 6 "
                 "were the earlier form. Last Used By User was absent on the Android 10 image. Last "
                 "Restriction Attempt and Restriction Reason are set on 75 rows; a blank Restriction "
                 "Reason is the platform having recorded no reason, which AOSP also renders as empty, "
                 "and it does not distinguish that from the attribute being absent on the older "
                 "schema.\nThis file names packages, not installed packages. Measured on the tested "
                 "emulator: of the 317 and 278 package names it held for the two Android users, one in "
                 "each was not installed for that user, and an app removed with pm uninstall was not "
                 "named here while system/appops_accesses.xml on that same device still named it. So "
                 "retention after a removal differs between the two files and was measured rather than "
                 "assumed. Whether an entry is removed at uninstall or on a later write was not "
                 "established.\nThe path pattern is tolerant, so a second copy of a user file in an "
                 "extraction would add its rows again. None of the 39 corpora carried more than one per "
                 "user, and the Source File column names the file each row came from.",
        "paths": ('*/system/users/*/app_idle_stats.xml',),
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 429 rows",
            "anne_a15": "Android 15 | 544 rows",
            "cookbook_a11": "Android 11 | 863 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 504 rows",
            "emu_a15_oss_v10": "Android 15 | 572 rows",
            "emu_a15_oss_v11": "Android 15 | 573 rows",
            "emu_a15_oss_v12": "Android 15 | 578 rows",
            "emu_a15_oss_v13": "Android 15 | 580 rows",
            "emu_a15_oss_v14": "Android 15 | 580 rows",
            "emu_a15_oss_v15": "Android 15 | 588 rows",
            "emu_a15_oss_v16": "Android 15 | 592 rows",
            "emu_a15_oss_v17": "Android 15 | 596 rows",
            "emu_a15_oss_v2": "Android 15 | 513 rows",
            "emu_a15_oss_v3": "Android 15 | 524 rows",
            "emu_a15_oss_v4": "Android 15 | 535 rows",
            "emu_a15_oss_v5": "Android 15 | 550 rows",
            "emu_a15_oss_v6": "Android 15 | 580 rows",
            "emu_a15_oss_v7": "Android 15 | 592 rows",
            "emu_a15_oss_v8": "Android 15 | 592 rows",
            "emu_a15_oss_v9": "Android 15 | 592 rows",
            "falken_a326u_a13": "Android 13 | 479 rows",
            "galaxys10_a10": "Android 10 | 416 rows",
            "hc_pixel8pro_a16": "Android 16 | 405 rows",
            "hc_pixel8pro_a17": "Android 17 | 424 rows",
            "hc_pixel8pro_a17_ail": "0 rows",
            "kevin_pocox7_a15": "Android 15 | 467 rows",
            "pixel3_a11": "Android 11 | 581 rows",
            "pixel3_a12": "Android 12 | 318 rows",
            "pixel7a_a14": "Android 14 | 382 rows",
            "russell_a14": "Android 14 | 816 rows",
            "russell_pixel6a_a13": "Android 13 | 597 rows",
            "s20fe_a13": "Android 13 | 485 rows",
            "samsunga53_a14": "Android 14 | 487 rows",
            "samsungs20_a13": "Android 13 | 839 rows",
            "sharon_a13": "Android 13 | 531 rows",
            "sharon_a14": "Android 14 | 617 rows",
            "userb2_a13": "Android 13 | 308 rows",
        },
    },
}

import datetime
import os
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import abxread, artifact_processor, checkabx, logfunc

# UsageStatsManager STANDBY_BUCKET constants, at android-15.0.0_r1.
STANDBY_BUCKETS = {
    '5': 'EXEMPTED',
    '10': 'ACTIVE',
    '20': 'WORKING_SET',
    '30': 'FREQUENT',
    '40': 'RARE',
    '45': 'RESTRICTED',
    '50': 'NEVER',
}

# UsageStatsManager REASON_MAIN constants, at android-15.0.0_r1.
REASON_MAIN_MASK = 0xFF00
REASON_SUB_MASK = 0x00FF
REASON_MAIN = {
    0x0100: 'DEFAULT',
    0x0200: 'TIMEOUT',
    0x0300: 'USAGE',
    0x0400: 'FORCED_BY_USER',
    0x0500: 'PREDICTED',
    0x0600: 'FORCED_BY_SYSTEM',
}

# REASON_SUB constants, keyed by their main reason because the same low byte means different
# things under different main reasons. At android-15.0.0_r1.
REASON_SUB = {
    0x0100: {
        0x00: 'UNDEFINED',
        0x01: 'APP_UPDATE',
        0x02: 'APP_RESTORED',
    },
    0x0300: {
        0x01: 'SYSTEM_INTERACTION',
        0x02: 'NOTIFICATION_SEEN',
        0x03: 'USER_INTERACTION',
        0x04: 'MOVE_TO_FOREGROUND',
        0x05: 'MOVE_TO_BACKGROUND',
        0x06: 'SYSTEM_UPDATE',
        0x07: 'ACTIVE_TIMEOUT',
        0x08: 'SYNC_ADAPTER',
        0x09: 'SLICE_PINNED',
        0x0A: 'SLICE_PINNED_PRIV',
        0x0B: 'EXEMPTED_SYNC_SCHEDULED_NON_DOZE',
        0x0C: 'EXEMPTED_SYNC_SCHEDULED_DOZE',
        0x0D: 'EXEMPTED_SYNC_START',
        0x0E: 'UNEXEMPTED_SYNC_SCHEDULED',
        0x0F: 'FOREGROUND_SERVICE_START',
    },
    0x0500: {
        0x01: 'RESTORED',
    },
}

# For the two forced main reasons the sub reason is a set of bit flags. At android-15.0.0_r1.
REASON_SUB_FLAGS = {
    0x0600: ((1 << 0, 'BACKGROUND_RESOURCE_USAGE'), (1 << 1, 'ABUSE'), (1 << 2, 'BUGGY')),
    0x0400: ((1 << 1, 'INTERACTION'),),
}

# AppIdleHistory writes this sentinel for a package it has no usage time for.
NEVER_USED = -2147483648


def _root(path):
    """The XML root, reading ABX binary XML or plain XML."""
    if checkabx(path):
        try:
            return abxread(path, False).getroot()
        except Exception:  # pylint: disable=broad-except
            return abxread(path, True).getroot()
    return ET.parse(path).getroot()


def _elapsed(value):
    """A device-on or screen-on offset as stored, with the platform's never-used sentinel and
    anything below it left blank."""
    if value is None:
        return ''
    try:
        if int(value) <= NEVER_USED:
            return ''
    except ValueError:
        return value
    return value


def _epoch_ms(value):
    """A datetime from milliseconds since the Unix epoch, in UTC, or '' when absent."""
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError):
        return value


def _reason(value):
    """The main and sub reason names for a bucketing reason, which the platform writes as
    hexadecimal without a prefix. Reported as stored when the main reason is outside the AOSP
    set."""
    if not value:
        return ''
    try:
        reason = int(value, 16)
    except ValueError:
        return value
    if reason == 0:
        # AppIdleHistory writes 0 where it has recorded no reason, and AOSP's own
        # reasonToString renders that as the empty string.
        return ''
    main = reason & REASON_MAIN_MASK
    sub = reason & REASON_SUB_MASK
    main_name = REASON_MAIN.get(main)
    if main_name is None:
        return value
    if main in REASON_SUB_FLAGS:
        names = [name for bit, name in REASON_SUB_FLAGS[main] if sub & bit]
        remainder = sub & ~sum(bit for bit, _ in REASON_SUB_FLAGS[main])
        if remainder:
            names.append(hex(remainder))
        return f'{main_name} / {" | ".join(names)}' if names else main_name
    sub_name = REASON_SUB.get(main, {}).get(sub)
    if sub_name is None:
        return main_name if sub == 0 else f'{main_name} / {hex(sub)}'
    if sub_name == 'UNDEFINED':
        return main_name
    return f'{main_name} / {sub_name}'


def _expiry(package):
    """The bucket expiry times, folding the version 1 expiryTimes item elements and the
    activeTimeoutTime and workingSetTimeoutTime attributes the previous version wrote."""
    parts = []
    for item in package.iter('item'):
        bucket = item.get('bucket', '')
        parts.append(f'{STANDBY_BUCKETS.get(bucket, bucket)}={item.get("expiry", "")}')
    for attribute, bucket in (('activeTimeoutTime', 'ACTIVE'),
                              ('workingSetTimeoutTime', 'WORKING_SET')):
        value = package.get(attribute)
        if value is not None:
            parts.append(f'{bucket}={value}')
    return '; '.join(parts)


@artifact_processor
def app_idle_stats(context):
    data_headers = (
        'Package Name',
        'User ID',
        'Standby Bucket',
        'Bucket Reason',
        'Bucket Reason (as stored)',
        ('Next Estimated App Launch', 'datetime'),
        'Last Used (device-on ms)',
        'Last Used By User (device-on ms)',
        'Last Used Screen On (screen-on ms)',
        'Last Predicted (device-on ms)',
        'Last Job Run (device-on ms)',
        'Bucket Expiry (device-on ms)',
        'Last Restriction Attempt (device-on ms)',
        'Restriction Reason',
        'Source File',
    )
    data_list = []
    sources = []

    for file_found in sorted(context.get_files_found()):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        if os.path.basename(file_found) != 'app_idle_stats.xml':
            continue
        user_id = os.path.basename(os.path.dirname(file_found))
        if not user_id.isdigit():
            continue
        try:
            root = _root(file_found)
        except Exception as error:  # pylint: disable=broad-except
            logfunc(f'App Standby Buckets: could not read user {user_id}: {error}')
            continue
        relative_path = context.get_relative_path(file_found)
        rows = 0
        for package in root.iter('package'):
            bucket = package.get('appLimitBucket', '')
            data_list.append((
                package.get('name', ''),
                user_id,
                STANDBY_BUCKETS.get(bucket, bucket),
                _reason(package.get('bucketReason')),
                package.get('bucketReason', ''),
                _epoch_ms(package.get('nextEstimatedAppLaunchTime')),
                _elapsed(package.get('elapsedIdleTime')),
                _elapsed(package.get('lastUsedByUserElapsedTime')),
                _elapsed(package.get('screenIdleTime')),
                _elapsed(package.get('lastPredictedTime')),
                _elapsed(package.get('lastJobRunTime')),
                _expiry(package),
                _elapsed(package.get('lastRestrictionAttemptElapsedTime')),
                _reason(package.get('lastRestrictionAttemptReason')),
                relative_path,
            ))
            rows += 1
        if rows:
            sources.append(file_found)

    return data_headers, data_list, '\n'.join(sources)
