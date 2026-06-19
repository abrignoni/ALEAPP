# pylint: disable=W0613
__artifacts_v2__ = {
    "get_chromeMediaHistorySessions": {
        "name": "Media History - Sessions",
        "description": "Parses Media History playback sessions from Chromium Based Browsers",
        "author": "",
        "creation_date": "2021-01-26",
        "last_update_date": "2021-01-26",
        "requirements": "none",
        "category": "Chromium",
        "notes": "",
        "paths": ('*/app_chrome/Default/Media History*', '*/app_sbrowser/Default/Media History*', '*/app_opera/Media History*', '*/app_webview/Default/Media History*'),
        "output_types": "standard",
        "artifact_icon": "image",
    },
    "get_chromeMediaHistoryPlaybacks": {
        "name": "Media History - Playbacks",
        "description": "Parses Media History playbacks from Chromium Based Browsers",
        "author": "",
        "creation_date": "2021-01-26",
        "last_update_date": "2021-01-26",
        "requirements": "none",
        "category": "Chromium",
        "notes": "",
        "paths": ('*/app_chrome/Default/Media History*', '*/app_sbrowser/Default/Media History*', '*/app_opera/Media History*', '*/app_webview/Default/Media History*'),
        "output_types": "standard",
        "artifact_icon": "image",
    },
    "get_chromeMediaHistoryOrigins": {
        "name": "Media History - Origins",
        "description": "Parses Media History origins from Chromium Based Browsers",
        "author": "",
        "creation_date": "2021-01-26",
        "last_update_date": "2021-01-26",
        "requirements": "none",
        "category": "Chromium",
        "notes": "",
        "paths": ('*/app_chrome/Default/Media History*', '*/app_sbrowser/Default/Media History*', '*/app_opera/Media History*', '*/app_webview/Default/Media History*'),
        "output_types": "standard",
        "artifact_icon": "image",
    }
}

import os

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, get_next_unused_name, open_sqlite_db_readonly, lava_process_artifact, lava_insert_sqlite_data, artifact_processor, convert_human_ts_to_utc
from scripts.artifacts.chrome import get_browser_name


def _media_history_files(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if not file_found.endswith('Media History'):
            continue  # Skip all other files
        browser_name = get_browser_name(file_found)
        if file_found.find('app_sbrowser') >= 0:
            browser_name = 'Browser'
        elif file_found.find('.magisk') >= 0 and file_found.find('mirror') >= 0:
            continue  # Skip sbin/.magisk/mirror/data/.. , it should be duplicate data
        yield file_found, browser_name


@artifact_processor
def get_chromeMediaHistorySessions(files_found, report_folder, seeker, wrap_text):
    all_data = []
    data_headers = ['Last Updated', 'Origin ID', 'URL', 'Position', 'Duration', 'Title', 'Artist', 'Album', 'Source Title']
    lava_data_headers = data_headers.copy()
    lava_data_headers[0] = (lava_data_headers[0], 'datetime')
    all_data_headers = lava_data_headers + ['Browser Name']
    report_file = 'Unknown'

    for file_found, browser_name in _media_history_files(files_found):
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        select
        datetime(last_updated_time_s-11644473600, 'unixepoch') as last_updated_time_s,
            origin_id,
            url,
            strftime('%H:%M:%S',position_ms/1000, 'unixepoch') as position_ms,
            strftime('%H:%M:%S',duration_ms/1000, 'unixepoch') as duration_ms,
            title,
            artist,
            album,
            source_title
        from playbackSession
        ''')

        all_rows = cursor.fetchall()
        if len(all_rows) > 0:
            report_file = file_found if report_file == 'Unknown' else report_file + ', ' + file_found
            data_list = []
            for row in all_rows:
                data_list.append((convert_human_ts_to_utc(row[0]),row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))

            report_name = f'{browser_name} - Media History - Sessions'
            report = ArtifactHtmlReport(report_name)
            report_path = os.path.join(report_folder, f'{report_name}.temphtml')
            report_path = get_next_unused_name(report_path)[:-9]  # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            table_name, object_columns, column_map = lava_process_artifact(
                "Chromium", "get_chromeMediaHistorySessions", report_name, lava_data_headers, len(data_list))
            lava_insert_sqlite_data(table_name, data_list, object_columns, lava_data_headers, column_map)

            data_list = [row + (browser_name,) for row in data_list]
            all_data.extend(data_list)
        else:
            logfunc(f'No {browser_name} - Media History - Sessions data available')
        db.close()

    return all_data_headers, all_data, report_file


@artifact_processor
def get_chromeMediaHistoryPlaybacks(files_found, report_folder, seeker, wrap_text):
    all_data = []
    data_headers = ['Last Updated', 'ID', 'Origin ID', 'URL', 'Watch Time', 'Has Audio', 'Has Video']
    lava_data_headers = data_headers.copy()
    lava_data_headers[0] = (lava_data_headers[0], 'datetime')
    all_data_headers = lava_data_headers + ['Browser Name']
    report_file = 'Unknown'

    for file_found, browser_name in _media_history_files(files_found):
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        select
            datetime(last_updated_time_s-11644473600, 'unixepoch') as last_updated_time_s,
            id,
            origin_id,
            url,
            strftime('%H:%M:%S',watch_time_s, 'unixepoch') as watch_time_s,
            case has_audio
                when 0 then ''
                when 1 then 'Yes'
            end as has_audio,
            case has_video
                when 0 then ''
                when 1 then 'Yes'
            end as has_video
        from playback
        ''')

        all_rows = cursor.fetchall()
        if len(all_rows) > 0:
            report_file = file_found if report_file == 'Unknown' else report_file + ', ' + file_found
            data_list = []
            for row in all_rows:
                data_list.append((convert_human_ts_to_utc(row[0]),row[1],row[2],row[3],row[4],row[5],row[6]))

            report_name = f'{browser_name} - Media History - Playbacks'
            report = ArtifactHtmlReport(report_name)
            report_path = os.path.join(report_folder, f'{report_name}.temphtml')
            report_path = get_next_unused_name(report_path)[:-9]  # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            table_name, object_columns, column_map = lava_process_artifact(
                "Chromium", "get_chromeMediaHistoryPlaybacks", report_name, lava_data_headers, len(data_list))
            lava_insert_sqlite_data(table_name, data_list, object_columns, lava_data_headers, column_map)

            data_list = [row + (browser_name,) for row in data_list]
            all_data.extend(data_list)
        else:
            logfunc(f'No {browser_name} - Media History - Playbacks data available')
        db.close()

    return all_data_headers, all_data, report_file


