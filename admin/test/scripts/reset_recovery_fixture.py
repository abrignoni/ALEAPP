"""Builds the synthetic inputs of sRecoveryhist and Bug Report - Recovery History.

Every value is invented: firmware names, codes, dates and reasons are made up. Only the structure is taken from the real
files: the Samsung recovery history files (``history``, ``extra_history``, ``last_history``, ``last_extra_history``) are
plain text with ``+ [CODE | date | firmware]`` headers, option lines, a status line and ``reboot_reason=`` lines; the bug
report zip reuses the banner, header and getprop builders of ``bugreport_fixture.py``.

Usage, from the repository root: python -m admin.test.scripts.reset_recovery_fixture <output folder>
Writes one zip per artifact and case into the folder (the files of the case under a ``Dump`` folder) and prints their names and sizes.
"""
import io
import json
import os
import sys

from admin.test.scripts import bugreport_fixture as base


# ---------------------------------------------------------------------------------------------
# Recovery history
# ---------------------------------------------------------------------------------------------
def entry(code, date, firmware, options, status='NP [-]', reboot_reason='UNKNOWN', suffix=' [-]'):
    """One history entry in the form the files use."""
    lines = ['+ [%s | %s | %s]%s' % (code, date, firmware, suffix)] + list(options) + [status, 'reboot_reason=' + reboot_reason]
    return '\n'.join(lines) + '\n'


WIPE_REASON = '--reason=MasterClearConfirm,2026-01-01T00:00:00Z'
SIM_OPTIONS = ('--just_exit', '--locale=')
UPDATE_OPTIONS = ('--update_package=@/cache/recovery/block.map', '--locale=en-US', '--carry_out=open_fota',
                  '--update_org_package=/data/fota/update.zip')


def wipe_and_sim_history():
    """Two wipe entries and SIM change and update entries between and after them; the first four headers are dated 1970."""
    return ''.join([
        entry('Aa', '1970/01/01 02:10:00', 'EXAMPLEFW1', ('--wipe_data', '--requested_time=2026/03/10 09:00:00.250', WIPE_REASON,
                                                        '--locale=en-US'), reboot_reason='Reboot:100 RecoverySystem MasterClearConfirm'),
        entry('Bb', '1970/01/01 02:50:00', 'EXAMPLEFW1', SIM_OPTIONS + ('--reason=[SIMBasedChangeCSC] AAA -> BBB',),
              reboot_reason='Reboot:101 RecoverySystem [SIMBasedChangeCSC] AAA -> BBB'),
        entry('Cc', '1970/01/03 04:40:00', 'EXAMPLEFW1', ('--wipe_data', '--requested_time=2026/03/12 11:30:00.750', WIPE_REASON,
                                                        '--locale=en-US'), reboot_reason='Reboot:102 RecoverySystem MasterClearConfirm'),
        entry('Dd', '1970/01/03 05:00:00', 'EXAMPLEFW1', UPDATE_OPTIONS, status='RP | OFFSRC: - / ONSRC: PWRON / RSTSTAT: SWRESET'),
        entry('Ee', '2026/03/20 08:00:00', 'EXAMPLEFW2', SIM_OPTIONS + ('--reason=[SIMBasedChangeCSC] BBB -> CCC',),
              status='RP | OFFSRC: - / ONSRC: PWRON / RSTSTAT: SWRESET', suffix=''),
    ])


def wipe_and_sim_extra():
    """Extra history: volumes for both wipe codes (the second one starts a step it does not end) and for a code with no entry."""
    return '\n'.join([
        'Created at Thu Jan  1 02:10:00 1970',
        '[Aa][S] format_volume : /data', '[Aa][E] format_volume : /data',
        '[Aa][S] format_volume : /cache', '[Aa][E] format_volume : /cache',
        '[Aa][S] resizing data', '[Aa][I]   10.0G //    2.0G //    8.0G', '[Aa][E] resizing data',
        '[Cc][S] format_volume : /data', '[Cc][E] format_volume : /data',
        '[Cc][S] format_volume : /metadata',
        '[Zz][S] format_volume : /data', '[Zz][E] format_volume : /data', ''])


