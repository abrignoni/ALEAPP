"""External storage events from the vold dump logs Samsung keeps under data/log.

Samsung devices write rotating text dumps of the volume daemon's log as
data/log/vold-dump_NN. Each line is "YYYY/MM/DD-HH:MM:SS(ZONE)  pid:tid tag message".
This artifact keeps the lines about removable disks: the disk vold creates for a card or
stick, the filesystem it finds, the mount, the unmount and the removal.
"""

__artifacts_v2__ = {
    "get_samsung_vold_external_storage": {
        "name": "Samsung vold - External Storage Events",
        "description": (
            "Parses Samsung's vold-dump logs under data/log for removable-storage events: "
            "disk created, filesystem found, volume mounted, public volume unmount, volume "
            "removed and block device added or removed for a disk vold created, one row per "
            "distinct log line, with the time and zone as stored."
        ),
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-17",
        "last_update_date": "2026-11-17",
        "requirements": "none",
        "category": "Device Events",
        "notes": (
            "Read from the text files data/log/vold-dump_NN. Each kept line is reported "
            "once, even when the rotating dumps repeat it; Dump File names the first file "
            "it was read from. Time (as stored) and Zone (as stored) are the line's own "
            "time and zone abbreviation, not converted: the dumps on one image mix zones "
            "(EST and UTC on samsung_a166u_a16_known_20261117, up to nine abbreviations on "
            "anne_a15). "
            "Kept lines: 'Disk::Disk create' (Disk created, with the disk label and "
            "major:minor numbers as stored), a 'public:M,m: UUID=... TYPE=...' line "
            "(Filesystem found), '<fs>::Mount() ... to <path>' (Volume mounted), "
            "'PublicVolume::doUnmount()++' (Public volume unmount; the line names no "
            "volume), 'VolumeBase::destroy()++ mPath=/storage/...' outside "
            "/storage/emulated (Volume removed), and 'handleBlockEvent with action=N' only "
            "for the major:minor numbers of a disk vold created in the same dumps (Block "
            "device event, action as stored). Log Line (as stored) keeps the whole line. "
            "Known data (samsung_a166u_a16_known_20261117, a microSD card inserted, "
            "unmounted from Settings and removed, with UTC times logged): the seven rows "
            "match the logged times to the second once EST (UTC-5) is applied: disk created "
            "and block event action=1 at the insert, filesystem vfat found, volume mounted "
            "6 seconds later, public volume unmount at the logged unmount, and volume "
            "removed with block event action=2 at the logged removal. action=1 and action=2 "
            "are reported as stored; their meaning rests on these two logged events. "
            "On the ten other registered images that hold vold-dump files no line about an "
            "external disk was found, so they give no rows; their dumps hold the emulated "
            "internal volume's unmount and destroy lines at shutdown, which are not "
            "reported. A USB stick, an adoptable (internal-formatted) card and an encrypted "
            "card are not exercised. The dumps rotate, so older events can be gone; an "
            "empty result does not show that no card was used."
        ),
        "paths": ("*/log/vold-dump*",),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "hard-drive",
        "sample_data": {
            "samsung_a166u_a16_known_20261117": "Android 16 | data/log/vold-dump | 7 rows",
            "adams_ss135dl_a13": "Android 13 | no external disk lines in vold-dump | 0 rows",
            "anne_a15": "Android 15 | no external disk lines in vold-dump | 0 rows",
            "cookbook_a11": "Android 11 | no external disk lines in vold-dump | 0 rows",
            "falken_a326u_a13": "Android 13 | no external disk lines in vold-dump | 0 rows",
            "galaxys10_a10": "Android 10 | no external disk lines in vold-dump | 0 rows",
            "s20fe_a13": "Android 13 | no external disk lines in vold-dump | 0 rows",
            "samsung_a166u_a16_known_20261116": "Android 16 | no external disk lines in vold-dump | 0 rows",
            "samsungs20_a13": "Android 13 | no external disk lines in vold-dump | 0 rows",
            "sharon_a13": "Android 13 | no external disk lines in vold-dump | 0 rows",
            "sharon_a14": "Android 14 | no external disk lines in vold-dump | 0 rows",
        },
    }
}

