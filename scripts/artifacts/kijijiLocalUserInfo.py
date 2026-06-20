# pylint: disable=W0613
__artifacts_v2__ = {
    "get_kijijiLocalUserInfo": {
        "name": "kijijiLocalUserInfo",
        "description": "Kijiji Local User Information",
        "author": "Terry Chabot (Krypterry)",
        "creation_date": "2022-05-13",
        "last_update_date": "2022-05-13",
        "requirements": "None",
        "category": "Kijiji",
        "notes": "",
        "paths": ('*/com.ebay.kijiji.ca/shared_prefs/LoginData.xml',),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "user",
    }
}

import xml.etree.ElementTree as ET

from scripts.ilapfuncs import artifact_processor, logfunc

userEmailXPath = "./string/[@name='UserEmailAddress']"
loggedInUserXPath = "./string/[@name='LoggedInAsUser']"
userDisplayNameXPath = "./string/[@name='UserDisplayName']"
eBayUserIdXPath = "./string/[@name='userEbayId{userEmailAddressPlaceholder}']"


def GetFirstChild(element):
    return element[0].text if len(element) else ''


def TryGetStringValue(root, xPathExpression):
    elems = root.findall(xPathExpression)
    return GetFirstChild(elems)


@artifact_processor
def get_kijijiLocalUserInfo(files_found, report_folder, seeker, wrap_text):
    source_path = str(files_found[0])
    logfunc(f'XML file {source_path} is being interrogated...')

    root = ET.parse(source_path).getroot()
    userEmailAddress = TryGetStringValue(root, userEmailXPath)  # May be available when logged-in/out.
    loggedInAsUser = TryGetStringValue(root, loggedInUserXPath)
    userDisplayName = TryGetStringValue(root, userDisplayNameXPath)

    # Build a unique user XPath expression in order to obtain their eBay user Id.
    userEbayId = TryGetStringValue(root, eBayUserIdXPath.format(userEmailAddressPlaceholder=userEmailAddress))

    data_list = [(userEmailAddress, userEbayId, userDisplayName, loggedInAsUser)]
    data_headers = ('User Email', 'User Ebay ID', 'User Display Name', 'Logged In User')
    return data_headers, data_list, source_path
