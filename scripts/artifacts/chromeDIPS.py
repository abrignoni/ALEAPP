# Module Description: Parses Chromium DIPS (Detect Incidental Party State)
# Author: @KevinPagano3
# Date: 2023-04-07
# Artifact version: 0.0.1
# Requirements: none
# Thanks to Ryan Benson for awareness https://github.com/obsidianforensics/hindsight/pull/146/commits/015ee189c97c0a4e48deb59568dfe4f536ace8aa

import os
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, get_next_unused_name, open_sqlite_db_readonly
from scripts.artifacts.chrome import get_browser_name

def get_chromeDIPS(files_found, report_folder):

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
        
        stateless = 'first_stateless_bounce_time' in columns

        if 'first_user_interaction_time' in columns:
            first_user_col = 'first_user_interaction_time'
        else:
            first_user_col = 'first_user_activation_time'

        if 'last_user_interaction_time' in columns:
            last_user_col = 'last_user_interaction_time'
        else:
            last_user_col = 'last_user_activation_time'

        if stateless:
            last_bounce_expr = """
            case first_stateless_bounce_time
                when 0 then ''
                else datetime((first_stateless_bounce_time/1000000)-11644473600,'unixepoch')
            end,
            case last_stateless_bounce_time
                when 0 then ''
                else datetime((last_stateless_bounce_time/1000000)-11644473600,'unixepoch')
            end
            """
        else:
            last_bounce_expr = """
            case first_bounce_time
                when 0 then ''
                else datetime((first_bounce_time/1000000)-11644473600,'unixepoch')
            end,
            case last_bounce_time
                when 0 then ''
                else datetime((last_bounce_time/1000000)-11644473600,'unixepoch')
            end
            """

        sql = f'''
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
            case {first_user_col}
                when 0 then ''
                else datetime(({first_user_col}/1000000)-11644473600,'unixepoch')
            end,
            case {last_user_col}
                when 0 then ''
                else datetime(({last_user_col}/1000000)-11644473600,'unixepoch')
            end,
            case first_stateful_bounce_time
                when 0 then ''
                else datetime((first_stateful_bounce_time/1000000)-11644473600,'unixepoch')
            end,
            case last_stateful_bounce_time
                when 0 then ''
                else datetime((last_stateful_bounce_time/1000000)-11644473600,'unixepoch')
            end,
            {last_bounce_expr}
            from bounces
        '''

        cursor.execute(sql)
        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
        if usageentries > 0:
            description = 'DIPS - Incidental parties are sites without meaningful user interactions, such as bounce trackers'
            report = ArtifactHtmlReport(f'{browser_name} - Detect Incidental Party State')
            report_path = os.path.join(report_folder, f'{browser_name} - Detect Incidental Party State.temphtml')
            report_path = get_next_unused_name(report_path)[:-9]
            report.start_artifact_report(report_folder, os.path.basename(report_path), description)
            report.add_script()
            data_headers = (
                'Site',
                'First Site Storage Timestamp',
                'Last Site Storage Timestamp',
                'First User Interaction Timestamp',
                'Last User Interaction Timestamp',
                'First Stateful Bounce Timestamp',
                'Last Stateful Bounce Timestamp',
                'First Stateless Bounce Timestamp',
                'Last Stateless Bounce Timestamp'
            )
            if stateless:
                tl_last = ('First Stateless Bounce Timestamp', 'Last Stateless Bounce Timestamp')
            else:
                tl_last = ('First Bounce Timestamp', 'Last Bounce Timestamp')
            tl_data_headers = (
                'First Site Storage Timestamp',
                'Site',
                'Last Site Storage Timestamp',
                'First User Interaction Timestamp',
                'Last User Interaction Timestamp',
                'First Stateful Bounce Timestamp',
                'Last Stateful Bounce Timestamp',
                tl_last[0],
                tl_last[1]
            )
            data_list = []
            tl_data_list = []
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
                tl_data_list.append((row[1], row[0], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))

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
