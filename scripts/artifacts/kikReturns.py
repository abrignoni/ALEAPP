import os
import datetime
import csv
import codecs
import shutil
import magic

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows

def get_kikReturns(files_found, report_folder, seeker, wrap_text):

    for file_found in files_found:
        file_found = str(file_found)
        filename = os.path.basename(file_found)
        
        if filename.startswith('bind.txt'):
            data_list =[]
            with open(file_found, 'r') as f:
                delimited = csv.reader(f, delimiter='\t')
                for item in delimited:
                    utctimestamp = (datetime.datetime.fromtimestamp(int(item[0])/1000).strftime('%Y-%m-%d %H:%M:%S'))
                    user = item[1]
                    ip = item[2]
                    port = item [3]
                    timestamp = item[4]
                    info = item[5]
                    data_list.append((utctimestamp, timestamp, user, ip, port, info))
                
            if data_list:
                report = ArtifactHtmlReport('Kik - Bind')
                report.start_artifact_report(report_folder, 'Kik - Bind.txt')
                report.add_script()
                data_headers = ('Timestamp UTC', 'Timestamp', 'User', 'IP', 'Port', 'Info')
                report.write_artifact_data_table(data_headers, data_list, file_found)
                report.end_artifact_report()
                
                tsvname = f'Kik - bind'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Kik - bind'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Kik - Bind data available')
                
        if filename.startswith('chat_platform_sent_received.txt'):
            data_list =[]
            with open(file_found, 'r') as f:
                delimited = csv.reader(f, delimiter='\t')
                for item in delimited:
                    utctimestamp = (datetime.datetime.fromtimestamp(int(item[0])/1000).strftime('%Y-%m-%d %H:%M:%S'))
                    user = item[2]
                    user_other = item[1]
                    app = item[3]
                    contentID = item[4]
                    info = item[5]
                    timestamp = item[6]
                    thumb = ''
                    for match in files_found:
                        if contentID in match:
                            shutil.copy2(match, report_folder)
                            mimetype = magic.from_file(match, mime = True)
                            
                            if mimetype == 'video/mp4':
                                thumb = f'<video width="320" height="240" controls="controls"><source src="{report_folder}{contentID}" type="video/mp4">Your browser does not support the video tag.</video>'
                            else:
                                thumb = f'<img src="{report_folder}{contentID}" width="300"></img>'
                            
                            data_list.append((utctimestamp, timestamp, user, user_other, app, info, contentID, thumb))
                            break
                            

            if data_list:
                report = ArtifactHtmlReport('Kik - Chat Platform Sent Received')
                report.start_artifact_report(report_folder, 'Kik - Chat Platform Sent Received')
                report.add_script()
                data_headers = ('Timestamp UTC', 'Timestamp', 'User', 'User', 'App', 'Info', 'Content ID', 'Content')
                report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Content'])
                report.end_artifact_report()
                
                tsvname = f'Kik - Chat Platform Sent Received'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Kik - Chat Platform Sent Received'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Kik Chat Platform Sent Received data available')
        
        if filename.startswith('chat_platform_sent.txt'):
            data_list =[]
            with open(file_found, 'r') as f:
                delimited = csv.reader(f, delimiter='\t')
                for item in delimited:
                    utctimestamp = (datetime.datetime.fromtimestamp(int(item[0])/1000).strftime('%Y-%m-%d %H:%M:%S'))
                    user = item[1]
                    user_other = item[2]
                    app = item[3]
                    contentID = item[4]
                    info = item[5]
                    timestamp = item[6]
                    thumb = ''
                    for match in files_found:
                        if contentID in match:
                            shutil.copy2(match, report_folder)
                            mimetype = magic.from_file(match, mime = True)
                            
                            if mimetype == 'video/mp4':
                                thumb = f'<video width="320" height="240" controls="controls"><source src="{report_folder}{contentID}" type="video/mp4">Your browser does not support the video tag.</video>'
                            else:
                                thumb = f'<img src="{report_folder}{contentID}" width="300"></img>'
                                
                            data_list.append((utctimestamp, timestamp, user, user_other, app, info, contentID, thumb))
                            break
                        
                        
            if data_list:
                report = ArtifactHtmlReport('Kik - Chat Platform Sent')
                report.start_artifact_report(report_folder, 'Kik - Sent')
                report.add_script()
                data_headers = ('Timestamp UTC', 'Timestamp', 'User', 'User', 'App', 'IP', 'Content ID', 'Content')
                report.write_artifact_data_table(data_headers, data_list, file_found, html_no_escape=['Content'])
                report.end_artifact_report()
                
                tsvname = f'Kik - Chat Platform Sent'
                tsv(report_folder, data_headers, data_list, tsvname)
                
                tlactivity = f'Kik - Chat Platform Sent'
                timeline(report_folder, tlactivity, data_list, data_headers)
            else:
                logfunc('No Kik Chat Platform Sent data available')
        
                