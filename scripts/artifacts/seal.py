__artifacts_v2__ = {
    "seal_downloads": {
        "name": "Seal - Downloaded Media",
        "description": "Parses the media download history from the Seal Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "Seal",
        "notes": "One row per entry in the DownloadedVideoInfo table of databases/app_database. "
                 "Seal is an open source front end for yt-dlp that downloads audio and video from "
                 "a URL a person supplies. Each row records one completed download: the Title and "
                 "Author as the source site reported them, the Source URL that was supplied, the "
                 "Thumbnail URL, the absolute Saved Path the file was written to, and the "
                 "Extractor, which is the yt-dlp handler that served it and therefore names the "
                 "service the media came from (the tested download read ArchiveOrg). Supplying a "
                 "URL and starting a download are both deliberate actions, so a row is stronger "
                 "evidence of intent than a cache entry is. "
                 "The table carries no timestamp column, so this artifact reports none: the only "
                 "time signal for a download is the modification time of the file named in Saved "
                 "Path, and the app's default command template on the tested device was "
                 "'--no-mtime -S \"ext\"', which tells yt-dlp not to set that file's time from the "
                 "source media, leaving it as the time the file was written. An examiner wanting "
                 "the download time should read it from that file rather than from this table. "
                 "The file itself is not copied into the report: Seal writes to shared storage "
                 "(the tested download landed under Download/Seal) where the media is already "
                 "within reach of the report's own media handling, and a video download can run "
                 "to gigabytes. Saved Path is reported so the file can be located.",
        "paths": ('*/com.junkfood.seal/databases/app_database*',),
        "output_types": "standard",
        "artifact_icon": "download",
    },
    "seal_config": {
        "name": "Seal - Cookies and Templates",
        "description": "Parses saved cookie profiles and command templates from the Seal Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "Seal",
        "notes": "Rows from the CookieProfile and CommandTemplate tables of "
                 "databases/app_database, combined because both are the app's configuration and "
                 "both key on a small identifier. Kind names which table a row came from. A "
                 "CookieProfile row is a set of cookies a person imported into Seal so it can "
                 "download from a site that requires being signed in, so its presence records "
                 "both the site and that the person had a session for it; the Content column "
                 "holds the cookie text itself and is reported because it is the substance of the "
                 "entry, and it should be treated as credential material. CookieProfile was "
                 "present and empty on the tested device, so that column is described from the "
                 "schema and not from decoded rows. A CommandTemplate row is a yt-dlp argument "
                 "string; the tested device held one, named 'Command template' with the value "
                 "'--no-mtime -S \"ext\"', which is the app's shipped default rather than "
                 "something a person wrote, so the presence of a single row here is not evidence "
                 "of configuration. The OptionShortcut table holds single yt-dlp options a person "
                 "pinned in the interface, was present and empty on the tested device, and is "
                 "named here rather than given its own artifact.",
        "paths": ('*/com.junkfood.seal/databases/app_database*',),
        "output_types": "standard",
        "artifact_icon": "settings",
    },
}

from scripts.ilapfuncs import artifact_processor, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/app_database'


def _db_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(DB_SUFFIX)]


@artifact_processor
def seal_downloads(context):
    query = '''SELECT videoTitle, videoAuthor, videoUrl, videoPath, extractor,
                      thumbnailUrl, id
               FROM DownloadedVideoInfo ORDER BY id DESC'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((r[0] or '', r[1] or '', r[2] or '', r[4] or '',
                              r[3] or '', r[5] or '', r[6],
                              context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = ('Title', 'Author', 'Source URL', 'Extractor', 'Saved Path',
                    'Thumbnail URL', 'Record ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def seal_config(context):
    cookie_query = 'SELECT id, url, content FROM CookieProfile'
    template_query = 'SELECT id, name, template FROM CommandTemplate'
    data_list = []
    sources = []
    for db_path in _db_files(context):
        seen = False
        for r in get_sqlite_db_records(db_path, cookie_query):
            seen = True
            data_list.append(('Cookie profile', r[1] or '', r[2] or '', r[0],
                              context.get_relative_path(db_path)))
        for r in get_sqlite_db_records(db_path, template_query):
            seen = True
            data_list.append(('Command template', r[1] or '', r[2] or '', r[0],
                              context.get_relative_path(db_path)))
        if seen and db_path not in sources:
            sources.append(db_path)

    data_headers = ('Kind', 'Name or URL', 'Content', 'Record ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
