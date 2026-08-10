__artifacts_v2__ = {
    "alex_live_appops": {
        "name": "App Ops",
        "description": "Reads App Ops Data \
            from a PRFS backup created by ALEX.",
        "author": "@C_Peter",
        "creation_date": "2026-01-30",
        "last_update_date": "2026-01-30",
        "requirements": "none",
        "category": "ALEX Live Data",
        "notes": "",
        "paths": ('*/extra/app_ops.json'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "package"
    },
    "alex_live_wifi_conf_net": {
        "name": "Dumpsys - Configured Networks",
        "description": "Outputs the configured \
            (known) networks from the Dumpsys \
                log of an ALEX PRFS backup.",
        "author": "@C_Peter",
        "creation_date": "2026-02-02",
        "last_update_date": "2026-02-02",
        "requirements": "none",
        "category": "ALEX Live Data",
        "notes": "",
        "paths": ('*/extra/dumpsys_*.txt'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "wifi"
    },
    "alex_live_usagestats_events": {
        "name": "Dumpsys - Usagestats Events",
        "description": "Outputs the Usagestats \
            Event entries from the Dumpsys \
                log of an ALEX PRFS backup.",
        "author": "@C_Peter",
        "creation_date": "2026-02-03",
        "last_update_date": "2026-02-03",
        "requirements": "none",
        "category": "ALEX Live Data",
        "notes": "",
        "paths": ('*/extra/dumpsys_*.txt'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "activity"
    },
    "alex_live_usagestats_yearly": {
        "name": "Dumpsys - Usagestats (yearly)",
        "description": "Outputs the Usagestats \
            (yearly) entries from the Dumpsys \
                log of an ALEX PRFS backup.",
        "author": "@C_Peter",
        "creation_date": "2026-02-04",
        "last_update_date": "2026-02-04",
        "requirements": "none",
        "category": "ALEX Live Data",
        "notes": "",
        "paths": ('*/extra/dumpsys_*.txt'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "chart-bar"
    },
    "alex_live_bt_bonded": {
        "name": "Dumpsys - BTM Bonded Devices",
        "description": "Outputs the Bonded \
            Bluetooth devices from the Dumpsys \
                log of an ALEX PRFS backup. \
                    Usually only included if \
                        Bluetooth was active \
                            during backup.",
        "author": "@C_Peter",
        "creation_date": "2026-02-05",
        "last_update_date": "2026-02-05",
        "requirements": "none",
        "category": "ALEX Live Data",
        "notes": "",
        "paths": ('*/extra/dumpsys_*.txt'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "bluetooth"
    },
    "alex_live_companiondevice": {
        "name": "Dumpsys - Companiondevice",
        "description": "Outputs the associated \
            Companion devices from the Dumpsys \
                log of an ALEX PRFS backup.",
        "author": "@C_Peter",
        "creation_date": "2026-02-06",
        "last_update_date": "2026-02-06",
        "requirements": "none",
        "category": "ALEX Live Data",
        "notes": "",
        "paths": ('*/extra/dumpsys_*.txt'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "device-watch"
    },
    "alex_live_role": {
        "name": "Dumpsys - Role (Default Apps)",
        "description": "Outputs the Default \
            Apps from the Dumpsys \
                log of an ALEX PRFS backup.",
        "author": "@C_Peter",
        "creation_date": "2026-02-06",
        "last_update_date": "2026-02-06",
        "requirements": "none",
        "category": "ALEX Live Data",
        "notes": "",
        "paths": ('*/extra/dumpsys_*.txt'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "circle-check"
    },
    "alex_live_account": {
        "name": "Dumpsys - Accounts",
        "description": "Outputs the Accounts \
            from the Dumpsys log of an \
                ALEX PRFS backup.",
        "author": "@C_Peter",
        "creation_date": "2026-02-06",
        "last_update_date": "2026-02-06",
        "requirements": "none",
        "category": "ALEX Live Data",
        "notes": "",
        "paths": ('*/extra/dumpsys_*.txt'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "user"
    },
    "alex_live_batterystats": {
        "name": "Dumpsys - Batterystats",
        "description": "Outputs the Batterystats \
            from the Dumpsys log of an \
                ALEX PRFS backup.",
        "author": "@C_Peter",
        "creation_date": "2026-03-19",
        "last_update_date": "2026-03-19",
        "requirements": "none",
        "category": "ALEX Live Data",
        "notes": "",
        "paths": ('*/extra/dumpsys_*.txt',
            '*/device_info_alex.json'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "battery-charging"
    },
    "alex_live_logcat": {
        "name": "Logcat",
        "description": "Parses the Logcat \
            logs of an \
                ALEX PRFS backup.",
        "author": "@C_Peter",
        "creation_date": "2026-03-03",
        "last_update_date": "2026-03-03",
        "requirements": "none",
        "category": "ALEX Live Data",
        "notes": "",
        "paths": ('*/extra/logcat.txt'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "terminal"
    }
}

import json
import re
import os
import datetime
from scripts.ilapfuncs import artifact_processor, \
    get_file_path, logfunc

_PARSED_DUMPSYS = False
_DUMPSYS_DICT = {}
_DEVICE_TIME = 0
#Convert arabic numbers:
trans = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

# Timestamp Helper - Converts to UNIX Timestamp
def parse_timestamp(s, device_ts):
    """Function reading string-times and converts them to unix-timestamps"""
    if not s or not isinstance(s, str):
        return None
    s = s.strip()
    s = s.translate(trans)
    # Dumpsys RESET:TIME: format
    try:
        dt = datetime.datetime.strptime(s, "%Y-%m-%d-%H-%M-%S")
        dt = dt.replace(tzinfo=datetime.timezone.utc)
        return int(dt.timestamp())
    except (ValueError, IndexError, TypeError):
        pass
    # ISO format: 2026-02-02T05:37:49.732
    try:
        dt = datetime.datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S")
        dt = dt.replace(tzinfo=datetime.timezone.utc)
        return int(dt.timestamp())
    except (ValueError, IndexError, TypeError):
        pass
    # Dumpsys format: 2026-02-02 12:11:46
    try:
        dt = datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
        dt = dt.replace(tzinfo=datetime.timezone.utc)
        return int(dt.timestamp())
    except (ValueError, IndexError, TypeError):
        pass
    # German formats
    for fmt in ("%d.%m.%Y, %H:%M", "%d.%m.%Y %H:%M"):
        try:
            dt = datetime.datetime.strptime(s, fmt)
            return int(dt.replace(tzinfo=datetime.timezone.utc).timestamp())
        except (ValueError, IndexError, TypeError):
            pass
    # Short format: 07-21 03:37:00.040
    if device_ts is None:
        pass
    try:
        device_dt = datetime.datetime.fromtimestamp(device_ts, tz=datetime.timezone.utc)
        if len(s) < 6 or s[2] != '-' or s[5] != ' ':
            pass
        else:
            month = int(s[0:2])
            day = int(s[3:5])
            year = device_dt.year
            if (month, day) > (device_dt.month, device_dt.day):
                year -= 1
            full_ts = f"{year}-{month:02d}-{day:02d}{s[5:]}"
            dt = datetime.datetime.strptime(full_ts, "%Y-%m-%d %H:%M:%S.%f")
            dt = dt.replace(tzinfo=datetime.timezone.utc)
            return float(dt.timestamp())
    except (ValueError, IndexError, TypeError):
        return None
    # Short format: date only MM-DD
    try:
        device_dt = datetime.datetime.fromtimestamp(device_ts, tz=datetime.timezone.utc)
        if len(s) == 5 and s[2] == '-':
            month = int(s[0:2])
            day = int(s[3:5])
            year = device_dt.year
            if (month, day) > (device_dt.month, device_dt.day):
                year -= 1
            # assume start of day
            full_ts = f"{year}-{month:02d}-{day:02d} 00:00:00.000"
            dt = datetime.datetime.strptime(full_ts, "%Y-%m-%d %H:%M:%S.%f")
            return int(dt.replace(tzinfo=datetime.timezone.utc).timestamp())

    except (ValueError, IndexError, TypeError):
        return None

# Time-Offset Helper
def parse_relative_time(s):
    """Function to convert time-offsets to seconds and milliseconds (as float)"""
    pattern = re.compile(
        r'\+?'
        r'(?:(\d+)d)?'
        r'(?:(\d+)h)?'
        r'(?:(\d+)m(?!s))?'
        r'(?:(\d+)s)?'
        r'(?:(\d+)ms)?'
    )
    match = pattern.fullmatch(s.strip())
    if not match:
        return 0
    d, h, m_, s_, ms = match.groups()
    d = int(d) if d else 0
    h = int(h) if h else 0
    m_ = int(m_) if m_ else 0
    s_ = int(s_) if s_ else 0
    ms = int(ms) if ms else 0
    total_ms = (
        d * 86400000 +
        h * 3600000 +
        m_ * 60000 +
        s_ * 1000 +
        ms
    )
    return total_ms / 1000

# Helper to split the Dumpsys Output
def split_dumpsys_log(dumpsys_file) -> dict:
    """Function to split the dumpsys txt file in service parts"""
    global _PARSED_DUMPSYS, _DUMPSYS_DICT, _DEVICE_TIME # pylint: disable=global-statement
    if _PARSED_DUMPSYS:
        return
    if not dumpsys_file:
        return

    ds_filename = os.path.basename(dumpsys_file)
    try:
        _DEVICE_TIME = int(ds_filename.split('_', 1)[1].split('.', 1)[0])
    except (ValueError, IndexError):
        logfunc("Dumpsys File does not contain a unix timestamp")

    with open(dumpsys_file, "r", encoding="utf-8", errors="ignore") as f:
        log_txt = f.read()

    dumpdict = {}
    start_re = re.compile(r"DUMP OF SERVICE\s+(\S+):")
    duration_re = re.compile(
        r"([\d.]+)s\s+was the duration of dumpsys.*ending at:\s+(.+)$"
    )

    current_service = None
    current_lines = []
    current_start_ts = None

    def flush():
        if current_service:
            dumpdict[current_service] = (
                "\n".join(current_lines),
                current_start_ts
            )

    for line in log_txt.splitlines():
        start_match = start_re.search(line)
        if start_match:
            flush()
            current_service = start_match.group(1)
            current_lines = []
            current_start_ts = None
            continue

        if not current_service:
            continue

        current_lines.append(line)

        dur_match = duration_re.search(line)
        if dur_match:
            duration_s = float(dur_match.group(1))
            end_time = datetime.datetime.strptime(
                dur_match.group(2).strip(),
                "%Y-%m-%d %H:%M:%S"
            )
            current_start_ts = (
                end_time - datetime.timedelta(seconds=duration_s)
            ).timestamp()

    flush()
    _DUMPSYS_DICT = dumpdict
    _PARSED_DUMPSYS = True

# Dumpsys - Wifi - Configured Networks
@artifact_processor
def alex_live_wifi_conf_net(context):
    """Parses the dumpsys wifi dump for configured networks"""
    files_found = context.get_files_found()
    source_path = files_found[0]
    data_list = []
    split_dumpsys_log(source_path)
    wifi_dump, wifi_ts = _DUMPSYS_DICT.get("wifi", (None, None))
    if wifi_dump is None:
        logfunc('Dumpsys does not include a \"wifi\" part.')
    else:
        logtext = (
            'Dumpsys does include a \"wifi\" part without timestamp.'
            if wifi_ts is None
            else f'Dumpsys does include a \"wifi\" part with timestamp: {str(wifi_ts)}'
        )
        logfunc(logtext)
        ID_RE = re.compile(r'^\s*[*-]?\s*(DSBLE ID|ID):\s*(\d+)')
        SECTION_BREAK_RE = re.compile(r'^(Dump of|DUMP OF SERVICE|WifiConfigManager|WifiConfigStore)')
        FIELD_PATTERNS = {
            "ssid": re.compile(r'SSID:\s*"([^"]*)"'),
            "bssid": re.compile(r'BSSID:\s*(\S+)'),
            "hidden": re.compile(r'HIDDEN:\s*(\S+)'),
            "creation_millis": re.compile(r'creation millis:\s*(\d+)'),
            "creation_time": re.compile(r'creationtime=([0-9\-:\.\s]+)|creation time=([0-9\-:\.\s]+)'),
            "randomized_mac": re.compile(r'^\s*[*-]?\s*mRandomizedMacAddress:\s*([0-9a-fA-F:]{17})', re.IGNORECASE),
            "last_connected": re.compile(r'lastConnected:\s*([^\s]+)'),
            "autojoin": re.compile(r'autojoin\s*:\s*(\d+)|allowAutojoin=(true|false)', re.IGNORECASE),
        }

        in_section = False
        current_key = None
        net_id = None
        dsble = None
        ssid = bssid = hidden = None
        creation_millis = creation_time = None
        randomized_mac = last_connected = autojoin = None
        create_time = last_connected_time = None

        for line in wifi_dump.splitlines():
            stripped = line.strip()

            if "Configured networks" in line:
                in_section = True
                continue
            if not in_section:
                continue

            if SECTION_BREAK_RE.match(stripped):
                if current_key is not None:
                    data_list.append((net_id, create_time, last_connected_time, ssid,
                                    bssid, dsble, hidden, randomized_mac, autojoin))
                current_key = None
                in_section = False
                continue

            m_id = ID_RE.match(line)
            if m_id:
                if current_key is not None:
                    data_list.append((net_id, create_time, last_connected_time, ssid,
                                    bssid, dsble, hidden, randomized_mac, autojoin))


                id_type, id_value = m_id.groups()
                net_id = int(id_value)
                dsble = (id_type == "DSBLE ID")
                current_key = net_id

                ssid = bssid = hidden = None
                creation_millis = creation_time = None
                randomized_mac = last_connected = autojoin = None
                create_time = last_connected_time = None

            if current_key is not None:
                for key, pattern in FIELD_PATTERNS.items():
                    m = pattern.search(line)
                    if m:
                        if key == "autojoin":
                            if m.group(1) is not None:
                                autojoin = int(m.group(1))
                            elif m.group(2) is not None:
                                autojoin = 1 if m.group(2).lower() == "true" else 0
                        elif key == "creation_time":
                            creation_time = m.group(1) or m.group(2)
                        else:
                            value = m.group(1)
                            if key == "ssid":
                                ssid = value
                            elif key == "bssid":
                                bssid = value
                            elif key == "hidden":
                                hidden = value
                            elif key == "creation_millis":
                                creation_millis = value
                            elif key == "creation_time":
                                creation_time = value
                            elif key == "randomized_mac":
                                randomized_mac = value
                            elif key == "last_connected":
                                last_connected = value

                if creation_millis:
                    create_time = datetime.datetime.fromtimestamp(int(creation_millis)//1000, tz=datetime.timezone.utc)
                elif creation_time and creation_time is not None:
                    c_time = parse_timestamp(creation_time, _DEVICE_TIME)
                    if c_time:
                        create_time = datetime.datetime.fromtimestamp(c_time, tz=datetime.timezone.utc)
                    else:
                        create_time = creation_time
                if last_connected:
                    l_time = parse_timestamp(last_connected, _DEVICE_TIME)
                    if l_time:
                        last_connected_time = datetime.datetime.fromtimestamp(l_time, tz=datetime.timezone.utc)
                    else:
                        last_connected_time = last_connected

        if current_key is not None:
            data_list.append((net_id, create_time, last_connected_time, ssid,
                            bssid, dsble, hidden, randomized_mac, autojoin))
          
    data_headers = ('ID', ('Creation Time', 'datetime'), ('Last Connected', 'datetime'), 'SSID', 'BSSID', 'DSBLE', 'Hidden', 'Random MAC', 'Autojoin')

    return data_headers, data_list, source_path

# Dumpsys - Usagestats - Events
@artifact_processor
def alex_live_usagestats_events(context):
    """Parses the dumpsys usagestats dump for event logs"""
    files_found = context.get_files_found()
    source_path = files_found[0]
    data_list = []
    split_dumpsys_log(source_path)
    us_dump, us_ts = _DUMPSYS_DICT.get("usagestats", (None, None))
    if us_dump is None:
        logfunc('Dumpsys does not include a \"usagestats\" part.')
    else:
        logtext = (
            'Dumpsys does include a \"usagestats\" part without timestamp.'
            if us_ts is None
            else f'Dumpsys does include a \"usagestats\" part with timestamp: {str(us_ts)}'
        )
        logfunc(logtext)
        PAIR_RE = re.compile(r'(\w+)=(".*?"|\S+)')
        data_list = []

        for line in us_dump.splitlines():
            stripped = line.strip()

            if not stripped.startswith("time=") or "type=" not in stripped or "package=" not in stripped:
                continue

            pairs = dict(
                (k, v.strip('"'))
                for k, v in PAIR_RE.findall(stripped))
            time = pairs.pop("time", None)
            timestamp = parse_timestamp(time, _DEVICE_TIME)
            if timestamp:
                out_time = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
            else:
                out_time = time
            event_type = pairs.pop("type", None)
            package = pairs.pop("package", None)
            reason = pairs.pop("reason", None)
            extra_data = pairs

            data_list.append((out_time, event_type, package, extra_data, reason))
    data_headers = (('Time', 'datetime'), 'Event Type', 'Package', 'Event', 'Reason')

    return data_headers, data_list, source_path

# Dumpsys - Usagestats - Packages (yearly)
@artifact_processor
def alex_live_usagestats_yearly(context):
    """Parses the dumpsys usagestats dump for event logs"""
    files_found = context.get_files_found()
    source_path = files_found[0]
    data_list = []
    data_headers = []
    ordered_keys = None
    split_dumpsys_log(source_path)
    us_dump, us_ts = _DUMPSYS_DICT.get("usagestats", (None, None))
    if us_dump is None:
        logfunc('Dumpsys does not include a \"usagestats\" part.')
    else:
        logtext = (
            'Dumpsys does include a \"usagestats\" part without timestamp.'
            if us_ts is None
            else f'Dumpsys does include a \"usagestats\" part with timestamp: {str(us_ts)}'
        )
        logfunc(logtext)
        us_yearly = us_dump.split("In-memory yearly stats")[1]
        PAIR_RE = re.compile(r'(\w+)=(".*?"|\S+)')
        data_list = []

        for line in us_yearly.splitlines():
            stripped = line.strip()
            if not stripped.startswith("package=") or "lastTime" not in stripped:
                continue

            pairs = dict(
                (k, v.strip('"'))
                for k, v in PAIR_RE.findall(stripped))

            if ordered_keys is None:
                ordered_keys = list(pairs.keys())
                for key in ordered_keys:
                    value = pairs[key]
                    if key == "package":
                        data_headers.append("Package")
                    else:
                        timestamp = parse_timestamp(value, _DEVICE_TIME)
                        if timestamp is None:
                            data_headers.append(key)
                        else:
                            data_headers.append((key, "datetime"))

            row_values = []
            for key in ordered_keys:
                value = pairs[key]
                if key == "package":
                    row_values.append(value)
                else:
                    timestamp = parse_timestamp(value, _DEVICE_TIME)
                    if timestamp is None:
                        value = value.translate(trans)
                        row_values.append(value)
                    else:
                        out_time = datetime.datetime.fromtimestamp(
                            timestamp, tz=datetime.timezone.utc)
                        row_values.append(out_time)

            data_list.append(tuple(row_values))

        return tuple(data_headers), data_list, source_path

# Dumpsys - Bluetooth Manager - Bonded Devices
@artifact_processor
def alex_live_bt_bonded(context):
    """Parses the dumpsys bluetooth_manager dump for bonded devices"""
    files_found = context.get_files_found()
    source_path = files_found[0]
    data_list = []
    split_dumpsys_log(source_path)
    btm_dump, btm_ts = _DUMPSYS_DICT.get("bluetooth_manager", (None, None))
    if btm_dump is None:
        logfunc('Dumpsys does not include a \"bluetooth_manager\" part.')
    else:
        logtext = (
            'Dumpsys does include a \"bluetooth_manager\" part without timestamp.'
            if btm_ts is None
            else f'Dumpsys does include a \"bluetooth_manager\" part with timestamp: {str(btm_ts)}'
        )
        logfunc(logtext)
        device_pattern = re.compile(r'''
            ^\s*
            ([0-9A-FX]{2}(?::[0-9A-FX]{2}){5})
            .*?
            (?<!\[)
            (\b[^\[\]\n]+\b)
            \s*$
        ''', re.VERBOSE)
        data_list = []
        in_bonded = False
        for line in btm_dump.splitlines():
            if "Bonded devices:" in line:
                in_bonded = True
                continue

            if in_bonded:
                if line.strip() == "":
                    break

                m = device_pattern.match(line)
                if m:
                    mac, name = m.groups()
                    if name:
                        data_list.append((mac, name.strip()))
                else:
                    continue
        data_headers = ('MAC', "Name")

    return data_headers, data_list, source_path

# Dumpsys - Companiondevice
@artifact_processor
def alex_live_companiondevice(context):
    """Parses the dumpsys companiondevice dump for entries"""
    files_found = context.get_files_found()

    source_path = files_found[0]
    data_list = []
    data_headers = []

    split_dumpsys_log(source_path)
    cmpd_dump, cmpd_ts = _DUMPSYS_DICT.get("companiondevice", (None, None))

    if cmpd_dump is None:
        logfunc('Dumpsys does not include a "companiondevice" part.')
        return data_headers, data_list, source_path
    
    else:
        logtext = (
            'Dumpsys does include a \"companiondevice\" part without timestamp.'
            if cmpd_ts is None
            else f'Dumpsys does include a \"companiondevice\" part with timestamp: {str(cmpd_ts)}'
        )
        logfunc(logtext)
        FIELD_SPLIT_RE = re.compile(r", (?=\w+=)")
        for line in cmpd_dump.splitlines():
            stripped = line.strip()
            if not stripped.startswith("Association{"):
                continue

            content = stripped[stripped.find("{") + 1 : stripped.rfind("}")]
            fields = FIELD_SPLIT_RE.split(content)

            assoc = {}
            for field in fields:
                if "=" not in field:
                    continue

                key, value = field.split("=", 1)
                key = key.strip()
                value = value.strip()
                if value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                if value in ("null", "None"):
                    value = None
                assoc[key] = value

            if not data_headers:
                data_headers = list(assoc.keys())

            row = tuple(assoc.get(key) for key in data_headers)
            data_list.append(row)

        return data_headers, data_list, source_path

# Dumpsys - Role (Default Apps)
@artifact_processor
def alex_live_role(context):
    """Parses the dumpsys role dump for entries"""
    files_found = context.get_files_found()
    source_path = files_found[0]
    data_list = []
    split_dumpsys_log(source_path)
    role_dump, role_ts = _DUMPSYS_DICT.get("role", (None, None))
   
    if role_dump is None:
        logfunc('Dumpsys does not include a "role" part.')
    else:
        logtext = (
            'Dumpsys does include a \"role\" part without timestamp.'
            if role_ts is None
            else f'Dumpsys does include a \"role\" part with timestamp: {str(role_ts)}'
        )
        logfunc(logtext)
        user_blocks = re.findall(r"user_states=\{(.*?)\n\}", role_dump, re.DOTALL)
       
        for block in user_blocks:
            user_id_match = re.search(r"user_id=(\d+)", block)
            uid = int(user_id_match.group(1)) if user_id_match else None
            roles_match = re.search(r"roles=\[(.*)\]", block, re.DOTALL)
            roles_block = roles_match.group(1) if roles_match else ""
            role_entries = re.findall(r"\{(.*?)\}", roles_block, re.DOTALL)
            for entry in role_entries:
                name_match = re.search(r"name=([^\n]+)", entry)
                name = name_match.group(1).strip() if name_match else None
                holders_match = re.search(r"holders=([^\n]+)", entry)
                holders = holders_match.group(1).strip() if holders_match else None
                data_list.append((name, holders, uid))
   
    data_headers = ('Name', 'Holders', 'User')
    return data_headers, data_list, source_path

# Dumpsys - Accounts
@artifact_processor
def alex_live_account(context):
    """Parses the dumpsys account dump for entires"""
    files_found = context.get_files_found()
    source_path = files_found[0]
    data_list = []
    split_dumpsys_log(source_path)
    acc_dump, acc_ts = _DUMPSYS_DICT.get("account", (None, None))
   
    if acc_dump is None:
        logfunc('Dumpsys does not include an "account" part.')
    else:
        logtext = (
            'Dumpsys does include a \"account\" part without timestamp.'
            if acc_ts is None
            else f'Dumpsys does include a \"account\" part with timestamp: {str(acc_ts)}'
        )
        logfunc(logtext)
        acc_pattern = re.compile(
                r'Account\s*\{\s*name=([^,}]+)\s*,\s*type=([^}]+)\s*\}'
            )
        for line in acc_dump.splitlines():
            m = acc_pattern.search(line)
            if m:
                data_list.append((m.group(2), m.group(1)))

    data_headers = ('Type', 'Name')
    return data_headers, data_list, source_path

# Dumpsys - Batterystats
@artifact_processor
def alex_live_batterystats(context):
    """Parses the dumpsys batterystats dump for entires"""
    files_found = context.get_files_found()
    source_path = ""
    alex_device = ""
    for file_found in files_found:
        if "dumpsys_" in str(file_found):
            source_path = file_found
        elif "device_info_alex.json" in str(file_found):
            alex_device = file_found
    software = None
    try:
        with open(alex_device, encoding="utf-8") as info_file:
            info_data = json.load(info_file)
            software = next(
                (entry["Software"] for entry in info_data if "Software" in entry),
                None)
    except (OSError, UnicodeDecodeError):
        pass
    data_list = []
    split_dumpsys_log(source_path)
    batts_dump, batts_ts = _DUMPSYS_DICT.get("batterystats", (None, None))
    if batts_dump is None:
        logfunc('Dumpsys does not include an "batterystats" part.')
    else:
        logtext = (
            'Dumpsys does include a \"batterystats\" part without timestamp.'
            if batts_ts is None
            else f'Dumpsys does include a \"batterystats\" part with timestamp: {str(batts_ts)}'
        )
        logfunc(logtext)

        bs_dict = {4:  {30: 'WAKE_LOCK', 29: 'SENSOR_ON', 28: 'GPS_ON',
                        27: 'PHONE_SCANNING', 26: 'WIFI_RUNNING', 25: 'WIFI_FULL_LOCK',
                        24: 'WIFI_SCAN_LOCK', 23: 'WIFI_MULTICAST_ON', 22: 'AUDIO_ON',
                        21: 'VIDEO_ON', 20: 'SCREEN_ON', 19: 'BATTERY_PLUGGED',
                        18: 'PHONE_IN_CALL', 17: 'WIFI_ON', 16: 'BLUETOOTH_ON'},
                   5:  {31: 'CPU_RUNNING', 30: 'WAKE_LOCK', 29: 'GPS_ON',
                        28: 'WIFI_FULL_LOCK', 27: 'WIFI_SCAN', 26: 'WIFI_MULTICAST_ON',
                        25: 'MOBILE_RADIO_ACTIVE', 23: 'SENSOR_ON', 22: 'AUDIO_ON',
                        21: 'PHONE_SCANNING', 20: 'SCREEN_ON', 19: 'BATTERY_PLUGGED',
                        18: 'PHONE_IN_CALL', 16: 'BLUETOOTH_ON'},
                   6:  {31: 'CPU_RUNNING', 30: 'WAKE_LOCK', 29: 'GPS_ON',
                        28: 'WIFI_FULL_LOCK', 27: 'WIFI_SCAN', 26: 'WIFI_RADIO_ACTIVE',
                        25: 'MOBILE_RADIO_ACTIVE', 23: 'SENSOR_ON', 22: 'AUDIO_ON',
                        21: 'PHONE_SCANNING', 20: 'SCREEN_ON', 19: 'BATTERY_PLUGGED',
                        16: 'WIFI_MULTICAST_ON'},
                   9:  {31: 'CPU_RUNNING', 30: 'WAKE_LOCK', 29: 'GPS_ON',
                        28: 'WIFI_FULL_LOCK', 27: 'WIFI_SCAN', 26: 'WIFI_RADIO_ACTIVE',
                        25: 'MOBILE_RADIO_ACTIVE', 23: 'SENSOR_ON', 22: 'AUDIO_ON',
                        21: 'PHONE_SCANNING', 20: 'SCREEN_ON', 19: 'BATTERY_PLUGGED',
                        18: 'SCREEN_DOZE', 16: 'WIFI_MULTICAST_ON'}
                    }

        if software:
            major = int(str(software).split('.', maxsplit=1)[0])
            mask_versions = sorted(bs_dict.keys())
            selected_v = None
            for v in mask_versions:
                if major >= v:
                    selected_v = v
                else:
                    break
        else:
            selected_v = None
        BATTERY_RE = re.compile(r'\s(\d{3})\s')
        HEX_RE = re.compile(r'\s([0-9a-fA-F]{8})\s')
        reset_time = None
        lines = batts_dump.splitlines()
        for line in lines[:5]:
            if "TIME:" in line:
                ts_str = line.split("TIME:")[-1].strip()
                reset_time = parse_timestamp(ts_str, _DEVICE_TIME)
                break
        current_ts = None

        rel_offset = 0
        for line in lines:
            line = line.strip()
            if not line:
                continue
            current_ts = None
            time_part = None
            # new format - absolute times
            if re.match(r'^\d{2}-\d{2} ', line):
                parts = line.split()
                ts_str = parts[0] + " " + parts[1]
                current_ts = parse_timestamp(ts_str, _DEVICE_TIME)
                out_time = datetime.datetime.fromtimestamp(current_ts / 1000, tz=datetime.timezone.utc)
                battery = parts[2] if len(parts) > 2 else None
                if not (battery and battery.strip().isdigit() and len(battery.strip()) == 3):
                    continue
                hex_mask = parts[3] if len(parts) > 3 else None
                message = " ".join(parts[4:]) if len(parts) > 4 else ""
            # old format - relative times
            elif line.startswith("+") or re.match(r'^0(\s|$)', line):
                parts = line.split()
                time_part = parts[0]
                rel_ms = parse_relative_time(time_part)
                battery_match = BATTERY_RE.search(line)
                battery = battery_match.group(1) if battery_match else None
                if not (battery and battery.strip().isdigit() and len(battery.strip()) == 3):
                    if "TIME:" in line:
                        time_str = line.split("TIME:")[1].strip()
                        abs_time = parse_timestamp(time_str, _DEVICE_TIME)
                        if abs_time:
                            reset_time = abs_time
                            rel_offset = rel_ms
                    continue
                if reset_time is not None:
                    current_ts = reset_time + rel_ms - rel_offset
                else:
                    current_ts = None
                hex_match = HEX_RE.search(line)
                hex_mask = hex_match.group(1) if hex_match else None
                if hex_match:
                    message = line.split(hex_mask, 1)[1].strip()
                else:
                    message = ""
            else:
                # ignoring multiline - mostly Stats messages
                continue
            if current_ts:
                out_time = datetime.datetime.fromtimestamp(current_ts, tz=datetime.timezone.utc)
            elif time_part:
                out_time = time_part
            else:
                out_time = None
            if isinstance(hex_mask, str):
                bmask = int(hex_mask, 16)
            elif isinstance(hex_mask, int):
                bmask = hex_mask
            else:
                bmask = None
            if selected_v and bmask:
                b_mapping = bs_dict.get(selected_v)
                active_bits = []
                for bit, name in b_mapping.items():
                    if bmask & (1 << bit):
                        active_bits.append(name)
                stat1 = ", ".join(active_bits)
            else:
                stat1 = None

            data_list.append((out_time, battery, hex_mask, stat1, message))
    data_headers = (('Time', 'datetime'), 'Battery Level', 'Mask', 'States (from Mask)', 'Message')
    return data_headers, data_list, source_path

# App Ops
@artifact_processor
def alex_live_appops(context):
    """Parses the app_ops.json included in an ALEX PRFS Backup"""
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "app_ops.json")
    data_list = []
    try:
        with open(source_path, "r", encoding="utf-8") as app_ops_file:
            app_ops_data = json.load(app_ops_file)
        for package, permissions in app_ops_data.items():
            for permission, value in permissions.items():
                state = None
                allowtime = None
                rejecttime = None
                if isinstance(value, str):
                    if value == "ignore":
                        continue
                    state = value
                elif isinstance(value, list):
                    state = value[0]
                    if state == "ignore":
                        continue
                    for entry in value[1:]:
                        if not isinstance(entry, dict):
                            continue
                        if "time" in entry:
                            try:
                                if isinstance(entry["time"], int):
                                    atime = entry["time"]
                                else:
                                    atime = int(entry["time"].split()[0])
                                allowtime = datetime.datetime.fromtimestamp(atime, tz=datetime.timezone.utc)
                            except ValueError:
                                pass
                        if "rejectTime" in entry:
                            try:
                                if isinstance(entry["rejectTime"], int):
                                    rtime = entry["rejectTime"]
                                else:
                                    rtime = int(entry["rejectTime"].split()[0])
                                rejecttime = datetime.datetime.fromtimestamp(rtime, tz=datetime.timezone.utc)
                            except ValueError:
                                pass
                data_list.append((allowtime, rejecttime, package, permission, state))  
    except (OSError, UnicodeDecodeError):
        pass

    data_headers = (('Access Timestamp', 'datetime'), ('Reject Timestamp', 'datetime'), 'Package Name', 'Permission', 'Value')

    return data_headers, data_list, source_path

# Logcat (Android 10 and up as these allow the epoch-timestamps)
@artifact_processor
def alex_live_logcat(context):
    """Parses the logcat logs"""
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "logcat.txt")
    data_list = []
    log_pattern = re.compile(
        r'^\s*'
        r'(\d+(?:\.\d+)?)\s+'
        r'(\d+)\s+'
        r'(\d+)\s+'
        r'([VDIWEF])\s+'
        r'(\S.*?)\s*:\s*'
        r'(.*)$'
    )

    log_levels = {
        "V" : "Verbose",
        "D" : "Debug",
        "I" : "Info",
        "W" : "Warn",
        "E" : "Error",
        "F" : "Fatal",
        "S" : "Silent"
    }
    with open(source_path, "r", encoding="utf-8") as logcat_file:
        for line in logcat_file:
            line = line.expandtabs().rstrip()
            match = log_pattern.match(line)
            if match:
                l_timestamp = match.group(1)
                l_time = datetime.datetime.fromtimestamp(float(l_timestamp), tz=datetime.timezone.utc)
                l_pid = match.group(2)
                l_tid = match.group(3)
                l_lvl = match.group(4)
                l_lvl_long = log_levels.get(l_lvl, l_lvl)
                l_tag = match.group(5)
                l_message = match.group(6)
                data_list.append((l_time, l_pid, l_tid, l_lvl_long, l_tag, l_message))
    data_headers = (('Timestamp', 'datetime'),  'PID', 'TID', 'Level', 'Tag', 'Message')
    return data_headers, data_list, source_path
