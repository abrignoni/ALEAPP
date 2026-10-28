__artifacts_v2__ = {
    "android_setup_flags": {
        "name": "Setup Flags",
        "description": "The setup and provisioning flags of each Android user (user_setup_complete and related names in settings_secure.xml), "
                       "the history entries of the secure and global settings for those names, and the setup properties of the persistent property store.",
        "author": "@danjethh, Claude",
        "creation_date": "2026-10-27",
        "last_update_date": "2026-10-28",
        "requirements": "none",
        "category": "Wipe & Setup",
        "notes": "Sources: settings_secure.xml of each Android user (plain XML, or the binary ABX form of "
                 "Android 12 and later, read with the ABX reader of the tool), settings_history_secure.json and "
                 "settings_history_global.json of the same folder, and persistent_properties (read as a protobuf store; its boot "
                 "reason entries are rows of Persistent Properties - Matched Text Observations). The current values of "
                 "settings_global.xml are not read here: they are rows of Settings Global, device_provisioned and the other setup "
                 "names among them. A copy under a mirror folder is skipped, as Settings Global does. Namespace is secure, global "
                 "or property and User is the number in the folder name; Location is the number "
                 "of the setting, history entry or record within the file.\n"
                 "Rows are the settings named user_setup_complete, device_provisioned, setup_skipped, do_setup_complete, "
                 "user_setup_personalization_state, last_setup_shown, secure_frp_mode, tv_user_setup_complete, setup_type, "
                 "first_enter_wifisetupwizard and device_provisioning_mobile_data (the setup-related names found in the tested "
                 "sources), and the properties persist.sys.device_provisioned, persist.sys.setupwizard and "
                 "persist.sys.setupwizard.user_setup_complete. Value, Written By (the package that wrote the value) and Default Value "
                 "are as stored. Record says where the row comes from; history rows are the entries of the settings change history, "
                 "with Old Value and, when the time is epoch milliseconds between 2009 and 2100, Time (UTC); any other time is shown as "
                 "stored in Time As Stored and has no UTC (the first entry of each setting in the tested files holds a number far below "
                 "2009 there; its meaning is not examined). Names and values are shown as stored and no meaning is applied by this tool: "
                 "a row says only that the setting held that value, or changed to it, with that writer. A setting "
                 "that is not listed has no row, which is not evidence that it is unset (a default that is not shown here applies); a source with "
                 "no row says nothing about the device. These flags also changed from 1 to 0 and back to 1 around update entries of the "
                 "recovery history in two of the tested sources, so a change of these flags is not by itself an indicator of a reset.\n"
                 "Evidence tiers. Data-proven on two Samsung full file system extractions (Android 16): both settings files are in the "
                 "ABX form; the artifact gave 27 and 31 rows (4 and 5 current secure values, 20 and 23 history entries, 3 property rows "
                 "each; the second extraction has a second user with a history file), equal to a count of the named settings, history "
                 "entries and properties read from the files by an independent parse. The 6 current global values of each extraction "
                 "(not read here) were equal in name and value to the rows of Settings Global. The history files hold the first entry of each "
                 "setting with a small number as time, then entries with epoch milliseconds. Constructed only: plain XML, a second "
                 "user, a cut ABX or XML file, JSON that is not an object and a history entry that is not an object. Not examined: "
                 "Android before 16, other vendors, and the settings_system namespace (no setup flag was found in it).",
        "paths": ('*/system/users/*/settings_secure.xml', '*/system/users/*/settings_history_secure.json',
                  '*/system/users/*/settings_history_global.json', '*/property/persistent_properties'),
        "output_types": "standard",
        "artifact_icon": "settings",
        "sample_data": {}
    },
}

import os

from scripts import android_boot_reason as boot
from scripts import android_setup_flags as setup
from scripts.artifacts.settingsSecure import parse_settings_root
from scripts.ilapfuncs import artifact_processor, logfunc

MAX_FILE_BYTES = 16 * 1024 * 1024

SETUP_HEADERS = (('Time (UTC)', 'datetime'), 'Time As Stored', 'Setting', 'Value', 'Written By', 'Record', 'Old Value',
                 'Default Value', 'Namespace', 'User', 'Location', 'Source File')


def read_text(path):
    """The decoded text of a file (utf-8, undecodable bytes replaced), or None when it cannot be read."""
    try:
        with open(path, 'rb') as handle:
            data = handle.read(MAX_FILE_BYTES + 1)
    except OSError as error:
        logfunc(f'Setup flags: {os.path.basename(path)} could not be read: {error}')
        return None
    if len(data) > MAX_FILE_BYTES:
        logfunc(f'Setup flags: {os.path.basename(path)} is larger than {MAX_FILE_BYTES} bytes, the first {MAX_FILE_BYTES} were read')
        data = data[:MAX_FILE_BYTES]
    return data.decode('utf-8', 'replace')


def load_store(path, label):
    """The records of a persistent_properties file, or None (the reason is logged)."""
    try:
        with open(path, 'rb') as handle:
            data = handle.read(MAX_FILE_BYTES)
    except OSError as error:
        logfunc(f'Setup flags: {label} could not be read: {error}')
        return None
    try:
        records, warning = boot.read_persistent_properties(data)
    except boot.StoreError as error:
        logfunc(f'Setup flags: {label} is not a persistent property store: {error}')
        return None
    if warning:
        logfunc(f'Setup flags: {label}: {warning}')
    return records


# ---------------------------------------------------------------------------------------------
# Setup flags
# ---------------------------------------------------------------------------------------------
def property_rows(records, label):
    rows = []
    for position, record in enumerate(records, 1):
        if record.name in setup.SETUP_PROPERTIES:
            rows.append((None, '', record.name, setup.tidy(record.value), '', 'Persistent property', '', '', 'property', '',
                         f'record {position}', label))
    return rows


def settings_rows(path, label):
    """Rows of one settings_<namespace>.xml or settings_history_<namespace>.json file."""
    namespace = setup.namespace_of(path)
    user = setup.user_of(path)
    if path.lower().endswith('.json'):
        text = read_text(path)
        if text is None:
            return []
        rows, warning = setup.history_rows(text, namespace, user, label)
        if warning:
            logfunc(f'Setup flags {label}: {warning}')
        return rows
    try:
        root = parse_settings_root(path, 'Setup flags')
    except Exception as error:  # pylint: disable=broad-exception-caught  # the ABX reader raises its own error class
        logfunc(f'Setup flags {label}: could not be read as settings XML: {error}')
        return []
    if root is None:
        return []
    return setup.current_rows(root, namespace, user, label)


@artifact_processor
def android_setup_flags(context):
    rows = []
    sources = []
    for path in sorted(str(item) for item in context.get_files_found()):
        name = os.path.basename(path)
        label = context.get_relative_path(path)
        if name == 'persistent_properties':
            records = load_store(path, label)
            if records is None:
                continue
            sources.append(label)
            rows += property_rows(records, label)
        elif setup.namespace_of(path) and '/mirror/' not in path.replace(os.sep, '/'):
            found = settings_rows(path, label)
            sources.append(label)
            rows += found
    return SETUP_HEADERS, rows, '\n'.join(sources)
