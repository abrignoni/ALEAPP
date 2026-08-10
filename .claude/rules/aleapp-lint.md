# ALEAPP lint specifics

The general CI facts are in `leapp-ci.md`. Two things are particular to this repo.

**Red lint exists on merged commits.** That is because maintainers have merged past it
historically, not because the job is advisory. It does fail PR checks. Do not take a
red-but-merged commit as licence to ignore a failure on your own PR.

**Touching a shared core file inherits its debt.** `ilapfuncs.py` in particular carries
backward-compatibility re-exports that raise `W0611 unused-import`. A one-line edit there
surfaces all of them. Use `admin/scripts/lint_changed.py` where available: it lints
merge-base against the change and fails only on *new* warnings.

Two traps that tool documents, worth knowing if you reimplement the comparison:

- pylint infers across the whole analysed set, so lint the same paths on both sides or the
  results are not comparable.
- pylint caches between runs. Pass `--persistent=no` or the second run is not reproducible.
