__artifacts_v2__ = {
    "permissionChangeDates": {
        "name": "Permission Change Dates",
        "description": "The day stored by the Permission Controller for each app's last permission change, from "
                       "permission_changes.xml, including copies kept in rollback snapshots.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-01",
        "last_update_date": "2026-11-01",
        "requirements": "none",
        "category": "Permissions",
        "notes": "Reads permission_changes.xml from the Permission Controller's device encrypted files folder (<package>/files under data/user_de/<user>, data_mirror/data_de or userdata/user_de, for com.google.android.permissioncontroller or com.android.permissioncontroller). Format and meanings come from AOSP packages/modules/Permission at commit 26231a7eac744c7d2a8fea4740926620f56b20c6. The file holds at most one entry per app package (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/PermissionChangeStorageImpl.kt#67, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/PermissionChangeStorageImpl.kt#192). When a permission's grant state or flags change on an app's permission screen (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/ui/model/AppPermissionViewModel.kt#1454, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/ui/model/AppPermissionViewModel.kt#1464), or when an app's runtime permission request is answered on Android 13 and later (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/ui/model/GrantPermissionsViewModel.kt#989, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/ui/model/GrantPermissionsViewModel.kt#996), the controller records the package with the current time, writes it first and drops that package's earlier entry (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/PermissionChangeStorageImpl.kt#86, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/PermissionChangeStorageImpl.kt#88, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/BasePermissionEventStorage.kt#55, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/BasePermissionEventStorage.kt#58). Last Permission Change (as stored) is the value written: the day as yyyy-MM-dd in the device's time zone when it was written (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/PermissionChangeStorageImpl.kt#56, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/PermissionChangeStorageImpl.kt#106). The controller writes the time to the millisecond instead only when its store-exact-time setting is on, which defaults to off (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/PermissionChangeStorageImpl.kt#204); the file's store-exact-time attribute was false in every tested file. The entry records neither the permission nor whether it was allowed or denied, and a second change to the same app replaces the first. Position is the entry's place in the file, 1 first: a new entry is written first and the others keep their order (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/BasePermissionEventStorage.kt#55, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/BasePermissionEventStorage.kt#58), so a lower Position was recorded later. Entries are removed by a cleanup job once older than the unused-app threshold, 90 days unless device configuration sets another value (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/PermissionChangeStorageImpl.kt#186, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/PermissionChangeStorageImpl.kt#188, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/BasePermissionEventStorage.kt#78, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/BasePermissionEventStorage.kt#85, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/hibernation/HibernationPolicy.kt#127), and when the app's data is cleared or the app is fully removed (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/PersistedStoragePackageUninstalledReceiver.kt#52, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/PersistedStoragePackageUninstalledReceiver.kt#64). When the controller finds the wall clock more than 60 seconds away from what the elapsed time since its last snapshot predicts, it moves every entry by the difference (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/PermissionStorageTimeChangeReceiver.kt#65, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/PermissionStorageTimeChangeReceiver.kt#102, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/PermissionStorageTimeChangeReceiver.kt#114, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/BasePermissionEventStorage.kt#106, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/BasePermissionEventStorage.kt#110), so a date can move with no permission change. The Permission Controller Log artifact lists those clock changes, removals and cleanups from the same folder. Known data (Google Permission Controller on an Android 15 emulator, no Google account): allowing Chrome's camera on its permission screen wrote one Chrome entry dated that day. Denying the Messages app's camera then wrote a Messages entry at Position 1, the same kind of entry as the allow. Moving the clock 10 days forward (the log recorded 863999 seconds) moved both entries from 2026-11-01 to 2026-11-10 with no permission touched: the stored day is read back as its local midnight, so a shift just under 10 days lands on the ninth day. Clearing Chrome's data then removed its entry, and the log recorded the data clear for it. Three images hold a rollback snapshot whose dates differ from the live file's, and on each the live file's dates are the snapshot's moved by one amount that a single clock change logged after the snapshot accounts for: hickman_a13, all 51 entries 30 days later and a logged change of about 30.55 days, logged about 83 seconds after a boot; russell_a14 user 0, both entries 11 days later and 11.25 days logged; hc_pixel8pro_a16, 30 of 31 entries 2 days later and 2.16 days logged; the other entry is 38 days earlier in the live file, and why was not established. What caused those clock changes was not established. In 7 live files an entry written later carried an earlier date than the entry after it (1 to 5 such pairs per file), which is what a forward clock change leaves when entries are recorded after it; which change produced each pair was not traced. Copy is Current for the app's own folder. Rollback snapshot <id> is the copy of an app's data Android keeps for a rollback, taken at one moment, under misc_de/<user>/rollback/<id>/<package> (https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/services/core/java/com/android/server/rollback/AppDataRollbackHelper.java#61, https://android.googlesource.com/platform/frameworks/native/+/4f463a6b1de9198963dc6aff74154a504ba3f8f6/cmds/installd/utils.cpp#274); a snapshot row equal in every column to a Current row of the same user is not shown, and a snapshot byte identical to the live file is not read. The storage views one extraction can hold for the folder (data/user_de, data_mirror) are read once. Android User is the user whose folder holds the file, read from its path (data/user_de/<n>, data_mirror/data_de/<volume>/<n>, misc_de/<n>/rollback); the files read are listed in the report's source paths. Not read here: recent_permission_decisions.xml, which records the permission group and the decision, is written only on Android Automotive (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/v33/PermissionDecisionStorageImpl.kt#93, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/v33/PermissionDecisionStorageImpl.kt#108, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/v33/PermissionDecisionStorageImpl.kt#109) and was on no tested image; apps_safety_label_history_persistence.xml and packages_already_notified_location_access in the same folder are other stores this artifact does not read. On the tested images: 447 rows on 16 of 20 images, 361 Current and 86 from rollback snapshots on hc_pixel8pro_a16, hickman_a13 and russell_a14. permission_changes.xml was not in the Android 10, 11 and 12 images (galaxys10_a10, cookbook_a11, pixel3_a11, pixel3_a12). Copy held Current on every row of the other 13 images with rows. A live file held 1 to 62 entries. Android User held 0 on every row of 13 of the 16 images; russell_a14 and russell_pixel6a_a13 also had user 10 and samsungs20_a13 user 150.",
        "paths": ('*/com.google.android.permissioncontroller/files/permission_changes.xml',
                  '*/com.android.permissioncontroller/files/permission_changes.xml'),
        "output_types": "standard",
        "artifact_icon": "shield",
        "sample_data": {
            "anne_a15": "Android 15 | 20 rows",
            "cookbook_a11": "Android 11 | 0 rows",
            "emu_a15_oss2_v3": "Android 15 | 3 rows",
            "emu_a15_oss_v17": "Android 15 | 23 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 62 rows",
            "hc_pixel8pro_a17": "Android 17 | 33 rows",
            "hickman_a13": "Android 13 | 102 rows",
            "kevin_pocox7_a15": "Android 15 | 11 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 0 rows",
            "pixel7a_a14": "Android 14 | 62 rows",
            "russell_a14": "Android 14 | 9 rows",
            "russell_pixel6a_a13": "Android 13 | 36 rows",
            "s20fe_a13": "Android 13 | 4 rows",
            "samsunga53_a14": "Android 14 | 12 rows",
            "samsungs20_a13": "Android 13 | 28 rows",
            "sharon_a13": "Android 13 | 14 rows",
            "sharon_a14": "Android 14 | 14 rows",
            "userb2_a13": "Android 13 | 14 rows",
        },
    },
    "permissionControllerLog": {
        "name": "Permission Controller Log",
        "description": "Clock changes, package removals and data clears, permission change cleanups, and unused-app "
                       "hibernation and auto-revoke runs the Permission Controller wrote to its LogToDump.log.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-01",
        "last_update_date": "2026-11-01",
        "requirements": "none",
        "category": "Permissions",
        "notes": "Reads LogToDump.log from the Permission Controller's device encrypted files folder (<package>/files under data/user_de/<user>, data_mirror/data_de or userdata/user_de, for com.google.android.permissioncontroller or com.android.permissioncontroller). Format and meanings come from AOSP packages/modules/Permission at commit 26231a7eac744c7d2a8fea4740926620f56b20c6. The controller appends a line per message: the wall clock time in milliseconds since 1970, the tag and level, and the message (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/DumpableLog.kt#75). Logged is that time in UTC, as the device clock read when the line was written; lines are not moved when the clock changes. Once the file passes 64 KiB the controller keeps its newer half and starts it with a 'truncated at <time>' line (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/DumpableLog.kt#25, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/DumpableLog.kt#70), so older lines are lost; each such line is a Log truncated row. Only these messages are reported. Clock change: the controller found the wall clock more than 60 seconds away from what the elapsed time since its last snapshot predicts and moved every permission change entry by the difference; Clock Change (seconds) is that difference as logged, rounded toward zero (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/PermissionStorageTimeChangeReceiver.kt#65, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/PermissionStorageTimeChangeReceiver.kt#102, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/PermissionStorageTimeChangeReceiver.kt#104, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/PermissionStorageTimeChangeReceiver.kt#114). Package data cleared and Package fully removed: the controller received that broadcast for Package and removed the package's permission change entry (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/PersistedStoragePackageUninstalledReceiver.kt#52, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/PersistedStoragePackageUninstalledReceiver.kt#60, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/PersistedStoragePackageUninstalledReceiver.kt#64). Old change entries removed: the cleanup job removed Entries Removed entries older than the unused-app threshold (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/BasePermissionEventStorage.kt#78, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/BasePermissionEventStorage.kt#85); on a device that is not Android Automotive this count is for permission_changes.xml alone (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/PermissionEventStorageImpls.kt#35, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/v33/PermissionDecisionStorageImpl.kt#108, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/v33/PermissionDecisionStorageImpl.kt#109); runs that removed nothing are not shown. Permissions auto-revoked, Hibernated for user and Hibernated globally: the hibernation job revoked the app's permissions or set it hibernating (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/AutoRevokePermissions.kt#279, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/AutoRevokePermissions.kt#287, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/hibernation/v31/HibernationController.kt#67, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/hibernation/v31/HibernationController.kt#94, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/hibernation/v31/HibernationController.kt#103, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/hibernation/v31/HibernationController.kt#104), after selecting it as unused for longer than the threshold, by its usage, install time and the start of tracking (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/hibernation/HibernationPolicy.kt#484, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/hibernation/HibernationPolicy.kt#1011, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/hibernation/HibernationPolicy.kt#1014). One row per package; Package User is the user named in the message. Every other message (job scheduling, the clock snapshots it takes, exemptions) is not reported. Known data (Google Permission Controller on an Android 15 emulator): moving the clock 10 days forward logged a clock change of 863999 seconds and moved the permission change entries by it; clearing Chrome's data logged Package data cleared for it and removed its entry. On hickman_a13 a logged clock change of about 30.55 days matched the 30 day shift between the live permission_changes.xml and its rollback snapshot. Copy is Current for the app's own folder. Rollback snapshot <id> is the copy of an app's data Android keeps for a rollback, taken at one moment, under misc_de/<user>/rollback/<id>/<package> (https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/services/core/java/com/android/server/rollback/AppDataRollbackHelper.java#61, https://android.googlesource.com/platform/frameworks/native/+/4f463a6b1de9198963dc6aff74154a504ba3f8f6/cmds/installd/utils.cpp#274); a snapshot row equal in every column to a Current row of the same user is not shown, and a snapshot byte identical to the live file is not read. The storage views one extraction can hold for the folder (data/user_de, data_mirror) are read once. Android User is the user whose folder holds the file, read from its path (data/user_de/<n>, data_mirror/data_de/<volume>/<n>, misc_de/<n>/rollback); the files read are listed in the report's source paths. On the tested images: 813 rows on 18 of 20 images: Clock change 479 rows on 15 images, Package fully removed 82 on 11, Package data cleared 43 on 8, Hibernated for user 89 and Hibernated globally 78 on 3, Permissions auto-revoked 8 on 3, Old change entries removed 17 on 2, and Log truncated 17 on 13. galaxys10_a10 and pixel3_a11 gave no row. Package and Package User are empty on Clock change, Log truncated and Old change entries removed rows, and Package User also on Hibernated globally rows; Clock Change (seconds) is empty on every row but Clock change rows, and Entries Removed is empty on every row but Old change entries removed rows. Event held Clock change on every row of userb2_a13. Copy held Current on every row of 16 of the 18 images; hc_pixel8pro_a16 (11 rows) and pixel3_a12 (1 row) had lines only their rollback snapshot logs hold. Android User held 0 on every row of 13 of the 18 images; emu_a15_oss2_v3, emu_a15_oss_v17, russell_a14 and russell_pixel6a_a13 also had user 10 and samsungs20_a13 user 150.",
        "paths": ('*/com.google.android.permissioncontroller/files/LogToDump.log',
                  '*/com.android.permissioncontroller/files/LogToDump.log'),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "anne_a15": "Android 15 | 47 rows",
            "cookbook_a11": "Android 11 | 2 rows",
            "emu_a15_oss2_v3": "Android 15 | 233 rows",
            "emu_a15_oss_v17": "Android 15 | 179 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 17 rows",
            "hc_pixel8pro_a17": "Android 17 | 10 rows",
            "hickman_a13": "Android 13 | 2 rows",
            "kevin_pocox7_a15": "Android 15 | 7 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 2 rows",
            "pixel7a_a14": "Android 14 | 14 rows",
            "russell_a14": "Android 14 | 184 rows",
            "russell_pixel6a_a13": "Android 13 | 5 rows",
            "s20fe_a13": "Android 13 | 7 rows",
            "samsunga53_a14": "Android 14 | 7 rows",
            "samsungs20_a13": "Android 13 | 40 rows",
            "sharon_a13": "Android 13 | 4 rows",
            "sharon_a14": "Android 14 | 45 rows",
            "userb2_a13": "Android 13 | 8 rows",
        },
    },
    "permissionControllerSafetyLabels": {
        "name": "Permission Controller Safety Label History",
        "description": "Per app, the last update time the Permission Controller took from the app when it recorded the "
                       "app's declared location sharing label, from apps_safety_label_history_persistence.xml.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-01",
        "last_update_date": "2026-11-01",
        "requirements": "none",
        "category": "Permissions",
        "notes": "Reads apps_safety_label_history_persistence.xml from the Permission Controller's device encrypted files folder (<package>/files under data/user_de/<user>, data_mirror/data_de or userdata/user_de, for com.google.android.permissioncontroller or com.android.permissioncontroller). Format and meanings come from AOSP packages/modules/Permission at commit 26231a7eac744c7d2a8fea4740926620f56b20c6. The controller keeps this history on Android 14 and later, except on Android Automotive, TV and Wear (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/utils/KotlinUtils.kt#248, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/utils/KotlinUtils.kt#254), for apps that request a location permission and were installed by a store or preloaded (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/safetylabel/SafetyLabelChangedBroadcastReceiver.kt#109, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/safetylabel/SafetyLabelChangedBroadcastReceiver.kt#113, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/model/livedatatypes/v34/LightInstallSourceInfo.kt#45). Each label it keeps is the location part of the data sharing section of the app's metadata, which the app's developer declares, not something the device user sets (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/safetylabel/SafetyLabelChangedBroadcastReceiver.kt#167, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/safetylabel/SafetyLabelChangedBroadcastReceiver.kt#177, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/safetylabel/AppsSafetyLabelHistory.kt#115). Package Last Update (when recorded) is the label's rcvd value, milliseconds since 1970 shown in UTC (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/safetylabel/AppsSafetyLabelHistoryPersistence.kt#54, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/safetylabel/AppsSafetyLabelHistoryPersistence.kt#504, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/safetylabel/AppsSafetyLabelHistoryPersistence.kt#538). It is not the time the controller wrote the entry: it is the app's last update time at the moment the label was recorded, taken from the package when the app is installed or updated (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/safetylabel/SafetyLabelChangedBroadcastReceiver.kt#62, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/safetylabel/SafetyLabelChangedBroadcastReceiver.kt#167) or when a periodic job records labels it is missing (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/v34/SafetyLabelChangesJobService.kt#276, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/v34/SafetyLabelChangesJobService.kt#363). A new label is added only when its location part differs from the app's newest kept label (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/safetylabel/AppsSafetyLabelHistoryPersistence.kt#568, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/safetylabel/AppsSafetyLabelHistoryPersistence.kt#572, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/safetylabel/AppsSafetyLabelHistoryPersistence.kt#576, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/safetylabel/AppsSafetyLabelHistoryPersistence.kt#583), so an update that leaves it unchanged adds nothing and the earlier time stays. At most 20 labels are kept per app unless device configuration sets another number (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/safetylabel/AppsSafetyLabelHistoryPersistence.kt#614, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/safetylabel/AppsSafetyLabelHistoryPersistence.kt#618). Label Order is 1 for the oldest kept label of an app. Declared Location Sharing (as stored) is the stored shared entries as category and ads value; it is empty when the stored label's shared set was empty, which is what a label whose location part declared no sharing leaves. Entries are deleted by the same periodic job, which runs every 30 days unless device configuration sets another interval (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/v34/SafetyLabelChangesJobService.kt#685, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/utils/KotlinUtils.kt#265): it removes the apps that are no longer among the installed apps that request location and were installed by a store or preloaded (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/v34/SafetyLabelChangesJobService.kt#403, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/v34/SafetyLabelChangesJobService.kt#406), and of the labels older than 30 days keeps only the newest one per app (https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/v34/SafetyLabelChangesJobService.kt#414, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/permission/service/v34/SafetyLabelChangesJobService.kt#635, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/safetylabel/AppsSafetyLabelHistoryPersistence.kt#230, https://android.googlesource.com/platform/packages/modules/Permission/+/26231a7eac744c7d2a8fea4740926620f56b20c6/PermissionController/src/com/android/permissioncontroller/safetylabel/AppsSafetyLabelHistoryPersistence.kt#241). An app removed since the last run can therefore still be listed; that is source-verified only, because every package in each tested file was in that image's packages.xml. Cross-check on the 9 live files of the 8 tested images that had one: of 255 kept labels, 81 had the app's first install time for that user (package-restrictions.xml first-install-time), 54 its last update time in packages.xml, 117 a time between the two, and 3 a time before that user's first install time. Two of those 3 are on user 10 of russell_a14 and are not before user 0's first install time of the same app; the third, on sharon_a14, was not explained. Of the 96 distinct app and time pairs that fell between first install and last update, none equals a value in the Play Store's localappstate.db, library.db or frosting.db on the same image, and 3 are within 2 seconds of one in a row for the same app; other stores were not compared. No known-data case was made: the emulator used for the other artifacts has no store installs, so this artifact is source-verified and cross-checked on the corpus only. Copy is Current for the app's own folder. Rollback snapshot <id> is the copy of an app's data Android keeps for a rollback, taken at one moment, under misc_de/<user>/rollback/<id>/<package> (https://android.googlesource.com/platform/frameworks/base/+/1cdfff555f4a21f71ccc978290e2e212e2f8b168/services/core/java/com/android/server/rollback/AppDataRollbackHelper.java#61, https://android.googlesource.com/platform/frameworks/native/+/4f463a6b1de9198963dc6aff74154a504ba3f8f6/cmds/installd/utils.cpp#274); a snapshot row equal in every column to a Current row of the same user is not shown, and a snapshot byte identical to the live file is not read. The storage views one extraction can hold for the folder (data/user_de, data_mirror) are read once. Android User is the user whose folder holds the file, read from its path (data/user_de/<n>, data_mirror/data_de/<volume>/<n>, misc_de/<n>/rollback); the files read are listed in the report's source paths. On the tested images: 255 rows on 8 of 20 images, Android 14 to 17; the 10 Android 10 to 13 images and the two Android 15 emulator images had no such file. Copy held Current on every row: the rollback snapshots on hc_pixel8pro_a16 and russell_a14 repeated their live files' labels. Android User held 0 on every row of 7 of the 8 images; russell_a14 also had user 10. Label Order held 1 on every row of 6 of the 8 images; it was 1 on 253 rows and 2 on 2, one app each on russell_a14 and sharon_a14. Declared Location Sharing (as stored) was empty on 229 rows, location (ads: false) on 14 and location (ads: true) on 12.",
        "paths": ('*/com.google.android.permissioncontroller/files/apps_safety_label_history_persistence.xml',
                  '*/com.android.permissioncontroller/files/apps_safety_label_history_persistence.xml'),
        "output_types": "standard",
        "artifact_icon": "tag",
        "sample_data": {
            "anne_a15": "Android 15 | 25 rows",
            "cookbook_a11": "Android 11 | 0 rows",
            "emu_a15_oss2_v3": "Android 15 | 0 rows",
            "emu_a15_oss_v17": "Android 15 | 0 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 26 rows",
            "hc_pixel8pro_a17": "Android 17 | 29 rows",
            "hickman_a13": "Android 13 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 16 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 0 rows",
            "pixel7a_a14": "Android 14 | 53 rows",
            "russell_a14": "Android 14 | 62 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 20 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 24 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
    },
}

