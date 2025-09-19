__artifacts_v2__ = {
    "get_callTranscription": {
        "name": "Android Call Transcriptions",
        "description": "Parses recorded calls transcriptions",
        "author": "Alexis Brignoni",
        "version": "0.0.1",
        "date": "2025-09-19",
        "requirements": "none",
        "category": "phone",
        "notes": "",
        "paths": ('*/com.google.android.dialer/files/fermat_files/*.pb'),
        "output_types": "standard",
        "artifact_icon": "phone"
    }
}

import blackboxprotobuf
from pathlib import Path
from datetime import *
from scripts.ilapfuncs import artifact_processor

@artifact_processor
def get_callTranscription(files_found, report_folder, seeker, wrap_text):

    data_list = []
    for file_found in files_found:
        if file_found.endswith('-transcription.pb'):
            path_object = Path(file_found)
            filename = path_object.name
            parentpath = path_object.parent
            with open (file_found, 'rb') as f:
                pb = f.read()
                protostuff, types = blackboxprotobuf.decode_message(pb)
                transcription_data = protostuff['1']
                
                for data in transcription_data:
                    timestamp = data['3']
                    timestamp = timestamp / 1000
                    usernumber  = data['4']
                    transcript = data['2'].decode()
                    data_list.append((timestamp,usernumber,transcript,filename))
            
                    
    data_headers = (('Timestamp','datetime'),'User','Transcript','Filename')
    return data_headers, data_list, str(parentpath)


        