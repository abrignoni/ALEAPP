import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows 
from scripts.parse3 import ParseProto

def get_vaulty_files(files_found, report_folder, seeker, wrap_text):

    title = "Vaulty - Files"

    # Media database
    db_filepath = str(files_found[0])
    conn = sqlite3.connect(db_filepath)
    c = conn.cursor()
    sql = """SELECT Media._id, datetime(Media.date_added, 'unixepoch'), datetime(Media.date_modified / 1000, 'unixepoch'), Media.path, Media._data FROM Media"""
    c.execute(sql)
    results = c.fetchall()
    conn.close()

    # Data results
    data_headers = ('ID', 'Date Created', 'Date Added', 'Original Path', 'Vault Path')
    data_list = results
    
    # Reporting
    description = "Vaulty (com.theronrogers.vaultyfree) - Research at https://kibaffo33.data.blog/2022/03/05/decoding-vaulty/"
    report = ArtifactHtmlReport(title)
    report.start_artifact_report(report_folder, title, description)
    report.add_script()
    report.write_artifact_data_table(data_headers, data_list, db_filepath, html_escape=False)
    report.end_artifact_report()
    
    tsv(report_folder, data_headers, data_list, title)

__artifacts__ = {
    "vaulty_files": (
        "Vaulty",
        ('*/com.theronrogers.vaultyfree/databases/media.db'),
        get_vaulty_files)
}