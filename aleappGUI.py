import sys, os, re, glob
from scripts.search_files import *
from scripts.ilapfuncs import *
import argparse
from argparse import RawTextHelpFormatter
from six.moves.configparser import RawConfigParser
from time import process_time
import  tarfile
import shutil
import webbrowser
from scripts.report import *
from zipfile import ZipFile
from tarfile import TarFile
import PySimpleGUI as sg

sg.theme('LightGreen5')   # Add a touch of color
# All the stuff inside your window.

layout = [  [sg.Text('Android Logs, Events, And Protobuf Parser.', font=("Helvetica", 25))], #added font type and font size
			[sg.Text('https://github.com/abrignoni/ALEAPP', font=("Helvetica", 18))],#added font type and font size
			[sg.Text('Select the file type or directory of the target Android full file system extraction for parsing.', font=("Helvetica", 16))],#added font type and font size
			[sg.Radio('.Tar', "rad1", default=True, font=("Helvetica", 14)), sg.Radio('Directory', "rad1", font=("Helvetica", 14)), sg.Radio('.Zip', "rad1", font=("Helvetica", 14))], #added font type and font size
			[sg.Text('File:', size=(8, 1), font=("Helvetica", 14)), sg.Input(), sg.FileBrowse(font=("Helvetica", 12))], #added font type and font size
			[sg.Text('Directory:', size=(8, 1), font=("Helvetica", 14)), sg.Input(), sg.FolderBrowse(font=("Helvetica", 12))], #added font type and font size
			[sg.Checkbox('Generate CSV output (Additional processing time)', size=(50, 1), default=False, font=("Helvetica", 14))],
			[sg.Output(size=(100,40))], #changed size from (88,20)
			[sg.Submit('Process',font=("Helvetica", 14)), sg.Button('Close', font=("Helvetica", 14))] ] #added font type and font size
			

