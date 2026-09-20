__artifacts_v2__ = {
    "get_nova_momo_prefs": {
        "name": "Shared Preferences - Account & Usage",
        "description": "Extracts account info, decoded Firebase JWT data, device identifiers, and usage metrics.",
        "author": "Guilherme Guilherme",
        "creation_date": "2026-05-30",
        "last_update_date": "2026-09-19",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": (
            "Values are reported as stored in the preference files; JWT payloads are "
            "base64-decoded for display without signature verification. An extraction can "
            "carry one copy of this file per Android user, and every copy is read. "
            "Developed against the author's own installation; no registered corpus image "
            "carries this app. The committed test case is the author's own extraction of "
            "the app's private data directory."
        ),
        "paths": ("*/com.scaleup.chatai/shared_prefs/MOMO_PREF_FILE.xml",),
        "output_types": "all",
        "artifact_icon": "settings",
    },
    "get_nova_adapty_prefs": {
        "name": "Shared Preferences - Adapty Payment",
        "description": "Extracts payment profile and installation metadata from AdaptySDKPrefs.xml.",
        "author": "Guilherme Guilherme",
        "creation_date": "2026-05-30",
        "last_update_date": "2026-09-19",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": (
            "Values are reported as stored in the preference files; JWT payloads are "
            "base64-decoded for display without signature verification. An extraction can "
            "carry one copy of this file per Android user, and every copy is read. "
            "Developed against the author's own installation; no registered corpus image "
            "carries this app. The committed test case is the author's own extraction of "
            "the app's private data directory."
        ),
        "paths": ("*/com.scaleup.chatai/shared_prefs/AdaptySDKPrefs.xml",),
        "output_types": "all",
        "artifact_icon": "credit-card",
    },
}


import base64
import json
import os
import xml.etree.ElementTree as ET

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, logfunc


def _prefs_files(context, basename):
    """Every copy of basename the extraction carries, duplicate storage views removed.

    An Android extraction repeats an app's private directory under data/data,
    data/user/0 and data_mirror, and can carry a second Android user's own copy
    under data/user/<n>. unique_files collapses the first kind and keeps the
    second, so a second user's preferences are read rather than skipped.
    """
    return sorted(
        str(f) for f in unique_files(context)
        if os.path.basename(str(f)) == basename
    )


def decode_jwt(token):
    try:
        payload_b64 = token.split(".")[1]
        missing_padding = len(payload_b64) % 4
        if missing_padding:
            payload_b64 += "=" * (4 - missing_padding)
        decoded = base64.b64decode(payload_b64).decode("utf-8")
        return json.loads(decoded)
    except Exception:  # pylint: disable=broad-exception-caught
        return None


def format_key_name(key):
    name = key.replace("KEY_", "").replace("_", " ")
    return " ".join(word.capitalize() for word in name.split())


@artifact_processor
def get_nova_momo_prefs(context):
    data_headers = ("Category", "Field", "Value")
    data_list = []
    sources = []

    for file_path in _prefs_files(context, "MOMO_PREF_FILE.xml"):
        try:
            root = ET.parse(file_path).getroot()
        except Exception as e:  # pylint: disable=broad-exception-caught
            logfunc(f"Nova account preferences - could not parse XML: {e}")
            continue

        for elem in root:
            name = elem.get("name")
            value = elem.get("value") if elem.get("value") is not None else elem.text
            if not name:
                continue

            if name == "KEY_USER_FIREBASE_ID_TOKEN":
                decoded = decode_jwt(value)
                if decoded:
                    for k, v in [
                        ("Email", decoded.get("email")),
                        ("Name", decoded.get("name")),
                        ("UID", decoded.get("user_id")),
                        ("Provider", decoded.get("firebase", {}).get("sign_in_provider")),
                    ]:
                        data_list.append(("Account", k, v))
            elif name.startswith("KEY_DID_") or name.startswith("KEY_IS_"):
                data_list.append(
                    ("Settings", format_key_name(name), "Yes" if value == "true" else "No")
                )
            else:
                data_list.append(("Data", format_key_name(name), value))

        sources.append(file_path)

    return data_headers, data_list, "\n".join(sources)


@artifact_processor
def get_nova_adapty_prefs(context):
    data_headers = ("Category", "Field", "Value")
    data_list = []
    sources = []

    for file_path in _prefs_files(context, "AdaptySDKPrefs.xml"):
        try:
            root = ET.parse(file_path).getroot()
        except Exception as e:  # pylint: disable=broad-exception-caught
            logfunc(f"Nova Adapty preferences - could not parse XML: {e}")
            continue

        for elem in root:
            name = elem.get("name")
            value = elem.get("value") if elem.get("value") is not None else elem.text
            if not name or not value:
                continue

            if name == "LAST_SENT_INSTALLATION_META":
                for k, v in json.loads(value).items():
                    data_list.append(("Installation Meta", k, str(v)))
            elif name in ["get_purchaser_info_response", "PROFILE"]:
                p_data = json.loads(value)
                attrs = p_data.get("data", p_data).get("attributes", p_data)
                custom = attrs.get("custom_attributes", {})
                for k, v in [
                    ("Is Test User", attrs.get("is_test_user")),
                    ("Old Instance ID", custom.get("oldAppInstanceId")),
                    ("Total Revenue", attrs.get("total_revenue_usd")),
                    ("Paywall", custom.get("paywallType")),
                ]:
                    data_list.append(("Payment Profile", k, str(v)))

        sources.append(file_path)

    return data_headers, data_list, "\n".join(sources)
