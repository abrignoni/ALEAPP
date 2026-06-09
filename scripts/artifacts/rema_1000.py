__artifacts_v2__ = {
        "rema1000_receipt_raw": {
        "name": "Rema1000 Receipts",
        "description": "Extracts Rema1000 receipts from the android app 'Rema1000 | Scan Selv'. All raw data.",
        "author": "Nicolai Martini",
        "version": "1.1",
        "creation_date": "2026-04-17",
        "last_update_date": "2026-06-09",
        "requirements": "Cellebrite UFED After First Unlock data acquisition, or similar",
        "category": "Rema1000 | Scan Selv",
        "notes": "forensics data of supermarket habit and location insights.",
        "paths": ("*/dk.rema1000.app/databases/receipts.db*",),
        "output_types": "standard",
        "artifact_icon": "shopping-cart"
    },
    "rema1000_receipt_prettified": {
        "name": "Rema1000 Receipts, prettified",
        "description": "Extracts Rema1000 receipts from the android app 'Rema1000 | Scan Selv'. Data is prettified.",
        "author": "Nicolai Martini",
        "version": "1.1",
        "creation_date": "2026-04-17",
        "last_update_date": "2026-06-09",
        "requirements": "Cellebrite UFED After First Unlock data acquisition, or similar",
        "category": "Rema1000 | Scan Selv",
        "notes": "forensics data of supermarket habit and location insights.",
        "paths": ("*/dk.rema1000.app/databases/receipts.db*"),
        "output_types": "standard",
        "artifact_icon": "shopping-cart"
    }
}

from datetime import datetime
from zoneinfo import ZoneInfo
from scripts.ilapfuncs import artifact_processor, open_sqlite_db_readonly, logfunc

@artifact_processor
def rema1000_receipt_raw(files_found, report_folder, seeker, wrap_text):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('receipts.db'):
            source_path = file_found
            data_headers = ('id','displayId','paymentDate','paymentSource',
                            'storeNumber','totalPrice','totalPriceString',
                            'totalDiscount','totalVat','Chargeback',
                            'searchText','zipString','pp_id','pp_cardType','pp_maskedPan')
            db = open_sqlite_db_readonly(file_found)
            cur = db.cursor()
            cur.execute(f"""
                        SELECT *
                        FROM ReceiptEntity;
                        """)
            rows=cur.fetchall()
            entries=len(rows)
            if entries>0:
                entries_list=[]
                for row in rows:
                    list_row=list(row)
                    for i in range(len(list_row)):
                        if list_row[i] is None:
                            list_row[i]="None"
                    entries_list.append(list_row)
                return data_headers, entries_list, source_path
            else:
                logfunc('No Rema1000 | Scan & Go data available')


@artifact_processor
def rema1000_receipt_prettified(files_found, report_folder, seeker, wrap_text):  
    available_products=[]
    translation_table = str.maketrans({
        "Æ": "AE", "æ": "ae",
        "Ø": "OE", "ø": "oe",
        "Å": "AA", "å": "aa",
        ".": ""
    })
    
    for file_found in files_found:
        if file_found.endswith('receipts.db'):
            source_path = file_found
            products=open_sqlite_db_readonly(file_found)
            products_cur=products.cursor()
            products_cur.execute(f"""
                                 SELECT shelfText1
                                 FROM ReceiptItemEntity;
                                 """)            
            for product in products_cur.fetchall():
                product=product[0].replace("SMÅKAGER","SMAKAGER") # Danish norm to replace Å/å with AA/aa but this one item diverts from norm.
                available_products.append(product.translate(translation_table).lower())
            data_headers = ('Date and time, DK','Location','Items','Total price, DKK', 'Payment method','Payment Card Type', 'Payment Card PAN')
            receipt_db = open_sqlite_db_readonly(file_found)
            receipt_cur = receipt_db.cursor()
            receipt_cur.execute(f"""
                        SELECT paymentDate, paymentSource,
                        totalPrice, searchText, zipString,
                        pp_cardType, pp_maskedPan
                        FROM ReceiptEntity;
                        """)
            rows=receipt_cur.fetchall()
            entries=len(rows)
            if entries>0:
                entries_list=[]
                for row in rows:
                    prettified_list=["","","","","","",""]
                    list_row=list(row)
                    for i in range(len(list_row)):
                        if list_row[i] is None:
                            list_row[i]="None"
                    prettified_list[0]=f"{datetime.fromtimestamp(list_row[0]/1000, tz=ZoneInfo('Europe/Copenhagen')).strftime('%Y-%m-%d %H:%M:%S')}"
                    prettified_list[1]= f"{list_row[3].split(";")[1].capitalize()}, {list_row[4]}, {list_row[3].split(";")[2].capitalize()}"
                    split_items = [item.translate(translation_table) for item in list_row[3].split(";")[3:]]
                    prettified_list[2]=", ".join([item for item in split_items if item in available_products])
                    prettified_list[3]=f"{list_row[2]/100:.2f}"
                    prettified_list[4]=list_row[1]
                    prettified_list[5]=list_row[5]
                    prettified_list[6]=list_row[6]
                    entries_list.append(prettified_list)
                return data_headers, entries_list, source_path
            else:
                logfunc('No Rema1000 | Scan & Go data available')