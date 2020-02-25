import sys, os, re, glob
from scripts.search_files import *
from scripts.ilapfuncs import *
from scripts.ilap_artifacts import *
import argparse
from argparse import RawTextHelpFormatter
from six.moves.configparser import RawConfigParser
from time import process_time
import  tarfile
import shutil
from scripts.report import *
from zipfile import ZipFile
from tarfile import TarFile

parser = argparse.ArgumentParser(description='ALEAPP: Android Logs, Events, and Protobuf Parser.')
parser.add_argument('-o', choices=['fs','tar','zip'], required=True, action="store",help="Input type (fs = extracted to file system folder)")
parser.add_argument('pathtodir',help='Path to directory')

start = process_time()
    
args = parser.parse_args()

pathto = args.pathtodir
extracttype = args.o
start = process_time()

os.makedirs(reportfolderbase)
os.makedirs(os.path.join(reportfolderbase, 'Script Logs'))

logfunc('\n--------------------------------------------------------------------------------------')
logfunc('ALEAPP: Android Logs, Events, and Protobuf Parser')
logfunc('Objective: Triage Android Full System Extractions.')
logfunc('By: Alexis Brignoni | @AlexisBrignoni | abrignoni.com')

if extracttype == 'fs':
    
    logfunc(f'Artifact categories to parse: {str(len(tosearch))}')
    logfunc(f'File/Directory selected: {pathto}')
    logfunc('\n--------------------------------------------------------------------------------------')
    logfunc( )

    log = open(os.path.join(reportfolderbase, 'Script Logs', 'ProcessedFilesLog.html'), 'w+', encoding='utf8')
    nl = '\n' #literal in order to have new lines in fstrings that create text files
    log.write(f'Extraction/Path selected: {pathto}<br><br>')
    
    # Search for the files per the arguments
    for key, val in tosearch.items():
        filefound = search(pathto, val[1])
        if not filefound:
            logfunc()
            logfunc(f'No files found for {key} -> {val[1]}.')
            log.write(f'No files found for {key} -> {val[1]}.<br>')
        else:
            logfunc()
            #globals()[key](filefound)
            process_artifact(filefound, key, val[0])
            for pathh in filefound:
                log.write(f'Files for {val[1]} located at {pathh}.<br>')
    log.close()

elif extracttype == 'tar':
    
    logfunc(f'Artifact categories to parse: {str(len(tosearch))}')
    logfunc(f'File/Directory selected: {pathto}')
    logfunc('\n--------------------------------------------------------------------------------------')
    
    log = open(os.path.join(reportfolderbase, 'Script Logs', 'ProcessedFilesLog.html'), 'w+', encoding='utf8')
    nl = '\n' #literal in order to have new lines in fstrings that create text files
    log.write(f'Extraction/Path selected: {pathto}<br><br>')    # tar searches and function calls

    t = TarFile(pathto)

    for key, val in tosearch.items():
        filefound = searchtar(t, val[1], reportfolderbase)
        if not filefound:
            
            logfunc()
            logfunc(f'No files found for {key} -> {val[1]}.')
            log.write(f'No files found for {key} -> {val[1]}.<br>')
        else:
            
            logfunc()
            #globals()[key](filefound)
            process_artifact(filefound, key, val[0])
            for pathh in filefound:
                log.write(f'Files for {val[1]} located at {pathh}.<br>')
    log.close()

elif extracttype == 'zip':
        
        logfunc(f'Artifact categories to parse: {str(len(tosearch))}')
        logfunc(f'File/Directory selected: {pathto}')
        logfunc('\n--------------------------------------------------------------------------------------')
        logfunc('')
        log = open(os.path.join(reportfolderbase,'Script Logs', 'ProcessedFilesLog.html'), 'w+', encoding='utf8')
        log.write(f'Extraction/Path selected: {pathto}<br><br>')    # tar searches and function calls

        z = ZipFile(pathto)
        name_list = z.namelist()
        for key, val in tosearch.items():
            filefound = searchzip(z, name_list, val[1], reportfolderbase)
            if not filefound:
                logfunc('')
                logfunc(f'No files found for {key} -> {val[1]}.')
                log.write(f'No files found for {key} -> {val[1]}.<br>')
            else:
                
                logfunc('')
                #globals()[key](filefound)
                process_artifact(filefound, key, val[0])
                for pathh in filefound:
                    log.write(f'Files for {val[1]} located at {pathh}.<br>')
        log.close()

        z.close()

else:
    logfunc('Error on argument -o')
'''    
if os.path.exists(reportfolderbase+'temp/'):
    shutil.rmtree(reportfolderbase+'temp/')
    #call reporting script        
'''

logfunc('')
logfunc('Processes completed.')
end = process_time()
time = start - end
logfunc("Processing time: " + str(abs(time)) )

log = open(os.path.join(reportfolderbase, 'Script Logs', 'ProcessedFilesLog.html'), 'a', encoding='utf8')
log.write(f'Processing time in secs: {str(abs(time))}')
log.close()

logfunc('')
logfunc('Report generation started.')
report(reportfolderbase, time, extracttype, pathto)
logfunc('Report generation Completed.')
logfunc('')
logfunc(f'Report name: {reportfolderbase}')
    
