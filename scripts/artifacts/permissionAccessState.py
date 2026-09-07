__artifacts_v2__ = {
    "permission_app_op_modes": {
        "name": "App Op Modes (Permission Store)",
        "description": "App op modes the permission subsystem stored in access.abx, with the op, the mode, and "
                       "the app id or package name the mode is stored against.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-07",
        "requirements": "none",
        "category": "Permissions",
        "notes": "A row is an app-op element in the permission subsystem's access.abx carrying a stored mode, with "
                 "the app id or the package name that mode is stored against. Two sections are read: "
                 "app-id-app-ops, whose app-id elements key on an app id, and package-app-ops, whose package "
                 "elements key on a package name. Mode Stored Against says which of the two the file recorded, and "
                 "with it how Package Name was obtained: 3,625 rows are stored against an app id and 2,182 against "
                 "a package name. Reference: AppIdAppOpPersistence and PackageAppOpPersistence, "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/services/permission/java/com/android/server/permission/access/appop/AppIdAppOpPersistence.kt#84 "
                 "and "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/services/permission/java/com/android/server/permission/access/appop/PackageAppOpPersistence.kt#80, "
                 "and the shared app-op element they both write, "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/services/permission/java/com/android/server/permission/access/appop/BaseAppOpPersistence.kt#58.\n"
                 "Android 14 and earlier keep these modes in system/appops.xml, which App Ops Permission Modes "
                 "reads, and this store is where they go instead. The boundary is a release boundary in one "
                 "direction only. It is not the case that system/appops.xml disappears at that release: of the 22 "
                 "tested images at Android 15 or later, 1 still carries it, a Samsung. Of the 40 registered "
                 "corpora, 16 carry system/appops.xml, 1 carries both files and 3 carry neither, those last being "
                 "partial extractions with no system files. Measured against the registry as it stood on "
                 "2026-09-07, across all 40 registered Android corpora, 22 carry access.abx, and those are the "
                 "same 22 the runs produced rows on. That boundary is in AOSP and not only in the corpus: the "
                 "subsystem that writes this file is selected on PermissionManager.USE_ACCESS_CHECKING_SERVICE, "
                 "which is SdkLevel.isAtLeastV(), so it turns on at Android 15, "
                 "https://android.googlesource.com/platform/frameworks/base/+/cf2b56d40d55c605a90c724f9e886ace0f2b365f/core/java/android/permission/PermissionManager.java#196. "
                 "The writer class is a release older than that and reading its presence in the tree as the "
                 "release the file appears would be wrong: it is in the tree at android-14.0.0_r1 and absent at "
                 "android-13.0.0_r1, and at 14 the previous implementation is constructed unconditionally and the "
                 "only reference to the new one is commented out, so the writer ships and never runs, "
                 "https://android.googlesource.com/platform/frameworks/base/+/bd9ef6de90a1b726729d939f48dd8e7dbbe27218/services/core/java/com/android/server/pm/permission/PermissionManagerService.java#156. "
                 "That matches the corpus: every one of the 22 images carrying the file reports Android 15 or "
                 "later, and none below it does. The store is written once for the system, with no Android user, "
                 "and once per Android user, AccessPersistence.writeSystemState and writeUserState, both named "
                 "access.abx, "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/services/permission/java/com/android/server/permission/access/AccessPersistence.kt#156 "
                 "and #160, in the directories PermissionApex names for the com.android.permission module, #173 "
                 "and #175. On the tested images those are misc/apexdata/com.android.permission for the system and "
                 "misc_de/<user>/apexdata/com.android.permission for each user.\n"
                 "The platform stores a mode only when it differs from that op's default mode, and removes the "
                 "entry when the mode is set back to the default. A row therefore records an op whose mode "
                 "differed from the platform default when the file was last written, and the absence of a row is "
                 "the op's default mode being in effect rather than evidence that an op was denied or never set. "
                 "Nothing in the file records what set a mode, or when. Reference: setAppOpMode in both policies, "
                 "which resolves AppOpsManager.opToDefaultMode and calls putWithDefault, "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/services/permission/java/com/android/server/permission/access/appop/AppIdAppOpPolicy.kt#82 "
                 "and "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/services/permission/java/com/android/server/permission/access/appop/PackageAppOpPolicy.kt#85, "
                 "and putWithDefault itself, which removes the entry when the new value equals the default, "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/services/permission/java/com/android/server/permission/access/immutable/IndexedMapExtensions.kt#104. "
                 "Checked against the data rather than taken on the source's word: of the 5,597 stored modes "
                 "across the tested images whose op AOSP's own table defines a default for, 5,597 differed from "
                 "that default and none matched it.\n"
                 "Mode is the AppOpsManager mode constant, and a value outside that set is reported as stored. "
                 "Across the tested images the stored modes were IGNORED on 2,974 rows, DEFAULT on 1,518 rows, "
                 "ALLOWED on 960 rows, FOREGROUND on 304 rows, ERRORED on 2 rows. The value 5 on 49 rows is "
                 "reported as stored: AOSP defines modes 0 to 4 and no more. Every row carrying it is on the same "
                 "image and pairs with an op string in a vendor namespace rather than the android one. Reference: "
                 "MODE_ALLOWED, MODE_IGNORED, MODE_ERRORED, MODE_DEFAULT and MODE_FOREGROUND, "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/core/java/android/app/AppOpsManager.java#412.\n"
                 "App Op is the op string as stored. Op Code is the AppOpsManager op code for it, so a row here "
                 "can be matched to a row in App Ops Permission Modes or App Ops Recent Accesses, which both "
                 "report the code rather than the string. It is taken from the ordered sAppOpInfos table, where "
                 "the array index is the op code and the second Builder argument is the op string; the extraction "
                 "asserted that the number of entries equalled the number of Builder occurrences in the array, "
                 "because a pattern that skips one entry shifts every later code, and index 96 is a retired "
                 "placeholder carrying an empty op string, so 155 of the 156 entries are mapped. Reference: "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/core/java/android/app/AppOpsManager.java#2685. "
                 "The op string is usually the short name that table gives, lowercased and prefixed, but four ops "
                 "break that, so the string cannot be turned into those artifacts' name by rule: "
                 "android:monitor_location_high_power is MONITOR_HIGH_POWER_LOCATION, "
                 "android:receive_ambient_trigger_audio is RECEIVE_SOUNDTRIGGER_AUDIO, "
                 "android:reserved_for_testing is OP_RESERVED_FOR_TESTING and android:unarchival_support is "
                 "UNARCHIVAL_CONFIRMATION, which is on 37 rows here. Op Code is blank for 210 rows carrying 12 op "
                 "strings that table does not define: MIUI:10008 on 61, MIUI:10017 on 55, MIUI:10020 on 26, "
                 "MIUI:10021 on 24, MIUI:10001 on 15, android:read_restricted_messages on 8, "
                 "android:system_application_overlay on 6, MIUI:10023 on 6, MIUI:10019 on 6, "
                 "android:write_restricted_messages on 1, android:read_screen_context on 1, MIUI:10007 on 1. They "
                 "appear on 3 of the 22 images with rows, and no source for them was found, so they are reported "
                 "as stored.\n"
                 "Android User is read from the path, because the file does not store it: AOSP writes one file per "
                 "user into that user's own directory. A row from the system file would carry no user, and none "
                 "does, because the system file holds none of the sections read here. Across the tested images the "
                 "value was 0 on 4,161 rows, 10 on 1,646 rows.\n"
                 "Package Name is resolved from system/packages.xml, not stored in this file. That lookup uses "
                 "identity the file records: the userId attribute of a package element, or the name of the "
                 "shared-user element when several packages share the app id, in which case the name is a shared "
                 "user id such as android.uid.system rather than a package. A uid is reduced to an app id first, "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/core/java/android/os/UserHandle.java#47. "
                 "Package Name is blank on 0 of 5,807 rows.\n"
                 "The path pattern is tolerant, so every copy of the file in an extraction is read. A row is keyed "
                 "on its content, so a copy that repeats a record costs no extra row and Source File names both "
                 "paths, while two copies that disagree produce a row each. On the 22 images carrying the store, "
                 "every Android 15 emulator carries a data_mirror copy of each user file, and all 36 of those 36 "
                 "pairs were byte-identical to the file they mirror. The reserve copy AtomicFile writes beside "
                 "each file, access.abx.reservecopy, "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/services/permission/java/com/android/server/permission/access/AccessPersistence.kt#167, "
                 "is not read, and neither is the copy under apexrollback that one image carries: both are "
                 "snapshots from another point in time and reading them would mix two states into one table with "
                 "no column saying which. The pattern also matches the system copy of the store, the one AOSP "
                 "writes with no Android user, which is present on 22 of those 22 images. It is read and named in "
                 "Source File and produces no row for either artifact, because it carries the permission "
                 "declarations and none of the per-user sections. Narrowing the pattern to the per-user directory "
                 "would drop those citations, and would also drop the file if a later release moved one of these "
                 "sections into it, so it is left broad deliberately. 3,890 of 5,807 rows cite more than one path.\n"
                 "What this artifact does not cover. It reads two of the sections in this file. app-id-permissions "
                 "is read by Permission Grants, the sibling artifact in this module. package-versions is not "
                 "reported: it is the permission state version the subsystem last wrote for each package, and it "
                 "held one value per file on every one of the 76 user files read, so it says nothing about an "
                 "individual package. default-permission-grant is not reported: it is a single build fingerprint "
                 "per file, recording the build at which the platform last applied its default grants, so it "
                 "identifies a build rather than anything an app or a person did. The system file's permissions "
                 "and permission-trees sections are not reported either: they are the permission declarations the "
                 "platform and the installed apps make in their manifests, 1,431 to 3,060 per image from 357 "
                 "declaring packages on the image with the most, which exist whether or not anyone used anything. "
                 "app-id-device-permissions was present and empty on all 76 user files read, and "
                 "app-id-app-function-accesses was present and empty on the 2 files that carry it, both on a "
                 "Pixel, so neither is parsed and both are checked absences rather than omissions. This artifact "
                 "also does not read system/appops_accesses.xml, which appOpsAccesses reads, nor "
                 "system/appops/discrete, which discreteNative reads.\n"
                 "Whether the two mode stores agree was settled on anne_a15, the one registered corpus carrying "
                 "both. Matching the two on the app id and the op, and translating appops.xml's numeric op code to "
                 "this file's op string: 951 pairs hold the same mode and 0 disagree, with 14 entries only in "
                 "appops.xml and 6 only here. At package scope for Android user 0, 23 agree, 0 disagree, 2 are "
                 "only in appops.xml and 0 only here. All 14 of the appops.xml-only entries belong to a single app "
                 "id that that extraction's own packages.xml does not name, which is the condition AOSP drops an "
                 "app id on: the parser removes an app id at or above FIRST_APPLICATION_UID that the package state "
                 "does not know and asks for a rewrite, "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/services/permission/java/com/android/server/permission/access/appop/AppIdAppOpPersistence.kt#52. "
                 "AOSP also carries a helper described as the provider of legacy app-ops data for the new "
                 "permission subsystem, which reads appops.xml and hands its contents on, "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/services/core/java/com/android/server/appop/AppOpMigrationHelperImpl.java#35. "
                 "That is one image, so it bounds the comparison rather than settling it for every device.\n"
                 "The file is written on a short delay rather than at acquisition: AOSP schedules the write 1 "
                 "second after a change and at most 2 seconds after the first pending one, "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/services/permission/java/com/android/server/permission/access/AccessPersistence.kt#183. "
                 "That is much tighter than the delay on system/appops_accesses.xml, whose writer uses "
                 "WRITE_DELAY, 30 minutes outside a debug build, "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/services/core/java/com/android/server/appop/AppOpsService.java#242. "
                 "So the contents are close to the state at acquisition, but they are still the last write and not "
                 "a live view.",
        "paths": ('*/apexdata/com.android.permission/access.abx', '*/system/packages.xml'),
        "output_types": "standard",
        "artifact_icon": "shield",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 0 rows",
            "anne_a15": "Android 15 | 980 rows",
            "cookbook_a11": "Android 11 | 0 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss2_v1": "Android 15 | 97 rows",
            "emu_a15_oss_v1": "Android 15 | 134 rows",
            "emu_a15_oss_v10": "Android 15 | 224 rows",
            "emu_a15_oss_v11": "Android 15 | 225 rows",
            "emu_a15_oss_v12": "Android 15 | 232 rows",
            "emu_a15_oss_v13": "Android 15 | 236 rows",
            "emu_a15_oss_v14": "Android 15 | 236 rows",
            "emu_a15_oss_v15": "Android 15 | 247 rows",
            "emu_a15_oss_v16": "Android 15 | 261 rows",
            "emu_a15_oss_v17": "Android 15 | 275 rows",
            "emu_a15_oss_v2": "Android 15 | 159 rows",
            "emu_a15_oss_v3": "Android 15 | 161 rows",
            "emu_a15_oss_v4": "Android 15 | 180 rows",
            "emu_a15_oss_v5": "Android 15 | 224 rows",
            "emu_a15_oss_v6": "Android 15 | 238 rows",
            "emu_a15_oss_v7": "Android 15 | 253 rows",
            "emu_a15_oss_v8": "Android 15 | 253 rows",
            "emu_a15_oss_v9": "Android 15 | 255 rows",
            "falken_a326u_a13": "Android 13 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 103 rows",
            "hc_pixel8pro_a17": "Android 17 | 117 rows",
            "hc_pixel8pro_a17_ail": "0 rows",
            "kevin_pocox7_a15": "Android 15 | 717 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 0 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "russell_a14": "Android 14 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 0 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
    },
    "permission_grants": {
        "name": "Permission Grants (Permission Store)",
        "description": "Permission state the permission subsystem stored in access.abx, one row per permission "
                       "held against an app id, with the grant state and the flags it was derived from.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-07",
        "requirements": "none",
        "category": "Permissions",
        "notes": "A row is a permission element in the app-id-permissions section of the permission subsystem's "
                 "access.abx, one per permission the subsystem holds state for against an app id. There were "
                 "194,284 rows across the tested images, carrying 4,514 distinct permission names. Reference: "
                 "AppIdPermissionPersistence, "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/services/permission/java/com/android/server/permission/access/permission/AppIdPermissionPersistence.kt#219.\n"
                 "Android 14 and earlier keep this state in "
                 "misc_de/<user>/apexdata/com.android.permission/runtime-permissions.xml, which runtimePerms "
                 "reads. That file is still present beside access.abx on every image carrying this store, so its "
                 "presence is not evidence that it still holds anything: on 21 of those 22 images it is a stub of "
                 "948 to 1,160 bytes carrying no permission element at all. On the remaining one, a Samsung "
                 "Android 15 image, it carries 12,258 of them beside this file's 14,683, and the two are written "
                 "within a minute of each other, so neither is a leftover. Matching them on the app id and the "
                 "permission name, they give the same grant state on 11,912 rows and a different one on 185, with "
                 "161 rows only in the older file. The cause of those differences was not established, so the two "
                 "stores should not be treated as interchangeable on a device that writes both. Measured against "
                 "the registry as it stood on 2026-09-07, across all 40 registered Android corpora, 22 carry "
                 "access.abx, and those are the same 22 the runs produced rows on. That boundary is in AOSP and "
                 "not only in the corpus: the subsystem that writes this file is selected on "
                 "PermissionManager.USE_ACCESS_CHECKING_SERVICE, which is SdkLevel.isAtLeastV(), so it turns on at "
                 "Android 15, "
                 "https://android.googlesource.com/platform/frameworks/base/+/cf2b56d40d55c605a90c724f9e886ace0f2b365f/core/java/android/permission/PermissionManager.java#196. "
                 "The writer class is a release older than that and reading its presence in the tree as the "
                 "release the file appears would be wrong: it is in the tree at android-14.0.0_r1 and absent at "
                 "android-13.0.0_r1, and at 14 the previous implementation is constructed unconditionally and the "
                 "only reference to the new one is commented out, so the writer ships and never runs, "
                 "https://android.googlesource.com/platform/frameworks/base/+/bd9ef6de90a1b726729d939f48dd8e7dbbe27218/services/core/java/com/android/server/pm/permission/PermissionManagerService.java#156. "
                 "That matches the corpus: every one of the 22 images carrying the file reports Android 15 or "
                 "later, and none below it does. The store is written once for the system, with no Android user, "
                 "and once per Android user, AccessPersistence.writeSystemState and writeUserState, both named "
                 "access.abx, "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/services/permission/java/com/android/server/permission/access/AccessPersistence.kt#156 "
                 "and #160, in the directories PermissionApex names for the com.android.permission module, #173 "
                 "and #175. On the tested images those are misc/apexdata/com.android.permission for the system and "
                 "misc_de/<user>/apexdata/com.android.permission for each user.\n"
                 "Permission Flags is the stored flags value decoded into the permission subsystem's own "
                 "PermissionFlags names, in bit order. A bit the table does not define is rendered as hex so it "
                 "stays visible, which 0 of the 194,284 tested rows needed. Reference: "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/services/permission/java/com/android/server/permission/access/permission/PermissionFlags.kt#56 "
                 "onwards for the constants and #503 for the names. Across the tested images the flags set were "
                 "PROTECTION_GRANTED on 79,811 rows, INSTALL_GRANTED on 63,543 rows, USER_SENSITIVE_WHEN_GRANTED "
                 "on 24,028 rows, RUNTIME_GRANTED on 19,533 rows, USER_SENSITIVE_WHEN_REVOKED on 19,061 rows, "
                 "INSTALL_REVOKED on 15,054 rows, PREGRANT on 12,553 rows, UPGRADE_EXEMPT on 9,115 rows, "
                 "SYSTEM_FIXED on 7,143 rows, ROLE on 4,750 rows, SYSTEM_EXEMPT on 4,661 rows, INSTALLER_EXEMPT on "
                 "2,503 rows, IMPLICIT on 1,298 rows, USER_SET on 1,054 rows, IMPLICIT_GRANTED on 85 rows, "
                 "USER_SELECTED on 69 rows, ONE_TIME on 27 rows, HIBERNATION on 6 rows, USER_FIXED on 3 rows.\n"
                 "Granted is AOSP's own determination from those flags, a port of "
                 "PermissionFlags.isPermissionGranted, "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/services/permission/java/com/android/server/permission/access/permission/PermissionFlags.kt#330. "
                 "It was Yes on 161,798 rows and No on 32,486. AOSP carries a second, stricter function, "
                 "isAppOpGranted, which additionally treats a restricted or app-op-revoked permission as not "
                 "granted; the two were computed side by side over every row here and gave the same answer on all "
                 "of them, so only one column is reported.\n"
                 "Not every row records a choice made on the device. AOSP documents INSTALL_GRANTED, "
                 "INSTALL_REVOKED and PROTECTION_GRANTED as the state the platform derives from an app's manifest "
                 "and from the permission's protection level, and a row carrying only those flags is 157,327 of "
                 "194,284 rows here. The flags AOSP documents as recording a choice are the runtime ones, and the "
                 "narrowest of them are USER_SET on 1,054 rows, USER_FIXED on 3, ONE_TIME on 27 and USER_SELECTED "
                 "on 69. Whether a given row followed from something a person did is not established by this file. "
                 "The whole table is reported rather than the runtime subset, so an absent row means the subsystem "
                 "held no state for that app id and permission rather than this artifact having filtered it, and "
                 "the flag names are in one column so the narrower sets can be found by sorting on it.\n"
                 "Android User is read from the path, because the file does not store it: AOSP writes one file per "
                 "user into that user's own directory. A row from the system file would carry no user, and none "
                 "does, because the system file holds none of the sections read here. Across the tested images the "
                 "value was 0 on 117,199 rows, 10 on 77,085 rows.\n"
                 "Package Name is resolved from system/packages.xml, not stored in this file. That lookup uses "
                 "identity the file records: the userId attribute of a package element, or the name of the "
                 "shared-user element when several packages share the app id, in which case the name is a shared "
                 "user id such as android.uid.system rather than a package. A uid is reduced to an app id first, "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/core/java/android/os/UserHandle.java#47. "
                 "Package Name is blank on 0 of 194,284 rows.\n"
                 "The path pattern is tolerant, so every copy of the file in an extraction is read. A row is keyed "
                 "on its content, so a copy that repeats a record costs no extra row and Source File names both "
                 "paths, while two copies that disagree produce a row each. On the 22 images carrying the store, "
                 "every Android 15 emulator carries a data_mirror copy of each user file, and all 36 of those 36 "
                 "pairs were byte-identical to the file they mirror. The reserve copy AtomicFile writes beside "
                 "each file, access.abx.reservecopy, "
                 "https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/services/permission/java/com/android/server/permission/access/AccessPersistence.kt#167, "
                 "is not read, and neither is the copy under apexrollback that one image carries: both are "
                 "snapshots from another point in time and reading them would mix two states into one table with "
                 "no column saying which. The pattern also matches the system copy of the store, the one AOSP "
                 "writes with no Android user, which is present on 22 of those 22 images. It is read and named in "
                 "Source File and produces no row for either artifact, because it carries the permission "
                 "declarations and none of the per-user sections. Narrowing the pattern to the per-user directory "
                 "would drop those citations, and would also drop the file if a later release moved one of these "
                 "sections into it, so it is left broad deliberately. 155,426 of 194,284 rows cite more than one "
                 "path.\n"
                 "What this artifact does not cover. It reads one section of this file; the app op modes in "
                 "app-id-app-ops and package-app-ops are read by App Op Modes, the sibling artifact in this "
                 "module, and that artifact's notes say which of the remaining sections were excluded and why. "
                 "This artifact holds no time: nothing in the section records when a permission was granted or "
                 "revoked, so a row says what the state was when the file was last written and nothing about when "
                 "it got there. The device-scoped section app-id-device-permissions, which would hold permissions "
                 "granted for a virtual device, was present and empty on all 76 user files read.",
        "paths": ('*/apexdata/com.android.permission/access.abx', '*/system/packages.xml'),
        "output_types": "standard",
        "artifact_icon": "shield",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 0 rows",
            "anne_a15": "Android 15 | 14,683 rows",
            "cookbook_a11": "Android 11 | 0 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss2_v1": "Android 15 | 7,006 rows",
            "emu_a15_oss_v1": "Android 15 | 7,354 rows",
            "emu_a15_oss_v10": "Android 15 | 8,771 rows",
            "emu_a15_oss_v11": "Android 15 | 8,802 rows",
            "emu_a15_oss_v12": "Android 15 | 9,008 rows",
            "emu_a15_oss_v13": "Android 15 | 9,091 rows",
            "emu_a15_oss_v14": "Android 15 | 9,091 rows",
            "emu_a15_oss_v15": "Android 15 | 9,416 rows",
            "emu_a15_oss_v16": "Android 15 | 9,602 rows",
            "emu_a15_oss_v17": "Android 15 | 9,957 rows",
            "emu_a15_oss_v2": "Android 15 | 7,613 rows",
            "emu_a15_oss_v3": "Android 15 | 7,655 rows",
            "emu_a15_oss_v4": "Android 15 | 7,919 rows",
            "emu_a15_oss_v5": "Android 15 | 8,637 rows",
            "emu_a15_oss_v6": "Android 15 | 8,793 rows",
            "emu_a15_oss_v7": "Android 15 | 8,893 rows",
            "emu_a15_oss_v8": "Android 15 | 8,893 rows",
            "emu_a15_oss_v9": "Android 15 | 8,925 rows",
            "falken_a326u_a13": "Android 13 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 7,475 rows",
            "hc_pixel8pro_a17": "Android 17 | 7,832 rows",
            "hc_pixel8pro_a17_ail": "0 rows",
            "kevin_pocox7_a15": "Android 15 | 8,868 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 0 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "russell_a14": "Android 14 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 0 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
    },
}

