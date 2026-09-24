# Standard Library imports
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable

# Tags requested from ExifTool. -G prefixes each key with its group, e.g. "EXIF:DateTimeOriginal".
REQUESTED_TAGS = (
    "-EXIF:DateTimeOriginal",
    "-EXIF:CreateDate",
    "-XMP:DateTimeOriginal",
    "-XMP:DateCreated",
    "-QuickTime:CreationDate",
    "-QuickTime:CreateDate",
    "-QuickTime:MediaCreateDate",
    "-QuickTime:TrackCreateDate",
    "-PNG:CreationTime",
    "-GPSLatitude",
    "-GPSLongitude",
    "-GPSCoordinates",
)

# Files per ExifTool call. Keeps memory and argument files small while
# avoiding the cost of starting ExifTool once per file.
_BATCH_SIZE = 100


class ExifToolNotFoundError(RuntimeError):
    pass


class ExifTool:
    """
    Runs ExifTool to read date and GPS tags from photos and videos.

    Looks for, in order:
      1. the IMAGE_SORTER_EXIFTOOL environment variable (path to an exiftool executable)
      2. <exiftool_dir>/windows/exiftool.exe on Windows
      3. <exiftool_dir>/perl/exiftool run with the system Perl on macOS/Linux
      4. exiftool on PATH
    """

    def __init__(self, exiftool_dir: Path | str | None = None):
        self.command: list[str] = self._find_command(Path(exiftool_dir) if exiftool_dir else None)

    @staticmethod
    def _find_command(exiftool_dir: Path | None) -> list[str]:
        override = os.environ.get("IMAGE_SORTER_EXIFTOOL")
        if override:
            return [override]

        if exiftool_dir:
            if sys.platform == "win32":
                windows_exe = exiftool_dir / "windows" / "exiftool.exe"
                if windows_exe.is_file():
                    return [str(windows_exe)]
            else:
                perl_script = exiftool_dir / "perl" / "exiftool"
                perl = shutil.which("perl")
                if perl_script.is_file() and perl:
                    return [perl, str(perl_script)]

        on_path = shutil.which("exiftool")
        if on_path:
            return [on_path]

        raise ExifToolNotFoundError(
            "ExifTool was not found. Rebuild the drive with scripts/build_drive.py"
            + ("" if sys.platform == "win32" else ", and make sure Perl is installed")
            + "."
        )

    def version(self) -> str:
        result = subprocess.run(
            [*self.command, "-ver"], capture_output=True, text=True, encoding="utf-8"
        )
        return result.stdout.strip()

    def read_tags(
        self, files: list[Path], progress: Callable[[int, int], None] | None = None
    ) -> dict[str, dict]:
        """
        Read tags for many files. Returns {normalized path: {tag: value}}.
        Files ExifTool cannot read are missing from the result.
        """
        results: dict[str, dict] = {}
        for start in range(0, len(files), _BATCH_SIZE):
            batch = files[start:start + _BATCH_SIZE]
            for record in self._run_batch(batch):
                source = record.pop("SourceFile", None)
                if source:
                    results[normalize_path(source)] = record
            if progress:
                progress(min(start + _BATCH_SIZE, len(files)), len(files))
        return results

    def _run_batch(self, files: list[Path]) -> list[dict]:
        main_logger = logging.getLogger("main")

        # File names go in a UTF-8 argument file so non-ASCII names and long
        # lists work on every OS (the Windows command line is limited and not UTF-8).
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", suffix=".args", delete=False
        ) as argfile:
            for file_path in files:
                argfile.write(f"{file_path}\n")
            argfile_path = argfile.name

        try:
            result = subprocess.run(
                [
                    *self.command,
                    "-json",
                    "-n",              # numbers: signed decimal GPS, raw dates
                    "-G",              # prefix tag names with their group
                    "-q", "-q",        # no warnings on stderr for normal files
                    "-charset", "filename=utf8",
                    "-api", "largefilesupport=1",
                    *REQUESTED_TAGS,
                    "-@", argfile_path,
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
        finally:
            os.unlink(argfile_path)

        if result.stderr.strip():
            main_logger.warning(f"ExifTool: {result.stderr.strip()}")

        if not result.stdout.strip():
            return []

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as error:
            main_logger.error(f"Could not parse ExifTool output: {error}")
            return []


def normalize_path(path: Path | str) -> str:
    """
    Normalize a path for matching ExifTool's SourceFile against our file list
    (ExifTool reports Windows paths with forward slashes).
    """
    return os.path.normcase(os.path.normpath(str(path)))
