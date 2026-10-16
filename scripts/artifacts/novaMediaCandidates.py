"""Filename candidates retain evidence scope without asserting attachment identity."""
import os
import re
import sqlite3
from scripts.artifacts.storagePathViews import canonical_path
from scripts.ilapfuncs import logfunc, open_sqlite_db_readonly

MEDIA_FOLDER = 'Android/media/com.scaleup.chatai/Nova'


def namespace(relative):
    key, _ = canonical_path(relative)
    parts = key.split('\x00')
    if len(parts) == 3:
        return parts[0], parts[1].split(':')[1]
    match = re.search(r'(^|/)data/media/(\d+)/Android/media/com\.scaleup\.chatai/Nova/',
                      str(relative).replace('\\', '/'))
    if match:
        return str(relative)[:match.start()] + match.group(1), match.group(2)
    return None


def filesystem_candidates(context, files):
    result = {}
    for path in files:
        if not os.path.isfile(path) or MEDIA_FOLDER + '/' not in path.replace('\\', '/'):
            continue
        relative = context.get_relative_path(path)
        candidate = {'path': relative, 'source': relative, 'scope': namespace(relative),
                     'extracted': path, 'name': os.path.basename(path)}
        result.setdefault(os.path.basename(path).lower(), []).append(candidate)
    return result


def mediastore_candidates(context, databases):
    result = {}
    for path in databases:
        source = context.get_relative_path(path)
        db = open_sqlite_db_readonly(path)
        if db is None:
            logfunc(f'Nova MediaStore lookup unavailable for {source}')
            continue
        try:
            for name, device_path in db.execute(
                    'SELECT _display_name, _data FROM files WHERE _data IS NOT NULL'):
                key = str(name or os.path.basename(str(device_path))).lower()
                candidate = {'path': str(device_path), 'source': source,
                             'scope': namespace(source), 'name': str(name or os.path.basename(str(device_path)))}
                bucket = result.setdefault(key, [])
                if candidate not in bucket:
                    bucket.append(candidate)
        except sqlite3.Error as exc:
            logfunc(f'Nova MediaStore lookup unavailable for {source}: {exc}')
        finally:
            db.close()
    return result


def describe_candidates(candidates, scope):
    paths, sources = [], []
    same, unknown, other = 0, 0, 0
    for candidate in sorted(candidates, key=lambda item: (item['path'], item['source'])):
        if scope is None or candidate['scope'] is None:
            relation = 'unknown user/evidence scope'
            unknown += 1
        elif candidate['scope'] == scope:
            relation = 'same Android user/evidence scope'
            same += 1
        else:
            relation = 'other Android user/evidence scope'
            other += 1
        paths.append(candidate['path'])
        sources.append(f"{candidate['name']} | {candidate['path']} | {candidate['source']} | {relation}")
    status = f'{same} same scope; {unknown} unknown scope; {other} other scope'
    return '\n'.join(sorted(set(paths))), '\n'.join(sources), status


def unique_file_candidate(candidates, scope):
    if scope is None or any(item['scope'] is None for item in candidates):
        return None
    same = [item for item in candidates if item['scope'] == scope]
    return same[0] if len(same) == 1 else None
