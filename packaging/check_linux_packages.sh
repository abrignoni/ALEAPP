#!/usr/bin/env bash
# Install the native Linux packages the way a user would and run what they installed.
#
#   bash packaging/check_linux_packages.sh <version>
#
# <version> is leapp_version as scripts/version_info.py has it (2026.4.6-dev), which is
# what `aleapp --version` must print. Run on an Ubuntu GitHub runner after
# `build.py linux-packages`, from the repository root: the .deb is installed on the runner
# with apt, and the .rpm with dnf inside a Fedora container, because a package can build
# cleanly and still not start once installed. Both are removed again afterwards.
set -euo pipefail

VERSION="${1:?usage: check_linux_packages.sh <version>}"
WANT="ALEAPP $VERSION"

shopt -s nullglob
debs=(dist/aleapp_*.deb)
rpms=(dist/aleapp-*.rpm)
if [ "${#debs[@]}" -ne 1 ] || [ "${#rpms[@]}" -ne 1 ]; then
  echo "::error::expected one .deb and one .rpm in dist/, found ${#debs[@]} and ${#rpms[@]}"
  exit 1
fi
DEB="${debs[0]}"
RPM="${rpms[0]}"

echo "==> $DEB"
dpkg-deb --info "$DEB"
tmp="$(mktemp -d)"
dpkg-deb --extract "$DEB" "$tmp"
desktop-file-validate "$tmp/usr/share/applications/aleapp.desktop"
rm -rf "$tmp"

sudo apt-get install -y -q "./$DEB" </dev/null
got="$(aleapp --version)"
[ "$(readlink -f "$(command -v aleapp)")" = /usr/lib/aleapp/aleapp ] || {
  echo "::error::aleapp on PATH is not /usr/lib/aleapp/aleapp"; exit 1; }
if [ "$got" != "$WANT" ]; then
  echo "::error::the installed .deb reports '$got', expected '$WANT'"
  exit 1
fi
echo "==> the installed .deb reports '$got'"
sudo apt-get remove -y -q aleapp </dev/null
if [ -e /usr/lib/aleapp ] || [ -e /usr/bin/aleapp ]; then
  echo "::error::removing the .deb left files behind"
  exit 1
fi

echo "==> $RPM"
rpm -qip "$RPM"
# The bundled libraries must not be advertised to dnf as provided by this package.
if rpm -qp --provides "$RPM" | grep -F '.so'; then
  echo "::error::the .rpm lists shared libraries under Provides"
  exit 1
fi
docker run --rm -v "$PWD/dist:/pkgs:ro" -e WANT="$WANT" -e RPM="$(basename "$RPM")" \
  fedora:latest bash -euo pipefail -c '
    cat /etc/fedora-release
    dnf install -y -q "/pkgs/$RPM"
    got="$(aleapp --version)"
    if [ "$got" != "$WANT" ]; then
      echo "::error::the installed .rpm reports [$got], expected [$WANT]"
      exit 1
    fi
    echo "==> the installed .rpm reports [$got]"
    dnf remove -y -q aleapp
    if [ -e /usr/lib/aleapp ] || [ -e /usr/bin/aleapp ]; then
      echo "::error::removing the .rpm left files behind"
      exit 1
    fi
  ' </dev/null
