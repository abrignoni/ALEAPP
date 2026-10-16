"""SwiftKey (Fluency) dynamic language models, read without the keyboard's engine.

The Samsung Keyboard and the SwiftKey app both keep the words the keyboard has stored in
a "Fluency language model file". The reader below follows the file's own layout. The term
text is masked; the masking rule was read from libfluency-java.so, the engine library
inside the Samsung Keyboard package (see the notes on SwiftKey Language Model - Terms).
"""

__artifacts_v2__ = {
    'swiftkey_lm_models': {
        'name': 'SwiftKey Language Model - Models',
        'description': 'SwiftKey engine language model files in the Samsung Keyboard and SwiftKey app '
                       'data folders, one row per file, with the times each file records and how much it holds.',
        'author': '@AlexisBrignoni, Claude, @crox4n6',
        'creation_date': '2026-10-01',
        'last_update_date': '2026-10-01',
        'requirements': 'none',
        'category': 'SwiftKey Keyboard',
        'notes': "One row per language model file found. Reads the Samsung Keyboard's "
                 "app_SwiftKey/user/dynamic.lm, its backup/dynamic.lm copy and the files under "
                 "user/specific, and the SwiftKey app's files/language_models/user/dynamic.lm. A file is "
                 "read only when it begins with the flue signature; a file that does not follow the layout "
                 "is named in the run log and gets no row. File Written is field 3 of the file header, read "
                 "as Unix seconds in UTC: it equalled the modification time the extraction zip records for "
                 "the file on 9 of the 9 dynamic.lm files whose zip records one in UTC. First Trained and "
                 "Last Trained are fields 2 and 3 of the sequence chunk header. The names are those of the "
                 "SwiftKey app (version 9.10.36.21 on sharon_a14), whose ModelData class holds "
                 "mFirstTrainedTime and mLastTrainedTime; on a synthetic model the engine returned the value "
                 "stored in those two fields for both times, and field 2 was not later than field 3 on the "
                 "68 tested files that carry them. The 2 tested files with no terms carry neither field and "
                 "those cells are blank. What event sets either time is not established. Terms is the number "
                 "of terms stored, Term Sequences the number of stored sequences of two or more terms, and "
                 "Longest Sequence the number of terms in the longest one, 4 at most on the tested files. "
                 "App Term Lists is the number of app package names under which the file keeps separate term "
                 "counts. App Term Lists held one value, 0, on every row of 9 of the 10 tested images; only "
                 "the two dynamic.lm copies on samsunga53_a14 hold lists, 14 each. Backup Same As Live File "
                 "is Yes when a file in a backup folder holds the same bytes as the file of the same name "
                 "one folder up, No when it does not or when no such file was found, and blank for a file "
                 "that is not in a backup folder; 29 of the 35 backup copies on the tested images were the "
                 "same. Tested on 70 files from 10 Samsung images. No tested image holds a file at the "
                 "SwiftKey app path, so that path has only been read on a synthetic model made with the "
                 "SwiftKey 9.10.49.20 engine and supplied by @crox4n6.",
        'paths': ('*/com.samsung.android.honeyboard/app_SwiftKey/user/dynamic.lm',
                  '*/com.samsung.android.honeyboard/app_SwiftKey/user/backup/dynamic.lm',
                  '*/com.samsung.android.honeyboard/app_SwiftKey/user/specific/*',
                  '*/com.touchtype.swiftkey/files/language_models/user/dynamic.lm'),
        'output_types': 'standard',
        'artifact_icon': 'keyboard',
        'sample_data': {
                           'adams_ss135dl_a13': 'Android 13 | 2 rows',
                           'anne_a15': 'Android 15 | 48 rows',
                           'cookbook_a11': 'Android 11 | 4 rows',
                           'falken_a326u_a13': 'Android 13 | 2 rows',
                           'galaxys10_a10': 'Android 10 | 2 rows',
                           'pixel7a_a14': 'Android 14 | 0 rows',
                           's20fe_a13': 'Android 13 | 2 rows',
                           'samsunga53_a14': 'Android 14 | 2 rows',
                           'samsungs20_a13': 'Android 13 | 4 rows',
                           'sharon_a13': 'Android 13 | 2 rows',
                           'sharon_a14': 'Android 14 | 2 rows',
                       },
    },
    'swiftkey_lm_terms': {
        'name': 'SwiftKey Language Model - Terms',
        'description': 'Terms stored in SwiftKey engine language model files, with the count each '
                       'model keeps for the term.',
        'author': '@AlexisBrignoni, Claude, @crox4n6',
        'creation_date': '2026-10-01',
        'last_update_date': '2026-10-01',
        'requirements': 'none',
        'category': 'SwiftKey Keyboard',
        'notes': 'One row per term that has a count of its own in the model file. The term text is stored '
                 'masked. The rule was read from libfluency-java.so (version string 5.0.6.138) inside the '
                 "Samsung Keyboard package on samsunga53_a14, and the same routine is in the SwiftKey app's "
                 "libfluency-java-internal.so (5.1.0.127) on sharon_a14: each stored byte is the term's byte "
                 'XORed with the low byte of (position * index * 0xAD) XOR ((index XOR 0xFF) + length), '
                 "index being the term's place in the vocabulary. Checked against the engine: a synthetic "
                 'model built by the SwiftKey 9.10.49.20 engine from a known word list, supplied by '
                 "@crox4n6, reads back as the engine's own export of it, 17 terms and 37 counted entries, "
                 'and each count there equals the number of times the term or sequence occurs in the word '
                 'list. Count is the number the model stores for the term. On a device, what adds to it is '
                 'not established, so a row shows the keyboard stored the term and does not show who entered '
                 "it or in which app. Term Index is the term's place in the model's vocabulary. On the 12 "
                 'live dynamic.lm files of the tested images the first 74 terms are the same, and 3 of those '
                 'files hold only those 74, so a Term Index of 74 or less in a dynamic.lm does not show the '
                 'term was entered on the device. None of the 23 live files under user/specific on anne_a15 '
                 'holds any of those 74 terms. Those files are separate models in folders whose names read '
                 'as an app package name with underscores in place of its dots, or as a number; their rows '
                 'appear here with the folder in Source File. A backup file holding the same bytes as its '
                 'live file is not repeated; where the two differ both are reported and Source File tells '
                 'them apart.',
        'paths': ('*/com.samsung.android.honeyboard/app_SwiftKey/user/dynamic.lm',
                  '*/com.samsung.android.honeyboard/app_SwiftKey/user/backup/dynamic.lm',
                  '*/com.samsung.android.honeyboard/app_SwiftKey/user/specific/*',
                  '*/com.touchtype.swiftkey/files/language_models/user/dynamic.lm'),
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'keyboard',
        'sample_data': {
                           'adams_ss135dl_a13': 'Android 13 | 195 rows',
                           'anne_a15': 'Android 15 | 1365 rows',
                           'cookbook_a11': 'Android 11 | 883 rows',
                           'falken_a326u_a13': 'Android 13 | 221 rows',
                           'galaxys10_a10': 'Android 10 | 74 rows',
                           'pixel7a_a14': 'Android 14 | 0 rows',
                           's20fe_a13': 'Android 13 | 129 rows',
                           'samsunga53_a14': 'Android 14 | 245 rows',
                           'samsungs20_a13': 'Android 13 | 611 rows',
                           'sharon_a13': 'Android 13 | 306 rows',
                           'sharon_a14': 'Android 14 | 1050 rows',
                       },
    },
    'swiftkey_lm_sequences': {
        'name': 'SwiftKey Language Model - Term Sequences',
        'description': 'Sequences of two or more terms stored in SwiftKey engine language model '
                       'files, with the count each model keeps for the sequence.',
        'author': '@AlexisBrignoni, Claude, @crox4n6',
        'creation_date': '2026-10-01',
        'last_update_date': '2026-10-01',
        'requirements': 'none',
        'category': 'SwiftKey Keyboard',
        'notes': 'One row per stored sequence of two or more terms per model file. The model keeps a tree: each '
                 'entry is a term index and a count, followed by the entries that continue it, so a row is the '
                 'chain of terms from the top of the tree down to that entry. Sequence joins the terms with a '
                 'space; Terms holds the same terms as a JSON list, which keeps the boundaries when a term itself '
                 'contains a space, as 3 term rows on the tested images do. Terms In Sequence was 2, 3 or 4 on the '
                 'tested files. Count is the number stored for the sequence. On a synthetic model built by the '
                 'SwiftKey 9.10.49.20 engine from a known word list, supplied by @crox4n6, each count equals the '
                 'number of times the sequence occurs in the list; that model holds sequences of 2 and 3 terms and '
                 'none of 4. On a device, what adds to a count is not established. A row is a run of terms the '
                 'model stored in that order. It is not a message, and nothing in the file dates a sequence or '
                 'names the app it was entered in. A backup file holding the same bytes as its live file is not '
                 'repeated; where the two differ both are reported and Source File tells them apart.',
        'paths': ('*/com.samsung.android.honeyboard/app_SwiftKey/user/dynamic.lm',
                  '*/com.samsung.android.honeyboard/app_SwiftKey/user/backup/dynamic.lm',
                  '*/com.samsung.android.honeyboard/app_SwiftKey/user/specific/*',
                  '*/com.touchtype.swiftkey/files/language_models/user/dynamic.lm'),
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'keyboard',
        'sample_data': {
                           'adams_ss135dl_a13': 'Android 13 | 330 rows',
                           'anne_a15': 'Android 15 | 4311 rows',
                           'cookbook_a11': 'Android 11 | 4005 rows',
                           'falken_a326u_a13': 'Android 13 | 634 rows',
                           'galaxys10_a10': 'Android 10 | 2 rows',
                           'pixel7a_a14': 'Android 14 | 0 rows',
                           's20fe_a13': 'Android 13 | 88 rows',
                           'samsunga53_a14': 'Android 14 | 670 rows',
                           'samsungs20_a13': 'Android 13 | 1637 rows',
                           'sharon_a13': 'Android 13 | 517 rows',
                           'sharon_a14': 'Android 14 | 2578 rows',
                       },
    },
    'swiftkey_lm_app_terms': {
        'name': 'SwiftKey Language Model - Terms by App',
        'description': 'Term counts that a SwiftKey engine language model file keeps under an app '
                       'package name.',
        'author': '@AlexisBrignoni, Claude, @crox4n6',
        'creation_date': '2026-10-01',
        'last_update_date': '2026-10-01',
        'requirements': 'none',
        'category': 'SwiftKey Keyboard',
        'notes': 'One row per entry under each app package name a model file keeps separate term counts for. '
                 'An entry of more than one term would show its terms joined with a space in Term; on the '
                 'tested images each row was a single term. After its sequence tree a dynamic.lm can hold a '
                 'list of package names, each followed by its own term counts. On the tested images only the '
                 'dynamic.lm on samsunga53_a14 holds such lists: 14 package names and 227 rows, each row a '
                 'single term. App Package is the name as stored. Each list also carries two numbers this '
                 'artifact does not report: one was 1 on every list, and the meaning of neither is '
                 'established. What makes the keyboard file a term under a package name is not established; '
                 'a row shows the model holds that count under that name. The separate model files under '
                 'user/specific, 23 live files on anne_a15, sit in folders whose names read as an app '
                 'package name and are reported by the Terms and Term Sequences artifacts. A backup file '
                 'holding the same bytes as its live file is not repeated; where the two differ both are '
                 'reported and Source File tells them apart.',
        'paths': ('*/com.samsung.android.honeyboard/app_SwiftKey/user/dynamic.lm',
                  '*/com.samsung.android.honeyboard/app_SwiftKey/user/backup/dynamic.lm',
                  '*/com.samsung.android.honeyboard/app_SwiftKey/user/specific/*',
                  '*/com.touchtype.swiftkey/files/language_models/user/dynamic.lm'),
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'keyboard',
        'sample_data': {
                           'adams_ss135dl_a13': 'Android 13 | 0 rows',
                           'anne_a15': 'Android 15 | 0 rows',
                           'cookbook_a11': 'Android 11 | 0 rows',
                           'falken_a326u_a13': 'Android 13 | 0 rows',
                           'galaxys10_a10': 'Android 10 | 0 rows',
                           'pixel7a_a14': 'Android 14 | 0 rows',
                           's20fe_a13': 'Android 13 | 0 rows',
                           'samsunga53_a14': 'Android 14 | 227 rows',
                           'samsungs20_a13': 'Android 13 | 0 rows',
                           'sharon_a13': 'Android 13 | 0 rows',
                           'sharon_a14': 'Android 14 | 0 rows',
                       },
    },
}

