import sqlite3
import sys, os, re
import glob
import datetime
from scripts.parse3 import ParseProto
import codecs
import json
import sqlite3
import io
import sys
import csv
import pathlib
import shutil
import textwrap
import base64
from time import process_time
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET  
import scripts.usagestatsservice_pb2 as usagestatsservice_pb2
from enum import IntEnum


nl = '\n' 
now = datetime.datetime.now()
currenttime = str(now.strftime('%Y-%m-%d_%A_%H%M%S'))
reportfolderbase = './ALEAPP_Reports_'+currenttime+'/'
base = '/ALEAPP_Reports_'+currenttime+'/'
temp = reportfolderbase+'temp/'

def logfunc(message=""):
	if pathlib.Path(reportfolderbase+'Script Logs/Screen Output.html').is_file():
		with open(reportfolderbase+'Script Logs/Screen Output.html', 'a', encoding='utf8') as a:
			print(message)
			a.write(message+'<br>')
	else:
		with open(reportfolderbase+'Script Logs/Screen Output.html', 'a', encoding='utf8') as a:
			print(message)
			a.write(message+'<br>')

def recentactivity(filefound):
	logfunc('Recent Tasks function executing')
	try:
		if os.path.isdir(reportfolderbase+'Recent Tasks/'):
			pass
		else:
			os.makedirs(reportfolderbase+'Recent Tasks/')
	except:
		logfunc('Error creating Recent Tasks() report directory')

	db = sqlite3.connect(reportfolderbase+'Recent Tasks/RecentAct.db')
	cursor = db.cursor()
	#Create table recent.
	cursor.execute('''
	CREATE TABLE 
	recent(task_id TEXT, effective_uid TEXT, affinity TEXT, real_activity TEXT, first_active_time TEXT, last_active_time TEXT,
	last_time_moved TEXT, calling_package TEXT, user_id TEXT, action TEXT, component TEXT, snap TEXT,recimg TXT, fullat1 TEXT, fullat2 TEXT)
	''')
	db.commit()
	err = 0
	
	stringfilefound = str(filefound[0])
	
	script_lev, tail = stringfilefound.split('/system_ce/')
	script_dir = script_lev+'/system_ce/0'
	for filename in glob.iglob(script_dir+r'/recent_tasks/**', recursive=True):
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
				print('Processed: '+filename)
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
					check1 = script_dir + '/snapshots/' + snapshot
					isit1 = os.path.isfile(check1)
					if isit1:
						#copy snaphot image to report folder
						shutil.copy2(check1, reportfolderbase+'Recent Tasks/')
						#snap = r'./snapshots/' + snapshot
						snap = snapshot
					else:
						snap = 'NO IMAGE'
					#Recent_images section
					if icon_image_path is not None:
						recent_image = os.path.basename(icon_image_path)
						check2 = script_dir + '/recent_images/' + recent_image
						isit2 = os.path.isfile(check2)
						if isit2:
							shutil.copy2(check2, reportfolderbase+'Recent Tasks/')
							#recimg = r'./recent_images/' + recent_image
							recimg = recent_image
						else:
							recimg = 'NO IMAGE'
					else:
						#check for other files not in the XML - all types
						check3 = glob.glob(script_dir + r'/recent_images/' + task_id + '*.*')
						if check3:
							check3 = check3[0]
							isit3 = os.path.isfile(check3)
						else:
							isit3 = 0
						
						if isit3:
							shutil.copy2(check3, reportfolderbase+'Recent Tasks/')
							recimg = os.path.basename(check3)
						else:
							recimg = 'NO IMAGE'
					#else:
					#	recimg = 'NO IMAGE'
					#insert all items in database
					cursor = db.cursor()
					datainsert = (task_id, effective_uid, affinity, real_activity, first_active_time, last_active_time, last_time_moved, calling_package, user_id, action, component, snap, recimg, fullat1, fullat2,)
					cursor.execute('INSERT INTO recent (task_id, effective_uid, affinity, real_activity, first_active_time, last_active_time, last_time_moved, calling_package, user_id, action, component, snap, recimg, fullat1, fullat2)  VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', datainsert)
					db.commit()
					
	#Create html file for report
	f1= open(reportfolderbase+'Recent Tasks/Recent Activity.html', 'w+')

	#HTML header
	f1.write('<html><body>')
	f1.write('<h2> Android Recent Tasks Report </h2>')
	f1.write(f'Recent Tasks, Snapshots, and Recent Images located at {script_dir}')
	f1.write('<br>')
	f1.write ('<style> table, th, td {border: 1px solid black; border-collapse: collapse;} img {width: 180px; height: 370px; object-fit: cover;}</style>')


	#Query to create report
	db = sqlite3.connect(reportfolderbase+'Recent Tasks/RecentAct.db')
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
	logfunc('Recent Tasks function completed')
	
