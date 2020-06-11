import argparse
import os
import scripts.report as report
import shutil

from scripts.search_files import *
from scripts.ilapfuncs import *
from scripts.ilap_artifacts import *
from scripts.version_info import aleapp_version
from time import process_time, gmtime, strftime

def main():
    parser = argparse.ArgumentParser(description='ALEAPP: Android Logs, Events, and Protobuf Parser.')
    parser.add_argument('-o', choices=['fs','tar','zip'], required=True, action="store",help="Input type (fs = extracted to file system folder)")
    parser.add_argument('pathtodir',help='Path to directory')
        
    args = parser.parse_args()

    pathto = args.pathtodir
    extracttype = args.o

    crunch_artifacts(tosearch, extracttype, pathto)

def crunch_artifacts(search_list, extracttype, pathto):
    start = process_time()

    os.makedirs(reportfolderbase)
    os.makedirs(os.path.join(reportfolderbase, 'Script Logs'))
    logfunc('Procesing started. Please wait. This may take a few minutes...')

    logfunc('\n--------------------------------------------------------------------------------------')
    logfunc(f'ALEAPP v{aleapp_version}: Android Logs, Events, and Protobuf Parser')
    logfunc('Objective: Triage Android Full System Extractions.')
    logfunc('By: Alexis Brignoni | @AlexisBrignoni | abrignoni.com')
    logfunc('By: Yogesh Khatri | @SwiftForensics | swiftforensics.com')

    seeker = None
    if extracttype == 'fs':
        seeker = FileSeekerDir(pathto)

    elif extracttype == 'tar':
        seeker = FileSeekerTar(pathto, reportfolderbase)

    elif extracttype == 'zip':
        seeker = FileSeekerZip(pathto, reportfolderbase)

    else:
        logfunc('Error on argument -o (input type)')
        return

    # Now ready to run
    logfunc(f'Artifact categories to parse: {str(len(search_list))}')
    logfunc(f'File/Directory selected: {pathto}')
    logfunc('\n--------------------------------------------------------------------------------------')

    log = open(os.path.join(reportfolderbase, 'Script Logs', 'ProcessedFilesLog.html'), 'w+', encoding='utf8')
    nl = '\n' #literal in order to have new lines in fstrings that create text files
    log.write(f'Extraction/Path selected: {pathto}<br><br>')
    
    # Search for the files per the arguments
    for key, val in search_list.items():
        artifact_pretty_name = val[0]
        artifact_search_regex = val[1]
        filefound = seeker.search(artifact_search_regex)
        if not filefound:
            logfunc()
            logfunc(f'No files found for {key} -> {artifact_search_regex}')
            log.write(f'No files found for {key} -> {artifact_search_regex}<br><br>')
        else:
            logfunc()
            process_artifact(filefound, key, artifact_pretty_name, seeker)
            for pathh in filefound:
                log.write(f'Files for {artifact_search_regex} located at {pathh}<br><br>')
    log.close()

    logfunc('')
    logfunc('Processes completed.')
    end = process_time()
    run_time_secs =  end - start
    run_time_HMS = strftime('%H:%M:%S', gmtime(run_time_secs))
    logfunc("Processing time = {}".format(run_time_HMS))

    logfunc('')
    logfunc('Report generation started.')
    report.generate_report(reportfolderbase, run_time_secs, run_time_HMS, extracttype, pathto)
    logfunc('Report generation Completed.')
    logfunc('')
    logfunc(f'Report location: {reportfolderbase}')

if __name__ == '__main__':
    main()