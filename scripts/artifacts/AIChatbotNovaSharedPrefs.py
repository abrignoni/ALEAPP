# AI Chatbot - Nova (com.scaleup.chatai)
# Artifact module: Shared Preferences - Account & Usage
#
# Author  : Guilherme Guilherme
# Version : 1.4
# Date    : 2026-05-30
# Category: AI Chatbot - Nova

__artifacts_v2__ = {
    "nova_momo_prefs": {
        "name": "Shared Preferences - Account & Usage",
        "description": "Extracts account info, decoded Firebase JWT data, device identifiers, and comprehensive usage metrics from MOMO_PREF_FILE.xml",
        "author": "Guilherme Guilherme",
        "version": "1.4",
        "date": "2026-05-30",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "paths": ("*/com.scaleup.chatai/shared_prefs/MOMO_PREF_FILE.xml",),
        "function": "get_nova_momo_prefs",
        "output_types": "all",
        "artifact_icon": "settings",
    },
    "nova_adapty_prefs": {
        "name": "Shared Preferences - Adapty Payment",
        "description": "Extracts payment profile and installation metadata from AdaptySDKPrefs.xml",
        "author": "Guilherme Guilherme",
        "version": "1.4",
        "date": "2026-05-30",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "paths": ("*/com.scaleup.chatai/shared_prefs/AdaptySDKPrefs.xml",),
        "function": "get_nova_adapty_prefs",
        "output_types": "all",
        "artifact_icon": "credit-card",
    },
}

import json
import base64
import xml.etree.ElementTree as ET
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import artifact_processor, logfunc, tsv


def decode_jwt(token):
    """Decode JWT payload without signature validation"""
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
    """Convert internal key names to user-friendly display names"""
    name = key.replace("KEY_", "").replace("_", " ")
    return " ".join(word.capitalize() for word in name.split())


@artifact_processor
def get_nova_momo_prefs(files_found, report_folder, seeker, wrap_text):
    """
    Extract data from MOMO_PREF_FILE.xml
    Note: No media handling needed as this contains only preference data
    """
    if not files_found:
        logfunc("[nova_momo_prefs] No MOMO_PREF_FILE.xml found")
        return

    file_path = str(files_found[0])
    account_data = []
    identifiers = []
    usage_data = []
    flags = []

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except Exception as e:
        logfunc(f"[nova_momo_prefs] Error parsing XML: {e}")
        return

    for elem in root:
        name = elem.get("name")
        value = elem.get("value") if elem.get("value") is not None else elem.text

        if not name:
            continue

        # Decode Firebase JWT for account info
        if name == "KEY_USER_FIREBASE_ID_TOKEN":
            decoded = decode_jwt(value)
            if decoded:
                account_data.extend(
                    [
                        ("Firebase Email", decoded.get("email", "")),
                        ("Firebase Name", decoded.get("name", "")),
                        ("Firebase UID", decoded.get("user_id", "")),
                        (
                            "Sign-in Provider",
                            decoded.get("firebase", {}).get("sign_in_provider", ""),
                        ),
                    ]
                )

        # Device identifiers
        elif name in [
            "KEY_USER_AUTHENTICATION_ID",
            "KEY_USER_INSTALLATIONS_ID",
            "KEY_PLATFORM_ID",
            "KEY_FCM_TOKEN",
        ]:
            identifiers.append((format_key_name(name), value))

        # Boolean flags and settings
        elif name.startswith("KEY_DID_") or name.startswith("KEY_IS_"):
            flags.append((format_key_name(name), "Yes" if value == "true" else "No"))

        # Usage metrics (all other KEY_USER_USAGE_* fields)
        elif name.startswith("KEY_USER_USAGE_") or name in [
            "KEY_SUCCESSFULL_CHAT_RESPONSE",
            "KEY_SESSION_COUNT",
            "KEY_HISTORY_BOX_SHOWN",
        ]:
            usage_data.append((format_key_name(name), value))

    # Generate reports
    if account_data:
        report = ArtifactHtmlReport("Shared Prefs - Account Information")
        report.start_artifact_report(
            report_folder, "Shared Prefs - Account Information"
        )
        report.add_script()
        report.write_artifact_data_table(
            ("Field", "Value"), account_data, file_path, html_escape=False
        )
        report.end_artifact_report()
        tsv(
            report_folder,
            ("Field", "Value"),
            account_data,
            "Shared Prefs - Account Information",
        )

    if identifiers:
        report = ArtifactHtmlReport("Shared Prefs - Device Identifiers")
        report.start_artifact_report(report_folder, "Shared Prefs - Device Identifiers")
        report.add_script()
        report.write_artifact_data_table(
            ("Identifier", "Value"), identifiers, file_path, html_escape=False
        )
        report.end_artifact_report()
        tsv(
            report_folder,
            ("Identifier", "Value"),
            identifiers,
            "Shared Prefs - Device Identifiers",
        )

    if usage_data:
        report = ArtifactHtmlReport("Shared Prefs - Usage Metrics")
        report.start_artifact_report(report_folder, "Shared Prefs - Usage Metrics")
        report.add_script()
        report.write_artifact_data_table(
            ("Metric", "Value"), usage_data, file_path, html_escape=False
        )
        report.end_artifact_report()
        tsv(
            report_folder,
            ("Metric", "Value"),
            usage_data,
            "Shared Prefs - Usage Metrics",
        )

    if flags:
        report = ArtifactHtmlReport("Shared Prefs - App Settings")
        report.start_artifact_report(report_folder, "Shared Prefs - App Settings")
        report.add_script()
        report.write_artifact_data_table(
            ("Setting", "Value"), flags, file_path, html_escape=False
        )
        report.end_artifact_report()
        tsv(report_folder, ("Setting", "Value"), flags, "Shared Prefs - App Settings")


