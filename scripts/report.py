import html
import os
import pathlib
import shutil

from collections import OrderedDict
from scripts.html_parts import *
from scripts.ilapfuncs import logfunc
from scripts.version_info import aleapp_version, aleapp_contributors


def get_icon_name(category, artifact):
    ''' Returns the icon name from the feathericons collection. To add an icon type for 
        an artifact, select one of the types from ones listed @ feathericons.com
        If no icon is available, the alert triangle is returned as default icon.
    '''
    category = category.upper()
    artifact = artifact.upper()
    icon = 'alert-triangle'  # default (if not defined!)

    ## Please keep list below SORTED by category

    if category.find('BROWSER CACHE') >= 0:
        if artifact.find('CHROME BROWSER CACHE') >= 0:  icon = 'chrome'
        else:                           icon = 'globe'
    if category.find('ACCOUNT') >= 0:
        if artifact.find('AUTH') >= 0:  
            icon = 'key'
        else:                           icon = 'user'
    elif category == 'AIRTAG DETECTION':       icon = 'alert-circle'
    elif category == 'ADB HOSTS':       icon = 'terminal'
    elif category == 'GALLERY TRASH':       icon = 'image'
    elif category == 'ADIDAS-RUNNING':
        if artifact.find('ACTIVITIES') >= 0:   icon = 'activity'
        elif artifact.find('GOALS') >= 0:   icon = 'target'
        elif artifact.find('USER') >= 0:       icon = 'user'
    elif category == 'AIRTAGS':       icon = 'map-pin'
    elif category == 'ANDROID SYSTEM INTELLIGENCE':
        if artifact.find('SIMPLESTORAGE') >=0:  icon = 'loader'
    elif category == 'APP INTERACTION': icon = 'bar-chart-2'
    elif category == 'APP ROLES':  icon = 'tool'
    elif category == 'BASH HISTORY':    icon = 'terminal'
    elif category == 'BADOO':
        if artifact.find('CHAT') >= 0:  icon = 'message-circle'
        elif artifact.find('CONNECTIONS') >= 0:  icon = 'heart'
    elif category == 'BITTORRENT':    icon = 'share'
    elif category == 'BLUETOOTH CONNECTIONS':       icon = 'bluetooth'
    elif category == 'BUMBLE':
        if artifact.find('USER SETTINGS') >= 0:   icon = 'user'
        if artifact.find('CHAT MESSAGES') >= 0:   icon = 'message-circle'
        if artifact.find('MATCHES') >= 0:   icon = 'smile'
    elif category == 'BURNER':
        if artifact.find('NUMBER INFORMATION') >= 0:         icon = 'user'
        elif artifact.find('COMMUNICATION INFORMATION') >= 0:           icon = 'message-circle'
    elif category == 'CALCULATOR LOCKER':       icon = 'lock'
    elif category == 'CALENDAR':
        if artifact.find('CALENDAR - EVENTS') >=0: icon = 'calendar'
        else:   icon = 'calendar'
    elif category == 'CALL LOGS':       icon = 'phone'
    elif category == 'OFFLINE PAGES':       icon = 'cloud-off'
    elif category == 'CASH APP':        icon = 'credit-card'
    elif category == 'CAST':            icon = 'cast'
    elif category == 'CHATS':           icon = 'message-circle'
    elif category == 'CHROMIUM':          
        if artifact.find('AUTOFILL') >= 0:        icon = 'edit-3'
        elif artifact.find('BOOKMARKS') >= 0:       icon = 'bookmark'
        elif artifact.find('DETECT INCIDENTAL PARTY STATE') >= 0:       icon = 'skip-forward'
        elif artifact.find('DOWNLOADS') >= 0:       icon = 'download'
        elif artifact.find('LOGIN') >= 0:           icon = 'log-in'
        elif artifact.find('MEDIA HISTORY') >= 0:   icon = 'video'
        elif artifact.find('NETWORK ACTION PREDICTOR') >=0:    icon = 'type'
        elif artifact.find('OFFLINE PAGES') >= 0:   icon = 'cloud-off'
        elif artifact.find('SEARCH TERMS') >= 0:      icon = 'search'
        elif artifact.find('TOP SITES') >= 0:       icon = 'list'
        elif artifact.find('WEB VISITS') >= 0:      icon = 'globe'
        else:                                       icon = 'chrome'
    elif category == 'CLIPBOARD':        icon = 'clipboard'
    elif category == 'CONTACTS':  icon = 'user'
    elif category == 'DEVICE HEALTH SERVICES':         
        if artifact.find('BLUETOOTH') >=0:  icon = 'bluetooth'
        elif artifact.find('BATTERY') >=0:  icon = 'battery-charging'
        else:                           icon = 'bar-chart-2'
    elif category == 'DEVICE INFO':     
        if artifact == 'BUILD INFO':                icon = 'terminal'
        elif artifact == 'PARTNER SETTINGS':        icon = 'settings'
        elif artifact.find('SETTINGS_SECURE_') >= 0: icon = 'settings'
        else:                                       icon = 'info'
    elif category == 'DIGITAL WELLBEING' or category == 'DIGITAL WELLBEING ACCOUNT': 
        if artifact.find('ACCOUNT DATA') >= 0:  icon = 'user'
        else:                           icon = 'layers'
    elif category == 'DOWNLOADS':   icon = 'download'
    elif category == 'DISCORD CHATS':   icon = 'message-square'        
    elif category == 'DUCKDUCKGO':
        if artifact == 'DUCKDUCKGO TAB THUMBNAILS':  icon = 'image'
        else:                           icon = 'layers'
    elif category == 'EMULATED STORAGE METADATA':     icon = 'database'
    elif category == 'ENCRYPTING MEDIA APPS':       icon = 'lock'
    elif category == 'ETC HOSTS':       icon = 'globe'
    elif category == 'FACEBOOK MESSENGER':
        if artifact.find('CALLS') >= 0:     icon = 'phone-call'
        elif artifact.find('CHAT') >= 0:  icon = 'message-circle'
        elif artifact.find('CONTACTS') >= 0: icon = 'users'
        else: icon = 'facebook'
    elif category == 'FILES BY GOOGLE':     icon = 'file'
    elif category == 'FIREBASE CLOUD MESSAGING':       icon = 'database'
    elif category == 'LIBRE TORRENT':       icon = 'download'
    elif category == 'FIREFOX':
        if artifact.find('BOOKMARKS') >= 0:                 icon = 'bookmark'
        elif artifact.find('COOKIES') >= 0:                 icon = 'info'
        elif artifact.find('DOWNLOADS') >= 0:               icon = 'download'
        elif artifact.find('FORM HISTORY') >= 0:            icon = 'edit-3'
        elif artifact.find('PERMISSIONS') >= 0:             icon = 'sliders'
        elif artifact.find('RECENTLY CLOSED TABS') >= 0:    icon = 'x-square'
        elif artifact.find('SEARCH TERMS') >= 0:            icon = 'search'
        elif artifact.find('TOP SITES') >= 0:               icon = 'list'
        elif artifact.find('VISITS') >= 0:                  icon = 'globe'
        elif artifact.find('WEB HISTORY') >= 0:             icon = 'globe'
    elif category == 'FITBIT':            icon = 'watch'
    elif category == 'GARMIN':      
        if artifact.find('DEVICES') >= 0: icon = 'watch'
        elif artifact.find('NOTIFICATIONS') >= 0: icon = 'bell'
        elif artifact.find('SLEEP') >= 0: icon = 'moon'
        elif artifact.find('WEATHER') >= 0: icon = 'sun'
        else:                       icon = 'activity'
    elif category == 'GARMIN-API':
        if artifact.find('ACTIVITY API') >= 0:
            icon = 'watch'
        elif artifact.find('DAILIES API') >= 0:
            icon = 'calendar'
        elif artifact.find('HEART RATE API') >= 0:
            icon = 'heart'
        elif artifact.find('STEPS API') >= 0:
            icon = 'arrow-up-circle'
        elif artifact.find('SLEEP API') >= 0:
            icon = 'moon'
        elif artifact.find('STRESS API') >= 0:
            icon = 'frown'
        elif artifact.find('POLYLINE API') >= 0:
            icon = 'map-pin'
    elif category == 'GARMIN-CACHE':
        if artifact.find('ACTIVITIES') >= 0:
            icon = 'watch'
        elif artifact.find('CHARTS') >= 0:
            icon = 'activity'
        elif artifact.find('DAILIES') >= 0:
            icon = 'calendar'
        elif artifact.find('POLYLINE') >= 0:
            icon = 'map-pin'
        elif artifact.find('RESPONSE') >= 0:
            icon = 'terminal'
        elif artifact.find('SPO2') >= 0:
            icon = 'heart'
        elif artifact.find('SLEEP') >= 0:
            icon = 'moon'
        elif artifact.find('WEIGHT') >= 0:
            icon = 'bar-chart-2'
    elif category == 'GARMIN-FILES':
        if artifact.find('LOG') >= 0:
            icon = 'file-text'
        elif artifact.find('PERSISTENT') >= 0:
            icon = 'code'
    elif category == 'GARMIN-GCM':
        if artifact.find('ACTIVITIES') >= 0:
            icon = 'watch'
        elif artifact.find('JSON') >= 0:
            icon = 'code'
    elif category == 'GARMIN-NOTIFICATIONS':
        icon = 'message-square'
    elif category == 'GARMIN-SHAREDPREFS':
        if artifact.find('FACEBOOK') >= 0:
            icon = 'facebook'
        elif artifact.find('USER') >= 0:
            icon = 'user'
    elif category == 'GARMIN-SYNC':
        icon = 'loader'
    elif category == 'GEO LOCATION':       icon = 'map-pin'
    elif category == 'GMAIL': 
        if artifact.find('ACTIVE') >= 0:  icon = 'at-sign'
        elif artifact.find('APP EMAILS') >= 0: icon = 'at-sign'
        elif artifact.find('DOWNLOAD REQUESTS') >= 0: icon = 'download-cloud'
        elif artifact.find('LABEL DETAILS')  >= 0: icon = 'mail'
    elif category == 'GOOGLE CALL SCREEN':  icon = 'phone-incoming'
    elif category == 'GOOGLE CHAT':
        if artifact.find('GROUP INFORMATION') >= 0:         icon = 'users'
        elif artifact.find('MESSAGES') >= 0:           icon = 'message-circle'
        elif artifact.find('DRAFTS') >= 0:      icon = 'edit-3'
        elif artifact.find('USERS') >= 0:       icon = 'users'
    elif category == 'GOOGLE DRIVE':     icon = 'file'
    elif category == 'GOOGLE DUO':
        if artifact.find('CALL HISTORY') >= 0:      icon = 'phone-call'
        elif artifact.find('CONTACTS') >= 0:      icon = 'users'
        elif artifact.find('NOTES') >= 0:      icon = 'edit-3'
    elif category == 'GOOGLE FIT (GMS)':     icon = 'activity'           
    elif category == 'GOOGLE KEEP':     icon = 'list'
    elif category == 'GBOARD KEYBOARD':
        if artifact.find('CLIPBOARD') >= 0: icon = 'clipboard'
        else: icon = 'edit-3'
    elif category == 'GOOGLE MAPS VOICE GUIDANCE': icon = 'map'
    elif category == 'GOOGLE MAPS TEMP VOICE GUIDANCE': icon = 'map'
    elif category == 'GOOGLE MESSAGES':     icon = 'message-circle'
    elif category == 'GOOGLE NOW & QUICKSEARCH': icon = 'search'
    elif category == 'GOOGLE PHOTOS':
        if artifact.find('LOCAL TRASH') >=0:            icon = 'trash-2'
        elif artifact.find('BACKED UP FOLDER') >= 0:    icon = 'refresh-cw'
        else:                                           icon = 'image'
    elif category == 'GOOGLE PLAY':     
        if artifact == 'GOOGLE PLAY SEARCHES':      icon = 'search'
        else:                                       icon = 'play'
    elif category == 'GOOGLE TASKS':     icon = 'list'
    elif category == 'GROUPME':
        if artifact.find('GROUP INFORMATION') >= 0:         icon = 'users'
        elif artifact.find('CHAT INFORMATION') >= 0:           icon = 'message-circle'
    elif category == 'HIDEX': icon = 'eye-off'
    elif category == 'IMAGE MANAGER CACHE':       icon = 'image'
    elif category == 'IMO':
        if artifact == 'IMO - ACCOUNT ID':  icon = 'user'
        elif artifact == 'IMO - MESSAGES':  icon = 'message-square'
    elif category == 'INSTALLED APPS':  icon = 'package'
    elif category == 'LINE':
        if artifact == 'LINE - CONTACTS':  icon = 'user'
        elif artifact == 'LINE - MESSAGES':  icon = 'message-square'
        elif artifact == 'LINE - CALL LOGS':  icon = 'phone'
    elif category == 'MAP-MY-WALK':
        if artifact.find('ACTIVITIES') >= 0:  icon = 'map'
        elif artifact.find('USER') >= 0:  icon = 'user'
    elif category == 'MASTODON':
        if artifact.find('ACCOUNT DETAILS') >= 0:    icon = 'user'
        elif artifact.find('ACCOUNT SEARCHES') >= 0:    icon = 'users'
        elif artifact.find('HASHTAG SEARCHES') >= 0:    icon = 'hash'
        elif artifact.find('INSTANCE DETAILS') >= 0:    icon = 'info'
        elif artifact.find('NOTIFICATIONS') >= 0:    icon = 'bell'
        elif artifact.find('TIMELINE') >= 0:    icon = 'activity'
    elif category == 'MEDIA METADATA':  icon = 'file-plus'
    elif category == 'MEGA': icon = 'message-circle'
    elif category == 'MEWE':  icon = 'message-circle'
    elif category == 'MY FILES':
        if artifact.find('MY FILES DB - CACHE MEDIA') >=0: icon = 'image'
        else:                           icon = 'file-plus'
    elif category == 'NIKE-RUN':
        if artifact.find('ACTIVITIES') >=0: icon = 'watch'
        elif artifact.find('ACTIVITY ROUTE') >=0: icon = 'map-pin'
        elif artifact.find('ACTIVITY MOMENTS') >=0: icon = 'list'
        elif artifact.find('NOTIFICATIONS') >= 0:    icon = 'bell'
    elif category == 'NOW PLAYING':           icon = 'music'
    elif category == 'PACKAGE PREDICTIONS':     icon = 'package'
    elif category == 'PERMISSIONS':  icon = 'check'
    elif category == 'PLAYGROUND VAULT':       icon = 'lock'
    elif category == 'PODCAST ADDICT': icon = 'music'
    elif category == 'POWER EVENTS':
        if artifact.find('POWER OFF RESET'):    icon = 'power'
        elif artifact.find('LAST BOOT TIME'):          icon = 'power'
        elif artifact.find('SHUTDOWN CHECKPOINTS'):    icon = 'power'
    elif category == 'PRIVACY DASHBOARD': icon = 'eye'
    elif category == 'PROTONMAIL':
        if artifact.find('CONTACTS') >=0: icon = 'users'
        elif artifact.find('MESSAGES') >=0: icon = 'inbox'
        else:                           icon = 'mail'
    elif category == 'PROTONVPN':       icon = 'shield'
    elif category == 'PUMA-TRAC':
        if artifact.find('ACTIVITIES') >=0: icon = 'watch'
        elif artifact.find('USER') >=0: icon = 'user'
    elif category == 'RCS CHATS':       icon = 'message-circle'
    elif category == 'RECENT ACTIVITY': icon = 'activity'
    elif category == 'RUNKEEPER':
        if artifact.find('ACTIVITIES') >=0: icon = 'watch'
        elif artifact.find('USER') >=0: icon = 'user'
    elif category == 'SAMSUNG SMARTTHINGS': icon = 'bluetooth'
    elif category == 'SAMSUNG WEATHER CLOCK':
        if artifact.find('DAILY') >=0:            icon = 'sunrise'
        elif artifact.find('HOURLY') >=0:            icon = 'thermometer'
        else:                                          icon = 'sun'
    elif category == 'SAMSUNG_CMH':     icon = 'disc'
    elif category == 'SCRIPT LOGS':     icon = 'archive'
    elif category == 'SETTINGS SERVICES':    
        if artifact.find('BATTERY') >=0:    icon = 'battery-charging'
    elif category == 'SKOUT':
        if artifact == 'SKOUT MESSAGES':  icon = 'message-circle'
        elif artifact == 'SKOUT USERS':  icon = 'users'
    elif category == 'SKYPE':
        if artifact == 'SKYPE - CALL LOGS':  icon = 'phone'
        elif artifact == 'SKYPE - MESSAGES':  icon = 'message-square'
        elif artifact == 'SKYPE - CONTACTS':  icon = 'user'
    elif category == 'SLOPES':
        if artifact == 'SLOPES - ACTIONS': icon = 'trending-down'
        elif artifact == 'SLOPES - LIFT DETAILS': icon = 'shuffle'
        elif artifact == 'SLOPES - RESORT DETAILS': icon = 'home'
    elif category == 'SMS & MMS':       icon = 'message-square'
    elif category == 'SNAPCHAT': icon = 'bell'
    elif category == 'SQLITE JOURNALING': icon = 'book-open'
    elif category == 'STRAVA':  icon = 'map'
    elif category == 'TANGO':
        if artifact == 'TANGO - MESSAGES':  icon = 'message-square'
    elif category == 'TEAMS':
        if artifact == 'TEAMS MESSAGES':  icon = 'message-circle'
        elif artifact == 'TEAMS USERS':  icon = 'users'
        elif artifact == 'TEAMS CALL LOG':  icon = 'phone'
        elif artifact == 'TEAMS ACTIVITY FEED':  icon = 'at-sign'
        elif artifact == 'TEAMS FILE INFO':  icon = 'file'
        else:                           icon = 'file-text'
    elif category == 'TEXT NOW':
        if artifact == 'TEXT NOW - CALL LOGS':  icon = 'phone'
        elif artifact == 'TEXT NOW - MESSAGES':  icon = 'message-square'
        elif artifact == 'TEXT NOW - CONTACTS':  icon = 'user'
    elif category == 'TIKTOK':
        if artifact == 'TIKTOK - MESSAGES':  icon = 'message-square'
        elif artifact == 'TIKTOK - CONTACTS':  icon = 'user'
    elif category == 'TODOIST':
        if artifact.find('ITEMS') >=0:  icon = 'list'
        elif artifact.find('NOTES') >=0:  icon = 'file-text'
        elif artifact.find('PROJECTS') >=0:  icon = 'folder'
    elif category == 'TOR':     icon = 'globe'
    elif category == 'TUSKY':
        if artifact.find('TIMELINE') >=0:    icon = 'activity'
        elif artifact.find('ACCOUNT') >=0:    icon = 'user'
    elif category == 'TWITTER':
        if artifact.find('SEARCHES') >=0:      icon = 'twitter'
    elif category == 'USAGE STATS':     icon = 'bar-chart-2'
    elif category == 'USER DICTIONARY': icon = 'book'
    elif category == 'VERIZON RDD ANALYTICS':
        if artifact == 'VERIZON RDD - BATTERY HISTORY' : icon = 'power'
        elif artifact == 'VERIZON RDD - WIFI DATA': icon = 'wifi'
    elif category == 'VIBER':
        if artifact == 'VIBER - CONTACTS':  icon = 'user'
        elif artifact == 'VIBER - MESSAGES':  icon = 'message-square'
        elif artifact == 'VIBER - CALL LOGS':  icon = 'phone'
    elif category == 'VLC':
        if artifact == 'VLC MEDIA LIST':  icon = 'film'
        elif artifact == 'VLC THUMBNAILS':  icon = 'image'
    elif category ==  'VLC THUMBS':
        if artifact == 'VLC MEDIA LIB':  icon = 'film'
        elif artifact == 'VLC THUMBNAILS':  icon = 'image'
        elif artifact == 'VLC THUMBNAIL DATA':  icon = 'image'
        else:                                   icon = 'image'
    elif category == 'WAZE': icon = 'navigation-2'
    elif category == 'HIKVISION':
        if artifact.find('CCTV CHANNELS') >=0: icon = 'film'
        elif artifact.find('CCTV ACTIVITY') >=0: icon = 'activity'
        elif artifact.find('CCTV INFO') >=0: icon = 'settings'
        elif artifact.find('USER CREATED MEDIA') >= 0:    icon = 'video'
    elif category == 'DAHUA TECHNOLOGY (DMSS)':
        if artifact.find('CHANNELS') >=0: icon = 'film'
        elif artifact.find('INFO') >=0: icon = 'settings'
        elif artifact.find('USER CREATED MEDIA') >= 0:   icon = 'video'
        elif artifact.find('SENSORS') >=0: icon = 'smartphone'
        elif artifact.find('DEVICES') >=0: icon = 'tablet'
        elif artifact.find('NOTIFICATIONS') >=0: icon = 'bell'
    elif category == 'WHATSAPP':
        if artifact == 'WHATSAPP - CONTACTS':  icon = 'users'
        elif artifact == 'WHATSAPP - ONE TO ONE MESSAGES': icon = 'message-circle'
        elif artifact == 'WHATSAPP - GROUP MESSAGES': icon = 'message-circle'
        elif artifact == 'WHATSAPP - CALL LOGS': icon = 'phone'
        elif artifact == 'WHATSAPP - GROUP DETAILS': icon = 'users'
        elif artifact == 'WHATSAPP - MESSAGES':  icon = 'message-square'
        else:                           icon = 'user'
    elif category == 'WIFI PROFILES':  icon = 'wifi'
    elif category == 'RAR LAB PREFS':  icon = 'settings'
    elif category == 'PIKPAK':  icon = 'cloud'
    elif category == 'WIPE & SETUP':
        if artifact == 'FACTORY RESET':                  icon = 'loader'
        elif artifact == 'SUGGESTIONS.XML':                icon = 'loader'
        elif artifact == 'SETUP_WIZARD_INFO.XML':          icon = 'loader'
        elif artifact == 'APPOPS.XML':                     icon = 'loader'
        elif artifact == 'SAMSUNG WIPE HISTORY':           icon = 'trash-2'
        elif artifact == 'SAMSUNG WIPE RECOVERY HISTORY LOG':           icon = 'trash-2'
        else:                                            icon = 'loader'
    return icon

