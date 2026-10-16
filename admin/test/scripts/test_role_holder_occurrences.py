"""Stored XML child names retain occurrence order and evidence origins."""
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from scripts.artifacts import roles


def context(root, files):
    return SimpleNamespace(get_files_found=lambda: files,
                           get_relative_path=lambda p: str(pathlib.Path(p).relative_to(root)))


def write_xml(root, relative, body):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding='utf-8')
    return str(path)


class RoleHolderOccurrencesTest(unittest.TestCase):
    def test_occurrences_blank_unknown_tag_and_source_union(self):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            first = write_xml(root, 'data/system/users/0/roles.xml', '<roles><role name="zero"/><role name="many"><holder name="a"/><holder name="a"/><other name=""/><holder name=" b "/></role></roles>')
            second = write_xml(root, 'copy/data/system/users/0/roles.xml', '<roles><role name="many"><holder name="other"/></role></roles>')
            empty = write_xml(root, 'empty/data/system/users/0/roles.xml', '<roles/>')
            headers, rows, source = roles.get_roles.__wrapped__(context(root, [first, empty, second]))
            self.assertEqual(headers[-1], 'Source File')
            self.assertEqual([(r[2], r[3]) for r in rows], [('zero', ''), ('many', 'a'), ('many', 'a'), ('many', ''), ('many', ' b '), ('many', 'other')])
            self.assertEqual([r[-1] for r in rows], [str(pathlib.Path(first).relative_to(root))]*5+[str(pathlib.Path(second).relative_to(root))])
            self.assertEqual(source, '\n'.join([first, empty, second]))
            headers, rows, _ = roles.get_roles.__wrapped__(context(root, [first, empty, first]))
            self.assertEqual(len(headers), 4)
            self.assertEqual(len(rows), 10)

    def test_missing_attributes_diagnostics_and_later_healthy(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(roles, 'logfunc') as logger:
            root = pathlib.Path(folder)
            file = write_xml(root, 'data/system/users/0/roles.xml', '<roles><role/><role name="mixed"><holder/><holder name="ok"/></role><role name="missing"><holder/></role><role name="last"><holder name="last"/></role></roles>')
            ctx = context(root, [file])
            ctx.get_relative_path = lambda p: 'line\n"'+'x'*1000
            headers, rows, _ = roles.get_roles.__wrapped__(ctx)
            self.assertEqual(len(headers), 4)
            self.assertEqual([(r[2], r[3]) for r in rows], [('mixed', 'ok'), ('missing', ''), ('last', 'last')])
            messages = [call.args[0] for call in logger.call_args_list]
            self.assertEqual(len(messages), 3)
            self.assertTrue(all('\n' not in m and '\\n' in m and '[truncated]' in m and len(m)<400 for m in messages))
            self.assertIn('role ordinal 2; child ordinal 1', messages[1])

    def test_selection_recovery_and_no_contributor_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            skipped = write_xml(root, 'mirror/data/system/users/0/roles.xml', '<roles><role name="skip"/></roles>')
            recovered = write_xml(root, 'data_mirror/data/system/users/0/roles.xml', '<roles><role name="a&b"><holder name="x&y"/></role></roles>')
            empty = write_xml(root, 'data/system/users/10/roles.xml', '<roles/>')
            headers, rows, source = roles.get_roles.__wrapped__(context(root, [skipped, recovered, empty]))
            self.assertEqual(rows, [('system/users/*/roles.xml', '0', 'a&b', 'x&y')])
            self.assertEqual(len(headers), 4)
            self.assertEqual(source, '\n'.join([recovered, empty]))
            _, rows, source = roles.get_roles.__wrapped__(context(root, [skipped, empty]))
            self.assertEqual(rows, [])
            self.assertEqual(source, empty)

    def test_data_mirror_misc_de_copy_is_skipped_only_beside_its_counterpart(self):
        tail = 'apexdata/com.android.permission/roles.xml'
        body = '<roles><role name="r"><holder name="h"/></role></roles>'
        with tempfile.TemporaryDirectory() as folder, patch.object(roles, 'logfunc') as logger:
            root = pathlib.Path(folder)
            kept = write_xml(root, f'data/misc_de/0/{tail}', body)
            mirror = write_xml(root, f'data_mirror/misc_de/null/0/{tail}', body)
            other_user = write_xml(root, f'data_mirror/misc_de/null/10/{tail}', body)
            headers, rows, source = roles.get_roles.__wrapped__(context(root, [mirror, kept, other_user]))
            self.assertEqual([(r[1], r[2], r[3]) for r in rows], [('0', 'r', 'h'), ('10', 'r', 'h')])
            self.assertEqual(headers[-1], 'Source File')
            self.assertEqual(source, '\n'.join([kept, other_user]))
            self.assertEqual(len(logger.call_args_list), 1)
            headers, rows, source = roles.get_roles.__wrapped__(context(root, [mirror]))
            self.assertEqual([(r[1], r[2], r[3]) for r in rows], [('0', 'r', 'h')])
            self.assertEqual(source, mirror)


if __name__ == '__main__':
    unittest.main()
