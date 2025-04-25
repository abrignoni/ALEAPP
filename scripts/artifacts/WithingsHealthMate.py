# Withings Health Mate App (com.withings.wiscale2)
# Author:  Marco Neumann (kalinko@be-binary.de)
# Version: 0.0.2
# 
# Tested with the following versions:
# 2020-10-09: Android 6, App: 5.1.4
# 2024-04-20: Android 13, App: 6.3.1

# Requirements:  datetime




__artifacts_v2__ = {

    
    "HealthMateAccounts": {
        "name": "Health Mate - Accounts",
        "description": "Health Mate Accounts",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "date": "2024-04-20",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-1-users.html",
        "paths": ('*/com.withings.wiscale2/databases/Withings-WiScale*'),
        "function": "get_healthmate_accounts"
    },
    "HealthMateTrackings": {
        "name": "Health Mate - Trackings",
        "description": "Health Mate Trackings",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "date": "2024-04-20",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-2.html",
        "paths": ('*/com.withings.wiscale2/databases/room-healthmate*','*/com.withings.wiscale2/databases/Withings-WiScale*'),
        "function": "get_healthmate_trackings"
    },
    "HealthMateLocations": {
        "name": "Health Mate - Locations",
        "description": "Health Mate Locations",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "date": "2024-04-20",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-3-heart.html",
        "paths": ('*/com.withings.wiscale2/databases/room-healthmate*'),
        "function": "get_healthmate_locations"
    },
    "HealthMateMessages": {
        "name": "Health Mate - Messages",
        "description": "Health Mate Messages",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "date": "2024-04-20",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-1-users.html",
        "paths": ('*/com.withings.wiscale2/databases/Withings-WiScale*'),
        "function": "get_healthmate_messages"
    },
    "HealthMateContacts": {
        "name": "Health Mate - Contacts",
        "description": "Health Mate Contacts",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "date": "2024-04-20",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-1-users.html",
        "paths": ('*/com.withings.wiscale2/databases/room-healthmate*'),
        "function": "get_healthmate_contacts"
    },
    "HealthMateMeasurements": {
        "name": "Health Mate - Measurements",
        "description": "Health Mate Measurements",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.2",
        "date": "2024-04-21",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-3-heart.html",
        "paths": ('*/com.withings.wiscale2/databases/Withings-WiScale*'),
        "function": "get_healthmate_measurements"
    },
    "HealthMateDevices": {
        "name": "Health Mate - Devices",
        "description": "Health Mate Devices",
        "author": "Marco Neumann {kalinko@be-binary.de}",
        "version": "0.0.1",
        "date": "2024-04-21",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-1-users.html",
        "paths": ('*/com.withings.wiscale2/databases/Withings-WiScale*'),
        "function": "get_healthmate_devices"
    }
}



import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_healthmate_accounts(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Withings Health Mate App - Accounts")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    Select *
    from users;
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries}  Withings Health Mate - Accounts")
        description = f"Existing account in Health Mate App from Withings.\n This decoding is based on the blog post https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-1-users.html"
        report = ArtifactHtmlReport('Withings Health Mate - Accounts')
        report.start_artifact_report(report_folder, 'Withings Health Mate - Accounts', description)
        report.add_script()
        data_headers = ('User ID', 'Last Name', 'First Name', 'Short Name', 'Gender', 'Pronoun', 'Birthdate', 'Fat Method', 'E-mail', 'Creation Timestamp', 'Last Modified Timestamp', 'Body Model')
        data_list = []
        for row in all_rows:
            id = row[0]
            lastname = row[4]
            firstname = row[3]
            shortname = row[5]
            gender = row[6]
            pronoun = row[8]
            birthdate = datetime.datetime.fromtimestamp(row[9]/1000).strftime('%Y-%m-%d %H:%M:%S')
            fatmethod = row[10]
            email = row[11]
            creationdate = datetime.datetime.fromtimestamp(row[18]/1000).strftime('%Y-%m-%d %H:%M:%S')
            modifieddate = datetime.datetime.fromtimestamp(row[19]/1000).strftime('%Y-%m-%d %H:%M:%S')
            bodymodel = row[25]

            data_list.append((id, lastname, firstname, shortname, gender, pronoun, birthdate, fatmethod, email, creationdate, modifieddate, bodymodel))

        tableID = 'healthmate_accounts'

        report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
        report.end_artifact_report()

        tsvname = f'Withings Health Mate - Accounts'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Withings Health Mate - Accounts'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Withings Health Mate Account data found!')

    db.close()


