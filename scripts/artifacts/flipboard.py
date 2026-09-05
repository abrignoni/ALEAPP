__artifacts_v2__ = {
    "flipboard_article_history": {
        "name": "Flipboard Article History",
        "description": "Articles opened in Flipboard, with publisher and source URL",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Flipboard",
        "sample_data": {
            "emu_a15_oss_v10": "Flipboard 4.3.62 | 2 rows",
        },
        "notes": "One row per row of the view_history table in "
                 "flipboard.app/databases/view_history_database, which the app writes when an "
                 "article is opened. Viewed is Unix seconds and is reported as UTC. Each row also "
                 "carries a JSON copy of the item as it stood when it was opened, in the "
                 "valid_item column, and Source URL, Author, Published and Excerpt are read out "
                 "of that JSON rather than fetched from anywhere. Published is the item's own "
                 "dateCreated in Unix seconds, so it is when the article was published and not "
                 "when it was read; the two are in separate columns for that reason. Excerpt is "
                 "the app's own strippedExcerptText and is truncated by the app, not by this "
                 "artifact. Source URL is reported as plain text and is not made clickable. Read "
                 "and Bookmarked come from the isRead and isBookmarked flags in the same JSON. "
                 "This table records that the article was opened in the app; it does not record "
                 "how long it stayed open or whether it was read. Flipboard runs without an "
                 "account, and the tested device was never signed in, so these rows were produced "
                 "by an anonymous session.",
        "paths": ('*/flipboard.app/databases/view_history_database*',),
        "output_types": "standard",
        "artifact_icon": "book-open",
    },
    "flipboard_sections": {
        "name": "Flipboard Followed Sections",
        "description": "Sections Flipboard lists, the topics followed and the feeds the app adds itself",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-09-05",
        "last_update_date": "2026-09-05",
        "requirements": "none",
        "category": "Flipboard",
        "sample_data": {
            "emu_a15_oss_v10": "Flipboard 4.3.62 | 5 rows",
        },
        "notes": "One row per row of the sections table in flipboard.app/databases/users-v6.db. "
                 "The table's own columns are almost all empty; everything reported here is read "
                 "from the descriptor column, which holds plain JSON. Title, Feed Type, Remote ID "
                 "and Private come from that JSON. A Feed Type of topic marks a subject feed "
                 "rather than a feed the app added by itself, and the Remote ID carries the "
                 "topic slug after flipboard/topic%2F. Rows with no Feed Type are the feeds the "
                 "app added, and their Remote ID names what they are: the tested device held "
                 "auth/flipboard/coverstories and one flipboard/mix row. Position is the sections "
                 "table's own pos column and is the order the app lists them in. There is no "
                 "timestamp in this table, so a row says the section is followed and not when it "
                 "was followed. On the tested device the three topics chosen during first run were "
                 "all present with Feed Type topic, alongside those two. Service held the single "
                 "value flipboard on every "
                 "row and User ID held one value, because the tested device carried one anonymous "
                 "profile and no other service. Both are kept: User ID is what separates the rows "
                 "on a device holding more than one profile, and Service is what would separate a "
                 "section pulled in from a linked account.",
        "paths": ('*/flipboard.app/databases/users-v6.db*',),
        "output_types": "standard",
        "artifact_icon": "hash",
    },
}

import json

from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, get_sqlite_db_records
from scripts.artifacts.storagePathViews import unique_files

HISTORY_SUFFIX = 'databases/view_history_database'
USERS_SUFFIX = 'databases/users-v6.db'


def _files(context, suffix):
    return [str(f).replace('\\', '/') for f in unique_files(context)
            if str(f).replace('\\', '/').endswith(suffix)]


def _secs(value):
    if not value or int(value) <= 0:
        return ''
    try:
        return convert_unix_ts_to_utc(int(value))
    except (TypeError, ValueError, OverflowError, OSError):
        return ''


def _payload(raw):
    """Parse the stored JSON copy of the item. Returns {} when it will not parse."""
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except (ValueError, TypeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _flag(value):
    if value is True:
        return 'Yes'
    if value is False:
        return 'No'
    return ''


@artifact_processor
def flipboard_article_history(context):
    query = ('SELECT time_viewed, title, publisher_name, domain_name, item_type, '
             'valid_item, id FROM view_history ORDER BY time_viewed DESC')
    data_list = []
    sources = []
    for db_path in _files(context, HISTORY_SUFFIX):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            item = _payload(r[5])
            data_list.append((
                _secs(r[0]), _secs(item.get('dateCreated')), r[1] or item.get('title', ''),
                r[2] or '', r[3] or item.get('sourceDomain', ''),
                item.get('sourceURL', ''), item.get('authorDisplayName', ''),
                item.get('strippedExcerptText', ''), r[4] or '',
                _flag(item.get('isRead')), _flag(item.get('isBookmarked')),
                r[6] or '', context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        ('Viewed', 'datetime'), ('Published', 'datetime'), 'Title', 'Publisher',
        'Domain', 'Source URL', 'Author', 'Excerpt', 'Item Type', 'Read',
        'Bookmarked', 'Item ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def flipboard_sections(context):
    query = 'SELECT descriptor, pos, uid, id FROM sections ORDER BY pos'
    data_list = []
    sources = []
    for db_path in _files(context, USERS_SUFFIX):
        records = get_sqlite_db_records(db_path, query)
        for r in records:
            raw = r[0]
            if isinstance(raw, (bytes, bytearray)):
                raw = raw.decode('utf-8', 'replace')
            item = _payload(raw)
            data_list.append((
                item.get('title', ''), item.get('feedType', ''),
                item.get('remoteid', ''), _flag(item.get('private')),
                item.get('service', ''), r[1], r[2] or '', r[3],
                context.get_relative_path(db_path)))
        if records and db_path not in sources:
            sources.append(db_path)

    data_headers = (
        'Title', 'Feed Type', 'Remote ID', 'Private', 'Service', 'Position',
        'User ID', 'Section Row ID', 'Source File')
    return data_headers, data_list, '\n'.join(sources)
