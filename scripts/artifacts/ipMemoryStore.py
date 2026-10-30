__artifacts_v2__ = {
    "ipMemoryStore": {
        "name": "Wi-Fi IP Memory Store",
        "description": "Rows of the NetworkAttributes table of the Android network stack's IpMemoryStore.db: "
                       "per Wi-Fi access point key, the IPv4 address, lease expiry, DNS servers and MTU "
                       "of its last stored DHCP lease, with the network's SSID where it can be recomputed.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-29",
        "last_update_date": "2026-10-29",
        "requirements": "none",
        "category": "WiFi Profiles",
        "notes": "Reads the NetworkAttributes table of the Android network stack's IP memory store in "
                 "user_de/0 of com.google.android.networkstack or com.android.networkstack, "
                 "IpMemoryStore.db or, after the network stack renames it, IpMemoryStoreV2.db "
                 "(https://android.googlesource.com/platform/packages/modules/NetworkStack/+/83ea07ed94890b52265e07d6760c7ed8f4cbd344/src/com/android/networkstack/ipmemorystore/IpMemoryStoreDatabase.java#195, "
                 "#297). Format and meanings come from AOSP NetworkStack at commit "
                 "44e87d4600f9f3f746de6940a13863110a60c452 and Wi-Fi at "
                 "82d2b854425b2e8731f4902bbba175c653b54d60 (both android14-release); the network stack is "
                 "updated through Google Play system updates, other versions were not compared, and "
                 "vendor builds were not decompiled. One row per table row "
                 "(https://android.googlesource.com/platform/packages/modules/NetworkStack/+/44e87d4600f9f3f746de6940a13863110a60c452/src/com/android/networkstack/ipmemorystore/IpMemoryStoreDatabase.java#66). "
                 "Lease Expires is assignedV4AddressExpiry, milliseconds since 1970-01-01 UTC "
                 "(https://android.googlesource.com/platform/packages/modules/NetworkStack/+/44e87d4600f9f3f746de6940a13863110a60c452/src/com/android/networkstack/ipmemorystore/IpMemoryStoreDatabase.java#78): "
                 "when DhcpClient saves a lease it writes the address, the DNS servers and the current "
                 "time plus the lease duration in one record "
                 "(https://android.googlesource.com/platform/packages/modules/NetworkStack/+/44e87d4600f9f3f746de6940a13863110a60c452/src/android/net/dhcp/DhcpClient.java#846). "
                 "It writes 1 for a lease it saw expire and Long.MAX_VALUE for an infinite lease (#275, "
                 "#851); the column is blank for both, and neither value occurred on the tested images. "
                 "Assigned IPv4 Address is assignedV4Address, stored as an integer by "
                 "inet4AddressToIntHTH "
                 "(https://android.googlesource.com/platform/packages/modules/NetworkStack/+/44e87d4600f9f3f746de6940a13863110a60c452/src/com/android/networkstack/ipmemorystore/IpMemoryStoreDatabase.java#263) "
                 "and shown dotted, most significant byte first; DNS Servers is dnsAddresses, each "
                 "address a length byte and its bytes "
                 "(https://android.googlesource.com/platform/packages/modules/NetworkStack/+/44e87d4600f9f3f746de6940a13863110a60c452/src/com/android/networkstack/ipmemorystore/IpMemoryStoreDatabase.java#232). "
                 "Record Expires is expiryDate, milliseconds since 1970-01-01 UTC "
                 "(https://android.googlesource.com/platform/packages/modules/NetworkStack/+/44e87d4600f9f3f746de6940a13863110a60c452/src/com/android/networkstack/ipmemorystore/IpMemoryStoreDatabase.java#71): "
                 "each time a record is stored for the key the store moves it forward by a relevance "
                 "bump, at most 400 days from then "
                 "(https://android.googlesource.com/platform/packages/modules/NetworkStack/+/44e87d4600f9f3f746de6940a13863110a60c452/src/com/android/networkstack/ipmemorystore/IpMemoryStoreService.java#230, "
                 "https://android.googlesource.com/platform/packages/modules/NetworkStack/+/44e87d4600f9f3f746de6940a13863110a60c452/src/com/android/networkstack/ipmemorystore/RelevanceUtils.java#302, "
                 "#192). It is when the store would drop the record, not when the record was written, and "
                 "the time of a write cannot be worked out from it alone. Group Hint and L2 Key are as "
                 "stored. Wi-Fi's score card writes the group hint for a key "
                 "(https://android.googlesource.com/platform/packages/modules/Wifi/+/82d2b854425b2e8731f4902bbba175c653b54d60/service/java/com/android/server/wifi/WifiScoreCard.java#2226): "
                 "G and the hex of a SHA-256 over the device's ANDROID_ID, the network's SSID and the "
                 "address 02:00:00:00:00:00 "
                 "(https://android.googlesource.com/platform/packages/modules/Wifi/+/82d2b854425b2e8731f4902bbba175c653b54d60/service/java/com/android/server/wifi/WifiScoreCard.java#301, "
                 "https://android.googlesource.com/platform/packages/modules/Wifi/+/82d2b854425b2e8731f4902bbba175c653b54d60/service/java/com/android/server/wifi/WifiScoreCard.java#2296, "
                 "https://android.googlesource.com/platform/packages/modules/Wifi/+/82d2b854425b2e8731f4902bbba175c653b54d60/service/java/com/android/server/wifi/WifiScoreCard.java#2339), "
                 "the ANDROID_ID being read from the secure settings "
                 "(https://android.googlesource.com/platform/packages/modules/Wifi/+/82d2b854425b2e8731f4902bbba175c653b54d60/service/java/com/android/server/wifi/WifiInjector.java#371). "
                 "L2 Key is W and the hex of the same hash with the access point's BSSID in place of that "
                 "address "
                 "(https://android.googlesource.com/platform/packages/modules/Wifi/+/82d2b854425b2e8731f4902bbba175c653b54d60/service/java/com/android/server/wifi/WifiScoreCard.java#2066). "
                 "SSID is filled when the hash of a saved network matches the group hint: the module "
                 "takes android_id from system/users/0/settings_secure.xml and every SSID in the "
                 "WifiConfigStore*.xml files of the extraction, rollback copies included. BSSIDs are not "
                 "in those files, so L2 Key is not resolved. A blank SSID means no saved network matched, "
                 "not that the network had no name. Rollback snapshots of the store "
                 "(misc_de/0/rollback/<id>/...) are read too: a snapshot row equal to a row of the live "
                 "store in every other column is left out, and any other snapshot row is kept with "
                 "Database naming the snapshot. The storage views one extraction can hold for an app data "
                 "directory are read once. Not read: the PrivateData table (the Wi-Fi score card's "
                 "per-key protobuf records), and in IpMemoryStoreV2.db the NetworkEvents table "
                 "(https://android.googlesource.com/platform/packages/modules/NetworkStack/+/83ea07ed94890b52265e07d6760c7ed8f4cbd344/src/com/android/networkstack/ipmemorystore/IpMemoryStoreDatabase.java#156), "
                 "which held no rows in any of the 8 copies on the tested images. On the tested images: "
                 "1,270 rows on 21 of 22 images (none on galaxys10_a10, which holds no store); 1,236 "
                 "named an SSID and 395 held an address, a lease expiry and DNS servers, all three or "
                 "none. Of the 34 rows with no SSID, 24 had no group hint and 10 had a hint no saved "
                 "network matched: 1 hint on cookbook_a11, 1 on pixel3_a11 and 2 on samsungs20_a13, whose "
                 "settings_secure.xml could not be parsed (a value holds unescaped quotes), so no "
                 "ANDROID_ID was read there. 80 rows on 4 images came from rollback snapshots, so "
                 "Database held one value on the images without one. Lease Expires leads the table as the "
                 "time tied to a connection, and is blank on the rows that hold no lease. On the emulator "
                 "images emu_a15_oss2_v3 and emu_a15_oss_v17 the named network was AndroidWifi, the only "
                 "network in their WifiConfigStore.xml.",
        "paths": ('*/com.google.android.networkstack/databases/IpMemoryStore*.db*',
                  '*/com.android.networkstack/databases/IpMemoryStore*.db*',
                  '*/system/users/0/settings_secure.xml',
                  '*/WifiConfigStore*.xml'),
        "output_types": "standard",
        "artifact_icon": "wifi",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 7 rows",
            "anne_a15": "Android 15 | 88 rows",
            "cookbook_a11": "Android 11 | 3 rows",
            "emu_a15_oss2_v3": "Android 15 | 3 rows",
            "emu_a15_oss_v17": "Android 15 | 3 rows",
            "falken_a326u_a13": "Android 13 | 18 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 20 rows",
            "hc_pixel8pro_a17": "Android 17 | 24 rows",
            "hickman_a13": "Android 13 | 47 rows",
            "kevin_pocox7_a15": "Android 15 | 279 rows",
            "pixel3_a11": "Android 11 | 14 rows",
            "pixel3_a12": "Android 12 | 14 rows",
            "pixel7a_a14": "Android 14 | 101 rows",
            "russell_a14": "Android 14 | 359 rows",
            "russell_pixel6a_a13": "Android 13 | 94 rows",
            "s20fe_a13": "Android 13 | 14 rows",
            "samsunga53_a14": "Android 14 | 17 rows",
            "samsungs20_a13": "Android 13 | 5 rows",
            "sharon_a13": "Android 13 | 32 rows",
            "sharon_a14": "Android 14 | 98 rows",
            "userb2_a13": "Android 13 | 30 rows",
        },
    }
}

