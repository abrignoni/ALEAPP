import os
import sqlite3

from scripts.ilapfuncs import logfunc, is_platform_windows 

def get_wellbeing(files_found, report_folder):

    head, tail = os.path.split(str(files_found[0]))
    db = sqlite3.connect(os.path.join(head, 'app_usage'))
    cursor = db.cursor()
    cursor.execute('''
    SELECT 
            events._id, 
            datetime(events.timestamp /1000, 'UNIXEPOCH') as timestamps, 
            packages.package_name,
            events.type,
            case
                when events.type = 1 THEN 'ACTIVITY_RESUMED'
                when events.type = 2 THEN 'ACTIVITY_PAUSED'
                when events.type = 12 THEN 'NOTIFICATION'
                when events.type = 18 THEN 'KEYGUARD_HIDDEN & || Device Unlock'
                when events.type = 19 THEN 'FOREGROUND_SERVICE_START'
                when events.type = 20 THEN 'FOREGROUND_SERVICE_STOP' 
                when events.type = 23 THEN 'ACTIVITY_STOPPED'
                when events.type = 26 THEN 'DEVICE_SHUTDOWN'
                when events.type = 27 THEN 'DEVICE_STARTUP'
                else events.type
                END as eventtype
            FROM
            events INNER JOIN packages ON events.package_id=packages._id 
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        with open(os.path.join(report_folder, 'Events.html'), 'w', encoding='utf8') as f:
            f.write('<html><body>')
            f.write('<h2> Wellbeing events report</h2>')
            f.write(f'Wellbeing event entries: {usageentries}<br>')
            f.write(f'Wellbeing events located at: {files_found[0]}<br>')
            f.write('<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>')
            f.write('<br/>')
            f.write('')
            f.write(f'<table class="table sticky">')
            f.write(f'<tr><th>Timestamp</th><th>Package ID</th><th>Event Type</th></tr>')
            for row in all_rows:
                f.write(f'<tr><td>{row[1]}</td><td>{row[2]}</td><td>{row[4]}</td></tr>')
            f.write(f'</table></body></html>')
    else:
            logfunc('No Wellbeing event data available')