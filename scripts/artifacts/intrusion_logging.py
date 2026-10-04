"""
Logs need to be generated manually and processed as the input. See androidqf process at the following link for more info:
https://securitylab.amnesty.org/latest/2026/05/android-intrusion-logging-as-a-new-source-of-data-for-consensual-forensic-analysis/
"""

__artifacts_v2__ = {
    "ail_dns_events": {
        "name": "Android Intrusion Logging - DNS Events",
        "description": "Parses DNS lookup resolution logs including requested hostname and resolved IP addresses.",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2026-08-05",
        "last_update_date": "2026-08-29",
        "requirements": "none",
        "category": "Android Intrusion Logging",
        "notes": "Reads date-named .txt intrusion logs from the intrusion_logs folder an androidqf acquisition creates (Reference: Amnesty International Security Lab, 'Android Intrusion Logging as a new source of data for consensual forensic analysis', https://securitylab.amnesty.org/latest/2026/05/android-intrusion-logging-as-a-new-source-of-data-for-consensual-forensic-analysis/), from a Download/Intrusion Logging folder, or at the root of a decrypted log export processed directly as the input. In the tested full filesystem extraction (Pixel 8 Pro, Android 17) the on-device Download/Intrusion Logging folder holds the downloaded logs as a zip archive; nested archives are not opened, so extract that archive and process it as its own input to parse these events. Timestamp is the event_time value read as Unix time, with the unit taken from the value's magnitude, reported to the whole second in UTC. A line that does not parse as JSON is skipped. IP Count is the event's ip_addresses_count, or the number of listed addresses when the event carries none.",
        "paths": (
            '*/intrusion_logs/*2[0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]*.txt',
            '*/Intrusion Logging/*2[0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]*.txt',
            'root/2[0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]*.txt',
        ),
        "sample_data": {
            "hc_pixel8pro_a17_ail": "Android 17 | decrypted Intrusion Logging download | 24,082 rows",
            "hc_pixel8pro_a17": "Android 17 | logs zipped in Download/Intrusion Logging, nested archive not opened | 0 rows",
        },
        "output_types": "standard",
        "artifact_icon": "world",
    },
    "ail_connect_events": {
        "name": "Android Intrusion Logging - Connection Events",
        "description": "Parses connect_event lines from the intrusion logs, with the package name, destination IP address and port.",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2026-08-05",
        "last_update_date": "2026-08-29",
        "requirements": "none",
        "category": "Android Intrusion Logging",
        "notes": "Reads date-named .txt intrusion logs from the intrusion_logs folder an androidqf acquisition creates (Reference: Amnesty International Security Lab, 'Android Intrusion Logging as a new source of data for consensual forensic analysis', https://securitylab.amnesty.org/latest/2026/05/android-intrusion-logging-as-a-new-source-of-data-for-consensual-forensic-analysis/), from a Download/Intrusion Logging folder, or at the root of a decrypted log export processed directly as the input. In the tested full filesystem extraction (Pixel 8 Pro, Android 17) the on-device Download/Intrusion Logging folder holds the downloaded logs as a zip archive; nested archives are not opened, so extract that archive and process it as its own input to parse these events. Timestamp is the event_time value read as Unix time, with the unit taken from the value's magnitude, reported to the whole second in UTC. A line that does not parse as JSON is skipped.",
        "paths": (
            '*/intrusion_logs/*2[0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]*.txt',
            '*/Intrusion Logging/*2[0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]*.txt',
            'root/2[0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]*.txt',
        ),
        "sample_data": {
            "hc_pixel8pro_a17_ail": "Android 17 | decrypted Intrusion Logging download | 16,298 rows",
            "hc_pixel8pro_a17": "Android 17 | logs zipped in Download/Intrusion Logging, nested archive not opened | 0 rows",
        },
        "output_types": "standard",
        "artifact_icon": "wifi",
    },
    "ail_security_events": {
        "name": "Android Intrusion Logging - Security Events",
        "description": "Parses security_event lines from the intrusion logs, with the action name, one process, package or uid value and the remaining fields in Details. Fields named process, package_name, package or pkg that are not the one shown in Process/Package/UID are not reported.",
        "author": "Kevin Pagano (@stark4n6)",
        "creation_date": "2026-08-05",
        "last_update_date": "2026-08-29",
        "requirements": "none",
        "category": "Android Intrusion Logging",
        "notes": "Reads date-named .txt intrusion logs from the intrusion_logs folder an androidqf acquisition creates (Reference: Amnesty International Security Lab, 'Android Intrusion Logging as a new source of data for consensual forensic analysis', https://securitylab.amnesty.org/latest/2026/05/android-intrusion-logging-as-a-new-source-of-data-for-consensual-forensic-analysis/), from a Download/Intrusion Logging folder, or at the root of a decrypted log export processed directly as the input. In the tested full filesystem extraction (Pixel 8 Pro, Android 17) the on-device Download/Intrusion Logging folder holds the downloaded logs as a zip archive; nested archives are not opened, so extract that archive and process it as its own input to parse these events. Timestamp is the event_time value read as Unix time, with the unit taken from the value's magnitude, reported to the whole second in UTC. A line that does not parse as JSON is skipped.",
        "paths": (
            '*/intrusion_logs/*2[0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]*.txt',
            '*/Intrusion Logging/*2[0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]*.txt',
            'root/2[0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]*.txt',
        ),
        "sample_data": {
            "hc_pixel8pro_a17_ail": "Android 17 | decrypted Intrusion Logging download | 2,352 rows",
            "hc_pixel8pro_a17": "Android 17 | logs zipped in Download/Intrusion Logging, nested archive not opened | 0 rows",
        },
        "output_types": "standard",
        "artifact_icon": "shield",
    }
}

