"""Read SwiftKey dynamic.lm with an explicitly configured external JNI backend.

Validated with synthetic models made by SwiftKey 9.10.49.20 / Fluency 5.5.0.160.
The backend is optional: importing this module never starts Java or downloads files.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile
import unicodedata

BACKEND_ENV = 'ALEAPP_SWIFTKEY_BACKEND'
ENGINE_SHA256 = 'b90e8ff3d9ffe9f44c1be77fdd98567c83dc5325d4deaa87c246e442340a2fc1'
ENGINE_VERSION = '5.5.0.160'
ENGINE_SOURCE_VERSION = '9aa76e7616431c8db0c1c29e008140f532977cd2'
MAX_INPUT_BYTES = 128 * 1024 * 1024
MAX_EXPORT_BYTES = 256 * 1024 * 1024


class SwiftKeyLMError(ValueError):
    """The optional backend or the model could not be validated."""


def sha256_file(path):
    """Hash a file without loading it into memory."""
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def backend_directory(value=None):
    """Only use an examiner-selected backend; never search the evidence tree."""
    value = value or os.environ.get(BACKEND_ENV)
    if not value:
        raise SwiftKeyLMError(
            f'SwiftKey native backend not configured. Set {BACKEND_ENV} to the '
            'external backend directory; see admin/docs/swiftkey_dynamic_lm.md.')
    root = Path(value).expanduser().resolve()
    library = root / 'engine' / 'libfluency-java-internal.so'
    adapter = root / 'classes' / 'SwiftKeyNative.class'
    if not library.is_file() or not adapter.is_file() or not (root / 'deps').is_dir():
        raise SwiftKeyLMError('SwiftKey backend must contain engine/, classes/ and deps/.')
    if sha256_file(library) != ENGINE_SHA256:
        raise SwiftKeyLMError('SwiftKey engine SHA-256 does not match the validated 9.10.49.20 engine.')
    return root


def find_java(root):
    """Use a bundled runtime, JAVA_HOME, then PATH; require Java 17 or newer."""
    executable = 'java.exe' if os.name == 'nt' else 'java'
    candidates = [root / 'runtime' / 'bin' / executable]
    if os.environ.get('JAVA_HOME'):
        candidates.append(Path(os.environ['JAVA_HOME']) / 'bin' / executable)
    on_path = shutil.which('java')
    if on_path:
        candidates.append(Path(on_path))
    flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    for candidate in candidates:
        if not candidate.is_file():
            continue
        try:
            version = subprocess.run([str(candidate), '-version'], capture_output=True, check=False,
                                     text=True, timeout=15, creationflags=flags)
        except (OSError, subprocess.TimeoutExpired):
            continue
        match = re.search(r'version "(?:1\.)?(\d+)', version.stderr + version.stdout)
        if version.returncode == 0 and match and int(match.group(1)) >= 17:
            return str(candidate)
    raise SwiftKeyLMError('SwiftKey native backend requires Java 17 or newer.')


def _integer(value, field):
    if type(value) is not int:  # bool is not an integer in this export contract
        raise SwiftKeyLMError(f'Invalid integer in {field}.')
    return value


def _list(value, field):
    if not isinstance(value, list):
        raise SwiftKeyLMError(f'Invalid array in {field}.')
    return value


def _pair(value, field):
    if not isinstance(value, list) or len(value) != 2:
        raise SwiftKeyLMError(f'Invalid offset/size pair in {field}.')
    return [_integer(item, field) for item in value]


def _utc(value):
    if value <= 0:
        return None
    try:
        return datetime.fromtimestamp(value, timezone.utc)
    except (ValueError, OverflowError, OSError):
        return None


def decode_export(raw):
    """Decode UTF-16 code-unit slices and the native depth-first N-gram tree.

    A node is (count, term_id, pop_count). Pops apply BEFORE appending the ID.
    IDs in the resulting stack are in term order, including repeated terms.
    No language tokenizer, normalization or message reconstruction is applied.
    """
    try:
        model = raw['model']
        if not isinstance(model, dict) or not isinstance(model['word_data'], str):
            raise SwiftKeyLMError('Invalid native model text buffer.')
        text_data = model['word_data'].encode('utf-16-le')
        words = _list(model['words'], 'words')
        encoding_sets = _list(model['encoding_sets'], 'encoding_sets')
        encodings = _list(model['encodings'], 'encodings')
        nodes = _list(model['ngram_nodes'], 'ngram_nodes')
        if len(words) != len(encoding_sets):
            raise SwiftKeyLMError('Word and encoding-set sizes differ.')

        def text_slice(pair):
            start, size = _pair(pair, 'text slice')
            if start < 0 or size < 0 or 2 * (start + size) > len(text_data):
                raise SwiftKeyLMError('Text slice is outside the UTF-16 buffer.')
            return text_data[2 * start:2 * (start + size)].decode('utf-16-le')

        terms = []
        for term_id, word in enumerate(words):
            start, size = _pair(encoding_sets[term_id], 'encoding_sets')
            if start < 0 or size < 0 or start + size > len(encodings):
                raise SwiftKeyLMError('Encoding set is outside the encoding array.')
            text = text_slice(word)
            terms.append({'id': term_id, 'text': text, 'model_count': None,
                          'encodings': [text_slice(item) for item in encodings[start:start + size]],
                          'contains_control_characters': any(
                              unicodedata.category(char) == 'Cc' for char in text)})
        stack = []
        ngrams = []
        for index, node in enumerate(nodes):
            if not isinstance(node, list) or len(node) != 3:
                raise SwiftKeyLMError('Invalid native N-gram node.')
            count, term_id, pops = [_integer(item, 'ngram_nodes') for item in node]
            if count < 0 or pops < 0 or pops > len(stack) or not 0 <= term_id < len(terms):
                raise SwiftKeyLMError('Invalid count, ID or pop count in native N-gram tree.')
            if pops:
                del stack[-pops:]
            stack.append(term_id)
            if len(stack) > 64:
                raise SwiftKeyLMError('Native N-gram tree exceeds the supported depth.')
            sequence = [terms[item]['text'] for item in stack]
            ngrams.append({'node_index': index, 'term_ids': stack.copy(), 'terms': sequence,
                           'text': ' '.join(sequence), 'order': len(stack), 'model_count': count})
            if len(stack) == 1:
                if terms[term_id]['model_count'] is not None:
                    raise SwiftKeyLMError('Duplicate unigram root in native N-gram tree.')
                terms[term_id]['model_count'] = count
        first = _integer(raw['first_trained_unix_seconds'], 'first_trained_unix_seconds')
        last = _integer(raw['last_trained_unix_seconds'], 'last_trained_unix_seconds')
        present = raw['native_ngram_export_present']
        if type(present) is not bool or (not present and (terms or nodes)):
            raise SwiftKeyLMError('Inconsistent native N-gram export presence flag.')
        times_valid = 0 < first <= last and _utc(first) is not None and _utc(last) is not None
        return {'terms': terms, 'ngrams': ngrams,
                'term_count': len(terms), 'ngram_node_count': len(ngrams),
                'max_order': max((item['order'] for item in ngrams), default=0),
                'first_trained_raw': first, 'last_trained_raw': last,
                'first_trained_utc': _utc(first) if times_valid else None,
                'last_trained_utc': _utc(last) if times_valid else None,
                'native_ngram_export_present': present}
    except (KeyError, TypeError, UnicodeError) as error:
        raise SwiftKeyLMError(f'Malformed native export: {error}') from error


def extract_model(source, backend=None, timeout=180):
    """Export a temporary snapshot, then verify the source content is unchanged.

    Runtime is offline. The native engine never receives the source file path.
    Reading the source may affect atime depending on its filesystem.
    """
    source = Path(source)
    before = source.stat()
    if not 12 <= before.st_size <= MAX_INPUT_BYTES:
        raise SwiftKeyLMError('Model size is outside the supported 12-byte to 128-MiB range.')
    with source.open('rb') as stream:
        header = stream.read(128)
    if header[:4] != b'flue':
        raise SwiftKeyLMError('Model does not carry the validated flue file signature.')
    root = backend_directory(backend)
    java = find_java(root)
    with tempfile.TemporaryDirectory(prefix='aleapp_swiftkey_') as temporary:
        work = Path(temporary)
        snapshot = work / 'input.lm'
        # Bound the copy even if a concurrently written source grows after stat().
        with source.open('rb') as reader, snapshot.open('wb') as writer:
            remaining = MAX_INPUT_BYTES + 1
            while remaining:
                block = reader.read(min(1024 * 1024, remaining))
                if not block:
                    break
                writer.write(block)
                remaining -= len(block)
        if snapshot.stat().st_size > MAX_INPUT_BYTES:
            raise SwiftKeyLMError('Model exceeded 128 MiB while taking the snapshot.')
        digest = sha256_file(snapshot)
        if digest != sha256_file(source) or snapshot.stat().st_size != before.st_size:
            raise SwiftKeyLMError('Source changed while taking the model snapshot.')
        raw_path = work / 'native_export.json'
        classpath = os.pathsep.join([str(root / 'classes'), str(root / 'deps' / '*')])
        command = [java, '-Xmx1536m', '-Dfile.encoding=UTF-8',
                   '-Dorg.slf4j.simpleLogger.defaultLogLevel=error', '-cp', classpath,
                   'SwiftKeyNative', 'extract', str(root / 'engine' / 'libfluency-java-internal.so'),
                   str(work / 'emuroot'), str(snapshot), str(raw_path)]
        try:
            process = subprocess.run(command, capture_output=True, text=True, check=False,
                                     encoding='utf-8', errors='replace', timeout=timeout,
                                     creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        except subprocess.TimeoutExpired as error:
            raise SwiftKeyLMError(f'Native export timed out after {timeout} seconds.') from error
        except OSError as error:
            raise SwiftKeyLMError(f'Could not start native export: {error}') from error
        if process.returncode or process.stdout or not raw_path.is_file():
            detail = (process.stderr + '\n' + process.stdout).strip()[-4096:]
            raise SwiftKeyLMError(f'Native export failed (exit {process.returncode}): {detail}')
        if raw_path.stat().st_size > MAX_EXPORT_BYTES:
            raise SwiftKeyLMError('Native export exceeds the supported 256-MiB size.')
        try:
            raw = json.loads(raw_path.read_text(encoding='utf-8'))
        except (ValueError, UnicodeError) as error:
            raise SwiftKeyLMError(f'Native export is not valid JSON: {error}') from error
        if not isinstance(raw, dict) or raw.get('engine_version') != ENGINE_VERSION or \
                raw.get('engine_source_version') != ENGINE_SOURCE_VERSION:
            raise SwiftKeyLMError('Native export reports an unexpected engine version.')
        decoded = decode_export(raw)
        if digest != sha256_file(source):
            raise SwiftKeyLMError('Source content changed during native export.')
        after = source.stat()
        decoded.update({'sha256': digest, 'size_bytes': before.st_size,
                        'engine_version': raw['engine_version'],
                        'engine_source_version': raw['engine_source_version'],
                        'engine_sha256': ENGINE_SHA256,
                        'adapter_sha256': sha256_file(root / 'classes' / 'SwiftKeyNative.class'),
                        'input_content_unchanged': True,
                        'mtime_unchanged': before.st_mtime_ns == after.st_mtime_ns,
                        'outer_declared_size': struct.unpack_from('<I', header, 4)[0]})
        return decoded
