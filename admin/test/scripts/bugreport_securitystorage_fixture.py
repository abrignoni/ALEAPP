"""Builds the synthetic Android bug report texts used by the security and storage test cases.

Every value is invented: package names are under example.*, protector ids, SIDs, device ids and user
names are made up, times and sizes are fixed. Only the layout is taken from real bug reports: the
section headings, the service dump trailers and the shape of each dump. Two layouts are built:

* ``new``: the layout of Android 14 and later (device policy with the policy engine, lock settings
  with a protector state and a log, biometric services with the session coordinator log, mount
  service with storage volumes and the vold log, dbinfo with operation times without a year, device
  config, platform compat, build time release flags and SDK extensions);
* ``old``: the layout of Android 10 (an empty admin list, the short lock settings dump, a trust
  state with wall clock events, df without inode counts, dbinfo with full dates, no flags).

The text is added to the base report of ``bugreport_fixture`` (banner, header and system properties
with the time zone) before the closing marker.

Usage: python bugreport_securitystorage_fixture.py <output folder>
Writes one zip per test case into the folder and prints their names and sizes.
"""
import json
import os
import sys

from admin.test.scripts import bugreport_fixture as base

SERVICE_END = '--------- 0.100s was the duration of dumpsys %s, ending at: 2026-11-02 10:15:20\n'
SERVICE_COMMON = 'Service host process PID: 1234\nThreads in use: 1/32\nClient PIDs: 11, 12\n'
COMMAND_END = "------ 0.012s was the duration of '%s' ------\n\n"

ENFORCING = ('EnforcingAdmin { mPackageName= com.example.guard, mComponentName= ComponentInfo{com.example.guard/'
             'com.example.guard.agent.GuardReceiver}, mAuthorities= [device_admin], mUserId= 0, mIsRoleAuthority= false, '
             'mSystemEntity = null }')


def service(name, body, layout='new', common=True, end=True):
    head = 'DUMP OF SERVICE %s:\n' % name
    if common and layout == 'new':
        head += SERVICE_COMMON
    return head + body + ('\n' + SERVICE_END % name + '\n' if end else '')


def command(title, shown, body):
    return '------ %s (%s) ------\n%s%s' % (title, shown, body, COMMAND_END % title)


