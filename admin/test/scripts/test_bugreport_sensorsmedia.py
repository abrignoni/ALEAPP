"""Android bug report text: location, sensors, camera, audio, media, accessibility, input method, display and window dumps."""
# pylint: disable=protected-access
import io
import os
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from admin.test.scripts import bugreport_sensorsmedia_fixture as fixture
from scripts import dumpstate_reader as reader
from scripts import dumpstate_sensorsmedia as sm
from scripts.artifacts import bugreportSensorsMedia as artifacts


class Context:
    def __init__(self, root, files):
        self.root = Path(root)
        self.files = list(map(str, files))

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root)).replace(os.sep, '/')


def scan_text(text):
    report = reader.Report(reader.Source('memory', ''))
    data = text.encode('utf-8') if isinstance(text, str) else text
    reader.scan_lines(reader.iter_lines(io.BytesIO(data)), report)
    report.finish()
    return report


def utc(*parts):
    return datetime(*parts, tzinfo=timezone.utc)


def a16(**kwargs):
    return scan_text(fixture.build_report('a16', **kwargs))


def a10(**kwargs):
    return scan_text(fixture.build_report('a10', **kwargs))


class LocationTests(unittest.TestCase):
    def test_providers_new_layout(self):
        report = a16()
        providers = {p.provider: p for p in sm.rows(report, 'location_providers')}
        self.assertEqual(list(providers), ['passive', 'network', 'gps'])
        passive = providers['passive']
        self.assertEqual((passive.service, passive.allowed, passive.listeners, passive.identity),
                         ('registered', 'true', 2, '1000/android[LocationService]'))
        network = providers['network']
        self.assertEqual((network.connected, network.target_service, network.stationary),
                         ('true', '10301/com.example.user.sideloaded/.NetService@2', 'false (not idle) (not stationary)'))
        self.assertEqual(providers['gps'].started, 'false   (changed +3m0s0ms ago)')

    def test_last_known_users_enabled_and_text(self):
        rows = sm.rows(a16(), 'location_last')
        by_key = {(r.provider, r.user): r for r in rows}
        self.assertEqual(sorted(by_key, key=str), sorted([('passive', 0), ('passive', 10), ('network', 0), ('gps', None)], key=str))
        self.assertEqual(by_key[('passive', 10)].enabled, 'false')
        self.assertEqual(by_key[('network', 0)].text, '')                   # an enabled line without a location
        self.assertEqual(by_key[('gps', None)].enabled, 'true')              # provider level enabled line after the location
        self.assertEqual(sm.parse_location_text(by_key[('gps', None)].text),
                         ('gps', '12.340000', '-45.670000', '4.5', '+1h0m0s0ms'))
        self.assertEqual(sm.parse_location_text('null'), ('', '', '', '', ''))

    def test_requests_fields(self):
        rows = sm.rows(a16(), 'location_requests')
        first = rows[0]
        self.assertEqual((first.uid, first.package, first.tag, first.listener, first.flags),
                         (10300, 'com.example.user.chat', 'chat_location', 'AB12CD34', '{bg}'))
        self.assertEqual(rows[1].flags, '(COARSE)')
        self.assertEqual(artifacts._quality(first.request), ('BALANCED', '+1h0m0s0ms'))
        self.assertEqual(artifacts._quality(rows[1].request), ('PASSIVE', ''))
        self.assertEqual(artifacts._quality('Request[POWER_LOW passive requested=0 fastest=0]'), ('POWER_LOW', ''))
        self.assertEqual(artifacts._field(first.request, 'minUpdateDistance'), '100.0')
        self.assertEqual(first.work_source, 'WorkSource{10300 com.example.user.chat}')

    def test_events_clients_and_times(self):
        report = a16(zone='Europe/Paris')
        events = sm.rows(report, 'location_events')
        self.assertEqual(events[0].event, '[u0] enabled')
        self.assertEqual(events[0].provider, 'passive')
        registration = events[1]
        self.assertEqual((registration.event, registration.client), ('+registration', '10300/com.example.user.chat[chat_location]/AB12CD34'))
        self.assertTrue(registration.detail.startswith('Request[@+1h0m0s0ms BALANCED'))
        self.assertEqual(events[2].event, 'request')
        self.assertEqual((events[3].event, events[3].client), ('delivered location[1]', '10300/com.example.user.chat[chat_location]/AB12CD34'))
        self.assertEqual(events[5].provider, '')
        self.assertEqual(sm.utc_for(report, events[0].time_text), utc(2026, 11, 2, 7, 30, 0, 123000))   # Paris is UTC+1 in November

    def test_usage_new_and_old(self):
        usage = sm.rows(a16(), 'location_usage')
        self.assertEqual((usage[0].provider, usage[0].min_interval, usage[0].max_interval, usage[0].total, usage[0].locations),
                         ('passive', '0s', '3600s', '+1h0m0s0ms', 7))
        self.assertEqual(usage[1].max_interval, 'passive')
        old = sm.rows(a10(), 'location_usage')
        self.assertEqual((old[0].client, old[0].provider, old[0].locations), ('com.example.user.chat', 'gps', None))
        self.assertTrue(old[1].detail.startswith('Min interval 0 seconds: Max interval 1800 seconds'))

    def test_old_layout(self):
        report = a10()
        requests = sm.rows(report, 'location_requests')
        self.assertEqual([(r.source, r.provider, r.uid, r.package, r.state) for r in requests],
                         [('Active Records by Provider', 'passive', 1000, 'android', 'foreground'),
                          ('Active Records by Provider', 'passive', 10300, 'com.example.user.chat', 'background')])
        self.assertEqual(requests[1].work_source, 'WorkSource{10301 com.example.user.sideloaded}')
        last = sm.rows(report, 'location_last')
        self.assertEqual([(r.source, r.provider) for r in last], [('Last Known Locations', 'fused'), ('Last Known Locations', 'network'),
                                                                   ('Last Known Locations Coarse Intervals', 'fused')])
        self.assertEqual(sm.parse_location_text(last[0].text)[1:3], ('12******', '-45******'))
        providers = {p.provider: p for p in sm.rows(report, 'location_providers')}
        self.assertEqual((providers['passive'].useable, providers['network'].enabled, providers['gps'].started),
                         ('true', 'false', 'false   (changed +59m34s287ms ago)'))
        self.assertEqual(sm.rows(report, 'location_events'), [])

    def test_time_zone_states(self):
        rows = sm.rows(a16(), 'time_zone_states')
        items = [(r.component, r.item) for r in rows]
        self.assertIn(('Primary provider config', 'config mode'), items)
        self.assertIn(('Primary provider config', 'config package'), items)
        history = [r for r in rows if r.item == 'controller state history']
        self.assertEqual([(r.index, r.elapsed, r.value) for r in history],
                         [(0, 'PT21.171S', 'UNKNOWN'), (1, 'PT21.175S', 'STOPPED'), (2, 'PT1H16M45.024S', 'CERTAIN')])
        self.assertEqual(len([r for r in rows if r.item == 'provider state history']), 2)
        self.assertIn(('Primary Provider', 'provider target service'), items)
        self.assertEqual(sm.rows(a10(), 'time_zone_states'), [])


