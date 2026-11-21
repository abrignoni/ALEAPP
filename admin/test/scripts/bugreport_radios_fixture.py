"""Builds the synthetic Android bug report texts used by the Android Bug Report radios test cases.

Every value is invented: package names are under example.*, the addresses, names, vendor and product
numbers, carrier names, network codes and times are made up (the SIM and phone numbers are made up too,
and are in the text on purpose: the artifacts must not report them). Only the structure is taken from
real bug reports: the sections and the line layouts of the Bluetooth manager, NFC, USB, telephony and
radio log dumps. Three layouts are built:

* ``a16``: an Android 16 style text with the Bluetooth manager dump with the masked bonded device list,
  the NFC dump with its event log, the NFC SYSTEM LOG and USB LOG command sections, the subscription
  manager service form of the isub dump and the state machine records of the isms dump;
* ``a15``: an Android 15 style text with the usb, telephony.registry and telecom service dumps and a
  short Bluetooth dump whose bonded devices have no class;
* ``a10``: an Android 10 style text with the older subscription controller form of the isub dump, the
  carrier configuration loading log and a Bluetooth dump of the older layout.

Usage: python -m admin.test.scripts.bugreport_radios_fixture <output folder>
Writes one zip per test case into the folder, each holding a synthetic extraction (files under a
``Dump`` folder), and prints their names and sizes. With ``--test-cases``, run from the repository root, it
writes the case zips and the case file under admin/test/cases instead.
"""
import fnmatch
import json
import os
import platform
import subprocess
import sys
from datetime import datetime

from admin.test.scripts import bugreport_fixture as base

REPORT = '2026-11-02 10:15:30'


def command(title, command_text, body, seconds='0.010'):
    return ('------ %s (%s) ------\n%s\n------ %ss was the duration of \'%s\' ------\n\n'
            % (title, command_text, body.rstrip('\n'), seconds, title))


def service(name, body, seconds='0.050', end='2026-11-02 10:15:20'):
    return ('DUMP OF SERVICE %s:\n%s\n--------- %ss was the duration of dumpsys %s, ending at: %s\n'
            '-------------------------------------------------------------------------------\n'
            % (name, body.rstrip('\n'), seconds, name, end))


