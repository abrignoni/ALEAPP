__artifacts_v2__ = {
    "package_dex_usage_list_cross_package": {
        "name": "Dex Usage (Legacy) - Cross-Package Code Loads",
        "description": "Primary code files one package loaded from another package's installation, read from "
         "the platform's text format dex use store, which records no times.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Android System",
        "notes": "Read from the platform's dex use store at /data/system/package-dex-usage.list. "
         "Reference: Android Open Source Project, "
         "frameworks/base/services/core/java/com/android/server/pm/dex/PackageDexUsage.java, "
         "whose constructor names the file and whose base class AbstractStatsBase.getFile() "
         "places it under Environment.getDataDirectory()/system. The grammar here was read from "
         "that class's write() and read() methods at android-13.0.0_r1, where the file is byte "
         "identical to android-12.0.0_r1, android-14.0.0_r1 and android-15.0.0_r1; "
         "android-10.0.0_r1 and android-11.0.0_r1 differ elsewhere in the class but emit the "
         "same lines. The file is a header line naming the format version, then for each package "
         "a line holding the package name, a \"+\" line for each primary code path followed by an "
         "\"@\" line listing the packages that loaded it, and a \"#\" line for each secondary dex "
         "file followed by a line of Android user, used-by-other-apps flag and instruction sets, "
         "an \"@\" line, and a class loader context line. The four lines of a \"#\" block are read "
         "in the order write() emits them; the comment inside read() lists them in a different "
         "order, and this artifact follows the code rather than that comment, which every store "
         "read here confirms. PACKAGE_DEX_USAGE_VERSION is 2, which the class's own comment "
         "dates to Oreo with version 1 support dropped in R, and every store read here carried "
         "version 2. Version 1 is a different grammar, so a file declaring any other version is "
         "logged and skipped rather than read with these rules. This artifact reports the \"+\" "
         "primary code path records, which are installed APKs and their splits, one row for each "
         "code path and loading package. The store does not record a package loading its own "
         "primary code: DexManager.notifyDexLoadInternal skips the record when the file is a "
         "primary or split APK and the loading package equals the owning package, an exemption "
         "that is unconditional at android-10.0.0_r1 and gated on the platform package \"android\" "
         "from android-11.0.0_r1. The store therefore has no equivalent of the protobuf store's "
         "app's-own-code rows, and this artifact is the whole of the primary side. 1 row of the "
         "1058 read here shows the same package in both columns, and that is the isolated "
         "process case described below, where the platform had recorded the loader under a name "
         "that differed from the owning package. 18 rows of the 1058 carry a blank Loading "
         "Package. Those are code paths whose recorded loaders have all been removed: from "
         "android-11.0.0_r1 PackageDexUsage.syncData drops a loading package that is no longer "
         "installed while keeping the code path, and DexManager.loadInternal calls syncData at "
         "every boot. The android-10.0.0_r1 syncData does not prune loading packages at all and "
         "reaches an empty list only by propagating a pre-upgrade used-by-other-apps flag onto a "
         "code path with no loader named. They are reported with the column blank rather than "
         "dropped, and a blank there is not evidence that nothing loaded the file. Isolated "
         "Process is true when the recorded loading package carried DexManager's "
         "ISOLATED_PROCESS_PACKAGE_SUFFIX \"..isolated\", which the platform appends so that a "
         "load from an isolated process counts as coming from a different package; the Loading "
         "Package column reports the name without that suffix. The suffix was added at "
         "android-12.0.0_r1 and is absent from android-10.0.0_r1 and android-11.0.0_r1. It was "
         "set on 1 row of the 1058 read here, and that row is the only one whose loading package "
         "equals its owning package once the suffix is removed. One package loading another's "
         "code is ordinary platform behaviour more often than not: 477 of the 1058 rows name "
         "Google Play services as the owning package and 140 the Android System WebView, which "
         "apps load to render web content, so the row worth attention is an unexpected pairing "
         "rather than the presence of pairings. 662 of the rows load a file under /data and 396 "
         "a platform path under /apex, /product, /system, /system_ext. The format records no "
         "time. There is no timestamp field anywhere in the writer, so a row records that a load "
         "happened at some point before the file was last written and says nothing about when. "
         "That is the difference from the protobuf store at /data/system/package-dex-usage.pb "
         "that replaces it, whose records each carry a last_used_at_ms. Only the file's own "
         "modification time bounds the store, and it bounds the whole file rather than any row. "
         "The platform writes through AbstractStatsBase.maybeWriteAsync, whose WRITE_INTERVAL_MS "
         "leaves at least 30 minutes between background writes on a production build, so a load "
         "in the last half hour before acquisition can be absent. An entry does not outlive the "
         "package it names. PackageDexUsage.syncData removes the record of an owning package "
         "that is no longer installed, removes secondary dex entries for a user that no longer "
         "exists, removes a code path the owning package no longer declares, and removes the "
         "whole package record once nothing is left; DexManager.loadInternal calls it at every "
         "boot. From android-11.0.0_r1 it passes an empty list of packages to keep data about, "
         "and android-10.0.0_r1 has no such parameter, so nothing is exempted on either. That is "
         "read from the source and was not exercised against a device here, so a name present is "
         "evidence the package was installed at the last boot rather than at acquisition, and a "
         "name absent is not evidence the package was never installed. Across the 39 registered "
         "Android corpora the file is populated on 13 images, which report Android 10, 11, 12, "
         "13 and 14. 4 images reporting Android 14 and 15 carry it reduced to its 38 byte header "
         "line, and it is absent from 17 Android 15 emulator images and 2 images reporting "
         "Android 16 and 17. The remaining 3 corpora are extractions that carry no /data/system "
         "content at all rather than devices without the store, which was checked by listing "
         "their members. The store is not simply superseded at Android 14: "
         "DexManager.notifyDexLoadInternal still calls PackageDexUsage.record at "
         "android-14.0.0_r1, and 2 of the images reporting Android 14 carry a populated file "
         "whose recorded modification time is within days of the extraction. Why the file stops "
         "being maintained on some Android 14 and 15 devices and not others was not established "
         "here, and because the format carries no times it cannot be settled from the file "
         "itself. One set of rows is reported per store found, each row carrying its own Source "
         "File, so an extraction holding the folder under more than one root reports each copy "
         "rather than merging them; every corpus read here held exactly one copy, and the "
         "two-copy case was exercised on a constructed tree. The path pattern is not anchored on "
         "a data/ prefix, so a raw userdata partition image that carries system/ at its root is "
         "matched as well, which is how one of the images read here is laid out. A file matching "
         "the pattern that does not begin with the format's header line is logged and not read. "
         "The two Dex Usage (Legacy) artifacts partition the file without overlap: this one and "
         "Secondary Dex Loads. Every line of the file is reported across them.",
        "paths": ('*/system/package-dex-usage.list',),
        "output_types": "standard",
        "artifact_icon": "share-2",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 99 rows",
            "anne_a15": "Android 15 | 0 rows",
            "cookbook_a11": "Android 11 | 108 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 0 rows",
            "emu_a15_oss_v10": "Android 15 | 0 rows",
            "emu_a15_oss_v11": "Android 15 | 0 rows",
            "emu_a15_oss_v12": "Android 15 | 0 rows",
            "emu_a15_oss_v13": "Android 15 | 0 rows",
            "emu_a15_oss_v14": "Android 15 | 0 rows",
            "emu_a15_oss_v15": "Android 15 | 0 rows",
            "emu_a15_oss_v16": "Android 15 | 0 rows",
            "emu_a15_oss_v17": "Android 15 | 0 rows",
            "emu_a15_oss_v2": "Android 15 | 0 rows",
            "emu_a15_oss_v3": "Android 15 | 0 rows",
            "emu_a15_oss_v4": "Android 15 | 0 rows",
            "emu_a15_oss_v5": "Android 15 | 0 rows",
            "emu_a15_oss_v6": "Android 15 | 0 rows",
            "emu_a15_oss_v7": "Android 15 | 0 rows",
            "emu_a15_oss_v8": "Android 15 | 0 rows",
            "emu_a15_oss_v9": "Android 15 | 0 rows",
            "falken_a326u_a13": "Android 13 | 105 rows",
            "galaxys10_a10": "Android 10 | 79 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "hc_pixel8pro_a17_ail": "0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "pixel3_a11": "Android 11 | 90 rows",
            "pixel3_a12": "Android 12 | 95 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "russell_a14": "Android 14 | 22 rows",
            "russell_pixel6a_a13": "Android 13 | 63 rows",
            "s20fe_a13": "Android 13 | 94 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 119 rows",
            "sharon_a13": "Android 13 | 64 rows",
            "sharon_a14": "Android 14 | 35 rows",
            "userb2_a13": "Android 13 | 85 rows",
        },
    },
    "package_dex_usage_list_secondary": {
        "name": "Dex Usage (Legacy) - Secondary Dex Loads",
        "description": "Dex and jar files a package loaded from outside its own installation, with the Android "
         "user, instruction sets and class loader context as stored, and no times.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-06",
        "last_update_date": "2026-09-06",
        "requirements": "none",
        "category": "Android System",
        "notes": "Read from the platform's dex use store at /data/system/package-dex-usage.list. "
         "Reference: Android Open Source Project, "
         "frameworks/base/services/core/java/com/android/server/pm/dex/PackageDexUsage.java, "
         "whose constructor names the file and whose base class AbstractStatsBase.getFile() "
         "places it under Environment.getDataDirectory()/system. The grammar here was read from "
         "that class's write() and read() methods at android-13.0.0_r1, where the file is byte "
         "identical to android-12.0.0_r1, android-14.0.0_r1 and android-15.0.0_r1; "
         "android-10.0.0_r1 and android-11.0.0_r1 differ elsewhere in the class but emit the "
         "same lines. The file is a header line naming the format version, then for each package "
         "a line holding the package name, a \"+\" line for each primary code path followed by an "
         "\"@\" line listing the packages that loaded it, and a \"#\" line for each secondary dex "
         "file followed by a line of Android user, used-by-other-apps flag and instruction sets, "
         "an \"@\" line, and a class loader context line. The four lines of a \"#\" block are read "
         "in the order write() emits them; the comment inside read() lists them in a different "
         "order, and this artifact follows the code rather than that comment, which every store "
         "read here confirms. PACKAGE_DEX_USAGE_VERSION is 2, which the class's own comment "
         "dates to Oreo with version 1 support dropped in R, and every store read here carried "
         "version 2. Version 1 is a different grammar, so a file declaring any other version is "
         "logged and skipped rather than read with these rules. This artifact reports the \"#\" "
         "secondary dex records, one row for each dex or jar file a package loaded from outside "
         "its own installation. Android User is the owner user id the platform recorded; it was "
         "0 on 1114 of the 1227 rows read here and named a second Android user on 113, so the "
         "column separates a second Android user's records from the first user's. Also "
         "Loaded By "
         "lists the packages on the record's \"@\" line, which excludes the owning package by "
         "construction, because PackageDexUsage.maybeAddLoadingPackage adds a loading package "
         "only when it differs from the owner. An empty Also Loaded By therefore means only the "
         "owning package was recorded as loading the file, not that nothing loaded it; 134 of "
         "the 1227 rows name another package. The record also carries a used-by-other-apps flag, "
         "which PackageDexUsage.writeBoolean writes as 1 or 0. It is not reported as its own "
         "column: the writer sets it from the same comparison that decides whether a loader is "
         "added, and on all 1227 rows read here it was true exactly when Also Loaded By is not "
         "empty, so a separate column would repeat that one. Instruction Sets holds the "
         "instruction sets the platform recorded for the load, arm64 on 1221 rows and arm on 19 "
         "rows. Class Loader Context is the encoding as stored; \"=VariableClassLoaderContext=\" "
         "is the marker PackageDexUsage.VARIABLE_CLASS_LOADER_CONTEXT writes when a file was "
         "loaded under more than one context, and it was the value on 225 of the 1227 rows, so "
         "on those rows the column names no classpath. The platform caps a package at "
         "MAX_SECONDARY_FILES_PER_OWNER, 100 secondary dex files, and that cap is reached in "
         "this data: com.samsung.android.app.routines holds exactly 100 rows on 4 of the images "
         "read here, so for that package the list is truncated by the platform and its absence "
         "of a file is not evidence the file was not loaded. The format records no time. There "
         "is no timestamp field anywhere in the writer, so a row records that a load happened at "
         "some point before the file was last written and says nothing about when. That is the "
         "difference from the protobuf store at /data/system/package-dex-usage.pb that replaces "
         "it, whose records each carry a last_used_at_ms. Only the file's own modification time "
         "bounds the store, and it bounds the whole file rather than any row. The platform "
         "writes through AbstractStatsBase.maybeWriteAsync, whose WRITE_INTERVAL_MS leaves at "
         "least 30 minutes between background writes on a production build, so a load in the "
         "last half hour before acquisition can be absent. An entry does not outlive the package "
         "it names. PackageDexUsage.syncData removes the record of an owning package that is no "
         "longer installed, removes secondary dex entries for a user that no longer exists, "
         "removes a code path the owning package no longer declares, and removes the whole "
         "package record once nothing is left; DexManager.loadInternal calls it at every boot. "
         "From android-11.0.0_r1 it passes an empty list of packages to keep data about, and "
         "android-10.0.0_r1 has no such parameter, so nothing is exempted on either. That is "
         "read from the source and was not exercised against a device here, so a name present is "
         "evidence the package was installed at the last boot rather than at acquisition, and a "
         "name absent is not evidence the package was never installed. Across the 39 registered "
         "Android corpora the file is populated on 13 images, which report Android 10, 11, 12, "
         "13 and 14. 4 images reporting Android 14 and 15 carry it reduced to its 38 byte header "
         "line, and it is absent from 17 Android 15 emulator images and 2 images reporting "
         "Android 16 and 17. The remaining 3 corpora are extractions that carry no /data/system "
         "content at all rather than devices without the store, which was checked by listing "
         "their members. The store is not simply superseded at Android 14: "
         "DexManager.notifyDexLoadInternal still calls PackageDexUsage.record at "
         "android-14.0.0_r1, and 2 of the images reporting Android 14 carry a populated file "
         "whose recorded modification time is within days of the extraction. Why the file stops "
         "being maintained on some Android 14 and 15 devices and not others was not established "
         "here, and because the format carries no times it cannot be settled from the file "
         "itself. One set of rows is reported per store found, each row carrying its own Source "
         "File, so an extraction holding the folder under more than one root reports each copy "
         "rather than merging them; every corpus read here held exactly one copy, and the "
         "two-copy case was exercised on a constructed tree. The path pattern is not anchored on "
         "a data/ prefix, so a raw userdata partition image that carries system/ at its root is "
         "matched as well, which is how one of the images read here is laid out. A file matching "
         "the pattern that does not begin with the format's header line is logged and not read. "
         "The two Dex Usage (Legacy) artifacts partition the file without overlap: this one and "
         "Cross-Package Code Loads. Every line of the file is reported across them.",
        "paths": ('*/system/package-dex-usage.list',),
        "output_types": "standard",
        "artifact_icon": "terminal",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 44 rows",
            "anne_a15": "Android 15 | 0 rows",
            "cookbook_a11": "Android 11 | 32 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 0 rows",
            "emu_a15_oss_v10": "Android 15 | 0 rows",
            "emu_a15_oss_v11": "Android 15 | 0 rows",
            "emu_a15_oss_v12": "Android 15 | 0 rows",
            "emu_a15_oss_v13": "Android 15 | 0 rows",
            "emu_a15_oss_v14": "Android 15 | 0 rows",
            "emu_a15_oss_v15": "Android 15 | 0 rows",
            "emu_a15_oss_v16": "Android 15 | 0 rows",
            "emu_a15_oss_v17": "Android 15 | 0 rows",
            "emu_a15_oss_v2": "Android 15 | 0 rows",
            "emu_a15_oss_v3": "Android 15 | 0 rows",
            "emu_a15_oss_v4": "Android 15 | 0 rows",
            "emu_a15_oss_v5": "Android 15 | 0 rows",
            "emu_a15_oss_v6": "Android 15 | 0 rows",
            "emu_a15_oss_v7": "Android 15 | 0 rows",
            "emu_a15_oss_v8": "Android 15 | 0 rows",
            "emu_a15_oss_v9": "Android 15 | 0 rows",
            "falken_a326u_a13": "Android 13 | 139 rows",
            "galaxys10_a10": "Android 10 | 28 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | 0 rows",
            "hc_pixel8pro_a17_ail": "0 rows",
            "kevin_pocox7_a15": "Android 15 | 0 rows",
            "pixel3_a11": "Android 11 | 67 rows",
            "pixel3_a12": "Android 12 | 95 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "russell_a14": "Android 14 | 105 rows",
            "russell_pixel6a_a13": "Android 13 | 94 rows",
            "s20fe_a13": "Android 13 | 143 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 173 rows",
            "sharon_a13": "Android 13 | 69 rows",
            "sharon_a14": "Android 14 | 173 rows",
            "userb2_a13": "Android 13 | 65 rows",
        },
    },
}

