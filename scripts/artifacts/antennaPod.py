__artifacts_v2__ = {
    "antennapod_subscriptions": {
        "name": "AntennaPod - Subscriptions",
        "description": "Parses podcast subscriptions from the AntennaPod Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "AntennaPod",
        "notes": "One row per entry in the Feeds table of databases/Antennapod.db. AntennaPod is "
                 "an open source podcast manager. Each row is a podcast the person subscribed to, "
                 "with the Title, an optional Custom Title the user set, the Author, the Feed URL "
                 "(the RSS download_url), the Website link, Language, Type, the feed Description, "
                 "and Last Update. Last Update is the feed's own published timestamp string as "
                 "stored (an RFC-822 date such as 'Tue, 25 Aug 2026 21:54:28 GMT'), not converted. "
                 "On the tested device one feed was added by RSS address (the Changelog podcast). "
                 "The feed content itself (episode list) is in the Episodes artifact. Subscribing "
                 "to a feed causes the app to download the feed's episode catalogue, so the "
                 "presence of a feed reflects a subscription the user made.",
        "paths": ('*/de.danoeh.antennapod/databases/Antennapod.db*',),
        "output_types": "standard",
        "artifact_icon": "rss",
    },
    "antennapod_episodes": {
        "name": "AntennaPod - Episodes",
        "description": "Parses podcast episodes and playback state from the AntennaPod Android app.",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-31",
        "last_update_date": "2026-08-31",
        "requirements": "none",
        "category": "AntennaPod",
        "notes": "One row per entry in the FeedItems table of databases/Antennapod.db, joined to "
                 "its FeedMedia record and its Feed. Each row is an episode of a subscribed "
                 "podcast. Most rows are the episode catalogue the app downloaded when the feed "
                 "was subscribed (the tested feed produced 1013 episode rows), so the row's "
                 "existence reflects the fetched feed rather than user activity; the user-activity "
                 "signal is in the state columns. Play State is decoded from the FeedItems.read "
                 "value, -1 New, 0 Unplayed, 1 Played (FeedItem.java at AntennaPod/AntennaPod tag "
                 "3.12.0, 980b2f32d9ded0bb65ca9e9d84a44790c2d0eab5); any other value is reported "
                 "as stored. In Queue is Yes when the episode is in the play Queue table, and "
                 "Favorite is Yes when it is in the Favorites table; on the tested device one "
                 "episode was marked Played, one was added to the queue and one was favourited. "
                 "Published is Unix milliseconds and is reported as UTC. Position is the saved "
                 "playback position and Last Played and Completed (playback_completion_date) are "
                 "Unix millisecond times reported as UTC; these were empty on the tested device "
                 "because the episode was marked played rather than played with a saved position, "
                 "and Downloaded was No for every row because no episode audio was downloaded. "
                 "Duration is formatted from milliseconds. File Size is the audio file size in "
                 "bytes as advertised by the feed. Media URL is the episode's audio download URL "
                 "and Episode Link is its web page. The SimpleChapters table (chapter markers "
                 "parsed from each episode's feed metadata) is feed-supplied content, not user "
                 "activity, and is not parsed.",
        "paths": ('*/de.danoeh.antennapod/databases/Antennapod.db*',),
        "output_types": "standard",
        "artifact_icon": "headphones",
    },
}

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

DB_SUFFIX = 'databases/Antennapod.db'

# FeedItem.java read constants at AntennaPod/AntennaPod tag 3.12.0.
READ_STATES = {-1: 'New', 0: 'Unplayed', 1: 'Played'}


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


def _hms(ms):
    try:
        total = int(ms) // 1000
    except (TypeError, ValueError):
        return ''
    if total <= 0:
        return ''
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f'{h}:{m:02d}:{s:02d}'


def _lookup(table, value):
    if value in table:
        return table[value]
    if value is None or value == '':
        return ''
    return f'{value} (as stored)'


def _yesno(value):
    return 'Yes' if value in (1, '1') else 'No'


@artifact_processor
def antennapod_subscriptions(context):
    query = '''SELECT title, custom_title, author, download_url, link, language,
                      last_update, type, description
               FROM Feeds ORDER BY id'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                r[0] or '', r[1] or '', r[2] or '', r[3] or '', r[4] or '',
                r[5] or '', r[6] or '', r[7] or '', r[8] or '',
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        'Title', 'Custom Title', 'Author', 'Feed URL', 'Website', 'Language',
        'Last Update', 'Type', 'Description', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def antennapod_episodes(context):
    query = '''SELECT f.title, fi.title, fi.pubDate, fi.read,
                      fm.position, fm.last_played_time, fm.playback_completion_date,
                      fm.duration, fm.downloaded, fm.filesize, fm.download_url, fi.link,
                      EXISTS(SELECT 1 FROM Queue q WHERE q.feeditem = fi.id),
                      EXISTS(SELECT 1 FROM Favorites fv WHERE fv.feeditem = fi.id)
               FROM FeedItems fi
               LEFT JOIN FeedMedia fm ON fm.feeditem = fi.id
               LEFT JOIN Feeds f ON f.id = fi.feed
               ORDER BY fi.pubDate DESC'''
    data_list = []
    sources = []
    for db_path in _db_files(context):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            data_list.append((
                r[0] or '', r[1] or '', _ms(r[2]), _lookup(READ_STATES, r[3]),
                _yesno(r[12]), _yesno(r[13]), _hms(r[4]), _ms(r[5]), _ms(r[6]),
                _hms(r[7]), _yesno(r[8]), r[9], r[10] or '', r[11] or '',
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        'Feed', 'Episode Title', ('Published', 'datetime'), 'Play State',
        'In Queue', 'Favorite', 'Position', ('Last Played', 'datetime'),
        ('Completed', 'datetime'), 'Duration', 'Downloaded', 'File Size (bytes)',
        'Media URL', 'Episode Link', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
