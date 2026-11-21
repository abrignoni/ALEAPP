"""Builds the synthetic Android bug report texts used by the sensors and media test cases.

Every value is invented: package names are under example.*, the coordinates, uids, pids, times and
window names are made up. Only the structure is taken from real bug reports (the section headings, the
line layouts of the location, sensorservice, media.camera, audio, media_session, media.metrics,
accessibility, input_method, display, window and SurfaceFlinger dumps). The text is added to the text
that ``bugreport_fixture`` builds, before its closing line. Two layouts are built:

* ``a16``: the layout of Android 12 and later (Location Manager State, the nested input method lists,
  month-day times in the sensor lists, name-time-owner media metrics records);
* ``a10``: the layout of Android 10 (Current Location Manager state, clock-time-only sensor events,
  colon separated media metrics records, the older audio log headings).

Usage: python bugreport_sensorsmedia_fixture.py <output folder>
Writes one zip per test case into the folder and prints their names and sizes.
"""
import os
import sys

from admin.test.scripts import bugreport_fixture as base

DONE = '== dumpstate: done (id 1)\n'
CHAT = 'com.example.user.chat'
SIDE = 'com.example.user.sideloaded'


def service(name, body, cut=False, seconds='0.100'):
    """One ``DUMP OF SERVICE`` section with its trailer (or the timeout marker the platform prints when it cuts a dump)."""
    text = 'DUMP OF SERVICE %s:\n%s' % (name, body if body.endswith('\n') else body + '\n')
    if cut:
        return text + "*** SERVICE '%s' DUMP TIMEOUT (10000ms) EXPIRED ***\n\n" % name
    return text + '--------- %ss was the duration of dumpsys %s, ending at: 2026-11-02 10:15:20\n\n' % (seconds, name)


# ------------------------------------------------------------------------------------------
# location
# ------------------------------------------------------------------------------------------
def location_new():
    return (
        'Service host process PID: 2682\nThreads in use: 0/32\nClient PIDs: 466, 467\n'
        'Location Manager State:\n'
        '  User Info:\n    running users: u[0, 10]\n    current users: u[0, 10]\n'
        '  Location Settings:\n    Location Setting: \n      [u0] true\n      [u10] false\n'
        '  Location Providers:\n'
        '    passive provider:\n      service: registered\n      listeners:\n'
        '        10300/%(chat)s[chat_location]/AB12CD34 {bg} Request[@+1h0m0s0ms BALANCED, minUpdateInterval=+30s0ms, '
        'minUpdateDistance=100.0, WorkSource{10300 %(chat)s}]\n'
        '        1000/android[ExampleService]/EF56AA11 (COARSE) Request[PASSIVE, minUpdateInterval=0, hiddenFromAppOps, '
        'WorkSource{1000 android}]\n'
        '      user 0:\n        last location=Location[fused 12.345678,-45.678901 hAcc=25.0 et=+2h3m4s500ms]\n        enabled=true\n'
        '      user 10:\n        last location=Location[fused 12.345678,-45.678901 hAcc=25.0 et=+2h3m4s500ms]\n        enabled=false\n'
        '      allowed=true\n      identity=1000/android[LocationService]\n'
        '      properties=ProviderProperties[powerUsage=Low, accuracy=Fine]\n'
        '    network provider:\n      service: ProviderRequest[OFF]\n      user 0:\n        enabled=true\n'
        '      allowed=true\n      identity=10301/%(side)s[network_provider]\n      target service=10301/%(side)s/.NetService@2\n'
        '      connected=true\n      stationary throttled=false (not idle) (not stationary)\n'
        '    gps provider:\n      service: ProviderRequest[OFF]\n'
        '      last location=Location[gps 12.340000,-45.670000 hAcc=4.5 et=+1h0m0s0ms alt=10.0]\n      enabled=true\n'
        '      allowed=true\n      identity=1000/android[GnssService]\n      mStarted=false   (changed +3m0s0ms ago)\n'
        '  Historical Aggregate Location Provider Data:\n    passive:\n'
        '      10300/%(chat)s[chat_location]: min/max interval = 0s/3600s, total/active/foreground duration = '
        '+1h0m0s0ms/+59m0s0ms/+10m0s0ms, locations = 7\n'
        '    gps:\n      1000/android[GnssService]: min/max interval = 1s/passive, total/active/foreground duration = '
        '+2h0m0s0ms/+1h0m0s0ms/+2h0m0s0ms, locations = 0\n'
        '  Geofence Manager:\n    service: unregistered\n'
        '  Event Log:\n'
        '    11-02 08:30:00.123: passive provider [u0] enabled\n'
        '    11-02 08:31:10.000: passive provider +registration 10300/%(chat)s[chat_location]/AB12CD34 -> '
        'Request[@+1h0m0s0ms BALANCED, WorkSource{10300 %(chat)s}]\n'
        '    11-02 08:31:11.500: passive provider request = ProviderRequest[@+1h0m0s0ms, BALANCED, WorkSource{10300 %(chat)s}]\n'
        '    11-02 08:40:00.000: passive provider delivered location[1] to 10300/%(chat)s[chat_location]/AB12CD34\n'
        '    11-02 09:00:00.000: passive provider -registration 10300/%(chat)s[chat_location]/AB12CD34\n'
        '    11-02 09:00:01.000: [u0] visible\n' % {'chat': CHAT, 'side': SIDE})


