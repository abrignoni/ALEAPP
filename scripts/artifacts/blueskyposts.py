__artifacts_v2__ = {
    "blueskyposts": {
        "name": "Bluesky",
        "description": "Bluesky Feed Posts",
        "author": "Alexis Brignoni",
        "version": "0.0.1",
        "date": "2024-11-20",
        "requirements": "none",
        "category": "Bluesky",
        "notes": "",
        "paths": ('*/xyz.blueskyweb.app/cache/http-cache/*.*'),
        "function": "get_blueskyposts"
    }
}
import os
import json
import sqlite3
from pathlib import Path 
from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, timeline, is_platform_windows,open_sqlite_db_readonly,convert_ts_human_to_utc,tsv,utf8_in_extended_ascii

def get_blueskyposts(files_found, report_folder, seeker, wrap_text):
    
    feed_data_list = []
    posts_data_list = []
    
    
    for file_found in files_found:
        file_found = str(file_found)

        try:
            with open(file_found, 'r',encoding='utf-8') as file:
                data = json.load(file)
                value = data.get('feed')
                if value is not None:
                    if len(value) > 0:
                        for items in value:
                            urip = (data['feed'][0]['post']['uri'])
                            cidp = (data['feed'][0]['post']['cid'])
                            typep = (data['feed'][0]['post']['record']['$type'])#
                            createdatp = (data['feed'][0]['post']['record']['createdAt'])#
                            langsp = (data['feed'][0]['post']['record']['langs'])#
                            textp = (data['feed'][0]['post']['record']['text'])#
                            didp = (data['feed'][0]['post']['author']['did'])#
                            handlep = (data['feed'][0]['post']['author']['handle'])#
                            displaynamep = (data['feed'][0]['post']['author']['displayName'])#
                            avatarp = (data['feed'][0]['post']['author']['avatar'])#
                            authorcreatedatp = (data['feed'][0]['post']['author']['createdAt'])#
                            replycountp =(data['feed'][0]['post']['replyCount'])#
                            repostcountp = (data['feed'][0]['post']['repostCount'])#
                            likecountp = (data['feed'][0]['post']['likeCount'])#
                            quotecountp = (data['feed'][0]['post']['quoteCount'])#
                            
                        
                            createdatp = createdatp.replace('T',' ')
                            createdatp = createdatp[:-1]
                            createdatp = convert_ts_human_to_utc(createdatp)#
                            
                            
                            authorcreatedatp = authorcreatedatp.replace('T',' ')
                            authorcreatedatp = authorcreatedatp[:-1]
                            authorcreatedatp = convert_ts_human_to_utc(authorcreatedatp)#
                            
                            source = file_found
                            
                            feedtuple = tuple((createdatp,authorcreatedatp,typep,handlep,displaynamep,textp,replycountp,repostcountp,likecountp,quotecountp,avatarp,didp,langsp,cidp,urip,source))
                            
                            if feedtuple in feed_data_list:
                                pass
                            else:
                                feed_data_list.append((feedtuple))
                    else:
                        pass
                posts = data.get('posts')
                if posts is not None:
                    if len(posts) > 0:
                        for post in posts:
                            urips = (post['uri'])
                            cidps = (post['cid'])
                            typeps = (post['record']['$type'])#
                            createdatps = (post['record']['createdAt'])#
                            langsps = (post['record']['langs'])#
                            textps = (post['record']['text'])#
                            didps = (post['author']['did'])#
                            handleps = (post['author']['handle'])#
                            displaynameps = (post['author']['displayName'])#
                            avatarps = (post['author']['avatar'])#
                            authorcreatedatps = (post['author']['createdAt'])#
                            replycountps =(post['replyCount'])#
                            repostcountps = (post['repostCount'])#
                            likecountps = (post['likeCount'])#
                            quotecountps = (post['quoteCount'])#
                            
                            createdatps = createdatps.replace('T',' ')
                            createdatps = createdatps[:-1]
                            createdatps = convert_ts_human_to_utc(createdatps)#
                            
                            
                            authorcreatedatps = authorcreatedatps.replace('T',' ')
                            authorcreatedatps = authorcreatedatps[:-1]
                            authorcreatedatps = convert_ts_human_to_utc(authorcreatedatps)#
                            
                            sources = file_found
                            
                            poststuple = tuple((createdatps,authorcreatedatps,typeps,handleps,displaynameps,textps,replycountps,repostcountps,likecountps,quotecountps,avatarps,didps,langsps,cidps,urips,sources))
                            
                            if poststuple in posts_data_list:
                                pass
                            else:
                                posts_data_list.append((poststuple))
                                
                    else:
                        pass            
        except:
            pass

            
    if len(feed_data_list) > 0:
        report = ArtifactHtmlReport('Bluesky Feed Posts')
        report.start_artifact_report(report_folder, f'Bluesky Feed Posts')
        report.add_script()
        data_headers = ('Timestamp','Author Created At','Type','Handle','Display Name','Text','Reply Count','Repost Count','Like Count','Quote Count', 'Avatar','DID','Language','CID','URI','Source')
        report.write_artifact_data_table(data_headers, feed_data_list, 'See report')
        report.end_artifact_report()
        
        tsvname = f'Bluesky Feed Posts'
        tsv(report_folder, data_headers, feed_data_list, tsvname)
        
        tlactivity = f'Bluesky Feed Posts'
        timeline(report_folder, tlactivity, feed_data_list, data_headers)
        
    else:
        logfunc(f'No Bluesky Feed Posts data available')
        
    
    if len(posts_data_list) > 0:
        report = ArtifactHtmlReport('Bluesky Posts')
        report.start_artifact_report(report_folder, f'Bluesky Posts')
        report.add_script()
        data_headers = ('Timestamp','Author Created At','Type','Handle','Display Name','Text','Reply Count','Repost Count','Like Count','Quote Count', 'Avatar','DID','Language','CID','URI','Source')
        report.write_artifact_data_table(data_headers, posts_data_list, 'See report')
        report.end_artifact_report()
        
        tsvname = f'Bluesky Posts'
        tsv(report_folder, data_headers, posts_data_list, tsvname)
        
        tlactivity = f'Bluesky Posts'
        timeline(report_folder, tlactivity, posts_data_list, data_headers)
        
    else:
        logfunc(f'No Bluesky Posts data available')
        
        