def no_wipe_history():
    """An update and SIM changes with valid header dates, and an entry that asks to prompt and wipe (no requested time)."""
    return ''.join([
        entry('Ff', '2026/04/01 10:00:00', 'EXAMPLEFW3', SIM_OPTIONS + ('--reason=[SIMBasedChangeCSC] AAA -> CCC',),
              status='RP | OFFSRC: - / ONSRC: PWRON / RSTSTAT: SWRESET', suffix=''),
        entry('Gg', '2026/04/02 11:00:00', 'EXAMPLEFW3', UPDATE_OPTIONS, status='RP | OFFSRC: - / ONSRC: ACOKB / RSTSTAT: SWRESET',
              suffix=''),
        entry('Hh', '2026/04/03 12:00:00', 'EXAMPLEFW4', UPDATE_OPTIONS, status='RP | OFFSRC: - / ONSRC: ACOKB / RSTSTAT: SWRESET',
              suffix=''),
        entry('Ii', '2026/04/04 13:00:00', 'EXAMPLEFW4', ('--prompt_and_wipe_data', '--locale=en-US'), reboot_reason='UNKNOWN'),
    ])


def unset_clock_history():
    """Entries with a 1970 or 2010 header date and no requested time anywhere."""
    return ''.join([
        entry('Jj', '1970/01/01 00:05:00', 'EXAMPLEFW5', ('--wipe_data', WIPE_REASON, '--locale=en-US')),
        entry('Kk', '2010/01/01 00:06:15', 'EXAMPLEFW5', ('--data_resizing', '--delete_apn_changes'), status='RP [-]'),
        entry('Ll', '1970/01/02 00:00:00', 'EXAMPLEFW5', SIM_OPTIONS + ('--reason=[SIMBasedChangeCSC] CCC -> AAA',)),
    ])


def unset_clock_extra():
    return 'Created at Fri Jan  1 00:06:15 2010\n[Kk][S] resizing data\n[Kk][E] resizing data\n[Kk][S] format_volume : /metadata\n' \
           '[Kk][E] format_volume : /metadata\n'


def repeated_code_history():
    """The same code twice in one file (the volumes of the extra file can only be matched by code)."""
    return ''.join([
        entry('Mm', '2026/05/01 10:00:00', 'EXAMPLEFW6', UPDATE_OPTIONS, suffix=''),
        entry('Mm', '2026/05/02 10:00:00', 'EXAMPLEFW6', ('--wipe_data', '--requested_time=2026/05/02 09:59:30.000', WIPE_REASON), suffix=''),
    ])


def repeated_code_extra():
    return 'Created at Fri May  1 10:00:00 2026\n[Mm][S] format_volume : /data\n[Mm][E] format_volume : /data\n'


def malformed_history():
    """Text that is not a clean history file: a stray line, a header without pipes, bad dates, control characters."""
    return ('stray line before any header\n'
            '+ [oldstyle header 2020/01/01 00:00:00]\n--wipe_data\n'
            '+ [Nn | not a date | EXAMPLEFW7]\n--requested_time=not a time\n--reason=bad\x01reason\nstatus words\nreboot reason: spaced form\n'
            '+ [Oo | 2026/06/01 10:00:00]\n--update_package=x\n')


def malformed_extra():
    return 'Created at never\nnot a line\n[Nn][S]\n[Nn][X] format_volume : /data\n[Nn][S] format_volume :\n[Nn][E] format_volume\n'


# ---------------------------------------------------------------------------------------------
# bug report zip
# ---------------------------------------------------------------------------------------------
def bug_report():
    """A short bug report text: banner, header and getprop (invented values)."""
    history = 'reboot,userrequested,%d' % base.epoch_s('2026-10-30 07:00:00')
    text = base.BANNER.format(report='2026-11-02 10:15:30') + '\n' + base.HEADER['a16'] + '\n'
    text += base.properties('a16', 'UTC', history)
    return text + '== dumpstate: done (id 1)\n'


def bug_report_zip(text, members=()):
    """The zip a device keeps: main_entry.txt, the main text and any extra members (name, bytes)."""
    main_text = 'bugreport-example-EXAMPLE-2026-11-02-10-15-30.txt'
    buffer = io.BytesIO()
    base.write_zip(buffer, [('main_entry.txt', main_text.encode()), (main_text, text.encode('utf-8'))] + list(members))
    return buffer.getvalue()


def recovery_members():
    return [('FS/cache/recovery/last_history', wipe_and_sim_history().encode()),
            ('FS/cache/recovery/last_all_history', wipe_and_sim_history().encode()),
            ('FS/cache/recovery/last_extra_history', wipe_and_sim_extra().encode()),
            ('FS/cache/recovery/last_extra_history_old', b''),
            ('FS/cache/recovery/last_log', b'recovery log text of an invented device\n'),
            ('FS/data/misc/recovery/ro.build.fingerprint', b'example/examplephone/examplephone:16/EXAMPLE/1001:user/release-keys')]


