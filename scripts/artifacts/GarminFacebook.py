# pylint: disable=W0613
__artifacts_v2__ = {
    "get_garminFB": {
        "name": "Garmin - Facebook Account",
        "description": "Cached Facebook account data (token, profile) from the Garmin Connect shared_prefs XML",
        "author": "Fabian Nunes {fabiannunes12@gmail.com}",
        "creation_date": "2023-02-24",
        "last_update_date": "2023-02-24",
        "requirements": "none",
        "category": "Garmin",
        "notes": "Parses on-device cached data only; the original's live Facebook Graph API lookup was removed.",
        "paths": ('*/com.garmin.android.apps.connectmobile/shared_prefs/com.facebook*',),
        "output_types": "standard",
        "artifact_icon": "activity",
        "sample_data": {
            "pixel7a_a14": "Android 14 | com.garmin.android.apps.connectmobile vc 8806 | 1 row",
        },
    }
}

import datetime
import json
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc

_ATTRIBUTES = ("com.facebook.AccessTokenManager.CachedAccessToken",
               "com.facebook.ProfileManager.CachedProfile",
               "anonymousAppDeviceGUID",
               "com.facebook.sdk.AutoInitEnabled")
_TS_KEYS = ("last_refresh", "data_access_expiration_time", "expires_at")


def _fb_ts(value):
    try:
        v = int(value)
    except (ValueError, TypeError):
        return str(value)
    try:
        dt = (datetime.datetime.fromtimestamp(v / 1000, datetime.timezone.utc)
              if len(str(abs(v))) == 13
              else datetime.datetime.fromtimestamp(v, datetime.timezone.utc))
        return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    except (ValueError, OverflowError, OSError):
        return str(value)


def _s(value):
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return value


@artifact_processor
def get_garminFB(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        source_path = file_found
        try:
            root = ET.parse(file_found).getroot()
        except (ET.ParseError, OSError, ValueError) as exc:
            logfunc(f'Garmin Facebook: could not parse {file_found}: {exc}')
            continue

        user_info = {}
        for child in root:
            name = child.attrib.get("name")
            if name in _ATTRIBUTES:
                if "value" in child.attrib:
                    user_info[name] = child.attrib["value"]
                elif child.text:
                    user_info[name] = child.text

        for key, value in user_info.items():
            if key == "com.facebook.AccessTokenManager.CachedAccessToken":
                try:
                    token_obj = json.loads(value)
                except (ValueError, TypeError):
                    data_list.append((key, value))
                    continue
                for k, v in token_obj.items():
                    data_list.append((k, _fb_ts(v) if k in _TS_KEYS else _s(v)))
            elif key == "com.facebook.ProfileManager.CachedProfile":
                try:
                    profile = json.loads(value)
                except (ValueError, TypeError):
                    data_list.append((key, value))
                    continue
                for k, v in profile.items():
                    data_list.append((k, _s(v)))
            else:
                data_list.append((key, _s(value)))

    data_headers = ('Name', 'Value')
    return data_headers, data_list, source_path