import os
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import abxread, artifact_processor, checkabx, logfunc

# The AppOpsManager mode constants are shared with appOpsAccesses, which reads the other App Ops
# store, so the two artifacts cannot drift apart on the same vocabulary.
from scripts.artifacts.appOpsAccesses import OP_MODES

# UserHandle.PER_USER_RANGE. getAppId is uid % PER_USER_RANGE.
PER_USER_RANGE = 100000

# The op string this store writes, to the op code the other two App Ops artifacts report, so a row
# here can be matched to a row there. Extracted from the ordered AppOpsManager.sAppOpInfos array at
# main 1cdfff555f4a21f71ccc978290e2e212e2f8b168, where the array index is the op code and the second
# Builder argument is the op string. The extraction asserted that the number of entries equalled the
# number of 'new AppOpInfo.Builder(' occurrences in the array, because a pattern that skips one entry
# shifts every later code. Index 96 is a retired placeholder carrying an empty op string and is left
# out, so the table has 155 of the 156 entries.
APP_OP_CODES = {
    "android:coarse_location": 0, "android:fine_location": 1,
    "android:gps": 2, "android:vibrate": 3,
    "android:read_contacts": 4, "android:write_contacts": 5,
    "android:read_call_log": 6, "android:write_call_log": 7,
    "android:read_calendar": 8, "android:write_calendar": 9,
    "android:wifi_scan": 10, "android:post_notification": 11,
    "android:neighboring_cells": 12, "android:call_phone": 13,
    "android:read_sms": 14, "android:write_sms": 15,
    "android:receive_sms": 16, "android:receive_emergency_broadcast": 17,
    "android:receive_mms": 18, "android:receive_wap_push": 19,
    "android:send_sms": 20, "android:read_icc_sms": 21,
    "android:write_icc_sms": 22, "android:write_settings": 23,
    "android:system_alert_window": 24, "android:access_notifications": 25,
    "android:camera": 26, "android:record_audio": 27,
    "android:play_audio": 28, "android:read_clipboard": 29,
    "android:write_clipboard": 30, "android:take_media_buttons": 31,
    "android:take_audio_focus": 32, "android:audio_master_volume": 33,
    "android:audio_voice_volume": 34, "android:audio_ring_volume": 35,
    "android:audio_media_volume": 36, "android:audio_alarm_volume": 37,
    "android:audio_notification_volume": 38, "android:audio_bluetooth_volume": 39,
    "android:wake_lock": 40, "android:monitor_location": 41,
    "android:monitor_location_high_power": 42, "android:get_usage_stats": 43,
    "android:mute_microphone": 44, "android:toast_window": 45,
    "android:project_media": 46, "android:activate_vpn": 47,
    "android:write_wallpaper": 48, "android:assist_structure": 49,
    "android:assist_screenshot": 50, "android:read_phone_state": 51,
    "android:add_voicemail": 52, "android:use_sip": 53,
    "android:process_outgoing_calls": 54, "android:use_fingerprint": 55,
    "android:body_sensors": 56, "android:read_cell_broadcasts": 57,
    "android:mock_location": 58, "android:read_external_storage": 59,
    "android:write_external_storage": 60, "android:turn_screen_on": 61,
    "android:get_accounts": 62, "android:run_in_background": 63,
    "android:audio_accessibility_volume": 64, "android:read_phone_numbers": 65,
    "android:request_install_packages": 66, "android:picture_in_picture": 67,
    "android:instant_app_start_foreground": 68, "android:answer_phone_calls": 69,
    "android:run_any_in_background": 70, "android:change_wifi_state": 71,
    "android:request_delete_packages": 72, "android:bind_accessibility_service": 73,
    "android:accept_handover": 74, "android:manage_ipsec_tunnels": 75,
    "android:start_foreground": 76, "android:bluetooth_scan": 77,
    "android:use_biometric": 78, "android:activity_recognition": 79,
    "android:sms_financial_transactions": 80, "android:read_media_audio": 81,
    "android:write_media_audio": 82, "android:read_media_video": 83,
    "android:write_media_video": 84, "android:read_media_images": 85,
    "android:write_media_images": 86, "android:legacy_storage": 87,
    "android:access_accessibility": 88, "android:read_device_identifiers": 89,
    "android:access_media_location": 90, "android:query_all_packages": 91,
    "android:manage_external_storage": 92, "android:interact_across_profiles": 93,
    "android:activate_platform_vpn": 94, "android:loader_usage_stats": 95,
    "android:auto_revoke_permissions_if_unused": 97, "android:auto_revoke_managed_by_installer": 98,
    "android:no_isolated_storage": 99, "android:phone_call_microphone": 100,
    "android:phone_call_camera": 101, "android:record_audio_hotword": 102,
    "android:manage_ongoing_calls": 103, "android:manage_credentials": 104,
    "android:use_icc_auth_with_device_identifier": 105, "android:record_audio_output": 106,
    "android:schedule_exact_alarm": 107, "android:fine_location_source": 108,
    "android:coarse_location_source": 109, "android:manage_media": 110,
    "android:bluetooth_connect": 111, "android:uwb_ranging": 112,
    "android:activity_recognition_source": 113, "android:bluetooth_advertise": 114,
    "android:record_incoming_phone_audio": 115, "android:nearby_wifi_devices": 116,
    "android:establish_vpn_service": 117, "android:establish_vpn_manager": 118,
    "android:access_restricted_settings": 119, "android:receive_ambient_trigger_audio": 120,
    "android:receive_explicit_user_interaction_audio": 121, "android:run_user_initiated_jobs": 122,
    "android:read_media_visual_user_selected": 123, "android:system_exempt_from_suspension": 124,
    "android:system_exempt_from_dismissible_notifications": 125, "android:read_write_health_data": 126,
    "android:foreground_service_special_use": 127, "android:system_exempt_from_power_restrictions": 128,
    "android:system_exempt_from_hibernation": 129, "android:system_exempt_from_activity_bg_start_restriction": 130,
    "android:capture_consentless_bugreport_on_userdebug_build": 131, "android:deprecated_2": 132,
    "android:use_full_screen_intent": 133, "android:camera_sandboxed": 134,
    "android:record_audio_sandboxed": 135, "android:receive_sandbox_trigger_audio": 136,
    "android:deprecated_3": 137, "android:create_accessibility_overlay": 138,
    "android:media_routing_control": 139, "android:enable_mobile_data_by_user": 140,
    "android:reserved_for_testing": 141, "android:rapid_clear_notifications_by_listener": 142,
    "android:read_system_grammatical_gender": 143, "android:deprecated_4": 144,
    "android:archive_icon_overlay": 145, "android:unarchival_support": 146,
    "android:emergency_location": 147, "android:receive_sensitive_notifications": 148,
    "android:read_heart_rate": 149, "android:read_skin_temperature": 150,
    "android:ranging": 151, "android:read_oxygen_saturation": 152,
    "android:write_system_preferences": 153, "android:control_audio": 154,
    "android:control_audio_partial": 155,}

