__artifacts_v2__ = {
    "accounts_ce_authtokens": {
        "name": "Authentication tokens",
        "description": "Application accounts that use authentication tokens.",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-03-04",
        "last_update_date": "2025-03-14",
        "requirements": "none",
        "category": "Accounts",
        "notes": "",
        "paths": ('*/system_ce/*/accounts_ce.db*'),
        "output_types": ["html", "lava", "tsv"],
        "artifact_icon": "key"
    }
}

from scripts.ilapfuncs import artifact_processor, \
    get_file_path_list_checking_uid, get_uid_sqlite_db_records

@artifact_processor
def accounts_ce_authtokens(files_found, report_folder, seeker, wrap_text):
    source_path_list = get_file_path_list_checking_uid(files_found, "accounts_ce.db", -2, "mirror")
    source_path = ""
    data_list = []

    query = '''
    SELECT
        accounts.type,
        accounts.name,
        authtokens.type,
        authtokens.authtoken
    FROM accounts, authtokens
    WHERE
        accounts._id = authtokens.accounts_id
    '''

    data_headers = ('Account Type', 'Account Name', 'Authtoken Type', 'Authtoken')

    data_headers, data_list, source_path = get_uid_sqlite_db_records(source_path_list, query, data_headers)

    return data_headers, data_list, source_path