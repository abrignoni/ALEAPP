import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, open_sqlite_db_readonly

def get_ChessComMessages(files_found, report_folder, seeker, wrap_text):
    
    title = "Chess.com Messages"

    # Chess database
    db_filepath = str(files_found[0])
    conn = sqlite3.connect(db_filepath)
    c = conn.cursor()
    sql = """SELECT datetime(messages.created_at, 'unixepoch') AS Sent, messages.conversation_id AS Conversation, messages.sender_username AS Sender, messages.content AS Message FROM messages"""
    c.execute(sql)
    results = c.fetchall()
    conn.close()

    # Data results
    data_headers = ('Sent', 'Conversation', 'Sender', 'Message')
    data_list = results
    
    # Reporting
    description = "Chess.com Messages"
    report = ArtifactHtmlReport(title)
    report.start_artifact_report(report_folder, title, description)
    report.add_script()
    report.write_artifact_data_table(data_headers, data_list, db_filepath, html_escape=False)
    report.end_artifact_report()
    
    tsv(report_folder, data_headers, data_list, title)

__artifacts__ = {
        "ChessComMessages": (
                "Chess.com",
                ('*/com.chess/databases/chess-database*'),
                get_ChessComMessages)
}

