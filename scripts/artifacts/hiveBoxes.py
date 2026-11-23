__artifacts_v2__ = {
    "hive_boxes": {
        "name": "Hive - Boxes and Superseded Frames",
        "description": "One row per file named *.hive that reads without an error, with the folder "
                       "name the App column takes from its path, the frames the read returned, the "
                       "entries a live read returns, and the frames holding an overwritten or a "
                       "deleted value. A file is taken as a Hive box by its name, because the format "
                       "has no signature to check. Several storage views of one path are reported "
                       "once.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-10-27",
        "last_update_date": "2026-11-22",
        "requirements": "none",
        "category": "Hive",
        "notes": "Hive is a key-value store used by Flutter applications through the hive and "
                 "hive_ce packages. A box is an append-only log of frames: a write appends a new "
                 "frame for the key rather than replacing the old one, and a delete appends a "
                 "tombstone. What the application reads back is the last frame written for each key "
                 "that has not since been deleted, so the frames a file still holds can carry "
                 "values the application has already replaced or removed. This artifact reports "
                 "where the boxes are and how far the file's contents and the live view have "
                 "diverged. It does not report keys or values. A box that appears under several "
                 "storage views of one path (data/data, data/user/0, data_mirror) is reported once, "
                 "and a rollback snapshot byte-identical to its live copy is left out. A file whose "
                 "read raises an error this module handles is written to the log and gets no row, "
                 "even when it holds other readable frames. One value the reader cannot convert "
                 "does this (on synthetic boxes: a BigInt holding non-digit text, an int frame "
                 "holding NaN). An int frame holding infinity raises an error this module does not "
                 "handle, so the artifact fails and produces no table for that run. "
                 "'Frames Read' counts every frame the read returned: value frames, tombstones, "
                 "frames that did not decode, and the frame at which a read stopped, if any. A frame "
                 "that failed its checksum or is cut short is counted there but was not verified. "
                 "For a box that reads as encrypted it counts every frame of the chain, none of them "
                 "verified. 'Entries a Live Read Returns' is this reader's count of keys whose last "
                 "readable frame, up to where the read ended, is not a tombstone. It is not taken "
                 "from the application. "
                 "'Frames Holding an Overwritten Value' counts value frames whose key's next "
                 "readable frame in the file is another write. 'Frames Holding a Deleted Value' "
                 "counts value frames whose key's next readable frame in the file is a tombstone. A "
                 "frame whose checksum failed, or whose key or value did not decode, is counted in "
                 "neither. 'How the Box Read' names the offset where the read stopped, and reports "
                 "a clean end only when the frames account for the whole file. Hive rewrites a box "
                 "once more than 60 frames have been superseded or deleted and that count exceeds "
                 "15 percent of the live entry count (isar/hive v2.2.3, "
                 "box/default_compaction_strategy.dart with box/keystore.dart). An overwrite counts "
                 "towards that total, not just a delete, and an application can supply its own "
                 "strategy or call compact() directly. The rewrite leaves no marker, so a row "
                 "showing no overwritten and no deleted frames does not establish that nothing was "
                 "ever overwritten or deleted in that box. Clearing a box truncates its file to zero "
                 "bytes (isar/hive v2.2.3, https://github.com/isar/hive/blob/470473ffc1ba39f6c90f31ababe0ee63b76b69fe/hive/lib/src/box/box_base_impl.dart#L137-L142 and https://github.com/isar/hive/blob/470473ffc1ba39f6c90f31ababe0ee63b76b69fe/hive/lib/src/backend/vm/storage_backend_vm.dart#L202-L208) and leaves no marker either, so a row reading "
                 "'the file is empty' does not establish that the box never held data. Hive also truncates a damaged tail "
                 "itself on the next open when crash recovery is enabled (isar/hive v2.2.3, "
                 "backend/vm/storage_backend_vm.dart), so a row naming a failed checksum or a "
                 "cut-short frame is consistent with the application not having reopened that box "
                 "since the damage, or with recovery being off. The copy in the extraction can also "
                 "have been taken while a write was in flight. Separately, the reader refuses a "
                 "frame declaring more than 1 MiB, which Hive itself does not, so a box holding a "
                 "larger frame reads as a stop at that offset. The App column is a folder name read from the path by position: the first folder above the box that carries a dot and follows a storage root name (data, user, user_de, data_ce, data_de, data_mirror, misc_ce, misc_de, null) or an all-digit folder. Under an app data directory this is normally the package directory, as on all 174 rows of the 18 images run that hold a box (emu_a15_oss_v1 to emu_a15_oss_v17 and sharon_a14). Outside one, such as shared storage, it can be another dotted folder. It is not checked against the installed packages. It is read by position only, so it can be wrong: a dotted folder that follows an all-digit folder earlier in the path is taken first, and when the package directory carries no dot a dotted folder deeper in the path that follows one of those names is reported instead. It is empty when no such folder exists. A box whose every frame fails its checksum while every key parses, with the "
                 "frames ending on the file end, is reported as reading like an encrypted box, and "
                 "its values are not decoded, because the encryption key is not in the file. For "
                 "such a row the entry, overwritten and deleted counts hold 0 and were not measured. "
                 "Only 'How the Box Read' says so, so do not filter or sort on those counts without "
                 "it. A "
                 "box whose every frame is damaged can read the same way, when each key still "
                 "parses and the frame lengths still chain to the end of the file. Measured on "
                 "emu_a15_oss_v14 (14 rows: 7 empty files, 2 boxes holding an overwritten value, 1 "
                 "box holding a deleted value) and emu_a15_oss_v15 (23 rows: 10 empty files, 5 "
                 "boxes holding an overwritten value, 1 box holding a deleted value). The 18 images "
                 "named above produced only two of the 'How the Box Read' outcomes, the read "
                 "reaching the end of the file and the file being empty; the truncated, failed-CRC, "
                 "undecoded-frame, encrypted, stopped-early and no-frame-at-offset-0 branches are "
                 "unexercised on those images. The reader's own tests (tests/test_hive_parser.py in "
                 "abrignoni/hive-parser at the vendored commit) cover a failed CRC, a truncated final "
                 "frame, an undecodable value, the encrypted shape and an unusable length at offset "
                 "0. A read that stops after good frames without recording a frame, and the phrases "
                 "this module builds for all of these, are covered by "
                 "admin/test/scripts/test_hive_boxes.py. No test holds a frame over 1 MiB that fits "
                 "inside the file. The reader is scripts/hive_parser.py, vendored from abrignoni/hive-parser.",
        "paths": ('*.hive',),
        "output_types": "standard",
        "artifact_icon": "database",
        "sample_data": {
            "emu_a15_oss_v14": "14 rows | 7 empty, 2 boxes with overwritten frames, 1 with deleted frames",
            "emu_a15_oss_v15": "23 rows | 10 empty, 5 boxes with overwritten frames, 1 with deleted frames",
        },
    }
}

