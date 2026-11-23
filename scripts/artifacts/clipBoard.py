# pylint: disable=W0631
__artifacts_v2__ = {
    "clipboard": {
        "name": "Clipboard Data",
        "description": "Files under a folder named clipboard or semclipboard: for a file alone in its folder the text read from one of two fixed line and character offsets, and in a folder holding several files each file other than clip as media, with the file's modification time as the tool reads it from the input",
        "author": "Alexis Brignoni, @AlexisBrignoni, Codex",
        "creation_date": "2022-01-08",
        "last_update_date": "2026-11-23",
        "requirements": "none",
        "category": "Clipboard",
        "notes": "Modified Time is the modification time the extraction records for the file, read from the "
                 "seeker's record of it and shown in UTC: a tar member's own time, the NTFS field (0x000a) or "
                 "else the extended timestamp field (0x5455) of a zip member, the file system time of a disk "
                 "image, or the file's time in a folder input. When the tool reads no UTC modification time, "
                 "Modified Time is blank. If the input holds a date and time with no zone, Modified (no zone, "
                 "as stored) shows it as text, with no zone conversion. A recorded time of 0 is treated as no "
                 "time. Both columns are blank when the input holds neither. That is the case for a FAT "
                 "directory entry, an exFAT directory entry (its stored UTC offset is not applied or shown "
                 "here) and a zip entry from which no UTC modification time is read, for example one with only"
                 " its DOS date and time, or with an extra field whose modification time is missing, 0 or "
                 "unreadable. Which zone such a reading is in is not established. A zip entry's DOS date and "
                 "time is shown as decoded, with no validity check, so an unset one reads 1980-00-00 00:00:00."
                 " Modified (no zone, as stored) had no value on any row of the registered images in "
                 "sample_data on a run of 2026-11-23. The reading was exercised on constructed FAT32, exFAT "
                 "and DOS-only zip inputs under two examiner time zones. The UTC column was blank, the no-zone"
                 " column showed the value decoded separately from the input for each file, and it did not "
                 "change with the zone. The time of the copy staged in the report folder is not used. On "
                 "anne_a15, galaxys10_a10 and samsunga53_a14 every matched file carried the extended timestamp"
                 " field; on samsungs20_a13 and sharon_a14 none did, and neither produced a row. The declared "
                 "pattern matches any folder whose name ends in clipboard; a matched file is read only when a "
                 "folder in its path is named exactly clipboard or semclipboard, and any other is skipped with"
                 " a line in the run log. Across the registered Android images checked for this artifact the "
                 "pattern matched files under folders of those two names only (data/clipboard, "
                 "data/semclipboard and com.samsung.android.honeyboard/clipboard), so that skip is not "
                 "exercised by a registered image. A file counts as alone in its folder only when no other "
                 "matched path holds its folder's path, and a zip that lists the folder itself supplies such a"
                 " path. On anne_a15, galaxys10_a10, samsunga53_a14 and cookbook_a11 every row was a media row"
                 " and no row carried text. Path is the file's path in the extraction.",
        "paths": ('*/*clipboard/*/*'),
        "output_types": "standard",
        "artifact_icon": "clipboard",
        "sample_data": {
            "anne_a15": "Android 15 | com.samsung.android.honeyboard vc 590202300 | 1 row",
            "galaxys10_a10": "Android 10 | 10 rows",
            "samsunga53_a14": "Android 14 | com.samsung.android.honeyboard | 3 rows",
            "samsungs20_a13": "Android 13 | com.samsung.android.honeyboard | 0 rows",
            "sharon_a14": "Android 14 | com.samsung.android.honeyboard vc 560051300 | 0 rows",
        },
    }
}

import os

from scripts.ilapfuncs import artifact_processor, check_in_media, convert_unix_ts_to_utc, logfunc

CLIPBOARD_FOLDERS = ('clipboard', 'semclipboard')

def _usable(value):
    """Whether a recorded time is a nonzero, finite number."""
    return isinstance(value, (int, float)) and value != 0 and value == value and abs(value) != float('inf')


def _file_times(seeker, path):
    """(UTC seconds, reading with no zone) the input records for a staged file.

    The staged copy's own time is not used: for a FAT, exFAT or DOS-only zip reading it is
    that reading placed in the examiner's time zone.
    """
    infos = getattr(seeker, 'file_infos', None) or {}
    windows = str(path).replace('/', '\\')
    bare = windows.removeprefix('\\\\?\\')
    info = next((infos[name] for name in (str(path), windows, bare, '\\\\?\\' + bare)
                 if name in infos), None)
    times = getattr(info, 'times', None)
    modified = getattr(times, 'modified', None)
    if _usable(modified):
        return modified, ''
    # a reading with no zone comes before the older field, which is never read as its UTC time
    reading = getattr(times, 'modified_no_zone', None)
    if reading:
        return None, reading
    modified = getattr(info, 'modification_date', None)
    if _usable(modified):
        return modified, ''
    return None, ''


def recorded_modtime(seeker, file_found):
    """(UTC modification time or '', reading with no zone or '') for a staged file."""
    recorded, no_zone = _file_times(seeker, file_found)
    return (convert_unix_ts_to_utc(recorded) if recorded else ''), no_zone


def triage_text(file_found):
    output = ''
    with open(file_found,'r' ,encoding="utf8", errors="backslashreplace") as file:
        counter = 0
        for f in file:
            counter = counter + 1
            if counter == 8:
                output = output + (f[20:])
            elif counter > 8:
                output = output + (f)
        
        if not output:
            counter = 0
            file.seek(0)
            for f in file:
                counter = counter + 1
                if counter == 7:
                    output = output + (f[91:])
                elif counter > 7:
                    output = output + (f)
    
    return str(output.rstrip())

@artifact_processor
def clipboard(context):
    files_found = context.get_files_found()
    seeker = context.get_seeker()
    data_list = []
    for file_found in files_found:
        if file_found.endswith('.DS_Store'):
            pass
        else:
            if os.path.isfile(file_found):
                folders = str(context.get_relative_path(file_found)).replace('\\', '/').lower().split('/')[:-2]
                if not any(folder in CLIPBOARD_FOLDERS for folder in folders):
                    logfunc(f'Clipboard Data: skipped {context.get_relative_path(file_found)}, '
                            'no folder in its path is named clipboard or semclipboard')
                    continue
                dirname = os.path.dirname(file_found)
                matching = [s for s in files_found if dirname in s]
                if len(matching) > 1:
                    if file_found.endswith('clip'):
                        pass
                    else:
                        media = check_in_media(file_found, name=os.path.basename(file_found)) or ''
                        path = context.get_relative_path(file_found)
                        modtime, no_zone = recorded_modtime(seeker, file_found)
                        data_list.append((modtime, no_zone, '', media, path))
                else:
                    #print('Outside of Matching')
                    path = context.get_relative_path(file_found)
                    textdata = triage_text(file_found)
                    modtime, no_zone = recorded_modtime(seeker, file_found)
                    data_list.append((modtime, no_zone, textdata, '', path))

    data_headers = (('Modified Time','datetime'), 'Modified (no zone, as stored)', 'Data', ('Media','media'), 'Path')
    return data_headers, data_list, file_found
