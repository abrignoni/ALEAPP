import glob
import json
import os
import shutil
import sqlite3
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import logfunc

def get_recentactivity(files_found, report_folder):

    db = sqlite3.connect(os.path.join(report_folder, 'RecentAct.db'))
    cursor = db.cursor()
    #Create table recent.
    cursor.execute('''
    CREATE TABLE 
    recent(task_id TEXT, effective_uid TEXT, affinity TEXT, real_activity TEXT, first_active_time TEXT, last_active_time TEXT,
    last_time_moved TEXT, calling_package TEXT, user_id TEXT, action TEXT, component TEXT, snap TEXT,recimg TXT, fullat1 TEXT, fullat2 TEXT)
    ''')
    db.commit()
    err = 0
    
    stringfilefound = str(files_found[0]) # Path should be xxx/xxx/system_ce/0
    
    #script_lev, tail = stringfilefound.split('/system_ce/')
    script_dir = stringfilefound #script_lev+'/system_ce/0'
    for filename in glob.iglob(os.path.join(script_dir, 'recent_tasks', '**'), recursive=True):
        if os.path.isfile(filename): # filter dirs
            file_name = os.path.basename(filename)
            #logfunc(filename)
            #logfunc(file_name)
            #numid = file_name.split('_')[0]
    
            try:
                ET.parse(filename)
            except ET.ParseError:
                logfunc('Parse error - Non XML file? at: '+filename)
                err = 1
                #print(filename)
                
            if err == 1:
                err = 0
                continue
            else:
                tree = ET.parse(filename)
                root = tree.getroot()
                #print('Processed: '+filename)
                for child in root:
                    #All attributes. Get them in using json dump thing
                    fullat1 = json.dumps(root.attrib)
                    task_id = (root.attrib.get('task_id'))
                    effective_uid = (root.attrib.get('effective_uid'))
                    affinity = (root.attrib.get('affinity'))
                    real_activity = (root.attrib.get('real_activity'))
                    first_active_time = (root.attrib.get('first_active_time'))
                    last_active_time = (root.attrib.get('last_active_time'))
                    last_time_moved = (root.attrib.get('last_time_moved'))
                    calling_package = (root.attrib.get('calling_package'))
                    user_id = (root.attrib.get('user_id'))
                    #print(root.attrib.get('task_description_icon_filename'))
                    
                    #All attributes. Get them in using json dump thing
                    fullat2 = json.dumps(child.attrib)
                    action = (child.attrib.get('action'))
                    component = (child.attrib.get('component'))
                    icon_image_path = (root.attrib.get('task_description_icon_filename'))
                    
                    #Snapshot section picture
                    snapshot = task_id + '.jpg'
                    #print(snapshot)
                    
                    #check for image in directories
                    check1 = os.path.join(script_dir, 'snapshots', snapshot)
                    isit1 = os.path.isfile(check1)
                    if isit1:
                        #copy snaphot image to report folder
                        shutil.copy2(check1, report_folder)
                        #snap = r'./snapshots/' + snapshot
                        snap = snapshot
                    else:
                        snap = 'NO IMAGE'
                    #Recent_images section
                    if icon_image_path is not None:
                        recent_image = os.path.basename(icon_image_path)
                        check2 = os.path.join(script_dir, 'recent_images', recent_image)
                        isit2 = os.path.isfile(check2)
                        if isit2:
                            shutil.copy2(check2, report_folder)
                            #recimg = r'./recent_images/' + recent_image
                            recimg = recent_image
                        else:
                            recimg = 'NO IMAGE'
                    else:
                        #check for other files not in the XML - all types
                        check3 = glob.glob(os.path.join(script_dir, 'recent_images', task_id, '*.*'))
                        if check3:
                            check3 = check3[0]
                            isit3 = os.path.isfile(check3)
                        else:
                            isit3 = 0
                        
                        if isit3:
                            shutil.copy2(check3, report_folder)
                            recimg = os.path.basename(check3)
                        else:
                            recimg = 'NO IMAGE'
                    #else:
                    #    recimg = 'NO IMAGE'
                    #insert all items in database
                    cursor = db.cursor()
                    datainsert = (task_id, effective_uid, affinity, real_activity, first_active_time, last_active_time, last_time_moved, calling_package, user_id, action, component, snap, recimg, fullat1, fullat2,)
                    cursor.execute('INSERT INTO recent (task_id, effective_uid, affinity, real_activity, first_active_time, last_active_time, last_time_moved, calling_package, user_id, action, component, snap, recimg, fullat1, fullat2)  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', datainsert)
                    db.commit()
                    
    #Create html file for report
    f1= open(os.path.join(report_folder, 'Recent Activity.html'), 'w+')

    #HTML header
    f1.write('<html><body>')
    f1.write('<h2> Android Recent Tasks Report </h2>')
    f1.write(f'Recent Tasks, Snapshots, and Recent Images located at {script_dir}')
    f1.write('<br>')
    f1.write ('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} img {width: 180px; height: 370px; object-fit: cover;}</style>')


    #Query to create report
    db = sqlite3.connect(os.path.join(report_folder, 'RecentAct.db'))
    cursor = db.cursor()

    #Query to create report
    cursor.execute('''
    SELECT 
        task_id as Task_ID, 
        effective_uid as Effective_UID, 
        affinity as Affinity, 
        real_activity as Real_Activity, 
        datetime(first_active_time/1000, 'UNIXEPOCH', 'LOCALTIME') as First_Active_Time, 
        datetime(last_active_time/1000, 'UNIXEPOCH', 'LOCALTIME') as Last_Active_Time,
        datetime(last_time_moved/1000, 'UNIXEPOCH', 'LOCALTIME') as Last_Time_Moved,
        calling_package as Calling_Package, 
        user_id as User_ID, 
        action as Action, 
        component as Component, 
        snap as Snapshot_Image, 
        recimg as Recent_Image
    FROM recent
    ''')
    all_rows = cursor.fetchall()
    colnames = cursor.description

    for row in all_rows:
        if row[2] is None:
            row2 = 'NO DATA'
        else:
            row2 = row[2]
        appName = '<h3> Application: ' + row2 + '<h3>'
        f1.write(appName)
        f1.write('<table> <tr><th>Key</th><th>Values</th></tr>')
        
        #do loop for headers
        
        for x in range(0, 13):
            
            if row[x] is None:
                dbCol = 'NO DATA'
                f1.write('<tr>')
                f1.write('<td align="left">')
                f1.write(colnames[x][0])
                f1.write('</td>')
            
                f1.write('<td align="left">')
                f1.write(dbCol)
                f1.write('</td>')
                f1.write('</tr>')
                #f1.write('</br>')
                
                
            else:
                f1.write('<tr>')
                f1.write('<td align="left">')
                f1.write(colnames[x][0])
                f1.write('</td>')
                
                f1.write('<td align="left">')
                f1.write(str(row[x]))
                f1.write('</td>')
                f1.write('</tr>')
                
                #f1.write('</br>')
        f1.write('</table></p>')    
        f1.write('<table> <tr><th>Snapshot_Images</th><th>Recent_Image</th></tr>')
        f1.write('<tr>')
        for x in range(11, 13):
                if row[x] == 'NO IMAGE':
                        
                    
                    f1.write('<td align="left">')
                    f1.write('No Image')
                    f1.write('</td>')
                    
                else:
                    
                #f1.write('</tr>')
                    #f1.write('<tr>')
                    f1.write('<td align="left">')
                    f1.write('<a href="')
                    f1.write(str(row[x]))
                    f1.write('"><img src="')
                    f1.write(str(row[x]))
                    f1.write('" alt="Smiley face">')
                    f1.write('</a>')
                    f1.write('</td>')
                    #f1.write('</tr>')
        f1.write('</tr>')
        f1.write('</table></p>')
    f1.close()
