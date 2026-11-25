__artifacts_v2__ = {
    "get_suggestions": {
        "name": "suggestions",
        "description": "Reports three setup_time keys from the Settings Intelligence suggestions.xml "
                       "preferences file, each with its value read as Unix milliseconds in UTC.",
        "author": "@abrignoni",
        "creation_date": "2021-08-15",
        "last_update_date": "2026-11-16",
        "requirements": "none",
        "category": "Device Information",
        "notes": "Only the three keys ending _setup_time that the module lists are reported; every other entry of the file is ignored. Name is the key as stored. What each time marks is not established here. One observation on one build: on the known data emu_a15_reset_known_20261116 (an Android 15 emulator; by the mint record it was booted with its user data wiped and the Settings app was opened about 21 seconds after the time the factory_reset bootstat file records), com.android.settings.suggested.category.DEFERRED_SETUP_setup_time held a time 22 seconds after that bootstat time and about 18 seconds after the suw_finished_time_ms that setup_wizard_info.xml holds, and suggestions.xml was last modified in that same second. The mint record says suggestions.xml did not exist before Settings was opened; the image cannot show that. No run was made with Settings left closed and the app's code was not read, so what writes the key is not established. Other builds and the other two keys were not compared with known times.",
        "paths": ('*/com.google.android.settings.intelligence/shared_prefs/suggestions.xml',),
        "output_types": "standard",
        "artifact_icon": "clock",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.google.android.settings.intelligence vc 1000282241 | 2 rows",
            "pixel7a_a14": "Android 14 | com.google.android.settings.intelligence vc 1000230247 | 3 rows",
            "russell_pixel6a_a13": "Android 13 | com.google.android.settings.intelligence vc 1000217934 | 5 rows",
            "userb2_a13": "Android 13 | com.google.android.settings.intelligence vc 1000232695 | 3 rows",
            "emu_a15_reset_known_20261116": "Android 15 | 1 row (known data)",
        },
    }
}

import datetime
import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.artifacts.storagePathViews import unique_files

SETUP_TIME_KEYS = (
    'com.android.settings.suggested.category.DEFERRED_SETUP_setup_time',
    'com.android.settings/com.android.settings.biometrics.fingerprint.FingerprintEnrollSuggestionActivity_setup_time',
    'com.google.android.setupwizard/com.google.android.setupwizard.deferred.DeferredSettingsSuggestionActivity_setup_time',
)


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
def get_suggestions(context):
    files_found = unique_files(context)

    data_list = []
    source_paths = []
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('suggestions.xml'):
            continue  # Skip all other files

        source_paths.append(file_found)
        root = _parse_xml(file_found)
        for elem in root:
            item = elem.attrib
            if item['name'] in SETUP_TIME_KEYS:
                timestamp = datetime.datetime.fromtimestamp(int(item['value']) / 1000, datetime.timezone.utc)
                data_list.append((timestamp, item['name']))

    data_headers = (('Timestamp', 'datetime'), 'Name')
    return data_headers, data_list, '\n'.join(source_paths)