# ------------------------------------------------------------------------------------------
# security
# ------------------------------------------------------------------------------------------
def device_policy(layout):
    if layout == 'old':
        return service('device_policy', (
            'Current Device Policy Manager state:\n\n  Enabled Device Admins (User 0, provisioningState: 0):\n \n'
            '    mPasswordOwner=-1\n\n  Constants:\n    DAS_DIED_SERVICE_RECONNECT_BACKOFF_SEC: 3600\n\n  Stats:\n'
            '    LockGuard.guard(): count=10, total=1.0ms, avg=0.100ms, max calls/s=1 max dur/s=1.0ms max time=1.0ms\n\n'
            '  Encryption Status: per-user\n\nDevice policy cache\n  Screen capture disabled: {0=false}\n'
            '  Password quality: {0=0}\n'), 'old', end=True)
    admin = ('  Enabled Device Admins (User 0, provisioningState: 0):\n'
             '    com.example.guard/.agent.GuardReceiver:\n'
             '      uid=5101\n      testOnlyAdmin=false\n      policies:\n        wipe-data\n        force-lock\n        disable-camera\n'
             '      passwordQuality=0x0\n      minimumPasswordLength=0\n      maximumFailedPasswordsForWipe=5\n'
             '      encryptionRequested=false\n      disabledKeyguardFeatures=0\n      isNetworkLoggingEnabled=false\n'
             '      mAlwaysOnVpnPackage=null\n      mAlwaysOnVpnLockdown=false\n      isParent=false\n      mCommonCriteriaMode=false\n'
             '      DeviceAdminInfo:\n        mVisible: true\n        Receiver:\n          name=com.example.guard.agent.GuardReceiver\n'
             '          packageName=com.example.other\n          ApplicationInfo:\n'
             '            name=com.example.guard.app.GuardApplication\n            packageName=com.example.other\n'
             '            sourceDir=/system/priv-app/ExampleGuard/ExampleGuard.apk\n'
             '      eas it policies:\n        allowWifi=true\n  \n'
             '    mPasswordOwner=-1\n    mUserSetupComplete=true\n    mFailedPasswordAttempts=0\n  \n  \n'
             '  Enabled Device Admins (User 10, provisioningState: 0):\n'
             '    com.example.vault/.backend.VaultReceiver:\n'
             '      uid=1010123\n      testOnlyAdmin=true\n      policies:\n        force-lock\n'
             '      passwordQuality=0x20000\n      minimumPasswordLength=6\n      maximumFailedPasswordsForWipe=10\n'
             '      encryptionRequested=true\n      disabledKeyguardFeatures=2\n      isNetworkLoggingEnabled=true\n'
             '      mAlwaysOnVpnPackage=com.example.vpn\n      mAlwaysOnVpnLockdown=true\n      isParent=true\n'
             '      mCommonCriteriaMode=true\n'
             '    mPasswordOwner=-1\n    mAppsSuspended=false\n  \n')
    body = ('Current Device Policy Manager state:\n  Immutable state:\n    mHasFeature=true\n    mIsWatch=false\n'
            '  Pending System Update: SystemUpdateInfo (receivedTime = 1790000000000, securityPatchState = unknown)\n  \n'
            '  Profile Owner (User 10): \n    admin=ComponentInfo{com.example.vault/com.example.vault.backend.VaultReceiver}\n'
            '    package=com.example.vault\n    isOrganizationOwnedDevice=false\n  \n' + admin +
            '  Constants:\n    DAS_DIED_SERVICE_RECONNECT_BACKOFF_SEC: 3600\n  \n'
            '  Stats:\n    LockGuard.guard(): count=2210, total=19.5ms, avg=0.009ms, max calls/s=31 max dur/s=2.2ms max time=1.9ms\n  \n'
            '  Local Policies: \n    User 0:\n      UserRestrictionPolicyKey userRestriction_no_factory_reset\n'
            '        Per-admin Policy:\n          null\n        Resolved Policy (MostRestrictive):\n          null\n      \n  \n'
            '  Global Policies: \n    DefaultPolicyKey exampleSetAllowMode\n      Per-admin Policy:\n        ' + ENFORCING + '\n'
            '          IntegerPolicyValue { mValue= 2 }\n      Resolved Policy (MostRecent):\n        IntegerPolicyValue { mValue= 2 }\n    \n'
            '    BooleanPolicyKey exampleBlockAll\n      Per-admin Policy:\n        null\n      Resolved Policy (TopPriority):\n'
            '        null\n    \n  \n'
            '  Default admin policy size limit: -1\n  Current admin policy size limit: -1\n  Admin Policies size: \n  User 0:\n'
            '    Admin : ' + ENFORCING + ' : 77\n\n'
            'Encryption Status: per-user\nLogout user: -10000\n\nno pending user created callback tokens\n\n'
            'Device policy cache:\n  Screen capture disallowed users: []\n  Password quality: {0=0, 10=131072}\n'
            '  Admin can grant sensors permission: false\n\n'
            'Device state cache:\n  Device provisioned: true\n  Device Owner Type: -1\n  Has PO:\n    User 10: true\n\n'
            'PersonalAppsSuspensionHelper\n  critical packages: 1 app\n    0: com.example.wellbeing\n'
            '  launcher packages: 2 apps\n    0: com.example.launcher\n    1: com.example.settings\n'
            '  accessibility services: empty\n  SMS package: com.example.messages\n  Settings package: com.example.settings\n'
            '  Packages subject to suspension: 2 apps\n    0: com.example.a\n    1: com.example.b\n')
    return service('device_policy', body)


LOCK_FILES_USER0 = ('        91 2026-06-09 18:42:07 0000000000000000.e0.bku\n'
                    '        57 2026-06-09 18:42:05 0000000000000000.handle\n'
                    '       193 2026-06-09 18:42:05 0123456789abcdef.spblob\n')


