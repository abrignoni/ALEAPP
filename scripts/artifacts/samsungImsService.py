"""Samsung IMS service logs (com.sec.imsservice).

Samsung's IMS stack writes plain-text logs under com.sec.imsservice/files and a small
shared_prefs snapshot. Every log line is 'MM/DD/YYYY HH:MM:SS.mmm   <message>' in the
device's local wall clock, with no time zone recorded.
"""

__artifacts_v2__ = {
    "samsungImsSubscriber": {
        "name": "Samsung IMS Subscriber Identity",
        "description": "Parses the IMS public user identity Samsung stores in com.sec.imsservice, mapping each SIM IMSI to its registered SIP URI.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Samsung IMS Service",
        "notes": "Read from com.sec.imsservice/shared_prefs/saved_impu.xml, which maps a SIM's IMSI to the IMS "
                 "public user identity the device registered. IMSI (as stored) is the map key, IMPU (as stored) is "
                 "the SIP or TEL URI, IMPU User Part is the URI's user portion (a phone number on the tested "
                 "images) and IMPU Domain is the host. IMPU Domain is blank for a tel: URI, which one tested image "
                 "stored with no host. On the 13 tested Android extractions 9 held this file, 10 identities in "
                 "all, one image carrying two. This file records no time. The identity is the one the SIM "
                 "presented to the carrier's IMS network as stored.",
        "paths": ('*/com.sec.imsservice/shared_prefs/saved_impu.xml',),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 1 rows",
            "anne_a15": "Android 15 | 1 rows",
            "cookbook_a11": "Android 11 | 1 rows",
            "falken_a326u_a13": "Android 326 | 2 rows",
            "galaxys10_a10": "Android 10 | 1 rows",
            "hc_pixel8pro_a17": "Android 17 | no com.sec.imsservice logs | 0 rows",
            "kevin_pocox7_a15": "Android 15 | no com.sec.imsservice logs | 0 rows",
            "pixel7a_a14": "Android 14 | no com.sec.imsservice logs | 0 rows",
            "s20fe_a13": "Android 13 | no com.sec.imsservice logs | 0 rows",
            "samsunga53_a14": "Android 14 | 1 rows",
            "samsungs20_a13": "Android 13 | 1 rows",
            "sharon_a13": "Android 13 | 1 rows",
            "sharon_a14": "Android 14 | 1 rows",
        },
    },
    "samsungImsRegistration": {
        "name": "Samsung IMS Registration Events",
        "description": "Parses the IMS registration log Samsung writes in com.sec.imsservice, one row per RegiMgr line with SIM slot, carrier profile and registration state as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Samsung IMS Service",
        "notes": "Read from com.sec.imsservice/files/RegiMgr.log, Samsung's IMS registration log. Each line is "
                 "'MM/DD/YYYY HH:MM:SS.mmm   message' in the device's local wall clock with no time zone recorded, "
                 "so Timestamp holds that local time stored verbatim and must not be read as UTC, and Time (as "
                 "stored) keeps the original text. One row per line. SIM Slot, Profile (as stored) and State (as "
                 "stored) come from the slot[N] and [Profile|State] tokens where a line carries them and are blank "
                 "otherwise; on one image whose log held only 22 early lines all three were blank. On the 13 "
                 "tested extractions 9 held this log, 15,049 rows, with SIM Slot on 14,705 and Profile on 13,999. "
                 "State (as stored) values were REGISTERED (12,097), CONNECTED (916), REGISTERING (667), "
                 "DEREGISTERING (224), IDLE (62) and CONFIGURED (33), and Profile named the carrier and access "
                 "type as stored, for example TMobile LTE/WiFi, FirstNet VoLTE and Dish VoLTE. The log records "
                 "registration state, not call or message content.",
        "paths": ('*/com.sec.imsservice/files/RegiMgr.log',),
        "output_types": "standard",
        "artifact_icon": "phone-call",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 1014 rows",
            "anne_a15": "Android 15 | 3374 rows",
            "cookbook_a11": "Android 11 | 3000 rows",
            "falken_a326u_a13": "Android 326 | 473 rows",
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
        "description": "Parses the IMS packet data network log Samsung writes in com.sec.imsservice, with interface, link addresses and P-CSCF addresses as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Samsung IMS Service",
        "notes": "Read from com.sec.imsservice/files/PdnController.log, Samsung's IMS packet data network log, "
                 "with the same local no-time-zone timestamps as the registration log. Interface (as stored) is "
                 "the rmnet name from an onPdnConnected or onLinkPropertiesChanged line; Link Addresses (as "
                 "stored) and P-CSCF Addresses (as stored) are the addresses from a full onLinkPropertiesChanged "
                 "block, which some images do not log, leaving those columns blank; SIM Slot comes from slot[N] "
                 "where present. On the 13 tested extractions 9 held this log, 1,574 rows, with Interface on 892 "
                 "and Link Addresses and P-CSCF Addresses on 786. Link Addresses are the device's own IMS "
                 "addresses and P-CSCF Addresses the carrier's SIP proxies, both as the carrier assigned them.",
        "paths": ('*/com.sec.imsservice/files/PdnController.log',),
        "output_types": "standard",
        "artifact_icon": "wifi",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 200 rows",
            "anne_a15": "Android 15 | 227 rows",
            "cookbook_a11": "Android 11 | 200 rows",
            "falken_a326u_a13": "Android 326 | 200 rows",
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
        "description": "Parses the IMS SIM manager log Samsung writes in com.sec.imsservice, with SIM slot, carrier MNO and MVNO names and IMSI as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Samsung IMS Service",
        "notes": "Read from com.sec.imsservice/files/SimManager_slot*.log, Samsung's IMS SIM manager log, with the "
                 "same local no-time-zone timestamps. MNO Name (as stored) and MVNO Name (as stored) are the "
                 "operator and virtual-operator names Samsung logged; MVNO Name is blank unless the SIM is an "
                 "MVNO, so it is empty on most rows, present on 37 of 3,248. SIM Slot comes from slot[N]. The IMSI "
                 "in this log is masked with asterisks, so it is not surfaced here; the SIM's real IMSI is in the "
                 "Samsung IMS Subscriber Identity artifact. On the 13 tested extractions 8 held this log, 3,248 "
                 "rows; MNO Name values included TMobile_US, TPG_SG, Telefonica_GB, ATT_US and VZW_US, and a SIM "
                 "change shows as MNO Name changing between rows.",
        "paths": ('*/com.sec.imsservice/files/SimManager_slot*.log',),
        "output_types": "standard",
        "artifact_icon": "smartphone",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 300 rows",
            "anne_a15": "Android 15 | 457 rows",
            "cookbook_a11": "Android 11 | no com.sec.imsservice logs | 0 rows",
            "falken_a326u_a13": "Android 326 | 300 rows",
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
        "name": "Samsung IMS Service Starts",
        "description": "Collects the process-start lines the Samsung IMS service writes at the head of its logs in com.sec.imsservice, with the process id and firmware build as stored.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Samsung IMS Service",
        "notes": "Collects the '> Created (pid: N, binary: <firmware>)' line Samsung writes at the head of each "
                 "com.sec.imsservice log, deduplicated to one row per process id (the earliest time that pid was "
                 "seen), with the same local no-time-zone timestamp. Service Start Time is when the IMS service "
                 "process started and Firmware Build (as stored) is the build string it recorded. Firmware Build "
                 "is one value on a device that took no update in the log window and several on a device that did, "
                 "so this doubles as a firmware update timeline; one tested image recorded ten builds. On the 13 "
                 "tested extractions 9 held these lines, 251 process starts in all.",
        "paths": ('*/com.sec.imsservice/files/*.log',),
        "output_types": "standard",
        "artifact_icon": "refresh-cw",
        "sample_data": {
            "adams_ss135dl_a13": "Android 13 | 24 rows",
            "anne_a15": "Android 15 | 47 rows",
            "cookbook_a11": "Android 11 | 16 rows",
            "falken_a326u_a13": "Android 326 | 26 rows",
            "galaxys10_a10": "Android 10 | no com.sec.imsservice logs | 0 rows",
            "hc_pixel8pro_a17": "Android 17 | no com.sec.imsservice logs | 0 rows",
            "kevin_pocox7_a15": "Android 15 | no com.sec.imsservice logs | 0 rows",
            "pixel7a_a14": "Android 14 | no com.sec.imsservice logs | 0 rows",
            "s20fe_a13": "Android 13 | 23 rows",
            "samsunga53_a14": "Android 14 | 9 rows",
            "samsungs20_a13": "Android 13 | 19 rows",
            "sharon_a13": "Android 13 | 20 rows",
            "sharon_a14": "Android 14 | 67 rows",
        },
    },
}