def location_old():
    return (
        'Current Location Manager state:\n  Current System Time: 11-02 10:15:20.000, Current Elapsed Time: +1h0m14s663ms\n'
        '  Current user: 0 [0]\n  Location mode: true\n'
        '  Location Listeners:\n'
        '    Reciever[46afe7 listener UpdateRecord[passive %(chat)s(10300 foreground) Request[POWER_NONE passive fastest=0] null] '
        'monitoring location: false]\n'
        '  Active Records by Provider:\n    gps:\n    passive:\n'
        '      UpdateRecord[passive android(1000 foreground) Request[POWER_NONE passive fastest=+30m0s0ms] null]\n'
        '      UpdateRecord[passive %(chat)s(10300 background) Request[POWER_LOW passive requested=0 fastest=0] '
        'WorkSource{10301 %(side)s}]\n'
        '    network:\n'
        '  Historical Records by Provider:\n'
        '    %(chat)s: gps: Interval 2 seconds: Duration requested 0 total, 0 foreground, out of the last 59 minutes: '
        'Last active 59 minutes ago\n'
        '    android: passive: Min interval 0 seconds: Max interval 1800 seconds: Duration requested 59 total, 59 foreground, '
        'out of the last 59 minutes: Currently active\n'
        '  Last Known Locations:\n    fused: Location[fused 12******,-45****** hAcc=30 et=+53m9s204ms alt=297.0 {Bundle[x]}]\n'
        '    network: Location[network 12******,-45****** hAcc=68 et=+55m20s796ms]\n'
        '  Last Known Locations Coarse Intervals:\n    fused: Location[fused 12******,-45****** hAcc=40 et=+51m8s126ms]\n'
        '  Geofences:\n'
        '  passive provider:\n    useable=true\n    properties=com.android.internal.location.ProviderProperties@f9e17f6\n'
        ' report location=true\n'
        '  gps provider:\n    useable=true\n    properties=com.android.internal.location.ProviderProperties@db6b314\n'
        '  mStarted=false   (changed +59m34s287ms ago)\n'
        '  network provider:\n    useable=false\n    enabled=false\n' % {'chat': CHAT, 'side': SIDE})


def time_zone():
    return (
        'Service host process PID: 2682\nLocationTimeZoneManagerService:\n'
        '  Primary provider config:\n    getMode()=enabled\n    getPackageName()=com.example.geotz\n'
        '  Secondary provider config:\n    getMode()=disabled\n    getPackageName()=\n'
        '  LocationTimeZoneProviderController:\n'
        '    mCurrentUserConfiguration=ConfigurationInternal{mUserId=0, mGeoDetectionEnabledSetting=true}\n'
        '    providerInitializationTimeout=PT5M\n    mState=CERTAIN\n'
        '    State history:\n      0@PT21.171S: UNKNOWN\n      1@PT21.175S: STOPPED\n      2@PT1H16M45.024S: CERTAIN\n'
        '    Primary Provider:\n      {BinderLocationTimeZoneProvider}\n      mProviderName=primary\n'
        '      mCurrentState=ProviderState{stateEnum=Started certain (2), mTimeZoneIds=[Example/Zone]}\n'
        '      State history:\n        0@PT21.172S: ProviderState{stateEnum=Stopped (4)}\n'
        '        1@PT1H16M45.023S: ProviderState{stateEnum=Started certain (2)}\n'
        '      Proxy details:\n        target service=10301/com.example.geotz/.GeoService@1\n        connected=true\n'
        '    Secondary Provider:\n      {DisabledLocationTimeZoneProvider}\n      mProviderName=secondary\n'
        '      mCurrentState=ProviderState{stateEnum=Perm failure (5)}\n')


