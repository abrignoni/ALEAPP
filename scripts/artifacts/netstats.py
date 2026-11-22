__artifacts_v2__ = {
    "netstats": {
        "name": "Netstats",
        "description": "Network data usage per UID, and rows with no UID detail (UID -1), from the "
                       "binary system netstats collections, bucketed over time, with the connection "
                       "type, subscriber ID and network ID of each network identity",
        "author": "Alex Caithness",
        "creation_date": "2026-08-05",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "Network Usage",
        "notes": "The binary format is read per NetworkStatsCollection.java, "
                 "NetworkIdentitySet.java and NetworkStatsHistory.java under "
                 "framework-t/src/android/net in AOSP packages/modules/Connectivity. The "
                 "release the layout was taken from is not recorded in this module. Only the "
                 "unified collection format "
                 "(version 16) is parsed. A file with any other collection version is skipped "
                 "and named in the run log. So is a file that fails to parse for any other "
                 "reason. No file was skipped this way on the sample_data images. Identity set version 8 is not in "
                 "NetworkIdentitySet.java at the android-13.0.0_r1, android-14.0.0_r1, "
                 "android-15.0.0_r1 or android-16.0.0_r1 tags. It was present on anne_a15, "
                 "hc_pixel8pro_a16, hc_pixel8pro_a17 and kevin_pocox7_a15. This module reads 8 "
                 "more bytes per identity for it and does not report them.\n"
                 "Bucket Start is the start of the bucket in milliseconds since the Unix epoch "
                 "(NetworkStatsHistory.java), shown in UTC. Duration is the bucket length in "
                 "milliseconds. Interface holds the connection type, subscriber ID and network "
                 "ID of each network identity, not an interface name. Its other identity fields are not shown.\n"
                 "UIDs are resolved through packages.xml, where it parses, to a package name "
                 "or, for a shared UID, to the shared user name. If packages.xml is absent, or "
                 "fails with an XML parse error, an I/O error or a ValueError, usage is still "
                 "reported with bare UIDs. Other ABX decoding errors are not caught, and the "
                 "artifact then returns no rows. None of the images listed in sample_data "
                 "exercised these paths. A UID of -1 is UID_ALL in AOSP NetworkStats.java, "
                 "documented there as the uid value 'when UID details unavailable' "
                 "(https://android.googlesource.com/platform/packages/modules/Connectivity/+/"
                 "bd692130a596b4e9bc1ea6778db72c423bb8ab6f/framework-t/src/android/net/"
                 "NetworkStats.java#77, "
                 "the android-14.0.0_r1 tag); where packages.xml parses, this module labels it "
                 "'[UID_ALL]'. It carries no per-application attribution.\n"
                 "A UID of 100000 or more that packages.xml does not list is looked up by its "
                 "app ID, the UID modulo 100000 (UserHandle.getAppId, "
                 "https://android.googlesource.com/platform/frameworks/base/+/"
                 "299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368/core/java/android/os/"
                 "UserHandle.java#399, the android-14.0.0_r1 tag). Where packages.xml lists "
                 "that app ID, its name is shown with the full UID in parentheses. "
                 "Otherwise the UID is shown alone.\n"
                 "Tag is the record's tag in the hexadecimal form of AOSP "
                 "NetworkStats.tagToString. Tag 0x0 is TAG_NONE, documented in NetworkStats.java "
                 "as the 'value for total data across all tags'. That file skips other tags "
                 "when totalling because they are 'already counted in TAG_NONE'. It also notes "
                 "that if VPN software uses tags, the total tagged traffic may be greater than "
                 "the TAG_NONE traffic. Do not add tagged rows to Tag 0x0 rows. UID -4 is UID_REMOVED "
                 "(https://android.googlesource.com/platform/packages/modules/Connectivity/+/"
                 "bd692130a596b4e9bc1ea6778db72c423bb8ab6f/framework-t/src/android/net/"
                 "TrafficStats.java#88) and UID -5 is UID_TETHERING (NetworkStats.java#80 at "
                 "the same commit, the android-14.0.0_r1 tag). UID -253 was present on every "
                 "sample_data key except galaxys10_a10, russell_pixel6a_a13 and s20fe_a13. Its "
                 "meaning is not established here and it is shown as stored. In AOSP "
                 "NetworkStats.setMatches, a query for all sets (SET_ALL) does not match the "
                 "debug sets, which include VPN_IN and VPN_OUT (NetworkStats.java#1417 at the "
                 "same commit). No VPN_IN or VPN_OUT row was present on the sample_data "
                 "images.\n"
                 "A collection file with the same SHA-256 as one already read is not read "
                 "again, and its path stays in the source list. Files that differ are all "
                 "reported, even when they share records: on hc_pixel8pro_a16 and sharon_a14, "
                 "different files in different netstats folders held identical buckets, so "
                 "those rows appear more than once. Rows do not show which folder or file kind "
                 "(dev, xt, uid, uid_tag) they came from. On galaxys10_a10, russell_pixel6a_a13, "
                 "sharon_a14 and userb2_a13, most UID -1 rows from the dev files of a netstats "
                 "folder were also present, identical, in the xt files of the same folder (218 "
                 "of 234, 336 of 371, 2,153 of 2,269 and 27 of 29). On sharon_a14 a second "
                 "folder showed the same (27 of 34) and a third folder held dev and xt files "
                 "with no identical rows. Do not total rows across files. Identical rows can "
                 "also be separate records, because Interface leaves out some identity fields.\n"
                 "Timeline output is deliberately off: the buckets produced up to 62,999 "
                 "timestamped rows (kevin_pocox7_a15).",
        "paths": ("*/netstats/dev*", "*/netstats/uid*", "*/netstats/xt*", "*/system/packages.xml"),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "wifi",
        "sample_data": {
            "anne_a15": "29876 rows",
            "galaxys10_a10": "4110 rows",
            "hc_pixel8pro_a16": "16738 rows",
            "hc_pixel8pro_a17": "12695 rows",
            "kevin_pocox7_a15": "62999 rows",
            "pixel7a_a14": "50819 rows",
            "russell_pixel6a_a13": "45469 rows",
            "s20fe_a13": "947 rows",
            "samsunga53_a14": "9825 rows",
            "samsungs20_a13": "5097 rows",
            "sharon_a14": "53032 rows",
            "userb2_a13": "7343 rows",
        },
    }
}

