__artifacts_v2__ = {
    "bugreport_system_log": {
        "name": "Bug Report - System Log",
        "description": "The logcat lines of the SYSTEM LOG and SYSTEM LOG AFTER DONE sections of an Android bug report text, "
                       "with time, uid, process id, thread id, level, tag and message as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Logs",
        "notes": "One row per line in logcat form of the SYSTEM LOG section (logcat -v threadtime -v uid) and, where the report "
                 "prints it, the SYSTEM LOG AFTER DONE section (the same command run once more after the dump, limited with -T). "
                 "Source Section says which one printed the row. Time As Printed is month, day and clock time with milliseconds in "
                 "the device's local time, without a year. Time (UTC) takes the year from the report time (the latest year, the "
                 "one of the report time or the one before, that does not put the line more than a day after the report time) "
                 "and converts with the zone shown in Bug Report - Device Facts; it is empty where the report records no zone. "
                 "UID is the uid column as printed (a number or a name such as root or shell), PID and TID are the process and "
                 "thread ids, Level is the letter as printed, Tag is the tag with the platform's padding removed, and Message is "
                 "the rest of the line, shown up to 2,000 characters with control characters shown as spaces. Buffer is the "
                 "text of the last '--------- beginning of' marker above the line (crash, system or main in the tested "
                 "reports). Log lines can hold text written by apps and by people using the phone; they are shown as printed.\n"
                 "The sections hold what the log buffers held when the dump ran, which spanned about 4 minutes (Transsion-brand), "
                 "1 hour (Huawei), 10.6 days (A-series), 7.5 hours (Motorola) and 37 minutes (S-series) in the five tested "
                 "reports, so a line that is not listed says nothing about earlier events. SYSTEM LOG AFTER DONE (two of the "
                 "five reports) can repeat lines of the first section. A non-blank line that is not in logcat form is not a row; "
                 "the log says how many there were (none in the tested reports apart from the markers). The table stops at "
                 "500,000 rows with a warning in the log (none of the tested reports reached it). A command stopped by the "
                 "platform's time limit prints a line the reader notices; the log then says the rows may be partial. Source "
                 "Section held one value, SYSTEM LOG, on all rows of the Transsion-brand, Huawei and Motorola reports, which "
                 "print no SYSTEM LOG AFTER DONE section.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 4,329 (Transsion-brand), 5,795 (Huawei), 342,885 "
                 "(A-series; 294,153 and 48,732 in the two sections), 20,077 (Motorola) and 405,850 (S-series; 273,200 and "
                 "132,650) rows, each equal to a count of lines starting with a "
                 "logcat timestamp in these sections of the raw text, with time, uid, process id, thread id, level, tag, "
                 "message and line equal to an independent split on every row. All five reports carry the uid column, print "
                 "every line with its own header, and record a UTC+0 zone without daylight saving, so the conversion to UTC "
                 "was the identity on every real row. Constructed text only: the layout without a uid column, a time printed "
                 "with a year, other zones and daylight saving, lines that are not in logcat form, a command stopped by a time "
                 "limit, and a year change inside the logs. Not examined: Android 11 to 14, other vendors, and logcat sections "
                 "other than these (RADIO LOG and LAST LOGCAT are not read here).",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "file-text"
    },
    "bugreport_event_log": {
        "name": "Bug Report - Event Log",
        "description": "The lines of the EVENT LOG section of an Android bug report text, with time, uid, process id, thread id, "
                       "event name and the bracketed values as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Logs",
        "notes": "One row per line in logcat form of the EVENT LOG section (logcat -b events -v threadtime -v uid). Tag is the "
                 "event name and Message is the bracketed value list as printed, not decoded: the meaning of each position "
                 "belongs to the event and is not applied here. Time As Printed, Time (UTC), UID, PID, TID, Level, Buffer and the "
                 "other columns are read as in Bug Report - System Log, including the year rule for the time. Level held one value, "
                 "I, on all rows of all five tested reports, and Buffer held one value, events, on the three reports whose "
                 "section opens with that marker (it is empty on all rows of the Huawei and Transsion-brand reports, which print "
                 "none). The section is one section, so there is no Source Section column. "
                 "The Huawei report prints 12 lines in this section, all with the tag auditd. A line that is not in logcat "
                 "form is not a row and is counted in the log. The buffer is limited, so an event that is not listed says "
                 "nothing about earlier use; the table stops at 500,000 rows with a warning in the log.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 15,122, 12, 2,863, 10,296 and 16,552 rows "
                 "(A-series, Huawei, Transsion-brand, Motorola and S-series respectively), each equal to a count of timestamped "
                 "lines in the raw section and to an independent split, field by field. The conversion to UTC was the identity "
                 "on every real row (UTC+0 zone on all five). Constructed only: a continuation of a value list on a line of its "
                 "own, zones with an offset, and the layout without a uid column. Not examined: Android 11 to 14 and other vendors.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "list"
    },
    "bugreport_kernel_log": {
        "name": "Bug Report - Kernel Log",
        "description": "The lines of the KERNEL LOG and LAST KMSG sections of an Android bug report text, with the "
                       "seconds-since-boot stamp, level, cpu or task tag and message as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Logs",
        "notes": "One row per non-blank line of the KERNEL LOG (dmesg) section and of the LAST KMSG section; Source Section says "
                 "which. The heading of LAST KMSG names the file the report took the text from (/proc/last_kmsg or "
                 "/sys/fs/pstore/console-ramoops-0 in the tested reports). Seconds Since Boot is the number in the first square "
                 "brackets, a count from the kernel's own clock, shown as printed: no clock time is computed from it, because the "
                 "report does not print the kernel clock's start. Level is the number in angle brackets that starts a KERNEL "
                 "LOG line, as printed (empty on LAST KMSG lines in the tested reports). CPU or Task is the second bracket "
                 "([T123], [C1], [ 2: kworker/u16:2: 86]) or a cpu word such as c0, as printed. Message is the rest of the "
                 "line, up to 2,000 characters. A line without a stamp (for example the first line of a ring buffer that was "
                 "cut) keeps its whole text in Message and leaves the first three columns empty. The platform's own notice "
                 "\"Skipping '...' on user build.\" that can follow the last kernel line is not a row. Kernel messages can "
                 "carry device names, network names and addresses; they are shown as printed. The log buffer is limited, "
                 "so a message that is not listed says nothing about earlier events. A section is empty or holds only an "
                 "error line when the platform could not read the log: the Huawei report's KERNEL LOG holds a single line "
                 "from the program that reads the kernel log, which reports a failed read, and nothing else. The table stops at 500,000 rows with a warning in the log.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 23,099 (A-series; 1,198 and 21,901 in "
                 "KERNEL LOG and LAST KMSG), 22,339 (S-series; 2,526 and 19,813), 1,279 (Motorola; 1,034 and 245), 10,887 "
                 "(Transsion-brand; 10,884 and 3) and 1 (Huawei) rows, each equal to a "
                 "count of the non-blank lines of the two sections in the raw text, with the section, stamp, level and line "
                 "equal to an independent regular expression on every row. Lines without a stamp: 43 (A-series), 1,776 (S-series) and the one "
                 "line of the Huawei report, none on the others; Seconds Since Boot, Level and CPU or Task are empty on that "
                 "Huawei row. Level is empty on every LAST KMSG row. Not examined: Android 11 to 14, other vendors, and kernel "
                 "lines that carry a wall-clock stamp or another prefix than those above.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "cpu"
    },
    "bugreport_anr_threads": {
        "name": "Bug Report - ANR Trace Threads",
        "description": "The threads of the thread dumps in an Android bug report: the VM TRACES sections of the text and the "
                       "anr files inside a bug report zip, with process, thread name, ids, state and top frame as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Boot, Crash and Dropbox",
        "notes": "One row per thread of each process dump (a block headed '----- pid N at TIME -----') in the VM TRACES JUST NOW, "
                 "VM TRACES AT LAST ANR and HISTORICAL ANR sections of the text, and in the anr_* and trace* files under "
                 "FS/data/anr of a bug report zip (the zip made by adb bugreport or kept by the Shell app). Source Section is the "
                 "section name or the zip member; Source File is the text or the zip. Dump Time As Printed is the time in the dump "
                 "header: nanoseconds and a UTC offset on the Android 15 and 16 reports (read exactly), seconds without an offset "
                 "on the Android 10 reports (converted with the report zone). Process is the Cmd line of the dump and Subject is "
                 "the 'Subject:' line that precedes the first dump of a file or section (empty where there is none). Thread, "
                 "Priority, Thread ID, State, Daemon, System Thread ID, Nice, Cgroup, OS State, User Ticks, System Ticks and Core "
                 "are the values the runtime prints for the thread (prio=, tid=, the state word after tid, sysTid=, nice=, cgrp=, "
                 "state=, utm=, stm=, core=); native threads listed as '\"name\" sysTid=N' have no priority, Thread ID or State. "
                 "State is the runtime's word as printed (Native, Waiting, TimedWaiting, Runnable, Blocked, '(not attached)'). Top Frame is "
                 "the first frame line of the thread as printed, cut at 300 characters, and Frames counts its frame lines; the "
                 "rest of the stack, held locks, mutexes and the 'Waiting Channels' blocks are not read. A dump is a snapshot of "
                 "the process at the dump time: a row does not say that a thread caused or took part in an ANR. VM TRACES JUST NOW "
                 "is taken when the report is made; the heading of VM TRACES AT LAST ANR names the anr file it repeats. In all "
                 "five tested reports that section equals the anr file it names, row for row, so its threads appear twice; HISTORICAL "
                 "ANR (Motorola) equals VM TRACES AT LAST ANR the same way.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): thread rows from the text sections 3,088, 4,143, "
                 "4,575, 2,956 and 1,847 and from zip members 46, 145, 702, 113 and 16 (A-series, S-series, Huawei, Motorola, "
                 "Transsion-brand), each equal to a count of thread header lines in the raw text and in the zip members, with the "
                 "name, tid, priority and line equal to an independent regular expression on every row (control characters "
                 "in a name are shown as spaces). Subject is empty on both Android 10 reports. All five reports record UTC+0, "
                 "so conversion of a dump time without an offset was the identity. The S-series zip also holds trace_00, an older "
                 "dump file with a different content, read in the same way. Constructed only: other zones and offsets in a dump "
                 "header, a dump time without an offset on an Android 10 layout in another zone, and the 500,000 thread limit "
                 "(the log says when it is reached). Not examined: Android 11 to 14, other vendors, and files of other names in "
                 "the anr folder.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "alert-triangle"
    },
    "bugreport_tombstones": {
        "name": "Bug Report - Tombstones",
        "description": "The tombstone files inside an Android bug report zip, with the crash time, process, command line, "
                       "signal, abort message and build as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Boot, Crash and Dropbox",
        "notes": "One row per member named FS/data/tombstones/tombstone_<n> (text) or tombstone_<n>.pb (protobuf) in a bug report zip "
                 "(the zip made by adb bugreport or kept by the Shell app; a bug report text read alone has none). The fields are "
                 "read with the parsers of Android Tombstones in androidDropbox.py, which is not repeated here: that artifact reads "
                 "tombstone files from a file system extraction under tombstones folders, and this one reads the copies a bug "
                 "report zip carries, which that artifact cannot reach because the zip is one file. Columns and their meaning "
                 "are those of Android Tombstones (Timestamp is the report's own timestamp with its UTC offset, shown in UTC; "
                 "Signal, Abort Message, Process Uptime and Build Fingerprint are as stored; the protobuf form is read field "
                 "by field and gives no thread name). Format says which form the row came from, a crash present in both forms "
                 "appears twice, Size is the size of the member, and Zip Member names it. A member that is empty, damaged or "
                 "not a tombstone message still gets a row with blank fields and the log says why; a tombstone wrapped with "
                 "headers (the form dropbox entries use) is not unwrapped here. Text members are read up to 512 KiB and protobuf "
                 "members up to 8 MiB. The backtrace, memory and thread sections are not read. Tombstones are the files present "
                 "when the report was made, not a crash history.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 2, 64, 3, 64 and 10 rows (A-series, S-series, "
                 "Huawei, Motorola, Transsion-brand), each equal to the number of matching zip members. The Huawei and "
                 "Transsion-brand reports hold text members only (the Transsion-brand member tombstone_01 has 0 bytes, so its "
                 "row is blank, as is its Timestamp); the other three hold a protobuf twin for each text member. Of the "
                 "twin pairs (1 on the A-series report, 32 on the S-series, 32 on the Motorola), the compared fields (time, "
                 "process, pid, tid, uid, uptime, build, signal and abort message) were equal on 1, 32 and 31; the remaining "
                 "Motorola pair differs by one trailing character of the abort message. "
                 "Command Line and Process Uptime are empty on all rows of the Transsion-brand report and Command Line, Abort Message and Process Uptime on all rows of the Huawei report (the Android 10 text form does not print them), and Thread is empty on every protobuf row. Constructed only: "
                 "a wrapped protobuf, a damaged member and a time with a negative offset. Not examined: Android 11 to 14 and "
                 "other vendors.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "cpu"
    },
    "bugreport_dropbox_entries": {
        "name": "Bug Report - Dropbox Entries",
        "description": "The dropbox entries an Android bug report text lists or prints, with time, tag, content type, size "
                       "and, for printed entries, the process, package and first line as stored.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Boot, Crash and Dropbox",
        "notes": "Two sources. DUMP OF SERVICE dropbox lists the entries the dropbox kept (one line each: time, tag, content type "
                 "and size, or 'contents lost'); Preview is the indented line the platform prints under it, which the platform "
                 "cuts and which joins header lines with '/'. The DROPBOX SYSTEM SERVER CRASHES, DROPBOX SYSTEM APP CRASHES and "
                 "DROPBOX SYSTEM WATCHDOG CRASHES sections (dumpsys dropbox -p <tag>) print the whole entries of the tags "
                 "system_server_crash, system_app_crash and system_server_watchdog; for these Process, PID, UID, Packages (repeated "
                 "Package headers joined with '; '), Foreground and Subject are the header lines of the entry as stored and First Body "
                 "Line is the first line after the header block (cut at 400 characters; it holds exception text as written by the "
                 "app). An entry printed in both places appears twice; Source Section tells the copies apart. Content is the text "
                 "in the parentheses before the size (text, data, compressed text, contents lost) and Size is in bytes. Time As "
                 "Printed is the entry time in the device's local time, converted with the zone shown in Bug Report - Device "
                 "Facts. Tags are the callers' own and are shown as stored. The log gives the 'Drop box contents: N entries' line of "
                 "each report. The dropbox keeps a bounded number of entries and trims old ones, so the list is a recent window "
                 "and a tag with '(No entries found.)' says nothing about the device. These sections are the report's copy of the "
                 "dropbox; Android Dropbox - App Crashes, ANRs and Errors reads the entry files themselves in a file system "
                 "extraction. A printed entry without a header block keeps its first line in First Body Line (constructed only).\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): listing rows 12 (A-series), 183 (S-series), 73 "
                 "(Huawei), 194 (Motorola) and 299 (Transsion-brand), each equal to the number of entries the listing prints "
                 "and to the 'Drop box contents' line; printed entries 1 (A-series, "
                 "system_server_crash) and 8 (Huawei, system_app_crash), and none on the other three, whose print sections say "
                 "'(No entries found.)'. Process, PID, UID, Packages, Foreground, Subject and First Body Line are empty on "
                 "every row of the Transsion-brand, Motorola and S-series reports (no entry is printed there), PID, UID, Packages, "
                 "Foreground and Subject on every row of the A-series report, Subject on every row of the Huawei report, and "
                 "Preview on every row of the Motorola report. Not examined: entries of other tags are listed but "
                 "not printed by the report (only the three tags above are), Android 11 to 14 and other vendors.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "archive"
    },
    "bugreport_reset_reasons": {
        "name": "Bug Report - Reset Reasons",
        "description": "The reset history lines of the AP RESET INFO EXTEND, POWER OFF RESET REASON and POWER OFF RESET REASON "
                       "BACKUP sections of an Android bug report text, with time, event, flag and detail as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Boot, Crash and Dropbox",
        "notes": "These sections are printed by the Samsung builds tested (the A-series and S-series reports, Android 16) and by "
                 "none of the other three reports. Form 'event line' is a line 'time | EVENT | flag | detail' (the history file "
                 "eRR.p, and the same lines inside the power off files): Event is the word between the first pair of bars (ON, "
                 "SHUTDOWN, REBOOT, LPM, PLATFORM or empty), Flag the second field (RP, NP, PF_SR or empty) and Detail the rest, "
                 "all as printed and not decoded; the number in brackets that ends many details is shown as printed. Form 'record' is "
                 "a record of the power off files: a 'yy/mm/dd HH:MM:SS' header and its 'reason :' line (Event holds the word "
                 "reason, Detail its text), and Caller Frames holds up to three stack frames printed after the last ShutdownThread "
                 "frame of the Java trace that follows. Time As Printed carries a UTC offset on event lines, so Time (UTC) "
                 "is exact (offsets +0000, +0700 and +0100 occur in the tested reports); a record header has no offset and is "
                 "converted with the report zone, which Time Note says; a line whose time is before 2009 has no UTC value. Two "
                 "event lines of the A-series report print 2010-01-01 times, shown as printed. The first line of eRR.p (binary "
                 "bytes) and the shutdown step lines that start with a clock time are not rows. The history is a file the "
                 "device keeps: it spans the year 2026 (A-series) and the years 2024 to 2026 (S-series), and "
                 "the power off files hold 7 (A-series) and 2 (S-series) records and their BACKUP sections 7 and 7, so a reset that is not listed "
                 "says nothing about whether it happened.\n"
                 "Evidence tiers. Data-proven on two real bug reports (Samsung A-series and S-series on Android 16): 204 and 952 "
                 "rows, equal to the pipe-separated lines (190 and 943) and the record headers (14 and 9) counted in the raw "
                 "text. Constructed only: a negative offset, a record time in another zone, and the cuts. The other three reports do not print "
                 "these sections. SHUTDOWN CHECKPOINTS (a Motorola section) appears in one of the "
                 "five reports and is not read.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "power"
    },
    "bugreport_vendor_services": {
        "name": "Bug Report - Vendor Service Lines",
        "description": "The lines of 11 Samsung dumpsys services of an Android bug report text, with the first time printed in "
                       "each line, as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report - Vendor",
        "notes": "One row per non-blank line of these dumpsys services: SveService, secims, sec_location, "
                 "sem_wifi, nfc SamsungExtension, advanced_protection, application_policy, enterprise_policy, persona, "
                 "motion_recognition and PkgPredictorService. The knoxguard_service and knoxcustom dumps are not here: "
                 "Bug Report - knoxguard_service Log and Bug Report - knoxcustom State present them, so that each fact appears "
                 "once. They are the vendor services with event histories or policy "
                 "states that both Samsung reports among the five tested (A-series and S-series, Android 16) print; vendor services "
                 "of one report only (Motorola moto* and motsettings, Huawei hw*, powergenius) are not read, and neither are the "
                 "Samsung services that print counters, tables or parameter lists (sdhms, HqmManagerService, "
                 "ChimeraManagerService, AODManagerService, CustomFrequencyManagerService, CocktailBarService, "
                 "SemInputDeviceManagerService, IntelligentBatterySaverService, PowerSolution_Framework_service, "
                 "knox_nwFilterMgr_policy, knox_vpn_policy, multicontrol, mum_container_policy, profilepolicy). Service is the "
                 "section name, Indent the number of leading spaces of the line (the dump's own nesting, with the leading "
                 "spaces removed from Text) and Text the line cut at 400 characters. Time As Printed is the first time found in "
                 "the first 80 characters of the line, in the form the service prints (2026-02-03 10:13:14, 02/03/2026 03:05:06.789, "
                 "2026/08/14 18:20:30, 05-09 08:41:12.345 without a year); it is empty for most lines. Time (UTC) converts it with "
                 "the report zone; a time without a year takes the year from the report time as in Bug Report - System Log, a time "
                 "whose year is masked by the platform (02/03/*026) or that is before 2009 has no UTC value, and Time Note says so. "
                 "The header lines of each service (host process, threads in use, client pids, 'Unknown argument'), the duration "
                 "line and lines made only of 60 or more letters, digits, plus, slash and equals signs (encoded blobs: 3,645 and "
                 "3,587 on the two reports, almost all in nfc SamsungExtension) are not rows. A service stops at 20,000 rows. "
                 "The services print SIM, location-request, Wi-Fi and enterprise policy text, partly masked by the platform, which is "
                 "shown as printed; a row says that the service printed the line, not what a person did. The sem_wifi dump of the "
                 "A-series report was cut by the platform's 10 second limit, "
                 "so its rows may be partial (the log says so); the platform's timeout marker line is kept as a row of that service.\n"
                 "Evidence tiers. Data-proven on two real bug reports (Samsung A-series and S-series on Android 16): 14,027 and "
                 "25,916 rows, each equal to a count of the non-blank lines of these services in the raw text after the exclusions "
                 "above. Time (UTC) is filled on 4,021 of the 14,027 and 9,228 of the 25,916 rows; most lines print no time. "
                 "Of the 11,973 and 21,868 rows with a time, 7,952 and 12,640 have a masked year (no UTC value) and 2,962 and "
                 "4,306 print no year (the year comes from the report time). Not in the other three reports (their services are not printed), so 2 of 5. Both reports record a UTC+0 "
                 "zone; other zones are constructed only. Not examined: other Samsung builds and Android versions.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "server"
    },
}