def lock_settings(layout):
    if layout == 'old':
        return service('lock_settings', ('Current lock settings service state:\nSP Enabled = false\n    User 0\n'
                                         '        SP Handle = 1234567890abcdef\n        SID = fedcba0987654321\n'), 'old')
    body = ('Current lock settings service state:\n\nDO Enabled: false\n\nUser State:\n  User 0\n'
            '    LSKF-based SP protector ID: 0123456789abcdef\n'
            '    LSKF last changed: 2026-06-09 18:42:05 (previous protector: fedcba9876543210)\n'
            '    Backup protector: 0000000000000000 (set : 1970-01-01 00:00:00, expire : 1970-01-01 00:00:00)\n'
            '    SI Checker: aaaaaaaaaaaaaaaa (For 0123456789abcdef)\n    Secure Mode: 0\n    SID: 1111222233334444\n    Quality: 0\n'
            '    CredentialType: PIN\n    SeparateChallenge: true\n    Metrics: known\n    failed attempt = 0\n'
            '  User 10\n    LSKF-based SP protector ID: 5555666677778888\n'
            '    LSKF last changed: 2025-08-14 11:05:27 (previous protector: 9999aaaabbbbcccc)\n'
            '    SID: ddddeeeeffff0000\n    Quality: 0\n    CredentialType: PASSWORD\n    SeparateChallenge: true\n'
            '    Metrics: unknown\n    Extra Field: odd value\n  \n'
            'Keys in namespace:\n  synthetic_password_0123456789abcdef\n  synthetic_password_fedcba9876543210\n  \n'
            'Storage:\n  User 0 [/data/system_de/0/spblob]:\n' + LOCK_FILES_USER0 +
            '  Backup [/data/sec_backup_de/0/spblob]:\n        57 2026-06-09 18:42:07 0000000000000000.handle\n  \n'
            'StrongAuth:\n  PrimaryAuthFlags state:\n    userId=0, primaryAuthFlags=0\n    userId=10, primaryAuthFlags=5\n    \n'
            '  NonStrongBiometricAllowed state:\n    userId=0, allowed=true\n    \n'
            '  strong auth timeout state:\n    strong biometric timeout:2026/11/05 06:01:36.858\n    \n  \n'
            'RebootEscrow:\n  mRebootEscrowWanted=false\n  mRebootEscrowReady=false\n'
            '  mRebootEscrowListener=com.example.RecoveryService@1a2b3c\n  mPendingRebootEscrowKey is not set\n'
            '  RebootEscrowProvider type is null\n  Event log:\n    \n  \n'
            'PasswordHandleCount: 0\nThirdPartyAppsStarted: true\nLSSLog:\n\n'
            '----------------- Start Summary state -----------------\n----------------- End Summary state -----------------\n\n'
            '----------------- Start Enroll state -----------------\n'
            '2026-02-03 08:14:22.311 Start Logging\n'
            '2026-06-09 18:42:05.127 Enroll [User 0 PIN][com.example.settings:19989]\n'
            '    com.example.server.locksettings.Service.setLockCredential:1090\n'
            '    com.example.settings.SaveWorker.run:40\n    <bottom of call stack>\n\n'
            '2026-06-09 18:42:05.481 Enroll Finish [User 0 PIN(1)][com.example.settings:19989]\n'
            '    [Enroll Success(0)][0123456789abcdef][1, -2, 3](352ms)\n\n'
            '2026-06-09 18:42:06.002   User 0 [/data/system_de/0/spblob]:\n' + LOCK_FILES_USER0 + '\n'
            '----------------- End Enroll state -----------------\n\n'
            '----------------- Start Verify state -----------------\n'
            '2026-10-30 07:12:40.215 User 0(1) weaver INCORRECT_KEY(2) [com.example.systemui][1, -2, 3](1/0)(213ms)\n'
            '2026-10-30 07:12:41.870 User 0(1) weaver Success! [com.example.systemui][1, -2, 3](134ms)\n'
            '2026-10-30 07:13:55.002 User 0 PIN OK on [com.example.systemui]\n'
            '2026-10-30 07:14:20.640 User 0 PIN Fail on [com.example.systemui](2/5)]\n')
    return service('lock_settings', body)


PRINTS_NEW = ('{"service":"%s\\/default","prints":[{"id":0,"count":2,"accept":3,"reject":1,"quality":0,"acquire":9,"lockout":0,'
              '"permanentLockout":0,"acceptCrypto":0,"rejectCrypto":0,"qualityCrypto":0,"acquireCrypto":0},'
              '{"id":10,"count":0,"accept":0,"reject":0,"acquire":0,"lockout":0,"permanentLockout":0,"acceptCrypto":0,'
              '"rejectCrypto":0,"acquireCrypto":0,"future":7}]}\n')
PRINTS_OLD = ('{"service":"%s","prints":[{"id":0,"count":1,"accept":1,"reject":0,"acquire":25,"lockout":0,"permanentLockout":0,'
              '"acceptCrypto":0,"rejectCrypto":0,"acquireCrypto":0,"lockoutCrypto":0,"permanentLockoutCrypto":0}]}\n')
COORDINATOR = ('---AuthSessionCoordinator logs begin---\n'
               '#0     resetLockoutFor(userId=0 ,biometricStrength=15, requestId=-1)\n'
               '#1     authStartedFor(userId=0, sensorId=0, requestId=1)\n'
               '#2     internal : onAuthSessionStarted(0)\n'
               '#3     authEndedFor(userId=0 ,biometricStrength=15, sensorId=0, requestId=1, wasSuccessful=false)\n'
               '#4     internal : onAuthSessionEnded(0)\n'
               '#5     authEndedFor(userId=0 ,biometricStrength=15, sensorId=0, requestId=2, wasSuccessful=true)\n')


