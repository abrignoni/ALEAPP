__artifacts_v2__ = {
    "battery_usage_stats_snapshots": {
        "name": "Battery Usage Stats Snapshots",
        "description": "Battery usage sessions the platform saved in system/battery-usage-stats before "
                       "resetting its battery statistics, with the session start and end times and the "
                       "battery discharged in it.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-28",
        "last_update_date": "2026-11-28",
        "requirements": "none",
        "category": "Device Activity",
        "notes": (
            "Reads the .bus files in system/battery-usage-stats. BatteryUsageStatsStore writes one "
            "when the platform is about to reset its battery statistics, holding the statistics "
            "collected since the previous reset "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/com/android/internal/os/BatteryUsageStatsStore.java#111), "
            "and names it after the session end time "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/com/android/internal/os/BatteryUsageStatsStore.java#271). "
            "It keeps about 100 KB of them and deletes the oldest past that "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/com/android/internal/os/BatteryUsageStatsStore.java#71 "
            "and #309), so the folder holds the most recent sessions, not the device's whole "
            "history. The store was read at the android12, 13 and 14 release branches; the write "
            "trigger, file naming, ABX format and size cap are the same in all three. At android15 "
            "and 16 only the XML writer classes were read. The 10 tested images that carried the "
            "folder were Android 12 to 14; the registered Android 15 and later zip extractions "
            "had no .bus files. On all 10, Samsung ones included, every element and attribute name "
            "was one the AOSP writers at android12 to android16 write. The field meanings below are "
            "AOSP's; Samsung's framework code was not read. The file is ABX binary XML "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/com/android/internal/os/BatteryUsageStatsStore.java#278). "
            "On samsungs20_a13 all 7 files were text XML, and none of the 126 .xml files under "
            "userdata/system on that image was ABX. Their XML declaration is not the one AOSP "
            "FastXmlSerializer writes "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/com/android/internal/util/FastXmlSerializer.java#370); "
            "how the extraction came to hold them in that form was not established, and they are "
            "read as given.\nOne row per file. Session Start is start_timestamp, the wall clock time "
            "of the battery statistics reset that began the session, and Session End is "
            "end_timestamp, when the snapshot was taken "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/android/os/BatteryUsageStats.java#196 "
            "and #204); both are Unix milliseconds rendered in UTC. The file name equalled the end "
            "time on all 44 tested files, and on the 9 tested images with more than one file each "
            "session began 2 to 56 milliseconds after the end of the one before it (34 pairs). "
            "Session Duration (ms) is duration, which the platform notes can differ from end minus "
            "start when a snapshot joins non-contiguous sessions "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/android/os/BatteryUsageStats.java#214); "
            "it equalled end minus start on all 44. Discharge (%) and the two Discharged bounds are "
            "discharge_pct, discharge_lower and discharge_upper, the battery charge drained in the "
            "session as a percentage and as a range in mAh "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/android/os/BatteryUsageStats.java#239 "
            "and #247); they were 0 on every session of two images, pixel7a_a14 and samsunga53_a14. "
            "Discharge Duration (ms) is discharge_duration, the time the battery was discharging "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/android/os/BatteryUsageStats.java#254), "
            "written from Android 13 and blank on Android 12. On s20fe_a13 it was 0 in all 4 "
            "sessions while Discharge (%) was 1 to 4. Device Consumed Power (mAh) is the power of "
            "the device-scope aggregate element, the total battery charge drained since the reset, "
            "in mAh "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/android/os/BatteryUsageStats.java#222). "
            "Battery Capacity (mAh) is battery_capacity, in mAh "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/android/os/BatteryUsageStats.java#230), "
            "as the reader returns it. UIDs Recorded counts the uid elements, which are the rows of "
            "Battery Usage Stats by App for the session. The columns from Session Duration to UIDs "
            "Recorded are typed as numbers, so LAVA sorts them as numbers and shows a whole value "
            "written with a trailing .0 without it.\nNot shown: the per-component power "
            "breakdowns, the all-apps scope aggregate (scope 1), the per-user consumers (none was "
            "present in the 44 tested files), and the battery and charge time remaining estimates. A "
            "Source File column is added when files are read from more than one folder. A test tree "
            "holding two copies of one image's folder gave each copy its own rows under its path."),
        "paths": ('*/system/battery-usage-stats/*.bus',),
        "output_types": "standard",
        "artifact_icon": "battery-charging",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 4 rows",
            "falken_a326u_a13": "Android 13 | 5 rows",
            "pixel3_a12": "Android 12 | 3 rows",
            "pixel7a_a14": "Android 14 | 5 rows",
            "russell_pixel6a_a13": "Android 13 | 3 rows",
            "s20fe_a13": "Android 13 | 4 rows",
            "samsunga53_a14": "Android 14 | 10 rows",
            "samsungs20_a13": "Android 13 | 7 rows",
            "sharon_a13": "Android 13 | 1 row",
            "sharon_a14": "Android 14 | 2 rows",
            "cookbook_a11": "Android 11 | 0 rows, no battery-usage-stats folder",
        },
    },
    "battery_usage_stats_apps": {
        "name": "Battery Usage Stats by App",
        "description": "Per-UID time in foreground and background in each battery usage session saved in "
                       "system/battery-usage-stats, with the process name the platform recorded as the "
                       "UID's highest drain.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-28",
        "last_update_date": "2026-11-28",
        "requirements": "none",
        "category": "Device Activity",
        "notes": (
            "Reads the .bus files in system/battery-usage-stats. BatteryUsageStatsStore writes one "
            "when the platform is about to reset its battery statistics, holding the statistics "
            "collected since the previous reset "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/com/android/internal/os/BatteryUsageStatsStore.java#111), "
            "and names it after the session end time "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/com/android/internal/os/BatteryUsageStatsStore.java#271). "
            "It keeps about 100 KB of them and deletes the oldest past that "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/com/android/internal/os/BatteryUsageStatsStore.java#71 "
            "and #309), so the folder holds the most recent sessions, not the device's whole "
            "history. The store was read at the android12, 13 and 14 release branches; the write "
            "trigger, file naming, ABX format and size cap are the same in all three. At android15 "
            "and 16 only the XML writer classes were read. The 10 tested images that carried the "
            "folder were Android 12 to 14; the registered Android 15 and later zip extractions "
            "had no .bus files. On all 10, Samsung ones included, every element and attribute name "
            "was one the AOSP writers at android12 to android16 write. The field meanings below are "
            "AOSP's; Samsung's framework code was not read. The file is ABX binary XML "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/com/android/internal/os/BatteryUsageStatsStore.java#278). "
            "On samsungs20_a13 all 7 files were text XML, and none of the 126 .xml files under "
            "userdata/system on that image was ABX. Their XML declaration is not the one AOSP "
            "FastXmlSerializer writes "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/com/android/internal/util/FastXmlSerializer.java#370); "
            "how the extraction came to hold them in that form was not established, and they are "
            "read as given.\nOne row per uid element. The writer writes a UID only when its consumed "
            "power is not zero "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/android/os/UidBatteryConsumer.java#150), "
            "so a UID that ran but drew no estimated power is absent. Session Start and Session End "
            "are the session's times from the file, as in Battery Usage Stats Snapshots. Android "
            "User is the UID divided by 100,000 (UserHandle.getUserId, "
            "https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/android/os/UserHandle.java#280), "
            "blank for a negative UID.\nTime in Foreground (ms) and Time in Background (ms) are "
            "time_in_foreground and time_in_background. At android12 to 14, "
            "BatteryUsageStatsProvider sums them from the UID's process state times since the reset. "
            "Foreground is the shorter of the top-state time and the foreground-activity time, plus "
            "the foreground process state time; on Android 12 and 13 it also adds the "
            "foreground-service state time "
            "(https://android.googlesource.com/platform/frameworks/base/+/c53e71dc397de7486c9a8899f71598c3c3a18d44/core/java/com/android/internal/os/BatteryUsageStatsProvider.java#203, "
            "https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/com/android/internal/os/BatteryUsageStatsProvider.java#283), "
            "and on Android 14 that time is counted in background instead "
            "(https://android.googlesource.com/platform/frameworks/base/+/6e47c7075b91983ae501114425ea25e6df7690c8/services/core/java/com/android/server/power/stats/BatteryUsageStatsProvider.java#271 "
            "and #292). Foreground time is therefore not screen or interaction time. In 34 of the 44 "
            "tested sessions three or more UIDs, app UIDs among them, held one identical non-zero "
            "foreground value (up to 32 UIDs in one session), and in all 26 of those sessions whose "
            "Discharge Duration was above 0 that value equalled the Discharge Duration; why was not "
            "established. Time in Foreground Service (ms) is time_in_foreground_service, which the "
            "android15 writer adds "
            "(https://android.googlesource.com/platform/frameworks/base/+/cc8bb19595c661f5cf42f330457000e643c67d1b/core/java/android/os/UidBatteryConsumer.java#184). "
            "The android16 writer writes none of the three time attributes "
            "(https://android.googlesource.com/platform/frameworks/base/+/99b01a65cc4c104933788b3143285ab6bae65827/core/java/android/os/UidBatteryConsumer.java#201), "
            "so all three columns would be blank there. Neither release was exercised, and Time in "
            "Foreground Service was blank on every tested row. The three time columns are typed as "
            "numbers. LAVA sorts Time in Foreground and Time in Background as numbers; Time in "
            "Foreground Service held no value on any tested row, so its sorting was not "
            "exercised.\nHighest Drain Process is "
            "highest_drain_package. Despite the name, at android12 to 14 CpuPowerCalculator fills it "
            "with the name of the UID's process with the highest sum of user CPU time, system CPU "
            "time and foreground time, preferring a name that does not begin with * "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/com/android/internal/os/CpuPowerCalculator.java#241-263), "
            "so it can be a package name or a native process name. It is blank when the platform "
            "recorded none.\nNot shown: the per-component power and usage duration values. A Source "
            "File column is added when files are read from more than one folder. A test tree holding "
            "two copies of one image's folder gave each copy its own rows under its path."),
        "paths": ('*/system/battery-usage-stats/*.bus',),
        "output_types": "standard",
        "artifact_icon": "battery-charging",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 413 rows",
            "falken_a326u_a13": "Android 13 | 411 rows",
            "pixel3_a12": "Android 12 | 447 rows",
            "pixel7a_a14": "Android 14 | 416 rows",
            "russell_pixel6a_a13": "Android 13 | 293 rows",
            "s20fe_a13": "Android 13 | 485 rows",
            "samsunga53_a14": "Android 14 | 400 rows",
            "samsungs20_a13": "Android 13 | 414 rows",
            "sharon_a13": "Android 13 | 166 rows",
            "sharon_a14": "Android 14 | 347 rows",
            "cookbook_a11": "Android 11 | 0 rows, no battery-usage-stats folder",
        },
    },
}