import os

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, logfunc

# The format is the one PackageDexUsage writes, in
# frameworks/base/services/core/java/com/android/server/pm/dex/PackageDexUsage.java.
# Its constructor names the file: super("package-dex-usage.list", ...), and
# AbstractStatsBase.getFile() places it in Environment.getDataDirectory()/system.
# Read at android-13.0.0_r1 and checked byte identical at android-12.0.0_r1,
# android-14.0.0_r1 and android-15.0.0_r1; android-10.0.0_r1 and android-11.0.0_r1
# differ elsewhere in the class but write the same grammar. write() emits:
#
#   PACKAGE_MANAGER__PACKAGE_DEX_USAGE__<version>   header, version 2 since Oreo
#   <owning package name>                           any line with no marker prefix
#   +<primary code path>                            CODE_PATH_LINE_CHAR
#   @<loading package>,<loading package>,...        LOADING_PACKAGE_CHAR, may be bare
#   #<secondary dex path>                           DEX_LINE_CHAR
#   <user id>,<used by other apps>,<isa>,<isa>...   SPLIT_CHAR is ","
#   @<loading package>,...                          may be bare
#   <class loader context>
#
# The four lines of a "#" block are read in the order write() emits them. The comment
# inside read() lists them in a different order and the code below follows the code
# rather than that comment, which the corpus confirms.
_HEADER = 'PACKAGE_MANAGER__PACKAGE_DEX_USAGE__'

