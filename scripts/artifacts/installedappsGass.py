__artifacts_v2__ = {
    "get_installedappsGass": {
        "name": "installedappsGass",
        "description": "Parses application records (bundle ID, version code and SHA-256 hash) from the app_info table of each Google Play services gass.db.",
        "author": "@abrignoni",
        "creation_date": "2020-03-01",
        "last_update_date": "2026-09-12",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "Reads each gass.db found under com.google.android.gms, including a second Android "
                 "user's, and takes one copy where one user's database appears under more than one of "
                 "the data/data, data/user/N and data_mirror/data_ce/null/N paths. The User column is "
                 "read from those directories: data/data gives 0 and the other two give N. "
                 "Reference: AOSP, 'create_data_user_ce_path', "
                 "https://android.googlesource.com/platform/frameworks/native/+/2827a4a16b0340ecd07c2d5a6c89991799b362bb/cmds/installd/utils.cpp#180 "
                 "Reference: AOSP, 'InstalldNativeService::tryMountDataMirror', "
                 "https://android.googlesource.com/platform/frameworks/native/+/2827a4a16b0340ecd07c2d5a6c89991799b362bb/cmds/installd/InstalldNativeService.cpp#3787 "
                 "On samsungs20_a13 the two databases sit under Volumes/userdata/data and "
                 "Volumes/userdata/user/150, which are read the same way. The column is blank where "
                 "the path shows none of these directories, which no tested image did. The report's "
                 "'located at' line lists every database read, including any that returned no rows. "
                 "Each row is a distinct package name, version code and SHA-256 hash from one "
                 "database's app_info table, so a package recorded under several version codes has a "
                 "row for each: on hc_pixel8pro_a16 the 696 rows hold 107 distinct package names. A "
                 "version code in this table can differ from the one data/system/packages.list gives: "
                 "on hc_pixel8pro_a16 the table's only row for com.google.android.gms has 253830035 "
                 "and packages.list gives 262031035. Whether an application was still installed at "
                 "the time of extraction is not established by its rows here.",
        "paths": ('*/com.google.android.gms/databases/gass.db*',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "package",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.gms | 408 rows",
            "galaxys10_a10": "Android 10 | com.google.android.gms vc 210915037 | 81 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.gms vc 262031035 | 696 rows",
            "kevin_pocox7_a15": "Android 15 | com.google.android.gms | 1310 rows",
            "pixel7a_a14": "Android 14 | com.google.android.gms vc 242632038 | 214 rows",
            "samsunga53_a14": "Android 14 | com.google.android.gms | 101 rows",
            "samsungs20_a13": "Android 13 | com.google.android.gms | 185 rows",
            "sharon_a14": "Android 14 | com.google.android.gms vc 243137039 | 1585 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.gms vc 232316044 | 382 rows",
            "userb2_a13": "Android 13 | com.google.android.gms | 171 rows",
            "cookbook_a11": "Android 11 | com.google.android.gms vc 242835031 | 210 rows",
            "emu_a15_oss2_v3": "Android 15 | com.google.android.gms vc 242335038 | 8 rows",
            "pixel3_a12": "Android 12 | com.google.android.gms vc 214516044 | 135 rows",
            "russell_a14": "Android 14 | com.google.android.gms vc 243233038 | 2874 rows",
        },
    }
}

import re

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly
from scripts.artifacts.storagePathViews import unique_files

# The Android user whose app data directory holds the database, read from the directories
# directly above the package directory: data/data is user 0, and data/user/N and
# data_mirror/data_ce/<volume>/N are user N. A userdata directory in place of the first
# data, as on samsungs20_a13, reads the same way. Any other path leaves the user blank.
_USER_DIR = re.compile(
    r'(?:^|/)(?:(?:user)?data/(?:data|user/(\d+))|data_mirror/data_ce/[^/]+/(\d+))'
    r'/com\.google\.android\.gms/databases/gass\.db$')


def _android_user(relative_path):
    match = _USER_DIR.search(str(relative_path).replace('\\', '/'))
    if not match:
        return ''
    return match.group(1) or match.group(2) or '0'


@artifact_processor
def get_installedappsGass(context):
    data_list = []
    source_paths = []

    for file_found in unique_files(context):
        file_found = str(file_found)
        if not file_found.endswith('.db'):
            continue

        source_paths.append(file_found)
        usernum = _android_user(context.get_relative_path(file_found))

        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
            SELECT distinct(package_name), version_code, digest_sha256
            FROM app_info
        ''')
        all_rows = cursor.fetchall()
        db.close()

        for row in all_rows:
            data_list.append((usernum, row[0], row[1], row[2]))

    data_headers = ('User', 'Bundle ID', 'Version Code', 'SHA-256 Hash')
    return data_headers, data_list, '\n'.join(source_paths)
