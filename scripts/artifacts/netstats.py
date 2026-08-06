__artifacts_v2__ = {
    "netstats": {
        "name": "netstats",
        "description": "Application accounts used on the device",
        "author": "Alex Caithness",
        "creation_date": "2026-08-05",
        "last_update_date": "2026-08-05",
        "requirements": "none",
        "category": "Network Usage",
        "notes": "",
        "paths": ("*/netstats/dev*", "*/netstats/uid*", "*/netstats/xt*", "*/system/packages.xml"),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "wifi",

    }
}

import dataclasses
import datetime
import enum
import re
import struct
import typing
import xml.etree.ElementTree as etree

from scripts.ilapfuncs import artifact_processor, checkabx, abxread, logfunc


# SEE: packages/modules/Connectivity/framework-t/src/android/net/NetworkStatsCollection.java
#      packages/modules/Connectivity/framework-t/src/android/net/NetworkIdentitySet.java
#      packages/modules/Connectivity/framework-t/src/android/net/NetworkStatsHistory.java



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
        for i in range(size):
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
                active_time = read_varlong_array(stream)
            else:
                active_time = [0 for _ in range(len(bucket_starts))]
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
        if version != NetstatsCollection.COLLECTION_VERSION_UID_INIT:
            stats = []
            ident_size = read_int(stream)
            for i in range(ident_size):
                identity_set = NetworkIdentitySet.read(stream)
                this_stat = NetStats(identity_set)
                stats.append(this_stat)
                history_size = read_int(stream)
                for j in range(history_size):
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

    # add special UIDS:
    uid_map[-5] = "[Tethering]"
    uid_map[-4] = "[Removed Application]"
    uid_map[-1] = "[UID Details Unavailable]"

    return uid_map

@artifact_processor
def netstats(context):
    files_found = context.get_files_found()

    packages = None
    for file in files_found:
        if file.endswith("packages.xml"):
            if checkabx(file):
                packages = abxread(file, False)
            else:
                packages = etree.parse(file)


    uid_map = map_uids(packages) if packages is not None else {}

    headers = [
        ("Bucket Start", "datetime"), "Duration", "UID/Package", "Interface", "Usage Set",
        "Rx Bytes", "Rx Packets", "Tx Bytes", "Tx Packets"]
    source_files = set()
    results = []
    for file in files_found:
        if file.endswith("packages.xml"):
            continue
        with open(file, "rb") as f:
            try:
                collection = NetstatsCollection.read(f)
            except ValueError as ex:
                logfunc(f"Error reading {file} as netstats ({ex}) - skipping...")
                continue

            for stat in collection.stats:
                for record in stat.records:
                    if record.uid in uid_map:
                        formatted_package = f"{uid_map[record.uid]} ({record.uid})"
                    else:
                        formatted_package = f"{record.uid}"

                    for entry in record.history.entries:
                        results.append(
                            (entry.start_time, entry.duration, formatted_package,
                             "\n".join(str(x) for x in stat.identity_set.identities),
                             NetstatsCollection.SET_TYPES.get(record.set, f"(unknown: {record.set})"),
                             entry.rx_bytes, entry.rx_packets, entry.tx_bytes, entry.tx_packets))

            source_files.add(context.get_relative_path(file))

    return headers, results, "\n".join(source_files)

