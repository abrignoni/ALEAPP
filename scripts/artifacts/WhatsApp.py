import sqlite3
import xmltodict

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, open_sqlite_db_readonly, does_column_exist_in_db, media_to_html

def get_WhatsApp(files_found, report_folder, seeker):

    separator = '/'
    source_file_msg = ''
    source_file_wa = ''
    whatsapp_msgstore_db = ''
    whatsapp_wa_db = ''
    file_found = ''
    for file_found in files_found:

        file_name = str(file_found)
        if file_name.endswith('msgstore.db'):
            whatsapp_msgstore_db = str(file_found)
            source_file_msg = file_found.replace(seeker.data_folder, '')

        if file_name.endswith('wa.db'):
            whatsapp_wa_db = str(file_found)
            source_file_wa = file_found.replace(seeker.data_folder, '')

    db = open_sqlite_db_readonly(whatsapp_wa_db)
    cursor = db.cursor()
    try:
        cursor.execute('''
                     SELECT
                        CASE 
                          WHEN WC.given_name IS NULL 
                               AND WC.family_name IS NULL 
                               AND WC.display_name IS NULL THEN WC.jid 
                          WHEN WC.given_name IS NULL 
                               AND WC.family_name IS NULL THEN WC.display_name 
                          WHEN WC.given_name IS NULL THEN WC.family_name 
                          WHEN WC.family_name IS NULL THEN WC.given_name 
                          ELSE WC.given_name 
                               || " " 
                               || WC.family_name 
                        END name,
                        jid, 
                        CASE 
                          WHEN WC.number IS NULL THEN WC.jid 
                          WHEN WC.number == "" THEN WC.jid 
                          ELSE WC.number 
                        END number 
                      FROM   wa_contacts AS WC
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except sqlite3.Error:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('WhatsApp - Contacts')
        report.start_artifact_report(report_folder, 'WhatsApp - Contacts')
        report.add_script()
        data_headers = ('Name','JID','Number') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1], row[2]))

        report.write_artifact_data_table(data_headers, data_list, file_found)
        report.end_artifact_report()
        
        tsvname = 'WhatsApp - Contacts'
        tsv(report_folder, data_headers, data_list, tsvname, source_file_wa)

    else:
        logfunc('No WhatsApp - Contacts found')

    db.close()

    db = open_sqlite_db_readonly(whatsapp_msgstore_db)
    cursor = db.cursor()
    
    cursor.execute('''attach database "''' + whatsapp_wa_db + '''" as wadb ''')
    
    try:
        cursor.execute('''
        SELECT
        datetime(call_log.timestamp/1000,'unixepoch') AS "Call Start",
        datetime((call_log.timestamp/1000 + call_log.duration),'unixepoch') as "Call End",
        strftime('%H:%M:%S', call_log.duration ,'unixepoch') AS "Call Duration",
        chat.subject AS "Group",
        CASE
        WHEN call_log.from_me=0 THEN "Incoming"
        WHEN call_log.from_me=1 THEN "Outgoing"
        END AS "Call Direction",
        CASE
        WHEN call_log.from_me=1 THEN "Self"
        ELSE wa_contacts.wa_name
        END AS "Caller",
        CASE
        WHEN call_log.from_me=1 THEN ""
        ELSE wa_contacts.jid
        END AS "Caller JID",
        CASE
        WHEN call_log.video_call=0 THEN "Audio"
        WHEN call_log.video_call=1 THEN "Video"
        END AS "Call Type"            
        FROM
        call_log
        LEFT JOIN jid ON jid._id=call_log.jid_row_id
        JOIN wa_contacts ON wa_contacts.jid=jid.raw_string
        LEFT JOIN chat ON chat.jid_row_id=call_log.group_jid_row_id
        ORDER BY "Call Time" ASC
        ''')

        all_rows = cursor.fetchall()
        usageentries = len(all_rows)
    except sqlite3.Error:
        usageentries = 0
        
    if usageentries > 0:
        report = ArtifactHtmlReport('WhatsApp - Call Logs')
        report.start_artifact_report(report_folder, 'WhatsApp - Call Logs')
        report.add_script()
        data_headers = ('Call Start Timestamp','Call End Timestamp','Call Duration','Group Name','Call Direction','Caller','Caller JID','Call Type') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
        data_list = []
        for row in all_rows:
            data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))

        report.write_artifact_data_table(data_headers, data_list, whatsapp_msgstore_db)
        report.end_artifact_report()
        
        tsvname = 'WhatsApp - Call Logs'
        tsv(report_folder, data_headers, data_list, tsvname, whatsapp_msgstore_db)

        tlactivity = 'WhatsApp - Call Logs'
        timeline(report_folder, tlactivity, data_list, data_headers)
        
    else:
        logfunc('No WhatsApp - Call Logs found')
        
    if does_column_exist_in_db(whatsapp_msgstore_db, 'messages', 'data'):
        
        try:
            cursor.execute('''
            SELECT 
            datetime(messages.timestamp/1000,'unixepoch') AS message_timestamp, 
            case messages.received_timestamp
                WHEN 0 THEN ''
                ELSE datetime(messages.received_timestamp/1000,'unixepoch')
            end as received_timestamp,
            messages.key_remote_jid AS id, 
            case 
            when contact_book_w_groups.recipients is null then messages.key_remote_jid
            else contact_book_w_groups.recipients
            end as recipients, 
            case key_from_me
                WHEN 0 THEN "Incoming"
                WHEN 1 THEN "Outgoing"
            end AS direction, 
            messages.data            AS content, 
            case 
                when messages.remote_resource is null then messages.key_remote_jid 
                else messages.remote_resource
            end AS group_sender,
            messages.media_url       AS attachment
            FROM   (SELECT jid, 
            recipients 
            FROM   wadb.wa_contacts AS contacts 
            left join (SELECT gjid, 
            Group_concat(CASE 
            WHEN jid == "" THEN NULL 
            ELSE jid 
            END) AS recipients 
            FROM   group_participants 
            GROUP  BY gjid) AS groups 
            ON contacts.jid = groups.gjid 
            GROUP  BY jid) AS contact_book_w_groups 
            join messages 
            ON messages.key_remote_jid = contact_book_w_groups.jid
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
        except sqlite3.Error:
            usageentries = 0
            
        if usageentries > 0:
            report = ArtifactHtmlReport('WhatsApp - Messages')
            report.start_artifact_report(report_folder, 'WhatsApp - Messages')
            report.add_script()
            data_headers = ('Message Timestamp', 'Received Timestamp','Message ID','Recipients', 'Direction', 'Message', 'Group Sender', 'Attachment') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
                
            report.write_artifact_data_table(data_headers, data_list, file_found)
            report.end_artifact_report()
            
            tsvname = 'WhatsApp - Messages'
            tsv(report_folder, data_headers, data_list, tsvname, source_file_msg)
            
            tlactivity = 'WhatsApp - Messages'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('No WhatsApp - Messages data available')

    #Looks for newly changed column names
    else:
        
        try:
            cursor.execute('''
            SELECT
            CASE
			WHEN message.timestamp = 0 then ''
			ELSE
			datetime(message.timestamp/1000,'unixepoch')
			END AS "Message Time",
            CASE
            WHEN message.received_timestamp = 0 then ''
            ELSE
            datetime(message.received_timestamp/1000,'unixepoch')
            END AS "Time Message Received",
            wa_contacts.wa_name AS "Other Participant WA User Name",
            CASE
            WHEN message.from_me=0 THEN wa_contacts.jid
            ELSE "" 
            END AS "Sending Party JID",
            CASE
            WHEN message.from_me=0 THEN "Incoming"
            WHEN message.from_me=1 THEN "Outgoing"
            END AS "Message Direction",
            CASE
            WHEN message.message_type=0 THEN "Text"
            WHEN message.message_type=1 THEN "Picture"
            WHEN message.message_type=2 THEN "Audio"
            WHEN message.message_type=3 THEN "Video"
            WHEN message.message_type=5 THEN "Static Location"
            WHEN message.message_type=7 THEN "System Message"
            WHEN message.message_type=9 THEN "Document"
            WHEN message.message_type=16 THEN "Live Location"
            ELSE message.message_type
            END AS "Message Type",
            message.text_data AS "Message",
            message_media.file_path AS "Local Path to Media",
            message_media.file_size AS "Media File Size",
            message_location.latitude AS "Shared Latitude/Starting Latitude (Live Location)",
            message_location.longitude AS "Shared Longitude/Starting Longitude (Live Location)",
            message_location.live_location_share_duration AS "Duration Live Location Shared (Seconds)",
            message_location.live_location_final_latitude AS "Final Live Latitude",
            message_location.live_location_final_longitude AS "Final Live Longitude",
            datetime(message_location.live_location_final_timestamp/1000,'unixepoch') AS "Final Location Timestamp"
            FROM
            message
            JOIN chat ON chat._id=message.chat_row_id
            JOIN jid ON jid._id=chat.jid_row_id
            LEFT JOIN message_media ON message_media.message_row_id=message._id
            LEFT JOIN message_location ON message_location.message_row_id=message._id
            JOIN wa_contacts ON wa_contacts.jid=jid.raw_string
            WHERE message.recipient_count=0
            ORDER BY "Message Time" ASC
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
        except sqlite3.Error:
            usageentries = 0
            
        if usageentries > 0:
            report = ArtifactHtmlReport('WhatsApp - One To One Messages')
            report.start_artifact_report(report_folder, 'WhatsApp - One To One Messages')
            report.add_script()
            data_headers = ('Message Timestamp','Received Timestamp','Other Participant WA User Name','Sending Party JID','Message Direction','Message Type','Message','Media','Local Path To Media','Media File Size','Shared Latitude/Starting Latitude (Live Location)','Shared Longitude/Starting Longitude (Live Location)','Duration Live Location Shared (Seconds)','Final Live Latitude','Final Live Longitude','Final Location Timestamp') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
              
                if row[7] is not None:
                    mediaident = row[7].split(separator)[-1]
                    # print(mediaident)
                    media = media_to_html(mediaident, files_found, report_folder)
                else:
                    media = row[7]
                  
                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], media, row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14]))

            report.write_artifact_data_table(data_headers, data_list, whatsapp_msgstore_db, html_no_escape=['Media'])
            report.end_artifact_report()
            
            tsvname = 'WhatsApp - One To One Messages'
            tsv(report_folder, data_headers, data_list, tsvname, whatsapp_msgstore_db)

            tlactivity = 'WhatsApp - One To One Messages'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('No WhatsApp - One To One Messages found')

        try:
            cursor.execute('''
            SELECT
            CASE
			WHEN message.timestamp = 0 then ''
			ELSE
			datetime(message.timestamp/1000,'unixepoch')
			END AS "Message Time",
            CASE
            WHEN message.received_timestamp = 0 then ''
            ELSE
            datetime(message.received_timestamp/1000,'unixepoch')
            END AS "Time Message Received",
            chat.subject AS "Conversation Name",
            CASE
            WHEN message.from_me=1 THEN "Self"
            ELSE
            wa_contacts.wa_name
            END AS "Sending Party",
            CASE
            WHEN message.from_me=0 THEN wa_contacts.jid
            ELSE "" 
            END AS "Sending Party JID",
            CASE
            WHEN message.from_me=0 THEN "Incoming"
            WHEN message.from_me=1 THEN "Outgoing"
            END AS "Message Direction",
            CASE
            WHEN message.message_type=0 THEN "Text"
            WHEN message.message_type=1 THEN "Picture"
            WHEN message.message_type=2 THEN "Audio"
            WHEN message.message_type=3 THEN "Video"
            WHEN message.message_type=5 THEN "Static Location"
            WHEN message.message_type=7 THEN "System Message"
            WHEN message.message_type=9 THEN "Document"
            WHEN message.message_type=16 THEN "Live Location"
            ELSE message.message_type
            END AS "Message Type",
            message.text_data AS "Message",
            message_media.file_path AS "Local Path to Media",
            message_media.file_size AS "Media File Size",
            message_location.latitude AS "Shared Latitude/Starting Latitude (Live Location)",
            message_location.longitude AS "Shared Longitude/Starting Longitude (Live Location)",
            message_location.live_location_share_duration AS "Duration Live Location Shared (Seconds)",
            message_location.live_location_final_latitude AS "Final Live Latitude",
            message_location.live_location_final_longitude AS "Final Live Longitude",
            datetime(message_location.live_location_final_timestamp/1000,'unixepoch') AS "Final Location Timestamp"
            FROM
            message
            JOIN chat ON chat._id=message.chat_row_id
            LEFT JOIN jid ON jid._id=message.sender_jid_row_id
            LEFT JOIN message_media ON message_media.message_row_id=message._id
            LEFT JOIN message_location ON message_location.message_row_id=message._id
            LEFT JOIN wa_contacts ON wa_contacts.jid=jid.raw_string
            WHERE message.recipient_count>=1
            ORDER BY "Message Time" ASC
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
        except sqlite3.Error:
            usageentries = 0
            
        if usageentries > 0:
            report = ArtifactHtmlReport('WhatsApp - Group Messages')
            report.start_artifact_report(report_folder, 'WhatsApp - Group Messages')
            report.add_script()
            data_headers = ('Message Timestamp','Received Timestamp','Conversation Name','Sending Party','Sending Party JID','Message Direction','Message Type','Message','Media','Local Path to Media','Media File Size','Shared Latitude/Starting Latitude (Live Location)','Shared Longitude/Starting Longitude (Live Location)','Duration Live Location Shared (Seconds)','Final Live Latitude','Final Live Longitude','Final Location Timestamp') # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                if row[8] is not None:
                    mediaident = row[8].split(separator)[-1]
                    # print(mediaident)
                    media = media_to_html(mediaident, files_found, report_folder)
                else:
                    media = row[8]

                data_list.append((row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], media, row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15]))

            report.write_artifact_data_table(data_headers, data_list, whatsapp_msgstore_db, html_no_escape=['Media'])
            report.end_artifact_report()
            
            tsvname = 'WhatsApp - Group Messages'
            tsv(report_folder, data_headers, data_list, tsvname, whatsapp_msgstore_db)

            tlactivity = 'WhatsApp - Group Messages'
            timeline(report_folder, tlactivity, data_list, data_headers)
            
        else:
            logfunc('No WhatsApp - Group Messages found')

        try:
            cursor.execute('''
                    SELECT
                    datetime(chat_view.created_timestamp/1000,'unixepoch') AS "Group Creation Time",
                    chat_view.subject AS "Group Name",
                    ( SELECT creator_jid FROM wadb.wa_group_admin_settings WHERE wadb.wa_group_admin_settings.jid = jid.raw_string) AS "Creator JID",
                    ( SELECT wa_name FROM wadb.wa_contacts WHERE wadb.wa_contacts.jid = (SELECT creator_jid FROM wadb.wa_group_admin_settings WHERE wadb.wa_group_admin_settings.jid = jid.raw_string) ) AS "Creator WA User Name",
                    ( SELECT number FROM wadb.wa_contacts WHERE wadb.wa_contacts.jid = (SELECT creator_jid FROM wadb.wa_group_admin_settings WHERE wadb.wa_group_admin_settings.jid = jid.raw_string) ) AS "Creator WA Number"
                    FROM
                    chat_view
					JOIN jid ON jid._id = chat_view.jid_row_id
                    LEFT JOIN wa_group_admin_settings ON wa_group_admin_settings.jid=chat_view.jid_row_id
                    LEFT JOIN wa_contacts ON wa_contacts.jid=jid.raw_string
					WHERE "Group Name" NOT NULL
                    ORDER BY "Group Creation Time" ASC
                    ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
        except sqlite3.Error:
            usageentries = 0

        if usageentries > 0:
            report = ArtifactHtmlReport('WhatsApp - Group Details')
            report.start_artifact_report(report_folder, 'WhatsApp - Group Details')
            report.add_script()
            data_headers = ('Group Creation Timestamp', 'Group Name', 'Creator JID',
                            'Creator WA User Name', 'Creator WA Number', 'Creator WA Profile Picture', )  # Don't remove the comma, that is required to make this a tuple as there is only 1 element
            data_list = []
            for row in all_rows:
                media = ''
                profile_picture = ''
                if row[4] is not None:
                    profile_picture = row[4]
                    if len(profile_picture) > 0:
                        if profile_picture.startswith("+"):
                            profile_picture = profile_picture[1:]
                        profile_picture += ".jpg"
                        media = media_to_html(profile_picture, files_found, report_folder)

                data_list.append((row[0], row[1], row[2], row[3], row[4], media))

            report.write_artifact_data_table(data_headers, data_list, whatsapp_msgstore_db, whatsapp_wa_db, html_no_escape=['Creator WA Profile Picture'])
            report.end_artifact_report()

            tsvname = 'WhatsApp - Group Details'
            tsv(report_folder, data_headers, data_list, tsvname, whatsapp_msgstore_db)

            tlactivity = 'WhatsApp - Group Details'
            timeline(report_folder, tlactivity, data_list, data_headers)

        else:
            logfunc('No WhatsApp - Group Details found')
    
    file_source = []
    data = {
        'push_name': None,
        'my_current_status': None,
        'version': None,
        'ph': None,
        'cc': None,
    }
    for file_found in files_found:
        if('com.whatsapp_preferences_light.xml' in file_found or 'startup_prefs.xml' in file_found):
            with open(file_found, encoding='utf-8') as fd:
                xml_dict = xmltodict.parse(fd.read())
                string_dict = xml_dict.get('map','').get('string','')
                file_source.append(file_found)
                for i in range(len(string_dict)):
                    if(string_dict[i]['@name'] == 'push_name' and data['push_name'] is None):                           # User Profile Name
                        data['push_name'] = string_dict[i]['#text']
                    if(string_dict[i]['@name'] == 'my_current_status' and data['my_current_status'] is None):           # User Current Status
                        data['my_current_status'] = string_dict[i]['#text']
                    if(string_dict[i]['@name'] == 'version' and data['version'] is None):                               # User current whatsapp version
                        data['version'] = string_dict[i]['#text']
                    if(string_dict[i]['@name'] == 'ph' and data['ph'] is None):                                         # User Mobile Number
                        data['ph'] = string_dict[i]['#text']
                    if(string_dict[i]['@name'] == 'cc' and data['cc'] is None):                                         # User country code
                        data['cc'] = string_dict[i]['#text']

                if(all(value is not None for value in data.values())):
                    report = ArtifactHtmlReport('WhatsApp - User Profile')
                    report.start_artifact_report(report_folder,'WhatsApp - User Profile')
                    report.add_script()
                    data_headers = ('Version', 'Name', 'User Status', 'Country Code', 'Mobile Number')
                    data_list = []
                    data_list.append((data['version'], data['push_name'], data['my_current_status'], data['cc'], data['ph']))
                    report.write_artifact_data_table(data_headers, data_list, ', '.join(file_source), html_escape=False)
                    report.end_artifact_report()

                    tsvname = "WhatsApp - User Profile"
                    tsv(report_folder, data_headers, data_list,tsvname)

                else:
                    logfunc("No WhatsApp - Profile data found")



__artifacts__ = {
    "WhatsApp": (
        "WhatsApp",
        ('*com.whatsapp*', '*/com.whatsapp/databases/*.db*','*/com.whatsapp/shared_prefs/com.whatsapp_preferences_light.xml','*/com.whatsapp/shared_prefs/startup_prefs.xml','*/com.whatsapp/shared_prefs/reg_prefs.xml','*/WhatsApp Images/*.*','*/WhatsApp Video/*.*'),
        get_WhatsApp)
}
