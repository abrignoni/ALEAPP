"""Builds the synthetic inputs of persistentProp (boot reason history) and Setup Flags.

Every value is invented: package names, settings values and epochs are made up. Only the structure is taken from the real
files:

* ``persistent_properties`` is a protobuf file (field 1 repeated, each record with the name as field 1 and the value as
  field 2), written here by a 20 line encoder;
* ``settings_secure.xml`` is XML, or the binary ABX form of Android 12 and later, which a small encoder writes here from the
  format of the reader in ``scripts/ilapfuncs.py``; ``settings_history_<namespace>.json`` is JSON.

Usage, from the repository root: python -m admin.test.scripts.reset_boot_setup_fixture <output folder>
Writes one zip per artifact and case into the folder (the files of the case under a ``Dump`` folder) and prints their names and sizes.
"""
import json
import os
import struct
import sys

from admin.test.scripts import bugreport_fixture as base

EPOCH = base.epoch_s


# ---------------------------------------------------------------------------------------------
# persistent_properties (protobuf)
# ---------------------------------------------------------------------------------------------
def _varint(number):
    out = bytearray()
    while True:
        byte = number & 0x7F
        number >>= 7
        if number:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def _field(number, payload):
    return _varint(number << 3 | 2) + _varint(len(payload)) + payload


def persistent_properties(records):
    """The bytes of a persistent_properties file holding ``records`` (name, value) in order."""
    return b''.join(_field(1, _field(1, name.encode()) + _field(2, value.encode())) for name, value in records)


BOOT_HISTORY = 'persist.sys.boot.reason.history'


def store_with_factory_reset():
    return persistent_properties([
        ('persist.sys.timezone', 'Europe/Paris'),
        (BOOT_HISTORY, 'reboot,userrequested,%d\nreboot,factory_reset,%d\nshutdown,lpm,%d\ncold,powerkey,%d' % (
            EPOCH('2026-05-20 10:00:00'), EPOCH('2026-05-10 07:30:15'), EPOCH('2026-05-01 22:00:00'), EPOCH('2026-04-20 05:00:00'))),
        ('persist.sys.boot.reason', 'reboot,factory_reset'),
        ('persist.sys.setupwizard', 'FINISH'),
        ('persist.sys.setupwizard.user_setup_complete', 'true'),
        ('persist.sys.device_provisioned', '1'),
        ('persist.sys.setupwizard.sep_ver', '170500'),
    ])


def store_without_factory_reset():
    return persistent_properties([
        (BOOT_HISTORY, 'reboot,%d\nreboot,userrequested,%d' % (EPOCH('2026-08-27 10:00:00'), EPOCH('2026-08-25 18:30:00'))),
        ('persist.sys.boot.reason', ''),
        ('persist.sys.device_provisioned', '1'),
    ])


def store_odd_entries():
    return persistent_properties([
        (BOOT_HISTORY, 'reboot\r\nreboot,a,b,%d\nreboot,notanumber\nreboot,100\nreboot,99999999999999\n\n,,\nREBOOT,FACTORY_RESET,%d' % (
            EPOCH('2026-07-01 00:00:00'), EPOCH('2026-07-02 00:00:00'))),
    ])


TEXT_LINES = (b'persist.sys.boot.reason.historyDreboot,%d\nreboot,%d\nreboot,factory_reset,%d\nreboot,userrequested,%d\nnot a match\n'
              % (EPOCH('2026-10-01 00:00:00'), EPOCH('2026-09-30 00:00:00'), EPOCH('2026-09-12 05:20:01'), EPOCH('2026-08-01 00:00:00')))


def store_truncated():
    data = store_with_factory_reset()
    return data[:len(data) - 9]


# ---------------------------------------------------------------------------------------------
# settings files
# ---------------------------------------------------------------------------------------------
def settings_xml(settings, version='0'):
    """Plain XML of a settings file. settings: list of (id, name, value, package, default or None)."""
    lines = ["<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>", '<settings version="%s">' % version]
    for number, name, value, package, default in settings:
        extra = ' defaultValue="%s" defaultSysSet="true"' % default if default is not None else ''
        lines.append('  <setting id="%s" name="%s" value="%s" package="%s"%s />' % (number, name, value, package, extra))
    lines.append('</settings>')
    return '\n'.join(lines).encode()


class AbxWriter:
    """A minimal writer of the Android binary XML form (see AbxReader in scripts/ilapfuncs.py for the layout)."""

    def __init__(self):
        self.out = bytearray(b'ABX\x00')
        self.interned = []

    def _string(self, text):
        data = text.encode('utf-8')
        self.out += struct.pack('>h', len(data)) + data

    def _interned(self, text):
        if text in self.interned:
            self.out += struct.pack('>h', self.interned.index(text))
        else:
            self.out += struct.pack('>h', -1)
            self._string(text)
            self.interned.append(text)

    def start(self, tag):
        self.out.append(0x30 | 2)
        self._interned(tag)

    def end(self, tag):
        self.out.append(0x30 | 3)
        self._interned(tag)

    def attribute(self, name, value):
        self.out.append(0x20 | 15)
        self._interned(name)
        self._string(value)


