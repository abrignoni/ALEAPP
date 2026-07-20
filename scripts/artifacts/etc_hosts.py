# pylint: disable=W0613
__artifacts_v2__ = {
    "get_etc_hosts": {
        "name": "Etc_hosts",
        "description": "Parses host-to-IP mappings (IP address and hostname) from the system etc/hosts file.",
        "author": "",
        "creation_date": "2020-10-09",
        "last_update_date": "2020-10-09",
        "requirements": "none",
        "category": "Etc Hosts",
        "notes": "",
        "paths": ('*/system/etc/hosts',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "file",
        "sample_data": {
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 0 rows",
            "pixel7a_a14": "Android 14 | 0 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "sharon_a14": "Android 14 | 0 rows",
            "russell_pixel6a_a13": "Android 13 | 0 rows",
        },
    }
}

import codecs

from scripts.ilapfuncs import artifact_processor


@artifact_processor
def get_etc_hosts(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = str(files_found[0])

    with codecs.open(source_path, 'r', 'utf-8-sig') as csvfile:
        for row in csvfile:
            sline = '\t'.join(row.split())
            sline = sline.split('\t')
            sline_one = sline[0]
            sline_two = sline[1]
            if (sline_one == '127.0.0.1' and sline_two == 'localhost') or \
                (sline_one == '::1' and sline_two == 'ip6-localhost'):
                pass  # Skipping the defaults, so only anomaly entries are seen
            else:
                data_list.append((sline_one, sline_two))

    data_headers = ('IP Address', 'Hostname')
    return data_headers, data_list, source_path