import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from scripts.artifacts.storagePathViews import union_view_rows, unique_files
from scripts.ilapfuncs import abxread, artifact_processor, checkabx, logfunc

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
# BatteryUsageStats.AGGREGATE_BATTERY_CONSUMER_SCOPE_DEVICE
SCOPE_DEVICE = '0'
# UserHandle.PER_USER_RANGE
PER_USER_RANGE = 100000


def _ms_to_utc(value):
    """A UTC datetime from Unix milliseconds, or '' for an absent, zero or unreadable value."""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    try:
        return _EPOCH + timedelta(milliseconds=value)
    except (OverflowError, ValueError):
        return ''


def _root(path):
    """The XML root of an ABX binary or a text XML file."""
    if checkabx(path):
        return abxread(path, False).getroot()
    return ET.parse(path).getroot()


def _bus_files(context):
    """(path, relative path, root) for each readable snapshot file, once per storage view."""
    found = []
    for path in unique_files(context, keep_differing_views=True):
        path = str(path)
        if os.path.isdir(path) or not path.endswith('.bus'):
            continue
        try:
            root = _root(path)
        except Exception as error:  # pylint: disable=broad-except
            logfunc(f'Battery Usage Stats: could not read {os.path.basename(path)}: {error}')
            continue
        if root is None or root.tag != 'battery_usage_stats':
            logfunc(f'Battery Usage Stats: {os.path.basename(path)} has no battery_usage_stats element')
            continue
        found.append((path, context.get_relative_path(path), root))
    return found


