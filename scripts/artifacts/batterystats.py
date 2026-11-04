__artifacts_v2__ = {
    "battery_stats_daily": {
        "name": "Android Battery Stats Daily",
        "description": "Parses the Android System batterystats-daily.xml. Each step string is "
                       "[mode letters]-[battery level, hexadecimal]-[step duration, hexadecimal], "
                       "as written by BatteryStats.LevelStepTracker.encodeEntryAt (AOSP "
                       "frameworks/base, android-14.0.0_r1, core/java/android/os/BatteryStats.java "
                       "lines 1388 to 1425)",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "creation_date": "2026-03-12",
        "last_update_date": "2026-10-09",
        "requirements": "xmltodict, xml",
        "category": "Android Battery Statistics",
        "notes": "Prefix Meaning is this module's reading of the mode letters. Lowercase letters "
                 "come from the step's initial mode bits and uppercase letters from its modified "
                 "mode bits, which a comment in AOSP BatteryStats.java at android-14.0.0_r1 (line "
                 "3471) describes as the modes that changed during the step. encodeEntryAt in "
                 "that file (lines 1388 to 1425) writes one of F, O, D or Z for every "
                 "step from the value of the two modified screen-state bits, so those letters are "
                 "reported as that bit value and not as a display change. How the writer sets "
                 "those two bits was not read here.",
        "output_types": ["standard"],
        "paths": (  '*/system/batterystats-daily.xml'),
        "artifact_icon": "battery-charging",
        "sample_data": {
            "anne_a15": "Android 15 | 170 rows",
            "galaxys10_a10": "Android 10 | 275 rows",
            "hc_pixel8pro_a16": "Android 16 | 367 rows",
            "kevin_pocox7_a15": "Android 15 | 586 rows",
            "pixel7a_a14": "Android 14 | 727 rows",
            "samsunga53_a14": "Android 14 | 335 rows",
            "samsungs20_a13": "Android 13 | 148 rows",
            "sharon_a14": "Android 14 | 230 rows",
            "russell_pixel6a_a13": "Android 13 | 714 rows",
            "userb2_a13": "Android 13 | 325 rows",
        }
    },
    "battery_stats_daily_package_changes": {
        "name": "Android Battery Stats Daily Package Changes",
        "description": "Package change records (upd and rem elements) inside each daily item of the "
                       "Android System batterystats-daily.xml: the day window, package name and "
                       "version code as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-31",
        "last_update_date": "2026-10-31",
        "requirements": "xmltodict, xml",
        "category": "Android Battery Statistics",
        "notes": "One row per upd or rem element inside an item element, in file order. Marco Neumann "
                 "described these records in his post Ten Days of Android Battery History and App Updates "
                 "(https://bebinary4n6.blogspot.com/2026/10/ten-days-of-android-battery-history-and.html). "
                 "AOSP BatteryStatsImpl writes upd with pkg and ver for a package change whose update flag is "
                 "set and rem with pkg otherwise (android-14.0.0_r1, "
                 "https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-14.0.0_r1/services/core/java/com/android/server/power/stats/BatteryStatsImpl.java "
                 "lines 11207 to 11221). ActivityManagerService notes an install with the package's version code "
                 "on every ACTION_PACKAGE_ADDED broadcast, a fresh install and a replacement alike, or 0 when "
                 "the package information it reads is null (android-14.0.0_r1, "
                 "https://android.googlesource.com/platform/frameworks/base/+/refs/tags/android-14.0.0_r1/services/core/java/com/android/server/am/ActivityManagerService.java "
                 "lines 14773 to 14790), so a upd row does not separate an install from an update. A full "
                 "uninstall is noted through notePackageUninstalledLocked, which also sets the update flag and no "
                 "version code (BatteryStatsImpl.java lines 5816 to 5824 at android-14.0.0_r1; the same "
                 "assignment is at line 5059 at android-11.0.0_r1, line 6428 at android-13.0.0_r1 and line 6127 "
                 "at android-16.0.0_r1), so it is written as upd with ver 0, not as rem. In the AOSP code read here, "
                 "Version Code (as stored) 0 comes from a full uninstall or from an add whose package information "
                 "was null. Which one is not established from the record, and no known uninstall was made to test it. "
                 "Android records a daily item with the stored daily start time as its start and the wall "
                 "clock at recording as its end, and moves into it every package change noted since the last "
                 "one it recorded (BatteryStatsImpl.java lines 11132 to 11152 at android-14.0.0_r1), so a row "
                 "carries no time of its own: Day Start and Day End are the item's start and end attributes, "
                 "milliseconds since 1970 read as UTC. Item Index is the item's position in the file, from 1. "
                 "Measured on the Android corpus (51 images): 27 of the 28 batterystats-daily.xml files found held "
                 "upd elements, on images registered or named as Android 10 to 17, and no file held a rem "
                 "element, which no note path above writes. On the eleven images in sample_data the row count "
                 "equals an independent count of the upd and rem elements in each file. The same package can "
                 "appear more than once in one item. On emu_a15_oss_v17 the daily items held only upd elements, "
                 "so Android Battery Stats Daily reports no rows there while this artifact reports 506.",
        "output_types": ["standard"],
        "paths": ('*/system/batterystats-daily.xml',),
        "artifact_icon": "package",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 230 rows",
            "pixel3_a11": "Android 11 | 23 rows",
            "pixel3_a12": "Android 12 | 26 rows",
            "hickman_a13": "Android 13 | 16 rows",
            "samsungs20_a13": "Android 13 | 153 rows",
            "userb2_a13": "Android 13 | 92 rows",
            "pixel7a_a14": "Android 14 | 128 rows",
            "kevin_pocox7_a15": "Android 15 | 233 rows",
            "emu_a15_oss_v17": "Android 15 | 506 rows",
            "hc_pixel8pro_a16": "Android 16 | 387 rows",
            "hc_pixel8pro_a17": "Android 17 | 243 rows",
        },
    }
}

