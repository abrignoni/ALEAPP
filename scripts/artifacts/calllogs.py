import os
import sqlite3
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, does_table_exist_in_db

def get_calllogs(files_found, report_folder, seeker, wrap_text):

    source_file = ''
    for file_found in files_found:
        
        file_name = str(file_found)
        if not os.path.basename(file_name) == 'contacts2.db' and \
           not os.path.basename(file_name) == 'contacts.db'  and \
           not os.path.basename(file_name) == 'logs.db': # skip -journal and other files
            continue
        source_file = file_found.replace(seeker.data_folder, '')

        db = open_sqlite_db_readonly(file_name)
        calls_table_exists = does_table_exist_in_db(file_name, 'calls')
        cursor = db.cursor()
        try:
            if calls_table_exists:
                cursor.execute('''
                    SELECT number, date/1000, (date/1000 + duration) as duration, 
                           case type when 1 then "Incoming"
                                     when 3 then "Incoming"
                                     when 2 then "Outgoing"
                                     when 5 then "Outgoing"
                                     else "Unknown" end as direction,
                            name FROM calls ORDER BY date DESC;''')
            else:
                cursor.execute('''
                    SELECT number, date/1000, (date/1000 + duration) as duration, 
                           case type when 1 then "Incoming"
                                     when 3 then "Incoming"
                                     when 2 then "Outgoing"
                                     when 5 then "Outgoing"
                                     else "Unknown" end as direction,
                           name FROM logs ORDER BY date DESC;''')
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
        except Exception as e:
            print (e)
            usageentries = 0
            
        if usageentries > 0:
            report = ArtifactHtmlReport('Call Logs2')
            report.start_artifact_report(report_folder, 'Call Logs2')
            report.add_script()
            data_headers = ('from_id', 'to_id','start_date', 'end_date', 'direction', 'name') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                callerId = None
                calleeId = None
                if row[3] == "Incoming":
                    callerId = row[0]                                   
                else:
                    calleeId = row[0]
                starttime = datetime.datetime.utcfromtimestamp(int(row[2])).strftime('%Y-%m-%d %H:%M:%S')
                endtime = datetime.datetime.utcfromtimestamp(int(row[2])).strftime('%Y-%m-%d %H:%M:%S')
                data_list.append((callerId, calleeId, starttime, endtime, row[3], row[4]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Call Logs2'
            tsv(report_folder, data_headers, data_list, tsvname, source_file)

            tlactivity = f'Call Logs2'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('No Call Logs found')

        db.close()
    
    return

__artifacts__ = {
    "Call Logs":(
        "Call Logs",
        ('*/com.android.providers.contacts/databases/contact*', '*/com.sec.android.provider.logsprovider/databases/logs.db*'),
        get_calllogs)
}
