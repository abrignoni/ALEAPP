# Module Description: Parses Chromium DIPS (Detect Incidental Party State)
# Author: @KevinPagano3
# Date: 2023-04-07
# Artifact version: 0.0.1
# Requirements: none
# Thanks to Ryan Benson for awareness https://github.com/obsidianforensics/hindsight/pull/146/commits/015ee189c97c0a4e48deb59568dfe4f536ace8aa

import os
import sqlite3
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, get_next_unused_name, open_sqlite_db_readonly
from chrome import get_browser_name

def get_chromeDIPS(files_found, report_folder, seeker, wrap_text, time_offset):

    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('DIPS'):
            continue # Skip all other files

        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'
        elif file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data??
        
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        
        columns = [i[1] for i in cursor.execute('PRAGMA table_info(bounces)')]
        
        if 'first_stateless_bounce_time' not in columns:
            cursor.execute('''
            select
            site,
            case first_site_storage_time
                when 0 then ''
                else datetime((first_site_storage_time/1000000)-11644473600,'unixepoch')
            end,
            case last_site_storage_time
                when 0 then ''
                else datetime((last_site_storage_time/1000000)-11644473600,'unixepoch')
            end,
            case first_user_interaction_time
                when 0 then ''
                else datetime((first_user_interaction_time/1000000)-11644473600,'unixepoch')
            end,
            case last_user_interaction_time
                when 0 then ''
                else datetime((last_user_interaction_time/1000000)-11644473600,'unixepoch')
            end,
            case first_stateful_bounce_time
                when 0 then ''
                else datetime((first_stateful_bounce_time/1000000)-11644473600,'unixepoch')
            end,
            case last_stateful_bounce_time
                when 0 then ''
                else datetime((last_stateful_bounce_time/1000000)-11644473600,'unixepoch')
            end,
            case first_bounce_time
                when 0 then ''
                else datetime((first_bounce_time/1000000)-11644473600,'unixepoch')
            end,
            case last_bounce_time
                when 0 then ''
                else datetime((last_bounce_time/1000000)-11644473600,'unixepoch')
            end
            from bounces
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                description = 'DIPS - Incidental parties are sites without meaningful user interactions, such as bounce trackers'
                report = ArtifactHtmlReport(f'{browser_name} - Detect Incidental Party State')
                #check for existing and get next name for report file, so report from another file does not get overwritten
                report_path = os.path.join(report_folder, f'{browser_name} - Detect Incidental Party State.temphtml')
                report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
                report.start_artifact_report(report_folder, os.path.basename(report_path), description)
                report.add_script()
                data_headers = ('Site','First Site Storage Timestamp','Last Site Storage Timestamp','First User Interaction Timestamp','Last User Interaction Timestamp','First Stateful Bounce Timestamp','Last Stateful Bounce Timestamp','First Stateless Bounce Timestamp','Last Stateless Bounce Timestamp') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                tl_data_headers = ('First Site Storage Timestamp','Site','Last Site Storage Timestamp','First User Interaction Timestamp','Last User Interaction Timestamp','First Stateful Bounce Timestamp','Last Stateful Bounce Timestamp','First Bounce Timestamp','Last Bounce Timestamp')
                data_list = []
                tl_data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))
                    
                    tl_data_list.append((row[1],row[0],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'{browser_name} - Detect Incidental Party State'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'{browser_name} - Detect Incidental Party State'
                timeline(report_folder, tlactivity, tl_data_list, tl_data_headers)
            else:
                logfunc(f'No {browser_name} - Detect Incidental Party State data available')
        
        else:
            cursor.execute('''
            select
            site,
            case first_site_storage_time
                when 0 then ''
                else datetime((first_site_storage_time/1000000)-11644473600,'unixepoch')
            end,
            case last_site_storage_time
                when 0 then ''
                else datetime((last_site_storage_time/1000000)-11644473600,'unixepoch')
            end,
            case first_user_interaction_time
                when 0 then ''
                else datetime((first_user_interaction_time/1000000)-11644473600,'unixepoch')
            end,
            case last_user_interaction_time
                when 0 then ''
                else datetime((last_user_interaction_time/1000000)-11644473600,'unixepoch')
            end,
            case first_stateful_bounce_time
                when 0 then ''
                else datetime((first_stateful_bounce_time/1000000)-11644473600,'unixepoch')
            end,
            case last_stateful_bounce_time
                when 0 then ''
                else datetime((last_stateful_bounce_time/1000000)-11644473600,'unixepoch')
            end,
            case first_stateless_bounce_time
                when 0 then ''
                else datetime((first_stateless_bounce_time/1000000)-11644473600,'unixepoch')
            end,
            case last_stateless_bounce_time
                when 0 then ''
                else datetime((last_stateless_bounce_time/1000000)-11644473600,'unixepoch')
            end
            from bounces
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                description = 'DIPS - Incidental parties are sites without meaningful user interactions, such as bounce trackers'
                report = ArtifactHtmlReport(f'{browser_name} - Detect Incidental Party State')
                #check for existing and get next name for report file, so report from another file does not get overwritten
                report_path = os.path.join(report_folder, f'{browser_name} - Detect Incidental Party State.temphtml')
                report_path = get_next_unused_name(report_path)[:-9] # remove .temphtml
                report.start_artifact_report(report_folder, os.path.basename(report_path), description)
                report.add_script()
                data_headers = ('Site','First Site Storage Timestamp','Last Site Storage Timestamp','First User Interaction Timestamp','Last User Interaction Timestamp','First Stateful Bounce Timestamp','Last Stateful Bounce Timestamp','First Stateless Bounce Timestamp','Last Stateless Bounce Timestamp') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
                tl_data_headers = ('First Site Storage Timestamp','Site','Last Site Storage Timestamp','First User Interaction Timestamp','Last User Interaction Timestamp','First Stateful Bounce Timestamp','Last Stateful Bounce Timestamp','First Stateless Bounce Timestamp','Last Stateless Bounce Timestamp')
                data_list = []
                tl_data_list = []
                for row in all_rows:
                    data_list.append((row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))
                    
                    tl_data_list.append((row[1],row[0],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))

                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'{browser_name} - Detect Incidental Party State'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'{browser_name} - Detect Incidental Party State'
                timeline(report_folder, tlactivity, tl_data_list, tl_data_headers)
            else:
                logfunc(f'No {browser_name} - Detect Incidental Party State data available')
        
        db.close()

__artifacts__ = {
        "ChromeDIPS": (
                "Chromium",
                ('*/app_chrome/Default/DIPS*','*/app_sbrowser/Default/DIPS*', '*/app_opera/DIPS*','*/app_webview/Default/DIPS*'),
                get_chromeDIPS)
}