# PermissionFlags, the permission subsystem's own flag set, at the same commit,
# services/permission/java/com/android/server/permission/access/permission/PermissionFlags.kt.
# Ordered by bit so a decoded value reads in the order AOSP's own flagsToString prints it.
PERMISSION_FLAGS = (
    (1 << 0, 'INSTALL_GRANTED'),
    (1 << 1, 'INSTALL_REVOKED'),
    (1 << 2, 'PROTECTION_GRANTED'),
    (1 << 3, 'ROLE'),
    (1 << 4, 'RUNTIME_GRANTED'),
    (1 << 5, 'USER_SET'),
    (1 << 6, 'USER_FIXED'),
    (1 << 7, 'POLICY_FIXED'),
    (1 << 8, 'SYSTEM_FIXED'),
    (1 << 9, 'PREGRANT'),
    (1 << 10, 'LEGACY_GRANTED'),
    (1 << 11, 'IMPLICIT_GRANTED'),
    (1 << 12, 'IMPLICIT'),
    (1 << 13, 'USER_SENSITIVE_WHEN_GRANTED'),
    (1 << 14, 'USER_SENSITIVE_WHEN_REVOKED'),
    (1 << 15, 'INSTALLER_EXEMPT'),
    (1 << 16, 'SYSTEM_EXEMPT'),
    (1 << 17, 'UPGRADE_EXEMPT'),
    (1 << 18, 'RESTRICTION_REVOKED'),
    (1 << 19, 'SOFT_RESTRICTED'),
    (1 << 20, 'APP_OP_REVOKED'),
    (1 << 21, 'ONE_TIME'),
    (1 << 22, 'HIBERNATION'),
    (1 << 23, 'USER_SELECTED'),
)

