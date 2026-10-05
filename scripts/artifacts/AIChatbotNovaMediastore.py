__artifacts_v2__ = {
    "nova_user_submissions": {
        "name": "Nova Media Records",
        "description": "Nova document/image records and discovered app-folder files. Filename candidates retain MediaStore/filesystem sources and Android user scope; they do not establish attachment identity.",
        "author": "@AlexisBrignoni, Codex",
        "creation_date": "2026-05-30",
        "last_update_date": "2026-10-05",
        "requirements": "none",
        "category": "AI Chatbot - Nova",
        "notes": "Original parser/research: Guilherme Guilherme. Scope describes the source evidence path, not ownership of a recorded device path. Both message sides are retained; Message Type is the stored value. Matching retains the existing case-insensitive filename comparison. Same-user evidence scope narrows filename candidates but does not prove attachment identity; unknown and other scopes are explicit. Media Candidate renders only a unique same-scope filesystem filename candidate with no unknown-scope collision. Ambiguous/unmatched app-folder files are reported separately, without a submission/deletion claim. MIME is stored, not sniffed. Epoch interpretation is unchanged. The author reference is an own-installation fixture, not a registered corpus sample; positive real-corpus/physical-media coverage is unavailable.",
        "paths": (
            "**/com.scaleup.chatai/databases/chat-ai.db",
            "**/com.android.providers.media/databases/external*.db",
            "**/com.google.android.providers.media.module/databases/external*.db",
            "**/data/media/*/Android/media/com.scaleup.chatai/Nova/*",
        ),
        "output_types": ["standard", "lava"],
        "artifact_icon": "folder",
    }
}

import datetime
import os
import sqlite3

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import (
    artifact_processor,
    check_in_media,
    logfunc,
    open_sqlite_db_readonly,
)

from scripts.artifacts.novaMediaCandidates import (
    filesystem_candidates, mediastore_candidates, namespace,
    describe_candidates, unique_file_candidate,
)


def _epoch_to_utc(value):
    """chat-ai.db epochs are milliseconds; values below 1e11 are read as
    seconds (the magnitudes cannot overlap for plausible dates)."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return ''
    if value <= 0:
        return ''
    if value > 1e11:
        value /= 1000
    try:
        return datetime.datetime.fromtimestamp(value, datetime.timezone.utc)
    except (ValueError, OverflowError, OSError):
        return ''


@artifact_processor
def nova_user_submissions(context):
    headers = (
        ("Date", "datetime"), "File Name", "Type", "Context", "MIME",
        ("Media Candidate", "media"), "MediaStore Candidate Paths",
        "MediaStore Candidate Sources", "MediaStore Match Scope",
        "Filesystem Candidate Paths", "Filesystem Candidate Sources",
        "Filesystem Match Scope", "Message Type", "Source File"
    )
    files = [str(path) for path in unique_files(context)]
    nova_dbs = sorted(path for path in files if os.path.basename(path) == 'chat-ai.db')
    media_dbs = sorted(path for path in files
                       if os.path.basename(path).startswith('external') and path.endswith('.db'))
    filesystem = filesystem_candidates(context, files)
    store = mediastore_candidates(context, media_dbs)
    rows, processed, sources = [], set(), [context.get_relative_path(p) for p in media_dbs]
    for path in nova_dbs:
        source = context.get_relative_path(path)
        scope = namespace(source)
        sources.append(source)
        db = open_sqlite_db_readonly(path)
        if db is None:
            logfunc(f'Nova Media Records database unavailable for {source}')
            continue
        try:
            queries = [
                ('Document', 'SELECT hdd.name, hdd.mimeType, hd.text, hd.createdAt, hd.type '
                 'FROM HistoryDetailDocument hdd INNER JOIN HistoryDetail hd '
                 'ON hd.id=hdd.historyDetailID'),
                ('Image', 'SELECT hdi.url, hdi.prompt, hd.text, hd.createdAt, hd.type '
                 'FROM HistoryDetailImage hdi INNER JOIN HistoryDetail hd '
                 'ON hd.id=hdi.historyDetailID')]
            for kind, query in queries:
                for name, detail, message, timestamp, message_type in db.execute(query):
                    filename = os.path.basename(str(name).split('?')[0]) if kind == 'Image' else name
                    key = str(filename or '').lower()
                    candidates = filesystem.get(key, [])
                    selected = unique_file_candidate(candidates, scope)
                    reference = ''
                    if selected:
                        reference = check_in_media(selected['extracted'],
                                                   name=os.path.basename(selected['extracted'])) or ''
                        processed.add(selected['extracted'])
                    context_text = f'Msg: {message} | Prompt: {detail}' if kind == 'Image' else message
                    rows.append((_epoch_to_utc(timestamp), filename, kind, context_text,
                                 detail or '' if kind == 'Document' else '', reference,
                                 *describe_candidates(store.get(key, []), scope),
                                 *describe_candidates(candidates, scope), message_type, source))
        except sqlite3.Error as exc:
            logfunc(f'Nova Media Records query unavailable for {source}: {exc}')
        finally:
            db.close()
    # Retain physical candidates that could not be uniquely associated by filename.
    for key in sorted(filesystem):
        candidates = filesystem[key]
        for item in sorted(candidates, key=lambda value: value['source']):
            if item['extracted'] in processed:
                continue
            filename = os.path.basename(item['extracted'])
            reference = check_in_media(item['extracted'], name=filename) or ''
            rows.append((None, filename, 'Filesystem Media',
                         'Discovered app-folder file; attachment identity is unestablished', '',
                         reference, *describe_candidates(store.get(filename.lower(), []), item['scope']),
                         *describe_candidates([item], item['scope']), None, item['source']))
            sources.append(item['source'])
    return headers, rows, '\n'.join(sorted(set(sources)))
