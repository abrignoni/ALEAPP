import aleapp
import os
import PySimpleGUI as sg
import sys
import webbrowser

from scripts.ilapfuncs import *
from scripts.version_info import aleapp_version
from time import process_time, gmtime, strftime

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
    GuiWindow.window_handle = window
    aleapp.crunch_artifacts(extracttype, pathto)

    if values[5] == True:
        start = process_time()
        logfunc('')
        logfunc(f'CSV export starting. This might take a while...')
        html2csv(reportfolderbase) 
        end = process_time()
        csv_time_secs =  end - start
        csv_time_HMS = strftime('%H:%M:%S', gmtime(csv_time_secs))
        logfunc("CSV processing time = {}".format(csv_time_HMS))

    locationmessage = ('Report name: ' + os.path.join(reportfolderbase, 'index.html'))
    sg.Popup('Processing completed', locationmessage)
    
    basep = os.getcwd()
    webbrowser.open_new_tab('file://' + basep + base + 'index.html')
    sys.exit()