def biometrics(layout):
    if layout == 'old':
        return (service('fingerprint', PRINTS_OLD % 'Fingerprint Manager' + 'HAL Deaths: 0\n', 'old') +
                service('face', PRINTS_OLD.replace('"count":1', '"count":0') % 'Face Manager' + 'HAL Deaths: 0\n', 'old') +
                service('biometric', '', 'old'))
    fingerprint = ('Dumping for sensorId: 0, provider: FingerprintProvider\nFps state: 0\n' + PRINTS_NEW % 'FingerprintProvider' +
                   'HAL deaths since last reboot: 1\n' + COORDINATOR)
    face = ('Dumping for sensorId: 1, provider: FaceProvider\n' + (PRINTS_NEW % 'FaceProvider').replace('"count":2', '"count":0') +
            'HAL deaths since last reboot: 0\n' + COORDINATOR)
    sensors = ('Legacy Settings: false\n\nSensors:\n ID(0), oemStrength: 15, updatedStrength: 15, modality 2, state: 0, cookie: 0\n'
               ' ID(1), oemStrength: 255, updatedStrength: 255, modality 8, state: 4, cookie: 770011\n\nCurrentSession: null\n\n')
    return service('fingerprint', fingerprint) + service('face', face) + service('biometric', sensors)


def trust(layout):
    if layout == 'old':
        return service('trust', ('Trust manager state:\n User "Example \u200fOwner" (id=0, flags=0x15) (current): trusted=0, trustManaged=0, '
                                 'deviceLocked=0, strongAuthRequired=0x0\n   Enabled agents:\n    com.example.gms/.ExampleTrustAgent\n'
                                 '     bound=1, connected=1, managingTrust=0, trusted=0\n   Events:\n'
                                 '    #0  10-29 09:12:45.118 AgentConnected: agent=ExampleTrustAgent\n'), 'old')
    return service('trust', (
        'Trust manager state:\n User "Example Owner" (id=0, flags=0x4a11) (current): trustState=UNTRUSTED, trustManaged=0, deviceLocked=0, '
        'isActiveUnlockRunning=0, strongAuthRequired=0x0\n   Enabled agents:\n    com.example.gms/.ExampleTrustAgent\n'
        '     bound=1, connected=1, managingTrust=0, trusted=0\n    com.example.gms/.LockingAgent\n'
        '     bound=1, connected=0, managingTrust=1, trusted=1\n   Events:\n'
        '    #0  10-29 11:02:14.250 AgentConnected: agent=ExampleTrustAgent\n'
        '    #1  10-29 11:02:13.904 AgentConnected: agent=LockingAgent\n\n'
        ' User "Work Profile" (id=10, flags=0x1002020) (profile with separate challenge): deviceLocked=1\n'
        '   Trust agents disabled because switching to this user is not possible.\n'))


def adb(layout):
    return service('adb', 'ADB MANAGER STATE (dumpsys adb):\n{\n  debugging_manager={\n    connected_to_adb=false\n  }\n}\n', layout)


def vendor(layout, cut=False):
    if layout == 'old':
        return ''
    guard = ('KG30.ExampleGuardService state: \nADB blocked : false\nDO blocked : false\nSF counter : 1\n'
             '2026-03-12 07:31:44 : [action] android.intent.action.TIMEZONE_CHANGED\n'
             '2026-03-12 07:31:52 : [android.intent.action.BOOT_COMPLETED] kgState : Prenormal | isNetworkConnected : false\n'
             '2026-03-14 19:05:30 : [TOKEN REFRESH] Refreshed token: AbCd1234\n'
             '1970-01-01 00:00:00 : [action] android.intent.action.TIME_SET\n')
    custom = ('KnoxCustomManagerService state:\n  ProKioskManager: false\n  ProKioskManager:ExitUI: null:null\n'
              '  SystemManager:BatteryLevelColour is null\n  SystemManager:InfraredState:false\n'
              '  SystemManager:LockScreenShortcuts: com.example.dialer/.Dial, com.example.camera/.Cam\n'
              '  SettingsManager:SettingsHiddenState: 0x00000000\n')
    if cut:
        guard += "\n*** SERVICE 'knoxguard_service' DUMP TIMEOUT (10000ms) EXPIRED ***\n"
        return service('knoxcustom', custom) + service('knoxguard_service', guard, end=False) + (
            '--------- 10.008s was the duration of dumpsys knoxguard_service, ending at: 2026-11-02 10:15:30\n\n')
    return service('knoxcustom', custom) + service('knoxguard_service', guard)


# ------------------------------------------------------------------------------------------
# storage
# ------------------------------------------------------------------------------------------
DF = ('Filesystem        1K-blocks     Used Available Use% Mounted on\n'
      '/dev/block/dm-8     3120400  3120400         0 100% /\n'
      'tmpfs               1500200     2810   1497390   1% /dev\n'
      '/dev/block/dm-63   61000700 41200100  19800600  68% /data\n'
      '/dev/block/loop1        640      612        16  96% /apex/com.example.tzdata@300100200\n'
      'none                99999999999999999999 1 2 3% /overflow\n'
      'short line\n')
