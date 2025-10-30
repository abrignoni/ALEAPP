# Microsoft Authenticator (com.azure.authenticator)
# Author:  Marco Neumann (kalinko@be-binary.de)
# Version: 0.0.1
# 
# Tested with the following versions:
# 2024-05-11: Android 14, App: 6.2404.2229

# Requirements: -




__artifacts_v2__ = {

    
    "MSAuthenticatorAccounts": {
        "name": "Microsoft Authenticator - Accounts",
        "description": "Parses the existing Accounts out of the Microsoft Authenticator App.",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "date": "2024-05-11",
        "requirements": "",
        "category": "MS Authenticator",
        "notes": "Get Account information from MS authenticator app.",
        "paths": ('*/com.azure.authenticator/databases/PhoneFactor*'),
        "function": "get_MSAuth_accounts"
    }
}


from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly




def get_MSAuth_accounts(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Microsoft Authenticator - Accounts")
 
    accountUUIDS = []
    mail_addresses = []
 
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    for file_found in files_found:
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
            SELECT name, username, oath_secret_key
            FROM accounts
        ''')
        data_rows = cursor.fetchall()
        
        if len(data_rows):
            logfunc(f"Found {len(data_rows)}  Microsoft Authenticator - Accounts")

            description = f"Existing accounts in the Microsoft Authenticator App. These accounts are set up for 2FA on the device. Service Name is a user given label that can give hint to existing cloud accounts."
            report = ArtifactHtmlReport('Microsoft Authenticator - Accounts')
            report.start_artifact_report(report_folder, 'Microsoft Authenticator - Accounts', description)
            report.add_script()
            data_headers = ('Service Name', 'User Name', 'OATH Secret Key')
            data_list = []
            for row in data_rows:
                service_name = row[0]
                user_name = row[1]
                secret = row[2]

                data_list.append((service_name, user_name, secret))                          
            tableID = 'msauth_accounts'

            report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
            report.end_artifact_report()

            tsvname = f'MS Authenticator - Accounts'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = f'MS Authenticator - Accounts'
            timeline(report_folder, tlactivity, data_list, data_headers)
        else:
            logfunc('No entries found for MS Authenticator.')

        db.close()
        
        
