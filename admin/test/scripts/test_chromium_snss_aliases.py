"""Real SNSS bytes, canonical tenants and exact-byte alias selection."""
import hashlib
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from admin.test.scripts.test_snss_parser import _file, _navigation
from scripts.artifacts import chromeSessionTabs as module
from scripts.artifacts.chromeSessionTabs import _tab_files as tab_files, _same_file_bytes as same_file_bytes
from scripts.artifacts.storagePathViews import canonical_path


class FileContext:
    def __init__(self, root, files):
        self.root = str(root)
        self.files = files

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root))


def write(root, relative, data):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    path.chmod(0o444)
    return str(path)


def exact_oracle(context):
    """Independent full-byte classes, not production fingerprint grouping."""
    classes = []
    failures = []
    for path in sorted(context.files):
        if Path(path).is_dir() or not Path(path).name.startswith('Tabs_'):
            continue
        key, rank = canonical_path(context.get_relative_path(path))
        try:
            data = Path(path).read_bytes()
        except OSError:
            failures.append(path)
            continue
        for group in classes:
            if group['key'] == key and group['data'] == data:
                group['choice'] = min(group['choice'], (rank, path))
                break
        else:
            classes.append({'key': key, 'data': data, 'choice': (rank, path)})
    return sorted(failures + [group['choice'][1] for group in classes])


