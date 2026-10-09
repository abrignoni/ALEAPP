__artifacts_v2__ = {
    "get_build": {
        "name": "Build",
        "description": "Parses thirteen named build properties from the vendor and system "
                       "build.prop files and reports each under a label this module assigns "
                       "(Manufacturer, Brand, Model, Device, Android Version, SDK, Version "
                       "Release) with its value. When both files are present the "
                       "vendor values are reported.",
        "author": "@abrignoni",
        "creation_date": "2020-03-30",
        "last_update_date": "2026-10-09",
        "requirements": "none",
        "category": "Device Information",
        "notes": "The Label column holds this module's label, not the stored property key. A "
                 "label is reported once, from the first file and line that carries one of its "
                 "keys, vendor file first. Recognized Build Property Observations lists every "
                 "matching line with its stored key.",
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
    },
    "get_build_property_observations": {
        "name": "Recognized Build Property Observations",
        "description": "Recognized build-property occurrences with stored keys, decoded values and original line bytes.",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-10-06",
        "last_update_date": "2026-10-06",
        "requirements": "none",
        "category": "Device Information",
        "notes": "Uses the original build parser's thirteen recognized property keys. Each matching "
                 "line is retained, including repeated keys and empty values. Property Value uses "
                 "UTF-8 replacement decoding, whole-line trimming and the first '=' separator, "
                 "as the original parser does. Raw Line Hex preserves that original physical line "
                 "including its LF, CRLF or CR terminator. Input Occurrence follows stable "
                 "vendor-first file order; Line Ordinal includes skipped physical lines. These "
                 "ordinals are not timestamps. Repeated paths and aliases remain observations. "
                 "No preferred or authoritative device identity is inferred. Original build "
                 "parser by @abrignoni remains unchanged and retains its vendor-first preference. "
                 "Only contributing sources are listed; Source File appears when multiple "
                 "distinct origins contribute. Unknown property keys are not reported.",
        "paths": ('*/vendor/build.prop', '*/system/build.prop'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "list",
        "sample_data": {
            "pixel7a_a14": "Android 14 | 13 rows",
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
    source_paths = []

    for file_found in files_found:
        with open(file_found, "r", encoding='utf-8', errors='replace') as f:
            for line in f:
                key, sep, value = line.strip().partition('=')
                label = BUILD_PROPS.get(key)
                if not sep or label is None or label in seen_labels:
                    continue
                seen_labels.add(label)
                data_list.append((label, value))
                if file_found not in source_paths:
                    source_paths.append(file_found)
                if label == 'Android Version':
                    if scripts.artifacts.artGlobals.versionf == 0:
                        scripts.artifacts.artGlobals.versionf = value
                    logfunc(f"Android version per build.props: {value}")
                logdevinfo(f"<b>{DEVINFO_TEXT.get(label, label)}: </b>{value}")

    if not source_paths:
        source_paths.append(files_found[0])

    data_headers = ('Label', 'Value')
    return data_headers, data_list, '\n'.join(source_paths)


@artifact_processor
def get_build_property_observations(context):
    import json
    import re

    files_found = [str(path) for path in context.get_files_found()]
    files_found.sort(key=lambda path: 0 if path.replace('\\', '/').endswith('/vendor/build.prop') else 1)
    rows = []
    sources = []
    failed = 0
    for occurrence, path in enumerate(files_found, start=1):
        relative = context.get_relative_path(path)
        try:
            with open(path, 'rb') as handle:
                data = handle.read()
        except OSError:
            failed += 1
            if failed <= 10:
                source = str(relative)
                if source.startswith(('/', '\\')) or re.match(r'^[A-Za-z]:[\\/]', source):
                    source = '[unavailable relative source]'
                escaped = json.dumps(source, ensure_ascii=True)
                escaped = escaped.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')[:240]
                logfunc(f'Build property observations: unreadable input {occurrence}, source {escaped}')
            continue
        for ordinal, match in enumerate(re.finditer(rb'.*?(?:\r\n|\r|\n|$)', data, re.DOTALL), start=1):
            raw = match.group()
            if not raw:
                continue
            key, separator, value = raw.decode('utf-8', errors='replace').strip().partition('=')
            if not separator or key not in BUILD_PROPS:
                continue
            rows.append((key, value, occurrence, ordinal, raw.hex(), relative))
            if relative not in sources:
                sources.append(relative)
    if failed:
        shown = min(failed, 10)
        logfunc(f'Build property observations: unreadable inputs total={failed}, shown={shown}, suppressed={failed-shown}')
    headers = ('Property Key', 'Property Value', 'Input Occurrence', 'Line Ordinal', 'Raw Line Hex')
    if len(sources) > 1:
        headers += ('Source File',)
    else:
        rows = [row[:-1] for row in rows]
    return headers, rows, '\n'.join(sources)
