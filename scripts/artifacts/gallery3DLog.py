from scripts.artifact_report import ArtifactHtmlReport
import scripts.ilapfuncs as ilap
import scripts.artifacts.artGlobals as aG
import re
import sqlite3

__artifacts_v2__ = {
    "Gallery3DLog": {
        "name": "Gallery3D Log",
        "description": "Extracts Log records from Gallery 3D database",
        "author": "@PensiveHike",
        "version": "0.1",
        "date": "2024-12-10",
        "requirements": "none",
        "category": "Gallery3D",
        "notes": "Decoding scripts located within ilapfuncs. There were provided to me by Jeroen Taal,"
                 "Cheeky Monkey Forensics, Mike Lacombe. From these, I pieced together this script and added it to"
                 "ALEAPP so that everybody may benefit.",
        "paths": '*/com.sec.android.gallery3d/databases/local.db*',
        "function": "get_gallery3d_log"
    }
}

artefact_title = "Gallery3D Log"


def process_gallery3d_log(input_data):
    output_data = []
    for entry in input_data:
        log_entry = entry[3]
        if log_entry:
            # print(count, log_entry)  # good to count where in the database the problem entry occurs
            # cat = entry[0]
            # 1 Thumbnail, 2 Function: MOVE_TO_TRASH.., RESTORE.., EMPTY.., FileOpLog_ver3, 4 getApiStatusList
            # 5 cmh:150000:poi=0, 9 2147484619:completed(ND)
            ts = entry[1]
            # thumb_hash = entry[2]  # so far unable to link this to thumbnail filename
            op_type = ''
            path1 = ''
            path2 = ''
            extra = ''
            if log_entry.startswith('Thumbnail'):
                if log_entry[12:16] == '#G$E':
                    for i in log_entry.split(' '):
                        if i.startswith('#G$E'):
                            path1 = try_decode(i)
                            break
                elif len(log_entry) > 15:
                    code = log_entry[11:-16]
                    path1 = try_decode(code)
                op_type = 'Thumbnail'

            elif log_entry.startswith('[EMPTY_'):
                op_type = search_operation(log_entry)
                items = search_total(log_entry)
                extra = f'Items affected - {items}'
                location = search_location(log_entry)
                if location:
                    extra += f', Location: {location}'

            elif log_entry.startswith('[FileOpLog_ver3]'):  # [FileOpLog_ver3][type=
                results = search_file_op(log_entry)
                if results:
                    op_type = results[0]
                    path1 = results[1]
                    path2 = results[2]
                    extra = results[3]

            elif log_entry.startswith('[RESTORE'):
                op_type = search_operation(log_entry)
                path1, path2 = search_text(log_entry, 'RESTORE')

            elif log_entry.startswith('[MOVE_TO_TRASH'):
                op_type = search_operation(log_entry)
                path1, path2 = search_text(log_entry)
                # location = search_location(log_entry)
                items = search_total(log_entry)
                extra = f'Items affected - {items}'

            elif log_entry.startswith('[DELETE_'):
                op_type = search_operation(log_entry)
                path1, path2 = search_text(log_entry)

            # output_data.append((ts, op_type, path1, path2, thumb_hash, extra, log_entry))
            output_data.append((ts, op_type, path1, path2, extra, log_entry))
            # count += 1
    return output_data


def process_paths(input_data) -> str:
    """Attempt to decode data entered (either list or string) and return as a string"""
    converted_str = ''
    if type(input_data) is list:
        length = len(input_data)
        for entry in input_data:
            result = try_decode(entry)
            converted_str += result

            if length > 1 and entry != input_data[-1]:
                converted_str += ', '

        return converted_str
    else:
        converted_str = try_decode(input_data)
        return converted_str


def search_file_op(input_string):
    """Processes 'FileOpLog_ver3' entries and returns the entry as a list of details
     (Operation type, Path1, Path2, bonus material"""
    # [FileOpLog_ver3][type=move][OP_CANCEL][src_path][ #G$E34uPZ8KW+y+Ov48/pv6DL8K+ohbTlm8Llvr/r9Lrj5+GupcurnaTL8LmN2vTqmsPgr6OD ][dst_path][ #G$E2XK5HUAG8VFpcuF5KH7xHWhfyAxAktVJLAJxDT1yQVlsavBxoG7xHTDKtQx8ltFdaHA== ][total=4][success=0][fail=0][replace=0][rename_file=0][skip=2][ppp_fail(src)=0][storage_state =mounted][empty_album=false][new_album=false][src_path_null=0][msg=null]
    source_path = ''
    dest_path = ''

    # remove first and last char, then split into list
    split_string = input_string[1:-1].split('][')
    op_type = split_string[1][5:]
    op_progress = split_string[2]
    bonus_string = f'Operation status: {op_progress}'
    position = 0
    for pos in split_string:
        if pos == 'src_path':
            source_path = split_string[position + 1].strip()
            source_path = try_decode(source_path)
            if source_path[:1] == '(' and source_path[-1:] == ')':  # process encapsulates string in ()
                source_path = source_path[1:-1]
        elif pos == 'dst_path':
            dest_path = split_string[position + 1].strip()
            dest_path = try_decode(dest_path)
        elif 'total=' in pos:
            bonus_string += f", Files affected: {pos[6:]}"
        elif 'success=' in pos:
            bonus_string += f", Files succeeded: {pos[8:]}"
        elif 'fail=' in pos:
            bonus_string += f", Files failed: {pos[5:]}"
        position += 1
    output_list = [f'Operation Type: {op_type}', source_path, dest_path, bonus_string]
    return output_list


