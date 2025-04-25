import os
import sqlite3
import textwrap

from packaging import version
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly

def get_slopes(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)
        if not os.path.basename(file_found) == 'slopes.db': # skip -journal and other files
            continue
           
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        
        cursor.execute('''
        select
        name,
        locality,
        admin_area,
        country,
        coordinate_lat,
        coordinate_long,
        website,
        generalNumber,
        skiPatrolNumber,
        baseAltitude,
        summitAltitude,
        distance,
        veryEasyRuns,
        easyRuns,
        intermediateRuns,
        expertRuns,
        case has_lift_data
            when 0 then ''
            when 1 then 'Yes'
        end as 'Has Ski Lift'
        from resort
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Slopes - Resort Details')
            report.start_artifact_report(report_folder, 'Slopes - Resort Details')
            report.add_script()
            data_headers = ('Resort Name','City','State','Country','Latitude','Longitude','Website','General Number','Ski Patrol Number','Base Altitude','Summit Altitude','Distance','Very Easy Runs','Easy Runs','Intermediate Runs','Expert Runs','Has Ski Lift')
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Slopes - Resort Details'
            tsv(report_folder, data_headers, data_list, tsvname)
            
        else:
            logfunc('No Slopes - Resort Details data available')

        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(action.start,'unixepoch'),
        datetime(action.end,'unixepoch'),
        strftime('%H:%M:%S',duration, 'unixepoch'),
        action.type,
        action.distance as 'Distance (M)',
        action.max_lat,
        action.max_long,
        action.min_lat,
        action.min_long,
        action.avg_speed,
        action.top_speed,
        action.max_alt,
        action.min_alt,
        activity.location_name
        from action
        left join activity on activity.id = action.activity
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Slopes - Actions')
            report.start_artifact_report(report_folder, 'Slopes - Actions')
            report.add_script()
            data_headers = ('Timestamp (Start)','Timestamp (End)','Duration','Type','Distance (M)','Max Latitude','Max Longitude','Min Latitude','Min Latitude','Average Speed','Top Speed','Max Altitude','Min Altitude','Resort Name')
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Slopes - Actions'
            tsv(report_folder, data_headers, data_list, tsvname)
            
            tlactivity = f'Slopes - Actions'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('No Slopes - Actions data available')

        cursor = db.cursor()
        cursor.execute('''
        select
        lift.name,
        lift.type,
        lift.capacity,
        lift.start_lat,
        lift.start_long,
        lift.end_lat,
        lift.end_long,
        lift.pivots,
        lift.id,
        resort.name,
        resort.locality,
        resort.admin_area,
        resort.country
        from lift
        left join resort on resort.id = lift.resort
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            report = ArtifactHtmlReport('Slopes - Lift Details')
            report.start_artifact_report(report_folder, 'Slopes - Lift Details')
            report.add_script()
            data_headers = ('Name','Type','Capacity','Start Latitude','Start Longitude','End Latitude','End Longitude','Pivots','ID','Resort Name','City','State','Country')
            data_list = []
            for row in all_rows:
                data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12]))

            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = f'Slopes - Lift Details'
            tsv(report_folder, data_headers, data_list, tsvname)
            
        else:
            logfunc('No Slopes - Lift Details data available')

        db.close()

__artifacts__ = {
        "slopes": (
                "Slopes",
                ('*/com.consumedbycode.slopes/databases/slopes.db*'),
                get_slopes)
}
