__artifacts_v2__ = {
    "appops_modes": {
        "name": "App Ops Permission Modes",
        "description": "App op modes stored in system/appops.xml, with the op, the mode, and the package or UID the "
                       "mode is stored against.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Permissions",
        "notes": "A row is an op element in system/appops.xml carrying a stored mode, with the package or the "
                 "UID that mode is stored against. Two shapes are read. From Android 14 the file holds uid "
                 "elements directly under the root and package modes under a user element per Android user, "
                 "and it holds no access records; that shape declares v=\"4\". Android 13 and earlier hold uid "
                 "elements under the root as well, and package modes under pkg then uid, beside the access "
                 "records; that shape declares v=\"1\". Measured across the 39 registered Android corpora on "
                 "2026-09-06: 16 carried the file, 5 of them the v=\"4\" shape on the Android 14 and 15 images "
                 "and 11 the v=\"1\" shape on the Android 10 to 13 images. Reference: Android Open Source "
                 "Project, AppOpsCheckingServiceImpl.writeState, "
                 "https://android.googlesource.com/platform/frameworks/base/+/4e43ad12e1b211f15152e9c5b16b0fe88e6b93f3/services/core/java/com/android/server/appop/AppOpsCheckingServiceImpl.java#389 "
                 "for the v=\"4\" shape, and AppOpsService.writeState, "
                 "https://android.googlesource.com/platform/frameworks/base/+/0d3ff311e6e80dee7fe88a2a2cfa272ce231c3c6/services/core/java/com/android/server/appop/AppOpsService.java#5135 "
                 "for the v=\"1\" shape.\n"
                 "The platform stores a mode only when it differs from that op's default mode, and removes the "
                 "entry when the mode is set back to the default. A row therefore records an op whose mode "
                 "differed from the platform default when the file was last written. The absence of a row is "
                 "not evidence that an op was denied or that it was never set: it is the op's default mode "
                 "being in effect. Nothing in the file records what set a mode, or when. Reference: setUidMode "
                 "and setPackageMode, "
                 "https://android.googlesource.com/platform/frameworks/base/+/4e43ad12e1b211f15152e9c5b16b0fe88e6b93f3/services/core/java/com/android/server/appop/AppOpsCheckingServiceImpl.java#191 "
                 "and #245, which delete the entry when the new mode equals opToDefaultMode; and for the v=\"1\" "
                 "shape the writer's own guard, "
                 "https://android.googlesource.com/platform/frameworks/base/+/0d3ff311e6e80dee7fe88a2a2cfa272ce231c3c6/services/core/java/com/android/server/appop/AppOpsService.java#5216, "
                 "which emits the m attribute only when the mode differs from opToDefaultMode.\n"
                 "Mode is the AppOpsManager mode constant, and a value outside that set is reported as stored. "
                 "Across the tested images the stored modes were IGNORED on 12,264 rows, FOREGROUND on 1,208, "
                 "ALLOWED on 568 and ERRORED on 6; DEFAULT did not appear on any row and no value fell outside "
                 "the set. Reference: MODE_ALLOWED, MODE_IGNORED, MODE_ERRORED, MODE_DEFAULT and "
                 "MODE_FOREGROUND, "
                 "https://android.googlesource.com/platform/frameworks/base/+/4e43ad12e1b211f15152e9c5b16b0fe88e6b93f3/core/java/android/app/AppOpsManager.java#402.\n"
                 "Mode Stored Against says which of the two the file recorded, and with it how Package Name "
                 "was obtained. Package means the file stores the mode against a package name, which is the "
                 "name in the row: 261 rows. UID means the file stores it against a UID and the package name "
                 "is resolved here from system/packages.xml: 13,785 rows. That lookup uses identity the file "
                 "records, the userId attribute of a package element, or the name of the shared-user element "
                 "when several packages share the uid, in which case the name is a shared user id such as "
                 "android.uid.system rather than a package. A UID is split into an Android user and an app id "
                 "first, "
                 "https://android.googlesource.com/platform/frameworks/base/+/4e43ad12e1b211f15152e9c5b16b0fe88e6b93f3/core/java/android/os/UserHandle.java#47. "
                 "Package Name is blank when nothing matched: 1,349 of 14,046 rows across 334 distinct UIDs. "
                 "1,302 of those rows and 300 of those UIDs are on one image whose packages.xml is neither "
                 "readable XML nor ABX, which the run log reports and which leaves that image's UID rows "
                 "unnamed. On the other 2 images it is 47 rows across 34 UIDs that the extraction's "
                 "packages.xml holds no record for; whether such a UID belonged to an app that had been "
                 "removed was not established here.\n"
                 "Android User is the userId attribute of the user element on the v=\"4\" shape, and is derived "
                 "from the stored UID on every other row. It is a single value on an image with one Android "
                 "user and varies where the device has more than one: 5 of the 16 images carried a second one, "
                 "and across the tested images the value was 0 on 12,153 rows, 10 on 1,239 and 150 on 654.\n"
                 "Permission is the AOSP short name for the Op Code, taken from the ordered "
                 "AppOpsManager.sAppOpInfos table where the array index is the op code. Codes the table does "
                 "not define are left unnamed and the number stays in Op Code. No row needed that: the 59 "
                 "distinct codes seen across the tested images run from 0 to 133 and the table names every "
                 "one. The extraction of that table asserted that the number of entries equalled the number of "
                 "Builder occurrences in the array, because a pattern that skips an entry shifts every later "
                 "name; index 96 is a retired placeholder that carries an empty name and is left unmapped. The "
                 "codes are the same in that table at the android-14.0.0_r1 and android-15.0.0_r1 tags and at "
                 "main, so the names do not depend on the release. Reference: "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/core/java/android/app/AppOpsManager.java#2685.\n"
                 "Three artifacts already read this file and none of them reports a mode. appops.py declares "
                 "two that read the st access records under pkg then uid then op, and appopSetupWiz.py reads "
                 "the same records for one package. The v=\"4\" shape holds no st element and no pkg element "
                 "under the root, so those artifacts return nothing from it. Measured on the same runs: App "
                 "Ops Permissions reported 0 rows on all 5 images carrying the v=\"4\" shape, where this "
                 "artifact reported 5,359, and reported rows on all 11 images carrying the v=\"1\" shape, where "
                 "this artifact reports the modes those artifacts do not.\n"
                 "What this artifact does not cover. It does not read system/appops_accesses.xml, which is "
                 "where Android 14 and later keep the access and rejection records and which appOpsAccesses.py "
                 "reads, nor system/appops/discrete, which discreteNative.py reads, nor system/appops/history, "
                 "which nothing reads. It also does not read the store the modes move to. system/appops.xml is "
                 "absent on 23 of the 39 corpora: on 18 of the 19 Android 15 images, on the Android 16 and "
                 "Android 17 images, and on three partial extractions carrying no system files at all. AOSP "
                 "carries a helper described as the provider of legacy app-ops data for the new permission "
                 "subsystem, which reads this file and hands its contents on, "
                 "https://android.googlesource.com/platform/frameworks/base/+/4e43ad12e1b211f15152e9c5b16b0fe88e6b93f3/services/core/java/com/android/server/appop/AppOpMigrationHelperImpl.java#35. "
                 "On one of those images the modes were found in "
                 "misc_de/<user>/apexdata/com.android.permission/access.abx, in its app-id-app-ops and "
                 "package-app-ops sections, which no ALEAPP artifact reads. An image carrying both files would "
                 "settle whether the two agree; none of the tested corpora carries both.\n"
                 "Two smaller limits. The path pattern is tolerant, so a second copy of the file in an "
                 "extraction is read as well; rows identical between copies are reported once with both paths "
                 "in Source File, and copies that disagree on a mode produce a row each. None of the tested "
                 "corpora carried more than one copy, so that behaviour was exercised on a constructed tree "
                 "and not on real evidence. And on 6 of the 16 images, all Samsung, the uid op elements carry "
                 "a u attribute that the AOSP writer does not write; it has no documented meaning and is not "
                 "reported.",
        "paths": ('*/system/appops.xml', '*/system/packages.xml'),
        "output_types": "standard",
        "artifact_icon": "shield",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 905 rows",
            "anne_a15": "Android 15 | 990 rows",
            "cookbook_a11": "Android 11 | 911 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 0 rows",
            "emu_a15_oss_v10": "Android 15 | 0 rows",
            "emu_a15_oss_v11": "Android 15 | 0 rows",
            "emu_a15_oss_v12": "Android 15 | 0 rows",
            "emu_a15_oss_v13": "Android 15 | 0 rows",
            "emu_a15_oss_v14": "Android 15 | 0 rows",
            "emu_a15_oss_v15": "Android 15 | 0 rows",
            "emu_a15_oss_v16": "Android 15 | 0 rows",
            "emu_a15_oss_v17": "Android 15 | 0 rows",
            "emu_a15_oss_v2": "Android 15 | 0 rows",
            "emu_a15_oss_v3": "Android 15 | 0 rows",
            "emu_a15_oss_v4": "Android 15 | 0 rows",
            "emu_a15_oss_v5": "Android 15 | 0 rows",
            "emu_a15_oss_v6": "Android 15 | 0 rows",
            "emu_a15_oss_v7": "Android 15 | 0 rows",
            "emu_a15_oss_v8": "Android 15 | 0 rows",
            "emu_a15_oss_v9": "Android 15 | 0 rows",
            "falken_a326u_a13": "Android 13 | 577 rows",
            "galaxys10_a10": "Android 10 | 207 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "hc_pixel8pro_a17_ail": "0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "pixel3_a11": "Android 11 | 727 rows",
            "pixel3_a12": "Android 12 | 763 rows",
            "pixel7a_a14": "Android 14 | 853 rows",
            "russell_a14": "Android 14 | 1179 rows",
            "russell_pixel6a_a13": "Android 13 | 978 rows",
            "s20fe_a13": "Android 13 | 580 rows",
            "samsunga53_a14": "Android 14 | 886 rows",
            "samsungs20_a13": "Android 13 | 1318 rows",
            "sharon_a13": "Android 13 | 1211 rows",
            "sharon_a14": "Android 14 | 1451 rows",
            "userb2_a13": "Android 13 | 510 rows",
        },
    },
}