import dataclasses
import datetime
import enum
import hashlib
import struct
import typing
import xml.etree.ElementTree as etree

from scripts.ilapfuncs import artifact_processor, checkabx, abxread, logfunc


# SEE: packages/modules/Connectivity/framework-t/src/android/net/NetworkStatsCollection.java
#      packages/modules/Connectivity/framework-t/src/android/net/NetworkIdentitySet.java
#      packages/modules/Connectivity/framework-t/src/android/net/NetworkStatsHistory.java



# android.os.UserHandle.PER_USER_RANGE: uid = userId * PER_USER_RANGE + appId
PER_USER_RANGE = 100000

UNIX_EPOCH = datetime.datetime(1970, 1, 1, 0, 0, 0)
def from_unix_ms(ms):
    return UNIX_EPOCH + datetime.timedelta(milliseconds=ms)

def read_raw(stream: typing.BinaryIO, length: int, throw_on_incomplete:bool=True) -> bytes:
    d = stream.read(length)
    if throw_on_incomplete and len(d) != length:
        raise ValueError("Could not read all data")
    return d

def read_bool(stream: typing.BinaryIO):
    b = stream.read(1)
    if not b:
        raise ValueError("Could not read all data")
    return b[0] != 0

def read_ushort(stream: typing.BinaryIO):
    return struct.unpack(">H", read_raw(stream, 2))[0]

def read_int(stream: typing.BinaryIO):
    return struct.unpack(">i", read_raw(stream, 4))[0]

def read_long(stream: typing.BinaryIO):
    return struct.unpack(">q", read_raw(stream, 8))[0]

def read_utf8(stream: typing.BinaryIO):
    buffer_length = read_ushort(stream)
    return read_raw(stream, buffer_length).decode("utf-8")

def read_optional_string(stream: typing.BinaryIO):
    present = read_bool(stream)
    if not present:
        return None
    else:
        return read_utf8(stream)

def read_var_long(stream: typing.BinaryIO):
    shift = 0
    result = 0
    while shift < 64:
        b = stream.read(1)
        if not b:
            raise ValueError("Could not read all data")
        b = b[0]
        result |= (b & 0x7F) << shift
        if (b & 0x80) == 0:
            return result
        shift += 7
    raise ValueError("malformed variable long")

def read_full_long_array(stream: typing.BinaryIO):
    count = read_int(stream)
    result = [read_long(stream) for _ in range(count)]
    return result

def read_varlong_array(stream: typing.BinaryIO):
    count = read_int(stream)
    result = [read_var_long(stream) for _ in range(count)]
    return result


