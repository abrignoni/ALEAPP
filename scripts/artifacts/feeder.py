__artifacts_v2__ = {
    "feeder_feeds": {
        "name": "Feeder - Subscribed Feeds",
        "description": "Parses subscribed RSS and Atom feeds from the Feeder Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "Feeder",
        "sample_data": {
            "emu_a15_oss_v5": "Feeder 2.22.0 | 1 rows",
        },
        "notes": "One row per entry in the feeds table of databases/rssDatabase. Feeder is an open "
                 "source RSS and Atom reader. Each row is a feed subscribed to in the app, with "
                 "its Title, the Custom Title where one was set in the app, the Feed URL, and the "
                 "Tag, which is the user-named group a feed is filed under and is empty when none "
                 "was set. Last Sync, When Modified and Site Fetched are Unix milliseconds and are "
                 "reported as UTC; they are stored as java.time.Instant values (Feed.kt at "
                 "spacecowboy/Feeder tag 2.22.0, 6764cf5f27581a2337cdc9099e8b7220e342f177). Notify "
                 "is the per-feed notification setting. The feed a person subscribes to is a "
                 "choice they made in the app, unlike the articles it then downloads, which are "
                 "in the Articles artifact. Feeder ships with its own release-notes feed already "
                 "subscribed, so its presence alone is not evidence of a subscription a person "
                 "chose; the Feed URL distinguishes it.",
        "paths": ('*/com.nononsenseapps.feeder/databases/rssDatabase*',),
        "output_types": "standard",
        "artifact_icon": "rss",
    },
    "feeder_articles": {
        "name": "Feeder - Articles",
        "description": "Parses downloaded feed articles and their read state from the Feeder Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-01",
        "last_update_date": "2026-09-01",
        "requirements": "none",
        "category": "Feeder",
        "sample_data": {
            "emu_a15_oss_v5": "Feeder 2.22.0 | 16 rows",
        },
        "notes": "One row per entry in the feed_items table of databases/rssDatabase, joined to "
                 "the feed it belongs to. Most rows are articles the app downloaded when it synced "
                 "a feed, so a row's existence records the fetch and not that anyone opened it; "
                 "the user-activity signal is in Read Time and Bookmarked. Read Time is when the "
                 "article was opened and is the app's own definition of read state: FeedItem.kt "
                 "computes unread as readTime being null (spacecowboy/Feeder tag 2.22.0, "
                 "6764cf5f27581a2337cdc9099e8b7220e342f177). The table also carries a stored "
                 "unread column, reported here as Unread Flag, and the two can disagree: on the "
                 "tested device an article opened in the app was given a Read Time while its "
                 "stored flag still read unread, so Read Time is the column to rely on. Bookmarked "
                 "is the saved-for-later flag. The pinned column is deprecated in the app and is "
                 "not reported. Published is the article's own publication date as the feed "
                 "supplied it, an ISO 8601 string reported as stored, and First Synced and Read "
                 "Time are Unix milliseconds reported as UTC. Word Count is the app's count for "
                 "the article body.",
        "paths": ('*/com.nononsenseapps.feeder/databases/rssDatabase*',),
        "output_types": "standard",
        "artifact_icon": "file-text",
    },
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/rssDatabase'


def _db_files(context):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(DB_SUFFIX)]


def _ms(value):
    if not value:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value) // 1000)
    except (TypeError, ValueError):
        return ''


def _yesno(value):
    if value in (1, '1'):
        return 'Yes'
    if value in (0, '0'):
        return 'No'
    return ''


@artifact_processor
def feeder_feeds(context):
    query = '''SELECT title, custom_title, url, tag, last_sync, when_modified,
                      site_fetched, notify, id
               FROM feeds ORDER BY id'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((_ms(r[4]), r[0] or '', r[1] or '', r[2] or '', r[3] or '',
                              _ms(r[5]), _ms(r[6]), _yesno(r[7]), r[8],
                              context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (('Last Sync', 'datetime'), 'Title', 'Custom Title', 'Feed URL', 'Tag',
                    ('When Modified', 'datetime'), ('Site Fetched', 'datetime'), 'Notify',
                    'Feed ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def feeder_articles(context):
    query = '''SELECT i.read_time, i.plain_title, i.author, i.pub_date, i.link,
                      i.unread, i.bookmarked, i.first_synced_time, i.word_count,
                      f.title, f.url, i.plain_snippet, i.id
               FROM feed_items i
               LEFT JOIN feeds f ON f.id = i.feed_id
               ORDER BY i.first_synced_time DESC'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((_ms(r[0]), r[1] or '', r[9] or '', r[2] or '', r[3] or '',
                              _yesno(r[6]), _yesno(r[5]), _ms(r[7]), r[8], r[4] or '',
                              r[10] or '', r[11] or '', r[12],
                              context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (('Read Time', 'datetime'), 'Title', 'Feed', 'Author', 'Published',
                    'Bookmarked', 'Unread Flag', ('First Synced', 'datetime'), 'Word Count',
                    'Article URL', 'Feed URL', 'Snippet', 'Article ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