INSTALL_GRANTED = 1 << 0
INSTALL_REVOKED = 1 << 1
PROTECTION_GRANTED = 1 << 2
RUNTIME_GRANTED = 1 << 4
LEGACY_GRANTED = 1 << 10
IMPLICIT_GRANTED = 1 << 11
RESTRICTION_REVOKED = 1 << 18


def _root(path):
    """The XML root, reading ABX binary XML or plain XML."""
    if checkabx(path):
        try:
            return abxread(path, False).getroot()
        except Exception:  # pylint: disable=broad-except
            return abxread(path, True).getroot()
    return ET.parse(path).getroot()


def _android_user(path):
    """The Android user from the path segment before apexdata, or '' when there is none.

    The store is written once per Android user under misc_de/<user>/apexdata, and once for the
    system with no user under misc/apexdata. The user is not stored inside the file, so the path
    is the only place it is recorded.
    """
    parts = path.replace('\\', '/').split('/')
    try:
        index = parts.index('apexdata')
    except ValueError:
        return ''
    if index == 0:
        return ''
    segment = parts[index - 1]
    return segment if segment.isdigit() else ''


def _app_id(value):
    """The app id from a stored uid or app id, or None when it is not an integer."""
    try:
        return int(value) % PER_USER_RANGE
    except (TypeError, ValueError):
        return None


