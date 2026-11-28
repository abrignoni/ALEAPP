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
            "(https://android.googlesource.com/platform/frameworks/base/+/99b01a65cc4c104933788b3143285ab6bae65827/services/core/java/com/android/server/appop/LegacyHistoricalRegistry.java#838-853). "
            "On all 17 tested images, Samsung ones included, every element and attribute was one "
            "that writer writes. Not tested below Android 11. This is a different store from "
            "appOpsHistoryDb.py (the Android 16 app_op_history database), discreteNative.py "
            "(system/appops/discrete) and appOpsAccesses.py (appops_accesses.xml).\nEach file holds "
            "intervals (ops elements) of one maximum length, and its name is the interval series "
            "value base x (1 + m + ... + m^depth) (generateFile and "
            "computeGlobalIntervalBeginMillis, "
            "https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/services/core/java/com/android/server/appop/HistoricalRegistry.java#851 "
            "and #1652). With the defaults of 15 minutes and 10 "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/services/core/java/com/android/server/appop/HistoricalRegistry.java#158 "
            "and #161), 900000.xml holds intervals of up to 15 minutes and each longer name "
            "intervals of up to ten times longer. On the 16 tested zips all 104 intervals in "
            "900000.xml were 15 minutes long, and 142 of the 402 intervals in the longer files were "
            "shorter than their file's full length. When the platform moves counts into a longer "
            "interval it can split an interval's counts by time (spliceFromEnd, "
            "https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/services/core/java/com/android/server/appop/HistoricalRegistry.java#1660).\nWithin "
            "an interval the counts are per UID, package, attribution tag, op and st key. Package, "
            "UID and Attribution Tag are the na attributes of the pkg, uid and ftr elements; "
            "Attribution Tag is blank where the platform wrote none. Op Code is the op element's na. "
            "Access Count, Reject Count and Access Duration (ms) are the ac, rc and du attributes as "
            "stored, written only when greater than zero "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/services/core/java/com/android/server/appop/HistoricalRegistry.java#1609-1616), "
            "so a blank means none was recorded. The duration is milliseconds of elapsed realtime "
            "between an op's start and finish "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/services/core/java/com/android/server/appop/AppOpsService.java#1130-1139).\nApp "
            "State and Access Flags are decoded from the st na key, the uid state shifted left 31 "
            "bits with the op flags in the low 32 "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/android/app/AppOpsManager.java#813-814 "
            "and #844-851), using the UID_STATE and OP_FLAG constants, which are the same at "
            "android11 and android13; a value outside them is shown as its number, and none occurred "
            "on the tested images. Op Name is the name AOSP main gives the code in the table "
            "appOpsAccesses.py uses (codes 17 and 61 are spelled differently in android11 to "
            "android13). It is shown only when the code is below that release's "
            "AppOpsManager._NUM_OP (100 at android11, 116 at android12, 121 at android13, 136 at "
            "android14, 149 at android15 and 163 at android16; "
            "https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/core/java/android/app/AppOpsManager.java#1348 "
            "at android13) and the table holds it. The table has no name for 96 and ends at 155, so "
            "codes 156 to 162 on Android 16 are unnamed. The release comes from ro.build.version.sdk "
            "in system/build.prop or from the Android release in the usagestats version file "
            "(UsageStatsDatabase.getBuildFingerprint, "
            "https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/services/usage/java/com/android/server/usage/UsageStatsDatabase.java#421-425), "
            "whichever sits nearest to the history folder in the input, so each extraction in a "
            "combined input uses its own; a test tree holding an Android 11 and an Android 16 "
            "extraction named codes for each by its own release. With neither, or with a release "
            "older than Android 11, codes from 100 are left unnamed. All 17 tested images gave a "
            "release. Codes left unnamed: 100 on cookbook_a11 (Samsung, Android 11, 129 rows), 139 "
            "on russell_a14 (Pixel, Android 14, 48 rows), and six codes from 10008 to 10044 on "
            "kevin_pocox7_a15 (Xiaomi, 5,036 rows); the Op Code is shown.\nInterval Start and "
            "Interval End are computed by this artifact from the stored offsets and one file time. "
            "Each ops element stores beg and end as millisecond offsets. As the platform's reader "
            "does, the artifact adds the ov values of the shorter-named files "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/services/core/java/com/android/server/appop/HistoricalRegistry.java#1266 "
            "and #1288, #1312-1315) and the interval ends of the levels before the file, which sum "
            "to the file name minus the base "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/services/core/java/com/android/server/appop/HistoricalRegistry.java#1037). "
            "It subtracts the result from the modification time of the history file with the "
            "shortest name, the time the platform reads at boot as its last write "
            "(getLastPersistTimeMillisDLocked, "
            "https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/services/core/java/com/android/server/appop/HistoricalRegistry.java#921-942, "
            "used at #242). That anchoring is the artifact's own: the platform's query path works "
            "from an in-memory time "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/services/core/java/com/android/server/appop/HistoricalRegistry.java#470-471) "
            "and moves its window by one more base interval "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/services/core/java/com/android/server/appop/HistoricalRegistry.java#1012-1013), "
            "which is not applied here. Reference Time is that file time as the input recorded it, "
            "one value per history folder, and Start Offset Before Reference (ms) and End Offset "
            "Before Reference (ms) are the offsets. The times are therefore only as good as the file "
            "time the extraction kept. When the input recorded only a reading with no zone (a DOS "
            "time in a zip) the interval times and Reference Time are left blank and the reading is "
            "shown in Reference Time (no zone, as stored), which was blank on every tested public "
            "image; when the file names do not form one series (not seen on the tested images), no "
            "times or offsets are computed. A file the series skips adds no ov, as the platform's "
            "reader keeps going past it "
            "(https://android.googlesource.com/platform/frameworks/base/+/d27f9960456403533af0a0d5d9f14cf71c9c8cf6/services/core/java/com/android/server/appop/HistoricalRegistry.java#1229-1236), "
            "as on samsunga53_a14, which has no 9900000.xml. When a file cannot be read, or an ov is "
            "not a number, the files after it in the series get no offsets or times, and an interval "
            "without a numeric beg or end gets none; their counts are still reported. A test tree "
            "with one unreadable file gave the rows of the files after it blank offsets and times. "
            "On 15 of the 16 tested zips the smallest stored offset was under 8 seconds; on "
            "samsungs20_a13 it was about 37 minutes.\nChecked against the separately kept discrete op "
            "records, which carry their own times, on 14 zips. In 900000.xml 1,263 of 1,275 records "
            "fell in an interval that counts an access to the same UID, package and op (99.1%); with "
            "the times moved 15 minutes earlier 79.2% did, and 15 minutes later 88.6%. In "
            "9900000.xml 10,233 of 10,948 did (93.5%), and more did with the times moved later "
            "(96.3% at 150 minutes), so the placement of that file's intervals is not confirmed to "
            "better than one of its intervals; why was not established. In 99900000.xml 39,072 of "
            "40,044 did (97.6%) and shifts up to 150 minutes did not change that, so it does not "
            "test the placement. Longer files held 12 records or none. Over all files 50,580 of "
            "53,117 did (95.2%, 62.5% to 99.4% per image). On samsungs20_a13 125 of 286 did: its "
            "900000.xml agreed on 38 of 40 as placed, and its 9900000.xml on 87 of 245 as placed and "
            "235 of 285 with the times moved 150 minutes later. An interval is the platform's bucket "
            "for counts, not the time of any one access.\nAn op element with no st child gives no "
            "row. A Source Folder column is added when more than one history folder is read; a test "
            "tree with two copies of one image's folder gave each copy its rows under its folder."),
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
    # Offsets need every earlier file's ov: once a file in the series cannot be read, the
    # files after it get no offsets or times. A file the series skips is not read by the
    # platform either, which adds no ov for it (HistoricalRegistry.java#1229-1236 at android13-release).
    chain = depths is not None
    for name, path in sorted(files, key=lambda item: (depths or {}).get(item[0], item[0])):
        try:
            root = _root(path)
        except Exception as error:  # pylint: disable=broad-except
            root = None
            logfunc(f'App Ops History: could not read {os.path.basename(path)}: {error}')
        if root is None or root.tag != 'history':
            if chain:
                logfunc(f'App Ops History: {os.path.basename(path)} was not read, so the longer '
                        f'interval files after it get no offsets or times')
            chain = False
            continue
        shift = overflow + (name - base) if chain else None
        for ops in root.findall('ops'):
            stored_begin, stored_end = _int(ops.get('beg')), _int(ops.get('end'))
            if shift is None or stored_begin is None or stored_end is None:
                if shift is not None:
                    logfunc(f'App Ops History: an interval in {os.path.basename(path)} has no usable '
                            f'beg or end, so its offsets and times are left blank')
                begin = end = None
            else:
                begin, end = stored_begin + shift, stored_end + shift
            start_time = _ms_to_utc(reference_ms - end) if reference_ms is not None and end is not None else ''
            end_time = _ms_to_utc(reference_ms - begin) if reference_ms is not None and begin is not None else ''
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
                                    _ms_to_utc(reference_ms) if reference_ms is not None else '',
                                    reading,
                                    package.get('na', ''), uid.get('na', ''),
                                    op_name, code, attribution.get('na', ''),
                                    app_state, flags,
                                    state.get('ac', ''), state.get('rc', ''), state.get('du', ''),
                                    end if end is not None else '',
                                    begin if begin is not None else '',
                                ))
        stored_overflow = _int(root.get('ov')) if root.get('ov') is not None else 0
        if stored_overflow is None:
            if chain:
                logfunc(f'App Ops History: {os.path.basename(path)} has an unusable ov, so the '
                        f'longer interval files after it get no offsets or times')
            chain = False
        else:
            overflow += stored_overflow
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


