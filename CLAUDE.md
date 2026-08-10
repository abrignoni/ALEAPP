# ALEAPP

Android logs, events and protobuf parser. Second largest of the five LEAPP extractors.

## Before changing an artifact

This repo does not carry its own copy of the module-authoring docs. **iLEAPP's
[`admin/docs/artifact_info_block.md`](https://github.com/abrignoni/iLEAPP/blob/main/admin/docs/artifact_info_block.md)
is the reference for the `__artifacts_v2__` block**, including the `paths` glob semantics,
and it applies here unchanged: the artifact format, the plugin loader and the seekers are
the same code.

`.claude/rules/leapp-artifact-paths.md` covers the parts most often got wrong.

## Repo-specific things worth knowing

- **Android reimplementations are not AOSP.** Do not assert an AOSP table or column meaning
  for a vendor's reimplementation of the same feature; Samsung in particular diverges. If
  the mapping is not proven on a real image, label it as unverified. See
  `.claude/rules/leapp-claims.md`.
- **blackboxprotobuf is vendored** under `scripts/`. Import from there, not from PyPI.
- **Lint has repo-specific traps.** See `.claude/rules/aleapp-lint.md`.
- **`coordinates.db`** ships in the repo and backs geolocation lookups. It is data, not
  evidence, and is the one SQLite file here that is legitimately opened read-write.

## Cross-core

Many apps in `scripts/artifacts/` also exist in iLEAPP, and the copies drift. After fixing
one here, check the sibling. `.claude/rules/leapp-cross-core.md` has the list of known
shared app names and the procedure.

## Rules

`.claude/rules/` holds the detail. Files prefixed `leapp-` are shared across all five
extractors and `lava-` across all six repos. **Edit those at their canonical source, not
here**, or the next sync overwrites you. `aleapp-` files are local to this repo.