# ------------------------------------------------------------------------------------------
# Bluetooth
# ------------------------------------------------------------------------------------------
def bluetooth(layout):
    if layout == 'a16':
        body = '''Service host process PID: 2000
Threads in use: 1/32
Client PIDs: 2001, 2002
Bluetooth Status
  enabled: true
  state: ON
  address: XX:XX:XX:XX:AA:01
  name: Example Phone BT
  time since enabled: 02:58:14.660

Enable log:
  11-02 07:17:31.490 \tPackage [android] requested to [Enable]. \tReason is SYSTEM_BOOT

Bluetooth crashed 0 times

Number of Ble app registered: 2
  com.example.beacon
  android

BluetoothManagerService:
  mEnable:true

\U0001f6a9Flag dump:
\t[\u25a0]: example_flag_one
\t[ ]: example_flag_two
AdapterProperties
  Name: Example Phone BT
  Address: XX:XX:XX:XX:AA:01
  ConnectionState: STATE_DISCONNECTED
  State: ON
  MaxConnectedAudioDevices: 2
  A2dpOffloadEnabled: false
  Discovering: false
  DiscoveryEndMs: 0
  Bonded devices:
                XX:XX:XX:XX:BB:11 [BR/EDR][ 0x340408 ] Example Car Kit (00000000-aaaa-bbbb-cccc-000000000001,SPP,AudioSink,Avrcp)
                XX:XX:XX:XX:BB:22 [ DUAL ][ 0x360408 ] Example Speaker (AudioSink,Avrcp,Handsfree)


  Devices in DB:
    XX:XX:XX:XX:BB:11 | Example Car Kit | 2 | 1 | 3408904 | 0 | null | SPP,AudioSink | 2 | 1787995211737 | 1787995211737 | null | 0 | 0 | 0

ScanMode: SCAN_MODE_CONNECTABLE
Scan Mode Changes:
  11-02 07:17:34.872 processProfileServiceStateChanged: SCAN_MODE_CONNECTABLE

AdapterState:
 total records=2
 rec[0]: time=11-02 07:17:34.003 processed=OffState org=OffState dest=TurningBleOnState what=3(0x3) BLE_TURN_ON
 rec[1]: time=11-02 07:17:34.903 processed=TurningOnState org=TurningOnState dest=OnState what=5(0x5) BREDR_STARTED
curState=OnState

Connection Events:
  None

Bond Events:
  Total Number of events: 0

Link Key Types:
  xx:xx:xx:xx:bb:11
    BR: AUTH_COMB
    LE:
  xx:xx:xx:xx:bb:22
    BR: AUTH_COMB_P_256
    LE:

A2DP State:
  TxQueue:
'''
    elif layout == 'a15':
        body = '''Service host process PID: 2000
Threads in use: 0/32
Bluetooth Status
  enabled: false
  state: BLE_ON
  address: 02:00:00:00:AA:02
  name: Example Phone BT
  time since enabled: 00:17:03.907

Enable log:
  11-02 06:05:38.007  Enabled  due to APPLICATION_REQUEST by android
  11-02 09:18:45.797 Disabled  due to AIRPLANE_MODE by android

Bluetooth crashed 0 times

1 BLE app registered
  com.example.beacon

  Bonded devices:
    02:00:00:00:CC:11 [ ???? ] Example Watch
    02:00:00:00:CC:22 [ ???? ] Example Buds
  Scan Mode Changes:
AdapterState:
 total records=1
 rec[0]: time=11-02 09:18:48.294 processed=OffState org=OffState dest=TurningBleOnState what=3(0x3) BLE_TURN_ON
curState=BleOnState

Connection Events:
  11-01 20:10:49.921 DISCONNECTED xx:xx:xx:xx:cc:11 reason=22
  11-01 20:06:13.641 CONNECTED    xx:xx:xx:xx:cc:11

Bond Events:
  Total Number of events: 0

Link Key Types:
  xx:xx:xx:xx:cc:11
    BR: UNAUTH_COMB
    LE: LE_KEY_PENC LE_KEY_LID
'''
    else:
        body = '''Bluetooth Status
  enabled: false
  state: BLE_ON
  address: 02:00:00:**:**:**
  name: Example Old Phone
  time since enabled: 00:59:32.678

Enable log:
  11-02 05:44:22  Enabled  due to APPLICATION_REQUEST by com.example.gms

Bluetooth crashed 0 times

1 BLE appregistered
  com.example.gms


btservice-BluetoothAdapterProperties
  Name: Example Old Phone
  Address: 02:00:**:**:**:CB
  BluetoothClass: 5a020c
  ScanMode: SCAN_MODE_NONE
  ConnectionState: STATE_DISCONNECTED
  State: BLE_ON
  Bonded devices:
    02:11:**:**:**:95 [BR/EDR] Example Car
    02:12:**:**:**:96 [LE] Example Tag
mSnoopLogSettingAtEnable = empty

btservice-BluetoothAdapterState:
 total records=1
 rec[0]: time=11-02 05:44:23.085 processed=OffState org=OffState dest=TurningBleOnState what=3(0x3) BLE_TURN_ON
curState=BleOnState

Connection Events:
  None

Bond Events:
  Total Number of events: 0
'''
    return service('bluetooth_manager', body)


# ------------------------------------------------------------------------------------------
# NFC
# ------------------------------------------------------------------------------------------
NFC_SERVICES = '''Registered HCE services for current user:
User Exa************
    ComponentInfo{com.example.nearby/com.example.nearby.NfcAdvertisingService} (Description: Example Nearby) (UID: 10501)
    On Host Service
    Static AID groups:
        Category: other(enabled: true)
            AID: F00000AAAA
    Dynamic AID groups:
    Settings Activity: null
    Requires Device Unlock: false
    Requires Device ScreenOn: true
    Should Default to Observe Mode: false

    ComponentInfo{com.example.pay/com.example.pay.HceService} (Description: Example Pay) (UID: 10501)
    On Host Service
    Static AID groups:
        Category: payment(enabled: true)
            AID: A0000000FFFF0000
    Dynamic AID groups:
        Category: payment(enabled: true)
            AID: A0000000FFFF0001
            AID: A0000000FFFF0002
    Settings Activity: com.example.pay.Settings
    Requires Device Unlock: false
    Requires Device ScreenOn: false

    ComponentInfo{com.example.transit/com.example.transit.OffHostService} (Description: null) (UID: 10502)
    Off-host Service
    Static AID groups:
    Dynamic AID groups:
    Settings Activity: null
    Requires Device Unlock: false
    Requires Device ScreenOn: false

Registered HCE-F services for current user:
User Exa************

Preferred services (in order of importance):
    *** Current preferred foreground service: null (UID:0)
    *** Current preferred payment service: ComponentInfo{com.example.pay/com.example.pay.HceService}
        Next tap default: null (Gid***)
        Default for foreground app (UID: 0): null

    AID cache entries:
    "A0000000FFFF0000" (category: other)
        *DEFAULT* ComponentInfo{com.example.pay/com.example.pay.HceService} (Description: Example Pay)

    Service preferred by foreground app: null
    Preferred payment service: null

Routing table:
    Default route: host
'''


