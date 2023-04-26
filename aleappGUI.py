import json
import pathlib
import typing
import aleapp
import PySimpleGUI as sg
import webbrowser
import plugin_loader
from scripts.ilapfuncs import *
from scripts.version_info import aleapp_version
from time import process_time, gmtime, strftime
from scripts.search_files import *

MODULE_START_INDEX = 1000
MODULE_END_INDEX = MODULE_START_INDEX


def ValidateInput(values, window):
    '''Returns tuple (success, extraction_type)'''
    global MODULE_END_INDEX

    i_path = values[0] # input file/folder
    o_path = values[1] # output folder
    ext_type = ''

    if len(i_path) == 0:
        sg.PopupError('No INPUT file or folder selected!')
        return False, ext_type
    elif not os.path.exists(i_path):
        sg.PopupError('INPUT file/folder does not exist!')
        return False, ext_type
    elif os.path.isdir(i_path):
        ext_type = 'fs'
    else: # must be an existing file then
        if not i_path.lower().endswith('.tar') and not i_path.lower().endswith('.zip') and not i_path.lower().endswith('.gz'):
            sg.PopupError('Input file is not a supported archive! ', i_path)
            return False, ext_type
        else:
            ext_type = Path(i_path).suffix[1:].lower() 
    
    # check output now
    if len(o_path) == 0 : # output folder
        sg.PopupError('No OUTPUT folder selected!')
        return False, ext_type

    one_element_is_selected = False
    for x in range(1000, MODULE_END_INDEX):
        if window.FindElement(x).Get():
            one_element_is_selected = True
            break
    if not one_element_is_selected:
        sg.PopupError('No module selected for processing!')
        return False, ext_type

    return True, ext_type

# initialize CheckBox control with module name   
def CheckList(mtxt, lkey, mdstring, disable=False):
    if mdstring == 'test1' or mdstring == 'ImagemngCache' : #items in the if are modules that take a long time to run. Deselects them by default.
        dstate = False
    else:
        dstate = True
    return [sg.CBox(mtxt, default=dstate, key=lkey, metadata=mdstring, disabled=disable)]

def pickModules():
    global MODULE_END_INDEX
    global mlist
    global loader

    loader = plugin_loader.PluginLoader()

    MODULE_END_INDEX = MODULE_START_INDEX     # arbitrary number to not interfere with other controls
    for plugin in sorted(loader.plugins, key=lambda p: p.category.upper()):
        disabled = plugin.is_required
        mlist.append(CheckList(
            f'{plugin.category} [{plugin.name} - {plugin.module_name}.py]', MODULE_END_INDEX, plugin, disabled))
        MODULE_END_INDEX = MODULE_END_INDEX + 1

sg.theme('LightGreen5')   # Add a touch of color
# All the stuff inside your window.

normal_font = ("Helvetica", 12)
loader: typing.Optional[plugin_loader.PluginLoader] = None
mlist = []
# go through list of available modules and confirm they exist on the disk
pickModules()
GuiWindow.progress_bar_total = len(loader)


layout = [  [sg.Text('Android Logs, Events, And Protobuf Parser', font=("Helvetica", 22))],
            [sg.Text('https://github.com/abrignoni/ALEAPP', font=("Helvetica", 14))],
            [sg.Frame(layout=[
                    [sg.Input(size=(97,1)), 
                     sg.FileBrowse(font=normal_font, button_text='Browse File', key='INPUTFILEBROWSE'),
                     sg.FolderBrowse(font=normal_font, button_text='Browse Folder', target=(sg.ThisRow, -2), key='INPUTFOLDERBROWSE')
                    ]
                ],
                title='Select a file (tar/zip/gz) or directory of the target Android full file system extraction for parsing:')],
            [sg.Frame(layout=[
                    [sg.Input(size=(112, 1)), sg.FolderBrowse(font=normal_font, button_text='Browse Folder')]
                ], 
                    title='Select Output Folder:')],
            [sg.Text('Available Modules')],
            [
                sg.Button('Select All', key='SELECT ALL'), sg.Button('Deselect All', key='DESELECT ALL'),
                sg.Button('Load Profile', key='LOAD PROFILE'), sg.Button('Save Profile', key='SAVE PROFILE'),
                sg.Text('  |', font=("Helvetica", 14)),
                sg.Button('Load Case Data', key='LOAD CASE DATA')
             ],
            [sg.Column(mlist, size=(300,310), scrollable=True),  sg.Output(size=(85,20))] ,
            [sg.ProgressBar(max_value=GuiWindow.progress_bar_total, orientation='h', size=(86, 7), key='PROGRESSBAR', bar_color=('DarkGreen', 'White'))],
            [sg.Submit('Process', font=normal_font), sg.Button('Close', font=normal_font)] ]
            
# Create the Window
window = sg.Window(f'ALEAPP version {aleapp_version}', layout)
GuiWindow.progress_bar_handle = window['PROGRESSBAR']


# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()

    if event in (None, 'Close'):   # if user closes window or clicks cancel
        break

    if event == "SELECT ALL":  
        # mark all modules
        for x in range(MODULE_START_INDEX, MODULE_END_INDEX):
            window[x].Update(True)
    if event == "DESELECT ALL":  
         # none modules
        for x in range(MODULE_START_INDEX, MODULE_END_INDEX):
            window[x].Update(window[x].metadata.is_required)  # usagestatsVersion.py is REQUIRED
    if event == "SAVE PROFILE":
        destination_path = sg.popup_get_file(
            "Save a profile", save_as=True,
            file_types=(('ALEAPP Profile (*.alprofile)', '*.alprofile'),),
            default_extension='.alprofile', no_window=True)

        if destination_path:
            ticked = []
            for x in range(MODULE_START_INDEX, MODULE_END_INDEX):
                if window.FindElement(x).Get():
                    key = window[x].metadata.name
                    ticked.append(key)
            with open(destination_path, "wt", encoding="utf-8") as profile_out:
                json.dump({"leapp": "aleapp", "format_version": 1, "plugins": ticked}, profile_out)
            sg.Popup(f"Profile saved: {destination_path}")

    if event == "LOAD PROFILE":
        destination_path = sg.popup_get_file(
            "Load a profile", save_as=False,
            file_types=(('ALEAPP Profile (*.alprofile)', '*.alprofile'), ('All Files', '*')),
            default_extension='.alprofile', no_window=True)

        if destination_path and os.path.exists(destination_path):
            profile_load_error = None
            with open(destination_path, "rt", encoding="utf-8") as profile_in:
                try:
                    profile = json.load(profile_in)
                except json.JSONDecodeError as json_ex:
                    profile_load_error = f"File was not a valid profile file: {json_ex}"

            if not profile_load_error:
                if isinstance(profile, dict):
                    if profile.get("leapp") != "aleapp" or profile.get("format_version") != 1:
                        profile_load_error = "File was not a valid profile file: incorrect LEAPP or version"
                    else:
                        ticked = set(profile.get("plugins", []))
                        #ticked.add("usagestatsVersion")  # always
                        for x in range(MODULE_START_INDEX, MODULE_END_INDEX):
                            if window[x].metadata.is_required:
                                window[x].update(True)
                            elif window[x].metadata.name in ticked:
                                window[x].update(True)
                                ticked.remove(window[x].metadata.name)
                            else:
                                window[x].update(False)

                        # plugins leftover?
                        if len(ticked) > 0:
                            profile_load_error = "Warning: The following plugins were not found: "
                            profile_load_error += "; ".join(sorted(ticked))
                else:
                    profile_load_error = "File was not a valid profile file: invalid format"

            if profile_load_error:
                sg.popup(profile_load_error)
            else:
                sg.popup(f"Loaded profile: {destination_path}")
                
    if event == 'LOAD CASE DATA':
        destination_path = sg.popup_get_file(
            "Load a case data", save_as=False,
            file_types=(('ALEAPP Profile (*.alprofile)', '*.alprofile'), ('All Files', '*')),
            default_extension='.alprofile', no_window=True)
        
        if destination_path and os.path.exists(destination_path):
            profile_load_error = None
            with open(destination_path, "rt", encoding="utf-8") as profile_in:
                try:
                    profile = json.load(profile_in)
                except json.JSONDecodeError as json_ex:
                    profile_load_error = f"File was not a valid profile file: {json_ex}"
                    
            if not profile_load_error:
                if isinstance(profile, dict):
                    casedata = profile
                else:
                    profile_load_error = "File was not a valid profile file: invalid format"
                    
            if profile_load_error:
                sg.popup(profile_load_error)
            else:
                sg.popup(f"Loaded Case Data: {destination_path}")
                
    if event == 'Process':
        #check is selections made properly; if not we will return to input form without exiting app altogether
        is_valid, extracttype = ValidateInput(values, window)
        if is_valid:
            GuiWindow.window_handle = window
            input_path = values[0]
            output_folder = values[1]

            # File system extractions can contain paths > 260 char, which causes problems
            # This fixes the problem by prefixing \\?\ on each windows path.
            if is_platform_windows():
                if input_path[1] == ':' and extracttype =='fs': input_path = '\\\\?\\' + input_path.replace('/', '\\')
                if output_folder[1] == ':': output_folder = '\\\\?\\' + output_folder.replace('/', '\\')
            
            # re-create modules list based on user selection
            #search_list = { 'usagestatsVersion' : tosearch['usagestatsVersion'] } # hardcode usagestatsVersion as first item
            #search_list = [loader['usagestatsVersion']]  # hardcode usagestatsVersion as first item
            search_list = [x for x in loader.plugins if x.is_required]

            s_items = 0
            for x in range(MODULE_START_INDEX, MODULE_END_INDEX):
                if window.FindElement(x).Get():
                    if isinstance(window[x].metadata, plugin_loader.PluginSpec) and not window[x].metadata.is_required:
                        search_list.append(window[x].metadata)

                    s_items = s_items + 1 # for progress bar
                
                # no more selections allowed
                window[x].Update(disabled=True)
                
            window['SELECT ALL'].update(disabled=True)
            window['DESELECT ALL'].update(disabled=True)
        
            GuiWindow.window_handle = window
            out_params = OutputParameters(output_folder)
            wrap_text = True
            
            try:
                casedata
            except NameError:
                casedata = {}
            
            crunch_successful = aleapp.crunch_artifacts(
                search_list, extracttype, input_path, out_params, len(loader)/s_items, wrap_text, casedata)
            if crunch_successful:
                report_path = os.path.join(out_params.report_folder_base, 'index.html')
                    
                if report_path.startswith('\\\\?\\'): # windows
                    report_path = report_path[4:]
                if report_path.startswith('\\\\'): # UNC path
                    report_path = report_path[2:]
                locationmessage = 'Report name: ' + report_path
                sg.Popup('Processing completed', locationmessage)
                webbrowser.open_new_tab('file://' + report_path)
            else:
                log_path = out_params.screen_output_file_path
                if log_path.startswith('\\\\?\\'): # windows
                    log_path = log_path[4:]
                sg.Popup('Processing failed    :( ', f'See log for error details..\nLog file located at {log_path}')
            break

window.close()
