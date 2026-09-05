__artifacts_v2__ = {
    "dropbox_boot_records": {
        "name": "Android Dropbox - Boot and Restart Records",
        "description": "Boot and system restart records the platform's BootReceiver wrote to the system dropbox, "
                       "with the time each record was written and the build, hardware, bootloader, radio and "
                       "kernel strings it carried.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Android System Logs",
        "notes": "Read from the entry files under the platform's system dropbox folder. Each "
                 "entry is one file named <tag>@<time>.<ext>, where the time is Unix milliseconds "
                 "and the extension records the content flags (txt for text, dat for binary, a "
                 ".gz suffix when compressed, lost when the content was deleted to save space). "
                 "Reference: Android Open Source Project, DropBoxManagerService.java and "
                 "DropBoxManager.java, frameworks/base. This artifact reports the SYSTEM_* tags "
                 "BootReceiver writes: SYSTEM_BOOT once per boot when the ro.runtime.firstboot "
                 "property is unset, SYSTEM_RESTART when the system server restarted without a "
                 "reboot, and the SYSTEM_LAST_KMSG, SYSTEM_RECOVERY_LOG, SYSTEM_RECOVERY_KMSG, "
                 "SYSTEM_AUDIT and SYSTEM_FSCK captures taken at the same moment. Reference: "
                 "Android Open Source Project, BootReceiver.java, "
                 "frameworks/base/services/core/java/com/android/server, logBootEvents. Timestamp "
                 "is the entry time from the file name, which is when BootReceiver ran shortly "
                 "after boot; a SYSTEM_BOOT row is therefore a device boot at about that time. "
                 "The header lines Build, Hardware, Revision, Bootloader, Radio and Kernel come "
                 "from the same class; when Headers From Previous Boot is True they describe the "
                 "build that was running before this boot, which is how the platform writes them "
                 "(getBootHeadersToLogAndUpdate); one of the 21 tested images with boot rows "
                 "(Android 10) carried two Build values across its rows and the rest one, so a "
                 "Build that differs between neighbouring rows is a change of build between those "
                 "boots. Last Boot Reason is the footer BootReceiver appends to a last-kmsg "
                 "capture from the ro.boot.bootreason property, as stored, and is blank on the "
                 "other tags. Truncated is True when the platform's [[TRUNCATED]] marker is in "
                 "the body. The dropbox keeps a bounded number of entries and trims old ones, so "
                 "this is a recent window rather than a full boot history. Vendors append their "
                 "own suffixes to some tags, as in SYSTEM_LAST_KMSG_<n>_<date>_<time>_<code> on "
                 "eight tested Samsung images; Tag is reported as stored. A .lost entry keeps "
                 "only its tag and time, so its header columns are blank; one tested image held "
                 "only .lost boot entries.",
        "paths": ('*/system/dropbox/*',),
        "output_types": "standard",
        "artifact_icon": "power",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 6 rows",
            "anne_a15": "Android 15 | 4 rows",
            "cookbook_a11": "Android 11 | 6 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 1 row",
            "emu_a15_oss_v2": "Android 15 | 1 row",
            "emu_a15_oss_v3": "Android 15 | 1 row",
            "emu_a15_oss_v4": "Android 15 | 1 row",
            "emu_a15_oss_v5": "Android 15 | 1 row",
            "emu_a15_oss_v6": "Android 15 | 1 row",
            "emu_a15_oss_v7": "Android 15 | 0 rows",
            "emu_a15_oss_v8": "Android 15 | 0 rows",
            "emu_a15_oss_v9": "Android 15 | 0 rows",
            "falken_a326u_a13": "Android 13 | 3 rows",
            "galaxys10_a10": "Android 10 | 34 rows",
            "hc_pixel8pro_a16": "Android 16 | 2 rows",
            "hc_pixel8pro_a17": "Android 17 | 1 row",
            "hc_pixel8pro_a17_ail": "0 rows",
            "kevin_pocox7_a15": "Android 15 | 3 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 0 rows",
            "pixel7a_a14": "Android 14 | 7 rows",
            "russell_a14": "Android 14 | 1 row",
            "russell_pixel6a_a13": "Android 13 | 4 rows",
            "s20fe_a13": "Android 13 | 29 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 30 rows",
            "sharon_a13": "Android 13 | 0 rows",
            "sharon_a14": "Android 14 | 14 rows",
            "userb2_a13": "Android 13 | 1 row",
        },
    },
    "dropbox_process_errors": {
        "name": "Android Dropbox - App Crashes, ANRs and Errors",
        "description": "Application crash, not-responding, wtf, strict-mode and native-crash records the platform "
                       "wrote to the system dropbox, with the time of each, the process and package involved, "
                       "whether it was in the foreground, and the first line of the report.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Android System Logs",
        "notes": "Read from the system dropbox entry files whose tag is <class>_<event>, where "
                 "the class is system_server, system_app or data_app and the event is crash, anr, "
                 "wtf, strictmode, native_crash or lowmem, plus the SYSTEM_TOMBSTONE and "
                 "SYSTEM_TOMBSTONE_PROTO tags BootReceiver writes for native crashes. The tag and "
                 "its header lines are written by ActivityManagerService.addErrorToDropBox and "
                 "appendDropBoxProcessHeaders: Process, PID, UID, Frozen, Flags, Package "
                 "(repeated, as <package> v<version code> (<version name>)), Foreground, "
                 "Process-Runtime, Activity, Parent-Process, Subject, ErrorId, Build, "
                 "Crash-Handler and, from the rate limiter, Dropped-Count. Reference: Android "
                 "Open Source Project, ActivityManagerService.java and DropboxRateLimiter.java, "
                 "frameworks/base/services/core/java/com/android/server/am. Timestamp is the "
                 "entry time from the file name in Unix milliseconds. Packages lists every "
                 "Package header as stored. Foreground is the platform's own Yes or No, written "
                 "from its isInterestingToUser flag. First Body Line is the first line after the "
                 "header block, which for a crash or wtf is the exception class and message as "
                 "the platform wrote it. Dropped Count is the number of entries the rate limiter "
                 "had dropped for that process when this one was written, as stored. Parent "
                 "Process, Process Runtime (ms), Error ID, Frozen and Activity are blank where "
                 "the entry carries no such header. Activity and Parent Process were blank on "
                 "every entry of the 26 tested images that held entries, the anr entries "
                 "included, and no entry file carried either header; Frozen, Process Runtime and "
                 "Error ID were present on 13, 15 and 9 of those images. A .lost entry keeps only "
                 "its tag and time; one tested image held only .lost entries. For the tombstone "
                 "tags the body is a native crash report: Process is the process named between "
                 ">>> and <<<, Signal is the signal line as stored, and Abort Message is the "
                 "abort message as stored. The protobuf entries are decoded with the vendored "
                 "blackboxprotobuf: SYSTEM_TOMBSTONE_PROTO, which Android 12 and 13 filed as the "
                 "bare Tombstone message (BootReceiver.addTombstoneToDropBox at "
                 "android-13.0.0_r1), and SYSTEM_TOMBSTONE_PROTO_WITH_HEADERS, which Android 14 "
                 "and later file wrapped in TombstoneWithHeadersProto (tombstone 1, dropped_count "
                 "2). The Tombstone field numbers are build_fingerprint 2, timestamp 4, pid 5, "
                 "tid 6, uid 7, command_line 9, signal_info 10 with number 1, name 2, code 3 and "
                 "code_name 4, and abort_message 14. Reference: Android Open Source Project, "
                 "core/proto/android/os/tombstone.proto in frameworks/base and "
                 "debuggerd/proto/tombstone.proto in system/core. Both forms decoded on every "
                 "live protobuf entry of the tested images (26 bare, 25 with headers). Reported "
                 "At is the Timestamp header the platform adds to a crash entry, written with the "
                 "pattern yyyy-MM-dd HH:mm:ss.SSSZ so it carries the device's UTC offset, and "
                 "rendered here in UTC; Timestamp from the file name is the moment the entry was "
                 "filed. For the tombstone tags Reported At is the crash time from the report "
                 "itself and BootReceiver files the entry afterwards: 12 of the 104 live "
                 "tombstone entries on the tested images were filed more than a minute after the "
                 "crash, 10 of them more than an hour. On five of the 13 tested images holding "
                 "tombstone entries, every one was a /system/bin/sh or ueventd crash dated on the "
                 "day of the newest dropbox entry, so an entry timed inside the acquisition "
                 "window should be weighed against the acquisition itself. A row records that the "
                 "platform logged the event; the dropbox keeps a bounded number of entries and "
                 "trims old ones, and the rate limiter drops repeats, so it is a recent, thinned "
                 "window rather than a full history.",
        "paths": ('*/system/dropbox/*',),
        "output_types": "standard",
        "artifact_icon": "alert-triangle",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 16 rows",
            "anne_a15": "Android 15 | 6 rows",
            "cookbook_a11": "Android 11 | 269 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 78 rows",
            "emu_a15_oss_v2": "Android 15 | 79 rows",
            "emu_a15_oss_v3": "Android 15 | 82 rows",
            "emu_a15_oss_v4": "Android 15 | 86 rows",
            "emu_a15_oss_v5": "Android 15 | 86 rows",
            "emu_a15_oss_v6": "Android 15 | 87 rows",
            "emu_a15_oss_v7": "Android 15 | 2 rows",
            "emu_a15_oss_v8": "Android 15 | 1 row",
            "emu_a15_oss_v9": "Android 15 | 1 row",
            "falken_a326u_a13": "Android 13 | 12 rows",
            "galaxys10_a10": "Android 10 | 237 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 4 rows",
            "hc_pixel8pro_a17_ail": "0 rows",
            "kevin_pocox7_a15": "Android 15 | 8 rows",
            "pixel3_a11": "Android 11 | 884 rows",
            "pixel3_a12": "Android 12 | 90 rows",
            "pixel7a_a14": "Android 14 | 210 rows",
            "russell_a14": "Android 14 | 12 rows",
            "russell_pixel6a_a13": "Android 13 | 344 rows",
            "s20fe_a13": "Android 13 | 146 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 120 rows",
            "sharon_a13": "Android 13 | 244 rows",
            "sharon_a14": "Android 14 | 18 rows",
            "userb2_a13": "Android 13 | 14 rows",
        },
    },
    "dropbox_other_entries": {
        "name": "Android Dropbox - Other Entries",
        "description": "The remaining entries in the system dropbox, with the time it was "
                       "written, its tag, its content flags, its size and its first line as "
                       "stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Android System Logs",
        "notes": "Read from the system dropbox entry files not reported by the boot or "
                 "process-error artifacts. Any system service or app holding the permission can "
                 "add an entry under a tag of its own, so the tags here vary by device: on the 16 "
                 "tested images that held any, they were storage_trim (13 images), "
                 "platform_stats_bookmark (5), event_log (4) and event_data (3) markers, dumpsys "
                 "captures such as dumpsys:account (2 images, the account types registered per "
                 "Android user), and on Samsung images ams_boot_progress_log_unlocked (6) and "
                 "tags named after Samsung packages such as com.samsung.android.app.reminder (9) "
                 "and com.sec.android.app.clockpackage (4). Tag is reported as stored, with the "
                 "colon in a dumpsys tag stored as %3A in the file name. Content Type and "
                 "Compressed come from the file extension, which encodes the platform's content "
                 "flags; Content Lost is True for a .lost entry, whose content the platform "
                 "deleted to save space and which has no body. First Line is the first non-empty "
                 "line of a text entry, as stored and cut at 200 characters; a binary entry "
                 "reports none. This is an inventory of what the platform logged and when, not a "
                 "decoding of each tag.",
        "paths": ('*/system/dropbox/*',),
        "output_types": "standard",
        "artifact_icon": "archive",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 10 rows",
            "anne_a15": "Android 15 | 12 rows",
            "cookbook_a11": "Android 11 | 32 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 0 rows",
            "emu_a15_oss_v2": "Android 15 | 0 rows",
            "emu_a15_oss_v3": "Android 15 | 0 rows",
            "emu_a15_oss_v4": "Android 15 | 0 rows",
            "emu_a15_oss_v5": "Android 15 | 0 rows",
            "emu_a15_oss_v6": "Android 15 | 0 rows",
            "emu_a15_oss_v7": "Android 15 | 0 rows",
            "emu_a15_oss_v8": "Android 15 | 0 rows",
            "emu_a15_oss_v9": "Android 15 | 0 rows",
            "falken_a326u_a13": "Android 13 | 8 rows",
            "galaxys10_a10": "Android 10 | 605 rows",
            "hc_pixel8pro_a16": "Android 16 | 3 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "hc_pixel8pro_a17_ail": "0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "pixel3_a11": "Android 11 | 116 rows",
            "pixel3_a12": "Android 12 | 259 rows",
            "pixel7a_a14": "Android 14 | 2 rows",
            "russell_a14": "Android 14 | 5 rows",
            "russell_pixel6a_a13": "Android 13 | 126 rows",
            "s20fe_a13": "Android 13 | 53 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 65 rows",
            "sharon_a13": "Android 13 | 143 rows",
            "sharon_a14": "Android 14 | 24 rows",
            "userb2_a13": "Android 13 | 2 rows",
        },
    },
    "android_tombstones": {
        "name": "Android Tombstones",
        "description": "Native crash reports the platform kept in its tombstones folder, with the time of the "
                       "crash, the process, its command line, the signal and the abort message.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Android System Logs",
        "notes": "Read from the tombstone_<n> text files and their tombstone_<n>.pb protobuf "
                 "twins under the platform's tombstones folder. The text form is the report "
                 "debuggerd writes: Build fingerprint, Timestamp, Cmdline and Process uptime "
                 "(both absent from the two Android 11 images, so Command Line and Process Uptime "
                 "are blank there and Process comes from the name line alone), the pid/tid/name "
                 "line naming the crashing process between >>> and <<<, uid, the signal line and "
                 "Abort message. The protobuf form is the Tombstone message, decoded with the "
                 "vendored blackboxprotobuf using its field numbers: build_fingerprint 2, "
                 "timestamp 4, pid 5, tid 6, uid 7, command_line 9, process_uptime 20, "
                 "signal_info 10 (number 1, name 2, code 3, code_name 4) and abort_message 14. "
                 "Reference: Android Open Source Project, debuggerd/proto/tombstone.proto in "
                 "system/core. Timestamp is the report's own timestamp, which carries a UTC "
                 "offset, rendered in UTC; Format says which form the row came from, and a crash "
                 "present in both forms appears twice. Process Uptime is the Process uptime line "
                 "in the text form and the process_uptime field in the protobuf form; proto3 "
                 "leaves a zero off the wire and debuggerd's own text converter prints the field "
                 "regardless (Reference: Android Open Source Project, "
                 "debuggerd/libdebuggerd/tombstone_proto_to_text.cpp in system/core), so an "
                 "absent field is rendered 0s, which is what the text twin of every such record "
                 "read on the tested images. The platform keeps a rotating set of tombstones, so "
                 "this is the most recent native crashes rather than a history. On five of the 24 "
                 "tested images with tombstones, every tombstone in the set was a /system/bin/sh "
                 "or ueventd crash dated on the day of the newest dropbox entry, so a tombstone "
                 "whose time falls in the acquisition window should be weighed against the "
                 "acquisition itself before it is read as activity on the device; the other "
                 "images held daemon and application crashes spread over up to 22 days. Signal "
                 "and Abort Message are reported as stored. Command Line is the command line with "
                 "its arguments as stored, so one process can appear under several (12 command "
                 "lines against 5 processes on one tested image); Process is the name between >>> "
                 "and <<< in the text form and the first token of the command line in the "
                 "protobuf form.",
        "paths": ('*/tombstones/tombstone_*',),
        "output_types": "standard",
        "artifact_icon": "cpu",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 2 rows",
            "anne_a15": "Android 15 | 2 rows",
            "cookbook_a11": "Android 11 | 2 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 2 rows",
            "emu_a15_oss_v2": "Android 15 | 2 rows",
            "emu_a15_oss_v3": "Android 15 | 2 rows",
            "emu_a15_oss_v4": "Android 15 | 2 rows",
            "emu_a15_oss_v5": "Android 15 | 2 rows",
            "emu_a15_oss_v6": "Android 15 | 2 rows",
            "emu_a15_oss_v7": "Android 15 | 2 rows",
            "emu_a15_oss_v8": "Android 15 | 2 rows",
            "emu_a15_oss_v9": "Android 15 | 2 rows",
            "falken_a326u_a13": "Android 13 | 2 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 2 rows",
            "hc_pixel8pro_a17": "Android 17 | 2 rows",
            "hc_pixel8pro_a17_ail": "0 rows",
            "kevin_pocox7_a15": "Android 15 | 3 rows",
            "pixel3_a11": "Android 11 | 3 rows",
            "pixel3_a12": "Android 12 | 16 rows",
            "pixel7a_a14": "Android 14 | 64 rows",
            "russell_a14": "Android 14 | 64 rows",
            "russell_pixel6a_a13": "Android 13 | 8 rows",
            "s20fe_a13": "Android 13 | 50 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 34 rows",
            "sharon_a14": "Android 14 | 64 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
    },
    "android_anr_traces": {
        "name": "Android ANR Traces",
        "description": "Application-not-responding trace files the platform kept in its anr folder, with the "
                       "time as stored, the subject line and the process each was taken for.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Android System Logs",
        "notes": "Read from the anr_<date>-<time>-<ms> and trace_<n> files under the platform's "
                 "anr folder. A newer file opens with a Subject line naming what timed out and "
                 "then the process dumps, each headed ----- pid <n> at <time> ----- and a Cmd "
                 "line; the debuggerd client writes a ----- Waiting Channels: pid <n> at <time> "
                 "----- block beside the dump it requests, holding each thread's kernel wait "
                 "channel (Reference: Android Open Source Project, "
                 "debuggerd/client/debuggerd_client.cpp in system/core, get_wchan_data), present "
                 "in 88 of the 95 tested files; an older trace_<n> file holds the dumps only. "
                 "Time is reported as stored, from the file name where it carries one and "
                 "otherwise from the first dump header, because neither form records a zone; the "
                 "matching system_app_anr or data_app_anr dropbox entry, when present, carries "
                 "the Unix time. Process and PID are the Cmd line and pid of the first dump, "
                 "which the platform writes for the not-responding process itself, ahead of its "
                 "parent and system_server (Reference: Android Open Source Project, "
                 "ProcessErrorStateRecord.java, "
                 "frameworks/base/services/core/java/com/android/server/am, appNotResponding); "
                 "the Subject line named that process on 71 of the 87 tested files carrying both. "
                 "A vendor variant seen on a Xiaomi image opens with ProcessName and Pid lines, "
                 "read when the file carries no Cmd line. Processes Dumped is the number of "
                 "distinct pids with a dump header, up to 34 on the tested files; two of the 95 "
                 "tested files held a Subject and no dump at all. Build Fingerprint is blank "
                 "where the file carries no Build fingerprint line, as on 45 of the 95 tested "
                 "files across five images.",
        "paths": ('*/anr/anr_*', '*/anr/trace*'),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 2 rows",
            "anne_a15": "Android 15 | 0 rows",
            "cookbook_a11": "Android 11 | 1 row",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 0 rows",
            "emu_a15_oss_v2": "Android 15 | 1 row",
            "emu_a15_oss_v3": "Android 15 | 1 row",
            "emu_a15_oss_v4": "Android 15 | 1 row",
            "emu_a15_oss_v5": "Android 15 | 1 row",
            "emu_a15_oss_v6": "Android 15 | 1 row",
            "emu_a15_oss_v7": "Android 15 | 1 row",
            "emu_a15_oss_v8": "Android 15 | 1 row",
            "emu_a15_oss_v9": "Android 15 | 1 row",
            "falken_a326u_a13": "Android 13 | 1 row",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 2 rows",
            "hc_pixel8pro_a17": "Android 17 | 2 rows",
            "hc_pixel8pro_a17_ail": "0 rows",
            "kevin_pocox7_a15": "Android 15 | 7 rows",
            "pixel3_a11": "Android 11 | 1 row",
            "pixel3_a12": "Android 12 | 1 row",
            "pixel7a_a14": "Android 14 | 55 rows",
            "russell_a14": "Android 14 | 7 rows",
            "russell_pixel6a_a13": "Android 13 | 1 row",
            "s20fe_a13": "Android 13 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 2 rows",
            "sharon_a14": "Android 14 | 5 rows",
            "userb2_a13": "Android 13 | 0 rows",
        },
    },
}

