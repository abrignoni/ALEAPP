__artifacts_v2__ = {
    "bugreport_bluetooth_status": {
        "name": "Bug Report - Bluetooth Adapter Status",
        "description": "The adapter status values of the bluetooth_manager service dump in an Android bug report text, "
                       "with the enabled flag, the state, the name and the scan mode as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Bluetooth, NFC and USB",
        "notes": "One row per value of the Bluetooth Status block (enabled, state, address, name, time since enabled), of the line that "
                 "counts the crashes of the Bluetooth process, of the line that counts the registered BLE apps and, once each, of "
                 "these adapter property lines when the dump prints them: ConnectionState, State, ScanMode, "
                 "MaxConnectedAudioDevices, A2dpOffloadEnabled, Discovering, DiscoveryEndMs, SarType and SarStatus. The values are "
                 "as printed and are the state the platform reported when the dump ran: a row says nothing about earlier states "
                 "(see Bug Report - Bluetooth Events for the times the dump lists). The adapter's own hardware address is printed "
                 "in this dump (masked by the platform in some layouts, complete in others) and is shown as printed, like every "
                 "other value here. name is the name the adapter reports for itself, as printed. Values are shown as printed; "
                 "nothing is masked or left out. A dump of an adapter that was never enabled prints only the status block and a sentence saying so.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei on Android 10, Motorola on Android 15 and a Transsion-brand phone on Android 10): 15, 14, 13, 13 and 5 rows, each equal to the lines "
                 "of those kinds counted in the raw text; the Transsion-brand report printed the never-enabled form (5 rows: "
                 "enabled, state, name, the crash count and the BLE app count). Not examined: Android 11, 12 and 14 and other vendors. "
                 "A section that is missing or empty gives no rows, which says nothing about the device."
                 " In a value read from the report text, ASCII control characters other than a tab are shown as spaces, and values longer than the limits named here are cut.\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave 16 rows (not compared with a second count).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "bluetooth",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 16 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_bluetooth_devices": {
        "name": "Bug Report - Bluetooth Devices",
        "description": "The Bonded devices and Other devices lists of the bluetooth_manager service dump in an Android bug "
                       "report text, with the name, address, type, class and profiles as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Bluetooth, NFC and USB",
        "notes": "One row per device line of the lists that the bluetooth_manager service dump heads Bonded devices and Other "
                 "devices. Listed Under is the heading as printed. Name, Address, Address Type, Device Type, Class (as stored), "
                 "Profiles, Packages and Connection State are the parts of the line in the order the layouts print them, and "
                 "none is decoded. The address is the one the dump prints and is partly masked by the platform in three of the "
                 "five tested reports (the first four octets as XX on the Samsung reports, the middle octets as ** on the Huawei "
                 "report), while the Motorola report prints complete addresses. The address of the device's own adapter is not "
                 "reported.\n"
                 "What the columns hold depends on the layout. Address Type was empty on all rows of the Samsung A-series, Huawei "
                 "and Motorola reports. Address Type held one value, Public, on all 36 rows of the Samsung S-series report. "
                 "Connection State was empty on all rows of the Samsung A-series, Huawei and Motorola reports. Connection State "
                 "held one value, ACL BR/EDR:N LE:N, on all 36 rows of the Samsung S-series report. Class (as stored) is the "
                 "class-of-device number the two Samsung layouts print as hexadecimal text, and it was empty on all rows of the "
                 "Huawei and Motorola reports. Profiles is the list of profile or service words after the name (Samsung "
                 "A-series) or on the UUIDs line under the device (Samsung S-series). Profiles was filled on 2 of 2 rows and 4 "
                 "of 36 rows and was empty on all rows of the Huawei and Motorola reports. Packages, from a packages line under "
                 "a device, was filled on 1 of the 36 Samsung S-series rows and was empty on all other rows of all reports. "
                 "Device Type is the word in square brackets. Device Type held one value on all rows of the Huawei report "
                 "(BR/EDR) and one value on all rows of the Motorola report (????, which is how the platform prints a type it "
                 "does not know). Listed Under held one value, Bonded devices, on all rows of the Samsung A-series, Huawei and "
                 "Motorola reports. The Samsung S-series report also prints an Other devices list (31 of its 36 rows). What puts "
                 "a device in the Other devices list is not established here and the heading is shown as printed. Where a "
                 "device name is followed by a comma-separated list in round brackets the Samsung A-series layout is read as "
                 "name and profiles, and a name that itself ends in round brackets is kept whole.\n"
                 "A bonded device is one the platform had a bond for when the dump ran; a device removed earlier has no row, and a "
                 "row does not say when the bond was made or that the device was ever connected. The Transsion-brand report "
                 "prints no list (it never enabled Bluetooth), so it has no rows, which says nothing about the device.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei on Android 10, Motorola on Android 15 and a Transsion-brand phone on Android 10): 2, 36 (5 bonded, 31 other), 7, 3 and 0 rows, each "
                 "equal to the number of device lines counted in the raw text. The Devices in DB list that the two Samsung reports "
                 "also print is not read. Not examined: Android 11, 12 and 14 and other vendors."
                 " In a value read from the report text, ASCII control characters other than a tab are shown as spaces, and values longer than the limits named here are cut.\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave no rows: its Bonded devices list is empty.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "bluetooth",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_bluetooth_events": {
        "name": "Bug Report - Bluetooth Events",
        "description": "The enable log, adapter state records, connection events, bond events and scan mode changes of the "
                       "bluetooth_manager service dump in an Android bug report text.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Bluetooth, NFC and USB",
        "notes": "One row per timed line of five lists of the bluetooth_manager service dump. Event Source says which: Enable "
                 "log, Adapter state (the rec[n] records of the adapter state machine), Connection events, Bond events or Scan "
                 "mode changes. Event is the first word of a connection event (CONNECTED, DISCONNECTED), the Enabled or Disabled "
                 "word or the bracketed action of an enable log line, and the name after what= of an adapter state record; "
                 "Detail is the rest of the line as printed (for an adapter state record, the processed, org and dest states); "
                 "Address is filled for connection events only. A row says that the Bluetooth service logged that "
                 "line at that time; it does not say what a person did.\n"
                 "Time As Printed is month, day and clock time without a year. The year is not in the dump: Time (UTC) uses the "
                 "latest year, the one of the report or the one before, that does not put the time more than a day after the "
                 "report time, then converts with the zone shown in Bug Report - Device Facts; an event more than a year before "
                 "the report would therefore be given a year too late, and the time is empty where the report has no time or no "
                 "zone. All five tested reports record a UTC+0 zone without daylight saving, so the conversion "
                 "was the identity on every real row and offsets were tested on constructed text only. Time Note was empty on all "
                 "rows of all five tested reports.\n"
                 "The lists are what the platform kept: the tested reports printed 0 to 3 enable log lines and up to 4 adapter "
                 "state records, so an event that is not listed says nothing about earlier use. The Connection Events list was "
                 "None on three reports (Samsung A-series, Huawei, Motorola), absent from the Transsion-brand report and held 3 "
                 "lines on the Samsung S-series report, which is why Address was filled on 3 of its 6 rows and "
                 "empty on all rows of the other reports. Four reports printed Total Number of events: 0 under Bond Events and "
                 "the Transsion-brand report prints no such list, so no bond event line was seen on real data; the layout of one "
                 "is not known here and such a line is read as a time and its text (constructed text only). Scan mode changes had "
                 "one line, on the Samsung A-series report.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei on Android 10, Motorola on Android 15 and a Transsion-brand phone on Android 10): 6, 6, 3, 5 and 0 rows, each equal to the "
                 "number of timed lines of those lists counted in the raw text. Not examined: Android 11, 12 and 14, other vendors "
                 "and a time more than a year old."
                 " In a value read from the report text, ASCII control characters other than a tab are shown as spaces, and values longer than the limits named here are cut.\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave 5 rows (not compared with a second count).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "bluetooth",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 5 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_bluetooth_link_keys": {
        "name": "Bug Report - Bluetooth Link Key Types",
        "description": "The Link Key Types list of the bluetooth_manager service dump in an Android bug report text, with "
                       "the BR/EDR and LE key types printed for each address.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Bluetooth, NFC and USB",
        "notes": "One row per address of the Link Key Types list. BR/EDR Key Type is the word printed after BR: (for example "
                 "AUTH_COMB) and LE Key Types the words printed after LE:, both as printed and not decoded; the key values "
                 "themselves are not in the dump. Address is as printed (lower case on the tested reports), with the first four octets masked as xx "
                 "on the Samsung reports and complete on the Motorola report, so a row cannot always be matched to a row of Bug "
                 "Report - Bluetooth Devices by address (the last two octets are the only part the masked form keeps). A row "
                 "says that the platform listed a key type for the address; a device with no row says nothing.\n"
                 "BR/EDR Key Type was empty on 1 of the 5 Samsung S-series rows (a device with only LE key words) and LE Key "
                 "Types was empty on all rows of the Samsung A-series and Motorola reports and on 3 of the 5 Samsung S-series "
                 "rows. The Huawei and Transsion-brand reports print no such list, so they have no rows.\n"
                 "Evidence tiers. Data-proven on three real bug reports (Samsung A-series and S-series on Android 16, Motorola on "
                 "Android 15): 2, 5 and 3 rows, each equal to the number of address lines counted in the raw text; none on the "
                 "two Android 10 reports. Not examined: Android 11, 12 and 14 and other vendors."
                 " In a value read from the report text, ASCII control characters other than a tab are shown as spaces, and values longer than the limits named here are cut.\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave no rows; its Bonded devices list is empty.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "bluetooth",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_nfc_state": {
        "name": "Bug Report - NFC State",
        "description": "The state lines, preferred services and default route of the nfc service dump in an Android bug "
                       "report text, as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Bluetooth, NFC and USB",
        "notes": "One row per line of three parts of the nfc service dump. Group Adapter state holds the key=value and key: "
                 "value lines before the list of card emulation services (for example mState, mScreenState, mTechMask), Group "
                 "Preferred services the lines of the Preferred services part (the current preferred foreground, wallet and "
                 "payment services and the next tap default) and Group Routing table the default route line. Item and Value are "
                 "as printed, and which lines are printed depends on the Android version and the vendor. The values are the "
                 "state when the dump ran: a row says nothing about earlier use. The service-wrapper lines (host process, "
                 "threads, client processes), the AID cache, the routing details, the NFC EE access and UID cache and the "
                 "Samsung extension dump are not read.\n"
                 "Evidence tiers. Data-proven on four real bug reports (Samsung A-series and S-series on Android 16, Huawei on "
                 "Android 10, Motorola on Android 15): 30, 32, 26 and 20 rows, each equal to the lines of those three parts "
                 "counted in the raw text; the Transsion-brand report has no nfc service dump, so it has no rows, which says "
                 "nothing about the device. Not examined: Android 11, 12 and 14 and other vendors."
                 " In a value read from the report text, ASCII control characters other than a tab are shown as spaces, and values longer than the limits named here are cut.\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave 30 rows (not compared with a second count).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "nfc",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 30 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_nfc_services": {
        "name": "Bug Report - NFC Card Emulation Services",
        "description": "The card emulation services of the nfc service dump in an Android bug report text, with each "
                       "service's AID groups, categories and AIDs as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Bluetooth, NFC and USB",
        "notes": "One row per AID of each ComponentInfo entry under the Registered HCE services heading of the nfc service dump, "
                 "and one row with empty AID columns for an entry that lists none. Package and Service are read from the "
                 "ComponentInfo text, Description and UID from the parentheses after it, Host Type from the On Host Service or "
                 "Off-host Service line, AID Group from the Static AID groups or Dynamic AID groups line above the AID, "
                 "Category from the Category line (with its enabled flag) and AID as printed, a hexadecimal text that is not "
                 "decoded or matched to an application here. Settings Activity, Requires Device Unlock and Requires Screen On "
                 "are the lines of those names. A row says that the package registered the service with the NFC service when the "
                 "dump ran; it does not say that the package or the AID was used.\n"
                 "Service List held one value, HCE services (the heading as printed), on all rows of all four reports that print "
                 "the list. Not every layout prints every column. UID was empty on all 3 rows of the Huawei report (an Android "
                 "10 layout). Requires Device Unlock was empty on all 3 rows of the Huawei report. Requires Screen On was empty "
                 "on all 3 rows of the Huawei report. Package held one value on all 3 rows of the Huawei report. AID Group held "
                 "one value, static, on all 3 rows of the Huawei report. Host Type held one value, On Host Service, on all rows "
                 "of the Huawei and Motorola reports. Settings Activity held one value, null, on all rows of the Huawei and "
                 "Motorola reports. Requires Device Unlock held one value, false, on all 12 rows of the Samsung A-series report "
                 "and on all 13 rows of the Motorola report. The Samsung reports also print Off-host Service entries. The "
                 "Samsung S-series report prints 100 rows (89 with an AID), which is the number of rows and not a limit.\n"
                 "Evidence tiers. Data-proven on four real bug reports (Samsung A-series and S-series on Android 16, Huawei on "
                 "Android 10, Motorola on Android 15): 12, 100, 3 and 13 rows, each equal to the number of AID lines plus the "
                 "entries with none, counted in the raw text; the Transsion-brand report has no nfc service dump. Entries "
                 "under the HCE-F heading are read the same way but none was non-empty in the tested reports (constructed text "
                 "only). Not examined: Android 11, 12 and 14 and other vendors."
                 " In a value read from the report text, ASCII control characters other than a tab are shown as spaces, and values longer than the limits named here are cut.\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave 5 rows (not compared with a second count).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "nfc",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 5 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_nfc_events": {
        "name": "Bug Report - NFC Events",
        "description": "The Nfc Event Log of the nfc service dump in an Android bug report text, with the time, event name "
                       "and detail as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Bluetooth, NFC and USB",
        "notes": "One row per line of the Nfc Event Log in the nfc service dump. Event is the first word after the time "
                 "(for example reader_mode_change, bootup_state, aid_registration) and Detail the rest of the line as printed, "
                 "cut at 400 characters. Time As Printed is device wall-clock text with milliseconds and no zone; Time (UTC) "
                 "converts it with the zone shown in Bug Report - Device Facts and is empty where the report records no zone "
                 "(Time Note says so). A row says that the NFC service logged that event; it does not say what caused it. The "
                 "log holds what the platform kept: the two Samsung reports printed exactly 100 entries each, which is "
                 "consistent with a fixed-size buffer but is not verified here, so an event that is not listed says nothing "
                 "about earlier use.\n"
                 "On the Motorola report all 50 entries were bootup_state entries with the same detail text, so Event and "
                 "Detail held one value on all 50 rows of that report. Time Note was empty on all rows of the three reports "
                 "that have rows; all tested reports are in a UTC+0 zone, so the conversion was the identity on every real "
                 "row (other zones tested on constructed text only).\n"
                 "Evidence tiers. Data-proven on three real bug reports (Samsung A-series and S-series on Android 16, Motorola on "
                 "Android 15): 100, 100 and 50 rows, each equal to the number of timed lines counted in the raw text; the "
                 "Huawei report has an nfc dump without this log and the Transsion-brand report no nfc dump, so they have no "
                 "rows. Not examined: Android 11, 12 and 14 and other vendors."
                 " In a value read from the report text, ASCII control characters other than a tab are shown as spaces, and values longer than the limits named here are cut.\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave no rows (why was not examined).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "nfc",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_nfc_driver_log": {
        "name": "Bug Report - NFC Driver Log",
        "description": "The lines of the NFC SYSTEM LOG section of an Android bug report text, with the kernel time and "
                       "the wall time when a line prints one.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Bluetooth, NFC and USB",
        "notes": "One row per non-empty line of the NFC SYSTEM LOG command section (/proc/nfclog, printed by some Samsung "
                 "builds). Kernel Time (as stored) is the text in the first square brackets, seconds on the kernel clock with a B on the early lines, the spaces around it in the brackets removed (not interpreted); Message is the rest of the line, cut at 400 "
                 "characters. About 1 line in 20 also prints a wall time in square brackets (Time As Printed, month, day and "
                 "clock time); Time (UTC) is filled for those lines only, with the year taken as in Bug Report - Bluetooth "
                 "Events, and is empty for a wall time earlier than the device start (the report time minus the printed uptime "
                 "by more than a minute; Time Note says so). The other lines get no time here: the kernel clock of a line is "
                 "not turned into a wall time, because the kernel times and wall times of the USB LOG section of the same "
                 "reports did not agree (see Bug Report - USB Log). The driver messages are as printed and are not interpreted; "
                 "most are the single word clk. The section is a ring buffer, so it covers an unknown span.\n"
                 "Lines without a kernel time are kept as printed with an empty Kernel Time: 3 of the 6,208 lines of the Samsung "
                 "A-series report and 4 of the 4,635 of the Samsung S-series report (a fragment such as the end of a bracketed "
                 "time, or a line of NUL characters). Time As Printed was filled on 309 and 231 rows and Time (UTC) on 309 and "
                 "229. Time Note was filled on 2 rows of the Samsung S-series report. Time Note was empty on all rows of the "
                 "Samsung A-series report. Both reports are in a UTC+0 zone, so the conversion was the identity on every real "
                 "row.\n"
                 "Evidence tiers. Data-proven on two real bug reports (Samsung A-series and S-series on Android 16): 6,208 and "
                 "4,635 rows, each equal to the number of non-empty lines counted in the raw text. The other three reports "
                 "have no such section, so they have no rows, which says nothing about the device. Not examined: other Android "
                 "versions and vendors."
                 " In a value read from the report text, ASCII control characters other than a tab are shown as spaces, and values longer than the limits named here are cut. Kernel Time comes first because every line carries it and it orders the lines; Time (UTC) is often empty (on the corpus it was empty on every row except 190 NFC driver log rows of sharon_a14).\nOn the corpus the Samsung error dumps print this log too: s20fe_a13 gave 562 rows (307 from the dumpState text and 205 and 50 from its two automatically generated dumps), samsungs20_a13 1,067 and sharon_a14 3,828; the partial texts of userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "nfc",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 562 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 1,067 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 3,828 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_usb_state": {
        "name": "Bug Report - USB Manager State",
        "description": "The device, host, port and ALSA manager state of the usb service dump in an Android bug report text "
                       "as path and value, with the USB event list.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Bluetooth, NFC and USB",
        "notes": "One row per key=value line under the device_manager, host_manager, port_manager and alsa_manager parts of the "
                 "USB MANAGER STATE text of the usb service dump. Path is the keys above the line joined with dots (a list of "
                 "ports is numbered [0], [1]) and Value is the text after the equals sign, as printed. The lines of the USB "
                 "Event list (USB Event=[ ... ]) are rows with Path ending in USB Event, the event text in Value and the time "
                 "in Time As Printed (month, day, clock time and milliseconds with no year); Time (UTC) takes the year as in Bug "
                 "Report - Bluetooth Events and Time Note says why a time has no UTC. The settings_manager part (the apps "
                 "registered to be offered when a USB device or accessory is attached) and the permissions_manager part are not "
                 "read. The values are the state when the dump ran (for example connected=false says the port was not "
                 "connected then); a row says nothing about earlier connections, and an unplugged device is not evidence "
                 "that none was used.\n"
                 "Time As Printed and Time (UTC) are filled on the 2 event rows of the Motorola report only. Time As Printed "
                 "was empty on all 28 rows of the Huawei report and on all 14 rows of the Transsion-brand report, which print no "
                 "event list (their Android 10 layout also prints a shorter port_manager part). Time Note was empty on all rows "
                 "of all three reports. All tested reports are in a UTC+0 zone, so the conversion was the identity on every real "
                 "row.\n"
                 "Evidence tiers. Data-proven on three real bug reports (Huawei on Android 10, Motorola on Android 15 and a Transsion-brand phone on Android 10): 28, 14 and 37 rows, each equal to the number of key=value lines and event lines "
                 "under those four parts counted in the raw text. The two Samsung reports have no usb service dump (they have "
                 "the USB LOG section instead), so they have no rows. Not examined: Android 11, 12 and 14 and other vendors."
                 " In a value read from the report text, ASCII control characters other than a tab are shown as spaces, and values longer than the limits named here are cut.\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave 38 rows (not compared with a second count).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "usb",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 38 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_usb_log": {
        "name": "Bug Report - USB Log",
        "description": "The lines of the USB LOG section of an Android bug report text, with the kernel time, the wall time "
                       "when a line prints one and the vendor and product numbers of port events.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Bluetooth, NFC and USB",
        "notes": "One row per non-empty line of the USB LOG command section (/proc/usblog, printed by some Samsung builds). Block "
                 "is the heading the line is under (CCIC EVENT, PCM, EXTRA, or the controller information block), the heading "
                 "lines themselves are rows with their counts as printed, and the time sync line is a row with Block time sync. "
                 "Kernel Time (as stored) is the seconds in the last square brackets, Time As Printed the wall time in the "
                 "first square brackets when a line prints one (month, day and clock time, no year), and Message the rest of the "
                 "line, cut at 400 characters. Event is port connect or port disconnect for those lines, with the Vendor ID and "
                 "Product ID the line prints (for example VID:0x... PID:0x...), which are the manufacturer and product numbers "
                 "of the attached USB device and not its serial number; the other lines (controller notifications, "
                 "device class lines) are kept as printed and not interpreted. Time (UTC) is filled for lines that print a "
                 "wall time, with the year taken as in Bug Report - Bluetooth Events, and is empty with a note for a wall time "
                 "earlier than the device start (the report time minus the printed uptime, by more than a minute).\n"
                 "The wall time of a line is not derived from its kernel time and the time sync line. On the Samsung S-series "
                 "report 1,808 lines print both stamps; the difference between the stamps and the time sync pair agreed within "
                 "one second on 704 of them, so the kernel clock is not treated as a wall clock here. The Samsung A-series "
                 "report prints kernel times only (one wall time, on its time sync line). The blocks are ring buffers (the "
                 "headings print a count and a maximum), so the section covers an unknown span and a missing event says "
                 "nothing about earlier use. A port connect line says that the log recorded a connect with those numbers; it does "
                 "not say what the device was or who attached it.\n"
                 "Event, Vendor ID and Product ID were filled on 14 of the 638 rows of the Samsung A-series report and empty on "
                 "all 1,825 rows of the Samsung S-series report (no port lines). Time Note was filled on 258 rows of the Samsung "
                 "S-series report (wall times earlier than the device start). Time Note was empty on all rows of the Samsung "
                 "A-series report. Both reports are in a UTC+0 zone, so the conversion was the identity on every real row.\n"
                 "Evidence tiers. Data-proven on two real bug reports (Samsung A-series and S-series on Android 16): 638 and "
                 "1,825 rows, each equal to the number of non-empty lines counted in the raw text. The other three reports have "
                 "no such section, so they have no rows, which says nothing about the device. Not examined: other Android "
                 "versions and vendors."
                 " In a value read from the report text, ASCII control characters other than a tab are shown as spaces, and values longer than the limits named here are cut. Kernel Time comes first because every line carries it and it orders the lines; Time (UTC) is often empty (on the corpus it was empty on every row except 190 NFC driver log rows of sharon_a14).\nOn the corpus the Samsung error dumps print this log too: s20fe_a13 gave 294 rows (78 from the dumpState text and 52 and 164 from its two automatically generated dumps), samsungs20_a13 128 and sharon_a14 127; the partial texts of userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "usb",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 294 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 128 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 127 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_telephony_state": {
        "name": "Bug Report - Telephony State",
        "description": "The state values of the telephony.registry, phone, isub and carrier_config service dumps in an "
                       "Android bug report text, as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Telephony",
        "notes": "One row per value line of four service dumps; Service says which. telephony.registry: the m...= lines of "
                 "the last known state of each phone (Phone Id) and of the registry itself (Phone Id empty), such as the call "
                 "state, the service state, the data connection state, the display info and mActiveDataSubId. phone: the "
                 "PhoneGlobals values. isub: the default subscription ids, the SIM slot mapping and the SIM state of each "
                 "slot. carrier_config: the loader's own state lines. Item and Value are as printed; long values (the service "
                 "state, signal strength and cell information texts) are cut at 400 characters. The cell identity and cell "
                 "information values carry the cell identifiers of the serving cell (cell id, tracking area, network codes); "
                 "they are network identifiers, not subscriber identifiers, and are reported as printed. The call states and "
                 "service states are the values when the dump ran and say nothing about earlier calls or coverage.\n"
                 "Values are shown as printed; nothing is masked or left out, including the number after mCallIncomingNumber "
                 "(empty on the three reports that print it) and any phone number, IMSI or ICCID that a value holds. The "
                 "emergency number list is not read.\n"
                 "Phone Id was empty on all 21 rows of the Samsung A-series report and all 20 rows of the Samsung S-series "
                 "report: those two reports have no telephony.registry dump, so their rows come from the isub, phone and "
                 "carrier_config dumps, which print no per-phone state. Value is empty where the platform printed an empty "
                 "value (2, 2 and 3 rows of the Huawei, Motorola and Transsion-brand reports).\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei on Android 10, Motorola on Android 15 and a Transsion-brand phone on Android 10): 21, 20, 45, 106 and 71 rows, each equal to the "
                 "state lines of those dumps counted in the raw text with the same line patterns. Not examined: Android 11, 12 "
                 "and 14, other vendors and a call in progress when the dump ran (mCallIncomingNumber was empty on every report that prints it)."
                 " In a value read from the report text, ASCII control characters other than a tab are shown as spaces, and values longer than the limits named here are cut.\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave 54 rows (not compared with a second count).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "phone",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 54 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_sim_subscriptions": {
        "name": "Bug Report - SIM Subscriptions",
        "description": "The subscription lists of the isub service dump in an Android bug report text, with "
                       "the slot, carrier, network codes, ICCID, IMSI, phone number and card string as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-31",
        "requirements": "none",
        "category": "Android Bug Report - Telephony",
        "notes": "One row per subscription line of the Active subscriptions and All subscriptions lists (ActiveSubInfoList and "
                 "AllSubInfoList on the Android 10 reports) of the isub service dump; Listed In says which list (a "
                 "subscription in both lists has a row in each). Subscription Id, Slot Index (-1 for a subscription with no "
                 "slot), Carrier Id, Display Name, Carrier Name, MCC, MNC, Country, Data Roaming, Type and Embedded are the "
                 "values printed for those keys, not decoded. ICCID, IMSI, Phone Number (the number or mNumber key), Card String and "
                 "Number From Carrier are the values printed on each line for iccId, imsi, number, cardString and numberFromCarrier, "
                 "with any bracketed platform mask kept; they are subscriber identifiers, and values are shown as printed, with "
                 "nothing masked or left out. A row says "
                 "that the subscription database held that record when the dump ran; a subscription with a slot of -1 is one "
                 "the platform remembers, and a row does not say that a SIM was in the phone then or at any time.\n"
                 "Layouts differ: the Android 15 and 16 reports print SubscriptionInfoInternal records (Type holds LOCAL_SIM, "
                 "Embedded 0) and the Android 10 reports print an older record in which the same keys are spelled differently "
                 "(Type holds the subscription type number, Embedded false). Type held one value on every row of each of the "
                 "five reports (LOCAL_SIM on the Android 15 and 16 reports, 0 on the two Android 10 reports). Embedded held one "
                 "value on every row of each of the five reports (0 on the Android 15 and 16 reports, false on the two Android "
                 "10 reports). Data Roaming held one value on every row of the Samsung A-series, Samsung S-series, Huawei and "
                 "Transsion-brand reports. MCC and Country held one value on every row of the Samsung A-series and "
                 "Transsion-brand reports. Carrier Id, MNC, Display Name and Carrier Name held one value on every row of the "
                 "Transsion-brand report. The Huawei report prints *** (the platform's own masking) in Carrier Id, Display Name, "
                 "Carrier Name, MCC, MNC and Country on all 3 rows. Display Name and Carrier Name were identical on all rows of "
                 "the Samsung A-series and Transsion-brand reports.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei on Android 10, Motorola on Android 15 and a Transsion-brand phone on Android 10): 6, 7, 3, 7 and 4 rows, each equal to the number "
                 "of subscription lines counted in the raw text. Not examined: Android 11, 12 and 14, other vendors, an embedded "
                 "(eSIM) subscription and a work profile."
                 " In a value read from the report text, ASCII control characters other than a tab are shown as spaces, and values longer than the limits named here are cut.\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave no rows: its isub dump prints no subscription.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "device-sim",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_carrier_config": {
        "name": "Bug Report - Carrier Config Values",
        "description": "The values the carrier configuration sources set in the carrier_config service dump in an Android "
                       "bug report text, and the cached configuration files it lists.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Telephony",
        "notes": "One row per key = value line printed under mConfigFromDefaultApp, mConfigFromOemApp, mConfigFromCarrierApp, "
                 "mPersistentOverrideConfigs, mOverrideConfigs and mNoSimConfig of each phone in the carrier_config service "
                 "dump (Source is that name; most of these print null and give no row), and one row per cached configuration "
                 "file (Source Cached config files, Key the file name, Value its modified time). Phone Id is empty on the "
                 "cached file rows and where the dump does not name a phone. Key and Value are as printed, keys cut at 150 "
                 "characters (a file name at 200) and values at 400 (a cached file's Value, which keeps its modified time= "
                 "label, at 100). The block of default values that the platform prints before them (720 lines for each of the two "
                 "phones of the Samsung A-series report, 734 lines with no phone named on the Samsung S-series report, 315 lines "
                 "for the one phone of the Huawei report, 895 for each phone of the Motorola report and 364 for each phone of "
                 "the Transsion-brand report) is the platform's default table and is counted in the log and not listed. A "
                 "value is a configuration setting the source applied; it does not say that the feature is in use. The "
                 "sources are packages of the system or of the carrier and not a person, so the rows describe the carrier "
                 "profile that was applied and do not show what the phone was used for. The cached file names contain the "
                 "SIM's ICCID; they are shown as printed, with nothing masked.\n"
                 "Source held one value, mConfigFromDefaultApp, on all rows of the Huawei and Transsion-brand reports, and Phone "
                 "Id held one value, 0, on all rows of the Huawei report (the Huawei and Transsion-brand layouts print no cached "
                 "file list). The log lines of the loader are rows of Bug Report - Telephony Service Logs.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei on Android 10, Motorola on Android 15 and a Transsion-brand phone on Android 10): 55, 66, 33, 26 and 62 rows, each equal to the "
                 "number of key = value lines under those sources plus the cached file lines, counted in the raw text. Not "
                 "examined: Android 11, 12 and 14, other vendors and a carrier app that sets values on a device with an active "
                 "carrier override."
                 " In a value read from the report text, ASCII control characters other than a tab are shown as spaces, and values longer than the limits named here are cut.\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave 22 rows (not compared with a second count).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "settings",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 22 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_telephony_logs": {
        "name": "Bug Report - Telephony Service Logs",
        "description": "The timestamped log lines of the telephony.registry, phone, isub, isms, carrier_config and telecom "
                       "service dumps in an Android bug report text.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Telephony",
        "notes": "One row per line that starts with a date and time (YYYY-MM-DDTHH:MM:SS.ffffff - text) in six service dumps; "
                 "Service says which and Heading is the last heading line above the row (for example local logs:, "
                 "mDataRoamingNotifLog:, CarrierConfigLoader local log=). Message is the text after the dash, cut at 1,000 "
                 "characters. The lines are the platform's own local logs: service state and data connection changes, roaming "
                 "status, SIM and carrier configuration events, the SMS handler's delivery lines (the receiving package, not "
                 "the message) and call focus changes. A row says that the service logged the text at that time; it does not say "
                 "what caused it. The logs are bounded buffers, so an event that is not listed says nothing about earlier "
                 "activity. Time As Printed is device wall-clock text and Time (UTC) converts it with the zone shown in Bug "
                 "Report - Device Facts (empty, with Time Note, where the report records no zone); Time Note was empty on all rows "
                 "of all five tested reports, which are in a UTC+0 zone, so the conversion was the identity on every real row.\n"
                 "Message may contain phone numbers, SIM and subscriber identifiers (the subscription and SMS logs do) and "
                 "message ids; it is shown as printed, with nothing masked or left out.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei on Android 10, Motorola on Android 15 and a Transsion-brand phone on Android 10): 199, 350, 24, 588 and 213 rows, each equal to "
                 "the number of date-and-time lines counted in the raw text in those six dumps. The telephony.registry and "
                 "telecom dumps are missing from the two Samsung reports. Not examined: Android 11, 12 and 14, other vendors and "
                 "log lines with another timestamp layout, which are not read."
                 " In a value read from the report text, ASCII control characters other than a tab are shown as spaces, and values longer than the limits named here are cut.\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave 133 rows (not compared with a second count).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 133 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_telephony_state_records": {
        "name": "Bug Report - Telephony State Machine Records",
        "description": "The state machine records (rec[n] lines) of the isms and other telephony service dumps in an Android "
                       "bug report text, with the time, states and event name as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Telephony",
        "notes": "One row per rec[n] line (time=MM-DD HH:MM:SS.mmm processed=... org=... dest=... what=...) of the state "
                 "machines in the telephony service dumps. State Machine is the heading above the total records line (for "
                 "example the inbound SMS or cell broadcast handler), Position the number n, Processed In, From and To the "
                 "processed, org and dest states and Message the what= text (an event name such as EVENT_NEW_SMS or a number), "
                 "all as printed and not decoded. A record says that the handler's state machine logged that transition; the "
                 "records hold no message text, sender or recipient. A handler lists a short history: the dump prints a total "
                 "records count that can be larger than the records it lists (the Samsung S-series report says 144 and lists 20 "
                 "for each of two handlers), so a transition that is not listed says nothing about earlier activity.\n"
                 "Time As Printed has no year: Time (UTC) takes it as in Bug Report - Bluetooth Events. Time Note was empty on all "
                 "rows of all five tested reports, which are in a UTC+0 zone, so the conversion was the identity on every real "
                 "row. In the tested reports every row came from the isms dump (Service held one value, isms, on all rows of all "
                 "five reports) and Processed In and From were identical on every row of all five reports.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei on Android 10, Motorola on Android 15 and a Transsion-brand phone on Android 10): 20, 56, 4, 48 and 8 rows, each equal to the "
                 "number of rec[n] lines counted in the raw text in the six telephony dumps. Not examined: Android 11, 12 and 14, "
                 "other vendors, and records in the phone, isub, telecom, carrier_config or telephony.registry dumps, which the "
                 "tested reports did not print."
                 " In a value read from the report text, ASCII control characters other than a tab are shown as spaces, and values longer than the limits named here are cut.\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave 10 rows (not compared with a second count).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "message",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 10 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_telecom_accounts": {
        "name": "Bug Report - Telecom Phone Accounts",
        "description": "The registered phone accounts of the telecom service dump in an Android bug report text, with the "
                       "calling package, capabilities and schemes as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Telephony",
        "notes": "One row per PhoneAccount line of the PhoneAccountRegistrar part of the telecom service dump. Package and "
                 "Service are read from the ComponentInfo text, Account Id is the id after it (the platform prints "
                 "*** for most of them), User the UserHandle number, Enabled Mark the character inside the first brackets "
                 "(X or a space), and Capabilities, Audio Routes, Schemes, Extras and Restrictions the text after those names, "
                 "as printed and cut at 200, 60, 100, 400 and 100 characters in that order; the group id is not read. "
                 "A row says that the package registered a "
                 "calling account with the telecom service; it does not say that the account was used to place or receive a call. "
                 "Calls (the Analytics and Historical Events parts, which print the call addresses) are not read.\n"
                 "Enabled Mark held one value, X, and Audio Routes one value, BESW, on all rows of the three reports that have rows "
                 "(2, 12 and 2); Restrictions held [NONE] on all 12 rows of the Motorola report and was empty on all rows of the "
                 "Huawei and Transsion-brand reports, whose layout does not print it.\n"
                 "Evidence tiers. Data-proven on three real bug reports (Huawei on Android 10, Motorola on Android 15 and a Transsion-brand phone on Android 10): 2, 12 and 2 rows, each equal to the number of PhoneAccount lines counted in the raw text; the "
                 "two Samsung reports have no telecom dump, so they have no rows. Not examined: Android 11, 12 and 14 and other "
                 "vendors. Calls were printed on one report only and are not read."
                 " In a value read from the report text, ASCII control characters other than a tab are shown as spaces, and values longer than the limits named here are cut.\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints this section; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not. s20fe_a13 gave 1 row.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "phone",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 1 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_radio_state_log": {
        "name": "Bug Report - Radio Log State Lines",
        "description": "The lines of the RADIO LOG section of an Android bug report text that carry the tags of the service, "
                       "network, data and subscription state trackers.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Telephony",
        "notes": "One row per line of the RADIO LOG command section (logcat -b radio) whose tag starts with one of these "
                 "state tracker tags: SST, ServiceStateTracker, SSCtr, NetworkTypeController, DNC-, DN-, DefaultPhoneNotifier, "
                 "LocaleTracker, NitzStateMachineImpl, PhoneSwitcher, SubscriptionController, SubscriptionManagerService, "
                 "TelephonyRegistry, TelephonyNetworkFactory, DIC-, TelephonyCountryDetector, CellularNetworkService, NRM- and "
                 "ImsPhone. The lines of every other tag (the modem request and response traces, the AT command trace, SMS and "
                 "SIM phone book handling, the chatty lines) are not read, and the log says how many lines of the section were "
                 "listed: 8,262 of 16,773, 7,441 of 12,788, 230 of 4,051, 2,095 of 6,678 and 317 of 3,130 on the Samsung A-series, "
                 "Samsung S-series, Huawei, Motorola and Transsion-brand reports. The tag list was chosen on these five reports "
                 "and is this plugin's rule, not a statement of the platform; a tag a vendor uses for the same job and that is "
                 "not on the list gives no row. UID, PID, TID, Level, Tag and Message are the logcat columns as printed; Message "
                 "is cut at 1,000 characters. A row says that the process logged the text at that time; it does not say what "
                 "caused it. The log is a bounded buffer: the lines of the tested reports span from about 12 minutes (Samsung "
                 "S-series) to about an hour (Huawei) by their first and last printed times.\n"
                 "Time As Printed is month, day and clock time without a year: Time (UTC) takes the year as in Bug Report - "
                 "Bluetooth Events. Time Note was empty on all rows of all five reports, which are in a UTC+0 zone, so the "
                 "conversion was the identity on every real row. On the Huawei report UID, PID, TID and Level each held one value "
                 "on all 230 rows (the uid word radio, one process id, one thread id and the level E); Level held one value, D, "
                 "on all 7,441 rows of the Samsung S-series report.\n"
                 "Message is shown as printed, with nothing masked or left out (the subscription tags print the ICCID and "
                 "IMSI).\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei on Android 10, Motorola on Android 15 and a Transsion-brand phone on Android 10): 8,262, 7,441, 230, 2,095 and 317 rows, each equal "
                 "to the number of lines with a listed tag counted in the raw text. The Huawei report prints no duration line "
                 "for the section (the log says so). Not examined: Android 11, 12 and 14 and other vendors."
                 " In a value read from the report text, ASCII control characters other than a tab are shown as spaces, and values longer than the limits named here are cut.\nOn the corpus every bug report text prints this log: s20fe_a13 gave 1,777 rows (549 from the dumpState text and 434 and 794 from its two automatically generated dumps), samsungs20_a13 1,361, sharon_a14 6,214 and the two partial texts of userb2_a13 1,285 and 1,212. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "radio",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 1,777 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 1,361 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 6,214 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 2,497 rows",
        }
    },
}

import re
from datetime import timedelta

from scripts import dumpstate_reader
from scripts.ilapfuncs import artifact_processor, logfunc


UPTIME_PART = re.compile(r'(\d+)\s+(week|day|hour|minute)s?')
NOTE_CLOCK_NOT_SET = 'earlier than the device start (report time minus the printed uptime): no UTC value'


def _reports(context):
    """The bug report texts among the staged files, as (Source File label, Report) pairs."""
    return dumpstate_reader.load_reports(context.get_files_found(), context.get_relative_path, logfunc)


def _source_path(context, reports):
    """The staged files that were read; the matched files when none was a bug report."""
    paths = [report.source.path for _label, report in reports] or sorted(str(path) for path in context.get_files_found())
    return '\n'.join(dict.fromkeys(str(path) for path in paths))


def _rows(report, table):
    """The rows of one table of the radios readers (empty when the report has none)."""
    return getattr(report, table, [])


def _checks(label, report, kind, name, lines=()):
    """Say once when the section is missing, was cut by the platform, has no duration line, or has no duration line."""
    messages = []
    sections = [section for section in report.sections if section.kind == kind and section.name == name]
    if not sections:
        messages.append(f'Bug report {label}: no {name} section in this report, so there are no rows from it')
    for section in sections:
        if kind == 'service' and section.timeout_ms:
            if not lines or any(section.line < number < section.end_line for number in lines):
                messages.append(f'Bug report {label}: the {name} service dump was cut by a {section.timeout_ms} ms timeout, '
                                f'the rows from it may be partial')
        elif kind == 'command' and section.duration is None:
            messages.append(f'Bug report {label}: the {name} section has no duration line (the platform prints one when a '
                            f'section finishes, some builds print none), so it cannot be shown to be complete')
    for message in messages:
        dumpstate_reader.say_once(logfunc, message)


def _wall(report, text):
    """``(UTC datetime or None, note)`` for a device wall time such as ``2026-10-25 06:05:38.007`` or ``2026-10-25T06:05:38``."""
    value = str(text).strip().replace('T', ' ')
    if value in dumpstate_reader.UNSET_WALL_TIMES:
        return None, dumpstate_reader.NOTE_UNSET
    if dumpstate_reader.parse_wall_time(value) is None:
        return None, dumpstate_reader.NOTE_NOT_A_TIME
    if not report.clock.known:
        return None, dumpstate_reader.NOTE_NO_ZONE
    moment = report.clock.to_utc(value)
    return moment, '' if moment is not None else dumpstate_reader.NOTE_NONEXISTENT


def _boot_wall(report):
    """The device wall time at which the device started (report time minus the printed uptime), or None."""
    uptime = next((fact.value for fact in report.facts if fact.name == 'Uptime'), '')
    report_time = dumpstate_reader.parse_wall_time(report.report_wall)
    units = {'week': 604800, 'day': 86400, 'hour': 3600, 'minute': 60}
    found = UPTIME_PART.findall(uptime)
    if report_time is None or not found:
        return None
    return report_time - timedelta(seconds=sum(int(number) * units[unit] for number, unit in found))


def _month_day(report, text, not_before=None):
    """``(UTC datetime or None, note)`` for a time printed without a year (``10-25 06:05:38.007``).

    ``not_before`` is a device wall time: a printed time earlier than it (by more than a minute) was printed before the
    device clock was set, so it gets no UTC value.
    """
    value = str(text).strip()
    if value.count(':') == 3:                      # the USB manager prints the milliseconds after a colon
        head, _, tail = value.rpartition(':')
        value = head + '.' + tail
    full, moment = report.setting_change_time(value)
    if not full:
        return None, 'no report time to take the year from: no UTC value'
    if not_before is not None and dumpstate_reader.parse_wall_time(full) < not_before - timedelta(minutes=1):
        return None, NOTE_CLOCK_NOT_SET
    if moment is None:
        return None, dumpstate_reader.NOTE_NO_ZONE
    return moment, ''


# ---------------------------------------------------------------------------------------------
# Bluetooth
# ---------------------------------------------------------------------------------------------
@artifact_processor
def bugreport_bluetooth_status(context):
    headers = ('Item', 'Value', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _checks(label, report, 'service', 'bluetooth_manager')
        for item in _rows(report, 'bt_status'):
            rows.append((item.item, item.value, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_bluetooth_devices(context):
    headers = ('Listed Under', 'Name', 'Address', 'Address Type', 'Device Type', 'Class (as stored)',
               'Profiles', 'Packages', 'Connection State', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _checks(label, report, 'service', 'bluetooth_manager')
        for item in _rows(report, 'bt_devices'):
            rows.append((item.list_name, item.name, item.address, item.address_type, item.device_type, item.device_class,
                         item.profiles, item.packages, item.connection, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_bluetooth_events(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Event Source', 'Event', 'Address', 'Detail',
               'Time Note', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _checks(label, report, 'service', 'bluetooth_manager')
        for item in _rows(report, 'bt_events'):
            moment, note = _month_day(report, item.time_text)
            rows.append((moment, item.time_text, item.source, item.event, item.address, item.detail, note, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_bluetooth_link_keys(context):
    headers = ('Address', 'BR/EDR Key Type', 'LE Key Types', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _checks(label, report, 'service', 'bluetooth_manager')
        for item in _rows(report, 'bt_link_keys'):
            rows.append((item.address, item.br_key, item.le_key, item.line, label))
    return headers, rows, _source_path(context, reports)


# ---------------------------------------------------------------------------------------------
# NFC
# ---------------------------------------------------------------------------------------------
@artifact_processor
def bugreport_nfc_state(context):
    headers = ('Group', 'Item', 'Value', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _checks(label, report, 'service', 'nfc')
        for item in _rows(report, 'nfc_state'):
            rows.append((item.group, item.item, item.value, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_nfc_services(context):
    headers = ('Package', 'Service', 'Description', 'UID', 'Service List', 'Host Type', 'AID Group', 'Category', 'AID',
               'Settings Activity', 'Requires Device Unlock', 'Requires Screen On', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _checks(label, report, 'service', 'nfc')
        for item in _rows(report, 'nfc_services'):
            rows.append((item.package, item.component, item.description, item.uid, item.service_list, item.host,
                         item.aid_group, item.category, item.aid, item.settings_activity, item.requires_unlock,
                         item.requires_screen_on, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_nfc_events(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Event', 'Detail', 'Time Note', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _checks(label, report, 'service', 'nfc')
        for item in _rows(report, 'nfc_events'):
            moment, note = _wall(report, item.time_text)
            rows.append((moment, item.time_text, item.event, item.detail, note, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_nfc_driver_log(context):
    headers = ('Kernel Time (as stored)', ('Time (UTC)', 'datetime'), 'Time As Printed', 'Message', 'Time Note', 'Source Line',
               'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _checks(label, report, 'command', 'NFC SYSTEM LOG')
        boot = _boot_wall(report)
        for item in _rows(report, 'nfc_driver_log'):
            moment, note = _month_day(report, item.wall_text, boot) if item.wall_text else (None, '')
            rows.append((item.kernel_time, moment, item.wall_text, item.message, note, item.line, label))
    return headers, rows, _source_path(context, reports)


# ---------------------------------------------------------------------------------------------
# USB
# ---------------------------------------------------------------------------------------------
@artifact_processor
def bugreport_usb_state(context):
    headers = ('Path', 'Value', 'Time As Printed', ('Time (UTC)', 'datetime'), 'Time Note', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _checks(label, report, 'service', 'usb')
        for item in _rows(report, 'usb_state'):
            moment, note = _month_day(report, item.time_text) if item.time_text else (None, '')
            rows.append((item.path, item.value, item.time_text, moment, note, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_usb_log(context):
    headers = ('Block', 'Kernel Time (as stored)', 'Time As Printed', ('Time (UTC)', 'datetime'), 'Event', 'Vendor ID',
               'Product ID', 'Message', 'Time Note', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _checks(label, report, 'command', 'USB LOG')
        boot = _boot_wall(report)
        for item in _rows(report, 'usb_log'):
            moment, note = _month_day(report, item.wall_text, boot) if item.wall_text else (None, '')
            rows.append((item.block, item.kernel_time, item.wall_text, moment, item.event, item.vendor_id, item.product_id,
                         item.message, note, item.line, label))
    return headers, rows, _source_path(context, reports)


# ---------------------------------------------------------------------------------------------
# Telephony
# ---------------------------------------------------------------------------------------------
def _telephony_checks(label, report, services):
    for service in services:
        _checks(label, report, 'service', service)


@artifact_processor
def bugreport_telephony_state(context):
    headers = ('Service', 'Phone Id', 'Item', 'Value', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _telephony_checks(label, report, ('telephony.registry', 'phone', 'isub', 'carrier_config'))
        for item in _rows(report, 'telephony_state'):
            rows.append((item.service, item.phone, item.item, item.value, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_sim_subscriptions(context):
    headers = ('Subscription Id', 'Slot Index', 'Listed In', 'Carrier Id', 'Display Name', 'Carrier Name', 'MCC', 'MNC',
               'Country', 'Data Roaming', 'Type', 'Embedded', 'ICCID', 'IMSI', 'Phone Number', 'Card String',
               'Number From Carrier', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _telephony_checks(label, report, ('isub',))
        for item in _rows(report, 'sim_subscriptions'):
            rows.append((item.sub_id, item.slot_index, item.list_name, item.carrier_id, item.display_name, item.carrier_name,
                         item.mcc, item.mnc, item.country_iso, item.data_roaming, item.sub_type, item.embedded, item.iccid,
                         item.imsi, item.phone_number, item.card_string, item.number_from_carrier, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_carrier_config(context):
    headers = ('Phone Id', 'Source', 'Key', 'Value', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _telephony_checks(label, report, ('carrier_config',))
        for phone, count in sorted(getattr(report, 'carrier_default_counts', {}).items()):
            logfunc(f'Bug report {label}: the default values block of the carrier_config dump '
                    f'(phone {phone or "not named"}: {count} lines) is counted and not listed')
        for item in _rows(report, 'carrier_values'):
            rows.append((item.phone, item.source, item.key, item.value, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_telephony_logs(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Service', 'Heading', 'Message', 'Time Note', 'Source Line',
               'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _telephony_checks(label, report, ('telephony.registry', 'phone', 'isub', 'isms', 'carrier_config', 'telecom'))
        for item in _rows(report, 'telephony_logs'):
            moment, note = _wall(report, item.time_text)
            rows.append((moment, item.time_text, item.service, item.heading, item.message, note, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_telephony_state_records(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Service', 'State Machine', 'Position', 'Processed In', 'From',
               'To', 'Message', 'Time Note', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _telephony_checks(label, report, ('isms', 'phone', 'isub', 'telecom', 'carrier_config', 'telephony.registry'))
        for item in _rows(report, 'state_records'):
            moment, note = _month_day(report, item.time_text)
            rows.append((moment, item.time_text, item.service, item.machine, item.position, item.processed, item.origin,
                         item.destination, item.what, note, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_telecom_accounts(context):
    headers = ('Package', 'Service', 'Account Id', 'User', 'Enabled Mark', 'Capabilities', 'Audio Routes',
               'Schemes', 'Extras', 'Restrictions', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _telephony_checks(label, report, ('telecom',))
        for item in _rows(report, 'telecom_accounts'):
            rows.append((item.package, item.component, item.account_id, item.user, item.enabled, item.capabilities,
                         item.audio_routes, item.schemes, item.extras, item.restrictions, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_radio_state_log(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'UID', 'PID', 'TID', 'Level', 'Tag', 'Message', 'Time Note',
               'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _checks(label, report, 'command', 'RADIO LOG')
        counts = getattr(report, 'radio_log_counts', None)
        if counts:
            dumpstate_reader.say_once(logfunc, f'Bug report {label}: {counts[1]} of {counts[0]} lines of the RADIO LOG '
                                               f'section are listed (only the tags of the state trackers are read)')
        for item in _rows(report, 'radio_log'):
            moment, note = _month_day(report, item.time_text)
            rows.append((moment, item.time_text, item.uid, item.pid, item.tid, item.level, item.tag, item.message, note,
                         item.line, label))
    return headers, rows, _source_path(context, reports)
