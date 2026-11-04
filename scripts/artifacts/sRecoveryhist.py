__artifacts_v2__ = {
    "get_sRecoveryhist": {
        "name": "sRecoveryhist",
        "description": "Parses Samsung recovery history (timestamp, firmware build, wipe and prompt-and-wipe arguments, reason, reboot reason, "
                       "locale, the options as printed, an activity reading and the volumes named in the extra history file) from the efs "
                       "and cache recovery history files.",
        "author": "@abrignoni, @danjethh, Claude",
        "creation_date": "2021-08-15",
        "last_update_date": "2026-10-28",
        "requirements": "none",
        "category": "Wipe & Setup",
        "notes": "Each record begins with a '+ [tag | timestamp | build]' header. One file shape closes the first bracket after the tag "
                 "('+ [tag] | timestamp | build]'); it is read the same way. A record can end with a lone '-' line or with no separator,"
                 " in which case the next '+' header ends the previous record. Both layouts are read, and so is an older header shape "
                 "without brackets ('+ ... : timestamp'). A lone '-' separator line is not shown. The header timestamp carries no time "
                 "zone and is reported as written, with slashes replaced by dashes. The zone it was written in is not established here. "
                 "A record with --wipe_data shows recovery was started with the argument AOSP documents as erasing user data and cache. "
                 "A record with --prompt_and_wipe_data shows recovery was started with the argument AOSP documents as prompting that "
                 "data is corrupt and erasing it with consent; the record does not show whether the erase went ahead. Wipe reads Yes "
                 "only for --wipe_data; a --prompt_and_wipe_data record reads Yes under Prompt & Wipe and leaves Wipe blank unless the "
                 "record also carries --wipe_data. The --carry_out value is reported as stored in Carry Out; its meaning is not sourced "
                 "here. Reference: AOSP, bootable/recovery/recovery.cpp at tag android-14.0.0_r1, "
                 "https://android.googlesource.com/platform/bootable/recovery/+/refs/tags/android-14.0.0_r1/recovery.cpp#83\n"
                 "Added 2026-10-28: Build no longer carries the closing bracket and the dash of a header that ends in ' [-]' (the "
                 "earlier reading returned them as part of the build text on the two Android 16 files tested). Options (as printed) "
                 "lists every '--' line of the record (control characters shown as a space, a line cut at 400 characters), so options "
                 "with no column of their own (for example --data_resizing) are visible. Activity is this tool's reading of the options:"
                 " 'Wipe requested (--wipe_data)', 'Prompt and wipe requested (--prompt_and_wipe_data)', 'Update package "
                 "(--update_package)', 'SIM-based CSC change (A -> B)' (read from a reason of the form '[SIMBasedChangeCSC] A -> B', A "
                 "and B shown as printed and not decoded; what CSC stands for is not sourced here) or 'Other'; the words say which "
                 "options are printed ('wipe requested'), not that a wipe or an update was carried out or finished, nor who asked for it"
                 " or why. Status Line is the NP or RP line of the record, Other Lines are lines of the record in no other form and "
                 "Entry Line is the line of the header in the file. Formatted Volumes lists the volumes named in 'format_volume : "
                 "<volume>' lines of the extra history file (extra_history, or last_extra_history next to the cache files) that carry "
                 "the same code ('start and end lines' when the file has an S line and an E line for the volume; what S and E stand for "
                 "is not sourced here, and the words are this tool's reading); a code in the extra file with no record in the history "
                 "file gets a row of its own, and a code used by more than one record of a file is noted because volumes can only be "
                 "matched by code. Other lines of the extra file (for example 'resizing data') are not shown.\n"
                 "Times. Timestamp is the header date and Request Timestamp the --requested_time value, both as printed (slashes "
                 "replaced by dashes, as before); no other time is derived from them and none is labelled UTC. A header date before 2012"
                 " is noted in Entry Notes. On the two Android 16 phones the author tested, the wipe records showed 1970 header dates "
                 "and one phone showed 2010. On ten corpus images (Android 10 to 15) each wipe record carried a header date in the same "
                 "year as a record next to it, or the year before or after, and one image held a record dated 2010 (listed in two of its"
                 " files). A header date is therefore not by itself the time of the record. Header dates were not always in ascending "
                 "order in the files tested (one bug report file with 19 entries held earlier dates after later ones), so the order of "
                 "rows is the order written and not a time order.\n"
                 "Files: efs/recovery/history with efs/recovery/extra_history, and cache/recovery/last_history, last_all_history and "
                 "last_extra_history wherever a search finds them (cache files also turn up loose when a bug report zip is the input; a "
                 "bug report zip kept inside an extraction is read by Bug Report - Recovery History). efs/recovery/history, last_history"
                 " and last_all_history can hold the same records. A record is then listed once per file, each with its own Source File,"
                 " so one record can appear up to three times here (on three corpus images every record did), and again in Bug Report - "
                 "Recovery History when a bug report zip on the device holds a copy of the cache files. last_extra_history_old and the "
                 "other recovery files (logs, kernel messages) are not read. sWipehist lists the wipe records of the same efs file and "
                 "reads data/log/recovery_history.log as well.\n"
                 "Evidence tiers. Data-proven on two Samsung full file system extractions (a flagship phone and an A-series phone, both "
                 "Android 16) and on three Samsung bug report zips that carry cache recovery files (Android 16): the efs files gave 5 "
                 "and 3 records, equal to a count of the header lines, and the columns of the earlier reading matched field by field "
                 "except Build (see above); the cache files gave 1, 4 and 19 records from last_history and the same numbers from "
                 "last_all_history. The 5-record file holds two wipe records with requested times and three SIM-based CSC change "
                 "records; the volumes of both wipe codes came from the extra file by code. The 3-record file holds one SIM-based CSC "
                 "change and two update records. Corpus run 2026-10-28 (-t fs): rows equal the '+' header lines in every file on 10 "
                 "Samsung images, Android 10 to 15 (efs history on 7, cache files on 7); totals in sample_data. Constructed text only: "
                 "prompt-and-wipe records, the spaced reboot reason form, header lines without pipes or firmware, CRLF line ends and an "
                 "extra file without a history file. Not examined: devices other than Samsung (the files are Samsung's; nine non-Samsung"
                 " corpus images hold none). A history file holds a limited number of records (4 to 50 on the corpus images): a record "
                 "that is not listed says nothing about earlier use, and a file with no wipe option says only that this file holds none."
                 " A wipe option says that a wipe was requested of recovery; it does not show that the wipe ran or finished, when it "
                 "ran, or who asked for it.",
        "paths": ('*/efs/recovery/history', '*/efs/recovery/extra_history', '*/cache/recovery/last_history',
                  '*/cache/recovery/last_all_history', '*/cache/recovery/last_extra_history'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "file",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 8 rows",
            "cookbook_a11": "Android 11 | 30 rows",
            "adams_ss135dl_a13": "Android 13 | 24 rows",
            "falken_a326u_a13": "Android 13 | 54 rows",
            "s20fe_a13": "Android 13 | 138 rows",
            "samsungs20_a13": "Android 13 | 14 rows",
            "sharon_a13": "Android 13 | 18 rows",
            "samsunga53_a14": "Android 14 | 50 rows",
            "sharon_a14": "Android 14 | 13 rows",
            "anne_a15": "Android 15 | 9 rows",
        },
    }
}