import os

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.artifacts.storagePathViews import unique_files
from scripts.hive_parser import (HiveError, displaced_counts, live_entries,
                                 looks_encrypted, read_frames)

# What a file named .hive that is not a Hive box, or is damaged, can raise.
READ_ERRORS = (HiveError, OSError, ValueError, IndexError, MemoryError)

# The directory names Android puts between the storage root and the package
# directory. The package is the segment that follows one of these, or follows the
# user id, so it is found by position rather than by guessing at its shape: the
# commonest package names carry one dot (com.kmplayer), not two.
_ROOT_MARKERS = {'data', 'data_ce', 'data_de', 'data_mirror', 'user', 'user_de',
                 'misc_ce', 'misc_de', 'null'}


def _owning_app(relative_path):
    """The package directory a box sits under, or '' when the path has none.

    Matched as a whole path segment in the position Android puts it. A substring
    test puts a box under the first package whose name happens to appear anywhere
    in the path, which silently attributes one app's data to another.
    """
    segments = relative_path.replace('\\', '/').split('/')
    for index, segment in enumerate(segments[:-2]):
        if not (segment in _ROOT_MARKERS or segment.isdigit()):
            continue
        following = segments[index + 1]
        if following in _ROOT_MARKERS or following.isdigit():
            continue
        if '.' in following:
            return following
    return ''


def _how_it_read(frames, encrypted, size):
    """Why the frame count and the entry count differ, or that nothing stopped the read.

    The counts on their own do not say whether a smaller number means the box is
    small or means the read stopped early, and those are different findings. The
    reader's walk gives up without recording a frame when a declared length is
    unusable, so a clean end is reported only once the frames account for the
    whole file.
    """
    if not frames:
        if size == 0:
            return 'the file is empty'
        return f'no frame could be read at offset 0, in a file of {size} byte(s)'
    if encrypted:
        return ('every frame failed its CRC while its keys read cleanly, which is how an '
                'encrypted box reads; values are not decoded')
    said = []
    unverified = [f for f in frames if not f['crc_ok']]
    if unverified:
        first = unverified[0]
        if first['truncated']:
            said.append(f'the read stopped at offset {first["offset"]}, where a frame is '
                        f'cut short by the end of the file')
        else:
            said.append(f'the read stopped at offset {first["offset"]}, where a frame '
                        f'failed its own CRC')
    else:
        end = frames[-1]['offset'] + frames[-1]['length']
        if end < size:
            said.append(f'the read stopped at offset {end}, where no further frame could be '
                        f'read, leaving {size - end} byte(s) unread')
    undecoded = [f for f in frames if f['error'] and f['crc_ok']]
    if undecoded:
        said.append(f'{len(undecoded)} frame(s) did not decode cleanly and are left out '
                    f'of the entry and displaced counts')
    return '; '.join(said) if said else 'the read reached the end of the file'


@artifact_processor
def hive_boxes(context):
    data_list = []
    sources = []

    for file_found in unique_files(context):
        file_found = str(file_found)
        if os.path.isdir(file_found):
            continue
        try:
            size = os.path.getsize(file_found)
            frames = read_frames(file_found)
        except READ_ERRORS as ex:
            logfunc(f'Hive boxes: {os.path.basename(file_found)} could not be read as a '
                    f'Hive box: {type(ex).__name__}: {ex}')
            continue

        encrypted = looks_encrypted(frames)
        # An encrypted box's values are ciphertext, so it has no entries to read back
        # and no displaced values that can be counted.
        live = {} if encrypted else live_entries(frames)
        overwritten, removed = (0, 0) if encrypted else displaced_counts(frames)

        relative = context.get_relative_path(file_found)
        data_list.append((
            _owning_app(relative),
            relative,
            len(frames),
            len(live),
            overwritten,
            removed,
            _how_it_read(frames, encrypted, size),
        ))
        sources.append(file_found)

    # The boxes holding what a live read drops are the reason this table exists, so
    # they lead it.
    data_list.sort(key=lambda row: (-(row[4] + row[5]), row[1]))

    data_headers = (
        'App',
        'Box',
        'Frames Read',
        'Entries a Live Read Returns',
        'Frames Holding an Overwritten Value',
        'Frames Holding a Deleted Value',
        'How the Box Read',
    )
    return data_headers, data_list, '\n'.join(sources)