import gzip
import os
import re
from datetime import datetime, timedelta, timezone

from scripts import blackboxprotobuf
from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, logfunc

_ENTRY = re.compile(r'^(?P<tag>.+?)@(?P<ts>\d{10,13})\.(?P<ext>txt|dat|lost)(?P<gz>\.gz)?$')
_PROCESS_TAG = re.compile(r'^(system_server|system_app|data_app)_(crash|anr|wtf|strictmode|native_crash|lowmem)$')
_TOMBSTONE_TAGS = ('SYSTEM_TOMBSTONE', 'SYSTEM_TOMBSTONE_PROTO', 'SYSTEM_TOMBSTONE_PROTO_WITH_HEADERS')
_HEADER = re.compile(r'^([A-Za-z][A-Za-z0-9-]*): ?(.*)$')
_OFFSET_TS = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})(\.\d+)?\s*([+-]\d{4})$')
_TOMB_PID = re.compile(r'^pid: (\d+),(?: ppid: \d+,)? tid: (\d+), name: (.*?)  >>> (.*?) <<<\s*$', re.M)
# '----- pid N at <time> -----' heads a thread dump; '----- Waiting Channels: pid N at <time> -----'
# heads the per-thread wait-channel block the debuggerd client writes beside the dump it requests
# (system/core debuggerd/client/debuggerd_client.cpp, get_wchan_data), so one process can own both
_ANR_DUMP = re.compile(r'^----- (?:[A-Za-z ]+: )?pid (\d+) at (.+?) -----$', re.M)
_ANR_NAME = re.compile(r'^anr_(\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})-(\d{3})$')
_READ_CAP = 512 * 1024
_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def _ms(value):
    try:
        return _EPOCH + timedelta(milliseconds=int(value))
    except (TypeError, ValueError, OverflowError):
        return ''