DF_INODES = ('Filesystem                      Inodes   IUsed                IFree IUse% Mounted on\n'
             '/dev/block/dm-8   18446744073709551615    5120 18446744073709546495    1% /\n'
             'tmpfs                           375050    1310               373740    1% /dev\n'
             '/dev/block/dm-63                3815424  120210              3695214    3% /data\n')
MOUNTS = ('/dev/block/dm-8 on / type erofs (ro,seclabel,relatime,user_xattr,acl,cache_strategy=readaround)\n'
          'tmpfs on /dev type tmpfs (rw,seclabel,nosuid,relatime,size=1500200k,nr_inodes=375050,mode=755)\n'
          '/dev/block/sdc30 on /metadata type ext4 (rw,sync,seclabel,nosuid,nodev,noatime)\n'
          'not a mount line\n')
STORAGED = ('name/uid fg_rchar fg_wchar fg_rbytes fg_wbytes bg_rchar bg_wchar bg_rbytes bg_wbytes fg_fsync bg_fsync\n'
            'com.example.chat 9120344 412008 51200000 1310720 880001200 44001300 7700000000 91000000 12 3400\n'
            'shared:android.uid.example 120045 88002 4096000 0 61000200 7300100 990000000 12000000 0 210\n'
            'com.example.huge 99999999999999999999 1 2 3 4 5 6 7 8 9\n'
            'broken line 1 2\n'
            '\nI/O perf history (KB/s) :  most_recent  <---------  least_recent \n'
            'last 24 hours : 4410 9120 12050\n'
            'last 7 days   : 8800 9100 9350\n')


def storage(layout):
    if layout == 'old':
        return (command('FILESYSTEMS & FREE SPACE', 'df', DF.replace('/overflow', '/other')) +
                command('STORAGED IO INFO', 'storaged -u -p', STORAGED) +
                service('mount', ('Disks:\n\nVolumes:\n  VolumeInfo{emulated}:\n    type=EMULATED diskId=null partGuid= mountFlags=PRIMARY|VISIBLE '
                                  'mountUserId=-10000 state=MOUNTED \n    fsType=null fsUuid=null fsLabel=null \n'
                                  '    path=/storage/emulated internalPath=/data/media linkName= \n\nRecords:\n\nPrimary storage UUID: null\n\n'
                                  'Internal storage (null) total size: 16000000000 (15258 MiB)\n\n'), 'old') +
                service('diskstats', DISKSTATS_OLD, 'old') + dbinfo_service('old'))
    vold = ''.join('2026/10/04-03:%02d:%02d(GMT)  412:9021 vold %s\n' % (minute, minute, message) for minute, message in (
        (7, 'Starting trim of /mnt/vendor/example'), (7, 'Failed to open /mnt/vendor/example: Permission denied'),
        (9, 'VolumeBase::unmount()++')))
    mount = ('\nStorageVolumes:\nSize:1\n  StorageVolume:\n'
             '    mId=emulated;0 mPath=/storage/emulated/0 mInternalPath=/storage/emulated/0 mDescription=Internal shared storage '
             'mPrimary=true mRemovable=false \n    mEmulated=true mExternallyManaged=false mAllowMassStorage=false mMaxFileSize=0 '
             'mOwner=UserHandle{0} mFsUuid=null mState=mounted mStorageId=65537 \n    mSubSystem=fuse mActivitySecureContainer=false \n\n'
             'Disks:\n\nVolumes:\nSize:2\n  VolumeInfo{emulated;0}:\n    type=EMULATED diskId=null partGuid= '
             'mountFlags=PRIMARY|VISIBLE_FOR_WRITE mountUserId=0 state=MOUNTED \n    fsType=null fsUuid=null fsLabel=null \n'
             '    path=/storage/emulated internalPath=/data/media \n  VolumeInfo{private}:\n    type=PRIVATE diskId=null state=MOUNTED '
             'fsType=ext4 fsUuid=0000-ffff fsLabel=example\n\nRecords:\n\nPrimary storage UUID: null\n\n'
             'Internal storage (null) total size: 68719476736 (65536 MiB)\n\nCE unlocked users: [0]\nSystem unlocked users: [0]\n'
             'Sharing media with parent : \nUser pairs for sharing media : \n\nVOLD LAST LOG BUF#0\n' + vold +
             '2026/10/04-03:12:12(UTC)  412:9021 vold idle maintenance completed\n' +
             'continuation without a time\n')
    return (command('MOUNT POINT DUMP', 'mount', MOUNTS) + command('STORAGED IO INFO', 'storaged -u -p', STORAGED) +
            command('FILESYSTEMS & FREE SPACE', 'df', DF) + command('FILESYSTEMS & FREE INODE', 'df -i', DF_INODES) +
            service('mount', mount) + service('diskstats', DISKSTATS_NEW) + dbinfo_service('new'))


