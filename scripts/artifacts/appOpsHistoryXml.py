__artifacts_v2__ = {
    "app_ops_history_xml": {
        "name": "App Ops History (history XML)",
        "description": "Aggregated app op access and rejection counts per package and op, in the time "
                       "intervals the platform keeps in system/appops/history, with the app state and "
                       "access flags each count was recorded under.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-28",
        "last_update_date": "2026-11-28",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": (
            "Reads the aggregated app op history that HistoricalRegistry keeps in "
            "system/appops/history, one row per st element. The element and attribute names "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/services/core/java/com/android/server/appop/HistoricalRegistry.java#821-836) "
            "are the same at the android11 to android15 release branches and in "
            "LegacyHistoricalRegistry at android16-release "
            "(https://android.googlesource.com/platform/frameworks/base/+/99b01a65cc4c104933788b3143285ab6bae65827/services/core/java/com/android/server/appop/LegacyHistoricalRegistry.java). "
            "On all 17 tested images, Samsung ones included, every element and attribute was one "
            "that writer writes. This is a different store from appOpsHistoryDb.py (the Android 16 "
            "app_op_history database), discreteNative.py (system/appops/discrete) and "
            "appOpsAccesses.py (appops_accesses.xml).\nEach file holds intervals (ops elements) at "
            "one granularity, and its name is the interval series value base x (1 + m + ... + "
            "m^depth) (generateFile and computeGlobalIntervalBeginMillis, "
            "https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/services/core/java/com/android/server/appop/HistoricalRegistry.java#851 "
            "and #1652), so 900000.xml holds 15-minute intervals and each longer name holds "
            "intervals ten times longer, with the defaults of 15 minutes and 10 "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/services/core/java/com/android/server/appop/HistoricalRegistry.java#158 "
            "and #161). Within an interval the counts are per UID, package, attribution tag, op and "
            "st key. Package, UID and Attribution Tag are the na attributes of the pkg, uid and ftr "
            "elements; Attribution Tag is blank where the platform wrote none. Op Code is the op "
            "element's na. Access Count, Reject Count and Access Duration (ms) are the ac, rc and du "
            "attributes as stored, written only when greater than zero "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/services/core/java/com/android/server/appop/HistoricalRegistry.java#1609-1616), "
            "so a blank means none was recorded.\nApp State and Access Flags are decoded from the st "
            "na key, the uid state shifted left 31 bits with the op flags in the low 32 "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/android/app/AppOpsManager.java#813-814 "
            "and #844-851), using the UID_STATE and OP_FLAG constants, which are the same at "
            "android11 and android13; a value outside them is shown as stored. Op Name is the AOSP "
            "name for the code from the table appOpsAccesses.py uses, shown only when the code is "
            "below that release's AppOpsManager._NUM_OP (100 at android11, 116 at android12, 121 at "
            "android13, 136 at android14, 149 at android15 and 163 at android16; "
            "https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/android/app/AppOpsManager.java#1348 "
            "at android13). The release comes from ro.build.version.sdk in system/build.prop, or "
            "else from the Android release in the usagestats version file "
            "(UsageStatsDatabase.getBuildFingerprint, "
            "https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/services/usage/java/com/android/server/usage/UsageStatsDatabase.java#421-425); "
            "with neither, codes from 100 are left unnamed. All 17 tested images gave a release. "
            "Codes left unnamed: 100 on cookbook_a11 (Samsung, Android 11, 129 rows), 139 on "
            "russell_a14 (Pixel, Android 14, 48 rows), and six codes from 10008 to 10044 on "
            "kevin_pocox7_a15 (Xiaomi, 5,036 rows); the Op Code is shown.\nInterval Start and "
            "Interval End follow the platform's own read path. An interval's stored beg and end are "
            "milliseconds back from the last write, after adding the ov values of the shorter-named "
            "files "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/services/core/java/com/android/server/appop/HistoricalRegistry.java#1266 "
            "and #1288, #1312-1315) and the end of the intervals before this file's series position, "
            "which is the file name minus the base "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/services/core/java/com/android/server/appop/HistoricalRegistry.java#1037 "
            "and #1086). The last write is taken, as the platform takes it at boot, as the "
            "modification time of the history file with the shortest name "
            "(getLastPersistTimeMillisDLocked, "
            "https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/services/core/java/com/android/server/appop/HistoricalRegistry.java#921-942, "
            "used at #242). Start Offset Before Reference (ms) and End Offset Before Reference (ms) "
            "are those offsets, and Reference Time is that file time as the input recorded it; it "
            "holds one value per history folder. The times are therefore only as good as the file "
            "time the extraction kept. When the input recorded only a reading with no zone (a DOS "
            "time in a zip) the interval times are left blank and the reading is shown in Reference "
            "Time (no zone, as stored), as on private_mobile_01; when the file names do not form one "
            "series, no times or offsets are computed. On the 16 tested zips the newest interval "
            "ended within 8 seconds of the reference on 15. Checked against the separately kept "
            "discrete op records, which carry their own times: on 14 images 50,580 of 53,117 records "
            "(95.2%, 62.5% to 99.4% per image) fell in an interval that counts an access to the same "
            "UID, package and op. On samsungs20_a13, whose history files all carry one identical "
            "time, 125 of 286 did, and agreement was best with the times moved 3 hours later; why "
            "was not established. An interval is the platform's bucket for counts, not the time of "
            "any one access.\nAn op element with no st child gives no row. A Source Folder column is "
            "added when more than one history folder is read; a test tree with two copies of one "
            "image's folder gave each copy its rows under its folder."),
        "paths": ('*/system/appops/history/*.xml', '*/system/build.prop',
                  '*/system/usagestats/*/version', '*/system_ce/*/usagestats/version'),
        "output_types": "standard",
        "artifact_icon": "shield",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 3440 rows",
            "anne_a15": "Android 15 | 12214 rows",
            "cookbook_a11": "Android 11 | 8338 rows",
            "falken_a326u_a13": "Android 13 | 3700 rows",
            "kevin_pocox7_a15": "Android 15 | 38947 rows",
            "pixel3_a11": "Android 11 | 8561 rows",
            "pixel3_a12": "Android 12 | 13953 rows",
            "pixel7a_a14": "Android 14 | 20730 rows",
            "russell_a14": "Android 14 | 22155 rows",
            "russell_pixel6a_a13": "Android 13 | 18378 rows",
            "s20fe_a13": "Android 13 | 2465 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | 4813 rows",
            "samsung_a166u_a16_known_20261117": "Android 16 | 5878 rows",
            "samsunga53_a14": "Android 14 | 3585 rows",
            "samsungs20_a13": "Android 13 | 6722 rows",
            "sharon_a13": "Android 13 | 12751 rows",
            "sharon_a14": "Android 14 | 16990 rows",
        },
    },
}

