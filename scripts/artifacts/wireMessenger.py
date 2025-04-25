__artifacts_v2__ = {
    "Wire User Profile": {
        "name": "Wire User Profile",
        "description": "Parses details about the user profile for Wire Messenger",
        "author": "@cf-eglendye",
        "version": "0.1",
        "date": "2024-04-24",
        "requirements": "None",
        "category": "Wire Messenger",
        "notes": "Tested on: Android 13 Wire v.3.81.35",
        "paths": ('*/com.wire/**'),
        "function": "get_wire_profile"
    },
        "Wire Contacts": {
        "name": "Wire Contacts",
        "description": "Parses user contacts for Wire Messenger",
        "author": "@cf-eglendye",
        "version": "0.1",
        "date": "2024-04-24",
        "requirements": "None",
        "category": "Wire Messenger",
        "notes": "Tested on: Android 13 Wire v.3.81.35",
        "paths": ('*/com.wire/**',),
        "function": "get_wire_contacts"
    },
    "Wire Messages": {
        "name": "Wire Messages",
        "description": "Parses messages and call history for Wire Messenger",
        "author": "@cf-eglendye",
        "version": "0.1",
        "date": "2024-04-24",
        "requirements": "None",
        "category": "Wire Messenger",
        "notes": "Tested on: Android 13 Wire v.3.81.35",
        "paths": ('*/com.wire/**'),
        "function": "get_wire_messages"
    }
}

#get the modules required
import re
import sqlite3
import xml.etree.ElementTree as ET
from os.path import isdir, basename

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, open_sqlite_db_readonly, media_to_html

#wire stores the user id as a uuid in an xml file
#this function checks for the uuid within the preferences file
#then returns it to a variable as a string
def get_user_id(files_found):
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.endswith('com.wire.preferences.xml'):
            tree = ET.parse(file_found)
            root = tree.getroot()
            for elem in root:
                if 'active_account' in str(elem.attrib):
                    user_id = elem.text
                    return user_id
    else:
        logfunc("Unable to locate files required to parse User ID")
        pass

#wire names the database from the user id
#this function checks the files found for the database matching the user id
#it also checks that the user id located is in a uuid format  
def get_user_database(files_found, user_id):
    #create a regular expression for uuids and compile it
    re_uuid = r'[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}$'
    uuid_match = re.compile(re_uuid)
    
    if re.match(uuid_match, user_id):
        for file_found in files_found:
            is_sqlite3 = lambda file_found: open(file_found, 'rb').read(16) == b'SQLite format 3\x00'
            file_found = str(file_found)
            user_id = str(user_id)
            #check if the file found ends with the uuid user id
            if file_found.endswith(user_id):
                #check if the file found is also a sqlite database and is not a directory
                if is_sqlite3 and not isdir(file_found):
                    user_database = file_found
                    #returns a string of the user database so it can then be queried using sqlite3
                    return user_database
                else:
                    logfunc("Located a file ending with the User ID, but it is not an SQLite DB - I'll continue looking!")
                    pass
            else:
                continue
    else:
        logfunc("User ID is not a UUID - decoding not supported!")
        pass