def nfc(layout):
    if layout == 'a16':
        head = '''Service host process PID: 2100
Threads in use: 0/5
Client PIDs: 2101
mState=on
mAlwaysOnState=off
mScreenState=ON_UNLOCKED
mIsSecureNfcEnabled=false
SnoopLogMode=FILTERED
listenTech=0x7
pollTech=0x2f
mTechMask: default
mEnableLPD: true
mEnableHostRouting: true

'''
        tail = '''mNfceeAccess=
\t3082aaaa3082bbbb
--- dumpRoutingTable: start ---
RoutingTableSize=49/1170
--- dumpRoutingTable:  end  ---
===== Nfc Event Log =====
2026-11-01 11:57:17.101:  reader_mode_change { app_info { package_name: "android" uid: 1000 } flags: 4096 }
2026-11-01 11:57:18.707:  reader_mode_change { app_info { package_name: "android" uid: 1000 } flags: 0 }
2026-11-02 03:05:37.290:  bootup_state { enabled: true }
2026-11-02 04:07:45.336:  aid_registration { aids: "A0000000FFFF0001" aids: "A0000000FFFF0002" app_info { uid: 10501 } }
===== Nfc Event Log =====
---BEGIN: NATIVE CRASH LOG----
---END: NATIVE CRASH LOG----
'''
        return service('nfc', head + NFC_SERVICES + tail)
    if layout == 'a15':
        head = '''mState=off
mAlwaysOnState=off
mScreenState=ON_UNLOCKED
mIsSecureNfcEnabled=false
mTechMask: 0
mEnableLPD: true

'''
        tail = '''===== Nfc Event Log =====
2026-10-01 13:34:58.998:  bootup_state {  enabled: false}
2026-10-02 06:04:28.338:  bootup_state {  enabled: false}
===== Nfc Event Log =====
'''
        return service('nfc', head + NFC_SERVICES + tail)
    head = '''mState=off
mIsZeroClickRequested=true
mScreenState=ON_UNLOCKED
mTechMask: 0
mEnableP2p: falsemEnable2ndLevelMenu: false

'''
    return service('nfc', head + NFC_SERVICES.split('Registered HCE-F')[0].replace(
        'Requires Device Unlock: false\n    Requires Device ScreenOn: true\n    Should Default to Observe Mode: false\n', '')
        + 'Registered HCE-F services for current user: \n\nRouting table:\n    Default route: secure element\n')


def nfc_log():
    body = '''[B   1.670555] sec_nfc_init
[B   2.337835] probe start
[B   7.204979] late_pvdd_en 1
[B  62.172558] sec_nfc_open
[B  72.187516] [11-01 16:33:33.757] en(0) firm(1) pvdd(1) irq(0) mode(2) clk_state(0)
[B  72.187691] clk
[687861.569311] [11-02 05:54:38.685] clk
[687861.729541] clk
32.684900] clk

'''
    return command('NFC SYSTEM LOG', '/proc/nfclog', body, '0.002')


# ------------------------------------------------------------------------------------------
# USB
# ------------------------------------------------------------------------------------------
def usb_log(sync='[11-02 06:02:46][688349.963811]'):
    body = '''time sync: %s
usblog CC IC info:
tcpc name: example77775
hw version = 0  0  0  2

usblog CCIC EVENT: count=6 maxline=512
[03-03 00:34:20] [    4.796833] manager notify: id=ID_CONNECT src=MUIC dest=BATTERY rprd=RD cable=0 DETACHED
[11-01 20:38:23] [ 1866.503644] ccic notify:    id=ID_CONNECT src=CCIC dest=MUIC rprd=RD rp status=NONE ATTACHED
[11-01 20:38:24][ 1867.029714] ccic notify:    id=ID_CLEAR_INFO src=CCIC dest=DEV ALL clear DEVICE INFO
[509596.560543] port connect - VID:0x1234 PID:0x5678 cnt:4
[764368.714082] device class 0, interface class 1
[509592.399821] port disconnect - VID:0x1234 PID:0x5678

usblog PCM: count=0 maxline=64

usblog EXTRA: count=1 maxline=128
[11-02 06:02:46][41500.118184] example: port=0000000000000000
''' % sync
    return command('USB LOG', '/proc/usblog', body, '0.012')


