__artifacts_v2__ = {
    "bugreport_device_facts": {
        "name": "Bug Report - Device Facts",
        "description": "Build and security properties and header lines of an Android bug report text (dumpstate), "
                       "with the report time and the time zone used for the UTC values in the other bug report artifacts.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report",
        "notes": "One row per header line of the bug report text that is named here, the report time as printed, and each of 35 "
                 "properties of the SYSTEM PROPERTIES (getprop) section that are on a fixed list (build, product, security state, locale and time zone), as printed (control characters shown as a space, a value over several lines joined with spaces, values cut at 400 characters) and once each. Header lines read: Build, Build fingerprint, Bootloader, Radio, "
                 "Network, Module Metadata version, Android SDK version, SDK extensions, Kernel, Uptime, Bugreport format version "
                 "and Dumpstate info. Origin says where a row came from: header, getprop or derived. Two derived rows close each "
                 "report: Report time (UTC), the printed report time converted with the time zone in the property "
                 "persist.sys.timezone, and Time zone used for UTC values, which is that zone or the sentence 'none: the report records no usable time zone', printed both when the property is missing and when it names a zone this tool does not know (the log says which). The device clock is printed without a zone, so every UTC value in the "
                 "Android Bug Report artifacts rests on that property naming the zone the device clock used; where it is missing "
                 "the UTC columns are empty and the printed time is kept. A wall time that occurs twice when clocks go back is read "
                 "with the daylight-saving offset, and one that does not occur has no UTC value. Serial numbers, IMEIs and account or advertising identifiers can be printed in this text (for example in some properties and in the bootconfig lines); they are not on the list and are not reported. A property on the list that the report does not "
                 "print has no row, which says nothing about the device. Uptime is the text of the header line (up N weeks, days, hours, minutes, and the load average), as printed. Source Line is the line of the text. Source File is the file, or file.zip!/member for the "
                 "main text inside a zip; it held one value on all rows of each tested report, since each was read alone, and "
                 "holds one value per report when several are staged.\n"
                 "Files read: dumpstate.txt, bugreport-*.txt and bugreport-*.zip (the zip made by adb bugreport, or the one the Shell app keeps on the device, whose main text is the file main_entry.txt names), the Shell app's bugreport-*.tmp texts, and the Samsung dumpstate zips under a log folder (*dumpState*.zip, dumpstate_*.zip). A file is read only when the "
                 "banner '== dumpstate:' is in its first 8,192 bytes; any other file the patterns matched is left out and the log "
                 "says so. The text is read line by line and is not modified; up to six report texts are kept for the four artifacts of one run, so each is read once per run (with more than six staged, a text can be read again).\n"
                 "Evidence tiers. Data-proven on five real bug reports: a Samsung A-series phone (Android 16), a Samsung S-series "
                 "phone (Android 16), a Huawei phone (Android 10), a Motorola phone (Android 15) and a Transsion-brand phone "
                 "(Android 10). The rows of each (45 to 47, plus the two derived rows) equal a count made from the raw text with "
                 "plain regular expressions and the rows of an independent parser written for another tool. Constructed only: the Shell app's finished bugreport-*.zip found in a file system extraction (the corpus extractions hold Samsung log zips and partial .tmp texts instead, see below). A report with no time zone property was built on constructed text and is also seen in the two partial .tmp texts of userb2_a13. Not examined: Android 11 and 12, vendors other than the five named here and the Google build of userb2_a13 (header lines only), other locales, and header lines or properties that other builds print under other names, which "
                 "are not read. On the corpus, bug report texts sit in Samsung dumpstate zips under a log folder (a dumpState zip holding a full dumpstate.txt, and dumpstate_app_error, dumpstate_app_native and dumpstate_sys_error zips, automatically generated as their banner says, whose main_entry.txt names the text) and in the Shell app's partial .tmp texts under bugreports; these are read too, and only when the dumpstate banner is in the first 8,192 bytes of the text. The automatically generated dumps print a line '== automatically generated by' under the banner, and the header lines after it are read. On the corpus the error dumps and the partial texts hold no package service dump. A byte-identical copy of a file found at a second path (s20fe_a13 holds the dumpState zip under both data/log and data/media/0/log) is read once, and the run log names the copy left out.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "device-mobile",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two error dumpstate zips | 139 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 47 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 48 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 26 rows",
        },
    },
    "bugreport_sections": {
        "name": "Bug Report - Sections",
        "description": "The command and dumpsys service sections that an Android bug report text opens, with their line "
                       "ranges and the Android Bug Report artifacts that present each one.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report",
        "notes": "One row per section that the bug report text opens: a command section (a line like '------ TITLE (command) "
                 "------'), a dumpsys service section (a line 'DUMP OF SERVICE name:', priority words dropped), a dumpsys group (a "
                 "command that runs the dumpsys binary and holds service sections) and the header before the first section. Start Line "
                 "is the line of the section header, Last Line is the line before the next section header or the section's own "
                 "duration line, and Lines counts the lines between. Printed Duration (s) is the number in the duration line that "
                 "the platform prints when it finishes a section (a line like '------ 0.3s was the duration of 'TITLE' ------' or "
                 "'--------- 0.3s was the duration of dumpsys name, ending at: ...'); it is empty for a section that has none, "
                 "for example the last section of a text that was cut. Timeout Marker (ms) holds the number of milliseconds in a "
                 "DUMP TIMEOUT line printed inside a service section; such a section may have been cut short and its rows may be "
                 "partial. Timeout Marker (ms) is empty for every other section, and it was "
                 "empty on all rows of two of the five tested reports. Read By names the Android Bug Report artifacts that present "
                 "rows from the section, and 'not read' means that none of them does, which says nothing about what the section "
                 "holds: the logs (SYSTEM LOG, EVENT LOG, RADIO LOG), app ops, battery, network, Wi-Fi, accounts, notifications, jobs, "
                 "alarms, kernel, process, ANR trace and tombstone sections are among those not read here. A service the platform "
                 "did not reach when it stopped dumping has no row, and a group's line range includes the services inside it. Members "
                 "of a bug report zip other than the main text (FS/data/anr, FS/data/tombstones, proto, FS/cache/recovery and others) "
                 "are not listed; whether ALEAPP's android_anr_traces and android_tombstones artifacts read the first two from a "
                 "zip given as the input was not tested here. The text is read line by line and is not modified; up to six report texts are kept for the four artifacts of one run, so each is read once per run (with more than six staged, a text can be read again). Source File held one value on "
                 "all rows of each tested report, which was read alone, and holds one value per report when several are staged.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 609, 656, 410, 343 and 539 rows, whose start lines, "
                 "end lines and durations equal those of an independent index written for another tool, except the end line of the "
                 "last section of two reports, which has no duration line and runs to the end of the text (the other index counts "
                 "one line more there). Not examined: Android 11 and 12, vendors other than those named here and the corpus builds in sample_data, and a text whose sections are laid out differently.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "list-details",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two error dumpstate zips | 824 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 74 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 101 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 74 rows",
        },
    },
    "bugreport_packages": {
        "name": "Bug Report - Installed Packages",
        "description": "One row per Package block of the package service dump in an Android bug report text, "
                       "with version, code path, flags, installer fields and the per-user state as printed.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report",
        "notes": "One row per Package [name] block of the Packages: and Hidden system packages: parts of the package service dump "
                 "(DUMP OF SERVICE package) of the bug report text. Block says which part. The same package name is in both parts "
                 "in the tested reports (29 to 90 names); the hidden part is read here as the system copy that an update replaced, "
                 "a reading this plugin does not cite from the platform, and the corpus report prints no hidden part. App ID is the "
                 "appId value (printed on the Android 15 and 16 reports) or the userId value (printed on the Android 10 and 13 "
                 "reports), as printed; Shared User is the name and id from the sharedUser line. Version Code, Min SDK and Target SDK come from the versionCode line; Version "
                 "Name, Code Path and Flags (the words of the flags line, or of the pkgFlags line when no flags line came before it; the Android 13 report prints both and the flags line comes first) are as printed. Installer, "
                 "Initiating Package and Originating Package are the installerPackageName, initiatingPackageName and "
                 "originatingPackageName values, empty where the value printed is null or the line is not printed. The Android 10 "
                 "builds tested print the installer only when one is set and print neither of the other two, so Initiating Package "
                 "is empty on all rows of two of the five reports. Originating Package was empty on all rows of four of the five tested "
                 "reports (the value printed was null). Initiating Package is identical to Installer on every row of one report. Package Source is the packageSource number as printed, not decoded. Package Source is empty on all rows of two reports and holds "
                 "one value, 0, on every row of two others. Users Installed lists the Android users for which the dump prints installed=true, and User "
                 "State shows for each user the installed, stopped, hidden, suspended and enabled values as printed (enabled is a "
                 "stored number, not decoded). Users Installed held one value, 0, on all rows of four of the five tested reports, "
                 "because the dump listed one Android user there; the fifth listed two users (0 and 11). Source Line is the line "
                 "of the Package header.\n"
                 "What the rows do not show: the dump is the package manager's list at the moment of the report: an app the package manager no longer lists has no row, and an app removed for one user can still have a row with installed=false for that user. A row does not say how or when the app arrived, from where, or whether "
                 "it was used. An empty installer does not show how an app was installed. Permissions, signatures, components, "
                 "shared users, package changes and the dexopt state, which the same dump holds, are not read. The package dump of "
                 "one tested report (Samsung A-series) ends with a DUMP TIMEOUT marker, the log says so, and its list may then be "
                 "partial (572 packages were read).\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 572, 720, 322, 284 and 667 rows, each equal to the "
                 "number of Package headers counted in the raw text and to an independent parser, field by field. Two Android users "
                 "in one dump were seen on one of the five reports; the per-user columns were also built on constructed text. Also "
                 "run on the corpus Samsung Android 13 report of s20fe_a13: 465 rows, equal to the Package headers counted in its "
                 "raw text. Not examined: Android 11, 12 and 14, other vendors, and dumps from a device with work profiles or a Private Space.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "package",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two error dumpstate zips | 465 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        },
    },
    "bugreport_package_times": {
        "name": "Bug Report - Package Times",
        "description": "The firstInstallTime, lastUpdateTime and timeStamp values printed in the package service dump "
                       "of an Android bug report text, with a note on unset values and image-wide placeholder values.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-26",
        "last_update_date": "2026-10-26",
        "requirements": "none",
        "category": "Android Bug Report",
        "notes": "One row per firstInstallTime, lastUpdateTime and timeStamp value printed in a Package block of the package "
                 "service dump. Event is the key as printed. firstInstallTime is printed for each Android user on the Android 13, 15 and "
                 "16 reports (User names the user) and once per package on the two Android 10 reports, where User is empty. lastUpdateTime and timeStamp are printed once per package. What the platform means by timeStamp is not "
                 "established here and the key is not interpreted. The values are device wall-clock text without a zone: Time (UTC) "
                 "converts them with the zone shown in Bug Report - Device Facts, Time As Printed keeps the text; Time (UTC) is kept to whole seconds in the report and in LAVA; and a value that cannot be converted has no UTC and says why in Time Note. Block "
                 "says whether the row belongs to the Packages or the Hidden system packages part.\n"
                 "Time Note. A value that, read in the report's zone, is 1970-01-01 00:00:00 UTC or one second before it, or that "
                 "is printed as 1970-01-01 00:00:00 or 1969-12-31 23:59:59, gets no UTC and the note says the time is not set on "
                 "the device (178 to 425 rows of three of the five tested reports, none on the others; 57 rows of s20fe_a13). A "
                 "value is also marked 'placeholder or image-wide value, not read as an install time' when "
                 "it passes one of three tests that look at values and never at package names: (1) a fixed placeholder, a time "
                 "whose minute is 00, 30 or 45 and whose second is 00 within 14 hours of 2009-01-01 00:00:00, or exactly "
                 "2022-01-01 00:00:00; (2) a time that 20 or more different packages share, counting only packages that sit on the "
                 "system image (code path outside /data, /mnt, /sdcard and /storage, or a package from the hidden system part); (3) "
                 "a run of such times no more than 2 seconds apart and within 30 seconds, shared by 20 or more of those packages "
                 "together. A marked row keeps its printed time and its UTC value, so a timeline can be filtered on the column; a "
                 "value that passes no test is not marked (22 user apps updated within two seconds of each other are not, in the "
                 "constructed text). The tests and their numbers are this plugin's rule for the image-wide values seen in the tested "
                 "reports, not a statement of the platform: a marked value could still be a real time in a rare case, and a factory "
                 "value shared by fewer than 20 packages is not marked. In the five tested reports 62 to 91 percent of the rows were "
                 "marked (1,199 of 1,716; 1,331 of 2,160; 876 of 966; 1,692 of 2,668; 734 of 852).\n"
                 "What the rows do not show: a time without a note is the value the dump prints for that package, not proof of the "
                 "date an app was installed, updated or used, and it says nothing about apps removed before the report. The same "
                 "package can have rows in both parts of the dump.\n"
                 "Evidence tiers. Data-proven on five real bug reports (Samsung A-series and S-series on Android 16, Huawei and a "
                 "Transsion-brand phone on Android 10, Motorola on Android 15): 1,716, 2,160, 966, 852 and 2,668 rows, equal to the "
                 "number of time lines counted in the raw text and, row by row with the marking, to an independent implementation "
                 "of the same rule. The thresholds (20 packages, 2 and 30 seconds) were chosen on these five reports. On the "
                 "corpus report of s20fe_a13, 1,230 of 1,395 rows carry one marked value, a test 1 placeholder printed for 410 "
                 "packages. Daylight-saving edges and a report with no time zone were tested on constructed text "
                 "only.",
        "paths": ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                  '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "s20fe_a13": "Android 13 | Samsung dumpState zip and two error dumpstate zips | 1,395 rows",
            "samsungs20_a13": "Android 13 | Samsung error dumpstate zip | 0 rows",
            "sharon_a14": "Android 14 | Samsung error dumpstate zip | 0 rows",
            "userb2_a13": "Android 13 | two partial Shell bug report texts (.tmp) | 0 rows",
        },
    },
}