import hashlib
from collections import Counter
import sqlite3
import struct

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, logfunc, open_sqlite_db_readonly
from scripts.artifacts.settingsSecure import parse_settings_root
from scripts.artifacts.storagePathViews import snapshot_key, user_files

# DhcpClient stores 1 for a lease it saw expire and Long.MAX_VALUE for an infinite lease.
_EXPIRED_LEASE = 1
_INFINITE_LEASE = 0x7FFFFFFFFFFFFFFF
# WifiInfo.DEFAULT_MAC_ADDRESS, the BSSID WifiScoreCard hashes for a network's group hint.
_PLACEHOLDER_MAC = bytes.fromhex('020000000000')


def _hash(seed, ssid, mac):
    """WifiScoreCard.computeHashLong: SHA-256 over length-prefixed seed, SSID and MAC, first 8 bytes."""
    mashed = b''.join(bytes([len(part)]) + part for part in (seed, ssid, mac))
    return struct.unpack('>Q', hashlib.sha256(mashed).digest()[:8])[0]


def _ssid_bytes(text):
    """A WifiConfigStore SSID is quoted UTF-8 or bare hex; NativeUtil.decodeSsid turns either into bytes."""
    if len(text) >= 2 and text.startswith('"') and text.endswith('"'):
        return text[1:-1].encode('utf-8')
    try:
        return bytes.fromhex(text)
    except ValueError:
        return None


