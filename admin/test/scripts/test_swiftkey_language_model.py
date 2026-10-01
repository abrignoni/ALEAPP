"""SwiftKey language model reader, checked against a model whose contents are known.

Case 2 of this module's test data is a synthetic model: the SwiftKey 9.10.49.20 engine
built it from the word list below, and @crox4n6 supplied both in ALEAPP pull request 1484.
Nothing in it came from a device. The expected counts here are worked out from the word
list, not from the reader.
"""
from collections import Counter
import fnmatch
import os
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts import swiftkeyLanguageModel as module  # pylint: disable=wrong-import-position
from scripts.context import Context  # pylint: disable=wrong-import-position

CASE_ZIP = (REPO_ROOT / 'admin/test/cases/data/swiftkeyLanguageModel'
            / 'testdata.swiftkeyLanguageModel.swiftkey_lm_terms.case2.zip')
SWIFTKEY_MEMBER = 'data/data/com.touchtype.swiftkey/files/language_models/user/dynamic.lm'
SAMSUNG_FOLDER = 'data/data/com.samsung.android.honeyboard/app_SwiftKey/user'

# The word list the engine was trained on, one typed sequence per entry.
WORD_LIST = [
    ['synthetikwolke', 'pruefwortalpha', 'synthetikwolke'],
    ['synthetikwolke', 'pruefwortalpha', 'synthetikwolke'],
    ['synthetikwolke', 'pruefwortalpha', 'synthetikwolke'],
    ['überprüfung', 'Straße', '🔬testwort'],
    ['überprüfung', 'Straße', '🔬testwort'],
    ['praefixalpha', 'praefixbeta', 'praefixalpha'],
    ['日本語', 'café', 'test123!'],
    ['<probe>', '=SUM(A1)', '@kunstwort'],
    ['eins', 'zwei', 'drei', 'vier'],
]


def synthetic_model():
    with zipfile.ZipFile(CASE_ZIP) as archive:
        return archive.read(SWIFTKEY_MEMBER)


def expected_counts():
    counts = Counter()
    for sequence in WORD_LIST:
        for order in range(1, 4):
            for start in range(len(sequence) - order + 1):
                counts[tuple(sequence[start:start + order])] += 1
    return dict(counts)


def build_model(terms, nodes, app_lists=(), written=1700000000, trained=(1600000000, 1650000000)):
    """A model file written from the layout, independently of the reader.

    nodes and each app list are trees: [(term index, count, [children])].
    """
    def varint(value):
        out = bytearray()
        while True:
            out.append((value & 0x7f) | (0x80 if value > 0x7f else 0))
            value >>= 7
            if not value:
                return bytes(out)

    def mask(index, raw):
        base = (index ^ 0xff) + len(raw)
        return bytes(byte ^ ((place * index * 0xad ^ base) & 0xff) for place, byte in enumerate(raw))

    def tree(entries, top=True):
        out = b''
        count = 0
        for index, number, children in entries:
            inner, inner_count = tree(children, top=False)
            out += struct.pack('<HI', index, number) + inner
            count += 1 + inner_count
        if not top:
            out += b'\x00\x00'
        return out, count

    header = b'\x0a\x04test\x18' + varint(written) + b'\x20\x01'
    raw_terms = [b''] + [term.encode('utf-8') for term in terms]
    text = b''.join(mask(index, raw) for index, raw in enumerate(raw_terms))
    vocabulary = (b'fluevoca' + struct.pack('<II', 0, 2) + b'\x08\x07' + b'voca'
                  + struct.pack('<I', len(text)) + text
                  + struct.pack('<I', len(raw_terms)) + bytes(len(raw) for raw in raw_terms)
                  + b'\xff' * 32 + b'\x00' * 8)
    map_header = b'\x10' + varint(trained[0]) + b'\x18' + varint(trained[1])
    body, count = tree(nodes)
    sequences = (b'vocadmap' + struct.pack('<II', 0, len(map_header)) + map_header + b'dmap'
                 + struct.pack('<I', count) + body + struct.pack('<I', len(app_lists)))
    for name, entries in app_lists:
        app_body, app_count = tree(entries)
        stored_name = name.encode('utf-8') + b'\x00'
        sequences += (struct.pack('<I', len(stored_name)) + stored_name
                      + struct.pack('<III', 1, 0, app_count) + app_body)
    rest = struct.pack('<I', len(header)) + header + vocabulary + sequences + b'dmapflue'
    return b'flue' + struct.pack('<I', len(rest)) + rest


