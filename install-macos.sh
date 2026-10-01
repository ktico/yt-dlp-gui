#!/bin/sh
# One-command installer for macOS.
#
# Downloading a release asset with curl does not set the
# com.apple.quarantine attribute that Safari/Finder add, so Gatekeeper never
# shows the "cannot be verified / malware" dialog for a binary installed this
# way. Run this script from Terminal:
#
#   curl -fsSL https://raw.githubusercontent.com/ktico/yt-dlp-gui/ktico-standalone-downloader-gui/install-macos.sh | sh
#
# It downloads the latest yt-dlp-gui-macos release, installs it to
# ~/Applications, makes sure no quarantine attribute is present, and launches
# it.

set -eu

REPO="ktico/yt-dlp-gui"
ASSET_NAME="yt-dlp-gui-macos"
INSTALL_DIR="$HOME/Applications"
INSTALL_PATH="$INSTALL_DIR/yt-dlp-gui-macos"

echo "Looking up the latest release of $REPO..."
DOWNLOAD_URL=$(curl -fsSL \
    -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/$REPO/releases/latest" |
    sed -n 's/.*"browser_download_url": *"\([^"]*'"$ASSET_NAME"'\)".*/\1/p' |
    head -n 1)

if [ -z "$DOWNLOAD_URL" ]; then
    echo "Could not find a $ASSET_NAME asset in the latest release of $REPO." >&2
    exit 1
fi

mkdir -p "$INSTALL_DIR"
echo "Downloading $DOWNLOAD_URL..."
curl -fsSL --output "$INSTALL_PATH" "$DOWNLOAD_URL"
chmod +x "$INSTALL_PATH"

# Defensive: clear any quarantine attribute in case curl ever inherits one
# (for example when run from inside a sandboxed terminal or downloaded via a
# tool that tags it). This is a no-op in the common case.
xattr -cr "$INSTALL_PATH" 2>/dev/null || true

echo "Installed to $INSTALL_PATH"
echo "Launching yt-dlp GUI..."
open "$INSTALL_PATH"