import hashlib
import json
import os
import struct

from scripts.artifacts.storagePathViews import unique_files
from scripts.ilapfuncs import artifact_processor, convert_unix_ts_to_utc, logfunc

SIGNATURE = b'flue'
CLOSING_TAGS = b'dmapflue'


class LanguageModelError(ValueError):
    """The file does not follow the layout this reader knows."""


def _varint(data, offset):
    value = shift = 0
    while True:
        if offset >= len(data):
            raise LanguageModelError('a header number runs past its header')
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7f) << shift
        shift += 7
        if not byte & 0x80:
            return value, offset


def _header_fields(data):
    """The protobuf fields of a chunk header: {field number: number or bytes}."""
    fields = {}
    offset = 0
    while offset < len(data):
        tag, offset = _varint(data, offset)
        number, wire_type = tag >> 3, tag & 7
        if wire_type == 0:
            value, offset = _varint(data, offset)
        elif wire_type == 2:
            length, offset = _varint(data, offset)
            value = data[offset:offset + length]
            offset += length
            if offset > len(data):
                raise LanguageModelError('a header field runs past its header')
        else:
            raise LanguageModelError(f'unexpected header wire type {wire_type}')
        fields[number] = value
    return fields


def _u32(data, offset):
    if offset < 0 or offset + 4 > len(data):
        raise LanguageModelError('the file ends inside a structure')
    return struct.unpack_from('<I', data, offset)[0]


