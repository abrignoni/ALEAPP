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

An extraction can instead expose the userdata partition itself, in a folder named
userdata that holds what the layouts above hold under data/. The same directories then
appear without the leading data/:

    userdata/data/<pkg>/...                     credential encrypted storage, user 0
    userdata/user/<user>/<pkg>/...              credential encrypted storage
    userdata/user_de/<user>/<pkg>/...           device encrypted storage

Of the 45 registered Android corpora only samsungs20_a13 has this shape (member listing
of every corpus, 2026-10-12): 43,280 files under userdata/data, 7,078 under
userdata/user/150 and 1,184 under userdata/user_de for users 0 and 150. It carries no
userdata/user/0, so nothing collapses there; the views give those files the same storage
class and Android user key as the other layouts. They are tried first because 68 files
on that image sit in a data/user/<n> folder inside an app's own cache directory (50
under userdata/data, 18 under userdata/user/150), and the enclosing app data directory
is the one that says whose storage it is. On the other 44 corpora no file's key or kept
copy changed (same listing, before and after).

Credential encrypted and device encrypted storage are separate directories holding
different files, so they are never collapsed together: on pixel3_a12
com.android.providers.telephony/databases/mmssms.db exists in both and the two copies
differ. The Android user id is part of the key for the same reason, so a second user's
data is never folded into user 0's.

The copies are usually byte identical, but not always, and the difference is worth
knowing when reading a report. On samsunga53_a14, 19 of the 35,177 files present under all
three credential encrypted views differ between them: write ahead logs, shared memory
files and logs an app was writing while the extraction ran, so each view caught a slightly
different moment. By default the copy under the preferred spelling is the one reported and
the others are not read. Measured 2026-08-27; on that image no artifact's row count changed
as a result, and contacts2.db returns the same rows through all three views.

That does not hold across the corpus. Over 95 of the 96 registered Android images (listings
of 2026-11-26), 12,946 files on 25 images are held under more than one spelling with a -wal
or -journal beside at least one copy. In 238 of them the copies differ in the main file, the -wal or the
-journal. In 176 of those another copy
holds rows the preferred copy does not, and in 153 each copy holds rows the other lacks, so
no single copy is complete. In 4 the preferred copy did not open as a plain SQLite database;
whether another copy opened was not recorded. An artifact can pass keep_differing_views=True
to unique_files, which then also keeps every copy that differs, and pass its rows through
union_view_rows, which reports a row the copies share once. Eight artifacts do so. The option is off by
default because an artifact that keeps the extra copies without the union reports every
shared row once per copy.

Keying is done on the evidence relative path rather than the extracted path. The report's
own extraction folder is itself named "data", so a pattern applied to the full on-disk
path can rewrite the harness boundary instead of the evidence path on extractions whose
members start with "data/".