from scripts import dumpstate_reader
from scripts.ilapfuncs import artifact_processor, logfunc


def _reports(context):
    """The bug report texts among the staged files, as (Source File label, Report) pairs."""
    return dumpstate_reader.load_reports(context.get_files_found(), context.get_relative_path, logfunc)


def _source_path(context, reports):
    """The staged files that were read; the matched files when none was a bug report."""
    paths = [report.source.path for _label, report in reports] or sorted(str(path) for path in context.get_files_found())
    return '\n'.join(dict.fromkeys(str(path) for path in paths))


def _utc_text(moment):
    return moment.strftime('%Y-%m-%d %H:%M:%S') if moment is not None else ''


@artifact_processor
def bugreport_device_facts(context):
    headers = ('Fact', 'Value', 'Origin', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        for fact in report.facts:
            rows.append((fact.name, fact.value, fact.origin, fact.line, label))
        rows.append(('Report time (UTC)', _utc_text(report.report_utc()), 'derived', None, label))
        rows.append(('Time zone used for UTC values',
                     report.zone_name if report.clock.known else 'none: the report records no usable time zone',
                     'derived', None, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_packages(context):
    headers = ('Package', 'Block', 'App ID', 'Shared User', 'Version Code', 'Version Name', 'Min SDK',
               'Target SDK', 'Code Path', 'Flags', 'Installer', 'Initiating Package', 'Originating Package',
               'Package Source', 'Users Installed', 'User State', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        if 'package' not in report.sections_seen:
            logfunc(f'Bug report {label}: no package service dump in this report')
        cut = [section.timeout_ms for section in report.sections if section.name == 'package' and section.timeout_ms]
        if cut:
            logfunc(f'Bug report {label}: the package service dump was cut by a {cut[0]} ms '
                    f'timeout, the list is partial')
        for package in report.packages:
            rows.append((package.package, package.block, package.app_id, package.shared_user, package.version_code,
                         package.version_name, package.min_sdk, package.target_sdk, package.code_path, package.flags,
                         package.installer, package.initiating, package.originating, package.package_source,
                         package.users_installed, package.user_states, package.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_package_times(context):
    headers = (('Time (UTC)', 'datetime'), 'Time As Printed', 'Package', 'Event', 'User', 'Installer', 'Block',
               'Time Note', 'Source Line', 'Source File')
    rows = []
    reports = _reports(context)
    for label, report in reports:
        for item in report.package_times:
            moment, note = report.time_value(item.wall)
            rows.append((moment, item.wall, item.package, item.event, item.user, item.installer, item.block,
                         note, item.line, label))
    return headers, rows, _source_path(context, reports)


@artifact_processor
def bugreport_sections(context):
    headers = ('Section', 'Kind', 'Start Line', 'Last Line', 'Lines', 'Printed Duration (s)', 'Timeout Marker (ms)', 'Read By',
               'Source File')
    kinds = {'preamble': 'header', 'command': 'command', 'service': 'dumpsys service'}
    rows = []
    reports = _reports(context)
    for label, report in reports:
        for section in report.sections:
            kind = 'dumpsys group' if section.group else kinds[section.kind]
            last = section.end_line - 1
            lines = last - section.line + (1 if section.kind == 'preamble' else 0)
            read_by = dumpstate_reader.READ_BY.get((section.kind, section.name), 'not read')
            rows.append((section.name, kind, section.line, last, lines, section.duration, section.timeout_ms, read_by, label))
    return headers, rows, _source_path(context, reports)
