__artifacts_v2__ = {
    "package_dex_usage_app_code": {
        "name": "Dex Usage - App Code Loads",
        "description": "Primary dex files a package loaded from its own installation, with the time of the most "
         "recent load ART Service recorded.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Android System",
        "notes": "Read from the ART Service dex use store at /data/system/package-dex-usage.pb. Reference: "
         "Android Open Source Project, art/libartservice/service/proto/dex_use.proto for the "
         "schema and libartservice/service/java/com/android/server/art/DexUseManagerLocal.java for "
         "the writer, which names that path in its own FILENAME constant. The field numbers taken "
         "here are identical at android-14.0.0_r1, the first release to ship ART Service, at "
         "android-15.0.0_r1 and at main: DexUseProto package_dex_use 1; PackageDexUseProto "
         "owning_package_name 1, primary_dex_use 2, secondary_dex_use 3; PrimaryDexUseProto "
         "dex_file 1, record 2; PrimaryDexUseRecordProto loading_package_name 1, isolated_process "
         "2, last_used_at_ms 3; SecondaryDexUseProto dex_file 1, user_id 2, record 3; "
         "SecondaryDexUseRecordProto loading_package_name 1, isolated_process 2, "
         "class_loader_context 3, abi_name 4, last_used_at_ms 5. The file is read field by field "
         "off the protobuf wire format, taking only those fields and skipping every other field by "
         "its length. This artifact reports the primary dex records whose loading package is the "
         "package that owns the file, which the platform writes when a package loads its own base "
         "or split APK. A row records that the package's code was loaded; it does not "
         "record what caused that to happen, and a process "
         "can be started by the system rather than by a person. Last Loaded is the record's "
         "last_used_at_ms, which DexUseManagerLocal takes from System.currentTimeMillis(), so it "
         "is the device wall clock at the moment the load was recorded, rendered here in UTC. It "
         "carried a value on all 8147 rows this module produced across the tested images. The "
         "store keeps one record per dex file and per loader and overwrites its timestamp, so a "
         "row gives the most recent load and not a history of loads. DexUseManagerLocal keys those "
         "records on a DexLoader, which carries the loading package together with whether the load "
         "went into an isolated process, so one package can hold two rows for the same dex file "
         "that differ only in Isolated Process and time: that happened on 23 pairings across 6 of "
         "the tested images and is not duplication. The platform writes the file through a "
         "debouncer with a 15 second minimum interval and also on the shutdown broadcast, so a "
         "load in the last seconds before acquisition can be absent. Isolated Process is the "
         "record's isolated_process flag, which the platform sets for a load into an isolated "
         "process. It was true on 21 of the 4347 rows of this artifact across the tested images "
         "and false on the rest, so a true value is uncommon rather than absent. An entry outlives "
         "the package it names until the platform's cleanup pass runs: "
         "DexUseManagerLocal.cleanup() drops entries whose owning or loading package is no longer "
         "installed, and ArtManagerLocal.cleanup() invokes it as part of the platform's routine "
         "maintenance. Measured on an Android 15 emulator whose package list no longer carried a "
         "test package that had been removed with pm uninstall: the store still named that "
         "package, as an owning package and as a loading package. A name here is therefore not "
         "evidence the package is still on the device, and its absence is not evidence it never "
         "was. This store is written from Android 14. Across the 39 registered Android corpora it "
         "is present on 25 images, which report Android 14, 15, 16 and 17, and on none reporting "
         "Android 13 or older; those 11 images carry a text file named package-dex-usage.list in "
         "the same folder, which records the same package, dex file and loading package "
         "relationships in the platform's older format and which this artifact does not read. 4 of "
         "the images carrying the protobuf store also carry that older file reduced to its 38 byte "
         "header line, and 2 carry a populated one. The remaining 3 corpora reporting no rows are "
         "extractions that carry no /data/system content at all rather than devices without the "
         "store. One set of rows is reported per store found, each row carrying its own Source "
         "File, so an extraction that holds the folder under more than one root reports each copy "
         "rather than merging them; on the tested images the store was present once per "
         "extraction. The path pattern is not anchored on a data/ prefix, so a raw userdata "
         "partition image that carries system/ at its root is matched as well. The three Dex Usage "
         "artifacts partition the store's records without overlap: this one, Cross-Package Code "
         "Loads, and Secondary Dex Loads. Every field of every message in the schema is reported "
         "across them, so nothing in the store is left unread.",
        "paths": ('*/system/package-dex-usage.pb',),
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "0 rows",
            "anne_a15": "Android 15 | 301 rows",
            "cookbook_a11": "0 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 78 rows",
            "emu_a15_oss_v10": "Android 15 | 141 rows",
            "emu_a15_oss_v11": "Android 15 | 144 rows",
            "emu_a15_oss_v12": "Android 15 | 148 rows",
            "emu_a15_oss_v13": "Android 15 | 150 rows",
            "emu_a15_oss_v14": "Android 15 | 150 rows",
            "emu_a15_oss_v15": "Android 15 | 161 rows",
            "emu_a15_oss_v16": "Android 15 | 166 rows",
            "emu_a15_oss_v17": "Android 15 | 173 rows",
            "emu_a15_oss_v2": "Android 15 | 88 rows",
            "emu_a15_oss_v3": "Android 15 | 90 rows",
            "emu_a15_oss_v4": "Android 15 | 103 rows",
            "emu_a15_oss_v5": "Android 15 | 119 rows",
            "emu_a15_oss_v6": "Android 15 | 124 rows",
            "emu_a15_oss_v7": "Android 15 | 130 rows",
            "emu_a15_oss_v8": "Android 15 | 130 rows",
            "emu_a15_oss_v9": "Android 15 | 131 rows",
            "falken_a326u_a13": "0 rows",
            "galaxys10_a10": "0 rows",
            "hc_pixel8pro_a16": "Android 16 | 307 rows",
            "hc_pixel8pro_a17": "Android 17 | 289 rows",
            "hc_pixel8pro_a17_ail": "0 rows",
            "kevin_pocox7_a15": "Android 15 | 227 rows",
            "pixel3_a11": "0 rows",
            "pixel3_a12": "0 rows",
            "pixel7a_a14": "Android 14 | 265 rows",
            "russell_a14": "Android 14 | 187 rows",
            "russell_pixel6a_a13": "0 rows",
            "s20fe_a13": "0 rows",
            "samsunga53_a14": "Android 14 | 203 rows",
            "samsungs20_a13": "0 rows",
            "sharon_a13": "0 rows",
            "sharon_a14": "Android 14 | 342 rows",
            "userb2_a13": "0 rows",
        },
    },
    "package_dex_usage_cross_package": {
        "name": "Dex Usage - Cross-Package Code Loads",
        "description": "Primary dex files one package loaded from a different package's installation, with the "
         "time of the most recent load.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Android System",
        "notes": "Read from the ART Service dex use store at /data/system/package-dex-usage.pb. Reference: "
         "Android Open Source Project, art/libartservice/service/proto/dex_use.proto for the "
         "schema and libartservice/service/java/com/android/server/art/DexUseManagerLocal.java for "
         "the writer, which names that path in its own FILENAME constant. The field numbers taken "
         "here are identical at android-14.0.0_r1, the first release to ship ART Service, at "
         "android-15.0.0_r1 and at main: DexUseProto package_dex_use 1; PackageDexUseProto "
         "owning_package_name 1, primary_dex_use 2, secondary_dex_use 3; PrimaryDexUseProto "
         "dex_file 1, record 2; PrimaryDexUseRecordProto loading_package_name 1, isolated_process "
         "2, last_used_at_ms 3; SecondaryDexUseProto dex_file 1, user_id 2, record 3; "
         "SecondaryDexUseRecordProto loading_package_name 1, isolated_process 2, "
         "class_loader_context 3, abi_name 4, last_used_at_ms 5. The file is read field by field "
         "off the protobuf wire format, taking only those fields and skipping every other field by "
         "its length. This artifact reports the primary dex records whose loading package differs "
         "from the package that owns the file, which is one package loading another package's "
         "installed code. Last Loaded is the record's last_used_at_ms, which DexUseManagerLocal "
         "takes from System.currentTimeMillis(), so it is the device wall clock at the moment the "
         "load was recorded, rendered here in UTC. It carried a value on all 8147 rows this module "
         "produced across the tested images. The store keeps one record per dex file and per "
         "loader and overwrites its timestamp, so a row gives the most recent load and not a "
         "history of loads. DexUseManagerLocal keys those records on a DexLoader, which carries "
         "the loading package together with whether the load went into an isolated process, so one "
         "package can hold two rows for the same dex file that differ only in Isolated Process and "
         "time: that happened on 23 pairings across 6 of the tested images and is not duplication. "
         "The platform writes the file through a debouncer with a 15 second minimum interval and "
         "also on the shutdown broadcast, so a load in the last seconds before acquisition can be "
         "absent. One package loading another's code is ordinary platform behaviour far more often "
         "than not: of the 2232 rows across the tested images, 1159 name Google Play services as "
         "the owning package and 458 the Android System WebView, which apps load to render web "
         "content, so the row worth attention is an unexpected pairing rather than the presence of "
         "pairings. 1549 of the rows load a file under /data/app and 683 a platform path under "
         "/system, /apex, /product, /vendor or /system_ext. Isolated Process is the record's "
         "isolated_process flag, set for a load into an isolated process; it was true on 3 of "
         "these 2232 rows across the tested images. An entry outlives the package it names until "
         "the platform's cleanup pass runs: DexUseManagerLocal.cleanup() drops entries whose "
         "owning or loading package is no longer installed, and ArtManagerLocal.cleanup() invokes "
         "it as part of the platform's routine maintenance. Measured on an Android 15 emulator "
         "whose package list no longer carried a test package that had been removed with pm "
         "uninstall: the store still named that package, as an owning package and as a loading "
         "package. A name here is therefore not evidence the package is still on the device, and "
         "its absence is not evidence it never was. This store is written from Android 14. Across "
         "the 39 registered Android corpora it is present on 25 images, which report Android 14, "
         "15, 16 and 17, and on none reporting Android 13 or older; those 11 images carry a text "
         "file named package-dex-usage.list in the same folder, which records the same package, "
         "dex file and loading package relationships in the platform's older format and which this "
         "artifact does not read. 4 of the images carrying the protobuf store also carry that "
         "older file reduced to its 38 byte header line, and 2 carry a populated one. The "
         "remaining 3 corpora reporting no rows are extractions that carry no /data/system content "
         "at all rather than devices without the store. One set of rows is reported per store "
         "found, each row carrying its own Source File, so an extraction that holds the folder "
         "under more than one root reports each copy rather than merging them; on the tested "
         "images the store was present once per extraction. The path pattern is not anchored on a "
         "data/ prefix, so a raw userdata partition image that carries system/ at its root is "
         "matched as well. The three Dex Usage artifacts partition the store's records without "
         "overlap: App Code Loads, this one, and Secondary Dex Loads. Every field of every message "
         "in the schema is reported across them, so nothing in the store is left unread.",
        "paths": ('*/system/package-dex-usage.pb',),
        "output_types": "standard",
        "artifact_icon": "share-2",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "0 rows",
            "anne_a15": "Android 15 | 126 rows",
            "cookbook_a11": "0 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 29 rows",
            "emu_a15_oss_v10": "Android 15 | 44 rows",
            "emu_a15_oss_v11": "Android 15 | 47 rows",
            "emu_a15_oss_v12": "Android 15 | 50 rows",
            "emu_a15_oss_v13": "Android 15 | 51 rows",
            "emu_a15_oss_v14": "Android 15 | 53 rows",
            "emu_a15_oss_v15": "Android 15 | 61 rows",
            "emu_a15_oss_v16": "Android 15 | 64 rows",
            "emu_a15_oss_v17": "Android 15 | 71 rows",
            "emu_a15_oss_v2": "Android 15 | 31 rows",
            "emu_a15_oss_v3": "Android 15 | 31 rows",
            "emu_a15_oss_v4": "Android 15 | 31 rows",
            "emu_a15_oss_v5": "Android 15 | 35 rows",
            "emu_a15_oss_v6": "Android 15 | 36 rows",
            "emu_a15_oss_v7": "Android 15 | 36 rows",
            "emu_a15_oss_v8": "Android 15 | 36 rows",
            "emu_a15_oss_v9": "Android 15 | 36 rows",
            "falken_a326u_a13": "0 rows",
            "galaxys10_a10": "0 rows",
            "hc_pixel8pro_a16": "Android 16 | 336 rows",
            "hc_pixel8pro_a17": "Android 17 | 318 rows",
            "hc_pixel8pro_a17_ail": "0 rows",
            "kevin_pocox7_a15": "Android 15 | 252 rows",
            "pixel3_a11": "0 rows",
            "pixel3_a12": "0 rows",
            "pixel7a_a14": "Android 14 | 202 rows",
            "russell_a14": "Android 14 | 102 rows",
            "russell_pixel6a_a13": "0 rows",
            "s20fe_a13": "0 rows",
            "samsunga53_a14": "Android 14 | 57 rows",
            "samsungs20_a13": "0 rows",
            "sharon_a13": "0 rows",
            "sharon_a14": "Android 14 | 97 rows",
            "userb2_a13": "0 rows",
        },
    },
    "package_dex_usage_secondary": {
        "name": "Dex Usage - Secondary Dex Loads",
        "description": "Dex, APK and JAR files an app loaded from its own data directory rather than from its "
         "installation, with the time of the most recent load.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Android System",
        "notes": "Read from the ART Service dex use store at /data/system/package-dex-usage.pb. Reference: "
         "Android Open Source Project, art/libartservice/service/proto/dex_use.proto for the "
         "schema and libartservice/service/java/com/android/server/art/DexUseManagerLocal.java for "
         "the writer, which names that path in its own FILENAME constant. The field numbers taken "
         "here are identical at android-14.0.0_r1, the first release to ship ART Service, at "
         "android-15.0.0_r1 and at main: DexUseProto package_dex_use 1; PackageDexUseProto "
         "owning_package_name 1, primary_dex_use 2, secondary_dex_use 3; PrimaryDexUseProto "
         "dex_file 1, record 2; PrimaryDexUseRecordProto loading_package_name 1, isolated_process "
         "2, last_used_at_ms 3; SecondaryDexUseProto dex_file 1, user_id 2, record 3; "
         "SecondaryDexUseRecordProto loading_package_name 1, isolated_process 2, "
         "class_loader_context 3, abi_name 4, last_used_at_ms 5. The file is read field by field "
         "off the protobuf wire format, taking only those fields and skipping every other field by "
         "its length. This artifact reports the secondary dex records. DexUseManagerLocal's own "
         "comment describes a secondary dex file as an APK or JAR an app adds to its own data "
         "directory and loads dynamically, as opposed to the base and split APKs of its "
         "installation. Last Loaded is the record's last_used_at_ms, which DexUseManagerLocal "
         "takes from System.currentTimeMillis(), so it is the device wall clock at the moment the "
         "load was recorded, rendered here in UTC. It carried a value on all 8147 rows this module "
         "produced across the tested images. The store keeps one record per dex file and per "
         "loader and overwrites its timestamp, so a row gives the most recent load and not a "
         "history of loads. DexUseManagerLocal keys those records on a DexLoader, which carries "
         "the loading package together with whether the load went into an isolated process, so one "
         "package can hold two rows for the same dex file that differ only in Isolated Process and "
         "time: that happened on 23 pairings across 6 of the tested images and is not duplication. "
         "The platform writes the file through a debouncer with a 15 second minimum interval and "
         "also on the shutdown broadcast, so a load in the last seconds before acquisition can be "
         "absent. Android User is the record's user_id. The platform stores it in a wrapper that "
         "is present but empty when the value is zero, so it is read as zero rather than left "
         "blank for the first user. It was 0 on the 25 tested images carrying rows here and "
         "additionally 10, a second Android user, on 18 of them. Class Loader Context is the "
         "record's class_loader_context, the dependency chain the loader was given, as stored; it "
         "carried a value on all 1568 rows of the tested images. ABI is the record's abi_name; it "
         "was arm64-v8a on all 1568 rows of the tested images, and a load for another ABI would be "
         "recorded here. Isolated Process was false on all 1568 of these rows across the tested "
         "images. An entry outlives the package it names until the platform's cleanup pass runs: "
         "DexUseManagerLocal.cleanup() drops entries whose owning or loading package is no longer "
         "installed, and ArtManagerLocal.cleanup() invokes it as part of the platform's routine "
         "maintenance. Measured on an Android 15 emulator whose package list no longer carried a "
         "test package that had been removed with pm uninstall: the store still named that "
         "package, as an owning package and as a loading package. A name here is therefore not "
         "evidence the package is still on the device, and its absence is not evidence it never "
         "was. This store is written from Android 14. Across the 39 registered Android corpora it "
         "is present on 25 images, which report Android 14, 15, 16 and 17, and on none reporting "
         "Android 13 or older; those 11 images carry a text file named package-dex-usage.list in "
         "the same folder, which records the same package, dex file and loading package "
         "relationships in the platform's older format and which this artifact does not read. 4 of "
         "the images carrying the protobuf store also carry that older file reduced to its 38 byte "
         "header line, and 2 carry a populated one. The remaining 3 corpora reporting no rows are "
         "extractions that carry no /data/system content at all rather than devices without the "
         "store. One set of rows is reported per store found, each row carrying its own Source "
         "File, so an extraction that holds the folder under more than one root reports each copy "
         "rather than merging them; on the tested images the store was present once per "
         "extraction. The path pattern is not anchored on a data/ prefix, so a raw userdata "
         "partition image that carries system/ at its root is matched as well. The three Dex Usage "
         "artifacts partition the store's records without overlap: App Code Loads, Cross-Package "
         "Code Loads, and this one. Every field of every message in the schema is reported across "
         "them, so nothing in the store is left unread.",
        "paths": ('*/system/package-dex-usage.pb',),
        "output_types": "standard",
        "artifact_icon": "terminal",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "0 rows",
            "anne_a15": "Android 15 | 37 rows",
            "cookbook_a11": "0 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 30 rows",
            "emu_a15_oss_v10": "Android 15 | 63 rows",
            "emu_a15_oss_v11": "Android 15 | 69 rows",
            "emu_a15_oss_v12": "Android 15 | 72 rows",
            "emu_a15_oss_v13": "Android 15 | 74 rows",
            "emu_a15_oss_v14": "Android 15 | 77 rows",
            "emu_a15_oss_v15": "Android 15 | 99 rows",
            "emu_a15_oss_v16": "Android 15 | 108 rows",
            "emu_a15_oss_v17": "Android 15 | 127 rows",
            "emu_a15_oss_v2": "Android 15 | 30 rows",
            "emu_a15_oss_v3": "Android 15 | 30 rows",
            "emu_a15_oss_v4": "Android 15 | 34 rows",
            "emu_a15_oss_v5": "Android 15 | 36 rows",
            "emu_a15_oss_v6": "Android 15 | 36 rows",
            "emu_a15_oss_v7": "Android 15 | 36 rows",
            "emu_a15_oss_v8": "Android 15 | 36 rows",
            "emu_a15_oss_v9": "Android 15 | 36 rows",
            "falken_a326u_a13": "0 rows",
            "galaxys10_a10": "0 rows",
            "hc_pixel8pro_a16": "Android 16 | 59 rows",
            "hc_pixel8pro_a17": "Android 17 | 74 rows",
            "hc_pixel8pro_a17_ail": "0 rows",
            "kevin_pocox7_a15": "Android 15 | 54 rows",
            "pixel3_a11": "0 rows",
            "pixel3_a12": "0 rows",
            "pixel7a_a14": "Android 14 | 153 rows",
            "russell_a14": "Android 14 | 118 rows",
            "russell_pixel6a_a13": "0 rows",
            "s20fe_a13": "0 rows",
            "samsunga53_a14": "Android 14 | 11 rows",
            "samsungs20_a13": "0 rows",
            "sharon_a13": "0 rows",
            "sharon_a14": "Android 14 | 69 rows",
            "userb2_a13": "0 rows",
        },
    },
}

