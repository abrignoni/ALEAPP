__artifacts_v2__ = {
    "get_walRecords": {
        "name": "SQLite Records Superseded in a WAL or Journal",
        "description": "Rebuilds each committed state a SQLite write ahead log or rollback "
                       "journal records, and reports the rows present in one of those states "
                       "that the current state of the database no longer holds.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-28",
        "last_update_date": "2026-08-28",
        "requirements": "none",
        "category": "SQLite Journaling",
        "notes": "A write ahead log stores complete page images, each carrying the page number "
                 "and the database size at the commit it belongs to, so the state after any "
                 "commit can be rebuilt by writing those pages onto a copy of the database and "
                 "letting SQLite read the result. Nothing here searches for record shaped bytes: "
                 "every page is located by a header field and every value is decoded by SQLite "
                 "from the schema the database itself carries. "
                 "A row is reported when it appears in a rebuilt state and is absent from the "
                 "current state. That says the row was present at an earlier commit and is not "
                 "present now. It does not establish who removed it or why: an application that "
                 "trims a rolling table produces the same result as a deletion. "
                 "Rows are compared by their values, so a schema change during the logged period "
                 "can make the same record read as two. Frames belonging to an earlier write "
                 "ahead log generation, which SQLite identifies by a salt that no longer matches "
                 "the file header, are counted in the log and not rebuilt, because they describe "
                 "a database state this file no longer carries. "
                 "The per database limits below are logged whenever one is reached, so a capped "
                 "run is never silently reported as a complete one. "
                 "On the four tested images most of what came back was application and framework "
                 "bookkeeping rather than user content: job scheduler queues, thermal counters, "
                 "carrier tables and configuration flags. The companion summary artifact exists "
                 "to make that visible per database. Rows carrying user activity were recovered "
                 "as well, a trimmed Digital Wellbeing usageEvents table among them, and no "
                 "message table was recovered on any of the four. "
                 "Journal Type reads WAL on every row of the tested images. A rollback journal that still holds its original pages is uncommon: four were found across the eighteen registered Android extractions, and none of them is in these four images, so the column is uniform here rather than unpopulated. ",
        "paths": ('*/*-wal', '*/*-journal'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "rotate-ccw",
        "sample_data": {
            "cookbook_a11": "Android 11 | 9712 rows",
            "samsunga53_a14": "Android 14 | 8354 rows",
            "pixel7a_a14": "Android 14 | 11931 rows",
            "sharon_a14": "Android 14 | 29375 rows",
        },
    },
    "get_walRecordsSummary": {
        "name": "SQLite Journals Holding Superseded Records",
        "description": "One row per database whose write ahead log or rollback journal still "
                       "holds rows the current state of that database does not, with the frame "
                       "counts the file itself records.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-28",
        "last_update_date": "2026-08-28",
        "requirements": "none",
        "category": "SQLite Journaling",
        "notes": "The companion detail artifact lists every recovered row. This one exists so "
                 "the databases worth opening can be picked out without reading that table "
                 "end to end: on a tested image it reported 9,712 rows, about a third of them "
                 "in job scheduler, thermal and configuration tables that are present on any "
                 "device. Nothing is filtered out of the detail artifact; this is a way into "
                 "it, not a substitute for it. "
                 "Frames and Frames From An Earlier Log are counted from the file's own frame "
                 "headers. The second group is not rebuilt, because those frames describe a "
                 "database state this file no longer carries. "
                 "Journal Type reads WAL on every row of the tested images. A rollback journal that still holds its original pages is uncommon: four were found across the eighteen registered Android extractions, and none of them is in these four images, so the column is uniform here rather than unpopulated. ",
        "paths": ('*/*-wal', '*/*-journal'),
        "output_types": ['html', 'tsv', 'lava'],
        "artifact_icon": "list",
        "sample_data": {
            "cookbook_a11": "Android 11 | 232 rows",
            "samsunga53_a14": "Android 14 | 241 rows",
            "pixel7a_a14": "Android 14 | 268 rows",
            "sharon_a14": "Android 14 | 438 rows",
        },
    }
}

import os
import sqlite3
import struct
import tempfile

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.artifacts.storagePathViews import unique_files

# https://sqlite.org/fileformat2.html
WAL_MAGIC = (0x377F0682, 0x377F0683)
JOURNAL_MAGIC = bytes.fromhex('d9d505f920a163d7')
SQLITE_MAGIC = b'SQLite format 3\x00'

# Reaching any of these logs a line naming the database, so a capped run is visible.
MAX_DB_BYTES = 256 * 1024 * 1024
MAX_SIDECAR_BYTES = 128 * 1024 * 1024
MAX_STATES = 400            # committed states rebuilt per database
MAX_ROWS_PER_TABLE = 20000  # a table larger than this in the current state is skipped
MAX_RECOVERED_PER_DB = 2000


def _page_size_from_db(header):
    """Page size recorded in the database header, or None if this is not a database."""
    if len(header) < 20 or header[:16] != SQLITE_MAGIC:
        return None
    size = struct.unpack('>H', header[16:18])[0]
    size = 65536 if size == 1 else size
    return size if size >= 512 and not size & (size - 1) else None


def _wal_frames(blob, fallback_page_size):
    """(page_size, [(page number, db size after commit, belongs to this generation, image)]).

    A write ahead log whose header has been zeroed still holds its frames, so the page size
    is taken from the database when the header cannot supply it.
    """
    live_header = False
    page_size = fallback_page_size
    salt = None
    if len(blob) >= 32:
        magic, _fmt, declared, _seq, salt1, salt2 = struct.unpack('>6I', blob[:24])
        if magic in WAL_MAGIC:
            declared = 65536 if declared == 1 else declared
            if declared >= 512 and not declared & (declared - 1):
                page_size, salt, live_header = declared, (salt1, salt2), True
    if not page_size:
        return None, []
    frame_size = 24 + page_size
    frames = []
    offset = 32
    while offset + frame_size <= len(blob):
        pgno, db_pages, salt1, salt2 = struct.unpack('>4I', blob[offset:offset + 16])
        image = blob[offset + 24:offset + frame_size]
        current = (salt is None) or ((salt1, salt2) == salt)
        if pgno:
            frames.append((pgno, db_pages, current, image))
        offset += frame_size
    return page_size, (frames if live_header or frames else [])


def _journal_pages(blob, page_size):
    """[(page number, original image)] from a rollback journal, or [] if it holds none."""
    if len(blob) < 28 or blob[:8] != JOURNAL_MAGIC or not page_size:
        return []
    _records, _nonce, _initial, sector, declared = struct.unpack('>5I', blob[8:28])
    if declared and declared >= 512 and not declared & (declared - 1):
        page_size = declared
    offset = sector if 512 <= sector <= 65536 else 512
    pages = []
    while offset + 8 + page_size <= len(blob):
        pgno = struct.unpack('>I', blob[offset:offset + 4])[0]
        if not pgno:
            break
        pages.append((pgno, blob[offset + 4:offset + 4 + page_size]))
        offset += 4 + page_size + 4
    return pages


def _read_tables(path):
    """{table: {row repr}} for a rebuilt database, or {} if SQLite will not read it."""
    tables = {}
    try:
        db = sqlite3.connect(f'file:{path}?mode=ro&immutable=1', uri=True)
    except sqlite3.Error:
        return tables
    try:
        names = [row[0] for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    except sqlite3.Error:
        db.close()
        return tables
    for name in names:
        try:
            cursor = db.execute(f'SELECT * FROM "{name}"')
            columns = [d[0] for d in cursor.description]
            rows = cursor.fetchmany(MAX_ROWS_PER_TABLE + 1)
            if len(rows) > MAX_ROWS_PER_TABLE:
                continue
            tables[name] = (columns, set(rows))
        except sqlite3.Error:
            continue
    db.close()
    return tables


def _render(columns, values):
    """The stored values of one row, labelled with the column names SQLite reported.

    A blob is summarised by its length rather than printed, so a row carrying an image or a
    protobuf stays readable in the report.
    """
    parts = []
    for name, value in zip(columns, values):
        if isinstance(value, bytes):
            value = f'<{len(value)} bytes>'
        parts.append(f'{name}={value}')
    return '; '.join(parts)


def _recover(db_bytes, page_size, frames, label, note):
    """Rows seen in a rebuilt state and absent from the current one.

    The database is rebuilt once with every frame applied to establish the current state,
    then again one commit at a time. Only rows missing from the current state are kept, so
    memory holds the recovered set rather than every state.
    """
    out = []
    work = tempfile.mkdtemp(prefix='aleapp-walrec-')
    path = os.path.join(work, 'rebuilt.db')
    try:
        def apply_to(selected, truncate_to):
            with open(path, 'wb') as handle:
                handle.write(db_bytes)
            with open(path, 'r+b') as handle:
                for pgno, image in selected:
                    handle.seek((pgno - 1) * page_size)
                    handle.write(image)
                if truncate_to:
                    handle.truncate(truncate_to * page_size)

        current_pages = [(f[0], f[3]) for f in frames if f[2]]
        final_size = next((f[1] for f in reversed(frames) if f[2] and f[1]), 0)
        apply_to(current_pages, final_size)
        current = _read_tables(path)
        if not current:
            return out

        commits = [i for i, f in enumerate(frames) if f[2] and f[1]]
        if len(commits) > MAX_STATES:
            logfunc(f'{label}: rebuilding the first {MAX_STATES} of {len(commits)} committed '
                    f'states; the remainder were not examined')
            commits = commits[:MAX_STATES]

        seen = {}
        for index in commits:
            apply_to([(f[0], f[3]) for f in frames[:index + 1] if f[2]], frames[index][1])
            for name, (columns, rows) in _read_tables(path).items():
                known = current.get(name, (columns, set()))[1]
                for row in rows - known:
                    if row not in seen:
                        seen[row] = (name, columns, index)
                        if len(seen) >= MAX_RECOVERED_PER_DB:
                            break
            if len(seen) >= MAX_RECOVERED_PER_DB:
                logfunc(f'{label}: stopped after {MAX_RECOVERED_PER_DB} recovered rows; '
                        f'{len(commits) - commits.index(index) - 1} committed states were '
                        f'not examined')
                break
        for row, (name, columns, index) in seen.items():
            out.append((name, index, _render(columns, row), note))
    finally:
        for entry in os.listdir(work):
            try:
                os.unlink(os.path.join(work, entry))
            except OSError:
                pass
        try:
            os.rmdir(work)
        except OSError:
            pass
    return out


def _main_database(sidecar, seeker, context):
    """The database a sidecar belongs to, staged if some other artifact has not staged it."""
    stem = sidecar[:-4] if sidecar.endswith('-wal') else sidecar[:-8]
    if os.path.isfile(stem):
        return stem
    relative = context.get_relative_path(stem).replace('\\', '/')
    escaped = relative.replace('[', '[[]')
    for candidate in seeker.search(f'*{escaped}'):
        if os.path.isfile(str(candidate)) and str(candidate).endswith(os.path.basename(stem)):
            return str(candidate)
    return None


_ANALYSIS = {}


def _analyse(context):
    """Both artifacts report on the same pass, so it is done once and reused."""
    if _ANALYSIS:
        return _ANALYSIS['records'], _ANALYSIS['summary'], _ANALYSIS['sources']
    seeker = context.get_seeker()
    data_list = []
    summary = []
    source_paths = set()
    unpaired = 0

    for sidecar in unique_files(context):
        sidecar = str(sidecar)
        if not os.path.isfile(sidecar) or os.path.getsize(sidecar) == 0:
            continue
        label = context.get_relative_path(sidecar)
        if os.path.getsize(sidecar) > MAX_SIDECAR_BYTES:
            logfunc(f'{label}: larger than the {MAX_SIDECAR_BYTES} byte limit, not examined')
            continue

        database = _main_database(sidecar, seeker, context)
        if not database:
            unpaired += 1
            continue
        if os.path.getsize(database) > MAX_DB_BYTES:
            logfunc(f'{label}: its database is larger than the {MAX_DB_BYTES} byte limit, '
                    f'not examined')
            continue

        try:
            with open(database, 'rb') as handle:
                db_bytes = handle.read()
            with open(sidecar, 'rb') as handle:
                blob = handle.read()
        except OSError as ex:
            logfunc(f'{label}: could not be read: {ex}')
            continue

        page_size = _page_size_from_db(db_bytes[:32])
        if not page_size:
            continue

        if sidecar.endswith('-wal'):
            found_size, frames = _wal_frames(blob, page_size)
            page_size = found_size or page_size
            note = 'WAL'
        else:
            frames = [(pgno, 0, True, image) for pgno, image in _journal_pages(blob, page_size)]
            if frames:
                # A rollback journal holds the pages as they were before the transaction, so
                # the whole set is one earlier state rather than a sequence of commits.
                frames[-1] = (frames[-1][0], len(db_bytes) // page_size, True, frames[-1][3])
            note = 'Rollback Journal'
        if not frames:
            continue

        stale = sum(1 for f in frames if not f[2])
        if stale:
            logfunc(f'{label}: {stale} frame(s) belong to an earlier write ahead log '
                    f'generation and were not rebuilt')

        try:
            recovered = _recover(db_bytes, page_size, frames, label, note)
        except (OSError, MemoryError, struct.error) as ex:
            logfunc(f'{label}: could not be rebuilt: {ex}')
            continue

        if recovered:
            database_label = context.get_relative_path(database)
            source_paths.add(database)
            source_paths.add(sidecar)
            for table, index, rendered, kind in recovered:
                data_list.append((database_label, kind, table, index, rendered))
            tables = sorted({r[0] for r in recovered})
            summary.append((database_label, note, len(frames), stale,
                            sum(1 for f in frames if f[2] and f[1]), len(recovered),
                            ', '.join(tables)))

    if unpaired:
        logfunc(f'{unpaired} write ahead log or journal file(s) had no database alongside them, '
                f'so no schema was available and they were not examined')

    _ANALYSIS['records'] = data_list
    _ANALYSIS['summary'] = summary
    _ANALYSIS['sources'] = '\n'.join(sorted(source_paths))
    return data_list, summary, _ANALYSIS['sources']


@artifact_processor
def get_walRecords(context):
    records, _summary, sources = _analyse(context)
    data_headers = ('Source Database', 'Journal Type', 'Table', 'Commit Index',
                    'Recovered Record')
    return data_headers, records, sources


@artifact_processor
def get_walRecordsSummary(context):
    _records, summary, sources = _analyse(context)
    data_headers = ('Source Database', 'Journal Type', 'Frames',
                    'Frames From An Earlier Log', 'Committed States Rebuilt',
                    'Records Recovered', 'Tables')
    return data_headers, summary, sources