# ------------------------------------------------------------------------------------------
# sensors
# ------------------------------------------------------------------------------------------
def sensors(layout):
    new = layout == 'a16'
    text = ('Service host process PID: 1852\nThreads in use: 0/32\nClient PIDs: 1\nCaptured at: 10:15:20.000\n'
            'Sensor Device:\nTotal 3 h/w sensors, 3 running 0 disabled clients:\n'
            '0x00000001) active-count = 1; sampling_period(ms) = {80.0}, selected = 80.00 ms; batching_period(ms) = {2000.0}, '
            'selected = 2000.00 ms\n'
            'Example Light  Non-wakeup(handle=0x00000005)  active-count = 2; sampling_period(ms) = {250.0, 200.0}, selected = '
            '200.00 ms; batching_period(ms) = {0.0, 0.0}, selected = 0.00 ms\n'
            'Sensor List:\n'
            '%s) example_acc               | example         | ver: 1 | type: android.sensor.accelerometer(1) | perm: n/a | '
            'flags: 0x00000000\n\tcontinuous | minRate=12.50Hz | maxRate=400.00Hz | FIFO (max,reserved) = (4500, 3000) events | '
            'non-wakeUp | \n'
            '0x00000005) example_light             | example         | ver: 1 | type: android.sensor.light(5) | perm: n/a | '
            'flags: 0x00000002\n\ton-change | minRate=1.00Hz | minDelay=0us | no batching | non-wakeUp | \n'
            '0x00000012) example_steps             | example         | ver: 1 | type: android.sensor.step_detector(18) | '
            'perm: android.permission.ACTIVITY_RECOGNITION | flags: 0x00000006\n\tspecial-trigger | maxDelay=0us | minDelay=0us | '
            'no batching | wakeUp | \n'
            'Fusion States:\n9-axis fusion disabled (0 clients)\n'
            'Recent Sensor events:\n' % ('0x00000001' if new else '0000000001'))
    wall = (lambda a, b: '10-' + a) if new else (lambda a, b: b)
    text += ('example_light: last 2 events\n\t 1 (ts=100.500000000, wall=%s) 12.00, 0.00, 0.00, \n'
             '\t 2 (ts=160.250000000, wall=%s) 40.00, 0.00, 0.00, \n'
             'example_steps: last 1 events\n\t 1 (ts=170.000000000, wall=%s) 1.00, 0.00, \n'
             % (wall('30 08:00:00.100', '08:00:00.100'), wall('30 08:01:00.200', '08:01:00.200'),
                wall('30 08:02:00.300', '08:02:00.300')))
    text += ('Active sensors:\nexample_acc (handle=0x00000001, connections=1)\nexample_light (handle=0x00000005, connections=2)\n'
             'Socket Buffer size = 984 events\nWakeLock Status: not held \nMode : NORMAL\nSensor Privacy: disabled\n'
             '4 active connections\n'
             'Connection Number: 0 \n\tOperating Mode: NORMAL\n\t com.example.server.Brightness$2 | WakeLockRefCount 0 | uid 1000 | '
             'cache size 0 | max cache size 0\n\t example_light 0x00000005 | status: active | pending flush events 0 \n'
             'Connection Number: 1 \n\tOperating Mode: NORMAL\n\t ab1 | WakeLockRefCount 0 | uid 10300 | cache size 0 | '
             'max cache size 0\n\t example_acc 0x00000001 | status: active | pending flush events 2 \n'
             '\t example_steps 0x00000012 | status: active | pending flush events 0 \n'
             'Connection Number: 2 \n\tOperating Mode: NORMAL\n \n\t com.example.server.Grip | WakeLockRefCount 0 | uid 1000 | '
             'cache size 0 | max cache size 0 | has sensor access: true\n'
             '\t Example Grip Sensor 0x02000012 | first flush pending: false | pending flush events 3 \n'
             'Connection Number: 3 \n\tOperating Mode: NORMAL\n'
             '0 direct connections\nPrevious Registrations:\n')
    if new:
        text += ('08:02:00 - 0x00000001 pid= 2682 uid= 1000 samplingPeriod=   N/A  us batchingPeriod=   N/A  us result=OK '
                 '(sensor, package): (example_acc Accelerometer Non-wakeup, com.example.server.Orientation)\n'
                 '08:01:00 + 0x00000001 pid= 4321 uid=10300 samplingPeriod=   20000us batchingPeriod= 5000000us result=OK '
                 '(sensor, package): (example_acc Accelerometer Non-wakeup, %s.collect.Scanner)\n' % CHAT)
    else:
        text += ('08:02:00 - 0x00000001 pid= 2682 uid= 1000 package=com.example.server.Orientation\n'
                 '08:01:00 + 0x00000001 pid=4321 uid=10300 package=%s.collect.Scanner samplingPeriod=20000us '
                 'batchingPeriod=0us\n' % CHAT)
    return text


