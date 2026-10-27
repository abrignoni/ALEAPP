__artifacts_v2__ = {
    "bugreport_wifi_saved_networks": {
        "name": "Bug Report - Wi-Fi Saved Networks",
        "description": "The Configured networks entries of the wifi service dump in an Android bug report text, with the SSID, "
                       "selection status, security, creation and update times and the creator fields as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Wi-Fi",
        "notes": "One row per entry of the WifiConfigManager - Configured networks block in the wifi service dump. The ConfigurationMap "
                 "block that follows it holds the same networks again and is not read. Entry Mark is the text printed before ID: "
                 "(an asterisk or - DSBLE; empty where nothing is printed). SSID and BSSID are as printed: with quote marks, in the "
                 "shortened or masked form some builds print, or as the platform wrote them. The other columns are the fields of the "
                 "entry as printed: Selection Status and Disable Reason (NetworkSelectionStatus and mNetworkSelectionDisableReason), "
                 "Has Ever Connected, Associations (numAssociation), Key Management and Protocols (the KeyMgmt and Protocols line of "
                 "the entry), MAC Randomization Setting and Randomized MAC, Creator UID and Creator Name, Last Update UID and Last "
                 "Update Name, Last Connect UID (the cuid, cname, luid, lname and lcuid values), Most Recently Connected, Reboots "
                 "Since Last Use, Recent Failure, and Connect Choice (the network name and signal some builds print after connect "
                 "choice). The column names expand the short names the dump prints; the expansion follows the platform's "
                 "WifiConfiguration text and was not checked against a second source here, and the values are not decoded "
                 "further. A row records that the Wi-Fi service held a configuration for that network when the dump ran; it does "
                 "not say who added it or that the device joined it, and a network that is not listed says nothing about earlier "
                 "use.\n"
                 "Creation Time and Update Time are printed (Android 10 reports only, on the entries that carry them) as month, day "
                 "and clock time without a year, device wall-clock time. The year is not in the dump: Time (UTC) uses the latest "
                 "year, the one of the report or the one before, that does not put the time more than a day after the report time, "
                 "and then converts with the zone shown in Bug Report - Device Facts; a time more than a year before the report "
                 "would be given a year too late. Time (UTC) is empty where the time is missing, where no year or zone is known, "
                 "and for a time before 2009. The Android 16 and Android 15 reports tested print neither time, so Creation Time (UTC), Creation Time As Printed, "
                 "Update Time (UTC) and Update Time As Printed are empty on their rows, which says nothing about the device.\n"
                 "BSSID, FQDN and PROVIDER-NAME printed null on every entry of the five tested reports (FQDN and provider name are "
                 "not columns), so BSSID (as printed) held the text null on all rows. Protocols held the text WPA RSN on all rows and Recent "
                 "Failure held one text per report, Association Rejection code: 0 (with last update time: 0 on the Android 16 and "
                 "Android 15 reports), on all rows of every tested report. Not as a statement about a person, the User Selected column is the dump's own key for the flag printed right after "
                 "Currently Connected, and it held false on all rows of the Samsung and Motorola reports; Carrier ID and Subscription ID held -1 on all rows of those three reports. Those two and "
                 "Currently Connected, Reboots Since Last Use and Most Recently Connected are empty on the two Android 10 reports, "
                 "whose builds do not print them (Randomized MAC is empty on the Huawei report only). The mark - DSBLE stood on 8 "
                 "entries of the three reports that print it and each of them had the selection status "
                 "NETWORK_SELECTION_PERMANENTLY_DISABLED; the asterisk stood on 2 entries with NETWORK_SELECTION_ENABLED. Key Management and the other fields are shown for the "
                 "first KeyMgmt line of each entry only, not for the upgraded security parameter sets listed after it. "
                 "On the tested reports these columns held one value on all rows of a report: Auto Join (true on four "
                 "reports, empty on the Huawei one), Hidden (false on four), PMF (false on four), Has Ever Connected "
                 "(true on the Samsung A-series, Huawei and Transsion-brand reports), Key Management (WPA_PSK on the "
                 "Samsung A-series and Huawei reports), MAC Randomization Setting (3 on the two Samsung reports, 1 on "
                 "the Huawei and Transsion-brand ones), Creator UID (1000 on four reports), Creator Name "
                 "(android.uid.system:1000 on four), Last Update UID (1000 on four), Last Update Name (the same text "
                 "on three), Last Connect UID (1000 on the Huawei, Transsion-brand and Motorola reports) and Selection "
                 "Status (NETWORK_SELECTION_ENABLED on the Huawei and Transsion-brand reports). Connect Choice is "
                 "empty on four reports and printed on 5 entries of the Motorola one, Associations is empty on the "
                 "Samsung S-series report, and Entry Mark, that flag, Disable Reason, Carrier ID and Subscription "
                 "ID are empty on the Huawei and Transsion-brand reports. Currently Connected and Most Recently "
                 "Connected are identical on all rows of the Samsung A-series and Motorola reports; they are two "
                 "separate fields of the dump.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 8, 17, 11, 3 and 32 rows, each equal to a count of "
                 "ID: entries in the block made from the raw text by a separate script and to an independent parser, field by field "
                 "(network id, SSID, entry mark, selection status, disable reason, key management, creator, reboot count, recent "
                 "failure), except Has Ever Connected on the 5 Motorola entries where the value shares a line with the connect "
                 "choice text, which the other parser leaves empty and this reader reads. All five record the zone Africa/Accra (UTC+0 "
                 "without daylight saving), so the UTC conversion was the identity on the real rows; offsets and daylight saving were "
                 "tested on constructed text only. Not examined: Android 11, 12 and 14, other vendors, Passpoint entries (none in the "
                 "tested reports)."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave no rows: its Configured networks block is empty and the wifi dump prints numSavedNetworks=0.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "wifi",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_wifi_connection_events": {
        "name": "Bug Report - Wi-Fi Connection Events",
        "description": "The mConnectionEvents lines of the Wi-Fi metrics in the wifi service dump of an Android bug report text, "
                       "with start time, SSID, BSSID, duration, result and signal strength as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Wi-Fi",
        "notes": "One row per startTime= line under mConnectionEvents in the WifiMetrics part of the wifi service dump. SSID, BSSID, "
                 "Duration (ms), Roam Type, Connection Result, Level 2 Failure Code, Connectivity Failure Code, Signal Strength, "
                 "Wi-Fi State, Screen On, Network Type, Connection Nominator and Network Creator are the key=value pairs of the line "
                 "as printed; Connection Result and Channel Info are shown as stored (no meaning is given to the numbers), Other "
                 "Fields holds the remaining pairs in the order printed, cut at 1,500 characters. The Android 10 builds print fewer "
                 "pairs, so Network Type and Network Creator are empty on those two reports. Start Time As Printed is month, day and "
                 "clock time without a year and with unpadded hours, minutes and seconds; Start Time (UTC) uses the year rule of "
                 "Bug Report - Wi-Fi Saved Networks and the zone of Bug Report - Device Facts. The fraction after the seconds is "
                 "printed unpadded on some builds (.45 was seen), so the UTC value is given to the whole second and the fraction is "
                 "kept only in the printed text.\n"
                 "The platform keeps a short list: the tested reports held 0 to 6 lines. A row records that the Wi-Fi metrics noted a "
                 "connection attempt with that outcome; it does not say who started it. The wifip2p service prints a list of the same "
                 "name that was empty on the three reports that print it and is not read.\n"
                 "All rows of the Samsung A-series, Huawei, Transsion-brand and Motorola reports held ROAM_UNRELATED in Roam Type, "
                 "1 in Connection Result, NONE in both failure code columns and WIFI_DISCONNECTED in Wi-Fi State; the Samsung "
                 "A-series, Huawei and Transsion-brand reports hold one row each, so the other columns are uniform there too. "
                 "Channel Info held 0 on the Huawei row. "
                 "On the Motorola report, whose six rows are the same network, SSID, BSSID, Level 2 Failure Code, "
                 "Connectivity Failure Code, Channel Info, Network Type, Connection Nominator and Network Creator held "
                 "one value on all rows.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 1, 0, 1, 1 and 6 rows, each equal to a count of "
                 "startTime= lines in the raw text made by a separate script and to an independent parser on SSID, BSSID, duration, "
                 "roam type, result, signal strength, state and screen flag; the Samsung S-series report printed none (its Wi-Fi was "
                 "off at the dump). The zone of all five is UTC+0, so the conversion was the identity on the real rows. Not "
                 "examined: Android 11, 12 and 14, other vendors, and failed attempts (every tested row reports result 1)."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave no rows: its mConnectionEvents list is empty.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "plug-connected",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_wifi_current_state": {
        "name": "Bug Report - Wi-Fi Current State",
        "description": "The Wi-Fi power and mode lines and the mWifiInfo snapshot of the wifi service dump in an Android bug report "
                       "text, with SSID, BSSID, signal, link speed and frequency as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Wi-Fi",
        "notes": "One row per mWifiInfo line of the wifi service dump, and one row with the Wi-Fi status and mode lines alone where "
                 "the dump prints no mWifiInfo line. Wi-Fi Status and Wi-Fi Mode are the Wi-Fi is enabled or disabled line and the "
                 "Current wifi mode line as printed. The other columns are the pairs of the mWifiInfo line as printed (the Android "
                 "10 builds print fewer of them, so those cells are empty there); Link Properties is the mLinkProperties line printed "
                 "just before it, cut at 1,000 characters, and Last BSSID is the mLastBssid line after it. Other Fields holds the "
                 "remaining pairs of the line. The dump holds one such line for each client mode instance it lists, so a report can "
                 "have several rows (the Motorola report has three, two of them with the supplicant state DISCONNECTED and an unknown "
                 "SSID); Source Line tells them apart.\n"
                 "This is a snapshot taken when the dump ran. It has no time of its own, so there is no time column, and a row says "
                 "nothing about earlier connections (see Bug Report - Wi-Fi Connection Events). Where the Wi-Fi was off the "
                 "connection columns are empty (the Samsung S-series report); that is the dump's content and not a failure to read. "
                 "On the Samsung S-series report (Wi-Fi off) SSID (as printed), BSSID (as printed), MAC (as printed), "
                 "IP (as printed), Security Type (as printed), Supplicant State, Wi-Fi Standard, RSSI, Link Speed, Tx "
                 "Link Speed, Rx Link Speed, Frequency, Net ID, Metered Hint, Last BSSID, Link Properties and Other "
                 "Fields have no value. BSSID (as printed), MAC (as printed), IP (as printed), Security Type (as "
                 "printed) and Wi-Fi Standard have no value on the Huawei report, and IP (as printed), Security Type "
                 "(as printed) and Wi-Fi Standard have none on the Transsion-brand one, whose builds print fewer "
                 "pairs. On the Motorola report Wi-Fi Status, Wi-Fi Mode "
                 "and Wi-Fi Standard held one value on all three rows, and Link Speed and Tx Link Speed were identical "
                 "on them.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 1, 1, 1, 1 and 3 rows, equal to the mWifiInfo lines "
                 "of the raw text (one row for the report without such a line) made by a separate script. Not examined: Android 11, "
                 "12 and 14, other vendors, and an SSID that itself contains a comma followed by a key name, which would be split there."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave 1 row.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "wifi",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 1 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_wifi_scan_results": {
        "name": "Bug Report - Wi-Fi Scan Results",
        "description": "The Latest scan results tables of the wifiscanner service dump in an Android bug report text, with BSSID, "
                       "frequency, signal, age, SSID and flags as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Wi-Fi",
        "notes": "One row per access point line of the Latest scan results and Latest native scan results tables of the wifiscanner "
                 "service dump; Scan Table says which. The Latest native pno scan results table and the hexadecimal Latest native "
                 "scan results IEs block are not read (the pno table was empty on the tested reports). BSSID, Frequency, RSSI, Age "
                 "(sec), SSID and Flags are the columns of the table as printed; RSSI Detail is the per-chain text some builds "
                 "print in brackets after the signal, for example 0:-81/1:-82. Age (sec) is the platform's text, including the >1000.0 "
                 "form, and is relative to the time of the dump, so the table has no time column. The Huawei build prints BSSIDs "
                 "with masked bytes and SSIDs in a shortened form, shown as printed.\n"
                 "The list is what the scanner kept for its last scans; a row says that the scanner had a result for that access "
                 "point when the dump ran, not that the device was near it for any length of time or joined it, and an access point "
                 "that is not listed says nothing about earlier locations. The same access point can appear in both tables. Flags "
                 "is the capability text as printed and is not decoded.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 9, 8, 28, 2 and 2 rows, each equal to a count of "
                 "access point lines in the two tables made from the raw text by a separate script. RSSI Detail is empty on four "
                 "reports and printed on the Samsung S-series report only. Not examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave no rows; its wifi dump prints numTotalScanResults=0.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "radar",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_wifi_state_records": {
        "name": "Bug Report - Wi-Fi State Machine Records",
        "description": "The rec[N]: time= lines of the state machines in the wifi, wifiscanner and wifip2p service dumps of an "
                       "Android bug report text, with time, states and message as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Wi-Fi",
        "notes": "One row per rec[N]: time= line of the three Wi-Fi services. Service is the dump the line is in; State Machine is "
                 "the heading line above it (for example WifiPnoScanStateMachine); Record is N; Processed State, Origin State and "
                 "Destination State are processed=, org= and dest=; What is the rest of the line after what= as printed, cut at 500 "
                 "characters (it can carry the sender package and uid of a request, the number of a message that the dump prints "
                 "without a name, or the platform's own message name). Nothing is decoded. Time As Printed is month, day and clock "
                 "time without a year; Time (UTC) uses the year rule of Bug Report - Wi-Fi Saved Networks and the zone of Bug "
                 "Report - Device Facts.\n"
                 "Each machine keeps a short list of its latest transitions (up to 128 records on the tested reports), so a "
                 "transition that is not listed says nothing. A row says that the state machine "
                 "recorded that transition; it does not say what caused the message.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 105, 194, 257, 80 and 457 rows, each equal to a count "
                 "of rec[N]: time= lines in the three services made from the raw text by a separate script. The zone of all five is "
                 "UTC+0, so the conversion was the identity on the real rows. Not examined: Android 11, 12 and 14, other vendors, state "
                 "machine records of services other than these three."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave 18 rows (not compared with a second count).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "arrows-transfer-down",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 18 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_wifi_service_log": {
        "name": "Bug Report - Wi-Fi Service Log",
        "description": "The time-stamped lines of the Log Begin blocks in the wifi and wifiscanner service dumps of an Android bug "
                       "report text, with the log name, time and message as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Wi-Fi",
        "notes": "One row per line that starts with an ISO time (YYYY-MM-DDTHH:MM:SS with a fraction) between a <name> - Log Begin "
                 "line and the matching Log End line in the wifi and wifiscanner service dumps (for example WifiScanningService, "
                 "WifiConnectivityManager, WifiConfigManager, WifiLastResortWatchdog). Log is the <name>; Message is the text after the time "
                 "(and its dash), as printed, cut at 1,000 characters; it can carry package names, uids, SSIDs and listener class names. Lines "
                 "inside a block that carry no time (settings printouts, health statistics) are not rows. Time As Printed is device "
                 "wall-clock time; Time (UTC) converts it with the zone shown in Bug Report - Device Facts and is empty for a time "
                 "before 2009, for the 1970 value the platform prints for a time never set, and where the report records no zone.\n"
                 "Each log is a ring of the latest lines the service kept, so a line that is not listed says nothing. A row says "
                 "that the service logged that message; it does not say what caused it or that a person did.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 127, 1,067, 684, 48 and 1,054 rows, each equal to a "
                 "count of time-stamped lines inside the Log Begin and Log End markers made from the raw text by a separate "
                 "script. The zone of all five is UTC+0, so the conversion was the identity on the real rows. Not examined: Android "
                 "11, 12 and 14, other vendors, a block with no Log End line."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave 21 rows (not compared with a second count).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "list-details",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 21 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_network_usage_buckets": {
        "name": "Bug Report - Network Usage Buckets",
        "description": "The statistics history buckets of the netstats service dump and the CHECKIN NETSTATS section of an Android "
                       "bug report text, with identity, UID, set, tag and byte and packet counts as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Network",
        "notes": "One row per history bucket. Statistics Table is the table the bucket is printed in: Dev stats, Xt stats, UID stats "
                 "or UID tag stats in the netstats service dump and in the CHECKIN NETSTATS section that prints the same tables, or "
                 "checkin plus the group name (xt) for the compact checkin form (v1 lines). Source Section says which section "
                 "printed the row; a report that prints a table in both sections lists its buckets twice. Identity is the ident=[...] "
                 "text of the table entry as printed (interface type, network key or SSID, metered flag; the subscriber id is "
                 "shortened by the platform), or the template word (cell, wifi) of the checkin form. UID, Set and Tag are the "
                 "entry's uid=, set= and tag=; UID -1 is the platform's value for a total over all UIDs. Bucket Start is epoch "
                 "seconds, shown as Time (UTC) when it falls between 2009 and 2100; Bucket Length is the bucketDuration or d, line "
                 "(3,600 s for the device tables and 7,200 s for the UID tables of the Android 16 reports). Received Bytes, Received "
                 "Packets, Transmitted Bytes, Transmitted Packets and Operations are the rb, rp, tb, tp and op values (the b, line "
                 "carries them in that order); Other Fields is the text after op= where the Android 10 builds print a second set "
                 "of four counters, kept as printed and not interpreted.\n"
                 "Per-app counters exist on two of the five tested reports only: the two Samsung reports (Android 16) print the "
                 "UID stats table (58,669 and 44,282 buckets for 128 and 172 distinct UIDs); the Huawei, Transsion-brand and Motorola "
                 "reports print device-wide tables only, with UID -1 on every row, so for them the artifact says nothing about "
                 "individual apps. The statistics are what the device kept: the Samsung histories span about 91 and 92 days, the others one day or "
                 "less. Buckets start at the platform's own boundaries and are not a record of what an app "
                 "did with the data; they carry no destinations. UID tag stats (per tag) were not printed by any tested report. "
                 "A bucket that is not listed says nothing.\n"
                 "UID is a number, not a package; the package behind it is in Bug Report - Installed Packages (App ID there) and is not "
                 "guessed here. "
                 "Tag held 0x0 on all rows of the two Samsung reports. Other Fields is empty on four reports and "
                 "holds the second counter set on the Huawei one. Bucket Length (s) held 3600 and Operations held 0 on "
                 "all rows of the Huawei, Transsion-brand and Motorola reports.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 64,097, 49,674, 11, 25 and 56 rows, each equal to a "
                 "count of st= history lines plus b, lines in the raw text made by a separate script. The 64,097, 49,674, 4, 6 and 24 "
                 "buckets of the service dump and the full dump were also equal to an independent parser in table, UID, set, tag, "
                 "bucket length and all five counters plus the second counter set; that parser does not read the compact checkin "
                 "lines (7, 19 and 32 rows of the Huawei, Transsion-brand and Motorola reports). The five counters of a "
                 "checkin b, line were compared with the same bucket of the Xt stats table of the service dump in the Motorola "
                 "report: the wifi bucket of 1793044800 was identical in all five numbers, and at 1793041200 the checkin cell and "
                 "wifi values equalled the sums of the two cell entries and the three wifi entries of the service table. Not examined: Android 11, 12 and 14, other vendors, and a UID tag table."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave no rows: its netstats dump prints the Dev stats and Xt stats headings with no bucket under them.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "chart-bar",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_netpolicy_uid_entries": {
        "name": "Bug Report - Network Policy UID Entries",
        "description": "The per-UID lists and rules of the netpolicy service dump in an Android bug report text (policy, allow "
                       "lists, status), with the UID and the value as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Network",
        "notes": "One row per UID= line, indented by two spaces, under a heading of the netpolicy service dump. List is the heading "
                 "(Policy for UIDs, Power save whitelist (except idle) app ids, Power save whitelist app ids, App idle whitelist "
                 "app ids, Default restrict background allowlist (or whitelist) uids, Uids transitioning to background, Status for "
                 "all known UIDs, Status for just UIDs with rules); the lists printed differ between builds (only the Android 10 reports print Status for just UIDs with rules). UID is the "
                 "number as printed (the power save lists print an app id) and Value is the rest of the line as printed, cut at 400 "
                 "characters: a policy number and name, true, a process state with rules, or a blocked state. Nothing is decoded "
                 "and the continuation lines under a status entry (callback info) are not read. The UID is a number, not a package; "
                 "the package behind it is in Bug Report - Installed Packages.\n"
                 "The lists are the state the service held when the dump ran. A UID that is not listed says nothing: the platform "
                 "applies its defaults to an app without an entry.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 585, 742, 269, 49 and 1,118 rows, each equal to a "
                 "count of two-space-indented UID= lines in the service dump made from the raw text by a separate script. Not "
                 "examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave 508 rows, equal to the UID= lines of its netpolicy dump.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "list-check",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 508 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_netpolicy_settings": {
        "name": "Bug Report - Network Policy Settings",
        "description": "The state, flag and policy lines of the netpolicy service dump in an Android bug report text, with the "
                       "heading, name and value as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Network",
        "notes": "One row per line of the netpolicy service dump that is not a UID line and not a line of the three event logs: the "
                 "state lines at the top (System ready, Restrict background, Restrict power, Device idle and others), the flag lines, "
                 "the Network policies and Subscription plans lines, the active subscriptions, the network to interface map, the "
                 "per-call statistics and the multipath tracker line. Group is the heading above the line (empty for a line with "
                 "none), Name is the text before the first colon when that text is plain words, otherwise empty, and Value is the "
                 "rest, cut at 1,500 characters. Subscriber ids in the policy lines are shortened by the platform. Nothing is "
                 "decoded; the process id lines at the top of the dump are not rows.\n"
                 "The values are the service state when the dump ran. A flag or policy that is not listed says nothing about the "
                 "factory default in effect.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 25, 26, 12, 13 and 26 rows, equal to a count of the "
                 "line classes above in the raw text made by a separate script. Not examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave 14 rows (not compared with a second count).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 14 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_netpolicy_events": {
        "name": "Bug Report - Network Policy Events",
        "description": "The mEventLogs, mNetworkBlockedLogs and mUidStateChangeLogs lines of the netpolicy service dump in an "
                       "Android bug report text, with time and message as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Network",
        "notes": "One row per time-stamped line of the three logs, printed most recent first. Log is mEventLogs (for example Firewall "
                 "rule changed: <uid>-<chain>-<allow or deny>), mNetworkBlockedLogs (a uid and a blocked state) or mUidStateChangeLogs "
                 "(a uid and a process state text). Message is the text after the time as printed, cut at 600 characters; the codes "
                 "in it are the platform's own and are not decoded here. The time is printed as YYYY-MM-DDTHH:MM:SS:mmm (a colon "
                 "before the milliseconds): Time As Printed keeps it, and Time (UTC) converts it as device wall-clock time with the "
                 "zone shown in Bug Report - Device Facts. Entries printed with the time 1970-01-01T00:00:00:000 and the message "
                 "null get no UTC value and Time Note says the time was not set.\n"
                 "Each log printed about 400 entries on four reports and 100 on the Transsion-brand one, so an event that is not "
                 "listed says nothing. A row says that the service "
                 "logged the change; it does not say what caused it. The Motorola report prints no mNetworkBlockedLogs.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 973, 1,203, 1,173, 300 and 800 rows, each equal to a "
                 "count of time-stamped lines in the service dump made from the raw text by a separate script. The zone of all five "
                 "is UTC+0, so the conversion was the identity on the real rows. Not examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave 743 rows (not compared with a second count).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "history",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 743 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_connected_networks": {
        "name": "Bug Report - Connected Networks",
        "description": "The Current Networks entries (NetworkAgentInfo) of the connectivity service dump in an Android bug report "
                       "text, with interface, addresses, DNS servers, routes, transports and capabilities as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Network",
        "notes": "One row per NetworkAgentInfo line under Current Networks in the connectivity service dump. Network ID is network{N}; "
                 "Default Network is true when it equals the Active default network line of the same dump. Network Info is the ni{} "
                 "text (Android 16 and 15: type and state; Android 10: a bracketed list), Created is created= where the build prints "
                 "it (Android 16 and 15, with a trailing Z, shown as UTC without conversion) and empty on the Android 10 builds. "
                 "Interface, Link Addresses, DNS Addresses, Domains and Routes are the InterfaceName, LinkAddresses, DnsAddresses, "
                 "Domains and Routes of the lp{} text; Transports, Capabilities, Signal Strength and SSID are the Transports, "
                 "Capabilities, SignalStrength and SSID of the nc{} text, as printed (the Huawei build prints the SSID as stars); "
                 "Score is the Score text. The Android 10 builds print no lp{} text, so the interface, address, DNS and route "
                 "columns are empty there. Request lists and the other parts of the dump are not read.\n"
                 "Some builds dump the service twice (a high priority part and the normal part); both dumps list the network and "
                 "give two rows, told apart by Source Line. The rows are the networks the service held when the dump ran: one to "
                 "four per tested report. A row says that the service had that network; it does not say how long. A VPN network "
                 "would show the transport VPN; none of the tested reports had one, and the vpn_management service dump that one "
                 "report printed is not read. "
                 "Signal Strength and SSID have no value on the Samsung S-series rows, Created As Printed has no "
                 "value on the Huawei and Transsion-brand rows, Interface, Link Addresses, DNS Addresses, Domains and "
                 "Routes have no value on the Huawei rows (no lp{} text), and Domains held null on all Transsion-brand "
                 "rows.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 1, 2, 2, 4 and 1 rows, each equal to a count of "
                 "NetworkAgentInfo{ lines in the raw text made by a separate script; network id, transports, interface and the "
                 "default flag also equal an independent parser as sets (that parser reads one of the two dumps of a service "
                 "dumped twice). Not examined: Android 11, 12 and 14, other vendors, "
                 "a VPN network."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave no rows: nothing is listed under Current Networks in its connectivity dump.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "network",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_network_interfaces": {
        "name": "Bug Report - Network Interfaces",
        "description": "The interface list of the NETWORK INTERFACES section (ip link) of an Android bug report text, with state, "
                       "MTU, link address and the counters the section prints.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Network",
        "notes": "One row per interface entry (N: name: <flags> mtu ...) of the NETWORK INTERFACES command section. Linked is the "
                 "name after @ where the entry prints one, Flags is the text in angle brackets, and Qdisc, State, Mode, Group and "
                 "Queue Length are the words after those names. Link Type, Link Address and Broadcast come from the link/ line "
                 "under the entry as printed (a hardware address for an ethernet-like interface, which is device data). The RX and "
                 "TX columns are the numbers under the RX: and TX: headings: the Samsung and Motorola reports print them (the "
                 "section is ip -s link), the Huawei and Transsion-brand reports print the plain ip link text without counters, "
                 "so those columns are empty there. The counters are the totals the section printed, not figures for a period.\n"
                 "The list is the interfaces present when the dump ran; an interface that is not listed says nothing. State is the "
                 "kernel's word and does not say whether traffic went through the interface. Group held default on all rows of the "
                 "five tested reports. Linked is empty on most rows. "
                 "RX Errors, RX Overrun, RX Multicast, TX Carrier and TX Collisions held 0 on all rows of the three "
                 "reports that print counters, and RX Dropped, TX Errors and TX Dropped held 0 on all rows of two of "
                 "them. RX Bytes, RX Packets, RX Errors, RX Dropped, RX Overrun, RX Multicast, TX Bytes, TX Packets, TX "
                 "Errors, TX Dropped, TX Carrier and TX Collisions have no value on the Huawei and Transsion-brand "
                 "reports. Mode held "
                 "DEFAULT on all rows of the Samsung S-series report and Queue Length held 1000 on all rows of the "
                 "Huawei report.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 54, 46, 35, 22 and 38 rows, each equal to a count of "
                 "interface entries in the raw text and to the number of rows of Bug Report - Network Interface Counters of the "
                 "same report. Not examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave 70 rows (not compared with a second count).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "network",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 70 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_interface_counters": {
        "name": "Bug Report - Network Interface Counters",
        "description": "The per-interface receive and transmit counters of the NETWORK DEV INFO section (/proc/net/dev) of an "
                       "Android bug report text.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Network",
        "notes": "One row per interface line of /proc/net/dev. The columns are the sixteen counters of the table in the order "
                 "printed: bytes, packets, errs, drop, fifo, frame, compressed and multicast for receive, and bytes, packets, errs, "
                 "drop, fifo, colls, carrier and compressed for transmit. The counters are the totals printed when the dump ran, not figures for a period; "
                 "they carry no app, no destination and no time. An interface that is not listed says nothing.\n"
                 "RX Errs, RX Fifo, RX Frame, RX Compressed, RX Multicast, TX Fifo, TX Colls, TX Carrier and TX "
                 "Compressed held 0 on all rows of every tested report; RX Drop and TX Errs held 0 on all rows of four "
                 "reports and TX Drop on three.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 54, 46, 35, 22 and 38 rows, each equal to a count of "
                 "lines with sixteen numbers after the colon in the raw text, and to the interface count of the NETWORK INTERFACES "
                 "section of the same report. Not examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave 70 rows, equal to the interface lines of its two /proc/net/dev sections (35 each).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "arrows-up-down",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 70 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_dns_servers": {
        "name": "Bug Report - DNS Servers",
        "description": "The DNS servers of each network in the dnsresolver service dump of an Android bug report text, with the "
                       "query counters, interface names and private DNS mode as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Network",
        "notes": "One row per server line under DNS servers in each NetId block of the dnsresolver service dump. Server is the address "
                 "as printed (an IPv6 link-local address carries its interface); Total, Successes, Errors, Timeouts and Internal "
                 "Errors are the counts in the parentheses, RTT Average (ms) and Last Sample (s) the last two values. The sample "
                 "window is the resolver's own (the dump prints a validity of 1,800 s and at most 64 samples), so the counts are "
                 "recent resolver samples, not a history of the device. Interfaces, Search Domains, Private DNS Mode, Transport "
                 "Type and Metered are the lines of the same NetId block (the Android 10 builds print no interface names, transport "
                 "type or metered line). The server statistics by transport, the DoT and DoH configuration and the experiment "
                 "flags are not read. A row says that the resolver had that server configured for that network; it does not say "
                 "what was queried, and the dump holds no query names.\n"
                 "Errors and Internal Errors held 0 on all rows of the five tested reports, Search Domains held none defined and "
                 "Private DNS Mode held OPPORTUNISTIC on all rows. "
                 "Interfaces, Transport Type and Metered have no value on the Huawei and Transsion-brand rows, and "
                 "Net ID held 100 on all Huawei rows.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 1, 2, 3, 3 and 1 rows, each equal to a count of "
                 "server lines in the raw text made by a separate script. Not examined: Android 11, 12 and 14, other vendors, a network "
                 "with search domains."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave no rows: its dnsresolver dump prints no network.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "world",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_private_dns_log": {
        "name": "Bug Report - Private DNS Log",
        "description": "The PrivateDnsLog lines of the dnsresolver service dump in an Android bug report text, with the time of day, "
                       "network, server and state as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Network",
        "notes": "One row per line of the PrivateDnsLog list: Time Of Day As Printed (hours, minutes, seconds and milliseconds with "
                 "no date), Net ID, Server (the address, port and path text in braces) and State (for example in_process, success, "
                 "fail). The list has no date, so there is no UTC value and no time column; the entries are older than the dump by "
                 "an amount the dump does not give. A row records that the resolver logged that validation state for the server; it "
                 "does not say what was queried. The Huawei and Transsion-brand builds (Android 10) print no such list, so the "
                 "table is empty for them, which says nothing about the device. "
                 "Net ID held 100 on all four rows of the Samsung S-series report.\n"
                 "Evidence tiers. Data-proven on three real bug reports (Samsung A-series and S-series on Android 16 and Motorola "
                 "on Android 15): 10, 4 and 54 rows, each equal to a count of the list's lines in the raw text made by a separate "
                 "script; none on the two Android 10 reports, which print none. Not examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave no rows: its PrivateDnsLog is empty.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "world",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_open_sockets": {
        "name": "Bug Report - Open Sockets",
        "description": "The Active Internet connections table of the NETSTAT section of an Android bug report text, with protocol, "
                       "queues, local and foreign address, state, UID and inode as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Network",
        "notes": "One row per tcp, udp or raw line of the Active Internet connections table of the NETSTAT command section "
                 "(netstat -npWae on the Samsung reports, a plainer netstat on the others). Local and Foreign are the addresses with "
                 "ports as printed; State is the word printed for tcp (empty for udp); UID, Inode and Program are printed by the "
                 "Samsung reports only (the Android 16 build) and empty on the other three reports. Program held the text - on all "
                 "rows of both Samsung reports. A raw6 line prints a number where the state word is and is read with that number as "
                 "State. The table is a snapshot of the sockets the "
                 "kernel listed when the section ran: a row says that a socket existed with that state then, not when it was "
                 "opened, how much data it carried or what it was used for. A foreign address is the peer the kernel recorded and "
                 "is not resolved to a name. The Active UNIX domain sockets table is in Bug Report - Unix Domain Sockets. "
                 "Send Queue held 0 on all rows of the Huawei report.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 39, 39, 51, 57 and 21 rows, each equal to a count of "
                 "tcp, udp and raw lines in the raw text made by a separate script. Send-Q held 0 on all rows of the Huawei report. "
                 "Not examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave no rows: its two netstat sections print no tcp or udp line.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "plug",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_unix_sockets": {
        "name": "Bug Report - Unix Domain Sockets",
        "description": "The Active UNIX domain sockets table of the NETSTAT section of an Android bug report text, with type, "
                       "state, inode and path as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Network",
        "notes": "One row per unix line of the Active UNIX domain sockets table of the NETSTAT command section. Reference Count, "
                 "Flags, Socket Type, State, Inode and Path are the columns as printed (State is empty for a socket that prints "
                 "none; Path is empty for an unnamed socket). Program is the PID/Program column printed by the Samsung reports "
                 "only; it held the text - on 617 of 618 rows of the A-series report (one row names a process) and on all rows of "
                 "the S-series report. The rows are a snapshot of the sockets listed when the section "
                 "ran and say nothing about what the sockets carried. Paths such as /dev/socket/... are the platform's own names. "
                 "Flags held [ ] on all rows of the Huawei, Transsion-brand and Motorola reports, and Program has no "
                 "value on them.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 618, 1,380, 604, 381 and 712 rows, each equal to a "
                 "count of unix lines in the raw text made by a separate script. Protocol held the text unix on all rows. Not "
                 "examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave 1,116 rows, equal to the unix lines of its two netstat sections (581 and 535).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "plug",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 1,116 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_socket_details": {
        "name": "Bug Report - Socket Details",
        "description": "The ss table of the DETAILED SOCKET STATE section of an Android bug report text, with netid, state, "
                       "queues, addresses, UID, inode and the TCP information line as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Network",
        "notes": "One row per socket line of the DETAILED SOCKET STATE command section (ss -eionptu on the tested builds). Netid, "
                 "State, Receive Queue, Send Queue, Local and Peer are the columns as printed; UID, Inode and Socket are the uid:, "
                 "ino: and sk: values and Timer and Users the timer:(...) and users:((...)) texts where printed; Extended Fields is "
                 "the rest of the line as printed. Info is the indented line under a tcp socket (congestion control, rtt, bytes "
                 "acknowledged and similar), joined and cut at 800 characters; it is not interpreted. The table is a snapshot: a "
                 "row says that a socket existed with that state when the section ran, not when it was opened or what it carried. "
                 "Peers are addresses as the kernel recorded them, not names.\n"
                 "Users is empty on the Samsung reports and printed on the other three. UID is empty on rows that print no uid:. "
                 "Send Queue held 0 on all rows of the Huawei report.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 36, 26, 51, 29 and 23 rows, each equal to a count of "
                 "non-indented non-header lines in the raw text made by a separate script. Not examined: Android 11, 12 and 14, other "
                 "vendors."
                 "\nOn the corpus the ss section of s20fe_a13 prints its header line only, so it gave no rows; the two partial texts of userb2_a13 gave 3 and 5 rows (not compared with a second count). The error dumps of samsungs20_a13 and sharon_a14 print no ss section.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "plug",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 8 rows",
        }
    },
    "bugreport_tethering_log": {
        "name": "Bug Report - Tethering Log",
        "description": "The time-stamped Log lines of the tethering service dump in an Android bug report text, with time and "
                       "message as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Network",
        "notes": "One row per time-stamped line under the Log heading of the tethering service dump. Message is the text after the "
                 "time as printed, cut at 1,000 characters (it includes the configuration text the service logs when its settings "
                 "change). Time As Printed is device wall-clock time with a fraction; Time (UTC) converts it with the zone shown in "
                 "Bug Report - Device Facts. A row records that the service logged that message; the messages seen in the tested "
                 "reports are configuration, entitlement, upstream and USB notices, which do not by themselves say that a hotspot "
                 "or tethering was used. The log is a ring of the latest lines, so a line that is not listed says nothing. Some builds dump the "
                 "service twice and then list the lines twice.\n"
                 "Only the Samsung A-series, Samsung S-series and Motorola reports print this service (the Huawei and Transsion-brand "
                 "Android 10 reports do not), so the table is empty for those two, which says nothing about the device.\n"
                 "Evidence tiers. Data-proven on three real bug reports (Samsung A-series and S-series on Android 16 and Motorola "
                 "on Android 15): 80, 1,000 and 188 rows, each equal to a count of time-stamped Log lines in the raw text made by a "
                 "separate script; none on the two Android 10 reports. The zone of all five is UTC+0, so the conversion was the "
                 "identity on the real rows. Not examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave 34 rows (not compared with a second count).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "antenna",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 34 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_tethering_state": {
        "name": "Bug Report - Tethering State",
        "description": "The configuration, entitlement, tether state and offload lines of the tethering service dump in an Android "
                       "bug report text, with heading, name and value as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Network",
        "notes": "One row per indented line of the tethering service dump outside the Log list. Group is the heading above the line "
                 "(Tethering, Configuration, Entitlement, Tether state, Hardware offload, BPF offload and so on), Name is the "
                 "text before the first colon when that text is plain words, otherwise empty, and Value is the rest, cut at 1,500 "
                 "characters. The values are the service state when the dump ran; a setting that is not listed says nothing "
                 "about the default in effect.\n"
                 "Only the Samsung A-series, Samsung S-series and Motorola reports print this service, with 132 rows each; the "
                 "table is empty for the two Android 10 reports, which says nothing about the device.\n"
                 "Evidence tiers. Data-proven on three real bug reports (Samsung A-series and S-series on Android 16 and Motorola "
                 "on Android 15): 132 rows each, equal to a count of the indented "
                 "non-Log lines in the raw text made by a separate script. Not examined: "
                 "Android 11, 12 and 14, other vendors, a report with an active tether."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave 142 rows (not compared with a second count).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "antenna",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 142 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
}

import re
from datetime import datetime, timezone

from scripts import dumpstate_reader
from scripts.ilapfuncs import artifact_processor, logfunc

NOTE_NO_YEAR = 'no report time: the year is not known, no UTC value'
NOTE_BEFORE_2009 = 'time before 2009: no UTC value'
_MONTH_DAY = re.compile(r'^(\d{1,2})-(\d{1,2}) (\d{1,2}):(\d{1,2}):(\d{1,2})(?:\.(\d+))?$')


def _reports(context):
    """The bug report texts among the staged files, as (Source File label, Report) pairs."""
    return dumpstate_reader.load_reports(context.get_files_found(), context.get_relative_path, logfunc)


def _source_path(context, reports):
    """The staged files that were read; the matched files when none was a bug report."""
    paths = [report.source.path for _label, report in reports] or sorted(str(path) for path in context.get_files_found())
    return '\n'.join(dict.fromkeys(str(path) for path in paths))


def _rows(report, table):
    return getattr(report, 'net_' + table, [])


def _log_cuts(label, report, service, lines):
    """Say so when the platform cut a dump of ``service`` that holds the rows (or when it cut one and there are no rows)."""
    cut = [section for section in report.sections if section.kind == 'service' and section.name == service and section.timeout_ms]
    if lines:
        cut = [section for section in cut if any(section.line < number < section.end_line for number in lines)]
    if cut:
        dumpstate_reader.say_once(logfunc, f'Bug report {label}: the {service} service dump was cut by a {cut[0].timeout_ms} ms '
                                           f'timeout, the rows from it may be partial')


def _wall(report, text):
    """``(UTC datetime or None, note)`` for a device wall-clock text (ISO ``T`` or space separator, optional fraction)."""
    value = str(text).strip().replace('T', ' ')
    if value[:19] in dumpstate_reader.UNSET_WALL_TIMES:
        return None, dumpstate_reader.NOTE_UNSET
    moment = dumpstate_reader.parse_wall_time(value)
    if moment is None:
        return None, dumpstate_reader.NOTE_NOT_A_TIME
    if moment.year < 2009:
        return None, NOTE_BEFORE_2009
    if not report.clock.known:
        return None, dumpstate_reader.NOTE_NO_ZONE
    utc = report.clock.to_utc(value)
    return utc, '' if utc else dumpstate_reader.NOTE_NONEXISTENT


def _policy_wall(report, text):
    """Like :func:`_wall` for ``YYYY-MM-DDTHH:MM:SS:mmm`` (the policy logs print a colon before the milliseconds)."""
    head, separator, tail = str(text).rpartition(':')
    return _wall(report, head + '.' + tail if separator and len(head) >= 19 and tail.isdigit() else text)


def _month_day(report, text, whole_seconds=False):
    """``(UTC datetime or None, note)`` for ``MM-DD HH:MM:SS[.mmm]`` (no year; hours and minutes may be unpadded).

    The year is the latest one, the report's or the one before, that does not put the time after the report time
    (see ``Report.setting_change_time``). ``whole_seconds`` drops the fraction (some builds print it unpadded).
    """
    if not text:
        return None, ''
    match = _MONTH_DAY.match(str(text).strip())
    if not match:
        return None, dumpstate_reader.NOTE_NOT_A_TIME
    month, day, hour, minute, second, fraction = match.groups()
    millis = '000' if whole_seconds or not fraction or len(fraction) != 3 else fraction
    normal = '%02d-%02d %02d:%02d:%02d.%s' % (int(month), int(day), int(hour), int(minute), int(second), millis)
    full, utc = report.setting_change_time(normal)
    if not full:
        return None, NOTE_NO_YEAR
    if utc is None:
        return None, dumpstate_reader.NOTE_NO_ZONE if not report.clock.known else dumpstate_reader.NOTE_NONEXISTENT
    return utc, ''


def _epoch(seconds):
    """UTC datetime for epoch seconds between 2009 and 2100, else None."""
    if seconds is None or not dumpstate_reader.plausible_epoch_ms(seconds * 1000):
        return None
    return dumpstate_reader.epoch_s_to_utc(seconds)


def _printed_utc(text):
    """UTC datetime for a time printed with a trailing Z (ISO, UTC), else None."""
    if not text.endswith('Z'):
        return None
    moment = dumpstate_reader.parse_wall_time(text[:-1])
    return moment.replace(tzinfo=timezone.utc) if isinstance(moment, datetime) else None


def _collect(context, table, service, build):
    """``(rows, source path)`` over every report: ``build(report, label, item)`` gives one row for each item of the table."""
    rows = []
    reports = _reports(context)
    for label, report in reports:
        items = _rows(report, table)
        if service:
            _log_cuts(label, report, service, [item.line for item in items])
        for item in items:
            rows.append(build(report, label, item))
    return rows, _source_path(context, reports)


@artifact_processor
def bugreport_wifi_saved_networks(context):
    headers = (('Creation Time (UTC)', 'datetime'), 'Creation Time As Printed', ('Update Time (UTC)', 'datetime'),
               'Update Time As Printed', 'Network ID', 'Entry Mark', 'SSID (as printed)', 'BSSID (as printed)',
               'Currently Connected', 'User Selected', 'Auto Join', 'Hidden', 'PMF', 'Selection Status', 'Disable Reason',
               'Has Ever Connected', 'Associations', 'Key Management', 'Protocols', 'MAC Randomization Setting',
               'Randomized MAC', 'Creator UID', 'Creator Name', 'Last Update UID', 'Last Update Name', 'Last Connect UID',
               'Most Recently Connected', 'Reboots Since Last Use', 'Recent Failure', 'Connect Choice', 'Carrier ID',
               'Subscription ID', 'Source Line', 'Source File')

    def build(report, label, item):
        created, _note = _month_day(report, item.creation)
        updated, _note = _month_day(report, item.update)
        return (created, item.creation, updated, item.update, item.network_id, item.prefix,
                item.ssid, item.bssid, item.currently_connected, item.user_selected, item.auto_join, item.hidden, item.pmf,
                item.selection_status, item.disable_reason, item.has_ever_connected, item.associations, item.key_mgmt,
                item.protocols, item.mac_setting, item.random_mac, item.creator_uid, item.creator_name, item.update_uid,
                item.update_name, item.connect_uid, item.most_recent, item.reboots, item.recent_failure, item.connect_choice,
                item.carrier_id, item.subscription_id, item.line, label)
    rows, source = _collect(context, 'wifi_networks', 'wifi', build)
    return headers, rows, source


@artifact_processor
def bugreport_wifi_connection_events(context):
    headers = (('Start Time (UTC)', 'datetime'), 'Start Time As Printed', 'SSID (as printed)', 'BSSID (as printed)',
               'Duration (ms)', 'Roam Type', 'Connection Result (as stored)', 'Level 2 Failure Code',
               'Connectivity Failure Code', 'Signal Strength', 'Wi-Fi State', 'Screen On', 'Channel Info (as stored)',
               'Network Type', 'Connection Nominator', 'Network Creator', 'Other Fields', 'Source Line', 'Source File')

    def build(report, label, item):
        moment, _note = _month_day(report, item.start, whole_seconds=True)
        return (moment, item.start, item.ssid, item.bssid, item.duration, item.roam, item.result, item.l2_failure,
                item.connectivity_failure, item.rssi, item.wifi_state, item.screen_on, item.channel, item.network_type,
                item.nominator, item.creator, item.other, item.line, label)
    rows, source = _collect(context, 'wifi_connections', 'wifi', build)
    return headers, rows, source


@artifact_processor
def bugreport_wifi_current_state(context):
    headers = ('Wi-Fi Status', 'Wi-Fi Mode', 'SSID (as printed)', 'BSSID (as printed)', 'MAC (as printed)', 'IP (as printed)',
               'Security Type (as printed)', 'Supplicant State', 'Wi-Fi Standard', 'RSSI', 'Link Speed', 'Tx Link Speed',
               'Rx Link Speed', 'Frequency', 'Net ID', 'Metered Hint', 'Last BSSID', 'Link Properties', 'Other Fields',
               'Source Line', 'Source File')

    def build(_report, label, item):
        return (item.power, item.mode, item.ssid, item.bssid, item.mac, item.ip, item.security, item.supplicant, item.standard,
                item.rssi, item.link_speed, item.tx_speed, item.rx_speed, item.frequency, item.net_id, item.metered,
                item.last_bssid, item.link_properties, item.other, item.line, label)
    rows, source = _collect(context, 'wifi_state', 'wifi', build)
    return headers, rows, source


@artifact_processor
def bugreport_wifi_scan_results(context):
    headers = ('Scan Table', 'BSSID (as printed)', 'Frequency', 'RSSI', 'RSSI Detail', 'Age (sec)', 'SSID (as printed)', 'Flags',
               'Source Line', 'Source File')

    def build(_report, label, item):
        return (item.table, item.bssid, item.frequency, item.rssi, item.rssi_detail, item.age, item.ssid, item.flags, item.line,
                label)
    rows, source = _collect(context, 'wifi_scan_results', 'wifiscanner', build)
    return headers, rows, source


@artifact_processor
def bugreport_wifi_state_records(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Service', 'State Machine', 'Record',
               'Processed State', 'Origin State', 'Destination State', 'What', 'Source Line', 'Source File')

    def build(report, label, item):
        moment, _note = _month_day(report, item.time_text)
        return (moment, item.time_text, item.service, item.machine, item.number, item.processed, item.origin,
                item.destination, item.what, item.line, label)
    rows = []
    reports = _reports(context)
    for label, report in reports:
        items = _rows(report, 'wifi_records')
        for service in ('wifi', 'wifiscanner', 'wifip2p'):
            _log_cuts(label, report, service, [item.line for item in items if item.service == service])
        rows.extend(build(report, label, item) for item in items)
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_wifi_service_log(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Service', 'Log', 'Message', 'Source Line', 'Source File')

    def build(report, label, item):
        moment, _note = _wall(report, item.time_text)
        return moment, item.time_text, item.service, item.log_name, item.message, item.line, label
    rows = []
    reports = _reports(context)
    for label, report in reports:
        items = _rows(report, 'wifi_log')
        for service in ('wifi', 'wifiscanner'):
            _log_cuts(label, report, service, [item.line for item in items if item.service == service])
        rows.extend(build(report, label, item) for item in items)
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_network_usage_buckets(context):
    headers = (('Bucket Start (UTC)', 'datetime'), 'Bucket Start (epoch s)', 'Bucket Length (s)', 'Statistics Table', 'UID',
               'Set', 'Tag', 'Identity (as printed)', 'Received Bytes', 'Received Packets', 'Transmitted Bytes',
               'Transmitted Packets', 'Operations', 'Other Fields', 'Source Section', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        items = _rows(report, 'usage_buckets')
        _log_cuts(label, report, 'netstats', [item.line for item in items if item.origin.startswith('DUMP')])
        for item in items:
            rows.append((_epoch(item.start), item.start, item.bucket_seconds, item.table, item.uid, item.net_set, item.tag,
                         item.identity, item.rx_bytes, item.rx_packets, item.tx_bytes, item.tx_packets, item.operations,
                         item.extra, item.origin, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_netpolicy_uid_entries(context):
    headers = ('List', 'UID', 'Value (as printed)', 'Source Line', 'Source File')

    def build(_report, label, item):
        return item.group, item.uid, item.value, item.line, label
    rows, source = _collect(context, 'policy_uids', 'netpolicy', build)
    return headers, rows, source


@artifact_processor
def bugreport_netpolicy_settings(context):
    headers = ('Group', 'Name', 'Value (as printed)', 'Source Line', 'Source File')

    def build(_report, label, item):
        return item.group, item.name, item.value, item.line, label
    rows, source = _collect(context, 'policy_settings', 'netpolicy', build)
    return headers, rows, source


@artifact_processor
def bugreport_netpolicy_events(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Time Note', 'Log', 'Message', 'Source Line', 'Source File')

    def build(report, label, item):
        moment, note = _policy_wall(report, item.time_text)
        return moment, item.time_text, note, item.log, item.message, item.line, label
    rows, source = _collect(context, 'policy_events', 'netpolicy', build)
    return headers, rows, source


@artifact_processor
def bugreport_connected_networks(context):
    headers = (('Created (UTC)', 'datetime'), 'Created As Printed', 'Network ID', 'Default Network', 'Network Info',
               'Interface', 'Link Addresses', 'DNS Addresses', 'Domains', 'Routes', 'Transports', 'Capabilities',
               'Signal Strength', 'SSID (as printed)', 'Score', 'Source Line', 'Source File')

    def build(_report, label, item):
        return (_printed_utc(item.created), item.created, item.network_id, item.default, item.info, item.interface,
                item.addresses, item.dns, item.domains, item.routes, item.transports, item.capabilities, item.signal,
                item.ssid, item.score, item.line, label)
    rows, source = _collect(context, 'connectivity_networks', 'connectivity', build)
    return headers, rows, source


@artifact_processor
def bugreport_network_interfaces(context):
    headers = ('Index', 'Name', 'Linked', 'Flags', 'MTU', 'Qdisc', 'State', 'Mode', 'Group', 'Queue Length', 'Link Type',
               'Link Address', 'Broadcast', 'RX Bytes', 'RX Packets', 'RX Errors', 'RX Dropped', 'RX Overrun', 'RX Multicast',
               'TX Bytes', 'TX Packets', 'TX Errors', 'TX Dropped', 'TX Carrier', 'TX Collisions', 'Source Line',
               'Source File')

    def build(_report, label, item):
        return (item.index, item.name, item.linked, item.flags, item.mtu, item.qdisc, item.state, item.mode, item.group,
                item.qlen, item.link_type, item.link_address, item.broadcast, item.rx_bytes, item.rx_packets, item.rx_errors,
                item.rx_dropped, item.rx_overrun, item.rx_mcast, item.tx_bytes, item.tx_packets, item.tx_errors,
                item.tx_dropped, item.tx_carrier, item.tx_collisions, item.line, label)
    rows, source = _collect(context, 'interfaces', None, build)
    return headers, rows, source


@artifact_processor
def bugreport_interface_counters(context):
    headers = ('Interface', 'RX Bytes', 'RX Packets', 'RX Errs', 'RX Drop', 'RX Fifo', 'RX Frame', 'RX Compressed',
               'RX Multicast', 'TX Bytes', 'TX Packets', 'TX Errs', 'TX Drop', 'TX Fifo', 'TX Colls', 'TX Carrier',
               'TX Compressed', 'Source Line', 'Source File')

    def build(_report, label, item):
        return (item.name, item.rx_bytes, item.rx_packets, item.rx_errs, item.rx_drop, item.rx_fifo, item.rx_frame,
                item.rx_compressed, item.rx_multicast, item.tx_bytes, item.tx_packets, item.tx_errs, item.tx_drop,
                item.tx_fifo, item.tx_colls, item.tx_carrier, item.tx_compressed, item.line, label)
    rows, source = _collect(context, 'interface_counters', None, build)
    return headers, rows, source


@artifact_processor
def bugreport_dns_servers(context):
    headers = ('Net ID', 'Server', 'Total', 'Successes', 'Errors', 'Timeouts', 'Internal Errors', 'RTT Average (ms)',
               'Last Sample (s)', 'Interfaces', 'Search Domains', 'Private DNS Mode', 'Transport Type', 'Metered',
               'Source Line', 'Source File')

    def build(_report, label, item):
        return (item.net_id, item.server, item.total, item.successes, item.errors, item.timeouts, item.internal_errors,
                item.rtt_ms, item.last_sample, item.interfaces, item.search_domains, item.private_mode, item.transport,
                item.metered, item.line, label)
    rows, source = _collect(context, 'dns_servers', 'dnsresolver', build)
    return headers, rows, source


@artifact_processor
def bugreport_private_dns_log(context):
    headers = ('Time Of Day As Printed', 'Net ID', 'Server', 'State', 'Source Line', 'Source File')

    def build(_report, label, item):
        return item.time_text, item.net_id, item.server, item.state, item.line, label
    rows, source = _collect(context, 'private_dns', 'dnsresolver', build)
    return headers, rows, source


@artifact_processor
def bugreport_open_sockets(context):
    headers = ('Protocol', 'Receive Queue', 'Send Queue', 'Local Address', 'Foreign Address', 'State', 'UID', 'Inode',
               'Program', 'Source Line', 'Source File')

    def build(_report, label, item):
        return (item.protocol, item.recv_q, item.send_q, item.local, item.foreign, item.state, item.uid, item.inode,
                item.program, item.line, label)
    rows, source = _collect(context, 'inet_sockets', None, build)
    return headers, rows, source


@artifact_processor
def bugreport_unix_sockets(context):
    headers = ('Protocol', 'Reference Count', 'Flags', 'Socket Type', 'State', 'Inode', 'Program', 'Path (as printed)',
               'Source Line', 'Source File')

    def build(_report, label, item):
        return (item.protocol, item.ref_count, item.flags, item.socket_type, item.state, item.inode, item.program, item.path,
                item.line, label)
    rows, source = _collect(context, 'unix_sockets', None, build)
    return headers, rows, source


@artifact_processor
def bugreport_socket_details(context):
    headers = ('Netid', 'State', 'Receive Queue', 'Send Queue', 'Local Address', 'Peer Address', 'UID', 'Inode', 'Socket',
               'Timer', 'Users', 'Extended Fields', 'Info', 'Source Line', 'Source File')

    def build(_report, label, item):
        return (item.netid, item.state, item.recv_q, item.send_q, item.local, item.peer, item.uid, item.inode, item.socket,
                item.timer, item.users, item.other, item.info, item.line, label)
    rows, source = _collect(context, 'socket_state', None, build)
    return headers, rows, source


@artifact_processor
def bugreport_tethering_log(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Message', 'Source Line', 'Source File')

    def build(report, label, item):
        moment, _note = _wall(report, item.time_text)
        return moment, item.time_text, item.message, item.line, label
    rows, source = _collect(context, 'tethering_log', 'tethering', build)
    return headers, rows, source


@artifact_processor
def bugreport_tethering_state(context):
    headers = ('Group', 'Name', 'Value (as printed)', 'Source Line', 'Source File')

    def build(_report, label, item):
        return item.group, item.name, item.value, item.line, label
    rows, source = _collect(context, 'tethering_state', 'tethering', build)
    return headers, rows, source
