import sqlite3
import textwrap
import xml.etree.ElementTree as ET

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, open_sqlite_db_readonly

def get_ChessComGames(files_found, report_folder, seeker, wrap_text):
    
    title = "Chess.com Games"

    # Username
    username = "None"
    session_file = list(filter(lambda x: "xml" in x, files_found))[0]
    sesh_tree = ET.parse(session_file)
    sesh_root = sesh_tree.getroot()
    sesh_strings = sesh_root.findall("string")
    for item in sesh_strings:
        key = item.attrib.get("name")
        if key == "pref_username":
            username = item.text

    # Chess database
    db_filepath = list(filter(lambda x: "chess-database" in x, files_found))[0]
    conn = sqlite3.connect(db_filepath)
    c = conn.cursor()
    sql = f"""SELECT datetime(daily_games.game_start_time, 'unixepoch') AS "First Move", datetime(daily_games.timestamp, 'unixepoch') AS "Last Move", daily_games.game_id AS "Game ID", daily_games.white_username AS "White", daily_games.black_username AS "Black", CASE daily_games.is_opponent_friend WHEN 1 THEN "Friend" WHEN 0 THEN "User" ELSE "ERROR" END AS "Friend Status", daily_games.result_message AS "Result" FROM daily_games WHERE daily_games.white_username = "{username}" OR daily_games.black_username = "{username}" ORDER BY daily_games.timestamp"""
    c.execute(sql)
    results = c.fetchall()
    conn.close()

    # Data results
    data_headers = ('First Move', 'Last Move', 'Game ID', 'White', 'Black', 'Friend Status', 'Result')
    data_list = results
    
    # Reporting
    description = "Chess.com Games"
    report = ArtifactHtmlReport(title)
    report.start_artifact_report(report_folder, title, description)
    report.add_script()
    report.write_artifact_data_table(data_headers, data_list, db_filepath, html_escape=False)
    report.end_artifact_report()
    
    tsv(report_folder, data_headers, data_list, title)

__artifacts__ = {
        "ChessComGames": (
                "Chess.com",
                ('*/com.chess/databases/chess-database*', '*/data/data/com.chess/shared_prefs/com.chess.app.session_preferences.xml'),
                get_ChessComGames)
}


