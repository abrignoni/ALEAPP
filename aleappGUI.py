import aleapp
import os
import PySimpleGUI as sg
import sys
import webbrowser

from scripts.ilapfuncs import *
from scripts.version_info import aleapp_version
from time import process_time, gmtime, strftime

GuiWindow.progress_bar_total = len(aleapp.tosearch)

sg.theme('LightGreen5')   # Add a touch of color
# All the stuff inside your window.

normal_font = ("Helvetica", 12)

layout = [  [sg.Text('Android Logs, Events, And Protobuf Parser', font=("Helvetica", 22))],
            [sg.Text('https://github.com/abrignoni/ALEAPP', font=("Helvetica", 14))],
            [sg.Text('Select the file type or directory of the target Android full file system extraction for parsing.', font=normal_font)],
            [   sg.Radio('.Tar', "rad1", default=True, font=normal_font, enable_events=True), 
                sg.Radio('Directory', "rad1", font=normal_font, enable_events=True), 
                sg.Radio('.Zip', "rad1", font=normal_font, enable_events=True) ],
            [   sg.Text('Input File/Folder', size=(12, 1), font=normal_font), 
                sg.Input(), 
                sg.FolderBrowse(font=normal_font, button_text='Browse Folder', key='INPUTFOLDERBROWSE', disabled=True), 
                sg.FileBrowse(font=normal_font, target=(4, 1), key='INPUTFILEBROWSE') ],
            [sg.Text('Output Folder', size=(12, 1), font=normal_font), sg.Input(), sg.FolderBrowse(font=normal_font, button_text='Browse Folder')],
            #[sg.Checkbox('Generate CSV output (Additional processing time)', size=(50, 1), default=False, font=normal_font)],
            [sg.ProgressBar(max_value=GuiWindow.progress_bar_total, orientation='h', size=(68, 7), key='PROGRESSBAR', bar_color=('DarkGreen', 'White'))],
            [sg.Output(size=(104,20))],
            [sg.Submit('Process',font=normal_font), sg.Button('Close', font=normal_font)] ]
            
# Create the Window
window = sg.Window(f'ALEAPP version {aleapp_version}', layout)
GuiWindow.progress_bar_handle = window['PROGRESSBAR']
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event in (None, 'Close'):   # if user closes window or clicks cancel
        break

    if event == 1: # Directory radiobutton selected
        window['INPUTFOLDERBROWSE'].update(disabled=False)
        window['INPUTFILEBROWSE'].update(disabled=True)
    elif event in (0, 2): # other radiobuttons selected
        window['INPUTFOLDERBROWSE'].update(disabled=True)
        window['INPUTFILEBROWSE'].update(disabled=False)

    if event == 'Process':
        output_folder = values[4]
        input_path = values[3]
            
        if len(output_folder) == 0:
            sg.PopupError('No OUTPUT folder selected. Run the program again.')
            sys.exit()
            
        if len(input_path) == 0:
            sg.PopupError('No INPUT file or folder selected. Run the program again.')
            sys.exit()

        if not os.path.exists(input_path):
            sg.PopupError('INPUT file/folder does not exist! Run the program again.')
            sys.exit()

        output_folder = os.path.abspath(output_folder)
        if values[0] == True:
            extracttype = 'tar'
            if not input_path.lower().endswith('.tar'):
                sg.PopupError('Input file does not have .tar extension! Run the program again.', input_path)
                sys.exit()
                
        elif values[1] == True:
            extracttype = 'fs'
            if not os.path.isdir(input_path):
                sg.PopupError('Input path is not a valid folder. Run the program again.', input_path)
                sys.exit()
        
        elif values[2] == True:
            extracttype = 'zip'
            if not input_path.lower().endswith('.zip'):
                sg.PopupError('No file or no .zip extension selected. Run the program again.', input_path)
                sys.exit()
        
        GuiWindow.window_handle = window
        out_params = OutputParameters(output_folder)
        aleapp.crunch_artifacts(extracttype, input_path, out_params)

        '''
        if values[5] == True:
            start = process_time()
            logfunc('')
            logfunc(f'CSV export starting. This might take a while...')
            html2csv(out_params.report_folder_base) 
            end = process_time()
            csv_time_secs =  end - start
            csv_time_HMS = strftime('%H:%M:%S', gmtime(csv_time_secs))
            logfunc("CSV processing time = {}".format(csv_time_HMS))
        '''

        report_path = os.path.join(out_params.report_folder_base, 'index.html')
        locationmessage = 'Report name: ' + report_path
        sg.Popup('Processing completed', locationmessage)
        
        #basep = os.getcwd()
        if report_path.startswith('\\\\'): # UNC path
            report_path = report_path[2:]
        webbrowser.open_new_tab('file://' + report_path)
        break
window.close()