def names_line(count):
    return json.dumps(['com.example.pkg%02d' % number for number in range(count)], separators=(',', ':'))


def numbers_line(values):
    return json.dumps(values, separators=(',', ':'))


DISKSTATS_NEW = (
    'Latency: 1ms [512B Data Write]\nRecent Disk Write Speed (kB/s) = 20450\nData-Free: 18010020K / 61000700K total = 29% free\n'
    'Cache-Free: 18010020K / 61000700K total = 29% free\nSystem-Free: 0K / 3120400K total = 0% free\nFile-based Encryption: true\n'
    'App Size: 12100200000\nApp Data Size: 20300500000\nApp Cache Size: 3100400000\nPhotos Size: 810500000\n'
    'Package Names: ' + names_line(4) + '\nApp Sizes: ' + numbers_line([0, 120832, 9400320, 5100544]) +
    '\nApp Data Sizes: ' + numbers_line([0, 18432, 250880, 90112]) + '\nCache Sizes: ' + numbers_line([0, 8192, 20480, 71680]) + '\n')
DISKSTATS_OLD = (
    'Latency: 1ms [512B Data Write]\nRecent Disk Write Speed (kB/s) = 30110\nData-Free: 9100200K / 24000100K total = 37% free\n'
    'File-based Encryption: true\nApp Size: 4100200000\n'
    'Package Names: ' + names_line(3) + '\nApp Sizes: ' + numbers_line([3000320, 0, 150000640]) +
    '\nApp Data Sizes: ' + numbers_line([20480, 4096]) + '\nCache Sizes: ' + numbers_line([0, 0, 16384]) + '\n')


def dbinfo_service(layout, cut=False):
    if layout == 'old':
        return service('dbinfo', DBINFO_OLD, 'old')
    return service('dbinfo', DBINFO_NEW, end=not cut) + (
        ("*** SERVICE 'dbinfo' DUMP TIMEOUT (10000ms) EXPIRED ***\n--------- 10.008s was the duration of dumpsys dbinfo, ending at: "
         "2026-11-02 10:15:30\n\n") if cut else '')


_PATH = '/data/user_de/0/com.example.settings/databases/example-db-v1'
DBINFO_NEW = (
    'Applications Database Info:\n\n** Database info for pid 4321 [com.example.settings] **\n  Attached db: false\n'
    'Connection pool for ' + _PATH + ':\n  Open: true\n  Max connections: 4\n  Total execution time (ms): 31\n'
    '  Total statements executed: 84\n  Average time per statement (ms): 0\n'
    '  Configuration: openFlags=805306368, isLegacyCompatibilityWalEnabled=false, journalMode=WAL, syncMode=NORMAL\n'
    '  IsReadOnlyDatabase: false\n  Secure db: false\n  Use WAL mode. \n  Available primary connection:\n    Connection #0:\n'
    '      isPrimaryConnection: true\n      onlyAllowReadOnlyOperations: false\n      totalLongOperations: 0\n'
    '      Most recently executed operations:\n'
    '        0: [11-01 14:22:31.250] [Pid:(4321)]execute took 1ms - succeeded, sql="CREATE TEMP TABLE IF NOT EXISTS example_log (id INTEGER PRIMARY KEY)", path=' + _PATH + '\n'
    '        1: [11-01 14:22:31.249] [Pid:(4321)]prepare took 1ms - succeeded, sql="SELECT \'a, b\' FROM t WHERE x = 1", path=' + _PATH + ', filledRows=3\n'
    '        2: [11-01 14:22:31.221] [Pid:(4321)]open took 7ms - succeeded, path=' + _PATH + '\n'
    '        3: [11-01 14:22:31.220] [Pid:(4321)]TRANSACTION-IMMEDIATE took 0ms - succeeded, path=' + _PATH + ' result=2\n'
    '        4: [11-01 14:22:31.219] [Pid:(4321)]executeForLong took 3ms - failed, sql="SELECT * FROM missing", path=' + _PATH + '\n'
    '        5: [12-31 23:59:59.999] [Pid:(4321)]execute took 0ms - succeeded, sql="PRAGMA query_only", path=' + _PATH + '\n'
    '        6: unreadable operation line\n'
    '      Operations exceeding 2000ms:\n'
    '        0: [11-01 12:40:18.733] [Pid:(4321)]TRANSACTION-EXCLUSIVE took 2310ms - succeeded, path=' + _PATH + ', filledRows=0, result=1\n'
    '  Available non-primary connections:\n    Connection #1:\n'
    '      isPrimaryConnection: false\n      onlyAllowReadOnlyOperations: true\n      Most recently executed operations:\n'
    '        0: [11-01 14:22:31.275] [Pid:(4321)]executeForCursorWindow took 0ms - succeeded, sql="SELECT * FROM BatteryState", path=' + _PATH + '\n'
    '      Operations exceeding 2000ms:\n        <none>\n  Acquired connections:\n    <none>\n  Connection waiters:\n    <none>\n  \n'
    '  ' + _PATH + ' :    84\n  \n'
    'Database files in /data/user_de/0/com.example.settings/databases:\n'
    '  example-db-v1                              8192b ctime=2026-05-17T08:12:09.114233Z mtime=2026-05-17T08:12:09.114233Z atime=2026-05-17T08:12:09.109233Z\n'
    '  example-db-v1-wal                       524288b ctime=2026-11-01T14:22:31.001858Z mtime=2026-11-01T14:22:31.001858Z atime=2026-05-17T08:12:09.121233Z\n'
    '  odd name.db                                    0b ctime=2026-03-02T10:41:07.512Z mtime=2026-03-02T10:41:07.512Z atime=1970-01-01T00:00:00Z\n'
    '** Database info for pid 4400 [com.example.second] **\n'
    'Connection pool for /data/user/0/com.example.second/databases/second.db:\n  Open: false\n  Max connections: 1\n'
    '  Total execution time (ms): 5\n  IsReadOnlyDatabase: true\n  Lookaside config: sz=0 cnt=0\n  Available primary connection:\n'
    '    Connection #0:\n      isPrimaryConnection: true\n      Most recently executed operations:\n        <none>\n')
