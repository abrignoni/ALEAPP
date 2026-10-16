# pylint: disable=W0631
__artifacts_v2__ = {
    "clipboard": {
        "name": "Clipboard Data",
        "description": "Files under a folder named clipboard or semclipboard: for a file alone in its folder the text read from a fixed line and character offset, and in a folder holding several files each file other than clip as media, with the file's modification time as the extraction records it",
        "author": "Alexis Brignoni, @AlexisBrignoni, Codex",
        "creation_date": "2022-01-08",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Clipboard",
        "notes": "Modified Time is the modification time the extraction records for the file, read from the "
                 "seeker's record of it and shown in UTC: a tar member's own time, the extended timestamp field "
                 "(0x5455) of a zip member, or the file's time in a folder input. It is blank for a zip member "
                 "with no extended timestamp field, because the seeker records no time for it and the member's "
                 "own date and time carry no zone. The time of the copy staged in the report folder is not used. On "
                 "anne_a15, galaxys10_a10 and samsunga53_a14 every matched file carried the extended timestamp "
                 "field; on samsungs20_a13 and sharon_a14 none did, and neither produced a row. The declared "
                 "pattern matches any folder whose name ends in clipboard; a matched file is read only when a "
                 "folder in its path is named exactly clipboard or semclipboard, and any other is skipped with "
                 "a line in the run log. Across the 44 registered Android images the pattern matched files "
                 "under folders of those two names only (data/clipboard, data/semclipboard and "
                 "com.samsung.android.honeyboard/clipboard), so that skip is not exercised by a registered "
                 "image. A file counts as alone in its folder only when no other matched path holds its "
                 "folder's path, and a zip that lists the folder itself supplies such a path. On anne_a15, "
                 "galaxys10_a10, samsunga53_a14 and cookbook_a11 every row was a media row and no row "
                 "carried text. Path is the file's path in the extraction.",
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

def recorded_modtime(seeker, file_found):
    """The modification time the extraction records for a staged file, or '' when it records none.

    The staged copy's own time is not used: for a zip member the seeker sets it from the
    member's zone-less date and time read in the examiner machine's zone.
    """
    info = seeker.file_infos.get(file_found) if seeker else None
    if info and info.modification_date:
        return convert_unix_ts_to_utc(info.modification_date)
    return ''

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
                        modtime = recorded_modtime(seeker, file_found)
                        data_list.append((modtime, '', media, path))
                else:
                    #print('Outside of Matching')
                    path = context.get_relative_path(file_found)
                    textdata = triage_text(file_found)
                    modtime = recorded_modtime(seeker, file_found)
                    data_list.append((modtime, textdata, '', path))

    data_headers = (('Modified Time','datetime'), 'Data', ('Media','media'), 'Path')
    return data_headers, data_list, file_found
