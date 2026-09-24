import shutil
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from src.core.app_paths import AppPaths
from src.core.organize_images import MoveKind, execute_moves, plan_moves
from src.core.processing_state import compute_file_hash, initialize_processing_state
from src.core.scan_unsorted import remove_empty_folders, scan_unsorted
from src.utils.classes.ImageMetadata import ImageMetadata
from src.utils.classes.Location import Location
from tests.helpers import close_main_logger


class TestOrganizeImages(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.paths = AppPaths(self.temp_dir)
        self.paths.ensure_folders()
        self.db_path = initialize_processing_state(self.paths.state_db)

    def tearDown(self) -> None:
        close_main_logger()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def add_file(self, relative: str, content: bytes) -> Path:
        path = self.paths.unsorted / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def item(self, path: Path, taken_at=None, location=None):
        metadata = ImageMetadata(path=path, taken_at=taken_at, location=location)
        return (metadata, compute_file_hash(str(path)))

    def test_plan_destinations(self) -> None:
        oslo = Location("Norway", "Oslo")
        complete = self.add_file("IMG_1.jpg", b"one")
        no_gps = self.add_file("IMG_2.jpg", b"two")
        nothing = self.add_file("sub/IMG_3.png", b"three")
        copy = self.add_file("sub/IMG_1 copy.jpg", b"one")

        planned = plan_moves(
            self.paths,
            [
                self.item(complete, datetime(2024, 7, 15, 9, 30), oslo),
                self.item(no_gps, datetime(2023, 1, 2, 3, 4, 5)),
                self.item(nothing),
                self.item(copy, datetime(2024, 7, 15, 9, 30), oslo),
            ],
            self.db_path,
        )

        destinations = [(self.paths.relative(move.destination), move.kind) for move in planned]
        self.assertEqual(
            destinations,
            [
                ("Sorted/2024/Norway/Oslo/2024-07-15_09-30-00_IMG_1.jpg", MoveKind.SORTED),
                ("Sorted/_Unknown/2023-01-02_03-04-05_IMG_2.jpg", MoveKind.UNKNOWN),
                ("Sorted/_Unknown/IMG_3.png", MoveKind.UNKNOWN),
                ("Duplicates/IMG_1 copy.jpg", MoveKind.DUPLICATE),
            ],
        )
        # Planning never touches files.
        self.assertTrue(all(move.source.exists() for move in planned))
        self.assertFalse((self.paths.sorted / "2024").exists())

    def test_same_name_same_time_gets_suffix(self) -> None:
        oslo = Location("Norway", "Oslo")
        taken_at = datetime(2024, 7, 15, 9, 30)
        first = self.add_file("a/IMG_1.jpg", b"first")
        second = self.add_file("b/IMG_1.jpg", b"second")

        planned = plan_moves(
            self.paths, [self.item(first, taken_at, oslo), self.item(second, taken_at, oslo)], self.db_path
        )
        self.assertEqual(
            [move.destination.name for move in planned],
            ["2024-07-15_09-30-00_IMG_1.jpg", "2024-07-15_09-30-00_IMG_1_1.jpg"],
        )

    def test_execute_then_rerun_detects_duplicate(self) -> None:
        oslo = Location("Norway", "Oslo")
        taken_at = datetime(2024, 7, 15, 9, 30)
        source = self.add_file("trip/IMG_1.jpg", b"photo")

        planned = plan_moves(self.paths, [self.item(source, taken_at, oslo)], self.db_path)
        result = execute_moves(self.paths, planned, self.db_path)
        remove_empty_folders(self.paths.unsorted)

        self.assertEqual(result.moved[MoveKind.SORTED], 1)
        self.assertFalse(source.exists())
        self.assertTrue(planned[0].destination.exists())
        self.assertFalse((self.paths.unsorted / "trip").exists())

        # Same file dropped in again -> Duplicates
        again = self.add_file("IMG_1.jpg", b"photo")
        planned_again = plan_moves(self.paths, [self.item(again, taken_at, oslo)], self.db_path)
        self.assertEqual(planned_again[0].kind, MoveKind.DUPLICATE)

        # ...unless the sorted copy has been deleted: then it is sorted again.
        planned[0].destination.unlink()
        planned_after_delete = plan_moves(self.paths, [self.item(again, taken_at, oslo)], self.db_path)
        self.assertEqual(planned_after_delete[0].kind, MoveKind.SORTED)

    def test_scan_skips_hidden_and_separates_other_files(self) -> None:
        self.add_file("IMG_1.JPG", b"1")
        self.add_file("clip.mov", b"2")
        self.add_file("notes.txt", b"3")
        self.add_file("._IMG_1.JPG", b"4")
        self.add_file(".hidden/IMG_2.jpg", b"5")
        self.add_file("Thumbs.db", b"6")

        media, other = scan_unsorted(self.paths.unsorted)
        self.assertEqual(sorted(path.name for path in media), ["IMG_1.JPG", "clip.mov"])
        self.assertEqual([path.name for path in other], ["notes.txt"])


if __name__ == "__main__":
    unittest.main()
