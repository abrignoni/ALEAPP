import codecs
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from PIL import Image

from scripts.ilapfuncs import abxread, artifact_processor, check_in_media, logfunc


__artifacts_v2__ = {
    'get_shortcut_service': {
        'name': 'Shortcut Service - Shortcuts',
        'description': 'Application shortcuts, labels, persons, intents, extras and '
                       'stored icon files.',
        'creation_date': '2026-10-09',
        'last_update_date': '2026-10-14',
        'requirements': 'none',
        'category': 'Shortcut Service',
        'notes': 'Shortcut Updated is the last change to shortcut fields in Unix '
                 'milliseconds, not a message receipt, read or upload time. '
                 'Timeline entries use Shortcut Updated; the original millisecond '
                 'value is retained. Names and case are preserved. Flags are a '
                 'bitmask decoded from AOSP ShortcutInfo constants; unknown bits '
                 'remain visible. Cached notification flags describe shortcut '
                 'state, not a notification receipt or user action. Disabled Reason '
                 'is an enum, with the stored value retained next to its label. '
                 'Identical backup and fallback copies are inventoried without '
                 'repeating shortcut rows; differing copies and copies without a '
                 'main file remain separate sources. Icons are matched by stored '
                 'path within the same extraction, Android user and package. '
                 'Shortcut Image is a stored shortcut icon, not an independently '
                 'identified message attachment. Missing, invalid or ambiguous '
                 'images remain visible in Bitmap Status. Dump files are '
                 'inventoried by Files and are not treated as current shortcut '
                 'records. Validation on DFRWS 2021 Galaxy S10, Magnet User Summit '
                 'CTF 2023 Pixel 3a XL and Magnet Virtual Summit CTF 2024 Pixel 3a '
                 'XL found Android User uniformly 0, Disabled Reason (as stored) '
                 'uniformly 0, Disabled Reason (decoded) uniformly not_disabled and '
                 'Source Kind uniformly Shortcut XML. File Format was uniform per '
                 'named image: XML on DFRWS 2021 Galaxy S10 and ABX on the two '
                 'named Magnet images. On DFRWS 2021 Galaxy S10, Locus ID was empty '
                 'and Persons (JSON) uniformly []; these observations apply only to '
                 'those named images.',
        'paths': (
            '*/system_ce/*/shortcut_service/shortcuts.xml*',
            '*/system_ce/*/shortcut_service/packages/*.xml*',
            '*/system_ce/*/shortcut_service/bitmaps/*',
        ),
        'output_types': ['html', 'tsv', 'timeline', 'lava'],
        'artifact_icon': 'link',
        'sample_data': {
            'galaxys10_a10': 'Android 10 | 68 shortcuts | 6 matched stored icons',
        },
    },
    'get_shortcut_service_discord': {
        'name': 'Shortcut Service - Discord',
        'description': 'Discord shortcut payloads, stored usernames, account IDs '
                       'and message JSON.',
        'creation_date': '2026-10-09',
        'last_update_date': '2026-10-14',
        'requirements': 'none',
        'category': 'Shortcut Service',
        'notes': 'One row per stored Discord payload. Extra fields and message JSON '
                 'are separate observations and are not substituted for one '
                 'another. Stored usernames are snapshots, not a complete alias '
                 'history. Shortcut Updated is a shortcut field-change time in Unix '
                 'milliseconds; timeline entries use it, not Message Time. Message '
                 'timestamps are converted only when an explicit timezone is '
                 'stored; original timestamps remain available. Missing Guild ID '
                 'and edit time values remain blank. Duplicate payload keys retain '
                 'every pair and report a conflict; named columns use the first '
                 'occurrence. An odd trailing array item remains in Shortcuts '
                 'Intents or Extras JSON. Identical backup and fallback copies do '
                 'not repeat payload rows; differing copies and copies without a '
                 'main file remain attributed to their source. On Magnet Virtual '
                 'Summit CTF 2024 Pixel 3a XL, Message Edited (UTC), Message Edited '
                 '(as stored), Guild ID (extra) and Guild ID (JSON) were empty in '
                 'the single observed payload; this is a dataset-specific result, '
                 'not a statement about other Discord extractions.',
        'paths': (
            '*/system_ce/*/shortcut_service/shortcuts.xml*',
            '*/system_ce/*/shortcut_service/packages/*.xml*',
        ),
        'output_types': ['html', 'tsv', 'timeline', 'lava'],
        'artifact_icon': 'message',
        'sample_data': {
            'galaxys10_a10': 'Android 10 | 0 Discord payloads',
        },
    },
    'get_shortcut_service_files': {
        'name': 'Shortcut Service - Files',
        'description': 'Shortcut files, backup comparisons and dump inventory with '
                       'formats, counts, hashes and status.',
        'creation_date': '2026-10-09',
        'last_update_date': '2026-10-14',
        'requirements': 'none',
        'category': 'Shortcut Service',
        'notes': 'One row per XML, ABX or dump file, including identical copies, '
                 'empty documents and read or parse failures. XML declaration only '
                 'means a valid declaration without a root element. Copy Comparison '
                 'first compares SHA-256, then parsed XML content without '
                 'formatting-only whitespace or attribute-order differences. Copies '
                 'are compared only with their main file in the same storage '
                 'directory. Different users and extraction trees are never '
                 'collapsed. Shortcut Count counts entries stored in the file; '
                 'Reported Shortcut Count is zero for identical copies and dump '
                 'files. Dump files retain their source, size, SHA-256, format and '
                 'parse status without placing the complete payload in a table '
                 'cell. For dumps, Android User identifies the storage directory, '
                 'not an independently established originating profile. A file with '
                 'no shortcuts does not establish that its app was unused or '
                 'uninstalled. Validation on DFRWS 2021 Galaxy S10, Magnet User '
                 'Summit CTF 2023 Pixel 3a XL and Magnet Virtual Summit CTF 2024 '
                 'Pixel 3a XL found Android User uniformly 0, Copy Comparison '
                 'uniformly Not a copy, Main Source File empty and Error empty. '
                 'Parse Status was uniformly Parsed on DFRWS 2021 Galaxy S10 and '
                 'Magnet User Summit CTF 2023 Pixel 3a XL; Magnet Virtual Summit '
                 'CTF 2024 Pixel 3a XL also contained an Empty ABX document. These '
                 'results apply only to the named images.',
        'paths': (
            '*/system_ce/*/shortcut_service/shortcuts.xml*',
            '*/system_ce/*/shortcut_service/packages/*.xml*',
            '*/system_ce/*/shortcut_service/shortcut_dump/*',
        ),
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'file',
        'sample_data': {
            'galaxys10_a10': 'Android 10 | 1 XML file | 68 stored shortcuts',
        },
    },
}