import os
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import abxread, artifact_processor, checkabx, logfunc

# The op code to AOSP short name table and the mode constants are shared with appOpsAccesses,
# which reads the other half of what used to be one file, so the two artifacts cannot drift apart
# on the same vocabulary. Both were re-derived here from the ordered AppOpsManager.sAppOpInfos
# array at main 1cdfff555f4a21f71ccc978290e2e212e2f8b168, asserting that the number of entries
# equalled the number of 'new AppOpInfo.Builder(' occurrences in the array, because a pattern that
# skips one entry shifts every later name, and the result matched the shared table on all 155
# entries. Index 96 is a retired placeholder that carries an empty name and is left unmapped.
from scripts.artifacts.appOpsAccesses import APP_OP_NAMES, OP_MODES

# UserHandle.PER_USER_RANGE. getUserId is uid / PER_USER_RANGE and getAppId is uid % PER_USER_RANGE.
PER_USER_RANGE = 100000


def _root(path):
    """The XML root, reading ABX binary XML or plain XML."""
    if checkabx(path):
        try:
            return abxread(path, False).getroot()
        except Exception:  # pylint: disable=broad-except
            return abxread(path, True).getroot()
    return ET.parse(path).getroot()


def _op_name(code):
    """The AOSP short name for an op code, or '' when the table does not define it."""
    try:
        return APP_OP_NAMES.get(int(code), '')
    except (TypeError, ValueError):
        return ''


