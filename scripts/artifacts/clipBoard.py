# pylint: disable=W0631
__artifacts_v2__ = {
    "clipboard": {
        "name": "Clipboard Data",
        "description": "Clipboard artifacts",
        "author": "Alexis Brignoni",
        "creation_date": "2022-01-08",
        "last_update_date": "2025-09-09",
        "requirements": "none",
        "category": "Clipboard",
        "notes": "",
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
import time

from scripts.ilapfuncs import artifact_processor, check_in_media

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
    data_list = []
    for file_found in files_found:
        if file_found.endswith('.DS_Store'):
            pass
        else:
            if os.path.isfile(file_found):
                dirname = os.path.dirname(file_found)
                matching = [s for s in files_found if dirname in s]
                if len(matching) > 1:
                    if file_found.endswith('clip'):
                        pass
                    else:
                        media = check_in_media(file_found, name=os.path.basename(file_found)) or ''
                        path = file_found
                        modtime = os.path.getmtime(file_found)
                        modtime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(modtime))
                        data_list.append((modtime, '', media, path))
                else:
                    #print('Outside of Matching')
                    path = file_found
                    textdata = triage_text(file_found)
                    modtime = os.path.getmtime(file_found)
                    modtime = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(modtime))
                    data_list.append((modtime, textdata, '', path))

    data_headers = (('Modified Time','datetime'), 'Data', ('Media','media'), 'Path')
    return data_headers, data_list, file_found
