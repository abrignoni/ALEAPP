
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

def get_appLockerfishingnetdb(files_found, report_folder, seeker, wrap_text):
    
    data_list = []
    for file_found in files_found:
        file_found = str(file_found)
        
        message = 'The located database is encrypted. It contains information regarding the source directory of the encrypted files, timestamp metadata, and original filenames.'
        decryptioninst = 'To decrypt follow the instructions at the following URL: https://theincidentalchewtoy.wordpress.com/2021/12/07/decrypting-the-calculator-apps/'
        keytodecrypt = 'Rny48Ni8aPjYCnUI'    
                       
        data_list.append((message, decryptioninst, keytodecrypt))
                            
                        
        if data_list:
            report = ArtifactHtmlReport('Calculator Locker Database')
            report.start_artifact_report(report_folder, 'Calculator Locker Database')
            report.add_script()
            data_headers = ('Encrypted Pattern', 'Decrypted Pattern', 'Key To Decrypt')
            report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Media'])
            report.end_artifact_report()
            
            tsvname = f'Calculator Locker Database data'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            
        else:
            logfunc('No Calculator Locker Database data available')
            
__artifacts__ = {
        "App Locker DB": (
                "Encrypting Media Apps",
                ('*/.privacy_safe/db/privacy_safe.db'),
                get_appLockerfishingnetdb)
}