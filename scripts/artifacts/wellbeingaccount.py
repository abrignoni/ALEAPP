import json
import os

from scripts.ilapfuncs import logfunc, is_platform_windows 
from scripts.parse3 import ParseProto

def get_wellbeingaccount(files_found, report_folder):
    content = ParseProto(str(files_found[0]))
    
    content_json_dump = json.dumps(content, indent=4, sort_keys=True, ensure_ascii=False)
    parsedContent = str(content_json_dump).encode(encoding='UTF-8',errors='ignore')
    
    with open(os.path.join(report_folder, 'Account Data.html'), 'w', encoding='utf8') as f:
        f.write('<html><body>')
        f.write('<h2> Wellbeing Account report</h2>')
        f.write(f'Wellbeing Account located at: {files_found[0]}<br>')
        f.write('<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>')
        f.write('<br/>')
        f.write('')
        f.write(f'<table class="table sticky">')
        f.write(f'<tr><th>Protobuf Parsed Data</th><th>Protobuf Data</th></tr>')
        f.write('<tr><td><pre id=\"json\">'+str(parsedContent).replace("\\n", "<br>")+'</pre></td><td>'+str(content)+'</td></tr>')
        f.write(f'</table></body></html>')