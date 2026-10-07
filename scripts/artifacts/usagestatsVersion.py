__artifacts_v2__ = {
    "usagestatsVersion": {
        "name": "OS Version",
        "description": "Extracts OS Version from Usagestats",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2021-04-15",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Device Information",
        "notes": "Only the first version file the search returns is read. Each line is stripped "
                 "and split on ';'; fewer than three fields produce no row. The first three "
                 "positions match the build fingerprint AOSP writes: Build.VERSION.RELEASE, "
                 "Build.VERSION.CODENAME and Build.VERSION.INCREMENTAL "
                 "(UsageStatsDatabase.getBuildFingerprint, frameworks/base "
                 "services/usage/java/com/android/server/usage/UsageStatsDatabase.java at "
                 "android-14.0.0_r1, lines 426 to 430). Additional positions are reported as "
                 "Field N (as stored), including empty split tokens, without assigning meaning. "
                 "Values retain the existing whole-line whitespace trimming, so these tokens "
                 "are not a lossless representation of the original file bytes.",
        "paths": ('*/system/usagestats/*/version', '*/system_ce/*/usagestats/version'),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "chart-bar",
        "sample_data": {
            "anne_a15": "Android 15 | 5 rows",
            "galaxys10_a10": "Android 10 | 4 rows",
            "hc_pixel8pro_a16": "Android 16 | 3 rows",
            "kevin_pocox7_a15": "Android 15 | 3 rows",
            "pixel7a_a14": "Android 14 | 3 rows",
            "samsunga53_a14": "Android 14 | 5 rows",
            "samsungs20_a13": "Android 13 | 4 rows",
            "sharon_a14": "Android 14 | 4 rows",
            "russell_pixel6a_a13": "Android 13 | 3 rows",
            "userb2_a13": "Android 13 | 3 rows",
        }
    }
}


import scripts.artifacts.artGlobals
from scripts.ilapfuncs import artifact_processor, \
    get_file_path, get_txt_file_content, \
    logfunc, device_info


@artifact_processor
def usagestatsVersion(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "version")
    data_list = []

    text_file = get_txt_file_content(source_path)
    for line in text_file:
        splits = line.strip().split(';')
        totalvalues = len(splits)
        if totalvalues >= 3:
            device_info("Usagestats", "Android version", splits[0])
            logfunc(f"Android version {str(splits[0])}")
            scripts.artifacts.artGlobals.versionf = splits[0]
            data_list.append(('Android Version', splits[0]))
            
            device_info("Usagestats", "Codename", splits[1])
            data_list.append(('Codename', splits[1]))
            
            device_info("Usagestats", "Build version", splits[2])
            data_list.append(('Build version', splits[2]))

        for position, value in enumerate(splits[3:], start=4):
            data_list.append((f'Field {position} (as stored)', value))

    data_headers = ('Property', 'Property Value')
    return data_headers, data_list, source_path