_COPY_SUFFIXES = ('.bak', '.backup', '.reservecopy', '.fallback')
_FLAGS = {
    1 << 0: 'dynamic',
    1 << 1: 'pinned',
    1 << 2: 'has_icon_res',
    1 << 3: 'has_icon_file',
    1 << 4: 'key_fields_only',
    1 << 5: 'manifest',
    1 << 6: 'disabled',
    1 << 7: 'strings_resolved',
    1 << 8: 'immutable',
    1 << 9: 'adaptive_bitmap',
    1 << 10: 'returned_by_service',
    1 << 11: 'icon_file_pending_save',
    1 << 12: 'shadow',
    1 << 13: 'long_lived',
    1 << 14: 'cached_notifications',
    1 << 15: 'has_icon_uri',
    1 << 29: 'cached_people_tile',
    1 << 30: 'cached_bubbles',
}
_DISABLED_REASONS = {
    0: 'not_disabled',
    1: 'by_app',
    2: 'app_changed',
    3: 'unknown',
    100: 'version_lower',
    101: 'backup_not_supported',
    102: 'signature_mismatch',
    103: 'other_restore_issue',
}


def _number(value):
    try:
        text = str(value).strip()
        return int(text, 16 if text.lower().startswith(('0x', '-0x', '+0x')) else 10)
    except (TypeError, ValueError):
        return None


