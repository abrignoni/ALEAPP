__artifacts_v2__ = {
    "claudeProjects": {
        "name": "Claude Projects",
        "description": "Parses projects made within Claude",
        "author": "Brandon Baye",
        "creation_date": "2026-07-24",
        "last_updated_date": "2026-08-06",
        "requirements": "none",
        "category": "Claude",
        "notes": "projects can include document and file uploads to each separate project"
                 "user can add conversations to a project to keep context for usage"
                 "project creator is stored as the full name in profile"
                 "timestamps are ISO 8601 combined date-time format",
        "paths": ('*/com.anthropic.claude/databases/acc_*_claude_cache.db*'),
        "output_types": "standard",
        "artifact_icon": "message-circle",
    }
}

from scripts.ilapfuncs import (
    artifact_processor,
    get_file_path,
    get_sqlite_db_records,
    convert_human_ts_to_utc
)

@artifact_processor
def claudeProjects(context):
    files_found = context.get_files_found()
    source_path = get_file_path(files_found, '*_claude_cache.db')
    data_list = []
    
    query = '''
    SELECT
        json_extract(cachedProjects.project_json, '$.created_at') as 'Project Created Time',
        json_extract(cachedProjects.project_json, '$.updated_at') as 'Project Updated Time',
        json_extract(cachedProjects.project_json, '$.name') as 'Project Name',
        json_extract(cachedProjects.project_json, '$.description') as 'Project Description',
        json_extract(cachedProjects.project_json, '$.creator.full_name') as 'Project Creator',
        CASE json_extract(cachedProjects.project_json, '$.is_starred') 
            WHEN 0 THEN 'False'
            WHEN 1 THEN 'True'
            ELSE 'Unknown'
        END AS 'Project Starred',
        json_extract(cachedProjects.project_json, '$.docs_count') as 'Number of Documents',
        json_extract(cachedProjects.project_json, '$.files_count') as 'Number of Files'
    FROM cachedProjects
    '''
    
    records = get_sqlite_db_records(source_path, query)
    for record in records:
        created_at = convert_human_ts_to_utc(
            record[0].replace('T', ' ').replace('Z', '')
            ) if record[0] else None
            
        updated_at = convert_human_ts_to_utc(
            record[1].replace('T', ' ').replace('Z', '')
            ) if record[1] else None
        
        data_list.append((
            created_at,
            updated_at,
            record[2],
            record[3],
            record[4],
            record[5],
            record[6],
            record[7]
        ))
        
    data_headers = (
        ('Project Created Time', 'datetime'),
        ('Project Updated Time', 'datetime'),
        'Project Name',
        'Project Description',
        'Project Creator',
        'Project Starred',
        'Number of Documents',
        'Number of Files'
    )
    
    return data_headers, data_list, source_path