@artifact_processor
def get_nova_adapty_prefs(files_found, report_folder, seeker, wrap_text):
    """Extract data from AdaptySDKPrefs.xml"""
    if not files_found:
        logfunc("[nova_adapty_prefs] No AdaptySDKPrefs.xml found")
        return

    file_path = str(files_found[0])
    data_list = []

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except Exception as e:
        logfunc(f"[nova_adapty_prefs] Error parsing XML: {e}")
        return

    for elem in root:
        name = elem.get("name")
        value = elem.get("value") if elem.get("value") is not None else elem.text

        if not name or not value:
            continue

        if name == "LAST_SENT_INSTALLATION_META":
            try:
                meta = json.loads(value)
                for k, v in meta.items():
                    data_list.append((f"Meta: {k}", str(v)))
            except Exception:
                pass

        if name in ["get_purchaser_info_response", "PROFILE"]:
            try:
                p_data = json.loads(value)
                if "data" in p_data:
                    attrs = p_data["data"].get("attributes", {})
                else:
                    attrs = p_data

                custom = attrs.get("custom_attributes", {})
                data_list.extend(
                    [
                        ("Is Test User", str(attrs.get("is_test_user", ""))),
                        (
                            "Old App Instance ID",
                            str(custom.get("oldAppInstanceId", "")),
                        ),
                        (
                            "Total Revenue (USD)",
                            str(attrs.get("total_revenue_usd", "")),
                        ),
                        ("Paywall Type", str(custom.get("paywallType", ""))),
                    ]
                )
            except Exception:
                pass

    if data_list:
        report = ArtifactHtmlReport("Shared Prefs - Adapty Payment Data")
        report.start_artifact_report(
            report_folder, "Shared Prefs - Adapty Payment Data"
        )
        report.add_script()
        report.write_artifact_data_table(
            ("Field", "Value"), data_list, file_path, html_escape=False
        )
        report.end_artifact_report()
        tsv(
            report_folder,
            ("Field", "Value"),
            data_list,
            "Shared Prefs - Adapty Payment Data",
        )
