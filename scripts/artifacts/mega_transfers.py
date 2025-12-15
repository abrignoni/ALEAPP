import sqlite3
import base64
from Crypto.Cipher import AES
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv



def decrypt(cell: str):
    cipher_text = base64.b64decode(cell)
    secret_key = "android_idfkvn8 w4y*(NC$G*(G($*GR*(#)*huio4h389$G"[0:32].encode('utf-8')
    algorithm = AES.new(secret_key, AES.MODE_ECB)
    plain_text = algorithm.decrypt(cipher_text).decode('utf-8')
    last_char = plain_text[-1]
    first_of_the_last_chars = plain_text.index(last_char)
    plain_text = plain_text[:first_of_the_last_chars]
    return plain_text


def get_mega_transfers(files_found, report_folder, seeker, wrap_text):
    
    db_filename = str(files_found[0])

    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()

    sql = """
        SELECT
            transfertimestamp,
            transferpath,
            transferfilename,
            transfersize,
            transfertype,
            transferstate,
            transferoriginalpath
        FROM 
            completedtransfers
        """
    cursor.execute(sql)
    results = cursor.fetchall()
    conn.close()

    data_headers = [
            "Timestamp",
            "Mega Folder",
            "Filename",
            "Size",
            "Direction",
            "State",
            "Transfer Path",
            ]
    data_list = []

    direction = {
            "0": "Download",
            "1": "Upload",
            "2": "Download",
            }

    state = {
            "0": "None",
            "1": "Queued",
            "2": "Active",
            "3": "Paused",
            "4": "Retrying",
            "5": "Completing",
            "6": "Completed",
            "7": "Cancelled",
            "8": "Failed",
            }

    for r in results:
        decrypted = list(map(lambda x: decrypt(x), r))
        timestamp = datetime.datetime.utcfromtimestamp(int(decrypted[0]) / 1000)
        decrypted[0] = f"{timestamp}" 
        decrypted[4] = direction[decrypted[4]]
        decrypted[5] = state[decrypted[5]]
        data_list.append(decrypted)

    if data_list:
        report = ArtifactHtmlReport('MEGA - Files')
        report.start_artifact_report(report_folder, "MEGA - Files")
        report.add_script()
        report.write_artifact_data_table(data_headers, data_list, db_filename)
        report.end_artifact_report()
        
        tsvname = f'MEGA - Files'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc('No MEGA files data available')
    
__artifacts__ = {
        "mega_transfers": (
                "Mega",
                ('*/mega.privacy.android.app/databases/megapreferences'),
                get_mega_transfers)
}