def usb_service(layout):
    ports = '''    usb_ports={
      port={
        id=port0
        supported_modes=dual
      }
      status={
        connected=false
        current_mode=none
        role_combinations={
          power_role=no-power
        }
      }
      can_change_mode=true
      connected_at_millis=0
    }
    usb_hal_version=13
''' if layout == 'a15' else ''
    events = '''    USB Event Log=UsbDeviceManager activity
    USB Event=[
      11-02 06:05:38:034 USB intent: Intent { act=android.hardware.usb.action.USB_STATE flg=0x31000000 (has extras) }
      11-02 06:05:38:039 USB intent: Intent { act=android.hardware.usb.action.USB_STATE flg=0x31000000 (has extras) }
    ]
''' if layout == 'a15' else ''
    body = '''USB MANAGER STATE (dumpsys usb):
{
  device_manager={
    handler={
      current_functions_applied=true
      connected=false
      kernel_state=DISCONNECTED
    }
%s  }
  host_manager={
    num_connects=0
  }
  port_manager={
    is_simulation_active=false
%s  }
  alsa_manager={
    cards_parser=-1
  }
  settings_manager={
    user_settings=[
      {
        user_id=0
        device_attached_activities=[
          {
            activity={
              package_name=com.example.mtp
              class_name=com.example.mtp.ReceiverActivity
            }
          }
        ]
      }
    ]
  }
}''' % (events, ports)
    return service('usb', body)


# ------------------------------------------------------------------------------------------
# Telephony
# ------------------------------------------------------------------------------------------
def telephony_registry():
    body = '''Service host process PID: 2300
last known state:
  Phone Id=0
    mCallState=0
    mCallIncomingNumber=+15550100
    mServiceState={mVoiceRegState=0(IN_SERVICE), mDataRegState=0(IN_SERVICE), mOperatorAlphaLong=ExampleCell, getRilVoiceRadioTechnology=14(LTE)}
    mDataConnectionState=2
    mCellIdentity=CellIdentityLte:{ mCi=1000 mPci=1 mTac=2 mMcc=001 mMnc=01 mAlphaLong=ExampleCell}
    mTelephonyDisplayInfo=TelephonyDisplayInfo {network=LTE, overrideNetwork=NONE, isRoaming=false}
  Phone Id=1
    mCallState=0
    mCellIdentity=null
  mPhoneCapability=mMaxActiveVoiceSubscriptions=1 mMaxActiveDataSubscriptions=1
  mActiveDataSubId=1
  mRadioPowerState=1
  mEmergencyNumberList={-1=[[EmergencyNumber: 112, countryIso=, mnc=, src=def , routing=unknown, categories=, urns=]]}
  mDefaultPhoneId=0
  mDefaultSubId=1
local logs:
  2026-11-02T06:05:40.308756 - notifyServiceStateForSubscriber: subId=-1 phoneId=0 state={mVoiceRegState=0(IN_SERVICE)}
  2026-11-02T06:05:47.467786 - notifyDataConnectionForSubscriber: phoneId=0 subId=1  state: CONNECTING, transport: WWAN
  2026-11-02T06:05:47.686650 - onDataConnectionStateChanged(CONNECTED, LTE) subId=1, phoneId=0
  listen logs:
  2026-11-02T06:05:48.100000 - listen subId=1 callback=ExampleCallback
registrations: count=1
  {callingPackage=android binder=android.telephony.PhoneStateListener$IPhoneStateListenerStub@a1b2c3 callback=null}'''
    return service('telephony.registry', body)


def phone(layout):
    if layout == 'a10':
        body = '''------- PhoneGlobals -------
  mNoDataDueToRoaming=false
  mDefaultDataSubId=2
  mDataRoamingNotifLog:
  isSmsCapable=true
------- End PhoneGlobals -------
******* OmtpVvm *******
======= Configs =======
  VisualVoicemailPackageName:null
======== Logs =========
  2026-11-02T06:33:37.833 - VvmSimStateTracker: android.telephony.action.CARRIER_CONFIG_CHANGED
  2026-11-02T06:33:37.848 - VvmSimStateTracker: android.intent.action.SIM_STATE_CHANGED'''
        return service('phone', body)
    body = '''Service host process PID: 2400
------- PhoneGlobals -------
  FeatureFlags:
    exampleFlag=true
  mCurrentRoamingNotification=0
  mDefaultDataSubId=1
  isSmsCapable=true
  mDataRoamingNotifLog:
    2026-11-02T11:34:14.480813 - updateDataRoamingStatus dataAllowed=true, disallowReasons=[], dataIsNowRoaming=false, RoamingNumeric=00101, CallingReason=3
    2026-11-02T11:34:18.792141 - updateDataRoamingStatus dataAllowed=false, disallowReasons=[DATA_DISABLED], dataIsNowRoaming=false, RoamingNumeric=00101, CallingReason=3
------- End PhoneGlobals -------
******* OmtpVvm *******
======= Configs =======
======== Logs =========
'''
    return service('phone', body)