def generate_report(reportfolderbase, time_in_secs, time_HMS, extraction_type, image_input_path, casedata):
    control = None
    side_heading = \
        """
        <h6 class="sidebar-heading justify-content-between align-items-center px-3 mt-4 mb-1 text-muted">
            {0}
        </h6>
        """
    list_item = \
        """
        <li class="nav-item">
            <a class="nav-link {0}" href="{1}">
                <span data-feather="{2}"></span> {3}
            </a>
        </li>
        """
    # Populate the sidebar dynamic data (depends on data/files generated by parsers)
    # Start with the 'saved reports' (home) page link and then append elements
    nav_list_data = side_heading.format('Saved Reports') + list_item.format('', 'index.html', 'home', 'Report Home')
    # Get all files
    side_list = OrderedDict() # { Category1 : [path1, path2, ..], Cat2:[..] } Dictionary containing paths as values, key=category

    for root, dirs, files in sorted(os.walk(reportfolderbase)):
        files = sorted(files)
        for file in files:
            if file.endswith(".temphtml"):
                fullpath = (os.path.join(root, file))
                head, tail = os.path.split(fullpath)
                p = pathlib.Path(fullpath)
                SectionHeader = (p.parts[-2])
                if SectionHeader == '_elements':
                    pass
                else:
                    if control == SectionHeader:
                        side_list[SectionHeader].append(fullpath)
                        icon = get_icon_name(SectionHeader, tail.replace(".temphtml", ""))
                        nav_list_data += list_item.format('', tail.replace(".temphtml", ".html"), icon,
                                                          tail.replace(".temphtml", ""))
                    else:
                        control = SectionHeader
                        side_list[SectionHeader] = []
                        side_list[SectionHeader].append(fullpath)
                        nav_list_data += side_heading.format(SectionHeader)
                        icon = get_icon_name(SectionHeader, tail.replace(".temphtml", ""))
                        nav_list_data += list_item.format('', tail.replace(".temphtml", ".html"), icon,
                                                          tail.replace(".temphtml", ""))

    # Now that we have all the file paths, start writing the files

    for path_list in side_list.values():
        for path in path_list:
            old_filename = os.path.basename(path)
            filename = old_filename.replace(".temphtml", ".html")
            # search for it in nav_list_data, then mark that one as 'active' tab
            active_nav_list_data = mark_item_active(nav_list_data, filename) + nav_bar_script
            artifact_data = get_file_content(path)

            # Now write out entire html page for artifact
            f = open(os.path.join(reportfolderbase, filename), 'w', encoding='utf8')
            artifact_data = insert_sidebar_code(artifact_data, active_nav_list_data, path)
            f.write(artifact_data)
            f.close()

            # Now delete .temphtml
            os.remove(path)
            # If dir is empty, delete it
            try:
                os.rmdir(os.path.dirname(path))
            except OSError:
                pass # Perhaps it was not empty!

    # Create index.html's page content
    create_index_html(reportfolderbase, time_in_secs, time_HMS, extraction_type, image_input_path, nav_list_data, casedata)
    elements_folder = os.path.join(reportfolderbase, '_elements')
    os.mkdir(elements_folder)
    __location__ = os.path.dirname(os.path.abspath(__file__))
    
    shutil.copy2(os.path.join(__location__,"logo.jpg"), elements_folder)
    shutil.copy2(os.path.join(__location__,"dashboard.css"), elements_folder)
    shutil.copy2(os.path.join(__location__,"feather.min.js"), elements_folder)
    shutil.copy2(os.path.join(__location__,"dark-mode.css"), elements_folder)
    shutil.copy2(os.path.join(__location__,"dark-mode-switch.js"), elements_folder)
    shutil.copytree(os.path.join(__location__,"MDB-Free_4.13.0"), os.path.join(elements_folder, 'MDB-Free_4.13.0'))
    # Chart.js
    shutil.copy2(os.path.join(__location__,"chart.umd.min.js"), elements_folder)
    # Moment
    shutil.copy2(os.path.join(__location__,"moment.min.js"), elements_folder)
    # D3
    shutil.copy2(os.path.join(__location__,"d3.v7.min.js"), elements_folder)
    # Popper
    shutil.copy2(os.path.join(__location__,"popper.min.js"), elements_folder)
    # Cal-Heatmap
    shutil.copy2(os.path.join(__location__,"cal-heatmap.css"), elements_folder)
    shutil.copy2(os.path.join(__location__,"cal-heatmap.min.js"), elements_folder)
    shutil.copy2(os.path.join(__location__,"Tooltip.min.js"), elements_folder)
    # Highlight.js
    shutil.copy2(os.path.join(__location__,"highlight.min.css"), elements_folder)
    shutil.copy2(os.path.join(__location__,"highlight.min.js"), elements_folder)
    # Garmin Custom JS
    shutil.copy2(os.path.join(__location__,"garmin-functions.js"), elements_folder)
    shutil.copytree(os.path.join(__location__,"timeline"), os.path.join(elements_folder, 'timeline'))
    shutil.copy2(os.path.join(__location__,"chat.css"), elements_folder)
    shutil.copy2(os.path.join(__location__,"chat.js"), elements_folder)

