# To add a new artifact module, import it here as shown below:
#     from scripts.artifacts.fruitninja import get_fruitninja
# Also add the grep search for that module using the same name
# to the 'tosearch' data structure.

import traceback

from scripts.artifacts.adb_hosts import get_adb_hosts
from scripts.artifacts.etc_hosts import get_etc_hosts
from scripts.artifacts.BashHistory import get_BashHistory
from scripts.artifacts.ChessWithFriends import get_ChessWithFriends
from scripts.artifacts.WordsWithFriends import get_WordsWithFriends
from scripts.artifacts.accounts_ce import get_accounts_ce
from scripts.artifacts.accounts_ce_authtokens import get_accounts_ce_authtokens
from scripts.artifacts.accounts_de import get_accounts_de
from scripts.artifacts.appicons import get_appicons
from scripts.artifacts.build import get_build
from scripts.artifacts.calllog import get_calllog
from scripts.artifacts.Cast import get_Cast
from scripts.artifacts.Cello import get_Cello
from scripts.artifacts.chrome import get_chrome 
from scripts.artifacts.chromeBookmarks import get_chromeBookmarks
from scripts.artifacts.chromeCookies import get_chromeCookies
from scripts.artifacts.chromeDownloads import get_chromeDownloads
from scripts.artifacts.chromeLoginData import get_chromeLoginData
from scripts.artifacts.chromeOfflinePages import get_chromeOfflinePages
from scripts.artifacts.chromeSearchTerms import get_chromeSearchTerms
from scripts.artifacts.chromeTopSites import get_chromeTopSites
from scripts.artifacts.chromeWebsearch import get_chromeWebsearch
from scripts.artifacts.cmh import get_cmh
from scripts.artifacts.DocList import get_DocList
from scripts.artifacts.emulatedSmeta import get_emulatedSmeta
from scripts.artifacts.FilesByGoogle_FilesMaster import get_FilesByGoogle_FilesMaster
from scripts.artifacts.FilesByGoogle_SearchHistory import get_FilesByGoogle_SearchHistory
from scripts.artifacts.gboard import get_gboardCache
from scripts.artifacts.googleNowPlaying import get_googleNowPlaying
from scripts.artifacts.googlePlaySearches import get_googlePlaySearches
from scripts.artifacts.googleQuickSearchbox import get_quicksearch
from scripts.artifacts.googleQuickSearchboxRecent import get_quicksearch_recent
from scripts.artifacts.installedappsGass import get_installedappsGass
from scripts.artifacts.installedappsLibrary import get_installedappsLibrary
from scripts.artifacts.installedappsVending import get_installedappsVending 
from scripts.artifacts.pSettings import get_pSettings
from scripts.artifacts.packageInfo import get_package_info
from scripts.artifacts.recentactivity import get_recentactivity
from scripts.artifacts.lgRCS import get_lgRCS
from scripts.artifacts.scontextLog import get_scontextLog
from scripts.artifacts.settingsSecure import get_settingsSecure
from scripts.artifacts.siminfo import get_siminfo
from scripts.artifacts.smanagerCrash import get_smanagerCrash
from scripts.artifacts.smanagerLow import get_smanagerLow
from scripts.artifacts.smembersAppInv import get_smembersAppInv
from scripts.artifacts.smembersEvents import get_smembersEvents
from scripts.artifacts.smsmms import get_sms_mms
from scripts.artifacts.smyfilesRecents import get_smyfilesRecents
from scripts.artifacts.smyFiles import get_smyFiles
from scripts.artifacts.smyfilesStored import get_smyfilesStored
from scripts.artifacts.swellbeing import get_swellbeing
from scripts.artifacts.Turbo import get_Turbo
from scripts.artifacts.usageapps import get_usageapps
from scripts.artifacts.usagestats import get_usagestats
from scripts.artifacts.userDict import get_userDict
from scripts.artifacts.Viber import get_Viber
from scripts.artifacts.walStrings import get_walStrings
from scripts.artifacts.wellbeing import get_wellbeing
from scripts.artifacts.wellbeingURLs import get_wellbeingURLs
from scripts.artifacts.wellbeingaccount import get_wellbeingaccount
from scripts.artifacts.wifiHotspot import get_wifiHotspot
from scripts.artifacts.wifiProfiles import get_wifiProfiles
from scripts.artifacts.Xender import get_Xender
from scripts.artifacts.Zapya import get_Zapya

from scripts.ilapfuncs import *

# GREP searches for each module
# Format is Key='modulename', Value=Tuple('Module Pretty Name', 'regex_term')
#   regex_term can be a string or a list/tuple of strings
# Here modulename must match the get_xxxxxx function name for that module. 
# For example: If modulename='profit', function name must be get_profit(..)
# Don't forget to import the module above!!!!