def isub(layout):
    if layout == 'a10':
        body = ''' SubscriptionController:
 defaultSubId=1
 defaultDataSubId=2
 sSlotIndexToSubId[0]: subIds=0=[1]
 sSlotIndexToSubId[1]: subIds=1=[2]
++++++++++++++++++++++++++++++++
 ActiveSubInfoList:
  {id=1, iccId=89990000000000000011 simSlotIndex=0 carrierId=9001 displayName=Example Cell carrierName=Example Cell nameSource=0 iconTint=-16746133 mNumber=+15550101 dataRoaming=0 iconBitmap=android.graphics.Bitmap@cafa83d mcc 001 mnc 01mCountryIso=xx isEmbedded false accessRules null cardString=89990000000000000011 cardId=0 isOpportunistic false mGroupUUID=null profileClass=-1 ehplmns = [] hplmns = [] subscriptionType=0 mGroupOwner=null}
++++++++++++++++++++++++++++++++
 AllSubInfoList:
  {id=1, iccId=89990000000000000011 simSlotIndex=0 carrierId=9001 displayName=Example Cell carrierName=Example Cell nameSource=0 iconTint=-16746133 mNumber=+15550101 dataRoaming=0 iconBitmap=android.graphics.Bitmap@cafa83d mcc 001 mnc 01mCountryIso=xx isEmbedded false accessRules null cardString=89990000000000000011 cardId=0 isOpportunistic false mGroupUUID=null profileClass=-1 ehplmns = [] hplmns = [] subscriptionType=0 mGroupOwner=null}
  {id=2, iccId=89990000000000000022 simSlotIndex=-1 carrierId=9002 displayName=Other Cell carrierName=No service nameSource=0 iconTint=-16746133 mNumber= dataRoaming=1 iconBitmap=android.graphics.Bitmap@5e24df5 mcc 001 mnc 02mCountryIso=xx isEmbedded false accessRules null cardString=89990000000000000022 cardId=1 isOpportunistic false mGroupUUID=null profileClass=-1 subscriptionType=0}
++++++++++++++++++++++++++++++++
  2026-11-02T06:33:42.005 - SubscriptionController: [getActiveSubscriptionInfo]- subId=0 imsi=001010000000001 mNumber=+15550101
'''
        return service('isub', body)
    body = '''Service host process PID: 2500
SubscriptionManagerService:
Active modem count=2
Logical SIM slot sub id mapping:
  Logical SIM slot 0: subId=1
ICCID:
  slot 0: 89990000000000000011[****]
  slot 1:
defaultSubId=1
defaultVoiceSubId=1
defaultDataSubId=1
activeDataSubId=1
areAllSubscriptionsLoaded=true
mSimState[0]=LOADED
mSimState[1]=NOT_READY
Active subscriptions:
  [SubscriptionInfoInternal: id=1 iccId=89990000000000000011[****] simSlotIndex=0 portIndex=0 isEmbedded=0 isRemovableEmbedded=0 carrierId=9001 displayName=Example Cell carrierName=Example Cell isOpportunistic=0 groupUuid= groupOwner= displayNameSource=SIM_SPN iconTint=-16746133 number=[****] dataRoaming=0 mcc=001 mnc=01 ehplmns= hplmns= cardString=89990000000000000011[****] cardId=1 countryIso=xx profileClass=-1 type=LOCAL_SIM imsi=001010000000001[****] numberFromCarrier= userId=-10000]

All subscriptions:
  [SubscriptionInfoInternal: id=1 iccId=89990000000000000011[****] simSlotIndex=0 portIndex=0 isEmbedded=0 isRemovableEmbedded=0 carrierId=9001 displayName=Example Cell carrierName=Example Cell isOpportunistic=0 groupUuid= groupOwner= displayNameSource=SIM_SPN iconTint=-16746133 number=[****] dataRoaming=0 mcc=001 mnc=01 ehplmns= hplmns= cardString=89990000000000000011[****] cardId=1 countryIso=xx profileClass=-1 type=LOCAL_SIM imsi=001010000000001[****]]
  [SubscriptionInfoInternal: id=2 iccId=89990000000000000022[****] simSlotIndex=-1 portIndex=-1 isEmbedded=0 isRemovableEmbedded=0 carrierId=9002 displayName=Other Cell carrierName=No service isOpportunistic=0 groupUuid= groupOwner= displayNameSource=SIM_SPN iconTint=-16746133 number= dataRoaming=1 mcc=001 mnc=02 cardString=89990000000000000022[****] cardId=2 countryIso=xx profileClass=-1 type=LOCAL_SIM imsi=001020000000002[****]]
'''
    return service('isub', body)


