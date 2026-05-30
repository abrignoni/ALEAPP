__artifacts_v2__ = {
    # Key must match the function name exactly
    "get_nova_momo_prefs": {
        "name": "Shared Preferences - Account & Usage",
        "description": "Extracts account info, decoded Firebase JWT data, device identifiers, and usage metrics.",
        "author": "Guilherme Guilherme",
        "version": "4.0",
        "date": "2026-05-30",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "paths": ("*/com.scaleup.chatai/shared_prefs/MOMO_PREF_FILE.xml",),
        "output_types": "all",
        "artifact_icon": "settings",
    },
    "get_nova_adapty_prefs": {
        "name": "Shared Preferences - Adapty Payment",
        "description": "Extracts payment profile and installation metadata from AdaptySDKPrefs.xml.",
        "author": "Guilherme Guilherme",
        "version": "4.0",
        "date": "2026-05-30",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "paths": ("*/com.scaleup.chatai/shared_prefs/AdaptySDKPrefs.xml",),
        "output_types": "all",
        "artifact_icon": "credit-card",
    },
}


import json
import base64
import xml.etree.ElementTree as ET
from scripts.ilapfuncs import artifact_processor, logfunc


def decode_jwt(token):
    try:
        payload_b64 = token.split(".")[1]
        missing_padding = len(payload_b64) % 4
        if missing_padding:
            payload_b64 += "=" * (4 - missing_padding)
        decoded = base64.b64decode(payload_b64).decode("utf-8")
        return json.loads(decoded)
    except Exception:
        return None


def format_key_name(key):
    name = key.replace("KEY_", "").replace("_", " ")
    return " ".join(word.capitalize() for word in name.split())


@artifact_processor
def get_nova_momo_prefs(files_found, report_folder, seeker, wrap_text):
    file_path = str(files_found[0])
    data_list = []

    try:
        root = ET.parse(file_path).getroot()
    except Exception as e:
        logfunc(f"[nova_momo_prefs] Error parsing XML: {e}")
        return (), [], ""

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

    return ("Category", "Field", "Value"), data_list, file_path


@artifact_processor
def get_nova_adapty_prefs(files_found, report_folder, seeker, wrap_text):
    file_path = str(files_found[0])
    data_list = []

    try:
        root = ET.parse(file_path).getroot()
    except Exception as e:
        logfunc(f"[nova_adapty_prefs] Error parsing XML: {e}")
        return (), [], ""

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

    return ("Category", "Field", "Value"), data_list, file_path