# The grammar above is version 2, which PackageDexUsage has written since Oreo. Version 1 is a
# different grammar: its package line is "<name>,<used by other apps>" rather than a bare name,
# it has no "+" code path lines at all (read() throws on one), and its "#" blocks carry neither
# an "@" line nor a class loader context line. Measured on a constructed version 1 file, reading
# one with the rules below yields no records and reports a truncated dex block, because the line
# after a dex data line is the next "#" rather than an "@". So the cost of not checking is not a
# wrong row, it is an empty result attributed to the wrong cause. The version is checked so the
# log says what actually happened.
_SUPPORTED_VERSION = '2'

# DexManager appends this to the loading package name when the load came from an
# isolated process, so that the platform's own "used by other apps" test treats it as a
# different package: DexManager.ISOLATED_PROCESS_PACKAGE_SUFFIX, added in
# android-12.0.0_r1 and absent from android-10.0.0_r1 and android-11.0.0_r1.
_ISOLATED_SUFFIX = '..isolated'

# PackageDexUsage.writeBoolean: "1" true, "0" false. Anything else is reported as stored.
_BOOLEANS = {'0': False, '1': True}


def _boolean(value):
    return _BOOLEANS.get(value, value)


def _loading_packages(line):
    """The packages named on an "@" line, or None when the line is not one.

    A bare "@" is an empty set. PackageDexUsage.syncData() drops a loading package that
    is no longer installed but keeps the code path, so an empty set is a code path whose
    recorded loaders have all been removed."""
    if line is None or not line.startswith('@'):
        return None
    body = line[1:]
    return [package for package in body.split(',') if package] if body else []


