import os
import re
import socket
import sqlite3
import textwrap
import datetime
import xml.etree.ElementTree as ET

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import timeline, tsv, is_platform_windows, open_sqlite_db_readonly, logfunc, logdevinfo, checkabx, abxread

def get_protonVPN(files_found, report_folder, seeker, wrap_text):

	for file_found in files_found:
		file_found = str(file_found)
		if file_found.endswith('ServerListUpdater.xml'):

			data_list = []
			
			if (checkabx(file_found)):
				multi_root = False
				tree = abxread(file_found, multi_root)
			else:
				tree = ET.parse(file_found)

			root = tree.getroot()

			for elem in root.iter():
				if elem.attrib.get('name') is not None:
					if elem.text is not None:
						data_list.append((elem.attrib.get('name'), elem.text))
					elif elem.attrib.get('value') is not None:
						data_list.append((elem.attrib.get('name'), elem.attrib.get('value')))

					if (elem.attrib.get('name')) == 'ipAddress':
						logdevinfo(f'<b>IP Address: </b>{elem.text}')

					if (elem.attrib.get('name')) == 'lastKnownIsp':
						logdevinfo(f'<b>ISP: </b>{elem.text}')

					if (elem.attrib.get('name')) == 'lastKnownCountry':
						logdevinfo(f'<b>Country: </b>{elem.text}')

					if (elem.attrib.get('name')) == 'ipAddressCheckTimestamp':
						timestamp =  datetime.datetime.utcfromtimestamp(int(elem.attrib.get("value"))/1000).strftime('%Y-%m-%d %H:%M:%S.%f')
						logdevinfo(f'<b>Last IP Check Time: </b>{timestamp}')
		
			if data_list:
				report = ArtifactHtmlReport('ProtonVPN Device Info.xml')
				report.start_artifact_report(report_folder, 'ProtonVPN - Device Info')
				report.add_script()
				data_headers = ('Key', 'Value')
				report.write_artifact_data_table(data_headers, data_list, file_found)
				report.end_artifact_report()

				tsvname = f'ProtonVPN - Device Info'
				tsv(report_folder, data_headers, data_list, tsvname)

				tlactivity = f'ProtonVPN - Device Info'
				timeline(report_folder, tlactivity, data_list, data_headers)
			else:
				logfunc('No ProtonVPN - Device Info available')

		elif file_found.endswith('Data.log'):

			data_list = []

			protonvpn_log = open(file_found, 'r')
			log_entries = protonvpn_log.readlines()
			protonvpn_log.close()
			
			regex = re.compile(r"node.+\.protonvpn\.net")
			for entry in log_entries: 
				initial_connect = entry.find('to:')
				if initial_connect != -1:
					timestamp = entry[:entry.find('|')-1].split('.')[0].replace('T', ' ')
					try:
						server_hostname = regex.search(entry)[0]
						server_ip = socket.gethostbyname(server_hostname)
						data_list.append((server_hostname + f"  -  [ {server_ip} ]", timestamp))
					except socket.error:
						server_hostname = regex.search(entry)[0]
						data_list.append((server_hostname, timestamp))
					except:
						pass

			if data_list:
				report = ArtifactHtmlReport('ProtonVPN Connection History')
				report.start_artifact_report(report_folder, 'ProtonVPN - Connection History')
				report.add_script()
				data_headers = ('Server Address', 'Timestamp')
				report.write_artifact_data_table(data_headers, data_list, file_found)
				report.end_artifact_report()

				tsvname = f'ProtonVPN - Conncetion History'
				tsv(report_folder, data_headers, data_list, tsvname)

				tlactivity = f'ProtonVPN - Connection History'
				timeline(report_folder, tlactivity, data_list, data_headers)
			else:
				logfunc('No ProtonVPN - Connection History available')

		elif file_found.endswith('db'):
			db = open_sqlite_db_readonly(file_found)

			# Cursor for User Data
			cursor = db.cursor()
			cursor.execute('SELECT * FROM main.UserEntity')
			user_data_rows = cursor.fetchall()
			
			# Cursor for Account Data
			cursor = db.cursor()
			cursor.execute('SELECT * FROM main.AccountEntity')
			account_data_rows = cursor.fetchall()

			userentries = len(user_data_rows)
			accountentries = len(account_data_rows)
			if userentries > 0 and accountentries > 0:
				report = ArtifactHtmlReport('ProtonVPN - User Info')
				report.start_artifact_report(report_folder, 'ProtonVPN - User data')
				report.add_script()
				data_headers = ('Email', 'Name', 'Username', 'Display Name', 'Account State')
				data_list = []
				for user_row, account_row in zip(user_data_rows, account_data_rows):
					data_list.append((user_row[1], user_row[2], account_row[1], user_row[3], account_row[5]))

				report.write_artifact_data_table(data_headers, data_list, file_found)
				report.end_artifact_report()

				tsvname = f'ProtonVPN - User Info'
				tsv(report_folder, data_headers, data_list, tsvname)

				tlactivity = f'ProtonVPN - User Info'
				timeline(report_folder, tlactivity, data_list, data_headers)
			else:
				logfunc('No ProtonVPN - User Info available')

			db.close()

__artifacts__ = {
	"protonVPN User": (
		"ProtonVPN", 
		('*/ch.protonvpn.android/databases/db', '*/ch.protonvpn.android/shared_prefs/ServerListUpdater.xml', '*/ch.protonvpn.android/log/Data.log'), get_protonVPN
	)
}
