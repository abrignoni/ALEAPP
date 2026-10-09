__artifacts_v2__ = {
  
    "sdhms_config_reloads": {
        "name": "SDHMS Config Reload History",
        "description": "Rows of the config_history table of the SDHMS anomaly.db: time, reason, configuration key and version as stored. More info: https://bebinary4n6.blogspot.com/2026/01/inside-android-samsung-dhms-extracting.html",
        "author": "Marco Neumann {kalinko@be-binary.de}, @AlexisBrignoni, Codex",
        "creation_date": "2026-01-10",
        "last_update_date": "2026-10-06",
        "requirements": "",
        "category": "Samsung Device Health Management Service",
        "notes": "Every distinct main database state is read; known canonical aliases collapse only when main/WAL/journal bytes agree. Conflicts remain separate. Combined inputs carry per-row evidence sources. The post linked in the description reports that in its test data most rows had the "
                 "reason BOOT_COMPLETED and that the last five matched that author's device "
                 "reboots. The reason column is reported as stored.",
        "paths": ('*/com.sec.android.sdhms/databases/anomaly.db*'),
        "output_types": "all",
        "artifact_icon": "settings",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.sdhms | 29 rows",
            "galaxys10_a10": "Android 10 | com.sec.android.sdhms | 11 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.sdhms | 9 rows",
            "samsungs20_a13": "Android 13 | com.sec.android.sdhms | 28 rows",
            "sharon_a14": "Android 14 | com.sec.android.sdhms | 100 rows",
        }
    },
    "sdhms_netstat": {
        "name": "SDHMS Netstat",
        "description": "Rows of the NETSTAT table of the SDHMS thermal_log database: a time window, package name, uid and net_usage as stored. More info: https://bebinary4n6.blogspot.com/2026/01/inside-android-samsung-dhms-extracting.html",
        "author": "Marco Neumann {kalinko@be-binary.de}, @AlexisBrignoni, Codex",
        "creation_date": "2026-01-10",
        "last_update_date": "2026-10-09",
        "requirements": "",
        "category": "Samsung Device Health Management Service",
        "notes": "The post linked in the description describes net_usage as bytes transferred in the "
                 "time window; that unit was not measured here, so the column is headed Net Usage "
                 "(as stored). The uid column is reported as UID (as stored), without inferred "
                 "package identity. Start Time and End Time are read as Unix milliseconds. Only the "
                 "distinct main databases are read. Known aliases collapse only when main/WAL/journal "
                 "bytes agree; conflicting states remain separate. Multi-input rows include their "
                 "evidence-relative Source File.",
        "paths": ('*/com.sec.android.sdhms/databases/thermal_log*'),
        "output_types": "all",
        "artifact_icon": "chart-bar-popular",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.sdhms | 1582 rows",
            "galaxys10_a10": "Android 10 | com.sec.android.sdhms | 839 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.sdhms | 1154 rows",
            "samsungs20_a13": "Android 13 | com.sec.android.sdhms | 324 rows",
            "sharon_a14": "Android 14 | com.sec.android.sdhms | 1160 rows",
        }
    },
    "sdhms_temperature": {
        "name": "SDHMS Temperature Logs",
        "description": "SDHMS temperature log, one row per reading with each sensor column divided by 10. More info: https://bebinary4n6.blogspot.com/2026/01/inside-android-samsung-dhms-extracting.html",
        "author": "Marco Neumann {kalinko@be-binary.de}, @AlexisBrignoni, Codex",
        "creation_date": "2026-01-10",
        "last_update_date": "2026-10-09",
        "requirements": "",
        "category": "Samsung Device Health Management Service",
        "notes": "Every distinct main database state is read; known canonical aliases collapse only when main/WAL/journal bytes agree. Conflicts remain separate. Combined inputs carry per-row evidence sources. The post linked in the description says the values are stored in degrees Celsius "
                 "times 10 and that on devices with different regional settings they may be stored "
                 "in degrees Fahrenheit, so the unit is not established for every device.",
        "paths": ('*/com.sec.android.sdhms/databases/thermal_log*'),
        "output_types": "all",
        "artifact_icon": "thermometer",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.sdhms | 567 rows",
            "galaxys10_a10": "Android 10 | com.sec.android.sdhms | 1237 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.sdhms | 356 rows",
            "samsungs20_a13": "Android 13 | com.sec.android.sdhms | 535 rows",
            "sharon_a14": "Android 14 | com.sec.android.sdhms | 443 rows",
        }
    },
    "sdhms_cpustats": {
        "name": "SDHMS CPU Stats",
        "description": "Rows of the CPUSTAT table of the SDHMS thermal_log database: a time window, uptime, process name, uid, pid and the process_usage figure as stored. More info: https://bebinary4n6.blogspot.com/2026/01/inside-android-samsung-dhms-extracting.html",
        "author": "Marco Neumann {kalinko@be-binary.de}, @AlexisBrignoni, Codex",
        "creation_date": "2026-01-10",
        "last_update_date": "2026-10-06",
        "requirements": "",
        "category": "Samsung Device Health Management Service",
        "notes": "The post linked in the description describes process_usage as CPU time used in the "
                 "time window, scaled and dependent on the number of cores, and uptime as seconds. "
                 "The uid column is reported as UID (as stored), without inferred package identity. "
                 "Start Time and End Time are "
                 "read as Unix milliseconds. Distinct main databases are read. Known aliases "
                 "collapse only when main/WAL/journal bytes agree; conflicting states remain "
                 "separate. Multi-input rows include their evidence-relative Source File.",
        "paths": ('*/com.sec.android.sdhms/databases/thermal_log*'),
        "output_types": "all",
        "artifact_icon": "cpu",
        "sample_data": {
            "anne_a15": "Android 15 | com.sec.android.sdhms | 963 rows",
            "galaxys10_a10": "Android 10 | com.sec.android.sdhms | 1045 rows",
            "samsunga53_a14": "Android 14 | com.sec.android.sdhms | 491 rows",
            "samsungs20_a13": "Android 13 | com.sec.android.sdhms | 595 rows",
            "sharon_a14": "Android 14 | com.sec.android.sdhms | 483 rows",
        }
    }

}