def _offset_ts(text):
    """A 'YYYY-MM-DD HH:MM:SS[.frac]-0400' report timestamp as an aware UTC datetime, else ''."""
    m = _OFFSET_TS.match(str(text or '').strip())
    if not m:
        return ''
    micros = (m.group(2) or '.0')[1:7].ljust(6, '0')
    try:
        stamp = datetime.strptime(f'{m.group(1)}.{micros}{m.group(3)}', '%Y-%m-%d %H:%M:%S.%f%z')
    except ValueError:
        return ''
    return stamp.astimezone(timezone.utc)


def _read(path, cap=_READ_CAP):
    """The entry bytes, decompressed when the name says gzip; b'' and a log line when unreadable.

    Dropbox text entries are cut at ``cap`` because only their headers are read. Tombstone
    protobufs and ANR traces are read whole (cap None): a truncated message does not decode, and
    the trace's dump headers run the length of the file.
    """
    try:
        with open(path, 'rb') as handle:
            data = handle.read() if cap is None else handle.read(cap + 1)
    except OSError as error:
        logfunc(f'Android Dropbox: could not read {os.path.basename(path)}: {error}')
        return b''
    if path.lower().endswith('.gz'):
        try:
            data = gzip.decompress(data)
        except (OSError, EOFError) as error:
            logfunc(f'Android Dropbox: {os.path.basename(path)} did not decompress: {error}')
            return b''
    return data if cap is None else data[:cap]