class ConnectionType(enum.IntEnum):
    # See packages/modules/Connectivity/framework/src/android/net/ConnectivityManager.java
    # all of these are deprecated in favour of capabilities but still seem to be used in
    # netstats

    TYPE_NONE = -1
    TYPE_MOBILE = 0
    TYPE_WIFI = 1
    TYPE_MOBILE_MMS = 2
    TYPE_MOBILE_SUPL = 3
    TYPE_MOBILE_DUN = 4
    TYPE_MOBILE_HIPRI = 5
    TYPE_WIMAX = 6
    TYPE_BLUETOOTH   = 7
    TYPE_DUMMY = 8
    TYPE_ETHERNET = 9
    TYPE_MOBILE_FOTA = 10
    TYPE_MOBILE_IMS = 11
    TYPE_MOBILE_CBS = 12
    TYPE_WIFI_P2P = 13
    TYPE_MOBILE_IA = 14
    TYPE_MOBILE_EMERGENCY = 15
    TYPE_PROXY = 16
    TYPE_VPN = 17


@dataclasses.dataclass(frozen=True)
class NetworkIdentity:
    net_type: ConnectionType
    rat_type: int
    subscriber_id: typing.Optional[str]
    network_id: typing.Optional[str]
    roaming: bool
    metered: bool
    default_network: bool
    oem_network_capabilities: int
    sub_id: int
    transport_type: int

    def __str__(self) -> str:
        return f"{self.net_type.name}: {' '.join(x for x in (self.subscriber_id, self.network_id) if x)} "

class NetworkIdentitySet:
    IDENT_VERSION_INIT = 1
    IDENT_VERSION_ADD_ROAMING = 2
    IDENT_VERSION_ADD_NETWORK_ID = 3
    IDENT_VERSION_ADD_METERED = 4
    IDENT_VERSION_ADD_DEFAULT_NETWORK = 5
    IDENT_VERSION_ADD_OEM_MANAGED_NETWORK = 6
    IDENT_VERSION_ADD_SUB_ID = 7
    IDENT_VERSION_ADD_TRANSPORT_TYPES = 8

    IDENT_MAX_VERSION = IDENT_VERSION_ADD_TRANSPORT_TYPES

    def __init__(self, identities: typing.Iterable[NetworkIdentity]):
        self._identities = tuple(identities)

    @property
    def identities(self) -> typing.Iterable[NetworkIdentity]:
        yield from self._identities

    @classmethod
    def read(cls, stream: typing.BinaryIO):
        version = read_int(stream)
        if version > NetworkIdentitySet.IDENT_MAX_VERSION:
            raise ValueError(f"Unexpected network identity version: {version}")
        size = read_int(stream)
        identities: list[NetworkIdentity] = []
        for _ in range(size):
            if version <= NetworkIdentitySet.IDENT_VERSION_INIT:
                _ = read_int(stream)
            net_type = ConnectionType(read_int(stream))
            rat_type = read_int(stream)
            subscriber_id = read_optional_string(stream)
            network_id = None
            if version >= NetworkIdentitySet.IDENT_VERSION_ADD_NETWORK_ID:
                network_id = read_optional_string(stream)
            roaming = False
            if version >= NetworkIdentitySet.IDENT_VERSION_ADD_ROAMING:
                roaming = read_bool(stream)
            if version >= NetworkIdentitySet.IDENT_VERSION_ADD_METERED:
                metered = read_bool(stream)
            else:
                metered = net_type == ConnectionType.TYPE_MOBILE
            default_network = True
            if version >= NetworkIdentitySet.IDENT_VERSION_ADD_DEFAULT_NETWORK:
                default_network = read_bool(stream)
            oem_net_capabilities = -1
            if version >= NetworkIdentitySet.IDENT_VERSION_ADD_OEM_MANAGED_NETWORK:
                oem_net_capabilities = read_int(stream)
            sub_id = -1
            if version >= NetworkIdentitySet.IDENT_VERSION_ADD_SUB_ID:
                sub_id = read_int(stream)
            transport_type_bits = 0
            if version >= NetworkIdentitySet.IDENT_VERSION_ADD_TRANSPORT_TYPES:
                transport_type_bits = read_long(stream)

            identities.append(
                NetworkIdentity(
                    net_type, rat_type, subscriber_id, network_id, roaming, metered, default_network,
                    oem_net_capabilities, sub_id, transport_type_bits))

        return cls(identities)


@dataclasses.dataclass(frozen=True)
class NetworkStatsHistoryEntry:
    start_time: datetime.datetime
    duration: int
    rx_bytes: int
    rx_packets: int
    tx_bytes: int
    tx_packets: int
    operations: int