# Android Samsung Device Health Management Service SDHMS (com.sec.android.sdhms)
# Author:  Marco Neumann (kalinko@be-binary.de)
#
# Requirements:
import hashlib

from scripts.artifacts.storagePathViews import canonical_path
from scripts.ilapfuncs import logfunc, artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records, null_absent_columns

def _stat_sources(context):
    """Collapse known aliases only when main and logical sidecar bytes agree."""
    paths = []
    seen = set()
    for candidate in context.get_files_found():
        path = str(candidate)
        if path.endswith(('wal', 'shm', 'journal')):
            continue
        try:
            state = []
            for suffix in ('', '-wal', '-journal'):
                try:
                    with open(path + suffix, 'rb') as source:
                        digest = hashlib.sha256()
                        for chunk in iter(lambda source=source: source.read(1024 * 1024), b''):
                            digest.update(chunk)
                    state.append(digest.hexdigest())
                except FileNotFoundError:
                    if not suffix:
                        raise
                    state.append(None)
            identity = (canonical_path(context.get_relative_path(path))[0], tuple(state))
        except OSError as error:
            logfunc(f'SDHMS: skipping unreadable database {context.get_relative_path(path)}: {error}')
            continue
        if identity not in seen:
            seen.add(identity)
            paths.append(path)
    return paths