def _with_source(context, found, file_rows, headers):
    """The rows joined across copies, with a Source File column when more than one folder is read."""
    folders = {os.path.dirname(path) for path, _relative, _root in found}
    if len(folders) > 1:
        headers += ('Source File',)
        relatives = {path: relative for path, relative, _root in found}
        file_rows = [(path, [row + (relatives[path],) for row in rows]) for path, rows in file_rows]
        return headers, union_view_rows(context, file_rows, ignore=(len(headers) - 1,))
    return headers, union_view_rows(context, file_rows)


@artifact_processor
def battery_usage_stats_snapshots(context):
    data_headers = (
        ('Session Start', 'datetime'),
        ('Session End', 'datetime'),
        ('Session Duration (ms)', 'number'),
        ('Discharge (%)', 'number'),
        ('Discharged Lower Bound (mAh)', 'number'),
        ('Discharged Upper Bound (mAh)', 'number'),
        ('Discharge Duration (ms)', 'number'),
        ('Device Consumed Power (mAh)', 'number'),
        ('Battery Capacity (mAh)', 'number'),
        ('UIDs Recorded', 'number'),
    )
    found = _bus_files(context)
    file_rows = []
    for path, _relative, root in found:
        device_power = ''
        for aggregate in root.findall('aggregate'):
            if aggregate.get('scope') == SCOPE_DEVICE:
                device_power = aggregate.get('power', '')
        row = (
            _ms_to_utc(root.get('start_timestamp')),
            _ms_to_utc(root.get('end_timestamp')),
            root.get('duration', ''),
            root.get('discharge_pct', ''),
            root.get('discharge_lower', ''),
            root.get('discharge_upper', ''),
            root.get('discharge_duration', ''),
            device_power,
            root.get('battery_capacity', ''),
            len(root.findall('uid')),
        )
        file_rows.append((path, [row]))
    data_headers, data_list = _with_source(context, found, file_rows, data_headers)
    return data_headers, data_list, '\n'.join(relative for _path, relative, _root in found)


@artifact_processor
def battery_usage_stats_apps(context):
    data_headers = (
        ('Session Start', 'datetime'),
        ('Session End', 'datetime'),
        'UID',
        'Android User',
        'Highest Drain Process',
        ('Time in Foreground (ms)', 'number'),
        ('Time in Background (ms)', 'number'),
        ('Time in Foreground Service (ms)', 'number'),
    )
    found = _bus_files(context)
    file_rows = []
    for path, _relative, root in found:
        start = _ms_to_utc(root.get('start_timestamp'))
        end = _ms_to_utc(root.get('end_timestamp'))
        rows = []
        for consumer in root.findall('uid'):
            uid = consumer.get('uid', '')
            try:
                user = int(uid) // PER_USER_RANGE if int(uid) >= 0 else ''
            except ValueError:
                user = ''
            rows.append((
                start, end, uid, user,
                consumer.get('highest_drain_package', ''),
                consumer.get('time_in_foreground', ''),
                consumer.get('time_in_background', ''),
                consumer.get('time_in_foreground_service', ''),
            ))
        file_rows.append((path, rows))
    data_headers, data_list = _with_source(context, found, file_rows, data_headers)
    return data_headers, data_list, '\n'.join(relative for _path, relative, _root in found)
