"""
This module provides functionality to search and extract files from various
extraction sources.
It handles file pattern matching, copying files to a data folder, extracting
metadata (creation/modification dates), and decrypting encrypted iTunes backups.

Classes:
    FileInfo: Container for file metadata (source path, creation date, modification date)
    FileSeekerBase: Abstract base class for file searching implementations
    FileSeekerDir: File seeker for local directories
    FileSeekerItunes: NOT HERE
    FileSeekerTar: File seeker for TAR/TAR.GZ archives
    FileSeekerZip: File seeker for ZIP archives
    FileSeekerFile: File seeker for individual files

Functions:
    get_itunes_backup_type: Determines iTunes backup type (db/mbdb)
    get_itunes_backup_encryption: Checks if iTunes backup is encrypted
    check_itunes_backup_status: Validates iTunes backup status and encryption
    decrypt_itunes_backup: Decrypts encrypted iTunes backups using provided passcode
"""

import time as timex
import os
import tarfile
import struct

from pathlib import Path
from scripts.ilapfuncs import *
from shutil import copy2
from zipfile import ZipFile
from fnmatch import _compile_pattern
from functools import lru_cache
normcase = lru_cache(maxsize=None)(os.path.normcase)

class FileInfo:
    """
    A class to store file metadata information.
    Attributes:
        source_path (str): The full path to the source file.
        creation_date (datetime): The date and time when the file was created.
        modification_date (datetime): The date and time when the file was last modified.
    """

    def __init__(self, source_path, creation_date, modification_date):
        self.source_path = source_path
        self.creation_date = creation_date
        self.modification_date = modification_date


class FileSeekerBase:
    """
    Abstract base class for file seeking operations.
    This class provides an interface for searching files and performing cleanup operations
    in different storage contexts (e.g., filesystem, archives, databases).
    """
    def search(self, filepattern, return_on_first_hit=False):
        '''Returns a list of paths for files/folders that matched'''
        raise NotImplementedError

    def cleanup(self):
        '''close any open handles'''


