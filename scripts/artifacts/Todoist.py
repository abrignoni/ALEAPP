# Todoist - Parses items, notes and projects
# Author:  Kevin Pagano (https://startme.stark4n6.com)
# Date 2023-04-26
# Version: 0.1
# Requirements:  None

import sqlite3
import textwrap

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, open_sqlite_db_readonly, kmlgen

def get_Todoist(files_found, report_folder, seeker, wrap_text):
    
    for file_found in files_found:
        file_found = str(file_found)  
        if file_found.endswith('database.db'):
            break
        else:
            continue # Skip all other files
            
    db = open_sqlite_db_readonly(file_found)
    
    cursor = db.cursor()
    cursor.execute('''
    select
    datetime(items.date_added/1000,'unixepoch') as "Timestamp Added",
    items.added_by_uid,
    items.content,
    items.description,
    items.due_date,
    items.due_timezone,
    items.due_string,
    case items.due_is_recurring
        when 0 then ''
        when 1 then 'Yes'
    end as "Recurring Due Date",
    items.priority,
    items.child_order,
    projects.name as "Project Name",
    item_labels.label_name,
    items._id
    from items
    left outer join projects on items.project_id = projects._id
    left outer join item_labels on items._id = item_labels.item_id
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Todoist - Items')
        report.start_artifact_report(report_folder, 'Todoist - Items')
        report.add_script()
        data_headers = ('Timestamp Added','Added By UID','Content','Description','Due Date','Due Timezone','Due String','Recurring Due Date','Priority','Child Order','Project Name','Label','Item ID')
        
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12]))
            
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Todoist - Items'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Todoist - Items'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Todoist - Items data available')
        
    cursor.execute('''
    select
    datetime(notes.posted/1000,'unixepoch') as "Timestamp Posted",
    notes.content,
    note_file_attachments.resource_type,
    note_file_attachments.file_url,
    note_file_attachments.file_name,
    note_file_attachments.file_type,
    note_file_attachments.file_size,
    note_file_attachments.image,
    note_file_attachments.title,
    note_file_attachments.description,
    notes._id
    from notes
    left outer join note_file_attachments on notes._id = note_file_attachments.note_id
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Todoist - Notes')
        report.start_artifact_report(report_folder, 'Todoist - Notes')
        report.add_script()
        data_headers = ('Timestamp Posted','Content','Resource Type','File URL','File Name','File Type','File Size','Image','Title','Description','Note ID')
        
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]))
            
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Todoist - Notes'
        tsv(report_folder, data_headers, data_list, tsvname)
        
        tlactivity = f'Todoist - Notes'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No Todoist - Notes data available')
        
    cursor.execute('''
    select
    name,
    color,
    view_style,
    child_order,
    case collapsed
        when 0 then ''
        when 1 then 'Yes'
    end,
    case shared
        when 0 then ''
        when 1 then 'Yes'
    end,
    case favorite
        when 0 then ''
        when 1 then 'Yes'
    end,
    type
    from projects
    ''')
    
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        report = ArtifactHtmlReport('Todoist - Projects')
        report.start_artifact_report(report_folder, 'Todoist - Projects')
        report.add_script()
        data_headers = ('Project Name','Color','View Style','Child Order','Collapsed','Shared','Favorited','Type')
        
        data_list = []
        for row in all_rows:
            data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7]))
            
        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = f'Todoist - Projects'
        tsv(report_folder, data_headers, data_list, tsvname)
        
    else:
        logfunc('No Todoist - Projects data available') 
                
    db.close()

__artifacts__ = {
        "Todoist": (
                "Todoist",
                ('*/com.todoist/databases/database.db*'),
                get_Todoist)
}
    