__artifacts_v2__ = {
    "get_build": {
        "name": "Build",
        "description": "Parses device build properties (key and value) from the vendor "
                       "and system build.prop files. When both files are present the "
                       "vendor values are reported.",
        "author": "@abrignoni",
        "creation_date": "2020-03-30",
        "last_update_date": "2026-07-30",
        "requirements": "none",
        "category": "Device Information",
        "notes": "",
        "paths": ('*/vendor/build.prop', '*/system/build.prop'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "info-circle",
        "sample_data": {
            "anne_a15": "Android 15 | 0 rows",
            "galaxys10_a10": "Android 10 | 7 rows",
            "hc_pixel8pro_a16": "Android 16 | 7 rows",
            "pixel7a_a14": "Android 14 | 7 rows",
            "samsunga53_a14": "Android 14 | 7 rows",
            "sharon_a14": "Android 14 | 7 rows",
            "russell_pixel6a_a13": "Android 13 | 7 rows",
        },
    }
}

import scripts.artifacts.artGlobals

from scripts.ilapfuncs import artifact_processor, logfunc, logdevinfo

# prop key -> report label. The vendor build.prop uses the ro.*vendor* keys; the
# system build.prop carries ro.product.system.* plus the unqualified legacy
# ro.build.version.* keys.
BUILD_PROPS = {
    'ro.product.vendor.manufacturer': 'Manufacturer',
    'ro.product.system.manufacturer': 'Manufacturer',
    'ro.product.vendor.brand': 'Brand',
    'ro.product.system.brand': 'Brand',
    'ro.product.vendor.model': 'Model',
    'ro.product.system.model': 'Model',
    'ro.product.vendor.device': 'Device',
    'ro.product.system.device': 'Device',
    'ro.vendor.build.version.release': 'Android Version',
    'ro.build.version.release': 'Android Version',
    'ro.vendor.build.version.sdk': 'SDK',
    'ro.build.version.sdk': 'SDK',
    'ro.system.build.version.release': 'Version Release',
}

# labels whose device info entry keeps its historical wording
DEVINFO_TEXT = {
    'Android Version': 'Android version per build.props',
    'Version Release': 'Version release',
}


@artifact_processor
def get_build(context):
    files_found = [str(x) for x in context.get_files_found()]
    # vendor/build.prop first so its values win over system/build.prop duplicates
    files_found.sort(key=lambda p: 0 if p.replace('\\', '/').endswith('/vendor/build.prop') else 1)

    data_list = []
    seen_labels = set()
    source_path = ''

    for file_found in files_found:
        with open(file_found, "r", encoding='utf-8', errors='replace') as f:
            for line in f:
                key, sep, value = line.strip().partition('=')
                label = BUILD_PROPS.get(key)
                if not sep or label is None or label in seen_labels:
                    continue
                seen_labels.add(label)
                data_list.append((label, value))
                if not source_path:
                    source_path = file_found
                if label == 'Android Version':
                    if scripts.artifacts.artGlobals.versionf == 0:
                        scripts.artifacts.artGlobals.versionf = value
                    logfunc(f"Android version per build.props: {value}")
                logdevinfo(f"<b>{DEVINFO_TEXT.get(label, label)}: </b>{value}")

    if not source_path:
        source_path = files_found[0]

    data_headers = ('Key', 'Value')
    return data_headers, data_list, source_path
