__artifacts_v2__ = {
    "rethinkdns_dns_queries": {
        "name": "RethinkDNS - DNS Queries",
        "description": "Parses the per-app DNS query log from the RethinkDNS Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "RethinkDNS",
        "sample_data": {
            "emu_a15_oss_v6": "RethinkDNS 0.5.6 | 117 rows",
        },
        "notes": "One row per entry in the DnsLogs table of databases/rethink_logs.db. RethinkDNS "
                 "runs as a local VPN and resolves DNS for the whole device, so while it is "
                 "running it records every name each app asked to resolve. Each row carries the "
                 "Query (the domain), the App and Package that asked for it, the record type as "
                 "the app labels it (Query Type, such as IPv4, IPv6 or HTTP Service Binding), the "
                 "Resolved IPs it got back with their country prefix, and the Resolver used. Time "
                 "is Unix milliseconds reported as UTC. Blocked is the app's own flag for a query "
                 "it refused, and Blocklists names the list that caused it, so a blocked row "
                 "records a name that was asked for and not resolved. Cached marks an answer "
                 "served from the app's cache rather than fetched, which means the query was made "
                 "but the resolver was not contacted for it. Latency and Response Time are the "
                 "app's own measurement in milliseconds; the table also stores a responseTime column "
                 "which held the identical value on all 79 tested rows, so only Latency (ms) is "
                 "reported. On the tested device the log held the "
                 "domains browsed in Brave and Firefox alongside background traffic from "
                 "Syncthing and Google Play services, each attributed to its own package. The log "
                 "only covers periods when RethinkDNS was running, so an absence is not evidence "
                 "a name was never resolved. Status was COMPLETE and DNS Type was 0 on every "
                 "tested row, and both are reported as stored because neither vocabulary is "
                 "documented in a source that was checked.",
        "paths": ('*/com.celzero.bravedns/databases/rethink_logs.db*',),
        "output_types": "standard",
        "artifact_icon": "globe",
    },
    "rethinkdns_connections": {
        "name": "RethinkDNS - Network Connections",
        "description": "Parses the per-app network connection log from the RethinkDNS Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "RethinkDNS",
        "sample_data": {
            "emu_a15_oss_v6": "RethinkDNS 0.5.6 | 214 rows",
        },
        "notes": "One row per entry in the ConnectionTracker table of databases/rethink_logs.db. "
                 "While RethinkDNS is running every network connection the device makes passes "
                 "through it, so each row records one connection with the App and Package that "
                 "opened it, its Linux UID, the destination IP Address and Port, the Country the "
                 "app resolved that address to, the bytes sent and received, and the connection "
                 "Duration. Timestamp is Unix milliseconds reported as UTC. Protocol is decoded "
                 "from the IANA protocol numbers, 1 ICMP, 6 TCP and 17 UDP; any other value is "
                 "reported as stored. Blocked and Blocked By Rule record whether the app stopped "
                 "the connection and which of its rules did so. DNS Query is the name that "
                 "resolved to this address where the app could associate the two, which is what "
                 "ties an IP back to a domain. On the tested device 113 connections were recorded "
                 "across seven packages, with Syncthing contacting relay servers in several "
                 "countries and the browsers contacting addresses for the domains loaded in them. "
                 "This log "
                 "records the app that opened a connection, which is not the same as a person "
                 "using that app at that moment: background sync and telemetry appear here "
                 "exactly like foreground browsing. It also only covers periods when RethinkDNS "
                 "was running. Blocklists was empty on every tested row because no blocklist was "
                 "enabled, so nothing was blocked; Connection Type held one value, Unmetered, "
                 "because the tested device was on wifi throughout; and Android User held 0 "
                 "because that image has a single user. All three are kept because each is a "
                 "real statement about the capture rather than a missing derivation.",
        "paths": ('*/com.celzero.bravedns/databases/rethink_logs.db*',),
        "output_types": "standard",
        "artifact_icon": "share-2",
    },
    "rethinkdns_events": {
        "name": "RethinkDNS - App Events",
        "description": "Parses the app's own event log from the RethinkDNS Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "RethinkDNS",
        "sample_data": {
            "emu_a15_oss_v6": "RethinkDNS 0.5.6 | 25 rows",
        },
        "notes": "One row per entry in the Events table of databases/rethink_logs.db, which is the "
                 "app's own record of its lifecycle. Each row has an Event Type, a Severity, a "
                 "Message, the Source component and a User Action flag. The event types seen on "
                 "the tested device were VPN_START, VPN_RESTART, TUN_UPDATE, APP_REFRESH and "
                 "UI_TOGGLE. These matter because the two log artifacts above only cover periods "
                 "when the VPN was running: a VPN_START bounds the beginning of a covered period, "
                 "so this table is how an examiner tells a gap in the connection log from a "
                 "period of no activity. User Action is the app's own flag for an event it "
                 "attributes to interaction rather than to its own scheduling, and it was 0 on "
                 "every row of the tested device. Timestamp is Unix milliseconds reported as UTC. "
                 "The event type and severity vocabularies are reported as stored. The app's "
                 "other store, databases/bravedns.db, holds a single AppInfo table which is "
                 "RethinkDNS's own inventory of the 293 installed packages with a per-app "
                 "firewall setting; on the tested device 292 of those carried the same default "
                 "and the only differing row was RethinkDNS excluding itself, so it recorded no "
                 "configuration a person had made and is not parsed. RethinkLog and IpInfo in "
                 "this database were present and empty and are likewise not parsed.",
        "paths": ('*/com.celzero.bravedns/databases/rethink_logs.db*',),
        "output_types": "standard",
        "artifact_icon": "power",
    },
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/rethink_logs.db'

# IANA Protocol Numbers registry.
PROTOCOLS = {1: 'ICMP', 6: 'TCP', 17: 'UDP', 58: 'ICMPv6'}


def _db_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(DB_SUFFIX)]


