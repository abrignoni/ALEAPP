# Kijiji Local User Information
# Author:  Terry Chabot (Krypterry)
# Version: 1.0.1
# Kijiji App Version Tested: v17.5.0b172 (2022-05-06)
# Requirements:  None
#
#   Description:
#   Obtains information about the logged-in Kijiji application user.
#
#   Additional Info:
#       Kijiji.ca is a Canadian online classified advertising website and part of eBay Classifieds Group, with over 16 million unique visitors per month.
#
#       Kijiji, May 2022 <https://help.kijiji.ca/helpdesk/basics/what-is-kijiji>
#       Wikipedia - The Free Encyclopedia, May 2022, <https://en.wikipedia.org/wiki/Kijiji>
import xml.etree.ElementTree as ET

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv

userEmailXPath = "./string/[@name='UserEmailAddress']"
loggedInUserXPath = "./string/[@name='LoggedInAsUser']"
userDisplayNameXPath = "./string/[@name='UserDisplayName']"
eBayUserIdXPath = "./string/[@name='userEbayId{userEmailAddressPlaceholder}']"

def TryGetStringValue(root, xPathExpression):
    elems = root.findall(xPathExpression)
    return GetFirstChild(elems)

def GetFirstChild(element): 
    return element[0].text if len(element) else ''

def get_kijijiLocalUserInfo(files_found, report_folder, seeker, wrap_text):
    file_found = str(files_found[0])
    logfunc(f'XML file {file_found} is being interrogated...')
    report = ArtifactHtmlReport('Kijiji Local User Information')
    report.start_artifact_report(report_folder, 'Kijiji Local User Information')
    report.add_script()

    document = ET.parse(file_found)
    root = document.getroot()
    userEmailAddress = TryGetStringValue(root, userEmailXPath) # May be available when logged-in/out.
    loggedInAsUser = TryGetStringValue(root, loggedInUserXPath)
    userDisplayName = TryGetStringValue(root, userDisplayNameXPath)

    # Build a unique user XPath expression in order to obtain their eBay user Id.
    userEbayId = TryGetStringValue(root, eBayUserIdXPath.format(userEmailAddressPlaceholder = userEmailAddress))

    data_headers = ('User Email', 'User Ebay ID', 'User Display Name', 'Logged In User',)
    data_list = []
    data_list.append((userEmailAddress, userEbayId, userDisplayName, loggedInAsUser))

    report.write_artifact_data_table(data_headers, data_list, file_found)
    report.end_artifact_report()
    
    tsvname = f'Kijiji Local User Information'
    tsv(report_folder, data_headers, data_list, tsvname)    

__artifacts__ = {
        "kijijiLocalUserInfo": (
                "Kijiji Local User Information",
                ('*/com.ebay.kijiji.ca/shared_prefs/LoginData.xml'),
                get_kijijiLocalUserInfo)
}
