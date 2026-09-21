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
import atexit
import importlib
import os
import tarfile
import hashlib
import struct

from pathlib import Path
from scripts.ilapfuncs import *
from shutil import copy2, copyfileobj
from zipfile import ZipFile
from fnmatch import _compile_pattern
from functools import lru_cache
normcase = lru_cache(maxsize=None)(os.path.normcase)

def _probe_volume_case_insensitive(folder):
    """True when this folder's volume folds case.

    os.path.normcase reports the platform convention, not the volume.
    Probe by creating Aa then exclusively creating aA.
    """
    try:
        os.makedirs(folder, exist_ok=True)
    except OSError:
        return os.path.normcase("Aa") == os.path.normcase("aA")
    probe_a = os.path.join(folder, ".leapp_case_probe_Aa")
    probe_b = os.path.join(folder, ".leapp_case_probe_aA")
    for leftover in (probe_a, probe_b):
        try:
            os.remove(leftover)
        except OSError:
            pass
    wrote_a = False
    wrote_b = False
    try:
        fd = os.open(probe_a, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, b"Aa")
        os.close(fd)
        wrote_a = True
        try:
            fd = os.open(probe_b, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, b"aA")
            os.close(fd)
            wrote_b = True
            return False
        except FileExistsError:
            return True
        except OSError:
            return os.path.normcase("Aa") == os.path.normcase("aA")
    except OSError:
        return os.path.normcase("Aa") == os.path.normcase("aA")
    finally:
        if wrote_a:
            try:
                os.remove(probe_a)
            except OSError:
                pass
        if wrote_b:
            try:
                os.remove(probe_b)
            except OSError:
                pass


def _dest_claim_key(data_path, folds_case):
    normalized = os.path.normpath(data_path)
    return normalized.casefold() if folds_case else normalized


def _case_variant_digest(hash_source):
    """Hex tag for a case-variant copy, derived from the source path.

    Hash the evidence-relative spelling, case preserved, separators normalized,
    so the same source maps to the same tag on every search, every run and
    every machine, and each case variant gets its own tag.
    """
    normalized = str(hash_source).replace('\\', '/').lstrip('/')
    return hashlib.sha256(normalized.encode('utf-8', 'surrogatepass')).hexdigest()


def _case_variant_candidates(root, ext, digest):
    """Candidate alternate names: short tag, full digest, then a counter tail.

    The later tiers only matter when a candidate name is already taken, for
    example by an evidence file that legitimately carries the tagged name. The
    walk over them stays finite because every blocker is a recorded claim or an
    existing file, and both sets are finite.
    """
    yield f"{root}~case-{digest[:8]}{ext}"
    yield f"{root}~case-{digest}{ext}"
    n = 2
    while True:
        yield f"{root}~case-{digest}-{n}{ext}"
        n += 1


def _disambiguated_data_path(data_path, source_key, dest_claims, folds_case,
                             hash_source=None):
    """Pick a dest that does not overwrite a different source.

    When the wanted destination is already claimed by a different source (two
    evidence paths differing only in case fold together on a case-insensitive
    report volume), the copy is written to name~case-<tag>.ext instead. The tag
    names the source rather than the arrival order, so re-searches and repeat
    runs land on the same path with nothing to remember.
    """
    key = _dest_claim_key(data_path, folds_case)
    claimed = dest_claims.get(key)
    if claimed is not None:
        claimed_source, claimed_path = claimed
        if claimed_source == source_key:
            return claimed_path
    elif not os.path.lexists(data_path):
        dest_claims[key] = (source_key, data_path)
        return data_path
    root, ext = os.path.splitext(data_path)
    digest = _case_variant_digest(source_key if hash_source is None else hash_source)
    for alt in _case_variant_candidates(root, ext, digest):
        alt_key = _dest_claim_key(alt, folds_case)
        claimed = dest_claims.get(alt_key)
        if claimed is not None:
            if claimed[0] == source_key:
                return claimed[1]
            continue
        if os.path.lexists(alt):
            continue
        dest_claims[alt_key] = (source_key, alt)
        logfunc(
            f"INFO: destination {data_path} already holds a different source; "
            f"writing {source_key} to {alt}"
        )
        return alt


