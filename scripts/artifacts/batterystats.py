__artifacts_v2__ = {
    "battery_stats_daily": {
        "name": "Android Battery Stats Daily",
        "description": "Parses the Android System batterystats-daily.xml - \
                        Steps string is in format: [device_state]-[battery_level]-[time_in_ms]",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "creation_date": "2026-03-12",
        "last_update_date": "2026-03-14",
        "requirements": "xmltodict, xml",
        "category": "Android Battery Statistics",
        "notes": "",
        "output_types": ["standard"],
        "paths": (  '*/system/batterystats-daily.xml'),
        "artifact_icon": "battery-charging"
    }
}


import xmltodict
import xml.etree.ElementTree as etree
from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, abxread

@artifact_processor
def battery_stats_daily(files_found, _report_folder, _seeker, _wrap_text):
    
    abx_file = ''

    for file_found in files_found:
        abx_file = str(file_found)

    data_headers = []
    data_list = []

    multi_root = False
    tree = abxread(abx_file, multi_root)
    xlmstring = (etree.tostring(tree.getroot()).decode())
    doc = xmltodict.parse(xlmstring)

    def _ensure_list(value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    # Mappings from https://android.googlesource.com/platform/frameworks/base/+/master/core/java/android/os/BatteryStats.java
    initial_state_meanings = {
        "f": "Screen OFF at step start (Display.STATE_OFF)",
        "o": "Screen ON at step start (Display.STATE_ON)",
        "d": "Screen DOZE at step start (Display.STATE_DOZE)",
        "z": "Screen DOZE SUSPEND at step start (Display.STATE_DOZE_SUSPEND)",
        "p": "Power save active at step start",
        "i": "Device idle active at step start",
    }

    change_flag_meanings = {
        "F": "Display changed to OFF during step",
        "O": "Display changed to ON during step",
        "D": "Display changed to DOZE during step",
        "Z": "Display changed to DOZE SUSPEND during step",
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
