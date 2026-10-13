import hashlib
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.ilapfuncs import abxread, artifact_processor, logfunc


__artifacts_v2__ = {
    'get_shortcut_service': {
        'name': 'Shortcut Service - Shortcuts',
        'description': 'Application shortcuts, labels, persons, intents and extras.',
        'creation_date': '2026-10-09',
        'last_update_date': '2026-10-13',
        'requirements': 'none',
        'category': 'Shortcut Service',
        'notes': 'Shortcut Updated is the last change to shortcut fields in Unix milliseconds, '
                 'not a message receipt, read or upload time. Names and case are preserved. '
                 'Backup files remain separate sources. Timeline entries use Shortcut Updated; '
                 'the raw millisecond timestamp is retained alongside LAVA dates. '
                 'In the three public CTF samples, Android User was uniformly 0 and '
                 'Disabled Reason (as stored) uniformly 0; profiles and stored codes remain separate. '
                 'File Format was uniform per sample: XML for Android 10 and ABX for Android 12. '
                 'Locus ID was absent and Persons (JSON) uniformly [] in the Android 10 sample; '
                 'other samples populated these fields. Source File separates files and backup '
                 'copies even when Package and Shortcut ID are the same.',
        'paths': (
            '*/system_ce/*/shortcut_service/shortcuts.xml*',
            '*/system_ce/*/shortcut_service/packages/*.xml*',
        ),
        'output_types': ['html', 'tsv', 'timeline', 'lava'],
        'artifact_icon': 'link',
    },
    'get_shortcut_service_fields': {
        'name': 'Shortcut Service - Fields',
        'description': 'XML elements, attributes, text and decoded JSON fields with their source paths.',
        'creation_date': '2026-10-09',
        'last_update_date': '2026-10-13',
        'requirements': 'none',
        'category': 'Shortcut Service',
        'notes': 'Preserves XML names, types, attributes and values. XML paths use one-based '
                 'sibling indices. JSON fields supplement the original value and use JSON Pointer. '
                 'Backup files remain separate sources. Android User was uniformly 0 in the '
                 'three public CTF samples; the synthetic fixture covers users 0 and 10. '
                 'File Format was uniform per sample: XML for Android 10 and ABX for Android 12. '
                 'Source File distinguishes separate files and backup copies; Package and '
                 'Shortcut ID alone do not identify a stored observation.',
        'paths': (
            '*/system_ce/*/shortcut_service/shortcuts.xml*',
            '*/system_ce/*/shortcut_service/packages/*.xml*',
        ),
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'list-details',
    },
    'get_shortcut_service_discord': {
        'name': 'Shortcut Service - Discord',
        'description': 'Discord shortcut payloads, stored usernames, account IDs and message JSON.',
        'creation_date': '2026-10-09',
        'last_update_date': '2026-10-13',
        'requirements': 'none',
        'category': 'Shortcut Service',
        'notes': 'One row per payload. Extra and JSON values are separate '
                 'observations and are not substituted for one another. Stored usernames '
                 'are snapshots, not a complete alias history. Message times are converted '
                 'only when their ISO timestamp includes a timezone; originals are retained. '
                 'Shortcut Updated is a field-change time in Unix milliseconds. Payload arrays '
                 'with duplicate keys retain every pair and report the conflict; columns use '
                 'the first occurrence. Backup files remain separate sources. Timeline entries '
                 'use Shortcut Updated, not Message Time. Original millisecond and ISO timestamps '
                 'are retained alongside LAVA dates. In the single Discord CTF payload, '
                 'Message Edited (UTC) and Message Edited (as stored) were blank because no '
                 'edit timestamp was stored; Guild ID (extra) and Guild ID (JSON) were absent. '
                 'Source File distinguishes backup copies of the same Shortcut ID.',
        'paths': (
            '*/system_ce/*/shortcut_service/shortcuts.xml*',
            '*/system_ce/*/shortcut_service/packages/*.xml*',
        ),
        'output_types': ['html', 'tsv', 'timeline', 'lava'],
        'artifact_icon': 'message',
    },
    'get_shortcut_service_files': {
        'name': 'Shortcut Service - Files',
        'description': 'Shortcut XML file inventory, format, counts, SHA-256 and parse status.',
        'creation_date': '2026-10-09',
        'last_update_date': '2026-10-13',
        'requirements': 'none',
        'category': 'Shortcut Service',
        'notes': 'Includes empty documents and files that could not be parsed. A file '
                 'with no shortcuts does not establish that an app was unused or uninstalled. '
                 'Android User was uniformly 0 in the three public CTF samples. File Format '
                 'was uniform per sample: XML for Android 10 and ABX for Android 12. '
                 'Parse Status was uniformly Parsed in the Android 10 sample and the first '
                 'Android 12 sample; the second Android 12 sample also had one Empty ABX document. '
                 'Error was blank in all three samples because no parse failed; the empty '
                 'ABX document is inventoried without an error.',
        'paths': (
            '*/system_ce/*/shortcut_service/shortcuts.xml*',
            '*/system_ce/*/shortcut_service/packages/*.xml*',
        ),
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'file',
    },
}