def _flags(value):
    if value in ('', None):
        return ''
    number = _number(value)
    if number is None or number < -(1 << 31):
        return 'Unrecognized value'
    if number < 0:
        number &= 0xffffffff
    labels = [label for bit, label in _FLAGS.items() if number & bit]
    unknown = number & ~sum(_FLAGS)
    if unknown:
        labels.append(f'unknown_bits(0x{unknown:x})')
    return '; '.join(labels) if labels else 'none'


def _disabled_reason(value):
    if value in ('', None):
        return ''
    number = _number(value)
    return _DISABLED_REASONS.get(number, f'unknown({value})')


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


def _storage(source):
    normalized = source.replace('\\', '/')
    match = re.search(r'(?:^|/)system_ce/(\d+)/shortcut_service/(.*)$', normalized)
    return (normalized[:match.start(2)], match.group(1), match.group(2)) if match else None


def _source_kind(source):
    storage = _storage(source)
    if storage and storage[2].startswith('shortcut_dump/'):
        return 'Dump file'
    if source.endswith('.fallback'):
        return 'Vendor fallback'
    return 'XML backup file' if source.endswith(_COPY_SUFFIXES) else 'Shortcut XML'


def _input_files(context):
    for found in sorted(set(str(path) for path in context.get_files_found())):
        path = Path(found)
        if path.is_file():
            yield path


def _files(context):
    suffixes = ('.xml',) + tuple('.xml' + suffix for suffix in _COPY_SUFFIXES)
    for path in _input_files(context):
        storage = _storage(context.get_relative_path(str(path)))
        if storage and (storage[2].startswith('shortcut_dump/') or
                        (not storage[2].startswith('bitmaps/') and path.name.endswith(suffixes))):
            yield path


def _error(exc, document):
    message = str(exc)
    path, source = str(document['path']), document['source']
    message = message.replace(repr(path), repr(source)).replace(path, source)
    return f'{type(exc).__name__}: {message}'


def _fingerprint(path):
    digest = hashlib.sha256()
    size, prefix, is_text = 0, b'', True
    decoder = codecs.getincrementaldecoder('utf-8')()
    with path.open('rb') as stream:
        while chunk := stream.read(65536):
            if not prefix:
                prefix = chunk[:256]
            size += len(chunk)
            digest.update(chunk)
            if is_text:
                try:
                    decoder.decode(chunk, final=False)
                    is_text = b'\x00' not in chunk
                except UnicodeDecodeError:
                    is_text = False
    if is_text:
        try:
            decoder.decode(b'', final=True)
        except UnicodeDecodeError:
            is_text = False
    return prefix, size, digest.hexdigest(), is_text


def _declaration_only(prefix, size):
    if size != len(prefix):
        return False
    try:
        encoding = 'utf-16' if prefix.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig'
        text = prefix.decode(encoding).strip()
        if not re.fullmatch(r'<\?xml\s+.*?\?>', text, re.DOTALL):
            return False
        ET.fromstring(text + '<empty/>')
        return True
    except (UnicodeError, ET.ParseError, ValueError):
        return False


def _semantic_node(element):
    text = element.text or ''
    tail = element.tail or ''
    return (element.tag, tuple(sorted(element.attrib.items())),
            text if text.strip() or not len(element) else '', tail if tail.strip() else '',
            tuple(_semantic_node(child) for child in element))