@artifact_processor
def get_chromeMediaHistoryOrigins(files_found, report_folder, seeker, wrap_text):
    all_data = []
    data_headers = ['Last Updated', 'ID', 'Origin', 'Aggregate Watchtime']
    lava_data_headers = data_headers.copy()
    lava_data_headers[0] = (lava_data_headers[0], 'datetime')
    all_data_headers = lava_data_headers + ['Browser Name']
    report_file = 'Unknown'

    for file_found, browser_name in _media_history_files(files_found):
        db = open_sqlite_db_readonly(file_found)
        cursor = db.cursor()
        cursor.execute('''
        select
            datetime(last_updated_time_s-11644473600, 'unixepoch') as last_updated_time_s,
            id,
            origin,
            cast(aggregate_watchtime_audio_video_s/86400 as integer) || ':' || strftime('%H:%M:%S', aggregate_watchtime_audio_video_s ,'unixepoch') as aggregate_watchtime_audio_video_s
        from origin
        ''')

        all_rows = cursor.fetchall()
        if len(all_rows) > 0:
            report_file = file_found if report_file == 'Unknown' else report_file + ', ' + file_found
            data_list = []
            for row in all_rows:
                data_list.append((convert_human_ts_to_utc(row[0]),row[1],row[2],row[3]))

            report_name = f'{browser_name} - Media History - Origins'
            report = ArtifactHtmlReport(report_name)
            report_path = os.path.join(report_folder, f'{report_name}.temphtml')
            report_path = get_next_unused_name(report_path)[:-9]  # remove .temphtml
            report.start_artifact_report(report_folder, os.path.basename(report_path))
            report.add_script()
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()

            table_name, object_columns, column_map = lava_process_artifact(
                "Chromium", "get_chromeMediaHistoryOrigins", report_name, lava_data_headers, len(data_list))
            lava_insert_sqlite_data(table_name, data_list, object_columns, lava_data_headers, column_map)

            data_list = [row + (browser_name,) for row in data_list]
            all_data.extend(data_list)
        else:
            logfunc(f'No {browser_name} - Media History - Origins data available')
        db.close()

    return all_data_headers, all_data, report_file