import re
from datetime import datetime, timezone

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
    """Local wall-clock datetime for a matched line, stored verbatim (no zone conversion)."""
    y, mon, d = int(mo.group(3)), int(mo.group(1)), int(mo.group(2))
    h, mi, s, ms = int(mo.group(4)), int(mo.group(5)), int(mo.group(6)), int(mo.group(7))
    return datetime(y, mon, d, h, mi, s, ms * 1000, tzinfo=timezone.utc)


def _stored(mo):
    return f"{mo.group(1)}/{mo.group(2)}/{mo.group(3)} {mo.group(4)}:{mo.group(5)}:{mo.group(6)}.{mo.group(7)}"


def _android_user(path):
    p = path.replace('\\', '/')
    m = re.search(r'/data/user(?:_de)?/(\d+)/', p)
    if m:
        return m.group(1)
    m = re.search(r'/data_mirror/data_[a-z]+/[^/]+/(\d+)/', p)
    if m:
        return m.group(1)
    m = re.search(r'/data/media/(\d+)/', p)
    if m:
        return m.group(1)
    return '0'


def _dedupe(files_found):
    """One file per (Android user, path from com.sec.imsservice) so mirrored storage views collapse."""
    seen = {}
    for f in files_found:
        p = str(f).replace('\\', '/')
        idx = p.find('com.sec.imsservice/')
        sub = p[idx:] if idx != -1 else p
        key = (_android_user(p), sub)
        seen.setdefault(key, f)
    return list(seen.values())