def isms():
    body = '''SmsManager for subId = 1:
    Enabled GSM channels:
    CellBroadcast log:
    SMS dispatcher controller log:
    GsmInboundSmsHandler extends StateMachine:
      GsmInboundSmsHandler:
       total records=3
       rec[0]: time=11-02 06:05:37.133 processed=StartupState org=StartupState dest=IdleState what=EVENT_START_ACCEPTING_SMS
       rec[1]: time=11-02 11:34:28.460 processed=IdleState org=IdleState dest=DeliveringState what=EVENT_NEW_SMS
       rec[2]: time=11-02 11:34:28.505 processed=DeliveringState org=DeliveringState dest=IdleState what=EVENT_RETURN_TO_IDLE
      curState=IdleState
    mLocalLog:
        2026-11-02T11:34:30.759660 - Delivering SMS to: com.example.messages com.example.messages.SmsDeliverReceiver, {x-message-id:-1234567890123456789}
CellBroadcastHandler:
 total records=1
  rec[0]: time=11-02 06:05:38.858 processed=IdleState org=IdleState dest=<null> what=3(0x3)
 curState=IdleState
'''
    return service('isms', body)


def carrier_config(layout):
    defaults = '\n'.join('            example_default_key_%02d = %d' % (number, number) for number in range(6))
    applied = '''            carrier_name_string = Example Cell
            carrier_volte_available_bool = true
            example_array_int_array = [-110, -90]
            example_number_string = +15550102'''
    if layout == 'a10':
        body = '''CarrierConfigLoader: com.example.CarrierConfigLoader@46237f2
Phone Id = 0
    Default Values from CarrierConfigManager :
%s

    mConfigFromDefaultApp :
%s

    mConfigFromCarrierApp : null

    mOverrideConfigs : null
CarrierConfigLoadingLog=
2026-11-02T06:33:33.808 - mHandler: 23 phoneId: 0
2026-11-02T06:33:42.677 - update config for phoneId: 0 simState: LOADED''' % (defaults, applied)
        return service('carrier_config', body)
    body = '''Service host process PID: 2600
CarrierConfigLoader: com.example.CarrierConfigLoader@b5a24ed
Phone Id = 0
    Default Values from CarrierConfigManager :
%s

    mConfigFromDefaultApp :
%s

    mConfigFromOemApp : null

    mOverrideConfigs : null

Phone Id = 1
    Default Values from CarrierConfigManager :
%s

    mConfigFromDefaultApp : null

    mNoSimConfig :
            example_nosim_bool = false
mNumPhones=2
mPlatformCarrierConfigPackage=com.example.carrier
mHasSentConfigChange=[true, true]
CarrierConfigLoader local log=
    2026-11-02T06:05:43.952898 - Update config for phoneId=1 simState=NOT_READY
    2026-11-02T06:05:46.041134 - Restored carrier config from cache. phoneId=0, xml=carrierconfig-com.example.carrier-89990000000000000011-9001-00101-FF.xml
    2026-11-02T07:21:51.052455 - System unlocked

Cached config files:
    carrierconfig-com.example.carrier-nosim.xml, modified time=2026-09-02 19:10:46
    carrierconfig-com.example.carrier-89990000000000000011-9001-00101-FF.xml, modified time=2026-09-02 19:10:47
''' % (defaults, applied, defaults)
    return service('carrier_config', body)


def telecom():
    body = '''Service host process PID: 2700
CallsManager:
  mCalls:
  mConnectionSvrFocusMgr:
    Call Focus History:
    2026-11-02T07:18:48.444834 - TC@1
    2026-11-02T07:18:48.468632 - <none>
PhoneAccountRegistrar:
  xmlVersion: 9
  phoneAccounts:
    [[X] PhoneAccount: ComponentInfo{com.example.phone/com.example.phone.TelephonyConnectionService}, 1, UserHandle{0} Capabilities: CallProvider MultiUser PlaceEmerg SimSub  Audio Routes: BESW Schemes: tel voicemail  Extras: Bundle[{android.telecom.extra.SORT_ORDER=0}] GroupId: *** SC Restrictions: [NONE]]
    [[ ] PhoneAccount: ComponentInfo{com.example.chat/com.example.chat.CallService}, ***, UserHandle{11} Capabilities: SelfManaged SuppVideo  Audio Routes: BESW Schemes: tel  Extras: Bundle[{isCoreTelecomAccount=true}] GroupId: ***]
    test emergency PhoneAccount filter: null
Analytics:
  Call TC@1: {
      startTime: 1787900000000
      direction: INCOMING
  }
Historical Events:
  CallTC@1 [Nov 2, 2026 7:18:28 AM](MT - incoming)(User=UserHandle{0})
  	To address: tel:**********
'''
    return service('telecom', body)


