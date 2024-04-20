__artifacts_v2__ = {
    "HealthMateAccounts": {
        "name": "Health Mate - Accounts",
        "description": "Health Mate Accounts",
        "author": "Marco Neumann {kalinko@be-binary.de})",
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
        "author": "Marco Neumann {kalinko@be-binary.de})",
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
        "author": "Marco Neumann {kalinko@be-binary.de})",
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
        "author": "Marco Neumann {kalinko@be-binary.de})",
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
        "author": "Marco Neumann {kalinko@be-binary.de})",
        "version": "0.0.1",
        "date": "2024-04-20",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-1-users.html",
        "paths": ('*/com.withings.wiscale2/databases/room-healthmate*'),
        "function": "get_healthmate_contacts"
    }
    ,
        "HealthMateMeasurements": {
        "name": "Health Mate - Measurements",
        "description": "Health Mate Measurements",
        "author": "Marco Neumann {kalinko@be-binary.de})",
        "version": "0.0.1",
        "date": "2024-04-20",
        "requirements": "none",
        "category": "Withings Health Mate",
        "notes": "Based on https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-1-users.html",
        "paths": ('*/com.withings.wiscale2/databases/Withings-WiScale*'),
        "function": "get_healthmate_measurements"
    }
}



import datetime

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly


def get_healthmate_accounts(files_found, report_folder, seeker, wrap_text, time_offset):
    logfunc("Processing data for Withings Healthmate App - Accounts")
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
        logfunc(f"Found {usageentries}  Withings Healthmate - Accounts")
        description = f"Existing account in Health Mate App from Withings.\n This decoding is based on the blog post https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-1-users.html"
        report = ArtifactHtmlReport('Withings Healthmate - Accounts')
        report.start_artifact_report(report_folder, 'Withings Healthmate - Accounts', description)
        report.add_script()
        data_headers = ('User ID', 'Last Name', 'First Name', 'Short Name', 'Gender', 'Pronoun', 'Birthdate', 'Fat Method', 'E-mail', 'Creation Date', 'Last Modified Date', 'Body Model')
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

        tsvname = f'Withings HealthMate - Accounts'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Withings HealthMate - Accounts'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Withings HealthMate Account data found!')

    db.close()


def get_healthmate_trackings(files_found, report_folder, seeker, wrap_text, time_offset):
    logfunc("Processing data for Withings Healthmate App - Trackings")
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
        report = ArtifactHtmlReport('Withings Healthmate - Trackings')
        report.start_artifact_report(report_folder, 'Withings Healthmate - Trackings', description)
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

        tsvname = f'Withings HealthMate - Trackings'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Withings HealthMate - Trackings'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Withings HealthMate Trackings data found!')

    db.close()

def get_healthmate_locations(files_found, report_folder, seeker, wrap_text, time_offset):
    logfunc("Processing data for Withings Healthmate App - Locations")
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
        logfunc(f"Found {usageentries}  Withings Healthmate - Locations")
        description = "Existing Location data in Health Mate App from Withings. This decoding is based on the blog post https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-3-heart.html."
        report = ArtifactHtmlReport('Withings Healthmate - Locations')
        report.start_artifact_report(report_folder, 'Withings Healthmate - Locations', description)
        report.add_script()
        data_headers = ('ID', 'User ID', 'Date', 'Speed', 'Horizontal Accuracy', 'Altitude', 'Vertical Accuracy', 'Latitude', 'Longitude')
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

        tsvname = f'Withings HealthMate - Locations'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Withings HealthMate - Locations'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Withings HealthMate Location data found!')

    db.close()

def get_healthmate_messages(files_found, report_folder, seeker, wrap_text, time_offset):
    logfunc("Processing data for Withings Healthmate App - Messages")
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
        logfunc(f"Found {usageentries}  Withings Healthmate - Messages")
        description = "Existing Message data in Health Mate App from Withings. This decoding is based on the blog post https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-1-users.html"
        report = ArtifactHtmlReport('Withings Healthmate - Messages')
        report.start_artifact_report(report_folder, 'Withings Healthmate - Messages', description)
        report.add_script()
        data_headers = ('Message ID', 'Sender ID', 'Receiver ID', 'Date', 'Message', 'Type')
        data_list = []
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
        report.end_artifact_report()

        tsvname = f'Withings HealthMate - Messages'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Withings HealthMate - Messages'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Withings HealthMate Message data found!')

    db.close()

def get_healthmate_contacts(files_found, report_folder, seeker, wrap_text, time_offset):
    logfunc("Processing data for Withings Healthmate App - Contacts")
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
        logfunc(f"Found {usageentries}  Withings Healthmate - Contacts")
        description = "Existing Contacts data in Health Mate App from Withings. This decoding is based on the blog post https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-1-users.html."
        report = ArtifactHtmlReport('Withings Healthmate - Contacts')
        report.start_artifact_report(report_folder, 'Withings Healthmate - Contacts', description)
        report.add_script()
        data_headers = ('ID', 'Date', 'User ID', 'Score', 'First Name', 'Last Name', 'Image URL', 'Modified')
        data_list = []
        for row in all_rows:
            id = row[0]
            date = row[1]
            userid = row[2]
            score = row[3]
            firstname = row[4]
            lastname = row[5]
            imageurl = row[6]
            modified = row[7]
            

            data_list.append((id, date, userid, score, firstname, lastname, imageurl, modified))

        tableID = 'healthmate_contacts'

        report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
        report.end_artifact_report()

        tsvname = f'Withings HealthMate - Contacts'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Withings HealthMate - Contacts'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Withings HealthMate Contacts data found!')

    db.close()

def get_healthmate_measurements(files_found, report_folder, seeker, wrap_text, time_offset):
    logfunc("Processing data for Withings Healthmate App - Measurements")
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
        logfunc(f"Found {usageentries}  Withings Healthmate - Contacts")
        description = "Existing Contacts data in Health Mate App from Withings. This decoding is based on the blog post https://bebinary4n6.blogspot.com/2020/10/app-healthmate-on-android-part-1-users.html."
        report = ArtifactHtmlReport('Withings Healthmate - Contacts')
        report.start_artifact_report(report_folder, 'Withings Healthmate - Contacts', description)
        report.add_script()
        data_headers = ('ID', 'Date', 'User ID', 'Score', 'First Name', 'Last Name', 'Image URL', 'Modified')
        data_list = []
        for row in all_rows:
            id = row[0]
            date = row[1]
            userid = row[2]
            score = row[3]
            firstname = row[4]
            lastname = row[5]
            imageurl = row[6]
            modified = row[7]
            

            data_list.append((id, date, userid, score, firstname, lastname, imageurl, modified))

        tableID = 'healthmate_contacts'

        report.write_artifact_data_table(data_headers, data_list, ','.join(files_found))
        report.end_artifact_report()

        tsvname = f'Withings HealthMate - Contacts'
        tsv(report_folder, data_headers, data_list, tsvname)

        tlactivity = f'Withings HealthMate - Contacts'
        timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('No Withings HealthMate Contacts data found!')

    db.close()