An update installed with rollback enabled can leave a third copy. Android keeps a snapshot of
the app's data from before the update under misc_ce/<user>/rollback/<rollback id>/<package>/
(credential encrypted) or misc_de/<user>/rollback/<rollback id>/<package>/ (device
encrypted), and a glob written for the app's own folder matches that copy too. On 7 of the 22
registered Android images (listings of 2026-10-27) 12 artifact modules read such snapshots, and
on s20fe_a13 the snapshot copy of MediaProvider's external.db doubled every Emulated Storage
Metadata table (Files 498 rows, 249 of them from the snapshot). A snapshot
is not a storage view: it was taken at one moment and may hold data the live copy no longer
does. So unique_files drops a snapshot only when the same call also holds the live copy of
that file, for the same storage class and user, the two are byte identical and, for a SQLite
database, their -wal and -journal hold the same content. Otherwise the
snapshot is kept, and its path names the rollback it belongs to. Of the 111 snapshot files
artifacts matched on those images, 98 had the size of their live copy and 13 did not. Run over
the 45 affected artifacts on the 7 images, this removed 363 of 18,361 rows, every one a copy of
a row the live file also gave. A database whose snapshot holds the same rows in different bytes
is still read twice: on russell_a14 and hc_pixel8pro_a16 the external.db snapshots differ from
the live file and their rows stay in Emulated Storage Metadata.
Those figures predate the -wal and -journal comparison. Across the 89 registered Android images
(2026-11-22), 11 snapshot databases on 5 images have a main file identical to the live copy and
a -wal that differs, and each reads different rows from its live copy. Artifact patterns reach
two: external.db on s20fe_a13 and picker.db on hc_pixel8pro_a16. A before and after run on those
two images left every artifact row count unchanged. On s20fe_a13 the snapshot external.db is now
read, and Emulated Storage Metadata leaves out its rows as repeats of the live rows. On
hc_pixel8pro_a16 the one artifact whose pattern reaches picker.db skips rollback snapshots.
The apexrollback folders beside them hold APEX module data, not an app data folder, and are
left as they are.
"""

import filecmp
import os
import re
from collections import Counter

# Ordered so the first alternative that matches is also the preferred spelling to keep.
_VIEWS = (
    ('ce', re.compile(r'(^|/)userdata/data/')),
    ('de', re.compile(r'(^|/)userdata/user_de/(\d+)/')),
    ('ce', re.compile(r'(^|/)userdata/user/(\d+)/')),
    ('ce', re.compile(r'(^|/)data/data/')),
    ('de', re.compile(r'(^|/)data/user_de/(\d+)/')),
    ('ce', re.compile(r'(^|/)data/user/(\d+)/')),
    ('ce', re.compile(r'(^|/)data_mirror/data_ce/[^/]+/(\d+)/')),
    ('de', re.compile(r'(^|/)data_mirror/data_de/[^/]+/(\d+)/')),
)

# A pre-update snapshot of an app's data folder, kept for a rollback (see the module notes).
_SNAPSHOT = re.compile(r'(^|/)(?:user)?data/misc_(ce|de)/(\d+)/rollback/\d+/')

_SQLITE_HEADER = b'SQLite format 3\x00'
# Each sidecar that can change what SQLite reads, and the size at or below which it holds nothing.
_CONTENT_SIDECARS = (('-wal', 32), ('-journal', 0))


def snapshot_key(relative_path):
    """The canonical_path key of the live file a rollback snapshot copies, or None."""
    path = str(relative_path).replace('\\', '/')
    match = _SNAPSHOT.search(path)
    if not match:
        return None
    return f'{path[:match.start()]}{match.group(1)}\x00{match.group(2)}:{match.group(3)}\x00/{path[match.end():]}'


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


def unique_files(context, files=None, keep_differing_views=False):
    """The context's files with the duplicate storage views of each file removed.

    Order follows the first appearance of each file, so an artifact that relied on the
    order the seeker returned keeps it. Where an extraction carries several copies the
    one under the shortest, most conventional path is the one reported. A rollback
    snapshot of a file is left out only when its live copy is among the files, the two
    are byte identical and, for a SQLite database, their -wal and -journal hold the same
    content; otherwise it is kept in its place.

    With keep_differing_views, a copy under another spelling is also kept, right after
    the preferred one, when it does not read the same: its bytes differ or, for a SQLite
    database, its -wal or -journal holds different content (the test applied to rollback
    snapshots). Copies that read the same as one already kept are still dropped. An
    artifact that sets it reads every differing copy, so it should pass its rows through
    union_view_rows to report a row the copies share once.
    """
    if files is None:
        files = context.get_files_found()
    best = {}
    order = []
    snapshots = {}
    for file_found in files:
        file_found = str(file_found)
        relative = context.get_relative_path(file_found)
        live_key = snapshot_key(relative)
        if live_key is not None:
            key = ('snapshot', str(relative).replace('\\', '/'))
            if key not in snapshots:
                snapshots[key] = (live_key, file_found)
                order.append(key)
            continue
        key, rank = canonical_path(relative)
        if key not in best:
            best[key] = [(rank, file_found)]
            order.append(key)
        elif all(path != file_found for _rank, path in best[key]):
            best[key].append((rank, file_found))
    kept_by_key = {}
    for key, copies in best.items():
        copies.sort(key=lambda copy: copy[0])
        kept = [copies[0][1]]
        if keep_differing_views:
            for _rank, path in copies[1:]:
                if not any(_same_database_state(path, other) for other in kept):
                    kept.append(path)
        kept_by_key[key] = kept
    result = []
    for key in order:
        if key in snapshots:
            live_key, file_found = snapshots[key]
            if any(_same_database_state(file_found, live) for live in kept_by_key.get(live_key, ())):
                continue
            result.append(file_found)
        else:
            result.extend(kept_by_key[key])
    return result


def union_view_rows(context, file_rows, ignore=()):
    """Rows read from every kept copy of each store, with the rows the copies share once.

    file_rows is a list of (path, rows) pairs, one per file read, in the order
    unique_files(context, keep_differing_views=True) returned the files. Copies of one
    file under different storage spellings (same storage class and Android user) are
    grouped, and a row is reported as many times as the copy holding it most often holds
    it: a row two copies share appears once, and a row only one copy holds appears with
    the rows of that copy. Positions in ignore (a Source File or path column, which
    differs between copies) are left out of the comparison. Rows keep their order and
    each comes from the path it was read from.
    """
    ignore = set(ignore)

    def value(row):
        return repr([cell for index, cell in enumerate(row) if index not in ignore])

    emitted = {}
    kept = []
    for path, rows in file_rows:
        key = canonical_path(context.get_relative_path(str(path)))[0]
        seen = emitted.setdefault(key, Counter())
        own = Counter()
        for row in rows:
            cell = value(row)
            own[cell] += 1
            if own[cell] > seen[cell]:
                seen[cell] += 1
                kept.append(row)
    return kept


def without_snapshot_repeats(rows, source_index=-1):
    """rows without the ones from a rollback snapshot that repeat a row the live copy gave.

    source_index is the position of each row's evidence relative source path. A row from a
    snapshot (see snapshot_key) is left out when a row from the live file of the same storage
    class and Android user is equal to it in every other position; each live row answers for
    one snapshot row. Every other row is kept, in order, so a record only the snapshot holds
    is still reported, under the snapshot's path.
    """
    def rest(row):
        values = list(row)
        del values[source_index]
        return repr(values)

    live = {}
    for row in rows:
        source = str(row[source_index])
        if snapshot_key(source) is None:
            live.setdefault(canonical_path(source)[0], Counter())[rest(row)] += 1
    kept = []
    for row in rows:
        key = snapshot_key(str(row[source_index]))
        if key is not None:
            counts = live.get(key)
            value = rest(row)
            if counts and counts[value] > 0:
                counts[value] -= 1
                continue
        kept.append(row)
    return kept

def _same_bytes(first, second):
    try:
        return filecmp.cmp(first, second, shallow=False)
    except OSError:
        return False


def _sidecar_size(path):
    try:
        return os.path.getsize(path)
    except FileNotFoundError:
        return 0


def _same_sidecar(first, second, empty_size):
    """True when two sidecars hold the same content. Up to empty_size bytes is no content."""
    try:
        first_size = _sidecar_size(first)
        second_size = _sidecar_size(second)
    except OSError:
        return False
    if first_size <= empty_size or second_size <= empty_size:
        return first_size <= empty_size and second_size <= empty_size
    return _same_bytes(first, second)


def _same_database_state(snapshot, live):
    """True when a snapshot reads the same as its live copy.

    The main files must be byte identical. For a SQLite database the -wal and -journal
    beside each must also match. SQLite reads the -wal with the main file, and a -journal
    is compared so a copy with one is not assumed to read the same. A missing sidecar, an empty one and a -wal of only its 32-byte header hold no content and
    count as equal. The -shm is an index SQLite rebuilds from the -wal, so it is not compared.
    """
    if not _same_bytes(snapshot, live):
        return False
    try:
        with open(snapshot, 'rb') as handle:
            if handle.read(len(_SQLITE_HEADER)) != _SQLITE_HEADER:
                return True
    except OSError:
        return False
    return all(_same_sidecar(snapshot + suffix, live + suffix, empty_size)
               for suffix, empty_size in _CONTENT_SIDECARS)


def android_user(relative_path):
    """The Android user whose storage holds a path under an app data directory.

    data/data and userdata/data are user 0's; data/user/<n>, data/user_de/<n>,
    userdata/user/<n>, userdata/user_de/<n> and data_mirror/data_*/<volume>/<n> name the
    user. A path outside every app data directory names no user and returns ''.
    """
    path = str(relative_path).replace('\\', '/')
    for _storage, pattern in _VIEWS:
        match = pattern.search(path)
        if match:
            return match.group(2) if match.lastindex and match.lastindex >= 2 else '0'
    return ''


def user_files(context, name, files=None, keep_differing_views=False):
    """[(path, Android user)] of the files called name, one per user and storage class.

    Sidecar files (-wal, -shm, -journal) are not matched because name is compared in full.
    The duplicate storage views of one file are collapsed by unique_files, and a second
    Android user's copy is kept, so an artifact that reads every pair reads every user's
    database once. With keep_differing_views a user can have more than one pair, one per
    copy that reads differently. A module that takes the first match instead reads one user's database
    and silently leaves out the others, which is how a Secure Folder user's near-empty
    copy can hide the owner's data.
    """
    pairs = []
    for path in unique_files(context, files, keep_differing_views):
        if str(path).replace('\\', '/').rsplit('/', 1)[-1] == name:
            pairs.append((str(path), android_user(context.get_relative_path(path))))
    return pairs
