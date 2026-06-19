# pylint: disable=W0613
__artifacts_v2__ = {
    "get_ChessComGames": {
        "name": "Chess.com Games",
        "description": "Parses Chess.com game records",
        "author": "",
        "creation_date": "2022-03-27",
        "last_update_date": "2022-03-27",
        "requirements": "none",
        "category": "Chess.com",
        "notes": "",
        "paths": ('*/com.chess/databases/chess-database*', '*/data/com.chess/shared_prefs/com.chess.app.session_preferences.xml'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "grid",
    }
}

import datetime
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly


@artifact_processor
def get_ChessComGames(files_found, report_folder, seeker, wrap_text):

    # Username
    username = "None"
    session_files = [str(x) for x in files_found if str(x).endswith('.xml')]
    if session_files:
        sesh_root = ET.parse(session_files[0]).getroot()
        for item in sesh_root.findall("string"):
            if item.attrib.get("name") == "pref_username":
                username = item.text

    # Chess database
    source_path = [str(x) for x in files_found if "chess-database" in str(x)][0]
    db = open_sqlite_db_readonly(source_path)
    cursor = db.cursor()
    cursor.execute('''
        SELECT daily_games.game_start_time, daily_games.timestamp, daily_games.game_id,
               daily_games.white_username, daily_games.black_username,
               CASE daily_games.is_opponent_friend WHEN 1 THEN "Friend" WHEN 0 THEN "User" ELSE "ERROR" END,
               daily_games.result_message
        FROM daily_games
        WHERE daily_games.white_username = ? OR daily_games.black_username = ?
        ORDER BY daily_games.timestamp
    ''', (username, username))
    all_rows = cursor.fetchall()
    db.close()

    data_list = []
    for row in all_rows:
        first_move = datetime.datetime.fromtimestamp(int(row[0]), datetime.timezone.utc) if row[0] else ''
        last_move = datetime.datetime.fromtimestamp(int(row[1]), datetime.timezone.utc) if row[1] else ''
        data_list.append((first_move, last_move, row[2], row[3], row[4], row[5], row[6]))

    data_headers = (('First Move', 'datetime'), ('Last Move', 'datetime'), 'Game ID', 'White', 'Black', 'Friend Status', 'Result')
    return data_headers, data_list, source_path
