"""Ambiguous filename candidates remain reviewable without arbitrary media export."""
import pathlib
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
from admin.test.scripts.test_randochat_media import make_fixture
from admin.test.scripts.test_sdhms_stat_sources import context
from scripts.artifacts.RandoChat import randochat_messages

def make_candidates(root):
    root = pathlib.Path(root)
    paths = make_fixture(root)
    for prefix, color in [('data/media/10', 'red'), ('OtherRoot/data/media/0', 'blue')]:
        target = root / prefix / 'Android/data/com.random.chat.app/files/images/exact.png'
        target.parent.mkdir(parents=True, exist_ok=True)
        Image.new('RGB', (1, 1), color).save(target)
        paths.append(target)
    return paths

class RandoChatCandidatesTest(unittest.TestCase):
    def test_ambiguity_order_and_spy(self):
        with tempfile.TemporaryDirectory() as folder:
            paths = make_candidates(folder)
            results = []
            for inputs in [paths, [paths[0], *reversed(paths[1:])]]:
                with patch('scripts.artifacts.RandoChat.check_in_media', side_effect=lambda path, name: name) as media:
                    headers, rows, source = randochat_messages.__wrapped__(context(folder, inputs))
                self.assertEqual(media.call_count, 1)
                self.assertEqual(media.call_args.args[1], 'quote"<&.png')
                count = headers.index('Media Filename Candidate Count')
                inventory = headers.index('Media Filename Candidate Paths')
                attachment = headers.index(('Media File', 'media'))
                for index in [4, 6]:
                    self.assertEqual(rows[index][count], 3)
                    self.assertEqual(rows[index][attachment], '')
                    candidates = rows[index][inventory].splitlines()
                    self.assertEqual(candidates, sorted(candidates))
                    self.assertTrue(all(not pathlib.Path(path).is_absolute() and (pathlib.Path(folder) / path).is_file() for path in candidates))
                self.assertEqual(rows[7][count], 1)
                self.assertEqual(source, str(paths[0]))
                self.assertNotIn('Source File', headers)
                results.append(rows)
            self.assertEqual(results[0], results[1])

    def test_repeated_identical_path_collapses_but_alias_remains(self):
        with tempfile.TemporaryDirectory() as folder:
            paths = make_fixture(folder)
            with patch('scripts.artifacts.RandoChat.check_in_media', return_value='reference') as media:
                headers, rows, _ = randochat_messages.__wrapped__(context(folder, [*paths, paths[1], paths[1]]))
            self.assertEqual(rows[4][headers.index('Media Filename Candidate Count')], 1)
            self.assertEqual(media.call_count, 3)
            alias = pathlib.Path(folder) / 'storage/emulated/0/Android/data/com.random.chat.app/files/images/exact.png'
            alias.parent.mkdir(parents=True, exist_ok=True)
            alias.write_bytes(paths[1].read_bytes())
            with patch('scripts.artifacts.RandoChat.check_in_media', return_value='reference') as media:
                headers, rows, _ = randochat_messages.__wrapped__(context(folder, [*paths, alias]))
            self.assertEqual(rows[4][headers.index('Media Filename Candidate Count')], 2)
            self.assertEqual(media.call_count, 1)