import io
import re
import zipfile

from scripts import dumpstate_reader
from scripts import dumpstate_logscrash as logscrash
from scripts.artifacts.androidDropbox import _offset_ts, _text, _tombstone_proto_fields, _tombstone_text_fields
from scripts.ilapfuncs import artifact_processor, logfunc

TOMBSTONE_MEMBER = re.compile(r'^FS/data/tombstones/tombstone_\d+(?:\.pb)?$')
ANR_MEMBER = re.compile(r'^FS/data/anr/(?:anr_|trace)[^/]*$')
TEXT_TOMBSTONE_CAP = 512 * 1024
PROTO_TOMBSTONE_CAP = 8 * 1024 * 1024


def _reports(context):
    """The bug report texts among the staged files, as (Source File label, Report) pairs."""
    return dumpstate_reader.load_reports(context.get_files_found(), context.get_relative_path, logfunc)


def _source_path(context, reports):
    """The staged files that were read; the matched files when none was a bug report."""
    paths = [report.source.path for _label, report in reports] or sorted(str(path) for path in context.get_files_found())
    return '\n'.join(dict.fromkeys(str(path) for path in paths))


def _log_zone(label, report):
    if not report.clock.known:
        dumpstate_reader.say_once(logfunc, f'Bug report {label}: the report records no usable time zone, Time (UTC) is empty')


