import shutil
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from src.utils.naming import dated_filename, path_key, safe_folder_name, unique_destination


class TestNaming(unittest.TestCase):
    def test_dated_filename(self) -> None:
        self.assertEqual(
            dated_filename("IMG_1234.jpg", datetime(2024, 7, 15, 9, 30, 5)),
            "2024-07-15_09-30-05_IMG_1234.jpg",
        )

    def test_dated_filename_replaces_existing_prefix(self) -> None:
        self.assertEqual(
            dated_filename("2020-01-01_00-00-00_IMG_1234.jpg", datetime(2024, 7, 15, 9, 30)),
            "2024-07-15_09-30-00_IMG_1234.jpg",
        )

    def test_dated_filename_without_date(self) -> None:
        self.assertEqual(dated_filename("IMG_1234.jpg", None), "IMG_1234.jpg")

    def test_safe_folder_name(self) -> None:
        self.assertEqual(safe_folder_name("Tromsø", "x"), "Tromsø")
        self.assertEqual(safe_folder_name('A/B: "C"?', "x"), "A_B_ _C__")
        self.assertEqual(safe_folder_name("St. ", "x"), "St")
        self.assertEqual(safe_folder_name("CON", "x"), "_CON")
        self.assertEqual(safe_folder_name("", "fallback"), "fallback")
        self.assertEqual(safe_folder_name(None, "fallback"), "fallback")

    def test_unique_destination(self) -> None:
        temp_dir = Path(tempfile.mkdtemp())
        try:
            (temp_dir / "photo.jpg").write_bytes(b"x")
            planned = {path_key(temp_dir / "PHOTO_1.jpg")}  # case-insensitive clash
            self.assertEqual(unique_destination(temp_dir / "new.jpg", planned), temp_dir / "new.jpg")
            self.assertEqual(unique_destination(temp_dir / "photo.jpg", planned), temp_dir / "photo_2.jpg")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
