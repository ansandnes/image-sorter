"""
Runs main.py against a temporary drive with real photo/video files.
Needs ExifTool: set IMAGE_SORTER_EXIFTOOL, have exiftool on PATH, or build the
drive once (python scripts/build_drive.py) so dist/ImageSorter has a copy.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.helpers import write_geodata

REPO_DIR = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def find_exiftool() -> list[str] | None:
    override = os.environ.get("IMAGE_SORTER_EXIFTOOL")
    if override:
        return [override]
    on_path = shutil.which("exiftool")
    if on_path:
        return [on_path]
    built = REPO_DIR / "dist" / "ImageSorter" / "app" / "exiftool" / "perl" / "exiftool"
    perl = shutil.which("perl")
    if built.is_file() and perl:
        return [perl, str(built)]
    return None


EXIFTOOL = find_exiftool()


@unittest.skipIf(EXIFTOOL is None, "ExifTool not available")
class TestEndToEnd(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp())
        self.unsorted = self.root / "Unsorted"
        self.unsorted.mkdir()
        write_geodata(self.root / "app" / "geodata")

    def tearDown(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)

    def make_file(self, fixture: str, relative: str, *tag_args: str) -> None:
        target = self.unsorted / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(FIXTURES / fixture, target)
        subprocess.run(
            [*EXIFTOOL, "-q", "-overwrite_original", *tag_args, str(target)],
            check=True,
        )

    def run_sorter(self, *args: str) -> subprocess.CompletedProcess:
        environment = dict(os.environ, PYTHONUTF8="1")
        # Hand ExifTool to the sorter the same way the test found it.
        if len(EXIFTOOL) == 1:
            environment["IMAGE_SORTER_EXIFTOOL"] = EXIFTOOL[0]
        else:
            perl_dir = self.root / "app" / "exiftool" / "perl"
            shutil.copytree(Path(EXIFTOOL[1]).parent, perl_dir, dirs_exist_ok=True)
        return subprocess.run(
            [sys.executable, str(REPO_DIR / "main.py"), "--root", str(self.root), *args],
            capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL,
        )

    def test_sorts_photos_and_videos(self) -> None:
        self.make_file(
            "base.jpg", "IMG_0001.jpg", "-all=",
            "-DateTimeOriginal=2024:07:15 09:30:00",
            "-GPSLatitude=59.9139", "-GPSLatitudeRef=N", "-GPSLongitude=10.7522", "-GPSLongitudeRef=E",
        )
        self.make_file(
            "base.jpg", "trip/Nordlys ø.jpg", "-all=",
            "-DateTimeOriginal=2024:12:31 23:59:00",
            "-GPSLatitude=69.6496", "-GPSLatitudeRef=N", "-GPSLongitude=18.956", "-GPSLongitudeRef=E",
        )
        self.make_file(
            "base.jpg", "rio.jpg", "-all=",
            "-DateTimeOriginal=2023:02:20 18:00:00",
            "-GPSLatitude=22.9068", "-GPSLatitudeRef=S", "-GPSLongitude=43.1729", "-GPSLongitudeRef=W",
        )
        self.make_file("base.jpg", "nogps.jpg", "-all=", "-DateTimeOriginal=2022:05:01 12:00:00")
        # 03:00 UTC on New Year's Day is still 2023 in New York.
        self.make_file(
            "base.mov", "VID_0042.MOV",
            "-QuickTime:CreateDate=2024:01:01 03:00:00",
            "-Keys:GPSCoordinates#=40.7128 -74.006 10",
        )
        shutil.copy(self.unsorted / "IMG_0001.jpg", self.unsorted / "trip" / "IMG_0001 copy.jpg")
        (self.unsorted / "notes.txt").write_text("not a photo")

        dry_run = self.run_sorter("--dry-run")
        self.assertEqual(dry_run.returncode, 0, dry_run.stdout + dry_run.stderr)
        self.assertFalse((self.root / "Sorted" / "2024").exists())

        result = self.run_sorter("--yes")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        found = sorted(
            path.relative_to(self.root).as_posix()
            for folder in ("Sorted", "Duplicates", "Unsorted")
            for path in (self.root / folder).rglob("*")
            if path.is_file()
        )
        self.assertEqual(
            found,
            [
                "Duplicates/IMG_0001 copy.jpg",
                "Sorted/2023/Brazil/Rio de Janeiro/2023-02-20_18-00-00_rio.jpg",
                "Sorted/2023/United States/New York City/2023-12-31_22-00-00_VID_0042.MOV",
                "Sorted/2024/Norway/Oslo/2024-07-15_09-30-00_IMG_0001.jpg",
                "Sorted/2024/Norway/Tromsø/2024-12-31_23-59-00_Nordlys ø.jpg",
                "Sorted/_Unknown/2022-05-01_12-00-00_nogps.jpg",
                "Unsorted/notes.txt",
            ],
        )


if __name__ == "__main__":
    unittest.main()