def _log_service_cuts(label, report, names):
    """Say so when the platform cut a dump of one of the services ``names`` (the rows from it may be partial)."""
    for section in report.sections:
        if section.kind == 'service' and section.name in names and section.timeout_ms:
            dumpstate_reader.say_once(logfunc, f'Bug report {label}: the {section.name} service dump was cut by a '
                                               f'{section.timeout_ms} ms timeout, the rows from it may be partial')


def _log_unparsed(label, report, names):
    """Say how many non-blank lines of the logcat sections ``names`` were not in logcat form (they are not rows)."""
    for name in names:
        count = logscrash.tables(report).unparsed.get(name)
        if count:
            dumpstate_reader.say_once(logfunc, f'Bug report {label}: {count} non-blank lines of {name} are not in logcat '
                                               f'form and are not rows')


def _open_zip(path, label):
    """The opened zip of a bug report, or None (and one log line) when it cannot be opened."""
    try:
        return zipfile.ZipFile(path)
    except dumpstate_reader.READ_ERRORS as error:
        dumpstate_reader.say_once(logfunc, f'Bug report {label}: could not open the zip: {error}')
        return None


def _zip_sources(reports):
    """``[(zip path, Source File label)]`` for the reports whose text sits inside a zip (each zip once)."""
    found = {}
    for label, report in reports:
        if report.source.member:
            found.setdefault(report.source.path, label.partition('!/')[0])
    return list(found.items())