DBINFO_OLD = (
    'Applications Database Info:\n\n** Database info for pid 2576 [com.example.settings] **\n\n'
    'Connection pool for /data/user_de/0/com.example.settings/databases/search_index.db:\n  Open: true\n  Max connections: 1\n'
    '  Total execution time: 1420\n  Configuration: openFlags=268435456, isLegacyCompatibilityWalEnabled=false, journalMode=, syncMode=\n'
    '  Lookaside config: sz=0 cnt=0\n  Available primary connection:\n    Connection #0:\n      isPrimaryConnection: true\n'
    '      onlyAllowReadOnlyOperations: true\n      Most recently executed operations:\n'
    '        0: [2026-11-02 08:19:03.552] executeForCursorWindow took 0ms - succeeded, sql="SELECT * FROM saved_queries", '
    'path=/data/user_de/0/com.example.settings/databases/search_index.db\n'
    '        1: [2026-11-02 08:19:02.904] prepare took 1ms - succeeded, sql="COMMIT;", path=/data/user_de/0/com.example.settings/databases/search_index.db\n'
    '  Available non-primary connections:\n  Acquired connections:\n  Connection waiters:\n\n'
    'Database files in /data/user_de/0/com.example.settings/databases:\n'
    '  athena.db                                  40960b ctime=2026-10-30T16:25:40Z mtime=2026-10-30T16:25:40Z atime=2026-10-30T16:25:40Z\n')


# ------------------------------------------------------------------------------------------
# configuration and build flags
# ------------------------------------------------------------------------------------------
def configuration(layout):
    if layout == 'old':
        return service('device_config', '', 'old') + service('platform_compat', '', 'old')
    device_config = ('DeviceConfig flags:\naccessibility/com.example.flags.example_flag_one=true\n'
                     'adservices/example_period_ms=3600000\ntest/empty_value=\n'
                     'messaging/example_app_list=com.example.one,\ncom.example.two,\ncom.example.three\n')
    compat = ('ChangeId(100200301; name=EXAMPLE_DOWNSCALE_65; disabled; overridable)\n'
              'ChangeId(100200302; name=EXAMPLE_FEATURE; enableSinceTargetSdk=35)\n'
              'ChangeId(111; name=EXAMPLE_LOG_ONLY; loggingOnly)\n'
              'ChangeId(222; name=EXAMPLE_AFTER; enableAfterTargetSdk=30; futureFlag)\n'
              'a line that is not a change\n')
    return service('device_config', device_config) + service('platform_compat', compat) + service('platform_compat_native', '')


