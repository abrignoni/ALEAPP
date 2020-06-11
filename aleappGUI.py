import aleapp
import os
import PySimpleGUI as sg
import sys
import webbrowser

from scripts.ilapfuncs import *
from scripts.version_info import aleapp_version
from time import process_time, gmtime, strftime
from scripts.ilap_artifacts import *
from scripts.search_files import *

def ValidateInput(values):
    if values[0]:
        i_path = values[0] #file
    else:
        i_path = values[1] #folder
        

    results = []
    results.append('False') # validation check
    results.append(i_path) # input_path, 

        
    if len(i_path) == 0:
        sg.PopupError('No INPUT file or folder selected!')
        return results
        
    if not os.path.exists(i_path):
        sg.PopupError('INPUT file/folder does not exist!')
        return results        

    if values[0]: #file
        if not i_path.lower().endswith('.tar') and not i_path.lower().endswith('.zip'):
            sg.PopupError('Input file is not a supported archive! ', i_path)
            return results
        else:
            results.append(Path(i_path).suffix[1:])          
            
    if values[1] : #folder
        results.append('fs') # extracttype
        if not os.path.isdir(i_path):
            sg.PopupError('Input path is not a valid folder!', i_path)
            return results
                   
    
    results[0] = 'True'   
    
    return results
    
# initialize CheckBox control with module name   
def CheckList(mtxt, lkey, mdstring):
    return [sg.CBox(mtxt, default=True, key=lkey, metadata=mdstring)]

# verify module (.py) file exists; only then add it to the "list"
def pickModules():
    script_path = os.getcwd()  + '\scripts\\artifacts\\'
    global indx
    indx = 1000     # arbitrary number to not interfere with other controls
    for key, val in tosearch.items():
        if os.path.isfile(script_path + key + '.py'):
            mlist.append( CheckList(key+'.py [' + val[0] + ']', indx, key ) ) 
            indx = indx +1

sg.theme('LightGreen5')   # Add a touch of color
# All the stuff inside your window.

normal_font = ("Helvetica", 12)
# go through list of available modules and confirm they exist on the disk
mlist =[]
pickModules()

layout = [  [sg.Text('Android Logs, Events, And Protobuf Parser', font=("Helvetica", 22))],
            [sg.Text('https://github.com/abrignoni/ALEAPP', font=("Helvetica", 14))],
            [sg.Text('Select the file type or directory of the target Android full file system extraction for parsing.', font=("Helvetica", 14))],
            [sg.Frame(layout=[
                [sg.Input(size=(0,1), enable_events=True,visible=False), sg.FileBrowse(button_text='Browse File', font=normal_font), 
                 sg.Input(enable_events=True, visible=False), sg.FolderBrowse(button_text='Browse Directory', font=normal_font),
                 sg.Text('Selected:',  font=normal_font, key='SText'), sg.Text(' ',  font=normal_font, background_color='white', size=(70,1), key='Argument')]
                ], title='Select')],
            [sg.Checkbox('Generate CSV output (Additional processing time)', size=(50, 1), default=False, font=normal_font)],
            [sg.Text('Available Modules')],
            [sg.Button('SELECT ALL'), sg.Button('DESELECT ALL')], 
            [sg.Column(mlist, size=(300,310), scrollable=True),  sg.Output(size=(104,20))] ,
            [sg.Submit('Process',font=normal_font), sg.Button('Close', font=normal_font)] ]
            
# Create the Window
window = sg.Window(f'ALEAPP version {aleapp_version}', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event in (None, 'Close'):   # if user closes window or clicks cancel
        break
    
    if values[0]:
        window['Argument'].Update(values[0])
        
    if values[1]:
        window['Argument'].Update(values[1])
    
    if event == "SELECT ALL":  
        # mark all modules
        for x in range(1000,indx):
            window[x].Update(True)
    if event == "DESELECT ALL":  
         # none modules
        for x in range(1000,indx):
            window[x].Update(False) 

    if event == 'Process':
        #check is selections made properly; if not we will return to input form without exiting app altogether
        res = ValidateInput(values)
        if res[0] == 'True':
            GuiWindow.window_handle = window
            pathto = res[1]
            extracttype = res[2]
            # re-create modules list based on user selection
            search_list = {}
            for x in range(1000,indx):
                if window.FindElement(x).Get():
                    if window[x].metadata in tosearch:
                        search_list[window[x].metadata] = tosearch[window[x].metadata]
                
                # no more selections allowed
                window[x].Update(disabled = True)
                
            window['SELECT ALL'].update(disabled=True)
            window['DESELECT ALL'].update(disabled=True)

            GuiWindow.window_handle = window
            aleapp.crunch_artifacts(search_list, extracttype, pathto)

            if values[2] == True:
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
            break