def _member_lines(archive, name):
    """The lines of one zip member as text, split on newlines only."""
    stream = io.BufferedReader(archive.open(name), buffer_size=1 << 20)
    try:
        for raw in dumpstate_reader.iter_lines(stream):
            if raw.endswith(b'\n'):
                raw = raw[:-1]
                if raw.endswith(b'\r'):
                    raw = raw[:-1]
            yield raw.decode('utf-8', 'replace')
    finally:
        stream.close()


# ---------------------------------------------------------------------------------------------
# Logcat
# ---------------------------------------------------------------------------------------------
def _log_rows(context, table, sections, with_section):
    headers = [('Time (UTC)', 'datetime'), 'Time As Printed', 'UID', 'PID', 'TID', 'Level', 'Tag', 'Message', 'Buffer']
    if with_section:
        headers.append('Source Section')
    headers += ['Source Line', 'Source File']
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _log_zone(label, report)
        _log_unparsed(label, report, sections)
        for item in getattr(logscrash.tables(report), table):
            if item[0] in sections:
                row = [logscrash.logcat_utc(report, item[1]), item[1], item[2], item[3], item[4], item[5], item[6], item[7],
                       item[8]]
                if with_section:
                    row.append(item[0])
                rows.append(tuple(row + [item[9], label]))
    return tuple(headers), rows, _source_path(context, reports)