def _package_names(files):
    """(app id to the name recorded for it in packages.xml, the files that were read).

    A package element carries its own userId; a set of packages sharing a uid carries
    sharedUserId instead, and the uid is named once by a shared-user element whose name is the
    shared user id rather than a package. Both are identity the file records, not a correlation.
    """
    private = {}
    shared = {}
    read = []
    for file_found in files:
        try:
            root = _root(file_found)
        except Exception as error:  # pylint: disable=broad-except
            logfunc(f'Permission store: could not read {os.path.basename(file_found)}: {error}')
            continue
        read.append(file_found)
        for element in root.iter('shared-user'):
            app_id = _app_id(element.get('userId'))
            name = element.get('name')
            if app_id is not None and name:
                shared.setdefault(app_id, name)
        for element in root.iter('package'):
            app_id = _app_id(element.get('userId'))
            name = element.get('name')
            if app_id is not None and name:
                private.setdefault(app_id, set()).add(name)
    names = dict(shared)
    for app_id, name_set in private.items():
        if app_id not in names:
            names[app_id] = ' | '.join(sorted(name_set))
    return names, read


def _split_files(context):
    """(the access.abx files, the packages.xml files) from what the seeker staged."""
    access_files = []
    packages_files = []
    for file_found in sorted({str(f) for f in context.get_files_found()}):
        if os.path.isdir(file_found):
            continue
        base = os.path.basename(file_found)
        if base == 'access.abx':
            access_files.append(file_found)
        elif base == 'packages.xml':
            packages_files.append(file_found)
    return access_files, packages_files