class ChromiumSnssAliasesTest(unittest.TestCase):
    def test_exact_aliases_divergent_decoded_equal_states_and_separate_tenants(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            data = _file((1, _navigation()), (1, _navigation()),
                         (4, struct.pack('<iiq', 7, 2, 13300000000000001)),
                         (4, struct.pack('<iiq', 7, 2, 13300000000000001)))
            tail = '/com.android.chrome/app_chrome/Default/Sessions/Tabs_100'
            paths = [write(root, prefix + tail, data) for prefix in
                     ['Dump/data/data', 'Dump/data/user/0', 'Dump/data_mirror/data_ce/null/0',
                      'Dump/data/user/10', 'Dump/data/user_de/0', 'OtherDump/data/data',
                      'UnknownRoot/custom']]
            paths.append(write(root, 'Dump/data_mirror/data_ce/other/0' + tail,
                               data + struct.pack('<H', 2) + b'\x63X'))
            paths.append(write(root, 'Dump/data/data/com.brave.browser/app_chrome/Default/Sessions/Tabs_100', data))
            paths.append(write(root, 'Dump/data/data/com.android.chrome/app_chrome/Profile 1/Sessions/Tabs_100', data))
            paths.append(write(root, 'Dump/data/data/com.android.chrome/app_chrome/Default/Sessions/Tabs_200', data))
            initial = {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths}
            for order in [paths, list(reversed(paths))]:
                context = FileContext(root, order)
                selected = list(tab_files(context))
                self.assertEqual(selected, exact_oracle(context))
                self.assertEqual(len(selected), 9)
                self.assertIn(paths[0], selected)
                for wrapper, width in [(module.chrome_session_tabs, 15),
                                       (module.chrome_session_tab_state, 5)]:
                    headers, rows, source = wrapper.__wrapped__(context)
                    expected = []
                    for path in selected:
                        expected.extend(wrapper.__wrapped__(FileContext(root, [path]))[1])
                    self.assertEqual(rows, expected)
                    self.assertEqual(len(rows), 18)
                    self.assertTrue(all(len(row) == width for row in rows))
                    self.assertEqual(len(headers), width)
                    self.assertEqual(source, '\n'.join(selected))
                    self.assertEqual(rows[0], rows[1])
            self.assertEqual(initial, {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths})

    def test_digest_collision_still_compares_complete_bytes_after_chunk_boundary(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            data = _file(*[(1, _navigation(url='https://large.test/' + str(i))) for i in range(400)],
                         (4, struct.pack('<iiq', 7, 2, 13300000000000001)))
            self.assertGreater(len(data), 65536)
            tail = '/com.android.chrome/app_chrome/Default/Sessions/Tabs_100'
            paths = [write(root, 'Dump/data/data' + tail, data),
                     write(root, 'Dump/data/user/0' + tail, data),
                     write(root, 'Dump/data_mirror/data_ce/null/0' + tail, data[:-1] + b'\x01')]
            # Force an index collision; only real streaming byte equality may collapse.
            with patch.object(module, '_file_fingerprint', return_value=(len(data), b'same-index')):
                self.assertEqual(list(tab_files(FileContext(root, paths))), [paths[0], paths[2]])
            self.assertEqual(list(tab_files(FileContext(root, paths))), exact_oracle(FileContext(root, paths)))
            self.assertTrue(same_file_bytes(paths[0], paths[1]))
            self.assertFalse(same_file_bytes(paths[0], paths[2]))

    def test_alias_reads_use_bounded_buffers(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            data = _file(*[(1, _navigation()) for _ in range(400)])
            tail = '/com.android.chrome/app_chrome/Default/Sessions/Tabs_100'
            paths = [write(root, prefix + tail, data) for prefix in
                     ['Dump/data/data', 'Dump/data/user/0']]
            reads = []

            class BoundedFile:
                def __init__(self, handle):
                    self.handle = handle

                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    self.handle.close()

                def read(self, size=-1):
                    reads.append(size)
                    return self.handle.read(size)

            def bounded_open(path, mode):
                self.assertEqual(mode, 'rb')
                return BoundedFile(Path(path).open('rb'))

            with patch('scripts.artifacts.chromeSessionTabs.open',
                       side_effect=bounded_open, create=True):
                self.assertEqual(list(tab_files(FileContext(root, paths))), [paths[0]])
            self.assertTrue(reads)
            self.assertTrue(all(0 < size <= 65536 for size in reads))

    def test_read_failures_reach_existing_wrapper_and_comparison_failure_retains_both(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            data = _file((1, _navigation()), (4, struct.pack('<iiq', 7, 2, 13300000000000001)))
            tail = '/com.android.chrome/app_chrome/Default/Sessions/Tabs_100'
            paths = [write(root, 'Dump/data/data' + tail, data),
                     write(root, 'Dump/data/user/0' + tail, data)]
            missing = str(root / ('Dump/data_mirror/data_ce/null/0' + tail))
            context = FileContext(root, paths + [missing])
            self.assertEqual(list(tab_files(context)), sorted([paths[0], missing]))
            for wrapper in [module.chrome_session_tabs, module.chrome_session_tab_state]:
                with patch.object(module, 'logfunc') as log:
                    _, rows, source = wrapper.__wrapped__(context)
                self.assertEqual(len(rows), 1)
                self.assertEqual(source, paths[0])
                self.assertEqual(log.call_count, 1)
                self.assertIn('could not read Tabs_100', log.call_args.args[0])
            with patch.object(module, '_same_file_bytes', side_effect=OSError('transient compare read')):
                self.assertEqual(list(tab_files(FileContext(root, paths))), sorted(paths))

    def test_rank_tie_unknown_prefixes_non_tabs_and_safe_invalid_decoder_behavior(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            data = _file((1, _navigation()))
            tail = '/com.android.chrome/app_chrome/Default/Sessions/Tabs_100'
            a = write(root, 'Dump/data_mirror/data_ce/a/0' + tail, data)
            b = write(root, 'Dump/data_mirror/data_ce/b/0' + tail, data)
            invalid = write(root, 'other/Tabs_bad', b'NOPE1234')
            non_tab = write(root, 'other/Session_100', data)
            directory = root / 'Tabs_directory'
            directory.mkdir()
            context = FileContext(root, [b, invalid, non_tab, str(directory), a])
            self.assertEqual(list(tab_files(context)), sorted([a, invalid]))
            with patch.object(module, 'logfunc') as log:
                _, rows, source = module.chrome_session_tabs.__wrapped__(context)
            self.assertEqual(len(rows), 1)
            self.assertEqual(source, a)
            self.assertEqual(log.call_count, 1)


if __name__ == '__main__':
    unittest.main()
