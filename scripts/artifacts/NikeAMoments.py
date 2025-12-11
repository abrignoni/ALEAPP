# Get Information relative to the activity moments that are present in the database (com.nike.nrc.room) from the Nike Run app
# Present the data in a timeline using timeline JS
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-03-18
# Version: 1.0
# Requirements: Python 3.7 or higher
import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_nike_activMoments(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Nike Activity Moments")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)

    cursor = db.cursor()
    cursor.execute('''
    Select as2_sa_id, as2_sa_start_utc_ms, as2_sa_end_utc_ms, as2_sa_active_duration_ms
    from activity
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries} Nike Activities")
        report = ArtifactHtmlReport('Nike - Activity Moments')
        report.start_artifact_report(report_folder, 'Nike - Activity Moments')
        report.add_script()
        data_headers = ('Activity ID', 'Start Time UTC', 'End Time UTC', 'Duration', 'Timeline')
        data_list = []
        timelineList = []
        for row in all_rows:
            timelineArray = []
            id = row[0]
            start_time_utc = row[1]
            # convert ms to date
            start_time_d = datetime.datetime.utcfromtimestamp(start_time_utc / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
            start_hour = datetime.datetime.utcfromtimestamp(start_time_utc / 1000.0).strftime('%H:%M:%S')
            start_hour = str(start_hour)
            timelineArray.append({'time': start_hour, 'text': 'Run started', 'type': 'fa-solid fa-person-running'})
            end_time_utc = row[2]
            # convert ms to date
            end_time_d = datetime.datetime.utcfromtimestamp(end_time_utc / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
            end_hour = datetime.datetime.utcfromtimestamp(end_time_utc / 1000.0).strftime('%H:%M:%S')
            end_hour = str(end_hour)
            duration = row[3]
            # convert ms to minutes
            duration = duration / 60000
            # round to 2 decimals
            duration = round(duration, 2)
            cursor.execute('''
                            Select as2_m_type, as2_m_value, as2_m_timestamp_utc_ms
                            from activity_moment
                            where as2_m_activity_id = ''' + str(id) + '''
                        ''')
            moment_rows = cursor.fetchall()
            usageentries_t = len(moment_rows)
            if usageentries_t > 0:
                for m_row in moment_rows:
                    time = m_row[2]
                    # convert ms to date
                    time = datetime.datetime.utcfromtimestamp(time / 1000.0).strftime('%H:%M:%S')
                    time = str(time)
                    if m_row[0] == 'halt':
                        if m_row[1] == 'auto_pause' or m_row[1] == 'pause':
                            timelineArray.append({'time': time, 'text': 'Run paused', 'type': 'fas fa-solid fa-stop'})
                        elif m_row[1] == 'auto_resume' or m_row[1] == 'resume':
                            timelineArray.append({'time': time, 'text': 'Run resumed', 'type': 'fas fa-solid fa-play'})
                    elif m_row[0] == 'split_km' or m_row[0] == 'lap':
                        timelineArray.append(
                            {'time': time, 'text': 'Split KM - ' + str(m_row[1]), 'type': 'fas fa-solid fa-flag'})
                    elif m_row[0] == 'split_mile':
                        timelineArray.append(
                            {'time': time, 'text': 'Split Mile - ' + str(m_row[1]), 'type': 'fas fa-solid fa-flag'})
                    elif m_row[0] == 'gps_signal':
                        if m_row[1] == 'lost':
                            timelineArray.append({'time': time, 'text': 'GPS signal lost',
                                                  'type': 'fas fa-solid fa-person-circle-question'})
                        elif m_row[1] == 'found':
                            timelineArray.append(
                                {'time': time, 'text': 'GPS signal found', 'type': 'fas fa-solid fa-location-dot'})
            timelineArray.append({'time': end_hour, 'text': 'Run ended', 'type': 'fas fa-solid fa-stopwatch'})
            data_list.append((id, start_time_d, end_time_d, duration,
                              '<button type="button" class="btn btn-light btn-sm" onclick="openTimeline(\'' + str(
                                  id) + '\')">Show Timeline</button>'))
            timelineList.append((id, timelineArray))
        # Added feature to allow the user to sort the data by the selected collumns and with the ID of the table
        tableID = 'nike_activities'
        report.filter_by_date(tableID, 1)

        report.write_artifact_data_table(data_headers, data_list, file_found, table_id=tableID, html_escape=False)
        report.add_section_heading("Timeline Data")
        for timeData in timelineList:
            report.add_timeline(timeData[0], timeData[1])
        report.add_timeline_script()
        report.end_artifact_report()

        tsvname = f'Nike - Activity Moments'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Nike - Activity Moments'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Nike Activities data available')

    db.close()


__artifacts__ = {
    "NikeActivityMoments": (
        "Nike-Run",
        ('*/com.nike.plusgps/databases/com.nike.nrc.room*'),
        get_nike_activMoments)
}
