"""Samsung IMS service logs (com.sec.imsservice).

Samsung's IMS stack writes plain-text logs under com.sec.imsservice/files and a small
shared_prefs snapshot. Every log line is 'MM/DD/YYYY HH:MM:SS.mmm   <message>', with no
time zone recorded, so the times are reported as text and not as datetimes.
"""

__artifacts_v2__ = {
    "samsungImsSubscriber": {
        "name": "Samsung IMS Subscriber Identity",
        "description": "Parses the IMS public user identity Samsung stores in com.sec.imsservice, one row per saved entry, with the key (15 digits on the tested images) and the SIP or TEL URI stored against it.",
        "author": "@AlexisBrignoni, Claude, @AlexisBrignoni, Codex",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-11-23",
        "requirements": "none",
        "category": "Samsung IMS Service",
        "notes": "Read from com.sec.imsservice/shared_prefs/saved_impu.xml, which holds saved entries, each "
                 "a key and an IMS public user identity. IMSI (as stored) is the map key, 15 digits on all 10 rows. "
                 "On anne_a15 its visible digits match the partly masked IMSI token in the SIM manager log. On cookbook_a11 the SIM manager log shows the token with all 15 digits, and it equals the key. No other image showed digits in that token. galaxys10_a10 has no SIM manager log. IMPU (as stored) is the SIP or TEL URI. IMPU User Part is the text after the URI's "
                 "scheme up to the first @, or all of it when there is no @, and IMPU Domain is the text after that "
                 "@. The module splits these two out of the stored URI. User Part was 11 or 13 digits on the tested images (9 rows of 11, 1 of 13), 4 of the 10 with a leading +; whether it is a phone number was not established. IMPU Domain is blank for a tel: URI, "
                 "which one tested image stored with no host. On the 13 tested Android extractions 9 held this file, 10 identities in "
                 "all, one image carrying two. This file records no time. What Samsung uses the saved "
                 "value for was not sourced; it is reported as stored.",
        "paths": ('*/com.sec.imsservice/shared_prefs/saved_impu.xml',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 1 rows",
            "anne_a15": "Android 15 | 1 rows",
            "cookbook_a11": "Android 11 | 1 rows",
            "falken_a326u_a13": "Android 13 | 2 rows",
            "galaxys10_a10": "Android 10 | 1 rows",
            "hc_pixel8pro_a17": "Android 17 | no com.sec.imsservice logs | 0 rows",
            "kevin_pocox7_a15": "Android 15 | no com.sec.imsservice logs | 0 rows",
            "pixel7a_a14": "Android 14 | no com.sec.imsservice logs | 0 rows",
            "s20fe_a13": "Android 13 | no saved_impu.xml | 0 rows",
            "samsunga53_a14": "Android 14 | 1 rows",
            "samsungs20_a13": "Android 13 | 1 rows",
            "sharon_a13": "Android 13 | 1 rows",
            "sharon_a14": "Android 14 | 1 rows",
        },
    },
    "samsungImsRegistration": {
        "name": "Samsung IMS Registration Events",
        "description": "Parses the IMS registration log Samsung writes in com.sec.imsservice, one row per timestamped RegiMgr line, with the SIM slot and the two values of the [Profile|State] token where a line carries them, as stored.",
        "author": "@AlexisBrignoni, Claude, @AlexisBrignoni, Codex",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "Samsung IMS Service",
        "notes": "Read from com.sec.imsservice/files/RegiMgr.log, Samsung's IMS registration log. Each line is "
                 "'MM/DD/YYYY HH:MM:SS.mmm   message' with no time zone recorded. That the clock is device local time is not "
                 "measured or sourced in this field. Log Time (no zone recorded) is the stored reading rewritten "
                 "as YYYY-MM-DD HH:MM:SS.mmm, the same digits in an order that sorts by time; it is text, is "
                 "not typed as a datetime and no time zone is attached to it. Time (as stored) keeps the "
                 "original text. One row per line that begins with a date and time; a line "
                 "with no leading timestamp is not reported. SIM Slot, Profile (as stored) and State (as "
                 "stored) come from the slot[N] and [Profile|State] tokens where a line carries them and are blank "
                 "otherwise; on all 22 rows of s20fe_a13 all three were blank. On the 13 "
                 "tested extractions 9 held this log, 15,049 rows, with SIM Slot on 14,705 and Profile on 13,999. "
                 "State (as stored) values were REGISTERED (12,097), CONNECTED (916), REGISTERING (667), "
                 "DEREGISTERING (224), IDLE (62) and CONFIGURED (33). Profile (as stored) is the text before the "
                 "pipe in the same bracket, for example TMobile LTE/WiFi, FirstNet VoLTE and Dish VoLTE. Profile is "
                 "this module's name for that text, and its meaning was not sourced. No row on those 9 images held "
                 "a sip: or tel: URI. That does not show the log never holds call or message content.",
        "paths": ('*/com.sec.imsservice/files/RegiMgr.log',),
        "output_types": "standard",
        "artifact_icon": "phone-call",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 1014 rows",
            "anne_a15": "Android 15 | 3374 rows",
            "cookbook_a11": "Android 11 | 3000 rows",
            "falken_a326u_a13": "Android 13 | 473 rows",
            "galaxys10_a10": "Android 10 | no com.sec.imsservice logs | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | no com.sec.imsservice logs | 0 rows",
            "kevin_pocox7_a15": "Android 15 | no com.sec.imsservice logs | 0 rows",
            "pixel7a_a14": "Android 14 | no com.sec.imsservice logs | 0 rows",
            "s20fe_a13": "Android 13 | 22 rows",
            "samsunga53_a14": "Android 14 | 838 rows",
            "samsungs20_a13": "Android 13 | 327 rows",
            "sharon_a13": "Android 13 | 3001 rows",
            "sharon_a14": "Android 14 | 3000 rows",
        },
    },
    "samsungImsPdn": {
        "name": "Samsung IMS PDN Network Events",
        "description": "Parses the IMS packet data network log Samsung writes in com.sec.imsservice, one row per timestamped line, with the interface, link addresses and P-CSCF addresses where a line carries them, as stored.",
        "author": "@AlexisBrignoni, Claude, @AlexisBrignoni, Codex",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "Samsung IMS Service",
        "notes": "Read from com.sec.imsservice/files/PdnController.log, Samsung's IMS packet data network log, "
                 "with the same no-time-zone timestamps as the registration log, reported as text. One row per line "
                 "that begins with a date and time, whatever the line reports. Interface (as stored) is the name "
                 "logged after InterfaceName: or on an onPdnConnected line. Link Addresses (as stored) and P-CSCF "
                 "Addresses (as stored) are the lists logged after LinkAddresses: and PcscfAddresses:. SIM Slot "
                 "comes from slot[N] where present. On the 13 tested extractions 9 held this log, 1,574 rows, with "
                 "Interface on 892 (all rmnet names) and Link Addresses and P-CSCF Addresses on 786. 682 rows had "
                 "no interface or address and carry only Message (as stored) and any SIM Slot. Three of the 9 "
                 "images (anne_a15, s20fe_a13, samsunga53_a14) had both address columns blank on every row.",
        "paths": ('*/com.sec.imsservice/files/PdnController.log',),
        "output_types": "standard",
        "artifact_icon": "wifi",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 200 rows",
            "anne_a15": "Android 15 | 227 rows",
            "cookbook_a11": "Android 11 | 200 rows",
            "falken_a326u_a13": "Android 13 | 200 rows",
            "galaxys10_a10": "Android 10 | no com.sec.imsservice logs | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | no com.sec.imsservice logs | 0 rows",
            "kevin_pocox7_a15": "Android 15 | no com.sec.imsservice logs | 0 rows",
            "pixel7a_a14": "Android 14 | no com.sec.imsservice logs | 0 rows",
            "s20fe_a13": "Android 13 | 22 rows",
            "samsunga53_a14": "Android 14 | 133 rows",
            "samsungs20_a13": "Android 13 | 188 rows",
            "sharon_a13": "Android 13 | 204 rows",
            "sharon_a14": "Android 14 | 200 rows",
        },
    },
    "samsungImsSimCarrier": {
        "name": "Samsung IMS SIM and Carrier State",
        "description": "Parses the IMS SIM manager log Samsung writes in com.sec.imsservice, one row per timestamped line, with the SIM slot and the mnoname= and mvnoname= values as stored.",
        "author": "@AlexisBrignoni, Claude, @AlexisBrignoni, Codex",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-11-23",
        "requirements": "none",
        "category": "Samsung IMS Service",
        "notes": "Read from com.sec.imsservice/files/SimManager_slot*.log, or SimManager.log on cookbook_a11, Samsung's IMS SIM manager log, with the "
                 "same no-time-zone timestamps as the registration log, reported as text. One row per line that begins with a date and time, whatever the line reports; "
                 "3,021 of the 3,485 rows have MNO Name and MVNO Name blank. MNO Name (as stored) is the text after "
                 "mnoname= and MVNO Name (as stored) is the text after mvnoname=. Each token was on 464 rows. MVNO "
                 "Name was non-blank on 78 of them. On 261 of the 464 mnoname= rows the same line says hassim=false, "
                 "so read the name with the rest of the line. Another 1,523 rows have a blank MNO Name and carry "
                 "mDevMno, mNetMno or mSimMno fields, which only Message (as stored) shows. What Samsung means by "
                 "these fields was not sourced. SIM Slot comes from slot[N]. The IMSI token in this log has no column of its own. It stays in Message (as stored). Where the token carries a value, it is masked in whole or in part on 7 of the 9 images that hold the log and is in the clear on cookbook_a11. On s20fe_a13 the token carries no value on any row. On anne_a15, 46 rows hold the token: 23 are fully masked and 23 show 8 of the 15 characters as digits (the first six and the last two). Those 23 rows also hold a second masked token that repeats the same digits. On the six other tested images that hold the token (139 rows), every character is an asterisk. On cookbook_a11, 41 rows show the token with all 15 digits in the clear. The Samsung IMS Subscriber Identity artifact reports the key stored in saved_impu.xml. On the 13 tested extractions 9 held this log, 3,485 rows; MNO Name values included TMobile_US, TPG_SG, Telefonica_GB, ATT_US and VZW_US.",
        "paths": ('*/com.sec.imsservice/files/SimManager_slot*.log', '*/com.sec.imsservice/files/SimManager.log'),
        "output_types": "standard",
        "artifact_icon": "smartphone",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 300 rows",
            "anne_a15": "Android 15 | 457 rows",
            "cookbook_a11": "Android 11 | SimManager.log | 237 rows",
            "falken_a326u_a13": "Android 13 | 300 rows",
            "galaxys10_a10": "Android 10 | no com.sec.imsservice logs | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | no com.sec.imsservice logs | 0 rows",
            "kevin_pocox7_a15": "Android 15 | no com.sec.imsservice logs | 0 rows",
            "pixel7a_a14": "Android 14 | no com.sec.imsservice logs | 0 rows",
            "s20fe_a13": "Android 13 | 316 rows",
            "samsunga53_a14": "Android 14 | 204 rows",
            "samsungs20_a13": "Android 13 | 496 rows",
            "sharon_a13": "Android 13 | 575 rows",
            "sharon_a14": "Android 14 | 600 rows",
        },
    },
    "samsungImsServiceStarts": {
        "name": "Samsung IMS Created Log Lines",
        "description": "Collects the '> Created (pid: N, binary: X)' lines found in the Samsung IMS service logs in com.sec.imsservice, with the process id and the binary string as stored. What makes the service write the line was not sourced.",
        "author": "@AlexisBrignoni, Claude, @AlexisBrignoni, Codex",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "Samsung IMS Service",
        "notes": "Collects the '> Created (pid: N, binary: X)' lines found anywhere in the com.sec.imsservice logs, "
                 "with the same no-time-zone timestamp as the registration log, reported as text. On the 9 tested "
                 "images that held these logs, 8 of 344 distinct log files had no such line, and 256 of the 6,407 "
                 "lines were the first timestamped line of their file. One log can hold more than one for the same "
                 "process id and binary string. What makes the service write the line was not sourced, so a row is "
                 "a group of these lines and is not shown to be one service start. "
                 "One row per Android user, process id and binary string. Created Line Time (no zone recorded) "
                 "is the time on the earliest '> Created' line of that group, Last Created Line Time (no zone recorded) "
                 "is the time on the latest, and Created Lines is how many such lines the group holds across the logs "
                 "read. Binary String (as stored) is the text after binary:; what it identifies was not sourced. "
                 "The lines carry nothing that separates an earlier use of a process id from a later use under the "
                 "same binary string, so those share a row and the row spans both. Across the 9 images, the median "
                 "spread of groups with more than one line was 0.7 to 5.3 seconds per image, while 18 groups on six "
                 "images spanned more than a day. A wide gap between the two times is consistent with a reused "
                 "process id; what gap separates one use from two is not established. The Android user comes from "
                 "the file's path. A data/data or userdata/data path counts as user 0, and a path outside the app "
                 "data folders leaves it blank. Every row on the 9 images showed user 0, so the split by user is not "
                 "exercised on real data. Per image, the rows carried 1 to 10 distinct binary strings. What a change of "
                 "string between rows means was not checked against an update record. On the 13 tested extractions "
                 "9 held these lines, 257 rows in all, 6 more than one row per process id would give: on four images "
                 "a process id appeared under more than one binary string.",
        "paths": ('*/com.sec.imsservice/files/*.log',),
        "output_types": "standard",
        "artifact_icon": "refresh-cw",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 24 rows",
            "anne_a15": "Android 15 | 48 rows",
            "cookbook_a11": "Android 11 | 16 rows",
            "falken_a326u_a13": "Android 13 | 27 rows",
            "galaxys10_a10": "Android 10 | no com.sec.imsservice logs | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | no com.sec.imsservice logs | 0 rows",
            "kevin_pocox7_a15": "Android 15 | no com.sec.imsservice logs | 0 rows",
            "pixel7a_a14": "Android 14 | no com.sec.imsservice logs | 0 rows",
            "s20fe_a13": "Android 13 | 23 rows",
            "samsunga53_a14": "Android 14 | 9 rows",
            "samsungs20_a13": "Android 13 | 19 rows",
            "sharon_a13": "Android 13 | 21 rows",
            "sharon_a14": "Android 14 | 70 rows",
        },
    },
}

