import datetime
import filecmp
import hashlib
import os
import shutil
import sqlite3
import tempfile

from scripts.artifacts.chrome import get_browser_name
from scripts.ilapfuncs import artifact_processor, check_in_embedded_media, logfunc, \
    open_sqlite_db_readonly

# favicons.icon_type holds 1 << (IconType - 1) (see notes), so these are the IconType
# names of the persisted values.
_ICON_TYPES = {1: 'kFavicon', 2: 'kTouchIcon', 4: 'kTouchPrecomposedIcon', 8: 'kWebManifestIcon'}
_PAGE_URL_TYPES = {0: 'kRegular', 1: 'kRedirect'}
_SQLITE_READONLY_ROLLBACK = 776

_CC = 'https://github.com/chromium/chromium/blob/33f34ef179f55596f6c2fc8a55878b7ccf6276e4'

__artifacts_v2__ = {
    "chromiumFavicons": {
        "name": "Chromium Favicons",
        "description": "Page URLs that a Chromium-based browser's Favicons database maps to an "
                       "icon, with the icon's URL, type, stored sizes, times and image, and "
                       "whether the urls table of the History database in the same folder holds "
                       "the page URL. Reads the Favicons databases found under the app_chrome, "
                       "app_sbrowser, app_opera and app_webview layouts; the browser is named from "
                       "the package.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-11-13",
        "last_update_date": "2026-11-21",
        "requirements": "none",
        "category": "Browsers",
        "notes": "One row per icon_mapping row, which Chromium's source describes as a page URL "
                 "and the id of an icon mapped to it, joined to that icon's favicons row (its URL "
                 f"and type) and to its favicon_bitmaps rows ({_CC}/components/favicon/core/"
                 "favicon_database.cc#L41-L90). Browser comes from the package folder in the path "
                 "through get_browser_name in chrome.py: a package containing brave, microsoft, "
                 "opera or android.chrome is shown as Brave, Edge, Opera or Chrome, app_sbrowser "
                 "as Browser (Samsung Internet), and any other package as stored. Page URL is "
                 "page_url and Icon URL is the icon's url, as stored. Icon Type is icon_type named "
                 "through Chromium's IconType: the database stores 1 shifted left by the IconType "
                 f"value less one ({_CC}/components/favicon/core/favicon_database.cc#L993-L998), so "
                 f"1, 2, 4 and 8 are kFavicon, kTouchIcon, kTouchPrecomposedIcon and "
                 f"kWebManifestIcon ({_CC}/components/favicon_base/favicon_types.h#L36-L42); any "
                 "other value is shown as stored. Values 1, 2 and 4 were present on the tested "
                 "images; 8 and the fallback were not exercised, and the enum is Chromium's, not "
                 "checked against each fork's build. Sizes lists the distinct width x height "
                 "values of the icon's bitmaps and Icon shows the bitmap with the largest area; "
                 "every icon on the tested images had one bitmap, so the choice among several was "
                 "not exercised. Last Updated and Last Requested are the latest last_updated and "
                 "last_requested of the bitmaps, read as microseconds since 1601-01-01 UTC "
                 f"({_CC}/components/favicon/core/favicon_database.cc#L446, {_CC}/components/"
                 f"favicon/core/favicon_database.cc#L451 and {_CC}/sql/statement.cc#L42-L44), with "
                 "a zero value shown blank; with one bitmap per icon on the tested images, the "
                 "latest was not exercised. Chromium's source describes last_updated as the time "
                 "the favicon was inserted, used to decide when to download it again, adding that "
                 "a zero marks a bitmap that was explicitly expired and is always zero for one "
                 "fetched on demand, so a blank Last Updated is one of those two; last_requested "
                 "is the time the bitmap was last requested, non-zero only for a bitmap fetched on "
                 f"demand ({_CC}/components/favicon/core/favicon_database.cc#L76-L90). In History "
                 "is a string comparison of Page URL against the urls table of the History "
                 "database in the same folder: Yes when it holds the URL, No when it does not, and "
                 "blank when no readable History sits beside the Favicons database (the blank case "
                 "did not occur on the tested images). The visits table is not read, so Yes does "
                 "not establish a visit (on the tested images 4 Yes rows had no row in visits), "
                 "and No does not establish that the page was not visited; Chromium's source notes "
                 "that a bitmap fetched on demand has no corresponding visit, and why other mapped "
                 "URLs are absent from History was not established. Page URL Type is page_url_type "
                 f"named through PageUrlType, 0 kRegular and 1 kRedirect ({_CC}/components/favicon/"
                 "core/favicon_types.h#L26-L35). Chromium adds this column when it upgrades the "
                 f"database to version 9 ({_CC}/components/favicon/core/favicon_database.cc#L1098-"
                 f"L1103, {_CC}/components/favicon/core/favicon_database.cc#L1137-L1140); the "
                 "artifact checks for the column, not the version, and a column the table lacks is "
                 "read as blank. On the tested images the Chrome, Brave and Edge databases at "
                 "version 9 carried it and it was set on every row (hc_pixel8pro_a16, "
                 "hc_pixel8pro_a17, anne_a15, kevin_pocox7_a15, samsunga53_a14, dragna_pixel9a_a16); the version 8 "
                 "Chrome, Brave, Edge and Opera databases (hickman_a13, pixel7a_a14, russell_a14, "
                 "and the Chrome databases on sharon_a14 and cookbook_a11) lacked it and every row "
                 "is blank. Samsung Internet numbers its database differently: version 10 carried "
                 "the column (hc_pixel8pro_a16, hc_pixel8pro_a17) and version 9 did not (anne_a15, "
                 "sharon_a14, cookbook_a11), so Samsung Internet rows are blank there. The forks "
                 "exercised on the tested images were Chrome, Samsung Internet (Browser), Brave "
                 "and Edge; Opera matched a version 8 database with no mappings (hickman_a13, "
                 "pixel7a_a14), and no file matched under app_webview or under a profile folder "
                 "inside app_opera. An extraction can hold the same file under several roots "
                 "(/data/data, /data/user/0 and the /data_mirror copy); Favicons files with the "
                 "same SHA1 are read once, which took samsunga53_a14 from 162 rows to 54 and "
                 "hickman_a13 from 286 to 143. A file under another user (/data/user/<n>) adds its "
                 "own rows when its bytes differ, as on russell_a14 and cookbook_a11; the "
                 "comparison covers the Favicons file only, not its journal. A Favicons or History "
                 "database with a pending rollback journal is read from a temporary copy, where "
                 "SQLite rolls the journal back, so its rows show the database with the journal's pages restored. That is the state before the unfinished write when the journal belongs to the file's last write, and the integrity check does not establish that. The rolled-back copy is used only if it passes SQLite's integrity check. Otherwise the file as found is used if it passes, with the journal ignored and the run log saying so. A file read this way can hold part of an unfinished write, and its rows are not marked in the report. The database is not read if neither passes, and the run log says so. Those two branches were exercised on constructed test databases, not on a corpus image. The artifact does not write to the evidence files, and the run log names each database read this way. The rollback read was exercised on Favicons databases on dragna_pixel9a_a16 "
                 "(Chrome, 32 rows) and russell_a14 (Brave, a second user, 14 rows); a History "
                 "database with a pending journal was not exercised. "
                 "Source File is the extraction path of the Favicons file the rows came from and is the column that "
                 "separates users. Values not reported include the favicon_bitmaps rows of icons "
                 "that no page URL maps to (none on the tested images).",
        "paths": (
            '*/app_chrome/*/Favicons*',
            '*/app_sbrowser/*/Favicons*',
            '*/app_opera/Favicons*',
            '*/app_opera/*/Favicons*',
            '*/app_webview/*/Favicons*',
            '*/app_chrome/*/History*',
            '*/app_sbrowser/*/History*',
            '*/app_opera/History*',
            '*/app_opera/*/History*',
            '*/app_webview/*/History*',
        ),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
            "hickman_a13": "Android 13 | 143 rows (Chrome, Brave, Edge)",
            "sharon_a14": "Android 14 | 182 rows (Chrome, Samsung Internet)",
            "pixel7a_a14": "Android 14 | 78 rows (Chrome, Brave, Edge)",
            "dragna_pixel9a_a16": "Android 16 | 32 rows (Chrome, read after journal rollback)",
            "russell_a14": "Android 14 | 63 rows (Chrome, two users; Brave read after journal "
                           "rollback)",
            "cookbook_a11": "Android 11 | 134 rows (Chrome, Samsung Internet across two users)",
            "anne_a15": "Android 15 | 111 rows (Chrome, Samsung Internet)",
            "kevin_pocox7_a15": "Android 15 | 60 rows (Chrome)",
            "samsunga53_a14": "Android 14 | 54 rows (Chrome)",
            "hc_pixel8pro_a16": "Android 16 | 43 rows (Chrome, Brave, Samsung Internet)",
            "hc_pixel8pro_a17": "Android 17 | 38 rows (Chrome, Brave, Samsung Internet)",
        },
    }
}


