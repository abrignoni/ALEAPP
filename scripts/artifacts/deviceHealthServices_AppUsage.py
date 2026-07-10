# pylint: disable=W0613
__artifacts_v2__ = {
    "get_Turbo_AppUsage": {
        "name": "Turbo_AppUsage",
        "description": "Parses application usage via Device Health Services",
        "author": "@KevinPagano3",
        "creation_date": "2021-06-29",
        "last_update_date": "2021-06-29",
        "requirements": "none",
        "category": "Device Health Services",
        "notes": "",
        "paths": ('*/com.google.android.apps.turbo/shared_prefs/app_usage_stats.xml',),
        "output_types": "standard",
        "artifact_icon": "chart-bar",
        "sample_data": {
            "anne_a15": "Android 15 | com.google.android.apps.turbo | 221 rows",
            "galaxys10_a10": "Android 10 | com.google.android.apps.turbo vc 10235989 | 744 rows",
            "hc_pixel8pro_a16": "Android 16 | com.google.android.apps.turbo vc 10272287 | 794 rows",
            "pixel7a_a14": "Android 14 | com.google.android.apps.turbo vc 10270262 | 1677 rows",
            "samsunga53_a14": "Android 14 | com.google.android.apps.turbo | 237 rows",
            "samsungs20_a13": "Android 13 | com.google.android.apps.turbo | 232 rows",
            "sharon_a14": "Android 14 | com.google.android.apps.turbo vc 10261629 | 79 rows",
        },
    }
}

import datetime
import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc


INVALID_XML_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
BARE_AMPERSAND = re.compile(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9A-Fa-f]+);)')


def _parse_xml(file_found):
    """Parse XML, recovering from invalid tokens / unescaped ampersands; empty element if unparseable."""
    try:
        return ET.parse(file_found).getroot()
    except ET.ParseError:
        with open(file_found, encoding='utf-8', errors='replace') as f:
            xml = BARE_AMPERSAND.sub('&amp;', INVALID_XML_CHARS.sub('', f.read()))
        try:
            return ET.fromstring(xml)
        except ET.ParseError as ex:
            logfunc(f'Skipping unparseable XML {file_found}: {ex}')
            return ET.Element('empty')


@artifact_processor
def get_Turbo_AppUsage(files_found, report_folder, seeker, wrap_text):

    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        source_path = file_found
        tree = _parse_xml(file_found)

        for elem in tree.iter(tag='string'):
            splits = elem.text.split('#')
            app_name = splits[0]
            timesplitter = splits[1].split(',')

            for ts in timesplitter:
                timestamp_split = datetime.datetime.fromtimestamp(int(ts) / 1000, datetime.timezone.utc)
                data_list.append((timestamp_split, app_name))

    data_headers = (('App Launch Timestamp', 'datetime'), 'App Name')
    return data_headers, data_list, source_path
