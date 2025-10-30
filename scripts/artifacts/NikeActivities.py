# Get Information relative to the user activities that are present in the database (com.nike.nrc.room) from the Nike Run app
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-03-18
# Version: 1.0
# Requirements: Python 3.7 or higher and json
import datetime
import json

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_nike_activities(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Garmin Activities")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)

    cursor = db.cursor()
    cursor.execute('''
    Select *
    from activity;
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries} Nike Activities")
        report = ArtifactHtmlReport('Nike - Activities')
        report.start_artifact_report(report_folder, 'Nike - Activities')
        report.add_script()
        data_headers = ('Activity ID', 'Name', 'Start Time UTC', 'End Time UTC', 'Location', 'Source', 'Version', 'Temperature', 'Weather', 'Duration', 'Calories', 'Max Speed', 'Mean Speed', 'Steps', 'Distance', 'Pace', 'Cadence')
        data_list = []
        activity_date = ''
        activity_json = []
        for row in all_rows:
            # If the second column of the row is not null, then the row is from the "activity_summaries" table, the data is then parsed from the json column
            id = row[0]
            source = row[2]
            start_time_utc = row[3]
            # convert ms to date
            start_time_utc = datetime.datetime.utcfromtimestamp(start_time_utc / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
            end_time_utc = row[4]
            # convert ms to date
            end_time_utc = datetime.datetime.utcfromtimestamp(end_time_utc / 1000.0).strftime('%Y-%m-%d %H:%M:%S')
            duration = row[5]
            # convert ms to minutes
            duration = duration / 60000
            # round to 2 decimals
            duration = round(duration, 2)
            name = None
            location = None
            version = None
            temperature = None
            weather = None
            calories = None
            max_speed = None
            mean_speed = None
            steps = None
            distance = None
            pace = None
            cadence = None

            cursor.execute('''
                Select *
                from activity_tag
                where as2_t_activity_id = ''' + str(id) + '''
            ''')
            tag_rows = cursor.fetchall()
            usageentries_t = len(tag_rows)
            if usageentries_t > 0:
                for t_row in tag_rows:
                    activity_id = t_row[1]
                    if activity_id == id:
                        if t_row[2] == 'com.nike.name':
                            name = t_row[3]
                        elif t_row[2] == 'location':
                            location = t_row[3]
                        elif t_row[2] == 'com.nike.running.recordingappversion':
                            version = t_row[3]
                        elif t_row[2] == 'com.nike.temperature':
                            temperature = t_row[3]
                        elif t_row[2] == 'com.nike.weather':
                            weather = t_row[3]

                cursor.execute('''
                                Select *
                                from activity_summary
                                where as2_s_activity_id = ''' + str(id) + '''
                            ''')
                sum_rows = cursor.fetchall()
                usageentries_s = len(sum_rows)
                if usageentries_s > 0:
                    for row_s in sum_rows:
                        activity_id = row_s[1]
                        if activity_id == id:
                            if row_s[3] == 'calories':
                                calories = row_s[6]
                                # round to 2 decimals
                                calories = round(calories, 2)
                            elif row_s[3] == 'speed':
                                if row_s[5] == 'max':
                                    max_speed = row_s[6]
                                    # round to 2 decimals
                                    max_speed = round(max_speed, 2)
                                elif row_s[5] == 'mean':
                                    mean_speed = row_s[6]
                                    # round to 2 decimals
                                    mean_speed = round(mean_speed, 2)
                            elif row_s[3] == 'steps':
                                steps = row_s[6]
                            elif row_s[3] == 'distance':
                                distance = row_s[6]
                                # round to 2 decimals
                                distance = round(distance, 2)
                            elif row_s[3] == 'pace':
                                pace = row_s[6]
                                # round to 2 decimals
                                pace = round(pace, 2)
                            elif row_s[3] == 'cadence':
                                cadence = row_s[6]
                                # round to 2 decimals
                                cadence = round(cadence, 2)


            # extract date from startTimeGMT
            current_date = start_time_utc
            if current_date != activity_date:
                activity_json.append({
                    'date': current_date,
                    'total': 1,
                })
                activity_date = current_date
            else:
                # Change the total of the last element of the list
                activity_json[-1]['total'] += 1

            data_list.append((id, name, start_time_utc, end_time_utc, location, source, version, temperature, weather, duration, calories, max_speed, mean_speed, steps, distance, pace, cadence))
        # Added feature to allow the user to sort the data by the selected collumns and with the ID of the table
        tableID = 'nike_activities'
        report.add_heat_map(json.dumps(activity_json))
        report.filter_by_date(tableID, 1)

        report.write_artifact_data_table(data_headers, data_list, file_found, table_id=tableID)
        report.end_artifact_report()

        tsvname = f'Nike - Activities'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Nike - Activities'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Nike Activities data available')

    db.close()


__artifacts__ = {
    "NikeActivities": (
        "Nike-Run",
        ('*/com.nike.plusgps/databases/com.nike.nrc.room*'),
        get_nike_activities)
}