"""Actual JPEG files keep their evidence rows across examiner staging renames."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

from scripts.artifacts import dmss as module


class Context:
    def __init__(self, root, files):
        self.root = Path(root)
        self.files = list(map(str, files))

    def get_files_found(self):
        return self.files

    def get_relative_path(self, path):
        return str(Path(path).relative_to(self.root)) if path else ''


def write_images(root):
    folder = Path(root) / 'Android/data/com.mm.android.DMSS/files/Download/snapshot'
    names = ['ordinary.jpg', 'video/snapshot.jpg', 'videogames.jpg', 'nested/ordinary.jpg',
             '.thumb/hidden.jpg', 'hidden.thumb.jpg', 'UPPER.JPG', 'control.png']
    files = []
    for index, name in enumerate(names):
        path = folder / name
        path.parent.mkdir(parents=True, exist_ok=True)
        Image.new('RGB', (3, 2), (index * 20, 34, 56)).save(
            path, format='PNG' if name.endswith('.png') else 'JPEG')
        files.append(path)
    return files


class DmssJpgCandidatesTest(unittest.TestCase):
    def test_actual_jpeg_selection_is_invariant_to_video_staging_prefix(self):
        with tempfile.TemporaryDirectory() as folder:
            results = []
            for name in ['case-neutral', 'case-video']:
                root = Path(folder) / name
                files = write_images(root)
                before = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in files}
                with patch.object(module, 'check_in_media', side_effect=lambda p, _: hashlib.sha256(Path(p).read_bytes()).hexdigest()):
                    headers, rows, source = module.get_dmss_media.__wrapped__(Context(root, files))
                self.assertEqual(headers, ('File Path', 'File Name', ('File Content', 'media')))
                self.assertEqual([row[1] for row in rows],
                                 ['ordinary.jpg', 'snapshot.jpg', 'videogames.jpg', 'ordinary.jpg'])
                self.assertEqual(source, 'Android/data/com.mm.android.DMSS/files/Download/snapshot/nested')
                self.assertEqual(before, {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                                          for p in files})
                results.append((rows, source))
            self.assertEqual(results[0], results[1])

    def test_repeated_paths_keep_order_and_thumb_limit_remains_explicit(self):
        with tempfile.TemporaryDirectory() as folder:
            files = write_images(folder)
            with patch.object(module, 'check_in_media', return_value='MEDIA'):
                _, rows, _ = module.get_dmss_media.__wrapped__(Context(folder, [files[1], files[0], files[1]]))
                self.assertEqual([row[1] for row in rows], ['snapshot.jpg', 'ordinary.jpg', 'snapshot.jpg'])
                root = Path(folder) / 'stage.thumb'
                thumb_files = write_images(root)
                self.assertEqual(module.get_dmss_media.__wrapped__(Context(root, thumb_files))[1], [])


if __name__ == '__main__':
    unittest.main()