def _expect(data, offset, tag):
    if data[offset:offset + len(tag)] != tag:
        raise LanguageModelError(f'expected the {tag.decode()} tag at offset {offset}')


def unmask_term(stored, index):
    """A term's bytes as written, from its stored bytes and its place in the vocabulary.

    Each stored byte is the term's byte XORed with the low byte of
    (position * index * 0xAD) XOR ((index XOR 0xFF) + length), where index is the term's
    place in the vocabulary, kept to 16 bits.
    """
    index &= 0xffff
    base = (index ^ 0xff) + len(stored)
    return bytes(byte ^ (((position * index * 0xad) ^ base) & 0xff)
                 for position, byte in enumerate(stored))


def _read_trie(data, offset, node_count, term_count):
    """Depth-first nodes: a 16-bit term index and a 32-bit count, then the node's children.

    A 16-bit zero closes a list of children. The outermost list is not closed, so reading
    stops at the declared node count and the lists still open must then close.
    """
    nodes = []
    stack = []
    while len(nodes) < node_count:
        if offset + 2 > len(data):
            raise LanguageModelError('the file ends inside the sequence tree')
        term_index = struct.unpack_from('<H', data, offset)[0]
        offset += 2
        if term_index == 0:
            if not stack:
                raise LanguageModelError('the sequence tree closes a list it never opened')
            stack.pop()
            continue
        if term_index >= term_count:
            raise LanguageModelError('the sequence tree names a term outside the vocabulary')
        count = _u32(data, offset)
        offset += 4
        stack.append(term_index)
        nodes.append((tuple(stack), count))
    closing = 2 * len(stack)
    if data[offset:offset + closing] != b'\x00' * closing:
        raise LanguageModelError('the sequence tree is not closed after its last node')
    return nodes, offset + closing