def settings_abx(settings, truncate=0):
    """The ABX form of the same settings. ``truncate`` cuts that many bytes off the end."""
    writer = AbxWriter()
    writer.out.append(0x10)
    writer.start('settings')
    writer.attribute('version', '0')
    for number, name, value, package, default in settings:
        writer.start('setting')
        writer.attribute('id', str(number))
        writer.attribute('name', name)
        writer.attribute('value', value)
        writer.attribute('package', package)
        if default is not None:
            writer.attribute('defaultValue', default)
        writer.end('setting')
    writer.end('settings')
    writer.out.append(0x11)
    data = bytes(writer.out)
    return data[:len(data) - truncate] if truncate else data


def secure_settings():
    return [
        (1, 'android_id', '0123456789abcdef', 'android', None),
        (2, 'user_setup_complete', '1', 'com.example.setupwizard', '1'),
        (3, 'user_setup_personalization_state', '10', 'com.example.setupwizard', '10'),
        (4, 'last_setup_shown', 'eclair_1', 'com.example.setupwizard', 'eclair_1'),
        (5, 'screen_off_timeout_note', 'x', 'android', None),
    ]


def other_settings():
    return [(21, 'adb_enabled', '0', 'android', None), (22, 'device_name', 'Example Phone', 'android', None)]


def history_secure_json():
    """settings_history style JSON: the first entry of a setting has a small time (not an epoch), later ones epoch milliseconds."""
    data = {
        'user_setup_complete': [
            {'mode': 0, 'newValue': '0', 'pkg': 'android', 'time': 18000000},
            {'mode': 1, 'newValue': '1', 'oldValue': '0', 'pkg': 'com.example.setupwizard', 'time': 1780000000000}],
        'last_setup_shown': [{'mode': 0, 'newValue': 'eclair_1', 'pkg': 'com.example.setupwizard', 'time': 1780000000500}],
        'adb_enabled': [{'mode': 0, 'newValue': '0', 'pkg': 'android', 'time': 18000005}],
    }
    return json.dumps(data).encode()


def history_global_json():
    """The history of the global namespace: an entry with a text time and an entry that is not an object are read around."""
    data = {
        'device_provisioned': [
            {'mode': 0, 'newValue': '0', 'pkg': 'android', 'time': 18000003},
            {'mode': 1, 'newValue': '1', 'oldValue': '0', 'pkg': 'com.example.setupwizard', 'time': 1780000000000}],
        'setup_skipped': [{'mode': 1, 'newValue': '0', 'oldValue': 'x', 'pkg': 'android', 'time': 'not a number'}, 'not a dict'],
        'adb_enabled': [{'mode': 0, 'newValue': '0', 'pkg': 'android', 'time': 18000005}],
    }
    return json.dumps(data).encode()


# ---------------------------------------------------------------------------------------------
# cases: {artifact: {case: [(member name, bytes), ...]}}
# ---------------------------------------------------------------------------------------------
def ffs_cases():
    out = {'get_persistentProp': {}, 'android_setup_flags': {}}
    boot_cases = out['get_persistentProp']
    boot_cases['synthetic_factory_reset'] = [('Dump/data/property/persistent_properties', store_with_factory_reset())]
    boot_cases['synthetic_no_factory_reset'] = [('Dump/data/property/persistent_properties', store_without_factory_reset())]
    boot_cases['synthetic_odd_entries'] = [('Dump/data/property/persistent_properties', store_odd_entries())]
    boot_cases['synthetic_truncated'] = [('Dump/data/property/persistent_properties', store_truncated())]
    boot_cases['synthetic_not_a_store'] = [('Dump/data/property/persistent_properties', b'This is a text file, not a store.\nreboot,1,2\n')]
    boot_cases['synthetic_empty_store'] = [('Dump/data/property/persistent_properties', b'')]
    boot_cases['synthetic_text_lines'] = [('Dump/data/property/persistent_properties', TEXT_LINES)]
    setup_cases = out['android_setup_flags']
    setup_cases['synthetic_xml_two_users'] = [
        ('Dump/data/system/users/0/settings_secure.xml', settings_xml(secure_settings())),
        ('Dump/data/system/users/0/settings_history_secure.json', history_secure_json()),
        ('Dump/data/system/users/0/settings_history_global.json', history_global_json()),
        ('Dump/data/system/users/10/settings_secure.xml', settings_xml([(1, 'user_setup_complete', '0', 'com.example.profile', '0')])),
        ('Dump/data/property/persistent_properties', store_with_factory_reset())]
    setup_cases['synthetic_abx'] = [
        ('Dump/data/system/users/0/settings_secure.xml', settings_abx(secure_settings())),
        ('Dump/data/system/users/0/settings_history_secure.json', history_secure_json())]
    setup_cases['synthetic_no_flags'] = [
        ('Dump/data/system/users/0/settings_secure.xml', settings_xml(other_settings())),
        ('Dump/data/property/persistent_properties', persistent_properties([('persist.sys.timezone', 'UTC')]))]
    setup_cases['synthetic_malformed_settings'] = [
        ('Dump/data/system/users/0/settings_secure.xml', settings_abx(secure_settings(), truncate=7)),
        ('Dump/data/system/users/11/settings_secure.xml', b'<settings><setting name="user_setup_complete" value="1"'),
        ('Dump/data/system/users/0/settings_history_secure.json', b'{"user_setup_complete": [ {"mode": 1'),
        ('Dump/data/system/users/0/settings_history_global.json', b'["not", "an object"]'),
        ('Dump/data/system/users/10/settings_secure.xml', b'\x00\x01\x02 not xml')]
    return out


