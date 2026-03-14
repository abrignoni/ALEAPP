import time as timex
import os
import tarfile
import struct

from pathlib import Path
from scripts.ilapfuncs import *
from shutil import copyfile, copytree
from zipfile import ZipFile

from fnmatch import _compile_pattern
from functools import lru_cache
normcase = lru_cache(maxsize=None)(os.path.normcase)

class FileInfo:
    def __init__(self, source_path, creation_date, modification_date):
        self.source_path = source_path
        self.creation_date = creation_date
        self.modification_date = modification_date

class FileSeekerBase:
    # This is an abstract base class
    def search(self, filepattern_to_search, return_on_first_hit=False):
        '''Returns a list of paths for files/folders that matched'''
        pass

    def cleanup(self):
        '''close any open handles'''
        pass

class FileSeekerDir(FileSeekerBase):
    def __init__(self, directory, data_folder):
        FileSeekerBase.__init__(self)
        self.directory = directory
        self._all_files = []
        self.data_folder = data_folder
        logfunc('Building files listing...')
        self.build_files_list(directory)
        logfunc(f'File listing complete - {len(self._all_files)} files')
        self.searched = {}
        self.copied = {}
        self.file_infos = {}        

    def build_files_list(self, directory):
        '''Populates all paths in directory into _all_files'''
        try:
            files_list = os.scandir(directory)
            for item in files_list:
                self._all_files.append(item.path)
                if item.is_dir(follow_symlinks=False):
                    self.build_files_list(item.path)
        except Exception as ex:
            logfunc(f'Error reading {directory} ' + str(ex))

    def search(self, filepattern, return_on_first_hit=False, force=False):
        if filepattern in self.searched and not force:
            pathlist = self.searched[filepattern]
            return self.searched[filepattern][0] if return_on_first_hit and pathlist else pathlist
        pathlist = []
        pat = _compile_pattern( normcase(filepattern) )
        root = normcase("root/")
        for item in self._all_files:
            if pat( root + normcase(item) ) is not None:
                item_rel_path = item.replace(self.directory, '')
                data_path = os.path.join(self.data_folder, item_rel_path[1:])
                if is_platform_windows():
                    data_path = data_path.replace('/', '\\')
                if item not in self.copied or force:
                    try:
                        os.makedirs(os.path.dirname(data_path), exist_ok=True)
                        if os.path.isdir(item):
                            copytree(item, data_path, dirs_exist_ok=True)
                        else:
                            copyfile(item, data_path)

                        # copyfile(item, data_path)
                        self.copied[item] = data_path
                        creation_date = Path(item).stat().st_ctime
                        modification_date = Path(item).stat().st_mtime
                        file_info = FileInfo(item, creation_date, modification_date)
                        self.file_infos[data_path] = file_info
                    except Exception as ex:
                        logfunc(f'Could not copy {item} to {data_path} ' + str(ex))
                else:
                    data_path = self.copied[item]
                pathlist.append(data_path)
                if return_on_first_hit:
                    self.searched[filepattern] = pathlist
                    return data_path
        self.searched[filepattern] = pathlist
        return pathlist

class FileSeekerTar(FileSeekerBase):
    def __init__(self, tar_file_path, data_folder):
        FileSeekerBase.__init__(self)
        self.is_gzip = tar_file_path.lower().endswith('gz')
        mode ='r:gz' if self.is_gzip else 'r'
        self.tar_file = tarfile.open(tar_file_path, mode)
        self.data_folder = data_folder
        self.searched = {}
        self.copied = {}
        self.file_infos = {}

    def search(self, filepattern, return_on_first_hit=False, force=False):
        if filepattern in self.searched and not force:
            pathlist = self.searched[filepattern]
            return self.searched[filepattern][0] if return_on_first_hit and pathlist else pathlist
        pathlist = []
        pat = _compile_pattern( normcase(filepattern) )
        root = normcase("root/")
        for member in self.tar_file.getmembers():
            if pat( root + normcase(member.name) ) is not None:
                clean_name = sanitize_file_path(member.name)
                full_path = os.path.join(self.data_folder, Path(clean_name))
                if member.name not in self.copied or force:
                    try:
                        if member.isdir():
                            os.makedirs(full_path, exist_ok=True)
                        else:
                            parent_dir = os.path.dirname(full_path)
                            if not os.path.exists(parent_dir):
                                os.makedirs(parent_dir)
                            with open(full_path, "wb") as fout:
                                fout.write(tarfile.ExFileObject(self.tar_file, member).read())
                                fout.close()
                                file_info = FileInfo(member.name, 0, member.mtime)
                                self.file_infos[full_path] = file_info
                                self.copied[member.name] = full_path
                            os.utime(full_path, (member.mtime, member.mtime))
                    except Exception as ex:
                        logfunc(f'Could not write file to filesystem, path was {member.name} ' + str(ex))
                else:
                    full_path = self.copied[member.name]
                pathlist.append(full_path)
                if return_on_first_hit:
                    self.searched[filepattern] = pathlist
                    return full_path
        self.searched[filepattern] = pathlist
        return pathlist

    def cleanup(self):
        self.tar_file.close()

class FileSeekerZip(FileSeekerBase):
    def __init__(self, zip_file_path, data_folder):
        FileSeekerBase.__init__(self)
        self.zip_file = ZipFile(zip_file_path)
        self.name_list = self.zip_file.namelist()
        self.data_folder = data_folder
        self.searched = {}
        self.copied = {}
        self.file_infos = {}

    def decode_extended_timestamp(self, extra_data):
        offset = 0
        length = len(extra_data)

        while offset < length:
            header_id, data_size = struct.unpack_from('<HH', extra_data, offset)
            offset += 4
            if header_id == 0x5455:
                creation_time = modification_time = None
                flags = struct.unpack_from('B', extra_data, offset)[0]
                offset += 1
                if flags & 1:  # Modification time
                    modification_time, = struct.unpack_from('<I', extra_data, offset)
                    offset += 4
                if flags & 4:  # Creation time
                    creation_time, = struct.unpack_from('<I', extra_data, offset)
                    offset += 4
                return creation_time, modification_time
            else:
                offset += data_size
        return None, None

    def search(self, filepattern, return_on_first_hit=False, force=False):
        if filepattern in self.searched and not force:
            pathlist = self.searched[filepattern]
            return self.searched[filepattern][0] if return_on_first_hit and pathlist else pathlist
        pathlist = []
        pat = _compile_pattern( normcase(filepattern) )
        root = normcase("root/")
        for member in self.name_list:
            if member.startswith("__MACOSX"):
                continue
            if pat( root + normcase(member) ) is not None:
                if member not in self.copied or force:
                    try:
                        extracted_path = self.zip_file.extract(member, path=self.data_folder) # already replaces illegal chars with _ when exporting
                        f = self.zip_file.getinfo(member)
                        creation_date, modification_date = self.decode_extended_timestamp(f.extra)
                        file_info = FileInfo(member, creation_date, modification_date)
                        self.file_infos[extracted_path] = file_info
                        date_time = f.date_time
                        date_time = timex.mktime(date_time + (0, 0, -1))
                        os.utime(extracted_path, (date_time, date_time))
                        self.copied[member] = extracted_path
                    except Exception as ex:
                        logfunc(f'Could not write file to filesystem, path was {member} ' + str(ex))
                else:
                    extracted_path = self.copied[member]
                pathlist.append(extracted_path)
                if return_on_first_hit:
                    self.searched[filepattern] = pathlist
                    return extracted_path
        self.searched[filepattern] = pathlist
        return pathlist

    def cleanup(self):
        self.zip_file.close()
