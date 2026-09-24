# Standard Library imports
import re
from datetime import datetime
from pathlib import Path

# Characters not allowed in file or folder names on Windows/exFAT, plus control characters.
_INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}

# Matches a prefix added by an earlier run, e.g. "2024-07-15_09-30-00_".
_DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}_")

DATE_PREFIX_FORMAT = "%Y-%m-%d_%H-%M-%S"


def safe_folder_name(name: str | None, fallback: str) -> str:
    """
    Make a place name safe to use as a folder name on Windows, macOS and Linux.
    """
    if not name:
        return fallback

    cleaned = _INVALID_CHARS.sub("_", name).strip().rstrip(". ")
    if not cleaned:
        return fallback
    if cleaned.split(".")[0].upper() in _RESERVED_NAMES:
        cleaned = f"_{cleaned}"
    return cleaned


def dated_filename(original_name: str, taken_at: datetime | None) -> str:
    """
    Prefix the capture time so files list in chronological order in any file browser:
    IMG_1234.jpg -> 2024-07-15_09-30-00_IMG_1234.jpg
    A prefix from an earlier run is replaced rather than stacked.
    """
    base_name = _DATE_PREFIX.sub("", original_name)
    if taken_at is None:
        return base_name
    return f"{taken_at.strftime(DATE_PREFIX_FORMAT)}_{base_name}"


def path_key(path: Path) -> str:
    """Case-insensitive key for a path, since exFAT/NTFS/APFS ignore case by default."""
    return str(path).casefold()


def unique_destination(destination: Path, taken: set[str] | None = None) -> Path:
    """
    Return a path that neither exists on disk nor is in `taken`
    (path_key() of paths already planned in this run), adding _1, _2, ... when needed.
    """
    taken = taken if taken is not None else set()

    def is_free(candidate: Path) -> bool:
        return not candidate.exists() and path_key(candidate) not in taken

    if is_free(destination):
        return destination

    index = 1
    while True:
        candidate = destination.with_name(f"{destination.stem}_{index}{destination.suffix}")
        if is_free(candidate):
            return candidate
        index += 1