def _webkit_to_utc(value):
    '''Chromium/WebKit timestamp = microseconds since 1601-01-01 UTC'''
    if value in (None, 0, ''):
        return ''
    return datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc) + \
        datetime.timedelta(microseconds=int(value))


def _enum_label(mapping, value):
    '''"name (value)" when the integer is known, else the value as stored.'''
    if value in (None, ''):
        return ''
    name = mapping.get(value)
    return f'{name} ({value})' if name else str(value)


def _columns(db, table):
    '''The column names of a table, or an empty set when the table does not exist.

    A read error (for example a database held open by a pending rollback journal)
    is left to raise, so the caller can tell "no such table" from "could not read".
    '''
    return {row[1] for row in db.execute(f'PRAGMA table_info({table})')}


def _dedupe_identical(paths):
    '''One path per distinct file content.

    Android stages the same user's data under several roots (/data/data,
    /data/user/0 and /data_mirror/data_ce/null/0), byte-identical copies that would
    otherwise each add their own rows. A different user (/data/user/<n>) has different
    bytes and is kept. The first path of each content hash, sorted, is the representative.
    '''
    by_hash = {}
    for path in sorted(paths):
        try:
            with open(path, 'rb') as handle:
                digest = hashlib.sha1(handle.read()).hexdigest()
        except OSError as ex:
            logfunc(f'Chromium Favicons: could not hash {path}: {ex}')
            by_hash[path] = path
            continue
        by_hash.setdefault(digest, path)
    return list(by_hash.values())


