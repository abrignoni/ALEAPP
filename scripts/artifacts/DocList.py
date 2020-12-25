import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_DocList(files_found, report_folder, seeker, wrap_text):
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    try:
        cursor.execute('''
        select
            title,
            owner,
            case creationTime
                when 0 then ''
                else datetime("creationTime"/1000, 'unixepoch')
            end    as C_D,
            case lastModifiedTime
                when 0 then ''
                else datetime("lastModifiedTime"/1000, 'unixepoch') 
            end as M_D,
            case lastOpenedTime
                when 0 then ''
                else datetime("lastOpenedTime"/1000, 'unixepoch')
            end as O_D,
            lastModifierAccountAlias,
            lastModifierAccountName,
            kind,
            shareableUri,
            htmlUri,
            md5Checksum,
            size
        from EntryView
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
    
    if usageentries > 0:
        report = ArtifactHtmlReport('DocList')
        report.start_artifact_report(report_folder, 'DocList')
        report.add_script()
        data_headers = ('File Name','Owner','Created Date','Modified Date','Opened Date','Last Modifier Account Alias','Last Modifier Account Name','File Type','Shareable URI','HTML URI','MD5 Checkusm','Size') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Google Docs - DocList'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Google Docs - DocList'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Google Docs - DocList data available')
    
    db.close()
    return
