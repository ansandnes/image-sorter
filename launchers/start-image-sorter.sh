#!/bin/sh
# Image Sorter launcher for macOS and Linux.
# Uses the Python bundled on the drive, or python3 from this computer as a fallback.

ROOT="$(cd "$(dirname "$0")" && pwd)"

case "$(uname -s)-$(uname -m)" in
    Darwin-arm64)               PY_DIR="macos-arm64" ;;
    Darwin-x86_64)              PY_DIR="macos-x64" ;;
    Linux-x86_64)               PY_DIR="linux-x64" ;;
    Linux-aarch64|Linux-arm64)  PY_DIR="linux-arm64" ;;
    *)                          PY_DIR="" ;;
esac

PYTHON="$ROOT/app/python/$PY_DIR/bin/python3"
if [ -z "$PY_DIR" ] || [ ! -f "$PYTHON" ]; then
    PYTHON="$(command -v python3 || true)"
fi

if [ "$(uname -s)" = "Darwin" ]; then
    # Files copied from the internet are quarantined by macOS and refuse to run.
    xattr -dr com.apple.quarantine "$ROOT/app" 2>/dev/null || true
fi

if [ -z "$PYTHON" ]; then
    echo "Python was not found. Rebuild the drive with scripts/build_drive.py."
    status=1
else
    PYTHONPATH="$ROOT/app/lib" PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1 \
        "$PYTHON" "$ROOT/app/image-sorter/main.py" --root "$ROOT" "$@"
    status=$?
fi

# Keep the window open when started by double-clicking.
if [ -t 0 ]; then
    printf "\nPress Enter to close..."
    read -r _
fi
exit $status