def usagestats(filefound):
	logfunc('UsageStats function executing')
	
	class EventType(IntEnum):
	    NONE = 0
	    MOVE_TO_FOREGROUND = 1
	    MOVE_TO_BACKGROUND = 2
	    END_OF_DAY = 3
	    CONTINUE_PREVIOUS_DAY = 4
	    CONFIGURATION_CHANGE = 5
	    SYSTEM_INTERACTION = 6
	    USER_INTERACTION = 7
	    SHORTCUT_INVOCATION = 8
	    CHOOSER_ACTION = 9
	    NOTIFICATION_SEEN = 10
	    STANDBY_BUCKET_CHANGED = 11
	    NOTIFICATION_INTERRUPTION = 12
	    SLICE_PINNED_PRIV = 13
	    SLICE_PINNED = 14
	    SCREEN_INTERACTIVE = 15
	    SCREEN_NON_INTERACTIVE = 16
	    KEYGUARD_SHOWN = 17
	    KEYGUARD_HIDDEN = 18

	    def __str__(self):
	        return self.name # This returns 'KNOWN' instead of 'EventType.KNOWN'

	class EventFlag(IntEnum):
	    FLAG_IS_PACKAGE_INSTANT_APP = 1
	    
	    def __str__(self):
	        return self.name

	def ReadUsageStatsPbFile(input_path):
		'''Opens file, reads usagestats protobuf and returns IntervalStatsProto object'''
		stats = usagestatsservice_pb2.IntervalStatsProto()

		with open (input_path, 'rb') as f:
			stats.ParseFromString(f.read())
			#print(stats)
			return stats

	def AddEntriesToDb(stats, db):
		cursor = db.cursor()
		# packages
		for usagestat in stats.packages:
			finalt = ''
			if usagestat.HasField('last_time_active_ms'):
				finalt = usagestat.last_time_active_ms
				if finalt < 0:
					finalt = abs(finalt)
				else:
					finalt += file_name_int
			tac = ''
			if usagestat.HasField('total_time_active_ms'):
				tac = abs(usagestat.total_time_active_ms)
			pkg = stats.stringpool.strings[usagestat.package_index - 1]
			alc = ''
			if usagestat.HasField('app_launch_count'):
				alc = abs(usagestat.app_launch_count)

			datainsert = ('packages', finalt, tac, '', '', '', alc, pkg, '' , '' , sourced, '')
			#print(datainsert)
			cursor.execute('INSERT INTO data (usage_type, lastime, timeactive, last_time_service_used, last_time_visible, total_time_visible, '
							'app_launch_count, package, types, classs, source, fullatt)  VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', datainsert)
		#configurations
		for conf in stats.configurations:
			usagetype = 'configurations'
			finalt = ''
			if usagestat.HasField('last_time_active_ms'):
				finalt = usagestat.last_time_active_ms
				if finalt < 0:
					finalt = abs(finalt)
				else:
					finalt += file_name_int
			tac = ''
			if usagestat.HasField('total_time_active_ms'):
				tac = abs(usagestat.total_time_active_ms)
			fullatti_str = str(conf.config)
			datainsert = (usagetype, finalt, tac, '', '', '', '', '', '', '', sourced, fullatti_str)
			#print(datainsert)
			cursor.execute('INSERT INTO data (usage_type, lastime, timeactive, last_time_service_used, last_time_visible, total_time_visible, '
							'app_launch_count, package, types, classs, source, fullatt)  VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', datainsert)							
		#event-log
		usagetype = 'event-log'
		for event in stats.event_log:
			pkg = ''
			classy = ''
			tipes = ''
			finalt = ''
			if event.HasField('time_ms'):
				finalt = event.time_ms
				if finalt < 0:
					finalt = abs(finalt)
				else:
					finalt += file_name_int
			if event.HasField('package_index'):
				pkg = stats.stringpool.strings[event.package_index - 1]
			if event.HasField('class_index'):
				classy = stats.stringpool.strings[event.class_index - 1]
			if event.HasField('type'):
				tipes = str(EventType(event.type)) if event.type <= 18 else str(event.type)
			datainsert = (usagetype, finalt, '' , '' , '' , '' ,'' , pkg , tipes , classy , sourced, '')
			cursor.execute('INSERT INTO data (usage_type, lastime, timeactive, last_time_service_used, last_time_visible, total_time_visible, '
						'app_launch_count, package, types, classs, source, fullatt)  VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', datainsert)

		db.commit()

	### MAIN PROGRAM ###
	processed = 0

	try:
		if os.path.isdir(reportfolderbase+'UsageStats/'):
			pass
		else:
			os.makedirs(reportfolderbase+'UsageStats/')
	except:
		logfunc('Error creating UsageStats() report directory')

	#Create sqlite databases
	db = sqlite3.connect(reportfolderbase+'UsageStats/usagestats.db')
	cursor = db.cursor()

	#Create table usagedata.

	cursor.execute('''

	    CREATE TABLE data(usage_type TEXT, lastime INTEGER, timeactive INTEGER,
						  last_time_service_used INTEGER, last_time_visible INTEGER, total_time_visible INTEGER,
						  app_launch_count INTEGER,
						  package TEXT, types TEXT, classs TEXT,
						  source TEXT, fullatt TEXT)

	''')

	db.commit()

	err=0
	stats = None


	logfunc ('Android Usagestats XML & Potobuf Parser')
	logfunc ('By: @AlexisBrignoni & @SwiftForensics')
	logfunc ('Web: abrignoni.com & swiftforensics.com')

	#script_dir = os.path.dirname(__file__)
	splitfilefound, tail = filefound[0].split('/usagestats/')
	for filename in glob.iglob(str(splitfilefound)+'/usagestats/**', recursive=True):
		if os.path.isfile(filename): # filter dirs
			file_name = os.path.basename(filename)
			#Test if xml is well formed
			if file_name == 'version':
				continue	
			else:
				if 'daily' in filename:
					sourced = 'daily'
				elif 'weekly' in filename:
					sourced = 'weekly'
				elif 'monthly' in filename:
					sourced = 'monthly'
				elif 'yearly' in filename:
					sourced = 'yearly'
				
				try:
					file_name_int = int(file_name)
				except: 
					logfunc('Invalid filename: ')
					logfunc(filename)
					logfunc('')
					err = 1
				
				try:
					ET.parse(filename)
				except ET.ParseError:
					# Perhaps an Android Q protobuf file
					try:
						stats = ReadUsageStatsPbFile(filename)
						err = 0
					except:
						logfunc('Parse error - Non XML and Non Protobuf file? at: ')
						logfunc(filename)
						logfunc('')
						err = 1
						#print(filename)
					if stats:
						#print('Processing - '+filename)
						#print('')
						AddEntriesToDb(stats, db)
						continue
				
				if err == 1:
					err = 0
					continue
				else:
					tree = ET.parse(filename)
					root = tree.getroot()
					print('Processing: '+filename)
					print('')
					for elem in root:
						#print(elem.tag)
						usagetype = elem.tag
						#print("Usage type: "+usagetype)
						if usagetype == 'packages':
							for subelem in elem:
								#print(subelem.attrib)
								fullatti_str = json.dumps(subelem.attrib)
								#print(subelem.attrib['lastTimeActive'])
								time1 = subelem.attrib['lastTimeActive']
								time1 = int(time1)
								if time1 < 0:
									finalt = abs(time1)
								else:
									finalt = file_name_int + time1
								#print('final time: ')
								#print(finalt)
								#print(subelem.attrib['package'])
								pkg = (subelem.attrib['package'])
								#print(subelem.attrib['timeActive'])
								tac = (subelem.attrib['timeActive'])
								#print(subelem.attrib['lastEvent'])
								alc = (subelem.attrib.get('appLaunchCount', ''))
								#insert in database
								cursor = db.cursor()
								datainsert = (usagetype, finalt, tac, '', '', '', alc, pkg, '', '', sourced, fullatti_str,)
								#print(datainsert)
								cursor.execute('INSERT INTO data (usage_type, lastime, timeactive, last_time_service_used, last_time_visible, total_time_visible, '
											   'app_launch_count, package, types, classs, source, fullatt)  VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', datainsert)
								db.commit()
						
						elif usagetype == 'configurations':
							for subelem in elem:
								fullatti_str = json.dumps(subelem.attrib)
								#print(subelem.attrib['lastTimeActive'])
								time1 = subelem.attrib['lastTimeActive']
								time1 = int(time1)
								if time1 < 0:
									finalt = abs(time1)
								else:
									finalt = file_name_int + time1
								#print('final time: ')
								#print(finalt)
								#print(subelem.attrib['timeActive'])
								tac = (subelem.attrib['timeActive'])
								#print(subelem.attrib)
								#insert in database
								cursor = db.cursor()
								datainsert = (usagetype, finalt, tac, '', '', '', '', '', '', '', sourced, fullatti_str,)
								#print(datainsert)
								cursor.execute('INSERT INTO data (usage_type, lastime, timeactive, last_time_service_used, last_time_visible, total_time_visible, '
											   'app_launch_count, package, types, classs, source, fullatt)  VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', datainsert)							
								#datainsert = (usagetype, finalt, tac, '' , '' , '' , sourced, fullatti_str,)
								#cursor.execute('INSERT INTO data (usage_type, lastime, timeactive, package, types, classs, source, fullatt)  VALUES(?,?,?,?,?,?,?,?)', datainsert)
								db.commit()
				
						elif usagetype == 'event-log':
							for subelem in elem:
								#print(subelem.attrib['time'])
								time1 = subelem.attrib['time']
								time1 = int(time1)
								if time1 < 0:
									finalt = abs(time1)
								else:
									finalt = file_name_int + time1
								
								#time1 = subelem.attrib['time']
								#finalt = file_name_int + int(time1)
								#print('final time: ')
								#print(finalt)
								#print(subelem.attrib['package'])
								pkg = (subelem.attrib['package'])
								#print(subelem.attrib['type'])
								tipes = (subelem.attrib['type'])
								#print(subelem.attrib)
								fullatti_str = json.dumps(subelem.attrib)
								#add variable for type conversion from number to text explanation
								#print(subelem.attrib['fs'])
								#classy = subelem.attrib['class']
								if 'class' in subelem.attrib:
									classy = subelem.attrib['class']
									cursor = db.cursor()
									datainsert = (usagetype, finalt, '' , '' , '' , '' ,'' , pkg , tipes , classy , sourced, fullatti_str,)
									cursor.execute('INSERT INTO data (usage_type, lastime, timeactive, last_time_service_used, last_time_visible, total_time_visible, '
											   'app_launch_count, package, types, classs, source, fullatt)  VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', datainsert)
									db.commit()
								else:
								#insert in database
									cursor = db.cursor()
									cursor.execute('INSERT INTO data (usage_type, lastime, timeactive, last_time_service_used, last_time_visible, total_time_visible, '
											   'app_launch_count, package, types, classs, source, fullatt)  VALUES(?,?,?,?,?,?,?,?,?,?,?,?)', datainsert)
									datainsert = (usagetype, finalt, '' , '' , '', '', '', pkg , tipes , '' , sourced, fullatti_str,)
									#cursor.execute('INSERT INTO data (usage_type, lastime, timeactive, package, types, classs, source, fullatt)  VALUES(?,?,?,?,?,?,?,?)', datainsert)
									db.commit()
									
	#query for reporting
	cursor.execute('''
	select 
	usage_type,
	datetime(lastime/1000, 'UNIXEPOCH', 'localtime') as lasttimeactive,
	timeactive as time_Active_in_msecs,
	timeactive/1000 as timeactive_in_secs,
	case last_time_service_used  WHEN '' THEN ''
	 ELSE datetime(last_time_service_used/1000, 'UNIXEPOCH', 'localtime')
	end last_time_service_used,
	case last_time_visible  WHEN '' THEN ''
	 ELSE datetime(last_time_visible/1000, 'UNIXEPOCH', 'localtime') 
	end last_time_visible,
	total_time_visible,
	app_launch_count,
	package,
	CASE types
	     WHEN '1' THEN 'MOVE_TO_FOREGROUND'
	     WHEN '2' THEN 'MOVE_TO_BACKGROUND'
	     WHEN '5' THEN 'CONFIGURATION_CHANGE'
		 WHEN '7' THEN 'USER_INTERACTION'
		 WHEN '8' THEN 'SHORTCUT_INVOCATION'
	     ELSE types
	END types,
	classs,
	source,
	fullatt
	from data
	order by lasttimeactive DESC
	''')
	all_rows = cursor.fetchall()

	#HTML report section
	h = open(reportfolderbase+'UsageStats/UsageStats.html', 'w')	
	h.write('<html><body>')
	h.write('<h2>Android Usagestats report (Dates are localtime!)</h2>')
	h.write('UsageStats located at '+str(splitfilefound)+'/usagestats/')
	h.write('<br>')
	h.write('<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>')
	h.write('<br>')
	h.write('')
	
	

	#HTML headers
	h.write(f'<table class="table sticky">')
	h.write('<tr>')
	h.write('<th>Usage Type</th>')
	h.write('<th>Last Time Active</th>')
	h.write('<th>Time Active in Msecs</th>')
	h.write('<th>Time Active in Secs</th>')
	h.write('<th>Last Time Service Used</th>')
	h.write('<th>Last Time Visible</th>')
	h.write('<th>Total Time Visible</th>')
	h.write('<th>App Launch Count</th>')
	h.write('<th>Package</th>')
	h.write('<th>Types</th>')
	h.write('<th>Class</th>')
	h.write('<th>Source</th>')
	h.write('</tr>')

	for row in all_rows:
		usage_type = row[0]
		lasttimeactive = row[1]
		time_Active_in_msecs = row[2]
		timeactive_in_secs = row[3]
		last_time_service_used = row[4]
		last_time_visible = row[5]
		total_time_visible = row[6]
		app_launch_count = row[7]
		package = row[8]
		types = row[9]
		classs = row[10]
		source = row[11]
		
		processed = processed+1
		#report data
		h.write('<tr>')
		h.write('<td>'+str(usage_type)+'</td>')
		h.write('<td>'+str(lasttimeactive)+'</td>')
		h.write('<td>'+str(time_Active_in_msecs)+'</td>')
		h.write('<td>'+str(timeactive_in_secs)+'</td>')
		h.write('<td>'+str(last_time_service_used)+'</td>')
		h.write('<td>'+str(last_time_visible)+'</td>')
		h.write('<td>'+str(total_time_visible)+'</td>')
		h.write('<td>'+str(app_launch_count)+'</td>')
		h.write('<td>'+str(package)+'</td>')
		h.write('<td>'+str(types)+'</td>')
		h.write('<td>'+str(classs)+'</td>')
		h.write('<td>'+str(source)+'</td>')
		h.write('</tr>')

	#HTML footer	
	h.write('<table>')
	h.write('<br />')	

	
	logfunc('Records processed: '+str(processed))
	logfunc('UsageStats function completed')
		




