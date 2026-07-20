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
        "artifact_icon": "layout-grid",
    }
}

import datetime
import re
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, logfunc


INVALID_XML_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
BARE_AMPERSAND = re.compile(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9A-Fa-f]+);)')


def _parse_xml(file_found):
    """Parse XML, recovering from invalid tokens / unescaped ampersands; empty element if unparseable."""
    try:
        return ET.parse(file_found).getroot()
    except ET.ParseError:
        with open(file_found, encoding='utf-8', errors='replace') as f:
            xml = BARE_AMPERSAND.sub('&amp;', INVALID_XML_CHARS.sub('', f.read()))
        try:
            return ET.fromstring(xml)
        except ET.ParseError as ex:
            logfunc(f'Skipping unparseable XML {file_found}: {ex}')
            return ET.Element('empty')


@artifact_processor
def get_ChessComGames(context):
    files_found = context.get_files_found()

    # Username
    username = "None"
    session_files = [str(x) for x in files_found if str(x).endswith('.xml')]
    if session_files:
        sesh_root = _parse_xml(session_files[0])
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