@artifact_processor
def bugreport_system_log(context):
    return _log_rows(context, 'system_log', ('SYSTEM LOG', 'SYSTEM LOG AFTER DONE'), True)


@artifact_processor
def bugreport_event_log(context):
    return _log_rows(context, 'event_log', ('EVENT LOG',), False)


# ---------------------------------------------------------------------------------------------
# Kernel log
# ---------------------------------------------------------------------------------------------
@artifact_processor
def bugreport_kernel_log(context):
    headers = ('Seconds Since Boot (as printed)', 'Level (as printed)', 'CPU or Task (as printed)', 'Message',
               'Source Section', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        for item in logscrash.tables(report).kernel_lines:
            rows.append((item[1], item[2], item[3], item[4], item[0], item[5], label))
    return headers, rows, _source_path(context, reports)


# ---------------------------------------------------------------------------------------------
# Thread dumps
# ---------------------------------------------------------------------------------------------
def _thread_row(report, item, source_file):
    moment = logscrash.stamp_utc(report, item[3])[0] if item[3] else None
    return (moment, item[3], item[1], item[2], item[4], item[5], item[6], item[7], item[8], item[9], item[10], item[11],
            item[12], item[13], item[14], item[15], item[16], item[17], item[18], item[0], item[19], source_file)


@artifact_processor
def bugreport_anr_threads(context):
    headers = (('Dump Time (UTC)', 'datetime'), 'Dump Time As Printed', 'Process ID', 'Process', 'Subject', 'Thread',
               'Daemon', 'Priority', 'Thread ID', 'State', 'System Thread ID', 'Nice', 'Cgroup', 'OS State',
               'User Ticks', 'System Ticks', 'Core', 'Top Frame', 'Frames', 'Source Section', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _log_zone(label, report)
        rows.extend(_thread_row(report, item, label) for item in logscrash.tables(report).anr_threads)
    for path, label in _zip_sources(reports):
        report = [one for _label, one in reports if one.source.path == path][0]
        archive = _open_zip(path, label)
        if archive is None:
            continue
        with archive:
            for name in sorted(info.filename for info in archive.infolist() if ANR_MEMBER.match(info.filename)):
                try:
                    found, full = logscrash.read_trace_text(name, _member_lines(archive, name), dumpstate_reader.MAX_ROWS)
                except dumpstate_reader.READ_ERRORS as error:
                    dumpstate_reader.say_once(logfunc, f'Bug report {label}: {name} could not be read: {error}')
                    continue
                if full:
                    dumpstate_reader.say_once(logfunc, f'Bug report {label}: {name} holds more than '
                                                       f'{dumpstate_reader.MAX_ROWS} threads, the rest were not kept')
                rows.extend(_thread_row(report, item, label) for item in found)
    return headers, rows, _source_path(context, reports)


# ---------------------------------------------------------------------------------------------
# Tombstones inside the zip
# ---------------------------------------------------------------------------------------------
BLANK_TOMBSTONE = dict.fromkeys(('process', 'cmdline', 'thread', 'pid', 'tid', 'uid', 'signal', 'abort', 'uptime', 'build',
                                 'when'), '')


@artifact_processor
def bugreport_tombstones(context):
    headers = (('Timestamp (UTC)', 'datetime'), 'Process', 'Command Line', 'Thread', 'PID', 'TID', 'UID', 'Signal',
               'Abort Message', 'Process Uptime', 'Build Fingerprint', 'Format', 'Size (bytes)', 'Zip Member',
               'Source File')
    rows = []
    reports = _reports(context)
    for path, label in _zip_sources(reports):
        archive = _open_zip(path, label)
        if archive is None:
            continue
        with archive:
            for info in sorted(archive.infolist(), key=lambda item: item.filename):
                name = info.filename
                if not TOMBSTONE_MEMBER.match(name):
                    continue
                is_proto = name.endswith('.pb')
                fields = None
                try:
                    with archive.open(name) as handle:
                        data = handle.read((PROTO_TOMBSTONE_CAP if is_proto else TEXT_TOMBSTONE_CAP) + 1)
                    data = data[:PROTO_TOMBSTONE_CAP if is_proto else TEXT_TOMBSTONE_CAP]
                    if data:
                        fields = _tombstone_proto_fields(data) if is_proto else _tombstone_text_fields(_text(data))
                except dumpstate_reader.READ_ERRORS as error:
                    dumpstate_reader.say_once(logfunc, f'Bug report {label}: {name} could not be read: {error}')
                if fields is None:
                    dumpstate_reader.say_once(logfunc, f'Bug report {label}: {name} ({info.file_size} bytes) holds no '
                                                       f'tombstone fields, its row is blank')
                    fields = BLANK_TOMBSTONE
                rows.append((_offset_ts(fields['when']) or None, fields['process'], fields['cmdline'], fields['thread'],
                             str(fields['pid']), str(fields['tid']), str(fields['uid']), fields['signal'], fields['abort'],
                             fields['uptime'], fields['build'], 'protobuf' if is_proto else 'text', info.file_size, name,
                             label))
    return headers, rows, _source_path(context, reports)


# ---------------------------------------------------------------------------------------------
# Dropbox
# ---------------------------------------------------------------------------------------------
@artifact_processor
def bugreport_dropbox_entries(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Tag', 'Content', 'Size (bytes)', 'Process', 'PID', 'UID',
               'Packages', 'Foreground', 'Subject', 'First Body Line', 'Preview', 'Source Section', 'Source Line',
               'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _log_zone(label, report)
        _log_service_cuts(label, report, ('dropbox',))
        store = logscrash.tables(report)
        listed = [(contents, maximum) for _section, contents, maximum in store.dropbox_totals if contents]
        if listed:
            dumpstate_reader.say_once(logfunc, f'Bug report {label}: the dropbox prints "{listed[0][0]}"'
                                               f'{"; " + listed[0][1] if listed[0][1] else ""}')
        for item in store.dropbox_entries:
            rows.append((logscrash.stamp_utc(report, item[1])[0], item[1], item[2], item[3], item[4], item[5], item[6],
                         item[7], item[8], item[9], item[10], item[11], item[12], item[0], item[13], label))
    return headers, rows, _source_path(context, reports)


# ---------------------------------------------------------------------------------------------
# Reset reasons
# ---------------------------------------------------------------------------------------------
NOTE_NO_OFFSET = 'printed without an offset, converted with the report time zone'


@artifact_processor
def bugreport_reset_reasons(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Time Note', 'Form', 'Event', 'Flag', 'Detail',
               'Caller Frames', 'Source Section', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        for item in logscrash.tables(report).reset_events:
            wall = logscrash.record_time_text(item[1]) if item[2] == 'record' else item[1]
            moment, note = logscrash.stamp_utc(report, wall)
            has_offset = item[2] != 'record' and wall[-5:-4] in ('+', '-') and wall[-4:].isdigit()
            if not has_offset and not note:
                note = NOTE_NO_OFFSET
            elif not has_offset and note:
                note = NOTE_NO_OFFSET + '; ' + note
            rows.append((moment, item[1], note, item[2], item[3], item[4], item[5], item[6], item[0], item[7], label))
    return headers, rows, _source_path(context, reports)


# ---------------------------------------------------------------------------------------------
# Vendor services
# ---------------------------------------------------------------------------------------------
@artifact_processor
def bugreport_vendor_services(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Time Note', 'Service', 'Text', 'Indent', 'Source Line',
               'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        _log_zone(label, report)
        _log_service_cuts(label, report, logscrash.VENDOR_SERVICES)
        for service, count in sorted(logscrash.tables(report).vendor_blobs.items()):
            dumpstate_reader.say_once(logfunc, f'Bug report {label}: {count} encoded blob lines of {service} are not rows')
        for item in logscrash.tables(report).vendor_lines:
            wall, note = logscrash.vendor_time_to_wall(item[2])
            moment = None
            if note == logscrash.NOTE_NO_YEAR:
                moment = logscrash.logcat_utc(report, item[2])
                note = 'printed without a year, the year is taken from the report time' if moment else note
            elif wall:
                moment, stamp_note = logscrash.stamp_utc(report, wall)
                note = stamp_note or note
            rows.append((moment, item[2], note, item[0], item[3], item[1], item[4], label))
    return headers, rows, _source_path(context, reports)
