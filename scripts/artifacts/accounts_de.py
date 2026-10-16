__artifacts_v2__ = {
    "accounts_de": {
        "name": "Accounts_de",
        "description": "Parses the account service's debug log entries from accounts_de.db (action type, time as stored, account id, table name and caller UID), with the account type, name and last password entry of the accounts row each entry names.",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-03-02",
        "last_update_date": "2026-10-04",
        "requirements": "none",
        "category": "Accounts",
        "notes": "One row per debug_table row. Account Type, Account Name and Last password entry "
                 "come from the accounts row whose _id equals the debug row's _id when the debug "
                 "row's table_name is accounts, and are blank when no accounts row has that _id. "
                 "An accounts row that no debug row names is not reported. On the 12 databases of "
                 "the 10 images in sample_data, 192 of 306 debug rows had no accounts row, every "
                 "debug row had table_name accounts, and 4 of 98 accounts rows were named by no "
                 "debug row. Debug Account ID is debug_table._id as stored. The platform also "
                 "writes debug rows for the shared_accounts table with that table's row id, and "
                 "rows with -1 "
                 "(https://github.com/aosp-mirror/platform_frameworks_base/blob/299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368/services/core/java/com/android/server/accounts/AccountManagerService.java#L4571-L4572 "
                 "and #L5312-L5318, tag android-14.0.0_r1); no shared_accounts debug row was on "
                 "the tested images. Debug Time is the debug_table time value as stored. The "
                 "platform writes it with a SimpleDateFormat that is given no time zone "
                 "(https://github.com/aosp-mirror/platform_frameworks_base/blob/299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368/services/core/java/com/android/server/accounts/AccountManagerService.java#L277 "
                 "and #L5365; the same two lines were read at tags android-10.0.0_r1, "
                 "android-13.0.0_r1 and android-16.0.0_r1), so it is a wall clock string with no "
                 "zone recorded and is reported as text, not converted. Rows are ordered by that "
                 "string. Action Type is the stored string; the platform's values are defined at "
                 "https://github.com/aosp-mirror/platform_frameworks_base/blob/299fe6f5d6fc6f1af7c3411dcf4e5efdf7217368/services/core/java/com/android/server/accounts/AccountsDb.java#L112-L133.",
        "paths": ('*/system_de/*/accounts_de.db*'),
        "output_types": "standard",
        "artifact_icon": "user",
        "sample_data": {
            "anne_a15": "Android 15 | 13 rows",
            "galaxys10_a10": "Android 10 | 10 rows",
            "hc_pixel8pro_a16": "Android 16 | 37 rows",
            "kevin_pocox7_a15": "Android 15 | 64 rows",
            "pixel7a_a14": "Android 14 | 31 rows",
            "samsunga53_a14": "Android 14 | 21 rows",
            "samsungs20_a13": "Android 13 | 70 rows",
            "sharon_a14": "Android 14 | 27 rows",
            "russell_pixel6a_a13": "Android 13 | 26 rows",
            "userb2_a13": "Android 13 | 7 rows",
        }
    }
}


from scripts.ilapfuncs import artifact_processor, \
    get_file_path_list_checking_uid, get_results_with_extra_sourcepath_if_needed, \
    convert_unix_ts_to_utc


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
    debug_table.time,
    debug_table._id,
    debug_table.table_name,
    debug_table.caller_uid
    FROM debug_table
    LEFT JOIN accounts on accounts._id=debug_table._id AND debug_table.table_name='accounts'
    ORDER by time, accounts.rowid, debug_table.rowid
    '''

    data_headers = (
        ('Last password entry', 'datetime'), 
        'Account Type', 'Account Name', 'Action Type', 
        'Debug Time', 'Debug Account ID', 'Debug Table Name', 'Caller UID')

    data_headers, data, source_path = get_results_with_extra_sourcepath_if_needed(source_path_list, query, data_headers)

    for record in data:
        record = list(record)
        record[0] = convert_unix_ts_to_utc(record[0])
        data_list.append(record)

    return data_headers, data_list, source_path
