__artifacts_v2__ = {
    "termux_apt_history": {
        "name": "Termux - Package Install History",
        "description": "Parses the package install and removal history that apt records in the Termux Android environment.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Termux",
        "notes": "One row per apt transaction from files/usr/var/log/apt/history.log, which "
                 "records apt transactions; on the tested image the shipped bootstrap packages "
                 "did not appear in it, only transactions made after setup. Each block carries a "
                 "Start-Date, the Commandline, one or more action lines (Install, Reinstall, "
                 "Upgrade, Downgrade, Remove, Purge) naming the packages and versions, and an "
                 "End-Date. When a block holds more than one action line only the first, in that "
                 "order, is reported in Action and Packages; the others are not shown. The "
                 "Requested By "
                 "column is reported as stored and was blank on the tested image. The timestamps "
                 "are written by apt in the device's local time with no zone stored: on the "
                 "tested emulator image the device time zone was America/New_York and a "
                 "Start-Date of 09:25:54 matched the log file's own modification time of "
                 "09:25:55 at offset -0400, so the value is reported as stored and labelled "
                 "local rather than converted to UTC, because converting a zone-less local time "
                 "as though it were UTC would move every install by the local offset. "
                 "The two columns are declared with the datetime type. For LAVA output a stored "
                 "value with two spaces between the date and the time "
                 "does not parse as an ISO date and is kept as text; a value with a single space "
                 "would be stored as though it were UTC. "
                 "history.log.1 and the numbered or gzipped rotations are read as well where "
                 "present, "
                 "and a gzipped rotation is decompressed in memory. The full set of packages present on the "
                 "device, as opposed to the ones installed later, is in the Installed Packages artifact.",
        "paths": ('*/com.termux/files/usr/var/log/apt/history.log*',),
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "emu_a15_oss_v1": "Android 15 | com.termux vc 1002 | 1 rows",
        },
    },
    "termux_installed_packages": {
        "name": "Termux - Installed Packages",
        "description": "Parses the packages currently installed in the Termux Android client's environment.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Termux",
        "notes": "One row per package from the dpkg status database at files/usr/var/lib/dpkg/status. This is "
                 "the state of the environment at acquisition, the shipped bootstrap packages together with "
                 "anything installed later, and the file carries no install date, so it cannot on its own "
                 "separate the two. The Package Install History artifact is what records which packages were "
                 "installed and when. Package name, version, architecture, the install status, the maintainer "
                 "and the homepage are reported as stored, along with the start of the "
                 "description, up to its first sentence end (this can include text from the long "
                 "description). The "
                 "Essential column shows Yes where a package's Essential field is yes and is blank "
                 "otherwise. Only entries whose "
                 "Status line reports the package as installed are included.",
        "paths": ('*/com.termux/files/usr/var/lib/dpkg/status',),
        "output_types": "standard",
        "artifact_icon": "box",
        "sample_data": {
            "emu_a15_oss_v1": "Android 15 | com.termux vc 1002 | 76 rows",
        },
    },
    "termux_configuration": {
        "name": "Termux - Configuration",
        "description": "Parses the Termux Android client's app preferences and terminal properties.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Termux",
        "notes": "One row per container, combining the app's shared_prefs/com.termux_preferences.xml "
                 "with the non-comment settings in files/home/.termux/termux.properties. The "
                 "preferences file holds a current_session identifier and a log_level; the Terminal "
                 "Properties Set column holds the non-comment settings present in "
                 "termux.properties, and is blank when there are none, as on the tested image. "
                 "Values are reported as stored. Every container in the extraction is read, so a "
                 "second Android user's configuration is reported rather than replacing the "
                 "first. A "
                 "container that holds the preferences file and no termux.properties is reported "
                 "with Terminal Properties Set blank. A container that holds neither file produces "
                 "no row.",
        "paths": ('*/com.termux/shared_prefs/com.termux_preferences.xml',
                  '*/com.termux/files/home/.termux/termux.properties'),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {
            "emu_a15_oss_v1": "Android 15 | com.termux vc 1002 | 2 rows",
        },
    }
}

import gzip
import os
import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.artifacts.storagePathViews import unique_files

PACKAGE = 'com.termux'


def _container_root(path):
    """The com.termux app data directory a matched file sits in, or None."""
    path = str(path).replace('\\', '/')
    marker = f'/{PACKAGE}/'
    index = path.find(marker)
    if index == -1:
        return None
    return path[:index + len(marker)]


def _read_text(file_found):
    """The file's text, decompressing a .gz rotation in memory, or None."""
    try:
        if file_found.endswith('.gz'):
            with gzip.open(file_found, 'rt', encoding='utf-8', errors='replace') as handle:
                return handle.read()
        with open(file_found, 'r', encoding='utf-8', errors='replace') as handle:
            return handle.read()
    except OSError as error:
        logfunc(f'Termux: could not read {file_found}: {error}')
        return None


