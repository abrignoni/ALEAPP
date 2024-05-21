import os, hashlib, os

from pathlib import Path
from time import gmtime
from time import localtime
from time import strftime
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly
from datetime import datetime



# Write digest results to file

def write_hashes(files_found, report_folder, seeker, wrap_text, time_offset):
    sha2pulls = {}
    data_list = []
    for file_found in files_found:
        artifact_path = file_found.replace(seeker.directory, '')
        if os.path.isfile(file_found):
            with open(file_found, "rb") as f:
                fdata = f.read()
                sha2pulls = hashlib.sha256(fdata).hexdigest()

        else:
            pass
            

        data_list.append((file_found, sha2pulls))
        
    report = ArtifactHtmlReport('SHA256 File Hashes')
    report.start_artifact_report(report_folder, 'Message Digest for Processed Files')
    report.add_script()
    data_headers = ['Artifact', 'SHA256']
    report.write_artifact_data_table(data_headers, data_list, artifact_path, html_escape=False)
    report.end_artifact_report()



__artifacts__ = {
"File Hashes": (
    "File Hashes",
    ('*/*'),
    write_hashes
)
}