def search_fp(input_string, search_type=None):
    """Searches through the string for FP and PP sections. If found returns the contents"""
    fp_list = []
    pp_list = []
    found = False

    # restore search char is I, normally is L
    if search_type == 'RESTORE':
        pp_search = re.search('PP\[.*\] I', input_string)
    else:
        pp_search = re.search('PP\[.*\] L', input_string)
    fp_search = re.search('FP\[.*\] P', input_string)

    if fp_search is not None:
        str_start = fp_search.start() + 3
        str_end = fp_search.end() - 3
        found_str = input_string[str_start:str_end].strip()
        fp_list = found_str.split('   ')
        found = True

    else:  # If FP not found, no point searching for, or returning, PP
        return '', '', found

    if pp_search is not None:
        str_start = pp_search.start() + 3
        str_end = pp_search.end() - 3
        found_str = input_string[str_start:str_end].strip()
        pp_list = found_str.split('   ')

    return fp_list, pp_list, found


def search_location(input_string):
    """Searches through the string for 'location' section. If found returns the contents"""
    result = 'not found'
    search = re.search('(?<=\[location:).+(?=])', input_string)
    if search is not None:
        result = search.group(0)
    return result


def search_operation(input_string):
    """Searches through the first section of the string to identify the operation name"""
    match = re.search('\]', input_string)
    return input_string[1:match.start()]


def search_path(input_string, search_type=None):
    """Searches through the string for Path sections. If found returns the contents"""
    found = False
    path_list = []
    if search_type == 'RESTORE':
        path_search = re.search('Path\[.*\] I', input_string)
    else:
        path_search = re.search('Path\[.*\] S', input_string)
    if path_search is not None:
        str_start = path_search.start() + 5
        str_end = path_search.end() - 3
        found_str = input_string[str_start:str_end].strip()
        path_list = found_str.split(' ')
        found = True
    return path_list, found


def search_text(input_string, search_type=None):
    path1, path2, fp_found = search_fp(input_string, search_type)
    if fp_found:
        if path1:
            path1 = process_paths(path1)
            path2 = process_paths(path2)
    else:
        path1, path_found = search_path(input_string, search_type)
        path2 = ''
        if path_found:
            path1 = process_paths(path1)
        else:
            path1 = search_text_within_brackets(input_string)
            path1 = process_paths(path1)
    return path1, path2


def search_text_within_brackets(input_string):
    """Searches through the string for and breaks into [] to search areas of interest and return the contents"""
    # Sometimes path not identified within either FP or Path, so last resort, search the brackets
    # [DELETE_SINGE][1][0][lo
    bracket_contents = []
    open_brackets = [m.start() for m in re.finditer('\[', input_string)]
    closed_brackets = [m.start() for m in re.finditer('\]', input_string)]
    if len(open_brackets) == len(closed_brackets):
        count = len(open_brackets)
        for i in range(count):
            # open_bracket pos at start of bracket, so need to add 1 to start after bracket
            bracket_contents.append(input_string[open_brackets[i] + 1:closed_brackets[i]])

    return bracket_contents[-1]


def search_total(input_string):
    """Searches through the string for 'Total' section. If found returns the contents"""
    result = 'not found'
    # could be LI is files and LV is folders
    search = re.search('(?<=Total\[).+(?=] LI)', input_string)
    if search is not None:
        result = search.group(0)
    return result


def try_decode(input_string):
    """Attempt to decode text to human readable format"""
    if input_string.startswith('#G$E'):
        decoded_text = ilap.process_xor(input_string)
    else:
        decoded_text = ilap.process_b64(input_string)

    return decoded_text


def get_gallery3d_log(files_found, report_folder, seeker, wrap_text, time_offset):
    sql = "select __category, __timestamp, hash, __log from log"
    html_source = ''
    processed_data = []
    for file_found in files_found:
        file_found = str(file_found)
        if file_found.lower().endswith('.db'):
            html_source = file_found
            try:
                results = ilap.fetch_all_from_sqlite_db(file_found, sql)
            except sqlite3.OperationalError:
                msg = "Unfamiliar with database layout; unable to process with gallery3DLog script."
                ilap.logfunc(msg)
                return

            if len(results) > 0:
                processed_data = process_gallery3d_log(results)
            else:
                msg = "No data within database to process; unable to process with gallery3DLog script."
                ilap.logfunc(msg)
                return

    if processed_data:
        report = ArtifactHtmlReport("Gallery3D - Log")
        report.start_artifact_report(report_folder, artefact_title)
        report.add_script()
        # data_headers = ('Timestamp', 'Operation Type', 'Path 1 / (Source)', 'Path 2 / (Destination)',
        #                'Thumbnail Name', 'Extra', 'Original Log Entry')
        data_headers = ('Timestamp', 'Operation Type', 'Path 1', 'Path 2',
                        'Extra Details', 'Original Log Entry')
        report.write_artifact_data_table(data_headers, processed_data, html_source)
        report.end_artifact_report()

        tsvname = artefact_title
        ilap.tsv(report_folder, data_headers, processed_data, tsvname)

        tlactivity = artefact_title
        ilap.timeline(report_folder, tlactivity, processed_data, data_headers)



