# To add a new artifact module, import it here as shown below:
#     from scripts.artifacts.fruitninja import get_fruitninja
# Also add the grep search for that module using the same name
# to the 'tosearch' data structure.

import traceback

from scripts.artifacts.accounts_ce import get_accounts_ce
from scripts.artifacts.accounts_ce_authtokens import get_accounts_ce_authtokens
from scripts.artifacts.accounts_de import get_accounts_de
from scripts.artifacts.calllog import get_calllog
from scripts.artifacts.cmh import get_cmh
from scripts.artifacts.installedappsGass import get_installedappsGass
from scripts.artifacts.installedappsVending import get_installedappsVending
from scripts.artifacts.installedappsLibrary import get_installedappsLibrary
from scripts.artifacts.recentactivity import get_recentactivity
from scripts.artifacts.smsmms import get_sms_mms
from scripts.artifacts.usagestats import get_usagestats
from scripts.artifacts.wellbeing import get_wellbeing
from scripts.artifacts.wellbeingaccount import get_wellbeingaccount
from scripts.artifacts.chrome import get_chrome 
from scripts.artifacts.chromeSearchTerms import get_chromeSearchTerms
from scripts.artifacts.chromeDownloads import get_chromeDownloads
from scripts.artifacts.chromeLoginData import get_chromeLoginData
from scripts.artifacts.chromeBookmarks import get_chromeBookmarks
from scripts.artifacts.chromeCookies import get_chromeCookies
from scripts.artifacts.chromeTopSites import get_chromeTopSites
from scripts.artifacts.googlequicksearchbox import get_quicksearch
from scripts.artifacts.googleNowPlaying import get_googleNowPlaying

from scripts.ilapfuncs import *

# GREP searches for each module
# Format is Key='modulename', Value=Tuple('Module Pretty Name', 'regex term')
# Here modulename must match the get_xxxxxx function name for that module. 
# For example: If modulename='profit', function name must be get_profit(..)
# Don't forget to import the module above!!!!

tosearch = {
    'wellbeing': ('Wellbeing', '**/com.google.android.apps.wellbeing/databases/app_usage*'), # Get app_usage & app_usage-wal
    'wellbeingaccount': ('Wellbeing account', '**/com.google.android.apps.wellbeing/files/AccountData.pb'),
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
    'chrome':('Chrome', '**/app_chrome/Default/History*'),
    'chromeSearchTerms':('Chrome', '**/app_chrome/Default/History*'),
    'chromeDownloads':('Chrome', '**/app_chrome/Default/History*'),
    'chromeLoginData':('Chrome', '**/app_chrome/Default/Login Data*'),
    'chromeBookmarks':('Chrome', '**/app_chrome/Default/Bookmarks*'),
    'chromeCookies':('Chrome', '**/app_chrome/Default/Cookies*'),
    'chromeTopSites':('Chrome', '**/app_chrome/Default/Top Sites*'),
    'quicksearch':('Google Now & QuickSearch', '**/com.google.android.googlequicksearchbox/files/recently/*'),
    'googleNowPlaying':('Now Playing', '**/com.google.intelligence.sense/db/history_db*')
    }
'''
tosearch = {'redditusers':'*Data/Application/*/Documents/*/accounts/*',
            'redditchats':'*Data/Application/*/Documents/*/accountData/*/chat/*/chat.sqlite'}
'''

slash = '\\' if is_platform_windows() else '/'

def process_artifact(files_found, artifact_func, artifact_name, seeker):
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
    #artifact_name_no_spaces = artifact_name.replace(" ", "")
    logfunc('{} artifact executing'.format(artifact_name))
    report_folder = os.path.join(reportfolderbase, artifact_name) + slash
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
