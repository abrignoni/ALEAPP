# pylint: disable=W0613
__artifacts_v2__ = {
    "get_build": {
        "name": "Build",
        "description": "",
        "author": "",
        "creation_date": "2020-03-30",
        "last_update_date": "2020-03-30",
        "requirements": "none",
        "category": "Device Information",
        "notes": "",
        "paths": ('*/vendor/build.prop',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "info-circle",
    }
}

import scripts.artifacts.artGlobals

from scripts.ilapfuncs import artifact_processor, logfunc, logdevinfo


@artifact_processor
def get_build(files_found, report_folder, seeker, wrap_text):
    data_list = []
    Androidversion = scripts.artifacts.artGlobals.versionf

    source_path = str(files_found[0])
    with open(source_path, "r", encoding='utf-8', errors='replace') as f:
        for line in f:
            splits = line.split('=')
            if splits[0] == 'ro.product.vendor.manufacturer':
                key = 'Manufacturer'
                value = splits[1]
                logdevinfo(f"<b>Manufacturer: </b>{value}")
                data_list.append((key, value))
            elif splits[0] == 'ro.product.vendor.brand':
                key = 'Brand'
                value = splits[1]
                logdevinfo(f"<b>Brand: </b>{value}")
                data_list.append((key, value))
            elif splits[0] == 'ro.product.vendor.model':
                key = 'Model'
                value = splits[1]
                logdevinfo(f"<b>Model: </b>{value}")
                data_list.append((key, value))
            elif splits[0] == 'ro.product.vendor.device':
                key = 'Device'
                value = splits[1]
                logdevinfo(f"<b>Device: </b>{value}")
                data_list.append((key, value))
            elif splits[0] == 'ro.vendor.build.version.release':
                key = 'Android Version'
                value = splits[1]
                if Androidversion == 0:
                    scripts.artifacts.artGlobals.versionf = value
                logfunc(f"Android version per build.props: {value}")
                logdevinfo(f"<b>Android version per build.props: </b>{value}")
                data_list.append((key, value))
            elif splits[0] == 'ro.vendor.build.version.sdk':
                key = 'SDK'
                value = splits[1]
                logdevinfo(f"<b>SDK: </b>{value}")
                data_list.append((key, value))
            elif splits[0] == 'ro.system.build.version.release':
                key = 'Version Release'
                value = splits[1]
                logdevinfo(f"<b>Version release: </b>{value}")
                data_list.append((key, value))

    data_headers = ('Key', 'Value')
    return data_headers, data_list, source_path
