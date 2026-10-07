"""Exercise parsed loader retention without changing legacy row ordering."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from scripts.artifacts.packageDexUsageList import (
    package_dex_usage_list_cross_package,
    package_dex_usage_list_secondary,
)


class TestDexListLoaderSuffix(unittest.TestCase):
    def report(self, blocks, extra=None):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / 'data/system/package-dex-usage.list'
            path.parent.mkdir(parents=True)
            text = 'PACKAGE_MANAGER__PACKAGE_DEX_USAGE__2\nowner\n'
            text += '+/data/app/base.apk\n@owner..isolated,other\n'
            for loaders, context in blocks:
                text += '#/data/secondary.dex\n0,1,arm64\n@' + loaders + '\n' + context + '\n'
            path.write_text(text, encoding='utf-8')
            files = [str(path)]
            if extra is not None:
                second = root / 'other/system/package-dex-usage.list'
                second.parent.mkdir(parents=True)
                second.write_text(text, encoding='utf-8')
                files += [str(second), str(path)]
            context = SimpleNamespace(get_files_found=lambda: files,
                                      get_relative_path=lambda p: str(Path(p).relative_to(root)))
            primary = package_dex_usage_list_cross_package.__wrapped__(context)
            secondary = package_dex_usage_list_secondary.__wrapped__(context)
            return primary, secondary

    def test_raw_suffix_would_reverse_legacy_sort(self):
        primary, secondary = self.report([('a!', 'same'), ('a..isolated', 'same')])
        self.assertEqual([r[3] for r in secondary[1]], ['a..isolated', 'a!'])
        self.assertEqual([r[:3] + r[4:] for r in secondary[1]],
                         [('owner', '/data/secondary.dex', '0', 'arm64', 'same',
                           'data/system/package-dex-usage.list')] * 2)
        self.assertEqual([r[:4] for r in primary[1]],
                         [('other', 'owner', '/data/app/base.apk', False),
                          ('owner', 'owner', '/data/app/base.apk', True)])

    def test_complete_key_ties_stay_stable_in_both_encounter_orders(self):
        for loaders in [('a..isolated,a', 'a,a..isolated'),
                        ('a,a..isolated', 'a..isolated,a')]:
            _, secondary = self.report([(loaders[0], 'same'), (loaders[1], 'same'),
                                        (loaders[0], 'same')])
            self.assertEqual([r[3] for r in secondary[1]],
                             [value.replace(',', ', ') for value in
                              [loaders[0], loaders[1], loaders[0]]])

    def test_later_key_fields_empty_tokens_and_source_occurrences(self):
        blocks = [('a..isolated', 'z'), ('a', 'a'),
                  ('', ''), (' ,雪..isolated,,a..isolated.middle,a..isolated..isolated', 'x')]
        primary, secondary = self.report(blocks, extra=True)
        self.assertEqual(len(primary[1]), 4)
        self.assertEqual(len(secondary[1]), 8)
        rows = secondary[1]
        self.assertEqual([r[5] for r in rows if r[3] in ['a', 'a..isolated']],
                         ['a', 'a', 'z', 'z'])
        self.assertEqual(sum(r[3] == '' for r in rows), 2)
        self.assertEqual(sum(r[3] == ' , 雪..isolated, a..isolated.middle, a..isolated..isolated'
                             for r in rows), 2)
        self.assertEqual({r[6] for r in rows},
                         {'data/system/package-dex-usage.list',
                          'other/system/package-dex-usage.list'})


if __name__ == '__main__':
    unittest.main()
