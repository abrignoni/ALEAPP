import datetime
import hashlib
import os
import re
import sqlite3

from scripts.ilapfuncs import artifact_processor, logfunc, open_sqlite_db_readonly

__artifacts_v2__ = {
    "androidKeystore2Keys": {
        "name": "Keystore Key Entries",
        "description": "Key entries of the Android Keystore 2.0 database (persistent.sqlite in "
                       "misc/keystore): per key its alias, the app user ID or SELinux namespace "
                       "it belongs to, its type and lifecycle state, the creation time Keystore "
                       "recorded, selected stored characteristics of the key and any grants of it to other "
                       "user IDs. Key blobs are not parsed or reported.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-15",
        "last_update_date": "2026-11-15",
        "requirements": "none",
        "category": "Encryption and Credentials",
        "notes": "One row per keyentry row of persistent.sqlite, joined to its keymetadata, keyparameter, "
                 "blobentry and grant rows; the tables are those created in Keystore 2.0's database.rs "
                 "(https://android.googlesource.com/platform/system/security/+/5a37034a3a97492cca75928193363c4f13bce5d3/keystore2/src/database.rs#922). Created is keymetadata tag 0, CreationDate, the first "
                 "KeyMetaEntry variant (database.rs#150; variants are numbered from 0 in declaration order, "
                 "https://android.googlesource.com/platform/system/security/+/5a37034a3a97492cca75928193363c4f13bce5d3/keystore2/src/database/utils.rs#146 and #223), milliseconds since 1970 (database.rs#394). "
                 "Keystore writes it when a key is generated or imported (security_level.rs#159 and #185 in the "
                 "same source), when a certificate-only entry is stored (database.rs#1855) and, with the time of "
                 "the move, when its legacy importer moves a key from the pre-Keystore 2.0 files into the "
                 "database (legacy_importer.rs#664). On a device that still held legacy files after an upgrade, "
                 "Created can therefore be the time Keystore imported the key, which happens when the key is "
                 "first requested (legacy_importer.rs#288), and not the time the key was made. Unexercised: no "
                 "tested image showed this (pixel3_a11 and pixel3_a12 shared no owner and alias). Created is the "
                 "device clock reading when it was written (database.rs#418); 3 rows on hickman_a13 carry a date "
                 "in 1970. Created was blank on all 171 Super "
                 "and 90 Attestation rows of the tested images. Generating a key under an alias that already has "
                 "one unbinds the old entry and sets it Unreferenced (database.rs#1640) for later removal, and "
                 "deleting a key deletes its keyentry, keymetadata, keyparameter and grant rows "
                 "(database.rs#2266), so Created is the time of the key currently under the alias and a deleted "
                 "key leaves no row. Both were seen in the known data emu_a15_keystore_known_20261115: a key "
                 "generated twice under one alias showed the second time, and a deleted key had no row. Key "
                 "Type is key_type named from KeyType (database.rs#291: Client 0, Super 1); Attestation (2) is "
                 "from the Android 13 source (https://android.googlesource.com/platform/system/security/+/1301fdbce765a71ca8d84f26285aba4312e0c1b4/keystore2/src/database.rs#251), which describes it as a "
                 "key created by the remote provisioning mechanism; Attestation rows were seen on russell_a14 "
                 "(13), russell_pixel6a_a13 (34) and userb2_a13 (43). Domain is domain named from Domain.aidl "
                 "(https://android.googlesource.com/platform/system/hardware/interfaces/+/34d76c29fff78058183215ab8d57fa8ea7944db0/keystore2/aidl/android/system/keystore2/Domain.aidl#22). Namespace is namespace as stored: for APP the owning Linux UID ("
                 "legacy_importer.rs#602), for "
                 "SELINUX a namespace of keystore2_key_contexts, and for a super key the Android user ID "
                 "(database.rs#1313). Android User is the UID divided by 100000 (AID_USER_OFFSET, "
                 "https://android.googlesource.com/platform/system/core/+/32bd7a7dd5190626302b661d818f1d23d9be7b0b/libcutils/include/private/android_filesystem_config.h#232), or the namespace for a super key. Owner is the fixed AID name of an app ID below "
                 "10000 (from the AID list in android_filesystem_config.h, https://android.googlesource.com/platform/system/core/+/32bd7a7dd5190626302b661d818f1d23d9be7b0b/libcutils/include/private/android_filesystem_config.h#43), else the packages that "
                 "data/system/packages.list under the same data root lists for that app ID (UID modulo 100000), else blank; for SELINUX it "
                 "is the namespace's context name (https://android.googlesource.com/platform/system/sepolicy/+/ad1c4255c49d57fe885894a8b690c0dfd542100b/private/keystore2_key_contexts#8), and namespace 1250, "
                 "not in that file, was blank (33 rows on seven Samsung images). An app ID that packages.list does "
                 "not list has a blank Owner; no tested image with a packages.list showed this. No packages.list "
                 "was found on samsunga53_a14, and its 118 app keys have a blank Owner; the run log says so. "
                 "Super keys show Owner as Keystore super key, a label of this module. 78 of the 90 Attestation "
                 "rows have no domain or namespace and 29 have no alias, so Domain, Namespace, Android User and "
                 "Owner are blank on them. State is state "
                 "named from KeyLifeCycle (database.rs#484); State held Live (1) on all 3,201 rows of the tested "
                 "images and all 18 known-data rows. Algorithm, Key Size, Purposes, Origin, No Auth Required, "
                 "Auth Timeout (s) and Unlocked Device Required are the keyparameter rows of the KeyMint tags "
                 "ALGORITHM, KEY_SIZE, PURPOSE, ORIGIN, NO_AUTH_REQUIRED, AUTH_TIMEOUT and UNLOCKED_DEVICE_REQUIRED "
                 "(https://android.googlesource.com/platform/hardware/interfaces/+/488942f82bd1bc9ad1cb65a02c71421dc3a6a3d6/security/keymint/aidl/android/hardware/security/keymint/Tag.aidl#46), with enum names from Algorithm.aidl, KeyPurpose.aidl and KeyOrigin.aidl in "
                 "the same folder; Yes means the boolean tag is stored and blank that it is not. Security Level is "
                 "the security_level stored on the ALGORITHM parameter row, named from SecurityLevel.aidl; other "
                 "parameter rows of the same key can carry a different level. These columns were blank "
                 "on the 280 rows that had no key parameters (super keys, attestation keys and certificate-only "
                 "entries). Auth Timeout (s) held a value on 83 of the 3,201 rows of the tested images and had no "
                 "value on any of the 18 known-data rows. Stored Blobs lists the blobentry subcomponent types present (database.rs#734: "
                 "KEY_BLOB, CERT, CERT_CHAIN); the blobs themselves, which hold the key material and certificates, "
                 "are not parsed or reported. Grants lists each grant row's grantee UID, with its Owner when one resolves, and access_vector as "
                 "stored (94 rows on 35 images). Not reported: blob contents, blobmetadata, the version table (one row on every tested image), keymetadata tags other "
                 "than CreationDate, keyparameter tags other than those named, the slotentry, slotmetadata and "
                 "pqc_keyparameter tables on anne_a15 (no rows), and vpnprofilestore.sqlite beside the database, which is "
                 "not read. Labels never seen on a tested image (states Existing and "
                 "Unreferenced, domains GRANT, BLOB and KEY_ID, TRIPLE_DES, ATTEST_KEY, origins DERIVED, RESERVED "
                 "and SECURELY_IMPORTED, security level KEYSTORE) are from the source only. Byte-identical copies "
                 "of persistent.sqlite are read once. On each of the 37 tested images the row count equalled the keyentry row count.",
        "paths": ('*/misc/keystore/persistent.sqlite*', '*/system/packages.list'),
        "output_types": "standard",
        "artifact_icon": "key",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 93 rows",
            "anne_a15": "Android 15 | 211 rows",
            "cookbook_a11": "Android 11 | 0 rows (legacy Keystore files only)",
            "falken_a326u_a13": "Android 13 | 120 rows",
            "galaxys10_a10": "Android 10 | 0 rows (legacy Keystore files only)",
            "hc_pixel8pro_a16": "Android 16 | 155 rows",
            "hc_pixel8pro_a17": "Android 17 | 174 rows",
            "hickman_a13": "Android 13 | 142 rows",
            "kevin_pocox7_a15": "Android 15 | 179 rows",
            "pixel3_a11": "Android 11 | 0 rows (legacy Keystore files only)",
            "pixel3_a12": "Android 12 | 132 rows",
            "pixel7a_a14": "Android 14 | 138 rows",
            "russell_a14": "Android 14 | 176 rows",
            "russell_pixel6a_a13": "Android 13 | 148 rows",
            "s20fe_a13": "Android 13 | 70 rows",
            "samsunga53_a14": "Android 14 | 144 rows",
            "samsungs20_a13": "Android 13 | 177 rows",
            "sharon_a13": "Android 13 | 165 rows",
            "sharon_a14": "Android 14 | 238 rows",
            "userb2_a13": "Android 13 | 109 rows",
            "emu_a15_oss_v1": "Android 15 | 22 rows",
            "emu_a15_oss_v17": "Android 15 | 43 rows",
            "emu_a15_oss2_v3": "Android 15 | 27 rows",
            "emu_a15_keystore_known_20261115": "Android 15 | 18 rows (known data)",
        },
    },
    "androidKeystoreLegacyEntries": {
        "name": "Keystore Legacy Entry Files",
        "description": "Entries of the Keystore files used before Keystore 2.0 "
                       "(misc/keystore/user_<n>/), one row per user folder, owner UID and alias, decoded "
                       "from the file names, with the kinds of file present for the entry and "
                       "the newest modified time the extraction recorded for them. File contents "
                       "are not read.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-15",
        "last_update_date": "2026-11-23",
        "requirements": "none",
        "category": "Encryption and Credentials",
        "notes": "Before Keystore 2.0, Keystore kept one file per entry under misc/keystore/user_<Android "
                 "user>/, named <uid>_<prefix>_<encoded alias>, with the entry's characteristics in "
                 ".<uid>_chr_<prefix>_<encoded alias> and the user's master key in .masterkey "
                 "(https://android.googlesource.com/platform/system/security/+/5a37034a3a97492cca75928193363c4f13bce5d3/keystore2/src/legacy_blob.rs#935);"
                 " the prefixes are USRPKEY, USRSKEY, USRCERT and CACERT (legacy_blob.rs#741). One row per "
                 "user folder, owner UID and alias, and one row for each .masterkey file. Alias is decoded as "
                 "decode_alias does (legacy_blob.rs#336); a name that does not decode is reported as stored "
                 "and logged (unexercised). Kinds lists the prefixes present for the entry, with "
                 "characteristics for a characteristics file. Files are the names as the extraction records "
                 "them in the evidence: a tar seeker stages a name holding ':' with '_', and the recorded name"
                 " is used (four files on pixel3_a11). Modified (UTC) is the newest modified time the "
                 "extraction recorded for the row's files, a file system time, not a time Keystore stored. "
                 "When the tool reads no UTC time for a file, that file adds nothing to Modified (UTC), and "
                 "its date and time count toward Modified (no zone, as stored), which holds the newest such "
                 "reading for the row, compared as text, with no zone conversion. That is the case for a FAT "
                 "directory entry, an exFAT directory entry (its stored UTC offset is not applied or shown "
                 "here) and a zip entry from which no UTC modification time is read: one with only its DOS "
                 "date and time, or with an extra field whose time is 0 or unreadable. Which zone such a "
                 "reading is in is not established. A zip entry's DOS date and time is shown as decoded, with "
                 "no validity check, so an unset one reads 1980-00-00 00:00:00. Modified (no zone, as stored) "
                 "had no value on any row of the registered images in sample_data on a run of 2026-11-23. The "
                 "reading was exercised on constructed FAT32, exFAT and DOS-only zip inputs. A row can fill "
                 "both columns when its files differ. Owner UID and Owner are resolved as in Keystore Key "
                 "Entries (fixed AID name, else packages.list under the same data root). File contents are not"
                 " read. Four files on galaxys10_a10 and four on cookbook_a11 have a 10-character alphanumeric"
                 " token where the AOSP form has the numeric UID; they are reported as stored with no Owner "
                 "UID or Alias, and logged. Measured: cookbook_a11 188 rows from 427 files (users 0 and 150), "
                 "galaxys10_a10 112 from 291, pixel3_a11 85 from 256 (users 0 and 10); every file under "
                 "user_<n> on those images is in a row. No known data was made: the Android 15 emulator used "
                 "for the Keystore 2.0 known data has no legacy files.",
        "paths": ('*/misc/keystore/user_*/*', '*/system/packages.list'),
        "output_types": "standard",
        "artifact_icon": "key",
        "sample_data": {
            "cookbook_a11": "Android 11 | 188 rows",
            "galaxys10_a10": "Android 10 | 112 rows",
            "pixel3_a11": "Android 11 | 85 rows",
            "pixel3_a12": "Android 12 | 0 rows (no files under user_<n>)",
            "hickman_a13": "Android 13 | 0 rows (no files under user_<n>)",
            "emu_a15_keystore_known_20261115": "Android 15 | 0 rows (no files under user_<n>)",
        },
    },
}

