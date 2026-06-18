# pylint: disable=W0611,W0613
__artifacts_v2__ = {
    "get_ChessComFriends": {
        "name": "ChessComFriends",
        "description": "Chess database",
        "author": "",
        "creation_date": "2022-02-23",
        "last_update_date": "2022-02-23",
        "requirements": "none",
        "category": "Chess.com",
        "notes": "",
        "paths": ('*/com.chess/databases/chess-database*',),
        "output_types": None,
        "artifact_icon": "grid",
    }
}

import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, open_sqlite_db_readonly

def get_ChessComFriends(files_found, report_folder, seeker, wrap_text):
    
    title = "Chess.com Friends"

    # Chess database
    db_filepath = str(files_found[0])
    conn = sqlite3.connect(db_filepath)
    c = conn.cursor()
    sql = """SELECT friends.id AS "ID", friends.username AS "Username", friends.first_name AS "First Name", friends.last_name AS "Last Name", datetime(friends.last_login_date, 'unixepoch') AS "Last Login" FROM friends"""
    c.execute(sql)
    results = c.fetchall()
    conn.close()

    # Data results
    data_headers = ('ID', 'Username', 'First Name', 'Last Name', 'Last Login')
    data_list = results
    
    # Reporting
    description = "Chess.com Friends"
    report = ArtifactHtmlReport(title)
    report.start_artifact_report(report_folder, title, description)
    report.add_script()
    report.write_artifact_data_table(data_headers, data_list, db_filepath, html_escape=False)
    report.end_artifact_report()
    
    tsv(report_folder, data_headers, data_list, title)