# ---------------------------------------------------------------------------------------------
# cases: {artifact: {case: [(member name, bytes), ...]}}
# ---------------------------------------------------------------------------------------------
def ffs_cases():
    out = {'get_sRecoveryhist': {}}
    recovery = out['get_sRecoveryhist']
    recovery['synthetic_wipe_and_sim'] = [('Dump/efs/recovery/history', wipe_and_sim_history().encode()),
                                          ('Dump/efs/recovery/extra_history', wipe_and_sim_extra().encode())]
    recovery['synthetic_no_wipe'] = [('Dump/efs/recovery/history', no_wipe_history().encode()),
                                     ('Dump/efs/recovery/extra_history', b'Created at Wed Apr  1 10:00:00 2026\n')]
    recovery['synthetic_unset_clock'] = [('Dump/efs/recovery/history', unset_clock_history().encode()),
                                         ('Dump/efs/recovery/extra_history', unset_clock_extra().encode())]
    recovery['synthetic_cache_recovery'] = [
        ('Dump/cache/recovery/last_history', wipe_and_sim_history().encode()),
        ('Dump/cache/recovery/last_all_history', no_wipe_history().encode()),
        ('Dump/cache/recovery/last_extra_history', wipe_and_sim_extra().encode()),
        ('Dump/efs/recovery/history', repeated_code_history().encode()),
        ('Dump/efs/recovery/extra_history', repeated_code_extra().encode())]
    recovery['synthetic_malformed'] = [('Dump/efs/recovery/history', malformed_history().encode()),
                                       ('Dump/efs/recovery/extra_history', malformed_extra().encode())]
    recovery['synthetic_empty'] = [('Dump/efs/recovery/history', b''), ('Dump/efs/recovery/extra_history', b'')]
    recovery['synthetic_extra_only'] = [('Dump/efs/recovery/extra_history', wipe_and_sim_extra().encode())]
    return out


def bugreport_cases():
    out = {'bugreport_recovery_history': {}}
    recovery = out['bugreport_recovery_history']
    recovery['synthetic_zip_recovery'] = [('Dump/bugreport-example-2026-11-02-10-15-30.zip',
                                           bug_report_zip(bug_report(), recovery_members()))]
    recovery['synthetic_zip_no_recovery'] = [('Dump/bugreport-example-2026-11-02-10-15-30.zip', bug_report_zip(bug_report()))]
    recovery['synthetic_zip_unset_clock'] = [('Dump/bugreport-example-2026-11-02-10-15-30.zip', bug_report_zip(bug_report(), [
        ('FS/cache/recovery/last_history', unset_clock_history().encode()),
        ('FS/cache/recovery/last_extra_history', unset_clock_extra().encode())]))]
    return out


def cases():
    """{artifact: {case name: [(member name, bytes), ...]}} for both modules."""
    out = ffs_cases()
    out.update(bugreport_cases())
    return out


MODULE_OF = {'get_sRecoveryhist': 'sRecoveryhist', 'bugreport_recovery_history': 'bugreportRecovery'}
DESCRIPTIONS = {
    'synthetic_wipe_and_sim': 'Synthetic recovery history: two wipe entries with requested times and header dates in 1970, '
                              'SIM region change and update entries between and after them, one entry with a header date after 2012, '
                              'and an extra history file with format lines for both wipe codes (one step without an end line) and for a '
                              'code with no entry.',
    'synthetic_no_wipe': 'Synthetic recovery history with header dates after 2012: SIM region change and update entries and one '
                         'prompt-and-wipe entry without a requested time, and an extra history file with no lines.',
    'synthetic_unset_clock': 'Synthetic recovery history with header dates near 1970 and 2010 and no requested time.',
    'synthetic_cache_recovery': 'Synthetic cache recovery folder (last_history, last_all_history, last_extra_history) and an efs history '
                                'in which one code is used twice.',
    'synthetic_malformed': 'Synthetic recovery files that are not clean: a stray line, a header without pipes, a bad date, a bad requested '
                           'time, a control character, the spaced reboot reason form, and an extra file with lines in other forms.',
    'synthetic_empty': 'Synthetic empty history and extra history files.',
    'synthetic_extra_only': 'Synthetic extra history file with no history file next to it.',
    'synthetic_zip_recovery': 'Synthetic bug report zip with the cache recovery folder: history files with wipe, SIM region change and '
                              'update entries and an extra history file.',
    'synthetic_zip_no_recovery': 'Synthetic bug report zip without a recovery folder.',
    'synthetic_zip_unset_clock': 'Synthetic bug report zip whose recovery history shows header dates near 1970 and 2010 and no requested '
                                 'time.',
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
    main(sys.argv[1] if len(sys.argv) > 1 else 'reset_recovery_fixture_out')
