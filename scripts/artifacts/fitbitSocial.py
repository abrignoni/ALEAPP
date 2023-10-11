import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_fitbitSocial(files_found, report_folder, seeker, wrap_text, time_offset):
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    OWNING_USER_ID,
    ENCODED_ID,
    DISPLAY_NAME,
    AVATAR_URL,
    FRIEND,
    CHILD
    FROM FRIEND
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Fitbit Friends')
        report.start_artifact_report(report_folder, 'Fitbit Friends')
        report.add_script()
        data_headers = ('Owning UserID','Encoded ID','Display Name','Avatar URL','Friend','Child') 
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Fitbit Friends'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc('No Fitbit Friend data available')
    
    
    cursor = db.cursor()
    cursor.execute('''
    SELECT
    datetime("LAST_UPDATED"/1000, 'unixepoch'),
    DISPLAY_NAME,
    FULL_NAME,
    ABOUT_ME,
    AVATAR_URL,
    COVER_PHOTO_URL,
    CITY,
    STATE,
    COUNTRY,
    datetime("JOINED_DATE"/1000, 'unixepoch'),
    datetime("DATE_OF_BIRTH"/1000, 'unixepoch'),
    HEIGHT,
    WEIGHT,
    GENDER,
    COACH
    FROM USER_PROFILE
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Fitbit User Profile')
        report.start_artifact_report(report_folder, 'Fitbit User Profile')
        report.add_script()
        data_headers = ('Last Updated','Display Name','Full Name','About Me','Avatar URL', 'Cover Photo URL', 'City', 'State', 'Country', 'Joined Date','Date of Birth','Height','Weight','Gender','Coach') 
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14]))
            
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Fitbit User Profile'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Fitbit User Profile'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Fitbit User Profile data available')
        
    db.close()

__artifacts__ = {
        "FitbitSocial": (
                "Fitbit",
                ('*/com.fitbit.FitbitMobile/databases/social_db*'),
                get_fitbitSocial)
}