def _op_code(op_string):
    """The AppOpsManager op code for an op string, or '' when the table does not define it."""
    code = APP_OP_CODES.get(op_string)
    return '' if code is None else code


def _mode_name(value):
    """The AppOpsManager mode name, or the value as stored when it is outside the AOSP set."""
    if value is None:
        return ''
    return OP_MODES.get(str(value), str(value))


def _flag_names(value):
    """The PermissionFlags names set in a stored flags value, in bit order.

    A bit the table does not define is rendered as hex, the way AOSP's own flagToString renders
    one, so an undefined bit is visible rather than dropped.
    """
    try:
        flags = int(value)
    except (TypeError, ValueError):
        return '' if value is None else str(value)
    names = []
    remainder = flags
    for bit, name in PERMISSION_FLAGS:
        if flags & bit:
            names.append(name)
            remainder &= ~bit
    while remainder:
        bit = remainder & -remainder
        names.append(f'0x{bit:X}')
        remainder &= ~bit
    return ' | '.join(names)


def _is_granted(value):
    """AOSP's own determination of whether a permission is granted, from its flags.

    A port of PermissionFlags.isPermissionGranted. Returned as stored when the value is not an
    integer, so a value this cannot decide is visible rather than reported as not granted.
    """
    try:
        flags = int(value)
    except (TypeError, ValueError):
        return '' if value is None else str(value)
    if flags & INSTALL_GRANTED:
        return 'Yes'
    if flags & INSTALL_REVOKED:
        return 'No'
    if flags & PROTECTION_GRANTED:
        return 'Yes'
    if (flags & LEGACY_GRANTED) or (flags & IMPLICIT_GRANTED):
        return 'Yes'
    if flags & RESTRICTION_REVOKED:
        return 'No'
    return 'Yes' if flags & RUNTIME_GRANTED else 'No'