class SensorTests(unittest.TestCase):
    def test_list_joined_with_active_state(self):
        sensors = {s.name: s for s in sm.rows(a16(), 'sensors')}
        accelerometer = sensors['example_acc']
        self.assertEqual((accelerometer.vendor, accelerometer.type, accelerometer.mode, accelerometer.active_count,
                          accelerometer.selected_sampling, accelerometer.selected_batching, accelerometer.connections),
                         ('example', 'android.sensor.accelerometer(1)', 'continuous', 1, '80.00', '2000.00', 1))
        light = sensors['example_light']
        self.assertEqual((light.active_count, light.sampling, light.connections), (2, '250.0, 200.0', 2))
        steps = sensors['example_steps']
        self.assertEqual((steps.active_count, steps.connections, steps.permission), (None, None, 'android.permission.ACTIVITY_RECOGNITION'))

    def test_decimal_handle_of_the_old_layout_joins(self):
        sensors = {s.name: s for s in sm.rows(a10(), 'sensors')}
        self.assertEqual(sensors['example_acc'].handle, '0000000001')
        self.assertEqual(sensors['example_acc'].active_count, 1)

    def test_connections(self):
        rows = sm.rows(a16(), 'sensor_connections')
        self.assertEqual([(r.number, r.uid, r.sensor, r.handle, r.pending_flush) for r in rows],
                         [(0, 1000, 'example_light', '0x00000005', '0'), (1, 10300, 'example_acc', '0x00000001', '2'),
                          (1, 10300, 'example_steps', '0x00000012', '0'), (2, 1000, 'Example Grip Sensor', '0x02000012', '3'),
                          (3, None, '', '', '')])
        self.assertEqual([(r.status, r.first_flush, r.access) for r in rows[:2] + rows[3:4]],
                         [('active', '', ''), ('active', '', ''), ('', 'false', 'true')])
        self.assertEqual(rows[0].label, 'com.example.server.Brightness$2')

    def test_registrations_both_layouts(self):
        new = sm.rows(a16(), 'sensor_registrations')
        self.assertEqual((new[0].clock, new[0].action, new[0].sampling, new[0].sensor, new[0].package),
                         ('08:02:00', '-', 'N/A', 'example_acc Accelerometer Non-wakeup', 'com.example.server.Orientation'))
        self.assertEqual((new[1].action, new[1].pid, new[1].uid, new[1].sampling, new[1].batching),
                         ('+', 4321, 10300, '20000', '5000000'))
        old = sm.rows(a10(), 'sensor_registrations')
        self.assertEqual((old[0].action, old[0].sampling, old[0].sensor, old[0].package), ('-', '', '', 'com.example.server.Orientation'))
        self.assertEqual((old[1].sampling, old[1].batching, old[1].package), ('20000', '0', 'com.example.user.chat.collect.Scanner'))

    def test_registration_with_date_and_bracketed_sensor(self):
        # the shape of a Samsung Android 13 report: month-day and milliseconds before the clock, sensor in brackets
        on = sm._REGISTRATION.match('10-30 08:02:00.123 + 0x0000001f pid= 4321 uid=10300 package=com.example.user.chat '
                                    'samplingPeriod=66667us batchingPeriod=0us [ example_light Light ]')
        off = sm._REGISTRATION.match('10-30 08:03:00.456 - 0x0000001f pid= 4321 uid=10300 package=com.example.user.chat '
                                     '[ example_light Light ]')
        self.assertEqual(on.group(1, 2, 6, 7, 8, 11),
                         ('10-30 08:02:00.123', '+', 'com.example.user.chat', '66667', '0', 'example_light Light'))
        self.assertEqual(off.group(1, 2, 7, 11), ('10-30 08:03:00.456', '-', None, 'example_light Light'))

    def test_events_dated_and_clock_only(self):
        report = a16(zone='Europe/Paris')
        events = sm.rows(report, 'sensor_events')
        self.assertEqual([(e.sensor, e.event, e.wall) for e in events],
                         [('example_light', 1, '10-30 08:00:00.100'), ('example_light', 2, '10-30 08:01:00.200'),
                          ('example_steps', 1, '10-30 08:02:00.300')])
        self.assertEqual(events[0].values, '12.00, 0.00, 0.00')
        self.assertEqual(sm.utc_for(report, events[0].wall), utc(2026, 10, 30, 7, 0, 0, 100000))
        self.assertEqual({e.wall for e in sm.rows(a10(), 'sensor_events')}, {'08:00:00.100', '08:01:00.200', '08:02:00.300'})

    def test_events_per_sensor_are_capped(self):
        lines = ''.join('\t %d (ts=%d.0, wall=08:00:%02d.000) 1.00, \n' % (n, n, n % 60) for n in range(1, 160))
        text = ('== dumpstate: 2026-01-01 10:00:00\n\n------ DUMPSYS (/system/bin/dumpsys) ------\nDUMP OF SERVICE sensorservice:\n'
                'Sensor List:\nRecent Sensor events:\nbusy: last 159 events\n' + lines)
        self.assertEqual(len(sm.rows(scan_text(text), 'sensor_events')), sm.SensorReader.max_events_per_sensor)