import re

from scripts.artifacts.storagePathViews import android_user as _android_user, unique_files
from scripts.ilapfuncs import artifact_processor

_LINE = re.compile(r'^(\d{2})/(\d{2})/(\d{4}) (\d{2}):(\d{2}):(\d{2})\.(\d{3})\s{2,}(.*)$')
_SLOT = re.compile(r'slot\[(\d+)\]')
_STATE = re.compile(r'\[([^\]|]+)\|([^\]]+)\]')
_CREATED = re.compile(r'^> Created \(pid: (\d+), binary: ([^)]*)\)')
_IMPU = re.compile(r'<string name="([^"]*)">([^<]*)</string>')
_MNO = re.compile(r'mnoname=(\S*)')
_MVNO = re.compile(r'mvnoname=(\S*)')
_IFACE = re.compile(r'InterfaceName:\s*(\S+)')
_PDN_IFACE = re.compile(r'onPdnConnected: network=\d+,\s*([^\s,]+)')
_LINKADDR = re.compile(r'LinkAddresses:\s*\[([^\]]*)\]')
_PCSCF = re.compile(r'PcscfAddresses:\s*\[([^\]]*)\]')


def _when(mo):
    """The line's stored time as sortable text (YYYY-MM-DD HH:MM:SS.mmm).

    The log records no time zone, so the reading is not turned into a datetime and no
    zone is attached to it. Text in this form sorts in the same order as the readings.
    """
    return (f"{mo.group(3)}-{mo.group(1)}-{mo.group(2)} "
            f"{mo.group(4)}:{mo.group(5)}:{mo.group(6)}.{mo.group(7)}")


