#!/bin/bash
set -e

# Verify python3 is installed
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 is required but was not found in PATH." >&2
    exit 1
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
REPO_DIR="$( cd "$SCRIPT_DIR/.." >/dev/null 2>&1 && pwd )"

if [ ! -f "$SCRIPT_DIR/patch_mainsail.py" ]; then
    echo "Error: patch_mainsail.py not found at $SCRIPT_DIR/patch_mainsail.py" >&2
    exit 1
fi

if [ ! -f "$REPO_DIR/index.html" ]; then
    echo "Error: ACE Control Deck index.html not found at $REPO_DIR/index.html" >&2
    exit 1
fi

case "$1" in
    -h|--help)
        python3 "$SCRIPT_DIR/patch_mainsail.py" "$@"
        exit 0
        ;;
esac

echo "Installing ACE Control Deck patches..."
python3 "$SCRIPT_DIR/patch_mainsail.py" "$@"
echo "Installation complete."
