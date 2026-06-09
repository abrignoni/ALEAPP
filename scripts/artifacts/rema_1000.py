__artifacts_v2__ = {
        "rema1000_receipt_raw": {
        "name": "Rema1000 Receipts, raw",
        "description": "Extracts Rema1000 receipts from the android app 'Rema1000 | Scan Selv'. All raw data.",
        "author": "Nicolai Martini",
        "version": "1.2",
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
        "version": "1.2",
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
from scripts.ilapfuncs import artifact_processor, get_file_path, get_sqlite_db_records, logfunc

@artifact_processor
def rema1000_receipt_raw(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "receipts.db")
    data_headers = ("id","displayId","paymentDate","paymentSource",
                    "storeNumber","totalPrice","totalPriceString",
                    "totalDiscount","totalVat","Chargeback",
                    "searchText","zipString","pp_id","pp_cardType","pp_maskedPan")
    query = """SELECT * FROM ReceiptEntity;"""
    raw_records = get_sqlite_db_records(source_path, query)
    entries=len(raw_records)
    if entries>0:
        entries_list=[]
        for record in raw_records:
            list_receipt=list(record)
            for index, item in enumerate(list_receipt):
                if item is None:
                    list_receipt[index] = "None"
            entries_list.append(list_receipt)
        return data_headers, entries_list, source_path
    else:
        logfunc("No Rema1000 | Scan & Go data available")


@artifact_processor
def rema1000_receipt_prettified(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, "receipts.db")
    available_products=[]
    translation_table = str.maketrans({
        "Æ": "AE", "æ": "ae",
        "Ø": "OE", "ø": "oe",
        "Å": "AA", "å": "aa",
        ".": ""
    })
    data_headers = ("Date and time, DK","Location","Items","Total price, DKK", "Payment method","Payment Card Type", "Payment Card PAN")
    query = """SELECT shelfText1 FROM ReceiptItemEntity;"""
    product_records = get_sqlite_db_records(source_path, query)
    for product in product_records:
        product=product[0].replace("SMÅKAGER","SMAKAGER") # Danish norm to replace Å/å with AA/aa but this one item diverts from norm.
        available_products.append(product.translate(translation_table).lower())
    query = """
                SELECT paymentDate, paymentSource,
                totalPrice, searchText, zipString,
                pp_cardType, pp_maskedPan
                FROM ReceiptEntity;
                """
    receipt_records = get_sqlite_db_records(source_path, query)
    entries=len(receipt_records)
    if entries>0:
        entries_list=[]
        for receipt in receipt_records:
            prettified_list=["","","","","","",""]
            list_receipt=list(receipt)
            for index, item in enumerate(list_receipt):
                if item is None:
                    list_receipt[index] = "None"
            prettified_list[0]=f"{datetime.fromtimestamp(list_receipt[0]/1000, tz=ZoneInfo('Europe/Copenhagen')).strftime('%Y-%m-%d %H:%M:%S')}"
            prettified_list[1]= f"{list_receipt[3].split(';')[1].capitalize()}, {list_receipt[4]}, {list_receipt[3].split(';')[2].capitalize()}"
            split_items = [item.translate(translation_table) for item in list_receipt[3].split(";")[3:]]
            prettified_list[2]=", ".join([item for item in split_items if item in available_products])
            prettified_list[3]=f"{list_receipt[2]/100:.2f}"
            prettified_list[4]=list_receipt[1]
            prettified_list[5]=list_receipt[5]
            prettified_list[6]=list_receipt[6]
            entries_list.append(prettified_list)
        return data_headers, entries_list, source_path
    else:
        logfunc("No Rema1000 | Scan & Go data available")
