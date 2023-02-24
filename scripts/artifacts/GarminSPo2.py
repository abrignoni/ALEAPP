# Get Information related to Garmin Pulse Ox from acclimation_pulse_ox_details table and generate a chart
# Author: Fabian Nunes {fabiannunes12@gmail.com}
# Date: 2023-02-24
# Version: 1.0
# Requirements: Python 3.7 or higher

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_garmin_spo2(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Garmin Pulse Ox details")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)

    # Get the data from the database whre the spo2 is not null
    cursor = db.cursor()
    cursor.execute('''
        SELECT 
        userProfilePk, 
        startTimestampGMT, 
        endTimestampGMT, 
        spo2Value, 
        spo2ValueAverage, 
        spo2ValuesArray,
        datetime("date"/1000, 'unixepoch'),
        date
        from acclimation_pulse_ox_details
        where spo2Value is not null
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f'Found {usageentries} Garmin Pulse Ox details')
        report = ArtifactHtmlReport('Garmin - SPO2')
        report.start_artifact_report(report_folder, 'Garmin - SPO2')
        report.add_script()
        data_headers = (
        'User Profile PK', 'Start Timestamp GMT', 'End Timestamp GMT', 'SPO2 Value Average', 'SPO2 Values Array')
        data_list = []
        imgs = []
        i = 0
        x_list = []
        y_list = []
        spo2Avg = []
        date = []

        for row in all_rows:
            # spo2ValuesArray
            spo2Array = row[5]
            # turn spo2ValuesArray into a list in the form of '[1669075200000', '96]'
            spo2Array = spo2Array[1:-1].split('],[')
            # remove [ from the first element
            spo2Array[0] = spo2Array[0][1:]
            # remove ] from the last element
            spo2Array[-1] = spo2Array[-1][:-1]
            # split each element in the list into a list of two elements
            spo2Array = [x.split(',') for x in spo2Array]
            # convert the first element of each list to a datetime object
            spo2Array = [[int(x[0]), int(x[1])] for x in spo2Array]
            # convert the second element of each list to an integer
            spo2Array = [[x[0], int(x[1])] for x in spo2Array]
            # convert the datetime object to a timestamp
            #spo2Array = [[x[0].strftime('%Y-%m-%d %H:%M:%S'), x[1]] for x in spo2Array]

            # Get the values from array and add them to x and y lists
            for x in spo2Array:
                #convert x[0] to a timestamp
                time = int(x[0])
                x_list.append(time)
                y_list.append(x[1])

            spo2Average = row[4]
            if spo2Average is None:
                spo2Average = row[3]
            spo2Avg.append(spo2Average)
            # only get the date from the timestamp
            date.append(row[6].split(' ')[0])

            data_list.append((row[0], row[1], row[2], spo2Average,
                              '<button class="btn btn-light btn-sm" onclick="createLineChart(\'' + str(y_list) + '\', \'' + str(x_list) + '\', true, \'Spo2 Variation\', \'Time\', \'Spo2%\')">View</button>'))
            i += 1

        # Create bar chart with SPO2 average per day
        #plt.bar(date, spo2Avg)
        #plt.xticks(rotation=90)
        #plt.title('SPO2 Average')
        #plt.xlabel('Time')
        #plt.ylabel('SPO2 Average')
        # show number on top of each bar center
        #for i, v in enumerate(spo2Avg):
            #plt.text(i, v, str(v), color='blue', fontweight='bold', horizontalalignment='center')
        #imgName = "spo2Avg"+ str(time.time()) +".png"
        #plt.savefig(report_folder + "\\" + imgName)
        #plt.close()

        # add /Garmin/ to the beginning of imageName
        #imgName = "Garmin-Cache/" + imgName

        # Add graph to the report
        table_id = "spo2"
        report.filter_by_date(table_id, 1)
        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False, table_id=table_id)
        # Add image to the report
        report.add_chart()
        # report.add_image_file(imgName, imgName, "Garmin SPO2 Average", secondImage=True)
        report.end_artifact_report()

        tsvname = f'SPO2'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'SPO2'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Garmin SPO2 data available')

    db.close()


__artifacts__ = {
    "GarminSPO2": (
        "Garmin-Cache",
        ('*/com.garmin.android.apps.connectmobile/databases/cache-database*'),
        get_garmin_spo2)
}