class NetworkStatsHistory:
    HISTORY_VERSION_INIT = 1
    HISTORY_VERSION_ADD_PACKETS = 2
    HISTORY_VERSION_ADD_ACTIVE = 3

    def __init__(self, stats: typing.Iterable[NetworkStatsHistoryEntry]):
        self._stats = tuple(stats)

    @property
    def entries(self):
        yield from self._stats

    @classmethod
    def read(cls, stream: typing.BinaryIO):
        version = read_int(stream)
        if version == NetworkStatsHistory.HISTORY_VERSION_INIT:
            bucket_duration = read_long(stream)
            bucket_starts = read_full_long_array(stream)
            rx_bytes = read_full_long_array(stream)
            rx_packets = [0 for _ in range(len(bucket_starts))]  # not stored in this version
            tx_bytes = read_full_long_array(stream)
            tx_packets = [0 for _ in range(len(bucket_starts))]  # not stored in this version
            operations = [0 for _ in range(len(bucket_starts))]  # not stored in this version
        elif version in (NetworkStatsHistory.HISTORY_VERSION_ADD_PACKETS, NetworkStatsHistory.HISTORY_VERSION_ADD_ACTIVE):
            bucket_duration = read_long(stream)
            bucket_starts = read_varlong_array(stream)
            if version >= NetworkStatsHistory.HISTORY_VERSION_ADD_ACTIVE:
                # consumed for stream position; the values are not reported
                _ = read_varlong_array(stream)
            rx_bytes = read_varlong_array(stream)
            rx_packets = read_varlong_array(stream)
            tx_bytes = read_varlong_array(stream)
            tx_packets = read_varlong_array(stream)
            operations = read_varlong_array(stream)
        else:
            raise ValueError(f"unexpected networkstats history version: {version}")

        # check buckets sizes match
        if (len(rx_bytes) != len(bucket_starts) or len(rx_packets) != len(bucket_starts)
                or len(tx_bytes) != len(bucket_starts) or len(tx_packets) != len(bucket_starts)
                or len(operations) != len(bucket_starts)):
            raise ValueError("mismatached buckets")

        return cls(
            (NetworkStatsHistoryEntry(from_unix_ms(bucket_starts[i]), bucket_duration, rx_bytes[i], rx_packets[i], tx_bytes[i],
                                      tx_packets[i], operations[i]) for i in range(len(bucket_starts))))

@dataclasses.dataclass(frozen=True)
class Record:
    uid: int
    set: int
    tag: int
    history: NetworkStatsHistory


class NetStats:
    def __init__(self, identity_set: NetworkIdentitySet):
        self._identity_set = identity_set
        self._records: list[Record] = []

    def add_record(self, record: Record):
        self._records.append(record)

    @property
    def identity_set(self) -> NetworkIdentitySet:
        return self._identity_set

    @property
    def records(self) -> typing.Iterable[Record]:
        yield from self._records


class NetstatsCollection:
    MAGIC = b"ANET"
    COLLECTION_VERSION_UID_INIT = 1
    COLLECTION_VERSION_UID_WITH_IDENT = 2
    COLLECTION_VERSION_UID_WITH_TAG = 3
    COLLECTION_VERSION_UID_WITH_SET = 4
    COLLECTION_VERSION_UNIFIED_INIT = 16

    # defined in packages/modules/Connectivity/framework-t/src/android/net/NetworkStats.java
    SET_TYPES = {
        -1: "Combined", 0: "Background", 1: "Foreground", 1001: "VPN_IN", 1002: "VPN_OUT"
    }

    def __init__(self, stats: typing.Iterable[NetStats]):
        self._stats = list(stats)

    @property
    def stats(self) -> typing.Iterable[NetStats]:
        yield from self._stats

    @classmethod
    def read(cls, stream: typing.BinaryIO) -> "NetstatsCollection":
        magic = stream.read(4)
        if magic != NetstatsCollection.MAGIC:
            raise ValueError(f"Invalid file signature (expected: {NetstatsCollection.MAGIC}; got: {magic})")
        version = read_int(stream)
        # Only the unified layout is parsed. The legacy UID formats (versions
        # 2-4) lay their records out differently, so reading them with this
        # layout would misparse rather than fail; reject them instead.
        if version == NetstatsCollection.COLLECTION_VERSION_UNIFIED_INIT:
            stats = []
            ident_size = read_int(stream)
            for _ in range(ident_size):
                identity_set = NetworkIdentitySet.read(stream)
                this_stat = NetStats(identity_set)
                stats.append(this_stat)
                history_size = read_int(stream)
                for _ in range(history_size):
                    # uid, set_, tag are used together to make a "Key" object
                    # Per the comments in the Key object in
                    # packages/modules/Connectivity/framework-t/src/android/net/NetworkStatsCollection.java:
                    #  uid Uid of the record.
                    #  set Set of the record,
                    #  tag Tag of the record, see {@link TrafficStats#setThreadStatsTag(int)}.
                    #
                    # uid is package ***uid(?)***, set indicates forground (1) and background (0) data or all combined (-1)

                    uid = read_int(stream)
                    set_ = read_int(stream)
                    tag = read_int(stream)
                    history = NetworkStatsHistory.read(stream)
                    this_stat.add_record(Record(uid, set_, tag, history))
            return cls(stats)
        else:
            raise ValueError(f"unexpected version: {version}")


