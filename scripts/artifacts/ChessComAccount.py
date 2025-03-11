import sqlite3
import textwrap
import xml.etree.ElementTree as ET
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, open_sqlite_db_readonly

def get_ChessComAccount(files_found, report_folder, seeker, wrap_text):
    
    title = "Chess.com Account"

    # Data results
    data_headers = ('Key', 'Value')
    data_list = []

    # Login credentials
    credentials_file = str(files_found[0])
    cred_tree = ET.parse(credentials_file)
    cred_root = cred_tree.getroot()
    cred_strings = cred_root.findall("string")
    for item in cred_strings:
        key = item.attrib.get("name")
        value = item.text
        if key in ["pref_username_or_email", "pref_password"]:
            data_list.append([key, value])

    # Session 
    session_file = str(files_found[1])
    sesh_tree = ET.parse(session_file)
    sesh_root = sesh_tree.getroot()
    sesh_strings = sesh_root.findall("string")
    for item in sesh_strings:
        key = item.attrib.get("name")
        value = item.text
        if key in ["pref_username", "pref_email", "pref_member_since"]:
            if key == "pref_member_since":
                value = datetime.datetime.utcfromtimestamp(int(value)).isoformat(sep=" ", timespec="seconds")
            data_list.append([key, value])

    # Reporting
    description = "Chess.com Account"
    report = ArtifactHtmlReport(title)
    report.start_artifact_report(report_folder, title, description)
    report.add_script()
    report.write_artifact_data_table(data_headers, data_list, credentials_file, html_escape=False)
    report.end_artifact_report()
    
    tsv(report_folder, data_headers, data_list, title)

__artifacts__ = {
        "ChessComAcct": (
                "Chess.com",
                ('*/com.chess/shared_prefs/com.chess.app.login_credentials.xml', '*/data/data/com.chess/shared_prefs/com.chess.app.session_preferences.xml'),
                get_ChessComAccount)
}
 

