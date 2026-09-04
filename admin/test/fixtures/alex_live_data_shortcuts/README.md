# Synthetic ALEX dumpsys fixture for ALEAPP PR #1217

Built 2026-09-04 for the "Dumpsys - Shortcuts" artifacts in `alex_live_data.py`.

Nothing here came off a device. Every id, name, label and message string is
invented, and the files carry a banner saying so.

## Files

| file | what it is |
|---|---|
| `dumpsys_1756900000.txt` | populated dumpsys, has a `shortcut` service section |
| `alex_shortcut_synthetic_extraction.zip` | the above at `ALEX_PRFS_synthetic/extra/`, ready for `make_test_data.py` |
| `no_shortcut_repro/dumpsys_1756900001.txt` | same shape, `shortcut` section absent |
| `with_decoys.zip` | the extraction plus four unrelated members, for the `make_test_data.py` check below |
| `build_fixture.py` | the generator, so the file can be regenerated or extended |

## Where the format came from

Read from AOSP on 2026-09-04:

- wrapper header and footer: `frameworks/native/cmds/dumpsys/dumpsys.cpp`,
  `writeDumpHeader()` and `writeDumpFooter()`
- `ShortcutInfo` body and field order: `frameworks/base/core/java/android/content/pm/ShortcutInfo.java`,
  `toDumpString()` calling `toStringInner(secure=false, includeInternalData=true, indent)`
- package framing: `frameworks/base/services/core/java/com/android/server/pm/ShortcutPackage.java`, `dump()`

One part is **not** sourced from AOSP: the payload inside `intents=` for the
Discord rows. No ALEX extraction was available to read the real shape from, so
it is shaped to match the regexes in `shortcut_data()`. Worth confirming against
a real dump before this is trusted as a format reference.

## What the populated file covers

Run against PR head `b23c62fc`:

`alex_live_shortcut` returns 6 rows, `alex_live_discord_shortcut` returns 3.

| row | exercises |
|---|---|
| `known-dm-alpha` | full Discord row: `message_content` and the `"timestamp":"..."` in the raw blob |
| `known-dm-bravo` | the `body,` fallback when `message_content` is absent, and the `scheduled_at,` fallback when the raw timestamp is absent |
| `known-guild-charlie` | guild/channel row with `persons=[]`, so `clean()` returns None |
| `known-dm-delta` | **`intents=null`**, the crash reported on this PR. The `and intents` guard now skips it, and it stays in the Discord table's input so the fix cannot silently regress |
| `known-camera-selfie` | non-Discord manifest shortcut, `persons=null` |
| `known-dialer-echo` | non-Discord pinned shortcut carrying a Person |

## What the no-shortcut file reproduces

Both new functions put `data_headers` and `return` inside the `else`, so on a
dumpsys with no `shortcut` section:

    alex_live_shortcut          -> returns None
                                   artifact_processor then raises
                                   TypeError: cannot unpack non-iterable NoneType object

    alex_live_discord_shortcut  -> TypeError: argument of type 'NoneType' is not
                                   a container or iterable

The second is the guard itself:

    if acc_dump is None and "packageName=com.discord" in acc_dump:

`and` does not short-circuit away the right operand when the left is true, so
`"..." in None` runs. It also reads inverted: `or ... not in ...` is what makes
the "no discord shortcut" message reachable.

`alex_live_companiondevice` in the same file already returns explicitly in both
branches, which is the shape to copy.

## make_test_data.py note

`alex_live_data.py` writes `"paths": ('*/extra/dumpsys_*.txt')` without the
trailing comma, so it is a string rather than a one-element tuple. Generating
test data from a real extraction on current main sweeps the whole extraction
into every artifact's zip. Measured with `with_decoys.zip` (5 members):

    before   alex_live_shortcut zip -> all 5 members
             alex_live_appops   zip -> all 5 members, though its glob is
                                       */extra/app_ops.json
    after    alex_live_shortcut zip -> the dumpsys file only
             alex_live_appops   zip -> app_ops.json only

"before" is PR #1217 at b23c62fc with its own copy of the script. "after" is the
same branch with the `make_test_data.py` now on main: ALEAPP PR #1273 merged
2026-09-04 as d5d17025, so pulling main is all it takes. Single-file inputs hide
this entirely, which is why the decoy zip exists.
