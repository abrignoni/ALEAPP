# pylint: disable=W0613,W0631
__artifacts_v2__ = {
    "get_cashApp": {
        "name": "Cash App",
        "description": "Parses Cash App transactions (date, sender and recipient display names, unique IDs and cashtags, amount, status and note) from cash_money.db.",
        "author": "",
        "creation_date": "2021-10-06",
        "last_update_date": "2021-10-06",
        "requirements": "none",
        "category": "Cash App",
        "notes": "",
        "paths": ('*/com.squareup.cash/databases/cash_money.db*',),
        "output_types": "standard",
        "artifact_icon": "package",
    }
}

from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, convert_human_ts_to_utc


@artifact_processor
def get_cashApp(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('.db'):
            source_path = file_found
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
    for row in all_rows:
        data_list.append((convert_human_ts_to_utc(row[8]),row[0],row[3],row[1],row[2],row[6],row[4],row[5],row[10],row[7],row[9]))
    db.close()

    data_headers = (
        ('Transaction Date', 'datetime'),
        'User Account Role',
        'Sender Display Name',
        'Sender Unique ID',
        'Sender Cashtag',
        'Recipient Display Name',
        'Recipient Unique ID',
        'Recipient Cashtag',
        'Transaction Amount',
        'Transaction Status',
        'Note',
    )
    return data_headers, data_list, source_path
