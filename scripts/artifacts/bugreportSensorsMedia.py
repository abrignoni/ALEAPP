__artifacts_v2__ = {
    "bugreport_location_providers": {
        "name": "Bug Report - Location Providers",
        "description": "The location providers listed in the location service dump of an Android bug report text, with the "
                       "state, identity and properties lines as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Location and Sensors",
        "notes": "One row per provider block (passive, network, fused, gps and, on some builds, others) of the location service "
                 "dump (DUMP OF SERVICE location). Two layouts are read. The layout headed Location Manager State (Android 12 "
                 "and later in the tested reports) prints for each provider a service line, a listeners list, allowed, "
                 "identity, properties and, for some providers, target service, connected, stationary throttled and mStarted; "
                 "the layout headed Current Location Manager state (the two Android 10 reports) prints useable, enabled and "
                 "an object name instead of properties. Service State is the text after service:, Allowed, Identity, "
                 "Properties, Target Service, Connected, Stationary Throttled and Started are the values printed (Started is "
                 "mStarted), Useable and Enabled are the values of the older layout, and Listeners counts the listener lines "
                 "under the provider (the lines themselves are in Bug Report - Location Requests). A column that the layout of "
                 "a report does not print is empty. The per-user last locations and enabled lines are in Bug Report - "
                 "Location Last Known.\n"
                 "A row records what the location service held for that provider when the dump ran. It does not say who "
                 "used a provider, when, or whether location was switched on for the user: the Location Setting lines of the "
                 "dump, the Geofence Manager and the GNSS statistics are not read. The platform cuts a service dump after a "
                 "time limit; a cut dump is logged, and a missing row is not evidence that a provider is absent.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): Allowed held one "
                 "value on all rows of the Samsung A-series, Samsung S-series and Motorola reports; Listeners held one value "
                 "on all rows of the Huawei and Transsion-brand reports; Useable held one value on all rows of the Transsion- "
                 "brand report; Enabled held one value on all rows of the Transsion-brand report; Useable was empty on all "
                 "rows of the Samsung A-series, Samsung S-series and Motorola reports; Enabled was empty on all rows of the "
                 "Samsung A-series, Samsung S-series and Motorola reports; Stationary Throttled was empty on all rows of the "
                 "Samsung A-series, Samsung S-series, Huawei and Transsion-brand reports; Service State was empty on all rows "
                 "of the Huawei and Transsion-brand reports; Allowed was empty on all rows of the Huawei and Transsion-brand "
                 "reports; Identity was empty on all rows of the Huawei and Transsion-brand reports; Properties was empty on "
                 "all rows of the Huawei and Transsion-brand reports; Target Service was empty on all rows of the Huawei and "
                 "Transsion-brand reports; Connected was empty on all rows of the Huawei and Transsion-brand reports.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 4, 4, 5, 4 and 4 rows, equal to a count of "
                 "provider headings in the raw text. Not examined: Android 11, 12 and 14, other vendors, and providers other than "
                 "the four named. None of the five dumps was cut by the time limit; the cut case was built on constructed "
                 "text only."
                 "\nOn the corpus the run gave s20fe_a13 4 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 4 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_location_last_known": {
        "name": "Bug Report - Location Last Known",
        "description": "The last location text that the location service dump of an Android bug report prints for each "
                       "provider and user, with the printed latitude, longitude, accuracy and elapsed time.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Location and Sensors",
        "notes": "One row per last location=Location[...] line under a provider and user of the Location Providers part of the "
                 "location service dump, and one per line of the Last Known Locations and Last Known Locations Coarse Intervals "
                 "lists of the older layout. List says which part printed the row, User is the Android user of the layout that "
                 "prints one (empty in the older layout and where a provider prints one line for all users). Enabled is the enabled= "
                 "line printed for that provider and user. Last Location (as printed) is the whole text (cut at 900 characters; "
                 "it can hold nested bundle text). Location Provider, Latitude, Longitude, Accuracy and Elapsed Time are taken "
                 "from it as printed, from the provider word, the two numbers after it, hAcc= and et=. A row with an enabled "
                 "line and no location text is kept, with empty location columns.\n"
                 "These columns are text copied from the dump. No coordinate is calculated, converted, rounded, geocoded or "
                 "checked here; one of the five reports (Huawei) prints its coordinates with asterisks in place of digits and they "
                 "are shown that way. Elapsed Time is the duration text of et= and is not turned into a clock time: the dump "
                 "does not print the time of the fix next to it, so there is no Time (UTC) column, no map output and no "
                 "timeline entry. A last location is the position the service kept for that provider when the dump ran; it does "
                 "not say when the device was there, which app asked for it, or that the user was at that place.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): List held one value "
                 "on all rows of the Samsung A-series, Samsung S-series and Motorola reports; Enabled held one value on all "
                 "rows of the Samsung A-series, Samsung S-series and Motorola reports; Last Location (as printed) held one "
                 "value on all rows of the Samsung A-series report; Latitude (as printed) held one value on all rows of the "
                 "Huawei report; Longitude (as printed) held one value on all rows of the Huawei report; User was empty on all "
                 "rows of the Samsung A-series, Samsung S-series and Huawei reports; Location Provider (as printed) was empty "
                 "on all rows of the Samsung A-series report; Latitude (as printed) was empty on all rows of the Samsung "
                 "A-series report; Longitude (as printed) was empty on all rows of the Samsung A-series report; Accuracy (as "
                 "printed) was empty on all rows of the Samsung A-series report; Elapsed Time (as printed) was empty on all "
                 "rows of the Samsung A-series report; Enabled was empty on all rows of the Huawei report.\n"
                 "Evidence tiers. Data-proven on four of five real bug reports (Samsung A-series and S-series on Android 16, "
                 "Huawei on Android 10, Motorola on Android 15): 4, 4, 6 and 8 rows, equal to a count of last location lines in "
                 "the raw text; the Transsion-brand report (Android 10) printed empty last known lists and has no rows, which says "
                 "nothing about the device. The Samsung and Huawei dumps print one line per provider for all users, so User is empty on "
                 "their rows; the Motorola dump prints two users (0 and 11) with the same text for both. The Samsung A-series "
                 "dump printed a null last location for its four providers (Location Provider, Latitude, Longitude, Accuracy "
                 "and Elapsed Time are empty on those rows, as Location Setting was printed false there), and Accuracy and "
                 "Elapsed Time were filled on every row of the other three reports. Enabled is false on the four rows of the Samsung "
                 "A-series report, true on every row of the Samsung S-series and Motorola reports and empty on every row of the "
                 "Huawei report, whose older layout prints no enabled line there. Not examined: Android 11, 12 "
                 "and 14, other vendors."
                 "\nOn the corpus the run gave s20fe_a13 4 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 4 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_location_requests": {
        "name": "Bug Report - Location Requests",
        "description": "The location requests that the location service dump of an Android bug report lists for each provider, "
                       "with the requesting uid, package, request text and flags as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Location and Sensors",
        "notes": "One row per listener line under a provider's listeners: list (Location Providers part) and, in the older layout, "
                 "one per UpdateRecord line of the Active Records by Provider list. UID, Package, Attribution Tag (the text in "
                 "square brackets after the package) and Listener ID come from the identity text uid/package[tag]/id; Flags are the "
                 "words in brackets or braces between the identity and the request (for example a coarse mark or {bg}); Request "
                 "(as printed) is the Request[...] text, Quality and Interval are its first words (a request quality word, and "
                 "the text after @ where one is printed), Min Update Interval and Min Update Distance are the values printed with "
                 "those names, State is the foreground or background word of the older layout, and Work Source is the "
                 "WorkSource{...} text.\n"
                 "The rows are the requests that were registered when the dump ran. They do not show what was delivered to an "
                 "app, whether the app used the result, or any past request; the requests that came and went earlier are in "
                 "Bug Report - Location Events. An app that is not listed made no request at that moment, which says nothing "
                 "about earlier use. Quality words are the platform's own and are not explained here.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): List held one value "
                 "on all rows of the Samsung A-series, Samsung S-series, Huawei, Transsion-brand and Motorola reports; "
                 "Provider held one value on all rows of the Huawei and Transsion-brand reports; UID held one value on all "
                 "rows of the Transsion-brand report; Package held one value on all rows of the Transsion-brand report; "
                 "Quality held one value on all rows of the Transsion-brand report; State held one value on all rows of the "
                 "Transsion-brand report; State was empty on all rows of the Samsung A-series, Samsung S-series and Motorola "
                 "reports; Attribution Tag was empty on all rows of the Huawei and Transsion-brand reports; Listener ID was "
                 "empty on all rows of the Huawei and Transsion-brand reports; Flags was empty on all rows of the Huawei and "
                 "Transsion-brand reports; Interval (as printed) was empty on all rows of the Huawei and Transsion-brand "
                 "reports; Min Update Interval was empty on all rows of the Huawei and Transsion-brand reports; Min Update "
                 "Distance was empty on all rows of the Huawei and Transsion-brand reports; Work Source was empty on all rows "
                 "of the Transsion-brand report.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 4, 14, 6, 2 and 6 rows, equal to the number "
                 "of listener lines (Android 12 and later layout) or UpdateRecord lines (Android 10 layout) in the raw text. "
                 "Attribution Tag, Flags and Listener ID are empty on every row of the older layout, which does not print them, "
                 "and Work Source is filled on one of its 8 rows. Not examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus the run gave s20fe_a13 5 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 5 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_location_events": {
        "name": "Bug Report - Location Events",
        "description": "The Event Log of the location service dump of an Android bug report: provider enable, request "
                       "registration and delivery lines with their time.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Location and Sensors",
        "notes": "One row per line of the Event Log part of the location service dump. Provider is the provider named at the start of "
                 "the line (empty where the line names none, for example a user visibility line). Event is the text after the "
                 "provider: +registration and -registration (a request registered or removed), request (the provider request "
                 "that changed), enabled and similar words, or a delivered-location line; Client is the uid/package[tag]/id "
                 "text of a registration or delivery, and Detail is the Request[...] text printed after an arrow, or the "
                 "rest of the line. Time As Printed is month, day and clock time with milliseconds and no year; Time (UTC) uses "
                 "the latest year, the one of the report or the one before, that does not put the line more than a day after the "
                 "report time, and then converts with the zone shown in Bug Report - Device Facts. The time is empty where the "
                 "report has no time or no zone.\n"
                 "The log is a ring of the most recent events, so it covers a few hours or days only and an earlier request is "
                 "not in it (the tested logs held 13 to 1,000 lines; 1,000 lines on one report suggests that the ring was full, "
                 "which was not confirmed). A row records that the location service noted the event; it does not show that the "
                 "device was moving, where it was, or what an app did with a fix. The older layout (Android 10) prints no event "
                 "log, so its table is empty, which says nothing about the device.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): no column was empty "
                 "or uniform.\n"
                 "Evidence tiers. Data-proven on three real bug reports (Samsung A-series and S-series on Android 16, Motorola "
                 "on Android 15): 13, 1,000 and 395 rows, each equal to a count of timestamped lines of the Event Log in the "
                 "raw text; none on the two Android 10 reports. All five reports record a UTC+0 zone, so the conversion to UTC "
                 "was the identity on real rows; offsets and daylight saving were tested on constructed text only. Not examined: "
                 "Android 11, 12 and 14 and other vendors."
                 "\nOn the corpus the run gave s20fe_a13 25 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "map-pin",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 25 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_location_usage": {
        "name": "Bug Report - Location Usage",
        "description": "The per-client usage totals that the location service dump of an Android bug report prints for each "
                       "provider, as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Location and Sensors",
        "notes": "One row per client line of the Historical Aggregate Location Provider Data part of the location service dump "
                 "(Android 12 and later layout) and per line of the Historical Records by Provider list (Android 10 layout). "
                 "Client is the uid/package[tag] text or the package name as printed. In the newer layout the Min Interval, Max "
                 "Interval, Total Duration, Active Duration and Foreground Duration columns hold the values of the printed "
                 "min/max interval and total/active/foreground duration fields and Locations holds the printed count; in "
                 "the older layout the line is free text and it is kept whole in Detail (as printed), with the other columns "
                 "empty. Durations are duration text and are not summed or converted. The totals cover the period the platform "
                 "keeps, which the dump does not state in the newer layout and states in minutes in the older one; a client "
                 "with no row made no request in that period.\n"
                 "A row says that the service totalled that client's requests; it does not show what the client was used for, "
                 "where the device was, or that a fix reached the app (the Locations count is the number the line prints).\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): List held one value "
                 "on all rows of the Samsung A-series, Samsung S-series, Huawei and Motorola reports; Active Duration held one "
                 "value on all rows of the Samsung A-series report; Locations held one value on all rows of the Samsung "
                 "A-series report; Detail (as printed) was empty on all rows of the Samsung A-series, Samsung S-series and "
                 "Motorola reports; Min Interval was empty on all rows of the Huawei report; Max Interval was empty on all "
                 "rows of the Huawei report; Total Duration was empty on all rows of the Huawei report; Active Duration was "
                 "empty on all rows of the Huawei report; Foreground Duration was empty on all rows of the Huawei report; "
                 "Locations was empty on all rows of the Huawei report.\n"
                 "Min Interval and Max Interval were identical on all 4 rows of the Samsung A-series report.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 4, 20, 8, 1 and 12 rows, equal to a count of "
                 "client lines in the raw text. Not examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus the run gave s20fe_a13 7 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "map-pin",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 7 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_time_zone_detection": {
        "name": "Bug Report - Time Zone Detection State",
        "description": "The provider configuration, controller state and state histories printed in the "
                       "location_time_zone_manager dump of an Android bug report.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Location and Sensors",
        "notes": "One row per item of the location_time_zone_manager service dump: the mode and package name of the primary and "
                 "secondary provider configuration, the controller state and user configuration, each State history entry of the "
                 "controller and of each provider, each provider's current state, and its target service and connected lines. Component says whether the row belongs to the "
                 "controller or to a provider, Item names the printed field, Index is the number before the @ of a history "
                 "entry, Elapsed (as printed) is the duration text after it (a time since boot, not a clock time) and Value (as "
                 "printed) is the state text, cut at 900 characters. A provider state can carry the time zone ids that the provider "
                 "suggested, as printed inside that text.\n"
                 "The entries are the service's own state changes; they have no clock time in the dump, so there is no Time (UTC) "
                 "column. A row says what state the service reported; it does not say that location was used, or where the "
                 "device was. A time zone id inside a value is a suggestion printed by the service and is not checked here.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): no column was empty "
                 "or uniform.\n"
                 "Evidence tiers. Data-proven on three real bug reports (Samsung A-series and S-series on Android 16, Motorola on "
                 "Android 15): 14, 14 and 19 rows, equal to a count of the printed items. The two Android 10 reports have no such "
                 "service dump and no rows, which says nothing about the device. Not examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus the run gave s20fe_a13 15 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "clock",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 15 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_sensors": {
        "name": "Bug Report - Sensors",
        "description": "The sensor list of the sensorservice dump of an Android bug report, with the type, vendor, rates and "
                       "the active state printed for each sensor.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Location and Sensors",
        "notes": "One row per sensor of the Sensor List part of the sensorservice dump. Handle, Name, Vendor, Version, Type (as "
                 "printed, with the platform's type number in brackets), Permission and Flags (as stored; a hexadecimal text, not "
                 "decoded) are the first printed line of the sensor; Reporting Mode is the first word of the second line "
                 "(continuous, on-change, one-shot or special-trigger) and Capabilities (as printed) is that whole line (rates, "
                 "FIFO sizes and the wake-up word). Active Count, the sampling and batching periods and Connections are joined by "
                 "handle from the Sensor Device and Active sensors parts of the dump: a sensor with no entry there has empty "
                 "columns, which means that the dump listed it as not active when it ran. Sensor names and vendors are the "
                 "device's own, so a list is also a hardware fact of the device.\n"
                 "A row says that the sensor service listed the sensor and what was active when the dump ran. It does not show "
                 "who used a sensor in the past (see Bug Report - Sensor Registrations) or what a sensor measured.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): Vendor held one value "
                 "on all rows of the Transsion-brand report; Version held one value on all rows of the Transsion-brand report; "
                 "Active Count was empty on all rows of the Transsion-brand report; Sampling Periods (ms) was empty on all "
                 "rows of the Transsion-brand report; Selected Sampling (ms) was empty on all rows of the Transsion-brand "
                 "report; Batching Periods (ms) was empty on all rows of the Transsion-brand report; Selected Batching (ms) "
                 "was empty on all rows of the Transsion-brand report; Connections was empty on all rows of the Transsion- "
                 "brand report.\n"
                 "Active Count and Connections were identical on every row of the Samsung A-series, Huawei and Motorola "
                 "reports (each active sensor listed as many connections as active requests).\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 37, 41, 35, 31 and 47 rows, equal to a count of "
                 "sensor heading lines in the raw text. The Huawei list prints its first handle as ten decimal digits and the "
                 "others as 0x hexadecimal; the join by handle treats both as numbers. Not examined: Android 11, 12 and 14, other "
                 "vendors."
                 "\nOn the corpus the run gave s20fe_a13 38 rows and userb2_a13 84 rows (42 from a partial text, 42 from a partial text); samsungs20_a13 and sharon_a14 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cpu",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 38 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 84 rows",
        }
    },
    "bugreport_sensor_connections": {
        "name": "Bug Report - Sensor Connections",
        "description": "The sensor connections that the sensorservice dump of an Android bug report lists, with the client "
                       "label, uid and the sensors each connection holds.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Location and Sensors",
        "notes": "One row per sensor held by a Connection Number block of the sensorservice dump (a connection with no sensor "
                 "line gets one row with empty sensor columns). Operating Mode, Client (as printed; a class name or a short "
                 "obfuscated label chosen by the app, not a package name), UID, Has Sensor Access (the has sensor access: value "
                 "of the newer lines), Sensor, Handle, Status (the status: value), First Flush Pending (the first flush pending: "
                 "value of the newer lines) and Pending Flush Events are the printed values; a column the build does not print is empty. The client label is app-defined text and is not mapped to a package here: the UID "
                 "can be matched to a package with Bug Report - Installed Packages.\n"
                 "The rows are the connections open when the dump ran. They do not show how long a sensor was used or what it "
                 "measured; closed connections are partly recorded in Bug Report - Sensor Registrations.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): Operating Mode held "
                 "one value on all rows of the Samsung A-series, Samsung S-series, Huawei and Motorola reports; Has Sensor "
                 "Access held one value on all rows of the Samsung A-series report; First Flush Pending held one value on all "
                 "rows of the Samsung A-series report; Pending Flush Events held one value on all rows of the Samsung "
                 "A-series, Huawei and Motorola reports; Status held one value on all rows of the Huawei and Motorola reports; "
                 "Status was empty on all rows of the Samsung A-series and Samsung S-series reports; Has Sensor Access was "
                 "empty on all rows of the Huawei and Motorola reports; First Flush Pending was empty on all rows of the "
                 "Huawei and Motorola reports.\n"
                 "Evidence tiers. Data-proven on four of five real bug reports (Samsung A-series and S-series on Android 16, "
                 "Huawei on Android 10, Motorola on Android 15): 7, 20, 14 and 22 rows, equal to a count of sensor lines in the "
                 "connection blocks of the raw text. The Transsion-brand report printed 0 connections. Not examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus the run gave s20fe_a13 10 rows and userb2_a13 14 rows (9 from a partial text, 5 from a partial text); samsungs20_a13 and sharon_a14 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cpu",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 10 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 14 rows",
        }
    },
    "bugreport_sensor_registrations": {
        "name": "Bug Report - Sensor Registrations",
        "description": "The Previous Registrations list of the sensorservice dump of an Android bug report: the clock time (with month and day where printed), "
                       "sign, handle, pid, uid, rates and client as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Location and Sensors",
        "notes": "One row per line of the Previous Registrations list. Clock Time (as printed) is hours, minutes and seconds with no "
                 "date on the tested reports, and month, day, hours, minutes, seconds and milliseconds with no year on the "
                 "Samsung Android 13 report of s20fe_a13, which also prints the sensor in square brackets at the end of the "
                 "line (read into Sensor). With no year, or no date, there is no Time (UTC) column and the rows cannot be placed on a "
                 "timeline here; the list is printed newest first and holds the platform's most recent entries only (500 lines "
                 "on three of the tested reports, 200 on the Huawei report). Sign (as printed) is the + or - character of the line. "
                 "From the platform's own dump code, + is understood to mark an activation and - a deactivation; this was not "
                 "checked against the published source here, and the real rows agree with it only in that + rows carry sampling "
                 "and batching values and - rows carry N/A or none. Handle, PID, UID, Sampling Period, Batching Period and Result "
                 "are as printed (periods in microseconds, or N/A). Sensor and Package or Class (as printed) come from the "
                 "(sensor, package) text of the newer layout or from package= in the Android 10 layout; the text is app-defined "
                 "and is not mapped to a package name here.\n"
                 "A row records that the sensor service noted the registration change at that time of day; it does not show "
                 "what was measured, whether a person was using the device, or on which day.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): Result held one value "
                 "on all rows of the Samsung A-series and Samsung S-series reports; Result was empty on all rows of the Huawei "
                 "and Motorola reports; Sensor was empty on all rows of the Huawei and Motorola reports.\n"
                 "Evidence tiers. Data-proven on four real bug reports (Samsung A-series and S-series on Android 16, Huawei on "
                 "Android 10, Motorola on Android 15): 500, 500, 200 and 500 rows, equal to a count of registration lines in the "
                 "raw text; the Transsion-brand report printed an empty list. Sensor is empty on every row of the Huawei and Motorola reports, "
                 "whose layout does not print it. Not examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus the run gave s20fe_a13 36 rows, equal to the lines of its Previous Registrations list, and userb2_a13 140 rows (85 and 55 from its two partial texts, not compared with a second count); samsungs20_a13 and sharon_a14 gave none.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "cpu",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 36 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 140 rows",
        }
    },
    "bugreport_sensor_events": {
        "name": "Bug Report - Sensor Events",
        "description": "The Recent Sensor events lists of the sensorservice dump of an Android bug report: event number, "
                       "timestamp, wall time and values as printed for each sensor.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Location and Sensors",
        "notes": "One row per event line under a sensor heading (name: last N events) of the Recent Sensor events part. Event "
                 "Number is the number printed on the line, Timestamp (as printed) is the ts= value (seconds, the platform's "
                 "event clock, not converted), Wall Clock (as printed) is the wall= text and Values (as printed) holds the "
                 "numbers after it, cut at 200 characters. The values are not decoded: what they mean depends on the sensor "
                 "type (shown in Bug Report - Sensors) and no unit or axis is assumed here. At most 100 lines per sensor are read.\n"
                 "Wall Clock is month, day and clock time on the Samsung reports and clock time only on the others; Time (UTC) "
                 "is filled for the dated form only (year chosen as for Bug Report - Location Events, zone from Bug Report - "
                 "Device Facts) and is empty for the clock-time-only form, which carries no date. The events are the last few "
                 "the service kept for each sensor, so they say nothing about use outside that stretch. A trigger-sensor "
                 "event records that the sensor reported; it does not say what caused it.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): Time Note held one "
                 "value on all rows of the Huawei and Motorola reports; Time Note was empty on all rows of the Samsung "
                 "A-series and Samsung S-series reports; Time (UTC) was empty on all rows of the Huawei and Motorola reports.\n"
                 "Evidence tiers. Data-proven on four real bug reports (Samsung A-series and S-series on Android 16, Huawei on "
                 "Android 10, Motorola on Android 15): 430, 1,261, 295 and 315 rows, equal to a count of event lines in the raw "
                 "text (at most 100 lines per sensor were printed, which is the number the cap allows); the Transsion-brand report printed an empty "
                 "list. The conversion to UTC was the identity on real rows (UTC+0 zone on all five reports). Not examined: "
                 "Android 11, 12 and 14, other vendors."
                 "\nOn the corpus the run gave s20fe_a13 264 rows and userb2_a13 221 rows (139 from a partial text, 82 from a partial text); samsungs20_a13 and sharon_a14 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "cpu",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 264 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 221 rows",
        }
    },
    "bugreport_camera_events": {
        "name": "Bug Report - Camera Service Events",
        "description": "The camera service events log of an Android bug report: client connect and disconnect lines, device "
                       "additions and user switches with their time.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Camera and Media",
        "notes": "One row per line of the Camera service events log (most recent at top) of the media.camera dump. Event is the "
                 "first word after the time (CONNECT, DISCONNECT, ADD, USER_SWITCH, Device State was changed, and others the "
                 "platform prints); Device, Package, PID and Priority are read from the line where it prints them and Detail is "
                 "the text after the event word. Time As Printed is month, day and second with no year; Time (UTC) uses the latest "
                 "year that does not put the line more than a day after the report time, converted with the zone shown in Bug "
                 "Report - Device Facts.\n"
                 "A CONNECT line records that the camera service noted a client of that package opening that camera device and a "
                 "DISCONNECT line that it closed it. The log does not show what the camera captured, whether anything was "
                 "recorded or saved, or the facing of device numbers. The log is short (5 to 51 lines in the tested reports), "
                 "so the absence of a package says nothing about earlier use. Priority is printed only on the newer connect "
                 "lines and is empty elsewhere.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): Priority was empty on "
                 "all rows of the Huawei, Transsion-brand and Motorola reports; Package was empty on all rows of the "
                 "Transsion-brand report; PID was empty on all rows of the Transsion-brand report.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 24, 51, 18, 5 and 40 rows, equal to a count of "
                 "timestamped lines of the log in the raw text. The Transsion-brand log holds device additions and one user "
                 "switch only (no CONNECT line). Not examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus the run gave s20fe_a13 20 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "camera",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 20 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_camera_devices": {
        "name": "Bug Report - Camera Devices",
        "description": "The open or closed state of each camera device in the media.camera dump of an Android bug report, with "
                       "the client details printed for an open device.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Camera and Media",
        "notes": "One row per Camera device N dynamic info block of the media.camera dump. State is closed or open as printed in "
                 "the Device N is line; for an open device Opened (as printed) is the time of that line, and Package, PID, UID, "
                 "Priority Score and Device Status are the Client package, Client PID, Current client UID, Client priority score "
                 "and Device status lines under it. Part is current for the live dump and previous open session for the saved dump "
                 "that the Samsung builds append under the line Dumpsys from previous open session. The Active Camera Clients "
                 "list was printed as [] in all five tested reports and has no rows.\n"
                 "A row is the state when the dump ran (or, for the previous open session part, when that session was saved). A "
                 "closed device says nothing about earlier use; the connect and disconnect history is in Bug Report - Camera "
                 "Service Events. The hardware static information, stream and vendor tag parts of the dump are not read.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): Part held one value "
                 "on all rows of the Samsung A-series, Huawei, Transsion-brand and Motorola reports; State held one value on "
                 "all rows of the Samsung A-series, Huawei, Transsion-brand and Motorola reports; Opened (as printed) was "
                 "empty on all rows of the Samsung A-series, Huawei, Transsion-brand and Motorola reports; Package was empty "
                 "on all rows of the Samsung A-series, Huawei, Transsion-brand and Motorola reports; PID was empty on all rows "
                 "of the Samsung A-series, Huawei, Transsion-brand and Motorola reports; UID was empty on all rows of the "
                 "Samsung A-series, Huawei, Transsion-brand and Motorola reports; Priority Score was empty on all rows of the "
                 "Samsung A-series, Huawei, Transsion-brand and Motorola reports; Device Status was empty on all rows of the "
                 "Samsung A-series, Huawei, Transsion-brand and Motorola reports.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 9, 15, 5, 2 and 3 rows, equal to a count of "
                 "device blocks in the raw text. An open device with a client was seen on one report only (Samsung S-series, in "
                 "the previous open session part), so the client columns hold a value on one row of the tested data and are empty "
                 "elsewhere; State held closed on every other row. Not examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus the run gave s20fe_a13 12 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "camera",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 12 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_audio_events": {
        "name": "Bug Report - Audio Events",
        "description": "The timestamped lines of the event logs in the audio service dump of an Android bug report: audio focus, "
                       "playback, recording, devices, volume and mute.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Camera and Media",
        "notes": "One row per timestamped line under an Events log (or Audio event log) heading of the audio service dump. Log is the "
                 "heading's name (for example focus commands as seen by MediaFocusControl, playback activity as reported through "
                 "PlayerBase, recording activity received by AudioService, volume changes, mute commands, wired/A2DP/hearing aid "
                 "device connection); the builds print different sets of logs. Event is the line after the time, cut at 600 characters. UID and PID are "
                 "read from uid/pid:N/N, uid/pid N/N or uid:N where the line prints one and are empty otherwise. Time As "
                 "Printed is month, day and clock time with milliseconds (a few logs print a year, which is then used as printed); "
                 "Time (UTC) uses the year rule and the zone as in Bug Report - Location Events.\n"
                 "The logs are short rings (up to 200 lines per log in the tested reports), so each covers minutes to days and an "
                 "unlisted event says nothing about earlier use. A row records that the audio service noted the line; a focus request "
                 "or a player line does not say what was heard, and a recording line does not say what was recorded. Device "
                 "addresses in the logs are printed with the leading bytes masked by the platform. Logs of other kinds that "
                 "print no time on their lines are not read.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): no column was empty "
                 "or uniform.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 266, 719, 164, 58 and 347 rows, equal to a count "
                 "of timestamped lines in the audio dump of the raw text. Not examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus the run gave s20fe_a13 75 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "volume-2",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 75 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_audio_clients": {
        "name": "Bug Report - Audio Clients",
        "description": "The notification clients and global session references that the media.audio_flinger dump of an Android "
                       "bug report lists, with pid, uid and name.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Camera and Media",
        "notes": "One row per line of the Notification Clients table (pid, uid, name) and of the Global session refs table (session, "
                 "count, pid, uid, name) of the media.audio_flinger dump. List says which table. Name is the process or package "
                 "label the platform prints (a shared uid label such as android.uid.system can stand for several packages). "
                 "Session and Count are empty for the first table.\n"
                 "A row records that the audio server held a registration for that process when the dump ran; it does not say that "
                 "the process played or recorded anything. The thread, effect, patch, setParameters and binder profile parts of "
                 "the dump are not read.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): List held one value "
                 "on all rows of the Samsung A-series report; Session was empty on all rows of the Samsung A-series report; "
                 "Count was empty on all rows of the Samsung A-series report.\n"
                 "Evidence tiers. Data-proven on three real bug reports (Samsung A-series and S-series on Android 16, Motorola on "
                 "Android 15): 3, 24 and 16 rows, equal to a count of the table lines in the raw text. The two Android 10 reports "
                 "print no such rows in their audio_flinger dump. Not examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus the run gave s20fe_a13 7 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "volume-2",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 7 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_media_sessions": {
        "name": "Bug Report - Media Sessions",
        "description": "The media sessions listed in the media_session dump of an Android bug report, with owner, package, "
                       "state, audio attributes and metadata as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Camera and Media",
        "notes": "One row per session block of the media_session dump: a heading of the form tag package/tag (userId=N) followed by "
                 "its detail lines. Session is the tag, Key the package/tag text, Role names the global priority session or the "
                 "media button session where the dump marks the block so; Owner PID, Owner UID, Package, Active, Flags (as "
                 "stored), Playback State (as printed), Audio Attributes, Volume (as printed) and Metadata (as printed) are the "
                 "lines printed in the block. Metadata is app-supplied text (a title or description) and is shown cut at 400 "
                 "characters.\n"
                 "The rows are the sessions that existed when the dump ran. The tested lists were short (1 or 2 sessions), "
                 "mostly the platform's own headset button session, so a short list says nothing about earlier use; the order in "
                 "which apps last played audio is in Bug Report - Audio Playback Order. A row does not show what was played.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): User held one value "
                 "on all rows of the Samsung S-series and Huawei reports; Volume (as printed) held one value on all rows of "
                 "the Samsung S-series and Huawei reports; Active held one value on all rows of the Huawei report; Playback "
                 "State (as printed) held one value on all rows of the Huawei report; Metadata (as printed) held one value on "
                 "all rows of the Huawei report.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 1, 2, 2, 1 and 1 rows, equal to a count of "
                 "session headings in the raw text. Metadata held an empty or null value on all rows of the tested reports except "
                 "one. Not examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus the run gave s20fe_a13 1 row; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "play-circle",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 1 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_audio_playback_order": {
        "name": "Bug Report - Audio Playback Order",
        "description": "The Audio playback list (lastly played comes first) of the media_session dump of an Android bug report: "
                       "the uids and the packages that share each uid, in the printed order.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Camera and Media",
        "notes": "One row per uid= packages= line under the heading Audio playback (lastly played comes first). Position is 1 for the "
                 "first line printed, which the heading says is the most recent. UID and Packages are as printed; Packages lists "
                 "every package that shares the uid (a shared uid label can list many, cut at 600 characters).\n"
                 "The dump prints no time, so the rows give an order only: it does not say when any uid played, for how long, "
                 "or what was played. The platform keeps a short list (1 to 6 lines in the tested reports); an app that is not "
                 "listed may have played earlier, or not at all.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): no column was empty "
                 "or uniform.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 2, 2, 2, 1 and 6 rows, equal to a count of the "
                 "lines in the raw text. Not examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus the run gave s20fe_a13 1 row; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "play-circle",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 1 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_media_metrics": {
        "name": "Bug Report - Media Metrics",
        "description": "The records kept in the media.metrics dump of an Android bug report: key, time, owner and the properties "
                       "as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Camera and Media",
        "notes": "One row per numbered record of the media.metrics dump. Two layouts are read. Record Form name, time, owner "
                 "(Android 15 and 16 in the tested reports) is {key, (time), (owner, pid, uid), (properties)}: Key is the record "
                 "kind (for example audio.track.N, codec, extractor, audio.mode), Time As Printed is month, day and clock time "
                 "with milliseconds and Time (UTC) uses the year rule and the zone as in Bug Report - Location Events. Record Form "
                 "colon separated (Android 10) is [version:key:N:uid:package:version code:pid:flag:time:count:properties]: Time "
                 "As Printed is the 19-digit number, read as nanoseconds since the Unix epoch for Time (UTC) when it falls "
                 "between 2009 and 2100. The positions of UID, Package and PID in that layout are read from the printed order "
                 "and were checked against the camera service events log on the Huawei report (the camera package, its uid "
                 "and its pid agree); the other fields of the layout are not named. Package is the owner label the record "
                 "carries (it can be a shared uid label such as android.uid.system); Properties (as printed) is the key=value "
                 "text of the record, cut at 1,500 characters.\n"
                 "The records are the most recent ones the service kept (38 to 2,500 in the tested reports; the service says "
                 "how many it discarded). A record says that the media metrics service received a record of that kind from "
                 "that owner at that time; it does not say what was played, recorded or decoded, or by whom beyond the owner "
                 "label. Properties can hold app-supplied text. Record No. is the number printed before the record.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): Record Form held one "
                 "value on all rows of the Samsung A-series, Samsung S-series, Huawei, Transsion-brand and Motorola reports.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 2,500, 2,500, 300, 38 and 2,000 rows, equal to a "
                 "count of numbered record lines in the raw text. Not examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus the run gave s20fe_a13 474 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "bar-chart-2",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 474 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_accessibility_services": {
        "name": "Bug Report - Accessibility Services",
        "description": "The installed, bound, enabled, binding and crashed accessibility service lists of the accessibility "
                       "dump of an Android bug report.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Display and Input",
        "notes": "One row per service component in the installed services list and, where a list is not empty, in the Bound, "
                 "Enabled, Binding and Crashed services lists of the current user's state in the accessibility service dump. User "
                 "is the currentUserId value, List names the list, Index is the number printed before an installed service "
                 "(for the other lists the order printed), Component is the package/class text and Tags (as printed) is the "
                 "bracketed word after an installed service (for example A11yTool; the meaning of that word is the platform's and "
                 "is not explained here).\n"
                 "An installed service is one the platform lists as available on the device when the dump ran, not one that is "
                 "switched on. The Bound, Enabled, Binding and Crashed lists were printed empty in all five tested reports, "
                 "so those lists have no rows; that is the state when the dump ran, not evidence that no service was ever "
                 "enabled (the enabled_accessibility_services setting, if the report prints it, is a row of Bug Report - "
                 "Settings). The log says when a list was printed empty. The registered client lists and the magnification and "
                 "shortcut state of the dump are not read.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): User held one value "
                 "on all rows of the Samsung A-series and Samsung S-series reports; List held one value on all rows of the "
                 "Samsung A-series and Samsung S-series reports; Tags (as printed) held one value on all rows of the Samsung "
                 "A-series report.\n"
                 "Evidence tiers. Data-proven on two real bug reports (Samsung A-series and S-series on Android 16): 4 and 5 rows, "
                 "all List installed, equal to a count of the numbered lines of the installed services list. The three other "
                 "reports (Android 10 and 15) print no installed services list, so they have no rows. Not examined: a report "
                 "with a non-empty Enabled or Bound list (the parsing of those lists is built on constructed text only), "
                 "Android 11, 12 and 14 and other vendors."
                 "\nOn the corpus the run gave s20fe_a13 5 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "eye",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 5 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_input_methods": {
        "name": "Bug Report - Input Methods",
        "description": "The input methods listed in the input_method dump of an Android bug report, with the service, package, "
                       "uid and version as printed and a mark for the one the dump names as current.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Display and Input",
        "notes": "One row per InputMethod #N block of the input_method service dump (the dump is printed twice in the Samsung and "
                 "Motorola reports, and each copy lists the input methods, so every method then has two rows that differ in Source "
                 "Line). Input Method ID is mId, Settings Activity is mSettingsActivityName, Package, Service and Permission are the "
                 "first packageName, name and permission lines of the ServiceInfo, UID and Version Code come from the "
                 "ApplicationInfo lines. Selected is true when mId equals the mSelectedMethodId (Android 16) or mCurMethodId "
                 "value the dump prints, false when it prints one and it differs, and empty when it prints none.\n"
                 "The rows are the input methods the platform listed when the dump ran. A listed method is installed and "
                 "known to the input method service; it is not necessarily enabled for the user. The Selected mark is the "
                 "dump's value at that moment. The client lists, window and editor state of the dump are not read. The system "
                 "voice typing and autofill services appear as input methods in some dumps.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): Permission held one "
                 "value on all rows of the Samsung A-series, Samsung S-series, Huawei and Motorola reports.\n"
                 "Evidence tiers. Data-proven on four real bug reports (Samsung A-series and S-series on Android 16, Huawei on "
                 "Android 10, Motorola on Android 15): 10, 12, 2 and 10 rows, equal to a count of InputMethod headings in the raw "
                 "text. The Transsion-brand report prints an input_method dump of two lines and no methods. Not examined: "
                 "Android 11, 12 and 14, other vendors."
                 "\nOn the corpus the run gave s20fe_a13 4 rows and userb2_a13 2 rows (1 from a partial text, 1 from a partial text); samsungs20_a13 and sharon_a14 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "type",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 4 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 2 rows",
        }
    },
    "bugreport_input_start_history": {
        "name": "Bug Report - Input Start History",
        "description": "The mStartInputHistory entries of the input_method dump of an Android bug report: time, reason, input "
                       "method and the target window package.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Display and Input",
        "notes": "One row per StartInput #N entry under mStartInputHistory. Entry is the number, Time As Printed is the time= text "
                 "(a device wall-clock time with milliseconds and a year), converted to Time (UTC) with the zone shown in Bug "
                 "Report - Device Facts. Reason, Restarting, Soft Input Mode, Input Type, IME Options, Field ID and Field Name are "
                 "the printed values (hexadecimal texts are not decoded); Input Method is the bracketed component after imeToken= "
                 "and Target Window is the bracketed text after targetWin=, which on the tested reports is a package name or "
                 "package/activity. Field names are app-defined text.\n"
                 "An entry records that the input method service started input for a window of that target at that time. It "
                 "does not record what was typed: no text is in the dump. The history is the service's own ring (up to 32 entries per "
                 "copy of the dump in the Android 16 and 15 reports, 16 in the Android 10 report), so it covers minutes to hours. "
                 "The Samsung and Motorola dumps are printed twice, so entries in both copies appear twice with different Source "
                 "Line values.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): Restarting held one "
                 "value on all rows of the Samsung A-series, Samsung S-series, Huawei and Motorola reports; Input Method held "
                 "one value on all rows of the Samsung A-series, Samsung S-series, Huawei and Motorola reports; Field Name "
                 "held one value on all rows of the Samsung A-series, Samsung S-series, Huawei and Motorola reports.\n"
                 "Evidence tiers. Data-proven on four real bug reports (Samsung A-series and S-series on Android 16, Huawei on "
                 "Android 10, Motorola on Android 15): 64, 64, 16 and 64 rows, equal to a count of StartInput headings in the raw "
                 "text; the Transsion-brand report has none. The conversion to UTC was the identity on real rows (UTC+0 zone). "
                 "Not examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus the run gave s20fe_a13 8 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "type",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 8 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_soft_input_history": {
        "name": "Bug Report - Soft Input History",
        "description": "The mSoftInputShowHideHistory entries of the input_method dump of an Android bug report: time, show or "
                       "hide reason, requesting uid and pid and the window names.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Display and Input",
        "notes": "One row per SoftInputShowHide #N entry under mSoftInputShowHideHistory. Entry is the number, Time As Printed is the "
                 "time= text (a device wall-clock time with milliseconds and a year) converted to Time (UTC) with the zone shown "
                 "in Bug Report - Device Facts. Reason is the printed reason word (for example SHOW_SOFT_INPUT or HIDE_SOFT_INPUT), "
                 "Requesting UID and Requesting PID come from the requestClient line, Focused Window and IME Control Target are "
                 "the focusedWindowName and imeControlTargetName texts (a window hash, a package and an activity) and Editor Info "
                 "is the editorInfo text. They are as printed and the window names can carry app-defined text.\n"
                 "An entry records that the service was asked to show or hide the soft keyboard for that window at that time; it "
                 "does not record any typed text, and a show request is not proof that a keyboard was seen. The history is a ring "
                 "of the last 32 entries per copy of the dump, so it covers minutes to hours; the Samsung and Motorola dumps are "
                 "printed twice, so entries can appear twice with different Source Line values.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): Requesting UID held "
                 "one value on all rows of the Motorola report; Requesting PID held one value on all rows of the Motorola "
                 "report; Focused Window held one value on all rows of the Motorola report; IME Control Target held one value "
                 "on all rows of the Motorola report; Editor Info held one value on all rows of the Motorola report.\n"
                 "Focused Window and IME Control Target were identical on all 32 rows of the Samsung A-series report.\n"
                 "Evidence tiers. Data-proven on three real bug reports (Samsung A-series and S-series on Android 16, Motorola on "
                 "Android 15): 32, 32 and 32 rows, equal to a count of SoftInputShowHide headings in the raw text; the two "
                 "Android 10 reports print no such history. The conversion to UTC was the identity on real rows (UTC+0 zone). Not "
                 "examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus none of s20fe_a13, samsungs20_a13, sharon_a14 and userb2_a13 gave a row; why was not examined.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "type",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_display_states": {
        "name": "Bug Report - Display States",
        "description": "The display states printed by the display dump of an Android bug report: state, brightness, name and "
                       "size of each display.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Display and Input",
        "notes": "One row per Display Id block of the Display States part and one per logical display of the Logical Displays "
                 "part of the display service dump. Source says which part. For the first, State, Brightness (as printed) and "
                 "SDR Brightness (as printed) are the printed values (a fraction, not a percentage); for the second, State is the "
                 "word after state in the DisplayInfo text, Name is its quoted name and Size is the real size, and the "
                 "brightness columns are empty. The Android 10 reports print the logical display part only.\n"
                 "The rows are the state when the dump ran (for example ON). They give no history: the display events that have "
                 "a time are in Bug Report - Brightness Events. The display modes, color modes, adapter and window state parts "
                 "of the dump are not read.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): Display held one "
                 "value on all rows of the Samsung A-series, Samsung S-series and Motorola reports; State held one value on "
                 "all rows of the Samsung A-series, Samsung S-series and Motorola reports.\n"
                 "Brightness (as printed) and SDR Brightness (as printed) were identical on both rows of the Samsung A-series, "
                 "Samsung S-series and Motorola reports, and empty on the one row of the Huawei and Transsion-brand reports, "
                 "whose logical display part carries no brightness.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 2, 2, 1, 1 and 2 rows, equal to a count of the "
                 "Display Id blocks and logical display blocks in the raw text. State held ON on every row of every tested report, "
                 "and Display held 0, so the table can show one value only on those devices. Not examined: a display that is off "
                 "or a second display, Android 11, 12 and 14, other vendors."
                 "\nOn the corpus the run gave s20fe_a13 2 rows; samsungs20_a13, sharon_a14 and userb2_a13 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "monitor",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 2 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_brightness_events": {
        "name": "Bug Report - Brightness Events",
        "description": "The BrightnessEvent lines and the brightness change lines of the display dump of an Android bug report, "
                       "with display state, policy, brightness, lux and reason as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Display and Input",
        "notes": "One row per line that starts with a month-day time and holds BrightnessEvent: (the display power controller's "
                 "event list) or isUserSetBrightness= (the brightness tracker's change list). Kind says which. For a BrightnessEvent "
                 "line, Display State, Display Policy, Brightness, Nits, Lux, Reason and Strategy are the key=value pairs "
                 "disp, displayState (or state), displayPolicy, brt, brtNits (or nits), lux, reason and strat that the build "
                 "prints (the builds print different pairs, so a column can be empty); Text (as printed) is the whole line after "
                 "the time, cut at 900 characters. For a brightness change line only Text is filled. Time As Printed has no year; "
                 "Time (UTC) uses the year rule and the zone as in Bug Report - Location Events.\n"
                 "A row records that the display service logged a brightness or display state change at that time; the display "
                 "state OFF and the policy DOZE or OFF in some rows are the service's words and are not interpreted here. The "
                 "lists are rings (up to 100 events and a longer change list), so they cover hours to weeks. They do not show "
                 "that a person looked at or used the device.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): Kind held one value "
                 "on all rows of the Samsung A-series report; Lux held one value on all rows of the Samsung A-series report; "
                 "Display was empty on all rows of the Samsung A-series and Samsung S-series reports; Display Policy was empty "
                 "on all rows of the Samsung A-series and Samsung S-series reports; Strategy was empty on all rows of the "
                 "Motorola report.\n"
                 "Evidence tiers. Data-proven on three real bug reports (Samsung A-series and S-series on Android 16, Motorola on "
                 "Android 15): 29, 179 and 161 rows, equal to a count of the event and change lines in the raw text; the two "
                 "Android 10 reports print neither list. The conversion to UTC was the identity on real rows (UTC+0 zone). Not "
                 "examined: Android 11, 12 and 14, other vendors."
                 "\nOn the corpus none of s20fe_a13, samsungs20_a13, sharon_a14 and userb2_a13 gave a row; why was not examined.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "sun",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 0 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_window_focus": {
        "name": "Bug Report - Window Focus",
        "description": "The focus lines of the window dump of an Android bug report: the focused window, the focused app, the "
                       "input method window and the top focused display.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Display and Input",
        "notes": "One row per mCurrentFocus, mFocusedApp, mTopFocusedDisplayId, mInputMethodWindow and mInputMethodTarget line of the "
                 "window service dump. Display is the display of the Display: mDisplayId line the focus lines follow (empty "
                 "for the lines that are not per display), Item is the printed name, Value is the printed text, cut at 400 "
                 "characters, and Package is the package in a window or activity record where the value holds one. The dump "
                 "is printed twice on the Samsung and Motorola reports (a short copy and a full one), so lines of the full copy "
                 "can repeat.\n"
                 "The rows are the focus when the dump ran. On the tested reports the focused app was the same system app on all five "
                 "and the focused window was that app's window on four (a system window on the fifth), as the capture was "
                 "started from the device; a focus line says what was in the foreground at the moment of the dump and nothing "
                 "about earlier use.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): no column was empty "
                 "or uniform.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 4, 4, 3, 3 and 4 rows, equal to a count of the "
                 "named lines in the raw text. Not examined: Android 11, 12 and 14, other vendors, a device with more than one display."
                 "\nOn the corpus the run gave s20fe_a13 4 rows and userb2_a13 6 rows (3 from a partial text, 3 from a partial text); samsungs20_a13 and sharon_a14 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "layout",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 4 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 6 rows",
        }
    },
    "bugreport_windows": {
        "name": "Bug Report - Windows",
        "description": "The windows listed in the window dump of an Android bug report, with the title, owner uid, package, "
                       "session pid and visibility fields as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Display and Input",
        "notes": "One row per Window #N block of the WINDOW MANAGER WINDOWS part of the window service dump. Title is the text after "
                 "the user in Window{hash uN title} (a package/activity name or a system window name), Display, Owner UID, Package "
                 "and Session PID come from the mDisplayId, mOwnerUid, package= and mSession lines, View Visibility (as stored) is "
                 "mViewVisibility (hexadecimal, not decoded), and Has Surface, Ready For Display, On Screen and Visible are the "
                 "values of mHasSurface, isReadyForDisplay(), isOnScreen and isVisible.\n"
                 "The rows are the windows the window manager held when the dump ran, including the system's own overlays and "
                 "windows of apps that are not on screen. A window with Visible true was visible at that moment; the rows give no "
                 "history and do not show what was displayed. The window manager's display contents, tokens, animator, policy and "
                 "configuration parts are not read.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): Display held one "
                 "value on all rows of the Samsung A-series, Samsung S-series, Huawei, Transsion-brand and Motorola reports.\n"
                 "Ready For Display, On Screen and Visible were identical on every row of the Samsung A-series, Samsung "
                 "S-series and Motorola reports (the three flags agree on every tested row, so on those reports they give the "
                 "same information); on the Huawei and Transsion-brand reports Has Surface and On Screen were identical on "
                 "every row, and so were Ready For Display and Visible.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 19, 27, 21, 11 and 22 rows, equal to a count of "
                 "Window # headings in the raw text. Not examined: Android 11, 12 and 14, other vendors, split-screen and freeform "
                 "windows."
                 "\nOn the corpus the run gave s20fe_a13 12 rows and userb2_a13 25 rows (13 from a partial text, 12 from a partial text); samsungs20_a13 and sharon_a14 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "layout",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 12 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 25 rows",
        }
    },
    "bugreport_surfaceflinger_layers": {
        "name": "Bug Report - SurfaceFlinger Layers",
        "description": "The HWC layer list of the SurfaceFlinger dump of an Android bug report: layer name, z, window type and "
                       "composition type as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Display and Input",
        "notes": "One row per layer of the Display N HWC layers table of the SurfaceFlinger dump. The columns are located from the "
                 "table's own header line. Layer is the name line (a package/activity name or a system layer name, cut by the "
                 "platform with [...] where it is long), Z, Window Type (as stored), Composition Type and Transform (as stored) "
                 "are the printed cells, and Focus Mark is true where the last cell holds [*] and false where it does not, empty "
                 "where the header has no Focused column.\n"
                 "The rows are the layers composited when the dump ran. They give no history and do not show what was displayed. "
                 "The visible layer list of the Android 10 layout, the scheduler and frame statistics and the buffer allocation "
                 "parts of the dump are not read.\n"
                 "Column check on the tested reports (a report with fewer than two rows is not checked): Display held one "
                 "value on all rows of the Samsung A-series, Samsung S-series, Huawei, Transsion-brand and Motorola reports; "
                 "Transform (as stored) held one value on all rows of the Samsung A-series, Samsung S-series, Huawei, "
                 "Transsion-brand and Motorola reports; Composition Type held one value on all rows of the Samsung S-series, "
                 "Transsion-brand and Motorola reports; Z held one value on all rows of the Transsion-brand report; Focus Mark "
                 "was empty on all rows of the Huawei and Transsion-brand reports.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 6, 6, 5, 3 and 3 rows, equal to a count of the layer "
                 "name lines of the table in the raw text. Focus Mark is empty on all rows of the two Android 10 reports. Not "
                 "examined: Android 11, 12 and 14, other vendors, more than one display."
                 "\nOn the corpus the run gave s20fe_a13 4 rows and userb2_a13 9 rows (6 from a partial text, 3 from a partial text); samsungs20_a13 and sharon_a14 gave none. Not compared with a second count.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "layers",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 4 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 9 rows",
        }
    },
}

import re

from scripts import dumpstate_reader
from scripts import dumpstate_sensorsmedia as sensorsmedia
from scripts.ilapfuncs import artifact_processor, logfunc


def _reports(context):
    """The bug report texts among the staged files, as (Source File label, Report) pairs."""
    return dumpstate_reader.load_reports(context.get_files_found(), context.get_relative_path, logfunc)


def _source_path(context, reports):
    """The staged files that were read; the matched files when none was a bug report."""
    paths = [report.source.path for _label, report in reports] or sorted(str(path) for path in context.get_files_found())
    return '\n'.join(dict.fromkeys(str(path) for path in paths))


def _log_state(label, report, services, rows_of_table):
    """Say so when none of the services was dumped, or when the platform cut a dump of one that holds rows (or when it cut one and there are no rows)."""
    seen = [section for section in report.sections if section.kind == 'service' and section.name in services]
    if not seen:
        dumpstate_reader.say_once(logfunc, f'Bug report {label}: no {" or ".join(services)} service dump in this report')
        return
    lines = [row.line for row in rows_of_table]
    cut = [section for section in seen if section.timeout_ms]
    if lines:
        cut = [section for section in cut if any(section.line < number < section.end_line for number in lines)]
    if cut:
        dumpstate_reader.say_once(logfunc, f'Bug report {label}: the {cut[0].name} service dump was cut by a {cut[0].timeout_ms} ms '
                                           f'timeout, the rows from it may be partial')


def _build(context, services, table, headers, make_row):
    """The (headers, rows, source path) of an artifact that presents one table of the sensors and media readers."""
    rows = []
    reports = _reports(context)
    for label, report in reports:
        found = sensorsmedia.rows(report, table)
        _log_state(label, report, services, found)
        for item in found:
            rows.append(make_row(report, item, label))
    return headers, rows, _source_path(context, reports)


def _quality(request):
    """``(quality word, interval text)`` of a Request[...] text: the first words, where an @ word is the interval."""
    inner = request[len('Request['):].split(',', 1)[0].split(']', 1)[0].split() if request.startswith('Request[') else []
    if inner and inner[0].startswith('@'):
        return (inner[1] if len(inner) > 1 else ''), inner[0][1:]
    return (inner[0] if inner else ''), ''


def _field(text, name):
    match = re.search(r'\b' + re.escape(name) + r'=([^,\]\s]+)', text)
    return match.group(1) if match else ''


def _utc(report, text):
    return sensorsmedia.utc_for(report, text)


@artifact_processor
def bugreport_location_providers(context):
    headers = ('Provider', 'Service State', 'Allowed', 'Useable', 'Enabled', 'Identity', 'Properties', 'Listeners',
               'Target Service', 'Connected', 'Stationary Throttled', 'Started', 'Source Line', 'Source File')
    return _build(context, ('location',), 'location_providers', headers, lambda report, item, label: (
        item.provider, item.service, item.allowed, item.useable, item.enabled, item.identity, item.properties,
        item.listeners, item.target_service, item.connected, item.stationary, item.started, item.line, label))


@artifact_processor
def bugreport_location_last_known(context):
    headers = ('List', 'Provider', 'User', 'Location Provider (as printed)', 'Latitude (as printed)',
               'Longitude (as printed)', 'Accuracy (as printed)', 'Elapsed Time (as printed)', 'Enabled',
               'Last Location (as printed)', 'Source Line', 'Source File')

    def make(_report, item, label):
        provider, latitude, longitude, accuracy, elapsed = sensorsmedia.parse_location_text(item.text)
        return (item.source, item.provider, item.user, provider, latitude, longitude, accuracy, elapsed, item.enabled,
                item.text, item.line, label)
    return _build(context, ('location',), 'location_last', headers, make)


@artifact_processor
def bugreport_location_requests(context):
    headers = ('List', 'Provider', 'UID', 'Package', 'Attribution Tag', 'Listener ID', 'Flags', 'Request (as printed)',
               'Quality', 'Interval (as printed)', 'Min Update Interval', 'Min Update Distance', 'State', 'Work Source',
               'Source Line', 'Source File')

    def make(_report, item, label):
        quality, interval = _quality(item.request)
        return (item.source, item.provider, item.uid, item.package, item.tag, item.listener, item.flags, item.request,
                quality, interval, _field(item.request, 'minUpdateInterval'), _field(item.request, 'minUpdateDistance'),
                item.state, item.work_source, item.line, label)
    return _build(context, ('location',), 'location_requests', headers, make)


@artifact_processor
def bugreport_location_events(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Provider', 'Event', 'Client', 'Detail', 'Source Line',
               'Source File')
    return _build(context, ('location',), 'location_events', headers, lambda report, item, label: (
        _utc(report, item.time_text), item.time_text, item.provider, item.event, item.client, item.detail, item.line, label))


@artifact_processor
def bugreport_location_usage(context):
    headers = ('List', 'Provider', 'Client', 'Min Interval', 'Max Interval', 'Total Duration', 'Active Duration',
               'Foreground Duration', 'Locations', 'Detail (as printed)', 'Source Line', 'Source File')
    return _build(context, ('location',), 'location_usage', headers, lambda report, item, label: (
        item.source, item.provider, item.client, item.min_interval, item.max_interval, item.total, item.active,
        item.foreground, item.locations, item.detail, item.line, label))


@artifact_processor
def bugreport_time_zone_detection(context):
    headers = ('Component', 'Item', 'Index', 'Elapsed (as printed)', 'Value (as printed)', 'Source Line', 'Source File')
    return _build(context, ('location_time_zone_manager',), 'time_zone_states', headers, lambda report, item, label: (
        item.component, item.item, item.index, item.elapsed, item.value, item.line, label))


@artifact_processor
def bugreport_sensors(context):
    headers = ('Handle', 'Name', 'Vendor', 'Version', 'Type (as printed)', 'Permission', 'Flags (as stored)',
               'Reporting Mode', 'Capabilities (as printed)', 'Active Count', 'Sampling Periods (ms)',
               'Selected Sampling (ms)', 'Batching Periods (ms)', 'Selected Batching (ms)', 'Connections', 'Source Line',
               'Source File')
    return _build(context, ('sensorservice',), 'sensors', headers, lambda report, item, label: (
        item.handle, item.name, item.vendor, item.version, item.type, item.permission, item.flags, item.mode,
        item.capabilities, item.active_count, item.sampling, item.selected_sampling, item.batching, item.selected_batching,
        item.connections, item.line, label))


@artifact_processor
def bugreport_sensor_connections(context):
    headers = ('Connection', 'Operating Mode', 'Client (as printed)', 'UID', 'Has Sensor Access', 'Sensor', 'Handle', 'Status',
               'First Flush Pending', 'Pending Flush Events', 'Source Line', 'Source File')

    return _build(context, ('sensorservice',), 'sensor_connections', headers, lambda report, item, label: (
        item.number, item.mode, item.label, item.uid, item.access, item.sensor, item.handle, item.status, item.first_flush,
        item.pending_flush, item.line, label))


@artifact_processor
def bugreport_sensor_registrations(context):
    headers = ('Clock Time (as printed)', 'Sign (as printed)', 'Handle', 'PID', 'UID', 'Sampling Period (us)',
               'Batching Period (us)', 'Result', 'Sensor', 'Package or Class (as printed)', 'Source Line', 'Source File')
    return _build(context, ('sensorservice',), 'sensor_registrations', headers, lambda report, item, label: (
        item.clock, item.action, item.handle, item.pid, item.uid, item.sampling, item.batching, item.result, item.sensor,
        item.package, item.line, label))


@artifact_processor
def bugreport_sensor_events(context):
    headers = (('Time (UTC)', 'datetime'), 'Wall Clock (as printed)', 'Time Note', 'Sensor', 'Event Number',
               'Timestamp (as printed)', 'Values (as printed)', 'Source Line', 'Source File')

    def make(report, item, label):
        dated = len(item.wall) > 14 and item.wall[2] == '-'
        return (_utc(report, item.wall) if dated else None, item.wall, '' if dated else 'clock time without a date: no UTC value',
                item.sensor, item.event, item.ts, item.values, item.line, label)
    return _build(context, ('sensorservice',), 'sensor_events', headers, make)


@artifact_processor
def bugreport_camera_events(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Event', 'Device', 'Package', 'PID', 'Priority', 'Detail',
               'Source Line', 'Source File')
    return _build(context, ('media.camera',), 'camera_events', headers, lambda report, item, label: (
        _utc(report, item.time_text), item.time_text, item.event, item.device, item.package, item.pid, item.priority,
        item.detail, item.line, label))


@artifact_processor
def bugreport_camera_devices(context):
    headers = ('Part', 'Device', 'State', 'Opened (as printed)', 'Package', 'PID', 'UID', 'Priority Score',
               'Device Status', 'Source Line', 'Source File')
    return _build(context, ('media.camera',), 'camera_devices', headers, lambda report, item, label: (
        item.part, item.device, item.state, item.opened, item.package, item.pid, item.uid, item.priority,
        item.device_status, item.line, label))


@artifact_processor
def bugreport_audio_events(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Log', 'UID', 'PID', 'Event', 'Source Line', 'Source File')
    return _build(context, ('audio',), 'audio_events', headers, lambda report, item, label: (
        _utc(report, item.time_text), item.time_text, item.log, item.uid, item.pid, item.text, item.line, label))


@artifact_processor
def bugreport_audio_clients(context):
    headers = ('List', 'PID', 'UID', 'Name', 'Session', 'Count', 'Source Line', 'Source File')
    return _build(context, ('media.audio_flinger',), 'audio_clients', headers, lambda report, item, label: (
        item.kind, item.pid, item.uid, item.name, item.session, item.count, item.line, label))


@artifact_processor
def bugreport_media_sessions(context):
    headers = ('Session', 'Key', 'Role', 'User', 'Owner PID', 'Owner UID', 'Package', 'Active', 'Flags (as stored)',
               'Playback State (as printed)', 'Audio Attributes', 'Volume (as printed)', 'Metadata (as printed)',
               'Source Line', 'Source File')
    return _build(context, ('media_session',), 'media_sessions', headers, lambda report, item, label: (
        item.tag, item.key, item.role, item.user, item.owner_pid, item.owner_uid, item.package, item.active, item.flags,
        item.state, item.audio_attributes, item.volume, item.metadata, item.line, label))


@artifact_processor
def bugreport_audio_playback_order(context):
    headers = ('Position', 'UID', 'Packages', 'Source Line', 'Source File')
    return _build(context, ('media_session',), 'audio_playback', headers, lambda report, item, label: (
        item.position, item.uid, item.packages, item.line, label))


@artifact_processor
def bugreport_media_metrics(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Key', 'Package', 'PID', 'UID', 'Properties (as printed)',
               'Record Form', 'Record No.', 'Source Line', 'Source File')

    def make(report, item, label):
        if item.form == 'colon separated':
            moment = None
            if dumpstate_reader.is_digits(item.time_text) and dumpstate_reader.plausible_epoch_ms(int(item.time_text) // 1000000):
                moment = dumpstate_reader.epoch_s_to_utc(int(item.time_text) // 1000000000)
        else:
            moment = _utc(report, item.time_text)
        return (moment, item.time_text, item.key, item.package, item.pid, item.uid, item.properties, item.form,
                item.number, item.line, label)
    return _build(context, ('media.metrics',), 'media_metrics', headers, make)


@artifact_processor
def bugreport_accessibility_services(context):
    headers = ('User', 'List', 'Index', 'Component', 'Tags (as printed)', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        found = sensorsmedia.rows(report, 'accessibility_services')
        _log_state(label, report, ('accessibility',), found)
        for name in sorted(report.__dict__.get('accessibility_empty', ())):
            dumpstate_reader.say_once(logfunc, f'Bug report {label}: the {name} accessibility services list was printed empty')
        for item in found:
            rows.append((item.user, item.list, item.index, item.component, item.tags, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_input_methods(context):
    headers = ('Index', 'Input Method ID', 'Package', 'Service', 'Settings Activity', 'UID', 'Version Code', 'Permission',
               'Selected', 'Source Line', 'Source File')
    return _build(context, ('input_method',), 'input_methods', headers, lambda report, item, label: (
        item.index, item.method_id, item.package, item.service, item.settings_activity, item.uid, item.version_code,
        item.permission, item.current, item.line, label))


@artifact_processor
def bugreport_input_start_history(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Entry', 'Reason', 'Restarting', 'Input Method',
               'Target Window', 'Soft Input Mode', 'Input Type', 'IME Options', 'Field ID', 'Field Name', 'Source Line',
               'Source File')
    return _build(context, ('input_method',), 'start_inputs', headers, lambda report, item, label: (
        _utc(report, item.time_text), item.time_text, item.entry, item.reason, item.restarting, item.ime,
        item.target_window, item.soft_input_mode, item.input_type, item.ime_options, item.field_id, item.field_name,
        item.line, label))


@artifact_processor
def bugreport_soft_input_history(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Entry', 'Reason', 'Requesting UID', 'Requesting PID',
               'Focused Window', 'IME Control Target', 'Editor Info', 'Source Line', 'Source File')
    return _build(context, ('input_method',), 'soft_input_toggles', headers, lambda report, item, label: (
        _utc(report, item.time_text), item.time_text, item.entry, item.reason, item.uid, item.pid, item.focused_window,
        item.ime_target, item.input_type, item.line, label))


@artifact_processor
def bugreport_display_states(context):
    headers = ('Source', 'Display', 'State', 'Brightness (as printed)', 'SDR Brightness (as printed)', 'Name', 'Size',
               'Source Line', 'Source File')
    return _build(context, ('display',), 'display_states', headers, lambda report, item, label: (
        item.source, item.display, item.state, item.brightness, item.sdr_brightness, item.name, item.size, item.line, label))


@artifact_processor
def bugreport_brightness_events(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Kind', 'Display', 'Display State', 'Display Policy',
               'Brightness', 'Nits', 'Lux', 'Reason', 'Strategy', 'Text (as printed)', 'Source Line', 'Source File')
    return _build(context, ('display',), 'brightness_events', headers, lambda report, item, label: (
        _utc(report, item.time_text), item.time_text, item.kind, item.display, item.state, item.policy, item.brightness,
        item.nits, item.lux, item.reason, item.strategy, item.text, item.line, label))


@artifact_processor
def bugreport_window_focus(context):
    headers = ('Display', 'Item', 'Value', 'Package', 'Source Line', 'Source File')
    return _build(context, ('window',), 'window_focus', headers, lambda report, item, label: (
        item.display, item.item, item.value, item.package, item.line, label))


@artifact_processor
def bugreport_windows(context):
    headers = ('Number', 'Title', 'Display', 'Owner UID', 'Package', 'Session PID', 'View Visibility (as stored)',
               'Has Surface', 'Ready For Display', 'On Screen', 'Visible', 'Source Line', 'Source File')
    return _build(context, ('window',), 'windows', headers, lambda report, item, label: (
        item.number, item.title, item.display, item.uid, item.package, item.session_pid, item.view_visibility,
        item.has_surface, item.ready, item.on_screen, item.visible, item.line, label))


@artifact_processor
def bugreport_surfaceflinger_layers(context):
    headers = ('Display', 'Layer', 'Z', 'Window Type (as stored)', 'Composition Type', 'Transform (as stored)',
               'Focus Mark', 'Source Line', 'Source File')
    return _build(context, ('SurfaceFlinger',), 'sf_layers', headers, lambda report, item, label: (
        item.display, item.name, item.z, item.window_type, item.composition, item.transform, item.focused, item.line, label))