# ------------------------------------------------------------------------------------------
# camera, audio, media
# ------------------------------------------------------------------------------------------
def camera(layout):
    new = layout == 'a16'
    text = ('Service host process PID: 1471\n\n== Service global info: ==\n\nNumber of camera devices: 2\n'
            '    Device 0 maps to "0"\n    Device 1 maps to "1"\nActive Camera Clients:\n[]\nAllowed user IDs: 0\n\n'
            '== Camera service events log (most recent at top): ==\n'
            '  11-02 09:30:35 : DISCONNECT device 0 client for package %(chat)s (PID 4321)\n'
            '  11-02 09:30:30 : CONNECT device 0 client for package %(chat)s (PID 4321%(prio)s)\n'
            '  11-02 08:00:00 : USER_SWITCH previous allowed user IDs: <None>, current allowed user IDs: 0\n'
            '  11-02 07:59:59 : ADD device 0, reason: (Device added)\n' % {'chat': CHAT, 'prio': ', priority 0' if new else ''})
    if new:
        text += '  11-02 07:59:50 : Device State was changed from FOLDED(0x6) to OPEN(0x1)\n'
    text += ('\n== Camera device 0 dynamic info: ==\n  Device 0 is closed, no client instance\n'
             '== Camera device 1 dynamic info: ==\n  Device 1 is closed, no client instance\n'
             '== Camera Provider HAL internal/0-0 (v2.6, remote) static info: 2 devices: ==\n'
             '== Camera error traces (0): ==\n')
    if new:
        text += ('**********Dumpsys from previous open session**********\n== Camera device 1 dynamic info: ==\n'
                 '  11-02 09:00:44 : Device 1 is open. Client instance dump:\n    Client priority score: 0 state: 2\n'
                 '    Client PID: 4322\n    Client package: %s\n  CameraDeviceClient[1] (0xa85678ce1970e422) dump:\n'
                 '    Current client UID 10300\n  Device dump:\n    Device status: ACTIVE\n' % CHAT)
    return text


def audio(layout):
    head = 'Events log: ' if layout == 'a16' else 'Audio event log: '
    return ('Service host process PID: 1852\n' + head + 'audio services lifecycle\n11-02 06:00:00:375 AudioService()\n\n'
            'Fun with Flags:\n\texample.flag:false\n\n' + head + 'focus commands as seen by MediaFocusControl\n'
            '11-02 08:50:39:133 abandonAudioFocus() from uid/pid%s10300/4321 clientId=android.media.AudioManager@b49d003\n'
            '11-02 08:50:39:732 requestAudioFocus() from uid/pid%s10300/4321 AA=USAGE_MEDIA/CONTENT_TYPE_UNKNOWN '
            'clientId=android.media.AudioManager@b49d003\n\n' % (':' if layout == 'a16' else ' ', ':' if layout == 'a16' else ' ') +
            'Ringer mode: \n- mode (internal) = NORMAL\n\n' + head + 'playback activity as reported through PlayerBase\n'
            '11-02 08:51:07:591 new player piid:4223 uid/pid:10300/4321 type:android.media.MediaPlayer\n'
            '11-02 08:51:08:028 player piid:4223 event:stopped\n\n' + head + 'recording activity received by AudioService\n'
            '11-02 08:52:56:782 rec start riid:-1 uid:10301 session:137 src:HOTWORD not silenced pack:\n\n'
            + head + 'volume changes (logged when command received by AudioService)\n'
            '2026-11-02 08:58:37:840 adjustSuggestedStreamVolume(sugg:STREAM_MUSIC dir:ADJUST_RAISE) from android/android uid:1000\n')


