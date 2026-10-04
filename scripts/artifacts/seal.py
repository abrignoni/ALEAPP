__artifacts_v2__ = {
    "seal_downloads": {
        "name": "Seal - Downloaded Media",
        "description": "Parses the media download history from the Seal Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "Seal",
        "sample_data": {
            "emu_a15_oss_v6": "Seal 1.13.1 | 1 rows",
        },
        "notes": "One row per entry in the DownloadedVideoInfo table of databases/app_database. "
                 "Seal is an open source front end for yt-dlp that downloads audio and video from "
                 "a URL a person supplies. In Seal 1.13.1 a row is written for each output file "
                 "after a download succeeds, and no row is written when the app's private mode is "
                 "on (DownloadUtil.kt, insertInfoIntoDownloadHistory, insertSplitChapterIntoHistory "
                 "and the privateMode branches, at tag v1.13.1). Each row holds the Title and "
                 "Author as the source site reported them, the Source URL the app stored (in Seal "
                 "1.13.1 this is the page URL yt-dlp reported, or the requested URL when yt-dlp "
                 "reported none; DownloadUtil.kt L500 at tag v1.13.1), the Thumbnail URL, the "
                 "absolute Saved Path the file was written to, and the Extractor, which is the "
                 "extractor key yt-dlp reported for the download (the tested download read "
                 "ArchiveOrg). The table carries no timestamp column, so this artifact reports "
                 "none: the only time signal for a download is the modification time of the file "
                 "named in Saved Path, and Seal 1.13.1 passes --no-mtime to yt-dlp for an ordinary "
                 "download (DownloadUtil.kt L538 at tag v1.13.1), which tells yt-dlp not to set "
                 "that file's time from the source media. An examiner wanting the download time "
                 "should read it from that file rather than from this table. The file itself is not "
                 "copied into the report: Seal writes to shared storage (the tested download landed "
                 "under Download/Seal), and a video download can run to gigabytes. Saved Path is "
                 "reported so the file can be located. Reference: Seal, DownloadUtil.kt at tag "
                 "v1.13.1, "
                 "https://github.com/JunkFood02/Seal/blob/v1.13.1/app/src/main/java/com/junkfood/seal/util/DownloadUtil.kt",
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
        "sample_data": {
            "emu_a15_oss_v6": "Seal 1.13.1 | 1 rows",
        },
        "notes": "Rows from the CookieProfile and CommandTemplate tables of "
                 "databases/app_database, combined because both are the app's configuration and "
                 "both key on a small identifier. Kind names which table a row came from. A "
                 "CookieProfile row holds a url and a content value. The table was present and "
                 "empty on the tested device, so what a populated row holds is not established from "
                 "data and the columns are described from the schema. The Content column is "
                 "reported as stored and, given the table's name, should be handled as credential "
                 "material. A CommandTemplate row is a yt-dlp argument string; the tested device "
                 "held one, named 'Command template' with the value '--no-mtime -S \"ext\"', which is "
                 "the sample template Seal 1.13.1 inserts by itself (PreferenceUtil.kt, "
                 "TEMPLATE_EXAMPLE at L161 and initializeTemplateSample at L311-321, at tag "
                 "v1.13.1, "
                 "https://github.com/JunkFood02/Seal/blob/v1.13.1/app/src/main/java/com/junkfood/seal/util/PreferenceUtil.kt) "
                 "rather than something a person wrote, so the presence of a single row here is not "
                 "evidence of configuration. The OptionShortcut table is not read by this artifact. "
                 "It was present and empty on the tested device, and is "
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
