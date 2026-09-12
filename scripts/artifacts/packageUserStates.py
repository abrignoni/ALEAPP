__artifacts_v2__ = {
    "package_user_states_orphaned": {
        "name": "Orphaned Package User States",
        "description": "Legacy domain verification user states in packages.xml that name a "
                       "package with no package record left in the same file.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "A row is a user-states element in packages.xml whose packageName has no package and no "
                 "updated-package record left in the same file. On every tested image those elements sit "
                 "in the domain-verifications-legacy section, and the search is not anchored to it. One "
                 "row per package name, Android user and stored state, so a row count is not a count of "
                 "packages: on one tested image 69 such package names produced 135 rows because most "
                 "were recorded for two Android users.\n"
                 "The section belongs to the platform's legacy domain verification store. Reference: "
                 "Android Open Source Project, DomainVerificationLegacySettings.java, in "
                 "frameworks/base/services/core/java/com/android/server/pm/verify/domain at commit "
                 "e55b8eeb28debdb2db618e6732d17a9e558ef704, which defines the tag and attribute names at "
                 "lines 49 to 54 and writes one user-states section per stored entry in writeSettings at "
                 "line 121. Read from that source and not exercised on a device by this work: the entry "
                 "can outlive the package record because remove at line 98 marks an entry attached and "
                 "returns its info without deleting it from the map writeSettings iterates, and "
                 "readSettings loads every entry back when the store is read.\n"
                 "A row is therefore evidence that the package name was recorded in this store on the "
                 "device. The absence of a row is not evidence that a package was never present. "
                 "writeSettings skips an entry that holds no per-user state, so a package the legacy "
                 "store never recorded state for has no element whether or not its record was later "
                 "removed. Measured on an Android 15 emulator on 2026-09-06: of four packages that had "
                 "been uninstalled from that device, three left an element and the fourth had none "
                 "either before or after the removal, and the reason for the difference was not "
                 "established. Nothing in the element carries a timestamp, so this artifact does not "
                 "report when a package record was removed.\n"
                 "Measured across the 39 registered Android corpora on 2026-09-06: 15 reported rows, 21 "
                 "carried a packages.xml and reported none, and 3 carried no packages.xml at all. The "
                 "rows held 285 distinct package names. 159 of those are versioned "
                 "com.google.android.trichromelibrary packages, and most of the remaining 126 "
                 "carry platform, vendor or resource overlay package name prefixes. Third party "
                 "application packages also "
                 "appear: 21 of the 285 names carry neither a platform nor a vendor prefix, and they are "
                 "the reason to read the table.\n"
                 "Legacy Domain Verification State is the stored state integer with the platform's label "
                 "where it has one, from "
                 "PackageManager.INTENT_FILTER_DOMAIN_VERIFICATION_STATUS_UNDEFINED, _ASK, _ALWAYS, "
                 "_NEVER and _ALWAYS_ASK, the values DomainVerificationService switches on in "
                 "approvalLevelForDomainInternal. It was Undefined (0) on every one of the 19,985 "
                 "user-state elements read across the tested images, orphaned and not, so it is uniform "
                 "in this data and is kept because it is part of the stored record. Android User is the "
                 "userId attribute; it is a single value on an image with one Android user, and 3 of the "
                 "15 images that reported rows carried more than one, one of them splitting 69 rows to "
                 "user 0 and 66 rows to user 10.\n"
                 "Both packages.xml and its packages.xml.reservecopy are read, and a package, user and "
                 "state carried by both produces one row naming both files, which was 381 of the 457 "
                 "rows. On the tested images the reserve copy carried no package name the live file did "
                 "not, so it adds no rows. It is also a fallback: on an input built from a readable "
                 "reserve copy beside an unreadable live file, the rows were read from the reserve copy "
                 "and cite it alone. Samsung devices also keep older snapshots of packages.xml under "
                 "system/pm_backup_files/pm_settings_backup/backup_item_*/packages.xml. This artifact "
                 "does not read them, because across the tested images they held no orphaned package "
                 "name the live file did not already carry, and reading them would repeat each row three "
                 "to five times on the images that carry them. An examiner wanting the snapshots can "
                 "read them at that path.\n"
                 "This element lives in packages.xml, and the per-user package-restrictions.xml files "
                 "are a different store that does not carry it: checked on three tested images carrying "
                 "8, 69 and 111 orphaned package names, they named none of them among the 407, 383 and "
                 "541 packages they list. That is a statement about those two files only, not about what "
                 "other stores keep.\n"
                 "An image with no rows can mean the section is empty rather than that nothing was "
                 "removed. The three tested Android 10 and 11 images carry no user-states element at "
                 "all, and so do ten Android 15 emulator images whose later captures do carry them, so "
                 "an empty section is not by itself a statement about the release. A file that is "
                 "neither ABX nor plain XML is logged by name and skipped; one tested image stores "
                 "several archive members at the packages.xml path, some of them encrypted, and the copy "
                 "the seeker stages there does not parse, so that image reports no rows while its "
                 "readable copy holds four.",
        "paths": ('*/system/packages.xml', '*/system/packages.xml.reservecopy'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "package",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 8 rows",
            "anne_a15": "Android 15 | 35 rows",
            "cookbook_a11": "Android 11 | 0 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 0 rows",
            "emu_a15_oss_v10": "Android 15 | 0 rows",
            "emu_a15_oss_v11": "Android 15 | 0 rows",
            "emu_a15_oss_v12": "Android 15 | 0 rows",
            "emu_a15_oss_v13": "Android 15 | 0 rows",
            "emu_a15_oss_v14": "Android 15 | 0 rows",
            "emu_a15_oss_v15": "Android 15 | 0 rows",
            "emu_a15_oss_v16": "Android 15 | 0 rows",
            "emu_a15_oss_v17": "Android 15 | 4 rows",
            "emu_a15_oss_v2": "Android 15 | 0 rows",
            "emu_a15_oss_v3": "Android 15 | 0 rows",
            "emu_a15_oss_v4": "Android 15 | 0 rows",
            "emu_a15_oss_v5": "Android 15 | 0 rows",
            "emu_a15_oss_v6": "Android 15 | 0 rows",
            "emu_a15_oss_v7": "Android 15 | 0 rows",
            "emu_a15_oss_v8": "Android 15 | 0 rows",
            "emu_a15_oss_v9": "Android 15 | 0 rows",
            "falken_a326u_a13": "Android 13 | 3 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 23 rows",
            "hc_pixel8pro_a17": "Android 17 | 32 rows",
            "hc_pixel8pro_a17_ail": "0 rows",
            "kevin_pocox7_a15": "Android 15 | 33 rows",
            "pixel3_a11": "Android 11 | 0 rows",
            "pixel3_a12": "Android 12 | 2 rows",
            "pixel7a_a14": "Android 14 | 8 rows",
            "russell_a14": "Android 14 | 135 rows",
            "russell_pixel6a_a13": "Android 13 | 13 rows",
            "s20fe_a13": "Android 13 | 18 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 26 rows",
            "sharon_a14": "Android 14 | 111 rows",
            "userb2_a13": "Android 13 | 6 rows",
        },
    },
}