def wellbeing(filefound):
	logfunc(f'Wellbeing events function executing')
	try:
		if os.path.isdir(reportfolderbase+'Wellbeing/'):
			pass
		else:
			os.makedirs(reportfolderbase+'Wellbeing/')
	except:
		logfunc('Error creating wellbeing() report directory')

	try:
		head, tail = os.path.split(filefound[0])
		db = sqlite3.connect(head+'/app_usage')
		cursor = db.cursor()
		cursor.execute('''
		SELECT 
				events._id, 
				datetime(events.timestamp /1000, 'UNIXEPOCH') as timestamps, 
				packages.package_name,
				events.type,
				case
					when events.type = 1 THEN 'ACTIVITY_RESUMED'
					when events.type = 2 THEN 'ACTIVITY_PAUSED'
					when events.type = 12 THEN 'NOTIFICATION'
					when events.type = 18 THEN 'KEYGUARD_HIDDEN & || Device Unlock'
					when events.type = 19 THEN 'FOREGROUND_SERVICE_START'
					when events.type = 20 THEN 'FOREGROUND_SERVICE_STOP' 
					when events.type = 23 THEN 'ACTIVITY_STOPPED'
					when events.type = 26 THEN 'DEVICE_SHUTDOWN'
					when events.type = 27 THEN 'DEVICE_STARTUP'
					else events.type
					END as eventtype
				FROM
				events INNER JOIN packages ON events.package_id=packages._id 
		''')

		all_rows = cursor.fetchall()
		usageentries = len(all_rows)
		if usageentries > 0:
			#logfunc(f'Wellbeing events function executing')
			with open(reportfolderbase+'Wellbeing/Events.html', 'w', encoding='utf8') as f:
				f.write('<html><body>')
				f.write('<h2> Wellbeing events report</h2>')
				f.write(f'Wellbeing event entries: {usageentries}<br>')
				f.write(f'Wellbeing events located at: {filefound[0]}<br>')
				f.write('<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>')
				f.write('<br/>')
				f.write('')
				f.write(f'<table class="table sticky">')
				f.write(f'<tr><th>Timestamp</th><th>Package ID</th><th>Event Type</th></tr>')
				for row in all_rows:
					f.write(f'<tr><td>{row[1]}</td><td>{row[2]}</td><td>{row[4]}</td></tr>')
				f.write(f'</table></body></html>')
		else:
				logfunc('No Wellbeing event data available')
	except:
		logfunc('Error in Wellbeing event section')
	logfunc('Wellbeing event function completed')