def _needs_rollback(error, journal):
    '''True for SQLITE_READONLY_ROLLBACK with a non-empty journal beside the database.'''
    code = getattr(error, 'sqlite_errorcode', None)
    matches = code == _SQLITE_READONLY_ROLLBACK if code is not None else 'readonly' in str(error)
    return matches and os.path.isfile(journal) and os.path.getsize(journal) > 0


def _integrity_ok(db):
    '''True when SQLite's integrity check passes on an open database.'''
    try:
        row = db.execute('PRAGMA integrity_check(1)').fetchone()
    except sqlite3.DatabaseError:
        return False
    return bool(row) and row[0] == 'ok'


def _read_rolled_back(copy, path, reader):
    '''(True, reader(db)) when SQLite restored pages to the copy and the result is sound.

    SQLite can delete a journal it decides not to play back, so a rollback is established by
    the copy's bytes differing from the evidence file after the read.
    '''
    db = sqlite3.connect(copy)
    try:
        if not _integrity_ok(db):
            return False, None
        result = reader(db)
    except sqlite3.DatabaseError:
        return False, None
    finally:
        db.close()
    return not filecmp.cmp(copy, path, shallow=False), result


def _read_database(path, reader, label):
    '''(reader(db), the journal path if one was rolled back) for the database at path.

    SQLite must roll a hot journal back before it can read, which a read-only open
    cannot do. In that case the database and its journal are copied to a temporary
    folder and read there, so SQLite rolls back the copy and the evidence is not changed.
    A stale journal can damage a sound database, so the rolled-back copy is used only if
    it passes SQLite's integrity check. Otherwise the file as found is used if it passes,
    and the read is refused if neither does.
    '''
    db = open_sqlite_db_readonly(path)
    if db is None:
        return None, None
    journal = f'{path}-journal'
    try:
        return reader(db), None
    except sqlite3.OperationalError as ex:
        if not _needs_rollback(ex, journal):
            raise
    finally:
        db.close()
    with tempfile.TemporaryDirectory() as folder:
        copy = os.path.join(folder, 'database')
        shutil.copyfile(path, copy)
        shutil.copyfile(journal, f'{copy}-journal')
        rolled_back, result = _read_rolled_back(copy, path, reader)
        if rolled_back:
            logfunc(f'Chromium Favicons: {label} had a pending rollback journal; read from a '
                    'temporary copy after SQLite rolled it back')
            return result, journal
        as_found = os.path.join(folder, 'as_found')
        shutil.copyfile(path, as_found)
        db = sqlite3.connect(as_found)
        try:
            if not _integrity_ok(db):
                raise sqlite3.DatabaseError('neither the rolled-back copy nor the file as found '
                                            'passed the integrity check')
            result = reader(db)
        finally:
            db.close()
    logfunc(f'Chromium Favicons: {label} had a pending rollback journal that did not give a sound '
            'database; read as found, with the journal ignored')
    return result, None