def read_language_model(data):
    """Read a Fluency dynamic language model. Every byte before the closing tags is accounted for."""
    if data[:4] != SIGNATURE:
        raise LanguageModelError('no flue signature')
    if len(data) < 28 or _u32(data, 4) != len(data) - 8:
        raise LanguageModelError('the size the file declares does not match its length')
    if data[-8:] != CLOSING_TAGS:
        raise LanguageModelError('the file does not end with its closing tags')
    header_length = _u32(data, 8)
    header = _header_fields(data[12:12 + header_length])
    offset = 12 + header_length

    _expect(data, offset, b'fluevoca')
    vocabulary_header_length = _u32(data, offset + 12)
    offset += 16 + vocabulary_header_length
    _expect(data, offset, b'voca')
    text_length = _u32(data, offset + 4)
    text = data[offset + 8:offset + 8 + text_length]
    if len(text) != text_length:
        raise LanguageModelError('the file ends inside the vocabulary text')
    offset += 8 + text_length
    entry_count = _u32(data, offset)
    if text_length == 0 and entry_count == 0xffffffff:
        lengths = b''
    else:
        lengths = data[offset + 4:offset + 4 + entry_count]
        offset += 4 + entry_count
        if len(lengths) != entry_count or sum(lengths) != text_length:
            raise LanguageModelError('the term lengths do not add up to the vocabulary text')
    terms = []
    position = 0
    for index, length in enumerate(lengths):
        raw = unmask_term(text[position:position + length], index)
        position += length
        try:
            terms.append(raw.decode('utf-8'))
        except UnicodeDecodeError as error:
            raise LanguageModelError(f'term {index} is not UTF-8 text once unmasked') from error

    # A lookup table sits between the vocabulary and the sequence chunk; nothing here needs it.
    offset = data.find(b'vocadmap', offset)
    if offset < 0:
        raise LanguageModelError('no sequence chunk after the vocabulary')
    map_header_length = _u32(data, offset + 12)
    map_header = _header_fields(data[offset + 16:offset + 16 + map_header_length])
    offset += 16 + map_header_length
    _expect(data, offset, b'dmap')
    term_count = max(len(terms), 1)
    nodes, offset = _read_trie(data, offset + 8, _u32(data, offset + 4), term_count)

    app_models = []
    app_model_count = _u32(data, offset)
    offset += 4
    for _ in range(app_model_count):
        name_length = _u32(data, offset)
        name = data[offset + 4:offset + 4 + name_length]
        offset += 4 + name_length
        if len(name) != name_length or not name.endswith(b'\x00'):
            raise LanguageModelError('an app name in the file is not terminated')
        app_nodes, offset = _read_trie(data, offset + 12, _u32(data, offset + 8), term_count)
        app_models.append((name[:-1].decode('utf-8', 'replace'), app_nodes))
    if offset != len(data) - 8:
        raise LanguageModelError(f'{len(data) - 8 - offset} bytes before the closing tags were not read')

    def stored_time(fields, number):
        value = fields.get(number)
        return value if isinstance(value, int) else None

    return {'terms': terms, 'nodes': nodes, 'app_models': app_models,
            'written': stored_time(header, 3),
            'first_trained': stored_time(map_header, 2),
            'last_trained': stored_time(map_header, 3)}


