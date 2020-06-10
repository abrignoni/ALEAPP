# To add a new artifact module, import it here as shown below:
#     from scripts.artifacts.fruitninja import get_fruitninja
# Also add the grep search for that module using the same name
# to the 'tosearch' data structure.

import traceback

from scripts.artifacts.accounts_ce import get_accounts_ce
from scripts.artifacts.accounts_ce_authtokens import get_accounts_ce_authtokens
from scripts.artifacts.accounts_de import get_accounts_de
from scripts.artifacts.build import get_build
from scripts.artifacts.calllog import get_calllog
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
from scripts.artifacts.googleNowPlaying import get_googleNowPlaying
from scripts.artifacts.googleQuickSearchbox import get_quicksearch
from scripts.artifacts.googleQuickSearchboxRecent import get_quicksearch_recent
from scripts.artifacts.googlePlaySearches import get_googlePlaySearches
from scripts.artifacts.installedappsGass import get_installedappsGass
from scripts.artifacts.installedappsVending import get_installedappsVending
from scripts.artifacts.installedappsLibrary import get_installedappsLibrary
from scripts.artifacts.journalStrings import get_journalStrings 
from scripts.artifacts.pSettings import get_pSettings
from scripts.artifacts.recentactivity import get_recentactivity
from scripts.artifacts.scontextLog import get_scontextLog
from scripts.artifacts.settingsSecure import get_settingsSecure
from scripts.artifacts.siminfo import get_siminfo
from scripts.artifacts.smanagerCrash import get_smanagerCrash
from scripts.artifacts.smanagerLow import get_smanagerLow
from scripts.artifacts.smembersEvents import get_smembersEvents
from scripts.artifacts.smembersAppInv import get_smembersAppInv
from scripts.artifacts.smsmms import get_sms_mms
from scripts.artifacts.smyfilesRecents import get_smyfilesRecents
from scripts.artifacts.smyfilesStored import get_smyfilesStored
from scripts.artifacts.usageapps import get_usageapps
from scripts.artifacts.usagestats import get_usagestats
from scripts.artifacts.userDict import get_userDict
from scripts.artifacts.walStrings import get_walStrings
from scripts.artifacts.wellbeing import get_wellbeing
from scripts.artifacts.swellbeing import get_swellbeing
from scripts.artifacts.wellbeingaccount import get_wellbeingaccount
from scripts.artifacts.wifiProfiles import get_wifiProfiles
from scripts.artifacts.ChessWithFriends import get_ChessWithFriends
from scripts.artifacts.WordsWithFriends import get_WordsWithFriends

from scripts.ilapfuncs import *

# GREP searches for each module
# Format is Key='modulename', Value=Tuple('Module Pretty Name', 'regex_term')
#   regex_term can be a string or a list/tuple of strings
# Here modulename must match the get_xxxxxx function name for that module. 
# For example: If modulename='profit', function name must be get_profit(..)
# Don't forget to import the module above!!!!