def cases():
    """{artifact: {case name: [(member name, bytes), ...]}} for both modules."""
    return ffs_cases()


MODULE_OF = {'get_persistentProp': 'persistentProp', 'android_setup_flags': 'androidSetupFlags'}
DESCRIPTIONS = {
    'synthetic_factory_reset': 'Synthetic persistent_properties (protobuf) with a boot reason history that holds a factory_reset entry, '
                               'a persist.sys.boot.reason value and other properties.',
    'synthetic_no_factory_reset': 'Synthetic persistent_properties with a boot reason history without a factory_reset entry and an '
                                  'empty persist.sys.boot.reason.',
    'synthetic_odd_entries': 'Synthetic boot reason history with entries that have no epoch, a text epoch, a small epoch, a huge epoch, '
                             'an empty line, a lower case and an upper case factory_reset word, a subreason with commas and CRLF line ends.',
    'synthetic_truncated': 'Synthetic persistent_properties cut in the middle of its last record.',
    'synthetic_not_a_store': 'A text file in place of persistent_properties, with no line the text rules select.',
    'synthetic_text_lines': 'A text file in place of persistent_properties with lines the text rules select (a history prefix line, two-part reboot lines, a factory_reset line).',
    'synthetic_empty_store': 'An empty persistent_properties file.',
    'synthetic_xml_two_users': 'Synthetic settings XML and history JSON of user 0, a second user with the flag set to 0, and a persistent '
                               'property store with the setup properties.',
    'synthetic_abx': 'Synthetic settings files of user 0 in the binary ABX form.',
    'synthetic_no_flags': 'Synthetic settings files (XML and ABX) without any setup flag and a property store without setup properties.',
    'synthetic_malformed_settings': 'Synthetic settings files that cannot be read: cut XML, cut ABX, cut JSON, JSON that is not an object, '
                                    'binary junk.',
}


def write_case_files(repo_root, patterns_of):
    """Write the case zips and the testdata JSON files of both modules under ``repo_root`` (the committed layout).

    ``patterns_of`` maps an artifact key to its ``paths`` tuple.
    """
    by_module = {}
    for artifact, named in cases().items():
        module = MODULE_OF[artifact]
        folder = os.path.join(repo_root, 'admin', 'test', 'cases', 'data', module)
        os.makedirs(folder, exist_ok=True)
        for name, members in named.items():
            key = 'case' + name
            base.write_zip(os.path.join(folder, 'testdata.%s.%s.%s.zip' % (module, artifact, key)), members)
            case = by_module.setdefault(module, {}).setdefault(key, {
                'description': DESCRIPTIONS[name] + ' Invented values, contains no real evidence.', 'maker': 'synthetic',
                'make_data': {'input_data_path': name + '.zip', 'os': 'Windows-10-10.0.19045-SP0',
                              'timestamp': '2026-10-27T12:00:00.000000',
                              'last_commit': {'hash': 'Uncommitted', 'author_name': 'N/A', 'author_email': 'N/A',
                                              'date': '2026-10-27T12:00:00.000000', 'message': 'File not yet committed to git'}},
                'artifacts': {}})
            case['artifacts'][artifact] = {'search_patterns': list(patterns_of[artifact]), 'file_count': len(members),
                                           'expected_output': {'headers': [], 'data': []}}
    for module, data in by_module.items():
        path = os.path.join(repo_root, 'admin', 'test', 'cases', 'testdata.%s.json' % module)
        with open(path, 'w', encoding='utf-8', newline='\n') as handle:
            json.dump(data, handle, indent=2)
            handle.write('\n')


def main(output):
    os.makedirs(output, exist_ok=True)
    for artifact, named in cases().items():
        for name, members in named.items():
            base.write_zip(os.path.join(output, '%s.%s.zip' % (artifact, name)), members)
    for name in sorted(os.listdir(output)):
        print(name, os.path.getsize(os.path.join(output, name)))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'reset_boot_setup_fixture_out')