def _documents(context):
    documents = []
    for path in _files(context):
        source = context.get_relative_path(str(path)).replace('\\', '/')
        kind = _source_kind(source)
        document = {
            'path': path, 'source': source, 'user': _user(source), 'root': None,
            'kind': kind, 'format': '', 'status': '', 'error': '', 'size': '', 'sha256': '',
            'main_source': '', 'comparison': 'Not a copy', 'include_rows': kind != 'Dump file',
        }
        try:
            prefix, size, digest, is_text = _fingerprint(path)
            document.update(size=size, sha256=digest)
            xml_prefix = prefix.lstrip(b'\xef\xbb\xbf \t\r\n').startswith(b'<')
            if kind == 'Dump file' and not (prefix.startswith(b'ABX\x00') or xml_prefix
                                             or path.name.endswith('.xml')):
                document['format'] = 'Text' if is_text else 'Binary'
                document['status'] = 'Text dump' if is_text else 'Binary dump'
                if not prefix:
                    document['status'] = 'Empty file'
            else:
                document['format'] = 'ABX' if prefix.startswith(b'ABX\x00') else 'XML'
                if not prefix:
                    document['status'] = 'Empty file'
                elif prefix in (b'ABX\x00\x10\x11', b'ABX\x00\x11') and size == len(prefix):
                    document['status'] = 'Empty ABX document'
                elif _declaration_only(prefix, size):
                    document['status'] = 'XML declaration only'
                else:
                    tree = abxread(str(path), False) if document['format'] == 'ABX' else ET.parse(path)
                    document['root'] = tree.getroot()
                    document['status'] = 'Parsed'
        except Exception as exc:  # pylint: disable=broad-exception-caught
            document['status'] = 'Parse error' if document['sha256'] else 'Read error'
            document['error'] = _error(exc, document)
            logfunc(f'Shortcut Service: {source}: {document["error"]}')
        documents.append(document)
    by_path = {str(document['path']): document for document in documents}
    for document in documents:
        if document['kind'] not in ('XML backup file', 'Vendor fallback'):
            continue
        path = document['path']
        suffix = next(suffix for suffix in _COPY_SUFFIXES if path.name.endswith(suffix))
        main = by_path.get(str(path.with_name(path.name[:-len(suffix)])))
        if main is None:
            document['comparison'] = 'Main file absent'
            continue
        document['main_source'] = main['source']
        if not document['sha256'] or not main['sha256']:
            document['comparison'] = 'Comparison unavailable'
            continue
        equal = document['sha256'] == main['sha256']
        if not equal and document['root'] is not None and main['root'] is not None:
            try:
                equal = _semantic_node(document['root']) == _semantic_node(main['root'])
            except RecursionError:
                document['comparison'] = 'Comparison unavailable'
                continue
        document['comparison'] = 'Identical to main' if equal else 'Differs from main'
        document['include_rows'] = not equal
    return documents


def _bitmap_index(context):
    index = {}
    for path in _input_files(context):
        source = context.get_relative_path(str(path)).replace('\\', '/')
        storage = _storage(source)
        if storage and storage[2].startswith('bitmaps/') and not path.is_symlink():
            index.setdefault((storage[0], storage[2]), []).append((path, source))
    return index