class MediaTests(unittest.TestCase):
    def test_camera_events(self):
        events = sm.rows(a16(), 'camera_events')
        self.assertEqual([e.event for e in events], ['DISCONNECT', 'CONNECT', 'USER_SWITCH', 'ADD', 'Device'])
        connect = events[1]
        self.assertEqual((connect.device, connect.package, connect.pid, connect.priority), ('0', 'com.example.user.chat', 4321, 0))
        self.assertEqual((events[0].priority, events[3].device), (None, '0'))
        self.assertEqual(events[2].detail, 'previous allowed user IDs: <None>, current allowed user IDs: 0')
        old = sm.rows(a10(), 'camera_events')
        self.assertEqual([e.priority for e in old], [None] * 4)

    def test_camera_devices_and_previous_session(self):
        devices = sm.rows(a16(), 'camera_devices')
        self.assertEqual([(d.part, d.device, d.state) for d in devices],
                         [('current', '0', 'closed'), ('current', '1', 'closed'), ('previous open session', '1', 'open')])
        last = devices[2]
        self.assertEqual((last.opened, last.package, last.pid, last.uid, last.priority, last.device_status),
                         ('11-02 09:00:44', 'com.example.user.chat', 4322, 10300, '0 state: 2', 'ACTIVE'))

    def test_audio_events_logs_and_ids(self):
        report = a16(zone='Europe/Paris')
        events = sm.rows(report, 'audio_events')
        self.assertEqual([e.log for e in events][:3], ['audio services lifecycle', 'focus commands as seen by MediaFocusControl',
                                                      'focus commands as seen by MediaFocusControl'])
        focus = events[1]
        self.assertEqual((focus.uid, focus.pid, focus.time_text), (10300, 4321, '11-02 08:50:39.133'))
        recording = [e for e in events if e.log.startswith('recording')][0]
        self.assertEqual((recording.uid, recording.pid), (10301, None))
        dated = [e for e in events if e.log.startswith('volume')][0]
        self.assertEqual(dated.time_text, '2026-11-02 08:58:37.840')
        self.assertEqual(sm.utc_for(report, dated.time_text), utc(2026, 11, 2, 7, 58, 37, 840000))
        self.assertFalse([e for e in events if 'Ringer' in e.text or 'example.flag' in e.text])     # lines outside the logs
        old = sm.rows(a10(), 'audio_events')
        self.assertEqual(len(old), len(events))
        self.assertEqual((old[1].uid, old[1].pid), (10300, 4321))

    def test_audio_clients(self):
        rows = sm.rows(a16(), 'audio_clients')
        self.assertEqual([(r.kind, r.pid, r.uid, r.name, r.session, r.count) for r in rows],
                         [('Notification Clients', 1229, 1041, 'audioserver', None, None),
                          ('Notification Clients', 4321, 10300, 'com.example.user.chat', None, None),
                          ('Global session refs', 2333, 86624, 'example.uid.systemui', 1953, 1)])

    def test_media_sessions_and_playback_order(self):
        report = a16()
        sessions = sm.rows(report, 'media_sessions')
        self.assertEqual([(s.tag, s.role, s.user, s.owner_uid, s.package, s.active) for s in sessions],
                         [('HeadsetMediaButton', 'global priority session', 0, 1000, 'com.example.server.telecom', 'false'),
                          ('Example player', '', 0, 10300, 'com.example.user.chat', 'true')])
        self.assertEqual(sessions[1].key, 'com.example.user.chat/Example player/6')       # a key with a space
        self.assertTrue(sessions[1].state.startswith('PlaybackState {state=PLAYING(3)'))
        self.assertEqual(sessions[1].metadata, 'size=1, description=Example title, Example artist')
        order = sm.rows(report, 'audio_playback')
        self.assertEqual([(o.position, o.uid, o.packages) for o in order],
                         [(1, 10300, 'com.example.user.chat'), (2, 10301, 'com.example.user.sideloaded example.uid.shared')])

    def test_media_metrics_both_forms(self):
        report = a16(zone='Europe/Paris')
        rows = sm.rows(report, 'media_metrics')
        self.assertEqual([(r.number, r.key, r.package, r.pid, r.uid) for r in rows],
                         [(0, 'audio.track.386', 'com.example.user.chat', 4321, 10300), (1, 'codec', 'com.example.user.chat', 0, 10300),
                          (2, 'audio.mode', 'android.uid.system', 0, 1000)])
        self.assertEqual(sm.utc_for(report, rows[0].time_text), utc(2026, 11, 2, 7, 51, 7, 308000))
        old = sm.rows(a10(), 'media_metrics')
        self.assertEqual((old[0].form, old[0].key, old[0].package, old[0].pid, old[0].uid, old[0].time_text),
                         ('colon separated', 'codec', 'com.example.user.chat', 4321, 10300, '1793000000000000000'))
        self.assertTrue(old[0].properties.startswith('android.media.mediacodec.codec=c2.example.decoder'))

    def test_media_metrics_properties_are_capped(self):
        long_value = 'x' * 4000
        text = ('== dumpstate: 2026-01-01 10:00:00\n\n------ DUMPSYS (/system/bin/dumpsys) ------\nDUMP OF SERVICE media.metrics:\n'
                '    0: {codec, (01-01 09:00:00.000), (pkg, 1, 2), (a=%s)}\n' % long_value)
        self.assertEqual(len(sm.rows(scan_text(text), 'media_metrics')[0].properties), sm.PROPERTY_CAP)


