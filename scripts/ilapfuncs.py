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