import os
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from scripts.artifacts.appOpsAccesses import APP_OP_NAMES, OP_FLAGS, UID_STATES
from scripts.artifacts.storagePathViews import union_view_rows, unique_files
from scripts.ilapfuncs import abxread, artifact_processor, checkabx, logfunc

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
# AppOpsManager._NUM_OP at each release branch, by SDK level; a code at or above it is not an
# op of that release and is left unnamed. 12L (SDK 32) takes the android12-release count.
NUM_OPS_BY_SDK = {30: 100, 31: 116, 32: 116, 33: 121, 34: 136, 35: 149, 36: 163}
# The same counts by Android release, for the release UsageStatsDatabase records in its version
# file when no build.prop gives the SDK level.
NUM_OPS_BY_RELEASE = {11: 100, 12: 116, 13: 121, 14: 136, 15: 149, 16: 163}
# Used when neither is known: the lowest count above.
NUM_OPS_UNKNOWN = 100
# AppOpsManager UID_STATE_OFFSET: the key packs the uid state above bit 31 and the flags below.
UID_STATE_OFFSET = 31
FLAGS_MASK = 0xFFFFFFFF


def _ms_to_utc(value):
    """A UTC datetime from Unix milliseconds, or '' when absent or out of range."""
    if value is None or value == '':
        return ''
    try:
        return _EPOCH + timedelta(milliseconds=value)
    except (OverflowError, ValueError, TypeError):
        return ''


def _int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _root(path):
    """The XML root of an ABX binary or a text XML file."""
    if checkabx(path):
        return abxread(path, False).getroot()
    return ET.parse(path).getroot()