class InterfaceTests(unittest.TestCase):
    def test_accessibility_lists(self):
        report = a16()
        rows = sm.rows(report, 'accessibility_services')
        self.assertEqual([(r.user, r.list, r.index, r.component, r.tags) for r in rows],
                         [(0, 'installed', 0, 'com.example.access/.ExampleService', '(A11yTool)'),
                          (0, 'installed', 1, 'com.example.other/com.example.other.SwitchService', ''),
                          (0, 'enabled', 0, 'com.example.access/.ExampleService', '')])
        self.assertEqual(report.__dict__['accessibility_empty'], {'bound', 'binding', 'crashed'})
        self.assertEqual(sm.rows(a10(), 'accessibility_services'), [])

    def test_input_methods_nested_and_flat_layouts(self):
        rows = sm.rows(a16(), 'input_methods')
        self.assertEqual([(r.index, r.method_id, r.package, r.service, r.uid, r.version_code, r.current) for r in rows],
                         [(0, 'com.example.keyboard/.KeyboardService', 'com.example.keyboard', 'com.example.keyboard.KeyboardService',
                           10120, 4242, 'true'),
                          (1, 'com.example.voice/.VoiceService', 'com.example.voice', 'com.example.voice.VoiceService', 10121, None, 'false')])
        self.assertEqual(rows[0].permission, 'android.permission.BIND_INPUT_METHOD')
        old = sm.rows(a10(), 'input_methods')
        self.assertEqual([(r.index, r.uid, r.version_code, r.current) for r in old], [(0, 10120, 4242, 'true')])

    def test_start_input_and_soft_input_histories(self):
        report = a16(zone='Europe/Paris')
        starts = sm.rows(report, 'start_inputs')
        self.assertEqual([(s.entry, s.reason, s.restarting, s.ime, s.target_window, s.input_type, s.field_id, s.field_name) for s in starts],
                         [(11, 'WINDOW_FOCUS_GAIN', 'false', 'com.example.keyboard/.KeyboardService', 'com.example.user.chat', '0x1',
                           '0x7f0a0001', 'search_box'),
                          (12, 'SESSION_CREATED_BY_IME', 'true', 'com.example.keyboard/.KeyboardService',
                           'com.example.user.sideloaded/.MainActivity', '', '', '')])
        self.assertEqual(starts[0].time_text, '2026-11-02 08:20:00.100')
        self.assertEqual(report.clock.to_utc(starts[0].time_text), utc(2026, 11, 2, 7, 20, 0, 100000))
        toggles = sm.rows(report, 'soft_input_toggles')
        self.assertEqual([(t.entry, t.reason, t.uid, t.pid, t.focused_window) for t in toggles],
                         [(7, 'SHOW_SOFT_INPUT', 10300, 4321, 'f750da com.example.user.chat/com.example.user.chat.Main')])
        old = sm.rows(a10(), 'start_inputs')
        self.assertEqual([(s.entry, s.target_window, s.field_id) for s in old], [(5, 'com.example.user.chat', '0xffffffff')])
        self.assertEqual(sm.rows(a10(), 'soft_input_toggles'), [])

    def test_display_states_and_brightness(self):
        report = a16(zone='Europe/Paris')
        states = sm.rows(report, 'display_states')
        self.assertEqual([(s.source, s.display, s.state, s.brightness, s.name, s.size) for s in states],
                         [('Display States', 0, 'ON', '0.25', '', ''), ('Logical Displays', 0, 'ON', '', 'Built-in Screen', '1080 x 2340')])
        events = sm.rows(report, 'brightness_events')
        self.assertEqual([(e.kind, e.state, e.policy, e.brightness, e.nits, e.lux, e.reason, e.strategy) for e in events[:2]],
                         [('BrightnessEvent', 'ON', 'BRIGHT', '0.25', '40.0', '12.5', 'automatic', 'ExampleStrategy'),
                          ('BrightnessEvent', 'OFF', 'DOZE', '0.0', '5.0', '0.0', 'screen_off', '')])
        self.assertEqual((events[2].kind, events[2].state), ('brightness change', ''))
        self.assertTrue(events[2].text.startswith('userId=0, 40.0->45.0, isUserSetBrightness=true'))
        self.assertEqual(sm.rows(a10(), 'brightness_events'), [])
        self.assertEqual([(s.source, s.state) for s in sm.rows(a10(), 'display_states')], [('Logical Displays', 'ON')])

    def test_window_focus_and_windows(self):
        report = a16()
        focus = sm.rows(report, 'window_focus')
        self.assertEqual([(f.display, f.item, f.package) for f in focus],
                         [('0', 'mCurrentFocus', 'com.example.user.chat'), ('0', 'mFocusedApp', 'com.example.user.chat'),
                          ('', 'mTopFocusedDisplayId', ''), ('', 'mInputMethodWindow', '')])
        windows = sm.rows(report, 'windows')
        self.assertEqual([(w.number, w.title, w.display, w.uid, w.package, w.session_pid, w.view_visibility, w.has_surface, w.ready,
                           w.on_screen, w.visible) for w in windows],
                         [(0, 'StatusBarOverlay', '0', 86624, 'com.example.systemui', 2333, '0x4', 'false', 'false', 'false', 'false'),
                          (1, 'com.example.user.chat/com.example.user.chat.Main', '0', 10300, 'com.example.user.chat', 4321, '0x0',
                           'true', 'true', 'true', 'true')])

    def test_surfaceflinger_columns_come_from_the_header(self):
        layers = sm.rows(a16(), 'sf_layers')
        self.assertEqual([(l.display, l.name, l.z, l.window_type, l.composition, l.transform, l.focused) for l in layers],
                         [('0', 'com.example.user.chat/com.example.user.chat.Main#4146', '18', 1, 'CLIENT', 0, 'true'),
                          ('0', 'StatusBar#93', '19', 2000, 'CLIENT', 0, 'false')])
        old = sm.rows(a10(), 'sf_layers')
        self.assertEqual([l.focused for l in old], ['', ''])


