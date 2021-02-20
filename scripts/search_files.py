import fnmatch
import os
import tarfile

from pathlib import Path
from scripts.ilapfuncs import *
from zipfile import ZipFile

class FileSeekerBase:
    # This is an abstract base class
    def search(self, filepattern_to_search, return_on_first_hit=False):
        '''Returns a list of paths for files/folders that matched'''
        pass

    def cleanup(self):
        '''close any open handles'''
        pass

class FileSeekerDir(FileSeekerBase):
    def __init__(self, directory):
        FileSeekerBase.__init__(self)
        self.directory = directory
        self._all_files = []
        logfunc('Building files listing...')
        self.build_files_list(directory)
        logfunc(f'File listing complete - {len(self._all_files)} files')

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

    def search(self, filepattern, return_on_first_hit=False):
        if return_on_first_hit:
            for item in self._all_files:
                if fnmatch.fnmatch(item, filepattern):
                    return [item]
            return []
        return fnmatch.filter(self._all_files, filepattern)

class FileSeekerTar(FileSeekerBase):
    def __init__(self, tar_file_path, temp_folder):
        FileSeekerBase.__init__(self)
        self.is_gzip = tar_file_path.lower().endswith('gz')
        mode ='r:gz' if self.is_gzip else 'r'
        self.tar_file = tarfile.open(tar_file_path, mode)
        self.temp_folder = temp_folder

    def search(self, filepattern, return_on_first_hit=False):
        pathlist = []
        for member in self.tar_file.getmembers():
            if fnmatch.fnmatch('root/' + member.name, filepattern):
                try:
                    clean_name = sanitize_file_path(member.name)
                    full_path = os.path.join(self.temp_folder, Path(clean_name))
                    if member.isdir():
                        os.makedirs(full_path, exist_ok=True)
                    else:
                        parent_dir = os.path.dirname(full_path)
                        if not os.path.exists(parent_dir):
                            os.makedirs(parent_dir)
                        with open(full_path, "wb") as fout:
                            fout.write(tarfile.ExFileObject(self.tar_file, member).read())
                            fout.close()
                        os.utime(full_path, (member.mtime, member.mtime))
                    pathlist.append(full_path)
                except Exception as ex:
                    logfunc(f'Could not write file to filesystem, path was {member.name} ' + str(ex))
        return pathlist

    def cleanup(self):
        self.tar_file.close()

class FileSeekerZip(FileSeekerBase):
    def __init__(self, zip_file_path, temp_folder):
        FileSeekerBase.__init__(self)
        self.zip_file = ZipFile(zip_file_path)
        self.name_list = self.zip_file.namelist()
        self.temp_folder = temp_folder

    def search(self, filepattern, return_on_first_hit=False):
        pathlist = []
        for member in self.name_list:
            if fnmatch.fnmatch('root/' + member, filepattern):
                try:
                    extracted_path = self.zip_file.extract(member, path=self.temp_folder) # already replaces illegal chars with _ when exporting
                    pathlist.append(extracted_path)
                except Exception as ex:
                    member = member.lstrip("/")
                    logfunc(f'Could not write file to filesystem, path was {member} ' + str(ex))
        return pathlist

    def cleanup(self):
        self.zip_file.close()

class FileSeekerABackup(FileSeekerTar):
    def __init__(self, ab_file_path, temp_folder):
        logfunc("Generating tar from AB file")
        logfunc(f"Tar will be generated in {temp_folder}")
        tar_file_path = self.build_tar_filepath(ab_file_path, temp_folder)
        try:
            self.generate_tar_file(ab_file_path, tar_file_path)
        except TypeError:
            logfunc("File doesn't seem to be an AB backup")
            raise TypeError
        FileSeekerTar.__init__(self, tar_file_path, temp_folder)

    def build_tar_filepath(self, input_path, output_dir):
        input_filename = os.path.splitext(os.path.basename(input_path))[0]
        output_filename = f"{input_filename}.tar.gz"
        logfunc(f"Output filename: {output_filename}")
        output_filepath = os.path.join(output_dir, output_filename)
        return output_filepath

    def generate_tar_file(self, ab_file_path, tar_file_path):
        ab_header = b"ANDROID BACKUP"
        tar_header = b"\x1f\x8b\x08\x00\x00\x00\x00\x00"
        ignore_offset = 24

        ab_data = open(ab_file_path, 'rb')

        ab_bytes_to_remove = ab_data.read(ignore_offset)

        if ab_bytes_to_remove[:14] == ab_header:
            logfunc("AB Header checked and intact")
        else:
            logfunc("AB Header not found; is it definitely the right file?")
            raise TypeError

        # Open the target tar file
        output_path = tar_file_path

        try:
            output_file = open(output_path, 'wb')
        except:
            logfunc("Unable to open file at {output_path}")
            raise FileNotFoundError

        logfunc("Writing tar header..")
        output_file.write(tar_header)

        logfunc("Writing rest of AB file..")
        output_file.write(ab_data.read())

        logfunc("..done.")
        logfunc("Closing files..")

        output_file.close()
        ab_data.close()

        # quick verify
        try:
            test_val = tarfile.is_tarfile(output_path)
            logfunc("Output verified OK")
        except:
            logfunc("Verification failed; maybe it's encrypted?")
            raise TypeError