def _usable(value):
    return isinstance(value, (int, float)) and value != 0 and value == value and abs(value) != float('inf')


def _recorded_mtime(seeker, path):
    """(UTC modification time in Unix seconds or None, reading with no zone or '') that the
    input recorded for a staged file.

    The staged copy's own time is not used: for a reading with no zone it is that reading
    placed in the examiner's time zone (see factory_reset.py).
    """
    infos = getattr(seeker, 'file_infos', None) or {}
    windows = str(path).replace('/', '\\')
    bare = windows.removeprefix('\\\\?\\')
    info = next((infos[name] for name in (str(path), windows, bare, '\\\\?\\' + bare)
                 if name in infos), None)
    times = getattr(info, 'times', None)
    modified = getattr(times, 'modified', None)
    if _usable(modified):
        return modified, ''
    reading = getattr(times, 'modified_no_zone', None)
    if reading:
        return None, reading
    modified = getattr(info, 'modification_date', None)
    return (modified if _usable(modified) else None), ''


def _sdk_level(paths):
    """ro.build.version.sdk from the first system/build.prop that carries it, or None."""
    for path in paths:
        try:
            with open(path, 'rb') as handle:
                for raw in handle:
                    line = raw.decode('utf-8', 'replace').strip()
                    if line.startswith('ro.build.version.sdk='):
                        value = _int(line.split('=', 1)[1].strip())
                        if value is not None:
                            return value
        except OSError as error:
            logfunc(f'App Ops History: could not read {os.path.basename(path)}: {error}')
    return None


def _depths(names):
    """{interval name: depth} when the names follow base * (1 + m + ... + m^depth) for one
    multiplier m, else None. Persistence.generateFile names each file this way."""
    base = min(names)
    if base <= 0:
        return None
    if len(names) == 1:
        return {base: 0}
    for multiplier in range(2, 101):
        sums = {}
        total, power, depth = 0, 1, 0
        largest = max(names)
        while base * total <= largest:
            total += power
            sums[base * total] = depth
            power *= multiplier
            depth += 1
        if all(name in sums for name in names):
            return {name: sums[name] for name in names}
    return None


def _decode_key(value):
    """(app state, access flags) from the st na key, values outside the AOSP sets as stored."""
    key = _int(value)
    if key is None:
        return ('' if value is None else value), ''
    state = key >> UID_STATE_OFFSET
    flags = key & FLAGS_MASK
    names = [name for bit, name in OP_FLAGS if flags & bit]
    remainder = flags & ~sum(bit for bit, _ in OP_FLAGS)
    if remainder:
        names.append(str(remainder))
    return UID_STATES.get(state, str(state)), ' | '.join(names)


def _folder_rows(seeker, files, num_ops):
    """The rows of one history folder. files is [(interval name, path)]."""
    names = [name for name, _path in files]
    depths = _depths(names)
    base = min(names)
    shortest = min(files, key=lambda item: (len(str(item[0])), item[0]))[1]
    reference, reading = _recorded_mtime(seeker, shortest) if depths is not None else (None, '')
    if depths is None:
        logfunc('App Ops History: the file names do not follow one interval series, so '
                'interval times are not computed')
    elif reference is None:
        logfunc('App Ops History: no zoned modification time was recorded for the history file '
                'with the shortest name, so interval times are not computed')
    reference_ms = reference * 1000 if reference is not None else None
    rows = []
    overflow = 0
    for name, path in sorted(files, key=lambda item: (depths or {}).get(item[0], item[0])):
        try:
            root = _root(path)
        except Exception as error:  # pylint: disable=broad-except
            logfunc(f'App Ops History: could not read {os.path.basename(path)}: {error}')
            continue
        if root is None or root.tag != 'history':
            continue
        shift = overflow + (name - base if depths is not None else 0)
        for ops in root.findall('ops'):
            begin = _int(ops.get('beg'), 0) + shift
            end = _int(ops.get('end'), 0) + shift
            start_time = _ms_to_utc(reference_ms - end) if reference_ms is not None else ''
            end_time = _ms_to_utc(reference_ms - begin) if reference_ms is not None else ''
            for uid in ops.findall('uid'):
                for package in uid.findall('pkg'):
                    for attribution in package.findall('ftr'):
                        for op in attribution.findall('op'):
                            code = op.get('na', '')
                            number = _int(code)
                            op_name = (APP_OP_NAMES.get(number, '')
                                       if number is not None and 0 <= number < num_ops else '')
                            for state in op.findall('st'):
                                app_state, flags = _decode_key(state.get('na'))
                                rows.append((
                                    start_time, end_time,
                                    package.get('na', ''), uid.get('na', ''),
                                    op_name, code, attribution.get('na', ''),
                                    app_state, flags,
                                    state.get('ac', ''), state.get('rc', ''), state.get('du', ''),
                                    end if depths is not None else '',
                                    begin if depths is not None else '',
                                    _ms_to_utc(reference_ms) if reference_ms is not None else '',
                                    reading,
                                ))
        overflow += _int(root.get('ov'), 0)
    return rows