import os
from datetime import datetime, timedelta, timezone

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, logfunc

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)

# Field numbers are taken from the ART Service schema that writes this file,
# art/libartservice/service/proto/dex_use.proto. Read at android-15.0.0_r1 and checked
# unchanged at android-14.0.0_r1, the first release to ship ART Service, and at main:
#   DexUseProto              package_dex_use 1
#   PackageDexUseProto       owning_package_name 1, primary_dex_use 2, secondary_dex_use 3
#   PrimaryDexUseProto       dex_file 1, record 2
#   PrimaryDexUseRecordProto loading_package_name 1, isolated_process 2, last_used_at_ms 3
#   SecondaryDexUseProto     dex_file 1, user_id 2, record 3
#   SecondaryDexUseRecordProto loading_package_name 1, isolated_process 2,
#                              class_loader_context 3, abi_name 4, last_used_at_ms 5
# user_id is the Int32Value wrapper from the sibling common.proto (value 1), which the
# schema requires to be set so absence and a zero can be told apart.
_TOP_FIELDS = {1}
_PACKAGE_FIELDS = {1, 2, 3}
_PRIMARY_FIELDS = {1, 2}
_PRIMARY_RECORD_FIELDS = {1, 2, 3}
_SECONDARY_FIELDS = {1, 2, 3}
_SECONDARY_RECORD_FIELDS = {1, 2, 3, 4, 5}
_INT32_VALUE_FIELDS = {1}