def radio_log():
    body = '''--------- beginning of radio
11-02 06:05:47.082 radio  2529  2529 D NetworkTypeController: [0] ServiceState updated: {mVoiceRegState=1(OUT_OF_SERVICE)}
11-02 06:05:47.083 radio  2529  2529 D DNC-0   : onServiceStateChanged: changed to {mVoiceRegState=1(OUT_OF_SERVICE), mDataRegState=1(OUT_OF_SERVICE)}
11-02 06:05:47.090 radio  2529  2529 D SST     : [0] pollState: modemTriggered=true, radioState=1
11-02 06:05:47.100 radio  2529  2529 D DefaultPhoneNotifier: notifyServiceStateForSubId: subId=1
11-02 06:05:47.200  1000  2529  2529 D RILJ    : [1234]> SEND_SMS {smsc=null, pdu=0123456789ABCDEF}
11-02 06:05:47.300  1000  2529  2529 D AT      : > AT+CMGS=15550100
11-02 06:05:47.400 86664 11562 11658 V PhoneNumberUtils: formatNumber: defaultCountryIso: XX
11-02 06:05:47.500 radio  2529  2529 D SST     : [0] subscriber info imsi=001010000000001 number=+15550101 iccid=89990000000000000011
11-02 06:05:47.600 radio  434   434 I chatty  : uid=1001(radio) com.example.phone expire 10 lines
this line is not a logcat line
'''
    return command('RADIO LOG', 'logcat -b radio -v threadtime -v printable -v uid -d *:v', body, '0.068')


# ------------------------------------------------------------------------------------------
# The whole text
# ------------------------------------------------------------------------------------------
def build_report(layout='a16', zone='Europe/Paris', cut=False, newline='\n'):
    properties_layout = 'a16' if layout in ('a16', 'a15') else 'a10'
    header_layout = properties_layout
    text = base.BANNER.format(report=REPORT) + '\n' + base.HEADER[header_layout] + '\n'
    text += base.properties(properties_layout, zone, '')
    text += radio_log()
    if layout == 'a16':
        text += nfc_log()
        text += usb_log()
    text += '------ DUMPSYS (/system/bin/dumpsys) ------\n'
    if layout == 'a16':
        text += nfc(layout) + phone(layout) + carrier_config(layout) + isms() + isub(layout) + bluetooth(layout)
    elif layout == 'a15':
        text += (bluetooth(layout) + nfc(layout) + phone(layout) + usb_service(layout) + telephony_registry() + telecom()
                 + carrier_config(layout) + isms() + isub(layout))
    else:
        text += (bluetooth(layout) + nfc(layout) + phone(layout) + usb_service(layout) + telephony_registry() + telecom()
                 + carrier_config(layout) + isms() + isub(layout))
    if cut:
        # the platform stopped waiting for the Bluetooth manager and the NFC service
        text = text.replace('--------- 0.050s was the duration of dumpsys bluetooth_manager, ending at: 2026-11-02 10:15:20\n',
                            "*** SERVICE 'bluetooth_manager' DUMP TIMEOUT (500ms) EXPIRED ***\n")
        text = text.replace('--------- 0.050s was the duration of dumpsys nfc, ending at: 2026-11-02 10:15:20\n',
                            "*** SERVICE 'nfc' DUMP TIMEOUT (10000ms) EXPIRED ***\n")
        text = text.replace("------ 0.010s was the duration of 'USB LOG' ------\n", '')
        text = text.replace("------ 0.012s was the duration of 'USB LOG' ------\n", '')
    text += "------ 0.900s was the duration of 'DUMPSYS' ------\n\n== dumpstate: done (id 1)\n"
    return text.replace('\n', newline)


def cases():
    """{case name: [(member name, bytes), ...]}"""
    out = {}
    out['synthetic_a16'] = [('Dump/dumpstate.txt', build_report('a16').encode('utf-8'))]
    out['synthetic_a15'] = [('Dump/dumpstate.txt', build_report('a15', zone='Asia/Kolkata').encode('utf-8'))]
    out['synthetic_a10'] = [('Dump/bugreport-example-EXOLD-2026-11-02-10-15-30.txt',
                             build_report('a10', newline='\r\n').encode('utf-8')),
                            ('Dump/main_entry.txt', b'bugreport-example-EXOLD-2026-11-02-10-15-30.txt')]
    out['synthetic_cut'] = [('Dump/dumpstate.txt', build_report('a16', cut=True).encode('utf-8'))]
    out['synthetic_empty'] = [('Dump/dumpstate.txt', (base.BANNER.format(report=REPORT) + '\n').encode())]
    return out


