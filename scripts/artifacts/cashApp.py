import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_cashApp(files_found, report_folder, seeker, wrap_text):
    for file_found in files_found:
        file_found = str(file_found)
        
        if file_found.endswith('.db'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            cursor.execute('''Select 
        payment.role,
        payment.sender_id,
        CASE WHEN customer.cashtag IS NULL THEN '***NO CASH TAG PRESENT***' ELSE customer.cashtag END,
        customer.customer_display_name,
        payment.recipient_id,
        CASE WHEN customer1.cashtag IS NULL THEN '***NO CASH TAG PRESENT***' ELSE customer1.cashtag END,
        customer1.customer_display_name,
        payment.state,
        datetime(payment.display_date / 1000.0, 'unixepoch'),
        CASE WHEN json_extract (payment.render_data, '$."note"') IS NULL THEN '***NO NOTE SUBMITTED***' ELSE json_extract (payment.render_data, '$."note"') END,
        printf("$%.2f", json_extract(payment.render_data, '$."amount"."amount"') / 100.0)
    From payment
        Inner Join customer On customer.customer_id = payment.sender_id
        Inner Join customer customer1 On payment.recipient_id = customer1.customer_id
    
    ORDER BY payment.display_date DESC
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Transactions')
        report.start_artifact_report(report_folder, 'Transactions')
        report.add_script()
        data_headers = ('Transaction Date', 'User Account Role','Sender Display Name','Sender Unique ID', 'Sender Cashtag','Recipient Display Name', 'Recipient Unique ID', 'Recipient Cashtag','Transaction Amount','Transaction Status','Note') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[8],row[0],row[3],row[1],row[2],row[6],row[4],row[5],row[10],row[7],row[9]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Cash App Transactions'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Cash App Transactions'
        timeline(report_folder, tlactivity, data_list, data_headers)
    else:
        logfunc('No Cash App Transactions data available')
    
    db.close()

__artifacts__ = {
        "Cash App": (
                "Cash App",
                ('*/com.squareup.cash/databases/cash_money.db*'),
                get_cashApp)
}

