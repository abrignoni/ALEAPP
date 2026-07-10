# pylint: disable=W0613
__artifacts_v2__ = {
    "get_wellbeingaccount": {
        "name": "wellbeingaccount",
        "description": "Parses account data from the Google Digital Wellbeing AccountData protobuf file.",
        "author": "",
        "creation_date": "2020-02-25",
        "last_update_date": "2020-02-25",
        "requirements": "none",
        "category": "Digital Wellbeing",
        "notes": "",
        "paths": ('*/com.google.android.apps.wellbeing/files/AccountData.pb',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "battery",
        "sample_data": {
            "hc_pixel8pro_a16": "Android 16 | com.google.android.apps.wellbeing vc 839927 | 1 row",
            "kevin_pocox7_a15": "Android 15 | com.google.android.apps.wellbeing vc 762847 | 1 row",
            "pixel7a_a14": "Android 14 | com.google.android.apps.wellbeing vc 550467 | 1 row",
        },
        "html_columns": ['Protobuf Parsed Data'],
    }
}

import json

from scripts.ilapfuncs import artifact_processor
from scripts.parse3 import ParseProto


@artifact_processor
def get_wellbeingaccount(files_found, report_folder, seeker, wrap_text):
    source_path = str(files_found[0])
    content = ParseProto(source_path)

    content_json_dump = json.dumps(content, indent=4, sort_keys=True, ensure_ascii=False)
    parsedContent = str(content_json_dump).encode(encoding='UTF-8',errors='ignore')

    data_list = []
    data_list.append(('<pre id=\"json\">'+str(parsedContent).replace("\\n", "<br>")+'</pre>', str(content)))

    data_headers = ('Protobuf Parsed Data', 'Protobuf Data')
    return data_headers, data_list, source_path