import os
import pathlib
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import abxread, artifact_processor, checkabx, logfunc

# PackageManager.INTENT_FILTER_DOMAIN_VERIFICATION_STATUS_*, the vocabulary the platform
# branches on in DomainVerificationService.approvalLevelForDomainInternal. Values outside it are reported
# as stored.
_STATE_NAMES = {
    '0': 'Undefined',
    '1': 'Ask',
    '2': 'Always',
    '3': 'Never',
    '4': 'Always ask',
}


def _root(path):
    """The XML root, reading ABX binary XML or plain XML, and tolerating a file that carries
    more than one root element."""
    if checkabx(path):
        try:
            return abxread(path, False).getroot()
        except Exception:  # pylint: disable=broad-except
            return abxread(path, True).getroot()
    try:
        return ET.parse(path).getroot()
    except ET.ParseError:
        text = pathlib.Path(path).read_text(encoding='utf-8', errors='replace')
        if text.lstrip().startswith('<?xml'):
            text = text.split('?>', 1)[1]
        return ET.fromstring(f'<root>{text}</root>')


def _known_package_names(root):
    """Every package name the file still carries a record for. package is an installed
    package and updated-package is the system copy a data-partition update superseded. A
    shared-user name is a shared user id rather than a package and is not included."""
    names = set()
    for tag in ('package', 'updated-package'):
        for element in root.iter(tag):
            name = element.get('name')
            if name:
                names.add(name)
    return names


def _state_label(value):
    text = '' if value is None else str(value).strip()
    if not text:
        return ''
    name = _STATE_NAMES.get(text)
    return f'{name} ({text})' if name else text


@artifact_processor
def package_user_states_orphaned(context):
    data_headers = (
        'Package Name',
        'Android User',
        'Legacy Domain Verification State',
        'Source File',
    )
    # (package, user, state) -> list of relative source paths carrying it. Keyed this way so
    # the reserve copy repeating the live file costs no extra row, while a disagreement in
    # the stored state still produces its own row.
    rows = {}
    sources = []

    # A path can be handed over more than once: one tested image carries several archive
    # members at the same path, which the seeker stages to one file.
    for file_found in sorted({str(f) for f in context.get_files_found()}):
        if os.path.isdir(file_found):
            continue
        if os.path.basename(file_found) not in ('packages.xml', 'packages.xml.reservecopy'):
            continue
        try:
            root = _root(file_found)
        except Exception as error:  # pylint: disable=broad-except
            logfunc(f'Orphaned Package User States: could not read {os.path.basename(file_found)}: {error}')
            continue

        known = _known_package_names(root)
        relative = context.get_relative_path(file_found)
        found_here = 0
        for user_states in root.iter('user-states'):
            package_name = user_states.get('packageName')
            if not package_name or package_name in known:
                continue
            for user_state in user_states.iter('user-state'):
                key = (package_name,
                       user_state.get('userId', ''),
                       _state_label(user_state.get('state')))
                rows.setdefault(key, [])
                if relative not in rows[key]:
                    rows[key].append(relative)
                found_here += 1
        if found_here:
            sources.append(file_found)

    data_list = [(package_name, user_id, state, ', '.join(paths))
                 for (package_name, user_id, state), paths in sorted(rows.items())]

    return data_headers, data_list, '\n'.join(sources)