def _varint(data, pos):
    result = shift = 0
    while True:
        byte = data[pos]
        pos += 1
        result |= (byte & 0x7f) << shift
        shift += 7
        if not byte & 0x80:
            return result, pos


def _wire_fields(data, want):
    """Top-level fields of one protobuf message: {str(field number): value}, repeated as a list.

    Reads the wire format directly (varint 0, 64-bit 1, length-delimited 2, 32-bit 5) and skips
    every field not in `want` by its length, so nothing is guessed at and no schema-less decoder
    is needed. A malformed message raises IndexError or ValueError."""
    out = {}
    pos, end = 0, len(data)
    while pos < end:
        tag, pos = _varint(data, pos)
        field, wire = tag >> 3, tag & 7
        if wire == 0:
            value, pos = _varint(data, pos)
        elif wire == 1:
            value, pos = data[pos:pos + 8], pos + 8
        elif wire == 2:
            length, pos = _varint(data, pos)
            value, pos = data[pos:pos + length], pos + length
        elif wire == 5:
            value, pos = data[pos:pos + 4], pos + 4
        else:
            raise ValueError(f'unsupported wire type {wire} at offset {pos}')
        if field not in want:
            continue
        key = str(field)
        if key in out:
            out[key] = (out[key] if isinstance(out[key], list) else [out[key]]) + [value]
        else:
            out[key] = value
    return out