@artifact_processor
def sdhms_config_reloads(context):
    source_paths = _stat_sources(context)
    multiple_sources = len(source_paths) > 1
    reported_sources = set()

    query = ('''
        SELECT
        time,
        reason,
        config_key,
        config_version
        FROM config_history
    ''')

    data_list = []

    for source_path in source_paths:
        columns = {str(row[1]).lower() for row in
                   get_sqlite_db_records(source_path, "PRAGMA table_info('config_history')")}
        if not ('time' in columns):
            logfunc(f'SDHMS: unsupported config_history schema in {context.get_relative_path(source_path)}; '
                    'required timestamp column absent, continuing other sources')
            continue
        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        for row in db_records:
            reported_sources.add(source_path)
            config_reload_time = convert_unix_ts_to_utc(int(row[0])/1000)
            reason = row[1]
            config_key = row[2]
            config_version = row[3]

            data_list.append(( config_reload_time, reason, config_key, config_version))
            if multiple_sources:
                data_list[-1] += (context.get_relative_path(source_path),)

    data_headers = (
                        ('Config Reload Time', 'datetime'),
                        'Config Reload Reason',
                        'Config Key',
                        'Config Version'
                    )

    if multiple_sources:
        data_headers += ('Source File',)
    return data_headers, data_list, '\n'.join(sorted(reported_sources))

@artifact_processor
def sdhms_netstat(context):
    source_paths = _stat_sources(context)
    multiple_sources = len(source_paths) > 1
    reported_sources = set()

    query = ('''
        SELECT
        start_time,
        end_time,
        id,        
        package_name,
        uid,
        net_usage
        FROM NETSTAT
    ''')

    data_list = []

    for source_path in source_paths:
        columns = {str(row[1]).lower() for row in
                   get_sqlite_db_records(source_path, "PRAGMA table_info('NETSTAT')")}
        if not {'start_time', 'end_time'}.issubset(columns):
            logfunc(f'SDHMS: unsupported NETSTAT schema in {context.get_relative_path(source_path)}; '
                    'required start_time/end_time columns absent, continuing other sources')
            continue
        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        for row in db_records:
            reported_sources.add(source_path)
            start_time = convert_unix_ts_to_utc(int(row[0])/1000)
            end_time = convert_unix_ts_to_utc(int(row[1])/1000)
            entry_id = row[2]
            package_name = row[3]
            package_uid = row[4]
            net_usage = row[5]

            data_list.append(( start_time, end_time, entry_id, package_name, package_uid, net_usage))

            if multiple_sources:
                data_list[-1] += (context.get_relative_path(source_path),)

    data_headers = (
                        ('Start Time', 'datetime'),
                        ('End Time', 'datetime'),
                        'Entry ID',
                        'Package Name',
                        'UID (as stored)',
                        'Net Usage (as stored)'
                    )

    if multiple_sources:
        data_headers += ('Source File',)
    return data_headers, data_list, '\n'.join(sorted(reported_sources))

# Older releases of this store call the temperature timestamp "time" rather than
# "timestamp". Both hold the same millisecond epoch in the same table, so the
# column is aliased rather than reported empty; substituting NULL would drop the
# time from every row on those devices. Observed on galaxys10_a10 (time) and
# sharon_a14 (timestamp).
TEMPERATURE_TIME_ALIASES = ('timestamp', 'time')


def _temperature_query(source_path, query):
    """Point the timestamp column at whichever spelling this database uses."""
    columns = {column[1].lower() for column in
               get_sqlite_db_records(source_path, 'PRAGMA table_info("TEMPERATURE")')}
    if not columns or 'timestamp' in columns:
        return query
    for candidate in TEMPERATURE_TIME_ALIASES[1:]:
        if candidate in columns:
            return query.replace('timestamp,', f'{candidate} AS timestamp,', 1)
    return query


