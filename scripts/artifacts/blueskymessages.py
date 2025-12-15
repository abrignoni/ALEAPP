__artifacts_v2__ = {
    "blueskymessages": {
        "name": "Bluesky",
        "description": "Bluesky Messages",
        "author": "Alexis Brignoni",
        "version": "0.0.1",
        "date": "2024-11-19",
        "requirements": "none",
        "category": "Bluesky",
        "notes": "",
        "paths": ('*/xyz.blueskyweb.app/databases/RKStorage*','*/xyz.blueskyweb.app/cache/http-cache/*.*'),
        "function": "get_blueskymessages"
    }
}
import os
import json
import sqlite3
from pathlib import Path 
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc,tsv, is_platform_windows,open_sqlite_db_readonly,convert_ts_human_to_utc,timeline,utf8_in_extended_ascii

def get_blueskymessages(files_found, report_folder, seeker, wrap_text):
    
    actors_data_list = []
    messages_data_list = []
    
    
    for file_found in files_found:
        file_found = str(file_found)
    
        if file_found.endswith('RKStorage'):
            db = open_sqlite_db_readonly(file_found)
            #SQL QUERY TIME!
            cursor = db.cursor()
            cursor.execute('''
            SELECT VALUE 
            from catalystLocalStorage where key = 'BSKY_STORAGE'
            ''')
            
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            
            if usageentries > 0:
                for row in all_rows:
                    localuser = row[0]
                    localuser = json.loads(localuser)
                    createdat = ''
                    displayname = ''
                    avatar = ''
                    viewer = ''
                    labels =''
                    description =''
                    did = (localuser ['session']['accounts'][0]['did'])
                    handle = (localuser ['session']['accounts'][0]['handle'])
                    email = (localuser ['session']['accounts'][0]['email'])
                    source = file_found
                    actortuple = tuple((createdat,did,handle,displayname,avatar,viewer,labels,description,email,source))
                    if actortuple in actors_data_list:
                        pass
                    else:
                        actors_data_list.append((actortuple))
        else:
            try:
                with open(file_found, 'r',encoding='utf-8') as file:
                    data = json.load(file)
                    value = data.get('actors')
                    if value is not None:
                        if len(value) > 0:
                            for items in value:
                                did = (items['did'])
                                handle = (items['handle'])
                                displayname =(items['displayName'])
                                avatar = (items['avatar'])
                                viewer = (items['viewer'])
                                labels = (items['labels'])
                                createdat = (items['createdAt'])
                                createdat = createdat.replace('T',' ')
                                createdat = createdat[:-1]
                                createdat = convert_ts_human_to_utc(createdat)
                                description =''
                                email = ''
                                source = file_found
                                actortuple = tuple((createdat,did,handle,displayname,avatar,viewer,labels,description,email,source))
                                if actortuple in actors_data_list:
                                    pass
                                else:
                                    actors_data_list.append((actortuple))
                        else:
                            pass
                            
                    didentry = data.get('did')
                    if didentry is not None:
                        if len(data) > 1:
                            did = (data['did'])
                            handle = (data['handle'])
                            displayname =(data['displayName'])
                            displayname = utf8_in_extended_ascii(displayname)[1]
                            avatar = (data['avatar'])
                            viewer = (data['viewer'])
                            labels = (data['labels'])
                            createdat = (items['createdAt'])
                            createdat = createdat.replace('T',' ')
                            createdat = createdat[:-1]
                            createdat = convert_ts_human_to_utc(createdat)
                            description = (data['description'])
                            description = utf8_in_extended_ascii(description)[1]
                            email = ''
                            source = file_found
                            actortuple = tuple((createdat,did,handle,displayname,avatar,viewer,labels,description,email,source))
                            if actortuple in actors_data_list:
                                pass
                            else:
                                actors_data_list.append((actortuple))
            except:
                pass
    
    for file_found in files_found:
        file_found = str(file_found)
    
        if file_found.endswith('RKStorage'):
            pass #Do nothing
        else:
            try:
                with open(file_found, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    messages = data.get('messages')
                    if messages is not None:
                        if len(messages) > 0:
                            for message in messages:
                                sentat = (message['sentAt'])
                                sentat = sentat.replace('T',' ')
                                sentat= sentat[:-1]
                                sentat = convert_ts_human_to_utc(sentat)
                                senderid = (message['sender']['did'])
                                messageid = (message['id'])
                                textmessage = (message['text'])
                                textmessage = utf8_in_extended_ascii(textmessage)[1]
                                messageusername = ''
                                actorurl = ''
                                source = file_found
                                for actors in actors_data_list:
                                    
                                    if senderid == actors[1]:
                                        
                                        messageusername = actors[3]
                                        actorurl = actors[2]
                                        break
                                    
                                messagetuple = tuple((sentat,actorurl,messageusername,textmessage,senderid,messageid,source))
                                if messagetuple in messages_data_list:
                                    pass
                                else:
                                    messages_data_list.append(messagetuple)
            except:
                pass
                
    if len(actors_data_list) > 0:
        report = ArtifactHtmlReport('Bluesky Actors')
        report.start_artifact_report(report_folder, f'Bluesky Actors')
        report.add_script()
        data_headers = ('Created At','Did','Handle','Display Name','Avatar','Viewer','Labels','Description','Email','Source')
        report.write_artifact_data_table(data_headers, actors_data_list, 'See report')
        report.end_artifact_report()
        
        tsvname = f'Bluesky Actors'
        tsv(report_folder, data_headers, actors_data_list, tsvname)
        
        tlactivity = f'Bluesky Actors'
        timeline(report_folder, tlactivity, actors_data_list, data_headers)
        
        #add timeline
        
    else:
        logfunc(f'No Bluesky Actors data available')
        
    if len(messages_data_list) > 0:
        report = ArtifactHtmlReport('Bluesky Messages')
        report.start_artifact_report(report_folder, f'Bluesky Messages')
        report.add_script()
        data_headers = ('Timestamp Sent','Actor URL','Username','Message','Sender ID','Message ID','Source')
        report.write_artifact_data_table(data_headers, messages_data_list, 'See report')
        report.end_artifact_report()
        
        tsvname = f'Bluesky Messages'
        tsv(report_folder, data_headers, messages_data_list, tsvname)
        
        tlactivity = f'Bluesky Messages'
        timeline(report_folder, tlactivity, messages_data_list, data_headers)
        
    else:
        logfunc(f'No Bluesky Messages available')

        