def _read_urls(db):
    if 'urls' not in {row[0] for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}:
        return None
    return {row[0] for row in db.execute('SELECT url FROM urls')}


def _history_urls(history_file, label):
    '''(url set or None when it cannot be read, the journal path if one was rolled back).'''
    try:
        return _read_database(history_file, _read_urls, label)
    except (sqlite3.Error, OSError) as ex:
        logfunc(f'Chromium Favicons: could not read {history_file}: {ex}')
        return None, None


def _bitmaps(db):
    '''{icon_id: (latest last_updated, latest last_requested, [sizes], largest image)}.

    A column the table lacks reads as NULL: an older database has no last_requested.
    '''
    present = _columns(db, 'favicon_bitmaps')
    requested = 'last_requested' if 'last_requested' in present else 'NULL'
    icons = {}
    for icon_id, updated, req, width, height, image in db.execute(
            f'SELECT icon_id, last_updated, {requested}, width, height, image_data '
            'FROM favicon_bitmaps ORDER BY icon_id, width, height, id'):
        latest_updated, latest_requested, sizes, largest = icons.get(icon_id, (0, 0, [], None))
        size = f'{width}x{height}'
        if size not in sizes:
            sizes.append(size)
        area = (width or 0) * (height or 0)
        if image and (largest is None or area >= largest[0]):
            largest = (area, image)
        icons[icon_id] = (max(latest_updated, updated or 0),
                          max(latest_requested, req or 0), sizes, largest)
    return icons


def _read_favicons(db):
    '''(mapping rows, icons), or None when a required table is missing.'''
    mapping = _columns(db, 'icon_mapping')
    if not mapping or not _columns(db, 'favicons') or not _columns(db, 'favicon_bitmaps'):
        return None
    url_type = 'm.page_url_type' if 'page_url_type' in mapping else 'NULL'
    rows = db.execute(
        f'SELECT m.page_url, m.icon_id, f.url, f.icon_type, {url_type} '
        'FROM icon_mapping m LEFT JOIN favicons f ON f.id = m.icon_id '
        'ORDER BY m.id').fetchall()
    return rows, _bitmaps(db)


@artifact_processor
def chromiumFavicons(context):
    data_headers = (('Last Updated', 'datetime'), ('Last Requested', 'datetime'), 'Page URL',
                    'In History', 'Icon URL', 'Icon Type', 'Sizes', ('Icon', 'media'),
                    'Page URL Type', 'Browser', 'Source File')
    files = [str(f) for f in context.get_files_found()]
    favicons = _dedupe_identical([f for f in files if os.path.basename(f) == 'Favicons'])
    histories = {os.path.dirname(f): f for f in files if os.path.basename(f) == 'History'}

    data_list = []
    sources = []
    for file_found in favicons:
        try:
            result, journal = _read_database(file_found, _read_favicons,
                                             context.get_relative_path(file_found))
        except (sqlite3.Error, OSError) as ex:
            logfunc(f'Chromium Favicons: could not read {file_found}: {ex}')
            continue
        if result is None:
            logfunc(f'Chromium Favicons: {file_found} could not be opened or has no icon_mapping, '
                    'favicons or favicon_bitmaps table')
            continue
        rows, icons = result

        sources.append(file_found)
        if journal:
            sources.append(journal)
        browser = get_browser_name(file_found)
        if 'app_sbrowser' in file_found:
            browser = 'Browser'
        history_file = histories.get(os.path.dirname(file_found))
        urls, history_journal = (_history_urls(history_file, context.get_relative_path(history_file))
                                 if history_file else (None, None))
        if history_file and urls is not None:
            sources.append(history_file)
            if history_journal:
                sources.append(history_journal)
        relative = context.get_relative_path(file_found)
        for page_url, icon_id, icon_url, icon_type, page_url_type in rows:
            updated, requested, sizes, largest = icons.get(icon_id, (0, 0, [], None))
            media = check_in_embedded_media(file_found, largest[1]) if largest else ''
            in_history = '' if urls is None else ('Yes' if page_url in urls else 'No')
            data_list.append((_webkit_to_utc(updated), _webkit_to_utc(requested), page_url,
                              in_history, icon_url or '', _enum_label(_ICON_TYPES, icon_type),
                              ', '.join(sizes), media or '',
                              _enum_label(_PAGE_URL_TYPES, page_url_type), browser, relative))

    return data_headers, data_list, '\n'.join(sources)