# Domain.aidl L22-L28
_DOMAINS = {0: 'APP', 1: 'GRANT', 2: 'SELINUX', 3: 'BLOB', 4: 'KEY_ID'}
# database.rs KeyType ToSql L300-L307 (Android 15); Attestation = 2 from the Android 13 source
_KEY_TYPES = {0: 'Client', 1: 'Super', 2: 'Attestation'}
# database.rs KeyLifeCycle ToSql L495-L503
_STATES = {0: 'Existing', 1: 'Live', 2: 'Unreferenced'}
# database.rs SubComponentType L734-L742
_SUBCOMPONENTS = {0: 'KEY_BLOB', 1: 'CERT', 2: 'CERT_CHAIN'}
# keystore2_key_contexts L8-L27
_SELINUX_NAMESPACES = {0: 'su_key', 1: 'shell_key', 100: 'vold_key', 101: 'odsign_key', 102: 'wifi_key',
                       103: 'locksettings_key', 120: 'resume_on_reboot_key'}
# KeyMint Tag.aidl and its enums
_TAG_PURPOSE = 0x20000001        # ENUM_REP | 1
_TAG_ALGORITHM = 0x10000002      # ENUM | 2
_TAG_KEY_SIZE = 0x30000003       # UINT | 3
_TAG_NO_AUTH_REQUIRED = 0x700001F7   # BOOL | 503
_TAG_AUTH_TIMEOUT = 0x300001F9   # UINT | 505
_TAG_UNLOCKED_DEVICE_REQUIRED = 0x700001FD   # BOOL | 509
_TAG_ORIGIN = 0x100002BE         # ENUM | 702
_ALGORITHMS = {1: 'RSA', 3: 'EC', 32: 'AES', 33: 'TRIPLE_DES', 128: 'HMAC'}
_PURPOSES = {0: 'ENCRYPT', 1: 'DECRYPT', 2: 'SIGN', 3: 'VERIFY', 5: 'WRAP_KEY', 6: 'AGREE_KEY', 7: 'ATTEST_KEY'}
_ORIGINS = {0: 'GENERATED', 1: 'DERIVED', 2: 'IMPORTED', 3: 'RESERVED', 4: 'SECURELY_IMPORTED'}
_SECURITY_LEVELS = {0: 'SOFTWARE', 1: 'TRUSTED_ENVIRONMENT', 2: 'STRONGBOX', 100: 'KEYSTORE'}