class ReaderTests(unittest.TestCase):
    def test_synthetic_model_reads_back_as_the_word_list(self):
        model = module.read_language_model(synthetic_model())
        terms = model['terms']
        observed = {tuple(terms[index] for index in indexes): count
                    for indexes, count in model['nodes']}
        self.assertEqual(observed, expected_counts())
        self.assertEqual(len(terms) - 1, 17)
        self.assertEqual(len(model['nodes']), 37)
        self.assertEqual(model['app_models'], [])
        self.assertEqual((model['written'], model['first_trained'], model['last_trained']),
                         (1790832183, 1790832183, 1790832183))

    def test_unmask_matches_bytes_copied_from_the_synthetic_model(self):
        # 'drei' is the 16th term; these four bytes are its stored form in the file.
        self.assertEqual(module.unmask_term(bytes.fromhex('975136ea'), 16), b'drei')
        self.assertEqual(module.unmask_term(bytes.fromhex('7fd8387fd00876de0f6ea10f7ba0'), 1),
                         b'synthetikwolke')

    def test_built_model_with_app_lists_and_deep_sequences(self):
        terms = ['alpha', 'beta', 'gamma delta', 'épsilon']
        nodes = [(1, 9, [(2, 4, [(3, 2, [(4, 1, [])])])]), (2, 5, []), (3, 2, []), (4, 1, [])]
        data = build_model(terms, nodes, app_lists=[('com.example.app', [(2, 3, []), (4, 1, [])])])
        model = module.read_language_model(data)
        self.assertEqual(model['terms'], [''] + terms)
        self.assertEqual(model['nodes'], [((1,), 9), ((1, 2), 4), ((1, 2, 3), 2), ((1, 2, 3, 4), 1),
                                          ((2,), 5), ((3,), 2), ((4,), 1)])
        self.assertEqual(model['app_models'], [('com.example.app', [((2,), 3), ((4,), 1)])])
        self.assertEqual((model['written'], model['first_trained'], model['last_trained']),
                         (1700000000, 1600000000, 1650000000))

    def test_damaged_files_are_refused(self):
        good = synthetic_model()
        damaged = {
            'signature': b'xxxx' + good[4:],
            'truncated': good[:len(good) // 2],
            'one byte short': good[:-1],
            'closing tags': good[:-8] + b'dmapxxxx',
            'trailing bytes': good[:4] + struct.pack('<I', len(good) - 8 + 4) + good[8:-8]
                              + b'\x00' * 4 + good[-8:],
        }
        for name, data in damaged.items():
            with self.subTest(name):
                with self.assertRaises(module.LanguageModelError):
                    module.read_language_model(data)

    def test_term_index_outside_the_vocabulary_is_refused(self):
        data = build_model(['alpha'], [(1, 1, []), (7, 1, [])])
        with self.assertRaises(module.LanguageModelError):
            module.read_language_model(data)


class PathTests(unittest.TestCase):
    def test_patterns_are_anchored_on_the_two_keyboards(self):
        patterns = module.__artifacts_v2__['swiftkey_lm_terms']['paths']

        def matched(path):
            return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)

        self.assertTrue(matched('x/' + SAMSUNG_FOLDER + '/dynamic.lm'))
        self.assertTrue(matched('x/' + SAMSUNG_FOLDER + '/backup/dynamic.lm'))
        self.assertTrue(matched('x/' + SAMSUNG_FOLDER + '/specific/specific_a/specific_a'))
        self.assertTrue(matched('x/data/user/10/com.samsung.android.honeyboard/app_SwiftKey/user/dynamic.lm'))
        self.assertTrue(matched('x/' + SWIFTKEY_MEMBER))
        self.assertFalse(matched('x/data/data/com.example.decoy/app_SwiftKey/user/dynamic.lm'))
        self.assertFalse(matched('x/data/data/com.touchtype.swiftkey.beta/files/language_models/user/dynamic.lm'))
        for key, artifact in module.__artifacts_v2__.items():
            self.assertEqual(artifact['paths'], patterns, key)


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='swiftkey_lm_test_')
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)
        Context.clear()
        Context.set_data_folder(str(self.root))
        Context.set_report_folder(str(self.root / 'report'))
        self.addCleanup(Context.set_data_folder, None)
        self.addCleanup(Context.clear)
        quiet = patch.object(module, 'logfunc')
        self.logged = quiet.start()
        self.addCleanup(quiet.stop)

    def stage(self, relative, data):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return str(path)

    def run_artifact(self, function, files):
        Context.set_files_found(files)
        return function.__wrapped__(Context)

    def test_rows_and_source_paths(self):
        live = build_model(['alpha', 'beta'], [(1, 3, [(2, 2, [])]), (2, 2, [])],
                           app_lists=[('com.example.app', [(1, 1, [])])])
        files = [self.stage(SAMSUNG_FOLDER + '/dynamic.lm', live)]
        relative = SAMSUNG_FOLDER + '/dynamic.lm'

        headers, rows, source = self.run_artifact(module.swiftkey_lm_terms, files)
        self.assertEqual(rows, [('alpha', 3, 1, relative), ('beta', 2, 2, relative)])
        self.assertEqual(len(headers), 4)
        self.assertEqual(source, files[0])

        _headers, rows, _source = self.run_artifact(module.swiftkey_lm_sequences, files)
        self.assertEqual(rows, [('alpha beta', 2, 2, '["alpha", "beta"]', relative)])

        _headers, rows, _source = self.run_artifact(module.swiftkey_lm_app_terms, files)
        self.assertEqual(rows, [('com.example.app', 'alpha', 1, relative)])

        headers, rows, _source = self.run_artifact(module.swiftkey_lm_models, files)
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(rows[0]), len(headers))
        self.assertEqual(rows[0][3:], (2, 1, 2, 1, '', relative))
        for cell in rows[0][:3]:
            self.assertNotEqual(cell, '')

    def test_same_backup_is_not_repeated_and_a_different_one_is(self):
        live = build_model(['alpha'], [(1, 3, [])])
        other = build_model(['alpha', 'beta'], [(1, 3, []), (2, 1, [])])
        same = [self.stage(SAMSUNG_FOLDER + '/dynamic.lm', live),
                self.stage(SAMSUNG_FOLDER + '/backup/dynamic.lm', live)]
        _headers, rows, _source = self.run_artifact(module.swiftkey_lm_terms, same)
        self.assertEqual(len(rows), 1)
        _headers, rows, _source = self.run_artifact(module.swiftkey_lm_models, same)
        self.assertEqual([row[7] for row in rows], ['Yes', ''])

        differ = [same[0], self.stage(SAMSUNG_FOLDER + '/backup/dynamic.lm', other)]
        _headers, rows, _source = self.run_artifact(module.swiftkey_lm_terms, differ)
        self.assertEqual(len(rows), 3)
        self.assertEqual({row[3] for row in rows},
                         {SAMSUNG_FOLDER + '/dynamic.lm', SAMSUNG_FOLDER + '/backup/dynamic.lm'})
        _headers, rows, _source = self.run_artifact(module.swiftkey_lm_models, differ)
        self.assertEqual([row[7] for row in rows], ['No', ''])

    def test_other_files_folders_and_damaged_models(self):
        good = build_model(['alpha'], [(1, 3, [])])
        folder = self.root / SAMSUNG_FOLDER / 'specific' / 'specific_a'
        folder.mkdir(parents=True)
        files = [str(folder),
                 self.stage(SAMSUNG_FOLDER + '/specific/specific_a/.config', b'{"models": []}'),
                 self.stage(SAMSUNG_FOLDER + '/specific/specific_a/specific_a', good[:-1]),
                 self.stage(SAMSUNG_FOLDER + '/dynamic.lm', good)]
        _headers, rows, source = self.run_artifact(module.swiftkey_lm_terms, files)
        self.assertEqual(rows, [('alpha', 3, 1, SAMSUNG_FOLDER + '/dynamic.lm')])
        self.assertEqual(source, files[3])
        logged = ' '.join(str(call.args[0]) for call in self.logged.call_args_list)
        self.assertIn('specific_a/specific_a', logged)
        self.assertNotIn(str(self.root), logged)

    def test_no_model_among_the_files_found(self):
        files = [self.stage(SAMSUNG_FOLDER + '/specific/specific_a/.config', b'{"models": []}')]
        for function in (module.swiftkey_lm_models, module.swiftkey_lm_terms,
                         module.swiftkey_lm_sequences, module.swiftkey_lm_app_terms):
            headers, rows, source = self.run_artifact(function, files)
            self.assertTrue(headers)
            self.assertEqual(rows, [])
            self.assertEqual(source, '')

    def test_a_second_android_user_adds_its_own_rows(self):
        first = build_model(['alpha'], [(1, 3, [])])
        second = build_model(['beta', 'gamma'], [(1, 1, []), (2, 1, [])])
        files = [self.stage(SAMSUNG_FOLDER + '/dynamic.lm', first),
                 self.stage('data/user/0/com.samsung.android.honeyboard/app_SwiftKey/user/dynamic.lm', first),
                 self.stage('data/user/10/com.samsung.android.honeyboard/app_SwiftKey/user/dynamic.lm', second)]
        _headers, rows, _source = self.run_artifact(module.swiftkey_lm_terms, files)
        self.assertEqual(sorted(row[0] for row in rows), ['alpha', 'beta', 'gamma'])
        self.assertEqual(os.path.commonpath([row[3] for row in rows if row[0] != 'alpha']),
                         'data/user/10/com.samsung.android.honeyboard/app_SwiftKey/user/dynamic.lm')


if __name__ == '__main__':
    unittest.main()
