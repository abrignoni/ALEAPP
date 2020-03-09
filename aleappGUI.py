import argparse
import os
import PySimpleGUI as sg
import scripts.report as report
import shutil
import sys
import webbrowser

from scripts.search_files import *
from scripts.ilapfuncs import *
from scripts.ilap_artifacts import *
from scripts.version_info import aleapp_version
from time import process_time
from tarfile import TarFile
from time import process_time, gmtime, strftime
from zipfile import ZipFile

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
window = sg.Window(f'ALEAPP version {aleapp_version}', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event in (None, 'Close'):   # if user closes window or clicks cancel
        break
    

    if values[0] == True:
        extracttype = 'tar'
        pathto = values[3]
        #logfunc(pathto)
        if pathto.lower().endswith('.tar'):
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
            if pathto.lower().endswith('.zip'):
                pass
            else:
                sg.PopupError('No file or no .zip extension selected. Run the program again.', pathto)
                sys.exit()
    
    start = process_time()
   
    os.makedirs(reportfolderbase)
    os.makedirs(os.path.join(reportfolderbase, 'Script Logs'))
    logfunc('Procesing started. Please wait. This may take a few minutes...')


    window.refresh()
    logfunc('\n--------------------------------------------------------------------------------------')
    logfunc(f'ALEAPP v{aleapp_version}: Android Logs, Events, and Protobuf Parser')
    logfunc('Objective: Triage Android Full System Extractions.')
    logfunc('By: Alexis Brignoni | @AlexisBrignoni | abrignoni.com')
    logfunc('By: Yogesh Khatri | @SwiftForensics | swiftforensics.com')
    window.refresh()
    
    if extracttype == 'fs':
        
        logfunc(f'Artifact categories to parse: {str(len(tosearch))}')
        logfunc(f'File/Directory selected: {pathto}')
        logfunc('\n--------------------------------------------------------------------------------------')
        logfunc('')
        window.refresh()
        log = open(os.path.join(reportfolderbase, 'Script Logs', 'ProcessedFilesLog.html'), 'w+', encoding='utf8')
        nl = '\n' #literal in order to have new lines in fstrings that create text files
        log.write(f'Extraction/Path selected: {pathto}<br><br>')
        
        # Search for the files per the arguments
        for key, val in tosearch.items():
            filefound = search(pathto, val[1])
            window.refresh()
            if not filefound:
                window.refresh()
                logfunc('')
                logfunc(f'No files found for {key} -> {val[1]}.')
                log.write(f'No files found for {key} -> {val[1]}.<br><br>')
            else:
                logfunc('')
                window.refresh()
                #globals()[key](filefound)
                process_artifact(filefound, key, val[0])
                for pathh in filefound:
                    log.write(f'Files for {val[1]} located at {pathh}.<br><br>')
        log.close()

    elif extracttype == 'tar':
        
        logfunc(f'Artifact categories to parse: {str(len(tosearch))}')
        logfunc(f'File/Directory selected: {pathto}')
        logfunc('\n--------------------------------------------------------------------------------------')
        logfunc('')
        window.refresh()
        log = open(os.path.join(reportfolderbase, 'Script Logs', 'ProcessedFilesLog.html'), 'w+', encoding='utf8')
        nl = '\n' #literal in order to have new lines in fstrings that create text files
        log.write(f'Extraction/Path selected: {pathto}<br><br>')    # tar searches and function calls
        
        t = TarFile(pathto)
        
        for key, val in tosearch.items():
            filefound = searchtar(t, val[1], reportfolderbase)
            window.refresh()
            if not filefound:
                window.refresh()
                logfunc('')
                logfunc(f'No files found for {key} -> {val[1]}.')
                log.write(f'No files found for {key} -> {val[1]}.<br><br>')
            else:
                
                logfunc('')
                window.refresh()
                #globals()[key](filefound)
                process_artifact(filefound, key, val[0])
                for pathh in filefound:
                    log.write(f'Files for {val[1]} located at {pathh}.<br><br>')
        log.close()

    elif extracttype == 'zip':
            
            logfunc(f'Artifact categories to parse: {str(len(tosearch))}')
            logfunc(f'File/Directory selected: {pathto}')
            logfunc('\n--------------------------------------------------------------------------------------')
            logfunc('')
            window.refresh()
            log = open(os.path.join(reportfolderbase, 'Script Logs', 'ProcessedFilesLog.html'), 'w+', encoding='utf8')
            nl = '\n' #literal in order to have new lines in fstrings that create text files
            log.write(f'Extraction/Path selected: {pathto}<br><br>')    # tar searches and function calls
            
            z = ZipFile(pathto)
            name_list = z.namelist()
            for key, val in tosearch.items():
                filefound = searchzip(z, name_list, val[1], reportfolderbase)
                window.refresh()
                if not filefound:
                    window.refresh()
                    logfunc('')
                    logfunc(f'No files found for {key} -> {val[1]}.')
                    log.write(f'No files found for {key} -> {val[1]}.<br><br>')
                else:
                    
                    logfunc('')
                    window.refresh()
                    #globals()[key](filefound)
                    process_artifact(filefound, key, val[0])
                    for pathh in filefound:
                        log.write(f'Files for {val[1]} located at {pathh}.<br><br>')
            log.close()
            z.close()

    else:
        logfunc('Error on argument -o')
 
    logfunc('')
    logfunc('Processes completed.')
    end = process_time()
    run_time_secs =  end - start
    run_time_HMS = strftime('%H:%M:%S', gmtime(run_time_secs))
    logfunc("Processing time = {}".format(run_time_HMS))
    
    # log = open(os.path.join(reportfolderbase, 'Script Logs', 'ProcessedFilesLog.html'), 'a', encoding='utf8')
    # log.write(f'Processing time in secs: {str(abs(time))}')
    # log.close()
    
    logfunc('')
    logfunc('Report generation started.')
    report.generate_report(reportfolderbase, run_time_secs, run_time_HMS, extracttype, pathto)
    logfunc('Report generation Completed.')

    if values[5] == True:
        start = process_time()
        window.refresh()
        logfunc('')
        logfunc(f'CSV export starting. This might take a while...')
        window.refresh()
        html2csv(reportfolderbase) 
        end = process_time()
        csv_time_secs =  end - start
        csv_time_HMS = strftime('%H:%M:%S', gmtime(csv_time_secs))
        logfunc("CSV processing time = {}".format(csv_time_secs))
    
    logfunc('')
    logfunc(f'Report location: {reportfolderbase}')
    locationmessage = ('Report name: '+reportfolderbase+'index.html')
    sg.Popup('Processing completed', locationmessage)
    
    basep = os.getcwd()
    webbrowser.open_new_tab('file://'+basep+base+'index.html')
    sys.exit()
