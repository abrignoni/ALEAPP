import glob
import json
import os
import shutil
import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, logdevinfo, is_platform_windows, open_sqlite_db_readonly

def get_siminfo(files_found, report_folder, seeker, wrap_text):

    slash = '\\' if is_platform_windows() else '/' 
    # Filter for path xxx/yyy/system_ce/0
    for file_found in files_found:
        file_found = str(file_found)
        parts = file_found.split(slash)
        uid = parts[-4]
        try:
            uid_int = int(uid)
            # Skip sbin/.magisk/mirror/data/system_de/0 , it should be duplicate data??
            if file_found.find('{0}mirror{0}'.format(slash)) >= 0:
                continue
            process_siminfo(file_found, uid, report_folder)
        except ValueError:
            pass # uid was not a number

def process_siminfo(folder, uid, report_folder):
    
    #Query to create report
    db = open_sqlite_db_readonly(folder)
    cursor = db.cursor()

    #Query to create report
    try:
        # Find columns that available
        columns_info = cursor.fetchall()
        available_columns = [col[1] for col in columns_info]
    except:
        # If siminfo table don't exist 
        logfunc(f'Error getting table schema for SIM_info_{uid}')
        db.close()
        return
    
    #Helper function
    def get_col(col_name):
        return col_name if col_name in available_columns else "''"
    
    id_col = "''"
    if 'imsi' in available_columns: id_col = 'imsi'
    elif 'card_id' in available_columns: id_col = 'card_id'
    elif 'sim_id' in available_columns: id_col = 'sim_id'
    
    iso_col = "''"
    if 'iso_country_code' in available_columns: iso_column = 'iso_country_code'
    elif 'country_iso' in available_columns: iso_column = 'country_iso'
    
    icc_col = get_col('icc_id')
    
    query = f'''
        SELECT
            {get_col('number')},
            {id_col} as sim_identifier,
            {get_col('display_name')},
            {get_col('carrier_name')},
            {iso_col} as country_iso,
            {get_col('carrier_id')},
            {icc_col}
        FROM siminfo
    '''
    
    try:
        cursor.execute(query)
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except Exception as e:
        logfunc(f'Error executing query for SIM_info_{uid}: {str(e)}')
        usageentries = 0
    if usageentries > 0:
        report = ArtifactHtmlReport('Device Info')
        report.start_artifact_report(report_folder, f'SIM_info_{uid}')
        report.add_script()
        data_headers = ('Number', 'IMSI', 'Display Name','Carrier Name', 'ISO Code', 'Carrier ID', 'ICC ID')
        
        data_list = []
        for row in all_rows:
            # Collect data directly
            number = str(row[0]) if row[0] is not None else ''
            identifier = str(row[1]) if row[1] is not None else ''
            display_name = str(row[2]) if row[2] is not None else ''
            carrier = str(row[3]) if row[3] is not None else ''
            iso = str(row[4]) if row[4] is not None else ''
            carrier_id = str(row[5]) if row[5] is not None else ''
            icc_id = str(row[6]) if row[6] is not None else ''
        
            data_list.append((number, identifier, display_name, carrier, iso, carrier_id, icc_id))
            
            logdevinfo(f"<b>SIM Number: </b>{number}")
            logdevinfo(f"<b>SIM ID (IMSI/CardID): </b>{identifier}")
            logdevinfo(f"<b>SIM Carrier: </b>{carrier}")
            
        report.write_artifact_data_table(data_headers, data_list, folder)
        report.end_artifact_report()
        
        tsvname = f'Sim info {uid}'
        tsv(report_folder, data_headers, data_list, tsvname)
    else:
        logfunc(f'No SIM_Info{uid} data available')    
    db.close()
    


__artifacts__ = {
        "siminfo": (
                "Device Info",
                ('*/user_de/*/com.android.providers.telephony/databases/telephony.db'),
                get_siminfo)
}