import datetime
import re
import xml.etree.ElementTree as ET

from scripts.artifacts.storagePathViews import android_user, unique_files, without_snapshot_repeats
from scripts.ilapfuncs import artifact_processor, logfunc

# A rollback snapshot of an app's data folder: misc_de/<user>/rollback/<rollback id>/<package>/ (see the notes).
_SNAPSHOT = re.compile(r'(?:^|/)(?:user)?data/misc_(?:ce|de)/(\d+)/rollback/(\d+)/')
_LINE = re.compile(r'^(\d{13}) (\S+?):([vdiwe]) (.*)$')
_TRUNCATED = re.compile(r'^truncated at (\d{13})\s*$')
_CLOCK = re.compile(r'Time changed by (-?\d+) seconds')
_RECEIVED = re.compile(r'Received android\.intent\.action\.(PACKAGE_DATA_CLEARED|PACKAGE_FULLY_REMOVED) for (\S+) for u(\d+)')
_OLD_REMOVED = re.compile(r'^(\d+) old permission events removed')
_REVOKED = re.compile(r'Done auto-revoke for user \d+ - revoked \[(.*)\]')
_HIBERNATED = re.compile(r'Done hibernating apps \[(.*)\]')
_GLOBAL = re.compile(r'Globally hibernating apps \[(.*)\]')
_PAIR = re.compile(r'\(([^,()\s]+), UserHandle\{(\d+)\}\)')
_RECEIVED_EVENTS = {'PACKAGE_DATA_CLEARED': 'Package data cleared', 'PACKAGE_FULLY_REMOVED': 'Package fully removed'}


