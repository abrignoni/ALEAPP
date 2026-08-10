__artifacts_v2__ = {
    "get_blueskyposts": {
        "name": "Bluesky - Posts",
        "description": "Bluesky feed and posts cached in the http-cache",
        "author": "Alexis Brignoni",
        "creation_date": "2024-11-20",
        "last_update_date": "2024-11-20",
        "requirements": "none",
        "category": "Bluesky",
        "notes": "",
        "paths": ('*/xyz.blueskyweb.app/cache/http-cache/*.*',),
        "output_types": "standard",
        "artifact_icon": "edit",
    }
}

import datetime
import json

from scripts.ilapfuncs import artifact_processor


def _iso_to_utc(value):
    if not value:
        return ''
    try:
        return datetime.datetime.fromisoformat(str(value).replace('Z', '+00:00')).astimezone(
            datetime.timezone.utc)
    except (ValueError, TypeError):
        return ''


def _extract_post(post, collection):
    record = post.get('record', {})
    author = post.get('author', {})
    langs = record.get('langs')
    langs = ', '.join(langs) if isinstance(langs, list) else (langs or '')
    return (
        collection, _iso_to_utc(record.get('createdAt')), _iso_to_utc(author.get('createdAt')),
        record.get('$type'), author.get('handle'), author.get('displayName'), record.get('text'),
        post.get('replyCount'), post.get('repostCount'), post.get('likeCount'), post.get('quoteCount'),
        author.get('avatar'), author.get('did'), langs, post.get('cid'), post.get('uri'))


@artifact_processor
def get_blueskyposts(context):
    files_found = context.get_files_found()
    seen = set()
    data_list = []
    source_path = ''
    for file_found in files_found:
        file_found = str(file_found)
        try:
            with open(file_found, 'r', encoding='utf-8') as handle:
                data = json.load(handle)
        except (ValueError, OSError, UnicodeDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        source_path = file_found
        for collection, key in (('Feed', 'feed'), ('Posts', 'posts')):
            for entry in data.get(key) or []:
                post = entry.get('post') if collection == 'Feed' else entry
                if not isinstance(post, dict):
                    continue
                row = _extract_post(post, collection)
                if row not in seen:
                    seen.add(row)
                    data_list.append(row)

    data_headers = ('Collection', ('Timestamp', 'datetime'), ('Author Created At', 'datetime'), 'Type',
                    'Handle', 'Display Name', 'Text', 'Reply Count', 'Repost Count', 'Like Count',
                    'Quote Count', 'Avatar', 'DID', 'Language', 'CID', 'URI')
    return data_headers, data_list, source_path