@artifact_processor
def samsungImsSubscriber(context):
    data_list = []
    source_paths = set()
    for source_path in _dedupe(context.get_files_found()):
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

    data_headers = ('IMSI (as stored)', 'IMPU (as stored)', 'IMPU User Part (as stored)',
                    'IMPU Domain (as stored)', 'Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def samsungImsRegistration(context):
    data_list = []
    source_paths = set()
    for source_path in _dedupe(context.get_files_found()):
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

    data_headers = (('Timestamp', 'datetime'), 'Time (as stored)', 'SIM Slot',
                    'Profile (as stored)', 'State (as stored)', 'Message (as stored)', 'Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def samsungImsPdn(context):
    data_list = []
    source_paths = set()
    for source_path in _dedupe(context.get_files_found()):
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

    data_headers = (('Timestamp', 'datetime'), 'Time (as stored)', 'SIM Slot',
                    'Interface (as stored)', 'Link Addresses (as stored)',
                    'P-CSCF Addresses (as stored)', 'Message (as stored)', 'Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def samsungImsSimCarrier(context):
    data_list = []
    source_paths = set()
    for source_path in _dedupe(context.get_files_found()):
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

    data_headers = (('Timestamp', 'datetime'), 'Time (as stored)', 'SIM Slot',
                    'MNO Name (as stored)', 'MVNO Name (as stored)', 'Message (as stored)', 'Source File')
    return data_headers, data_list, '\n'.join(sorted(source_paths))


@artifact_processor
def samsungImsServiceStarts(context):
    instances = {}
    source_paths = set()
    for source_path in _dedupe(context.get_files_found()):
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
            cr = _CREATED.match(mo.group(8))
            if not cr:
                continue
            pid, firmware = cr.group(1), cr.group(2)
            when = _when(mo)
            rec = instances.get(pid)
            if rec is None or when < rec[0]:
                instances[pid] = [when, _stored(mo), firmware]

    data_list = [(rec[0], rec[1], pid, rec[2]) for pid, rec in instances.items()]
    data_headers = (('Service Start Time', 'datetime'), 'Time (as stored)',
                    'Process PID (as stored)', 'Firmware Build (as stored)')
    return data_headers, data_list, '\n'.join(sorted(source_paths))