tosearch = {
    'adb_hosts':('ADB Hosts', '**/data/misc/adb/adb_keys'),
    'etc_hosts':('Etc Hosts', '**/system/etc/hosts'),
    'BashHistory':('Bash History', '**/.bash_history'),
    'ChessWithFriends':('Chats', ('**/com.zynga.chess.googleplay/databases/wf_database.sqlite', '**/com.zynga.chess.googleplay/db/wf_database.sqlite')),
    'WordsWithFriends':('Chats', '**/com.zynga.words/db/wf_database.sqlite'),
    'accounts_ce': ('Accounts_ce', '**/system_ce/*/accounts_ce.db'),
    'accounts_ce_authtokens':('Accounts_ce', '**/accounts_ce.db'),
    'accounts_de': ('Accounts_de', '**/system_de/*/accounts_de.db'),
    'appicons':('Installed Apps', '**/data/com.google.android.apps.nexuslauncher/databases/app_icons.db*'),
    'build':('Device Info', '**/vendor/build.prop'),
    'calllog': ('Call Logs', '**/com.android.providers.contacts/databases/calllog.db'),
    'Cast':('Cast', '**/com.google.android.gms/databases/cast.db'),
    'Cello': ('Google Docs', ('*/com.google.android.apps.docs/app_cello/*/cello.db*', '*/com.google.android.apps.docs/files/shiny_blobs/blobs/*')),
    'chrome':('Chrome', ('**/app_chrome/Default/History*', '**/app_sbrowser/Default/History*')),
    'chromeBookmarks':('Chrome', ('**/app_chrome/Default/Bookmarks*', '**/app_sbrowser/Default/Bookmarks*')),
    'chromeCookies':('Chrome', ('**/app_chrome/Default/Cookies*', '**/app_sbrowser/Default/Cookies*')),
    'chromeDownloads':('Chrome', ('**/app_chrome/Default/History*', '**/app_sbrowser/Default/History*')),
    'chromeLoginData':('Chrome', ('**/app_chrome/Default/Login Data*', '**/app_sbrowser/Default/Login Data*')),
    'chromeOfflinePages':('Chrome', ('**/app_chrome/Default/Offline Pages/metadata/OfflinePages.db*', '**/app_sbrowser/Default/Offline Pages/metadata/OfflinePages.db*')),
    'chromeSearchTerms':('Chrome', ('**/app_chrome/Default/History*', '**/app_sbrowser/Default/History*')),
    'chromeTopSites':('Chrome', ('**/app_chrome/Default/Top Sites*', '**/app_sbrowser/Default/Top Sites*')),
    'chromeWebsearch':('Chrome', ('**/app_chrome/Default/History*', '**/app_sbrowser/Default/History*')),
    'cmh':('Samsung_CMH', '**/cmh.db'),
    'DocList':('Google Docs', '**/com.google.android.apps.docs/databases/DocList.db*'),
    'emulatedSmeta':('Emulated Storage Metadata', '**/com.google.android.providers.media.module/databases/external.db*'),
    'FilesByGoogle_FilesMaster':('Files By Google', '**/com.google.android.apps.nbu.files/databases/files_master_database'),
    'FilesByGoogle_SearchHistory':('Files By Google','**/com.google.android.apps.nbu.files/databases/search_history_database'),
    'gboardCache':('Gboard Keyboard', '**/com.google.android.inputmethod.latin/databases/trainingcache*.db'),
    'googleNowPlaying':('Now Playing', '**/com.google.intelligence.sense/db/history_db*'),
    'googlePlaySearches':('Google Play', '**/com.android.vending/databases/suggestions.db*'),
    'installedappsGass':('Installed Apps', '**/com.google.android.gms/databases/gass.db'),
    'installedappsLibrary': ('Installed Apps', '**/com.android.vending/databases/library.db'),
    'installedappsVending': ('Installed Apps', '**/com.android.vending/databases/localappstate.db'),
    'pSettings':('Device Info', '**/com.google.android.gsf/databases/googlesettings.db*'),
    'package_info': ('Installed Apps', '**/system/packages.xml'),
    'quicksearch':('Google Now & QuickSearch', '**/com.google.android.googlequicksearchbox/app_session/*.binarypb'),
    'quicksearch_recent':('Google Now & QuickSearch', '**/com.google.android.googlequicksearchbox/files/recently/*'),
    'recentactivity':('Recent Activity', '**/system_ce/*'),
    'lgRCS':('RCS Chats', '*/mmssms.db*'),
    'scontextLog':('App Interaction', '**/com.samsung.android.providers.context/databases/ContextLog.db'),
    'settingsSecure':('Device Info', '**/system/users/*/settings_secure.xml'),
    'siminfo':('Device Info', '**/user_de/*/com.android.providers.telephony/databases/telephony.db'),
    'smanagerCrash':('App Interaction', '**/com.samsung.android.sm/databases/sm.db'),
    'smanagerLow':('App Interaction', '**/com.samsung.android.sm/databases/lowpowercontext-system-db'),
    'smembersAppInv':('App Interaction', '**/com.samsung.oh/databases/com_pocketgeek_sdk_app_inventory.db'),
    'smembersEvents':('App Interaction', '**/com.samsung.oh/databases/com_pocketgeek_sdk.db'),
    'sms_mms':('SMS & MMS', '**/com.android.providers.telephony/databases/mmssms*'), # Get mmssms.db, mms-wal.db
    'smyfilesRecents':('Media Metadata', '**/com.sec.android.app.myfiles/databases/myfiles.db'),
    'smyFiles':('Media Metadata', '**/com.sec.android.app.myfiles/databases/MyFiles*.db*'),
    'smyfilesStored':('Media Metadata', '**/com.sec.android.app.myfiles/databases/FileCache.db'),
    'swellbeing': ('Wellbeing', '**/com.samsung.android.forest/databases/dwbCommon.db*'),
    'Turbo': ('Battery', '**/com.google.android.apps.turbo/databases/turbo.db*'),
    'usageapps': ('App Interaction', '**/com.google.android.as/databases/reflection_gel_events.db*'),
    'usagestats':('Usage Stats', ('**/system/usagestats/*', '**/system_ce/*/usagestats*')), # fs: matches only 1st level folders under usagestats/, tar/zip matches every single file recursively under usagestats/
    'userDict':('User Dictionary', '**/com.android.providers.userdictionary/databases/user_dict.db*'),
    'Viber':('SMS & MMS', '**/com.viber.voip/databases/*'),
    'walStrings':('SQLite Journaling', ('**/*-wal', '**/*-journal')),
    'wellbeing': ('Wellbeing', '**/com.google.android.apps.wellbeing/databases/app_usage*'),
    'wellbeingURLs': ('Wellbeing', '**/com.google.android.apps.wellbeing/databases/app_usage*'), # Get app_usage & app_usage-wal
    'wellbeingaccount': ('Wellbeing', '**/com.google.android.apps.wellbeing/files/AccountData.pb'),
    'wifiHotspot':('WiFi Profiles', ('**/misc/wifi/softap.conf', '**/misc**/apexdata/com.android.wifi/WifiConfigStoreSoftAp.xml')),
    'wifiProfiles':('WiFi Profiles', ('**/misc/wifi/WifiConfigStore.xml', '**/misc**/apexdata/com.android.wifi/WifiConfigStore.xml')),
    'Xender':('File Transfer', '**/cn.xender/databases/trans-history-db*'), # Get trans-history-db and trans-history-db-wal
    'Zapya':('File Transfer', '**/com.dewmobile.kuaiya.play/databases/transfer20.db'),
    }

