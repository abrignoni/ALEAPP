import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, open_sqlite_db_readonly

def get_installedappsGass(files_found, report_folder, seeker, wrap_text):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('.db'):
            
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''
            SELECT 
                distinct(package_name) 
                FROM
                app_info  
            ''')
            
            if 'user' in file_found:
                usernum = file_found.split("/")
                usernum = '_'+str(usernum[-4])
            else:
                usernum = ''

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                report = ArtifactHtmlReport('Installed Apps')
                report.start_artifact_report(report_folder, f'Installed Apps (GMS){usernum}')
                report.add_script()
                data_headers = ('Bundle ID',) # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                data_list = []
                for row in all_rows:
                    data_list.append((row[0],))
        
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'installed apps - GMS{usernum}'
                tsv(report_folder, data_headers, data_list, tsvname)
            else:
                logfunc('No Installed Apps data available{usernum}')
            
            db.close()