def _timestamp(value):
    return convert_unix_ts_to_utc(value) if value else ''


def _models(context):
    """(path, relative path, model, same-as-live flag) for each language model file found.

    The flag is '' for a file that is not a backup copy, 'Yes' for a backup holding the same
    bytes as the file it backs up, and 'No' for one that differs or has no such file here.
    """
    found = {}
    for path in unique_files(context):
        if os.path.isdir(path) or not os.path.isfile(path):
            continue
        with open(path, 'rb') as stream:
            data = stream.read()
        if data[:4] != SIGNATURE:
            continue
        found[path] = data
    digests = {path: hashlib.sha256(data).digest() for path, data in found.items()}
    for path in sorted(found):
        relative = context.get_relative_path(path)
        folder, name = os.path.split(path)
        same_as_live = ''
        if os.path.basename(folder) == 'backup':
            live = os.path.join(os.path.dirname(folder), name)
            same_as_live = 'Yes' if digests.get(live) == digests[path] else 'No'
        try:
            model = read_language_model(found[path])
        except LanguageModelError as error:
            logfunc(f'SwiftKey language model not read: {relative}: {error}')
            continue
        yield path, relative, model, same_as_live


def _report_rows(models):
    """Skip a backup that holds the same bytes as its live file, so its rows are not repeated."""
    for path, relative, model, same_as_live in models:
        if same_as_live == 'Yes':
            logfunc(f'SwiftKey language model backup holds the same bytes as its live file, '
                    f'rows not repeated: {relative}')
            continue
        yield path, relative, model


