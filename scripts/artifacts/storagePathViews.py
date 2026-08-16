"""Collapse the duplicate storage paths an Android extraction can carry for one file.

A full file system extraction commonly holds the same app data directory under more
than one path. On the tested images:

    data/data/<pkg>/...                         credential encrypted storage, user 0
    data/user/<user>/<pkg>/...                  credential encrypted storage
    data_mirror/data_ce/<volume>/<user>/<pkg>/  credential encrypted storage (Android 11+)
    data/user_de/<user>/<pkg>/...               device encrypted storage
    data_mirror/data_de/<volume>/<user>/<pkg>/  device encrypted storage (Android 11+)

An artifact that iterates every file its glob matched then reads the same database or
preferences file two or three times and reports every row that many times.

Credential encrypted and device encrypted storage are separate directories holding
different files, so they are never collapsed together: on pixel3_a12
com.android.providers.telephony/databases/mmssms.db exists in both and the two copies
differ. The Android user id is part of the key for the same reason, so a second user's
data is never folded into user 0's.

Keying is done on the evidence relative path rather than the extracted path. The report's
own extraction folder is itself named "data", so a pattern applied to the full on-disk
path can rewrite the harness boundary instead of the evidence path on extractions whose
members start with "data/".
"""

import re

# Ordered so the first alternative that matches is also the preferred spelling to keep.
_VIEWS = (
    ('ce', re.compile(r'(^|/)data/data/')),
    ('de', re.compile(r'(^|/)data/user_de/(\d+)/')),
    ('ce', re.compile(r'(^|/)data/user/(\d+)/')),
    ('ce', re.compile(r'(^|/)data_mirror/data_ce/[^/]+/(\d+)/')),
    ('de', re.compile(r'(^|/)data_mirror/data_de/[^/]+/(\d+)/')),
)


def canonical_path(relative_path):
    """(key, rank) for a path under an app data directory, else (path, 0).

    The key is the path with the storage view replaced by the storage class and Android
    user it denotes, so every spelling of one file shares a key. The rank orders the
    spellings, lowest first, so the copy that is kept is the same one on every image.
    """
    path = str(relative_path).replace('\\', '/')
    for rank, (storage, pattern) in enumerate(_VIEWS):
        match = pattern.search(path)
        if not match:
            continue
        user = match.group(2) if match.lastindex and match.lastindex >= 2 else '0'
        key = (f'{path[:match.start()]}{match.group(1)}'
               f'\x00{storage}:{user}\x00/{path[match.end():]}')
        return key, rank
    return path, 0


def unique_files(context, files=None):
    """The context's files with the duplicate storage views of each file removed.

    Order follows the first appearance of each file, so an artifact that relied on the
    order the seeker returned keeps it. Where an extraction carries several copies the
    one under the shortest, most conventional path is the one reported.
    """
    if files is None:
        files = context.get_files_found()
    best = {}
    order = []
    for file_found in files:
        file_found = str(file_found)
        key, rank = canonical_path(context.get_relative_path(file_found))
        if key not in best:
            best[key] = (rank, file_found)
            order.append(key)
        elif rank < best[key][0]:
            best[key] = (rank, file_found)
    return [best[key][1] for key in order]