def audio_flinger():
    return ('Libraries loaded:\n  example.so\n'
            'Notification Clients:\n   pid    uid  name\n  1229   1041  audioserver\n  4321  10300  %s\n\n'
            'Global session refs:\n  session  cnt     pid    uid  name\n      1953    1    2333  86624  example.uid.systemui\n'
            'Hardware status: 0\n' % CHAT)


def media_session(layout):
    key = 'com.example.server.telecom/HeadsetMediaButton' + ('/1' if layout == 'a16' else '')
    return ('MEDIA SESSION SERVICE (dumpsys media_session)\n\n2 sessions listeners.\n'
            'Global priority session is %(key)s (userId=0)\n'
            '  HeadsetMediaButton %(key)s (userId=0)\n    ownerPid=1852, ownerUid=1000, userId=0\n'
            '    package=com.example.server.telecom\n    active=false\n    flags=65537\n    state=null\n'
            '    audioAttrs=AudioAttributes: usage=USAGE_VOICE_COMMUNICATION content=CONTENT_TYPE_SPEECH flags=0x800\n'
            '    volumeType=LOCAL, controlType=ABSOLUTE, max=0, current=0, volumeControlId=null\n    metadata: null\n'
            '  Example player %(chat)s/Example player/6 (userId=0)\n    ownerPid=4321, ownerUid=10300, userId=0\n'
            '    package=%(chat)s\n    active=true\n    flags=3\n    state=PlaybackState {state=PLAYING(3), position=0}\n'
            '    metadata: size=1, description=Example title, Example artist\n'
            'User Records:\nRecord for full_user=0, profile_user=10\n'
            'Audio playback (lastly played comes first)\n  uid=10300 packages=%(chat)s \n'
            '  uid=10301 packages=%(side)s example.uid.shared \nMedia session config:\n  x: [cur: 1, def: 1]\n'
            % {'key': key, 'chat': CHAT, 'side': SIDE})


def media_metrics(layout):
    if layout == 'a16':
        return ('Dump of the media.metrics process:\nMetrics gathering: enabled\nSince Boot: Submissions: 12 Accepted: 12\n'
                '    0: {audio.track.386, (11-02 08:51:07.308), (%(chat)s, 4321, 10300), (event#=start, state=STATE_ACTIVE)}\n'
                '    1: {codec, (11-02 08:51:07.838), (%(chat)s, 0, 10300), (android.media.mediacodec.codec=c2.example.decoder, '
                'android.media.mediacodec.mode=audio)}\n'
                '    2: {audio.mode, (11-02 08:52:00.000), (android.uid.system, 0, 1000), (event#=set, mode=MODE_NORMAL)}\n'
                % {'chat': CHAT})
    return ('Dump of the media.metrics process:\nProtocol Version: 1\nMetrics gathering: enabled\n\nFinalized Metrics (oldest first):\n'
            '    0: [1:codec:35:10300:%(chat)s:100110016:4321:1:1793000000000000000:2:android.media.mediacodec.codec=c2.example.'
            'decoder:android.media.mediacodec.mode=audio:]\n'
            '    1: [1:extractor:36:1013:media:5:1048:1:1793000060000000000:1:android.media.mediaextractor.fmt=ExampleExtractor:]\n'
            % {'chat': CHAT})


def accessibility():
    return ('ACCESSIBILITY MANAGER (dumpsys accessibility)\n\ncurrentUserId=0\nhasMagnificationConnection=false\nUser state[\n'
            '     attributes:{id=0}\n\n     installed services: {\n'
            '      0 : com.example.access/.ExampleService  (A11yTool)\n'
            '      1 : com.example.other/com.example.other.SwitchService\n     }\n'
            '     Bound services:{}\n     Enabled services:{{com.example.access/.ExampleService}}\n     Binding services:{}\n'
            '     Crashed services:{}\n')