def _collect(context, section_reader):
    """(rows keyed on their content to the paths carrying them, the files read).

    The platform writes one element per scope and key, so a key repeats only when an extraction
    holds more than one copy of the file, which every tested Android 15 emulator does through
    data_mirror. Keyed this way a repeat costs no extra row while two copies that disagree still
    produce one row each. Insertion order is kept, so rows stay in the order the file stores them.
    """
    access_files, packages_files = _split_files(context)
    names, packages_read = _package_names(packages_files) if access_files else ({}, [])
    rows = {}
    sources = []
    for file_found in access_files:
        try:
            root = _root(file_found)
        except Exception as error:  # pylint: disable=broad-except
            logfunc(f'Permission store: could not read {file_found}: {error}')
            continue
        # The file was read, so it is cited whether or not it held any of this artifact's sections.
        sources.append(file_found)
        relative_path = context.get_relative_path(file_found)
        android_user = _android_user(file_found)
        for key in section_reader(root, names, android_user):
            paths = rows.setdefault(key, [])
            if relative_path not in paths:
                paths.append(relative_path)
    if sources:
        sources.extend(packages_read)
    return rows, sources


def _op_mode_rows(root, names, android_user):
    """The stored app op modes, from both the app id scoped and the package scoped sections."""
    for element in root.findall('./app-id-app-ops/app-id'):
        stored_id = element.get('id', '')
        app_id = _app_id(stored_id)
        package = names.get(app_id, '')
        for app_op in element:
            if app_op.tag != 'app-op':
                continue
            op_string = app_op.get('name', '')
            yield (package, stored_id, android_user, op_string, _op_code(op_string),
                   _mode_name(app_op.get('mode')), 'App ID')
    for element in root.findall('./package-app-ops/package'):
        package = element.get('name', '')
        for app_op in element:
            if app_op.tag != 'app-op':
                continue
            op_string = app_op.get('name', '')
            yield (package, '', android_user, op_string, _op_code(op_string),
                   _mode_name(app_op.get('mode')), 'Package')


def _grant_rows(root, names, android_user):
    """The stored permission grants, from the app id scoped section."""
    for element in root.findall('./app-id-permissions/app-id'):
        stored_id = element.get('id', '')
        app_id = _app_id(stored_id)
        package = names.get(app_id, '')
        for permission in element:
            if permission.tag != 'permission':
                continue
            flags = permission.get('flags')
            yield (package, stored_id, android_user, permission.get('name', ''),
                   _is_granted(flags), _flag_names(flags))


@artifact_processor
def permission_app_op_modes(context):
    data_headers = (
        'Package Name',
        'App ID',
        'Android User',
        'App Op',
        'Op Code',
        'Mode',
        'Mode Stored Against',
        'Source File',
    )
    rows, sources = _collect(context, _op_mode_rows)
    data_list = [key + (', '.join(paths),) for key, paths in rows.items()]
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def permission_grants(context):
    data_headers = (
        'Package Name',
        'App ID',
        'Android User',
        'Permission',
        'Granted',
        'Permission Flags',
        'Source File',
    )
    rows, sources = _collect(context, _grant_rows)
    data_list = [key + (', '.join(paths),) for key, paths in rows.items()]
    return data_headers, data_list, '\n'.join(sources)