def _where(context, path):
    """(relative path, Android User) for a file the seeker found."""
    relative = str(context.get_relative_path(path)).replace('\\', '/')
    snapshot = _SNAPSHOT.search(relative)
    return relative, snapshot.group(1) if snapshot else android_user(relative)


def _with_copy(rows):
    """rows (ending in Android User and the relative path) without the snapshot rows that repeat a live row, each
    given its Copy before the Android User, and the path dropped. Copy is left out of the comparison, which is what
    lets a snapshot row equal its live row."""
    kept = []
    for row in without_snapshot_repeats(rows):
        snapshot = _SNAPSHOT.search(row[-1])
        kept.append(row[:-2] + (f'Rollback snapshot {snapshot.group(2)}' if snapshot else 'Current', row[-2]))
    return kept


def _files(context, name):
    return [path for path in unique_files(context) if str(path).replace('\\', '/').rsplit('/', 1)[-1] == name]


def _ms(value):
    return datetime.datetime.fromtimestamp(int(value) / 1000, tz=datetime.timezone.utc)


@artifact_processor
def permissionChangeDates(context):
    data_headers = ('Last Permission Change (as stored)', 'Package', 'Position', 'Copy', 'Android User')
    rows, sources = [], []
    for path in _files(context, 'permission_changes.xml'):
        relative, user = _where(context, path)
        sources.append(str(path))
        try:
            with open(path, 'rb') as handle:
                root = ET.fromstring(handle.read())
        except (OSError, ET.ParseError) as ex:
            logfunc(f'Permission Change Dates: could not read {relative}: {type(ex).__name__}')
            continue
        if root.tag != 'permission-changes':
            logfunc(f'Permission Change Dates: {relative} starts with <{root.tag}>, not <permission-changes>; skipped')
            continue
        position = 0
        for entry in root:
            if entry.tag != 'permission-change':
                continue
            position += 1
            rows.append((entry.get('event-time', ''), entry.get('package-name', ''), position, user, relative))
    return data_headers, _with_copy(rows), '\n'.join(sources)