# ------------------------------------------------------------------------------------------
# input method, display, window, SurfaceFlinger
# ------------------------------------------------------------------------------------------
def input_method(layout):
    if layout == 'a16':
        return ('Input Method Manager Service state:\n  mSystemReady=true\n  mStartInputHistory:\n'
                '    StartInput #11:\n      time=2026-11-02 08:20:00.100 (timestamp=1000) reason=WINDOW_FOCUS_GAIN restarting=false\n'
                '      imeToken=android.os.Binder@1 [com.example.keyboard/.KeyboardService] imeUserId=0 imeDisplayId=0\n'
                '      targetWin=android.os.BinderProxy@2 [%(chat)s] targetUserId=0 targetDisplayId=0 clientBindSeq=12\n'
                '      softInputMode=STATE_UNSPECIFIED|ADJUST_RESIZE\n'
                '      inputType=0x1 imeOptions=0x2 fieldId=0x7f0a0001 fieldName=search_box actionId=0 actionLabel=null\n'
                '    StartInput #12:\n      time=2026-11-02 08:21:00.200 (timestamp=1100) reason=SESSION_CREATED_BY_IME restarting=true\n'
                '      imeToken=android.os.Binder@1 [com.example.keyboard/.KeyboardService] imeUserId=0 imeDisplayId=0\n'
                '      targetWin=android.os.BinderProxy@3 [%(side)s/.MainActivity] targetUserId=0 targetDisplayId=0 clientBindSeq=13\n'
                '  mSoftInputShowHideHistory:\n'
                '    SoftInputShowHide[0] #7:\n      time=2026-11-02 08:20:05.362 (timestamp=1200)\n'
                '      reason=SHOW_SOFT_INPUT inFullscreenMode=false\n'
                '      requestClient=ClientState{f937021 mUid=10300 mPid=4321 mSelfReportedDisplayId=0}\n'
                '      focusedWindowName=f750da %(chat)s/%(chat)s.Main\n'
                '      imeControlTargetName=f750da %(chat)s/%(chat)s.Main\n'
                '      editorInfo: inputType=1 privateImeOptions=null fieldId (viewId)=1\n'
                '  mSoftInputShowHideHistory End\n'
                '  UserId=0\n    mSelectedMethodId=com.example.keyboard/.KeyboardService\n'
                '    Input Methods:\n      InputMethod #0:\n'
                '        mId=com.example.keyboard/.KeyboardService mSettingsActivityName=com.example.keyboard.Settings mIsVrOnly=false\n'
                '        Service:\n          ServiceInfo:\n            name=com.example.keyboard.KeyboardService\n'
                '            packageName=com.example.keyboard\n            permission=android.permission.BIND_INPUT_METHOD\n'
                '            ApplicationInfo:\n              uid=10120 flags=0x1\n'
                '              enabled=true minSdkVersion=29 targetSdkVersion=36 versionCode=4242 targetSandboxVersion=1\n'
                '      InputMethod #1:\n        mId=com.example.voice/.VoiceService mSettingsActivityName=null\n'
                '        Service:\n          ServiceInfo:\n            name=com.example.voice.VoiceService\n'
                '            packageName=com.example.voice\n            ApplicationInfo:\n              uid=10121 flags=0x1\n'
                % {'chat': CHAT, 'side': SIDE})
    return ('Current Input Method Manager state:\n  Input Methods: mMethodMapUpdateCount=3\n  InputMethod #0:\n'
            '    mId=com.example.keyboard/.KeyboardService mSettingsActivityName=com.example.keyboard.Settings\n'
            '    mIsDefaultResId=0x0\n    Service:\n      ServiceInfo:\n        name=com.example.keyboard.KeyboardService\n'
            '        packageName=com.example.keyboard\n        permission=android.permission.BIND_INPUT_METHOD\n'
            '        ApplicationInfo:\n          uid=10120 flags=0x1\n'
            '          enabled=true minSdkVersion=26 targetSdkVersion=29 versionCode=4242 targetSandboxVersion=1\n'
            '  Clients:\n  Client ClientState{40f9fd2 uid=1000 pid=84498 displayId=0}:\n    sessionRequested=false\n'
            '  mCurMethodId=com.example.keyboard/.KeyboardService\n'
            '  mStartInputHistory:\n    StartInput #5:\n'
            '      time=2026-11-02 08:20:00.100 (timestamp=1000) reason=WINDOW_FOCUS_GAIN restarting=false\n'
            '      imeToken=android.os.Binder@1 [com.example.keyboard/.KeyboardService] imeUserId=0 imeDisplayId=0\n'
            '      targetWin=android.os.BinderProxy@2 [%s] targetUserId=0 targetDisplayId=0 clientBindSeq=6\n'
            '      softInputMode=STATE_ALWAYS_HIDDEN|ADJUST_RESIZE\n'
            '      inputType=0x0 imeOptions=0x0 fieldId=0xffffffff fieldName=null actionId=0 actionLabel=null\n'
            '  mService=com.android.internal.view.IInputMethodManager$Stub$Proxy@43c624c\n' % CHAT)