class FileSeekerDir(FileSeekerBase):
    """
    This class extends FileSeekerBase to provide functionality for searching files
    within a directory structure, copying matched files to a destination folder,
    and caching search results for performance.
    Attributes:
        directory (str): The root directory to search within.
        data_folder (str): The destination folder where matched files will be copied.
        _all_files (list): Internal list containing all file paths found in the directory tree.
        searched (dict): Cache of search results, mapping file patterns to lists of matched paths.
        copied (dict): Mapping of source file paths to their copied destination paths.
        file_infos (dict): Dictionary storing FileInfo objects with metadata for copied files.
    Methods:
        build_files_list(directory): Recursively scans directory and populates _all_files list.
        search(filepattern, return_on_first_hit=False, force=False): Searches for files matching
            the given pattern, copies them to data_folder, and returns matching paths.
    """

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
        except OSError as ex:
            logfunc(f'Error reading {directory} ' + str(ex))

    def search(self, filepattern, return_on_first_hit=False, force=False):
        if filepattern in self.searched and not force:
            pathlist = self.searched[filepattern]
            return self.searched[filepattern][0] if return_on_first_hit and pathlist else pathlist
        pathlist = []
        pat = _compile_pattern(normcase(filepattern))
        root = normcase("root/")
        for item in self._all_files:
            if pat(root + normcase(item)) is not None:
                item_rel_path = item.replace(self.directory, '')
                data_path = os.path.join(self.data_folder, item_rel_path[1:])
                if is_platform_windows():
                    data_path = data_path.replace('/', '\\')
                if item not in self.copied or force:
                    try:
                        if os.path.isdir(item):
                            pass
                        elif os.path.isfile(item):
                            os.makedirs(os.path.dirname(data_path), exist_ok=True)
                            copy2(item, data_path)
                            self.copied[item] = data_path
                            creation_date = Path(item).stat().st_ctime
                            modification_date = Path(item).stat().st_mtime
                            file_info = FileInfo(item, creation_date, modification_date)
                            self.file_infos[data_path] = file_info
                        else:
                            logfunc(f"INFO: Item '{item}' is neither a file nor a directory "
                                    "(e.g. symlink not followed, or broken). Skipped.")
                    except OSError as ex:
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
    """
    This is a class that extends FileSeekerBase to facilitate searching and extracting files
    from a tar archive. It supports both gzip and regular tar files.
    Attributes:
        tar_file_path (str): The path to the tar file.
        data_folder (str): The directory where extracted files will be stored.
        is_gzip (bool): Indicates if the tar file is gzipped.
        tar_file (tarfile.TarFile): The opened tar file object.
        searched (dict): A dictionary to keep track of searched file patterns and their results.
        copied (dict): A dictionary to keep track of files that have been copied.
        file_infos (dict): A dictionary to store file information for extracted files.
    Methods:
        __init__(tar_file_path, data_folder):
            Initializes the FileSeekerTar instance with the specified tar file path and data folder.
        search(filepattern, return_on_first_hit=False, force=False):
            Searches for files matching the given pattern in the tar archive and extracts them to the data folder.
            Returns a list of paths to the extracted files or the first hit if specified.
        cleanup():
            Closes the tar file to free up resources.
    """

    def __init__(self, tar_file_path, data_folder):
        FileSeekerBase.__init__(self)
        self.is_gzip = tar_file_path.lower().endswith('gz')
        mode = 'r:gz' if self.is_gzip else 'r'
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
        pat = _compile_pattern(normcase(filepattern))
        root = normcase("root/")
        for member in self.tar_file.getmembers():
            if pat(root + normcase(member.name)) is not None:
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
                    except OSError as ex:
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
    """
    This is a class that extends FileSeekerBase to facilitate searching and extracting files from a ZIP archive.
    Attributes:
        zip_file (ZipFile): The ZIP file object representing the archive.
        name_list (list): A list of file names contained in the ZIP archive.
        data_folder (str): The directory where extracted files will be stored.
        searched (dict): A dictionary to keep track of searched file patterns and their corresponding paths.
        copied (dict): A dictionary to keep track of files that have been extracted and their paths.
        file_infos (dict): A dictionary to store file information such as creation and modification dates.
    Methods:
        __init__(zip_file_path, data_folder):
            Initializes the FileSeekerZip instance with the specified ZIP file path and data folder.
        decode_extended_timestamp(extra_data):
            Decodes the extended timestamp information from the extra data of a file in the ZIP archive.
        search(filepattern, return_on_first_hit=False, force=False):
            Searches for files matching the specified pattern in the ZIP archive and extracts them if found.
        cleanup():
            Closes the ZIP file to free up resources.
    """

    def __init__(self, zip_file_path, data_folder):
        FileSeekerBase.__init__(self)
        self.zip_file = ZipFile(zip_file_path)
        self.name_list = self.zip_file.namelist()
        self.data_folder = data_folder
        self.searched = {}
        self.copied = {}
        self.file_infos = {}

    def decode_extended_timestamp(self, extra_data):
        """
        Decode extended timestamps from the provided extra data.
        Parameters:
            extra_data (bytes): The byte sequence containing the extended timestamp
                                information.
        Returns:
            tuple: A tuple containing the creation time and modification time as
                   integers. If the timestamps are not found, returns (None, None).
        """

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
        pat = _compile_pattern(normcase(filepattern))
        root = normcase("root/")
        for member in self.name_list:
            if member.startswith("__MACOSX"):
                continue
            if pat(root + normcase(member)) is not None:
                if member not in self.copied or force:
                    try:
                        # already replaces illegal chars with _ when exporting
                        extracted_path = self.zip_file.extract(member, path=self.data_folder)
                        f = self.zip_file.getinfo(member)
                        creation_date, modification_date = self.decode_extended_timestamp(f.extra)
                        file_info = FileInfo(member, creation_date, modification_date)
                        self.file_infos[extracted_path] = file_info
                        date_time = f.date_time
                        date_time = timex.mktime(date_time + (0, 0, -1))
                        os.utime(extracted_path, (date_time, date_time))
                        self.copied[member] = extracted_path
                    except OSError as ex:
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