# Create the Window
window = sg.Window('ALEAPP', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
	event, values = window.read()
	if event in (None, 'Close'):   # if user closes window or clicks cancel
		break
	

	if values[0] == True:
		extracttype = 'tar'
		pathto = values[3]
		#logfunc(pathto)
		if pathto.endswith('.tar'):
			pass
		else:
			sg.PopupError('No file or no .tar extension selected. Run the program again.')
			sys.exit()	
			
	elif values[1] == True:
		extracttype = 'fs'
		pathto = values[4]
		if os.path.isdir(pathto):
			pass
		else:
			sg.PopupError('No path or the one selected is invalid. Run the program again.', pathto)
			sys.exit()
	
	elif values[2] == True:
			extracttype = 'zip'
			pathto = values[3]
			if pathto.endswith('.zip'):
				pass
			else:
				sg.PopupError('No file or no .zip extension selected. Run the program again.', pathto)
				sys.exit()
	
	start = process_time()
	
	
	tosearch = {'wellbeing': '*/com.google.android.apps.wellbeing/databases/*',
				'wellbeingaccount':'*/com.google.android.apps.wellbeing/files/AccountData.pb',
				'usagestats':'*/usagestats/*',
				'recentactivity':'*/system_ce/*'}
	'''
	tosearch = {'lastbuild': '*LastBuildInfo.plist',
				'interactionc':'*interactionC.db'}
	'''
			
	os.makedirs(reportfolderbase)
	os.makedirs(reportfolderbase+'Script Logs')
	logfunc('Procesing started. Please wait. This may take a few minutes...')

	
	window.refresh()
	logfunc('\n--------------------------------------------------------------------------------------')
	logfunc('ALEAPP: Android Logs, Events, and Protobuf Parser')
	logfunc('Objective: Triage Android Full System Extractions.')
	logfunc('By: Alexis Brignoni | @AlexisBrignoni | abrignoni.com')
	window.refresh()
	
	if extracttype == 'fs':
		
		logfunc(f'Artifact categories to parse: {str(len(tosearch))}')
		logfunc(f'File/Directory selected: {pathto}')
		logfunc('\n--------------------------------------------------------------------------------------')
		logfunc('')
		window.refresh()
		log = open(reportfolderbase+'Script Logs/ProcessedFilesLog.html', 'w+', encoding='utf8')
		nl = '\n' #literal in order to have new lines in fstrings that create text files
		log.write(f'Extraction/Path selected: {pathto}<br><br>')
		
		# Search for the files per the arguments
		for key, val in tosearch.items():
			filefound = search(pathto, val)
			window.refresh()
			if not filefound:
				window.refresh()
				logfunc('')
				logfunc(f'No files found for {key} -> {val}.')
				log.write(f'No files found for {key} -> {val}.<br><br>')
			else:
				logfunc('')
				window.refresh()
				globals()[key](filefound)
				for pathh in filefound:
					log.write(f'Files for {val} located at {pathh}.<br><br>')
		log.close()

	elif extracttype == 'tar':
		
		logfunc(f'Artifact categories to parse: {str(len(tosearch))}')
		logfunc(f'File/Directory selected: {pathto}')
		logfunc('\n--------------------------------------------------------------------------------------')
		logfunc('')
		window.refresh()
		log = open(reportfolderbase+'Script Logs/ProcessedFilesLog.html', 'w+', encoding='utf8')
		nl = '\n' #literal in order to have new lines in fstrings that create text files
		log.write(f'Extraction/Path selected: {pathto}<br><br>')	# tar searches and function calls
		
		t = TarFile(pathto)
		
		for key, val in tosearch.items():
			filefound = searchtar(t, val, reportfolderbase)
			window.refresh()
			if not filefound:
				window.refresh()
				logfunc('')
				logfunc(f'No files found for {key} -> {val}.')
				log.write(f'No files found for {key} -> {val}.<br><br>')
			else:
				
				logfunc('')
				window.refresh()
				globals()[key](filefound)
				for pathh in filefound:
					log.write(f'Files for {val} located at {pathh}.<br><br>')
		log.close()

	elif extracttype == 'zip':
			
			logfunc(f'Artifact categories to parse: {str(len(tosearch))}')
			logfunc(f'File/Directory selected: {pathto}')
			logfunc('\n--------------------------------------------------------------------------------------')
			logfunc('')
			window.refresh()
			log = open(reportfolderbase+'Script Logs/ProcessedFilesLog.html', 'w+', encoding='utf8')
			nl = '\n' #literal in order to have new lines in fstrings that create text files
			log.write(f'Extraction/Path selected: {pathto}<br><br>')	# tar searches and function calls
			
			z = ZipFile(pathto)
			name_list = z.namelist()
			for key, val in tosearch.items():
				filefound = searchzip(z, name_list, val, reportfolderbase)
				window.refresh()
				if not filefound:
					window.refresh()
					logfunc('')
					logfunc(f'No files found for {key} -> {val}.')
					log.write(f'No files found for {key} -> {val}.<br><br>')
				else:
					
					logfunc('')
					window.refresh()
					globals()[key](filefound)
					for pathh in filefound:
						log.write(f'Files for {val} located at {pathh}.<br><br>')
			log.close()
			z.close()

	else:
		logfunc('Error on argument -o')
	
		
	#if os.path.exists(reportfolderbase+'temp/'):
	#	shutil.rmtree(reportfolderbase+'temp/')		

	#logfunc(f'iOS version: {versionf} ')
	
	logfunc('')
	logfunc('Processes completed.')
	end = process_time()
	time = start - end
	logfunc("Processing time in secs: " + str(abs(time)) )
	
	log = open(reportfolderbase+'Script Logs/ProcessedFilesLog.html', 'a', encoding='utf8')
	log.write(f'Processing time in secs: {str(abs(time))}')
	log.close()
	
	report(reportfolderbase, time, extracttype, pathto)
	
	
	if values[5] == True:
		start = process_time()
		window.refresh()
		logfunc('')
		logfunc(f'CSV export starting. This might take a while...')
		window.refresh()
		html2csv(reportfolderbase)
		
	if values[5] == True:
		end = process_time()
		time = start - end
		logfunc("CSV processing time in secs: " + str(abs(time)) )
	
	locationmessage = ('Report name: '+reportfolderbase+'index.html')
	sg.Popup('Processing completed', locationmessage)
	
	basep = os.getcwd()
	webbrowser.open_new_tab('file://'+basep+base+'index.html')
	sys.exit()