def _mode_name(value):
    """The AppOpsManager mode name, or the value as stored when it is outside the AOSP set."""
    if value is None:
        return ''
    return OP_MODES.get(str(value), str(value))


def _split_uid(value):
    """(android user, app id) from a uid, or (None, None) when it is not an integer."""
    try:
        uid = int(value)
    except (TypeError, ValueError):
        return None, None
    return uid // PER_USER_RANGE, uid % PER_USER_RANGE


def _uid_names(files):
    """(app id to the name recorded for it in packages.xml, the files that were read).

    A package element carries its own userId; a set of packages sharing a uid carries
    sharedUserId instead, and the uid is named once by a shared-user element whose name is
    the shared user id rather than a package. Both are identity the file records, not a
    correlation. A uid several packages hold privately would join their names, which no
    tested image produced.
    """
    private = {}
    shared = {}
    read = []
    for file_found in files:
        try:
            root = _root(file_found)
        except Exception as error:  # pylint: disable=broad-except
            logfunc(f'App Ops Permission Modes: could not read {os.path.basename(file_found)}: {error}')
            continue
        read.append(file_found)
        for element in root.iter('shared-user'):
            _, app_id = _split_uid(element.get('userId'))
            name = element.get('name')
            if app_id is not None and name:
                shared.setdefault(app_id, name)
        for element in root.iter('package'):
            _, app_id = _split_uid(element.get('userId'))
            name = element.get('name')
            if app_id is not None and name:
                private.setdefault(app_id, set()).add(name)
    names = dict(shared)
    for app_id, name_set in private.items():
        if app_id not in names:
            names[app_id] = ' | '.join(sorted(name_set))
    return names, read


