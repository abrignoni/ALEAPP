__artifacts_v2__ = {
    "netstats": {
        "name": "Android NetworkStats",
        "description": "Parses Android NetworkStats Data",
        "author": "Erik (@0x4552494b)",
        "creation_date": "2026-01-07",
        "last_update_date": "2026-01-07",
        "requirements": "mutf8",
        "category": "Netstats",
        "notes": "",
        "paths": ("*/data/system/netstats/uid*"),
        "output_types": ["html"],
        "function": "parse_netstats"
    }}

# Tested against:
# Google Pixel 3 - Android 11
# Samsung Galaxy A32 (SM-A326B) - Android 13
# Realme C11 2021 - Android 11


import struct
from enum import Enum

import mutf8

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, convert_unix_ts_to_utc


# NetworkIdentity type labels
# defined in https://cs.android.com/android/platform/superproject/main/+/main:frameworks/layoutlib/bridge/src/android/net/ConnectivityManager.java;l=118;drc=e29e1d58d803cb0f8f375d145294fcf78f6a8e57
class NetworkIdentityType(Enum):
    TYPE_NONE = -1
    TYPE_MOBILE = 0
    TYPE_WIFI = 1
    TYPE_MOBILE_MMS = 2
    TYPE_MOBILE_SUPL = 3
    TYPE_MOBILE_DUN = 4
    TYPE_MOBILE_HIPRI = 5
    TYPE_WIMAX = 6
    TYPE_BLUETOOTH = 7
    TYPE_DUMMY = 8
    TYPE_ETHERNET = 9
    TYPE_MOBILE_FOTA = 10
    TYPE_MOBILE_IMS = 11
    TYPE_MOBILE_CMS = 12
    TYPE_WIFI_P2P = 13
    TYPE_MOBILE_IA = 14
    TYPE_MOBILE_EMERGENCY = 15
    TYPE_PROXY = 16
    TYPE_VPN = 17
    TYPE_TEST = 18


# NetworkIdentity RAT (Radio Access Technology) type labels
# defined in https://cs.android.com/android/platform/superproject/main/+/main:frameworks/base/telephony/java/android/telephony/TelephonyManager.java;l=3119;drc=61197364367c9e404c7da6900658f1b16c42d0da
class NetworkIdentityRATType(Enum):
    NETWORK_TYPE_UNKNOWN = 0
    NETWORK_TYPE_GPRS = 1
    NETWORK_TYPE_EDGE = 2
    NETWORK_TYPE_UMTS = 3
    NETWORK_TYPE_CDMA = 4
    NETWORK_TYPE_EVDO_0 = 5
    NETWORK_TYPE_EVD0_A = 6
    NETWORK_TYPE_1XRTT = 7
    NETWORK_TYPE_HSDPA = 8
    NETWORK_TYPE_HSUPA = 9
    NETWORK_TYPE_HSPA = 10
    NETWORK_TYPE_IDEN = 11
    NETWORK_TYPE_EVDO_B = 12
    NETWORK_TYPE_LTE = 13
    NETWORK_TYPE_EHRPD = 14
    NETWORK_TYPE_HSPAP = 15
    NETWORK_TYPE_GSM = 16
    NETWORK_TYPE_TD_SCDMA = 17
    NETWORK_TYPE_IWLAN = 18
    NETWORK_TYPE_LTE_CA = 19
    NETWORK_TYPE_NR = 20
    NETWORK_TYPE_NB_IOT_NTNT = 21


def read_var_long(stream):
    """
    Reads Protobuf-style VarLong from input stream

    See https://cs.android.com/android/platform/superproject/main/+/main:packages/modules/Connectivity/framework-t/src/android/net/NetworkStatsHistory.java?q=symbol%3A%5Cbandroid.net.NetworkStatsHistory.DataStreamUtils.readVarLong%5Cb%20case%3Ayes
    """
    shift = 0
    result = 0

    while True:
        byte = stream.read(1)[0]
        result |= (byte & 0x7f) << shift
        if not byte & 0x80:
            return result
        shift += 7


def read_var_long_array(stream):
    """
    Reads array of VarLongs from input stream

    See https://cs.android.com/android/platform/superproject/main/+/main:packages/modules/Connectivity/framework-t/src/android/net/NetworkStatsHistory.java?q=symbol%3A%5Cbandroid.net.NetworkStatsHistory.DataStreamUtils.readVarLongArray%5Cb%20case%3Ayes
    """
    size = struct.unpack('>i', stream.read(4))[0]
    if size == -1:
        return None
    else:
        return [read_var_long(stream) for _ in range(size)]


def read_optional_mutf(stream):
    """
    Reads modified utf string from input stream

    See https://cs.android.com/android/platform/superproject/main/+/main:packages/modules/Connectivity/framework-t/src/android/net/NetworkIdentitySet.java?q=symbol%3A%5Cbandroid.net.NetworkIdentitySet.readOptionalString%5Cb%20case%3Ayes
    """
    if stream.read(1) == b'\x00':
        return None
    else:
        size = struct.unpack('>H', stream.read(2))[0]
        return mutf8.decode_modified_utf8(stream.read(size))


