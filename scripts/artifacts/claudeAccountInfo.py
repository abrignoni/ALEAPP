__artifacts_v2__ = {
    "claudeAccountInfo": {
        "name": "Claude Account Information",
        "description": "Parses the account information for the Claude app",
        "author": "Brandon Baye",
        "creation_date": "2026-07-23",
        "last_updated_date": "2026-08-06",
        "requirements": "none",
        "category": "Claude",
        "notes": "timestamps stored as  ISO 8601 combined date-time format"
                 "display name is what AI addresses user as"
                 "email address stored in additional XML, does not contain any other account info",
        "paths": ('*/com.anthropic.claude/cache/app_start/acc_*/org_*/cache.json'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
    }
}

from scripts.ilapfuncs import (
    artifact_processor,
    json,
    get_file_path,
    convert_human_ts_to_utc
)

@artifact_processor
def claudeAccountInfo(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, 'cache.json')
    data_list = []
    
    with open(source_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    account = data['response']['account']
    
    ts = account['created_at']
    ts = ts.replace('T', ' ').replace('Z', '')
    created_at = convert_human_ts_to_utc(ts)
    
    ts = account['updated_at']
    ts = ts.replace('T', ' ').replace('Z', '')
    updated_at = convert_human_ts_to_utc(ts)
    
    full_name = account['full_name']
    display_name = account['display_name']
    email = account['email_address']
    
        
    data_list.append((
        created_at,
        updated_at,
        full_name,
        display_name,
        email,
    ))
        
    data_headers = (
        ('Account Created Time', 'datetime'),
        ('Account Updated Time', 'datetime'),
        'Full Name',
        'Display Name',
        'Email Address',
    )
    
    return data_headers, data_list, source_path