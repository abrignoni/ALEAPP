# Build and release

One driver, `packaging/build.py`, on every platform, in two phases so a signed build is
possible. It replaced six PyInstaller specs, one per program and platform, each with its own
hand-kept list of hidden imports and its own copy of the version. It is iLEAPP's driver
(abrignoni/iLEAPP#2298 and the fixes after it), with mister_skinnylegs, which iLEAPP does
not ship.

    python packaging/build.py exe               phase 1: dist/ALEAPP/ holding aleapp; on macOS also dist/ALEAPP.app
    python packaging/build.py exe --onefile     phase 1: dist/aleapp, a single file; no installer from this
    python packaging/build.py smoke             run what phase 1 built, headlessly (xvfb-run on Linux)
    python packaging/build.py installer         phase 2: Windows dist/ALEAPP-Setup-<v>.exe, macOS dist/ALEAPP-<v>.dmg,
                                                Linux dist/ALEAPP-<v>.AppImage
    python packaging/build.py installer --sign-tool NAME
                                                Windows: Inno Setup signs the installer and the uninstaller
    python packaging/build.py all               both phases, unsigned; refuses --sign-tool and --onefile
    python packaging/build.py verify PATH ...   a signature is present and valid; --subject checks the signer

## One executable, the window or the command line

The spec builds `packaging/entrypoint.py`, not `aleapp.py` or `aleappGUI.py`, which stay the
way to run from source. The result is one executable, `aleapp`, and there is no `aleappGUI`
in a build. Started without arguments, as a double-click, the Start menu or the Finder
start it, it opens the window. Given arguments it is the command line, exactly as before,
so tools that run `aleapp -t fs -i ... -o ...` see no change. Where no window can open
(Linux with no display, as over SSH) it prints the command line's help.

It is a console program. On Windows `hide_console="hide-early"`, which the old GUI build
used, hides the console when nobody started it from one. On macOS it is the bundle's own
executable, `ALEAPP.app/Contents/MacOS/aleapp`. `console=True` makes PyInstaller mark the
bundle `LSBackgroundOnly`, which leaves the window without a Dock icon or menu bar, so the
spec sets it back to false.

The bundle identifier is `org.leapps.ALEAPP`. It replaced `4n6.brigs.ALEAPP`, the earlier
GUI bundle's, so macOS treats the two as different apps: permissions granted to the old
one, Full Disk Access included, have to be granted again.

`scripts/lavafuncs.py` records `leapp_mode` from the script name from source and, in a
build, from whether a `*leappGUI` module was loaded, which only the window's path does.
That file is shared across the LEAPPs; the line is iLEAPP's, kept identical.

## mister_skinnylegs

The browser artifacts (`browserArtifactsViaMisterSkinnylegs.py`) run mister_skinnylegs'
plugins, and it finds them with `PLUGIN_PATH.glob("*_plugin.py")` beside its own package.
So the spec ships `mister_skinnylegs.plugins` as files (`collect_data_files`, with the
`.py` files) and names every submodule as a hidden import, so what the plugins import is
bundled too.

Phase 1 installs `requirements.txt` and `packaging/requirements-build.txt`, then
`requirements-msl-lock.txt` over them with `--no-deps`, as that file prescribes:
mister_skinnylegs declares its `ccl_*` readers as unversioned git URLs, and without the lock
a build would carry whatever their master was that day. Bumping mister_skinnylegs means
bumping both files; a test checks they name the same repository.

If mister_skinnylegs does not import, the artifact empties its own `__artifacts_v2__`, so
its 28 artifacts disappear quietly rather than failing. `smoke` catches that through the
artifact count. It also catches a missing plugin file, which the count cannot see, by
comparing the plugins installed with those in the bundle.

## What goes into the bundle

Decided in `build.py`, which the spec loads, so it is tested without running PyInstaller
(`admin/test/scripts/test_packaging_build.py`, which also exec's the spec with PyInstaller
stubbed out).

- `scripts/`, `leapp_functions/` and `assets/` ship as files, without `__pycache__`.
- **Every artifact module is also a hidden import.** What it still cannot follow is a module
  imported by a name built at run time, and an artifact whose file name is not a valid
  module name, which ships and loads but is not analysed.
- `google.protobuf`, `PIL` and `Crypto` are still collected whole, and the short list of
  imports the six old specs carried is kept in `FIXED_HIDDEN_IMPORTS`.

## Signing goes between the phases

Sign `aleapp.exe` in `dist/ALEAPP/`, or codesign `dist/ALEAPP.app`, after phase 1 and before
phase 2, or the installer ships an unsigned executable inside a signed wrapper. `all`
refuses `--sign-tool` for exactly that reason. `verify` is the last step before anything is
uploaded.

## What the driver guarantees

The version is read from `scripts/version_info.py` as text and passed to the spec and to
Inno Setup; `installer.iss` refuses to compile without it. Windows and macOS take only
numbers there, so `2026.4.1-dev` becomes `2026.4.1` in those fields. `ONEFILE` reaches the
spec through `ALEAPP_ONEFILE`. PyInstaller and dmgbuild are pinned in
`packaging/requirements-build.txt`. Every artifact is asserted to exist after the step
that makes it. `--clean` removes `build/` and the driver's own output in `dist/`, never the
rest of `dist/`.

`dist/aleapp` and `dist/ALEAPP/` are the same path on a case-insensitive file system, the
default on macOS, and PyInstaller's `--noconfirm` deletes whatever is there. The driver
refuses to build one layout over the other; `--clean` is the explicit way.

## What `smoke` checks

`--version` against `scripts/version_info.py`; a run over an empty extraction; a run over
the NTFS raw fixture, whose log has to show the walk; the mister_skinnylegs plugins in the
bundle (read from the archive inside the executable for `--onefile`); and
`aleapp --selfcheck`, which takes the window's path, starts Tk, loads the images from
`assets/` and every artifact, then exits before drawing a window, and whose artifact count
has to match the source's. On Linux it also starts `aleapp` with no arguments and no
display, which must print the command line's help. On macOS all of it runs against the
`.app`.

Measured on 2026-09-29, macOS arm64, Python 3.14.7, PyInstaller 6.22.3: phase 1 in 42 s,
`smoke` in 7 s, 1,293 artifacts loaded by the build and from source (28 of them
mister_skinnylegs'), a 101 MB bundle, a 47 MB disk image, and a 44 MB `--onefile`
executable.

## What is and is not wired up

Windows (x64 and ARM64): the folder build and an Inno Setup installer, which on ARM64
installs only on ARM64. macOS (Apple silicon and Intel): `.app` and `.dmg`, laid out by
dmgbuild from `packaging/dmg_settings.py` on `packaging/dmg_background.png` (960x540; the
settings place the icons either side of its arrow). `dmg_background@2x.png` beside it, at
exactly 1920x1080, is what a Retina screen shows; dmgbuild joins the two with `tiffutil
-cathidpicheck`, which refuses a pair that is not exactly 1x and 2x. Export both from the
source artwork; upscaling the 1x brings the blur back. Linux (x64 and ARM64): the folder
build and an AppImage, made by appimagetool 1.9.1 with the type2 runtime 20251108, both
pinned by digest in `build.py`. Linux builds are made on Ubuntu 22.04 for its glibc 2.35.
`test_builds.yml` builds and smoke-tests all six legs weekly, on dispatch, and on pull
requests that touch packaging or the requirements.

`release.yml` runs the same steps when a `v*` tag is pushed, refuses a tag that is not
`v` + `leapp_version`, names the assets `ALEAPP-<version>-<platform>-<arch>` (setup.exe and
portable.zip on Windows, .dmg on macOS, .AppImage on Linux; no Linux .tar.gz), gathers them
in `release-assets/` (never `assets/`, which holds the window's images), adds
`SHA256SUMS.txt`, and creates a **draft** release. `.github/release-footer.md` is appended
to the notes. macOS is signed with a Developer ID, smoke-tested again as signed, notarised
and stapled, using the `MACOS_CERT_P12`, `MACOS_CERT_PASSWORD`, `MACOS_SIGN_IDENTITY`,
`MACOS_TEAM_ID`, `MACOS_NOTARY_KEY`, `MACOS_NOTARY_KEY_ID` and `MACOS_NOTARY_ISSUER_ID`
secrets. A tag refuses to publish without them, checked before building; a dispatched
rehearsal builds unsigned. Windows signing is not wired.

These names replaced the per-program downloads (`aleappGUI-v*-Windows_x86_64.zip` and the
like). Tools that run `aleapp` from a release are told in the footer what changed for them:
on Windows and macOS the executable needs its folder, and `aleappGUI` is gone.
