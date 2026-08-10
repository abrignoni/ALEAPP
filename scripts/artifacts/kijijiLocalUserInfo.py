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

import re
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


INVALID_XML_CHARS = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
BARE_AMPERSAND = re.compile(r'&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9A-Fa-f]+);)')


def _parse_xml(file_found):
    """Parse XML, recovering from invalid tokens / unescaped ampersands; empty element if unparseable."""
    try:
        return ET.parse(file_found).getroot()
    except ET.ParseError:
        with open(file_found, encoding='utf-8', errors='replace') as f:
            xml = BARE_AMPERSAND.sub('&amp;', INVALID_XML_CHARS.sub('', f.read()))
        try:
            return ET.fromstring(xml)
        except ET.ParseError as ex:
            logfunc(f'Skipping unparseable XML {file_found}: {ex}')
            return ET.Element('empty')


@artifact_processor
def get_kijijiLocalUserInfo(context):
    files_found = context.get_files_found()
    source_path = str(files_found[0])
    logfunc(f'XML file {source_path} is being interrogated...')

    root = _parse_xml(source_path)
    userEmailAddress = TryGetStringValue(root, userEmailXPath)  # May be available when logged-in/out.
    loggedInAsUser = TryGetStringValue(root, loggedInUserXPath)
    userDisplayName = TryGetStringValue(root, userDisplayNameXPath)

    # Build a unique user XPath expression in order to obtain their eBay user Id.
    userEbayId = TryGetStringValue(root, eBayUserIdXPath.format(userEmailAddressPlaceholder=userEmailAddress))

    data_list = [(userEmailAddress, userEbayId, userDisplayName, loggedInAsUser)]
    data_headers = ('User Email', 'User Ebay ID', 'User Display Name', 'Logged In User')
    return data_headers, data_list, source_path