slash = '\\' if is_platform_windows() else '/'

def process_artifact(files_found, artifact_func, artifact_name, seeker, report_folder_base, wrap_text):
    ''' Perform the common setup for each artifact, ie, 
        1. Create the report folder for it
        2. Fetch the method (function) and call it
        3. Wrap processing function in a try..except block

        Args:
            files_found: list of files that matched regex

            artifact_func: method to call

            artifact_name: Pretty name of artifact

            seeker: FileSeeker object to pass to method
            
            wrap_text: whether the text data will be wrapped or not using textwrap.  Useful for tools that want to parse the data.
    '''
    logfunc('{} [{}] artifact executing'.format(artifact_name, artifact_func))
    report_folder = os.path.join(report_folder_base, artifact_name) + slash
    try:
        if os.path.isdir(report_folder):
            pass
        else:
            os.makedirs(report_folder)
    except Exception as ex:
        logfunc('Error creating {} report directory at path {}'.format(artifact_name, report_folder))
        logfunc('Reading {} artifact failed!'.format(artifact_name))
        logfunc('Error was {}'.format(str(ex)))
        return
    try:
        method = globals()['get_' + artifact_func]
        method(files_found, report_folder, seeker, wrap_text)
    except Exception as ex:
        logfunc('Reading {} artifact had errors!'.format(artifact_name))
        logfunc('Error was {}'.format(str(ex)))
        logfunc('Exception Traceback: {}'.format(traceback.format_exc()))
        return

    logfunc('{} [{}] artifact completed'.format(artifact_name, artifact_func))