def _log_rows(text):
    """(time, Event, Package, Package User, Clock Change (seconds), Entries Removed) for the reported messages."""
    rows = []
    last_time = None
    for line in text.splitlines():
        truncated = _TRUNCATED.match(line)
        if truncated:
            rows.append((_ms(truncated.group(1)), 'Log truncated', '', '', '', ''))
            continue
        match = _LINE.match(line)
        if match:
            last_time, message = _ms(match.group(1)), match.group(4)
        elif last_time is not None:
            message = line  # a message written over several lines continues here
        else:
            continue
        if (clock := _CLOCK.search(message)) and match:
            rows.append((last_time, 'Clock change', '', '', int(clock.group(1)), ''))
        elif (received := _RECEIVED.search(message)) and match:
            rows.append((last_time, _RECEIVED_EVENTS[received.group(1)], received.group(2), received.group(3), '', ''))
        elif (removed := _OLD_REMOVED.match(message)) and match and match.group(2) == 'BasePermissionEventStorage':
            if int(removed.group(1)):
                rows.append((last_time, 'Old change entries removed', '', '', '', int(removed.group(1))))
        elif revoked := _REVOKED.search(message):
            for package, user in _PAIR.findall(revoked.group(1)):
                rows.append((last_time, 'Permissions auto-revoked', package, user, '', ''))
        elif hibernated := _HIBERNATED.search(message):
            for package, user in _PAIR.findall(hibernated.group(1)):
                rows.append((last_time, 'Hibernated for user', package, user, '', ''))
        if not match and (globally := _GLOBAL.search(message)):
            for package in (name.strip() for name in globally.group(1).split(',')):
                if package:
                    rows.append((last_time, 'Hibernated globally', package, '', '', ''))
    return rows