def wellbeingaccount(filefound):	
	logfunc(f'Wellbeing Account function executing')
	try:
		if os.path.isdir(reportfolderbase+'Wellbeing/'):
			pass
		else:
			os.makedirs(reportfolderbase+'Wellbeing/')
	except:
		logfunc('Error creating wellbeing() report directory')

	try:
		content = ParseProto(filefound[0])
		
		content_json_dump = json.dumps(content, indent=4, sort_keys=True, ensure_ascii=False)
		parsedContent = str(content_json_dump).encode(encoding='UTF-8',errors='ignore')
		
		with open(reportfolderbase+'Wellbeing/Account Data.html', 'w', encoding='utf8') as f:
			f.write('<html><body>')
			f.write('<h2> Wellbeing Account report</h2>')
			f.write(f'Wellbeing Account located at: {filefound[0]}<br>')
			f.write('<style> table, td {border: 1px solid black; border-collapse: collapse;}tr:nth-child(even) {background-color: #f2f2f2;} .table th { background: #888888; color: #ffffff}.table.sticky th{ position:sticky; top: 0; }</style>')
			f.write('<br/>')
			f.write('')
			f.write(f'<table class="table sticky">')
			f.write(f'<tr><th>Protobuf Parsed Data</th><th>Protobuf Data</th></tr>')
			f.write('<tr><td><pre id=\"json\">'+str(parsedContent).replace("\\n", "<br>")+'</pre></td><td>'+str(content)+'</td></tr>')
			f.write(f'</table></body></html>')
	except:
		logfunc('Error in Wellbeing Account section')
	logfunc('Wellbeing Account function completed')
	
