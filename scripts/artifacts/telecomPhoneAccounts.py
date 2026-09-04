__artifacts_v2__ = {
    "telecom_phone_accounts": {
        "name": "Telecom Phone Accounts",
        "description": "The calling accounts registered with the Android telecom service, "
                       "covering the SIM subscriptions and the apps that registered themselves to "
                       "place or receive calls, with the number and carrier label stored for each.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Device Connections",
        "notes": "Read from phone-account-registrar-state.xml in the telecom service's own "
                 "folder, ABX binary XML on modern releases and plain XML on older ones. One "
                 "row per phone_account element.\n"
                 "Component is the account_handle's component name, which names the app that "
                 "registered the account: the platform telephony component for a SIM, or a "
                 "third-party package for a calling app. Account ID is that handle's id, which "
                 "for a SIM is the subscription it belongs to. Handle and Subscription Number "
                 "are stored as tel URIs and are percent-decoded for display, so a leading plus "
                 "is shown rather than its escape; the value is otherwise as stored. Label and "
                 "Short Description are the strings the registering app supplied, and for a SIM "
                 "the description names the slot.\n"
                 "Capabilities, Highlight Color and Supported Audio Routes are integers the "
                 "platform defines and are reported as stored. Is Default Outgoing is True for "
                 "the account the default_outgoing record names for that user. The account icon "
                 "is stored here as well and is not reported. Enabled held the same value on every row "
                 "of the tested images, so it is kept as a column rather than dropped.\n"
                 "A zero length registrar file is reported as no rows and logged; it was present and "
                 "empty on one tested image. A row records that an account was registered on the "
                 "device. It does not "
                 "establish that a call was placed or received on it.",
        "paths": ('*/com.android.server.telecom/files/phone-account-registrar-state.xml',),
        "output_types": "standard",
        "artifact_icon": "phone",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 4 rows",
            "anne_a15": "Android 15 | 5 rows",
            "cookbook_a11": "Android 11 | 3 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 2 rows",
            "falken_a326u_a13": "Android 13 | 4 rows",
            "galaxys10_a10": "Android 10 | 1 row",
            "hc_pixel8pro_a16": "Android 16 | 6 rows",
            "hc_pixel8pro_a17": "Android 17 | 6 rows",
            "hc_pixel8pro_a17_ail": "Android 17 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 5 rows",
            "pixel3_a11": "Android 11 | 3 rows",
            "pixel3_a12": "Android 12 | 12 rows",
            "pixel7a_a14": "Android 14 | 8 rows",
            "russell_a14": "Android 14 | 11 rows",
            "russell_pixel6a_a13": "Android 13 | 5 rows",
            "s20fe_a13": "Android 13 | 3 rows",
            "samsunga53_a14": "Android 14 | 8 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 4 rows",
            "sharon_a14": "Android 14 | 7 rows",
            "userb2_a13": "Android 13 | 3 rows",
        },
    },
}

import os
import urllib.parse
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import abxread, artifact_processor, checkabx, logfunc


def _root(path):
    if checkabx(path):
        return abxread(path, False).getroot()
    return ET.parse(path).getroot()


def _text(element, path):
    if element is None:
        return ''
    found = element.find(path)
    if found is None:
        return ''
    return (found.text or '').strip()


def _tel(value):
    """A tel URI as stored, percent-decoded so an escaped plus reads as a plus."""
    if not value:
        return ''
    return urllib.parse.unquote(value)


def _handle_parts(account):
    """(component name, account id, user serial) from an account_handle element."""
    handle = account.find('account_handle/phone_account_handle')
    if handle is None:
        return '', '', ''
    return (_text(handle, 'component_name'), _text(handle, 'id'), _text(handle, 'user_serial_number'))


@artifact_processor
def telecom_phone_accounts(context):
    data_headers = (
        'Label',
        'Handle',
        'Subscription Number',
        'Short Description',
        'Component',
        'Account ID',
        'User Serial Number',
        'Enabled',
        'Is Default Outgoing',
        'Supported URI Schemes',
        'Capabilities (as stored)',
        'Highlight Color (as stored)',
        'Supported Audio Routes (as stored)',
        'Source File',
    )
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        if os.path.basename(file_found) != 'phone-account-registrar-state.xml':
            continue
        try:
            root = _root(file_found)
        except Exception as error:  # pylint: disable=broad-except
            logfunc(f'Telecom Phone Accounts: could not read {os.path.basename(file_found)}: {error}')
            continue

        default_handle = root.find('default_outgoing/default_outgoing_phone_account_handle')
        default_key = ('', '', '')
        if default_handle is not None:
            inner = default_handle.find('account_handle/phone_account_handle')
            if inner is not None:
                default_key = (_text(inner, 'component_name'), _text(inner, 'id'),
                               _text(default_handle, 'user_serial_number'))

        rows = 0
        for account in root.iter('phone_account'):
            component, account_id, user_serial = _handle_parts(account)
            schemes = [(value.text or '').strip()
                       for value in account.findall('supported_uri_schemes/value')]
            data_list.append((
                _text(account, 'label'),
                _tel(_text(account, 'handle')),
                _tel(_text(account, 'subscription_number')),
                _text(account, 'short_description'),
                component,
                account_id,
                user_serial,
                _text(account, 'enabled'),
                (component, account_id, user_serial) == default_key and any(default_key),
                ', '.join(s for s in schemes if s),
                _text(account, 'capabilities'),
                _text(account, 'highlight_color'),
                _text(account, 'supported_audio_routes'),
                context.get_relative_path(file_found),
            ))
            rows += 1
        if rows:
            sources.append(file_found)

    return data_headers, data_list, '\n'.join(sources)