import os
import re

from scripts.ilapfuncs import artifact_processor, logfunc

LINE_RE = re.compile(
    r"^(?P<time>\d{4}/\d{2}/\d{2}-\d{2}:\d{2}:\d{2})\((?P<zone>[^)]*)\)\s+"
    r"(?P<pid>\d+):(?P<tid>\d+)\s+(?P<tag>\S+)\s(?P<msg>.*)$")
DISK_RE = re.compile(r"Disk::Disk create\((?P<syspath>[^,]*), (?P<label>\w+):(?P<maj>\d+):(?P<min>\d+), "
                     r"flags:(?P<flags>\d+)\)")
FS_RE = re.compile(r"(?P<vol>public:\d+,\d+): UUID=\"(?P<uuid>[^\"]*)\" TYPE=\"(?P<type>[^\"]*)\"")
MOUNT_RE = re.compile(r"(?P<fs>\w+)::Mount\(\) /dev/block/vold/(?P<vol>public:\d+,\d+) to (?P<path>\S+)")
DESTROY_RE = re.compile(r"VolumeBase::destroy\(\)\+\+ mPath=(?P<path>/storage/(?!emulated)\S+)")
BLOCK_RE = re.compile(r"handleBlockEvent with action=(?P<action>\d+) major=(?P<maj>\d+) minor=(?P<min>\d+)")


def _read_lines(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            return handle.read().splitlines()
    except OSError as error:
        logfunc(f"vold-dump: could not read {path}: {error}")
        return []


@artifact_processor
def get_samsung_vold_external_storage(context):
    files = sorted(str(p) for p in context.get_files_found()
                   if os.path.basename(str(p)).startswith("vold-dump") and os.path.isfile(str(p)))
    parsed = []
    disks = set()
    for path in files:
        for line in _read_lines(path):
            match = LINE_RE.match(line)
            if not match:
                continue
            parsed.append((match, line, path))
            disk = DISK_RE.search(match.group("msg"))
            if disk:
                disks.add((disk.group("maj"), disk.group("min")))

    seen = set()
    data_list = []
    source_paths = set()
    for match, line, path in parsed:
        msg = match.group("msg")
        event = volume = fs_type = uuid = mount_path = ""
        disk = DISK_RE.search(msg)
        if disk:
            event = "Disk created"
            volume = f"{disk.group('label')} {disk.group('maj')}:{disk.group('min')}"
        elif FS_RE.search(msg):
            fs = FS_RE.search(msg)
            event, volume, uuid, fs_type = ("Filesystem found", fs.group("vol"),
                                            fs.group("uuid"), fs.group("type"))
        elif MOUNT_RE.search(msg):
            mount = MOUNT_RE.search(msg)
            event, volume, fs_type, mount_path = ("Volume mounted", mount.group("vol"),
                                                  mount.group("fs"), mount.group("path"))
        elif "PublicVolume::doUnmount()++" in msg:
            event = "Public volume unmount"
        elif DESTROY_RE.search(msg):
            event, mount_path = "Volume removed", DESTROY_RE.search(msg).group("path")
        else:
            block = BLOCK_RE.search(msg)
            if block and (block.group("maj"), block.group("min")) in disks:
                event = f"Block device event (action={block.group('action')})"
                volume = f"{block.group('maj')}:{block.group('min')}"
        if not event:
            continue
        key = line.strip()
        if key in seen:
            continue
        seen.add(key)
        source_paths.add(path)
        data_list.append((
            match.group("time"), match.group("zone"), event, volume, fs_type, uuid,
            mount_path, f"{match.group('pid')}:{match.group('tid')}", line.strip(),
            os.path.basename(path),
        ))

    data_list.sort(key=lambda row: (row[0], row[8]))
    data_headers = (
        "Time (as stored)",
        "Zone (as stored)",
        "Event",
        "Disk or Volume",
        "Filesystem",
        "Volume UUID",
        "Path",
        "PID:TID",
        "Log Line (as stored)",
        "Dump File",
    )
    return data_headers, data_list, "\n".join(sorted(source_paths))