def display(layout):
    text = 'DISPLAY MANAGER (dumpsys display)\n  mSafeMode=false\n\n'
    if layout == 'a16':
        text += ('Display States: size=1\n---------------------\n  Display Id=0\n  Display State=ON\n'
                 '  Display Brightness=0.25\n  Display SdrBrightness=0.25\n\nDisplay State Overrides: size=1\n'
                 '  Display Id=0\n  Display State Override=UNKNOWN\n\n')
    text += ('Logical Displays: size=1\n  Display 0:\n    mDisplayId=0\n    mPrimaryDisplayDevice=Built-in Screen\n'
             '    mBaseDisplayInfo=DisplayInfo{"Built-in Screen", displayId 0, real 1080 x 2340, rotation 0, state ON, '
             'brightnessMinimum 0.0}\n\n')
    if layout == 'a16':
        text += ('Display Power Controller:\n'
                 '  11-02 08:00:00.100 - BrightnessEvent: disp=0, physDisp=local:0, displayState=ON, displayPolicy=BRIGHT, '
                 'brt=0.25, brtNits=40.0, lux=12.5, reason=automatic, strat=ExampleStrategy, flags=\n'
                 '  11-02 08:30:00.200 - BrightnessEvent: disp=0, physDisp=local:0, displayState=OFF, displayPolicy=DOZE, '
                 'brt=0.0, brtNits=5.0, lux=0.0, reason=screen_off\n'
                 '  10-30 12:00:00.300, userId=0, 40.0->45.0, isUserSetBrightness=true, powerBrightnessFactor=1.0\n')
    return text


def window():
    return ('WINDOW MANAGER LAST ANR (dumpsys window lastanr)\n  <no ANR has occurred since boot>\n\n'
            '-------------------------------------------------------------------------------\n'
            'WINDOW MANAGER DISPLAY CONTENTS (dumpsys window displays)\n  Display: mDisplayId=0 (organized)\n'
            '    init=1080x2340 cur=1080x2340\n'
            '  mCurrentFocus=Window{94913b7 u0 %(chat)s/%(chat)s.Main}\n'
            '  mFocusedApp=ActivityRecord{2fe6c62 u0 %(chat)s/.Main t28709}\n'
            '  mTopFocusedDisplayId=0\n  mInputMethodWindow=Window{237e85c u0 InputMethod}\n'
            'WINDOW MANAGER WINDOWS (dumpsys window windows)\n'
            '  Window #0 Window{b7fccea u0 StatusBarOverlay}:\n'
            '    mDisplayId=0 rootTaskId=1 mSession=Session{495ae2e 2333:u0a10385} mClient=android.os.BinderProxy@bcf9805\n'
            '    mOwnerUid=86624 showForAllUsers=true package=com.example.systemui appop=NONE\n'
            '    mViewVisibility=0x4 mHaveFrame=true mObscured=false\n'
            '    mHasSurface=false isReadyForDisplay()=false mWindowRemovalAllowed=false\n'
            '    isOnScreen=false\n    isVisible=false\n'
            '  Window #1 Window{94913b7 u0 %(chat)s/%(chat)s.Main}:\n'
            '    mDisplayId=0 rootTaskId=7 mSession=Session{1 4321:u0a10300} mClient=android.os.BinderProxy@1\n'
            '    mOwnerUid=10300 showForAllUsers=false package=%(chat)s appop=NONE\n'
            '    mViewVisibility=0x0 mHaveFrame=true mObscured=false\n'
            '    mHasSurface=true isReadyForDisplay()=true mWindowRemovalAllowed=false\n'
            '    isOnScreen=true\n    isVisible=true\n'
            'WINDOW MANAGER TRACE (dumpsys window trace)\nStatus: Disabled\n' % {'chat': CHAT})