# android_filesystem_config.h: the fixed AIDs below 10000
_AIDS = {
    0: 'root', 1: 'daemon', 2: 'bin', 3: 'sys', 1000: 'system', 1001: 'radio', 1002: 'bluetooth',
    1003: 'graphics', 1004: 'input', 1005: 'audio', 1006: 'camera', 1007: 'log', 1008: 'compass',
    1009: 'mount', 1010: 'wifi', 1011: 'adb', 1012: 'install', 1013: 'media', 1014: 'dhcp',
    1015: 'sdcard_rw', 1016: 'vpn', 1017: 'keystore', 1018: 'usb', 1019: 'drm', 1020: 'mdnsr',
    1021: 'gps', 1023: 'media_rw', 1024: 'mtp', 1026: 'drmrpc', 1027: 'nfc', 1028: 'sdcard_r',
    1029: 'clat', 1030: 'loop_radio', 1031: 'media_drm', 1032: 'package_info', 1033: 'sdcard_pics',
    1034: 'sdcard_av', 1035: 'sdcard_all', 1036: 'logd', 1037: 'shared_relro', 1038: 'dbus',
    1039: 'tlsdate', 1040: 'media_ex', 1041: 'audioserver', 1042: 'metrics_coll', 1043: 'metricsd',
    1044: 'webserv', 1045: 'debuggerd', 1046: 'media_codec', 1047: 'cameraserver', 1048: 'firewall',
    1049: 'trunks', 1050: 'nvram', 1051: 'dns', 1052: 'dns_tether', 1053: 'webview_zygote',
    1054: 'vehicle_network', 1055: 'media_audio', 1056: 'media_video', 1057: 'media_image',
    1058: 'tombstoned', 1059: 'media_obb', 1060: 'ese', 1061: 'ota_update', 1062: 'automotive_evs',
    1063: 'lowpan', 1064: 'hsm', 1065: 'reserved_disk', 1066: 'statsd', 1067: 'incidentd',
    1068: 'secure_element', 1069: 'lmkd', 1070: 'llkd', 1071: 'iorapd', 1072: 'gpu_service',
    1073: 'network_stack', 1074: 'gsid', 1075: 'fsverity_cert', 1076: 'credstore',
    1077: 'external_storage', 1078: 'ext_data_rw', 1079: 'ext_obb_rw', 1080: 'context_hub',
    1081: 'virtualizationservice', 1082: 'artd', 1083: 'uwb', 1084: 'thread_network', 1085: 'diced',
    1086: 'dmesgd', 1087: 'jc_weaver', 1088: 'jc_strongbox', 1089: 'jc_identitycred',
    1090: 'sdk_sandbox', 1091: 'security_log_writer', 1092: 'prng_seeder', 1093: 'uprobestats',
    2000: 'shell', 2001: 'cache', 2002: 'diag', 3001: 'net_bt_admin', 3002: 'net_bt', 3003: 'inet',
    3004: 'net_raw', 3005: 'net_admin', 3006: 'net_bw_stats', 3007: 'net_bw_acct', 3009: 'readproc',
    3010: 'wakelock', 3011: 'uhid', 3012: 'readtracefs', 3013: 'virtualmachine', 9997: 'everybody',
    9998: 'misc', 9999: 'nobody',
}
_AID_USER_OFFSET = 100000

