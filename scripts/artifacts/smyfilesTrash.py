import shutil

from scripts.artifact_report import ArtifactHtmlReport
from scripts.ilapfuncs import logfunc, tsv, timeline, is_platform_windows, media_to_html
from scripts.filetype import guess_mime
import datetime
import os

__artifacts_v2__ = {
    "smyfilesTrash": {
        "name": "My Files Trash",
        "description": "Shows Original Location and Deletion Timestamp of files/folders within My Files Trash",
        "author": "@PensiveHike",
        "version": "0.1",
        "date": "2024-06-05",
        "requirements": "none",
        "category": "My Files",
        "notes": "Timestamp corroborated with My Files Operation History database",
        "paths": ('*/com.sec.android.app.myfiles/files/trash/*', '*/.Trash/com.sec.android.app.myfiles/*'),
        "function": "get_smyfiles_trash"
    }
}

# example filepaths
# /data/media/0/Android/data/com.sec.android.app.myfiles/files/trash/%.'ar74b%a$&7rcrGZ-Y.5$QT2/1639144040510/storage/emulated/0/Download/.!%#@$/Untitled.mov
# /data/media/0/Android/.Trash/com.sec.android.app.myfiles/09b6cc33-bd68-46ee-8fbd-a147b0348f1aT3/1714648136151/storage/emulated/0/DCIM/Camera/.!%#@$/20240502_120754.mp4

platform = is_platform_windows()
if platform:
    splitter = '\\'
else:
    splitter = '/'


def relative_paths(source):
    splitted_a = source.split(splitter)
    for x in splitted_a:
        if 'LEAPP_Reports_' in x:
            report_folder = x

    splitted_b = source.split(report_folder)
    return '.' + splitted_b[1]


def modded_media_to_html(input):
    source = relative_paths(input)
    mimetype = guess_mime(input)
    if mimetype == None:
        mimetype = ''
    filename = os.path.basename(input)
    if 'video' in mimetype:
        thumb = f'<video width="320" height="240" controls="controls"><source src="{source}" type="video/mp4" preload="none">Your browser does not support the video tag.</video>'
    elif 'image' in mimetype:
        thumb = f'<a href="{source}" target="_blank"><img src="{source}"width="300"></img></a>'
    elif 'audio' in mimetype:
        thumb = f'<audio controls><source src="{source}" type="audio/ogg"><source src="{source}" type="audio/mpeg">Your browser does not support the audio element.</audio>'
    else:
        thumb = f'<a href="{source}" target="_blank"> Link to {filename} file</>'
    return thumb


def get_smyfiles_trash(files_found, report_folder, seeker, wrap_text):
    if files_found:
        separator = ".!%#@$"
        data_list = []
        html_source = ''
        # Keep Trash files together as opposed to filling the My Files report folder
        report_folder = os.path.join(report_folder, 'Trash')
        if not os.path.exists(report_folder):
            os.mkdir(report_folder)

        for file_found in files_found:
            # only want to process files or (empty) folders at the end of the chain, not folders mid-chain
            if (separator in file_found
                    and not file_found.endswith(separator)
                    and (os.path.isfile(file_found) or (os.path.isdir(file_found) and not os.listdir(file_found)))):
                parts = file_found.split('\\')
                path_length = len(parts)

                app_loc = parts.index("com.sec.android.app.myfiles")

                # GET USER FROM PATH
                user = parts[(app_loc-3)]
                try:
                    if user.isdigit():
                        pass
                except ValueError:
                    user = ''

                # version affects location of folders within filepath and their relative index
                if '.Trash' in parts:
                    folder_index = 0
                else:
                    folder_index = 2

                # GET TIMESTAMP FROM PATH (FROM TESTING THIS IS UTC)
                timestamp_position = app_loc + folder_index + 2
                timestamp = parts[timestamp_position]
                # catch timestamp error in case index count is wrong
                try:
                    converted_timestamp = datetime.datetime.utcfromtimestamp(int(timestamp) / 1000).strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    converted_timestamp = ''

                # PROVIDE SOURCE TO RESULTING HTML REPORT
                if html_source == '':
                    html_source = '\\'.join(parts[:timestamp_position])

                # GET ORIGINAL FILE/FOLDER LOCATION FROM PATH
                separator_loc = parts.index(separator)
                orig_loc_start_pos = timestamp_position + 1
                original_location = '\\'

                for i in range(orig_loc_start_pos, separator_loc, 1):
                    original_location += parts[i] + '\\'

                # GET FILES/FOLDERS MARKED FOR DELETION
                num_items = path_length - separator_loc - 1
                if num_items == 1:  # a file
                    marked_for_deletion = parts[-1]
                    marked_for_deletion_contents = ''
                else:  # a folder
                    marked_for_deletion = '\\' + parts[separator_loc + 1] + '\\'

                    marked_for_deletion_contents = '\\'
                    for i in range(separator_loc + 1, path_length, 1):
                        #print(parts[i])
                        marked_for_deletion_contents += parts[i] + '\\'
                    # remove final backslash
                    marked_for_deletion_contents = marked_for_deletion_contents[:-1]

                # GET RECORD FILEPATH FOR REPORT
                start = app_loc - 5
                record_filepath = '\\'
                for i in range(start, path_length, 1):
                    record_filepath += parts[i] + '\\'
                # remove final backslash
                record_filepath = record_filepath[:-1]

                # PROVIDE LINK TO MEDIA IN REPORT
                # If the file's parent is the separator, media does not play in report.
                # The limitation of media to html, is it places the media file within a folder titled by its parent
                # If the file Camera\ABC.jpg is deleted multiple times and has the same filename for multiple images,
                # the same image would display for each record. Therefore, have output media to unique locations based
                # on unix parent.
                # Using media_to_html does not keep this uniqueness, so have copied sections from that function
                # to use within this script
                record_for_log = ''
                if os.path.isfile(file_found) and os.path.getsize(file_found) > 0:
                    media_file_path = report_folder

                    # add folders to path and create a folder at each stage if required
                    for entry in parts[timestamp_position:-1]:
                        if entry != separator:
                            media_file_path = os.path.join(media_file_path, entry)
                            record_for_log = os.path.join(record_for_log, entry)
                            if not os.path.exists(media_file_path):
                                os.mkdir(media_file_path)
                    record_for_log = os.path.join(record_for_log, parts[-1])
                    logfunc(f"Processing {record_for_log}")

                    media_file_path = os.path.join(media_file_path, parts[-1])
                    shutil.copy2(file_found, media_file_path)

                    thumb = modded_media_to_html(media_file_path)
                else:
                    thumb = ''

                data_list.append((thumb, record_filepath, user, converted_timestamp, original_location, marked_for_deletion, marked_for_deletion_contents))

        if data_list:
            report = ArtifactHtmlReport('My Files - Trash Folder')
            report.start_artifact_report(report_folder, 'My Files - Trash Folder')
            report.add_script()
            data_headers = ('Media', 'Record Path', 'Account', 'Marked for Deletion Timestamp', 'Original Location',
                            'File/Folder Marked For Deletion', 'Contents of Folder Marked for Deletion')
            report.write_artifact_data_table(data_headers, data_list, html_source, html_no_escape=['Media'])
            report.end_artifact_report()

            tsvname = f'My Files - Trash Folder'
            tsv(report_folder, data_headers, data_list, tsvname)

            tlactivity = f'My Files - Trash Folder'
            timeline(report_folder, tlactivity, data_list, data_headers)

    else:
        logfunc('Nothing Located within My Files Trash')