def _text(data):
    return data.decode('utf-8', errors='replace')


def _split_headers(text):
    """The leading 'Key: value' block as a dict (repeated keys become lists) and the body after it."""
    headers = {}
    lines = text.split('\n')
    index = 0
    for index, line in enumerate(lines):
        m = _HEADER.match(line)
        if not m:
            break
        key, value = m.group(1), m.group(2)
        if key in headers:
            if not isinstance(headers[key], list):
                headers[key] = [headers[key]]
            headers[key].append(value)
        else:
            headers[key] = value
    body = '\n'.join(lines[index:]).lstrip('\n')
    return headers, body


def _first_line(text, limit=200):
    for line in text.split('\n'):
        if line.strip():
            return line.strip()[:limit]
    return ''


def _joined(value):
    if isinstance(value, list):
        return ', '.join(str(v) for v in value)
    return value if value is not None else ''


def _entries(context, want):
    """Dropbox entry files as (path, tag, timestamp, ext, gzipped), for tags `want` accepts."""
    out = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found) or os.path.basename(os.path.dirname(file_found)) != 'dropbox':
            continue
        m = _ENTRY.match(os.path.basename(file_found))
        if not m:
            continue
        tag = m.group('tag')
        if not want(tag):
            continue
        out.append((file_found, tag, _ms(m.group('ts')), m.group('ext'), bool(m.group('gz'))))
    return out