# legacy_blob.rs KNOWN_KEYSTORE_PREFIXES L747-L748, file names L935-L956
_LEGACY_NAME = re.compile(r'^(?P<chr>\.)?(?P<uid>\d+)_(?P<c>chr_)?(?P<prefix>USRPKEY|USRSKEY|USRCERT|CACERT)_(?P<alias>.*)$')


def _label(mapping, value):
    if value is None or value == '':
        return ''
    name = mapping.get(value)
    return f'{name} ({value})' if name else str(value)


def _ms_to_utc(value):
    if not isinstance(value, int) or value <= 0:
        return ''
    try:
        return datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(milliseconds=value)
    except OverflowError:
        return ''


def _data_root(path, marker):
    '''The part of a path before marker ("/misc/keystore/" or "/system/packages.list").'''
    norm = path.replace(os.sep, '/')
    index = norm.find(marker)
    return norm[:index] if index >= 0 else None


def _packages_by_root(files_found):
    '''{data root: {app id: [package, ...]}} from each packages.list (first column name, second uid).'''
    found = {}
    for path in files_found:
        root = _data_root(path, '/system/packages.list')
        if root is None or not path.replace(os.sep, '/').endswith('/system/packages.list'):
            continue
        names = found.setdefault(root, {})
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as handle:
                for line in handle:
                    parts = line.split()
                    if len(parts) >= 2 and parts[1].isdigit():
                        names.setdefault(int(parts[1]) % _AID_USER_OFFSET, set()).add(parts[0])
        except OSError as ex:
            logfunc(f'Keystore: could not read {path}: {ex}')
    return {root: {appid: sorted(n) for appid, n in names.items()} for root, names in found.items()}