def _display_ssid(text):
    if len(text) >= 2 and text.startswith('"') and text.endswith('"'):
        return text[1:-1]
    return text


def _android_ids(paths):
    seeds = []
    for path in paths:
        root = parse_settings_root(path, 'Wi-Fi IP Memory Store')
        if root is None:
            continue
        for setting in root.iter('setting'):
            value = setting.get('value')
            if setting.get('name') == 'android_id' and value and value not in seeds:
                seeds.append(value)
    return seeds


def _ssids(paths):
    found = []
    for path in paths:
        root = parse_settings_root(path, 'Wi-Fi IP Memory Store')
        if root is None:
            continue
        for element in root.iter():
            text = element.text if element.text is not None else element.get('value')
            if element.get('name') == 'SSID' and text and text not in found:
                found.append(text)
    return found


def _hint_names(seeds, ssids):
    names = {}
    for seed in seeds:
        for ssid in ssids:
            raw = _ssid_bytes(ssid)
            if raw is None:
                continue
            names.setdefault(format(_hash(seed.encode('utf-8'), raw, _PLACEHOLDER_MAC), 'x'),
                             _display_ssid(ssid))
    return names


def _ipv4(value):
    if value is None:
        return ''
    return '.'.join(str(b) for b in struct.pack('>i', value))