def _shortcut_image(document, package, stored_path, index):
    if not stored_path:
        return '', 'No bitmap path', ''
    if _source_kind(document['source']) == 'Dump file':
        return '', 'Dump profile not established', ''
    normalized = stored_path.replace('\\', '/')
    if '..' in normalized.split('/') or '\x00' in normalized:
        return '', 'Invalid bitmap path', ''
    storage = _storage(normalized)
    if storage:
        if storage[1] != document['user']:
            return '', 'Android user mismatch', ''
        relative = storage[2]
    elif normalized.startswith('bitmaps/'):
        relative = normalized
    else:
        return '', 'Unsupported bitmap path', ''
    if not package or not relative.startswith(f'bitmaps/{package}/'):
        return '', 'Package mismatch', ''
    candidates = index.get((_storage(document['source'])[0], relative), [])
    if not candidates:
        return '', 'Bitmap file missing', ''
    if len(candidates) != 1:
        return '', 'Ambiguous bitmap path', ''
    path, source = candidates[0]
    try:
        with Image.open(path) as image:
            image_format = image.format
            image.verify()
        image_types = {'PNG': ('image/png', 'png'), 'JPEG': ('image/jpeg', 'jpg'),
                       'WEBP': ('image/webp', 'webp'), 'GIF': ('image/gif', 'gif'),
                       'BMP': ('image/bmp', 'bmp')}
        if image_format not in image_types:
            return source, 'Unsupported image format', ''
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError) as exc:
        logfunc(f'Shortcut Service: {source}: {type(exc).__name__}')
        return source, 'Invalid or unreadable image', ''
    mime, extension = image_types[image_format]
    try:
        reference = check_in_media(str(path), path.name, force_type=mime, force_extension=extension)
    except OSError as exc:
        logfunc(f'Shortcut Service: {source}: {type(exc).__name__}')
        return source, 'Media registration unavailable', ''
    return source, 'Matched' if reference else 'Media registration unavailable', reference or ''


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
        warnings.append('Odd array length; trailing item retained in Shortcuts Intents or Extras JSON')
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
        'Long Label', 'Activity', 'Locus ID', 'Rank (as stored)', 'Flags (as stored)', 'Flags (decoded)',
        'Disabled Reason (as stored)', 'Disabled Reason (decoded)', 'Persons (JSON)', 'Categories (JSON)',
        'Intents (JSON)', 'Extras (JSON)', 'Attributes (JSON)', 'XML Path',
        'File Format', 'Source Kind', 'Bitmap Path (as stored)', 'Bitmap Source File',
        'Bitmap Status', ('Shortcut Image', 'media', 'max-width:80px;max-height:80px'), 'Source File',
    )
    rows, sources = [], []
    bitmaps = _bitmap_index(context)
    for document in _documents(context):
        root = document['root']
        if root is None or not document['include_rows']:
            continue
        sources.append(document['source'])
        for element, path, package, shortcut_id, index in _walk(root):
            if _tag(element) != 'shortcut':
                continue
            attrs = element.attrib
            bitmap_path = attrs.get('bitmap-path', '')
            bitmap_source, bitmap_status, image = _shortcut_image(
                document, package, bitmap_path, bitmaps)
            rows.append((
                _ms(attrs.get('timestamp')), attrs.get('timestamp', ''), document['user'],
                package, shortcut_id, index, attrs.get('title', ''), attrs.get('text', ''),
                attrs.get('activity', ''), attrs.get('locus-id', ''), attrs.get('rank', ''),
                attrs.get('flags', ''), _flags(attrs.get('flags')),
                attrs.get('disabled-reason', ''), _disabled_reason(attrs.get('disabled-reason')),
                _json([_node(child) for child in _children(element, 'person')]),
                _json([_node(child) for child in _children(element, 'categories')]),
                _json([_node(child) for child in _children(element, 'intent')]),
                _json([_node(child) for child in element if _tag(child) in ('extras', 'intent-extras')]),
                _json(dict(attrs)), path, document['format'], _source_kind(document['source']),
                bitmap_path, bitmap_source, bitmap_status, image, document['source'],
            ))
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
        if root is None or not document['include_rows']:
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
        'Android User', 'Source Kind', 'File Format', 'Root Element', 'Packages (JSON)',
        'Package Count', 'Shortcut Count', 'Reported Shortcut Count', 'Size (bytes)',
        'SHA-256', 'Copy Comparison', 'Main Source File', 'Parse Status', 'Error', 'Source File',
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
        sources.append(document['source'])
        rows.append((
            document['user'], document['kind'], document['format'],
            _tag(root) if root is not None else '', _json(packages), len(packages), shortcuts,
            shortcuts if document['include_rows'] else 0, document['size'], document['sha256'],
            document['comparison'], document['main_source'], document['status'],
            document['error'], document['source'],
        ))
    return headers, rows, '\n'.join(sources)
