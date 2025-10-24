__artifacts_v2__ = {
    "Calendar": {
        "name": "Calendar",
        "description": "Parses provider calendars and events",
        "author": "@KevinPagano3",
        "version": "0.0.1",
        "date": "2023-01-06",
        "requirements": "none",
        "category": "Calendar",
        "notes": "",
        "paths": ('*/data/com.google.android.calendar/databases/cal_v2a*','*/com.android.providers.calendar/databases/calendar.db*'),
        "function": "get_calendar"
    }
}

import zlib
import sqlite3
import blackboxprotobuf
from datetime import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, timeline, tsv, is_platform_windows, open_sqlite_db_readonly, convert_ts_human_to_utc, convert_utc_human_to_timezone

def get_calendar(files_found, report_folder, seeker, wrap_text):
    
    data_list_events = []
    data_list_calendars = []
    
    for file_found in files_found:
        file_found = str(file_found)

        if file_found.endswith('calendar.db'):
            calendarDB = file_found
            source_calendarDB = file_found.replace(seeker.data_folder, '')
            
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
                for row in all_rows:
                    event_start = row[0]
                    if event_start is None:
                        pass
                    else:
                        event_start = convert_utc_human_to_timezone(convert_ts_human_to_utc(event_start),'UTC')

                    event_end = row[1]
                    if event_end is None:
                        pass
                    else:
                        event_end = convert_utc_human_to_timezone(convert_ts_human_to_utc(event_end),'UTC')
                
                    data_list_events.append((event_start,event_end,row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10], calendarDB))
                    
            # Get provider calendars
            cursor = db.cursor()
            cursor.execute('''
            select
            case
                when cal_sync8 is NULL then ''
                else datetime(cal_sync8/1000,'unixepoch')
            end,
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
                for row in all_rows:
                    cal_sync = row[0]
                    if cal_sync is "":
                        pass
                    else:
                        cal_sync = convert_utc_human_to_timezone(convert_ts_human_to_utc(cal_sync),'UTC')
                    
                    data_list_calendars.append((cal_sync,row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11], calendarDB))       
                
        if file_found.endswith('cal_v2a'):
            g_calendarDB = file_found
            source_g_calendarDB = file_found.replace(seeker.data_folder, '')

        else:
            continue # Skip all other files
        
    if data_list_events:
        description = 'Calendar - Events'
        report = ArtifactHtmlReport('Calendar - Events')
        report.start_artifact_report(report_folder, 'Calendar - Events', description)
        report.add_script()
        data_headers = ('Event Start Timestamp','Event End Timestamp','Event Timezone','Title','Description','Event Location','Sync ID','Organizer','Calendar Display Name','All Day Event','Has Alarm','Source')
        report.write_artifact_data_table(data_headers, data_list_events, source_calendarDB,html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'Calendar - Events'
        tsv(report_folder, data_headers, data_list_events, tsvname)
        
        tlactivity = 'Calendar - Events'
        timeline(report_folder, tlactivity, data_list_events, data_headers)
    
    else:
        logfunc('No Calendar - Events data available')
        
    if data_list_calendars:
        description = 'Calendar - Calendars'
        report = ArtifactHtmlReport('Calendar - Calendars')
        report.start_artifact_report(report_folder, 'Calendar - Calendars', description)
        report.add_script()
        data_headers = ('Created Timestamp','Calendar Name','Calendar Display Name','Account Name','Account Type','Visible','Calendar Location','Timezone','Owner Account','Is Primary','Color','Color Index','Source')
        report.write_artifact_data_table(data_headers, data_list_calendars, source_calendarDB,html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'Calendar - Calendars'
        tsv(report_folder, data_headers, data_list_calendars, tsvname)
        
        tlactivity = 'Calendar - Calendars'
        timeline(report_folder, tlactivity, data_list_calendars, data_headers)
    
    else:
        logfunc('No Calendar - Calendars data available')