def _uid_owner(uid, packages):
    '''The fixed AID name of the uid's app id, else its packages.list names, else blank.'''
    if not isinstance(uid, int) or uid < 0:
        return ''
    appid = uid % _AID_USER_OFFSET
    if appid in _AIDS:
        return f'AID {_AIDS[appid]}'
    if appid in packages:
        return '; '.join(packages[appid])
    return ''


def _dedupe_identical(paths):
    by_hash = {}
    for path in sorted(paths):
        try:
            with open(path, 'rb') as handle:
                digest = hashlib.sha1(handle.read()).hexdigest()
        except OSError as ex:
            logfunc(f'Keystore: could not hash {path}: {ex}')
            by_hash[path] = path
            continue
        by_hash.setdefault(digest, path)
    return list(by_hash.values())


def _params(db):
    '''{keyentryid: {tag: [(value, security_level), ...]}}'''
    params = {}
    for key_id, tag, data, level in db.execute(
            'SELECT keyentryid, tag, data, security_level FROM keyparameter ORDER BY rowid'):
        params.setdefault(key_id, {}).setdefault(tag, []).append((data, level))
    return params


@artifact_processor
def androidKeystore2Keys(context):
    files_found = context.get_files_found()
    packages_by_root = _packages_by_root(files_found)
    databases = _dedupe_identical([p for p in files_found if p.endswith('persistent.sqlite')])
    data_list = []
    sources = []
    for db_path in databases:
        packages = packages_by_root.get(_data_root(db_path, '/misc/keystore/'), {})
        if not packages:
            logfunc(f'Keystore Key Entries: no packages.list beside {db_path}; app owners not named')
        db = open_sqlite_db_readonly(db_path)
        if db is None:
            logfunc(f'Keystore Key Entries: could not open {db_path}')
            continue
        try:
            tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if 'keyentry' not in tables:
                logfunc(f'Keystore Key Entries: no keyentry table in {db_path}')
                sources.append(db_path)
                continue
            created = {}
            if 'keymetadata' in tables:
                # KeyMetaEntry CreationDate is the first variant, tag 0, milliseconds since 1970
                created = dict(db.execute('SELECT keyentryid, data FROM keymetadata WHERE tag = 0'))
            params = _params(db) if 'keyparameter' in tables else {}
            blobs = {}
            if 'blobentry' in tables:
                for key_id, sub in db.execute('SELECT DISTINCT keyentryid, subcomponent_type FROM blobentry '
                                              'ORDER BY keyentryid, subcomponent_type'):
                    blobs.setdefault(key_id, []).append(_SUBCOMPONENTS.get(sub, str(sub)))
            grants = {}
            if 'grant' in tables:
                for key_id, grantee, access in db.execute(
                        'SELECT keyentryid, grantee, access_vector FROM "grant" ORDER BY id'):
                    owner = _uid_owner(grantee, packages)
                    grants.setdefault(key_id, []).append(
                        f'{grantee}{f" ({owner})" if owner else ""}, access vector {access}')
            rows = db.execute('SELECT id, key_type, domain, namespace, alias, state FROM keyentry')
            for key_id, key_type, domain, namespace, alias, state in rows:
                kp = params.get(key_id, {})
                algorithm = kp.get(_TAG_ALGORITHM, [(None, None)])[0]
                if domain == 0 and key_type == 1:
                    user = namespace if isinstance(namespace, int) else ''
                    owner = 'Keystore super key'
                elif domain == 0:
                    user = namespace // _AID_USER_OFFSET if isinstance(namespace, int) else ''
                    owner = _uid_owner(namespace, packages)
                elif domain == 2:
                    user = ''
                    owner = _SELINUX_NAMESPACES.get(namespace, '')
                else:
                    user, owner = '', ''
                if isinstance(alias, bytes):
                    alias = alias.decode('utf-8', 'replace')
                data_list.append((
                    _ms_to_utc(created.get(key_id)),
                    alias if alias is not None else '',
                    _label(_KEY_TYPES, key_type),
                    _label(_DOMAINS, domain),
                    namespace if namespace is not None else '',
                    user,
                    owner,
                    _label(_STATES, state),
                    _label(_ALGORITHMS, algorithm[0]),
                    kp.get(_TAG_KEY_SIZE, [('', None)])[0][0],
                    ', '.join(_label(_PURPOSES, v) for v, _ in kp.get(_TAG_PURPOSE, [])),
                    _label(_SECURITY_LEVELS, algorithm[1]),
                    _label(_ORIGINS, kp.get(_TAG_ORIGIN, [(None, None)])[0][0]),
                    'Yes' if _TAG_NO_AUTH_REQUIRED in kp else '',
                    kp.get(_TAG_AUTH_TIMEOUT, [('', None)])[0][0],
                    'Yes' if _TAG_UNLOCKED_DEVICE_REQUIRED in kp else '',
                    ', '.join(blobs.get(key_id, [])),
                    '\n'.join(grants.get(key_id, [])),
                    key_id,
                ))
            sources.append(db_path)
        except sqlite3.Error as ex:
            logfunc(f'Keystore Key Entries: could not read {db_path}: {ex}')
        finally:
            db.close()

    data_headers = (
        ('Created (UTC)', 'datetime'), 'Alias', 'Key Type', 'Domain', 'Namespace', 'Android User', 'Owner',
        'State', 'Algorithm', 'Key Size', 'Purposes', 'Security Level', 'Origin', 'No Auth Required',
        'Auth Timeout (s)', 'Unlocked Device Required', 'Stored Blobs', 'Grants', 'Key Entry ID')
    return data_headers, data_list, '\n'.join(sources)


