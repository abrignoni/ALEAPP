"""The setup and provisioning flags of an Android device, read by the Setup Flags artifact.

The flags are settings of the Settings provider (``settings_secure.xml`` of each user; ``settings_global.xml`` is read by Settings Global) and a few
persistent system properties. This module holds the list of names that are reported and the reading of the history file
of the provider (``settings_history_<namespace>.json``).

Nothing here depends on the rest of ALEAPP. Names and values are shown as stored; no meaning is applied beyond the two
that the platform documents (see the notes of the artifacts).
"""
import json
from datetime import datetime, timezone

# Names of settings that carry the setup state, as found in the tested extractions and bug reports.
SETUP_SETTINGS = (
    'user_setup_complete', 'device_provisioned', 'setup_skipped', 'do_setup_complete', 'user_setup_personalization_state',
    'last_setup_shown', 'secure_frp_mode', 'tv_user_setup_complete', 'setup_type', 'first_enter_wifisetupwizard',
    'device_provisioning_mobile_data',
)
# Persistent or boot-time properties that carry the same state.
SETUP_PROPERTIES = ('persist.sys.device_provisioned', 'persist.sys.setupwizard', 'persist.sys.setupwizard.user_setup_complete')
NAMESPACES = ('secure', 'global', 'system')
MS_FLOOR = 1230768000000        # 2009-01-01 in epoch milliseconds
MS_CEILING = 4102444800000      # 2100-01-01
MAX_HISTORY_ENTRIES = 50000
VALUE_CHARS = 400
CONTROL_TABLE = {code: ' ' for code in list(range(0, 9)) + list(range(11, 32)) + [127]}


def tidy(value):
    """A text with control characters shown as a space and cut to VALUE_CHARS."""
    return ('' if value is None else str(value)).translate(CONTROL_TABLE)[:VALUE_CHARS]


def ms_moment(value):
    """UTC datetime for epoch milliseconds between 2009 and 2100, else None."""
    try:
        number = int(str(value).strip())
    except ValueError:
        return None
    if number < MS_FLOOR or number >= MS_CEILING:
        return None
    return datetime.fromtimestamp(number / 1000.0, timezone.utc)


def namespace_of(file_name):
    """``secure``, ``global`` or ``system`` for a file name such as ``settings_secure.xml``, else ''."""
    base = str(file_name).replace('\\', '/').rsplit('/', 1)[-1].lower()
    for namespace in NAMESPACES:
        if base in ('settings_%s.xml' % namespace, 'settings_history_%s.json' % namespace):
            return namespace
    return ''


def user_of(path):
    """The Android user number in a path ``.../users/<n>/...``, else ''."""
    parts = str(path).replace('\\', '/').split('/')
    for index, part in enumerate(parts[:-1]):
        if part == 'users' and parts[index + 1].isdigit():
            return parts[index + 1]
    return ''


def current_rows(root, namespace, user, label):
    """Rows for the setup settings among the ``<setting>`` elements of an XML root.

    Row: (moment, stored time, name, value, written by, record, old value, default value, namespace, user, location, source).
    """
    rows = []
    position = 0
    for element in root.iter('setting'):
        position += 1
        name = element.get('name', '')
        if name not in SETUP_SETTINGS:
            continue
        rows.append((None, '', name, tidy(element.get('value')), tidy(element.get('package')),
                     'Current value (settings file)', '', tidy(element.get('defaultValue')), namespace, user, 'setting %d' % position, label))
    return rows


def history_rows(text, namespace, user, label):
    """``(rows, warning)`` for the history file of the provider: one row for each entry of a setup setting.

    The file is a JSON object whose keys are setting names and whose values are lists of
    ``{"mode": n, "newValue": v, "oldValue": v, "pkg": p, "time": t}``. A time between 2009 and 2100 in epoch milliseconds
    is also shown in UTC; any other time is shown as stored and gets no UTC (the tested files hold small numbers there for
    the first entry of a setting).
    """
    try:
        data = json.loads(text)
    except ValueError as error:
        return [], 'not readable as JSON: %s' % error
    if not isinstance(data, dict):
        return [], 'the top level is not a JSON object'
    rows = []
    warning = ''
    for name in SETUP_SETTINGS:
        entries = data.get(name)
        if not isinstance(entries, list):
            continue
        for position, entry in enumerate(entries, 1):
            if len(rows) >= MAX_HISTORY_ENTRIES:
                warning = 'more than %d history entries, the rest were not read' % MAX_HISTORY_ENTRIES
                break
            if not isinstance(entry, dict):
                continue
            stored = entry.get('time', '')
            rows.append((ms_moment(stored), tidy(stored), name, tidy(entry.get('newValue')), tidy(entry.get('pkg')),
                         'History entry (settings history file, mode %s)' % tidy(entry.get('mode', '')),
                         tidy(entry.get('oldValue')), '', namespace, user, 'entry %d' % position, label))
    return rows, warning