def get_wire_profile(files_found, report_folder, seeker, wrap_text):
    #get the user id and the database of the user
    user_id = get_user_id(files_found)
    user_database = get_user_database(files_found, user_id)
    #create an empty list for the profile data
    profile_data = list()
    
    #connect to the db
    db = open_sqlite_db_readonly(user_database)
    cursor = db.cursor()
    #sqlite query time                
    cursor.execute('''
    SELECT Users._id AS "User ID",
        Users.name AS "Display Name",
        Users.email AS"Email Address",
        Users.phone AS "Phone Number",
        json_extract(data, '$.clients[0].verification') AS "Verification Status",
        json_extract(data, '$.clients[0].label') AS "Verification Device",
        json_extract(data, '$.clients[0].model') AS "Device Model",
        datetime(json_extract(data, '$.clients[0].regTime') / 1000, 'unixepoch') AS "Registration Date / Time",
        Users.picture AS "Profile Picture"
    FROM Users
        LEFT JOIN Clients ON Users._id = Clients._id
        WHERE Users."connection" = "self";
    ''')
    all_rows = cursor.fetchall()
    db.close()
    usage_entries = len(all_rows)
    
    #check if there were any entries in the database
    if usage_entries > 0:
        #iterate through all rows in the database
        for row in all_rows:
            profile_picture = str(row[8])
            found_profile_picture = False
            #iterate through all files located from the regex search
            for file_found in files_found:
                #check if the profile picture name from the sqlite db is in the files located
                if profile_picture in file_found:
                    filename = basename(file_found)
                    thumb = media_to_html(filename,files_found,report_folder)
                    #update the boolean value to ensure that the profile picture gets parsed
                    found_profile_picture = True

            #check if there was a profile picture located    
            if found_profile_picture:
                profile_data.append((row[0],row[1],row[2],row[3],row[4], row[5], row[6], row[7], row[8], thumb))
            else:
                profile_data.append((row[0],row[1],row[2],row[3],row[4], row[5], row[6], row[7], row[8], "No profile picture located"))
                
    else:
        logfunc("No entries in the SQLite database!")
    
    #checks if the profile data variable is populated then writes the data to the report
    if profile_data:
        description = 'Parses details about the user profile for Wire Messenger'
        report = ArtifactHtmlReport('Wire User Profile')
        report.start_artifact_report(report_folder, 'Wire User Profile', description)
        report.add_script()
        data_headers = ('User ID','Display Name','Email Address','Phone Number','Verification Status',
                        'Verification Device','Device Model','Date Registered','Profile Picture Name', 'Profile Picture')
        report.write_artifact_data_table(data_headers, profile_data, user_database, html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'Wire User Profile'
        tsv(report_folder, data_headers, profile_data, tsvname)
    else:
        logfunc("No profile data located!")

def get_wire_contacts(files_found, report_folder, seeker, wrap_text):
    #get the user id and the database of the user
    user_id = get_user_id(files_found)
    user_database = get_user_database(files_found, user_id)
    #create an empty list for the contacts data
    contacts_data = list()
    
    #connect to the db
    db = open_sqlite_db_readonly(user_database)
    cursor = db.cursor()
    #sqlite query time                
    cursor.execute('''
    Select Users._id As "User ID",
        Users.name As "Display Name",
        Users.handle As "Handle",
        Users.connection As "Connection Status",
        DateTime(Users.conn_timestamp / 1000, 'unixepoch') As "Connection Date / Time",
        Users.picture AS "Profile Picture ID"
    From Users
        Where Users.connection != 'self'
    ''')           
    
    all_rows = cursor.fetchall()
    db.close()
    usage_entries = len(all_rows)
    
    #check if there were any entries in the database
    if usage_entries > 0:
        #iterate through all rows in the database
        for row in all_rows:
            
            user_id = row[0]
            display_name = row[1]
            handle_id = row[2]
            conn_status = row[3]
            conn_time = row[4]
            profile_picture = row[5]
            
            contacts_data.append((user_id, display_name, handle_id,
                                  conn_status, conn_time, profile_picture))
    else:
        logfunc("No entries in the SQLite database!")
        
    #checks if the contacts data variable is populated then writes the data to the report
    if contacts_data:
        description = 'Parses details about the user contacts for Wire Messenger'
        report = ArtifactHtmlReport('Wire User Contacts')
        report.start_artifact_report(report_folder, 'Wire User Contacts', description)
        report.add_script()
        data_headers = ('User ID', 'Display Name', 'Handle ID', 'Connection Status', 'Connection Time', 'Profile Picture ID')
        report.write_artifact_data_table(data_headers, contacts_data, user_database, html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'Wire User Contacts'
        tsv(report_folder, data_headers, contacts_data, tsvname)
    else:
        logfunc("No contacts data located!")
        
def get_wire_messages(files_found, report_folder, seeker, wrap_text):
    #get the user id and the database of the user
    user_id = get_user_id(files_found)
    user_database = get_user_database(files_found, user_id)
    #create an empty list for the messages data
    messages_data = list()
    
    #connect to the db
    db = open_sqlite_db_readonly(user_database)
    cursor = db.cursor()
    #sqlite query time

    cursor.execute('''
    SELECT message_id,
    timestamp               
    FROM MsgDeletion;
    ''')
    
    deleted_rows = cursor.fetchall()
    
    if len(deleted_rows) == 0:
        cursor.execute('''
        Select
            datetime(Messages.time / 1000, 'unixepoch'),
            Messages._id AS "Message ID",
            Users.name,
            Messages.msg_type,
            json_extract(Messages.content, '$[0].content') AS "Content",
            CASE Likings."action" WHEN 1 THEN "Liked" END,
            datetime(Likings."timestamp" / 1000, 'unixepoch'),
            Users1.name As "Liked By",
            time(Messages.duration / 1000, 'unixepoch'),
            Assets2.name
        From Messages
            Left Join Users On Users._id = Messages.user_id
            Left Join Likings On Messages._id = Likings.message_id
            Left Join Users Users1 On Likings.user_id = Users1._id
            LEFT JOIN Assets2 ON Messages.asset_id = Assets2._id           
        Order By time;
        ''')
    
    #closing read only db and opening write mode
    #inserting the deleted messages into the Messages table    
    else:
        db.close()
        db = sqlite3.connect(user_database)
        cursor = db.cursor()
        cursor.execute('''
        INSERT INTO Messages (_id, time)
        SELECT message_id, timestamp
        FROM MsgDeletion;         
        ''')

        cursor.execute('''
        UPDATE Messages
        SET msg_type = 'Deleted' WHERE msg_type = '';
        ''')
        
        cursor.execute('''
        Select
            datetime(Messages.time / 1000, 'unixepoch'),
            Messages._id AS "Message ID",
            Users.name,
            Messages.msg_type,
            json_extract(Messages.content, '$[0].content')AS "Content",
            CASE Likings."action" WHEN 1 THEN "Liked" END,
            datetime(Likings."timestamp" / 1000, 'unixepoch'),
            Users1.name As "Liked By",
            time(Messages.duration / 1000, 'unixepoch'),
            Assets2.name
        From Messages
            Left Join Users On Users._id = Messages.user_id
            Left Join Likings On Messages._id = Likings.message_id
            Left Join Users Users1 On Likings.user_id = Users1._id
            LEFT JOIN Assets2 ON Messages.asset_id = Assets2._id           
        Order By time;
        ''')
        
    all_rows = cursor.fetchall()
    db.close()
    usage_entries = len(all_rows)
    
    #check if there were any entries in the database
    if usage_entries > 0:
        #iterate through all rows in the database
        for row in all_rows:
            
            date_time = row[0]
            message_id = row[1]
            user_id = row[2]
            message_type = row[3]
            message_content = row[4]
            reaction = row[5]
            reaction_dt = row[6]
            reacted_by = row[7]
            call_duration = row[8]
            asset_id = row[9]
                
            
            messages_data.append((date_time, message_id, user_id,message_type, message_content,
                                  reaction, reaction_dt, reacted_by, call_duration, asset_id))
    else:
        logfunc("No entries in the SQLite database!")
               
    #checks if the messages data variable is populated then writes the data to the report
    if messages_data:
        description = 'Parses details about the messages for Wire Messenger'
        report = ArtifactHtmlReport('Wire User Messages')
        report.start_artifact_report(report_folder, 'Wire User Messages', description)
        report.add_script()
        data_headers = ('Date / Time Sent', 'Message ID', 'User Name', 'Message Type', 'Message Content', 'Reaction', 'Date / Time Reacted',
                        'Reacted By','Call Duration','Asset ID - Check Path: /data/media/0/Pictures/Wire Images/')
        report.write_artifact_data_table(data_headers, messages_data, user_database, html_escape=False)
        report.end_artifact_report()
        
        tsvname = 'Wire User Contacts'
        tsv(report_folder, data_headers, messages_data, tsvname)
    else:
        logfunc("No message data located!")