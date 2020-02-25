import os
from pathlib import Path
import tarfile
from zipfile import ZipFile
import fnmatch
from scripts.ilapfuncs import *


def search(pathto, filename):
    list = []
    for file in Path(pathto).rglob(filename):
        list.append(file)
    return list

def searchtar(t, val, reportfolderbase):
    temp = os.path.join(reportfolderbase, 'temp')
    pathlist = []
    for member in t.getmembers():
        if fnmatch.fnmatch(member.name, val):
            try:
                t.extract(member.name, path=temp)
                pathlist.append(os.path.join(temp, member.name))
            except:
                logfunc('Could not write file to filesystem')
    return pathlist

def searchzip(z, name_list, val, reportfolderbase):
    temp = os.path.join(reportfolderbase, 'temp')
    pathlist = []
    for member in name_list:
        if fnmatch.fnmatch(member, val):
            try:
                z.extract(member, path=temp)
                pathlist.append(os.path.join(temp, member))
            except:
                logfunc('Could not write file to filesystem')    
    return pathlist