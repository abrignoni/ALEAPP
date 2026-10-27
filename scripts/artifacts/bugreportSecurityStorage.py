__artifacts_v2__ = {
    "bugreport_device_policy_admins": {
        "name": "Bug Report - Device Policy Admins",
        "description": "The Enabled Device Admins entries of each Android user in the device_policy dump of an Android bug "
                       "report text, with the admin component, uid, declared policies and the password and lock values as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Security and Device Policy",
        "notes": "One row per admin component printed under an Enabled Device Admins (User N, provisioningState: P) heading of the "
                 "device_policy service dump. Admin Component is the component as printed (package, a slash and the class); Package "
                 "is the part before the slash. Declared Policies are the lines printed under policies: for the entry, in the order "
                 "printed, and are the platform's own policy names. Password Quality (as stored), Minimum Password Length, Max "
                 "Failed Passwords For Wipe, Encryption Requested, Disabled Keyguard Features (as stored), Network Logging, "
                 "VPN Package and VPN Lockdown (the mAlwaysOnVpnPackage and mAlwaysOnVpnLockdown values), Is Parent and Common Criteria Mode are the values printed on the entry "
                 "(null stays null; the two hexadecimal or numeric values are not decoded). Source Dir is the first sourceDir= "
                 "line in the application info of the entry and is empty where the entry prints none (the Motorola entry prints no "
                 "application info). A row says that the device policy service listed the component as an enabled admin with the "
                 "printed declared policies; it does not say what the admin did, and a declared policy is not an action taken. "
                 "Device owner and profile owner entries are rows of Bug Report - Device Policy State.\n"
                 "The two Android 10 reports (Huawei and the Transsion-brand phone) print the heading with no admin under it, "
                 "so the table is empty for them, which says nothing about the device. The dump is the state when it ran. Not "
                 "read: the eas it policies, the device admin info block, the keys of the entry that are not shown here "
                 "(for example the cross profile lists) and the per-user keys printed after the entries (those are in "
                 "Device Policy State).\n"
                 "Evidence tiers. Data-proven on three of five real bug reports: a Samsung A-series phone (1 row) and a Samsung "
                 "S-series phone (1 row) on Android 16 and a Motorola phone on Android 15 (1 row, user 11), each equal to a "
                 "count of admin component lines in the raw text; none on the two Android 10 reports, which print none. "
                 "Test Only, Is Parent, Common Criteria Mode, Password Quality, Minimum Password Length, Max Failed Passwords For Wipe, "
                 "Encryption Requested, Disabled Keyguard Features, Network Logging and the two VPN columns held one value on all three "
                 "rows. Not examined: Android 11, 12 and 14, an entry for a device owner, a second admin for one user, "
                 "other vendors."
                 "\nOn the corpus the run gave s20fe_a13 1 row; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "shield",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 1 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_device_policy_state": {
        "name": "Bug Report - Device Policy State",
        "description": "The owner entries, per-user state lines, device policy cache and device state cache of the device_policy "
                       "dump of an Android bug report text, as name and value pairs.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Security and Device Policy",
        "notes": "One row per name and value line of these parts of the device_policy service dump: Group says which part. The groups "
                 "are the Immutable state, a Profile Owner or Device Owner entry (User holds the user of the entry), the lines "
                 "printed after the admin entries of a user (Device admins state, for example mPasswordOwner and "
                 "mUserSetupComplete), the lines of the main state (Pending System Update, the policy size limits), Admin policies "
                 "size (one row per admin with the number printed after it), the lines printed after the main state (Encryption "
                 "Status, Logout user), the Device policy cache, the Device state cache (a nested line has its parent in "
                 "Name, for example Has PO / User 10) and the Personal apps suspension helper (the settings and counts it prints). "
                 "Name and Value are as printed; Value is empty where the line has none. The lists of package names printed "
                 "under the personal apps helper (80 to 147 packages) and the Constants and Stats parts are not read.\n"
                 "A row records a value printed by the device policy service when the dump ran. It does not say how the value "
                 "came about, and a profile owner entry does not say who set it. Absence of an owner entry is absence of a "
                 "printed line.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 41, 41, 4, 4 and 46 rows. The Motorola report "
                 "prints a Profile Owner entry for user 11; the other four print none. Device Owner entries were not "
                 "present in the tested reports and that layout is constructed only. Not examined: Android 11 and 12, other vendors."
                 "\nOn the corpus the run gave s20fe_a13 19 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "shield",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 19 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_device_policies": {
        "name": "Bug Report - Device Policies",
        "description": "The Local Policies and Global Policies of the device_policy dump of an Android bug report text, with the "
                       "policy key, the admin, the value each admin set and the resolved value as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Security and Device Policy",
        "notes": "One row per admin printed under Per-admin Policy of a policy, or one row for a policy that prints null there. "
                 "Scope is Local (User holds the user printed above the policy) or Global (User is empty). Policy Key is the "
                 "key type and key as printed. Admin Package and Admin Authorities come from the EnforcingAdmin text; Admin Value "
                 "is the value line printed under it. Resolved Mechanism is the word in brackets after Resolved Policy "
                 "(for example MostRestrictive, MostRecent) and Resolved Value the line under it, empty where null is printed. "
                 "The words and values are the platform's own and are not decoded. A row says what the policy engine printed; it "
                 "does not say when the policy was set or why.\n"
                 "Only the Android 16 and Android 15 builds tested print a policy engine section with entries. The Local "
                 "Policies and Global Policies headings are empty on the Motorola report (Android 15), and the two Android 10 "
                 "reports do not print them, so the table is empty for those three, which says nothing about the device. The "
                 "policy size limit lines are rows of Device Policy State.\n"
                 "Evidence tiers. Data-proven on two real Android 16 bug reports (Samsung A-series 1 row, Samsung S-series 3 "
                 "rows). Not examined: other Android versions and vendors, a policy with more than one admin and a policy value "
                 "other than an integer."
                 "\nOn the corpus none of s20fe_a13, samsungs20_a13, sharon_a14 and userb2_a13 gave a row; the device_policy dump of s20fe_a13 (Android 13) prints no Local Policies or Global Policies section (its admin's declared policies are in Bug Report - Device Policy Admins).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "shield",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_lock_settings_users": {
        "name": "Bug Report - Lock Settings Users",
        "description": "The credential state of each Android user in the lock_settings dump of an Android bug report text, with "
                       "the protector ids, the last change time, the credential type and the counters as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Security and Device Policy",
        "notes": "One row per User N entry of the lock_settings service dump. The Android 14 and later layout (User State) prints "
                 "Protector ID, LSKF last changed with the previous protector, Backup protector, SI Checker, Secure Mode, SID, "
                 "Quality, CredentialType, SeparateChallenge, Metrics and failed attempt; the Android 10 layout prints only "
                 "SP Handle and SID. A key this reader does not know is kept in Other as name: value. The hexadecimal ids are "
                 "as printed. Credential Type is the word the platform prints (for example PIN); the dump does not print the "
                 "credential, a hash of it or its length. Quality and Secure Mode are the printed numbers (as stored). Last "
                 "Changed As Printed is a device wall-clock time without a zone; Last Changed (UTC) converts it with the zone "
                 "shown in Bug Report - Device Facts and is empty, with a Time Note, where the report records no zone or the "
                 "time was not set. Backup Protector keeps its own printed times (1970-01-01 when not set).\n"
                 "A row says what the lock settings service printed when the dump ran. It does not say how the credential "
                 "was chosen or whether a screen lock is on: a Credential Type of PIN is the printed word. The log of "
                 "credential enrollments and verifications that the Samsung reports print is in Bug Report - Lock Settings Log.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 1, 1, 1, 1 and 2 rows (the Motorola report lists "
                 "users 0 and 11), each equal to a count of User N lines in the raw text. The two Android 10 reports print the "
                 "short layout, so Protector ID, Last Changed and Credential Type are empty for them. Not examined: Android 11 "
                 "and 12, other vendors, a user with a pattern or password credential."
                 "\nOn the corpus the run gave s20fe_a13 1 row; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "lock",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 1 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_lock_settings_files": {
        "name": "Bug Report - Lock Settings Files",
        "description": "The file listing of the protector directories in the lock_settings dump of an Android bug report text, "
                       "with the size, modification time and file name as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Security and Device Policy",
        "notes": "One row per file printed under Storage: in the lock_settings service dump. Location says which listing (User N, "
                 "or Backup) and Directory is the directory printed on the heading. Size is the number printed before the time "
                 "(a count of bytes, as printed). Modified As Printed is a device wall-clock time without a zone and Modified "
                 "(UTC) converts it with the zone shown in Bug Report - Device Facts, empty with a Time Note where the report has "
                 "no zone. File Name is as printed; it contains the protector id. The dump lists names, sizes and times only: the "
                 "file contents are not in a bug report.\n"
                 "The Android 10 reports (Huawei and the Transsion-brand phone) print no Storage listing, so the table is empty "
                 "for them. A listing is the state when the dump ran, and the same files are also listed inside the log "
                 "entries of the Samsung reports (not read here).\n"
                 "Evidence tiers. Data-proven on three of five real bug reports (13 rows on the Samsung A-series and the Samsung "
                 "S-series phone on Android 16, 12 rows on the Motorola phone on Android 15), each equal to a count of "
                 "listing lines in the raw text. Not examined: other Android versions and vendors."
                 "\nOn the corpus none of s20fe_a13, samsungs20_a13, sharon_a14 and userb2_a13 gave a row; why was not examined.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "lock",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_lock_settings_state": {
        "name": "Bug Report - Lock Settings State",
        "description": "The service lines, keys in namespace, strong authentication state and reboot escrow lines of the "
                       "lock_settings dump of an Android bug report text, as name and value pairs.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Security and Device Policy",
        "notes": "One row per line of these parts of the lock_settings service dump: Service (for example DO Enabled, SP Enabled, "
                 "PasswordHandleCount, ThirdPartyAppsStarted), Keys in namespace (the key names printed, which contain protector "
                 "ids), StrongAuth (one row per name and value, with User for the lines that print userId=) and RebootEscrow "
                 "(the flags and counters it prints). A sub-heading is part of Group (for example StrongAuth: "
                 "PrimaryAuthFlags state). Name and Value are as printed. The strong biometric timeout is a date and time "
                 "printed without a zone and is shown as printed. The primary auth flags are numbers shown as stored.\n"
                 "A row records what the service printed when the dump ran. The strong authentication lines are the platform's "
                 "state, not a record of an authentication, and a value of 0 is the printed number.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 13, 13, 1, 1 and 12 rows. The Android 10 reports "
                 "print only the SP Enabled line. Not examined: Android 11 and 12, other vendors, a reboot escrow event list "
                 "(the tested reports print it empty)."
                 "\nOn the corpus the run gave s20fe_a13 10 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "lock",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 10 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_lock_settings_log": {
        "name": "Bug Report - Lock Settings Log",
        "description": "The timestamped LSSLog entries of the lock_settings dump of an Android bug report text (credential "
                       "enrollments and verifications), with the section, time, message and detail lines as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Security and Device Policy",
        "notes": "One row per timestamped entry after the LSSLog: line of the lock_settings service dump. State is the part the "
                 "entry sits in (the text between Start and End on the dashed lines: Enroll, Verify, Events, Restore, Keyguard, "
                 "Summary, KeystoreErr and Unknown in the tested reports). Message is the "
                 "first line of the entry as printed after the time; Detail joins the lines that follow it and are not call "
                 "stack frames (up to 50 lines, 1,000 characters) with ' | '; Stack Frames counts the call stack lines of the entry, "
                 "which are not listed. Time As Printed is a device wall-clock time with milliseconds and no zone; Time (UTC) "
                 "converts it with the zone shown in Bug Report - Device Facts and is empty, with a Time Note, where the report "
                 "records no zone. The numbers in square brackets in some messages are printed by the platform and are not decoded.\n"
                 "An entry records that the lock settings service logged that message at that time. The platform wording (for "
                 "example INCORRECT_KEY, PIN Fail) is shown as printed and the table does not say who was entering what, or "
                 "why. The log is a bounded list kept by the device: the entries of the tested reports span about ten months "
                 "(Samsung A-series) and eighteen months (Samsung S-series), so an event that is not listed says nothing about "
                 "whether it happened.\n"
                 "Only the two Samsung reports (Android 16) print this log; the Huawei, Motorola and Transsion-brand reports have no "
                 "LSSLog lines, so the table is empty for them. Evidence tiers. Data-proven on two real bug reports (Samsung "
                 "A-series 479 rows and Samsung S-series 463 rows), each equal to a count of timestamped lines after LSSLog: in "
                 "the raw text. As both are in a UTC+0 zone, the conversion to UTC was checked on constructed text for other "
                 "zones. Not examined: other vendors and Android versions."
                 "\nOn the corpus none of s20fe_a13, samsungs20_a13, sharon_a14 and userb2_a13 gave a row; why was not examined.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "lock",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_biometric_statistics": {
        "name": "Bug Report - Biometric Statistics",
        "description": "The statistics JSON of the fingerprint and face service dumps of an Android bug report text, with the "
                       "counters of each print entry as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Security and Device Policy",
        "notes": "One row per entry of the prints list in the {\"service\": ...} line of the fingerprint and face service dumps. "
                 "Service is the dump (fingerprint or face); Sensor ID and Provider come from the Dumping for sensorId line "
                 "(empty on the Android 10 layout, which prints none); Provider Service is the service text of the JSON line. "
                 "ID (as printed) is the id of the entry; in the tested reports it matches a user id listed in the same report "
                 "(0, and 11 on the Motorola phone). Count, Accept, Reject, Quality, Acquire, Lockout and Permanent Lockout and the "
                 "Crypto counters are the numbers printed and are not decoded; a counter the line does not print is empty, and "
                 "a key this reader does not know is kept in Other Counters. HAL Deaths is the number printed after HAL deaths since "
                 "last reboot (or HAL Deaths). Count is a number the platform prints for the entry; the dump holds no "
                 "biometric template or image.\n"
                 "The counters accumulate in the service since its start or since the platform last reset them, so a count "
                 "of 0 is not a statement about earlier use, and a row says nothing about who was trying to authenticate. The "
                 "authentication session coordinator log of the same dumps is in Bug Report - Biometric Authentication Events.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 2, 2, 1, 2 and 4 rows, each equal to a count of "
                 "id entries in the raw JSON lines. Not examined: Android 11 and 12, other vendors, a device with more than one "
                 "sensor of a kind."
                 "\nOn the corpus the run gave s20fe_a13 2 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "fingerprint",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 2 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_biometric_sensors": {
        "name": "Bug Report - Biometric Sensors",
        "description": "The Sensors list of the biometric service dump of an Android bug report text, with the strength, "
                       "modality, state and cookie values as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Security and Device Policy",
        "notes": "One row per ID(n) line under Sensors: in the biometric service dump. OEM Strength, Updated Strength, Modality, State "
                 "and Cookie are the numbers printed (as stored) and are not decoded here: the strength and modality numbers are "
                 "the platform's own values. A row says which sensor ids the biometric service listed when the dump ran.\n"
                 "The Huawei and Transsion-brand reports (Android 10) print an empty biometric dump, so the table is empty for them, "
                 "which says nothing about the device. A line printed after CurrentSession (a record that starts with AP and has "
                 "times, on the Samsung S-series report) has no header in the dump and is not read.\n"
                 "Evidence tiers. Data-proven on three of five real bug reports (2 rows each on the Samsung A-series and S-series "
                 "phones on Android 16 and the Motorola phone on Android 15), each equal to a count of ID( lines in the raw "
                 "text. Not examined: other Android versions and vendors."
                 "\nOn the corpus the run gave s20fe_a13 2 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "fingerprint",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 2 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_biometric_events": {
        "name": "Bug Report - Biometric Authentication Events",
        "description": "The AuthSessionCoordinator log lines in the fingerprint and face service dumps of an Android bug report "
                       "text, with the event, user, sensor, request and result as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Security and Device Policy",
        "notes": "One row per numbered line after the AuthSessionCoordinator logs begin line. Service says which dump printed the "
                 "line. Sequence is the number after #. Event is the function name printed (for example authStartedFor, "
                 "authEndedFor, resetLockoutFor), with internal: in front for the lines the platform marks internal. User, Sensor "
                 "ID, Request ID, Biometric Strength and Was Successful are the values printed in the brackets and are empty "
                 "where the line prints none. As Printed keeps the line. The log has no times, so no time column is shown and the "
                 "rows can be ordered only by Sequence.\n"
                 "A row records a line of the platform's coordinator log. Was Successful is the printed word; the table does not say "
                 "who was authenticating or by what means, and a log that holds a limited number of lines (76 to 100 in the "
                 "tested reports) says nothing about earlier events. The fingerprint and face dumps print the same coordinator "
                 "log in the Samsung reports, so each line appears twice there, once for each Service.\n"
                 "The Android 10 reports (Huawei and Transsion-brand) print no coordinator log. Evidence tiers. Data-proven on "
                 "three of five real bug reports: Samsung A-series 152 rows and Samsung S-series 200 rows (Android 16, each line "
                 "twice) and Motorola 100 rows (Android 15), each equal to a count of numbered lines in the raw text. Not "
                 "examined: other Android versions and vendors."
                 "\nOn the corpus none of s20fe_a13, samsungs20_a13, sharon_a14 and userb2_a13 gave a row; why was not examined.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "fingerprint",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_trust_agents": {
        "name": "Bug Report - Trust Agents",
        "description": "The user entries and enabled trust agents of the trust manager dump of an Android bug report text, with "
                       "the trust state values as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Security and Device Policy",
        "notes": "One row per enabled trust agent of each User entry in the trust service dump, or one row for a user entry that "
                 "prints no agent (Agent is empty; Note holds the sentence the dump prints for it). User ID, User Name, "
                 "Flags (as stored) and the words in brackets (Qualifiers, for example current) are as printed; the name is "
                 "the display name of the Android user and is shown as printed, including any invisible text-direction "
                 "characters. Trust State, Trusted, Trust Managed, Device Locked, Active Unlock Running and Strong Auth Required "
                 "are the values printed after the colon (Trust State appears on the newer layout and Trusted on the Android 10 "
                 "layout, so one of them is empty). Agent, Bound, Connected, Managing Trust and Agent Trusted are the values "
                 "printed for the agent.\n"
                 "A row records the trust manager state when the dump ran. It does not say that a trusted place or device was "
                 "set up, and the agent list is what is enabled, not what happened. The Samsung reports print no trust service "
                 "dump, so the table is empty for them. The events of the same dump are in Bug Report - Trust Events.\n"
                 "Evidence tiers. Data-proven on three of five real bug reports (Huawei and Transsion-brand on Android 10, 1 "
                 "row each; Motorola on Android 15, 3 rows for two users), each equal to a count of agent and user lines in "
                 "the raw text; none on the two Samsung Android 16 reports. Not examined: Android 11, 12 and 14, other vendors, a "
                 "user whose agent is trusted."
                 "\nOn the corpus the run gave s20fe_a13 1 row; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "shield",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 1 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_trust_events": {
        "name": "Bug Report - Trust Events",
        "description": "The Events lists of each user in the trust manager dump of an Android bug report text, with the "
                       "time, event and detail as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Security and Device Policy",
        "notes": "One row per numbered line under Events: of a user entry in the trust service dump. Sequence is the number after "
                 "#, Event the word before the colon and Detail the text after it (for example agent=...). Time As Printed is month, "
                 "day and clock time without a year or zone. The year is not in the dump: Time (UTC) uses the latest year, the one "
                 "of the report or the one before, that does not put the event more than a day after the report time, and "
                 "converts with the zone shown in Bug Report - Device Facts (the rule of Bug Report - Settings Changes), and is "
                 "empty with a Time Note where the report has no time or zone. A row records that the trust manager noted that "
                 "event for the user's agent; it does not say what caused it.\n"
                 "The lists are short (1 or 2 lines in the tested reports) and the platform keeps a limited number, so an event "
                 "that is not listed says nothing about earlier events. The Samsung reports print no trust dump.\n"
                 "Evidence tiers. Data-proven on three of five real bug reports (1 row on Huawei and 1 on the Transsion-brand "
                 "phone on Android 10, 2 rows on the Motorola phone on Android 15), each equal to a count of event lines in the "
                 "raw text. As the tested reports are in a UTC+0 zone the conversion to UTC was checked on constructed text for "
                 "other zones. Not examined: other Android versions and vendors, a list longer than two lines."
                 "\nOn the corpus none of s20fe_a13, samsungs20_a13, sharon_a14 and userb2_a13 gave a row; the Events list of the trust dump of s20fe_a13 is empty.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "shield",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_adb_state": {
        "name": "Bug Report - ADB Manager State",
        "description": "The ADB MANAGER STATE of the adb service dump of an Android bug report text, as the path and value of "
                       "each printed key.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Security and Device Policy",
        "notes": "One row per key=value line of the nested ADB MANAGER STATE text of the adb service dump. Path joins the names of "
                 "the enclosing blocks with dots (for example debugging_manager.connected_to_adb) and Value is as printed. A row "
                 "records what the ADB manager printed when the dump ran: connected_to_adb=false says that the manager listed no "
                 "connection at that moment, not that debugging was off or never used. Whether ADB debugging is enabled is a "
                 "setting (adb_enabled in Bug Report - Settings) and the keys and signers of authorized computers are not in a "
                 "bug report.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 1 row each, the same path and value on all five "
                 "(debugging_manager.connected_to_adb, false), each equal to a count of key=value lines in the raw text. "
                 "The reader also reads a deeper nesting and a key with a value in other layouts, which is constructed text only. "
                 "Not examined: Android 11 and 12, other vendors, a report with a connected computer."
                 "\nOn the corpus the run gave s20fe_a13 1 row; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 1 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_vendor_guard_log": {
        "name": "Bug Report - knoxguard_service Log",
        "description": "The state lines and timestamped event lines of the knoxguard_service dump of an Android bug report text, "
                       "with the time, tag and message as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Vendor",
        "notes": "One row per line of the knoxguard_service service dump after its heading. Kind is Log for a line of the form "
                 "time : [tag] message and State for any other line (for example ADB blocked : false, DO blocked : false, "
                 "SF counter : 1). Tag is the text in square brackets and Message the text after it. Time As Printed is a device "
                 "wall-clock time without a zone; Time (UTC) converts it with the zone shown in Bug Report - Device Facts and is "
                 "empty, with a Time Note, where the report has no zone or the time was not set (1970-01-01). Values are shown "
                 "as printed, with nothing masked or left out; this includes a value printed after token: or token= in a "
                 "message (the dump prints a refresh token). A row records a line of the vendor service's own log; the table does not interpret the "
                 "state words (for example kgState values) or say what caused an event.\n"
                 "The rows are in the order printed: 2 of the 203 log rows of the Samsung A-series report have a time earlier than the "
                 "row before them. The Samsung S-series dump was cut by "
                 "the platform's 10,000 ms limit (a DUMP TIMEOUT line follows its last line), so its rows may be partial; this is "
                 "written to the log of the run. The section exists only on the two Samsung reports (Android 16); the others do "
                 "not print it. Evidence tiers. Data-proven on two real bug reports (Samsung A-series 206 rows, Samsung S-series "
                 "444 rows), each equal to a count of lines in the raw text. As both are in a UTC+0 zone the conversion to UTC was "
                 "checked on constructed text for other zones. Not examined: other vendors and Android versions."
                 "\nOn the corpus the run gave s20fe_a13 12 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "shield",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 12 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_vendor_custom_state": {
        "name": "Bug Report - knoxcustom State",
        "description": "The manager settings of the knoxcustom dump of an Android bug report text, as manager, name and value "
                       "as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Vendor",
        "notes": "One row per line of the knoxcustom service dump of the form Manager:Name: value (the heading line is skipped). "
                 "Manager is the text before the first colon (for example SystemManager), Name and Value the rest as printed. A "
                 "line printed as Name is null gives Value null and a line printed as Name:value is split at the colon; "
                 "As Printed keeps the line. The list values (up to 2,000 characters) are not split. A row records a "
                 "setting the vendor service printed when the dump ran; the table does not say whether the setting was changed "
                 "by anyone, and a default value is not distinguishable from a configured one.\n"
                 "The section exists only on the two Samsung reports (Android 16); the others do not print it. Evidence tiers. "
                 "Data-proven on two real bug reports (106 rows each), each equal to a count of lines with a colon after the "
                 "heading in the raw text. The two reports do not print the same set of names. Not examined: "
                 "other vendors and Android versions."
                 "\nOn the corpus the run gave s20fe_a13 100 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 100 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_file_systems": {
        "name": "Bug Report - File Systems",
        "description": "The df output (FILESYSTEMS & FREE SPACE) of an Android bug report text, with the blocks, used, "
                       "available, use percentage and mount point of each file system as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Storage and Databases",
        "notes": "One row per line of the FILESYSTEMS & FREE SPACE (df) command section, after the header line. Filesystem, "
                 "1K-blocks, Used, Available, Use% and Mounted On are as printed (the counts are in 1K blocks as the header says; "
                 "a number larger than SQLite can hold is shown as printed text). The sizes are the state when the command ran. A "
                 "line that does not have the six columns is not read and is counted in the log of the run.\n"
                 "A row says how much space the file system reported when the report was made. It does not say what the space "
                 "holds, and a figure for a mount point that is a copy or an overlay of another is the figure the command printed.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 70, 78, 41, 15 and 55 rows, each equal to a count "
                 "of lines after the header in the raw text. Not examined: Android 11 and 12, other vendors."
                 "\nOn the corpus the run gave s20fe_a13 186 rows (62 from the dumpState text, 62 from an automatically generated dump, 62 from an automatically generated dump), samsungs20_a13 57 rows and sharon_a14 126 rows; userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "storage",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 186 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 57 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 126 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_file_system_inodes": {
        "name": "Bug Report - File System Inodes",
        "description": "The df -i output (FILESYSTEMS & FREE INODE) of an Android bug report text, with the inode counts and "
                       "mount point of each file system as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Storage and Databases",
        "notes": "One row per line of the FILESYSTEMS & FREE INODE (df -i) command section, after the header line. Inodes, IUsed, "
                 "IFree and IUse% are shown as printed text, because the platform prints 18446744073709551615 (the largest 64-bit "
                 "unsigned number) for file systems that do not count inodes, and the counts are not converted. A row says what the "
                 "command printed when the report was made.\n"
                 "Only the two Samsung reports (Android 16) have this section; the others print the df section only, so the table "
                 "is empty for them. Evidence tiers. Data-proven on two real bug reports (Samsung A-series 70 rows, Samsung S-series "
                 "78 rows), each equal to a count of lines after the header in the raw text and to the number of rows of Bug Report - "
                 "File Systems of the same report. Not examined: other vendors and Android versions."
                 "\nOn the corpus the run gave s20fe_a13 186 rows (62 from the dumpState text, 62 from an automatically generated dump, 62 from an automatically generated dump), samsungs20_a13 57 rows and sharon_a14 126 rows; userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "storage",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 186 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 57 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 126 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_mount_points": {
        "name": "Bug Report - Mount Points",
        "description": "The MOUNT POINT DUMP (mount) output of an Android bug report text, with the device, mount point, file "
                       "system type and options as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Storage and Databases",
        "notes": "One row per line of the MOUNT POINT DUMP (mount) command section of the form device on path type fs (options). "
                 "Device, Mount Point, FS Type and Options are as printed and the options (up to 1,000 characters) are not split or "
                 "decoded. A line of another shape is not read. A row says what the mount command printed when the report was "
                 "made.\n"
                 "Only the two Samsung reports (Android 16) have this section; the others do not print it, so the table is empty "
                 "for them. Evidence tiers. Data-proven on two real bug reports (Samsung A-series 164 rows, Samsung S-series 178 "
                 "rows), each equal to a count of lines containing ' on ' and ' type ' in the raw text. Not examined: other "
                 "vendors and Android versions."
                 "\nOn the corpus the run gave s20fe_a13 471 rows (157 from the dumpState text, 157 from an automatically generated dump, 157 from an automatically generated dump), samsungs20_a13 146 rows and sharon_a14 152 rows; userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "storage",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 471 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 146 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 152 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_storage_volumes": {
        "name": "Bug Report - Storage Volumes",
        "description": "The StorageVolumes, Volumes and Disks parts of the mount service dump of an Android bug report text, "
                       "with the id, state, paths and attributes of each as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Storage and Databases",
        "notes": "One row per StorageVolume: entry, per VolumeInfo{id} entry and per DiskInfo entry of the mount service dump. Kind "
                 "says which. ID is the id printed (emulated;0, for example). State, Path and Internal Path are mState or state, "
                 "mPath or path, mInternalPath or internalPath; Description, Primary, Removable and Emulated are the m-prefixed "
                 "fields of a StorageVolume entry; Mount Flags, Mount User ID, Disk ID, FS Type, FS UUID, FS Label and Volume Type "
                 "are the fields of a VolumeInfo entry (fields the entry does not print are empty); every other attribute is kept in "
                 "Other Attributes as name=value. The Records part (known volume records) is not read: it is empty in the tested "
                 "reports. A row says what the mount service listed when the dump ran. It lists the volumes mounted at that "
                 "time and does not list a card or drive that was connected earlier.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16: 2 rows each "
                 "(one StorageVolume and one Volume); Huawei, Transsion-brand and Motorola: 1 row each, the emulated Volume), "
                 "each equal to a count of entries in the raw text. Every tested volume was the emulated internal storage; an "
                 "external volume, a private volume and a Disk entry were not present and are constructed text only. Not "
                 "examined: Android 11 and 12, a device with an SD card."
                 "\nOn the corpus the run gave s20fe_a13 2 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "storage",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 2 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_vold_log": {
        "name": "Bug Report - Vold Log",
        "description": "The VOLD LAST LOG lines of the mount service dump of an Android bug report text, with the time, process "
                       "and thread ids, component and message as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Storage and Databases",
        "notes": "One row per line after a VOLD LAST LOG BUF#n line in the mount service dump. Buffer is the BUF heading. Time As "
                 "Printed is year/month/day-hour:minute:second followed by the label (GMT or UTC); Time (UTC) is that time read as UTC. PID, TID, "
                 "Component and Message are as printed. A line without a time (92 rows of the Samsung A-series report and 530 of the S-series report: "
                 "continuation lines of a message) is kept with an empty time and the text as Message. "
                 "The messages are the platform's own text (for example trim and garbage collection of file systems, "
                 "unmounting a volume) and a row records that vold logged the message; it does not say why.\n"
                 "The log is a ring of lines and its times span 26 days (Samsung A-series) and about three years and nine months "
                 "(Samsung S-series) as printed. The label after the time is (GMT) or (UTC) and both are read as UTC. Only the "
                 "two Samsung reports (Android 16) print it; the other three do not, so the table is empty for them. Evidence "
                 "tiers. Data-proven on two real bug reports (Samsung A-series 3,265 rows, Samsung S-series 5,663 rows), each "
                 "equal to a count of lines after the BUF heading in the raw text. Not examined: other vendors and Android "
                 "versions, a log with more than one BUF heading."
                 "\nOn the corpus the run gave s20fe_a13 566 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "storage",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 566 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_storage_io": {
        "name": "Bug Report - Storage IO Counters",
        "description": "The STORAGED IO INFO (storaged -u -p) output of an Android bug report text, with the counters of each "
                       "package or uid under the column names the section prints.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Storage and Databases",
        "notes": "One row per line of the STORAGED IO INFO (storaged -u -p) command section after its name/uid header. Name/UID is "
                 "as printed (a package name, a shared:... uid name or a number). The ten columns are named as the section's own "
                 "header names them (fg_rchar to bg_fsync) and are shown as printed numbers, not decoded or converted to "
                 "other units; a value larger than SQLite can hold is shown as printed text. A line that does not have ten numbers "
                 "after the name is not read. The counters accumulate for a period the dump does not state, so a row says nothing "
                 "about a time window, and a name that is not listed says nothing about whether it wrote.\n"
                 "The three lines headed I/O perf history that follow the table in the tested reports (last 24 hours, last 7 days, last 52 "
                 "weeks) are rows of Bug Report - Disk Statistics. The storaged service dump of the same reports (three of five) "
                 "prints numbers without column names and is not read.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 266, 275, 117, 86 and 224 rows, each equal to a "
                 "count of lines after the header in the raw text. Not examined: Android 11 and 12, other vendors."
                 "\nOn the corpus the run gave s20fe_a13 404 rows (152 from the dumpState text, 89 from an automatically generated dump, 163 from an automatically generated dump), samsungs20_a13 156 rows and sharon_a14 187 rows; userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "storage",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 404 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 156 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 187 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_disk_statistics": {
        "name": "Bug Report - Disk Statistics",
        "description": "The diskstats service dump and the scalar lines of the mount service dump of an Android bug report text "
                       "(free space, size totals, storage totals), as item and value as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Storage and Databases",
        "notes": "One row per line of the diskstats service dump other than the per-package lists (Latency, Recent Disk Write Speed, "
                 "the Data-Free, Cache-Free, System-Free and Metadata-Free lines, File-based Encryption and the App, App Data, App "
                 "Cache, Photos, Videos, Audio, Downloads, System and Other size lines), one row per I/O perf history line printed "
                 "under the storaged -u -p table (Source Section storaged -u -p; the numbers are the platform's, most recent "
                 "first, and no unit of time is printed for each), and one row per scalar line of the mount "
                 "service dump (Primary storage UUID, Internal storage total size, CE unlocked users, System unlocked users and the "
                 "sharing lines). Source Section says which dump. Item and Value are as printed (Value keeps the units, for example "
                 "18231280K / 868525705K total = 22% free); a line of the form name = number is split at the equals sign. The size "
                 "lines carry no unit in the dump and are shown as printed. The per-package lists are in Bug Report - Package Sizes. "
                 "A row says what the service printed when the dump ran.\n"
                 "The Internal storage total size line printed a MiB figure that is not consistent with its byte figure on the "
                 "Huawei and Transsion-brand reports (Android 10); both are shown as printed.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 25, 25, 21, 21 and 23 rows. Not examined: Android "
                 "11 and 12, other vendors."
                 "\nOn the corpus the run gave s20fe_a13 19 rows (14 from the dumpState text, 2 from an automatically generated dump, 3 from an automatically generated dump), samsungs20_a13 3 rows and sharon_a14 3 rows; userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "storage",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 19 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 3 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 3 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_package_sizes": {
        "name": "Bug Report - Package Sizes",
        "description": "The Package Names, App Sizes, App Data Sizes and Cache Sizes lists of the diskstats service dump of an "
                       "Android bug report text, joined by position, as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Storage and Databases",
        "notes": "One row per entry of the Package Names list of the diskstats service dump, joined by position with the same position "
                 "of the App Sizes, App Data Sizes and Cache Sizes lists. Index is the position (from 0). The sizes are the numbers "
                 "printed; the dump states no unit and no user. If the lists have different lengths the shortest is used and the "
                 "run's log says so; a list cut by the 65,536-character line limit gives its complete items and the log says so. "
                 "A package that is not listed says nothing about whether it is installed.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 495, 629, 292, 240 and 587 rows, each equal to the "
                 "number of names in the raw list and to the length of each size list. Not examined: Android 11 and 12, other "
                 "vendors, a device with a list longer than the line limit."
                 "\nOn the corpus none of s20fe_a13, samsungs20_a13, sharon_a14 and userb2_a13 gave a row; the diskstats dump of s20fe_a13 prints no package sizes.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "storage",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_open_databases": {
        "name": "Bug Report - Open Databases",
        "description": "The Connection pool entries of the dbinfo service dump of an Android bug report text, with the process, "
                       "database path, configuration and statement counters as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Storage and Databases",
        "notes": "One row per Connection pool for <path> entry of the dbinfo service dump, under the ** Database info for pid N "
                 "[process] ** heading it follows. Open, Max Connections, Total Execution Time (the number printed, in ms on the "
                 "newer layout and with no unit on the Android 10 layout), Total Statements, Average Time Per Statement, "
                 "Configuration, Read Only and Secure are as printed; WAL is yes where the entry prints Use WAL mode; Connections "
                 "and Operations Listed are counts made from the entry (connections listed and operation lines read); a line the "
                 "reader does not know is kept in Other. A row says that the process had the database open with that pool when the "
                 "dump ran. The dump is a snapshot of the processes running at that time, so a database that is not listed says "
                 "nothing about whether it exists or was used.\n"
                 "The dbinfo dump of the Samsung S-series report was cut by the platform's 10,000 ms limit, so its rows may be "
                 "partial; this is written to the log of the run. Evidence tiers. Data-proven on five real bug reports (Samsung "
                 "A-series 210 rows and S-series 64 rows on Android 16, Huawei 219 and Transsion-brand 151 on Android 10, Motorola "
                 "211 on Android 15), each equal to a count of Connection pool for lines in the raw text. Not examined: Android "
                 "11 and 12, other vendors."
                 "\nOn the corpus the run gave s20fe_a13 161 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "database",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 161 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_database_files": {
        "name": "Bug Report - Database Files",
        "description": "The Database files in <directory> listings of the dbinfo service dump of an Android bug report text, with "
                       "the size and the ctime, mtime and atime of each file as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Storage and Databases",
        "notes": "One row per file line of a Database files in <directory>: listing of the dbinfo service dump. Process and PID come from "
                 "the ** Database info for pid N [process] ** heading above the listing. Directory is the path printed, File Name and "
                 "Size (bytes) are as printed (the size is the number before the b). ctime, mtime and atime are the three times the "
                 "line prints, as ISO text ending in Z; each (UTC) column reads that text as UTC. The listing names, sizes and "
                 "times only; the file contents are not in a bug report. The platform's ctime is the inode change time, not a "
                 "creation time. A time of 1970-01-01 is shown as printed. A row records what the listing printed for a file when "
                 "the dump ran, for the processes that were running; a file that is not listed says nothing about whether it "
                 "exists.\n"
                 "The dbinfo dump of the Samsung S-series report was cut by the platform's 10,000 ms limit, so its listings may be "
                 "partial; this is written to the log of the run. The Huawei report (Android 10) prints no file listing. "
                 "Evidence tiers. Data-proven on four of five real bug reports (Samsung A-series 1,120 rows and S-series 373 rows "
                 "on Android 16, Transsion-brand 543 on Android 10, Motorola 1,614 on Android 15), each equal to a count of file "
                 "lines in the raw text. Not examined: Android 11 and 12, other vendors."
                 "\nOn the corpus the run gave s20fe_a13 628 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "database",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 628 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_database_operations": {
        "name": "Bug Report - Database Operations",
        "description": "The Most recently executed operations of the connections in the dbinfo service dump of an Android bug "
                       "report text, with the time, operation, duration, status and SQL text as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Storage and Databases",
        "notes": "One row per numbered operation line under Most recently executed operations: of a connection in the dbinfo service "
                 "dump. Process, PID and Database Path come from the headings above it; Connection is the connection number and "
                 "Index the number before the time. Operation is the first word (for example prepare, execute, "
                 "executeForCursorWindow, open), Took (ms) and Status are the values printed, SQL is the text between sql=\" and the "
                 "closing quote before path= (up to 2,000 characters, with SQL Length the full length) and Details is any text "
                 "after it. A line the reader cannot split keeps its text in Details. The SQL text is shown exactly as the "
                 "platform printed it: it can contain values the application used in a statement.\n"
                 "Time As Printed is month, day and clock time without a year (the Android 14 and later reports) or a full date and "
                 "time (the Android 10 and 15 reports). Time (UTC) converts it with the zone shown in Bug Report - Device Facts; for "
                 "a time without a year it uses the latest year, the one of the report or the one before, that does not put the time "
                 "more than a day after the report time (the rule of Bug Report - Settings Changes), and it is empty with a Time Note "
                 "where the report has no time or zone. Each connection lists a bounded number of operations (a median of 7 to 20 and at most 108 in the tested reports), "
                 "so the list covers a short window and says nothing about statements outside it; a row records that the "
                 "process executed the statement, not why. List says which list the line is in: the Most recently executed "
                 "operations or the Operations exceeding 2000ms (36 rows of the Samsung A-series report).\n"
                 "The dbinfo dump of the Samsung S-series report was cut by the platform's 10,000 ms limit, so its rows may be "
                 "partial; this is written to the log of the run. Evidence tiers. Data-proven on five real bug reports (Samsung "
                 "A-series 8,564 rows and S-series 3,586 rows on Android 16, Huawei 5,060 and Transsion-brand 3,415 on Android 10, "
                 "Motorola 5,955 on Android 15), each equal to a count of numbered operation lines in the raw text. As the tested "
                 "reports are in a UTC+0 zone the conversion to UTC was checked on constructed text for other zones. Not "
                 "examined: Android 11 and 12, other vendors, an operation line with a stack trace or exception text."
                 "\nOn the corpus the run gave s20fe_a13 4,033 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "database",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 4,033 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_device_config": {
        "name": "Bug Report - Device Config Flags",
        "description": "The DeviceConfig flags of the device_config service dump of an Android bug report text, with the "
                       "namespace, flag name and value as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Settings and Config",
        "notes": "One row per namespace/flag=value line after the DeviceConfig flags: heading of the device_config service dump. A "
                 "value that continues on the following lines is joined with one space (up to 1,000 characters). Namespace, Flag and "
                 "Value are as printed. These are feature flags that the platform and its servers set, and they are present on "
                 "a device whether or not anyone used the feature: a row records the value the device configuration service "
                 "held when the dump ran, not an action on the device, and the table is a reference for the device state, not "
                 "user activity. The flag names and values are not interpreted here.\n"
                 "The Huawei and Transsion-brand reports (Android 10) print an empty dump, so the table is empty for them. Evidence "
                 "tiers. Data-proven on three of five real bug reports (Samsung A-series 4,633 rows and S-series 4,842 rows on "
                 "Android 16, Motorola 4,005 rows on Android 15), each equal to a count of namespace/flag= lines in the raw text. "
                 "Not examined: Android 11, 12 and 14 other than the Android 15 report, other vendors."
                 "\nOn the corpus none of s20fe_a13, samsungs20_a13, sharon_a14 and userb2_a13 gave a row; the device_config dump of s20fe_a13 prints only its service header lines.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_platform_compat": {
        "name": "Bug Report - Platform Compat Changes",
        "description": "The ChangeId lines of the platform_compat service dump of an Android bug report text, with the id, name "
                       "and the enable and flag words as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Settings and Config",
        "notes": "One row per ChangeId(id; name=...; ...) line of the platform_compat service dump. Enable Since Target SDK and "
                 "Enable After Target SDK are the numbers printed after enableSinceTargetSdk= and enableAfterTargetSdk=; Disabled, "
                 "Logging Only and Overridable are yes where the line prints the word disabled, loggingOnly or overridable; any other "
                 "word is kept in Other. The rows list the compatibility changes the platform defines for this build, not changes "
                 "applied to any app, and are a reference for the build. The platform_compat_native dump is empty in the tested "
                 "reports and is not read.\n"
                 "The Huawei and Transsion-brand reports (Android 10) do not print the dump, so the table is empty for them. Evidence "
                 "tiers. Data-proven on three of five real bug reports (Samsung A-series 354 rows and S-series 357 rows on Android "
                 "16, Motorola 326 rows on Android 15), each equal to a count of ChangeId( lines in the raw text. Not examined: other "
                 "Android versions and vendors."
                 "\nOn the corpus the run gave s20fe_a13 173 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 173 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_build_release_flags": {
        "name": "Bug Report - Build Release Flags",
        "description": "The BUILD-TIME RELEASE FLAGS sections (build_flags.json of the system, system_ext, product and vendor "
                       "partitions) of an Android bug report text, with the flag name, namespace, description and values as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Device and Build",
        "notes": "One row per flag of the flags (or flag_artifacts) list of each build_flags.json text printed in a SYSTEM, SYSTEM_EXT, "
                 "PRODUCT or VENDOR BUILD-TIME RELEASE FLAGS section. Partition comes from the section name. Flag Name, Namespace, "
                 "Description (up to 500 characters), Workflow and Containers are the declaration's fields as printed. Declared Value "
                 "Type and Declared Value are the declaration's default (the key of its Val, for example BoolValue, and its value); "
                 "Value Type and Value are the value the file sets, empty where the file sets none. A row lists what the build file "
                 "contained; it does not say that the flag was in effect on the device or that a feature was used. The file time "
                 "printed in the section heading is not read.\n"
                 "The text is parsed as JSON after the section ends; a section that is not complete JSON is not read and the log says "
                 "so. The Huawei and Transsion-brand reports (Android 10) have no such section. The vendor partition section exists on "
                 "the Samsung A-series report only. Evidence tiers. Data-proven on three of five real bug reports (Samsung A-series "
                 "641 rows and S-series 686 rows on Android 16, Motorola 261 rows on Android 15), each equal to a count of "
                 "flag_declaration objects in the raw text. Not examined: other Android versions and vendors."
                 "\nOn the corpus none of s20fe_a13, samsungs20_a13, sharon_a14 and userb2_a13 gave a row; s20fe_a13 prints no release flag section.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_sdk_extensions": {
        "name": "Bug Report - SDK Extensions",
        "description": "The SDK EXTENSIONS (derive_sdk --dump) section of an Android bug report text, with the extension "
                       "properties, module versions and version requirements as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Device and Build",
        "notes": "One row per indented line of the SDK EXTENSIONS command section. Group is the heading line (system properties, apex "
                 "module versions, last 3 version requirements) and Name and Value are the text before and after the first colon "
                 "(for example build.version.extensions.t and 23; <not set> is shown as printed). A row says what the extension "
                 "tool printed for the build when the report was made.\n"
                 "The Huawei and Transsion-brand reports (Android 10) have no such section. The SDK extensions line of the report "
                 "header is a row of Bug Report - Device Facts. Evidence tiers. Data-proven on three of five real bug reports "
                 "(30 rows each: Samsung A-series and S-series on Android 16, Motorola on Android 15), each equal to a count of "
                 "indented lines in the raw text. Not examined: other Android versions and vendors."
                 "\nOn the corpus none of s20fe_a13, samsungs20_a13, sharon_a14 and userb2_a13 gave a row; s20fe_a13 prints no SDK extensions section.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
}

import re
from datetime import timezone

from scripts import dumpstate_reader
from scripts import dumpstate_securitystorage as storage_reader
from scripts.ilapfuncs import artifact_processor, logfunc

_TIME_WITH_SUFFIX = re.compile(r'^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d \([^()\s]*\)$')
NOTE_NO_YEAR = ('no UTC value: the report has no time, or the text is not a month, day and clock time')


def _reports(context):
    """The bug report texts among the staged files, as (Source File label, Report) pairs."""
    return dumpstate_reader.load_reports(context.get_files_found(), context.get_relative_path, logfunc)


def _source_path(context, reports):
    """The staged files that were read; the matched files when none was a bug report."""
    paths = [report.source.path for _label, report in reports] or sorted(str(path) for path in context.get_files_found())
    return '\n'.join(dict.fromkeys(str(path) for path in paths))


def _log_cuts(label, report, service, lines):
    """Say so when the platform cut a dump of ``service`` that holds the rows (or when it cut one and there are no rows)."""
    cut = [section for section in report.sections if section.kind == 'service' and section.name == service and section.timeout_ms]
    if lines:
        cut = [section for section in cut if any(section.line < number < section.end_line for number in lines)]
    if cut:
        dumpstate_reader.say_once(logfunc, f'Bug report {label}: the {service} service dump was cut by a {cut[0].timeout_ms} ms '
                                           f'timeout, the rows from it may be partial')


def _collect(context, table, services, make_row):
    """The rows of one reader table of every report: ``make_row(report, item, label)`` builds each row."""
    rows = []
    reports = _reports(context)
    for label, report in reports:
        items = getattr(report, table, [])
        for service in services:
            _log_cuts(label, report, service, [item.line for item in items])
        rows.extend(make_row(report, item, label) for item in items)
    return rows, _source_path(context, reports)


def wall_time(report, text):
    """``(UTC datetime or None, note)`` for a device wall-clock time printed in the report."""
    value = str(text).strip()
    if not value:
        return None, ''
    if value in dumpstate_reader.UNSET_WALL_TIMES:
        return None, dumpstate_reader.NOTE_UNSET
    if dumpstate_reader.parse_wall_time(value) is None:
        return None, dumpstate_reader.NOTE_NOT_A_TIME
    if not report.clock.known:
        return None, dumpstate_reader.NOTE_NO_ZONE
    moment = report.clock.to_utc(value)
    return moment, '' if moment else dumpstate_reader.NOTE_NONEXISTENT


def no_year_time(report, text):
    """``(UTC datetime or None, note)`` for a time printed as ``MM-DD HH:MM:SS.mmm`` (the year is derived, see the notes)."""
    full, moment = report.setting_change_time(str(text).strip())
    if not full:
        return None, NOTE_NO_YEAR
    if moment is None:
        return None, dumpstate_reader.NOTE_NO_ZONE
    return moment, ''


def _printed_time(text):
    """The ``YYYY-MM-DD HH:MM:SS`` part of a time printed with a bracketed word after it, as ``... (0)``; other text unchanged."""
    value = str(text).strip()
    return value[:19] if _TIME_WITH_SUFFIX.match(value) else value


def either_time(report, text):
    """A time with a year as ``YYYY-MM-DD ...`` or without one as ``MM-DD ...``."""
    value = str(text).strip()
    if len(value) > 5 and value[4:5] == '-' and value[:4].isdigit():
        return wall_time(report, value)
    return no_year_time(report, value) if value else (None, '')


def iso_utc(text):
    """UTC datetime for ``2026-04-27T15:30:05.259227Z`` text, or None."""
    return storage_reader.utc_from_iso(text)


def gmt_time(text):
    """UTC datetime for the vold log time ``2026/10/04-03:07:02(GMT)`` (the label is GMT or UTC), or None."""
    value = str(text).strip()[:19]
    if len(value) != 19:
        return None
    moment = dumpstate_reader.parse_wall_time(value[:10].replace('/', '-') + ' ' + value[11:])
    return moment.replace(tzinfo=timezone.utc) if moment is not None else None


# ---------------------------------------------------------------------------------------------
# device policy
# ---------------------------------------------------------------------------------------------
@artifact_processor
def bugreport_device_policy_admins(context):
    headers = ('User', 'Provisioning State', 'Admin Component', 'Package', 'UID', 'Test Only', 'Declared Policies',
               'Password Quality (as stored)', 'Minimum Password Length', 'Max Failed Passwords For Wipe',
               'Encryption Requested', 'Disabled Keyguard Features (as stored)', 'Network Logging', 'VPN Package',
               'VPN Lockdown', 'Is Parent', 'Common Criteria Mode', 'Source Dir', 'Source Line', 'Source File')
    rows, source = _collect(context, 'ss_dp_admins', ('device_policy',), lambda _r, i, label: (
        i.user, i.provisioning, i.component, i.package, i.uid, i.test_only, i.policies, i.password_quality, i.min_length,
        i.wipe_after, i.encryption_requested, i.keyguard_disabled, i.network_logging, i.vpn_package, i.vpn_lockdown,
        i.is_parent, i.common_criteria, i.source_dir, i.line, label))
    return headers, rows, source


@artifact_processor
def bugreport_device_policy_state(context):
    headers = ('Group', 'User', 'Name', 'Value', 'Source Line', 'Source File')
    rows, source = _collect(context, 'ss_dp_state', ('device_policy',), lambda _r, i, label: (
        i.group, i.user, i.name, i.value, i.line, label))
    return headers, rows, source


@artifact_processor
def bugreport_device_policies(context):
    headers = ('Scope', 'User', 'Policy Key', 'Admin Package', 'Admin Authorities', 'Admin Value', 'Resolved Mechanism',
               'Resolved Value', 'Source Line', 'Source File')
    rows, source = _collect(context, 'ss_dp_policies', ('device_policy',), lambda _r, i, label: (
        i.scope, i.user, i.key, i.package, i.authorities, i.admin_value, i.mechanism, i.resolved_value, i.line, label))
    return headers, rows, source


# ---------------------------------------------------------------------------------------------
# lock settings
# ---------------------------------------------------------------------------------------------
@artifact_processor
def bugreport_lock_settings_users(context):
    headers = (('Last Changed (UTC)', 'datetime'), 'Last Changed As Printed', 'Time Note', 'User', 'Protector ID',
               'Previous Protector', 'Backup Protector', 'SI Checker', 'Secure Mode (as stored)', 'SID', 'Quality (as stored)',
               'Credential Type', 'Separate Challenge', 'Metrics', 'Failed Attempts', 'SP Handle', 'Other', 'Source Line',
               'Source File')

    def make(report, item, label):
        moment, note = wall_time(report, _printed_time(item.changed_text))
        return (moment, item.changed_text, note, item.user, item.protector_id, item.previous_protector, item.backup_protector,
                item.si_checker, item.secure_mode, item.sid, item.quality, item.credential_type, item.separate_challenge,
                item.metrics, item.failed_attempts, item.sp_handle, item.other, item.line, label)
    rows, source = _collect(context, 'ss_lock_users', ('lock_settings',), make)
    return headers, rows, source


@artifact_processor
def bugreport_lock_settings_files(context):
    headers = (('Modified (UTC)', 'datetime'), 'Modified As Printed', 'Time Note', 'Location', 'Directory', 'Size (bytes)',
               'File Name', 'Source Line', 'Source File')

    def make(report, item, label):
        moment, note = wall_time(report, item.mtime_text)
        return moment, item.mtime_text, note, item.location, item.directory, item.size, item.name, item.line, label
    rows, source = _collect(context, 'ss_lock_files', ('lock_settings',), make)
    return headers, rows, source


@artifact_processor
def bugreport_lock_settings_state(context):
    headers = ('Group', 'User', 'Name', 'Value', 'Source Line', 'Source File')
    rows, source = _collect(context, 'ss_lock_state', ('lock_settings',), lambda _r, i, label: (
        i.group, i.user, i.name, i.value, i.line, label))
    return headers, rows, source


@artifact_processor
def bugreport_lock_settings_log(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Time Note', 'State', 'Message', 'Detail', 'Stack Frames',
               'Source Line', 'Source File')

    def make(report, item, label):
        moment, note = either_time(report, item.time_text)
        return moment, item.time_text, note, item.state, item.message, item.detail, item.frames, item.line, label
    rows, source = _collect(context, 'ss_lock_log', ('lock_settings',), make)
    return headers, rows, source


# ---------------------------------------------------------------------------------------------
# biometrics and trust
# ---------------------------------------------------------------------------------------------
@artifact_processor
def bugreport_biometric_statistics(context):
    headers = ('Service', 'Sensor ID', 'Provider', 'Provider Service', 'ID (as printed)', 'Count', 'Accept', 'Reject',
               'Quality', 'Acquire', 'Lockout', 'Permanent Lockout', 'Accept (Crypto)', 'Reject (Crypto)', 'Quality (Crypto)',
               'Acquire (Crypto)', 'Lockout (Crypto)', 'Permanent Lockout (Crypto)', 'HAL Deaths', 'Other Counters',
               'Source Line', 'Source File')

    def make(_report, item, label):
        counters = item.counters
        return (item.service, item.sensor_id, item.provider, item.provider_service, item.print_id, counters.get('count'),
                counters.get('accept'), counters.get('reject'), counters.get('quality'), counters.get('acquire'),
                counters.get('lockout'), counters.get('permanentLockout'), counters.get('acceptCrypto'),
                counters.get('rejectCrypto'), counters.get('qualityCrypto'), counters.get('acquireCrypto'),
                counters.get('lockoutCrypto'), counters.get('permanentLockoutCrypto'), item.hal_deaths,
                counters.get('other', ''), item.line, label)
    rows, source = _collect(context, 'ss_bio_stats', ('fingerprint', 'face'), make)
    return headers, rows, source


@artifact_processor
def bugreport_biometric_sensors(context):
    headers = ('Sensor ID', 'OEM Strength (as stored)', 'Updated Strength (as stored)', 'Modality (as stored)',
               'State (as stored)', 'Cookie', 'Source Line', 'Source File')
    rows, source = _collect(context, 'ss_bio_sensors', ('biometric',), lambda _r, i, label: (
        i.sensor_id, i.oem_strength, i.updated_strength, i.modality, i.state, i.cookie, i.line, label))
    return headers, rows, source


@artifact_processor
def bugreport_biometric_events(context):
    headers = ('Service', 'Sequence', 'Event', 'User', 'Sensor ID', 'Request ID', 'Biometric Strength (as stored)',
               'Was Successful', 'As Printed', 'Source Line', 'Source File')
    rows, source = _collect(context, 'ss_bio_events', ('fingerprint', 'face'), lambda _r, i, label: (
        i.service, i.sequence, i.event, i.user, i.sensor_id, i.request_id, i.strength, i.successful, i.text, i.line, label))
    return headers, rows, source


@artifact_processor
def bugreport_trust_agents(context):
    headers = ('User ID', 'User Name', 'Flags (as stored)', 'Qualifiers', 'Trust State', 'Trusted', 'Trust Managed',
               'Device Locked', 'Active Unlock Running', 'Strong Auth Required', 'Note', 'Agent', 'Bound', 'Connected',
               'Managing Trust', 'Agent Trusted', 'Source Line', 'Source File')
    rows, source = _collect(context, 'ss_trust_agents', ('trust',), lambda _r, i, label: (
        i.user_id, i.user_name, i.flags, i.qualifiers, i.trust_state, i.trusted, i.trust_managed, i.device_locked,
        i.active_unlock, i.strong_auth, i.note, i.agent, i.bound, i.connected, i.managing, i.agent_trusted, i.line, label))
    return headers, rows, source


@artifact_processor
def bugreport_trust_events(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Time Note', 'User ID', 'User Name', 'Sequence', 'Event',
               'Detail', 'Source Line', 'Source File')

    def make(report, item, label):
        moment, note = no_year_time(report, item.time_text)
        return moment, item.time_text, note, item.user_id, item.user_name, item.sequence, item.event, item.detail, item.line, label
    rows, source = _collect(context, 'ss_trust_events', ('trust',), make)
    return headers, rows, source


@artifact_processor
def bugreport_adb_state(context):
    headers = ('Path', 'Value', 'Source Line', 'Source File')
    rows, source = _collect(context, 'ss_adb', ('adb',), lambda _r, i, label: (i.path, i.value, i.line, label))
    return headers, rows, source


# ---------------------------------------------------------------------------------------------
# vendor security services
# ---------------------------------------------------------------------------------------------
@artifact_processor
def bugreport_vendor_guard_log(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Time Note', 'Kind', 'Tag', 'Message', 'Source Line',
               'Source File')

    def make(report, item, label):
        moment, note = wall_time(report, item.time_text)
        return moment, item.time_text, note, item.kind, item.tag, item.message, item.line, label
    rows, source = _collect(context, 'ss_knox_log', ('knoxguard_service',), make)
    return headers, rows, source


@artifact_processor
def bugreport_vendor_custom_state(context):
    headers = ('Manager', 'Name', 'Value', 'As Printed', 'Source Line', 'Source File')
    rows, source = _collect(context, 'ss_knox_custom', ('knoxcustom',), lambda _r, i, label: (
        i.manager, i.name, i.value, i.text, i.line, label))
    return headers, rows, source


# ---------------------------------------------------------------------------------------------
# storage
# ---------------------------------------------------------------------------------------------
@artifact_processor
def bugreport_file_systems(context):
    headers = ('Filesystem', '1K-blocks', 'Used', 'Available', 'Use%', 'Mounted On', 'Source Line', 'Source File')
    rows, source = _collect(context, 'ss_df', (), lambda _r, i, label: (
        i.filesystem, i.blocks, i.used, i.available, i.use_percent, i.mount, i.line, label))
    return headers, rows, source


@artifact_processor
def bugreport_file_system_inodes(context):
    headers = ('Filesystem', 'Inodes', 'IUsed', 'IFree', 'IUse%', 'Mounted On', 'Source Line', 'Source File')
    rows, source = _collect(context, 'ss_df_inodes', (), lambda _r, i, label: (
        i.filesystem, i.inodes, i.used, i.free, i.use_percent, i.mount, i.line, label))
    return headers, rows, source


@artifact_processor
def bugreport_mount_points(context):
    headers = ('Device', 'Mount Point', 'FS Type', 'Options', 'Source Line', 'Source File')
    rows, source = _collect(context, 'ss_mounts', (), lambda _r, i, label: (
        i.device, i.mount_point, i.fs_type, i.options, i.line, label))
    return headers, rows, source


@artifact_processor
def bugreport_storage_volumes(context):
    headers = ('Kind', 'ID', 'State', 'Path', 'Internal Path', 'Description', 'Primary', 'Removable', 'Emulated',
               'Mount Flags', 'Mount User ID', 'Disk ID', 'FS Type', 'FS UUID', 'FS Label', 'Volume Type',
               'Other Attributes', 'Source Line', 'Source File')
    rows, source = _collect(context, 'ss_volumes', ('mount',), lambda _r, i, label: (
        i.kind, i.volume_id, i.state, i.path, i.internal_path, i.description, i.primary, i.removable, i.emulated,
        i.mount_flags, i.mount_user, i.disk_id, i.fs_type, i.fs_uuid, i.fs_label, i.volume_type, i.other, i.line, label))
    return headers, rows, source


@artifact_processor
def bugreport_vold_log(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'PID', 'TID', 'Component', 'Message', 'Buffer', 'Source Line',
               'Source File')
    rows, source = _collect(context, 'ss_vold', ('mount',), lambda _r, i, label: (
        gmt_time(i.time_text), i.time_text, i.pid, i.tid, i.component, i.message, i.buffer, i.line, label))
    return headers, rows, source


@artifact_processor
def bugreport_storage_io(context):
    headers = ('Name/UID', 'fg_rchar', 'fg_wchar', 'fg_rbytes', 'fg_wbytes', 'bg_rchar', 'bg_wchar', 'bg_rbytes',
               'bg_wbytes', 'fg_fsync', 'bg_fsync', 'Source Line', 'Source File')
    rows, source = _collect(context, 'ss_storage_io', (), lambda _r, i, label: (i.name, *i.values, i.line, label))
    return headers, rows, source


@artifact_processor
def bugreport_disk_statistics(context):
    headers = ('Source Section', 'Item', 'Value', 'Source Line', 'Source File')
    rows, source = _collect(context, 'ss_disk_items', ('diskstats', 'mount'), lambda _r, i, label: (
        i.section, i.item, i.value, i.line, label))
    return headers, rows, source


@artifact_processor
def bugreport_package_sizes(context):
    headers = ('Index', 'Package', 'App Size (as printed)', 'App Data Size (as printed)', 'Cache Size (as printed)',
               'Source Line', 'Source File')
    rows, source = _collect(context, 'ss_package_sizes', ('diskstats',), lambda _r, i, label: (
        i.index, i.package, i.app_size, i.data_size, i.cache_size, i.line, label))
    return headers, rows, source


# ---------------------------------------------------------------------------------------------
# open databases
# ---------------------------------------------------------------------------------------------
@artifact_processor
def bugreport_open_databases(context):
    headers = ('Process', 'PID', 'Database Path', 'Open', 'Max Connections', 'Total Execution Time (as printed)',
               'Total Statements', 'Average Time Per Statement', 'Configuration', 'Read Only', 'Secure', 'WAL',
               'Connections', 'Operations Listed', 'Other', 'Source Line', 'Source File')
    rows, source = _collect(context, 'ss_db_pools', ('dbinfo',), lambda _r, i, label: (
        i.process, i.pid, i.path, i.open, i.max_connections, i.total_time, i.total_statements, i.average_time,
        i.configuration, i.read_only, i.secure, i.wal, i.connections, i.operations, i.other, i.line, label))
    return headers, rows, source


@artifact_processor
def bugreport_database_files(context):
    headers = (('mtime (UTC)', 'datetime'), 'mtime As Printed', ('ctime (UTC)', 'datetime'), 'ctime As Printed',
               ('atime (UTC)', 'datetime'), 'atime As Printed', 'Process', 'PID', 'Directory', 'File Name', 'Size (bytes)',
               'Source Line', 'Source File')
    rows, source = _collect(context, 'ss_db_files', ('dbinfo',), lambda _r, i, label: (
        iso_utc(i.mtime), i.mtime, iso_utc(i.ctime), i.ctime, iso_utc(i.atime), i.atime, i.process, i.pid, i.directory,
        i.name, i.size, i.line, label))
    return headers, rows, source


@artifact_processor
def bugreport_database_operations(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Time Note', 'Process', 'PID', 'Database Path', 'Connection',
               'List', 'Index', 'Operation', 'Took (ms)', 'Status', 'SQL', 'SQL Length', 'Details', 'Source Line', 'Source File')

    def make(report, item, label):
        moment, note = either_time(report, item.time_text)
        return (moment, item.time_text, note, item.process, item.pid, item.path, item.connection, item.listing, item.index,
                item.operation, item.took_ms, item.status, item.sql, item.sql_length, item.details, item.line, label)
    rows, source = _collect(context, 'ss_db_ops', ('dbinfo',), make)
    return headers, rows, source


# ---------------------------------------------------------------------------------------------
# configuration and build flags
# ---------------------------------------------------------------------------------------------
@artifact_processor
def bugreport_device_config(context):
    headers = ('Namespace', 'Flag', 'Value', 'Source Line', 'Source File')
    rows, source = _collect(context, 'ss_device_config', ('device_config',), lambda _r, i, label: (
        i.namespace, i.flag, i.value, i.line, label))
    return headers, rows, source


@artifact_processor
def bugreport_platform_compat(context):
    headers = ('Change ID', 'Name', 'Enable Since Target SDK', 'Enable After Target SDK', 'Disabled', 'Logging Only',
               'Overridable', 'Other', 'Source Line', 'Source File')
    rows, source = _collect(context, 'ss_compat', ('platform_compat',), lambda _r, i, label: (
        i.change_id, i.name, i.since_sdk, i.after_sdk, i.disabled, i.logging_only, i.overridable, i.other, i.line, label))
    return headers, rows, source


@artifact_processor
def bugreport_build_release_flags(context):
    headers = ('Partition', 'Flag Name', 'Namespace', 'Description', 'Declared Value Type', 'Declared Value', 'Value Type',
               'Value', 'Workflow', 'Containers', 'Source File')
    rows, source = _collect(context, 'ss_release_flags', (), lambda _r, i, label: (
        i.partition, i.name, i.namespace, i.description, i.declared_type, i.declared_value, i.value_type, i.value,
        i.workflow, i.containers, label))
    return headers, rows, source


@artifact_processor
def bugreport_sdk_extensions(context):
    headers = ('Group', 'Name', 'Value', 'Source Line', 'Source File')
    rows, source = _collect(context, 'ss_sdk', (), lambda _r, i, label: (i.group, i.name, i.value, i.line, label))
    return headers, rows, source
