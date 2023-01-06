# Module Description: Parses provider calendars and events
# Author: @KevinPagano3 (Twitter) / stark4n6@infosec.exchange (Mastodon)
# Date: 2023-01-06
# Artifact version: 0.0.1

import zlib
import sqlite3
import blackboxprotobuf
import os
from datetime import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, timeline, tsv, is_platform_windows, open_sqlite_db_readonly

def get_calendar(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('-wal'):
            continue
        elif file_found.endswith('-shm'):
            continue
        elif file_found.endswith('-journal'):
            continue
        if os.path.basename(file_found).endswith('calendar.db'):
            calendarDB = file_found
            source_calendarDB = file_found.replace(seeker.directory, '')
        
        if os.path.basename(file_found).endswith('cal_v2a'):
            g_calendarDB = file_found
            source_g_calendarDB = file_found.replace(seeker.directory, '')
        
    db = open_sqlite_db_readonly(calendarDB)
    
    #Get provider calendar events
    cursor = db.cursor()
    cursor.execute('''
    select
    datetime(Events.dtstart/1000,'unixepoch') as "Event Start Timestamp",
    datetime(Events.dtend/1000,'unixepoch') as "Event End Timestamp",
    Events.eventTimezone,
    Events.title,
    Events.description,
    Events.eventLocation,
    Events._sync_id,
    Events.organizer,
    Calendars.calendar_displayName,
    case Events.allDay
        when 0 then ''
        when 1 then 'Yes'
    end,
    case Events.hasAlarm
        when 0 then ''
        when 1 then 'Yes'
    end
    from Events
    left join Calendars on Calendars._id = Events.calendar_id
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
                            
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]))

        description = 'Calendar - Events'
        report = ArtifactHtmlReport('Calendar - Events')
        report.start_artifact_report(report_folder, 'Calendar - Events', description)
        report.add_script()
        data_headers = ('Event Start Timestamp','Event End Timestamp','Event Timezone','Title','Description','Event Location','Sync ID','Organizer','Calendar Display Name','All Day Event','Has Alarm')
        report.write_artifact_data_table(data_headers, data_list, source_calendarDB,html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'Calendar - Events'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Calendar - Events'
        timeline(report_folder, tlactivity, data_list, data_headers)
    
    else:
        logfunc('No Calendar - Events data available')
        
    #Get provider calendars
    cursor = db.cursor()
    cursor.execute('''
    select
    datetime(cal_sync8/1000,'unixepoch') as "Last Synced Timestamp",
    name,
    calendar_displayName,
    account_name,
    account_type,
    case visible
        when 0 then 'No'
        when 1 then 'Yes'
    end,
    calendar_location,
    calendar_timezone,
    ownerAccount,
    case isPrimary
        when 0 then ''
        when 1 then 'Yes'
    end,
    calendar_color,
    calendar_color_index
    from Calendars
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        data_list = []
        for row in all_rows:
                            
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11]))

        description = 'Calendar - Calendars'
        report = ArtifactHtmlReport('Calendar - Calendars')
        report.start_artifact_report(report_folder, 'Calendar - Calendars', description)
        report.add_script()
        data_headers = ('Created Timestamp','Calendar Name','Calendar Display Name','Account Name','Account Type','Visible','Calendar Location','Timezone','Owner Account','Is Primary','Color','Color Index')
        report.write_artifact_data_table(data_headers, data_list, source_calendarDB,html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'Calendar - Calendars'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = 'Calendar - Calendars'
        timeline(report_folder, tlactivity, data_list, data_headers)
    
    else:
        logfunc('No Calendar - Calendars data available')
    
__artifacts__ = {
        "Calendar": (
                "Calendar",
                ('*/data/com.google.android.calendar/databases/cal_v2a*','*/com.android.providers.calendar/databases/calendar.db*'),
                get_calendar)
}