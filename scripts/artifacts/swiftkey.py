"""Optional native export of the SwiftKey user language model."""

__artifacts_v2__ = {
    'swiftkey_model_words': {
        'name': 'SwiftKey - Model Words',
        'description': 'Exports terms and unigram model counts from SwiftKey dynamic.lm. '
                       'Counts are model values, not verified typing counts. '
                       'Automated validation uses synthetic SwiftKey 9.10.49.20 models.',
        'author': 'SwiftKey contributors',
        'creation_date': '2026-10-01',
        'last_update_date': '2026-10-01',
        'requirements': 'Optional external SwiftKey JNI backend; Java 17+; ALEAPP_SWIFTKEY_BACKEND',
        'category': 'SwiftKey Keyboard',
        'notes': 'Read-only snapshot export using InternalFluency.extractModelData. '
                 'No app, recipient or per-term input time is established. '
                 'The selected backend engine version is not the acquired app version. '
                 'Source SHA-256 has one value per source file and distinguishes model content. '
                 'In the synthetic fixture Encodings JSON was uniformly [] and Contains Control Characters '
                 'was uniformly False; both columns retain values from other exports. '
                 'See admin/docs/swiftkey_dynamic_lm.md. Select Model Metadata for failure status.',
        'paths': ('*/com.touchtype.swiftkey/files/language_models/user/dynamic.lm',),
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'keyboard',
        'sample_data': {'synthetic_9_10_49_20': 'SYNTHETIC engine-generated fixture; 17 terms; no device extraction'},
    },
    'swiftkey_model_ngrams': {
        'name': 'SwiftKey - Model N-grams',
        'description': 'Exports N-grams of order two or higher from SwiftKey dynamic.lm. '
                       'These are model sequences, not reconstructed messages. '
                       'Automated validation uses synthetic SwiftKey 9.10.49.20 models.',
        'author': 'SwiftKey contributors',
        'creation_date': '2026-10-01',
        'last_update_date': '2026-10-01',
        'requirements': 'Optional external SwiftKey JNI backend; Java 17+; ALEAPP_SWIFTKEY_BACKEND',
        'category': 'SwiftKey Keyboard',
        'notes': 'UTF-16 code-unit offsets and native depth-first nodes are decoded without tokenization. '
                 'Terms JSON preserves term boundaries; the joined text is for display only. '
                 'Counts are model values. No per-sequence timestamp or source app is established. '
                 'Source SHA-256 has one value per source file and distinguishes model content. '
                 'See admin/docs/swiftkey_dynamic_lm.md. Select Model Metadata for failure status.',
        'paths': ('*/com.touchtype.swiftkey/files/language_models/user/dynamic.lm',),
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'keyboard',
        'sample_data': {'synthetic_9_10_49_20': 'SYNTHETIC engine-generated fixture; 20 N-grams of order 2/3'},
    },
    'swiftkey_model_metadata': {
        'name': 'SwiftKey - Model Metadata',
        'description': 'Reports SwiftKey dynamic.lm export status, SHA-256, model sizes and native '
                       'first/last trained fields. Times describe the model, not individual terms. '
                       'Automated validation uses synthetic SwiftKey 9.10.49.20 models.',
        'author': 'SwiftKey contributors',
        'creation_date': '2026-10-01',
        'last_update_date': '2026-10-01',
        'requirements': 'Optional external SwiftKey JNI backend; Java 17+; ALEAPP_SWIFTKEY_BACKEND',
        'category': 'SwiftKey Keyboard',
        'notes': 'One row per matched file, including failures. Raw training fields are Unix seconds; '
                 'invalid/zero fields retain their raw values but have no converted timestamp. '
                 'An empty successful export is distinct from a failed export. '
                 'Error is empty for successful exports and records a reason for failed exports. '
                 'Native Engine Version identifies the backend, not the acquired SwiftKey app. '
                 'Synthetic fixtures were generated on Linux without an Android OS or real typing. '
                 'Other engine versions remain unvalidated.',
        'paths': ('*/com.touchtype.swiftkey/files/language_models/user/dynamic.lm',),
        'output_types': ['html', 'tsv', 'lava'],
        'artifact_icon': 'info-circle',
        'sample_data': {'synthetic_9_10_49_20': 'SYNTHETIC engine-generated fixture; 1 successful metadata row'},
    },
}

