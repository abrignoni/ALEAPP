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

    if len(values[0])>0: #file
        if not i_path.lower().endswith('.tar') and not i_path.lower().endswith('.zip'):
            sg.PopupError('Input file is not a supported archive! ', i_path)
            return results
        else:
            results.append(Path(i_path).suffix[1:])          

    if len(values[1])>0 : #folder
        results.append('fs') # extracttype
        if not os.path.isdir(i_path):
            sg.PopupError('Input path is not a valid folder!', i_path)
            return results

    if len(values[2])==0 : # output folder
        sg.PopupError('No OUTPUT folder selected!')
        return results
    else:
        results.append(values[2])
        if not os.path.isdir(values[2]):
            sg.PopupError('Output path is not a valid folder!', values[2])
            return results

    results[0] = 'True'   

    return results

# initialize CheckBox control with module name   
def CheckList(mtxt, lkey, mdstring):
    return [sg.CBox(mtxt, default=True, key=lkey, metadata=mdstring)]

# verify module (.py) file exists; only then add it to the "list"
def pickModules():
    global indx
    
    script_path = os.getcwd()  + '\scripts\\artifacts\\'

    indx = 1000     # arbitrary number to not interfere with other controls
    for key, val in tosearch.items():
        if os.path.isfile(script_path + key + '.py'):
            mlist.append( CheckList(key+'.py [' + val[0] + ']', indx, key ) ) 
            indx = indx +1
            




sg.theme('LightGreen5')   # Add a touch of color
# All the stuff inside your window.

normal_font = ("Helvetica", 12)
mlist =[]
# go through list of available modules and confirm they exist on the disk
pickModules()
GuiWindow.progress_bar_total = indx-1000 #len(aleapp.tosearch)


layout = [  [sg.Text('Android Logs, Events, And Protobuf Parser', font=("Helvetica", 22))],
            [sg.Text('https://github.com/abrignoni/ALEAPP', font=("Helvetica", 14))],
            [sg.Frame(layout=[
                [sg.Input(size=(0,1), enable_events=True,visible=False), sg.FileBrowse(button_text='Browse File', font=normal_font), 
                 sg.Input(enable_events=True, visible=False), sg.FolderBrowse(button_text='Browse Directory', font=normal_font),
                 sg.Text('Selected:',  font=normal_font, key='SText_i'), sg.Text(' ',  font=normal_font, background_color='white', size=(65,1), key='Argument')
                ]],
                title='Select the file type or directory of the target Android full file system extraction for parsing:')],
            [sg.Frame(layout=[[sg.Input(size=(0,1), enable_events=True,visible=False), sg.FolderBrowse(font=normal_font, button_text='Browse Output Folder'),
                               sg.Text('Selected:',  font=normal_font, key='SText_o'), sg.Text(' ',  font=normal_font, background_color='white', size=(73,1), key='Argument_o')]], 
                      title='Select Output Folder:')],
            [sg.Text('Available Modules')],
            [sg.Button('SELECT ALL'), sg.Button('DESELECT ALL')], 
            [sg.Column(mlist, size=(300,310), scrollable=True),  sg.Output(size=(85,20))] ,
            #[sg.Checkbox('Generate CSV output (Additional processing time)', size=(50, 1), default=False, font=normal_font)],
            [sg.ProgressBar(max_value=GuiWindow.progress_bar_total, orientation='h', size=(73, 7), key='PROGRESSBAR', bar_color=('DarkGreen', 'White'))],
            [sg.Submit('Process',font=normal_font), sg.Button('Close', font=normal_font)] ]
            
# Create the Window
window = sg.Window(f'ALEAPP version {aleapp_version}', layout)
GuiWindow.progress_bar_handle = window['PROGRESSBAR']




# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event in (None, 'Close'):   # if user closes window or clicks cancel
        break

    if values[0]:
        window['Argument'].Update(values[0])
        
    if values[1]:
        window['Argument'].Update(values[1])

    if values[2]:
        window['Argument_o'].Update(values[2])    

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
            input_path = res[1]
            extracttype = res[2]
            output_folder = res[3] #os.path.abspath(output_folder)
            
            # re-create modules list based on user selection
            search_list = {}
            s_items = 0
            for x in range(1000,indx):
                if window.FindElement(x).Get():
                    if window[x].metadata in tosearch:
                        search_list[window[x].metadata] = tosearch[window[x].metadata]
                        s_items = s_items +1 #for progress bar
                
            # no more selections allowed
            window[x].Update(disabled = True)
                
            window['SELECT ALL'].update(disabled=True)
            window['DESELECT ALL'].update(disabled=True)
        
            #GuiWindow.progress_bar_total = s
            GuiWindow.window_handle = window
            out_params = OutputParameters(output_folder)
            aleapp.crunch_artifacts(search_list, extracttype, input_path, out_params, len(aleapp.tosearch)/s_items)
            
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