def _is_boot_tag(tag):
    return tag.startswith('SYSTEM_') and not tag.startswith('SYSTEM_TOMBSTONE')


def _is_process_tag(tag):
    return bool(_PROCESS_TAG.match(tag)) or tag in _TOMBSTONE_TAGS


def _tombstone_text_fields(text):
    """Fields of a debuggerd text tombstone: process, cmdline, pid, tid, uid, signal, abort, uptime, build, when."""
    headers = {}
    for key in ('Build fingerprint', 'Timestamp', 'Cmdline', 'uid', 'Process uptime', 'Abort message'):
        m = re.search(rf'^{re.escape(key)}: ?(.*)$', text, re.M)
        headers[key] = m.group(1).strip() if m else ''
    m = _TOMB_PID.search(text)
    sig = re.search(r'^signal .*$', text, re.M)
    return {
        'process': m.group(4).strip() if m else '',
        'thread': m.group(3).strip() if m else '',
        'cmdline': headers['Cmdline'],
        'pid': m.group(1) if m else '',
        'tid': m.group(2) if m else '',
        'uid': headers['uid'],
        'signal': sig.group(0).strip() if sig else '',
        'abort': headers['Abort message'].strip("'"),
        'uptime': headers['Process uptime'],
        'build': headers['Build fingerprint'].strip("'"),
        'when': headers['Timestamp'],
    }


