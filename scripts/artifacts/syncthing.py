__artifacts_v2__ = {
    "syncthing_devices": {
        "name": "Syncthing - Devices",
        "description": "Parses the devices configured in the Syncthing Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Syncthing",
        "notes": "One row per device element in files/config.xml, which lists this device together "
                 "with every device it is configured to synchronise with. Each row carries the Device "
                 "ID, the Name the user gave it, its configured addresses, whether it is paused or "
                 "marked untrusted, the Auto Accept Folders flag, and the introducer fields. Auto "
                 "Accept Folders is blank unless the device is set to accept folders offered to it "
                 "automatically, which neither device was on the tested config. "
                 "Introduced By names the device that added this one to the configuration when Syncthing"
                 "'s introducer feature was used, which is a trust relationship worth following. The "
                 "config does not itself flag which entry is the local device; on the tested device the "
                 "local one carried the device model as its Name. The local device's own ID can be "
                 "derived from the certificate in files/cert.pem, which is not parsed here. A device "
                 "being present means the user set up a sync relationship with it, not that a transfer "
                 "took place.",
        "paths": ('*/com.nutomic.syncthingandroid/files/config.xml',),
        "output_types": "standard",
        "artifact_icon": "devices"
    },
    "syncthing_folders": {
        "name": "Syncthing - Folders",
        "description": "Parses the shared folders configured in the Syncthing Android client.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-30",
        "last_update_date": "2026-08-30",
        "requirements": "none",
        "category": "Syncthing",
        "notes": "One row per folder element in files/config.xml. Each row gives the folder's ID, the "
                 "user's Label, the local Path being synced, the folder Type (sendonly, receiveonly or "
                 "sendreceive as stored), whether it is paused, the rescan interval, and Shared With, "
                 "the devices the folder is shared with. Shared With resolves each shared device id to "
                 "the device name from the same config where one is set, so it shows which other "
                 "devices receive or send this folder's files. The Path is where the synced files live "
                 "on this device. On the tested device Syncthing had auto created a sendonly Camera "
                 "folder for the DCIM directory.",
        "paths": ('*/com.nutomic.syncthingandroid/files/config.xml',),
        "output_types": "standard",
        "artifact_icon": "folder-share"
    }
}

import os
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.artifacts.storagePathViews import unique_files


def _child_text(element, tag):
    child = element.find(tag)
    if child is None or child.text is None:
        return ''
    return child.text.strip()


def _configs(context):
    for file_found in unique_files(context):
        file_found = str(file_found).replace('\\', '/')
        if os.path.isdir(file_found) or not file_found.endswith('config.xml'):
            continue
        try:
            root = ET.parse(file_found).getroot()
        except ET.ParseError as error:
            logfunc(f'Syncthing: could not parse {file_found}: {error}')
            continue
        if root.tag != 'configuration':
            continue
        yield root, file_found


def _device_names(root):
    names = {}
    for device in root.findall('device'):
        did = device.get('id')
        if did:
            names[did] = device.get('name', '')
    return names


@artifact_processor
def syncthing_devices(context):
    data_list = []
    sources = []
    for root, file_found in _configs(context):
        read_any = False
        for device in root.findall('device'):
            addresses = '; '.join(a.text.strip() for a in device.findall('address')
                                  if a.text and a.text.strip())
            data_list.append((
                device.get('id', '') or '',
                device.get('name', '') or '',
                addresses,
                device.get('compression', '') or '',
                'Yes' if _child_text(device, 'paused').lower() == 'true' else '',
                'Yes' if _child_text(device, 'untrusted').lower() == 'true' else '',
                'Yes' if _child_text(device, 'autoAcceptFolders').lower() == 'true' else '',
                device.get('introducer', '') or '',
                device.get('introducedBy', '') or '',
                context.get_relative_path(file_found),
            ))
            read_any = True
        if read_any and file_found not in sources:
            sources.append(file_found)

    data_headers = ('Device ID', 'Name', 'Addresses', 'Compression', 'Paused', 'Untrusted',
                    'Auto Accept Folders', 'Introducer', 'Introduced By', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def syncthing_folders(context):
    data_list = []
    sources = []
    for root, file_found in _configs(context):
        names = _device_names(root)
        read_any = False
        for folder in root.findall('folder'):
            shared = []
            for device in folder.findall('device'):
                did = device.get('id', '')
                name = names.get(did, '')
                shared.append(f'{name} ({did})' if name else did)
            data_list.append((
                folder.get('id', '') or '',
                folder.get('label', '') or '',
                folder.get('path', '') or '',
                folder.get('type', '') or '',
                'Yes' if _child_text(folder, 'paused').lower() == 'true' else '',
                folder.get('rescanIntervalS', '') or '',
                '; '.join(shared),
                context.get_relative_path(file_found),
            ))
            read_any = True
        if read_any and file_found not in sources:
            sources.append(file_found)

    data_headers = ('Folder ID', 'Label', 'Path', 'Type', 'Paused',
                    'Rescan Interval (seconds)', 'Shared With', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
