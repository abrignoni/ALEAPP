__artifacts_v2__ = {
    "burnerSubscription": {
        "name": "Burner: Second Phone Number",
        "description": "Parses Burner Subscription Information",
        "author": "Heather Charpentier (With Tons of Help from Alexis Brignoni!)",
        "version": "0.0.1",
        "date": "2024-02-15",
        "requirements": "none",
        "category": "Burner",
        "notes": "",
        "paths": ('*/data/data/com.adhoclabs.burner/databases/burnerDatabase.db*'),
        "function": "get_burnerSubscription"
    }
}

import sqlite3

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, timeline, tsv, is_platform_windows, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_burnerSubscription(files_found, report_folder, seeker, wrap_text):
    
    data_list = []
    
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('burnerDatabase.db'):
            db = open_sqlite_db_readonly(file_found)
            #SQL QUERY TIME!
            cursor = db.cursor()
            cursor.execute('''
            SELECT
            json_extract(SubscriptionEntity.value, '$.burnerIds') as 'User ID',
            datetime(json_extract(SubscriptionEntity.value, '$.creationDate')/1000, 'unixepoch') as 'Date Created',
            datetime(json_extract(SubscriptionEntity.value, '$.renewalDate')/1000, 'unixepoch') as 'Renewal Date',
            json_extract(SubscriptionEntity.value, '$.sku') as 'SKU',
            json_extract(SubscriptionEntity.value, '$.store') as 'Store',
            CASE json_extract(SubscriptionEntity.value, '$.trial')
                WHEN 1 THEN 'True'
                WHEN 2 THEN 'False'
                ELSE 'Unknown'
            END as Trial,
            json_extract(SubscriptionEntity.value, '$.state') as 'State'
            FROM SubscriptionEntity
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                for row in all_rows:
               
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6]))
            db.close()
                    
        else:
            continue
        
    if data_list:
        description = 'Burner: Second Phone Number'
        report = ArtifactHtmlReport('Burner Subscription Information')
        report.start_artifact_report(report_folder, 'Burner Subscription', description)
        report.add_script()
        data_headers = ('User ID','Timestamp','Renewal Date','SKU','Store','Trial','State')
        report.write_artifact_data_table(data_headers, data_list, file_found,html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'Burner Subscription'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Burner Subscription'
        timeline(report_folder, tlactivity, data_list, data_headers)
    
    else:
        logfunc('No Burner data available')