def _mode_ops(element):
    """The op children of an element that carry a stored mode."""
    return [op for op in element if op.tag == 'op' and op.get('m') is not None]


@artifact_processor
def appops_modes(context):
    data_headers = (
        'Package Name',
        'UID',
        'Android User',
        'Permission',
        'Op Code',
        'Mode',
        'Mode Stored Against',
        'Source File',
    )
    # The stored record, minus the file it came from, to the files carrying it. The platform
    # writes one op element per scope and op, so a key repeats only when an extraction holds
    # more than one copy of the file. Keyed this way a repeat costs no extra row while two
    # copies that disagree on a mode still produce one row each. Insertion order is kept, so
    # rows stay in the order the file stores them.
    rows = {}
    sources = []

    files_found = sorted({str(f) for f in context.get_files_found()})
    appops_files = []
    packages_files = []
    for file_found in files_found:
        if os.path.isdir(file_found):
            continue
        base = os.path.basename(file_found)
        if base == 'appops.xml':
            appops_files.append(file_found)
        elif base == 'packages.xml':
            packages_files.append(file_found)

    uid_names, packages_read = _uid_names(packages_files) if appops_files else ({}, [])

    def record(key, relative_path):
        paths = rows.setdefault(key, [])
        if relative_path not in paths:
            paths.append(relative_path)

    for file_found in appops_files:
        try:
            root = _root(file_found)
        except Exception as error:  # pylint: disable=broad-except
            logfunc(f'App Ops Permission Modes: could not read {os.path.basename(file_found)}: {error}')
            continue
        relative_path = context.get_relative_path(file_found)
        # The file was read, so it is cited whether or not it held a stored mode.
        sources.append(file_found)

        for child in root:
            if child.tag == 'uid':
                # Both schemas store uid scoped modes here. The package name is resolved from
                # packages.xml rather than stored, which Mode Stored Against says.
                stored_uid = child.get('n', '')
                android_user, app_id = _split_uid(stored_uid)
                name = uid_names.get(app_id, '')
                for op in _mode_ops(child):
                    record((name, stored_uid, '' if android_user is None else str(android_user),
                            _op_name(op.get('n')), op.get('n', ''), _mode_name(op.get('m')), 'UID'),
                           relative_path)
            elif child.tag == 'user':
                # Android 14 and later store package scoped modes under a user element, which
                # carries the Android user and no uid.
                android_user = child.get('n', '')
                for pkg in child:
                    if pkg.tag != 'pkg':
                        continue
                    for op in _mode_ops(pkg):
                        record((pkg.get('n', ''), '', android_user, _op_name(op.get('n')),
                                op.get('n', ''), _mode_name(op.get('m')), 'Package'), relative_path)
            elif child.tag == 'pkg':
                # Android 13 and earlier store package scoped modes under pkg then uid.
                package = child.get('n', '')
                for uid_element in child:
                    if uid_element.tag != 'uid':
                        continue
                    stored_uid = uid_element.get('n', '')
                    android_user, _app_id = _split_uid(stored_uid)
                    for op in _mode_ops(uid_element):
                        record((package, stored_uid,
                                '' if android_user is None else str(android_user),
                                _op_name(op.get('n')), op.get('n', ''),
                                _mode_name(op.get('m')), 'Package'), relative_path)

    data_list = [key + (', '.join(paths),) for key, paths in rows.items()]
    if sources:
        sources.extend(packages_read)
    return data_headers, data_list, '\n'.join(sources)