def parse_netstats(files_found, report_folder, _seeker, _wrap_text):
    """
    Parses NetworkStats files

    Adapted from https://cs.android.com/android/platform/superproject/main/+/main:packages/modules/Connectivity/framework-t/src/android/net/NetworkStatsCollection.java;l=507;drc=da6020a329e7f51c2b0b431bd14035ea24f805b7
    """
    entries = []

    files_found.sort()
    for file in files_found:
        with open(file, 'rb') as f:

            # check file magic bytes ("ANET")
            if f.read(4) != b'ANET':
                logfunc(f'{file}: Invalid magic bytes, skipping file.')
                continue

            # check file version (must be 16)
            if struct.unpack('>i', f.read(4))[0] != 16:
                logfunc(f'{file}: Invalid version, skipping file.')
                continue

            entry_count = struct.unpack('>i', f.read(4))[0]
            for _ in range(0, entry_count):
                network_identities_version = struct.unpack('>i', f.read(4))[0]
                network_identities_count = struct.unpack('>i', f.read(4))[0]

                network_identities = []
                for _ in range(0, network_identities_count):

                    if network_identities_version < 1:
                        _ = f.read(4)

                    identity = {'type': struct.unpack('>i', f.read(4))[0],
                                'rat_type': struct.unpack('>i', f.read(4))[0],
                                'subscriber_id': read_optional_mutf(f),
                                'network_id': read_optional_mutf(f) if network_identities_version >= 3 else None,
                                'roaming': struct.unpack('?', f.read(1))[
                                    0] if network_identities_version >= 2 else None,
                                'metered': struct.unpack('?', f.read(1))[0] if network_identities_version >= 4 else
                                identity['type'] == 0,
                                'default_network': struct.unpack('?', f.read(1))[
                                    0] if network_identities_version >= 5 else None,
                                'oem_net_capabilities': struct.unpack('>i', f.read(4))[
                                    0] if network_identities_version >= 6 else None,
                                'sub_id': struct.unpack('>i', f.read(4))[
                                    0] if network_identities_version >= 7 else None,
                                }
                    network_identities.append(identity)

                buckets = []
                bucket_count = struct.unpack('>i', f.read(4))[0]
                for _ in range(0, bucket_count):
                    # from key field only save the UID and discard "set" and "tag" since their usage is unknown
                    uid = struct.unpack('>i', f.read(4))[0]
                    _ = f.read(8)

                    # check bucket version - only VERSION_ADD_ACTIVE (3) is implemented
                    # other versions were never observed in testing
                    if (version := struct.unpack('>i', f.read(4))[0]) != 3:
                        logfunc(f"[ERROR] Unsupported bucket version {version} in {file}. Parsing aborted.")
                        return

                    bucket = {'uid': uid,
                              'duration': struct.unpack('>q', f.read(8))[0],
                              'start': read_var_long_array(f),
                              'active_time': read_var_long_array(f),
                              'rx_bytes': read_var_long_array(f),
                              'rx_packets': read_var_long_array(f),
                              'tx_bytes': read_var_long_array(f),
                              'tx_packets': read_var_long_array(f),
                              'operations': read_var_long_array(f)}

                    bucket['total_bytes'] = [rxb + txb for rxb, txb in zip(bucket['rx_bytes'], bucket['tx_bytes'])]

                    buckets.append(bucket)
                entries.append({'network_identities': network_identities, 'buckets': buckets, 'file_found': file})

    report = ArtifactHtmlReport('NetworkStats')
    report.start_artifact_report(report_folder, 'NetworkStats')
    report.add_script()

    for entry in entries:

        # generate a descriptive string that can be used as subtitle in the report
        if (first_id := entry['network_identities'][0]).get('subscriber_id') is not None:
            description = first_id.get('subscriber_id')
        elif first_id.get('network_id') is not None:
            description = first_id.get('network_id')
        else:
            description = 'Unknown'

        report.write_minor_header(f'Network Identity - "{description}"')

        # convert parsed type and rat_type into respective label
        identity_converters = [
            lambda type: NetworkIdentityType(type).name,
            lambda rat_type: NetworkIdentityRATType(rat_type).name,
            lambda subscriber_id: subscriber_id,
            lambda network_id: network_id,
            lambda roaming: roaming,
            lambda metered: metered,
            lambda default_network: default_network,
            lambda oem_net_capabilities: oem_net_capabilities,
            lambda sub_id: sub_id
        ]

        report.write_artifact_data_table(
            ['Type', 'RAT type', 'Subscriber ID', 'Network ID', 'Roaming', 'Metered', 'Default Network',
             'oem_net_capabilities', 'sub_id'],
            [[f(col) for f, col in zip(identity_converters, e.values())] for e in entry['network_identities']],
            entry['file_found'], False, True, False, False)

        # functions to convert parsed data (mostly arrays of VarLongs) to strings that can be printed in the report
        bucket_converters = [
            lambda pid: pid,
            lambda duration: f'{duration // 60000} min',
            lambda start: '<br>'.join([convert_unix_ts_to_utc(x).strftime('%Y-%m-%d&nbsp;%H:%M:%S') for x in start]),
            lambda active_time: '<br>'.join([f'{x // 60000} min' for x in active_time]),
            lambda rx_bytes: '<br>'.join([str(x) for x in rx_bytes]),
            lambda rx_packets: '<br>'.join([str(x) for x in rx_packets]),
            lambda tx_bytes: '<br>'.join([str(x) for x in tx_bytes]),
            lambda tx_packets: '<br>'.join([str(x) for x in tx_packets]),
            lambda operations: '<br>'.join([str(x) for x in operations]),
            lambda total_bytes: '<br>'.join([str(x) for x in total_bytes])
        ]

        report.write_minor_header('Data Buckets', 'h4')
        report.write_artifact_data_table(
            ['UID', 'Duration', 'Start', 'Active Time', 'rxBytes', 'rxPackets', 'txBytes', 'txPackets', 'Operations',
             'totalBytes'],
            [[f(col) for f, col in zip(bucket_converters, e.values())] for e in entry['buckets']],
            None, False, False, False, False)