def _stored(mo):
    return f"{mo.group(1)}/{mo.group(2)}/{mo.group(3)} {mo.group(4)}:{mo.group(5)}:{mo.group(6)}.{mo.group(7)}"


@artifact_processor
def samsungImsSubscriber(context):
    data_list = []
    source_paths = set()
    for source_path in unique_files(context):
        try:
            with open(source_path, 'r', encoding='utf-8', errors='replace') as f:
                text = f.read()
        except OSError:
            continue
        source_paths.add(str(source_path))
        for key, value in _IMPU.findall(text):
            uri = value.strip()
            user = ''
            domain = ''
            m = re.match(r'^\w+:(.+)$', uri)
            if m:
                rest = m.group(1)
                if '@' in rest:
                    user, domain = rest.split('@', 1)
                else:
                    user = rest
            data_list.append((key, uri, user, domain, context.get_relative_path(source_path)))

    data_headers = ('IMSI (as stored)', 'IMPU (as stored)', 'IMPU User Part',
                    'IMPU Domain', 'Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def samsungImsRegistration(context):
    data_list = []
    source_paths = set()
    for source_path in unique_files(context):
        try:
            with open(source_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
        except OSError:
            continue
        source_paths.add(str(source_path))
        for line in lines:
            mo = _LINE.match(line.rstrip('\n'))
            if not mo:
                continue
            msg = mo.group(8)
            slot = _SLOT.search(msg)
            state = _STATE.search(msg)
            data_list.append((
                _when(mo), _stored(mo),
                slot.group(1) if slot else '',
                state.group(1).strip() if state else '',
                state.group(2).strip() if state else '',
                msg,
                context.get_relative_path(source_path)))

    data_headers = ('Log Time (no zone recorded)', 'Time (as stored)', 'SIM Slot',
                    'Profile (as stored)', 'State (as stored)', 'Message (as stored)', 'Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def samsungImsPdn(context):
    data_list = []
    source_paths = set()
    for source_path in unique_files(context):
        try:
            with open(source_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
        except OSError:
            continue
        source_paths.add(str(source_path))
        for line in lines:
            mo = _LINE.match(line.rstrip('\n'))
            if not mo:
                continue
            msg = mo.group(8)
            slot = _SLOT.search(msg)
            iface = _IFACE.search(msg) or _PDN_IFACE.search(msg)
            link = _LINKADDR.search(msg)
            pcscf = _PCSCF.search(msg)
            data_list.append((
                _when(mo), _stored(mo),
                slot.group(1) if slot else '',
                iface.group(1) if iface else '',
                link.group(1).strip() if link else '',
                pcscf.group(1).strip() if pcscf else '',
                msg,
                context.get_relative_path(source_path)))

    data_headers = ('Log Time (no zone recorded)', 'Time (as stored)', 'SIM Slot',
                    'Interface (as stored)', 'Link Addresses (as stored)',
                    'P-CSCF Addresses (as stored)', 'Message (as stored)', 'Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def samsungImsSimCarrier(context):
    data_list = []
    source_paths = set()
    for source_path in unique_files(context):
        try:
            with open(source_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
        except OSError:
            continue
        source_paths.add(str(source_path))
        for line in lines:
            mo = _LINE.match(line.rstrip('\n'))
            if not mo:
                continue
            msg = mo.group(8)
            slot = _SLOT.search(msg)
            mno = _MNO.search(msg)
            mvno = _MVNO.search(msg)
            data_list.append((
                _when(mo), _stored(mo),
                slot.group(1) if slot else '',
                mno.group(1) if mno else '',
                mvno.group(1) if mvno else '',
                msg,
                context.get_relative_path(source_path)))

    data_headers = ('Log Time (no zone recorded)', 'Time (as stored)', 'SIM Slot',
                    'MNO Name (as stored)', 'MVNO Name (as stored)', 'Message (as stored)', 'Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def samsungImsServiceStarts(context):
    instances = {}
    source_paths = set()
    for source_path in unique_files(context):
        try:
            with open(source_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
        except OSError:
            continue
        source_paths.add(str(source_path))
        android_user = _android_user('/' + str(context.get_relative_path(source_path)).replace('\\', '/'))
        for line in lines:
            mo = _LINE.match(line.rstrip('\n'))
            if not mo:
                continue
            cr = _CREATED.match(mo.group(8))
            if not cr:
                continue
            # A process id is reused over time, so it does not identify one start on
            # its own. The Android user and the build string are the only other things a
            # '> Created' line and its file carry, so the key uses all three.
            key = (android_user, cr.group(1), cr.group(2))
            when = _when(mo)
            rec = instances.get(key)
            if rec is None:
                instances[key] = [when, _stored(mo), when, 1]
                continue
            rec[3] += 1
            if when < rec[0]:
                rec[0], rec[1] = when, _stored(mo)
            if when > rec[2]:
                rec[2] = when

    data_list = [(rec[0], rec[1], rec[2], rec[3], key[1], key[2], key[0])
                 for key, rec in instances.items()]
    data_headers = ('Created Line Time (no zone recorded)', 'Time (as stored)',
                    'Last Created Line Time (no zone recorded)', 'Created Lines',
                    'Process PID (as stored)', 'Binary String (as stored)', 'Android User')
    return data_headers, data_list, '\n'.join(sorted(source_paths))
