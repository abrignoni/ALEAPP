__artifacts_v2__ = {
    "load_whatsapp_log": {
        "name": "WhatsApp - Log",
        "description": "Indexes log lines from WhatsApp logfiles",
        "author": "",
        "creation_date": "2026-07-09",
        "last_update_date": "2026-08-05",
        "requirements": "none",
        "category": "WhatsApp",
        "notes": "",
        "paths": ('*/com.whatsapp/files/Logs/whatsapp*',),
        "output_types": "standard",
        "artifact_icon": "users",
    }
}

from pathlib import Path
from datetime import datetime
import gzip
import re
from scripts.ilapfuncs import artifact_processor

DATE_PATTERN = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3})"

@artifact_processor
def load_whatsapp_log(files_found, report_folder, seeker, wrap_text):
    data_list = []
    
    for input_file in files_found:
        source = str(input_file)
        
        if source.lower().endswith('gz'):
            data = gzip.open(input_file, 'r' ).read().decode('utf-8')
        else:
            data = open(input_file, 'r').read()

        lines = re.split(DATE_PATTERN, data)
        for i in range(1, len(lines), 2):
            log_date = datetime.strptime(lines[i], "%Y-%m-%d %H:%M:%S.%f")
            data_list.append((Path(source).name, log_date, lines[i+1]))
                        
    data_headers = ('logfile', 'log_date', 'log')
    return data_headers, data_list, source
