
---

## Which file to download

| Platform | File |
|---|---|
| Windows 10 or 11, 64-bit Intel or AMD | `-windows-x64-portable.zip` |
| Windows 11 on ARM | `-windows-arm64-portable.zip` |
| macOS, Apple silicon | `-macos-arm64.dmg` |
| macOS, Intel | `-macos-x64.dmg` |
| Linux, 64-bit Intel or AMD | `-linux-x64.AppImage` |
| Linux on ARM | `-linux-arm64.AppImage` |
| Linux (Debian/Ubuntu), 64-bit Intel or AMD | `-linux-x64.deb` |
| Linux (Debian/Ubuntu) on ARM | `-linux-arm64.deb` |
| Linux (Fedora/RHEL/openSUSE), 64-bit Intel or AMD | `-linux-x64.rpm` |
| Linux (Fedora/RHEL/openSUSE) on ARM | `-linux-arm64.rpm` |
| Arch Linux | AUR `aleapp-git` (see below) |

Every download holds one program, `aleapp`. Started without arguments, from the
Applications folder or a double-click, it opens the window. Given arguments in a terminal,
it is the command line. On macOS the command line is inside the app:

```bash
/Applications/ALEAPP.app/Contents/MacOS/aleapp --help
```

**For tools that run ALEAPP themselves.** The options, output and exit codes of `aleapp`
are those of earlier releases, but there is no `aleappGUI` any more, since `aleapp`
without arguments opens the window. On Windows the zip holds the whole program as one
file, `aleapp.exe`, which can be put wherever the tool expects it; there is no installer.
The executable inside the macOS app needs the folder it came in; on Linux the AppImage is
the whole program.

**`aleapp.exe` on Windows** unpacks itself to a temporary folder each time it starts, so it
takes a few seconds to start, and it does not run where a policy (AppLocker, WDAC) forbids
running programs from the temporary folder. There, run ALEAPP from source; the README has
the steps.

## First launch

The macOS disk images are signed with a Developer ID and notarised by Apple, so they open
without a warning.

The Windows binaries are not signed yet, so SmartScreen says "Windows protected your PC"
the first time. Choose More info, then Run anyway.

On Linux, make the AppImage executable once (`chmod +x ALEAPP-*.AppImage`). It needs FUSE
to start; where FUSE is not available, run it with `--appimage-extract-and-run`.

If you would rather not clear a warning, run from source instead; the README has the steps.

## Verify what you downloaded

`SHA256SUMS.txt` covers every file in this release. On macOS or Linux, from the folder you
downloaded into:

```bash
grep <the file you downloaded> SHA256SUMS.txt | shasum -a 256 -c -
```

Use `sha256sum` in place of `shasum -a 256` on Linux. On Windows, in PowerShell:

```powershell
(Get-FileHash -Algorithm SHA256 .\<the file you downloaded>).Hash
```

and compare it with the line in `SHA256SUMS.txt`, which is lower case.

## Linux

The build is made on Ubuntu 22.04, so it needs glibc 2.35 or newer and will not start on
an older distribution. That covers the AppImage and the `.deb`/`.rpm` packages alike:
all three wrap the same build.

The `.deb` installs with `sudo dpkg -i ALEAPP-*-linux-*.deb` on Debian/Ubuntu and the
`.rpm` with `sudo dnf install ALEAPP-*-linux-*.rpm` (or `sudo rpm -Uvh` it) on
Fedora/RHEL/openSUSE. Either puts `aleapp` on PATH with a desktop entry.

On Arch Linux, install `aleapp-git` from the AUR, which builds the latest commit:

```bash
yay -S aleapp-git
```

One-line install of the latest release (picks the `.deb`, `.rpm`, AUR package or
AppImage for the machine it runs on, and checks `SHA256SUMS.txt` first):

```bash
curl -fsSL https://raw.githubusercontent.com/abrignoni/ALEAPP/main/scripts/install.sh | bash
```

## Code signing policy

The [code signing policy](https://github.com/abrignoni/ALEAPP#code-signing-policy) covers
Windows signing, team roles and privacy.
