__artifacts_v2__ = {
    "mozillaProfileTimes": {
        "name": "Mozilla Browser Profile Times",
        "description": "The created and firstUse values of each Mozilla-based browser profile's times.json "
                       "(Firefox, Tor Browser and other apps that keep a files/mozilla/<profile> folder).",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-30",
        "last_update_date": "2026-10-30",
        "requirements": "none",
        "category": "Mozilla Browsers",
        "notes": "Reads times.json in each files/mozilla/<profile> folder of an app's data directory, one "
                 "row per profile. Mozilla's ProfileAge module writes this file "
                 "(https://github.com/mozilla-firefox/firefox/blob/204a96d56b40285148fea160628bbad54ff98f3c/toolkit/modules/ProfileAge.sys.mjs): "
                 "when created is missing and the profile's creation time is asked for (lines 85-98), it "
                 "stores the oldest timestamp among the files in the profile folder at that moment, using "
                 "the file creation time where the platform has one and the modification time otherwise "
                 "(lines 13-45 and 136-145), and when firstUse is null it stores the current time (lines "
                 "59-62). Android builds were not decompiled, so whether they reach that code is not "
                 "established. Created is the created value read as milliseconds since 1970 UTC and shown "
                 "to the second. On all 12 tested profiles it was within one second of the oldest "
                 "modification time, in UTC, among the profile folder's files in the image (the file "
                 "times were 0.1 to 1.0 seconds earlier), and that oldest file was times.json itself. It "
                 "is not established as the time the app was installed or first opened. First Use (as "
                 "stored) is the firstUse value: it was null on every tested profile that had the key and "
                 "absent on pixel3_a11. Other Keys (as stored) lists any further keys, such as reset or "
                 "recoveredFromBackup, which ProfileAge writes; none were present on the tested images. "
                 "App Package is the folder the profile sits in, so a Firefox fork with its own package "
                 "name is reported under that name; on the tested images the packages were "
                 "org.mozilla.firefox and org.torproject.torbrowser. Android User is the user whose "
                 "storage holds the file, and the duplicate storage views of one file (data/data, "
                 "data/user/0, data_mirror) are read once: the 20 tested files gave 12 rows, two of them "
                 "for Android user 10.",
        "paths": ('*/files/mozilla/*/times.json',),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "cookbook_a11": "Android 11 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | 1 row",
            "hc_pixel8pro_a17": "Android 17 | 1 row",
            "hickman_a13": "Android 13 | 2 rows",
            "pixel3_a11": "Android 11 | 2 rows",
            "pixel3_a12": "Android 12 | 2 rows",
            "pixel7a_a14": "Android 14 | 1 row",
            "russell_a14": "Android 14 | 1 row",
            "russell_pixel6a_a13": "Android 13 | 1 row",
        },
    }
}

import json
import re

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, logfunc
from scripts.artifacts.storagePathViews import user_files

_PROFILE = re.compile(r'/([^/]+)/files/mozilla/([^/]+)/times\.json$')


def _ms(value):
    """Milliseconds since 1970 as a UTC datetime; blank for anything else."""
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        return ''
    return convert_unix_ts_to_utc(value / 1000)


def _as_stored(value):
    if value is None:
        return 'null'
    return json.dumps(value) if not isinstance(value, str) else value


@artifact_processor
def mozillaProfileTimes(context):
    data_headers = (('Created', 'datetime'), 'First Use (as stored)', 'App Package', 'Profile Folder',
                    'Other Keys (as stored)', 'Android User', 'Source File')
    data_list, read = [], []
    for path, user in user_files(context, 'times.json'):
        relative = context.get_relative_path(path).replace('\\', '/')
        match = _PROFILE.search('/' + relative.lstrip('/'))
        if not match:
            continue
        try:
            with open(path, 'r', encoding='utf-8') as handle:
                times = json.load(handle)
        except (OSError, ValueError, UnicodeDecodeError) as error:
            logfunc(f'Mozilla Browser Profile Times: {relative} not read: {type(error).__name__}')
            continue
        if not isinstance(times, dict):
            continue
        read.append(path)
        other = {key: value for key, value in times.items() if key not in ('created', 'firstUse')}
        data_list.append((
            _ms(times.get('created')), _as_stored(times['firstUse']) if 'firstUse' in times else '',
            match.group(1), match.group(2), json.dumps(other, sort_keys=True) if other else '', user, relative))
    data_list.sort(key=lambda row: str(row[0]))
    return data_headers, data_list, '\n'.join(read)