class RobustnessTests(unittest.TestCase):
    def test_readers_are_registered_in_the_single_pass(self):
        self.assertTrue(set(sm.READERS) <= set(reader.READERS))
        self.assertEqual(len(reader.READERS), len(set(reader.READERS)))
        self.assertIn(('service', 'media.camera'), reader.READ_BY)
        self.assertIn('Camera Service Events', reader.READ_BY[('service', 'media.camera')])

    def test_empty_and_unrelated_text_gives_no_rows(self):
        report = scan_text(fixture.base.BANNER.format(report='2026-11-02 10:15:30') + '\n')
        self.assertEqual({t: sm.rows(report, t) for t in sm.TABLES if sm.rows(report, t)}, {})

    def test_damaged_lines_do_not_stop_the_pass(self):
        text = fixture.build_report('a16').replace('Request[@+1h0m0s0ms', 'Request[\xff\x00\x0c', 1).replace('pid=', 'pid=²', 1)
        report = scan_text(text.replace('time=2026-11-02 08:20:00.100', 'time=²', 1))
        self.assertTrue(sm.rows(report, 'windows'))
        self.assertTrue(sm.rows(report, 'location_requests'))

    def test_row_cap_is_reported(self):
        body = ''.join('    %d: {k, (01-01 09:00:00.000), (pkg, 1, 2), (a=b)}\n' % n for n in range(5))
        text = ('== dumpstate: 2026-01-01 10:00:00\n\n------ DUMPSYS (/system/bin/dumpsys) ------\nDUMP OF SERVICE media.metrics:\n' + body)
        with mock.patch.object(reader, 'MAX_ROWS', 3):
            report = scan_text(text)
        self.assertEqual(len(sm.rows(report, 'media_metrics')), 3)
        self.assertTrue([w for w in report.warnings if 'media_metrics' in w])

    def test_split_clock(self):
        self.assertEqual(sm.split_clock('10-25 13:07:07:591 text'), ('10-25 13:07:07.591', 'text'))
        self.assertEqual(sm.split_clock('2026-10-25 13:07:07.5 - x'), ('2026-10-25 13:07:07.500', 'x'))
        self.assertEqual(sm.split_clock('no time'), ('', 'no time'))
        report = a16(zone='')
        self.assertIsNone(sm.utc_for(report, '10-25 13:07:07.591'))
        self.assertIsNone(sm.utc_for(report, ''))


