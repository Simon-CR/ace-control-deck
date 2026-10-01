#!/bin/bash
set -e

echo "Installing ACE Control Deck patches..."

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
python3 "$DIR/patch_mainsail.py" "$@"

echo "Installation complete."