class FileSeekerFile(FileSeekerBase):
    """
    This is a class that extends FileSeekerBase to facilitate searching for and copying a specific file
    based on a provided filename pattern. It validates the input file path and manages the copying of the file to a
    designated data folder while keeping track of searched patterns and copied files.
    Attributes:
        single_file_abs_path (str): The absolute path of the single file to be sought.
        data_folder (str): The folder where the file will be copied.
        single_file_basename (str or None): The basename of the file if valid; otherwise None.
        searched (dict): A dictionary to store previously searched patterns and their results.
        copied (dict): A dictionary to track copied files and their destination paths.
        file_infos (dict): A dictionary to store file information objects for copied files.
    Methods:
        search(filepattern, return_on_first_hit=False, force=False):
            Searches for the file based on the provided filename pattern and copies it
            to the data folder if a match is found.
        cleanup():
            Placeholder method for cleanup operations (currently does nothing).
    """

    def __init__(self, file_path, data_folder):
        FileSeekerBase.__init__(self)
        self.single_file_abs_path = os.path.abspath(file_path)
        self.data_folder = data_folder

        if not os.path.isfile(self.single_file_abs_path):
            logfunc(f"Error: Input path '{file_path}' provided to FileSeekerFile is not a valid file.")
            self.single_file_basename = None
        else:
            self.single_file_basename = os.path.basename(self.single_file_abs_path)

        self.searched = {}
        self.copied = {}
        self.file_infos = {}

    def search(self, filepattern, return_on_first_hit=False, force=False):
        if not self.single_file_basename:
            return []

        if filepattern in self.searched and not force:
            return self.searched[filepattern]

        pattern_to_match_filename_against = None  # The specific filename pattern to use

        if '/' in filepattern or '\\' in filepattern:  # Original pattern contains path separators
            basename_of_pattern = os.path.basename(filepattern)

            # If the original pattern implied a path, we only proceed if its filename component
            # is NOT an overly generic wildcard.
            # Overly generic wildcards for a filename part of a path: '*', '**', '*.*'
            # These suggest matching 'any file' within that path, which isn't specific enough
            # for FileSeekerFile if the user provided one specific file.
            if basename_of_pattern not in ('*', '**', '*.*'):
                pattern_to_match_filename_against = basename_of_pattern
            else:
                # Log that this pattern is too generic for a single file context if it includes paths
                logfunc(f"FileSeekerFile: Artifact pattern '{filepattern}' contains path separators, AND its filename "
                        f"component ('{basename_of_pattern}') is too generic (e.g., '*', '**', '*.*'). "
                        f"FileSeekerFile will not match its single file ('{self.single_file_basename}') "
                        "against such a broad path-based pattern. No match.")
                self.searched[filepattern] = []
                return []
        else:  # Original pattern does not contain path separators (e.g., "*.json", "myfile.db")
            # This is a direct filename pattern.
            pattern_to_match_filename_against = filepattern

        # This safeguard should ideally not be hit if logic above is correct
        if not pattern_to_match_filename_against:
            # logfunc(f"FileSeekerFile: No effective filename pattern was derived from original '{filepattern}' to "
            #         f"match against basename '{self.single_file_basename}'. No match.")
            self.searched[filepattern] = []
            return []

        pat = _compile_pattern(normcase(pattern_to_match_filename_against))
        found_data_paths = []

        # logfunc("FileSeekerFile: Attempting to match effective filename pattern "
        #         f"'{pattern_to_match_filename_against}' (derived from artifact pattern "
        #         f"'{filepattern}') against actual file basename '{self.single_file_basename}'")

        if pat(normcase(self.single_file_basename)) is not None:
            # Match successful, proceed to copy
            dest_data_path = os.path.join(self.data_folder, self.single_file_basename)
            if is_platform_windows():
                dest_data_path = dest_data_path.replace('/', '\\')

            if self.single_file_abs_path not in self.copied or force:
                try:
                    os.makedirs(self.data_folder, exist_ok=True)
                    copy2(self.single_file_abs_path, dest_data_path)
                    self.copied[self.single_file_abs_path] = dest_data_path
                    s = Path(self.single_file_abs_path).stat()
                    file_info_obj = FileInfo(self.single_file_abs_path, s.st_ctime, s.st_mtime)
                    self.file_infos[dest_data_path] = file_info_obj
                    found_data_paths.append(dest_data_path)
                    # logfunc(f"FileSeekerFile: Matched and copied. Dest: {dest_data_path}")
                except OSError as ex:
                    logfunc("FileSeekerFile: Could not copy file "
                            f"{self.single_file_abs_path} to {dest_data_path}: {str(ex)}")
            else:  # Already copied
                copied_dest_path = self.copied.get(self.single_file_abs_path)
                if copied_dest_path:
                    found_data_paths.append(copied_dest_path)
                    # logfunc(f"FileSeekerFile: Matched (already copied). Dest: {copied_dest_path}")
        else:
            logfunc("FileSeekerFile: No match for effective filename pattern "
                    f"'{pattern_to_match_filename_against}' against "
                    f"actual file basename '{self.single_file_basename}'")

        self.searched[filepattern] = found_data_paths
        return found_data_paths

    def cleanup(self):
        pass