def _release(paths):
    """The Android release from a usagestats version file, or None. Its second line is
    Build.VERSION.RELEASE;CODENAME;INCREMENTAL (UsageStatsDatabase.getBuildFingerprint)."""
    for path in paths:
        try:
            with open(path, 'rb') as handle:
                lines = handle.read(4096).decode('utf-8', 'replace').splitlines()
        except OSError as error:
            logfunc(f'App Ops History: could not read {os.path.basename(path)}: {error}')
            continue
        if len(lines) >= 2 and ';' in lines[1]:
            major = _int(lines[1].split(';', 1)[0].strip().split('.', 1)[0])
            if major is not None:
                return major
    return None


@artifact_processor
def app_ops_history_xml(context):
    data_headers = (
        ('Interval Start', 'datetime'),
        ('Interval End', 'datetime'),
        'Package',
        'UID',
        'Op Name',
        'Op Code',
        'Attribution Tag',
        'App State',
        'Access Flags',
        ('Access Count', 'number'),
        ('Reject Count', 'number'),
        ('Access Duration (ms)', 'number'),
        ('Start Offset Before Reference (ms)', 'number'),
        ('End Offset Before Reference (ms)', 'number'),
        ('Reference Time', 'datetime'),
        'Reference Time (no zone, as stored)',
    )
    seeker = context.get_seeker()
    found = [str(path) for path in unique_files(context, keep_differing_views=True)]
    props = [path for path in found if os.path.basename(path) == 'build.prop' and not os.path.isdir(path)]
    sdk = _sdk_level(props)
    newest = max(NUM_OPS_BY_SDK.values())
    if sdk is not None:
        num_ops = NUM_OPS_BY_SDK.get(sdk, newest if sdk > 36 else NUM_OPS_UNKNOWN)
        basis = f'SDK level {sdk} from build.prop'
    else:
        versions = [path for path in found if os.path.basename(path) == 'version'
                    and '/usagestats' in path.replace('\\', '/') and not os.path.isdir(path)]
        release = _release(versions)
        if release is not None:
            num_ops = NUM_OPS_BY_RELEASE.get(release, newest if release > 16 else NUM_OPS_UNKNOWN)
            basis = f'Android {release} from the usagestats version file'
        else:
            num_ops = NUM_OPS_UNKNOWN
            basis = 'no Android version found'
    logfunc(f'App Ops History: {basis}; op codes below {num_ops} are named')
    folders = {}
    for path in found:
        if os.path.isdir(path) or not path.endswith('.xml') or '/appops/history/' not in path.replace('\\', '/'):
            continue
        name = _int(os.path.basename(path)[:-4])
        if name is None:
            continue
        folders.setdefault(os.path.dirname(path), []).append((name, path))
    file_rows = []
    sources = []
    for folder in sorted(folders):
        files = folders[folder]
        rows = _folder_rows(seeker, files, num_ops)
        relative = context.get_relative_path(min(files)[1])
        if len(folders) > 1:
            rows = [row + (os.path.dirname(relative),) for row in rows]
        file_rows.append((folder, rows))
        sources.extend(context.get_relative_path(path) for _name, path in sorted(files))
    if len(folders) > 1:
        data_headers += ('Source Folder',)
        data_list = union_view_rows(context, file_rows, ignore=(len(data_headers) - 1,))
    else:
        data_list = union_view_rows(context, file_rows)
    return data_headers, data_list, '\n'.join(sources)
