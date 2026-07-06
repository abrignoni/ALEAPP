# pylint: disable=W0613
__artifacts_v2__ = {
    "get_smyfiles_trash": {
        "name": "My Files Trash",
        "description": "Shows Original Location and Deletion Timestamp of files/folders within My Files Trash",
        "author": "@PensiveHike",
        "creation_date": "2024-06-05",
        "last_update_date": "2024-06-05",
        "requirements": "none",
        "category": "My Files",
        "notes": "Timestamp corroborated with My Files Operation History database",
        "paths": ('*/com.sec.android.app.myfiles/files/trash/*', '*/.Trash/com.sec.android.app.myfiles/*'),
        "output_types": "standard",
        "artifact_icon": "trash",
    }
}

# Example trash paths the metadata is parsed out of:
# .../data/com.sec.android.app.myfiles/files/trash/<id>/<deltime>/storage/emulated/0/Download/.!%#@$/Untitled.mov
# .../Android/.Trash/com.sec.android.app.myfiles/<id>/<deltime>/storage/emulated/0/DCIM/Camera/.!%#@$/20240502_120754.mp4

import datetime
import os

from scripts.ilapfuncs import artifact_processor, check_in_media

SEPARATOR = ".!%#@$"
APP = "com.sec.android.app.myfiles"


def _ms_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError, TypeError):
        return ''


@artifact_processor
def get_smyfiles_trash(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        norm = file_found.replace('\\', '/')

        # Only process files / empty folders at the end of the chain, not mid-chain folders
        if SEPARATOR not in norm or norm.endswith(SEPARATOR):
            continue
        if not (os.path.isfile(file_found) or (os.path.isdir(file_found) and not os.listdir(file_found))):
            continue

        parts = norm.split('/')
        if APP not in parts or SEPARATOR not in parts:
            continue
        app_loc = parts.index(APP)
        separator_loc = parts.index(SEPARATOR)
        path_length = len(parts)

        # Account / user id sits three segments before the app folder
        user = parts[app_loc - 3] if app_loc >= 3 else ''
        if not user.isdigit():
            user = ''

        # The deletion-time folder position depends on the trash layout version
        folder_index = 0 if '.Trash' in parts else 2
        timestamp_position = app_loc + folder_index + 2
        if timestamp_position >= separator_loc:
            continue  # indices don't line up - malformed path
        converted_timestamp = _ms_to_utc(parts[timestamp_position])

        if not source_path:
            source_path = '/'.join(parts[:timestamp_position])

        # Original location: segments between the timestamp folder and the separator
        original_location = '/' + '/'.join(parts[timestamp_position + 1:separator_loc]) + '/'

        # What was marked for deletion: a single file, or a folder and its contents
        if path_length - separator_loc - 1 == 1:
            marked_for_deletion = parts[-1]
            marked_for_deletion_contents = ''
        else:
            marked_for_deletion = '/' + parts[separator_loc + 1] + '/'
            marked_for_deletion_contents = '/' + '/'.join(parts[separator_loc + 1:])

        start = max(0, app_loc - 5)
        record_filepath = '/' + '/'.join(parts[start:])

        if os.path.isfile(file_found) and os.path.getsize(file_found) > 0:
            media = check_in_media(file_found, parts[-1])
        else:
            media = ''

        data_list.append((media, record_filepath, user, converted_timestamp, original_location,
                          marked_for_deletion, marked_for_deletion_contents))

    data_headers = (
        ('Media', 'media'), 'Record Path', 'Account', ('Marked for Deletion Timestamp', 'datetime'),
        'Original Location', 'File/Folder Marked For Deletion', 'Contents of Folder Marked for Deletion')
    return data_headers, data_list, source_path