@artifact_processor
def swiftkey_lm_models(context):
    data_headers = (('File Written', 'datetime'), ('First Trained', 'datetime'),
                    ('Last Trained', 'datetime'), 'Terms', 'Term Sequences',
                    'Longest Sequence', 'App Term Lists', 'Backup Same As Live File',
                    'Source File')
    data_list = []
    sources = []
    for path, relative, model, same_as_live in _models(context):
        sources.append(path)
        orders = [len(indexes) for indexes, _count in model['nodes']]
        data_list.append((_timestamp(model['written']), _timestamp(model['first_trained']),
                          _timestamp(model['last_trained']), max(len(model['terms']) - 1, 0),
                          sum(1 for order in orders if order > 1), max(orders, default=0),
                          len(model['app_models']), same_as_live, relative))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def swiftkey_lm_terms(context):
    data_headers = ('Term', 'Count', 'Term Index', 'Source File')
    data_list = []
    sources = []
    for path, relative, model in _report_rows(_models(context)):
        sources.append(path)
        terms = model['terms']
        for indexes, count in model['nodes']:
            if len(indexes) == 1:
                data_list.append((terms[indexes[0]], count, indexes[0], relative))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def swiftkey_lm_sequences(context):
    data_headers = ('Sequence', 'Count', 'Terms In Sequence', 'Terms', 'Source File')
    data_list = []
    sources = []
    for path, relative, model in _report_rows(_models(context)):
        sources.append(path)
        terms = model['terms']
        for indexes, count in model['nodes']:
            if len(indexes) > 1:
                sequence = [terms[index] for index in indexes]
                data_list.append((' '.join(sequence), count, len(sequence),
                                  json.dumps(sequence, ensure_ascii=False), relative))
    return data_headers, data_list, '\n'.join(sources)


@artifact_processor
def swiftkey_lm_app_terms(context):
    data_headers = ('App Package', 'Term', 'Count', 'Source File')
    data_list = []
    sources = []
    for path, relative, model in _report_rows(_models(context)):
        sources.append(path)
        terms = model['terms']
        for package, nodes in model['app_models']:
            for indexes, count in nodes:
                data_list.append((package, ' '.join(terms[index] for index in indexes),
                                  count, relative))
    return data_headers, data_list, '\n'.join(sources)
