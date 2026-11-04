__artifacts_v2__ = {
    "bugreport_recovery_history": {
        "name": "Bug Report - Recovery History",
        "description": "The Samsung recovery history files kept inside an Android bug report zip that is itself a file of an extraction "
                       "(cache or efs recovery folder), in the columns of sRecoveryhist.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-27",
        "last_update_date": "2026-10-28",
        "requirements": "none",
        "category": "Android Bug Report - Boot, Crash and Dropbox",
        "notes": "The members of a bug report zip named FS/cache/recovery/history, last_history, last_all_history, last_extra_history "
                 "and extra_history (and the same names under efs/recovery) are read from the zip as it is, with the reader and the "
                 "columns of sRecoveryhist (see its notes for the fields, the Activity words, the volumes of the extra history file and "
                 "the times, shown as printed with nothing derived). Source File names the zip and the member.\n"
                 "Two cases are read by two different artifacts, so that no file is listed twice. The same record can still appear in "
                 "both artifacts when the device holds the cache files and a bug report zip with a copy of them (on one corpus image all"
                 " 42 bug report records also appear in sRecoveryhist). When the bug report zip is the input of the tool (input type "
                 "zip), its members are already files of the extraction and sRecoveryhist reads them; this artifact then finds only the "
                 "bug report text, which holds no recovery files, and says so in the log. When the zip is a file inside an extraction "
                 "(for example a Shell app bug report kept on the device), its members are not files of the extraction and this artifact"
                 " reads them. A zip with no such member gives no rows and the log says so; no rows say nothing about the device. "
                 "last_history and last_all_history can hold the same entries, and then both are listed, each with its own Source File.\n"
                 "Evidence tiers. Data-proven on seven real bug reports (Samsung phones on Android 16, a Huawei and a Transsion-brand "
                 "phone on Android 10, a Motorola phone on Android 15): the three Samsung reports that carry last_history gave 1, 4 and "
                 "19 entries, and the same numbers again from last_all_history, each equal to a count of the header lines of the member;"
                 " the other four reports carry no such member and give no rows. The 4-entry and 19-entry members hold update entries "
                 "only. The reading was done on the zips themselves, called in place, and on a zip placed inside a folder given to the "
                 "tool (input type fs); the whole tool with the zip as input (type zip) gave the same entries through sRecoveryhist. "
                 "Corpus run 2026-10-28 (-t fs): a Samsung Android 13 image holding a dumpState zip under data/log gave 42 + 42 rows "
                 "(s20fe_a13; a byte-identical copy of the zip under data/media/0/log was not read a second time); four other Samsung "
                 "dumpstate zips on three images (Android 13 and 14) hold no recovery member; a Pixel Shell bug report file on one image"
                 " is 46 bytes and not a zip, logged as unopenable. Constructed text only: SIM-based CSC change and prompt-and-wipe "
                 "entries inside a bug report zip (wipe entries: 4, each listed in two files, on one corpus image). Not examined: "
                 "Android 11 and 12, and vendors other than the four families (a Pixel Shell bug report on one corpus image was not a "
                 "readable zip).",
        "paths": ('*/bugreport-*.zip', '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'),
        "output_types": "standard",
        "artifact_icon": "rotate-ccw",
        "sample_data": {
            "s20fe_a13": "Android 13 | 84 rows",
        },
    },
}

import posixpath
import re
import zipfile

from scripts import android_recovery_history as recovery
from scripts import dumpstate_reader
from scripts.artifacts.sRecoveryhist import DATA_HEADERS, row_of
from scripts.ilapfuncs import artifact_processor, logfunc

MEMBER = re.compile(r'^(?:.*/)?(?:cache|efs)/recovery/(?:%s)$' % '|'.join(recovery.HISTORY_NAMES + recovery.EXTRA_NAMES))
MEMBER_CAP = 8 * 1024 * 1024


@artifact_processor
def bugreport_recovery_history(context):
    files = []
    read_from = []
    paths = sorted(str(path) for path in context.get_files_found())
    sources, notes = dumpstate_reader.find_sources(paths)
    for note in notes:
        dumpstate_reader.say_once(logfunc, 'Bug report: ' + note)
    for source in sources:
        label = context.get_relative_path(source.path)
        if not source.member:
            dumpstate_reader.say_once(logfunc, f'Bug report {label}: a bug report text read alone holds no recovery history files '
                                               f'(they are members of a zip; when the zip is the input, sRecoveryhist reads them), '
                                               f'no rows from it')
            continue
        try:
            archive = zipfile.ZipFile(source.path)
        except dumpstate_reader.READ_ERRORS as error:
            dumpstate_reader.say_once(logfunc, f'Bug report {label}: could not be opened: {error}')
            continue
        with archive:
            found = False
            for info in sorted(archive.infolist(), key=lambda item: item.filename):
                if info.is_dir() or not MEMBER.match(info.filename):
                    continue
                try:
                    with archive.open(info) as handle:
                        data = handle.read(MEMBER_CAP + 1)
                except dumpstate_reader.READ_ERRORS as error:
                    dumpstate_reader.say_once(logfunc, f'Bug report {label}: {info.filename} could not be read: {error}')
                    continue
                if len(data) > MEMBER_CAP:
                    dumpstate_reader.say_once(logfunc, f'Bug report {label}: {info.filename} is larger than {MEMBER_CAP} bytes, '
                                                       f'the first {MEMBER_CAP} were read')
                    data = data[:MEMBER_CAP]
                found = True
                files.append((label + '!/' + posixpath.dirname(info.filename), posixpath.basename(info.filename),
                              label + '!/' + info.filename, data.decode('utf-8', 'replace')))
            if found:
                read_from.append(source.path)
            else:
                dumpstate_reader.say_once(logfunc, f'Bug report {label}: the zip holds no recovery history file '
                                                   f'(cache or efs recovery folder), no rows from it')

    def warn(label, text):
        dumpstate_reader.say_once(logfunc, f'Recovery history {label}: {text}')
    rows = [row_of(record) for record in recovery.records_from_files(files, warn)]
    return DATA_HEADERS, rows, '\n'.join(read_from if read_from else paths)
