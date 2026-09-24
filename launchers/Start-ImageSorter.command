#!/bin/sh
# macOS: double-clicking a .command file opens it in Terminal.
exec sh "$(dirname "$0")/start-image-sorter.sh" "$@"
