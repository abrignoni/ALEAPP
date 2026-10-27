__artifacts_v2__ = {
    "bugreport_usage_intervals": {
        "name": "Bug Report - Usage Intervals",
        "description": "The daily, weekly, monthly and yearly interval statistics per package in the usagestats dump of an Android "
                       "bug report text, with the durations, last times and launch counts as printed and converted.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - App Usage",
        "notes": "One row per package line of the packages list under each In-memory daily, weekly, monthly and yearly stats "
                 "heading of each Android user, in the usagestats service dump (DUMP OF SERVICE usagestats) and in the CHECKIN "
                 "USAGESTATS command section. Source Section says which one printed the row. Interval is the heading word. "
                 "Interval As Printed is the timeRange text of the service form (a locale-formatted device time) or the "
                 "beginTime and endTime numbers of the checkin form; Interval Begin (UTC) and Interval End (UTC) are those two "
                 "numbers read as epoch milliseconds and are empty for the service form, which prints no numbers. The Total Time "
                 "columns and the Last Time columns are the values the dump prints as totalTimeUsed, totalTimeVisible, "
                 "totalTimeFS and lastTimeUsed, lastTimeVisible, lastTimeComponentUsed, lastTimeFS; the labels are the dump's own "
                 "and are not expanded here. The checkin form prints durations as milliseconds and times as epoch milliseconds. "
                 "The service form prints durations as clock text (MM:SS or H:MM:SS, whole seconds, shown in the (ms) columns as "
                 "seconds times 1000) and times as device wall-clock text without a zone, which is converted with the zone shown "
                 "in Bug Report - Device Facts. A time printed as 0, or as a wall-clock text before 2009 (the platform prints "
                 "1970-01-01 00:00:00), has no UTC value and keeps its printed text. Time Note says when a wall-clock text could "
                 "not be converted because the report records no zone.\n"
                 "Package lines whose durations are all zero, whose times are all unset and whose launch count is zero are counted "
                 "in the log and not listed (234, 315, 85, 1,603 and 45 per section of the Samsung A-series, Samsung S-series, "
                 "Huawei, Motorola and Transsion-brand reports). The Huawei, Motorola and Transsion-brand reports print the "
                 "statistics in both sections, so a package appears twice with the same values there; Source Section tells the "
                 "copies apart. The two Samsung reports (Android 16) have no usagestats service section and print only the "
                 "CHECKIN USAGESTATS copy. A row says what the usage statistics service kept for that package and interval; it "
                 "does not say what a person did, and a package that is not listed says nothing about use. The statistics are "
                 "interval summaries, not an event log; the events are in Bug Report - Usage Events and the event totals of each "
                 "interval in Bug Report - Usage Interval Event Counts. The configurations and chooser counts of the same dump "
                 "are not read.\n"
                 "User held one value, 0, on all rows of all five reports (a second user's statistics were built on constructed "
                 "text only). Last Time Component Used is empty on all rows of the two Android 10 reports, which do not print it. "
                 "Interval End (UTC) held one value on all rows of each Samsung report. Time Note was empty on all 6,074 rows of "
                 "the five reports, because each of them records a time zone.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 790, 926, 1,138, 1,346 and 1,874 rows, each equal "
                 "to a count of the package lines in the raw text (rows plus the unlisted lines) and to an independent parser "
                 "for the package, user, interval, durations, last times and launch count as printed. All five reports record a "
                 "UTC+0 time zone without daylight saving, so the conversion of wall-clock text to UTC was the identity on every "
                 "real row; other zones and daylight saving were tested on constructed text only. Not examined: Android 11 and 12 "
                 "and other vendors."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints the service dumps read here; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not print a usagestats dump. s20fe_a13 gave 886 rows, 457 from the usagestats dump and 429 from CHECKIN USAGESTATS; with the 1,158 and 1,186 rows the log counts and does not list, each adds up to the 1,615 package lines of its section.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "bar-chart",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 886 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_usage_interval_events": {
        "name": "Bug Report - Usage Interval Event Counts",
        "description": "The event aggregation lines of each daily, weekly, monthly and yearly interval in the usagestats dump of an "
                       "Android bug report text, with the count and the total time as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - App Usage",
        "notes": "One row per line of the event aggregations list under each In-memory daily, weekly, monthly and yearly stats "
                 "heading of each Android user, in the usagestats service dump and in the CHECKIN USAGESTATS command section "
                 "(Source Section says which). Event is the name as printed (screen-interactive, screen-non-interactive, "
                 "keyguard-shown and keyguard-hidden in the tested reports), Count is the number before the x, Total Time As "
                 "Printed is the amount after for (milliseconds in the checkin form, clock text in the service form, whole "
                 "seconds) and Total Time (ms) is that amount in milliseconds. Printed After is the rest of the line, for "
                 "example (now running, started at ) where the platform notes the event as still running. Interval, Interval As "
                 "Printed and the interval begin and end are as in Bug Report - Usage Intervals.\n"
                 "A row is a total the usage statistics service kept for the interval; it says how often and for how long the "
                 "platform noted the event in that interval, not what a person did. The Huawei, Motorola and Transsion-brand "
                 "reports print the lists in both sections (16 rows each, so 32), the two Samsung reports print only the "
                 "CHECKIN USAGESTATS copy (16 and 15 rows). User held one value, 0, on all rows of all five reports and "
                 "Interval End (UTC) held one value on all rows of each Samsung report.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 16, 15, 32, 32 and 32 rows, each equal to a count of "
                 "the event lines in the raw text and to an independent parser, field by field. Not examined: Android 11 and 12, "
                 "other vendors, and event names other than the four seen."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints the service dumps read here; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not print a usagestats dump. s20fe_a13 gave 16 rows, equal to the event lines of its two sections (8 each).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "bar-chart",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 16 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_standby_buckets": {
        "name": "Bug Report - Standby Buckets",
        "description": "The App Standby States lines of each Android user in the usagestats dump of an Android bug report text, "
                       "with the bucket, reason code and relative times as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - App Usage",
        "notes": "One row per package line of the App Standby States list of each Android user, in the usagestats service dump "
                 "and in the CHECKIN USAGESTATS command section (Source Section says which). Android 10 prints the list indented "
                 "under each user, Android 15 and 16 under a User N App Standby States heading. Bucket is the number after "
                 "bucket= and Reason is the code after reason=, both as printed and the reason code is not decoded. Bucket Name "
                 "is the name of the constant of that number in the platform's UsageStatsManager (5 EXEMPTED, 10 ACTIVE, 20 "
                 "WORKING_SET, 30 FREQUENT, 40 RARE, 45 RESTRICTED, 50 NEVER); this mapping is source-verified from the "
                 "platform's constants and was not decoded from the dump, and a number outside that list has an empty name. "
                 "Used, Used By User, Used Screen, Last Predicted, Expiry Times, Last Job and Next Estimated Launch are the "
                 "values printed after used=, usedByUser=, usedScr=, lastPred=, expiryTimes=, lastJob= and "
                 "nextEstimatedLaunchTime=; they are printed as signed offsets and "
                 "are shown as printed, not converted (<uninitialized> and <none> are the dump's own markers). Last Informed Bucket and Idle "
                 "are lastInformedBucket= and idle=. Other Fields keeps any other key=value pair of the line (activeLeft and "
                 "wsLeft on Android 10).\n"
                 "A row says which bucket the platform held for the package when the dump ran. It does not say why (the reason "
                 "code is the platform's) or that the app was used, and a package that is not listed says nothing about the "
                 "device. The Huawei, Motorola and Transsion-brand reports print the list in both sections, so a package "
                 "appears twice there; the two Samsung reports (Android 16) print only the CHECKIN USAGESTATS copy. The "
                 "Motorola report lists two Android users (0 and 11); User held one value, 0, on all rows of the other four "
                 "reports. Used By User, Expiry Times, Last Informed Bucket and Next Estimated Launch are empty on all rows of "
                 "the two Android 10 reports, which do not print them.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 516, 753, 596, 2,412 and 486 rows, each equal to a "
                 "count of the package lines in the raw text and to an independent parser for the package, user, bucket, reason, "
                 "used and lastJob values. Cross-check of the bucket names: for the 2,436 registered jobs of the five reports "
                 "whose package and user also have a bucket here, the job scheduler's own bucket name equalled the mapped name on "
                 "2,042; on the other 394 the job scheduler printed EXEMPTED or ACTIVE for a package in another bucket (bucket 5 "
                 "printed ACTIVE on 211 of them). Numbers 5, 10, 20, 40, 45 and 50 each matched their name on most pairs; 30 never "
                 "appeared with FREQUENT in a pair (6 pairs with ACTIVE and 31 with EXEMPTED), so the name of 30 is "
                 "source-verified only. Not examined: Android 11 and 12 and other vendors."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints the service dumps read here; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not print a usagestats dump. s20fe_a13 gave 930 rows, 465 from each section; each equal to the bucket= lines of its section.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "layers",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 930 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_scheduled_jobs": {
        "name": "Bug Report - Scheduled Jobs",
        "description": "The registered jobs and, where printed, the recent jobs in the jobscheduler dump of an Android bug report "
                       "text, with the constraints, standby bucket, relative times and last run times as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Alarms and Jobs",
        "notes": "One row per JOB entry of the Registered N jobs list and, where the dump prints one, per entry of the Recently "
                 "completed jobs list of the jobscheduler service dump (List says which). Package is the pkg= of the Source line "
                 "(the app the job belongs to), User and UID are its user= and uid= as printed, Namespace, Job ID and Tag are "
                 "from the entry heading and the tag= line, and Service, Job Type, Persisted, Priority, Requires, Network, "
                 "Minimum Latency, Max Execution Delay and Extras are the lines of its JobInfo block as printed (Extras is app "
                 "text, cut at 400 characters). Required, Satisfied and Unsatisfied Constraints are the constraint names without "
                 "their hexadecimal value, Standby Bucket is the printed name, and Restricted Due To and Ready are as printed. "
                 "Enqueue Time, Run Time Earliest and Run Time Latest, and Completed for the recently completed list, are offsets "
                 "from the moment of the dump as printed; the jobscheduler dump prints no absolute anchor, so they are not "
                 "converted to UTC. Last Successful Run and Last Failed Run are device wall-clock texts without a zone; (UTC) "
                 "converts them with the zone shown in Bug Report - Device Facts, a time printed as 1970-01-01 00:00:00 gets no UTC value, and "
                 "Time Note says why a value has none. The constraint history, the controllers, the quota and execution "
                 "statistics, the pending queue, the active jobs and the idle contexts of the same dump are not read.\n"
                 "A row says that the job scheduler held that job when the dump ran, with the state printed; it does not say "
                 "that the job ran or will run. The two Android 10 reports print no namespace, priority, restriction or recently "
                 "completed list: Namespace, Priority and Restricted Due To are empty on all rows of the Huawei and "
                 "Transsion-brand reports and List held one value, Registered. The three Android 15 and 16 reports print the "
                 "recently completed list with 20 entries each. User held one value, 0, on all rows of the other four reports; "
                 "the Motorola report has jobs of users 0 and 11.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 490, 749, 243, 711 and 303 rows (470, 729, 243, "
                 "691 and 303 registered, 20 recently completed on three), each equal to the number the dump prints for the "
                 "registered list plus a count of the completed entries, and to an independent parser for the list, job id, "
                 "package, service, bucket, last run times and enqueue time. All five reports record a UTC+0 time zone, so the "
                 "wall-clock conversion was the identity on every real row; other zones were tested on constructed text only. "
                 "Not examined: Android 11 and 12 and other vendors."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints the service dumps read here; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not print a jobscheduler dump. s20fe_a13 gave 268 rows: 248 Registered rows, equal to its JOB # lines, and 20 Recently completed rows.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "clock",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 268 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_pending_alarms": {
        "name": "Bug Report - Pending Alarms",
        "description": "The pending alarms and the next alarm clock in the alarm dump of an Android bug report text, with the "
                       "trigger offset, tag, window and flags as printed and the trigger time computed from nowRTC.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Alarms and Jobs",
        "notes": "One row per alarm of the pending alarm list of the alarm service dump (List: Pending alarms) and one row for "
                 "each line under Next alarm clock information (List: Next alarm clock). Android 10 prints the alarms in batches "
                 "(Batch holds the batch id), Android 15 and 16 as N pending alarms. Alarm Type is the printed type name, "
                 "Package (as printed) is the text that ends the Alarm{...} heading (the Huawei report prints more than a package "
                 "name there), Tag is the tag= line, and Window, Repeat Interval (ms), Count, Flags, Exact Allow Reason, "
                 "Operation and Listener are as printed (the original-time text of an RTC alarm is shown in Original When). "
                 "Trigger As Printed and Latest Trigger As Printed are the whenElapsed and maxWhenElapsed offsets from the "
                 "moment of the dump (the epoch milliseconds and wall-clock text for the alarm clock line). Trigger Time (UTC) "
                 "and Latest Trigger Time (UTC) are the nowRTC epoch milliseconds printed in the same dump plus those offsets, "
                 "so they do not depend on the time zone; they are empty, with a Time Note, where the dump prints no nowRTC.\n"
                 "A row says that the alarm manager held that alarm when the dump ran; it does not say that the alarm fired or "
                 "what the app did with it. The alarm clock line is the next alarm clock the alarm manager noted; it was printed "
                 "on the two Samsung reports (one row each) and was empty on the other three. Count held one value, 0, on all "
                 "rows of the Huawei, Motorola and Transsion-brand reports, Exact Allow Reason and Original When are empty on all "
                 "rows of the Huawei and Transsion-brand reports, and Batch is empty on all rows of the Android 15 and 16 "
                 "reports. The "
                 "alarm statistics, the top alarms, the quota and the per-uid counts of the same dump are not read.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 130, 207, 116, 108 and 106 rows (129 and 206 "
                 "pending alarms plus the alarm clock on the Samsung reports), each equal to a count of the alarm headings in the "
                 "raw text and to an independent parser for the type, package, tag and trigger offset. The nowRTC arithmetic "
                 "reproduced the printed wall-clock time of the Next wakeup alarm and Next non-wakeup alarm lines on all five "
                 "reports (10 of 10 lines, to the millisecond). Not examined: Android 11 and 12 and other vendors."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints the service dumps read here; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not print an alarm dump. s20fe_a13 gave 70 rows, equal to the alarm entry lines of its alarm dump.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "alarm",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 70 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_alarm_history": {
        "name": "Bug Report - Alarm History",
        "description": "The alarm history lists in the alarm dump of an Android bug report text (removals, additions, deliveries, "
                       "wakeups and per-app alarm times), with the time as printed and converted, and the tag and reason as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Alarms and Jobs",
        "notes": "One row per entry of these lists of the alarm service dump (History says which): Removal history, Addition "
                 "history, Delivery history and Wakeup Alarm history(screen off) (the last three are printed by the Samsung "
                 "reports only), and App Alarm history, Allow while idle history and Allow while idle compat history, where each "
                 "time printed for a package is one row. UID is the uid heading or uid= of the entry as printed (Removal, "
                 "Addition, Delivery, Wakeup), Package and User are as printed in the per-app lists, and User of the other rows "
                 "is derived from the uid (the number before the a of u0a123, or the uid divided by 100000). Alarm Type, Tag and "
                 "Reason are as printed; Detail keeps the other fields of an addition or delivery entry as printed. Time As "
                 "Printed is the rtc= wall-clock text of the entry (empty for the per-app lists), Offset From Dump As Printed "
                 "is the printed offset from the moment of the dump. Time (UTC) is the rtc= text converted with the zone shown "
                 "in Bug Report - Device Facts where an entry has one; otherwise it is the nowRTC epoch milliseconds printed in "
                 "the same dump plus the offset (and empty, with a Time Note, where the dump prints no nowRTC).\n"
                 "An entry records that the alarm manager noted that alarm or app time; it does not say what the app or a person "
                 "did, and the lists are the manager's own limited histories (the Samsung wakeup list printed 200 entries on the "
                 "S-series report, which was not checked for a limit). The Expiration history, top alarms and alarm statistics of "
                 "the same dump are not read. User held one value, 0, on all rows of the Samsung, Huawei and Transsion-brand "
                 "reports; the Motorola report has users 0 and 11.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 434, 1,093, 65, 177 and 12 rows, each equal to a "
                 "count of the entries in the raw text per list. On the 368 removal entries of the three Android 15 and 16 "
                 "reports the converted rtc= text and the nowRTC plus offset differed by at most 0.51 seconds. The Android 10 "
                 "reports print the App Alarm history only. All five reports record a UTC+0 time zone, so the wall-clock "
                 "conversion was the identity on every real row; other zones were tested on constructed text only. Not examined: "
                 "Android 11 and 12 and other vendors."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints the service dumps read here; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not print an alarm dump. s20fe_a13 gave 154 rows, equal to its Addition, Delivery and Wakeup history entries and App alarm times (94, 38, 11 and 11).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "history",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 154 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_notification_records": {
        "name": "Bug Report - Notification Records",
        "description": "The notification list and the notification archive in the notification dump of an Android bug report text, "
                       "with the package, channel, importance and times as printed and converted.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Notifications",
        "notes": "One row per NotificationRecord of the Notification List (List: Notification list) and one row per "
                 "StatusBarNotification the dump prints under mArchive (List: Archive) in the notification service dump. The "
                 "notification list is printed, in the tested reports, in the section the bug report labels CRITICAL, the archive in the main one. "
                 "Package, User, Notification ID, Tag, Key, Flags, Category, Group Key and Seen are as printed (a line break "
                 "inside a tag or key is shown as one space), Channel is the channel id of the record's channel, Importance is "
                 "the number after importance= and Importance Reason is mImportanceExplanation. Ticker Text is the short text "
                 "the platform prints for tickerText, shown as printed: of the 64 values that were not null on the five reports "
                 "every one ended with ... and 45 held eight characters before it, so the dump prints a cut form of the text. UID is the uid= line of a list record and is empty for an archive entry. Created, Updated, "
                 "Interruption and Visible Since are mCreationTimeMs, mUpdateTimeMs, mInterruptionTimeMs and mVisibleSinceMs: "
                 "epoch milliseconds, read as UTC, with the printed text in the As Printed columns (the Android 16 reports "
                 "print a readable time beside the number). A number of 0 or outside 2009 to 2100 has no UTC value. Archive "
                 "entries carry no times and no uid. The message text, the extras and the actions of a record are not read.\n"
                 "A row records that the notification manager held or archived that notification; it does not say that anyone "
                 "saw or read it. The archive list is short: the dump printed at most five entries, followed by a ... line where "
                 "the archive holds more (the totals the dump states are 78, 100, 15, 0 and 5 on the Samsung A-series, Samsung "
                 "S-series, Huawei, Motorola and Transsion-brand reports), so the archive rows are a sample the platform chose to "
                 "print and the log names the totals. User held one value, 0, on all rows of the Samsung, Huawei and Motorola "
                 "reports; the Transsion-brand report has a record of user -1. Importance Reason held one value, app, on all "
                 "rows of the Motorola report.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 36, 53, 26, 29 and 9 rows (31, 48, 21, 29 and 4 "
                 "notification list records plus 5, 5, 5, 0 and 5 archive entries), each equal to a count of the record and "
                 "archive headings in the raw text and, for the list records, to an independent parser for the package, user, id, "
                 "importance and creation time. On the 300 times the two Android 16 reports print beside a number, the converted "
                 "value equalled the printed time to the millisecond. Not examined: Android 11 and 12 and other vendors."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints the service dumps read here; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not print the notification settings. Notification records come from the CRITICAL notification dump, which s20fe_a13 and both partial texts of userb2_a13 print: 4 rows and 5 rows (3 and 2, in file order), equal to their NotificationRecord lines.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "bell",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 4 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 5 rows",
        }
    },
    "bugreport_notification_listeners": {
        "name": "Bug Report - Notification Listeners",
        "description": "The notification listener and assistant lists in the notification dump of an Android bug report text, "
                       "with the component, user and state as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Notifications",
        "notes": "One row per component in the lists under Notification listeners and Notification assistant services of the "
                 "notification service dump. Role is Listener or Assistant. List is the list heading: Allowed (the allowed "
                 "components, split at the colons the dump joins them with), Enabled for current profiles, Live and Snoozed. "
                 "Component is as printed, Package is the part before the slash, User is the user printed beside the entry "
                 "(empty where the list prints none) and Detail is the rest of the line without the object address (for example "
                 "isPrimary: true, or SYSTEM and GUEST on live entries). The same component can appear in several lists; each "
                 "list entry is one row. The condition providers, the user-set lists and the trusted listener ids of the same "
                 "dump are not read.\n"
                 "A row says that the notification manager listed that component in that list; it does not say that the "
                 "component read any notification. Role held one value, Listener, on all rows of the Transsion-brand report, "
                 "which lists no assistant.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 21, 27, 11, 20 and 6 rows, each equal to a count "
                 "of the list entries in the raw text. Not examined: Android 11 and 12 and other vendors."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints the service dumps read here; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not print the notification settings. s20fe_a13 gave 18 rows, equal to the components of its Allowed, Enabled, Live and Snoozed lists (4, 4, 8 and 2).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "bell",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 18 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
    "bugreport_notification_channels": {
        "name": "Bug Report - Notification Channels",
        "description": "The per-package notification settings and channels in the notification dump of an Android bug report "
                       "text, with the channel id, importance and deletion state as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Notifications",
        "notes": "One row per NotificationChannel line under each AppSettings: line of the PackagePreferences list of the "
                 "notification service dump, and one row (with an empty Channel ID) for each package whose AppSettings: line "
                 "carries settings but no channel. Package and UID are as printed, User is derived from the uid (the uid divided "
                 "by 100000), App Settings is the text after the uid (for example importance=NONE userSet=false, as printed and "
                 "not interpreted). Channel ID, Importance, Bypass DND, Lockscreen Visibility, Sound, Lights, Show Badge, "
                 "Vibration Enabled, Deleted, Group and User Locked Fields are the mId, mImportance, mBypassDnd, "
                 "mLockscreenVisibility, mSound, mLights, mShowBadge, mVibrationEnabled, mDeleted, mGroup and mUserLockedFields "
                 "values as printed (the last as stored, not decoded). Name is mName as printed; the dump cuts it short and ends it with ... "
                 "(three characters on the five tested reports, where it ended with ... on 736, 1,020, 483, 1,000 and 564 of the 801, 1,126, 483, 1,006 and 566 "
                 "channels, and six on s20fe_a13), so the full name is not shown. Deleted Time is mDeletedTimeMs, read as UTC epoch milliseconds; -1 "
                 "or a number outside 2009 to 2100 has no UTC value. The channel groups and the rest of each channel line are "
                 "not read. Channel IDs are app-chosen text; some channel ids in the tested reports held account names, and they "
                 "are shown as printed.\n"
                 "A row records the notification settings the manager held for the package when the dump ran; it does not say "
                 "that a notification was posted on the channel. Channels with Deleted true are listed by the dump (81, 26, 114, 26 "
                 "and 145 channels). Deleted Time and Deleted Time As Printed are empty on all rows of the Huawei and "
                 "Transsion-brand reports, whose Android 10 lines print no deletion time. User held one value, 0, on all rows "
                 "of the other four reports; the Motorola report has packages of users 0 and 11.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 942, 1,292, 484, 1,246 and 567 rows (801, 1,126, "
                 "483, 1,006 and 566 channels plus 141, 166, 1, 240 and 1 package rows without a channel), each equal to a count "
                 "of the channel lines in the raw text and to an independent parser for the package, uid, channel id, importance "
                 "and deleted flag. Not examined: Android 11 and 12 and other vendors."
                 "\nOn the corpus only the full Samsung dumpState text of s20fe_a13 (Android 13) prints the service dumps read here; the error dumps of s20fe_a13, samsungs20_a13 and sharon_a14 and the partial texts of userb2_a13 do not print the notification settings. s20fe_a13 gave 412 rows: 203 NotificationChannel lines and 209 packages with settings but no channel.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "bell",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two automatically generated dumpstate zips | 412 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        }
    },
}