@artifact_processor
def sdhms_temperature(context):
    source_paths = _stat_sources(context)
    multiple_sources = len(source_paths) > 1
    reported_sources = set()

    query = ('''
        SELECT
        timestamp,
        skin_temp/10.0 [Chassis Temperature],
        ap_temp/10.0 [Processor Temperature],
        bat_temp/10.0 [Battery Temperature],
        usb_temp/10.0 [USB Temperature],
        chg_temp/10.0 [Charging IC Temperature],
        pa_temp/10.0 [Cellular Radio Temperature],
        wifi_temp/10.0 [WiFi Temperature]
        FROM TEMPERATURE
    ''')

    data_list = []

    for source_path in source_paths:
        columns = {str(row[1]).lower() for row in
                   get_sqlite_db_records(source_path, "PRAGMA table_info('TEMPERATURE')")}
        if not (bool(set(TEMPERATURE_TIME_ALIASES) & columns)):
            logfunc(f'SDHMS: unsupported TEMPERATURE schema in {context.get_relative_path(source_path)}; '
                    'required timestamp column absent, continuing other sources')
            continue
        source_query = _temperature_query(source_path, query)
        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, source_query))

        for row in db_records:
            reported_sources.add(source_path)
            timestamp = convert_unix_ts_to_utc(int(row[0])/1000)
            skin_temp = row[1]
            ap_temp = row[2]
            bat_temp = row[3]
            usb_temp = row[4]
            chg_temp = row[5]
            pa_temp = row[6]
            wifi_temp = row[7]

            data_list.append((  timestamp,
                                skin_temp,
                                ap_temp,
                                bat_temp,
                                usb_temp,
                                chg_temp,
                                pa_temp,
                                wifi_temp)
                            )
            if multiple_sources:
                data_list[-1] += (context.get_relative_path(source_path),)

    data_headers = (
                        ('Timestamp', 'datetime'),
                        'Chassis Temperature',
                        'Processor Temperature',
                        'Battery Temperature',
                        'USB Temperature',
                        'Charging IC Temperature',
                        'Cellular Radio Temperature',
                        'WiFi Temperature'
                    )

    if multiple_sources:
        data_headers += ('Source File',)
    return data_headers, data_list, '\n'.join(sorted(reported_sources))

@artifact_processor
def sdhms_cpustats(context):
    source_paths = _stat_sources(context)
    multiple_sources = len(source_paths) > 1
    reported_sources = set()

    query = ('''
        SELECT
        start_time,
        end_time,
        uptime [Uptime],
        process_name [Process Name],
        uid [UID (as stored)],
        pid [Process ID],
        process_usage [Process Usage]
        FROM CPUSTAT
    ''')

    data_list = []

    for source_path in source_paths:
        columns = {str(row[1]).lower() for row in
                   get_sqlite_db_records(source_path, "PRAGMA table_info('CPUSTAT')")}
        if not {'start_time', 'end_time'}.issubset(columns):
            logfunc(f'SDHMS: unsupported CPUSTAT schema in {context.get_relative_path(source_path)}; '
                    'required start_time/end_time columns absent, continuing other sources')
            continue
        db_records = get_sqlite_db_records(source_path, null_absent_columns(source_path, query))

        for row in db_records:
            reported_sources.add(source_path)
            start_time = convert_unix_ts_to_utc(int(row[0])/1000)
            end_time = convert_unix_ts_to_utc(int(row[1])/1000)
            uptime = row[2]
            process_name = row[3]
            package_id = row[4]
            process_id = row[5]
            process_cpu_usage = row[6]

            data_list.append((  start_time,
                                end_time,
                                uptime,
                                process_name,
                                package_id,
                                process_id,
                                process_cpu_usage))

            if multiple_sources:
                data_list[-1] += (context.get_relative_path(source_path),)

    data_headers = (
                        ('Start Time', 'datetime'),
                        ('End Time', 'datetime'),
                        'Uptime',
                        'Process Name',
                        'UID (as stored)',
                        'Process ID',
                        'Process CPU Usage'
                    )

    if multiple_sources:
        data_headers += ('Source File',)
    return data_headers, data_list, '\n'.join(sorted(reported_sources))