def get_file_content(path):
    f = open(path, 'r', encoding='utf8')
    data = f.read()
    f.close()
    return data

def create_index_html(reportfolderbase, time_in_secs, time_HMS, extraction_type, image_input_path, nav_list_data, casedata):
    '''Write out the index.html page to the report folder'''
    content = '<br />'
    content += """
                   <div class="card bg-white" style="padding: 20px;">
                   <h2 class="card-title">Case Information</h2>
               """  # CARD start

    case_list = [
        ['Extraction location', image_input_path],
        ['Extraction type', extraction_type],
        ['Report directory', reportfolderbase],
        ['Processing time', f'{time_HMS} (Total {time_in_secs} seconds)']
    ]
    
    if len(casedata) > 0:
        for key, value in casedata.items():
            case_list.append([key, value])
    
    tab1_content = generate_key_val_table_without_headings('', case_list) + \
        """
            <p class="note note-primary mb-4">
            All dates and times are in UTC unless noted otherwise!
            </p>
        """

    # Get script run log (this will be tab2)
    devinfo_files_path = os.path.join(reportfolderbase, 'Script Logs', 'DeviceInfo.html')
    tab2_content = get_file_content(devinfo_files_path)

    # Get script run log (this will be tab3)
    script_log_path = os.path.join(reportfolderbase, 'Script Logs', 'Screen Output.html')
    tab3_content = get_file_content(script_log_path)

    # Get processed files list (this will be tab3)
    processed_files_path = os.path.join(reportfolderbase, 'Script Logs', 'ProcessedFilesLog.html')
    tab4_content = get_file_content(processed_files_path)

    content += tabs_code.format(tab1_content, tab2_content, tab3_content, tab4_content)

    content += '</div>'  # CARD end

    authors_data = generate_authors_table_code(aleapp_contributors)
    credits_code = credits_block.format(authors_data)

    # WRITE INDEX.HTML LAST
    filename = 'index.html'
    page_title = 'ALEAPP Report'
    body_heading = 'Android Logs Events And Protobuf Parser'
    body_description = 'ALEAPP is an open source project that aims to parse every known Android artifact for the purpose of forensic analysis.'
    active_nav_list_data = mark_item_active(nav_list_data, filename) + nav_bar_script

    f = open(os.path.join(reportfolderbase, filename), 'w', encoding='utf8')
    f.write(page_header.format(page_title))
    f.write(body_start.format(f"ALEAPP {aleapp_version}"))
    f.write(body_sidebar_setup + active_nav_list_data + body_sidebar_trailer)
    f.write(body_main_header + body_main_data_title.format(body_heading, body_description))
    f.write(content)
    f.write(thank_you_note)
    f.write(credits_code)
    f.write(body_main_trailer + body_end + nav_bar_script_footer + page_footer)
    f.close()