def release_flags(layout):
    if layout == 'old':
        return ''
    flags = {'flags': [
        {'flag_declaration': {'name': 'RELEASE_EXAMPLE_ONE', 'namespace': 'example_team', 'description': 'An invented flag.',
                              'value': {'Val': {'UnspecifiedValue': False}}, 'workflow': 1, 'containers': ['product', 'system']},
         'value': {'Val': {'BoolValue': True}}},
        {'flag_declaration': {'name': 'RELEASE_EXAMPLE_TWO', 'namespace': 'example_team', 'description': 'Another invented flag.',
                              'value': {'Val': {'StringValue': 'READ_WRITE'}}, 'workflow': 3, 'containers': ['vendor']},
         'value': {'Val': {'StringValue': 'READ_ONLY'}}},
        {'flag_declaration': {'name': 'RELEASE_EXAMPLE_THREE', 'namespace': 'other_team', 'description': 'No value.',
                              'value': {'Val': {'UnspecifiedValue': False}}, 'workflow': 1}}]}
    artifacts = {'flag_artifacts': [flags['flags'][1]]}
    text = (command('SYSTEM BUILD-TIME RELEASE FLAGS', '/system/etc/build_flags.json: 2022-01-01 00:00:00',
                    json.dumps(flags, indent=2) + '\n') +
            command('PRODUCT BUILD-TIME RELEASE FLAGS', '/product/etc/build_flags.json: 2009-01-01 00:00:00',
                    json.dumps(artifacts, indent=2) + '\n') +
            command('VENDOR BUILD-TIME RELEASE FLAGS', '/vendor/etc/build_flags.json: 2022-01-01 00:00:00',
                    '{\n  "flags": [\n    {"flag_declaration": {"name": "CUT_OFF"\n') +
            command('SDK EXTENSIONS', '/apex/com.example.sdkext/bin/derive_sdk --dump',
                    'system properties:\n  build.version.extensions.ad_services:23\n  build.version.extensions.c:<not set>\n'
                    '  ro.build.version.sdk:36\napex module versions:\n  AD_SERVICES:23\n  ART:23\n'
                    'last 3 version requirements:\n  23: ART AD_SERVICES \n  22: ART \n'))
    return text


# ------------------------------------------------------------------------------------------
# the whole text
# ------------------------------------------------------------------------------------------
def sections(layout='new', cut=False):
    text = ''
    text += '------ DUMPSYS HIGH (/system/bin/dumpsys) ------\n'
    text += device_policy(layout) + lock_settings(layout) + biometrics(layout) + trust(layout) + adb(layout)
    text += vendor(layout, cut) + configuration(layout)
    text += "------ 0.900s was the duration of 'DUMPSYS HIGH' ------\n\n"
    text += storage(layout) if not cut else storage(layout).replace(dbinfo_service('new'), dbinfo_service('new', True))
    text += release_flags(layout)
    return text


def build_report(layout='new', zone='Europe/Paris', report='2026-11-02 10:15:30', cut=False, newline='\n'):
    """The base report (banner, header, properties) with the security and storage sections added."""
    plain = base.build_report('a16' if layout == 'new' else 'a10', zone=zone, report=report)
    closing = '== dumpstate: done (id 1)\n'
    head = plain[:plain.rindex(closing)]
    return (head + sections(layout, cut) + closing).replace('\n', newline)


# ------------------------------------------------------------------------------------------
# cases
# ------------------------------------------------------------------------------------------
def cases():
    """{case name: [(member name, bytes), ...]}"""
    out = {}
    out['synthetic_new'] = [('Dump/dumpstate.txt', build_report('new').encode('utf-8'))]
    out['synthetic_old'] = [('Dump/bugreport-example-EXOLD-2026-11-02-10-15-30.txt',
                             build_report('old', zone='Asia/Kolkata', newline='\r\n').encode('utf-8')),
                            ('Dump/main_entry.txt', b'bugreport-example-EXOLD-2026-11-02-10-15-30.txt')]
    out['synthetic_cut'] = [('Dump/dumpstate.txt', build_report('new', cut=True).encode('utf-8'))]
    out['synthetic_two_reports'] = [('Dump1/dumpstate.txt', build_report('new', zone='Asia/Kolkata').encode('utf-8')),
                                    ('Dump2/bugreport-example-EXOLD-2026-11-02-10-15-30.txt',
                                     build_report('old', zone='America/Sao_Paulo').encode('utf-8'))]
    out['synthetic_empty'] = [('Dump/dumpstate.txt', (base.BANNER.format(report='2026-11-02 10:15:30') + '\n').encode())]
    out['synthetic_not_a_report'] = [('Dump/dumpstate.txt', b'This file has no banner.\nDUMP OF SERVICE device_policy:\n  Enabled Device Admins\n'),
                                     ('Dump/bugreport-notes.txt', bytes(range(256)) * 4)]
    return out


def main(output):
    os.makedirs(output, exist_ok=True)
    for name, members in cases().items():
        base.write_zip(os.path.join(output, name + '.zip'), members)
    for name in sorted(os.listdir(output)):
        print(name, os.path.getsize(os.path.join(output, name)))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'bugreport_securitystorage_fixture_out')