class ArtifactTests(unittest.TestCase):
    FUNCTIONS = tuple(getattr(artifacts, name) for name in artifacts.__artifacts_v2__)

    def setUp(self):
        self.work = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        reader.clear_cache()
        self.addCleanup(reader.clear_cache)

    def stage(self, name, text):
        path = Path(self.work) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode('utf-8') if isinstance(text, str) else text)
        return path

    def run_artifact(self, function, *paths):
        return function.__wrapped__(Context(self.work, paths))

    def test_every_artifact_is_defined_and_unique(self):
        names = [info['name'] for info in artifacts.__artifacts_v2__.values()]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(len(self.FUNCTIONS), len(artifacts.__artifacts_v2__))
        for key, info in artifacts.__artifacts_v2__.items():
            self.assertTrue(info['category'].startswith('Android Bug Report - '))
            self.assertEqual(info['paths'], ('*/dumpstate.txt', '*/bugreport-*.txt', '*/bugreport-*.zip', '*/bugreports/bugreport-*.tmp',
                '*/log/*dumpState*.zip', '*/log/dumpstate_*.zip'))
            self.assertTrue(callable(getattr(artifacts, key)))

    def test_row_width_matches_the_headers(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', users=(0, 10)))
        old = self.stage('Dump2/bugreport-example-EXOLD.txt', fixture.build_report('a10'))
        for function in self.FUNCTIONS:
            headers, rows, source_path = self.run_artifact(function, path, old)
            self.assertTrue(rows, function.__name__)
            self.assertTrue(all(len(row) == len(headers) for row in rows), function.__name__)
            self.assertEqual(set(source_path.split('\n')), {str(path), str(old)})

    def test_nothing_to_read(self):
        path = self.stage('Dump/dumpstate.txt', 'not a bug report\n')
        for function in self.FUNCTIONS:
            headers, rows, _source = self.run_artifact(function, path)
            self.assertEqual(rows, [])
            self.assertTrue(headers)

    def test_a_text_without_these_sections_gives_no_rows_and_says_so(self):
        path = self.stage('Dump/dumpstate.txt', fixture.base.BANNER.format(report='2026-11-02 10:15:30'))
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append):
            for function in self.FUNCTIONS:
                self.assertEqual(self.run_artifact(function, path)[1], [])
        self.assertTrue([m for m in messages if 'no media.camera service dump' in m])
        self.assertEqual(len([m for m in messages if 'no location service dump' in m]), 1)    # said once for the five location artifacts

    def test_time_columns(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', zone='Europe/Paris'))
        _h, rows, _s = self.run_artifact(artifacts.bugreport_camera_events, path)
        self.assertEqual((rows[1][0], rows[1][1]), (utc(2026, 11, 2, 8, 30, 30), '11-02 09:30:30'))
        _h, rows, _s = self.run_artifact(artifacts.bugreport_sensor_events, path)
        self.assertEqual(rows[0][0], utc(2026, 10, 30, 7, 0, 0, 100000))
        self.assertEqual(rows[0][2], '')
        old = self.stage('Dump2/bugreport-example-EXOLD.txt', fixture.build_report('a10', zone='Europe/Paris'))
        _h, rows, _s = self.run_artifact(artifacts.bugreport_sensor_events, old)
        self.assertEqual((rows[0][0], rows[0][1], rows[0][2]), (None, '08:00:00.100', 'clock time without a date: no UTC value'))
        _h, rows, _s = self.run_artifact(artifacts.bugreport_media_metrics, old)
        self.assertEqual(rows[0][0], utc(2026, 10, 26, 7, 33, 20))         # 1793000000 seconds
        self.assertEqual(rows[0][1], '1793000000000000000')

    def test_last_known_location_columns_are_text_as_printed(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        headers, rows, _s = self.run_artifact(artifacts.bugreport_location_last_known, path)
        gps = [row for row in rows if row[1] == 'gps'][0]
        self.assertEqual(dict(zip(headers, gps))['Latitude (as printed)'], '12.340000')
        self.assertEqual(dict(zip(headers, gps))['Elapsed Time (as printed)'], '+1h0m0s0ms')
        self.assertFalse([h for h in headers if isinstance(h, tuple)])     # no datetime column, no map output

    def test_a_dump_cut_by_the_platform_is_logged_once(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16', cut=True))
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append):
            for function in (artifacts.bugreport_location_providers, artifacts.bugreport_location_events,
                             artifacts.bugreport_sensors, artifacts.bugreport_sensor_events):
                self.run_artifact(function, path)
        self.assertEqual(len([m for m in messages if 'location service dump was cut by a 10000 ms timeout' in m]), 1)
        self.assertEqual(len([m for m in messages if 'sensorservice service dump was cut by a 10000 ms timeout' in m]), 1)

    def test_empty_accessibility_lists_are_logged(self):
        path = self.stage('Dump/dumpstate.txt', fixture.build_report('a16'))
        messages = []
        with mock.patch.object(artifacts, 'logfunc', messages.append):
            self.run_artifact(artifacts.bugreport_accessibility_services, path)
        self.assertTrue([m for m in messages if 'bound accessibility services list was printed empty' in m])
        self.assertFalse([m for m in messages if 'enabled accessibility services list was printed empty' in m])

    def test_two_reports_give_both_sets_of_rows(self):
        first = self.stage('Dump1/dumpstate.txt', fixture.build_report('a16'))
        second = self.stage('Dump2/bugreport-example-EXOLD.txt', fixture.build_report('a10'))
        alone = len(self.run_artifact(artifacts.bugreport_windows, first)[1])
        both = self.run_artifact(artifacts.bugreport_windows, first, second)[1]
        self.assertEqual(len(both), alone * 2)
        self.assertEqual({row[-1] for row in both}, {'Dump1/dumpstate.txt', 'Dump2/bugreport-example-EXOLD.txt'})


if __name__ == '__main__':
    unittest.main()
