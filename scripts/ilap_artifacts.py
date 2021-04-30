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
from scripts.artifacts.chromeMediaHistory import get_chromeMediaHistory
from scripts.artifacts.chromeNetworkActionPredictor import get_chromeNetworkActionPredictor
from scripts.artifacts.chromeOfflinePages import get_chromeOfflinePages
from scripts.artifacts.chromeSearchTerms import get_chromeSearchTerms
from scripts.artifacts.chromeTopSites import get_chromeTopSites
from scripts.artifacts.chromeWebsearch import get_chromeWebsearch
from scripts.artifacts.cmh import get_cmh
from scripts.artifacts.DocList import get_DocList
from scripts.artifacts.emulatedSmeta import get_emulatedSmeta
from scripts.artifacts.FacebookMessenger import get_FacebookMessenger
from scripts.artifacts.fitbitExercise import get_fitbitExercise
from scripts.artifacts.fitbitSleep import get_fitbitSleep
from scripts.artifacts.fitbitSocial import get_fitbitSocial
from scripts.artifacts.fitbitWalk import get_fitbitWalk
from scripts.artifacts.fitbitHeart import get_fitbitHeart
from scripts.artifacts.fitbitActivity import get_fitbitActivity
from scripts.artifacts.gboard import get_gboardCache
from scripts.artifacts.googlePhotos import get_googlePhotos
from scripts.artifacts.googleNowPlaying import get_googleNowPlaying
from scripts.artifacts.googlePlaySearches import get_googlePlaySearches
from scripts.artifacts.googleQuickSearchbox import get_quicksearch
from scripts.artifacts.googleQuickSearchboxRecent import get_quicksearch_recent
from scripts.artifacts.imo import get_imo
from scripts.artifacts.installedappsGass import get_installedappsGass
from scripts.artifacts.installedappsLibrary import get_installedappsLibrary
from scripts.artifacts.installedappsVending import get_installedappsVending 
from scripts.artifacts.pSettings import get_pSettings
from scripts.artifacts.packageInfo import get_package_info
from scripts.artifacts.permissions import get_permissions
from scripts.artifacts.recentactivity import get_recentactivity
from scripts.artifacts.lgRCS import get_lgRCS
from scripts.artifacts.roles import get_roles
from scripts.artifacts.runtimePerms import get_runtimePerms
from scripts.artifacts.scontextLog import get_scontextLog
from scripts.artifacts.settingsSecure import get_settingsSecure
from scripts.artifacts.shareit import get_shareit
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
from scripts.artifacts.tangomessage import get_tangomessage
from scripts.artifacts.tikTok import get_tikTok
from scripts.artifacts.Turbo import get_Turbo
from scripts.artifacts.usageapps import get_usageapps
from scripts.artifacts.usagestats import get_usagestats
from scripts.artifacts.usagestatsVersion import get_usagestatsVersion
from scripts.artifacts.userDict import get_userDict
from scripts.artifacts.Viber import get_Viber
from scripts.artifacts.Whatsapp import get_Whatsapp
from scripts.artifacts.walStrings import get_walStrings
from scripts.artifacts.wellbeing import get_wellbeing
from scripts.artifacts.wellbeingURLs import get_wellbeingURLs
from scripts.artifacts.wellbeingaccount import get_wellbeingaccount
from scripts.artifacts.wifiHotspot import get_wifiHotspot
from scripts.artifacts.wifiProfiles import get_wifiProfiles
from scripts.artifacts.Xender import get_Xender
from scripts.artifacts.Zapya import get_Zapya
from scripts.artifacts.contacts import get_contacts
from scripts.artifacts.Oruxmaps import get_Oruxmaps
from scripts.artifacts.vlcMedia import get_vlcMedia
from scripts.artifacts.vlcThumbs import get_vlcThumbs
from scripts.artifacts.textnow import get_textnow
from scripts.artifacts.skype import get_skype
from scripts.artifacts.line import get_line
from scripts.artifacts.calllogs import get_calllogs
from scripts.artifacts.cachelocation import get_cachelocation
from scripts.artifacts.browserlocation import get_browserlocation
from scripts.artifacts.googlemaplocation import get_googlemaplocation
from scripts.artifacts.packageGplinks import get_packageGplinks
from scripts.artifacts.teams import get_teams 
from scripts.artifacts.LBC_userlog import get_LBC_userlog
from scripts.artifacts.LBC_userlog_details import get_LBC_userlog_details

from scripts.ilapfuncs import *

# GREP searches for each module
# Format is Key='modulename', Value=Tuple('Module Pretty Name', 'regex_term')
#   regex_term can be a string or a list/tuple of strings
# Here modulename must match the get_xxxxxx function name for that module. 
# For example: If modulename='profit', function name must be get_profit(..)
# Don't forget to import the module above!!!!

tosearch = {
    'usagestatsVersion':('Usage Stats', ('*/system/usagestats/*/version', '*/system_ce/*/usagestats/version')),
    'LBC_userlog': ('LBC', ('*/LBC_userlog.csv')),
    'LBC_userlog_details': ('LBC', ('*/LBC_userlog_details.csv')),
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