def _nearest(paths, folder):
    """paths ordered by how much of folder's path they share, longest first, so a version
    file from the same extraction as a history folder is read before one from another."""
    def shared(path):
        try:
            return len(os.path.commonpath([path, folder]))
        except ValueError:
            return 0
    return sorted(paths, key=lambda path: (-shared(path), os.path.basename(path) != 'build.prop', path))


def _num_ops(folder, props, versions):
    """The op count below which codes are named for one history folder, and a log line saying
    where it came from. The build.prop or usagestats version file nearest to the folder that
    gives a version is used; at an equal distance build.prop is read first."""
    newest = max(NUM_OPS_BY_SDK.values())
    candidates = [(path, 'prop') for path in props] + [(path, 'version') for path in versions]
    ordered = _nearest([path for path, _kind in candidates], folder)
    kinds = dict(candidates)
    num_ops, basis = NUM_OPS_UNKNOWN, 'no Android version found'
    for path in ordered:
        if kinds[path] == 'prop':
            sdk = _sdk_level([path])
            if sdk is not None:
                num_ops = NUM_OPS_BY_SDK.get(sdk, newest if sdk > 36 else NUM_OPS_UNKNOWN)
                basis = f'SDK level {sdk} from build.prop'
                break
        else:
            release = _release([path])
            if release is not None:
                num_ops = NUM_OPS_BY_RELEASE.get(release, newest if release > 16 else NUM_OPS_UNKNOWN)
                basis = f'Android {release} from the usagestats version file'
                break
    logfunc(f'App Ops History: {basis}; op codes below {num_ops} are named')
    return num_ops


@artifact_processor
def app_ops_history_xml(context):
    data_headers = (
        ('Interval Start', 'datetime'),
        ('Interval End', 'datetime'),
        ('Reference Time', 'datetime'),
        'Reference Time (no zone, as stored)',
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
    )
    seeker = context.get_seeker()
    found = [str(path) for path in unique_files(context, keep_differing_views=True)]
    props = [path for path in found if os.path.basename(path) == 'build.prop' and not os.path.isdir(path)]
    versions = [path for path in found if os.path.basename(path) == 'version'
                and '/usagestats' in path.replace('\\', '/') and not os.path.isdir(path)]
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
        rows = _folder_rows(seeker, files, _num_ops(folder, props, versions))
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