def _text(value):
    if isinstance(value, (bytes, bytearray)):
        return value.decode('utf-8', errors='replace').rstrip('\x00')
    return '' if value is None else value


def _repeated(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _ms(value):
    try:
        return _EPOCH + timedelta(milliseconds=int(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _by_time(row):
    """Sort key that keeps a row whose timestamp could not be read at the end.

    _ms returns '' on an unreadable value, and '' cannot be compared with a datetime."""
    return (row[0] != '', row[0] if row[0] != '' else _EPOCH)


def _flag(value):
    """A proto3 bool: the encoder leaves false off the wire, so an absent field is False."""
    return bool(value)


def _user_id(record):
    """The Android user from the Int32Value wrapper, or '' when the wrapper is absent.

    proto3 leaves a zero scalar off the wire, so the wrapper for user 0 is an empty message.
    Reading the inner field without checking for the wrapper would blank the column on every
    row belonging to the first user."""
    if '2' not in record:
        return ''
    return _wire_fields(record['2'], _INT32_VALUE_FIELDS).get('1', 0)


def _stores(context):
    """(path, parsed top-level message) for each dex-use store, skips logged."""
    out = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        try:
            with open(file_found, 'rb') as handle:
                data = handle.read()
        except OSError as error:
            logfunc(f'Could not read {file_found}: {error}')
            continue
        if not data:
            logfunc(f'Dex usage store is empty: {file_found}')
            continue
        try:
            out.append((file_found, _wire_fields(data, _TOP_FIELDS)))
        except (IndexError, ValueError) as error:
            logfunc(f'Could not read the dex usage store {file_found}: {error}')
    return out


def _primary_rows(context):
    """(own-package rows, cross-package rows, source paths) from every primary dex record."""
    own, cross, sources = [], [], []
    for path, top in _stores(context):
        sources.append(path)
        relative = context.get_relative_path(path)
        for package_raw in _repeated(top.get('1')):
            package = _wire_fields(package_raw, _PACKAGE_FIELDS)
            owner = _text(package.get('1'))
            for primary_raw in _repeated(package.get('2')):
                primary = _wire_fields(primary_raw, _PRIMARY_FIELDS)
                dex_file = _text(primary.get('1'))
                for record_raw in _repeated(primary.get('2')):
                    record = _wire_fields(record_raw, _PRIMARY_RECORD_FIELDS)
                    loader = _text(record.get('1'))
                    isolated = _flag(record.get('2'))
                    stamp = _ms(record.get('3'))
                    if loader == owner:
                        own.append((stamp, owner, dex_file, isolated, relative))
                    else:
                        cross.append((stamp, loader, owner, dex_file, isolated, relative))
    return own, cross, sources


@artifact_processor
def package_dex_usage_app_code(context):
    data_headers = (
        ('Last Loaded', 'datetime'),
        'Package',
        'Dex File',
        'Isolated Process',
        'Source File',
    )
    own, _cross, sources = _primary_rows(context)
    own.sort(key=_by_time, reverse=True)
    return data_headers, own, '\n'.join(sources)


@artifact_processor
def package_dex_usage_cross_package(context):
    data_headers = (
        ('Last Loaded', 'datetime'),
        'Loading Package',
        'Owning Package',
        'Dex File',
        'Isolated Process',
        'Source File',
    )
    _own, cross, sources = _primary_rows(context)
    cross.sort(key=_by_time, reverse=True)
    return data_headers, cross, '\n'.join(sources)


@artifact_processor
def package_dex_usage_secondary(context):
    data_headers = (
        ('Last Loaded', 'datetime'),
        'Loading Package',
        'Owning Package',
        'Android User',
        'Dex File',
        'ABI',
        'Class Loader Context',
        'Isolated Process',
        'Source File',
    )
    data_list = []
    sources = []
    for path, top in _stores(context):
        sources.append(path)
        relative = context.get_relative_path(path)
        for package_raw in _repeated(top.get('1')):
            package = _wire_fields(package_raw, _PACKAGE_FIELDS)
            owner = _text(package.get('1'))
            for secondary_raw in _repeated(package.get('3')):
                secondary = _wire_fields(secondary_raw, _SECONDARY_FIELDS)
                dex_file = _text(secondary.get('1'))
                user = _user_id(secondary)
                for record_raw in _repeated(secondary.get('3')):
                    record = _wire_fields(record_raw, _SECONDARY_RECORD_FIELDS)
                    data_list.append((
                        _ms(record.get('5')),
                        _text(record.get('1')),
                        owner,
                        user,
                        dex_file,
                        _text(record.get('4')),
                        _text(record.get('3')),
                        _flag(record.get('2')),
                        relative,
                    ))
    data_list.sort(key=_by_time, reverse=True)
    return data_headers, data_list, '\n'.join(sources)