CASE_DESCRIPTIONS = {
    'synthetic_a16': 'Synthetic Android 16 style bug report text (dumpstate.txt) with the Bluetooth manager dump with masked bonded '
                     'devices, link key types, enable log, adapter state records and scan mode changes, the NFC dump with its '
                     'event log, the NFC SYSTEM LOG and USB LOG sections, the subscription manager form of the isub dump with '
                     'SIM identifiers that must not be reported, carrier configuration with a default block, the isms state '
                     'machine records and a RADIO LOG with state tracker, request trace and identifier lines. Device zone '
                     'Europe/Paris. Invented values, contains no real evidence.',
    'synthetic_a15': 'Synthetic Android 15 style bug report text (dumpstate.txt) with the usb, telephony.registry, telecom, '
                     'Bluetooth and NFC service dumps: bonded devices with no class, connection events, a USB event list, '
                     'registered phone accounts, a phone number in the registry state that must not be reported. Device zone '
                     'Asia/Kolkata. Invented values, contains no real evidence.',
    'synthetic_a10': 'Synthetic Android 10 style bug report text (bugreport-*.txt, CRLF line endings) with the older Bluetooth '
                     'layout (middle octets masked), the NFC dump without event log, the usb service dump, the subscription '
                     'controller form of the isub dump and the carrier configuration loading log. Device zone Europe/Paris. '
                     'Invented values, contains no real evidence.',
    'synthetic_cut': 'Synthetic bug report text in which the platform stopped waiting for the Bluetooth manager and the NFC '
                     'service (DUMP TIMEOUT markers) and the USB LOG section has no duration line. Invented values, contains '
                     'no real evidence.',
    'synthetic_empty': 'Synthetic bug report text with the banner and no sections. Invented values, contains no real evidence.',
}


def write_test_cases(repo_root):
    """Writes the case zips (one per artifact and case) and the case file under admin/test/cases."""
    from scripts.artifacts import bugreportRadios      # imported here: the artifact module is not needed to build the texts

    cases_dir = os.path.join(repo_root, 'admin', 'test', 'cases')
    data_dir = os.path.join(cases_dir, 'data', 'bugreportRadios')
    os.makedirs(data_dir, exist_ok=True)
    patterns = list(next(iter(bugreportRadios.__artifacts_v2__.values()))['paths'])
    commit = subprocess.run(['git', '-C', repo_root, 'log', '-1', '--format=%H%n%an%n%ae%n%aI%n%s'], capture_output=True,
                            text=True, check=True).stdout.splitlines()
    last_commit = dict(zip(('hash', 'author_name', 'author_email', 'date', 'message'), commit))
    result = {}
    for case, members in cases().items():
        name = 'case' + case
        for artifact in bugreportRadios.__artifacts_v2__:
            base.write_zip(os.path.join(data_dir, 'testdata.bugreportRadios.%s.%s.zip' % (artifact, name)), members)
        matching = [member for member, _data in members
                    if any(fnmatch.fnmatchcase('root/' + member, pattern) for pattern in patterns)]
        result[name] = {
            'description': CASE_DESCRIPTIONS[case], 'maker': 'synthetic',
            'make_data': {'input_data_path': case + '.zip', 'os': platform.platform(), 'timestamp': datetime.now().isoformat(),
                          'last_commit': last_commit},
            'artifacts': {artifact: {'search_patterns': patterns, 'file_count': len(matching),
                                     'expected_output': {'headers': [], 'data': []}}
                          for artifact in bugreportRadios.__artifacts_v2__}}
    with open(os.path.join(cases_dir, 'testdata.bugreportRadios.json'), 'w', encoding='utf-8') as handle:
        json.dump(result, handle, indent=2)
        handle.write(chr(10))


def main(output):
    os.makedirs(output, exist_ok=True)
    for name, members in cases().items():
        base.write_zip(os.path.join(output, name + '.zip'), members)
    for name in sorted(os.listdir(output)):
        print(name, os.path.getsize(os.path.join(output, name)))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test-cases':
        write_test_cases(os.getcwd())
    else:
        main(sys.argv[1] if len(sys.argv) > 1 else 'bugreport_radios_fixture_out')