def _ms(value):
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value) // 1000)
    except (TypeError, ValueError):
        return ''


def _yesno(value):
    if value in (1, '1'):
        return 'Yes'
    if value in (0, '0'):
        return 'No'
    return ''


def _protocol(value):
    try:
        key = int(value)
    except (TypeError, ValueError):
        return '' if value in (None, '') else f'{value} (as stored)'
    if key in PROTOCOLS:
        return PROTOCOLS[key]
    return f'{key} (as stored)'


@artifact_processor
def rethinkdns_dns_queries(context):
    query = '''SELECT time, queryStr, appName, packageName, typeName, responseIps,
                      isBlocked, blockLists, resolver, latency,
                      isCached, status, dnsType, uid, id
               FROM DnsLogs ORDER BY time DESC'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                _ms(r[0]), r[1] or '', r[2] or '', r[3] or '', r[4] or '', r[5] or '',
                _yesno(r[6]), r[7] or '', r[8] or '', r[9], _yesno(r[10]),
                r[11] or '', r[12], r[13], r[14],
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Time', 'datetime'), 'Query', 'App', 'Package', 'Query Type', 'Resolved IPs',
        'Blocked', 'Blocklists', 'Resolver', 'Latency (ms)',
        'Cached', 'Status (as stored)', 'DNS Type (as stored)', 'UID', 'Query ID',
        'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def rethinkdns_connections(context):
    query = '''SELECT timeStamp, appName, packageName, ipAddress, port, protocol,
                      flag, dnsQuery, isBlocked, blockedByRule, blocklists,
                      downloadBytes, uploadBytes, duration, connType, uid, usrId,
                      connId, message, id
               FROM ConnectionTracker ORDER BY timeStamp DESC'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                _ms(r[0]), r[1] or '', r[2] or '', r[3] or '', r[4], _protocol(r[5]),
                r[6] or '', r[7] or '', _yesno(r[8]), r[9] or '', r[10] or '',
                r[11], r[12], r[13], r[14] or '', r[15], r[16], r[17] or '',
                r[18] or '', r[19],
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Timestamp', 'datetime'), 'App', 'Package', 'IP Address', 'Port', 'Protocol',
        'Country', 'DNS Query', 'Blocked', 'Blocked By Rule', 'Blocklists',
        'Download Bytes', 'Upload Bytes', 'Duration (s)', 'Connection Type', 'UID',
        'Android User', 'Connection ID', 'Message', 'Record ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def rethinkdns_events(context):
    query = '''SELECT timestamp, eventType, severity, message, source, userAction,
                      details, id
               FROM Events ORDER BY timestamp DESC'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                _ms(r[0]), r[1] or '', r[2] or '', r[3] or '', r[4] or '',
                _yesno(r[5]), r[6] or '', r[7],
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Timestamp', 'datetime'), 'Event Type (as stored)', 'Severity (as stored)',
        'Message', 'Source', 'User Action', 'Details', 'Event ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