def _isolated(package):
    """(package name as the platform would have recorded it, was it an isolated process)."""
    if package.endswith(_ISOLATED_SUFFIX):
        return package[:-len(_ISOLATED_SUFFIX)], True
    return package, False


def _parse(text, path):
    """(primary code path records, secondary dex records) from one store.

    Follows PackageDexUsage.read(): a line starting with "#" opens a four line secondary
    dex block, a line starting with "+" opens a two line primary code path block, and any
    other line names the package that the blocks after it belong to. A block that runs off
    the end of the file, or a dex data line with fewer than the three fields read()
    requires, is logged rather than dropped silently."""
    lines = text.split('\n')
    if lines and lines[-1] == '':
        lines.pop()
    if not lines:
        logfunc(f'Dex usage list is empty: {path}')
        return [], []
    if not lines[0].startswith(_HEADER):
        logfunc(f'Not a dex usage list, unexpected first line: {path}')
        return [], []
    version = lines[0][len(_HEADER):].strip()
    if version != _SUPPORTED_VERSION:
        logfunc(f'Dex usage list format version {version!r} is not the version 2 grammar '
                f'this reads, skipped: {path}')
        return [], []
    primary, secondary = [], []
    package = None
    index = 1
    while index < len(lines):
        line = lines[index]
        index += 1
        if line.startswith('#'):
            if package is None:
                logfunc(f'Dex line before any package line, skipped: {path}')
                continue
            dex_path = line[1:]
            data = lines[index] if index < len(lines) else None
            loaders = _loading_packages(lines[index + 1] if index + 1 < len(lines) else None)
            context_line = lines[index + 2] if index + 2 < len(lines) else None
            index += 3
            if data is None or loaders is None or context_line is None:
                logfunc(f'Truncated dex block for {dex_path}, stopped reading: {path}')
                break
            fields = data.split(',')
            if len(fields) < 3:
                logfunc(f'Short dex data line for {dex_path}, skipped: {path}')
                continue
            secondary.append((package, dex_path, fields[0], _boolean(fields[1]),
                              fields[2:], loaders, context_line))
        elif line.startswith('+'):
            if package is None:
                logfunc(f'Code path line before any package line, skipped: {path}')
                continue
            code_path = line[1:]
            loaders = _loading_packages(lines[index] if index < len(lines) else None)
            index += 1
            if loaders is None:
                logfunc(f'Truncated code path block for {code_path}, stopped reading: {path}')
                break
            primary.append((package, code_path, loaders))
        else:
            package = line
    return primary, secondary