def get_healthmate_trackings(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Withings Health Mate App - Trackings")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    # get activity categories from database Whithings-WiScale
    db = open_sqlite_db_readonly(str(files_found[1]))
    cursor = db.cursor()
    cursor.execute('''
    select id, name
    from activityCategory
    ''')
    all_categories = cursor.fetchall()
    category_entries = len(all_categories)
    activity_categories = {}
    if category_entries > 0:
        logfunc(f"Activity Categories for Withings Health Mate Trackings found")
        for category in all_categories:
            activity_categories[category[0]] = category[1]
            # add activity categories that are not part of the listing but were recognizable by manual analysis
        activity_categories[37] = 'Sleeping'
        activity_categories[272] = 'Activity Tracking started manually'
    else:
        logfunc(f"No Activity Categories for Withings Health Mate Trackings found")
    db.close()

    # get activities from database room-healthmate*
    db = open_sqlite_db_readonly(str(files_found[0]))
    cursor = db.cursor()
    cursor.execute('''
    Select *
    from Track;
    ''')
    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries}  Withings Health Mate - Trackings")
        description = f"Automatically and manually tracked Activities by Withings Devices connected to Health Mate App.\n This decoding is based on the blog post https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-2.html"
        report = ArtifactHtmlReport('Withings Health Mate - Trackings')
        report.start_artifact_report(report_folder, 'Withings Health Mate - Trackings', description)
        report.add_script()
        data_headers = ('ID', 'wsId', 'UserID', 'Start Time','End Time', 'Modified Time','Activity Category ID','Activity Category Name','Tracking Data')
        data_list = []
        for row in all_rows:
            id = row[0]
            wsid = row[1]
            userid = row[2]
            starttime = datetime.datetime.fromtimestamp(row[3]/1000).strftime('%Y-%m-%d %H:%M:%S')
            endtime = datetime.datetime.fromtimestamp(row[4]/1000).strftime('%Y-%m-%d %H:%M:%S')
            modifiedtime = datetime.datetime.fromtimestamp(row[7]/1000).strftime('%Y-%m-%d %H:%M:%S')
            devicetype = row[10]
            category_id = row[12]
            try:
                category_name = activity_categories[category_id]
            except:
                category_name = "Not listed - Unknown"
            datajson = row[13]

            data_list.append((id, wsid, userid, starttime, endtime, modifiedtime, category_id, category_name, datajson))

        tableID = 'healthmate_trackings'
 

        report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
        report.end_artifact_report()

        tsvname = f'Withings Health Mate - Trackings'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Withings Health Mate - Trackings'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Withings Health Mate Trackings data found!')

    db.close()

def get_healthmate_locations(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Withings Health Mate App - Locations")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    Select *
    from WorkoutLocation;
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries}  Withings Health Mate - Locations")
        description = "Existing Location data in Health Mate App from Withings. This decoding is based on the blog post https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-3-heart.html."
        report = ArtifactHtmlReport('Withings Health Mate - Locations')
        report.start_artifact_report(report_folder, 'Withings Health Mate - Locations', description)
        report.add_script()
        data_headers = ('ID', 'User ID', 'Timestamp', 'Speed', 'Horizontal Accuracy', 'Altitude', 'Vertical Accuracy', 'Latitude', 'Longitude')
        data_list = []
        for row in all_rows:
            id = row[0]
            userid = row[1]
            date = datetime.datetime.fromtimestamp(row[2]/1000).strftime('%Y-%m-%d %H:%M:%S')
            speed = row[3]
            h_accuracy = row[4]
            altitude = row[5]
            v_accuracy = row[6]
            lat = row[7]
            lon = row[8]            

            data_list.append((id, userid, date, speed, h_accuracy, altitude, v_accuracy, lat, lon))

        tableID = 'healthmate_locations'

        report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
        report.end_artifact_report()

        tsvname = f'Withings Health Mate - Locations'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Withings Health Mate - Locations'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Withings Health Mate Location data found!')

    db.close()

def get_healthmate_messages(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Withings Health Mate App - Messages")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    Select *
    from chat;
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries}  Withings Health Mate - Messages")
        description = "Existing Message data in Health Mate App from Withings. This decoding is based on the blog post https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-1-users.html"
        report = ArtifactHtmlReport('Withings Health Mate - Messages')
        report.start_artifact_report(report_folder, 'Withings Health Mate - Messages', description)
        report.add_script()
        data_headers = ('Message ID', 'Sender ID', 'Receiver ID', 'Timestamp', 'Message', 'Type')
        data_list = []
        #message_list = []
        for row in all_rows:
            id = row[0]
            senderid = row[1]
            receiverid = row[2]
            date = datetime.datetime.fromtimestamp(row[3]/1000).strftime('%Y-%m-%d %H:%M:%S')
            message = row[4]
            message_type = row[6]
            

            data_list.append((id, senderid, receiverid, date, message, message_type))

        tableID = 'healthmate_messages'

        
        report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
        #report.add_chat()
        report.end_artifact_report()

        tsvname = f'Withings Health Mate - Messages'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Withings Health Mate - Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Withings Health Mate Message data found!')

    db.close()

