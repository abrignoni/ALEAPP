__artifacts_v2__ = {
    "accounts_de": {
        "name": "Accounts_de",
        "description": "",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-03-02",
        "last_update_date": "2025-03-14",
        "requirements": "none",
        "category": "Accounts",
        "notes": "",
        "paths": ('*/system_de/*/accounts_de.db*'),
        "output_types": "standard",
        "artifact_icon": "user"
    }
}


from scripts.ilapfuncs import artifact_processor, \
    get_file_path_list_checking_uid, get_results_with_extra_sourcepath_if_needed, \
    convert_unix_ts_to_utc, convert_ts_human_to_utc


@artifact_processor
def accounts_de(files_found, report_folder, seeker, wrap_text):
    source_path_list = get_file_path_list_checking_uid(files_found, "accounts_de.db", -2, "mirror")
    source_path = ""
    data_list = []

    query = '''
    SELECT 
    last_password_entry_time_millis_epoch,
    accounts.type, 
    accounts.name, 
    debug_table.action_type, 
    debug_table.time
    FROM accounts
    INNER JOIN debug_table on accounts._id=debug_table._id
    ORDER by time
    '''

    data_headers = (
        ('Last password entry', 'datetime'), 
        'Account Type', 'Account Name', 'Action Type', 
        ('Debug Time', 'datetime'))

    data_headers, data, source_path = get_results_with_extra_sourcepath_if_needed(source_path_list, query, data_headers)

    for record in data:
        record = list(record)
        record[0] = convert_unix_ts_to_utc(record[0])
        record[4] = convert_ts_human_to_utc(record[4])
        data_list.append(record)

    return data_headers, data_list, source_path
