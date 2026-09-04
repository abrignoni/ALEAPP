__artifacts_v2__ = {
    "install_sessions": {
        "name": "Package Install Sessions",
        "description": "Application install sessions the package installer still had on record, "
                       "with the package being installed, the app that started the install, the "
                       "size staged and the times the session was created, updated and committed.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-03",
        "last_update_date": "2026-09-03",
        "requirements": "none",
        "category": "Installed Apps",
        "notes": "Read from install_sessions.xml in the system folder, ABX binary XML on modern "
                 "releases and plain XML on older ones. One row per session element. Created, "
                 "Updated and Committed are the createdMillis, updatedMillis and committedMillis "
                 "attributes in Unix milliseconds.\n"
                 "Installer Package is the app that owns the session and Initiating Package is "
                 "the app that started it; for a store install both name the store, while a "
                 "session started from a file manager or over a debug bridge names that source "
                 "instead. Originating UID is recorded as stored and is -1 where the platform "
                 "kept none.\n"
                 "Install Reason, Install Location, Package Source and Mode are integers the "
                 "platform defines and are reported as stored. Two attributes are read under the "
                 "spellings the platform writes, installRason and updateOwnererPackageName, and "
                 "the corrected spellings are accepted as well so the artifact keeps working if "
                 "they change.\n"
                 "A session is a record of an install that was staged, not proof that the app "
                 "was installed and run: Applied and Failed report the outcome the platform "
                 "stored, and Error Message is blank unless the platform recorded a failure, which it "
                 "had not on any tested image. On an image whose sessions all come from one store "
                 "for one user, User ID, Installer UID and Update Owner Package each hold a single "
                 "value, and Size Bytes is -1 where the platform stored no staged size; all four are "
                 "kept as columns because they separate sessions on a device with more than one "
                 "user or installer. "
                 "A session can remain here after it finished. The file holds the "
                 "sessions the installer had not yet cleaned up, so it is a recent window rather "
                 "than a full install history.",
        "paths": ('*/system/install_sessions.xml',),
        "output_types": "standard",
        "artifact_icon": "package",
        "sample_data": {
            "adams_ss134dl_a03s_logical": "0 rows",
            "adams_ss135dl_a13": "Android 13 | 21 rows",
            "anne_a15": "Android 15 | 29 rows",
            "cookbook_a11": "Android 11 | 0 rows",
            "df020_mavic_pro_android": "0 rows",
            "emu_a15_oss_v1": "Android 15 | 0 rows",
            "falken_a326u_a13": "Android 13 | 30 rows",
            "galaxys10_a10": "Android 10 | 0 rows",
            "hc_pixel8pro_a16": "Android 16 | 43 rows",
            "hc_pixel8pro_a17": "Android 17 | 32 rows",
            "hc_pixel8pro_a17_ail": "Android 17 | 0 rows",
            "kevin_pocox7_a15": "Android 15 | 49 rows",
            "pixel3_a11": "Android 11 | 1 row",
            "pixel3_a12": "Android 12 | 26 rows",
            "pixel7a_a14": "Android 14 | 24 rows",
            "russell_a14": "Android 14 | 31 rows",
            "russell_pixel6a_a13": "Android 13 | 3 rows",
            "s20fe_a13": "Android 13 | 30 rows",
            "samsunga53_a14": "Android 14 | 0 rows",
            "samsungs20_a13": "Android 13 | 0 rows",
            "sharon_a13": "Android 13 | 3 rows",
            "sharon_a14": "Android 14 | 0 rows",
            "userb2_a13": "Android 13 | 3 rows",
        },
    },
}

import os
import pathlib
import xml.etree.ElementTree as ET

from scripts.ilapfuncs import abxread, artifact_processor, checkabx, convert_unix_ts_to_utc, logfunc


def _root(path):
    """The XML root, reading ABX binary XML or plain XML, and tolerating a file that carries
    more than one root element, which both forms do for some of these records."""
    if checkabx(path):
        try:
            return abxread(path, False).getroot()
        except Exception:  # pylint: disable=broad-except
            return abxread(path, True).getroot()
    try:
        return ET.parse(path).getroot()
    except ET.ParseError:
        text = pathlib.Path(path).read_text(encoding='utf-8', errors='replace')
        if text.lstrip().startswith('<?xml'):
            text = text.split('?>', 1)[1]
        return ET.fromstring(f'<root>{text}</root>')


def _ms(value):
    """Unix milliseconds as an aware UTC datetime; 0 and empty are reported as blank."""
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        return ''
    if number <= 0:
        return ''
    return convert_unix_ts_to_utc(number)


def _first(element, *names):
    """The first of these attributes the element carries, so a corrected platform spelling
    is read as well as the one currently written."""
    for name in names:
        value = element.get(name)
        if value is not None:
            return value
    return ''


@artifact_processor
def install_sessions(context):
    data_headers = (
        ('Created', 'datetime'),
        ('Updated', 'datetime'),
        ('Committed', 'datetime'),
        'App Package',
        'App Label',
        'Installer Package',
        'Initiating Package',
        'Update Owner Package',
        'User ID',
        'Originating UID',
        'Installer UID',
        'Session ID',
        'Parent Session ID',
        'Size Bytes',
        'Staging Directory',
        'Install Reason (as stored)',
        'Install Location (as stored)',
        'Package Source (as stored)',
        'Applied',
        'Failed',
        'Error Message',
        'Source File',
    )
    data_list = []
    sources = []

    for file_found in context.get_files_found():
        file_found = str(file_found)
        if os.path.isdir(file_found) or os.path.basename(file_found) != 'install_sessions.xml':
            continue
        try:
            root = _root(file_found)
        except Exception as error:  # pylint: disable=broad-except
            logfunc(f'Install Sessions: could not read {os.path.basename(file_found)}: {error}')
            continue
        rows = 0
        for session in root.iter('session'):
            data_list.append((
                _ms(session.get('createdMillis')),
                _ms(session.get('updatedMillis')),
                _ms(session.get('committedMillis')),
                session.get('appPackageName', ''),
                session.get('appLabel', ''),
                session.get('installerPackageName', ''),
                session.get('installInitiatingPackageName', ''),
                _first(session, 'updateOwnererPackageName', 'updateOwnerPackageName'),
                session.get('userId', ''),
                session.get('originatingUid', ''),
                session.get('installerUid', ''),
                session.get('sessionId', ''),
                session.get('parentSessionId', ''),
                session.get('sizeBytes', ''),
                session.get('sessionStageDir', ''),
                _first(session, 'installRason', 'installReason'),
                session.get('installLocation', ''),
                session.get('packageSource', ''),
                session.get('isApplied', ''),
                session.get('isFailed', ''),
                session.get('errorMessage', ''),
                context.get_relative_path(file_found),
            ))
            rows += 1
        if rows:
            sources.append(file_found)

    return data_headers, data_list, '\n'.join(sources)
