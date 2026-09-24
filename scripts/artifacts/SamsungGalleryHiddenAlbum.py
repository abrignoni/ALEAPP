__artifacts_v2__ = {
    "samsung_gallery_hidden_album": {
        "name": "Samsung Gallery Hidden Album",
        "description": "Samsung Gallery Hidden Album",
        "author": "@Snoop168",
        "creation_date": "2026-09-23",
        "last_update_date": "2026-09-23",
        "requirements": "Must extract with the Hidden Album Unlocked",
        "category": "Samsung Gallery",
        "notes": "",
        "paths": ('*/sec/gallery/secured/databases/secured.db*','*/data/sec_pass/*'),
        "output_types": "standard",
        "artifact_icon": "user"
    }
}


from scripts.ilapfuncs import artifact_processor, \
    get_file_path_list_checking_uid, get_results_with_extra_sourcepath_if_needed, open_sqlite_db_readonly, \
    get_sqlite_db_records, check_in_media


@artifact_processor
def samsung_gallery_hidden_album(context):
    data_list = []
    data_headers = (
        ('Date Added', 'datetime'), ('Date Modified', 'datetime'), ('Datetime', 'datetime'), ('Media', 'media'), 'Size',
        'Display Name', 'Captured URL', 'Original Path', 'Cam Model', 'Owner Package Name')
    source_path = ''
    files_found = context.get_files_found()
    for file_found in files_found:
        if file_found.endswith("secured.db"):

            source_path = file_found
            query = '''
            SELECT
                date_added,
                date_modified,
                datetime,
                _data,
                _size,
                _display_name,
                captured_url,
                original_path,
                cam_model,
                owner_package_name
            FROM
            files
            '''
            records = get_sqlite_db_records(file_found, query)
            for record in records:
                record = list(record)
                record[3] = check_in_media('*' + record[3], record[3])
                data_list.append(tuple(record))


    return data_headers, data_list, source_path