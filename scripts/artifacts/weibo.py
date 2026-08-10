__artifacts_v2__ = {
    "weibo_timeline": {
        "name": "Weibo - Timeline Posts",
        "description": "Posts cached in the Weibo home timeline, with the post text, the author, "
                       "the posting time, the engagement counts and the stored posted-from string",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Weibo",
        "notes": "Read from child_flow_item_table in the feed_database Room store. Each row holds "
                 "the whole post as a JSON document in serialized_data, and the columns reported "
                 "here are read out of that document: text, created_at, the nested user object, "
                 "the engagement counts and region_name.\n"
                 "These are posts the app had cached for the timeline it was showing. That is a "
                 "record of what the client held, and it does not establish that the account "
                 "holder read any particular post. The Account UID column is the uid the row is "
                 "filed under, which is the local account the timeline belongs to, not the "
                 "author.\n"
                 "Posted From is the stored region_name string, which was present on some rows "
                 "and absent on others in the tested corpus; it is reported as stored and is not "
                 "translated. The separate 'source' field of the JSON is reported as Author "
                 "Subtitle because in the tested corpus it carried the author's own descriptive "
                 "blurb or follower count rather than a posting client, so it is not labelled as "
                 "a source application.\n"
                 "created_at is a string in the format 'Wed May 21 11:00:20 +0800 2025' and is "
                 "converted to UTC using the offset it carries. Text is stored as written, so "
                 "posts appear in their original language.\n"
                 "Validation boundary: no row in the tested corpus carried a retweeted_status or "
                 "a geo object, so reposts and precise post coordinates are not covered. The "
                 "flow_item_table parent rows were almost all empty of serialized_data in the "
                 "same corpus, so this artifact reads the child table.",
        "paths": ('*/com.sina.weibo/databases/feed_database*',),
        "output_types": "standard",
        "artifact_icon": "message-square",
        "sample_data": {
            "kevin_pocox7_a15": "Android 15 | Weibo | 25 rows",
        },
    },
    "weibo_long_posts": {
        "name": "Weibo - Long Posts",
        "description": "Long-form post bodies cached by Weibo, with the full text, the post id "
                       "and the linked page title and URLs",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Weibo",
        "notes": "Read from long_text_table in ArticleDb.db, which holds the expanded body of "
                 "posts too long to fit the timeline entry. _own_uid is the local account the row "
                 "is filed under and is reported as Account UID; _mid is the post id, which is "
                 "the same identifier the timeline artifact reports as Post ID, so rows can be "
                 "matched between the two.\n"
                 "Some rows in this table store more than one value in a single field, joined "
                 "by the literal separator '#sina#', across the page title, the short and "
                 "original URLs and the page type. One of the five rows in the tested corpus did "
                 "so. Those fields are reported as stored, separator included, rather than split "
                 "on an assumption about which value belongs to which link, so most rows show a "
                 "single plain value and some show the joined form.\n"
                 "Topics are read from the _mblog_topic JSON where present and reported as the "
                 "topic titles.",
        "paths": ('*/com.sina.weibo/databases/ArticleDb.db*',),
        "output_types": "standard",
        "artifact_icon": "file-text",
        "sample_data": {
            "kevin_pocox7_a15": "Android 15 | Weibo | 5 rows",
        },
    },
    "weibo_post_images": {
        "name": "Weibo - Post Images",
        "description": "Images referenced by cached Weibo posts, with the post id, the picture id "
                       "and the remote URLs for each stored size",
        "author": "@AlexisBrignoni, Claude",
        "creation_date": "2026-08-07",
        "last_update_date": "2026-08-07",
        "requirements": "none",
        "category": "Weibo",
        "notes": "Read from mblog_pic_table in the sina_weibo database. The table records the "
                 "remote URLs Weibo serves each image from at several sizes, together with the "
                 "picture id and the id of the post the image belongs to.\n"
                 "No image bytes are reported, because none were found. The image files "
                 "themselves were searched for in the tested corpus and were not located: the "
                 "localpath column is empty on every row; no picture id appears in any file name "
                 "anywhere under the package, including its external storage directory; and "
                 "neither the MD5 of a picture id nor the MD5 of any of the stored URLs matches "
                 "any of the hash-named cache files present. The image-bearing files that are "
                 "present under the package are emoji packs and interface card graphics. So this "
                 "artifact checks nothing in as media, and an entry records that the client held "
                 "a reference to an image rather than that the image was stored on the device.\n"
                 "The URL columns are reported as links. Following one requests the image from "
                 "Sina's servers, which is a live network request, so whether to follow it is a "
                 "decision for the examiner rather than something this artifact does.\n"
                 "Post Author Name and Post Text are looked up by post id from the timeline and "
                 "long post stores so a row carries its own context; they are blank when the "
                 "post is in neither store. Post ID matches the Post ID reported by the Weibo - "
                 "Timeline Posts and Weibo - Long Posts artifacts.\n"
                 "Picture ID and the Image IDs column of Weibo - Timeline Posts use the same "
                 "identifier, but the two stores held overlapping rather than identical sets in "
                 "the tested corpus: 37 picture ids in each, 9 of them in common. So a picture "
                 "id present in one is not necessarily present in the other, and neither store "
                 "should be read as the complete set of images the app had referenced.",
        "paths": ('*/com.sina.weibo/databases/sina_weibo*',
                  '*/com.sina.weibo/databases/feed_database*',
                  '*/com.sina.weibo/databases/ArticleDb.db*'),
        "output_types": "standard",
        "artifact_icon": "image",
        "sample_data": {
            "kevin_pocox7_a15": "Android 15 | Weibo | 37 rows",
        },
    },
}

