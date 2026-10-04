__artifacts_v2__ = {
    "accounts_de": {
        "name": "Accounts_de",
        "description": "Parses device accounts and the account service's debug log entries for each account (account type and name, last password entry, action type and time as stored) from accounts_de.db.",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-03-02",
        "last_update_date": "2025-03-14",
        "requirements": "none",
        "category": "Accounts",
        "notes": "Rows come from the accounts table joined to debug_table on accounts._id = "
                 "debug_table._id, so a debug_table row whose _id matches no accounts row is not "
                 "reported. Debug Time is the debug_table time value. The platform writes that "
                 "value as a wall clock string with no time zone (AOSP AccountManagerService.java "
                 "at tag android-14.0.0_r1, lines 277 and 5365; only that tag was read). This "
                 "parser labels it UTC without conversion, so it is not established to be UTC.",
        "paths": ('*/system_de/*/accounts_de.db*'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "anne_a15": "Android 15 | 11 rows",
            "galaxys10_a10": "Android 10 | 5 rows",
            "hc_pixel8pro_a16": "Android 16 | 10 rows",
            "kevin_pocox7_a15": "Android 15 | 8 rows",
            "pixel7a_a14": "Android 14 | 21 rows",
            "samsunga53_a14": "Android 14 | 11 rows",
            "samsungs20_a13": "Android 13 | 19 rows",
            "sharon_a14": "Android 14 | 15 rows",
            "russell_pixel6a_a13": "Android 13 | 11 rows",
            "userb2_a13": "Android 13 | 3 rows",
        }
    }
}


from scripts.ilapfuncs import artifact_processor, \
    get_file_path_list_checking_uid, get_results_with_extra_sourcepath_if_needed, \
    convert_unix_ts_to_utc, convert_ts_human_to_utc


@artifact_processor
def accounts_de(context):
    files_found = context.get_files_found()
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
    ORDER by time, accounts.rowid, debug_table.rowid
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
