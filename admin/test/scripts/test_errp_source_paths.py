"""Every eRR.p that was read is named in the source path."""
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import errp


class SourcePaths(unittest.TestCase):
    def test_both_files_are_named(self):
        with tempfile.TemporaryDirectory() as folder:
            first = pathlib.Path(folder) / 'service' / 'eRR.p'
            second = pathlib.Path(folder) / 'service' / 'data' / 'eRR.p'
            second.parent.mkdir(parents=True)
            first.write_text('2023-01-01 10:00:00+0000 | one | c | d\n')
            second.write_text('2023-01-02 10:00:00+0000 | two | c | d\n')
            context = SimpleNamespace(get_files_found=lambda: [str(first), str(second)])
            _headers, rows, source = errp.get_errp.__wrapped__(context)
        self.assertEqual(len(rows), 2)
        self.assertEqual(source.split('\n'), [str(first), str(second)])

    def test_one_file_is_named_alone(self):
        with tempfile.TemporaryDirectory() as folder:
            only = pathlib.Path(folder) / 'eRR.p'
            only.write_text('2023-01-01 10:00:00+0000 | one | c | d\n')
            context = SimpleNamespace(get_files_found=lambda: [str(only)])
            _headers, _rows, source = errp.get_errp.__wrapped__(context)
        self.assertEqual(source, str(only))


if __name__ == '__main__':
    unittest.main()
