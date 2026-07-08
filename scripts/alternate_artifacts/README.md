# Alternate artifacts

Artifacts in this folder are **not** part of a normal ALEAPP run. They are
developer/tooling oriented modules. Nothing in ALEAPP loads this folder;
developer tooling (batch-leapp) stages the module into `scripts/artifacts/`
for the duration of a coverage run, or you can copy it there manually:

```
cp scripts/alternate_artifacts/appInventory.py scripts/artifacts/
python3 aleapp.py -t zip -i <extraction.zip> -o <output>
rm scripts/artifacts/appInventory.py
```

(iLEAPP exposes the same module through `--custom_artifacts_path`; ALEAPP does
not have that CLI option yet, so staging is the interim mechanism.)

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