import os

from scripts import android_recovery_history as recovery
from scripts.ilapfuncs import artifact_processor, logfunc

MAX_FILE_BYTES = 16 * 1024 * 1024

DATA_HEADERS = ('Timestamp', 'Request Timestamp', 'Build', 'Entry Tag (as stored)', 'Wipe', 'Prompt & Wipe', 'Reason',
                'Reboot Reason', 'Locale', 'Carry Out', 'Update ORG', 'Update PKG', 'Activity', 'Options (as printed)',
                'Formatted Volumes', 'Status Line', 'Other Lines', 'Entry Notes', 'Entry Line', 'Extra History File', 'Source File')


def read_text(path):
    """The decoded text of a file (utf-8, undecodable bytes replaced), or None when it cannot be read."""
    try:
        with open(path, 'rb') as handle:
            data = handle.read(MAX_FILE_BYTES + 1)
    except OSError as error:
        logfunc(f'Recovery history: {os.path.basename(path)} could not be read: {error}')
        return None
    if len(data) > MAX_FILE_BYTES:
        logfunc(f'Recovery history: {os.path.basename(path)} is larger than {MAX_FILE_BYTES} bytes, the first {MAX_FILE_BYTES} were read')
        data = data[:MAX_FILE_BYTES]
    return data.decode('utf-8', 'replace')


def dashed(text):
    """A date as the earlier reading of this artifact showed it: slashes replaced by dashes."""
    return text.replace('/', '-')


def row_of(record):
    """The row of one record of android_recovery_history.records_from_files."""
    entry = record['entry']
    names = [option.split('=', 1)[0] for option in entry.options] if entry else []
    return (dashed(record['header_text']), dashed(record['requested']), record['firmware'], record['code'],
            'Yes' if '--wipe_data' in names else '', 'Yes' if '--prompt_and_wipe_data' in names else '',
            record['reason'], record['reboot_reason'],
            recovery.option_value(entry, '--locale') if entry else '', recovery.option_value(entry, '--carry_out') if entry else '',
            recovery.option_value(entry, '--update_org_package') if entry else '', entry.update_package if entry else '',
            record['activity'], record['options'], record['volumes'],
            record['status'], record['other'], record['notes'], record['line'], record['extra_file'], record['source'])


@artifact_processor
def get_sRecoveryhist(context):
    files = []
    for path in sorted(str(item) for item in context.get_files_found()):
        name = os.path.basename(path)
        if name not in recovery.HISTORY_NAMES and name not in recovery.EXTRA_NAMES:
            continue  # Skip all other files
        text = read_text(path)
        if text is None:
            continue
        files.append((os.path.dirname(path), name, context.get_relative_path(path), text))

    def warn(label, text):
        logfunc(f'Recovery history {label}: {text}')
    data_list = [row_of(record) for record in recovery.records_from_files(files, warn)]
    sources = list(dict.fromkeys(label for _folder, _name, label, _text in files))
    return DATA_HEADERS, data_list, '\n'.join(sources)
