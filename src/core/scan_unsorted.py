# Standard Library imports
import logging
import os
from pathlib import Path

PHOTO_EXTENSIONS = {
    ".jpg", ".jpeg", ".jpe", ".png", ".heic", ".heif", ".avif", ".webp",
    ".tif", ".tiff", ".gif", ".bmp",
    # Camera raw formats
    ".dng", ".cr2", ".cr3", ".crw", ".nef", ".nrw", ".arw", ".srf", ".sr2",
    ".orf", ".rw2", ".raf", ".pef", ".srw", ".x3f",
}

VIDEO_EXTENSIONS = {
    ".mp4", ".mov", ".m4v", ".3gp", ".3g2", ".avi", ".mts", ".m2ts",
    ".mkv", ".wmv", ".mpg", ".mpeg", ".insv",
}

MEDIA_EXTENSIONS = PHOTO_EXTENSIONS | VIDEO_EXTENSIONS

# Files the OS creates on its own; safe to delete when cleaning up empty folders.
OS_JUNK_FILES = {".ds_store", "thumbs.db", "desktop.ini"}


def scan_unsorted(unsorted_dir: Path) -> tuple[list[Path], list[Path]]:
    """
    Walk the Unsorted folder, including subfolders.
    Returns (media files, other files). Hidden files are ignored.
    """
    media_files: list[Path] = []
    other_files: list[Path] = []

    for dirpath, dirnames, filenames in os.walk(unsorted_dir):
        # Skip hidden folders such as .Trashes or .Spotlight-V100
        dirnames[:] = sorted(name for name in dirnames if not name.startswith("."))

        for filename in sorted(filenames):
            # Hidden files include macOS "._IMG_1234.jpg" resource-fork companions.
            if filename.startswith(".") or filename.lower() in OS_JUNK_FILES:
                continue
            file_path = Path(dirpath) / filename
            if file_path.suffix.lower() in MEDIA_EXTENSIONS:
                media_files.append(file_path)
            else:
                other_files.append(file_path)

    return media_files, other_files


def remove_empty_folders(unsorted_dir: Path) -> None:
    """
    Remove subfolders of Unsorted that are empty after sorting
    (apart from OS junk files). Unsorted itself is kept.
    """
    main_logger = logging.getLogger("main")

    for dirpath, _, _ in sorted(os.walk(unsorted_dir), key=lambda entry: len(entry[0]), reverse=True):
        folder = Path(dirpath)
        if folder == unsorted_dir:
            continue
        try:
            entries = list(folder.iterdir())
            if all(entry.is_file() and _is_removable_junk(entry.name) for entry in entries):
                for entry in entries:
                    entry.unlink()
                folder.rmdir()
                main_logger.info(f"Removed empty folder {folder}")
        except OSError as error:
            main_logger.warning(f"Could not remove folder {folder}: {error}")


def _is_removable_junk(filename: str) -> bool:
    return filename.lower() in OS_JUNK_FILES or filename.startswith("._")