def _pb(value):
    if isinstance(value, (bytes, bytearray)):
        return value.decode('utf-8', errors='replace').rstrip('\x00')
    if value is None:
        return ''
    return value


def _fields_from_message(message):
    """Row fields from a decoded Tombstone message (a blackboxprotobuf dict keyed by field number)."""
    signal = message.get('10') if isinstance(message.get('10'), dict) else {}
    cmd = message.get('9')
    cmdline = ' '.join(_pb(c) for c in cmd) if isinstance(cmd, list) else _pb(cmd)
    sig = ''
    if signal:
        sig = f"signal {_pb(signal.get('1'))} ({_pb(signal.get('2'))}), code {_pb(signal.get('3'))} ({_pb(signal.get('4'))})"
    # proto3 leaves a zero scalar off the wire, and debuggerd's own text rendering prints the field
    # unconditionally as 'Process uptime: %ds' (libdebuggerd/tombstone_proto_to_text.cpp), so an
    # absent field 20 is 0s; the text twin of every such record on the tested images read 0s
    uptime = message.get('20')
    return {
        'process': cmdline.split(' ')[0] if cmdline else '',
        'thread': '',
        'cmdline': cmdline,
        'pid': _pb(message.get('5')),
        'tid': _pb(message.get('6')),
        'uid': _pb(message.get('7')),
        'signal': sig,
        'abort': _pb(message.get('14')),
        'uptime': f"{_pb(uptime) if uptime is not None else 0}s",
        'build': _pb(message.get('2')),
        'when': _pb(message.get('4')),
    }


