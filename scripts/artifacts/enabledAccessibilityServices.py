"""Enabled accessibility services from settings_secure.xml, for ALEAPP.

Author: @AlexisBrignoni, Claude.
"""

__artifacts_v2__ = {
    "enabledAccessibilityServices": {
        "name": "Enabled Accessibility Services",
        "description": "Accessibility services listed in the enabled_accessibility_services setting of each "
                       "Android user's settings_secure.xml, one row per service, with the accessibility_enabled "
                       "value and the package the file records for each of the two settings.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-15",
        "last_update_date": "2026-11-15",
        "requirements": "none",
        "category": "Device Information",
        "notes": "Reads settings_secure.xml under system/users/<user id> (text or ABX, through the same reader as "
                 "settingsSecure). In AOSP (android-16.0.0_r1) the setting is "
                 "Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES, documented there as the list of the enabled "
                 "accessibility providers (frameworks/base core/java/android/provider/Settings.java, lines 8899 to "
                 "8904), and AccessibilityManagerService reads it as a list split at ':' "
                 "(services/accessibility/java/com/android/server/accessibility/AccessibilityManagerService.java, "
                 "line 284 for the separator and lines 2860 to 2878 for the split, reached from "
                 "readEnabledAccessibilityServicesLocked at line 2628 through lines 2812 to 2815 and 2853 to "
                 "2857), so one row is one part of the stored value, empty parts left out. A part that is not a "
                 "valid component name, or a repeated part, still gets a row. Service Component is that part as "
                 "read (package/class, where the class can be in the short .Class form; "
                 "AccessibilityManagerService.java lines 2815 and 2838); if the file needs the reader's repair "
                 "pass, control characters are removed first. Package is the part before the '/'. Accessibility "
                 "Enabled is the value of accessibility_enabled in the same file, as read. Services Setting "
                 "Package and Accessibility Enabled Package are the package attribute of each setting: "
                 "SettingsState writes it with every setting "
                 "(packages/SettingsProvider/src/com/android/providers/settings/SettingsState.java, line 1331), "
                 "and SettingsProvider passes the caller's package when a secure setting is changed "
                 "(SettingsProvider.java, line 1861). It is the package recorded with the setting's current entry, "
                 "normally the last caller that changed it, not who first enabled a service; a reset to default "
                 "keeps the earlier package (SettingsState.java, line 1775). On the known data "
                 "enabled_accessibility_services was set from adb shell and recorded com.android.shell; "
                 "accessibility_enabled recorded android, and AccessibilityManagerService writes that setting "
                 "itself (lines 3475 to 3487). AOSP writes no time attribute with a setting (SettingsState.java, "
                 "lines 1326 to 1342), and none was present in the files read. Being listed does not show the "
                 "service was running or what it did, and the artifact does not say whether a listed service is "
                 "benign. A value stored under valueBase64 is decoded from base64. A setting that is absent or "
                 "empty gives no row, and a file that does not parse gives no row and a log line. Other "
                 "accessibility settings (shortcut targets, button targets, touch exploration) are not read. The "
                 "app ops artifacts name the BIND_ACCESSIBILITY_SERVICE and ACCESS_ACCESSIBILITY ops when the app "
                 "ops files hold them. User is the user id folder. Evidence tier: data-proven on a "
                 "settings_secure.xml (ABX) pulled from an Android 15 emulator (google_apis image, no account) "
                 "after two built-in services were enabled with adb shell settings put for this artifact and reset "
                 "afterwards: 2 rows. That file is not a corpus image and has no corpus key. The nine corpus "
                 "images in sample_data did not hold the setting; the samsungs20_a13 user 0 file did not parse.",
        "paths": ('*/system/users/*/settings_secure.xml',),
        "output_types": ["html", "tsv", "lava"],
        "artifact_icon": "eye",
        "sample_data": {
            "anne_a15": "Android 15 | 0 rows (setting absent)",
            "galaxys10_a10": "Android 10 | 0 rows (setting absent)",
            "hc_pixel8pro_a16": "Android 16 | 0 rows (setting absent)",
            "kevin_pocox7_a15": "Android 15 | 0 rows (setting absent)",
            "pixel7a_a14": "Android 14 | 0 rows (setting absent)",
            "samsunga53_a14": "Android 14 | 0 rows (setting absent)",
            "sharon_a14": "Android 14 | 0 rows (setting absent)",
            "russell_pixel6a_a13": "Android 13 | 0 rows (setting absent)",
            "userb2_a13": "Android 13 | 0 rows (setting absent)",
        },
    }
}

import base64
import binascii
import os

from scripts.ilapfuncs import artifact_processor
from scripts.artifacts.settingsSecure import parse_settings_root

_SERVICES = 'enabled_accessibility_services'
_ENABLED = 'accessibility_enabled'


def _value(setting):
    """The value attribute, or valueBase64 decoded as UTF-8; '' when neither is present."""
    if setting.get('value') is not None:
        return setting.get('value')
    encoded = setting.get('valueBase64')
    if encoded is None:
        return ''
    try:
        return base64.b64decode(encoded).decode('utf-8', 'replace')
    except (binascii.Error, ValueError):
        return encoded


def service_rows(root):
    """(component, package, accessibility_enabled, services written by, enabled written by) per listed service."""
    settings = {s.get('name'): s for s in root.iter('setting')}
    services = settings.get(_SERVICES)
    if services is None:
        return []
    enabled = settings.get(_ENABLED)
    enabled_value = '' if enabled is None else _value(enabled)
    enabled_by = '' if enabled is None else (enabled.get('package') or '')
    rows = []
    for part in _value(services).split(':'):
        if not part:
            continue
        rows.append((part, part.split('/', 1)[0], enabled_value, services.get('package') or '', enabled_by))
    return rows


@artifact_processor
def enabledAccessibilityServices(context):
    data_headers = ('User', 'Service Component', 'Package', 'Accessibility Enabled',
                    'Services Setting Package', 'Accessibility Enabled Package')
    data_list, sources = [], []
    for file_found in sorted(str(f) for f in context.get_files_found()):
        parts = file_found.replace('\\', '/').split('/')
        if '/mirror/' in file_found.replace('\\', '/') or os.path.basename(file_found) != 'settings_secure.xml':
            continue
        user = parts[-2]
        if not user.isdigit():
            continue
        root = parse_settings_root(file_found, 'Enabled Accessibility Services')
        if root is None:
            continue
        sources.append(file_found)
        data_list.extend((user,) + row for row in service_rows(root))
    return data_headers, data_list, '\n'.join(sources)