class FileInfo:
    """
    A class to store file metadata information.
    Attributes:
        source_path (str): Where the file sits in the evidence: an archive
            member name as stored, a path relative to the input directory, a
            volume path inside a raw image, or the file name for a single-file
            input. Never a path on the examiner's machine.
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

    def __init__(self):
        # Refined by _init_dest_guard once the subclass knows its data folder;
        # the defaults leave the dest-guard a pass-through.
        self._dest_claims = {}
        self._data_folder_folds_case = False

    def cleanup(self):
        '''close any open handles'''

    def _init_dest_guard(self, data_folder):
        self._dest_claims = {}
        self._data_folder_folds_case = _probe_volume_case_insensitive(data_folder)

    def _unique_data_path(self, data_path, source_key, hash_source=None):
        return _disambiguated_data_path(
            data_path, source_key, self._dest_claims,
            self._data_folder_folds_case, hash_source=hash_source
        )


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
        self._init_dest_guard(self.data_folder)

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
                # Relative to the input root, so the staged tree and the recorded
                # source path do not depend on where the extraction sits on the
                # examiner's machine, on a trailing separator in the input path or
                # on the \\?\ prefix the entry points add on Windows. The former
                # prefix slice dropped the first character of every staged path
                # after a trailing separator, and every dot when the input was '.'.
                item_rel_path = os.path.relpath(item, self.directory)
                source_path = item_rel_path.replace('\\', '/')
                data_path = os.path.join(self.data_folder, item_rel_path)
                if item not in self.copied or force:
                    try:
                        if os.path.isdir(item):
                            pass
                        elif os.path.isfile(item):
                            data_path = self._unique_data_path(
                                data_path, item, hash_source=source_path)
                            os.makedirs(os.path.dirname(data_path), exist_ok=True)
                            copy2(item, data_path)
                            self.copied[item] = data_path
                            creation_date = Path(item).stat().st_ctime
                            modification_date = Path(item).stat().st_mtime
                            file_info = FileInfo(source_path, creation_date, modification_date)
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


def _compressed_tar_streams():
    """The reader classes tarfile wraps a compressed tar in, for the codecs this Python has."""
    streams = []
    for module, name in (('gzip', 'GzipFile'), ('bz2', 'BZ2File'), ('lzma', 'LZMAFile'),
                         ('compression.zstd', 'ZstdFile')):
        try:
            streams.append(getattr(importlib.import_module(module), name))
        except (ImportError, AttributeError):
            pass
    return tuple(streams)


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

    A tar can store one member name more than once (an appended archive does).
    A search matches each name once. Entries holding the same bytes are staged
    once, from the last entry, which is the one tar itself extracts. When the
    entries differ, the entry recording the latest modification time is staged
    under the name (the earlier entry on a tie), and every other version is
    staged beside it as <name>~tar-entry-<N><ext>, N being the entry's position
    in the archive, and logged. Those other versions are not returned to
    artifacts, so an artifact reads one version of each name.
    """

    def __init__(self, tar_file_path, data_folder):
        FileSeekerBase.__init__(self)
        self.is_gzip = tar_file_path.lower().endswith('gz')
        mode = 'r:gz' if self.is_gzip else 'r'
        self.tar_file = tarfile.open(tar_file_path, mode)
        self.data_folder = data_folder
        self._spool_path = None
        if isinstance(self.tar_file.fileobj, _compressed_tar_streams()):
            self._read_from_a_decompressed_copy(tar_file_path, mode)
        self.searched = {}
        self.copied = {}
        self.file_infos = {}
        self._init_dest_guard(self.data_folder)
        self._search_members, self._other_versions = self._index_member_names()

    def _read_from_a_decompressed_copy(self, tar_file_path, mode):
        """Decompress a compressed tar once and read the plain copy instead.

        A compressed stream can only seek backwards by decompressing again from its
        start. Each search reads its matches in archive order, but artifacts search one
        after another, so reading a compressed tar in place rewinds over and over. On a
        5.36 GB Android extraction that was 56 rewinds and 220 GB decompressed as a
        .tar.gz (347 s against 33 s for the plain tar), and about two hours projected
        as a .tar.xz. The copy sits in the report folder and is deleted by cleanup(),
        or at exit if a run never reaches it. When it cannot be written, the archive is
        read in place as before.
        """
        spool = os.path.join(os.path.dirname(os.path.normpath(self.data_folder)), '_decompressed_input.tar')
        logfunc(f'Decompressing {os.path.basename(tar_file_path)} once so its files can be read in any order')
        started = timex.time()
        written = False
        try:
            self.tar_file.fileobj.seek(0)
            with open(spool, 'wb') as out:
                copyfileobj(self.tar_file.fileobj, out, 16 << 20)
            written = True
        except OSError as ex:
            logfunc(f'Could not write the decompressed copy ({ex.strerror or type(ex).__name__}); '
                    'reading the compressed archive in place, which is much slower')
        finally:
            if not written and os.path.exists(spool):
                os.remove(spool)
        self.tar_file.close()
        if not written:
            self.tar_file = tarfile.open(tar_file_path, mode)
            return
        self._spool_path = spool
        atexit.register(self._discard_spool)
        self.tar_file = tarfile.open(spool, 'r:')
        logfunc(f'Decompressed {os.path.getsize(spool):,} bytes in {timex.time() - started:.0f} s')

    def _index_member_names(self):
        """One member per distinct name, in archive order, and the other versions of any name stored twice."""
        by_name = {}
        for index, member in enumerate(self.tar_file.getmembers()):
            by_name.setdefault(member.name, []).append((index, member))
        search_members = []
        other_versions = {}
        repeated = differing = 0
        for name, entries in by_name.items():
            if len(entries) < 2:
                search_members.append(entries[0][1])
                continue
            repeated += 1
            contents = [self._member_content_key(member) for _, member in entries]
            if len(set(contents)) == 1:
                search_members.append(entries[-1][1])
                continue
            differing += 1
            # Latest recorded time wins; on a tie the earlier entry does.
            pick = max(((member.mtime, -position), position)
                       for position, (_, member) in enumerate(entries))[1]
            search_members.append(entries[pick][1])
            seen = {contents[pick]}
            for position, (index, member) in enumerate(entries):
                if position != pick and contents[position] not in seen:
                    seen.add(contents[position])
                    other_versions.setdefault(name, []).append((index, member))
        if repeated:
            versions = sum(len(v) for v in other_versions.values())
            logfunc(f'INFO: {repeated} member name(s) are stored more than once in this archive. '
                    f'{repeated - differing} repeat the same content and are staged once. '
                    f'{differing} hold different content: the entry recording the latest '
                    f'modification time is staged under the name, and {versions} other version(s) '
                    f'are staged beside it as <name>~tar-entry-<N><ext>, N being the entry\'s '
                    f'position in the archive. Artifacts read the version under the name.')
        return search_members, other_versions

    def _member_content_key(self, member):
        """What a member holds: the digest of a regular file's bytes, else its type and link target."""
        if not member.isreg():
            return (member.type, member.linkname, member.size)
        digest = hashlib.sha256()
        with tarfile.ExFileObject(self.tar_file, member) as fin:
            for chunk in iter(lambda: fin.read(1 << 20), b''):
                digest.update(chunk)
        return (member.size, digest.hexdigest())

    def search(self, filepattern, return_on_first_hit=False, force=False):
        if filepattern in self.searched and not force:
            pathlist = self.searched[filepattern]
            return self.searched[filepattern][0] if return_on_first_hit and pathlist else pathlist
        pathlist = []
        pat = _compile_pattern(normcase(filepattern))
        root = normcase("root/")
        for member in self._search_members:
            if pat(root + normcase(member.name)) is not None:
                clean_name = sanitize_file_path(member.name)
                full_path = os.path.join(self.data_folder, Path(clean_name))
                if member.name not in self.copied or force:
                    try:
                        if member.isdir():
                            os.makedirs(full_path, exist_ok=True)
                        else:
                            full_path = self._unique_data_path(str(full_path), member.name)
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
                            self._stage_other_versions(member.name)
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

    def _stage_other_versions(self, name):
        """Stage each other version of a name whose entries hold different content."""
        for index, member in self._other_versions.get(name, ()):
            base, ext = os.path.splitext(os.path.join(self.data_folder, Path(sanitize_file_path(name))))
            dest_path = self._unique_data_path(
                f'{base}~tar-entry-{index}{ext}', (name, index),
                hash_source=f'{name}~tar-entry-{index}')
            try:
                parent = os.path.dirname(dest_path)
                if parent:
                    os.makedirs(parent, exist_ok=True)
                with tarfile.ExFileObject(self.tar_file, member) as fin, open(dest_path, 'wb') as fout:
                    copyfileobj(fin, fout)
                os.utime(dest_path, (member.mtime, member.mtime))
                logfunc(f'INFO: {name} is stored more than once with different content; '
                        f'entry {index} ({member.size} bytes) staged as {dest_path}')
            except OSError as ex:
                logfunc(f'Could not write file to filesystem, path was {name} (entry {index}) ' + str(ex))

    def cleanup(self):
        self.tar_file.close()
        if self._spool_path:
            atexit.unregister(self._discard_spool)
            self._discard_spool()

    def _discard_spool(self):
        """Close the archive and delete the decompressed copy made for it."""
        self.tar_file.close()
        if self._spool_path and os.path.exists(self._spool_path):
            os.remove(self._spool_path)
        self._spool_path = None


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

    A zip can store one member name more than once. A search matches each name
    once. Entries repeating the same content (same CRC-32 and size) are staged
    once, from the entry ZipFile resolves the name to. When the entries hold
    different content, the entry recording the latest modification time is
    staged under the name (the earlier entry on a tie), and every other
    version is staged beside it as <name>~zip-entry-<N><ext>, N being the
    entry's position in the archive, and logged. Those other versions are not
    returned to artifacts, so an artifact reads one version of each name.
    """

    def __init__(self, zip_file_path, data_folder):
        FileSeekerBase.__init__(self)
        self.zip_file = ZipFile(zip_file_path)
        self.name_list = self.zip_file.namelist()
        self.data_folder = data_folder
        self.searched = {}
        self.copied = {}
        self.file_infos = {}
        self._init_dest_guard(self.data_folder)
        self._search_names, self._chosen, self._other_versions = self._index_member_names()

    def _index_member_names(self):
        """Distinct member names, and how to stage a name stored more than once.

        Returns the distinct names in archive order, the entry to stage under
        each name whose copies differ, and the other versions of those names.

        ZipFile keys NameToInfo on the member name while it reads the central
        directory, so that dict is short by exactly the number of names stored more
        than once. Reading its length costs nothing and answers the only question
        the walk below exists to answer. Grouping every member to learn the same
        thing costs a dict entry, a list and a tuple per member: on a 630,560 member
        archive that measured 138 MB, spent to discover that no name repeats.
        NameToInfo is not part of zipfile's documented surface, so an absent one
        falls through to the walk rather than assuming anything.
        """
        by_member_name = getattr(self.zip_file, 'NameToInfo', None)
        if by_member_name is not None and len(self.name_list) == len(by_member_name):
            return list(self.name_list), {}, {}
        by_name = {}
        for index, info in enumerate(self.zip_file.infolist()):
            by_name.setdefault(info.filename, []).append((index, info))
        chosen = {}
        other_versions = {}
        repeated = 0
        for name, entries in by_name.items():
            if len(entries) < 2:
                continue
            repeated += 1
            if len({(info.CRC, info.file_size) for _, info in entries}) == 1:
                continue
            times = self._recorded_mtimes([info for _, info in entries])
            # Latest recorded time wins; on a tie the earlier entry does.
            pick = max(((stamp, -i), i) for i, stamp in enumerate(times))[1]
            chosen[name] = entries[pick][1]
            seen = {(entries[pick][1].CRC, entries[pick][1].file_size)}
            for index, info in entries[:pick] + entries[pick + 1:]:
                content = (info.CRC, info.file_size)
                if content not in seen:
                    seen.add(content)
                    other_versions.setdefault(name, []).append((index, info))
        if repeated:
            versions = sum(len(v) for v in other_versions.values())
            logfunc(f'INFO: {repeated} member name(s) are stored more than once in this archive. '
                    f'{repeated - len(chosen)} repeat the same content (CRC-32 and size) and are '
                    f'staged once. {len(chosen)} hold different content: the entry recording the '
                    f'latest modification time is staged under the name, and {versions} other '
                    f'version(s) are staged beside it as <name>~zip-entry-<N><ext>, N being the '
                    f'entry\'s position in the archive. Artifacts read the version under the name.')
        return list(by_name), chosen, other_versions

    @staticmethod
    def _recorded_mtimes(infos):
        """Modification times recorded for entries of one name, on one clock.

        Uses the extended timestamp (0x5455) when every entry carries one, else
        the NTFS times (0x000a), else the DOS date and time, so entries are only
        ever compared on the same clock.
        """
        def fields(info):
            found = {}
            extra, offset = info.extra, 0
            while offset + 4 <= len(extra):
                header_id, size = struct.unpack_from('<HH', extra, offset)
                body = extra[offset + 4:offset + 4 + size]
                if header_id == 0x5455 and len(body) >= 5 and body[0] & 1:
                    found['unix'] = float(struct.unpack_from('<I', body, 1)[0])
                elif header_id == 0x000a and len(body) >= 16:
                    tag, tag_size = struct.unpack_from('<HH', body, 4)
                    if tag == 1 and tag_size >= 8:
                        found['ntfs'] = struct.unpack_from('<Q', body, 8)[0]
                offset += 4 + size
            found['dos'] = info.date_time
            return found
        recorded = [fields(info) for info in infos]
        for clock in ('unix', 'ntfs', 'dos'):
            if all(clock in r for r in recorded):
                return [r[clock] for r in recorded]
        return [r['dos'] for r in recorded]

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
        for member in self._search_names:
            if member.startswith("__MACOSX"):
                continue
            if pat(root + normcase(member)) is not None:
                if member not in self.copied or force:
                    source = self._chosen.get(member, member)
                    try:
                        if member.endswith('/'):
                            # Case-variant directories fold into one on a
                            # case-insensitive volume; their files disambiguate
                            # individually, so directory members take no guard.
                            extracted_path = self._extract_member(member, source=source)
                        else:
                            intended = self._intended_extract_path(member)
                            extracted_path = self._extract_member(
                                member,
                                dest_path=self._unique_data_path(intended, member),
                                source=source)
                        f = self.zip_file.getinfo(member) if source is member else source
                        creation_date, modification_date = self.decode_extended_timestamp(f.extra)
                        file_info = FileInfo(member, creation_date, modification_date)
                        self.file_infos[extracted_path] = file_info
                        date_time = f.date_time
                        date_time = timex.mktime(date_time + (0, 0, -1))
                        os.utime(extracted_path, (date_time, date_time))
                        self.copied[member] = extracted_path
                    except OSError as ex:
                        logfunc(f'Could not write file to filesystem, path was {member} ' + str(ex))
                        continue
                    self._stage_other_versions(member)
                else:
                    extracted_path = self.copied[member]
                pathlist.append(extracted_path)
                if return_on_first_hit:
                    self.searched[filepattern] = pathlist
                    return extracted_path
        self.searched[filepattern] = pathlist
        return pathlist

    def _stage_other_versions(self, member):
        """Stage each other version of a name whose copies hold different content."""
        for index, info in self._other_versions.get(member, ()):
            base, ext = os.path.splitext(self._intended_extract_path(member))
            dest_path = self._unique_data_path(
                f'{base}~zip-entry-{index}{ext}', (member, index),
                hash_source=f'{member}~zip-entry-{index}')
            try:
                parent = os.path.dirname(dest_path)
                if parent:
                    os.makedirs(parent, exist_ok=True)
                with self.zip_file.open(info) as fin, open(dest_path, 'wb') as fout:
                    copyfileobj(fin, fout)
                date_time = timex.mktime(info.date_time + (0, 0, -1))
                os.utime(dest_path, (date_time, date_time))
                logfunc(f'INFO: {member} is stored more than once with different content; '
                        f'entry {index} ({info.file_size} bytes) staged as {dest_path}')
            except OSError as ex:
                logfunc(f'Could not write file to filesystem, path was {member} (entry {index}) ' + str(ex))

    def _intended_extract_path(self, member):
        clean_member = sanitize_file_path(member)
        parts = [part for part in clean_member.replace('\\', '/').split('/')
                 if part not in ('', '.', '..')]
        if not parts:
            return self.data_folder
        return os.path.join(self.data_folder, *parts)

    def _extract_member(self, member, dest_path=None, source=None):
        """Extract one member, sanitizing names ZipFile.extract() cannot write.

        ZipFile.extract() only replaces a fixed set of printable characters
        (:<>|"?*) and only on Windows; ASCII control characters in the stored
        name (present in real iOS extractions, e.g. chronod icon files) reach
        the OS untouched and Windows rejects them with EINVAL. Members whose
        names need sanitizing are written out manually to a cleaned path.

        dest_path, when given, is the already-disambiguated destination so a
        later case-variant member cannot overwrite an earlier one. source,
        when given, is the entry to read (a ZipInfo) for a name the archive
        stores more than once; otherwise the name resolves as ZipFile resolves it.
        """
        intended = self._intended_extract_path(member)
        if dest_path is None:
            dest_path = intended
        if source is None:
            source = member
        clean_member = sanitize_file_path(member)
        if dest_path == intended and clean_member == member:
            return self.zip_file.extract(source, path=self.data_folder)
        if member.endswith('/'):
            os.makedirs(dest_path, exist_ok=True)
        else:
            parent = os.path.dirname(dest_path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with self.zip_file.open(source) as fin, open(dest_path, 'wb') as fout:
                fout.write(fin.read())
        return dest_path

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
        self._init_dest_guard(self.data_folder)

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
                    dest_data_path = self._unique_data_path(
                        dest_data_path, self.single_file_abs_path,
                        hash_source=self.single_file_basename)
                    os.makedirs(
                        os.path.dirname(dest_data_path) or self.data_folder,
                        exist_ok=True,
                    )
                    copy2(self.single_file_abs_path, dest_data_path)
                    self.copied[self.single_file_abs_path] = dest_data_path
                    s = Path(self.single_file_abs_path).stat()
                    # The file name is all that places this input in the evidence;
                    # the directory it came from is the examiner's, not the device's.
                    file_info_obj = FileInfo(self.single_file_basename, s.st_ctime, s.st_mtime)
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