def _decode_alias(name):
    '''legacy_blob.rs decode_alias L336-L360: bytes '+'..'.' start a two-character escape.'''
    out = bytearray()
    multi = None
    for c in name.encode('utf-8', 'surrogateescape'):
        if multi is not None:
            if ord('0') <= c <= ord('o'):
                out.append(multi | (c - ord('0')))
                multi = None
                continue
            return None
        if ord('+') <= c <= ord('.'):
            multi = (c - ord('+')) << 6
        elif ord('0') <= c <= ord('~'):
            out.append(c)
        else:
            return None
    if multi is not None:
        return None
    try:
        return out.decode('utf-8')
    except UnicodeDecodeError:
        return None


def _sec_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=value // 1)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


def _usable(value):
    """Whether a recorded time is a nonzero, finite number."""
    return isinstance(value, (int, float)) and value != 0 and value == value and abs(value) != float('inf')


def _file_times(seeker, path):
    """(UTC seconds, reading with no zone) the input records for a staged file.

    The staged copy's own time is not used: for a FAT, exFAT or DOS-only zip reading it is
    that reading placed in the examiner's time zone.
    """
    infos = getattr(seeker, 'file_infos', None) or {}
    windows = str(path).replace('/', '\\')
    bare = windows.removeprefix('\\\\?\\')
    info = next((infos[name] for name in (str(path), windows, bare, '\\\\?\\' + bare)
                 if name in infos), None)
    times = getattr(info, 'times', None)
    modified = getattr(times, 'modified', None)
    if _usable(modified):
        return modified, ''
    # a reading with no zone comes before the older field, which is never read as its UTC time
    reading = getattr(times, 'modified_no_zone', None)
    if reading:
        return None, reading
    modified = getattr(info, 'modification_date', None)
    if _usable(modified):
        return modified, ''
    return None, ''