def _tombstone_proto_fields(data):
    """Fields of a debuggerd Tombstone message; field numbers from system/core debuggerd/proto/tombstone.proto."""
    try:
        message, _types = blackboxprotobuf.decode_message(data)
    except Exception as error:  # pylint: disable=broad-exception-caught
        logfunc(f'Android Dropbox: a tombstone protobuf did not decode: {error}')
        return None
    return _fields_from_message(message)


def _unwrap_with_headers(data):
    """TombstoneWithHeadersProto: tombstone bytes at 1, dropped_count at 2."""
    try:
        message, _types = blackboxprotobuf.decode_message(data)
    except Exception as error:  # pylint: disable=broad-exception-caught
        logfunc(f'Android Dropbox: a tombstone-with-headers protobuf did not decode: {error}')
        return None, ''
    inner = message.get('1')
    if not isinstance(inner, (bytes, bytearray)):
        # blackboxprotobuf may already have decoded the nested message
        return (inner if isinstance(inner, dict) else None), _pb(message.get('2'))
    return inner, _pb(message.get('2'))


def _proto_fields_from_any(inner):
    """Fields from the unwrapped tombstone, whether blackboxprotobuf left it as bytes or decoded it."""
    return _fields_from_message(inner) if isinstance(inner, dict) else _tombstone_proto_fields(inner)