import json
from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc


@artifact_processor
def ail_dns_events(context):
    files_found = context.get_files_found()

    data_list = []
    source_path = ""
    source_paths = set()

    for source_path in files_found:
        source_paths.add(str(source_path))

        with open(source_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or '"dns_event"' not in line:
                    continue
                try:
                    data = json.loads(line)
                    if "dns_event" in data:
                        event = data["dns_event"]
                        timestamp = convert_unix_ts_to_utc(event.get("event_time"))
                        event_id = event.get("event_id", "")
                        package_name = event.get("package_name", "")
                        hostname = event.get("hostname", "")
                        
                        raw_ips = event.get("ip_addresses", [])
                        ip_addresses = ", ".join([ip.lstrip('/') for ip in raw_ips])
                        ip_count = event.get("ip_addresses_count", len(raw_ips))

                        data_list.append((timestamp, event_id, package_name, hostname, ip_addresses, ip_count, context.get_relative_path(source_path)))
                except json.JSONDecodeError:
                    continue

    data_headers = (('Timestamp', 'datetime'), 'Event ID', 'Package Name', 'Hostname', 'Resolved IPs', 'IP Count', 'Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def ail_connect_events(context):
    files_found = context.get_files_found()

    data_list = []
    source_path = ""
    source_paths = set()

    for source_path in files_found:
        source_paths.add(str(source_path))
        with open(source_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or '"connect_event"' not in line:
                    continue
                try:
                    data = json.loads(line)
                    if "connect_event" in data:
                        event = data["connect_event"]
                        timestamp = convert_unix_ts_to_utc(event.get("event_time"))
                        event_id = event.get("event_id", "")
                        package_name = event.get("package_name", "")
                        ip_address = event.get("ip_address", "").lstrip('/')
                        port = event.get("port", "")

                        data_list.append((timestamp, event_id, package_name, ip_address, port, context.get_relative_path(source_path)))
                except json.JSONDecodeError:
                    continue

    data_headers = (('Timestamp', 'datetime'), 'Event ID', 'Package Name', 'Destination IP', 'Port', 'Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))
    
@artifact_processor
def ail_security_events(context):
    files_found = context.get_files_found()

    data_list = []
    source_path = ""
    source_paths = set()
    package_actions = ("package_installed", "package_updated", "package_uninstalled")

    for source_path in files_found:
        source_paths.add(str(source_path))
        with open(source_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or '"security_event"' not in line:
                    continue
                try:
                    data = json.loads(line)
                    if "security_event" in data:
                        event = data["security_event"]
                        timestamp = convert_unix_ts_to_utc(event.get("event_time"))
                        event_id = event.get("event_id", "")
                        
                        # Identify action type and extract dynamic payload
                        action_type = "Unknown"
                        process_or_pkg = ""
                        details_list = []

                        for key, value in event.items():
                            if key in ("event_id", "event_time"):
                                continue
                            
                            action_type = key
                            if isinstance(value, dict):
                                if action_type in package_actions:
                                    process_or_pkg = value.get(
                                        "package_name", value.get("package", value.get("pkg", ""))
                                    )
                                else:
                                    process_or_pkg = value.get(
                                        "process", value.get("package_name", value.get("uid", ""))
                                    )

                                # Build detail string excluding process/package_name extracted above
                                for sub_k, sub_v in value.items():
                                    if sub_k not in ("process", "package_name", "package", "pkg"):
                                        details_list.append(f"{sub_k}: {sub_v}")
                            elif value:
                                details_list.append(str(value))

                        details = ", ".join(details_list)
                        data_list.append((timestamp, event_id, action_type, process_or_pkg, details, context.get_relative_path(source_path)))

                except json.JSONDecodeError:
                    continue

    data_headers = (('Timestamp', 'datetime'), 'Event ID', 'Action Type', 'Process/Package/UID', 'Details', 'Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))