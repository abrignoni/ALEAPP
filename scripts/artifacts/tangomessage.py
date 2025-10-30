import sqlite3
import base64
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def _decodeMessage(wrapper, message):
    result = ""
    decoded = base64.b64decode(message)
    try:
        Z = decoded.decode("ascii", "ignore")
        result = Z.split(wrapper)[1]
    except Exception as ex:
        print ("Error decoding a Tango message. " + str(ex))
        pass
    return result


def get_tangomessage(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('tc.db'):
            break

    source_file = file_found.replace(seeker.data_folder, '')

    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    try:
        cursor.execute('''
        SELECT conv_id, payload, create_time/1000 as create_time, 
               case direction when 1 then "Incoming" else "Outgoing" end direction 
          FROM messages ORDER BY create_time DESC
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('Tango - Messages')
        report.start_artifact_report(report_folder, 'Tango - Messages')
        report.add_script()
        data_headers = ('Create Time', 'Direction','Message') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            message = _decodeMessage(row[0], row[1]) 
            timestamp = datetime.datetime.utcfromtimestamp(int(row[2])).strftime('%Y-%m-%d %H:%M:%S')

            data_list.append((timestamp, row[3], message))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Tango Messages'
        tsv(report_folder, data_headers, data_list, tsvname, source_file)
                
        tlactivity = f'Tango Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Tango Messages data available')

    db.close()

__artifacts__ = {
        "tangomessage": (
                "Tango",
                ('*/com.sgiggle.production/files/tc.db*'),
                get_tangomessage)
}