@artifact_processor
def dropbox_boot_records(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Tag',
        'Headers From Previous Boot',
        'Build',
        'Hardware',
        'Bootloader',
        'Radio',
        'Kernel',
        'Last Boot Reason',
        'Truncated',
        'Size Bytes',
        'Source File',
    )
    data_list = []
    sources = []
    for path, tag, stamp, ext, _gz in _entries(context, _is_boot_tag):
        text = _text(_read(path)) if ext != 'lost' else ''
        headers, _body = _split_headers(text)
        reason = re.search(r'^Last boot reason: (.*)$', text, re.M)
        data_list.append((
            stamp,
            tag,
            headers.get('isPrevious', ''),
            headers.get('Build', ''),
            headers.get('Hardware', ''),
            headers.get('Bootloader', ''),
            headers.get('Radio', ''),
            headers.get('Kernel', ''),
            reason.group(1).strip() if reason else '',
            '[[TRUNCATED]]' in text,
            os.path.getsize(path),
            context.get_relative_path(path),
        ))
        sources.append(path)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def dropbox_process_errors(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Tag',
        'Process',
        'PID',
        'UID',
        'Packages',
        'Foreground',
        'Subject',
        'Activity',
        'Parent Process',
        'First Body Line',
        'Signal',
        'Abort Message',
        ('Reported At', 'datetime'),
        'Frozen',
        'Process Runtime (ms)',
        'Error ID',
        'Dropped Count',
        'Build',
        'Size Bytes',
        'Source File',
    )
    data_list = []
    sources = []
    for path, tag, stamp, ext, _gz in _entries(context, _is_process_tag):
        data = (_read(path, cap=None) if ext == 'dat' else _read(path)) if ext != 'lost' else b''
        row = {'process': '', 'pid': '', 'uid': '', 'packages': '', 'foreground': '', 'subject': '', 'activity': '',
               'parent': '', 'first': '', 'signal': '', 'abort': '', 'reported': '', 'frozen': '', 'runtime': '',
               'error_id': '', 'dropped': '', 'build': ''}
        if tag in _TOMBSTONE_TAGS and ext == 'dat':
            if tag == 'SYSTEM_TOMBSTONE_PROTO_WITH_HEADERS':
                # Android 14 and later wrap the tombstone in TombstoneWithHeadersProto
                # (BootReceiver.addTombstoneToDropBox at main)
                inner, dropped = _unwrap_with_headers(data)
                fields = _proto_fields_from_any(inner) if inner is not None else None
            else:
                # Android 12 and 13 filed the bare Tombstone message under SYSTEM_TOMBSTONE_PROTO
                # (BootReceiver.addTombstoneToDropBox at android-13.0.0_r1)
                dropped = ''
                fields = _tombstone_proto_fields(data)
            if fields:
                row.update(process=fields['process'], pid=fields['pid'], uid=fields['uid'], signal=fields['signal'],
                           abort=fields['abort'], reported=fields['when'], build=fields['build'], dropped=dropped)
        elif data:
            text = _text(data)
            headers, body = _split_headers(text)
            row.update(
                process=headers.get('Process', ''), pid=headers.get('PID', ''), uid=headers.get('UID', ''),
                packages=_joined(headers.get('Package', '')), foreground=headers.get('Foreground', ''),
                subject=headers.get('Subject', ''), activity=headers.get('Activity', ''),
                parent=headers.get('Parent-Process', ''), reported=headers.get('Timestamp', ''),
                frozen=headers.get('Frozen', ''), runtime=headers.get('Process-Runtime', ''),
                error_id=headers.get('ErrorId', ''), dropped=headers.get('Dropped-Count', ''),
                build=headers.get('Build', ''), first=_first_line(body))
            if tag in _TOMBSTONE_TAGS:
                fields = _tombstone_text_fields(text)
                row.update(process=fields['process'] or row['process'], pid=fields['pid'] or row['pid'],
                           uid=fields['uid'] or row['uid'], signal=fields['signal'], abort=fields['abort'],
                           reported=fields['when'] or row['reported'], build=fields['build'] or row['build'],
                           first='')
        data_list.append((
            stamp, tag, row['process'], row['pid'], row['uid'], row['packages'], row['foreground'], row['subject'],
            row['activity'], row['parent'], row['first'], row['signal'], row['abort'], _offset_ts(row['reported']),
            row['frozen'], row['runtime'], row['error_id'], row['dropped'], row['build'],
            os.path.getsize(path), context.get_relative_path(path),
        ))
        sources.append(path)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def dropbox_other_entries(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Tag',
        'Content Type',
        'Compressed',
        'Content Lost',
        'Size Bytes',
        'First Line',
        'Source File',
    )
    data_list = []
    sources = []
    for path, tag, stamp, ext, gz in _entries(context, lambda t: not _is_boot_tag(t) and not _is_process_tag(t)):
        first = ''
        if ext == 'txt':
            first = _first_line(_text(_read(path)))
        data_list.append((
            stamp,
            tag,
            {'txt': 'text', 'dat': 'data', 'lost': ''}[ext],
            gz,
            ext == 'lost',
            os.path.getsize(path),
            first,
            context.get_relative_path(path),
        ))
        sources.append(path)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def android_tombstones(context):
    data_headers = (
        ('Timestamp', 'datetime'),
        'Process',
        'Command Line',
        'Thread',
        'PID',
        'TID',
        'UID',
        'Signal',
        'Abort Message',
        'Process Uptime',
        'Build Fingerprint',
        'Format',
        'Source File',
    )
    data_list = []
    sources = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        base = os.path.basename(file_found)
        if os.path.isdir(file_found) or os.path.basename(os.path.dirname(file_found)) != 'tombstones':
            continue
        if not re.match(r'^tombstone_\d+(\.pb)?$', base):
            continue
        data = _read(file_found, cap=None if base.endswith('.pb') else _READ_CAP)
        if not data:
            continue
        if base.endswith('.pb'):
            fields = _tombstone_proto_fields(data)
            fmt = 'protobuf'
        else:
            fields = _tombstone_text_fields(_text(data))
            fmt = 'text'
        if not fields:
            continue
        data_list.append((
            _offset_ts(fields['when']),
            fields['process'],
            fields['cmdline'],
            fields['thread'],
            fields['pid'],
            fields['tid'],
            fields['uid'],
            fields['signal'],
            fields['abort'],
            fields['uptime'],
            fields['build'],
            fmt,
            context.get_relative_path(file_found),
        ))
        sources.append(file_found)
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def android_anr_traces(context):
    data_headers = (
        'Time (as stored)',
        'Subject',
        'Process',
        'PID',
        'Processes Dumped',
        'Build Fingerprint',
        'Size Bytes',
        'Source File',
    )
    data_list = []
    sources = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        base = os.path.basename(file_found)
        if os.path.isdir(file_found) or os.path.basename(os.path.dirname(file_found)) != 'anr':
            continue
        if not (base.startswith('anr_') or base.startswith('trace')):
            continue
        text = _text(_read(file_found, cap=None))
        if not text:
            continue
        dumps = _ANR_DUMP.findall(text)
        m = _ANR_NAME.match(base)
        when = f'{m.group(1)}.{m.group(2)}' if m else (dumps[0][1] if dumps else '')
        subject = re.search(r'^Subject: ?(.*)$', text, re.M)
        # Cmd line heads each dump; a vendor variant seen on a Xiaomi image carries ProcessName instead
        cmd = re.search(r'^Cmd line: ?(.*)$', text, re.M) or re.search(r'^ProcessName\s*: ?(.*)$', text, re.M)
        pid_line = re.search(r'^Pid\s*: ?(\d+)', text, re.M)
        build = re.search(r"^Build fingerprint: ?'?(.*?)'?$", text, re.M)
        data_list.append((
            when,
            subject.group(1).strip() if subject else '',
            cmd.group(1).strip() if cmd else '',
            dumps[0][0] if dumps else (pid_line.group(1) if pid_line else ''),
            len({pid for pid, _ in dumps}),
            build.group(1).strip() if build else '',
            os.path.getsize(file_found),
            context.get_relative_path(file_found),
        ))
        sources.append(file_found)
    return data_headers, data_list, '\n'.join(sources)
