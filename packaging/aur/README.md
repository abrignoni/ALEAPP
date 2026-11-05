# Arch User Repository (AUR)

`aleapp-git` builds ALEAPP from the latest commit, so every reinstall tracks
`main`: its `pkgver()` reads `scripts/version_info.py` and appends the commit
count and short SHA, which is how a `-git` package stays current without a
maintainer bumping the version.

## For users

Once published, install with an AUR helper:

```bash
yay -S aleapp-git
```

Track the latest commit on upgrades (helpers only rebuild `-git` packages
with this enabled):

```bash
yay -Syu --devel
```

Without a helper, from this directory:

```bash
makepkg -si
```

## For maintainers

The AUR is hosted on `aur.archlinux.org`, not on GitHub: each AUR package is
its own Git repository there, and there is no pull-request mechanism. This
directory is the canonical source; review happens here, and publishing is a
push of exactly these files:

```bash
cd packaging/aur/aleapp-git
git init  # first time only
git remote add aur ssh://aur@aur.archlinux.org/aleapp-git.git
makepkg --printsrcinfo > .SRCINFO
makepkg --verifysource
namcap PKGBUILD
git add PKGBUILD .SRCINFO
git commit -m "update to <version>"
git push aur master
```

Before pushing, on Arch:

1. `makepkg --printsrcinfo > .SRCINFO` so the published metadata matches the
   `PKGBUILD` (this file drifts whenever `pkgver()` output moves).
2. `namcap PKGBUILD` and fix what it reports.
3. Build in a clean chroot (`extra-x86_64-build`) so missing `makedepends`
   are caught before users hit them.

The `PKGBUILD` builds the same PyInstaller folder (`python
packaging/build.py exe`) the AppImage wraps and installs it under
`/usr/lib/aleapp/`, with `/usr/bin/aleapp` as a symlink, so a system install
runs the same binary the releases ship. The `.desktop` entry is generated from
`packaging/build.py`'s `appimage_desktop_entry()`, the single source of that
text.
