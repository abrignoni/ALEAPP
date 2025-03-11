import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, open_sqlite_db_readonly

def get_userDict(files_found, report_folder, seeker, wrap_text):
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    select 
    word,
    frequency,
    locale,
    appid,
    shortcut
    from words
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('User Dictionary')
        report.start_artifact_report(report_folder, 'User Dictionary')
        report.add_script()
        data_headers = ('Word','Frequency','Locale','AppID','Shortcut' ) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'user dictionary'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc('No User Dictionary data available')
    
    db.close()

__artifacts__ = {
    "userDict": (
        "User Dictionary",
        ('*/com.android.providers.userdictionary/databases/user_dict.db*'),
        get_userDict)
}

