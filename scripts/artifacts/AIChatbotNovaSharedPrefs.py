__artifacts_v2__ = {
    "nova_shared_prefs": {
        "name": "Shared Preferences",
        "description": (
            "Extracts account info, decoded Firebase JWT data, usage metrics, and Adapty payment "
            "profile data from ChatAI app preference files, optimized using LAVA-compliant timestamp parsing."
        ),
        "author": "Guilherme Guilherme",
        "version": "1.1",
        "date": "2026-05-29",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": "Decodes Firebase JWT tokens and parses nested Adapty JSON strings.",
        "paths": (
            "*/com.scaleup.chatai/shared_prefs/MOMO_PREF_FILE.xml",
            "*/com.scaleup.chatai/shared_prefs/AdaptySDKPrefs.xml",
        ),
        "function": "get_chat_ai_prefs",
        "output_types": "standard",
        "artifact_icon": "settings",
    }
}


import json
import base64
import xml.etree.ElementTree as ET
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv


def decode_jwt(token):
    try:
        # JWT is Header.Payload.Signature
        payload_b64 = token.split(".")[1]
        # Add padding if necessary
        missing_padding = len(payload_b64) % 4
        if missing_padding:
            payload_b64 += "=" * (4 - missing_padding)
        decoded = base64.b64decode(payload_b64).decode("utf-8")
        return json.loads(decoded)
    except Exception:
        return None


def get_chat_ai_prefs(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for ChatAI Shared Preferences")

    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith("MOMO_PREF_FILE.xml"):
            try:
                tree = ET.parse(file_found)
                root = tree.getroot()
            except Exception as e:
                logfunc(f"[ChatAIPrefs] Error parsing XML file {file_found}: {e}")
                continue

            jwt_info = {}
            usage_metrics = []
            generic_ids = []

            for elem in root:
                name = elem.get("name")
                value = elem.get("value") if elem.get("value") else elem.text

                if not name:
                    continue

                # Decode Firebase JWT
                if name == "KEY_USER_FIREBASE_ID_TOKEN" and value:
                    decoded = decode_jwt(value)
                    if decoded:
                        jwt_info = {
                            "Email": decoded.get("email"),
                            "Name": decoded.get("name"),
                            "Firebase UID": decoded.get("user_id"),
                            "Sign-in Provider": decoded.get("firebase", {}).get(
                                "sign_in_provider"
                            ),
                        }

                # Identity Keys
                elif name in [
                    "KEY_USER_AUTHENTICATION_ID",
                    "KEY_USER_INSTALLATIONS_ID",
                    "KEY_PLATFORM_ID",
                    "KEY_FCM_TOKEN",
                ]:
                    generic_ids.append((name, value or ""))

                # Global Metrics
                elif name in ["KEY_SUCCESSFULL_CHAT_RESPONSE", "KEY_SESSION_COUNT"]:
                    usage_metrics.append((name, value or ""))

                # Individual Bot Usage (Generalizing the pattern)
                elif (
                    "KEY_USER_USAGE_RIGHT_COUNT" in name
                    or "KEY_USER_USAGE_TOTAL_COUNT" in name
                ):
                    usage_metrics.append((name, value or ""))

            # Report 1: MOMO Account & IDs (Sem timestamp nativo associado às chaves)
            if jwt_info or generic_ids:
                report_name = "Shared Prefs - Account Identifiers"
                report = ArtifactHtmlReport(report_name)
                report.start_artifact_report(report_folder, report_name)
                report.add_script()

                data_list = []
                for k, v in jwt_info.items():
                    data_list.append(("", k, v, "Decoded from JWT"))
                for k, v in generic_ids:
                    data_list.append(("", k, v, "XML Raw Value"))

                headers = ("Timestamp", "Key/Field", "Value", "Source Type")
                report.write_artifact_data_table(
                    headers, data_list, file_found, html_escape=True
                )
                report.end_artifact_report()
                tsv(report_folder, headers, data_list, report_name, file_found)

            # Report 2: MOMO Usage Metrics
            if usage_metrics:
                report_name = "Shared Prefs - Usage Metrics"
                report = ArtifactHtmlReport(report_name)
                report.start_artifact_report(report_folder, report_name)
                report.add_script()

                data_list = [("", k, v) for k, v in usage_metrics]
                headers = ("Timestamp", "Metric Key", "Value")

                report.write_artifact_data_table(
                    headers, data_list, file_found, html_escape=True
                )
                report.end_artifact_report()
                tsv(report_folder, headers, data_list, report_name, file_found)

        elif file_found.endswith("AdaptySDKPrefs.xml"):
            try:
                tree = ET.parse(file_found)
                root = tree.getroot()
            except Exception as e:
                logfunc(f"[ChatAIPrefs] Error parsing XML file {file_found}: {e}")
                continue

            adapty_main = []
            adapty_meta = []

            for elem in root:
                name = elem.get("name")
                value = elem.get("value") if elem.get("value") else elem.text

                if not name:
                    continue

                # Parse Installation Meta JSON
                if name == "LAST_SENT_INSTALLATION_META" and value:
                    try:
                        meta = json.loads(value)
                        for k, v in meta.items():
                            adapty_meta.append(("", k, str(v)))
                    except Exception:
                        pass

                # Parse Profile JSON
                if name in ["get_purchaser_info_response", "PROFILE"] and value:
                    try:
                        p_data = json.loads(value)
                        if "data" in p_data:
                            attrs = p_data["data"].get("attributes", {})
                        else:
                            attrs = p_data

                        custom = attrs.get("custom_attributes", {})
                        ts = attrs.get("timestamp") or p_data.get("timestamp")

                        # Conversão para Float Epoch compatível com LAVA (Segundos)
                        lava_timestamp = ""
                        if ts is not None:
                            try:
                                lava_timestamp = float(ts) / 1000
                            except (ValueError, TypeError):
                                lava_timestamp = ts

                        adapty_main.append(
                            (
                                lava_timestamp,
                                "Is Test User",
                                str(attrs.get("is_test_user", "")),
                            )
                        )
                        adapty_main.append(
                            (
                                lava_timestamp,
                                "Old App Instance ID",
                                str(custom.get("oldAppInstanceId", "")),
                            )
                        )
                        adapty_main.append(
                            (
                                lava_timestamp,
                                "Total Revenue (USD)",
                                str(attrs.get("total_revenue_usd", "")),
                            )
                        )
                        adapty_main.append(
                            (
                                lava_timestamp,
                                "Paywall Type",
                                str(custom.get("paywallType", "")),
                            )
                        )
                    except Exception:
                        pass

            if adapty_main:
                report_name = "Shared Prefs - Adapty Payment Profile"
                report = ArtifactHtmlReport(report_name)
                report.start_artifact_report(report_folder, report_name)
                report.add_script()

                headers = ("Timestamp", "Attribute", "Value")
                report.write_artifact_data_table(
                    headers, adapty_main, file_found, html_escape=True
                )
                report.end_artifact_report()
                tsv(report_folder, headers, adapty_main, report_name, file_found)

            if adapty_meta:
                report_name = "Shared Prefs - Adapty Device Meta"
                report = ArtifactHtmlReport(report_name)
                report.start_artifact_report(report_folder, report_name)
                report.add_script()

                headers = ("Timestamp", "Meta Key", "Value")
                report.write_artifact_data_table(
                    headers, adapty_meta, file_found, html_escape=True
                )
                report.end_artifact_report()
                tsv(report_folder, headers, adapty_meta, report_name, file_found)
