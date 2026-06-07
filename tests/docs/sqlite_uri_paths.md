# SQLite URI Path Tests

The `tests/core/test_sqlite_uri_paths.py` script verifies that LEAPPs can open
SQLite databases in read-only URI mode when their paths contain characters that
have special meaning in a URI.

The test exercises both core SQLite helpers:

- `open_sqlite_db_readonly()`
- `attach_sqlite_db_readonly()`

Each database contains a known value. The test opens the database through both
helpers and confirms that the expected value can be read.

## Local Path Tests

The default test run creates SQLite databases under the operating system's
temporary directory. It tests paths containing:

- A normal directory name
- Spaces
- A hash (`#`)
- A percent sign (`%`)
- Unicode characters
- A question mark (`?`) on macOS and Linux

The question mark case is not created on Windows because `?` is not permitted
in Windows file or directory names.

On Windows, the script also tests an extended-length local path longer than 260
characters.

Temporary local test directories are removed after each test.

## Running The Tests

Run the local tests from the repository root:

```shell
python tests/core/test_sqlite_uri_paths.py -v
```

The optional network-share test is skipped when no network path is supplied.

## Network Share Test

On Windows, an authenticated UNC share can be supplied with `--unc-root`:

```powershell
python .\tests\core\test_sqlite_uri_paths.py -v `
    --unc-root "\\server\share\test-folder"
```

The network test:

1. Creates a uniquely named directory containing spaces and `#`.
2. Creates a SQLite fixture locally.
3. Copies the completed database bytes to the network share.
4. Tests the ordinary UNC path.
5. Tests the extended UNC path (`\\?\UNC\...`).
6. Removes the uniquely named test directory.

The supplied directory must already exist and be authenticated with permission
to create and remove files and directories.

The network test is Windows-only because UNC and extended UNC paths are Windows
path formats. On macOS and Linux, mounted SMB shares appear as normal POSIX
paths and are covered by the regular path handling code.

## Notes

These tests focus on SQLite URI path construction. They do not test writable
output databases such as LAVA, timeline, or KML databases because those
connections use normal filesystem paths rather than SQLite `file:` URIs.