from scripts import dumpstate_reader
from scripts import dumpstate_usagejobs as uj
from scripts.ilapfuncs import artifact_processor, logfunc

BUCKET_NAMES = {'5': 'EXEMPTED', '10': 'ACTIVE', '20': 'WORKING_SET', '30': 'FREQUENT', '40': 'RARE', '45': 'RESTRICTED',
                '50': 'NEVER'}
NOTE_NO_ANCHOR = 'no nowRTC in the alarm dump: no UTC value'


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


def _log_checkin_cut(label, report):
    if any(what == 'cut' for (what, _key) in uj.counts(report)):
        dumpstate_reader.say_once(logfunc, f'Bug report {label}: the CHECKIN USAGESTATS output carries a dump timeout marker, '
                                           f'the rows from it may be partial')


def _wall(report, text):
    """``(UTC datetime or None, note)`` for a device wall-clock text printed in the report (not a package time)."""
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
    return moment, ('' if moment is not None else dumpstate_reader.NOTE_NONEXISTENT)


def _epoch(text):
    """UTC datetime of the leading digits of a printed epoch-milliseconds value (``1793005582167(2026-10-24 ...)`` also works)."""
    digits = ''
    for char in str(text).strip():
        if not char.isascii() or not char.isdigit():
            break
        digits += char
    if not digits or not dumpstate_reader.plausible_epoch_ms(int(digits)):
        return None
    return dumpstate_reader.epoch_ms_to_utc(int(digits))