def deviceinfoin(ordes, kas, vas, sources):
	sources = str(sources)
	db = sqlite3.connect(reportfolderbase+'Device Info/di.db')
	cursor = db.cursor()
	datainsert = (ordes, kas, vas, sources,)
	cursor.execute('INSERT INTO devinf (ord, ka, va, source)  VALUES(?,?,?,?)', datainsert)
	db.commit()
	
def html2csv(reportfolderbase):
	#List of items that take too long to convert or that shouldn't be converted
	itemstoignore = ['index.html',
					'Distribution Keys.html', 
					'StrucMetadata.html',
					'StrucMetadataCombined.html']
					
	if os.path.isdir(reportfolderbase+'_CSV Exports/'):
		pass
	else:
		os.makedirs(reportfolderbase+'_CSV Exports/')
	for root, dirs, files in sorted(os.walk(reportfolderbase)):
		for file in files:
			if file.endswith(".html"):
				fullpath = (os.path.join(root, file))
				head, tail = os.path.split(fullpath)
				if file in itemstoignore:
					pass
				else:
					data = open(fullpath, 'r', encoding='utf8')
					soup=BeautifulSoup(data,'html.parser')
					tables = soup.find_all("table")
					data.close()
					output_final_rows=[]

					for table in tables:
						output_rows = []
						for table_row in table.findAll('tr'):

							columns = table_row.findAll('td')
							output_row = []
							for column in columns:
									output_row.append(column.text)
							output_rows.append(output_row)
		
						file = (os.path.splitext(file)[0])
						with codecs.open(reportfolderbase+'_CSV Exports/'+file+'.csv', 'a', 'utf-8-sig') as csvfile:
							writer = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_ALL)
							writer.writerows(output_rows)
