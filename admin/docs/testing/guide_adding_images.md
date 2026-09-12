# Guide: Adding a New Image to the Manifest

This guide covers adding a test image to `admin/image_manifest.json`. The manifest tracks
metadata about publicly available test images, which are far too large to keep in the
repository, and it lets `admin/test/scripts/make_test_data.py` find your local copy so it can
generate focused test case data. Accurate metadata, `os_version` especially, also helps when
writing test cases for modules whose logic branches on the Android release.

The manifest has a second job. `admin/scripts/check_pr_test_data.py` runs on artifact pull
requests, and when a changed module's `sample_data` cites a corpus key the manifest knows, the
bot tells the contributor a maintainer can generate the fixture from the public image instead
of asking them to supply test data.

**An entry is a statement that the image can be obtained.** Only publicly available images go
in. Corpus keys naming images that are not distributed stay out, and are listed instead in
[public_corpus_images.md](../public_corpus_images.md) so a reader knows not to go looking.

## Steps to Add a New Image

1. **Obtain the Test Image**:
   - Acquire a publicly available test image containing sample data for Android artifacts.
   - Note the source, creation date, and any relevant information about the image.

2. **Extract a File Path List** (optional):
   - Extract a list of file paths from the test image and save it as a CSV in
     `admin/data/filepath-lists/`, compressed as a zip.
   - Point the entry's `file_path_list` at it. No entry carries one today, and
     `make_test_data.py` works without it.

3. **Analyze File Path Patterns** (optional, needs step 2):
   - Run `admin/scripts/filepath_search_list.py`, which reads `admin/data/filepath-lists/` and
     writes `admin/data/generated/filepath_results.csv` and
     `admin/docs/filepath_search_summary.md`.

4. **Update the Image Manifest**:
   - Open `admin/image_manifest.json`.
   - Add a new entry to the `"images"` array with the following structure:

```json
{
  "image_name": "unique_image_name",
  "sample_data_key": "corpus_key_used_in_sample_data",
  "description": "Device and OS, then who published it",
  "published_file": "Image-Filename-As-Published.zip",
  "download_url": "https://example.com/download/link/for/image",
  "author": {
    "name": "Author Name",
    "organization": "Organization Name (if applicable)"
  },
  "image_info": {
    "os_name": "Android",
    "os_version": "14",
    "device_model": "Device model (if known)"
  },
  "file_info": {
    "md5_hash": "md5_hash_as_published"
  },
  "notes": "What the published hash is of, and anything else a reader needs"
}
```

   - `sample_data_key` is the corpus key artifacts cite in `sample_data` and in
     [public_corpus_images.md](../public_corpus_images.md). For new entries make it the same
     string as `image_name`.
   - `published_file` is the exact filename the publisher distributes, with no path. The
     resolver searches for that name, so getting it right is what makes `search_roots` work.
   - Record `md5_hash` in lowercase, as published. Say in `notes` whether that hash is of the
     file itself or of a wrapper archive, because a working copy is often the inner image
     un-nested from the wrapper and cannot match the wrapper's hash.
   - Fill `image_info` only where a source records the value. Leave a field out rather than
     guessing it.
   - Manifest entries carry no machine-specific paths. Older entries in other cores still list
     `local_image_paths` and those keep working, but do not add that field to new entries.

5. **Record Your Local Path**:
   - Machine-specific locations live in `admin/image_manifest.local.json`, which is
     git-ignored. Map the image directly, or name folders to search for `published_file`:

```json
{
  "image_paths": {
    "unique_image_name": "~/phone-images/Image-Filename-As-Published.zip"
  },
  "search_roots": [
    "~/phone-images"
  ]
}
```

   - `image_paths` keys can be either the `image_name` or the `sample_data_key`.
   - A direct `image_paths` mapping is checked first and is the reliable option when your copy
     is renamed, or is the un-nested inner image rather than the published wrapper. That is the
     common case for the Cellebrite CTF images, where the working copy is an
     `EXTRACTION_FFS.zip` inside the published archive.

6. **Commit Changes**:
   - Commit the updated `image_manifest.json`.
   - Include the file path list zip in the same commit if you made one.

## Best Practices

- Use concise and unique names for the `image_name` field.
- Keep `description` short: the device and OS, then who published it.
- Put anything a reader needs in order to trust the hash into `notes`.

## Troubleshooting

- If `make_test_data.py` cannot find your image, check your mapping in
  `admin/image_manifest.local.json` and that the mapped file exists. The script warns when a
  mapped path is missing rather than failing silently.
- LEAPP reads zip and tar, not 7z. Where a publisher ships a `.7z`, register the published
  name in `published_file` and map your un-packed copy in `image_manifest.local.json`.
- If you set `file_path_list`, make sure it points at a real CSV zip under
  `admin/data/filepath-lists/`.