def generate_authors_table_code(aleapp_contributors):
    authors_data = ''
    for author_name, blog, tweet_handle, git in aleapp_contributors:
        author_data = ''
        if blog:
            author_data += f'<a href="{blog}" target="_blank">{blog_icon}</a> &nbsp;\n'
        else:
            author_data += f'{blank_icon} &nbsp;\n'
        if tweet_handle:
            author_data += f'<a href="https://twitter.com/{tweet_handle}" target="_blank">{twitter_icon}</a> &nbsp;\n'
        else:
            author_data += f'{blank_icon} &nbsp;\n'
        if git:
            author_data += f'<a href="{git}" target="_blank">{github_icon}</a>\n'
        else:
            author_data += f'{blank_icon}'

        authors_data += individual_contributor.format(author_name, author_data)
    return authors_data

def generate_key_val_table_without_headings(title, data_list, html_escape=True, width="70%"):
    '''Returns the html code for a key-value table (2 cols) without col names'''
    code = ''
    if title:
        code += f'<h2>{title}</h2>'
    table_header_code = \
        """
        <div class="table-responsive">
            <table class="table table-bordered table-hover table-sm" width={}>
                <tbody>
        """
    table_footer_code = \
        """
                </tbody>
            </table>
        </div>
        """
    code += table_header_code.format(width)

    # Add the rows
    if html_escape:
        for row in data_list:
            code += '<tr>' + ''.join( ('<td>{}</td>'.format(html.escape(str(x))) for x in row) ) + '</tr>'
    else:
        for row in data_list:
            code += '<tr>' + ''.join( ('<td>{}</td>'.format(str(x)) for x in row) ) + '</tr>'

    # Add footer
    code += table_footer_code

    return code

def insert_sidebar_code(data, sidebar_code, filename):
    pos = data.find(body_sidebar_dynamic_data_placeholder)
    if pos < 0:
        logfunc(f'Error, could not find {body_sidebar_dynamic_data_placeholder} in file {filename}')
        return data
    else:
        ret = data[0: pos] + sidebar_code + data[pos + len(body_sidebar_dynamic_data_placeholder):]
        return ret

def mark_item_active(data, itemname):
    '''Finds itemname in data, then marks that node as active. Return value is changed data'''
    pos = data.find(f'" href="{itemname}"')
    if pos < 0:
        logfunc(f'Error, could not find {itemname} in {data}')
        return data
    else:
        ret = data[0: pos] + " active" + data[pos:]
        return ret
    
