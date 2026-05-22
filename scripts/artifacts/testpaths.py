__artifacts_v2__ = {
    "testpaths": {
        "name": "Paths in Extraction",
        "description": "",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-03-02",
        "last_update_date": "2025-03-14",
        "requirements": "none",
        "category": "Verification",
        "notes": "",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "arrow-right-circle"
    },
    "notfoundpaths": {
        "name": "Paths not in the Extraction ",
        "description": "",
        "author": "@AlexisBrignoni",
        "creation_date": "2020-03-02",
        "last_update_date": "2025-03-14",
        "requirements": "Paths Validation must be executed first",
        "category": "Verification",
        "notes": "",
        "paths": None,
        "output_types": "standard",
        "artifact_icon": "arrow-left-circle"
    }
}


from scripts.ilapfuncs import artifact_processor, logfunc, get_file_path
from scripts.verification_paths import paths 


@artifact_processor
def testpaths(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = get_file_path(files_found, '_lava_artifacts.db')

    
    logfunc(f'Targeted Paths: {str(len(paths))}')
    
    try:
        filelist = seeker.name_list
    except:
        filelist = seeker.all_files
    
    logfunc(f'Paths in source: {str(len(filelist))}')
    
    matching_items = []
    matched_in_filelist = []
    not_in_paths = []
    
    for item1 in paths:
        for item2 in filelist:
            if item1 in item2:  # Checks if item2 is a substring of item1
                data_list.append((item1, item2))
                matched_in_filelist.append(item1)
                break
    
    for item in paths:
        if item not in matched_in_filelist:
            not_in_paths.append((item,))
            
    logfunc(f'Matching paths: {str(len(data_list))}')
    #logfunc(f'Not matched from targeted paths: {str(len(not_in_paths))}')
    
    data_headers = ('Targeted Paths','Path in Extraction')

    #data_headers, data, source_path = get_results_with_extra_sourcepath_if_needed(source_path_list, query, data_headers)


    return data_headers, data_list, 'Extraction'

@artifact_processor
def notfoundpaths(files_found, report_folder, seeker, wrap_text):
    data_list = []
    source_path = get_file_path(files_found, '_lava_artifacts.db')

    
    logfunc(f'Targeted Paths: {str(len(paths))}')
    
    try:
        filelist = seeker.name_list
    except:
        filelist = seeker.all_files
    
    matching_items = []
    matched_in_filelist = []
    not_in_paths = []
    
    for item1 in paths:
        for item2 in filelist:
            if item1 in item2:  # Checks if item2 is a substring of item1
                data_list.append((item1, item2))
                matched_in_filelist.append(item1)
                break
        
    for item in paths:
        if item not in matched_in_filelist:
            not_in_paths.append((item,))
            
    logfunc(f'Not matched from targeted paths: {str(len(not_in_paths))}')
    
    data_headers = ('Paths not in Extraction',)
    
    return data_headers, not_in_paths, 'Extraction'
    
    