def _tag(element):
    return element.tag.rsplit('}', 1)[-1]


def _json(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def _text(value):
    if value is None:
        return ''
    return value if isinstance(value, str) else _json(value)


def _ms(value):
    try:
        number = int(value)
        if number <= 0:
            return ''
        return datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(milliseconds=number)
    except (TypeError, ValueError, OverflowError):
        return ''


def _iso(value):
    if not isinstance(value, str) or not value:
        return ''
    try:
        parsed = datetime.fromisoformat(value[:-1] + '+00:00' if value.endswith('Z') else value)
        return parsed.astimezone(timezone.utc) if parsed.tzinfo is not None else ''
    except (ValueError, OverflowError):
        return ''


def _user(source):
    match = re.search(r'(?:^|/)system_ce/(\d+)/shortcut_service/', source.replace('\\', '/'))
    return match.group(1) if match else ''


def _files(context):
    seen = set()
    for found in sorted(str(path) for path in context.get_files_found()):
        if found in seen:
            continue
        seen.add(found)
        path = Path(found)
        if path.is_file() and path.name.endswith(('.xml', '.xml.bak', '.xml.reservecopy')):
            yield path


def _error(exc, document):
    message = str(exc)
    path, source = str(document['path']), document['source']
    message = message.replace(repr(path), repr(source)).replace(path, source)
    return f'{type(exc).__name__}: {message}'


def _documents(context):
    for path in _files(context):
        source = context.get_relative_path(str(path)).replace('\\', '/')
        document = {
            'path': path, 'source': source, 'user': _user(source), 'root': None,
            'format': '', 'status': '', 'error': '',
        }
        try:
            with path.open('rb') as stream:
                prefix = stream.read(6)
            document['format'] = 'ABX' if prefix.startswith(b'ABX\x00') else 'XML'
            if not prefix:
                document['status'] = 'Empty file'
            elif prefix in (b'ABX\x00\x10\x11', b'ABX\x00\x11') and path.stat().st_size == len(prefix):
                document['status'] = 'Empty ABX document'
            else:
                tree = abxread(str(path), False) if document['format'] == 'ABX' else ET.parse(path)
                document['root'] = tree.getroot()
                document['status'] = 'Parsed'
        except Exception as exc:  # pylint: disable=broad-exception-caught
            document['status'] = 'Parse error'
            document['error'] = _error(exc, document)
            logfunc(f'Shortcut Service: {source}: {document["error"]}')
        yield document


def _walk(element, path=None, package='', shortcut_id='', shortcut_index=''):
    tag = _tag(element)
    if path is None:
        path = f'/{tag}[1]'
    if tag == 'package':
        package = element.get('name', '')
    if tag == 'shortcut':
        shortcut_id = element.get('id', '')
        shortcut_index = path.rsplit('[', 1)[-1].rstrip(']')
    yield element, path, package, shortcut_id, shortcut_index
    counts = Counter()
    for child in element:
        child_tag = _tag(child)
        counts[child_tag] += 1
        child_path = f'{path}/{child_tag}[{counts[child_tag]}]'
        yield from _walk(child, child_path, package, shortcut_id, shortcut_index)


def _node(element):
    result = {'tag': element.tag, 'attributes': dict(element.attrib)}
    if element.text is not None and (not len(element) or element.text.strip()):
        result['text'] = element.text
    if len(element):
        result['children'] = [_node(child) for child in element]
    return result


def _children(element, tag):
    return [child for child in element if _tag(child) == tag]


def _json_fields(value, pointer=''):
    if isinstance(value, dict):
        for key, child in value.items():
            escaped = str(key).replace('~', '~0').replace('/', '~1')
            yield from _json_fields(child, f'{pointer}/{escaped}')
        if not value:
            yield pointer, 'object', '{}'
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _json_fields(child, f'{pointer}/{index}')
        if not value:
            yield pointer, 'array', '[]'
    else:
        kind = 'null' if value is None else 'boolean' if isinstance(value, bool) else \
            'number' if isinstance(value, (int, float)) else 'string'
        yield pointer, kind, _text(value) if value is not None else 'null'


def _decode_json(value):
    if not isinstance(value, str) or not value.lstrip().startswith(('{', '[')):
        return None
    try:
        return json.loads(value)
    except (ValueError, RecursionError):
        return None


def _pairs(array):
    items = [item.get('value', item.text or '') for item in array if _tag(item) == 'item']
    pairs = list(zip(items[::2], items[1::2]))
    warnings = []
    if len(items) % 2:
        warnings.append('Odd array length; trailing item retained in Fields')
    if array.get('num') is not None and array.get('num') != str(len(items)):
        warnings.append('Array count mismatch')
    counts = Counter(key for key, _ in pairs)
    duplicates = [key for key, count in counts.items() if count > 1]
    if duplicates:
        warnings.append('Duplicate keys: ' + ', '.join(duplicates))
    return pairs, warnings


def _discord_payloads(shortcut, shortcut_path):
    for element, path, _, _, _ in _walk(shortcut, shortcut_path):
        if _tag(element) == 'string-array' and element.get('name') == 'discord_shortcut_data':
            pairs, warnings = _pairs(element)
            yield path, pairs, warnings
        elif _tag(element) in ('extras', 'intent-extras'):
            pairs = []
            for child in element:
                if _tag(child) in ('string', 'boolean', 'int', 'long', 'double', 'float'):
                    name = child.get('name')
                    if name is not None:
                        pairs.append((name, child.get('value', child.text or '')))
            if {'user_username', 'message_content', 'message_id'}.intersection(key for key, _ in pairs):
                yield path, pairs, []


@artifact_processor
def get_shortcut_service(context):
    headers = (
        ('Shortcut Updated (UTC)', 'datetime'), 'Shortcut Timestamp (ms, as stored)',
        'Android User', 'Package', 'Shortcut ID', 'Shortcut Index', 'Short Label',
        'Long Label', 'Activity', 'Locus ID', 'Rank (as stored)', 'Flags (as stored)',
        'Disabled Reason (as stored)', 'Persons (JSON)', 'Categories (JSON)',
        'Intents (JSON)', 'Extras (JSON)', 'Attributes (JSON)', 'XML Path',
        'File Format', 'Source File',
    )
    rows, sources = [], []
    for document in _documents(context):
        root = document['root']
        if root is None:
            continue
        sources.append(document['source'])
        for element, path, package, shortcut_id, index in _walk(root):
            if _tag(element) != 'shortcut':
                continue
            attrs = element.attrib
            rows.append((
                _ms(attrs.get('timestamp')), attrs.get('timestamp', ''), document['user'],
                package, shortcut_id, index, attrs.get('title', ''), attrs.get('text', ''),
                attrs.get('activity', ''), attrs.get('locus-id', ''), attrs.get('rank', ''),
                attrs.get('flags', ''), attrs.get('disabled-reason', ''),
                _json([_node(child) for child in _children(element, 'person')]),
                _json([_node(child) for child in _children(element, 'categories')]),
                _json([_node(child) for child in _children(element, 'intent')]),
                _json([_node(child) for child in element if _tag(child) in ('extras', 'intent-extras')]),
                _json(dict(attrs)), path, document['format'], document['source'],
            ))
    return headers, rows, '\n'.join(sources)


@artifact_processor
def get_shortcut_service_fields(context):
    headers = (
        'Android User', 'Package', 'Shortcut ID', 'Shortcut Index', 'XML Path',
        'Entry Name (as stored)', 'Field', 'Type', 'Value', 'Representation',
        'JSON Pointer', 'File Format', 'Source File',
    )
    rows, sources = [], []
    for document in _documents(context):
        root = document['root']
        if root is None:
            continue
        sources.append(document['source'])
        for element, path, package, shortcut_id, index in _walk(root):
            prefix = (document['user'], package, shortcut_id, index, path, element.get('name', ''))
            suffix = (document['format'], document['source'])
            rows.append(prefix + ('', _tag(element), '', 'element', '') + suffix)
            values = [(f'@{key}', value, 'attribute') for key, value in element.attrib.items()]
            if element.text is not None and (not len(element) or element.text.strip()):
                values.append(('#text', element.text, 'text'))
            if element.tail is not None and element.tail.strip():
                values.append(('#tail', element.tail, 'tail'))
            for field, value, representation in values:
                rows.append(prefix + (field, _tag(element), value, representation, '') + suffix)
                decoded = _decode_json(value)
                if decoded is not None:
                    try:
                        decoded_rows = list(_json_fields(decoded))
                    except RecursionError:
                        continue
                    for pointer, kind, decoded_value in decoded_rows:
                        rows.append(prefix + (field, kind, decoded_value, 'JSON', pointer) + suffix)
    return headers, rows, '\n'.join(sources)


@artifact_processor
def get_shortcut_service_discord(context):
    headers = (
        ('Shortcut Updated (UTC)', 'datetime'), 'Shortcut Timestamp (ms, as stored)',
        ('Message Time (UTC)', 'datetime'), 'Message Time (as stored)',
        ('Message Edited (UTC)', 'datetime'), 'Message Edited (as stored)',
        'Android User', 'Shortcut ID', 'Shortcut Label',
        'User ID (extra)', 'Username (extra)', 'Author ID (JSON)',
        'Author Username (JSON)', 'Author Global Name (JSON)', 'Author Discriminator (JSON)',
        'Receiving User ID (extra)', 'Channel ID (extra)', 'Channel ID (JSON)',
        'Message ID (extra)', 'Message ID (JSON)', 'Guild ID (extra)', 'Guild ID (JSON)',
        'Message Content (extra)', 'Message Content (JSON)', 'Event Type (extra)',
        'Channel Type (extra)', 'Attachments (JSON)', 'Referenced Message (JSON)',
        'Payload Pairs (JSON)', 'Message JSON (as stored)', 'Decode Status',
        'Payload XML Path', 'Source File',
    )
    rows, sources = [], []
    for document in _documents(context):
        root = document['root']
        if root is None:
            continue
        used = False
        for element, path, package, shortcut_id, _ in _walk(root):
            if _tag(element) != 'shortcut' or package != 'com.discord':
                continue
            for payload_path, pairs, warnings in _discord_payloads(element, path):
                payload = {}
                for key, value in pairs:
                    payload.setdefault(key, value)
                raw_message = payload.get('message', '')
                message = _decode_json(raw_message)
                if not isinstance(message, dict):
                    message = {}
                    if raw_message:
                        warnings = warnings + ['Message is not a JSON object']
                author = message.get('author', {})
                if not isinstance(author, dict):
                    author = {}
                timestamp = message.get('timestamp', '')
                edited = message.get('edited_timestamp', '')
                attrs = element.attrib
                rows.append((
                    _ms(attrs.get('timestamp')), attrs.get('timestamp', ''),
                    _iso(timestamp), _text(timestamp), _iso(edited), _text(edited),
                    document['user'], shortcut_id, attrs.get('title', ''),
                    payload.get('user_id', ''), payload.get('user_username', ''),
                    _text(author.get('id')), _text(author.get('username')),
                    _text(author.get('global_name')), _text(author.get('discriminator')),
                    payload.get('receiving_user_id', ''), payload.get('channel_id', ''),
                    _text(message.get('channel_id')), payload.get('message_id', ''),
                    _text(message.get('id')), payload.get('guild_id', ''),
                    _text(message.get('guild_id')), payload.get('message_content', ''),
                    _text(message.get('content')), payload.get('type', ''),
                    payload.get('channel_type', ''),
                    _json(message['attachments']) if 'attachments' in message else '',
                    _json(message['referenced_message']) if 'referenced_message' in message else '',
                    _json(pairs), raw_message, '; '.join(warnings) if warnings else 'Decoded',
                    payload_path, document['source'],
                ))
                used = True
        if used:
            sources.append(document['source'])
    return headers, rows, '\n'.join(sources)


@artifact_processor
def get_shortcut_service_files(context):
    headers = (
        'Android User', 'File Format', 'Root Element', 'Packages (JSON)', 'Package Count',
        'Shortcut Count', 'Size (bytes)', 'SHA-256', 'Parse Status', 'Error', 'Source File',
    )
    rows, sources = [], []
    for document in _documents(context):
        root = document['root']
        packages, shortcuts = [], 0
        if root is not None:
            for element, _, _, _, _ in _walk(root):
                if _tag(element) == 'package':
                    packages.append(element.get('name', ''))
                elif _tag(element) == 'shortcut':
                    shortcuts += 1
        digest, size = '', ''
        try:
            with document['path'].open('rb') as stream:
                hasher = hashlib.sha256()
                while chunk := stream.read(65536):
                    hasher.update(chunk)
                digest = hasher.hexdigest()
            size = document['path'].stat().st_size
        except OSError as exc:
            document['error'] = _error(exc, document)
        sources.append(document['source'])
        rows.append((
            document['user'], document['format'], _tag(root) if root is not None else '',
            _json(packages), len(packages), shortcuts, size, digest, document['status'],
            document['error'], document['source'],
        ))
    return headers, rows, '\n'.join(sources)
