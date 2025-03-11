__artifacts_v2__ = {
    "chatgpt": {
        "name": "ChatGPT",
        "description": "Get user's ChatGPT conversations, settings and media files. This parser is based on a research project. Parser is validated up to the app's 1.2024.177 version",
        "author": "Evangelos Dragonas (@theAtropos4n6)",
        "version": "1.0.2",
        "date": "2024-07-09",
        "requirements": "",
        "category": "ChatGPT",
        "paths": (
            '**/com.openai.chatgpt/databases/*.*',
            '**/com.openai.chatgpt/files/datastore/*.*',
            '**/com.openai.chatgpt/shared_prefs/*',
            '**/com.openai.chatgpt/cache/files/*',
        ),
        "function": "get_chatgpt"
    }
}

import xml.etree.ElementTree as ET
from datetime import *
import os
import blackboxprotobuf
import json
from pathlib import Path
from PIL import Image

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, is_platform_windows, timeline, open_sqlite_db_readonly, media_to_html,convert_utc_human_to_timezone

def is_image(file_path):
    try:
        with Image.open(file_path) as img:
            return True
    except IOError:
        return False

def get_chatgpt(files_found, report_folder, seeker, wrap_text):
    counter=1
    for file_found in files_found:
        file_found = str(file_found)
        file_name = os.path.basename(file_found)
        if file_name.endswith('_conversations.db'):
            db = open_sqlite_db_readonly(file_found)
            cursor = db.cursor()
            #Conversations Metadata
            cursor.execute('''
                    select 
                        id,
                        json_extract(conversation, '$.id') AS id,
                        json_extract(conversation, '$.remote_id') AS remote_id,
                        json_extract(conversation, '$.creation_date') AS creation_date,
                        json_extract(conversation, '$.modification_date') AS modification_date,
                        json_extract(conversation, '$.title') AS title,
                        json_extract(conversation, '$.moderation_results') AS moderation_results,
                        json_extract(conversation, '$.gizmo_id') AS gizmo_id,
                        CASE
                        when json_extract(conversation, '$.has_title') = true then 'Yes' 
                        else 'No'
                        end has_title
                    from DBConversation
                 ''')
            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                description = 'Metadata related to the user conversations'
                report = ArtifactHtmlReport(f"ChatGPT - Conversations Metadata - Account: {file_name[:-17]}") # webpage title
                #multiple accounts.db may exist. counter keeps track of their number
                if counter == 1:
                    report.start_artifact_report(report_folder, f"Conversations Metadata", description) # html + artifact title
                else:
                    report.start_artifact_report(report_folder, f"Conversations Metadata {counter}", description) # html + artifact title
                report.add_script()
                #data_headers = ('Conversation ID','Remote ID','Title','Creation Date','Modification Date','Custom Instructions', 'Model') 
                data_headers = ('Creation Date','Modification Date','Title','Custom Instructions', 'Model','ID','Conversation ID','Remote ID') 
                data_list = []
                for row in all_rows:
                    cdate_without_z = row[3].rstrip('Z')
                    mdate_without_z = row[4].rstrip('Z')
                    cdatetime_obj = datetime.fromisoformat(cdate_without_z).replace(tzinfo=timezone.utc)
                    cdatetime_obj_no_microseconds = cdatetime_obj.replace(microsecond=0)
                    mdatetime_obj = datetime.fromisoformat(mdate_without_z).replace(tzinfo=timezone.utc)
                    mdatetime_obj_no_microseconds = mdatetime_obj.replace(microsecond=0)
                    conv_cdate = convert_utc_human_to_timezone(cdatetime_obj_no_microseconds, 'UTC')
                    conv_mdate = convert_utc_human_to_timezone(mdatetime_obj_no_microseconds, 'UTC')
                    data_list.append((conv_cdate,conv_mdate,row[5],row[6],row[7],row[0],row[1],row[2]))

                report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                report.end_artifact_report()
                
                tsvname = f"ChatGPT - Conversations Metadata - {file_name[:-17]}"
                tsv(report_folder, data_headers, data_list, tsvname)

                tlactivity = f'ChatGPT - Conversations Metadata - {file_name[:-17]}'
                timeline(report_folder, tlactivity, data_list, data_headers)

            else:
                logfunc(f'No ChatGPT - Conversations Metadata available within {file_name}')

            #Conversations 
            cursor.execute('''
                    select 
                        DBMessage.id as message_id,
                        DBMessage.conversationId as conversationId_id,
                        json_extract(DBConversation.conversation, '$.title') AS conversation,
                        json_extract(DBMessage.messageNode, '$.content.role') AS role,
                        json_extract(DBMessage.messageNode, '$.content.content.content') AS content,
                        json_extract(DBMessage.messageNode, '$.content.date') AS date,
                        json_extract(DBMessage.messageNode, '$.content.role_name') AS role_name,
                        json_extract(DBMessage.messageNode, '$.content.attachments') AS attachments,
                        json_extract(DBMessage.messageNode, '$.content.model') AS model,
                        CASE
                            when json_extract(DBMessage.messageNode, '$.content.is_complete') = true then 'Yes' 
                        else 'No'
                            end is_complete,
                        CASE
                            when json_extract(DBMessage.messageNode, '$.content.is_blocked') = true then 'Yes' 
                        else 'No'
                            end is_blocked,
                        CASE
                            when json_extract(DBMessage.messageNode, '$.content.is_flagged') = true then 'Yes' 
                        else 'No'
                            end is_flagged,
                        CASE
                            when json_extract(DBMessage.messageNode, '$.content.is_interrupted') = true then 'Yes' 
                        else 'No'
                            end is_interrupted,
                        CASE
                            when json_extract(DBMessage.messageNode, '$.content.is_user_system_message') = true then 'Yes' 
                        else 'No'
                            end is_user_system_message,
                        CASE
                            when json_extract(DBMessage.messageNode, '$.content.is_voice_message') = true then 'Yes' 
                        else 'No'
                            end is_voice_message
                    from DBMessage
                    join DBConversation on DBMessage.conversationId = DBConversation.id
            ''')

            all_rows = cursor.fetchall()
            usageentries = len(all_rows)
            if usageentries > 0:
                description = f'User:{file_name[:-17]} conversations with ChatGPT'
                report = ArtifactHtmlReport(f"ChatGPT - Conversations - Account: {file_name[:-17]}")
                if counter == 1:
                    report.start_artifact_report(report_folder, f"Conversations", description)
                else:
                    report.start_artifact_report(report_folder, f"Conversations {counter}", description)
                report.add_script()
                data_headers = ('Date','Message ID','Conversation ID','Title','Role','Content','Role Name','Attachments','Model','Complete','Blocked','Flagged','Interrupted','User System Message','Voice Message') 
                data_list = []
                for row in all_rows:
                    #Date sanitization => changing the ISO format of the date to more aleapp friendly format
                    if row[5] is not None and row[5].endswith("Z"):
                        date_without_z = row[5].rstrip('Z')
                        datetime_obj = datetime.fromisoformat(date_without_z).replace(tzinfo=timezone.utc)
                        message_date = convert_utc_human_to_timezone(datetime_obj, 'UTC')
                        data_list.append((message_date,row[0],row[1],row[2],row[3],row[4],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14]))
                    else:
                        data_list.append((row[5],row[0],row[1],row[2],row[3],row[4],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14]))
                report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                report.end_artifact_report()
                
                tsvname = f"ChatGPT - Conversations - {file_name[:-17]}"
                tsv(report_folder, data_headers, data_list, tsvname)
                
            else:
                logfunc(f'No ChatGPT - Conversations data available within {file_name}')
            counter+=1
            db.close()

            #parsing protobuf files
        if file_name.endswith('.preferences_pb'):
            #parse user-ID__user.preferences_pb
            if file_name.endswith("_user.preferences_pb"):
                with open(file_found, 'rb') as file:
                    data = file.read()
                    values, types = blackboxprotobuf.decode_message(data)
                    data_list = []
                    if isinstance(values, dict):
                        try:
                            pb = values.get('1', {}).get('2', {}).get('5', b'{}')
                            info = pb.decode('utf-8')
                            userinfo = json.loads(info)
                            id = userinfo.get('id', None)
                            email = userinfo.get('email', '')
                            name = userinfo.get('name', '')
                            picture = userinfo.get('picture', '')
                            created_timestamp = int(userinfo.get('created', 0))
                            created = datetime.fromtimestamp(created_timestamp, tz=timezone.utc)
                            createdts = convert_utc_human_to_timezone(created, 'UTC')
                            data_list.append((id,email,name,createdts,picture))
                        except:
                            logfunc(f'Error parsing ChatGPT - error occured when parsing {file_name} protobuf')
                        
                    if len(data_list) > 0:
                        description = f'User preferences'
                        report = ArtifactHtmlReport('ChatGPT - User')
                        report.start_artifact_report(report_folder, f'User', description)
                        report.add_script()
                        data_headers = ('User-ID', 'Email','Name','Account Creation Time','Picture')
                        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                        report.end_artifact_report()
                        
                        tsvname = f'ChatGPT - User'
                        tsv(report_folder, data_headers, data_list, tsvname)
                        
                    else:
                        logfunc(f'No ChatGPT - User available')

                            #parse user-ID_accountstatus.preferences_pb
            if file_name.endswith("_accountstatus.preferences_pb"):
                with open(file_found, 'rb') as file:
                    data = file.read()
                    values, types = blackboxprotobuf.decode_message(data)
                    data_list = []
                    if isinstance(values, dict):
                        try:
                            pb = values.get('1', {}).get('2', {}).get('5', b'{}')
                            info = pb.decode('utf-8')
                            accstatus = json.loads(info)
                            if 'accounts' in accstatus:  
                                for k in accstatus['accounts'].keys():
                                    account = accstatus['accounts'][k]
                                    account_id = account.get('account_id', None)
                                    account_user_id = account.get('account_user_id', None)
                                    subscription = account.get('subscription', {})
                                    subscription_plan = subscription.get('plan', '')
                                    plan_type = account.get('plan_type', '')
                                    subscription_purchase_origin = subscription.get('purchase_origin', '')
                                    subscription_will_renew = subscription.get('will_renew', False)
                                    structure = account.get('structure', '')
                                    is_deactivated = account.get('is_deactivated', False)
                                    data_list.append((k,account_id,account_user_id,subscription_plan,plan_type,subscription_purchase_origin,subscription_will_renew,structure,is_deactivated))
                        except:
                            logfunc(f'Error parsing ChatGPT - error occured when parsing {file_name} protobuf')
                        
                    if len(data_list) > 0:
                        description = f'ChatGPT account status prefs'
                        report = ArtifactHtmlReport('ChatGPT - Account Status')
                        report.start_artifact_report(report_folder, f'Account Status', description)
                        report.add_script()
                        data_headers = ('Account','Account-ID', 'Account-User-ID','Subscription Plan','Plan Type','Subscription Purchase Origin','Subscription Will Renew','Structure','Is Deactivated')
                        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                        report.end_artifact_report()
                        
                        tsvname = f'ChatGPT - Account Status'
                        tsv(report_folder, data_headers, data_list, tsvname)
                        
                    else:
                        logfunc(f'No ChatGPT - Account Status available')
            #parse  _accountuser_state protobuf
            if file_name.endswith("_accountuser_state.preferences_pb"):
                with open(file_found, 'rb') as file:
                    data = file.read()
                    values, types = blackboxprotobuf.decode_message(data)
                    data_list = []
                    if isinstance(values, dict):
                        try:
                            pb = values.get('1', {}).get('2', {}).get('5', b'{}')
                            info = pb.decode('utf-8')
                            accuserstate = json.loads(info)
                            active_account_id = accuserstate.get('active_account_id', None)
                            for i in accuserstate.get('available_account_users', []):
                                account = i.get('account', {})
                                user = i.get('user', {})
                                account_id = account.get('account_id', None)
                                user_id = user.get('id', None)
                                account_user_id = account.get('account_user_id', None)
                                email = user.get('email', '')
                                name = user.get('name', '')
                                created = datetime.fromtimestamp(int(user.get('created', 0)), tz=timezone.utc)
                                createdts = convert_utc_human_to_timezone(created, 'UTC')

                                subscription = account.get('subscription', {})
                                subscription_plan = subscription.get('plan', '')
                                plan_type = account.get('plan_type', '')
                                subscription_purchase_origin = subscription.get('purchase_origin', '')
                                subscription_will_renew = subscription.get('will_renew', False)
                                expiration_date = subscription.get('expiration_date', '')
                                structure = account.get('structure', '')
                                is_deactivated = account.get('is_deactivated', False)
                                picture = user.get('picture', '')
                                is_active_account = 'Yes' if active_account_id == account_id else 'No'
                                data_list.append((is_active_account,account_id,user_id,account_user_id,email,name,createdts,subscription_plan,plan_type,subscription_purchase_origin,subscription_will_renew,expiration_date,structure,is_deactivated,picture))
                        except:
                            logfunc(f'Error parsing ChatGPT - error occured when parsing {file_name} protobuf')
                    
                    if len(data_list) > 0:
                        description = f'Account user state preferences'
                        report = ArtifactHtmlReport('ChatGPT - Account User State')
                        report.start_artifact_report(report_folder, f'Account User State', description)
                        report.add_script()
                        data_headers = ('Is Active Account','Account-ID', 'User-ID','Account-User-ID','Email','Name','Account Creation Time','Subscription Plan','Plan Type','Subscription Purchase Origin','Subscription Will Renew','Plan Expiration Date','Structure','Is Deactivated','Picture')
                        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                        report.end_artifact_report()
                        
                        tsvname = f'ChatGPT - Account User State'
                        tsv(report_folder, data_headers, data_list, tsvname)
                        
                    else:
                        logfunc(f'No ChatGPT - Account User State available')
                #parse custom instructions protobuf
            if file_name.endswith("_custom_instructions.preferences_pb"):
                with open(file_found, 'rb') as file:
                    data = file.read()
                    values, types = blackboxprotobuf.decode_message(data)
                    data_list = []
                    if isinstance(values, dict):
                        try:
                            pb = values.get('1', {}).get('2', {}).get('5', b'{}')
                            info = pb.decode('utf-8')
                            custominst = json.loads(info)
                            is_enabled = custominst.get('enabled', False)
                            about_user_message = custominst.get('about_user_message', '')
                            about_model_message = custominst.get('about_model_message', '')
                            data_list.append((is_enabled,about_user_message,about_model_message))
                        except:
                            logfunc(f'Error parsing ChatGPT - error occured when parsing {file_name} protobuf')
                    
                    if len(data_list) > 0:
                        description = f'User provided custom instructions to ChatGPT'
                        report = ArtifactHtmlReport('ChatGPT - Custom Instructions')
                        report.start_artifact_report(report_folder, f'Custom Instructions', description)
                        report.add_script()
                        data_headers = ('Are Enabled','About User Message', 'About Model Message')
                        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                        report.end_artifact_report()
                        
                        tsvname = f'ChatGPT - Custom Instructions'
                        tsv(report_folder, data_headers, data_list, tsvname)
                        
                    else:
                        logfunc(f'No ChatGPT - Custom Instructions available')
                #parse history sync status from user settings protobuf
            if file_name.endswith("_user_settings.preferences_pb"):
                with open(file_found, 'rb') as file:
                    data = file.read()
                    values, types = blackboxprotobuf.decode_message(data)
                    data_list = []
                    if isinstance(values, dict):
                        try:
                            pb = values.get('1', {}).get('2', {}).get('5', b'{}')
                            info = pb.decode('utf-8')
                            usersets = json.loads(info)
                            history_disabled = usersets.get('history_disabled', False)
                            seen_custom_instructions_introduction = usersets.get('seen_custom_instructions_introduction', False) 
                            has_seen_voice_intro = usersets.get('has_seen_voice_intro', False)
                            has_seen_voice_selection = usersets.get('has_seen_voice_selection', False)
                            data_list.append((history_disabled,seen_custom_instructions_introduction,has_seen_voice_intro,has_seen_voice_selection,))
                        except:
                            logfunc(f'Error parsing ChatGPT - error occured when parsing {file_name} protobuf')
                    
                    if len(data_list) > 0:
                        description = f'User settings'
                        report = ArtifactHtmlReport('ChatGPT - User Settings')
                        report.start_artifact_report(report_folder, f'User Settings', description)
                        report.add_script()
                        data_headers = ('Chat History Disabled','Seen Custom Instructions Intro', 'Seen Voice Intro','Seen Voice Selection')
                        report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                        report.end_artifact_report()
                        
                        tsvname = f'ChatGPT - User Settings'
                        tsv(report_folder, data_headers, data_list, tsvname)
                        
                    else:
                        logfunc(f'No ChatGPT - User Settings available')
               
        #parse analytics-android-oai.xml
        if file_name == 'analytics-android-oai.xml':
            tree = ET.parse(file_found)
            root = tree.getroot()
            data_list = []
            data_dict = {}
            for elem in root.findall('string'):
                key = elem.get('name')
                value = elem.text
                data_dict[key] = value
            try:
                segment_traits = json.loads(data_dict['segment.traits'])
                anonymousId = data_dict['segment.anonymousId']
                userId = data_dict['segment.userId']
                device_id = data_dict['segment.device.id']
                app_ver = data_dict['segment.app.version']
                email = segment_traits['email']
                workspace_id = segment_traits['workspace_id']
                account_has_plus = segment_traits['account_has_plus']
                has_active_subscription = segment_traits['has_active_subscription']
                plan_type = segment_traits['plan_type']
                data_list.append((userId,anonymousId,email,device_id,workspace_id,account_has_plus,plan_type,has_active_subscription,app_ver))
            except:
                 logfunc(f'Error parsing ChatGPT - error occured when parsing {file_name} XML')
            
            if len(data_list) > 0:
                description = f'User settings'
                report = ArtifactHtmlReport('ChatGPT - User Analytics')
                report.start_artifact_report(report_folder, f'User Analytics', description)
                report.add_script()
                data_headers = ('User-ID','Anonymous-ID', 'Email','Device-ID','Workspace-ID','Account Has Plus','Plan Type','Has Active Subscription','App Version')
                report.write_artifact_data_table(data_headers, data_list, file_found, html_escape=False)
                report.end_artifact_report()
                
                tsvname = f'ChatGPT - User Analytics'
                tsv(report_folder, data_headers, data_list, tsvname)
                
            else:
                logfunc(f'No ChatGPT - User Analytics available')
             
             #parse media files
        if "cache" in file_found and "files" in file_found and os.path.isfile(file_found):
            is_file_image = is_image(file_found)
            data_list = []
            if is_file_image:
                filename = (Path(file_found).name)
                filepath = str(Path(file_found).parents[1])
                    
                thumb = media_to_html(filename, files_found, report_folder)
                
                platform = is_platform_windows()
                if platform:
                    thumb = thumb.replace('?', '')
                    
                data_list.append((thumb, filename, file_found))
                if len(data_list) > 0:
                    description = 'ChatGPT - Media Uploads'
                    report = ArtifactHtmlReport('ChatGPT - Media Uploads')
                    report.start_artifact_report(report_folder, 'Media Uploads', description)
                    report.add_script()
                    data_headers = ('Thumbnail','Filename','Location' )
                    report.write_artifact_data_table(data_headers, data_list, filepath, html_escape=False)
                    report.end_artifact_report()
                    
                    tsvname = 'ChatGPT - Media Uploads'
                    tsv(report_folder, data_headers, data_list, tsvname)
                    
                else:
                    logfunc('No ChatGPT - Media Uploads available')   
                            