def _addresses(blob):
    """IpMemoryStoreDatabase.encodeAddressList: each address as a length byte and its bytes."""
    if not blob:
        return ''
    out, i = [], 0
    while i < len(blob):
        size = blob[i]
        raw = blob[i + 1:i + 1 + size]
        if len(raw) != size:
            out.append('(truncated)')
            break
        if size == 4:
            out.append('.'.join(str(b) for b in raw))
        elif size == 16:
            out.append(':'.join(raw[j:j + 2].hex() for j in range(0, 16, 2)))
        else:
            out.append(raw.hex())
        i += 1 + size
    return '\n'.join(out)


def _lease(value):
    if value is None or value in (_EXPIRED_LEASE, _INFINITE_LEASE):
        return ''
    return convert_unix_ts_to_utc(value / 1000)


def _without_snapshot_repeats(rows):
    """Rows without those from a rollback snapshot that repeat a live row in every other column.

    A rollback snapshot can hold IpMemoryStore.db while the live store has been renamed to
    IpMemoryStoreV2.db, so rows are matched on their values, not on the file they came from.
    """
    live = Counter(row[:-1] for row in rows if snapshot_key(row[-1]) is None)
    kept = []
    for row in rows:
        if snapshot_key(row[-1]) is not None and live[row[:-1]] > 0:
            live[row[:-1]] -= 1
            continue
        kept.append(row)
    return kept


@artifact_processor
def ipMemoryStore(context):
    files = [str(f) for f in context.get_files_found()]
    rel = {f: str(context.get_relative_path(f)).replace('\\', '/') for f in files}
    settings = [f for f in files if rel[f].endswith('/system/users/0/settings_secure.xml')]
    configs = [f for f in files if rel[f].rsplit('/', 1)[-1].startswith('WifiConfigStore')
               and rel[f].endswith('.xml')]
    names = _hint_names(_android_ids(settings), _ssids(configs))

    data_list = []
    sources = []
    stores = user_files(context, 'IpMemoryStore.db') + user_files(context, 'IpMemoryStoreV2.db')
    for path, _user in stores:
        if '/databases/' not in str(context.get_relative_path(path)).replace('\\', '/'):
            continue
        db = open_sqlite_db_readonly(path)
        if db is None:
            continue
        try:
            rows = db.execute('SELECT l2Key, expiryDate, assignedV4Address, assignedV4AddressExpiry, '
                              'groupHint, dnsAddresses FROM NetworkAttributes '
                              'ORDER BY assignedV4AddressExpiry DESC, expiryDate DESC').fetchall()
        except sqlite3.Error as ex:
            logfunc(f'Wi-Fi IP Memory Store: could not read {context.get_relative_path(path)}: {ex}')
            continue
        finally:
            db.close()
        sources.append(path)
        database = str(context.get_relative_path(path)).replace('\\', '/')
        for l2_key, expiry, address, lease_expiry, hint, dns in rows:
            lease_time = _lease(lease_expiry)
            record_expiry = convert_unix_ts_to_utc(expiry / 1000) if expiry else ''
            ssid = names.get((hint or '')[1:], '') if (hint or '').startswith('G') else ''
            data_list.append((lease_time, record_expiry, ssid, _ipv4(address),
                              _addresses(dns), hint or '', l2_key, database))
    if names:
        sources.extend(f for f in settings + configs if f not in sources)

    data_headers = (('Lease Expires', 'datetime'), ('Record Expires', 'datetime'), 'SSID',
                    'Assigned IPv4 Address', 'DNS Servers', 'Group Hint', 'L2 Key', 'Database')
    return data_headers, _without_snapshot_repeats(data_list), '\n'.join(sources)