def _stores(context):
    """(path, primary records, secondary records) per store found. Skips are logged."""
    out = []
    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        try:
            with open(file_found, 'r', encoding='utf-8', errors='replace') as handle:
                text = handle.read()
        except OSError as error:
            logfunc(f'Could not read {file_found}: {error}')
            continue
        primary, secondary = _parse(text, file_found)
        out.append((file_found, primary, secondary))
    return out


@artifact_processor
def package_dex_usage_list_cross_package(context):
    data_headers = (
        'Loading Package',
        'Owning Package',
        'Code Path',
        'Isolated Process',
        'Source File',
    )
    data_list = []
    sources = []
    for path, primary, _secondary in _stores(context):
        sources.append(path)
        relative = context.get_relative_path(path)
        for owner, code_path, loaders in primary:
            # A code path whose loaders have all been pruned still records that the code
            # was loaded by something, so it is reported with the loader left blank
            # rather than dropped.
            for loader in loaders or ['']:
                name, isolated = _isolated(loader)
                data_list.append((name, owner, code_path, isolated, relative))
    data_list.sort()
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def package_dex_usage_list_secondary(context):
    data_headers = (
        'Owning Package',
        'Dex File',
        'Android User',
        'Also Loaded By',
        'Instruction Sets',
        'Class Loader Context',
        'Source File',
    )
    data_list = []
    sources = []
    for path, _primary, secondary in _stores(context):
        sources.append(path)
        relative = context.get_relative_path(path)
        for owner, dex_path, user, _used_by_others, isas, loaders, class_loader in secondary:
            names = [_isolated(loader)[0] for loader in loaders]
            data_list.append((owner, dex_path, user, ', '.join(names),
                              ', '.join(isas), class_loader, relative))
    data_list.sort()
    return data_headers, data_list, '\n'.join(sources)