@artifact_processor
def androidKeystoreLegacyEntries(context):
    files_found = context.get_files_found()
    packages_by_root = _packages_by_root(files_found)
    try:
        seeker = context.get_seeker()
    except ValueError:
        seeker = None
    entries = {}
    seen = set()
    for path in sorted(files_found):
        # The name as the evidence holds it: a seeker can rename a staged copy (a tar's ':'
        # is staged as '_'), and only the platform separator is a separator, since a legacy
        # alias can hold a literal backslash.
        info = seeker.file_infos.get(path) if seeker else None
        source = getattr(info, 'source_path', '') or ''
        norm = path.replace(os.sep, '/')
        match = re.search(r'/misc/keystore/user_(\d+)/([^/]+)$', norm)
        if not match or not os.path.isfile(path):
            continue
        user, name = int(match.group(1)), match.group(2)
        source_match = re.search(r'misc/keystore/user_(\d+)/([^/]+)$', source.replace(os.sep, '/'))
        if source_match and int(source_match.group(1)) == user:
            name = source_match.group(2)
        root = norm[:match.start()]
        # the same file can be staged twice under one extraction; keep one per user folder and name
        if (root, user, name) in seen:
            continue
        seen.add((root, user, name))
        parsed = _LEGACY_NAME.match(name)
        if name == '.masterkey':
            key = (root, user, '', '.masterkey')
            kind, uid, alias = 'masterkey', '', ''
        elif parsed and bool(parsed.group('chr')) == bool(parsed.group('c')):
            alias = _decode_alias(parsed.group('alias'))
            uid = int(parsed.group('uid'))
            kind = parsed.group('prefix') + (' characteristics' if parsed.group('chr') else '')
            if alias is None:
                logfunc(f'Keystore Legacy Entry Files: alias of {name} did not decode; reported as stored')
                alias = parsed.group('alias')
            key = (root, user, uid, alias)
        else:
            logfunc(f'Keystore Legacy Entry Files: file name not in the AOSP form, reported as stored: {name}')
            key = (root, user, '', name)
            kind, uid, alias = '', '', ''
        entry = entries.setdefault(key, {'uid': uid, 'alias': alias, 'kinds': [], 'files': [], 'mtime': None, 'no_zone': '',
                                         'paths': []})
        if kind and kind not in entry['kinds']:
            entry['kinds'].append(kind)
        entry['files'].append(name)
        entry['paths'].append(path)
        recorded, no_zone = _file_times(seeker, path)
        mtime = _sec_to_utc(recorded)
        if mtime and (entry['mtime'] is None or mtime > entry['mtime']):
            entry['mtime'] = mtime
        if no_zone > entry['no_zone']:
            entry['no_zone'] = no_zone

    data_list = []
    sources = []
    for (root, user, _uid, _alias), entry in sorted(entries.items(), key=lambda kv: (kv[0][0], kv[0][1],
                                                                                     str(kv[0][2]), kv[0][3])):
        uid = entry['uid']
        data_list.append((
            entry['mtime'] or '',
            entry['no_zone'],
            user,
            uid,
            _uid_owner(uid, packages_by_root.get(root, {})) if uid != '' else '',
            entry['alias'],
            ', '.join(sorted(entry['kinds'])),
            '\n'.join(entry['files']),
        ))
        sources.extend(entry['paths'])

    data_headers = (('Modified (UTC)', 'datetime'), 'Modified (no zone, as stored)', 'Android User', 'Owner UID',
                    'Owner', 'Alias', 'Kinds', 'Files')
    return data_headers, data_list, '\n'.join(dict.fromkeys(sources))