@artifact_processor
def permissionControllerLog(context):
    data_headers = (('Logged', 'datetime'), 'Event', 'Package', 'Package User', 'Clock Change (seconds)',
                    'Entries Removed', 'Copy', 'Android User')
    rows, sources = [], []
    for path in _files(context, 'LogToDump.log'):
        relative, user = _where(context, path)
        sources.append(str(path))
        try:
            with open(path, 'rb') as handle:
                text = handle.read().decode('utf-8', 'replace')
        except OSError as ex:
            logfunc(f'Permission Controller Log: could not read {relative}: {type(ex).__name__}')
            continue
        rows.extend(row + (user, relative) for row in _log_rows(text))
    return data_headers, _with_copy(rows), '\n'.join(sources)


def _shared(label):
    """The stored shared entries of a label as category and ads value, in file order."""
    entries = []
    for entry in label.iter('entry'):
        entries.append(f"{entry.get('cat', '')} (ads: {entry.get('ads', '')})")
    return ', '.join(entries)


@artifact_processor
def permissionControllerSafetyLabels(context):
    data_headers = (('Package Last Update (when recorded)', 'datetime'), 'Package', 'Label Order',
                    'Declared Location Sharing (as stored)', 'Copy', 'Android User')
    rows, sources = [], []
    for path in _files(context, 'apps_safety_label_history_persistence.xml'):
        relative, user = _where(context, path)
        sources.append(str(path))
        try:
            with open(path, 'rb') as handle:
                root = ET.fromstring(handle.read())
        except (OSError, ET.ParseError) as ex:
            logfunc(f'Permission Controller Safety Label History: could not read {relative}: {type(ex).__name__}')
            continue
        if root.tag != 'apps-hstry':
            logfunc(f'Permission Controller Safety Label History: {relative} starts with <{root.tag}>, not <apps-hstry>; '
                    'skipped')
            continue
        for history in root.iter('app-hstry'):
            info = history.find('app-info')
            package = info.get('pkg-name', '') if info is not None else ''
            for order, label in enumerate(history.iter('sfty-lbl'), 1):
                received = label.get('rcvd', '')
                when = _ms(received) if received.isdigit() else received
                rows.append((when, package, order, _shared(label), user, relative))
    return data_headers, _with_copy(rows), '\n'.join(sources)