import json
from datetime import datetime, timezone

from scripts.ilapfuncs import (artifact_processor, get_file_path, get_sqlite_db_records,
                               does_table_exist_in_db, logfunc)

# Weibo stores several values per column joined by this literal separator.
SINA_SEPARATOR = '#sina#'


def _weibo_ts(value):
    """created_at looks like 'Wed May 21 11:00:20 +0800 2025'. It carries its own
    offset, so convert with it and report UTC."""
    if not value:
        return ''
    try:
        return datetime.strptime(str(value), '%a %b %d %H:%M:%S %z %Y').astimezone(timezone.utc)
    except (ValueError, TypeError):
        return str(value)


def _json_or_none(value):
    if not value:
        return None
    try:
        parsed = json.loads(value)
    except (ValueError, TypeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _topics(value):
    """_mblog_topic and topic_struct both hold a JSON list of topic objects."""
    if not value:
        return ''
    try:
        parsed = json.loads(value) if isinstance(value, str) else value
    except (ValueError, TypeError):
        return ''
    if not isinstance(parsed, list):
        return ''
    titles = []
    for item in parsed:
        if isinstance(item, dict):
            title = item.get('topic_title') or item.get('title')
            if title:
                titles.append(str(title))
    return ', '.join(titles)


@artifact_processor
def weibo_timeline(context):
    source_path = get_file_path(context.get_files_found(), 'feed_database')
    data_list = []

    if source_path and does_table_exist_in_db(source_path, 'child_flow_item_table'):
        query = '''
        SELECT uid, item_id, serialized_data
        FROM child_flow_item_table
        WHERE serialized_data IS NOT NULL
        '''
        for record in get_sqlite_db_records(source_path, query):
            post = _json_or_none(record[2])
            if post is None:
                logfunc(f'Weibo: could not read the cached post for item {record[1]}')
                continue
            user = post.get('user') if isinstance(post.get('user'), dict) else {}
            data_list.append((
                _weibo_ts(post.get('created_at')),
                post.get('text', ''),
                user.get('screen_name', ''),
                str(user.get('idstr') or user.get('id') or ''),
                user.get('location', ''),
                'Yes' if user.get('verified') else 'No',
                user.get('verified_reason', ''),
                post.get('region_name') or '',
                post.get('attitudes_count'),
                post.get('comments_count'),
                post.get('reposts_count'),
                post.get('pic_num'),
                ', '.join(str(x) for x in post.get('pic_ids') or []),
                _topics(post.get('topic_struct')),
                post.get('source', ''),
                str(post.get('idstr') or post.get('id') or ''),
                post.get('mblogid', ''),
                record[0],
            ))

    data_headers = (
        ('Created Timestamp', 'datetime'),
        'Post Text',
        'Author Name',
        'Author UID',
        'Author Location',
        'Author Verified',
        'Author Verified Reason',
        'Posted From',
        'Likes',
        'Comments',
        'Reposts',
        'Image Count',
        'Image IDs',
        'Topics',
        'Author Subtitle',
        'Post ID',
        'Post Short ID',
        'Account UID',
    )
    return data_headers, data_list, source_path


@artifact_processor
def weibo_long_posts(context):
    source_path = get_file_path(context.get_files_found(), 'ArticleDb.db')
    data_list = []

    if source_path and does_table_exist_in_db(source_path, 'long_text_table'):
        query = '''
        SELECT _mid, _content, _page_title, _page_short_url, _page_ori_url, _mblog_topic,
               _is_paid, _pic_num, _page_type, _own_uid
        FROM long_text_table
        '''
        for record in get_sqlite_db_records(source_path, query):
            data_list.append((
                record[1],
                _topics(record[5]),
                record[2],
                record[3],
                record[4],
                'Yes' if record[6] else 'No',
                record[7],
                record[8],
                record[0],
                record[9],
            ))

    data_headers = (
        'Post Text',
        'Topics',
        f'Page Title (multiple values joined by {SINA_SEPARATOR})',
        f'Short URL (multiple values joined by {SINA_SEPARATOR})',
        f'Original URL (multiple values joined by {SINA_SEPARATOR})',
        'Is Paid',
        'Image Count',
        'Page Type (as stored)',
        'Post ID',
        'Account UID',
    )
    return data_headers, data_list, source_path


def _post_text_by_id(files_found):
    """Post text lives in a different database from the image rows, so build a
    lookup keyed on the post id the two share."""
    posts = {}

    article_path = get_file_path(files_found, 'ArticleDb.db')
    if article_path and does_table_exist_in_db(article_path, 'long_text_table'):
        for record in get_sqlite_db_records(
                article_path, 'SELECT _mid, _content FROM long_text_table'):
            if record[0]:
                posts[str(record[0])] = ('', record[1] or '')

    feed_path = get_file_path(files_found, 'feed_database')
    if feed_path and does_table_exist_in_db(feed_path, 'child_flow_item_table'):
        query = ('SELECT serialized_data FROM child_flow_item_table '
                 'WHERE serialized_data IS NOT NULL')
        for record in get_sqlite_db_records(feed_path, query):
            post = _json_or_none(record[0])
            if not post:
                continue
            post_id = str(post.get('idstr') or post.get('id') or '')
            if not post_id:
                continue
            user = post.get('user') if isinstance(post.get('user'), dict) else {}
            posts[post_id] = (user.get('screen_name', ''), post.get('text', ''))

    return posts


@artifact_processor
def weibo_post_images(context):
    source_path = get_file_path(context.get_files_found(), 'sina_weibo')
    data_list = []
    posts = _post_text_by_id(context.get_files_found())

    if source_path and does_table_exist_in_db(source_path, 'mblog_pic_table'):
        query = '''
        SELECT mblogid, picid, objectid, pictype, originalurl, originalwidth, originalheight,
               largesturl, thumbnailurl, localpath
        FROM mblog_pic_table
        '''
        for record in get_sqlite_db_records(source_path, query):
            author, text = posts.get(str(record[0]), ('', ''))
            data_list.append((
                record[0],
                author,
                text,
                record[1],
                record[3],
                f'{record[5]} x {record[6]}' if record[5] and record[6] else '',
                record[4],
                record[7],
                record[8],
                record[9] or '',
                record[2],
            ))

    data_headers = (
        'Post ID',
        'Post Author Name',
        'Post Text',
        'Picture ID',
        'Picture Type',
        'Original Size',
        'Original URL',
        'Largest URL',
        'Thumbnail URL',
        'Local Path (as stored)',
        'Object ID',
    )
    return data_headers, data_list, source_path