@artifact_processor
def termux_apt_history(context):
    files_found = unique_files(context)

    data_list = []
    sources = []
    for file_found in files_found:
        file_found = str(file_found).replace('\\', '/')
        if os.path.isdir(file_found):
            continue
        text = _read_text(file_found)
        if text is None:
            continue
        read_any = False
        # Blocks are separated by a blank line; each holds Key: value lines.
        for block in re.split(r'\n\s*\n', text):
            block = block.strip()
            if not block:
                continue
            fields = {}
            for line in block.splitlines():
                if ':' not in line:
                    continue
                key, _, value = line.partition(':')
                fields[key.strip()] = value.strip()
            if 'Start-Date' not in fields:
                continue
            # The package action is whichever of these the block carries.
            action = ''
            packages = ''
            for name in ('Install', 'Reinstall', 'Upgrade', 'Downgrade', 'Remove', 'Purge'):
                if name in fields:
                    action = name
                    packages = fields[name]
                    break
            data_list.append((
                fields.get('Start-Date', ''),
                fields.get('End-Date', ''),
                fields.get('Commandline', ''),
                action,
                packages,
                fields.get('Requested-By', ''),
                context.get_relative_path(file_found),
            ))
            read_any = True
        if read_any and file_found not in sources:
            sources.append(file_found)

    data_headers = (
        ('Start Date (local, as stored)', 'datetime'),
        ('End Date (local, as stored)', 'datetime'),
        'Command Line', 'Action', 'Packages', 'Requested By', 'Source File',
    )
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def termux_installed_packages(context):
    files_found = unique_files(context)

    data_list = []
    sources = []
    for file_found in files_found:
        file_found = str(file_found).replace('\\', '/')
        if os.path.isdir(file_found):
            continue
        text = _read_text(file_found)
        if text is None:
            continue
        read_any = False
        for block in re.split(r'\n\s*\n', text):
            block = block.strip()
            if not block:
                continue
            fields = {}
            key = None
            for line in block.splitlines():
                if line[:1] in (' ', '\t') and key:
                    # A continuation line of the previous field (e.g. Description).
                    fields[key] += ' ' + line.strip()
                    continue
                if ':' not in line:
                    continue
                key, _, value = line.partition(':')
                key = key.strip()
                fields[key] = value.strip()
            if 'Package' not in fields:
                continue
            status = fields.get('Status', '')
            # dpkg records desired/error/state; only report packages actually installed.
            if 'installed' not in status.split():
                continue
            description = fields.get('Description', '')
            data_list.append((
                fields.get('Package', ''),
                fields.get('Version', ''),
                fields.get('Architecture', ''),
                status,
                'Yes' if fields.get('Essential', '').lower() == 'yes' else '',
                fields.get('Maintainer', ''),
                fields.get('Homepage', ''),
                description.split('. ')[0] if description else '',
                context.get_relative_path(file_found),
            ))
            read_any = True
        if read_any and file_found not in sources:
            sources.append(file_found)

    data_headers = ('Package', 'Version', 'Architecture', 'Status', 'Essential',
                    'Maintainer', 'Homepage', 'Description', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


def _preferences(path):
    """{name: value} from com.termux_preferences.xml, or {}."""
    values = {}
    try:
        tree = ET.parse(path)
    except (OSError, ET.ParseError) as error:
        logfunc(f'Termux: could not parse {path}: {error}')
        return values
    for element in tree.getroot():
        name = element.get('name')
        if not name:
            continue
        if element.tag == 'string':
            values[name] = element.text or ''
        else:
            values[name] = element.get('value', '')
    return values


def _properties(path):
    """{key: value} from the non-comment lines of termux.properties, or {}."""
    values = {}
    text = _read_text(path)
    if text is None:
        return values
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, _, value = line.partition('=')
        values[key.strip()] = value.strip()
    return values


@artifact_processor
def termux_configuration(context):
    files_found = unique_files(context)

    prefs_by_root = {}
    props_by_root = {}
    for file_found in files_found:
        file_found = str(file_found).replace('\\', '/')
        if os.path.isdir(file_found):
            continue
        root = _container_root(file_found)
        if root is None:
            continue
        if file_found.endswith('shared_prefs/com.termux_preferences.xml'):
            prefs_by_root[root] = (_preferences(file_found), file_found)
        elif file_found.endswith('files/home/.termux/termux.properties'):
            props_by_root[root] = (_properties(file_found), file_found)

    data_list = []
    sources = []
    for root in dict.fromkeys(list(prefs_by_root) + list(props_by_root)):
        prefs, prefs_path = prefs_by_root.get(root, ({}, ''))
        props, props_path = props_by_root.get(root, ({}, ''))
        # Report the changed terminal properties as a compact key=value summary.
        props_summary = '; '.join(f'{k}={v}' for k, v in sorted(props.items()))
        source = prefs_path or props_path
        data_list.append((
            prefs.get('current_session', ''),
            prefs.get('log_level', ''),
            props_summary,
            context.get_relative_path(source),
        ))
        if source and source not in sources:
            sources.append(source)

    data_headers = ('Current Session ID', 'Log Level (as stored)',
                    'Terminal Properties Set', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