def map_uids(packages: etree.ElementTree):
    uid_map = {}
    for package in packages.getroot().findall("package"):
        if uid := package.get("userId"):
            uid_map[int(uid)] = package.get("name")

    for shared_user in packages.findall("shared-user"):
        if uid := shared_user.get("userId"):
            uid_map[int(uid)] = shared_user.get("name")

    # Special UIDs per android.net.TrafficStats (UID_TETHERING = -5,
    # UID_REMOVED = -4) and android.net.NetworkStats (UID_ALL = -1,
    # documented there as the value used when UID details are unavailable).
    uid_map[-5] = "[Tethering]"
    uid_map[-4] = "[Removed Application]"
    uid_map[-1] = "[UID_ALL]"

    return uid_map

def package_for_uid(uid: int, uid_map: dict) -> typing.Optional[str]:
    """Package for a UID, through its app ID when the UID belongs to a secondary user."""
    if uid in uid_map:
        return uid_map[uid]
    if uid >= PER_USER_RANGE:
        return uid_map.get(uid % PER_USER_RANGE)
    return None


def format_tag(tag: int) -> str:
    """The tag as AOSP NetworkStats.tagToString prints it (Java's unsigned hex of an int)."""
    return f"0x{tag & 0xFFFFFFFF:x}"


def file_sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


@artifact_processor
def netstats(context):
    files_found = context.get_files_found()

    # packages.xml is an enrichment, not a requirement: it only maps UIDs to
    # package names. An unreadable copy must not cost the netstats rows.
    packages = None
    for file in files_found:
        if file.endswith("packages.xml"):
            try:
                if checkabx(file):
                    packages = abxread(file, False)
                else:
                    packages = etree.parse(file)
            except (etree.ParseError, OSError, ValueError) as ex:
                logfunc(f"Could not parse {file} for UID resolution ({ex}); "
                        "usage is reported with bare UIDs")

    uid_map = map_uids(packages) if packages is not None else {}

    headers = [
        ("Bucket Start", "datetime"), "Duration", "UID/Package", "Interface", "Usage Set", "Tag",
        "Rx Bytes", "Rx Packets", "Tx Bytes", "Tx Packets"]
    source_files = set()
    results = []
    # Sorted so the copy that is read does not depend on the order of the walk.
    read_files = {}
    for file in sorted(f for f in files_found if not f.endswith("packages.xml")):
        sha256 = file_sha256(file)
        if sha256 in read_files:
            logfunc(f"Skipping {context.get_relative_path(file)}: byte-identical to "
                    f"{context.get_relative_path(read_files[sha256])}")
            source_files.add(context.get_relative_path(file))
            continue
        with open(file, "rb") as f:
            try:
                collection = NetstatsCollection.read(f)
            except ValueError as ex:
                logfunc(f"Error reading {file} as netstats ({ex}) - skipping...")
                continue

            for stat in collection.stats:
                for record in stat.records:
                    package = package_for_uid(record.uid, uid_map)
                    if package is not None:
                        formatted_package = f"{package} ({record.uid})"
                    else:
                        formatted_package = f"{record.uid}"

                    for entry in record.history.entries:
                        results.append(
                            (entry.start_time, entry.duration, formatted_package,
                             "\n".join(str(x) for x in stat.identity_set.identities),
                             NetstatsCollection.SET_TYPES.get(record.set, f"(unknown: {record.set})"),
                             format_tag(record.tag),
                             entry.rx_bytes, entry.rx_packets, entry.tx_bytes, entry.tx_packets))

            read_files[sha256] = file
            source_files.add(context.get_relative_path(file))

    return headers, results, "\n".join(source_files)