def _usage_notes(report, *texts):
    """Time Note of a usage row: a wall-clock text that could not be converted because the report records no zone."""
    wall = [text for text in texts if text and not dumpstate_reader.is_digits(str(text).strip())
            and dumpstate_reader.parse_wall_time(text) is not None and text not in dumpstate_reader.UNSET_WALL_TIMES]
    return dumpstate_reader.NOTE_NO_ZONE if wall and not report.clock.known else ''


def _offset_time(anchor_ms, offset):
    """``(UTC datetime or None, note)`` for a time printed as an offset from the moment of the dump."""
    amount = uj.duration_ms(offset) if offset else None
    if amount is None:
        return None, ''
    if anchor_ms is None:
        return None, NOTE_NO_ANCHOR
    return dumpstate_reader.epoch_ms_to_utc(anchor_ms + amount), ''


@artifact_processor
def bugreport_usage_intervals(context):
    headers = ('Package', 'User', 'Interval', ('Interval Begin (UTC)', 'datetime'), ('Interval End (UTC)', 'datetime'),
               'Interval As Printed', ('Last Time Used (UTC)', 'datetime'), 'Last Time Used As Printed', 'Total Time Used (ms)',
               ('Last Time Visible (UTC)', 'datetime'), 'Last Time Visible As Printed', 'Total Time Visible (ms)',
               ('Last Time Component Used (UTC)', 'datetime'), 'Last Time Component Used As Printed',
               ('Last Time FS (UTC)', 'datetime'), 'Last Time FS As Printed', 'Total Time FS (ms)', 'App Launch Count',
               'Time Note', 'Source Section', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        items = uj.table(report, 'uj_intervals')
        _log_cuts(label, report, 'usagestats', [item.line for item in items if item.section.startswith('DUMP')])
        _log_checkin_cut(label, report)
        for key, number in uj.counts(report).items():
            if key[0] == 'interval_skipped':
                dumpstate_reader.say_once(logfunc, f'Bug report {label}: {number} package rows of {key[1]} with no time, no '
                                                   f'launch and no last-used time were counted and not listed')
        for item in items:
            rows.append((item.package, item.user, item.interval, report.usage_time(item.begin), report.usage_time(item.end),
                         item.range_text or ('%s - %s' % (item.begin, item.end) if item.begin else ''),
                         report.usage_time(item.last_used), item.last_used, uj.time_amount_ms(item.total_used),
                         report.usage_time(item.last_visible), item.last_visible, uj.time_amount_ms(item.total_visible),
                         report.usage_time(item.last_component), item.last_component,
                         report.usage_time(item.last_fs), item.last_fs, uj.time_amount_ms(item.total_fs), item.launches,
                         _usage_notes(report, item.last_used, item.last_visible, item.last_component, item.last_fs),
                         item.section, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_usage_interval_events(context):
    headers = (('Interval Begin (UTC)', 'datetime'), ('Interval End (UTC)', 'datetime'), 'Interval', 'Interval As Printed',
               'User', 'Event', 'Count', 'Total Time (ms)', 'Total Time As Printed', 'Printed After', 'Source Section',
               'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        items = uj.table(report, 'uj_interval_events')
        _log_cuts(label, report, 'usagestats', [item.line for item in items if item.section.startswith('DUMP')])
        _log_checkin_cut(label, report)
        for item in items:
            rows.append((report.usage_time(item.begin), report.usage_time(item.end), item.interval,
                         item.range_text or ('%s - %s' % (item.begin, item.end) if item.begin else ''), item.user, item.event,
                         item.count, uj.time_amount_ms(item.total), item.total, item.tail, item.section, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_standby_buckets(context):
    headers = ('Package', 'User', 'Bucket', 'Bucket Name', 'Reason', 'Used (as printed)', 'Used By User (as printed)',
               'Used Screen (as printed)', 'Last Predicted (as printed)', 'Expiry Times (as printed)', 'Last Job (as printed)',
               'Last Informed Bucket', 'Next Estimated Launch (as printed)', 'Idle', 'Other Fields', 'Source Section',
               'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        items = uj.table(report, 'uj_standby')
        _log_cuts(label, report, 'usagestats', [item.line for item in items if item.section.startswith('DUMP')])
        _log_checkin_cut(label, report)
        for item in items:
            rows.append((item.package, item.user, item.bucket, BUCKET_NAMES.get(item.bucket, ''), item.reason, item.used,
                         item.used_by_user, item.used_scr, item.last_pred, item.expiry, item.last_job, item.last_informed,
                         item.next_launch, item.idle, item.other, item.section, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_scheduled_jobs(context):
    headers = ('Package', 'User', 'List', 'Namespace', 'Job ID', 'UID', 'Service', 'Tag', 'Job Type', 'Persisted', 'Priority',
               'Requires', 'Network', 'Minimum Latency', 'Max Execution Delay', 'Extras', 'Required Constraints',
               'Satisfied Constraints', 'Unsatisfied Constraints', 'Standby Bucket', 'Enqueue Time (relative)',
               'Run Time Earliest (relative)', 'Run Time Latest (relative)', ('Last Successful Run (UTC)', 'datetime'),
               'Last Successful Run As Printed', ('Last Failed Run (UTC)', 'datetime'), 'Last Failed Run As Printed',
               'Completed (relative)', 'Restricted Due To', 'Ready', 'Time Note', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        items = uj.table(report, 'uj_jobs')
        _log_cuts(label, report, 'jobscheduler', [item.line for item in items])
        for item in items:
            success, note_success = _wall(report, item.last_success)
            failure, note_failure = _wall(report, item.last_failure)
            note = '; '.join(dict.fromkeys(part for part in (note_success, note_failure) if part))
            rows.append((item.package, item.user, item.listing, item.namespace, item.job_id, item.uid_label, item.service,
                         item.tag, item.job_type, item.persisted, item.priority, item.requires, item.network, item.min_latency,
                         item.max_delay, item.extras, item.required, item.satisfied, item.unsatisfied, item.bucket,
                         item.enqueue, item.run_earliest, item.run_latest, success, item.last_success, failure,
                         item.last_failure, item.completed, item.restricted, item.ready, note, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_pending_alarms(context):
    headers = (('Trigger Time (UTC)', 'datetime'), 'Trigger As Printed', ('Latest Trigger Time (UTC)', 'datetime'),
               'Latest Trigger As Printed', 'List', 'Alarm Type', 'Package (as printed)', 'Tag', 'Original When (as printed)',
               'Window', 'Repeat Interval (ms)', 'Count', 'Flags', 'Exact Allow Reason', 'Operation', 'Listener', 'Batch',
               'Index', 'Time Note', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        items = uj.table(report, 'uj_alarms')
        _log_cuts(label, report, 'alarm', [item.line for item in items])
        for item in items:
            if item.clock_ms is not None:
                moment, latest, note = dumpstate_reader.epoch_ms_to_utc(item.clock_ms), None, ''
                shown = '%s = %s' % (item.when, item.clock_text)
            else:
                moment, note = _offset_time(item.anchor_ms, item.when)
                latest, latest_note = _offset_time(item.anchor_ms, item.max_when)
                note = note or latest_note
                shown = item.when
            rows.append((moment, shown, latest, item.max_when, item.listing, item.alarm_type, item.package, item.tag,
                         item.orig_when, item.window, item.repeat, item.count, item.flags, item.exact_reason, item.operation,
                         item.listener, item.batch, item.index, note, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_alarm_history(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Offset From Dump As Printed', 'History', 'UID', 'Package', 'User',
               'Alarm Type', 'Tag', 'Reason', 'Detail', 'Time Note', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        items = uj.table(report, 'uj_alarm_history')
        _log_cuts(label, report, 'alarm', [item.line for item in items])
        for item in items:
            moment, note = None, ''
            if item.rtc_text:
                moment, note = _wall(report, item.rtc_text)
            if moment is None and item.offset:
                moment, note = _offset_time(item.anchor_ms, item.offset)
            rows.append((moment, item.rtc_text, item.offset, item.history, item.uid_label, item.package, item.user,
                         item.alarm_type, item.tag, item.reason, item.detail, note, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_notification_records(context):
    headers = (('Created (UTC)', 'datetime'), 'Created As Printed', ('Updated (UTC)', 'datetime'), 'Updated As Printed',
               ('Interruption (UTC)', 'datetime'), 'Interruption As Printed', ('Visible Since (UTC)', 'datetime'),
               'Visible Since As Printed', 'List', 'User', 'Package', 'UID', 'Notification ID', 'Tag', 'Key', 'Channel',
               'Importance', 'Importance Reason', 'Flags', 'Category', 'Group Key', 'Ticker Text', 'Seen', 'Source Line',
               'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        items = uj.table(report, 'uj_notifications')
        _log_cuts(label, report, 'notification', [item.line for item in items])
        for (what, key), number in uj.counts(report).items():
            if what == 'archive_total':
                listed = uj.counts(report).get(('archive_listed', key), 0)
                if number > listed:
                    dumpstate_reader.say_once(
                        logfunc, f'Bug report {label}: the notification archive holds {number} notifications and the dump '
                                 f'lists {listed} of them')
        for item in items:
            rows.append((_epoch(item.created), item.created, _epoch(item.updated), item.updated, _epoch(item.interrupted),
                         item.interrupted, _epoch(item.visible_since), item.visible_since, item.listing, item.user,
                         item.package, item.uid, item.notification_id, item.tag, item.key, item.channel, item.importance,
                         item.importance_note, item.flags, item.category, item.group_key, item.ticker, item.seen, item.line,
                         label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_notification_listeners(context):
    headers = ('Role', 'List', 'Package', 'Component', 'User', 'Detail', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        items = uj.table(report, 'uj_listeners')
        _log_cuts(label, report, 'notification', [item.line for item in items])
        for item in items:
            rows.append((item.role, item.listing, item.package, item.component, item.user, item.detail, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_notification_channels(context):
    headers = ('Package', 'UID', 'User', 'App Settings (as printed)', 'Channel ID', 'Name (as printed)', 'Importance',
               'Bypass DND', 'Lockscreen Visibility', 'Sound', 'Lights', 'Show Badge', 'Vibration Enabled', 'Deleted',
               ('Deleted Time (UTC)', 'datetime'), 'Deleted Time As Printed', 'Group', 'User Locked Fields (as stored)',
               'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        items = uj.table(report, 'uj_channels')
        _log_cuts(label, report, 'notification', [item.line for item in items])
        for item in items:
            rows.append((item.package, item.uid, uj.uid_user(str(item.uid)), item.app_settings, item.channel_id, item.name,
                         item.importance, item.bypass_dnd, item.lockscreen, item.sound, item.lights, item.badge,
                         item.vibration, item.deleted, _epoch(item.deleted_ms), item.deleted_ms, item.group,
                         item.locked_fields, item.line, label))
    return headers, rows, _source_path(context, reports)