def get_healthmate_contacts(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Withings Health Mate App - Contacts")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    Select *
    from leaderboard;
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries}  Withings Health Mate - Contacts")
        description = "Existing Contacts data in Health Mate App from Withings. This decoding is based on the blog post https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-1-users.html."
        report = ArtifactHtmlReport('Withings Health Mate - Contacts')
        report.start_artifact_report(report_folder, 'Withings Health Mate - Contacts', description)
        report.add_script()
        data_headers = ('ID', 'Date', 'User ID', 'Score', 'First Name', 'Last Name', 'Image URL', 'Modified Timestamp')
        data_list = []
        for row in all_rows:
            id = row[0]
            date = row[1]
            userid = row[2]
            score = row[3]
            firstname = row[4]
            lastname = row[5]
            imageurl = row[6]
            modified = datetime.datetime.fromtimestamp(row[7]/1000).strftime('%Y-%m-%d %H:%M:%S')
            

            data_list.append((id, date, userid, score, firstname, lastname, imageurl, modified))

        tableID = 'healthmate_contacts'

        report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
        report.end_artifact_report()

        tsvname = f'Withings Health Mate - Contacts'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Withings Health Mate - Contacts'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Withings Health Mate Contacts data found!')

    db.close()

def get_healthmate_measurements(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Withings Health Mate App - Measurements")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    Select *
    from vasistas;
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries}  Withings Health Mate - Measurements")
        description = "Existing Measurements data in Health Mate App from Withings. This decoding is based on the blog post https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-1-users.html."
        report = ArtifactHtmlReport('Withings Healthmate - Measurements')
        report.start_artifact_report(report_folder, 'Withings Health Mate - Measurements', description)
        report.add_script()
        data_headers = ('ID', 'Category ID', 'Category', 'Timestamp', 'User ID', 'Duration', 'Steps', 'Distance', 'Ascent', 'Descent', 'Heartrate', 'SPO2', 'SPO2 Quality', 'Swim Laps', 'Swim Movements', 'Core Temperature')
        data_list = []
        for row in all_rows:
            id = row[0]
            category_id = row[24]
            match category_id:
                case -22:
                    category = 'Core Temperature'
                case -19:
                    category = 'SPO2'
                case -16:
                    category = 'Heart Rate'
                case 16:
                    category = 'Steps'
                case _:
                    category = 'Unknown Category ID'
            timestamp = datetime.datetime.fromtimestamp(row[4]/1000).strftime('%Y-%m-%d %H:%M:%S')
            userid = row[1]
            duration = row[5]
            steps = row[11]
            distance = row[12]
            ascent = row[13]
            descent = row[14]
            heartrate =row[18]
            spo2 = row[32]
            spo2_quality = row[33]
            swim_laps = row[23]
            swim_movements = row[22]
            temperature = row[42]
            

            data_list.append((id, category_id, category, timestamp, userid, duration, steps, distance, ascent, descent, heartrate, spo2, spo2_quality, swim_laps, swim_movements, temperature))

        tableID = 'healthmate_measurements'

        report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
        report.end_artifact_report()

        tsvname = f'Withings Health Mate - Measurements'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Withings Health Mate - Measurements'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Withings Health Mate Measurements data found!')

    db.close()

def get_healthmate_devices(files_found, report_folder, seeker, wrap_text):
    logfunc("Processing data for Withings Health Mate App - Devices")
    files_found = [x for x in files_found if not x.endswith('wal') and not x.endswith('shm')]
    
    file_found = str(files_found[0])
    db = open_sqlite_db_readonly(file_found)
    cursor = db.cursor()
    cursor.execute('''
    Select *
    from devices;
    ''')

    all_rows = cursor.fetchall()
    usageentries = len(all_rows)
    if usageentries > 0:
        logfunc(f"Found {usageentries}  Withings Health Mate - Devices")
        description = "Existing Devices data in Health Mate App from Withings. This decoding is based on the blog post https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-1-users.html."
        report = ArtifactHtmlReport('Withings Health Mate - Devices')
        report.start_artifact_report(report_folder, 'Withings Health Mate - Devices', description)
        report.add_script()
        data_headers = ('ID', 'User ID', 'Association Timestamp', 'Last Used Timestamp', 'Modified Timestamp', 'MAC', 'Firmware', 'Latitude', 'Longitude', 'Device Type', 'Device Model')
        data_list = []
        for row in all_rows:
            id = row[0]
            userid = row[1]
            assdate = datetime.datetime.fromtimestamp(row[2]/1000).strftime('%Y-%m-%d %H:%M:%S')
            lastdate = datetime.datetime.fromtimestamp(row[3]/1000).strftime('%Y-%m-%d %H:%M:%S')
            moddate = datetime.datetime.fromtimestamp(row[4]/1000).strftime('%Y-%m-%d %H:%M:%S')
            mac = row[5]
            firmware = row[6]
            lat = row[8]
            lon = row[9]  
            dev_type = row[14]  
            dev_modell = row[15]      

            data_list.append((id, userid, assdate, lastdate, moddate, mac, firmware, lat, lon, dev_type, dev_modell))

        tableID = 'healthmate_devices'

        report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
        report.end_artifact_report()

        tsvname = f'Withings Health Mate - Devices'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Withings Health Mate - Devices'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Withings Health Mate Devices data found!')

    db.close()