import xmltodict
import xml.etree.ElementTree as etree
from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, abxread, checkabx, logfunc

@artifact_processor
def battery_stats_daily(context):
    files_found = context.get_files_found()
    
    abx_file = ''

    for file_found in files_found:
        abx_file = str(file_found)

    data_headers = []
    data_list = []

    multi_root = False
    if (checkabx(abx_file)):
        multi_root = False
        tree = abxread(abx_file, multi_root)
    else:
        tree = etree.parse(abx_file)
    
    xlmstring = (etree.tostring(tree.getroot()).decode())
    doc = xmltodict.parse(xlmstring)

    def _ensure_list(value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    # Letters from BatteryStats.LevelStepTracker.encodeEntryAt, AOSP frameworks/base at
    # android-14.0.0_r1, core/java/android/os/BatteryStats.java lines 1388 to 1425.
    initial_state_meanings = {
        "f": "Screen OFF at step start (Display.STATE_OFF)",
        "o": "Screen ON at step start (Display.STATE_ON)",
        "d": "Screen DOZE at step start (Display.STATE_DOZE)",
        "z": "Screen DOZE SUSPEND at step start (Display.STATE_DOZE_SUSPEND)",
        "p": "Power save active at step start",
        "i": "Device idle active at step start",
    }

    change_flag_meanings = {
        "F": "Modified screen-state bits equal Display.STATE_OFF - 1",
        "O": "Modified screen-state bits equal Display.STATE_ON - 1",
        "D": "Modified screen-state bits equal Display.STATE_DOZE - 1",
        "Z": "Modified screen-state bits equal Display.STATE_DOZE_SUSPEND - 1",
        "P": "Power save mode changed during step",
        "I": "Device idle mode changed during step",
    }

    def _decode_prefix(prefix):
        meanings = []
        if not prefix:
            return meanings
        for ch in prefix:
            if ch.islower():
                meanings.append(initial_state_meanings.get(ch, f"UnknownInitial({ch})"))
            else:
                meanings.append(change_flag_meanings.get(ch, f"UnknownFlag({ch})"))
        return meanings

    def _parse_step(step_value):
        # Expected format: <prefix>-<level_hex>-<time_hex>
        parts = step_value.split("-", 2)
        if len(parts) != 3:
            return {
                "prefix": step_value,
                "initial_state": "",
                "change_flags": "",
                "level_hex": "",
                "level_int": "",
                "time_hex": "",
                "time_ms": "",
                "prefix_meanings": ["Unparsed"],
            }
        prefix, level_hex, time_hex = parts
        initial_state = "".join([c for c in prefix if c.islower()])
        change_flags = "".join([c for c in prefix if c.isupper()])
        try:
            level_int = int(level_hex, 16)
        except ValueError:
            level_int = ""
        try:
            time_ms = int(time_hex, 16)
        except ValueError:
            time_ms = ""
        return {
            "prefix": prefix,
            "initial_state": initial_state,
            "change_flags": change_flags,
            "level_hex": level_hex,
            "level_int": level_int,
            "time_hex": time_hex,
            "time_ms": time_ms,
            "prefix_meanings": _decode_prefix(prefix),
        }

    daily_items = doc.get('daily-items', {})
    items = _ensure_list(daily_items.get('item'))

    for item in items:
        start_ms = item.get('@start')
        end_ms = item.get('@end')

        dis = item.get('dis')
        chg = item.get('chg')

        dis_steps = [s.get('@v', '') for s in _ensure_list(dis.get('s'))] if dis else []
        chg_steps = [s.get('@v', '') for s in _ensure_list(chg.get('s'))] if chg else []

        start_utc = convert_unix_ts_to_utc(int(start_ms) / 1000) if start_ms else ''
        end_utc = convert_unix_ts_to_utc(int(end_ms) / 1000) if end_ms else ''

        for step_value in dis_steps:
            parsed = _parse_step(step_value)
            data_list.append((
                start_utc,
                end_utc,
                "discharge",
                step_value,
                parsed["prefix"],
                parsed["initial_state"],
                parsed["change_flags"],
                "; ".join(parsed["prefix_meanings"]),
                parsed["level_int"],
                parsed["time_ms"]
            ))

        for step_value in chg_steps:
            parsed = _parse_step(step_value)
            data_list.append((
                start_utc,
                end_utc,
                "charge",
                step_value,
                parsed["prefix"],
                parsed["initial_state"],
                parsed["change_flags"],
                "; ".join(parsed["prefix_meanings"]),
                parsed["level_int"],
                parsed["time_ms"]
            ))

    data_headers = (
        ("Start Time", "datetime"),
        ("End Time", "datetime"),
        "Step Type",
        "Raw Step Content",
        "Content Prefix",
        "Initial State",
        "Change Flags",
        "Prefix Meaning",
        "Battery Level",
        "Time (ms)"
    )

    source_path = abx_file
    return data_headers, data_list, source_path


def _daily_root(path):
    """The root element of a batterystats-daily.xml, ABX or text XML."""
    if checkabx(path):
        return abxread(path, False).getroot()
    return etree.parse(path).getroot()


def _ms_utc(value):
    """A datetime for milliseconds since 1970, or '' when absent, zero or not a number."""
    try:
        millis = int(value) if value else 0
    except ValueError:
        return ''
    return convert_unix_ts_to_utc(millis / 1000) if millis else ''


def package_change_rows(root):
    """One row per upd or rem element inside an item element, in file order."""
    rows = []
    for index, item in enumerate(root.findall('item'), 1):
        start, end = _ms_utc(item.get('start')), _ms_utc(item.get('end'))
        for change in item:
            if change.tag in ('upd', 'rem'):
                rows.append((start, end, change.tag, change.get('pkg', ''),
                             change.get('ver', '') if change.tag == 'upd' else '', index))
    return rows


@artifact_processor
def battery_stats_daily_package_changes(context):
    data_headers = (("Day Start", "datetime"), ("Day End", "datetime"), "Record", "Package",
                    "Version Code (as stored)", "Item Index")
    data_list = []
    sources = []
    for file_found in sorted({str(f) for f in context.get_files_found()}):
        try:
            root = _daily_root(file_found)
        except (etree.ParseError, OSError, ValueError) as ex:
            logfunc(f'Battery Stats Daily Package Changes: could not read {context.get_relative_path(file_found)}: {ex}')
            continue
        sources.append(file_found)
        rows = package_change_rows(root)
        data_list.extend(rows)
        logfunc(f'Battery Stats Daily Package Changes: {len(rows)} upd and rem elements in '
                f'{len(root.findall("item"))} items of {context.get_relative_path(file_found)}')
    return data_headers, data_list, '\n'.join(sources)
