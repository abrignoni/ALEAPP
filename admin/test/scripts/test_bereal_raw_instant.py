"""Real nested JSON/cache files exercise raw RealMoji flags without vendor mappings."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

from scripts.artifacts import bereal as module


class Context:
    def __init__(self, files):
        self.files = list(map(str, files))

    def get_files_found(self):
        return self.files


def write_fixture(root):
    root = Path(root) / 'data/data/com.bereal.ft/cache/network'
    root.mkdir(parents=True, exist_ok=True)
    values = [None, True, False, 0, 1, 2.5, '', 'true', 'false', 'null', [], {}, [0, False], {'raw': 'é'}]
    reactions = [{'emoji': 'missing', 'createdAt': '2024-07-28T12:34:56.123Z'}]
    for index, value in enumerate(values):
        reactions.append({'emoji': f'raw-{index}', 'isInstant': value,
                          'createdAt': '2024-07-28T12:34:56.123Z'})
    for reaction in reactions:
        reaction.update({'mediaUrl': 'https://example.test/reaction',
                         'user': {'id': 'uid', 'username': 'reactor',
                                  'profilePicture': 'https://example.test/avatar'}})
    # These all previously displayed the same Standard row; preserve their distinctions.
    collision = [{'emoji': 'collision'}, {'emoji': 'collision', 'isInstant': None},
                 {'emoji': 'collision', 'isInstant': False}, {'emoji': 'collision', 'isInstant': 0},
                 {'emoji': 'collision', 'isInstant': 'false'}]
    reactions += collision + [copy.deepcopy(collision[-1])]
    reactions += [{'mediaUrl': 'https://example.test/unmatched', 'isInstant': True},
                  {'emoji': '', 'isInstant': False}, None, 'invalid']
    post = {'id': 'post-main', 'takenAt': '2024-07-28T12:34:56Z', 'realMojis': reactions}
    document = {'userPosts': post}
    (root / 'feed.0').write_text('https://example.test/feeds/friends\nGET\nHTTP/1.1 200 OK\n')
    (root / 'feed.1').write_text(json.dumps(document, ensure_ascii=False))
    for name, url, kind in [('reaction', 'reaction', 'JPEG'), ('avatar', 'avatar', 'PNG')]:
        (root / f'{name}.0').write_text(f'https://example.test/{url}\nGET\nHTTP/1.1 200 OK\n')
        Image.new('RGB', (2, 2), (12, 34, 56)).save(root / f'{name}.1', format=kind)
    return root, values, document


def project(files):
    with patch.object(module, 'check_in_media', side_effect=lambda path, **kwargs: f'media:{Path(path).name}'):
        return module.bereal_realmojis.__wrapped__(Context(files))


class BeRealRawInstantTest(unittest.TestCase):
    def test_real_disk_cache_raw_types_media_and_projection(self):
        with tempfile.TemporaryDirectory() as folder:
            root, values, _ = write_fixture(folder)
            files = sorted(root.iterdir())
            before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
            headers, rows, sources = project(files)
            self.assertEqual(headers[0], ('Created', 'datetime'))
            self.assertEqual(len(headers), 11)
            self.assertEqual(len(rows), 21)
            self.assertEqual(rows[0][4:6], ('Unclassified (isInstant missing)', ''))
            for row, value in zip(rows[1:15], values):
                self.assertIs(type(json.loads(row[5])), type(value))
                self.assertEqual(json.loads(row[5]), value)
                if type(value) is bool:
                    expected = ('Instant (parser label; isInstant=true)' if value else
                                'Standard (parser label; isInstant=false)')
                elif value is None:
                    expected = 'Unclassified (isInstant null)'
                else:
                    expected = 'Unclassified (isInstant nonboolean)'
                self.assertEqual(row[4], expected)
            for row in rows[:15]:
                self.assertEqual(row[0].isoformat(), '2024-07-28T12:34:56.123000+00:00')
                self.assertEqual(row[1:3], ('post-main', 'reactor'))
                self.assertEqual(row[6:11], ('https://example.test/reaction', 'media:reaction.1',
                                            'https://example.test/avatar', 'media:avatar.1',
                                            'https://example.test/feeds/friends'))
            self.assertEqual(set(sources.splitlines()), {str(root / name) for name in
                                                        ['feed.0', 'feed.1', 'reaction.1', 'avatar.1']})
            self.assertEqual(before, {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in files})

    def test_raw_collision_split_and_exact_repeat_dedupe(self):
        with tempfile.TemporaryDirectory() as folder:
            root, _, _ = write_fixture(folder)
            _, rows, _ = project(sorted(root.iterdir()))
            collision = [row for row in rows if row[3] == 'collision']
            self.assertEqual([row[5] for row in collision], ['', 'null', 'false', '0', '"false"'])
            # The old projection has one identical Standard row; the new one has five.
            old = [row[:4] + ('Standard',) + row[6:] for row in collision]
            self.assertEqual(len({tuple(map(str, row)) for row in old}), 1)
            self.assertEqual(len(collision), 5)

    def test_nested_wrapper_shapes_and_standalone_json(self):
        with tempfile.TemporaryDirectory() as folder:
            root, _, document = write_fixture(folder)
            post = document['userPosts']
            post['realMojis'] = [{'emoji': 'same', 'isInstant': False}]
            shapes = [{'myPosts': post}, {'myPosts': [post]}, {'userPosts': [post]},
                      {'friendsPosts': [post]}, {'friendsPosts': [{'user': {'username': 'friend'}, 'posts': [post]}]},
                      {'user': {'username': 'friend'}, 'posts': [post]}]
            for index, shape in enumerate(shapes):
                path = root / f'shape-{index}.json'
                path.write_text(json.dumps(shape))
                _, rows, _ = project([path])
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0][1:4], ('post-main', '', 'same'))
                self.assertEqual(rows[0][5], 'false')
                self.assertEqual(rows[0][-1], '')

    def test_invalid_json_and_non_dict_or_empty_reactions_unchanged(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'invalid.json'
            path.write_text('{invalid')
            self.assertEqual(project([path])[1], [])
            path.write_text(json.dumps({'userPosts': {'id': 'p', 'takenAt': 1722170096,
                                                     'realMojis': [None, 1, {}, {'isInstant': True}]}}))
            self.assertEqual(project([path])[1], [])


if __name__ == '__main__':
    unittest.main()
