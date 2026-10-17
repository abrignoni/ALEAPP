![ALEAPP](assets/ALEAPP_logo.png)

# Android Logs Events And Protobuf Parser

If you want to contribute hit me up here: https://abrignoni.github.io

Blog posts here: https://leapps.org/blog

## Download

Pre-built releases need no Python installation: [ALEAPP GitHub Releases](https://github.com/abrignoni/ALEAPP/releases),
or [LEAPPs Releases](https://leapps.org/releases) for the whole LEAPP family.

| Platform | Download |
| -------- | -------- |
| Windows (Intel/AMD) | `ALEAPP-*-windows-x64-portable.zip` |
| Windows (ARM) | `ALEAPP-*-windows-arm64-portable.zip` |
| macOS (Apple Silicon) | `ALEAPP-*-macos-arm64.dmg` |
| macOS (Intel) | `ALEAPP-*-macos-x64.dmg` |
| Linux (Intel/AMD) | `ALEAPP-*-linux-x64.AppImage` |
| Linux (ARM) | `ALEAPP-*-linux-arm64.AppImage` |

Each download holds one program, `aleapp`. `SHA256SUMS.txt` in each release lets you check a download.

**GUI**: open ALEAPP the usual way: by double-clicking `aleapp.exe` from the zip on
Windows, ALEAPP in Applications on macOS, or the AppImage on Linux. Started without
arguments, it opens the window.

**CLI**: give `aleapp` arguments in a terminal and it runs as a command line instead. The
output folder must already exist. On Windows, use `aleapp.exe` from the zip.

```
aleapp.exe -t zip -i C:\path\to\extraction.zip -o C:\path\to\output\
```

On Linux, run the AppImage with the same arguments. On macOS it is inside the app; to
type just `aleapp` in a terminal, link it onto your PATH once:

```
sudo ln -s /Applications/ALEAPP.app/Contents/MacOS/aleapp /usr/local/bin/aleapp
```

## Requirements

**Python 3.10 or above**

### Dependencies

Dependencies for your python environment are listed in `requirements.txt`. Install them using the below command. Ensure
the `py` part is correct for your environment, eg `py`, `python`, or `python3`, etc.

`py -m pip install -r requirements.txt`
or
`pip3 install -r requirements.txt`

For the exact mister_skinnylegs dependency chain the releases are built with, install
`requirements-msl-lock.txt` over that, without dependencies:

`pip3 install --no-deps -r requirements-msl-lock.txt`

To run on **Linux**, you will also need to install `tkinter` separately like so:

`sudo apt-get install python3-tk`

## Building the binaries

`packaging/build.py` builds `aleapp` with PyInstaller for the machine it runs on, from the
same virtual environment. It installs `requirements.txt`, the pinned build tools and
`requirements-msl-lock.txt` first.

```
python packaging/build.py exe          # dist/ALEAPP/, and dist/ALEAPP.app on macOS
python packaging/build.py smoke        # run what it built, without opening a window
python packaging/build.py installer    # Windows: Inno Setup installer; macOS: .dmg; Linux: AppImage
```

`exe --onefile` makes `dist/aleapp` (`dist\aleapp.exe` on Windows) as a single file
instead. The Windows installer needs [Inno Setup](https://jrsoftware.org/isdl.php); on
Linux, `smoke` needs a display, which `xvfb-run` provides. `python packaging/build.py --help`
has the rest.

## Usage

### CLI

```
$ python aleapp.py -t <zip | tar | fs | gz | raw> -i <path_to_extraction> -o <path_for_report_output>
```

`raw` reads a disk image (`.img`, `.dd`, `.bin`, or any numbered `.001` segment of
a split set), or an acquisition and the segments or files beside it (EnCase/EWF
`.E01`, SMART `.s01`, EWF2 `.Ex01`, AFF `.aff`, AFM `.afm`, any `.aff` in an AFD folder,
AFF4 `.aff4`, an Apple `.dmg`, with any `.dmgpart` files beside it, `.sparseimage` or
`.sparsebundle` folder, or a virtual machine disk, `.vhd`, `.vhdx`, `.vmdk` or `.qcow2`), in
place: no mounting and no administrator rights. Its NTFS, FAT32, FAT16, FAT12, exFAT, ext2/3/4,
F2FS, HFS+, APFS, QNX6, QNX4, ETFS, EFS, SquashFS, JFFS2, UBI/UBIFS, YAFFS and QNX IFS
volumes are searched directly (and a U-Boot environment or Belkin NVRM store is read as one
file), and
only the files an artifact asks for are read out of the image. Logical evidence, an
EnCase `.L01` or an FTK Imager `.ad1`, is read as the files it holds. The GUI picks
`raw` on its own for those extensions, and for a sparse bundle or AFD folder chosen with
its folder button. See `admin/docs/raw_image_input.md`.

An encrypted image opens with its password (`--image_password_file` or
`--image_password_env`), or, when it is sealed to a certificate, with that certificate's
RSA private key (`--image_private_key`). A BitLocker volume in an image opens with its
password or recovery password, given the same way, or its startup key
(`--bitlocker_key`, repeatable), and an APFS volume macOS encrypted in software with its
password or personal recovery key, given the same way. At a terminal whatever is missing
is asked for, and the GUI asks in dialogs; a BitLocker or APFS volume nothing opens is
reported and not searched.

The disk images of a Linux software RAID set (md, or LVM2 across disks) are read
together: give them all to `-i` with `-t raw`, or pick them together in the GUI's file
dialog. Given one image that holds a member, the other members are looked for in its
folder by what each file records about itself, not by its name; the command line lists
what it found and what it left out and why before reading the set (`--no-find-members`
reads only the image given), and the GUI asks before reading files it found. The report
names every image read and marks the ones found automatically. One image that holds an
md member is read with its arrays too: a lone RAID1 member with metadata 1.1 or 1.2
now reads its filesystem through the array, and its volume names gain the image's or
the array's name in front. One disk given twice is read once. An image in which no
RAID metadata is found is read as before; see `admin/docs/raw_image_input.md` for what
qnxprobe 1.71 does with DDF, IMSM and md member images read alone.

`tar` also reads an xz-compressed tar (`.tar.xz`), and the GUI picks `tar` for that
extension. A compressed tar, `.tar.gz` included, is decompressed once into the report folder
before any file is read, so the run needs free space there for the uncompressed tar. The
copy is deleted when the run ends, and the run log says how long the step took.

### GUI

```
$ python aleappGUI.py
```

### Help

```
$ python aleapp.py --help
```

## Contributing artifact plugins

Artifact modules live in `scripts/artifacts/` and are loaded each time ALEAPP runs.

**New modules:** start with [How to Write an iLEAPP Module](https://leapps.org/blog-post?post=2026-06-14-how-to-write-an-ileapp-module). It uses iLEAPP as its reference, and ALEAPP modules use the same `__artifacts_v2__` block and `@artifact_processor` decorator. The helpers are not identical across the tools, so check that one exists in ALEAPP's `scripts/ilapfuncs.py` before you import it.

The helper functions a module calls to find files, read SQLite, check in media and convert timestamps are described in [Helper Functions for Artifact Modules](admin/docs/helper_functions.md).

A module has two parts: an `__artifacts_v2__` dictionary at the top of the file, and one function per artifact decorated with `@artifact_processor`. For example:

```python
__artifacts_v2__ = {
    "get_cool_messages": {
        "name": "Cool App Messages",
        "description": "Messages from the Cool App database",
        "author": "@username",
        "creation_date": "2026-10-14",
        "last_update_date": "2026-10-14",
        "requirements": "none",
        "category": "Cool App",
        "notes": "",
        "paths": ('*/CoolApp/cool.db*',),
        "output_types": "standard",
        "artifact_icon": "message",
    }
}

from scripts.ilapfuncs import (
    artifact_processor, convert_unix_ts_to_utc, get_file_path, get_sqlite_db_records)


@artifact_processor
def get_cool_messages(context):
    source_path = get_file_path(context.get_files_found(), 'cool.db')
    if not source_path:
        return (), [], ''

    query = 'SELECT sent_at, sender, body FROM messages'
    data_list = []
    for row in get_sqlite_db_records(source_path, query):
        data_list.append((convert_unix_ts_to_utc(row[0]), row[1], row[2]))

    data_headers = (('Sent', 'datetime'), 'Sender', 'Message')
    return data_headers, data_list, source_path
```

The key of each entry (`get_cool_messages` above) must match the name of its decorated function. That is how the loader and the decorator find each other. The entry holds:

- `name`: the artifact name shown in the report. It must be unique within ALEAPP; the loader stops on a duplicate.
- `description`, `author`, `notes`: text about the artifact. `notes` can be empty.
- `creation_date`, `last_update_date`: dates in `YYYY-MM-DD` form. Both are written to the LAVA output. Bump `last_update_date` when you change the module.
- `requirements`: a note on anything the artifact needs, or `"none"`.
- `category`: groups artifacts in the report.
- `paths`: a tuple of patterns for the files the artifact reads. They are matched with Python's `fnmatch`, so `*` can cross `/`.
- `output_types`: `"standard"` (every output except KML), `"all"`, or a list taken from `html`, `tsv`, `timeline`, `lava` and `kml`.
- `artifact_icon`: a Tabler icon name that appears in `scripts/_elements/tabler-icons.css`.

Optional keys:

- `html_columns`: columns written to the HTML report without escaping. Pass any value that comes from the evidence through the helpers in `scripts/html_safe.py`.
- `data_views`: alternate LAVA views, such as a conversation view for message artifacts. Column order for those is in [Conversation Column Order](admin/docs/conversation_column_order.md).
- `sample_data`: a mapping of test corpus name to a short note about what that corpus produced. The artifact processor ignores it. See [Test data and sample_data for your PR](#test-data-and-sample_data-for-your-pr).

The function takes one argument, `context`, which gives it the files its `paths` matched (`context.get_files_found()`) and the rest of the run. It returns three things: the column headers, a list of row tuples, and the path of the file the rows came from. The decorator writes the HTML, TSV, timeline, KML and LAVA output from them, as `output_types` asks. An empty list writes no table.

A header can be a tuple that names a column type: `('Sent', 'datetime')`, `('Day', 'date')`, `('Number', 'phonenumber')` or `('Photo', 'media')`. A plain string is a text column.

## Test data and sample_data for your PR

A PR that adds or changes an artifact is easiest to review and merge when it arrives with
two things: a small test fixture cut from a real extraction, and `sample_data` values that
record what the module produced. Scripts generate both. Here is the whole flow.

One rule before anything else: whatever you commit here becomes public. Only use data you
are allowed to share, like a test device you populated yourself, a public research image,
or a file you sanitized by hand. Never casework.

**1. Cut a fixture from your extraction**

```
python admin/test/scripts/make_test_data.py <module> --case 1 --input <extraction.zip>
```

This pulls the files your module's `paths` patterns match out of the extraction and writes
the case file `admin/test/cases/testdata.<module>.json` plus one small zip per artifact
under `admin/test/cases/data/<module>/`.

Size rules: under 10 MB per zip, commit it with the PR. Between 10 and 25 MB, commit the
case file and attach the zip to a PR comment. Bigger than that, say so in the PR and a
maintainer will arrange a handoff.

**2. Record the expected output**

```
TZ=UTC python admin/test/scripts/test_module.py <module> -a all -c all
```

This runs the module against the fixture and writes a snapshot of the output under
`admin/test/results/<module>/`. Commit the snapshot too. It becomes the baseline that
guards the module after merge. Keep the `TZ=UTC` part: the committed snapshots are UTC
and CI runs UTC.

**3. Run the same comparison CI will run**

```
python admin/test/scripts/run_test_cases.py --module <module>
```

**4. Generate the sample_data values**

```
python admin/scripts/validate_sample_data.py --emit <extraction.zip> --key <image_name>
```

This runs ALEAPP end to end on your extraction and prints ready-to-paste `sample_data`
blocks for the modules changed on your branch. Paste them into your module's
`__artifacts_v2__` and add the app name and version you saw on the image. If a count is
zero, check the source file really is empty before recording it.

**5. Commit it all and open the PR**

Commit the module, the case file, the fixture zips, and the recorded snapshot together.
More detail lives in
[admin/docs/testing/create_module_test_cases.md](admin/docs/testing/create_module_test_cases.md).

If your extraction cannot be shared, open the PR anyway and say so. A fixture can often be
cut from a public research image instead, or the real file can be sanitized by hand. The
review does not stop while we work that out.

## Code signing policy

Free code signing provided by [SignPath.io](https://about.signpath.io/), certificate by
[SignPath Foundation](https://signpath.org/).

The Windows builds are not signed yet. ALEAPP is applying to SignPath Foundation's free code
signing program for open source projects, and this policy applies to every Windows release
signed under it.

The Windows executables attached to
[GitHub Releases](https://github.com/abrignoni/ALEAPP/releases) are built from this
repository by GitHub Actions, on GitHub-hosted runners
([`release.yml`](.github/workflows/release.yml)). Under this policy, SignPath signs only
what that workflow built. The macOS disk images are signed separately, with an Apple
Developer ID, and notarised by Apple.

SignPath signs `aleapp.exe`, the single-file program in the portable zip. Third-party files
packed inside it are not signed on their own.

### Team roles

- Committers and reviewers: [@abrignoni](https://github.com/abrignoni),
  [@JamesHabben](https://github.com/JamesHabben),
  [@Johann-PLW](https://github.com/Johann-PLW), [@stark4n6](https://github.com/stark4n6)
- Approvers: [@abrignoni](https://github.com/abrignoni),
  [@Johann-PLW](https://github.com/Johann-PLW)

Changes proposed by people who are not committers are reviewed by a committer before they
are merged. Every release signing request is approved by an approver.

### Privacy policy

ALEAPP processes extractions locally, on the machine it runs on. This program will not
transfer any information to other networked systems unless specifically requested by the
user or the person installing or operating it.

The same policy covers the other LEAPPs:
[leapps.org/releases#code-signing-policy](https://leapps.org/releases#code-signing-policy).

## Acknowledgements

This tool is the result of a collaborative effort of many people in the DFIR community.

ALEAPP logo courtesy of Kevin Pagano. The earlier ALEAPP logo was by Derek Eiri.
