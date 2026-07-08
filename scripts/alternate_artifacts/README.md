# Alternate artifacts

Artifacts in this folder are **not** part of a normal ALEAPP run. They are
developer/tooling oriented modules, loaded only when the CLI is given this
folder explicitly (option ported from iLEAPP in PR #939):

```
python3 aleapp.py -t zip -i <extraction.zip> -o <output> \
    --custom_artifacts_path scripts/alternate_artifacts
```

On checkouts that predate `--custom_artifacts_path`, developer tooling
(batch-leapp) falls back to staging the module into `scripts/artifacts/` for
the duration of a coverage run and removing it afterwards.

## Modules

- **appInventory.py** — writes three tables into the LAVA SQLite output
  (`_lava_artifacts.db`) for parsing-coverage analysis (used by batch-leapp to
  determine which installed apps are not parsed by the tooling):
  - `extractioninfo`: extraction/device/run identifiers (build.prop values,
    LEAPP version, input path)
  - `installedappinventory`: one row per package from packages.xml (plain or
    Android Binary XML)
  - `appfileinventory`: every file in the extraction mapped to its owning app
    package via /data/data, /data/user[_de], Android/{data,media,obb} and
    /data/app locations (lava_only; can be hundreds of thousands of rows)