import json
import os

from scripts.ilapfuncs import artifact_processor, logfunc
from scripts.swiftkey_lm import SwiftKeyLMError, extract_model


def _model_files(context):
    try:
        found = context.get_files_found()
    except ValueError:
        return []
    suffix = '/com.touchtype.swiftkey/files/language_models/user/dynamic.lm'
    seen = set()
    files = []
    for item in found:
        path = os.fspath(item)
        if not os.path.normcase(path.replace('\\', '/')).endswith(os.path.normcase(suffix)):
            continue
        key = os.path.normcase(os.path.abspath(path))
        if key not in seen:
            seen.add(key)
            files.append(path)
    return sorted(files)


def _read_models(context):
    for path in _model_files(context):
        relative = context.get_relative_path(path)
        try:
            yield path, relative, extract_model(path), ''
        except (SwiftKeyLMError, OSError) as error:
            detail = str(error)
            logfunc(f'SwiftKey model export failed for {relative}: {detail}')
            yield path, relative, None, detail


@artifact_processor
def swiftkey_model_words(context):
    headers = ('Term ID', 'Term', 'Unigram Model Count', 'Encodings JSON',
               'Contains Control Characters', 'Source SHA-256', 'Source File')
    rows = []
    sources = []
    for path, relative, model, _error in _read_models(context):
        if model is None:
            continue
        sources.append(path)
        for term in model['terms']:
            rows.append((term['id'], term['text'], term['model_count'],
                         json.dumps(term['encodings'], ensure_ascii=False),
                         term['contains_control_characters'], model['sha256'], relative))
    return headers, rows, '\n'.join(sources)


@artifact_processor
def swiftkey_model_ngrams(context):
    headers = ('Node Index', 'Order', 'Model Sequence', 'Model Count', 'Term IDs JSON',
               'Terms JSON', 'Source SHA-256', 'Source File')
    rows = []
    sources = []
    for path, relative, model, _error in _read_models(context):
        if model is None:
            continue
        sources.append(path)
        for ngram in model['ngrams']:
            if ngram['order'] < 2:
                continue
            rows.append((ngram['node_index'], ngram['order'], ngram['text'], ngram['model_count'],
                         json.dumps(ngram['term_ids']), json.dumps(ngram['terms'], ensure_ascii=False),
                         model['sha256'], relative))
    return headers, rows, '\n'.join(sources)


@artifact_processor
def swiftkey_model_metadata(context):
    headers = ('Status', 'Term Count', 'N-gram Node Count', 'Maximum Order',
               ('Model First Trained (UTC)', 'datetime'), ('Model Last Trained (UTC)', 'datetime'),
               'First Trained Raw Seconds', 'Last Trained Raw Seconds', 'Native N-gram Export Present',
               'Size Bytes', 'Outer Declared Size', 'Source SHA-256', 'Source Content Unchanged',
               'Source Mtime Unchanged', 'Native Engine Version', 'Native Engine Source Version',
               'Native Engine SHA-256', 'Adapter Class SHA-256', 'Error', 'Source File')
    rows = []
    sources = []
    for path, relative, model, error in _read_models(context):
        sources.append(path)
        if model is None:
            rows.append(('error',) + (None,) * 17 + (error, relative))
            continue
        rows.append(('exported', model['term_count'], model['ngram_node_count'], model['max_order'],
                     model['first_trained_utc'], model['last_trained_utc'], model['first_trained_raw'],
                     model['last_trained_raw'], model['native_ngram_export_present'], model['size_bytes'],
                     model['outer_declared_size'], model['sha256'], model['input_content_unchanged'],
                     model['mtime_unchanged'], model['engine_version'], model['engine_source_version'],
                     model['engine_sha256'], model['adapter_sha256'], '', relative))
    return headers, rows, '\n'.join(sources)