def surfaceflinger(layout):
    focus = ' |     Frame Rate (Explicit) (Seamlessness) [Focused]' if layout == 'a16' else ''
    mark = lambda flag: (' |                                              [%s]' % flag) if layout == 'a16' else ''
    return ('Display identification data:\nDisplay 0 (HWC display 0): no display identification data\n'
            'Display 0 (active) HWC layers:\n'
            '---------------------------------------------------------------------------------------------\n'
            ' Layer name\n'
            '           Z |  Window Type |  Comp Type |  Transform |   Disp Frame (LTRB) |          Source Crop (LTRB)%s\n'
            '---------------------------------------------------------------------------------------------\n'
            ' %s/%s.Main#4146\n'
            '          18 |            1 |     CLIENT |          0 |    0    0 1080 2340 |    0.0    0.0 1080.0 2340.0%s\n'
            '---------------------------------------------------------------------------------------------\n'
            ' StatusBar#93\n'
            '          19 |         2000 |     CLIENT |          0 |    0    0 1080  117 |    0.0    0.0 1080.0  117.0%s\n'
            '---------------------------------------------------------------------------------------------\n\n'
            'Displays (1 entries)\nDisplay 0\n' % (focus, CHAT, CHAT, mark('*'), mark(' ')))


def sections(layout='a16', cut=False):
    """The text of the added dumpsys group."""
    text = '------ DUMPSYS (/system/bin/dumpsys) ------\n'
    text += service('location', location_new() if layout == 'a16' else location_old(), cut=cut)
    if layout == 'a16':
        text += service('location_time_zone_manager', time_zone())
    text += service('sensorservice', sensors(layout), cut=cut)
    text += service('media.camera', camera(layout))
    text += service('audio', audio(layout))
    if layout == 'a16':
        text += service('media.audio_flinger', audio_flinger())
    text += service('media_session', media_session(layout))
    text += service('media.metrics', media_metrics(layout))
    if layout == 'a16':
        text += service('accessibility', accessibility())
    text += service('input_method', input_method(layout))
    text += service('display', display(layout))
    text += service('window', window())
    text += service('SurfaceFlinger', surfaceflinger(layout))
    return text + "------ 0.900s was the duration of 'DUMPSYS' ------\n\n"


def build_report(layout='a16', newline='\n', cut=False, **kwargs):
    """The base fixture text of ``layout`` with the sensors and media dumps added before its closing line."""
    kwargs.setdefault('stamp_count', 3)       # a short package list: these cases are about the other dumps
    kwargs.setdefault('bulk_count', 3)
    text = base.build_report(layout, newline='\n', **kwargs)
    at = text.rindex(DONE)
    return (text[:at] + sections(layout, cut) + text[at:]).replace('\n', newline)


def cases():
    """{case name: [(member name, bytes), ...]}"""
    out = {}
    out['synthetic_a16'] = [('Dump/dumpstate.txt', build_report('a16', users=(0, 10)).encode('utf-8'))]
    out['synthetic_a10'] = [('Dump/bugreport-example-EXOLD-2026-11-02-10-15-30.txt',
                             build_report('a10', newline='\r\n').encode('utf-8')),
                            ('Dump/main_entry.txt', b'bugreport-example-EXOLD-2026-11-02-10-15-30.txt')]
    out['synthetic_cut'] = [('Dump/dumpstate.txt', build_report('a16', cut=True).encode('utf-8'))]
    out['synthetic_empty'] = [('Dump/dumpstate.txt', (base.BANNER.format(report='2026-11-02 10:15:30') + '\n').encode())]
    out['synthetic_two_reports'] = [
        ('Dump1/dumpstate.txt', build_report('a16', zone='Asia/Kolkata').encode('utf-8')),
        ('Dump2/bugreport-example-EXOLD-2026-11-02-10-15-30.txt', build_report('a10', zone='America/Sao_Paulo').encode('utf-8'))]
    return out


def main(output):
    os.makedirs(output, exist_ok=True)
    for name, members in cases().items():
        base.write_zip(os.path.join(output, name + '.zip'), members)
    for name in sorted(os.listdir(output)):
        print(name, os.path.getsize(os.path.join(output, name)))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'bugreport_sensorsmedia_fixture_out')