tosearch = {
    'wellbeing': ('Wellbeing', '**/com.google.android.apps.wellbeing/databases/app_usage*'), # Get app_usage & app_usage-wal
    'wellbeingaccount': ('Wellbeing', '**/com.google.android.apps.wellbeing/files/AccountData.pb'),
    'swellbeing': ('Wellbeing', '**/com.samsung.android.forest/databases/dwbCommon.db*'),
    'usageapps': ('App Interaction', '**/com.google.android.as/databases/reflection_gel_events.db*'),
    'usagestats':('Usage Stats', '**/system/usagestats/*'), # fs: matches only 1st level folders under usagestats/, tar/zip matches every single file recursively under usagestats/
    'recentactivity':('Recent Activity', '**/system_ce/*'),
    'installedappsGass':('Installed Apps', '**/com.google.android.gms/databases/gass.db'),
    'installedappsVending': ('Installed Apps', '**/com.android.vending/databases/localappstate.db'),
    'installedappsLibrary': ('Installed Apps', '**/com.android.vending/databases/library.db'),
    'calllog': ('Call Logs', '**/com.android.providers.contacts/databases/calllog.db'),
    'accounts_de': ('Accounts_de', '**/system_de/*/accounts_de.db'),
    'accounts_ce': ('Accounts_ce', '**/system_ce/*/accounts_ce.db'),
    'accounts_ce_authtokens':('Accounts_ce', '**/accounts_ce.db'),
    'cmh':('Samsung_CMH', '**/cmh.db'),
    'sms_mms':('SMS & MMS', '**/com.android.providers.telephony/databases/mmssms*'), # Get mmssms.db, mms-wal.db
    'chrome':('Chrome', ('**/app_chrome/Default/History*', '**/app_sbrowser/Default/History*')),
    'chromeSearchTerms':('Chrome', ('**/app_chrome/Default/History*', '**/app_sbrowser/Default/History*')),
    'chromeDownloads':('Chrome', ('**/app_chrome/Default/History*', '**/app_sbrowser/Default/History*')),
    'chromeLoginData':('Chrome', ('**/app_chrome/Default/Login Data*', '**/app_sbrowser/Default/Login Data*')),
    'chromeBookmarks':('Chrome', ('**/app_chrome/Default/Bookmarks*', '**/app_sbrowser/Default/Bookmarks*')),
    'chromeCookies':('Chrome', ('**/app_chrome/Default/Cookies*', '**/app_sbrowser/Default/Cookies*')),
    'chromeTopSites':('Chrome', ('**/app_chrome/Default/Top Sites*', '**/app_sbrowser/Default/Top Sites*')),
    'chromeWebsearch':('Chrome', ('**/app_chrome/Default/History*', '**/app_sbrowser/Default/History*')),
    'chromeOfflinePages':('Chrome', ('**/app_chrome/Default/Offline Pages/metadata/OfflinePages.db*', '**/app_sbrowser/Default/Offline Pages/metadata/OfflinePages.db*')),
    'quicksearch_recent':('Google Now & QuickSearch', '**/com.google.android.googlequicksearchbox/files/recently/*'),
    'quicksearch':('Google Now & QuickSearch', '**/com.google.android.googlequicksearchbox/app_session/*.binarypb'),
    'googleNowPlaying':('Now Playing', '**/com.google.intelligence.sense/db/history_db*'),
    'googlePlaySearches':('Google Play', '**/com.android.vending/databases/suggestions.db*'),
    'siminfo':('Device Info', '**/user_de/*/com.android.providers.telephony/databases/telephony.db'),
    'build':('Device Info', '**/vendor/build.prop'),
    'userDict':('User Dictionary', '**/com.android.providers.userdictionary/databases/user_dict.db*'),
    'pSettings':('Device Info', '**/com.google.android.gsf/databases/googlesettings.db*'),
    'settingsSecure':('Device Info', '**/system/users/*/settings_secure.xml'),
    'wifiProfiles':('WiFi Profiles', '**/misc/wifi/WifiConfigStore.xml'),
    'journalStrings':('SQLite Journaling', '**/*-journal'),
    'walStrings':('SQLite Journaling', '**/*-wal'),
    'smyfilesRecents':('Media Metadata', '**/com.sec.android.app.myfiles/databases/myfiles.db'),
    'smyfilesStored':('Media Metadata', '**/com.sec.android.app.myfiles/databases/FileCache.db'),
    'smembersAppInv':('App Interaction', '**/com.samsung.oh/databases/com_pocketgeek_sdk_app_inventory.db'),
    'smembersEvents':('App Interaction', '**/com.samsung.oh/databases/com_pocketgeek_sdk.db'),
    'smanagerLow':('App Interaction', '**/com.samsung.android.sm/databases/lowpowercontext-system-db'),
    'smanagerCrash':('App Interaction', '**/com.samsung.android.sm/databases/sm.db'),
    'scontextLog':('App Interaction', '**/com.samsung.android.providers.context/databases/ContextLog.db'),
    'ChessWithFriends':('Chats', '**/com.zynga.chess.googleplay/databases/wf_database.sqlite'),
    'ChessWithFriends':('Chats', '**/com.zynga.chess.googleplay/db/wf_database.sqlite'),
    'WordsWithFriends':('Chats', '**/com.zynga.words/db/wf_database.sqlite')
    }
'''
tosearch = {'journalStrings':('SQLite Journaling', '**/*-journal'),
            'walStrings':('SQLite Journaling', '**/*-wal')
            }
'''
#'walStrings':('SQLite Journaling - Strings', '**/*-wal')

slash = '\\' if is_platform_windows() else '/'

def process_artifact(files_found, artifact_func, artifact_name, seeker, report_folder_base):
    ''' Perform the common setup for each artifact, ie, 
        1. Create the report folder for it
        2. Fetch the method (function) and call it
        3. Wrap processing function in a try..except block

        Args:
            files_found: list of files that matched regex

            artifact_func: method to call

            artifact_name: Pretty name of artifact

            seeker: FileSeeker object to pass to method
    '''
    logfunc('{} artifact executing'.format(artifact_name))
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
        method(files_found, report_folder, seeker)
    except Exception as ex:
        logfunc('Reading {} artifact had errors!'.format(artifact_name))
        logfunc('Error was {}'.format(str(ex)))
        logfunc('Exception Traceback: {}'.format(traceback.format_exc()))
        return

    logfunc('{} artifact completed'.format(artifact_name))
